# P2.13 configuration, charts and GitOps ownership plan

Prepared: 15 November 2026, Asia/Dubai. Status: **planning package for review; P2.13 remains in progress**. PR #35 is merged at `28fb2bfc8285f037843100f4a2f4bc2d533b04f8`, and exact-main CI passed. This package inventories the source and defines implementation order before adding platform manifests. It does not seed the empty repositories, fetch dependencies, install a controller or deploy anything.

The machine-readable companion is [platform-ownership-plan.json](../tracking/platform-ownership-plan.json). Its paths and resource families describe planned work; they are not an enforced inventory or completed render result. Current repository IDs/aliases remain in `tracking/workspace-layout.json`. Keep all 48 task/issue identities, four existing GitHub names and the private Project's four links through P2.15.

## Starting point and retained boundaries

- Seven canonical clones exist. Config, GitOps and pipelines are empty; infra, charts, Python workloads and lab preserve their original histories. No parent Git repository is introduced. The old workspace and Downloads scaffold remain preserved.
- Charts currently has 15 tracked files, including `local/`, `profiles/` and `telemetry-contract.md`. Retain their paths and Git-normalized contents initially. Preserve Collector 0.164.0 and Jaeger 2.22.0's recorded image digests and Windows package checksums; do not replace them with reference defaults. New Kubernetes profile behavior requires separate proof.
- The 298-file reference scaffold still matches the reviewed bytes. Its missing upstream dependencies/Gateway CRD and unsafe workflow/security defaults are historical findings, not adopted configuration. Do not import its customer-like names, Node/UI applications, anonymous administration, broad AppProjects, cluster-admin pipeline or automatic apply.
- Runtime stays **Python agents on AKS -> APIM outside AKS -> approved model endpoints**. Terraform owns Azure/APIM; runner, pod-to-gateway and gateway-to-model identities remain separate. SRE stays read-only and telemetry metadata-only. Existing Azure AI reuse remains optional and unverified.
- Azure remains disabled, G2/G3/G4/G5 remain pending, and registry/live-model publication is outside this work. GitLab credentials/helpers/remotes and global Git settings are preserved.

## One author and one active spec writer

Source ownership and deployment authority are different. GitOps selects source revisions; it does not become the author of every template. The proposed steady-state spec writer for Kubernetes resources is Argo after an explicit handover. Kubernetes controllers may maintain their normal status fields; this does not authorize a second desired-spec writer.

| Repository role / canonical folder | Authored source and planned roots | Boundary |
| --- | --- | --- |
| Infra / `ai-platform-infra` | Existing `foundation/`; future `bootstrap/` orchestration and handover guard | Sole Azure/APIM Terraform owner. Bootstrap consumes pinned Kubernetes source; it does not maintain copied templates or Terraform Kubernetes resources for Argo-owned objects. |
| Config / `ai-platform-config` | `namespaces/`, `policies/`, `rbac/`, `vendor/`, `environments/dev/`, `environments/qa/` | Namespace objects, foundation RBAC/policy and selected CRDs. Never duplicate namespaces/CRDs in chart templates. Gateway/mesh files need a separately selected supported profile. |
| Charts / `ai-platform-charts` | Existing `local/`, `profiles/`, contract; new `charts/otel-collector/`, `charts/jaeger/`, reviewed `charts/argocd/` | Generic platform/control-plane templates and safe defaults. Dependencies belong in chart locks; environment choices belong in GitOps. The current GitHub URL remains `ai-observability-config` until cutover. |
| Workloads / `ai-agent-workloads` | Existing Python source/contracts/fixtures; new `charts/ai-lab/` | Agent/retrieval deployments, services and application service accounts. Config may bind to their documented names but must not create the same accounts. No agent behavior refactor in this migration. |
| GitOps / `ai-platform-gitops` | `projects/`, `applications/`, `environments/dev/`, `environments/qa/`, `bootstrap/` seed declarations | AppProjects/Applications, environment values and immutable release selections. It references authored source rather than copying templates. Start with explicit Applications; add ApplicationSets only when repetition justifies them. |
| Pipelines / `ai-platform-pipelines` | Reusable validation/publication templates in P2.14 | Validation and guarded delivery tooling, never a concurrent writer for objects handed to Argo. Remains empty in this planning step. |
| Lab / `ai-platform-lab` | HLD/plan/tracker/evidence, render matrix, cross-repo acceptance and release coordination | Owns the ownership ledger and combined checks, not sibling resource definitions. Preserve historical receipts and release candidates. |

Use the current verified GitHub destinations in reviewed source until P2.15 renames them. A canonical local folder does not establish a renamed remote.

## Proposed first slice and folders

Build a small source-only slice: namespace/policy/RBAC foundations; Collector and ephemeral Jaeger charts; the existing Python agent/retrieval chart; and pinned Argo control-plane/desired-state definitions. `dev` comes first; `qa` is an offline overlay/parity case, not approval for a second AKS cluster. Use synthetic namespace names such as `ai-lab-dev`, `ai-lab-qa` and `ai-observability`; actual Azure/cluster targets stay unset.

