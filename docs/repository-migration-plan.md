# Seven-repository migration plan

Finalized: 15 November 2026, Asia/Dubai. The user selected the seven-repository structure and requested this names-and-plan package first. **This package performs planning and tracking only. Repository creation, renames, folder moves and migration execution have not started.**

## Final names and ownership

All seven target repositories belong to `AI-SRE-Oberveability`, use `main`, and have matching local folder names. Retain the existing public-source model; keep the shared GitHub Project private. New repositories contain reviewed personal lab source only. The Node reference backend and frontend are deferred and do not add repositories to this scope.

| Final repository and local folder | Operation at migration | Owns |
| --- | --- | --- |
| `ai-platform-infra` | Rename `AI-Observability-Infra`, preserving repository ID 1437529000 | Terraform, state/bootstrap ownership, Azure network/AKS/registry/Key Vault, APIM resources and versioned gateway policies |
| `ai-platform-config` | Create new | Authored Kubernetes cluster/namespace configuration, scoped RBAC, Gateway/mesh configuration and bootstrap handover contract |
| `ai-platform-charts` | Rename `ai-observability-config`, preserving repository ID 1437530253 | Platform Helm charts, OTel/backend configuration, native/local profiles and telemetry/compatibility contracts |
| `ai-platform-gitops` | Create new | Argo CD Applications/ApplicationSets, allowed projects, environment values and promotion of pinned source/chart/image artifacts |
| `ai-platform-pipelines` | Create new | Reusable Python, Terraform, Helm and manifest CI; reviewed publication/deployment templates with minimal permissions |
| `ai-agent-workloads` | Keep repository ID 1437529826 and name | Python AI agents, retrieval/tools, API contracts, synthetic fixtures/evaluations, Dockerfiles and workload-owned charts |
| `ai-platform-lab` | Rename `ai-observability-lab`, preserving repository ID 1437531335 | Plan/HLD, tracker/Project coordination, sanitized evidence, release manifests, local proof orchestration and workspace mapping |

The `ai-platform-*` names replace the review's short clone aliases (`iac`, `helm`, `platform-gitops`, `gitops-argocd-templates`, `pipeline-templates`). The seven responsibility boundaries are unchanged. Matching clone and repository names removes this extra translation from the final workspace. [ADR 0002](adr-0002-seven-repositories.md) records the decision. [Repository targets](../tracking/repository-targets.json) are a planning blueprint; live tools must not consume them as a completed inventory yet.

Authenticated organization inventory found no case-insensitive collision for the six changed/new names. This is a point-in-time availability check, not a reservation. Recheck immediately before execution. Preserve original names as redirects rather than reusing them for other repositories. GitHub documents repository/issue/Git redirects and cautions that hosted action references are not redirected in its [rename guidance](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository).

## Final workspace

Prepare a parallel workspace under the existing approved Azure AI working directory:

```text
AI-PLATFORM-LAB/                  no parent Git repository
  ai-platform-infra/
  ai-platform-config/
  ai-platform-charts/
  ai-platform-gitops/
  ai-platform-pipelines/
  ai-agent-workloads/
  ai-platform-lab/
  .runtime/                      private caches, binaries and raw captures
```

Keep the current `personal-ai-observability/` workspace as the rollback/reference copy through acceptance. The supplied Downloads scaffold stays unchanged. Version the workspace descriptor and repository/path map in `ai-platform-lab`. Version maintained bootstrap source in `ai-platform-infra/bootstrap/`. Do not copy downloaded runtimes, auth configuration, state/plans, raw captures, study files or the original private handoff into public repositories.

## Runtime and delivery boundaries retained

