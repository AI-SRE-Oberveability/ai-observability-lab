"""Exercise ownership, runtime safety and consumers across both real layout shapes."""

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from lab_fixtures import temporary_directory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import poc_tracker as tracker
import sync_github_project as project_sync
from workspace import Workspace, load_registry, validate_registry


def layout(root, canonical):
    registry = load_registry()
    for row in registry["repositories"]:
        if (
            not canonical
            and not row["legacy_folders"]
            and row["role"] not in {"workloads", "lab"}
        ):
            continue
        folder = (
            row["folder"]
            if canonical or not row["legacy_folders"]
            else row["legacy_folders"][0]
        )
        (root / folder).mkdir()
    workspace = Workspace(root)
    (workspace.repo("lab") / "tracking").mkdir()
    for role, file in [
        ("charts", "local/compose.yaml"),
        ("workloads", "compose.yaml"),
        ("lab", "evidence/result.json"),
    ]:
        path = workspace.repo(role) / file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8", newline="\n")
    return workspace


class LayoutChecks(unittest.TestCase):
    def test_old_and_new_aliases_resolve_same_owned_content(self):
        for canonical in (False, True):
            with self.subTest(canonical=canonical), temporary_directory() as folder:
                root = Path(folder)
                workspace = layout(root, canonical)
                charts = workspace.repo("charts")
                for alias in ("ai-observability-config", "ai-platform-charts"):
                    self.assertEqual(
                        workspace.path(alias + "/local/compose.yaml"),
                        charts / "local/compose.yaml",
                    )
                self.assertEqual(workspace.repo("observability"), charts)
                self.assertEqual(
                    len(workspace.editor()["folders"]), 7 if canonical else 4
                )

    def test_historical_watch_keys_and_evidence_links_survive_clone_rename(self):
        snapshots = []
        for canonical in (False, True):
            with temporary_directory() as folder:
                root = Path(folder)
                workspace = layout(root, canonical)
                watched = ["ai-observability-config/local"]
                snapshots.append(tracker.snapshot(root, watched))
                for alias in ("ai-observability-lab", "ai-platform-lab"):
                    self.assertEqual(
                        workspace.lab_relative(alias + "/evidence/result.json"),
                        "evidence/result.json",
                    )
                self.assertEqual(
                    workspace.path("ai-observability-lab/evidence/result.json"),
                    workspace.repo("lab") / "evidence/result.json",
                )
                (workspace.repo("charts") / "local/compose.yaml").write_text(
                    "changed\n"
                )
                self.assertNotEqual(snapshots[-1], tracker.snapshot(root, watched))
        self.assertEqual(snapshots[0], snapshots[1])
        self.assertEqual(
            set(snapshots[0]), {"ai-observability-config/local/compose.yaml"}
        )

    def test_rendered_tracker_links_work_with_canonical_lab_folder(self):
        with temporary_directory() as folder:
            root = Path(folder)
            workspace = layout(root, True)
            task = {
                "id": "P1.1",
                "title": "Fixture",
                "owner": "Codex",
                "depends_on": [],
                "gates": [],
                "watch": ["ai-observability-lab/evidence/result.json"],
                "artifacts": [],
                "acceptance": "fixture only",
            }
            plan = {"phases": {"P1": "Fixture"}, "gates": {}, "tasks": [task]}
            evidence = ["ai-observability-lab/evidence/result.json"]
            state = {
                "decisions": {"G0": {"status": "accepted"}},
                "steps": {
                    "P1.1": {
                        "status": "done",
                        "evidence": evidence,
                        "source_hashes": tracker.snapshot(root, task["watch"]),
                        "evidence_hashes": tracker.snapshot(root, evidence),
                    }
                },
            }
            tracker.render(plan, state, root, workspace.repo("lab"))
            text = (workspace.repo("lab") / "POC_TRACKER.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("](evidence/result.json)", text)
            self.assertIn("**1 / 1**", text)

    def test_compose_uses_resolved_inputs_in_both_layouts(self):
        for canonical in (False, True):
            with self.subTest(canonical=canonical), temporary_directory() as folder:
                workspace = layout(Path(folder), canonical)
                output = workspace.write_compose(workspace.runtime() / "compose.yaml")
                values = [
                    json.loads(line.strip()[2:])
                    for line in output.read_text().splitlines()
                    if line.strip().startswith("- ")
                ]
                self.assertEqual(
                    set(values),
                    {
                        (workspace.repo("charts") / "local/compose.yaml").as_posix(),
                        (workspace.repo("workloads") / "compose.yaml").as_posix(),
                    },
                )
                with self.assertRaises(ValueError):
                    workspace.write_compose(workspace.repo("lab") / "private.yaml")

    def test_duplicate_alias_checkout_cannot_silently_select_another_source(self):
        with temporary_directory() as folder:
            root = Path(folder)
            workspace = layout(root, True)
            (root / "ai-observability-config").mkdir()
            with self.assertRaisesRegex(ValueError, "Ambiguous"):
                workspace.repo("charts")

    def test_traversal_absolute_and_foreign_evidence_paths_rejected(self):
        with temporary_directory() as folder:
            workspace = layout(Path(folder), True)
            for path in (
                "../outside",
                "/outside",
                "C:\\outside",
                "ai-platform-lab/../outside",
            ):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    workspace.path(path)
            with self.assertRaises(ValueError):
                workspace.lab_relative("ai-agent-workloads/evidence/result.json")

    def test_registry_rejects_unsafe_or_ambiguous_role_definitions(self):
        valid = load_registry()
        for change in (
            lambda data: data.update(schema_version=2),
            lambda data: data["repositories"][0].update(folder="../escape"),
            lambda data: data["repositories"][0].update(repository_id=True),
            lambda data: data["repositories"][0].update(
                repository_id=data["repositories"][1]["repository_id"]
            ),
            lambda data: data["repositories"][0]["legacy_folders"].append(
                data["repositories"][1]["folder"]
            ),
        ):
            altered = copy.deepcopy(valid)
            change(altered)
            with self.assertRaises(ValueError):
                validate_registry(altered)

    def test_local_origin_checks_reject_foreign_owner_and_host_without_network(self):
        with temporary_directory() as folder:
            workspace = layout(Path(folder), True)
            repo = workspace.repo("workloads")
            subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "remote",
                    "add",
                    "origin",
                    "https://github.com/AI-SRE-Oberveability/ai-agent-workloads.git",
                ],
                check=True,
            )
            self.assertEqual(workspace.verify_clone("workloads"), repo)
            for url in (
                "https://github.com/another-owner/ai-agent-workloads.git",
                "https://gitlab.example.invalid/lab/ai-agent-workloads.git",
            ):
                subprocess.run(
                    ["git", "-C", str(repo), "remote", "set-url", "origin", url],
                    check=True,
                )
                with self.assertRaises(ValueError):
                    workspace.verify_clone("workloads")


