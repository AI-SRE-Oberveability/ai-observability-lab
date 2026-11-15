# AI-PLATFORM-LAB structure review and proposed migration

Reviewed: 15 November 2026, Asia/Dubai. Status: **review completed; target structure is a proposal, migration has not started**.

The user supplied a local AI-PLATFORM-LAB folder as the reference for a repository redesign. It is a scaffold for seven independent repositories, with no Git metadata in the supplied copy. No remote, commit history, deployed environment or CI run can be inferred from it. The supplied files were unchanged by this review. The existing four repositories, GitLab authentication and disabled Azure deployment are preserved.

## What the reference provides

| Folder | Responsibility |
| --- | --- |
| `iac/` | Terraform resource roots, environment inputs and shared modules |
| `platform-gitops/` | Cluster/namespace configuration, Gateway API, mesh and RBAC |
| `helm/` | Platform charts, monitoring and load-test configuration |
| `gitops-argocd-templates/` | Argo CD Applications/ApplicationSets and environment release pointers |
| `pipeline-templates/` | Reusable Terraform, Node.js and Helm workflows |
| `lab-backend-nodejs/` | Synthetic gateway, catalog, request and notification services |
| `lab-frontend/` | A synthetic React/Vite application |

The parent also contains bootstrap scripts, documentation and a manual CSV checklist. It is designed as a multi-repository workspace rather than a monorepo. Separating infrastructure, chart authoring, desired deployment state and pipeline templates gives clearer ownership than our present folder layout. Those benefits do not establish that the scaffold is deployable.

The reference is a general application/mesh lab. Its README explicitly excludes APIM and Dynatrace. Our Python AI agents, Citadel/APIM governance, optional verified Azure AI reuse, read-only SRE capability and conditional Managed profile must remain explicit additions. The Node application is a useful optional synthetic system to investigate; it does not replace the AI agent implementation.

## Findings to address before reuse