Keep application namespaces in config and their Deployments/Services/ServiceAccounts in the owning charts. Default services to internal access in the proposed AKS profile. Specify resource limits, probes, volumes and supported non-root identities in the render contract; rootless Docker UID mapping is not proof of AKS pod-security compatibility. Secret values stay outside Git; only references can be planned before secure delivery is selected.

Grafana/Prometheus wrappers, RabbitMQ, Kiali, k6, Node/UI applications and a mesh/Gateway rollout are outside the proposed first slice. This avoids adopting the reference's unlocked dependencies without an experiment. If any is selected during plan review, add its exact versions, CRDs, ownership and checks before implementation acceptance. APIM remains outside AKS regardless of a later in-cluster gateway choice.

## Ordered work packages

These are P2.13 substeps, not new Project task IDs. Each implementation step records changed source, actual checks, HLD/current/next/remaining and a published evidence ref before Project sync.

| Order | Concrete work | Required evidence / exit |
| --- | --- | --- |
| 1. Preserve and inventory — performed in this planning package | Verify the merged compatibility baseline, current repo IDs/heads, empty additions, reference fingerprint and retained profile hashes | `pr35-merge.json`, `platform-ownership-start.json`, `platform-ownership-inventory.json`; no manifest or dependency adoption |
| 2. Review ownership and scope — this package | Agree this table, first slice, folders, resource identities, active-writer states, pin sequence and negative cases | Published plan/JSON and a coherent task graph; keep P2.13 in progress |
| 3. Select and lock inputs | Choose a compatible Kubernetes API/schema, Helm/Kustomize and Argo release/chart/CRD matrix; freeze upstream URLs, exact versions, archive/CRD SHA256 and licences | Real checked inputs, version coherence, `Chart.lock` for dependencies plus archive checksums. No broad ranges or implicit updates; no install/login. Missing inputs fail validation. |
| 4. Establish config source | Seed README/ignore rules and namespace/policy/RBAC bases, dev/qa overlays, selected vendored CRDs/provenance | Offline Kustomize builds and schema validation; unique identities; explicit RBAC/resource scope; no duplicate chart-owned service accounts |
| 5. Establish chart source | Add minimal platform charts and workload-owned application chart; preserve existing local/native profiles; render supported settings | Helm lint/schema/template results for dev/qa, exact image pins, safety checks, unchanged retained profile hashes and API/telemetry contracts. Dependency archives reproduce from locks. |
| 6. Establish GitOps and bootstrap contract | Create narrow AppProjects, explicit manual Applications, immutable chart/source/value selections, and a bootstrap-to-Argo ownership ledger | Correct source paths/commits, restricted destinations/kinds, no duplicate templates, fail-closed handover model and rollback fixtures. No live sync or bootstrap execution. |
| 7. Validate the combined source | Join config, platform charts, application chart and GitOps selections for each logical environment; exercise positive and negative cases below | Machine-readable render/ownership/pin results tied to exact source commits. Unknown scope/schema and unresolved references fail. Passing templates do not prove a running backend. |
| 8. Review and publish | Public-source/secret review, independent repository PRs, exact-head relevant checks and documented dependencies; merge only with applicable authorization | P2.13 acceptance receipt only after required source/locks/renders pass; then P2.14 seven-repo CI. Renames/Project cutover remain P2.15; fresh runtime and seven exact-main receipts remain P2.16. |

No versions are selected solely because a client is installed or a documentation URL says stable. Observed local versions are inventory only. Check the chosen Argo renderer/tool matrix before pinning; an unplanned Helm major upgrade is not part of migration.

## Immutable inputs and publication order

Config owns reviewed vendored CRDs plus a source/version/checksum/licence manifest. Charts own `Chart.yaml`, real dependency locks and archive integrity records; thin charts without dependencies do not need a fabricated lock. GitOps release records bind exact config/chart/workload/value commits and existing image digests to an environment. Lab records the cross-repo render matrix and the selected GitOps catalog revision.

Stage actual source publication in dependency order: config commit C -> platform/workload chart commits H/W -> values commit V -> Applications/catalog commit G referring to C/H/W/V. Use existing stable public repo IDs/names and immutable 40-character Git commits; image references require `sha256` digests. A future root bootstrap consumes the selected catalog G from the lab release record. No object must contain its own future commit hash. Land values first, then promote their already-published revision; do not invent zeros or substitute `main`/`latest` as a deployable pin. P2.16 prepares the new seven-repo source candidate; P2.4 still owns workload image publication/immutable replay.

