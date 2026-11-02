"""Validate a source-pinned candidate without fetching, publishing or deploying anything."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

LAB = Path(__file__).resolve().parents[1]
BASE = LAB.parent
DEFAULT = LAB / "releases/local-v0.1.0-source-candidate.json"
REPOSITORIES = {
    "infra": ("ai-observability-infra", "AI-SRE-Oberveability/AI-Observability-Infra"),
    "workloads": ("ai-agent-workloads", "AI-SRE-Oberveability/ai-agent-workloads"),
    "observability": (
        "ai-observability-config",
        "AI-SRE-Oberveability/ai-observability-config",
    ),
    "lab": ("ai-observability-lab", "AI-SRE-Oberveability/ai-observability-lab"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value, length):
    return (
        isinstance(value, str)
        and re.fullmatch(r"[0-9a-f]{" + str(length) + "}", value) is not None
        and value != "0" * length
    )


def immutable_image(value):
    return (
        isinstance(value, str)
        and re.fullmatch(r"[a-z0-9][a-z0-9./:_-]*@sha256:[0-9a-f]{64}", value)
        is not None
        and digest(value.rsplit(":", 1)[1], 64)
    )


def validate(manifest, *, require_deployable=False):
    require(isinstance(manifest, dict), "Manifest must be a JSON object")
    require(
        type(manifest.get("schema_version")) is int and manifest["schema_version"] == 1,
        "Unsupported manifest schema",
    )
    require(
        manifest.get("status") == "source-pinned-candidate",
        "Only candidate status is supported",
    )
    require(
        manifest.get("deployable") is False,
        "A source candidate must not claim deployability",
    )
    require(
        manifest.get("azure_deployment_enabled") is False,
        "Azure deployment must remain disabled",
    )
    require(
        manifest.get("model_mode") == "deterministic-mock",
        "Only the deterministic cohort is pinned",
    )
    repositories = manifest.get("repositories", {})
    require(
        set(repositories) == set(REPOSITORIES),
        "Exactly four approved repositories are required",
    )
    for role, (_, expected) in REPOSITORIES.items():
        entry = repositories[role]
        require(
            entry.get("repository") == expected,
            "Repository ownership mismatch: " + role,
        )
        require(
            digest(entry.get("commit"), 40),
            "A full immutable commit is required: " + role,
        )
        ci = entry.get("main_ci", {})
        run_id = ci.get("run_id")
        require(
            type(run_id) is int and run_id > 0, "A CI run receipt is required: " + role
        )
        require(
            ci.get("conclusion") == "success"
            and ci.get("event") in {"push", "workflow_dispatch"},
            "Passing main CI is required: " + role,
        )
        require(
            ci.get("url") == f"https://github.com/{expected}/actions/runs/{run_id}",
            "CI receipt URL mismatch: " + role,
        )
    images = manifest.get("images", {})
    require(
        set(images) == {"workload", "workload_base", "collector", "jaeger"},
        "Image roles mismatch",
    )
    for role in ("workload_base", "collector", "jaeger"):
        require(
            immutable_image(images[role].get("reference")),
            "Immutable image digest required: " + role,
        )
    workload = images["workload"]
    if workload.get("reference") is None:
        require(
            workload.get("state") == "awaiting_registry_publication",
            "Missing image state is required",
        )
    else:
        require(
            immutable_image(workload["reference"]),
            "Workload image must use an immutable digest",
        )
        require(
            workload.get("state") == "digest_available_replay_pending",
            "Image replay remains pending",
        )
    packages = manifest.get("native_packages", {})
    require(set(packages) == {"collector", "jaeger"}, "Native package roles mismatch")
    for role, package in packages.items():
        require(
            re.fullmatch(r"\d+\.\d+\.\d+", package.get("version", "")) is not None,
            "Explicit native package version required: " + role,
        )
        require(
            digest(package.get("sha256"), 64), "Native package digest required: " + role
        )
        url = urlsplit(package.get("url", ""))
        require(
            url.scheme == "https"
            and url.netloc == "github.com"
            and not url.query
            and not url.fragment
            and "/releases/download/" in url.path,
            "Expected a direct HTTPS GitHub release archive: " + role,
        )
    sources = manifest.get("source_files", [])
    require(
        isinstance(sources, list) and bool(sources), "Pinned source files are required"
    )
    seen = set()
    for source in sources:
        role, name = source.get("role"), source.get("path", "")
        require(role in REPOSITORIES, "Unknown source role")
        require(
            isinstance(name, str)
            and name
            and "\\" not in name
            and not any(ord(c) < 32 for c in name),
            "Invalid source path",
        )
        path = PurePosixPath(name)
        require(
            not path.is_absolute()
            and all(p not in {".", ".."} for p in path.parts)
            and not any(p.startswith(".env") for p in path.parts),
            "Unsafe source path",
        )
        require((role, name) not in seen, "Duplicate source file")
        require(digest(source.get("sha256"), 64), "Source hash required")
        seen.add((role, name))
    require(
        {role for role, _ in seen} == set(REPOSITORIES),
        "Source hashes must cover all four repositories",
    )
    require(
        bool(manifest.get("pending")),
        "The incomplete candidate must list remaining work",
    )
    require(
        manifest.get("evidence", {}).get("main_ci")
        == "evidence/main-ci-revalidation.json",
        "Expected the reviewed main CI receipt",
    )
    if require_deployable:
        raise ValueError(
            "Candidate is not deployable: workload image publication and container replay remain pending"
        )
    return {
        "candidate_valid": True,
        "deployable": False,
        "workload_image_missing": workload.get("reference") is None,
    }


def read_source(manifest, role, name, base):
    folder = REPOSITORIES[role][0]
    commit = manifest["repositories"][role]["commit"]
    result = subprocess.run(
        ["git", "-C", str(base / folder), "show", commit + ":" + name],
        capture_output=True,
    )
    require(
        result.returncode == 0, "Pinned Git object unavailable: " + role + "/" + name
    )
    return result.stdout


def verify_sources(manifest, base=BASE):
    validate(manifest)
    receipt = json.loads(
        (LAB / manifest["evidence"]["main_ci"]).read_text(encoding="utf-8")
    )
    rows = {row["repo"]: row for row in receipt["repositories"]}
    require(len(rows) == 4, "Four main CI receipts required")
    for role, (_, repository) in REPOSITORIES.items():
        entry = manifest["repositories"][role]
        row = rows.get(repository.split("/")[1], {})
        require(
            row.get("head") == entry["commit"]
            and row.get("run_id") == entry["main_ci"]["run_id"]
            and row.get("conclusion") == "success",
            "Main CI receipt does not cover the pinned commit",
        )
    pinned = {}
    for source in manifest["source_files"]:
        role, name = source["role"], source["path"]
        content = read_source(manifest, role, name, base)
        require(
            hashlib.sha256(content).hexdigest() == source["sha256"],
            "Pinned content hash mismatch",
        )
        pinned[(role, name)] = content
    required = {
        ("workloads", "Dockerfile"),
        ("observability", "local/compose.yaml"),
        ("observability", "local/windows-binaries.lock.json"),
    }
    require(required <= set(pinned), "Required image/package pin sources are missing")
    dockerfile = pinned[("workloads", "Dockerfile")].decode("utf-8")
    declared_base = re.search(r"^FROM\s+(\S+)", dockerfile, re.MULTILINE)
    require(
        declared_base is not None
        and declared_base.group(1) == manifest["images"]["workload_base"]["reference"],
        "Docker base pin differs from its tested source",
    )
    compose = pinned[("observability", "local/compose.yaml")].decode("utf-8")
    declared_images = set(re.findall(r"^\s+image:\s*(\S+)\s*$", compose, re.MULTILINE))
    require(
        declared_images
        == {manifest["images"][role]["reference"] for role in ("collector", "jaeger")},
        "Monitoring image pins differ from their tested source",
    )
    packages = json.loads(pinned[("observability", "local/windows-binaries.lock.json")])
    require(
        packages == manifest["native_packages"],
        "Native package pins differ from their tested lock",
    )
    return len(pinned)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path, default=DEFAULT)
    parser.add_argument(
        "--verify-sources",
        action="store_true",
        help="Read pinned objects in existing sibling clones; no fetch or checkout",
    )
    parser.add_argument(
        "--require-deployable",
        action="store_true",
        help="Fail closed for this incomplete source candidate",
    )
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = validate(manifest, require_deployable=args.require_deployable)
        result["source_files_verified"] = (
            verify_sources(manifest) if args.verify_sources else 0
        )
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, "Release validation failed: " + str(error) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
