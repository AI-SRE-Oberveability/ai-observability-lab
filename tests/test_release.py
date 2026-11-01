"""Reject mutable or misleading release candidates without any remote actions."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

LAB = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_release", LAB / "scripts/validate_release.py"
)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)
CANDIDATE = json.loads(
    (LAB / "releases/local-v0.1.0-source-candidate.json").read_text(encoding="utf-8")
)


class ReleaseCandidateChecks(unittest.TestCase):
    def setUp(self):
        self.manifest = copy.deepcopy(CANDIDATE)

    def test_checked_in_candidate_is_valid_but_not_deployable(self):
        result = release.validate(self.manifest)
        self.assertTrue(result["candidate_valid"])
        self.assertFalse(result["deployable"])
        self.assertTrue(result["workload_image_missing"])

    def test_missing_image_cannot_pass_deployment_readiness(self):
        with self.assertRaisesRegex(ValueError, "not deployable"):
            release.validate(self.manifest, require_deployable=True)

    def test_mutable_workload_tag_is_rejected(self):
        self.manifest["images"]["workload"]["reference"] = (
            "ghcr.io/example/policy:latest"
        )
        with self.assertRaisesRegex(ValueError, "immutable digest"):
            release.validate(self.manifest)

    def test_moving_branch_is_not_a_release_pin(self):
        self.manifest["repositories"]["workloads"]["commit"] = "main"
        with self.assertRaisesRegex(ValueError, "immutable commit"):
            release.validate(self.manifest)

    def test_unapproved_repository_owner_is_rejected(self):
        self.manifest["repositories"]["workloads"]["repository"] = (
            "someone/ai-agent-workloads"
        )
        with self.assertRaisesRegex(ValueError, "ownership mismatch"):
            release.validate(self.manifest)

    def test_source_path_cannot_escape_a_checkout(self):
        self.manifest["source_files"][0]["path"] = "../outside"
        with self.assertRaisesRegex(ValueError, "Unsafe source path"):
            release.validate(self.manifest)

    def test_changed_pinned_content_is_rejected(self):
        with (
            patch.object(release, "read_source", return_value=b"tampered"),
            self.assertRaisesRegex(ValueError, "content hash mismatch"),
        ):
            release.verify_sources(self.manifest)

    def test_another_commit_cannot_reuse_the_main_ci_receipt(self):
        self.manifest["repositories"]["workloads"]["commit"] = "1" * 40
        with self.assertRaisesRegex(ValueError, "does not cover the pinned commit"):
            release.verify_sources(self.manifest)


if __name__ == "__main__":
    unittest.main()
