"""Pure checks for issue ownership, managed content and honest status mapping."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_github_project import (  # noqa: E402
    board_status,
    ensure_issue_state,
    managed_body,
    merge_body,
    observed_fields,
    repository_for,
)


class ProjectSyncChecks(unittest.TestCase):
    def test_workflow_race_requires_observed_desired_issue_state(self):
        class WorkflowRace:
            state = "closed"

            def rest(self, method, path, body=None):
                if method == "PATCH":
                    raise RuntimeError("Concurrent workflow transition")
                return {"state": self.state}

        github = WorkflowRace()
        ensure_issue_state(github, "/approved-issue", {"state": "open"}, "closed")
        github.state = "open"
        with self.assertRaises(RuntimeError):
            ensure_issue_state(github, "/approved-issue", {"state": "open"}, "closed")

    def test_project_metadata_union_does_not_hide_managed_fields(self):
        response = {
            "fieldValues": {
                "nodes": [
                    {},
                    {"text": "P2.7", "field": {"name": "Task ID"}},
                    {"name": "Done", "field": {"name": "Status"}},
                ]
            }
        }
        self.assertEqual(
            observed_fields(response), {"Task ID": "P2.7", "Status": "Done"}
        )

    def test_only_done_maps_to_done(self):
        self.assertEqual(board_status("done"), "Done")
        self.assertEqual(board_status("in_progress"), "In Progress")
        for state in [
            "draft",
            "planned",
            "blocked",
            "failed",
            "needs_revalidation",
            "waiting_for_decision",
            "deferred",
        ]:
            self.assertEqual(board_status(state), "Todo")

    def test_responsibilities_map_to_four_owned_repositories(self):
        self.assertEqual(
            repository_for({"repo": "infra/lab"}), "AI-Observability-Infra"
        )
        self.assertEqual(
            repository_for({"repo": "workloads/config"}), "ai-agent-workloads"
        )
        self.assertEqual(
            repository_for({"repo": "observability-config"}), "ai-observability-config"
        )
        self.assertEqual(repository_for({"repo": "all four"}), "ai-observability-lab")

    def test_human_notes_are_preserved(self):
        task = {
            "id": "P1.1",
            "owner": "Codex",
            "depends_on": [],
            "gates": [],
            "acceptance": "Trace reaches backend",
        }
        row = {"status": "draft", "blocked_by": [], "evidence": []}
        original = managed_body(task, row)
        with_notes = original + "\n\nHuman review notes must remain."
        updated = managed_body(task, {**row, "status": "done"})
        result = merge_body(with_notes, updated)
        self.assertIn("Human review notes must remain.", result)
        self.assertIn("**Evidence status:** done", result)

    def test_unmanaged_issue_body_cannot_be_replaced(self):
        with self.assertRaises(ValueError):
            merge_body("Unrelated issue", "Generated body")

    def test_evidence_urls_are_repository_local_and_no_missing_evidence_is_invented(
        self,
    ):
        task = {
            "id": "P1.1",
            "owner": "Codex",
            "depends_on": ["P0.4"],
            "gates": ["G0"],
            "acceptance": "Validate",
        }
        row = {
            "status": "draft",
            "blocked_by": [],
            "evidence": ["ai-observability-lab/evidence/example.md"],
        }
        body = managed_body(task, row)
        self.assertIn(
            "AI-SRE-Oberveability/ai-observability-lab/blob/main/evidence/example.md",
            body,
        )
        self.assertIn("**Dependencies:** P0.4", body)
        self.assertIn(
            "No completed-step evidence", managed_body(task, {**row, "evidence": []})
        )


if __name__ == "__main__":
    unittest.main()
