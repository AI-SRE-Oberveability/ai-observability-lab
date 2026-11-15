# ADR 0002: seven platform repositories with preserved AI boundaries

Date: 15 November 2026, Asia/Dubai. Status: **seven-repository direction selected by the user; names and migration sequence finalized for planning; execution pending**.

The current four public repositories provide tested Python agents, native backend evidence, CI and a non-deployable source candidate. The supplied reference separates platform concerns but omits our APIM/Managed goals and contains deployment defaults unsuitable for our disabled Azure boundary.

Use seven canonical repositories with matching clone names: `ai-platform-infra`, `ai-platform-config`, `ai-platform-charts`, `ai-platform-gitops`, `ai-platform-pipelines`, `ai-agent-workloads`, and `ai-platform-lab`. Rename three existing repositories in place, retain the workload repository, and create three additional repositories. Preserve stable repository IDs, Git histories, issues and the private shared Project. Optional Node/UI repositories are deferred.

Retain Terraform-owned Azure and APIM outside AKS; retain Python AI workloads, metadata-only telemetry and read-only SRE behavior. Separate source ownership from reconciliation: config/charts/workloads author their owned definitions, GitOps selects tested immutable artifacts, and a bounded bootstrap hands Kubernetes ownership to Argo. Use independent CI and shared templates pinned to reviewed commits.

Introduce a tested old/new path resolver before renaming or moving clones. Keep the old workspace, events, manifests and receipts intact. Final canonical names are planning targets until verified cutover; live four-repository allowlists stay unchanged during this task. No state movement, cloud identity/resource creation, deployment or registry publication is authorized by this ADR.

The user reports Azure Owner subscription access; exact target/budget verification and a costed Terraform scope remain later prerequisites. See [the migration plan](repository-migration-plan.md), [repository blueprint](../tracking/repository-targets.json) and [file map](../tracking/migration-file-map.json). The cost is additional coordination across seven repositories; the benefit is explicit ownership for cluster config, desired state and reusable delivery while preserving the existing source histories.
