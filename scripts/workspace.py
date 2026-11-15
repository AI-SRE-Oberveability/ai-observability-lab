"""Resolve approved repository layouts and private runtime paths without network calls."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

LAB = Path(__file__).resolve().parents[1]
REGISTRY = LAB / "tracking/workspace-layout.json"
ROLES = {"infra", "config", "charts", "gitops", "pipelines", "workloads", "lab"}
ROLE_ALIASES = {"observability": "charts", "observability-config": "charts"}


def load_registry(path=REGISTRY):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_registry(data)


def validate_registry(data):
    if (
        not isinstance(data, dict)
        or type(data.get("schema_version")) is not int
        or data["schema_version"] != 1
        or not isinstance(data.get("repositories"), list)
    ):
        raise ValueError("Unsupported workspace registry")
    rows = data["repositories"]
    if (
        len(rows) != 7
        or not all(
            isinstance(row, dict) and isinstance(row.get("role"), str) for row in rows
        )
        or {row.get("role") for row in rows} != ROLES
    ):
        raise ValueError("Exactly seven unique approved roles are required")
    owners = {}
    identities = set()
    for row in rows:
        if type(row.get("repository_id")) is not int or row["repository_id"] <= 0:
            raise ValueError("Verified repository ID required")
        if row["repository_id"] in identities:
            raise ValueError("Repository IDs must be unique")
        identities.add(row["repository_id"])
        if (
            not isinstance(row.get("github_names"), list)
            or not row["github_names"]
            or any(
                not isinstance(name, str)
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*", name)
                for name in row["github_names"]
            )
        ):
            raise ValueError("Approved GitHub repository names required")
        if not isinstance(row.get("legacy_folders"), list):
            raise ValueError("Legacy folder aliases must be explicit")
        for folder in [row.get("folder"), *row["legacy_folders"]]:
            if not isinstance(folder, str) or not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9-]*", folder
            ):
                raise ValueError("Repository folder must be one safe component")
            previous = owners.setdefault(folder.casefold(), row["role"])
            if previous != row["role"]:
                raise ValueError("Repository alias belongs to multiple roles")
    return data


def parts(name):
    if not isinstance(name, str) or not name or any(ord(c) < 32 for c in name):
        raise ValueError("Relative workspace path required")
    value = name.replace("\\", "/")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p == ".." or ":" in p for p in path.parts):
        raise ValueError("Workspace path must not escape its root")
    if not path.parts and value not in {".", "./"}:
        raise ValueError("Relative workspace path required")
    return path.parts


class Workspace:
    def __init__(self, root, *, registry=None):
        self.root = Path(root).resolve()
        self.registry = (
            load_registry() if registry is None else validate_registry(registry)
        )
        rows = self.registry["repositories"]
        self.roles = {row["role"]: row for row in rows}
        self.aliases = {
            folder.casefold(): row["role"]
            for row in rows
            for folder in [row["folder"], *row["legacy_folders"]]
        }
        self.canonical = (self.root / self.roles["lab"]["folder"]).is_dir()

    def repo(self, role, *, required=True):
        role = ROLE_ALIASES.get(role, role)
        if role not in self.roles:
            raise ValueError("Unknown repository role")
        row = self.roles[role]
        aliases = [row["folder"], *row["legacy_folders"]]
        found = []
        for alias in aliases:
            candidate = self.root / alias
            if not candidate.exists() and not candidate.is_symlink():
                continue
            resolved = candidate.resolve()
            if not resolved.is_relative_to(self.root) or not resolved.is_dir():
                raise ValueError(
                    "Repository alias leaves the workspace or is not a directory"
                )
            # WSL on NTFS can expose two case aliases for the same inode even
            # though pathlib's POSIX spelling differs. Reject distinct clones.
            if not any(resolved.samefile(previous) for previous in found):
                found.append(resolved)
        if len(found) > 1:
            raise ValueError("Ambiguous repository aliases for " + role)
        if found:
            return found[0]
        if required:
            raise ValueError("Repository checkout missing for " + role)
        preferred = (
            row["folder"]
            if self.canonical or not row["legacy_folders"]
            else row["legacy_folders"][0]
        )
        return self.root / preferred

    def path(self, name):
        components = parts(name)
        if not components:
            return self.root
        role = self.aliases.get(components[0].casefold())
        boundary = self.repo(role, required=False) if role else self.root
        target = (
            boundary.joinpath(*components[1:])
            if role
            else boundary.joinpath(*components)
        ).resolve()
        if not target.is_relative_to(boundary.resolve()) or not target.is_relative_to(
            self.root
        ):
            raise ValueError("Workspace path or symlink leaves its ownership boundary")
        return target

    def lab_relative(self, name):
        components = parts(name)
        if len(components) < 2 or self.aliases.get(components[0].casefold()) != "lab":
            raise ValueError("Lab-owned evidence path required")
        return PurePosixPath(*components[1:]).as_posix()

    def verify_clone(self, role):
        role = ROLE_ALIASES.get(role, role)
        folder = self.repo(role)
        top = subprocess.run(
            ["git", "-C", str(folder), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        origin = subprocess.run(
            ["git", "-C", str(folder), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if (
            top.returncode
            or origin.returncode
            or Path(top.stdout.strip()).resolve() != folder
        ):
            raise ValueError("Expected an independent Git checkout for " + role)
        url = urlsplit(origin.stdout.strip())
        name = url.path.strip("/").removesuffix(".git").split("/")
        if not (
            url.scheme == "https"
            and url.netloc.casefold() == "github.com"
            and not url.query
            and not url.fragment
            and len(name) == 2
            and name[0].casefold() == "AI-SRE-Oberveability".casefold()
            and name[1].casefold()
            in {value.casefold() for value in self.roles[role]["github_names"]}
        ):
            raise ValueError("GitHub origin is outside the approved repository role")
        return folder

    def runtime(self, requested=None):
        location = self.root / ".runtime"
        if location.is_symlink() or location.is_junction():
            raise ValueError("Private runtime root must not be a symlink or junction")
        private = location.resolve()
        target = private if requested is None else Path(requested).resolve()
        if not private.is_relative_to(self.root) or not target.is_relative_to(private):
            raise ValueError("Runtime must stay in the workspace's private .runtime")
        # Detect real/nested worktrees and bare repositories, independent of clone names.
        for ancestor in (target, *target.parents):
            marker = ancestor / ".git"
            if (
                marker.exists()
                or marker.is_symlink()
                or ((ancestor / "HEAD").is_file() and (ancestor / "objects").is_dir())
            ):
                raise ValueError("Runtime must be outside every Git repository")
        return target

    def write_compose(self, destination):
        destination = self.runtime(destination)
        includes = [
            self.repo("charts") / "local/compose.yaml",
            self.repo("workloads") / "compose.yaml",
        ]
        if not all(path.is_file() for path in includes):
            raise ValueError("Compose inputs are missing")
        destination.parent.mkdir(parents=True, exist_ok=True)
        text = "name: personal-ai-observability\ninclude:\n" + "".join(
            "  - " + json.dumps(path.as_posix()) + "\n" for path in includes
        )
        destination.write_text(text, encoding="utf-8", newline="\n")
        return destination

    def editor(self):
        return {
            "folders": [
                {
                    "name": role,
                    "path": "."
                    if role == "lab"
                    else "../" + self.repo(role, required=False).name,
                }
                for role in self.roles
                if self.repo(role, required=False).is_dir()
            ]
        }


def current():
    return Workspace(LAB.parent)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["describe", "compose", "editor"])
    parser.add_argument("--root", type=Path, default=LAB.parent)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify local Git origins; no network or credentials",
    )
    args = parser.parse_args()
    workspace = Workspace(args.root)
    if args.verify:
        for role in workspace.roles:
            if workspace.repo(role, required=False).is_dir():
                workspace.verify_clone(role)
    if args.command == "compose":
        target = args.output or workspace.runtime() / "compose.yaml"
        result = {"compose_file": str(workspace.write_compose(target))}
    elif args.command == "editor":
        result = workspace.editor()
        if args.output:
            # Editor output is authored JSON; it contains paths only, never credentials.
            args.output.write_text(
                json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n"
            )
    else:
        result = {
            "canonical_layout": workspace.canonical,
            "repositories": {
                role: str(workspace.repo(role, required=False))
                for role in workspace.roles
            },
            "runtime": str(workspace.runtime()),
            "azure_deployment_enabled": False,
        }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
