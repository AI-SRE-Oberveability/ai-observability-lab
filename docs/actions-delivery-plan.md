# GitHub Actions delivery plan

Date: 29 October 2026, Asia/Dubai. Authorized by the user's request to configure Actions across all four repositories, starting with CI and Terraform deployment workflows. This authorizes workflow implementation/publication; the existing personal-Azure target and spending gates remain pending.

## Scope and sequence

| Step | Deliverable | Validation / exit |
| --- | --- | --- |
| 1 | Record this plan, HLD boundary and two new coordination tasks | Task dependency model validates; existing acceptance gates preserved |
| 2 | Activate independent CI for all four repositories | Workloads: locked dependencies, lint/tests/contracts, container build. Observability: Compose and pinned Collector validation. Lab: tracker/sync tests and lint. Infra: Terraform format/init/validate and deployment-guard tests |
| 3 | Prepare minimal Terraform foundation and manual plan/apply workflow | Real provider lock; no cloud calls for PR CI. Cloud workflow refuses missing configuration, wrong branch, disabled deployment or an unreviewed plan fingerprint |
| 4 | Configure protected GitHub deployment environments and publish reviewed changes through PRs | Plan/apply identities remain separate; apply requires owner review; branch restricted to main. No Azure identity or role is created during this task |
| 5 | Verify GitHub execution and publish evidence | All four main-branch CI runs succeed; workflow syntax checked; deployment dispatch fails safely before Azure login while unconfigured |

Update HLD, local tracker and shared Project after each coherent step. Use task P2.8 for this four-repository CI baseline and P2.9 for guarded Terraform delivery. These tasks do not complete P1 backend proof, P2.3 end-to-end release acceptance, or P3 cloud deployment. The user's latest instruction advances CI preparation ahead of those later exits.

## Delivery HLD

PR/push -> read-only CI -> reviewed merge. Manual dispatch on main -> explicit deployment-enabled check and complete personal configuration -> environment-specific OIDC -> private Azure Blob state -> Terraform plan. Apply requires a protected environment review and the fingerprint from a previously reviewed plan; a fresh plan must match before the saved plan is applied.

The first Terraform root manages only one tagged lab resource group. It supplies a concrete, testable workflow foundation without selecting AKS, networking, paid services or Managed sizing before the costed design. Bootstrap/state storage and Azure federation remain prerequisites owned by infra. Later platform modules will follow the separate Azure design and spending decisions.

Plan/state files stay on ephemeral runners and are never uploaded as public artifacts. The workflow publishes action counts, source commit and a deterministic plan fingerprint without resource attribute values. Apply re-plans at the same source version, checks the fingerprint and applies that exact saved plan in one job. Drift or source changes require a newly reviewed plan. No automatic push/PR apply or destroy workflow is introduced.

## Repository contracts

- All external actions use verified full commit SHAs; ordinary CI has contents:read, bounded job time and cancelable PR concurrency. Checkout does not persist credentials. Fork PRs receive no cloud identity.
- Each repository can validate its own checkout. The lab tracker CI uses temporary synthetic workspace fixtures; it does not claim sibling checkout freshness or contact GitHub/Azure.
- The workload CI builds the existing synthetic container without publishing an image. Registry delivery, image-digest rollout and Kubernetes/Helm deployment remain P2.4/P3 work.
- Terraform CI uses backend-disabled initialization and provider validation. It does not log in to Azure or run a cloud plan. Deployment uses manual dispatch and separate protected environments.
- GitHub Project updates remain event driven through the existing approved local sync. No Project token is placed in a workflow or repository secret.
- Preserve GitLab credentials/remotes and global Git configuration. Existing repository-local GitHub destinations remain unchanged.

## Prerequisites before Azure execution

Exact personal tenant/subscription, region, bounded resource-group name and budget; G2/G3 decisions; protected state storage/container/key; separate plan/apply Entra identities with scoped RBAC; verified actual GitHub OIDC subject/issuer/audience; owner review of concrete resource scope. Do not derive personal authorization from cached Azure accounts.

Set deployment-enabled configuration only after these are confirmed. Missing values are reported by name without printing credentials. No cloud workflow will be dispatched for real provisioning during this setup.

## Evidence and limitations

Record source commits, local checks, GitHub run URLs/conclusions, environment protections and the disabled-cloud guard result. Docker is currently unavailable on this Windows host; the workload container build and Linux Collector validation must be proved on GitHub-hosted CI. A green CI run does not establish backend ingestion, live-model usage, Managed compatibility or deployed Azure resources.

References: [GitHub secure action use](https://docs.github.com/en/actions/reference/security/secure-use), [AzureRM backend authentication](https://developer.hashicorp.com/terraform/language/backend/azurerm), [GitHub OIDC concepts](https://docs.github.com/en/actions/concepts/security/openid-connect).
