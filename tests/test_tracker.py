"""Tracker safety checks only; these tests do not run application or cloud work."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "poc_tracker", Path(__file__).parents[1] / "scripts/poc_tracker.py"
)
tracker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tracker)


class TrackerChecks(unittest.TestCase):
    def test_atomic_json_save_survives_transient_destination_lock(self):
        target = self.base / "state.json"
        target.write_text('{"old": true}', encoding="utf-8")
        original = Path.replace
        calls = []

        def briefly_locked(source, destination):
            calls.append(destination)
            if len(calls) < 3:
                self.assertEqual(target.read_text(), '{"old": true}')
                raise PermissionError("Temporary sync lock")
            return original(source, destination)

        with (
            patch.object(Path, "replace", briefly_locked),
            patch.object(tracker.time, "sleep"),
        ):
            tracker.write_json(target, {"new": True})
        self.assertEqual(tracker.json.loads(target.read_text()), {"new": True})
        self.assertEqual(len(calls), 3)

    def test_permanent_destination_lock_preserves_previous_json(self):
        target = self.base / "state.json"
        target.write_text('{"old": true}', encoding="utf-8")
        with (
            patch.object(Path, "replace", side_effect=PermissionError("Locked")),
            patch.object(tracker.time, "sleep"),
            self.assertRaises(PermissionError),
        ):
            tracker.write_json(target, {"new": True})
        self.assertEqual(tracker.json.loads(target.read_text()), {"old": True})

    def setUp(self):
        runtime = Path(__file__).resolve().parents[2] / ".runtime" / "tracker-tests"
        runtime.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=runtime)
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        (self.base / "source.txt").write_text("version 1")
        (self.base / "proof.txt").write_text("observed validation")
        self.task = {
            "id": "P1.1",
            "title": "Example",
            "owner": "Codex",
            "acceptance": "Example accepted outcome",
            "depends_on": [],
            "gates": [],
            "watch": ["source.txt"],
            "artifacts": ["source.txt"],
        }
        self.plan = {
            "tasks": [self.task],
            "gates": {"G0": "User acceptance"},
            "phases": {"P1": "Example phase"},
        }
        self.state = {"decisions": {}, "steps": {}}

    def completed(self):
        self.state["steps"]["P1.1"] = {
            "status": "done",
            "evidence": ["proof.txt"],
            "source_hashes": tracker.snapshot(self.base, ["source.txt"]),
            "evidence_hashes": tracker.snapshot(self.base, ["proof.txt"]),
        }

    def status(self):
        return tracker.derive(self.plan, self.state, self.base)[0]["status"]

    def test_file_presence_does_not_prove_completion(self):
        self.assertEqual(self.status(), "draft")

    def test_changed_source_invalidates_pass(self):
        self.completed()
        self.assertEqual(self.status(), "done")
        (self.base / "source.txt").write_text("version 2")
        self.assertEqual(self.status(), "needs_revalidation")

    def test_missing_or_tampered_evidence_invalidates_pass(self):
        self.completed()
        (self.base / "proof.txt").write_text("different")
        self.assertEqual(self.status(), "needs_revalidation")
        (self.base / "proof.txt").unlink()
        self.assertEqual(self.status(), "needs_revalidation")

    def test_pending_gate_prevents_completion(self):
        self.completed()
        self.task["gates"] = ["G0"]
        self.assertEqual(self.status(), "blocked")
        self.state["decisions"]["G0"] = {"status": "accepted"}
        self.assertEqual(self.status(), "done")

    def test_cycle_and_unknown_dependency_are_rejected(self):
        self.task["depends_on"] = ["P1.1"]
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            tracker.validate_plan(self.plan)
        self.task["depends_on"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "Unknown"):
            tracker.validate_plan(self.plan)

    def test_failed_validation_is_retained(self):
        self.state["steps"]["P1.1"] = {"status": "failed", "note": "Observed failure"}
        self.assertEqual(self.status(), "failed")

    def test_dependencies_prevent_false_completion(self):
        self.completed()
        dependency = {**self.task, "id": "P0.1"}
        self.plan["tasks"].append(dependency)
        self.task["depends_on"] = ["P0.1"]
        self.assertEqual(self.status(), "blocked")

    def test_path_traversal_is_rejected(self):
        with self.assertRaises(ValueError):
            tracker.snapshot(self.base, ["../outside"])

    def test_refresh_renders_tracker_remaining_work_and_machine_status(self):
        lab = self.base / "lab"
        (lab / "tracking").mkdir(parents=True)
        tracker.render(self.plan, self.state, self.base, lab)
        self.assertIn("PAUSED", (lab / "POC_TRACKER.md").read_text(encoding="utf-8"))
        self.assertIn(
            "Example accepted outcome",
            (lab / "REMAINING.md").read_text(encoding="utf-8"),
        )
        self.assertTrue((lab / "tracking/status.json").is_file())
        self.assertEqual(self.state["decisions"], {})

    def test_snapshot_excludes_secret_and_runtime_files(self):
        (self.base / ".env").write_text("SYNTHETIC_SECRET_CANARY")
        runtime = self.base / ".runtime"
        runtime.mkdir()
        (runtime / "ignored.txt").write_text("runtime only")
        hashes = tracker.snapshot(self.base, ["."])
        self.assertNotIn(".env", hashes)
        self.assertNotIn(".runtime/ignored.txt", hashes)

    def test_evidence_links_stay_inside_published_repository(self):
        lab = self.base / "ai-observability-lab"
        (lab / "tracking").mkdir(parents=True)
        (lab / "evidence").mkdir()
        proof = lab / "evidence/result.txt"
        proof.write_text("recorded result")
        self.completed()
        record = self.state["steps"]["P1.1"]
        record["evidence"] = ["ai-observability-lab/evidence/result.txt"]
        record["evidence_hashes"] = tracker.snapshot(self.base, record["evidence"])
        tracker.render(self.plan, self.state, self.base, lab)
        content = (lab / "POC_TRACKER.md").read_text(encoding="utf-8")
        self.assertIn("[result.txt](evidence/result.txt)", content)
        self.assertNotIn("../ai-observability-lab/evidence", content)


if __name__ == "__main__":
    unittest.main()
