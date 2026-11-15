# Migration baseline and PR #25 review

15 November 2026, Asia/Dubai. Scope: first migration work package P2.11 following the user's plan approval and explicit PR #26 merge instruction. **Baseline preservation and review are complete; repository renames/cutover and PR #25 integration have not occurred.**

## Accepted plan and preserved baseline

[PR #26](https://github.com/AI-SRE-Oberveability/ai-observability-lab/pull/26) was marked ready and merged only after its exact approved head `d9b1684a58306fb0c8c6edc015ccdf61dccd5b81` had passing CI. The merge commit is `36944db6ab12fdec949317cef4666cab1814337b`. Its main CI run [43722081314](https://github.com/AI-SRE-Oberveability/ai-observability-lab/actions/runs/43722081314) passed. [Merge receipt](../evidence/pr26-merge.json).

The preserved baseline is `20261115T141227Z`. [Its ledger](../evidence/migration-baseline.json) records original repository IDs, exact main/branch/tag refs, open PRs, issue IDs, merge/Actions/protection settings, environment branch/reviewer rules, lock/source object hashes and private rollback bundle locations/checksums. Project ID, all 48 managed issue/item IDs and the four existing repository links are captured with private visibility retained.

| Current repository | Preserved ID | Main commit |
| --- | --- | --- |
| AI-Observability-Infra | 1437529000 | 62f079f9c9a25e0c83f202931bd30bca18959a3a |
| ai-agent-workloads | 1437529826 | aff0a686b0f4a8a9cc5dec9ccfef2f3fa3d3d7cb |
| ai-observability-config | 1437530253 | ca193e79a75d7129e01ea507cf39c6e5de917b6a |
| ai-observability-lab | 1437531335 | 36944db6ab12fdec949317cef4666cab1814337b |

Each local bundle passed `git bundle verify`, restoration into a fresh mirror repository, `git fsck --full`, and comparison of the restored main ref. The lab's preserved PR #25 and PR #26 review refs were also restored and checked. The first restore attempt used a bare clone, which did not fetch custom baseline refs; that attempt was retained, and the complete mirror restore corrected the verification method. The bundles themselves were valid. No source history or workspace was deleted or overwritten.

Bundles and complete private GitHub/Project snapshots remain in the ignored workspace runtime. No credential-store contents or secret values were included in the baseline; existing GitHub authentication was used for API access. A Git bundle restores committed objects/refs, not uncommitted work or GitHub settings/secrets. The lab's expected uncommitted HLD/tracking receipts are outside the preserved merged-main source snapshot. Other source worktrees remained clean. Old manifests and receipts were not rewritten.

For a later recovery, verify the recorded bundle checksum and `git bundle verify`, restore it with `git clone --mirror <bundle> <new-empty-directory>`, then verify its main and custom `refs/migration-baselines/...` refs before choosing any recovery action. Restore current GitHub settings/remotes only through the ledger's verified repository IDs. Never replace GitLab helpers/credentials or force-push a recovery as part of verification.

## PR #25 review scope and result

Reviewed exact draft head `dde301710f21fe7d8a99f1a9e20000291f836555` of [PR #25](https://github.com/AI-SRE-Oberveability/ai-observability-lab/pull/25). Its hosted PR CI [42435384537](https://github.com/AI-SRE-Oberveability/ai-observability-lab/actions/runs/42435384537) passed. The runner's Git bytes match the historical parent-verification SHA256 `90a86804488a032fdfab938bb7ebbffa532c6625728cc5ce1912a6c0e944e9cf`.

The runner, both new test files, tracker-test delta, proof/publication receipts, runbook and overlapping HLD/tracking changes were reviewed. All **51 standard-library tests passed in Ubuntu-24.04 WSL with Python `-S`**. These are fresh unit checks, not a fresh Docker/backend proof. The recorded November 8 Docker runs remain historical branch evidence with their stated limitations. No Docker, Azure, model or registry operation was performed in this review.

Verdict: **two corrections are required before integration**. Preserve the draft branch and its original evidence. This task does not merge or rewrite PR #25.

### R1 — P2: runtime-folder rejection depends on obsolete clone names

[The path guard at lines 1022-1035](https://github.com/AI-SRE-Oberveability/ai-observability-lab/blob/dde301710f21fe7d8a99f1a9e20000291f836555/scripts/prove_linux_backend.py#L1022-L1035) permits a path whenever `.runtime` occurs in its components and the path is outside four literal clone names. On POSIX paths it accepts `/workspace/ai-observability-infra/.runtime` because only the differently capitalized `AI-Observability-Infra` is rejected. It also accepts `.runtime` nested inside every newly named `ai-platform-*` repository. That violates its stated outside-public-repositories boundary; future renames must not weaken where generated auth and raw captures are written. Existing ignore rules are an additional control, not enforcement of this path contract.

Reproduction evaluated the exact parsed guard with POSIX path semantics and made no filesystem/Docker writes. Fix it through the migration's shared workspace/path resolver: constrain the runtime location to an explicitly approved private workspace runtime, reject containment in any actual Git worktree regardless of clone name/case alias, and test all legacy/canonical names plus nested or symlinked paths. Add positive checks for the intended private runtime. Do not treat the renamed repositories as safe merely because they are absent from a list.

### R2 — P2: Linux-specific regressions break the common Windows test command

[The cleanup test's assertion at line 250](https://github.com/AI-SRE-Oberveability/ai-observability-lab/blob/dde301710f21fe7d8a99f1a9e20000291f836555/tests/test_linux_proof.py#L203-L250) expects `validator failed`, but the fixture leaves the real OS/architecture gate active. On the Windows workspace it stops earlier with `Linux x86-64 required`. That failure was reproduced with just this mocked test and a private writable temporary directory; no Docker process was invoked.

The process-group timeout test also calls POSIX `os.killpg` through the runner without a Windows skip; it was deliberately not executed on Windows. Keep host-independent validation fixtures independent by mocking the intended platform. Mark real POSIX process-group tests as Linux/POSIX-only and retain their real Ubuntu run. Re-run the common Windows suite and all Linux checks after correction so adding the Linux proof does not break the existing documented Windows tracker/test workflow.

## Reconciliation with the merged seven-repository plan

A non-working-tree `git merge-tree` check reports six conflicts against merged main: `HLD.md`, `POC_TRACKER.md`, `REMAINING.md`, `tracking/events.jsonl`, `tracking/state.json` and `tracking/status.json`. No merge or conflict resolution was applied to the source worktree.

PR #25's changed source and historical evidence are valuable, but its 41-task/Linux checkout state is not a replacement for the approved 48-task model. The integration sequence is:

1. Keep the approved seven-repo plan, task/issue/item identities, Azure readiness record and disabled gates as the coordination baseline.
2. In P2.12's isolated compatibility work, make the path/runtime resolver accept both supported layouts safely and correct the platform-specific test fixtures before consuming the Linux runner.
3. Forward-integrate the runner, meaningful regressions, source-bound receipts and runbook changes through a review branch. Preserve both event histories as audit inputs; append reconciled events rather than selecting one history wholesale. Do not copy generated tracker views or an obsolete Project mapping from the feature branch.
4. Update actual watch paths, regenerate views for the selected workspace, and preserve profile/line-ending/case limitations. The historical Linux tracker showing stale evidence and the Windows tracker showing accepted Windows-bound evidence describe different checkout conditions; neither authorizes blanket reacceptance in the new layout.
5. Obtain the applicable merge authorization for the concrete corrected integration after CI. PR #25 remains draft and unmerged here. A changed runner needs fresh source-bound proof on its supported profile during migration acceptance; 51 passing unit checks alone do not satisfy that proof.

P2.11 is accepted as **baseline preserved and review/integration sequence recorded**. This is not acceptance of PR #25, seven live repositories, source migration, immutable-registry replay, new POC functionality or cloud deployment. Next work package: P2.12, isolated canonical workspace and tested old/new path compatibility.

The target remains Python AI agents on AKS with APIM outside AKS, metadata-only telemetry and read-only SRE behavior. The user-reported Azure Owner subscription still needs exact personal target/region/budget and concrete scope checks later. Azure deployment is false; Project privacy, GitLab credentials/remotes/helpers and global Git configuration are preserved.