1. **Deployment is not disabled by default in the reference.** `iac/.github/workflows/terraform.yml:98` enables apply on a push to main. `platform-gitops/.github/workflows/gitops.yml:42` enables a main-branch deployment that signs into Azure and obtains admin credentials at line 54. Keep our existing false deployment flag and protected execution path; do not publish these workflows unchanged.
2. **A privileged identity trusts PR execution.** `bootstrap/New-LabBootstrap.ps1:26` adds PR/main/environment subjects to one identity; lines 38-42 give it subscription-level Contributor and User Access Administrator, plus state write access. Split validation, plan and apply capabilities; PR CI must have no deployment identity. Before any future federation is created, verify the actual subject format for the exact repository and environment. GitHub's current documentation also describes immutable default subject claims for newly created, renamed or transferred repositories: [OIDC in Azure](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure).
3. **Apply is not bound to the reviewed saved plan.** The reusable Terraform workflow runs an unsaved plan at line 68, then independently runs `terraform apply -auto-approve` at line 96. Retain our reviewed plan/target/cost checks, constrain plan access and lifetime, and apply the reviewed saved plan only after the applicable authorization. Terraform distinguishes speculative plans from saved execution plans in its [plan reference](https://developer.hashicorp.com/terraform/cli/commands/plan).
4. **Change detection misses shared inputs.** The Terraform detector selects top-level resource folders from `HEAD^..HEAD`; module-only changes do not select their consuming roots. The platform detector similarly omits consumers of shared Kustomize bases. Use event-appropriate comparison bases and explicitly expand shared dependencies; do not rely on matrix concurrency to prove resource dependency ordering.
5. **Releases are mutable.** Reusable workflows use branch refs, actions use version tags, charts allow broad dependency ranges, and images use tags. Application CI edits environment values directly in its source branch. Carry forward our immutable action/source/image requirements, hash-locked Python environment and release validator. Prefer a reviewed GitOps promotion PR naming the tested image digest, chart version and source commit.
6. **The bootstrap and validation inputs are incomplete.** Three monitoring charts lack fetched upstream dependencies, and the Gateway API CRD file referenced by the cluster base is absent. Lock and verify these inputs before rendering; do not silently resolve newer releases. The registry YAML files explicitly say they are not consumed by a workflow, so they are not yet an enforced source of truth.
7. **Runtime security and telemetry need a separate acceptance pass.** Grafana enables anonymous Admin, Argo projects allow every cluster-scoped kind, the platform pipeline obtains cluster-admin credentials, and the reference Collector is traces-only. Adopt namespace/resource allowlists and our metadata-only telemetry contract; validate signals, redaction, propagation and duplication on the actual selected profile. A successful template render does not prove these properties. Argo's [cluster bootstrap guidance](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/) identifies bootstrap configuration as an administrative trust boundary.
8. **The existing evidence-backed tracker should remain authoritative.** The reference CSV has twenty manual unchecked rows and no source/evidence freshness detection. Keep our 41 stable task IDs, audit events, source hashes, shared Project mappings and decision gates. Never equate importing folders with completing those tasks. The supplied documentation also contains reference-platform labels; review provenance and remove reference-specific material before any public import.

## Proposed target, subject to the user's structure decision

Preserve the four existing GitHub repository IDs, histories, issues and remotes. Use the supplied separation to add three platform repositories. The local names below are **proposed clone aliases**, not changes already made to GitHub:

```text
AI-PLATFORM-LAB/                  workspace only; no parent .git
  ai-observability-lab/           HLD, plan, tracker, evidence, releases, local runners
  iac/                           existing infrastructure repository
  helm/                          existing observability-config repository, expanded deliberately
  ai-agent-workloads/             existing Python AI workload repository
  platform-gitops/                proposed new cluster/namespace configuration repository
  gitops-argocd-templates/         proposed new Argo desired-state repository
  pipeline-templates/             proposed new reusable CI repository
  lab-backend-nodejs/             optional separate synthetic target application
  lab-frontend/                   optional separate demonstration UI
  .runtime/                      private caches, tool binaries and raw review results
```

This is seven core repositories if selected, with two optional application repositories. It is not a decision to create or rename any repository. The parent workspace descriptor and clone/path mapping should be versioned in the lab repository. Any maintained bootstrap code belongs in a controlled repository such as `iac/bootstrap/`, rather than existing only in an unversioned parent folder.

| Current source | Proposed location/ownership | Preservation requirement |
| --- | --- | --- |
| Infrastructure `foundation/`, guard scripts and workflow | `iac/`; module/root redesign in a later isolated change | Keep the exact infrastructure remote and all fail-closed guard tests; no state move is authorized |
| Observability `local/`, compatibility profiles and telemetry contract | `helm/`, retaining `local/`, `profiles/` and contracts; add reviewed `charts/` | Preserve the proven native configuration and package/image locks; introduce no version downgrade from the scaffold |
| Python `src/ai_lab`, contracts, tests and fixtures | `ai-agent-workloads/`; service/POC reorganization only when separately mapped | Keep behavior and evidence reproducible; do not replace Python code with Node examples |
| Lab HLD/tracker/evidence/releases/scripts | `ai-observability-lab/` | Keep task/issue IDs, immutable historical manifests and raw-data exclusions |
| Cluster/namespace bases and Gateway/mesh configuration | proposed `platform-gitops/` | One writer per resource; no overlap with Terraform or Argo |
| Argo applications and environment release values | proposed `gitops-argocd-templates/` | Pin tested artifacts; narrow project permissions; no deployment during migration |
| Reusable workflow implementations | proposed `pipeline-templates/` | Callers pin reviewed commits; offline PR CI remains independent of Azure |

Keep chart templates with their owning workload or platform chart repository. Keep environment-specific deployment selections in GitOps. Prefer main plus environment directories and reviewed digest promotion; separate environment branches are an alternative that requires an explicit reason. A narrowly scoped bootstrap writer may install prerequisites before Argo owns designated resources, but two controllers must never own the same object.

The HLD runtime boundary remains Terraform-owned Azure, planned AKS workloads, APIM outside AKS, and separate runner/pod/gateway identities. Istio/Gateway API is an additional candidate inside the AKS design, not a substitute for the APIM governance boundary. Mesh selection needs a supported version, cost/complexity rationale and separate propagation/duplication tests.

## Step-by-step migration plan

| Step | Work and exit evidence | HLD/tracker update |
| --- | --- | --- |
| 1 — Review (complete) | Inventory the supplied source; static checks; identify ownership, safety and missing-input gaps | This review and sanitized check receipt; label proposal unselected |
| 2 — Select the layout | Agree exact core/optional repositories, clone aliases, visibility and names; produce file-by-file old-to-new map and an ADR | Record the actual decision and migration tasks; retain existing IDs and gates |
| 3 — Preserve the baseline | Verify current remote heads/open PRs, worktree cleanliness, Git configuration preservation hashes and tested release pins | Record immutable baseline and rollback refs; historical pins remain unchanged |
| 4 — Prepare parallel workspaces | Create review branches or isolated clones; introduce a versioned repository/path map before changing aliases | Show current versus proposed boundaries; no deletion or force push |
| 5 — Move one boundary at a time | Move owned files, fix imports, Compose paths, CI, native runner, release validation, workspace descriptors and tracker watch paths together | Preserve historical events/hashes; recapture affected evidence instead of relabelling it fresh |
| 6 — Add platform delivery | Review new platform/GitOps/template source; build all locked Helm and Kustomize variants offline; test detection and deployment guards | Mark drafts and local evidence separately; Azure flag stays false |
| 7 — Reprove and publish | Run workload/tracker/release tests, native backend proof for moved paths and relevant CI; public-source review; publish PRs | Link exact tested commits, failed attempts and remaining acceptance; request merge only for the concrete reviewed result |
| 8 — Accept the new baseline | After authorized merges and exact-main CI, prepare a new release candidate and separately verify image/container replay | Preserve the previous candidate; P2.4 remains incomplete without a verified image digest and replay |

Cloud bootstrap, account operations, RBAC/state creation, AKS/APIM deployment, registry publication and live models are outside this structure review. G2/G3/G4/G5 remain pending. No repository creation, rename, move, import, service startup or cloud action was performed.

## Observed offline validation

Source inventory: 298 files, no `.git` metadata. Source fingerprint and sanitized results are in [the review receipt](../evidence/platform-structure-review.json). Private raw command output stays in the ignored workspace runtime.

| Check | Result | Meaning/limit |
| --- | --- | --- |
| JSON parsing | 10 passed | Syntax only |
| Non-template YAML parsing | 116 passed | Does not establish workflow/schema correctness |
| JavaScript syntax | 17 passed | No dependency install, unit tests or UI build |
| PowerShell parsing | 5 passed | Scripts were parsed, never executed |
| Helm environment renders | 16 passed, 3 blocked by missing dependencies | No install; upstream wrappers not validated |
| Kustomize builds | 4 passed, 2 blocked by absent CRD bundle | Local rendering only; no API-server validation |
| Terraform formatting | Passed on identical copied `.tf`/`.tfvars` files | Direct access was denied to Terraform; the copied-source check used no backend/init/plan/apply |
| Gitleaks source scan | 0 findings | Default rules, full redaction; not a provenance or secret-history guarantee |
| Source preservation | All source hashes unchanged | No modifications to the supplied folder |

No existing POC implementation acceptance was added by these checks. Release image publication/container replay, personal Azure/cost decisions, licensed Managed evidence and governed live-model evidence remain outstanding.

A read-only check also found existing draft [lab PR #25](https://github.com/AI-SRE-Oberveability/ai-observability-lab/pull/25), titled "test: prove Linux rootless Compose telemetry". Its code, CI and evidence were not reviewed or adopted in this assessment. Reconcile that in-flight work before migrating runners, Compose paths or release acceptance. It was left untouched.
