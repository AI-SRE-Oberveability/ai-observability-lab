# Lab working agreement

Read POC_PLAN.md, HLD.md, POC_TRACKER.md and docs/engineering-standards.md before work. The user approved the plan and source publication. Current owner is organization AI-SRE-Oberveability; personal administrator javedkumail is its verified active owner. The current four public repositories retain their IDs/history. The user selected a seven-repository target; final names and ordered migration are in docs/repository-migration-plan.md and tracking/repository-targets.json. The task model has 48 tasks; the private shared Project retains the current four live repository links until verified cutover. This names/plan task does not execute migration.

Update HLD and the tracker after each work step with actual evidence. Every progress update states current HLD, what changed, next action and remaining work. Distinguish draft files, local tests, backend ingestion, CI execution and cloud deployment.

After recording each local work step, run `scripts/sync_github_project.py --apply` from this repository (or the corresponding parent-relative path) to update the approved shared Project and managed issues. Its default invocation is a safe local dry-run. Keep tracking/github-project.json, HLD.md and the generated POC tracker current; record authentication/sync failures explicitly. The user approved the additional GitHub Project scope. Never change GitLab credentials or global Git helpers for this sync.

Terraform owns Azure infrastructure. Workloads, shared observability and lab coordination retain separate repository ownership. Preserve GitLab credentials/helpers/remotes and global Git settings; use the existing GitHub credential and repository-local settings. Never expose tokens or contact email in source/evidence.

Use only synthetic data and exact verified personal cloud targets. Cloud spending and live-model usage remain separately gated. Managed remains the preferred compatibility profile, conditional on entitlement and supported sizing/version. Updates are event driven after work steps; no scheduled job exists.

Keep Python AI agents and APIM outside AKS in the selected design. The user reports Azure Owner subscription access; exact targets, region and budget remain unverified, with G2/G3/G4/G5 pending. Finish repository setup before new POC execution. Plan compatibility before clone/remote renames; preserve original evidence and in-flight PR #25.