- Terraform remains the sole Azure infrastructure owner. Custom Python agents and tools target AKS; model requests follow **agent -> APIM outside AKS -> approved Foundry/OpenAI endpoint**. Existing Azure AI reuse stays optional until verified.
- Preserve runner OIDC, AKS workload-to-gateway identity and APIM-to-model identity as separate boundaries. Governed agents receive no direct inference fallback. The SRE path stays read-only; no automatic remediation is introduced.
- Workloads own application chart templates; charts owns platform chart templates; config owns cluster manifest source. GitOps selects immutable revisions and environment values. It does not duplicate their definitions.
- Future Argo CD reconciles declared platform configuration and releases from GitOps. A narrowly scoped bootstrap job may install Argo prerequisites; record an explicit ownership handover and stop the bootstrap writer for handed-over objects. No concurrent Terraform/pipeline/Argo ownership of the same Kubernetes object.
- Start with manual Argo sync and `main` plus environment directories. Promote tested image digests and chart/source revisions through reviewed GitOps PRs. Mesh/Gateway API selection still needs supported versions and propagation/duplication evidence; the folder decision does not approve an Istio rollout.
- PR CI has no Azure deployment identity. Extract tested workflows without changing their behavior first; pin reusable workflows/actions to reviewed commits. Preserve the disabled flag, protected environments, exact-target guards and reviewed saved-plan binding.
- Existing runtime and official-icon architecture diagrams retain their current/cloud-planned meanings. Update delivery/repository views during cutover; the unchanged runtime diagrams do not claim seven live repositories.

## Ordered work and acceptance

The tracker adds P2.10-P2.16 without replacing any original task or issue ID. P2.4 release acceptance waits for the migration exit. Account-specific Azure preparation and new POC work follow repository setup; regression checks run during each migration step.

| Order / task | Concrete work | Required exit evidence |
| --- | --- | --- |
| 0 — P2.10: finalize (this package) | Fix the seven names, ownership, file map, work order, rollback and deferred cloud conditions; record the user's selected structure | Linked plan/ADR, seven unique target entries, authenticated name check, valid task dependency graph, HLD/tracker updated |
| 1 — P2.11: preserve and reconcile | Re-read all remote heads/open PRs and local worktrees. Review the Linux Compose proof in draft PR #25 alongside planning PR #26; decide their integration sequence through their existing review/merge process. Capture Git config preservation hashes, repository IDs/branches/settings, locks, CI/proof receipts and old release pins | An immutable baseline ledger with exact main and in-flight refs; no lost commit/issue, no inferred acceptance from PR descriptions; review/merge authorization recorded where needed |
| 2 — P2.12: prepare path compatibility | Create the three new empty public repositories only after the baseline is ready. Prepare isolated clones/branches in the parallel workspace. Implement and test one repository/path resolver for tracker, Project sync, native/Linux runners, Compose, workspace files, release validator and fixtures. Keep the existing four-name mode working | Verified IDs/remotes for three new repositories, clean isolated checkouts, schema-checked path mapping and positive/negative tests for both layouts; no parent Git repo or global Git changes |
| 3 — P2.13: establish content ownership | Seed reviewed cluster configuration, chart organization and Argo desired state; retain proven local Collector/Jaeger configuration and package locks. Define the config/bootstrap/Argo handover. Keep application and APIM Terraform ownership in their selected repositories. Resolve and lock missing chart/CRD inputs; do not copy unsafe reference workflows | Locked local Helm/Kustomize/schema renders for selected environments, resource-owner collision checks, telemetry contract preserved, no reference/client-specific material, no cloud/cluster execution |
| 4 — P2.14: establish seven-repo CI | Add independent offline CI to each new repository and extract existing tested CI into immutable reusable templates. Cover shared-input change detection, clean checkouts, contract tests, image build and Terraform mocked/backend-disabled safety checks. Keep deployment and registry publication disabled | Passing exact-head CI for all seven repos and meaningful deployment-disable/fork-permission tests; no PR OIDC identity or implicit apply on push; template source reviewed before callers adopt it |
| 5 — P2.15: controlled rename/cutover | Rename charts first, infra second and lab last, verifying each stable ID and all refs/settings. Update only the intended clones' GitHub origins. Land compatibility settings in the dependency order established above. Expand Project sync to the seven verified IDs/names, preserve original issue/item IDs, and update current links/workspace/diagrams | Three before/after identity receipts, four preserved histories, three verified new histories, seven linked repositories, unchanged Project privacy and accurate tasks, old/new path compatibility, Azure flag/protections preserved |
| 6 — P2.16: prove the new workspace | From clean canonical clones, rerun workload/tracker/release checks and affected native/Linux backend proofs; verify telemetry identity/privacy/graphs and owned cleanup. Reconcile PR #25's actual reviewed evidence. Revalidate exact main CI after authorized merges. Prepare a new seven-repository source candidate and current runbook | Seven exact-main CI receipts, fresh source-bound proof on the selected profiles, accurate source/evidence hashes, tested rollback/runbook, no lost original evidence. Source candidate remains non-deployable until P2.4's image/digest/replay acceptance |

