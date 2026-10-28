# Engineering standards and definition of done

User decisions on 28 October 2026: plan before implementation; HLD/current/next/remaining updates; tracking after each step; four GitHub repositories under `javedkumail` (subsequently created public by the user); preserve GitLab credentials; **Terraform for Azure IaC**; apply best practices throughout.

These are acceptance requirements for implementation and review, not claims that the existing drafts already satisfy them. Keep the POC small and record a justified, accepted trade-off whenever a practice is not appropriate for the selected lab scope. Do not add enterprise components without a concrete experiment.

## Terraform and Azure

- Infra is the single owner of Azure resources. Use small modules with explicit typed inputs/outputs and separate root states for bootstrap, platform and optional Managed. Avoid coupling unrelated component state.
- Pin a tested Terraform version and provider constraints; generate and commit `.terraform.lock.hcl` from real initialization. Include runner-platform checksums. Pin external module versions separately: provider locks do not lock remote module versions.
- Run `terraform fmt -check -recursive`, initialize the required providers and run `terraform validate`; add TFLint/security/policy checks relevant to the selected resources. Test important module behavior and deployment guarantees rather than mirroring expressions.
- Review a concrete plan against exact personal targets, allowed resources and cost before apply. Protect any saved plan as sensitive; never publish unredacted plans, state or secret tfvars as general CI artifacts.
- Use protected Azure Blob remote state with locking, encryption, least-privilege data access and documented recovery/bootstrap ownership. Choose supported Entra/OIDC authentication and reachable networking; avoid long-lived access keys/client secrets by default.
- Use explicit subscription/tenant binding, scoped roles, workload identity/Key Vault or equivalent supported secret delivery, owner/environment/project/expiry tags and dedicated lab groups. No credential values in Git or shell logs.
- Serialize apply/destroy for each environment. Document import/drift/upgrade and teardown behavior. Retain state/evidence according to an explicit decision. Validate idle costs and cleanup against actual resource IDs.

These choices follow the [Terraform style guide](https://developer.hashicorp.com/terraform/language/style), [provider dependency lock guidance](https://developer.hashicorp.com/terraform/language/files/dependency-lock) and [Azure backend documentation](https://developer.hashicorp.com/terraform/language/backend/azurerm). Recheck selected release/provider behavior at implementation time.

## Repositories and delivery

- Four independent repositories with README, ignore rules and one owner per resource. Each POC has identifiable code, contracts, fixtures and evidence. The parent workspace is not a nested-repository Git root.
- Preserve GitLab credentials/helpers/remotes. Use separate GitHub destinations and repository-local identity/settings; WSL is optional. Verify the personal identity and exact remote before writing.
- Review source and secret exclusions before initial push. Version authored source/configuration/docs; exclude credentials, virtual environments, downloaded binaries, state/plans and customer material. Use branches/PRs and available review controls after bootstrap; do not rely on unavailable GitHub-plan features.
- Lock dependencies, pin action references, minimize workflow permissions, restrict deployment identities to authorized environments and keep untrusted fork code away from them. CI must build/test a clean checkout; images deploy by immutable digest.
- A workflow draft remains inactive until its inputs are complete. A local pass is not a GitHub Actions pass. Release manifests pin the tested combination of repositories and images.

## Application, AI and observability

- Agree contracts before behavior changes. Validate auth/input/output; keep errors bounded and sanitized. Enforce time, step, tool-call, retry and response-size limits. A real provider additionally needs tested actual token-budget behavior.
- Use versioned synthetic fixtures and expected-answer/incident datasets. Separate transport success, answer quality and operational outcomes. Treat retrieved content as data; the SRE path gets allowlisted read-only capabilities only.
- Keep secret/personal content out of telemetry by default. Check exported signals, fixed service/version/environment identity, W3C propagation and expected graph edges. Avoid high-cardinality metric labels, duplicate instrumentation and unbounded telemetry buffering.
- Choose instrumentation and GenAI schema versions explicitly. Validate each signal/backend separately. Do not use local or SaaS results to claim licensed Managed compatibility.

## Required evidence before a task is done

1. The planned outcome and acceptance criteria are met for the stated scope.
2. Relevant lint, contract, behavior, security/secret and deployment checks pass; their actual results are recorded.
3. Evidence states source version/hash, environment/profile, model mode, test/load conditions, observed outcome and limitations.
4. HLD/ADRs, runbooks and resource ownership reflect the change; failures or deviations remain visible.
5. The tracker records the work and refreshes next/remaining steps. Source changes invalidate prior proof for watched files.
6. Source is pushed to the confirmed personal GitHub repository when that repository and authorization are available. A local file or commit is not a remote push; record the remote commit separately.

If a requirement is blocked, record the blocker and the next dependency. Do not fabricate passing results, quietly waive criteria or treat a decision as accepted without the user's applicable instruction.