class RuntimeChecks(unittest.TestCase):
    def test_private_runtime_positive_and_every_repo_alias_negative(self):
        with temporary_directory() as folder:
            workspace = layout(Path(folder), True)
            self.assertEqual(
                workspace.runtime(workspace.root / ".runtime/proof"),
                workspace.root / ".runtime/proof",
            )
            for row in workspace.roles.values():
                for alias in [row["folder"], *row["legacy_folders"]]:
                    with self.subTest(alias=alias), self.assertRaises(ValueError):
                        workspace.runtime(workspace.root / alias / ".runtime/proof")
            with self.assertRaises(ValueError):
                workspace.runtime(workspace.root.parent / ".runtime")

    def test_unknown_nested_worktree_git_file_and_bare_repo_rejected(self):
        for kind in ("directory", "file", "bare"):
            with self.subTest(kind=kind), temporary_directory() as folder:
                workspace = layout(Path(folder), True)
                nested = workspace.root / ".runtime/unknown-checkout"
                nested.mkdir(parents=True)
                if kind == "directory":
                    (nested / ".git").mkdir()
                elif kind == "file":
                    (nested / ".git").write_text("gitdir: somewhere\n")
                else:
                    (nested / "HEAD").write_text("ref: refs/heads/main\n")
                    (nested / "objects").mkdir()
                with self.assertRaisesRegex(ValueError, "Git repository"):
                    workspace.runtime(nested / "captures")

    def test_symlink_escape_and_public_runtime_redirect_rejected(self):
        with temporary_directory() as folder, temporary_directory() as outside:
            workspace = layout(Path(folder), True)
            private = workspace.root / ".runtime"
            private.mkdir()
            try:
                (private / "redirect").symlink_to(
                    workspace.repo("lab"), target_is_directory=True
                )
                (workspace.repo("charts") / "outside").symlink_to(
                    Path(outside), target_is_directory=True
                )
                (Path(outside) / "source.txt").write_text("foreign")
                (workspace.repo("charts") / "foreign.txt").symlink_to(
                    Path(outside) / "source.txt"
                )
            except OSError:
                self.skipTest("Directory symlink privilege unavailable")
            with self.assertRaises(ValueError):
                workspace.runtime(private / "redirect/captures")
            with self.assertRaises(ValueError):
                workspace.path("ai-platform-charts/outside/capture.json")
            with self.assertRaises(ValueError):
                tracker.snapshot(workspace.root, ["ai-platform-charts"])

    def test_symlinked_private_root_rejected(self):
        with temporary_directory() as folder, temporary_directory() as outside:
            workspace = layout(Path(folder), True)
            try:
                (workspace.root / ".runtime").symlink_to(
                    Path(outside), target_is_directory=True
                )
            except OSError:
                self.skipTest("Directory symlink privilege unavailable")
            with self.assertRaises(ValueError):
                workspace.runtime()


