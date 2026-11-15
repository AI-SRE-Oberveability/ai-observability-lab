# Seven-repository workspace compatibility

P2.12 prepares a parallel `AI-PLATFORM-LAB` under the approved Azure AI directory. The old `personal-ai-observability` workspace and supplied Downloads scaffold remain available. Neither parent is a Git repository. The four existing GitHub repositories retain their current names, IDs and histories until P2.15. Three new public repositories are empty: config (1458904336), gitops (1458904423) and pipelines (1458904499). Their workflow tokens are read-only, cannot approve PRs, and `AZURE_DEPLOYMENT_ENABLED=false` is explicit. Empty repositories have no CI or deployment implementation.

The versioned `tracking/workspace-layout.json` maps seven roles to canonical folders and approved legacy aliases. `AI-PLATFORM-LAB.code-workspace` opens all seven canonical sibling folders. The original four-folder descriptor remains a baseline. New clones contain source only; no credential store, CLI authentication, downloaded runtime, state or raw captures were copied.

## Checks and generated local inputs

Run from either lab folder (`ai-observability-lab` or `ai-platform-lab`):

```text
python scripts/workspace.py describe --verify
python scripts/workspace.py compose
python scripts/workspace.py editor
python scripts/validate_release.py --verify-sources
python -S -m unittest discover -s tests -v
```

`describe --verify` checks independent local Git roots and allowlisted HTTPS GitHub origins without network/authentication. Live repository IDs were checked separately in `evidence/workspace-setup.json`. Canonical folder names do not imply completed GitHub renames.

`compose` writes the unresolved-key include file to the parent `.runtime/compose.yaml`, resolving charts/workload inputs by role. Use that generated file with Compose in the canonical workspace. The historical lab `compose.yaml` remains unchanged for pinned historical source verification. A Compose config render proves paths, service definitions and loopback bindings; it does not start containers or prove backend behavior. Raw rendered config can contain a runtime key and stays private.

The native installer/proof and rootless Linux proof resolve sibling source through the same registry. Runtime output is allowed only in the workspace's private `.runtime`; symlink/junction escapes, nested worktrees, arbitrary `.git` directories/files and bare Git repositories are rejected independently of clone names. Runners verify approved source origins before executing. No new native installation or service replay is required for path acceptance.

## Tracker and Project evidence

Logical watch/evidence keys retain their historical aliases while resolving the actual folder. New tracker records use `utf8-lf-v1`: known authored UTF-8 text hashes use LF as required by `.gitattributes`; binary bytes stay unchanged. Historical records without a policy keep their original raw hashes. The explicit `port-receipts --note <reason>` operation adds a fingerprint-bound checkout-compatibility envelope only when every current legacy source/evidence byte still matches the original raw receipt. It preserves original hashes, status, dates and notes, records a portability receipt/event, and leaves changed runner proofs stale. It does not execute workloads or turn normalization into runtime evidence. Semantic source/evidence changes still invalidate acceptance.

Publish current HLD, tracker and cited evidence before live Project synchronization:

```text
python scripts/sync_github_project.py --evidence-ref <published-40-character-commit>
python scripts/sync_github_project.py --apply --evidence-ref <published-40-character-commit>
```

The preflight verifies published Git blobs against Git-normalized local files before any Project/issue writes. Managed links use the verified immutable commit. The default `main` resolves to a verified commit and fails if the working documents differ. The Project retains 48 task/issue identities, private visibility and four linked repositories until P2.15. Existing CLI authentication can be referenced with process-only PATH/GH_CONFIG_DIR; do not copy credentials or change Git helpers.

## PR #25 reconciliation and proof boundary

The Linux runner/tests and three historical sanitized receipts were forward-ported from preserved head `dde301710f21fe7d8a99f1a9e20000291f836555`. Its audit journal is retained separately as `evidence/pr25-audit-history.jsonl`. Its old 41-task state, generated views and Project mapping were not imported. PR #25 itself remains unchanged and unmerged.

R1 now uses the common private runtime containment check. R2 mocks the supported Linux/x86-64 profile for the validator-cleanup test and skips real POSIX signals on Windows. The descendant timeout regression waits for its owned fixture to become ready before timing, avoiding a false result from WSL startup latency. Linux must execute the signal and symlink cases that Windows may skip.

Current observed checks and source hashes live in `evidence/migration-path-compatibility.json`. Prior native/Linux backend receipts retain their actual dates, sources and limitations. No fresh backend ingestion, image publication, AKS deployment, Azure access or live inference is claimed. Changed runner sources require fresh supported-profile backend proof at P2.16; P2.4 still requires an immutable workload image and replay.

## Next steps and rollback

Review/merge the compatibility PR under applicable authorization, then P2.13 separates configuration, charts and GitOps source. P2.14 establishes seven independent CI results; P2.15 performs identity-preserving renames/Project cutover; P2.16 replays affected local runtime and prepares the new source baseline. Keep the old workspace and verified rollback bundles through acceptance. Terraform, AKS agents, APIM outside AKS, separate identities, safe telemetry and read-only SRE remain selected. Azure stays disabled and cloud/model/Managed gates remain pending. GitLab credentials and global Git settings are preserved.