Helm dependencies must have a reviewed lock before reconstruction. The official [Helm dependency-build documentation](https://helm.sh/docs/v3/helm/helm_dependency_build/) explains that a missing lock can cause update-like behavior; validation must reject that condition before invoking it. Chart lock metadata is not a substitute for verifying downloaded archive bytes.

## Bootstrap handover and rollback contract

Argo renders Helm templates and manages their lifecycle; it is not a second Helm release manager ([Argo Helm documentation](https://argo-cd.readthedocs.io/en/stable/user-guide/helm/)). The future bootstrap must consume the exact config/chart/GitOps inputs, rather than run a separate maintained template copy or leave a Helm/Terraform writer behind.

1. **PREPARED:** ledger names each logical cluster/group/kind/namespace/name, source repo/path/commit, provisional writer, intended steady writer and prerequisite. P2.13 tests this state with synthetic fixtures only.
2. **BOOTSTRAP_ONLY — future gated execution:** the narrow installer writes only enumerated Argo prerequisites/seed objects. Applications have no automated sync/prune/self-heal. No app reconciliation is started by the migration.
3. **FROZEN:** stop the bootstrap job and revoke/disable its write path; record object UIDs, source/render hashes and readiness. Only after this receipt can manual Argo adoption begin. CRDs must be established and controllers ready before dependent resources; ordering annotations alone do not prove that.
4. **ARGO_ONLY:** verify the adopted objects and exact desired inputs, then persist the handover receipt. Argo becomes the sole desired-spec writer for handed-over resources; pipelines only validate or propose GitOps changes. There is no background bootstrap reconciler.
5. **Rollback:** pause the affected Argo reconciliation and verify it is stopped before any bootstrap writer resumes. Select one owner in the ledger, retain failed receipts, and restore the reviewed input revision through a PR. Never use delete-all/prune as a migration rollback.

CRDs and namespaces have one config author. If a selected chart also contains CRDs, explicitly disable that chart emission and verify the rendered result; Argo supports `skipCrds` for Helm's CRD directory, which is not proof that a chart has no templated CRD elsewhere. Argo control-plane/seed configuration is an administrative boundary and needs protected review; ordinary workload projects cannot deploy to `argocd`. See [Argo bootstrapping guidance](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/).

The handover above is a future execution contract. P2.13 accepts its offline model/negative cases, not a live adoption receipt. No Azure identity, Kubernetes access or controller is created to exercise it in this phase.

## Combined validation and negative cases

The planned validator consumes exact rendered objects and declared destinations. Its resource key is **logical cluster + API group + kind + effective namespace + name**; API versions do not create different owners. Resolve omitted namespaces through the Application destination using locked schema/scope metadata. Reject unknown scope rather than guessing. Report the source path/revision for each object and reject repeated keys across owners/applications. Do not rely on Argo's last-source precedence for duplicates ([multiple-source behavior](https://argo-cd.readthedocs.io/en/stable/user-guide/multiple_sources/)).

| Check | Positive case | Required failing case |
| --- | --- | --- |
| Ownership | Namespace/CRDs in config; workload/platform resources in their own chart; GitOps references them | Duplicate Namespace, ServiceAccount, CRD or Deployment; same object under a different API version |
| Scope and projects | Explicit source URLs, environment namespaces and allowed kinds; separate privileged platform project | Wildcard source/destination/kind, unapproved repository/path, workload access to Argo namespace or cluster-admin binding |
| Immutable inputs | Real published source/value commits, image digests and verified locks/checksums | Missing/zero/nonexistent commit, branch/tag-only rollout pin, tag-only image, missing lock/CRD/archive or changed archive bytes |
| Template and contract | Dev/qa Helm/Kustomize/schema renders preserve names, limits, auth references, safe telemetry and read-only tool boundary | Unresolved values, missing file silently ignored, inline credentials, public listener/anonymous admin, prohibited telemetry field or direct-model fallback |
| Handover | PREPARED -> BOOTSTRAP_ONLY -> FROZEN -> ARGO_ONLY with one writer | Concurrent bootstrap/Argo writer, adoption before freeze, missing UID/readiness receipt, rollback before stopping the current writer |
| Preserve baseline | Existing local/native profiles, package/image locks, Python contracts and historical receipts unchanged | Source move/downgrade, rewritten historical receipt, copying old 41-task state, unplanned repository rename or changed GitLab/global Git settings |

Use dedicated AppProjects with explicit permissions instead of the permissive default ([Argo project guidance](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/)). Where sync waves are used, validate their purpose within a sync and use explicit manual readiness gates between Applications; they are not a blanket cross-Application dependency proof ([sync-wave behavior](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/)). No new API-server, pod-security or backend acceptance is inferred from offline schema checks.

## Updates, acceptance and remaining work

After each implementation substep: update HLD -> record actual evidence/source hashes -> refresh generated tracker -> publish reviewed files -> sync the private Project using the immutable published evidence commit -> retain sync receipts. Failed attempts remain visible. Update P2.13 watch paths to the actual manifests/charts/locks/checks before accepting it; keep the 48-task model and pending gates intact.

This planning package finishes the inventory and proposed work breakdown only. `evidence/migration-platform-validation.json` must not be created as a placeholder success: it belongs to actual P2.13 source/renders/handover validation. Three new repositories remain empty, and P2.13 stays **in progress**. Next is plan review followed by input locking and the first config source PR. Azure remains disabled; GitLab credentials/global Git configuration and original histories remain intact.