Before accepting any execution task, update its watch list from this planning blueprint to the actual implementation/CI inputs and preserve its failed attempts. A placeholder evidence path or newly present folder is never completion evidence. Leave tasks unaccepted when a required tool/profile is unavailable; record the exact dependency.

## File mapping and history

[The file map](../tracking/migration-file-map.json) inventories every tracked file in the four current local source snapshots and assigns its canonical repository and unchanged relative path for the first move. It is a planning snapshot, not a verified cutover baseline; regenerate/reconcile it after the in-flight PR review. New chart/config/pipeline files are separately reviewed additions.

Keep `src/ai_lab`, contracts/tests/fixtures, infra `foundation/`, monitoring `local/`/`profiles/`/`telemetry-contract.md`, and lab evidence/tracker/release relative paths intact in the first migration. Defer package refactors, Terraform state-root changes and application behavior changes to separately scoped work. The repository resolver handles clone-name changes before any moved runner executes.

Historical events, receipts and the four-repo release candidate stay immutable. Resolve old repository names by verified stable ID/alias, or use the retained old workspace for legacy validators. New evidence uses canonical names and Git-normalized source bytes. Never mass-replace historical paths/hashes or accept Linux/Windows evidence without its actual platform and byte/version limitations.

Project-sync cutover is transactional in intent: capture current IDs -> stop sync writes during the rename window -> verify each rename and prepare all aliases -> update the live allowlist/mappings and link the verified new repos -> dry-run -> apply -> verify. Continue using the existing four-repo live mapping until that window. Planning tasks are coordinated in the existing lab repo; final ownership does not move an existing issue's identity.

Workflow references and cloud trust must be checked explicitly after rename. GitHub documents immutable subject claims for new/renamed/transferred repositories in its [OIDC reference](https://docs.github.com/en/actions/reference/security/oidc). Do not create Azure federation in this migration; verify and configure exact claims later under the cloud prerequisites. Do not reuse old repository names or assume redirects fix `uses:` references.

## Rollback and sequencing controls

Keep a baseline ledger of repository IDs, old names/remotes, exact main/in-flight refs, Project mapping and file-map revision. Do not delete the old workspace or force-push/rewrite histories. If one stage fails, stop promotion, retain its failure receipt and continue using the accepted baseline. Correct through a review branch or a documented revert; a GitHub rename-back is a separately verified operation after checking the old name is still free. Restore Project allowlists and GitHub origins from the ledger when reverting a cutover. GitLab credentials/helpers/remotes and global Git settings are never part of these operations.

Migration exit requires all seven repositories to exist with the intended ownership/visibility, relevant code/config published through review, accurate Project links and task states, clean-checkout CI and the affected local proof. It does not require deploying Azure or finishing future POC functionality.

## Azure readiness after repository setup

The user reports obtaining an Azure subscription with Owner access. Record this as **user-reported readiness, not independently verified access**. Do not query Azure or mark G2/G3 accepted from that statement. After repository setup, confirm the exact personal tenant/subscription, permitted region, budget/currency and required models; match the selected login to those targets. Then produce the costed AKS/APIM/registry/network/state plan and review its concrete Terraform scope before any deployment/spending.

The planned order is repository migration -> exact Azure target/budget confirmation and release-registry decision -> costed Terraform/APIM design and scope review -> immutable image/digest/replay acceptance before an AKS application rollout -> guarded mock AKS POC -> separately authorized live-model and Managed tests. P3.1 now depends on the repository migration exit, so confirming targets does not wait on a registry that may itself require Azure. If ACR is chosen, any registry infrastructure tranche needs its own G2/G3-covered costed scope before publication; application rollout still requires P2.4's tested digest. G4 Managed entitlement and G5 paid/live inference remain separate. **Azure deployment remains disabled throughout this planning and migration work.**