class ProjectRefChecks(unittest.TestCase):
    def test_both_lab_aliases_link_to_current_github_repo_and_pinned_ref(self):
        task = {
            "id": "P1.1",
            "owner": "Codex",
            "depends_on": [],
            "gates": [],
            "acceptance": "Fixture",
        }
        for prefix in ("ai-observability-lab", "ai-platform-lab"):
            body = project_sync.managed_body(
                task,
                {
                    "status": "draft",
                    "blocked_by": [],
                    "evidence": [prefix + "/evidence/result.json"],
                },
                "1" * 40,
            )
            self.assertIn(
                "ai-observability-lab/blob/" + "1" * 40 + "/evidence/result.json", body
            )
        for reference in (
            "../main",
            "feature/mutable",
            "https://elsewhere.invalid",
            "0" * 39,
        ):
            with self.assertRaises(ValueError):
                project_sync.evidence_ref(reference)

    def test_unpublished_or_stale_evidence_blocks_before_mutation(self):
        sha = "1" * 40

        class GitHub:
            def __init__(self, stale):
                self.stale = stale

            def rest(self, method, path):
                self.assert_read(method)
                if "/git/ref/" in path:
                    return {"object": {"sha": sha}}
                if "/git/commits/" in path:
                    return {"sha": sha, "tree": {"sha": "2" * 40}}
                return {
                    "truncated": False,
                    "tree": [
                        {
                            "path": name,
                            "type": "blob",
                            "sha": "wrong" if self.stale else "hash",
                        }
                        for name in ["HLD.md", "POC_TRACKER.md", "evidence/result.json"]
                    ],
                }

            def assert_read(self, method):
                if method != "GET":
                    raise AssertionError(
                        "No mutation permitted before evidence verification"
                    )

        with temporary_directory() as folder:
            workspace = layout(Path(folder), True)
            lab = workspace.repo("lab")
            for name in ("HLD.md", "POC_TRACKER.md"):
                (lab / name).write_text("fixture")
            rows = [{"evidence": ["ai-observability-lab/evidence/result.json"]}]
            result = subprocess.CompletedProcess([], 0, "hash\n", "")
            with (
                patch.object(project_sync, "BASE", workspace.root),
                patch.object(project_sync, "LAB", lab),
                patch.object(project_sync.subprocess, "run", return_value=result),
            ):
                self.assertEqual(
                    project_sync.verify_evidence_ref(GitHub(False), rows, "main"), sha
                )
                with self.assertRaisesRegex(ValueError, "Publish current"):
                    project_sync.verify_evidence_ref(GitHub(True), rows, sha)


if __name__ == "__main__":
    unittest.main()
