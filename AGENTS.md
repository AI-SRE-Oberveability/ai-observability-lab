# Lab working agreement

Read POC_PLAN.md, HLD.md, POC_TRACKER.md and docs/engineering-standards.md before work. The user requested plan review before further application implementation; The user has now explicitly accepted G0 and authorized public source review and pushes to all four repositories. Cloud spending remains separately gated.

Update the tracker after every work step with actual evidence. Every progress update states current HLD, what changed, next action and what remains. Update HLD.md when architecture changes. Do not equate artifacts, historical local tests, backend ingestion or cloud deployments.

Confirmed choices: Terraform for Azure IaC; four private repositories under personal owner `javedkumail`; user creates the new repositories; preserve GitLab credentials and settings; event-driven tracking with no scheduled job. Follow the engineering standards throughout. Never infer acceptance of a gate or repeat a scoped approval already supplied.

Use synthetic data and exact verified personal targets only. Keep secrets out of Git/chat/evidence. Managed remains the preferred compatibility profile, conditional on legitimate entitlement and supported sizing/version. Keep repository ownership boundaries and independent Git roots.

Visibility update, 28 October 2026: the user later created all four repositories as public and requested verification. Public metadata and empty contents were checked. Preserve current visibility unless asked to change it; use exact destinations from docs/repository-layout.md in the lab folder. Source review and initial push remain pending. This does not accept the implementation plan or authorize credential changes.

Approved publication step: use repository-local identity/authentication; sanitize reference-enterprise names and local machine paths from public files, preserve historical evidence labels, and keep the original handoff outside these repositories.
