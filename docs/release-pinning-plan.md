# Release pinning plan

1 November 2026, Asia/Dubai. Scope: revalidate merged main CI and begin a reviewable local release candidate. Azure deployment stays disabled; Terraform plan/apply, registry publication, GitHub releases/tags and cluster rollout are not part of this preparation.

1. Verify and merge workloads #11, observability #5 and lab #23 at their tested heads; record merge commits and preserve credentials. Completed in evidence/local-proof-main-merges.json.
2. Collect fresh CI results against the exact current main commits of all four repositories. The infra run is read-only CI with backend-disabled Terraform validation and mocked scope tests; no deployment dispatch. Restore P2.8/P2.9 only from actual passing evidence, and accept P2.3 only when clean-checkout workload tests/build are evidenced.
3. Create a source-pinned candidate manifest: exact four repository commits, tested CI receipts, pinned Docker base and monitoring images, native backend package hashes and selected runtime profile. Keep the application OCI image reference explicitly missing until a registry artifact exists.
4. Validate the manifest offline and compare pins against files at the pinned Git commits. Add checks that reject mutable refs, foreign source repositories, inconsistent known hashes and any claim that the incomplete candidate is deployable. Existing CI discovers the manifest tests; CI permissions remain unchanged.
5. Publish the candidate, validation tool/tests, HLD and tracker in a new review PR. Record P2.4 as in progress; do not fabricate an image digest or call a build-only image pullable.
6. Later: select a registry/visibility/retention approach, publish a narrowly scoped immutable workload image, verify the pulled digest/provenance and run the local container replay from the locked manifest. ACR remains gated with Azure scope; other registry publication requires its own concrete reviewed workflow. Only then can P2.4 be accepted.

The manifest's containing Git commit identifies the manifest revision. Its lab execution pin deliberately names the already tested merged lab commit that contains the proof runner; it does not recursively attempt to pin itself. Native Windows and container evidence remain separate. Multi-platform index digests must not be described as tested platform image digests without inspection.
