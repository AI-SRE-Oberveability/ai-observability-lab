# Workspace and GitHub delivery plan

Personal GitHub owner: **javedkumail**. On 28 October 2026 the user reported creation with public visibility. Read-only GitHub API checks verified all four repositories are **public and empty**. This replaces the initial private-visibility recommendation as the recorded actual state. Terraform remains the confirmed Azure IaC choice. Source review and initial pushes are pending.

```text
Azure AI/                          Existing project and study material
  personal-ai-observability/        Parent workspace; no Git repository here
    AGENTS.md                      Working agreement, plan-first and HLD updates
    README.md
    personal-ai-observability.code-workspace
    project-brief.original.txt      Preserved original; outside repository publication
    .runtime/                      Ignored local binaries/cache/temporary files
    ai-observability-lab/           Plan, HLD, tracker, coordination, evidence
    ai-agent-workloads/             Three POCs, application contracts/code/tests/images
    ai-observability-config/        Shared telemetry/backends/monitoring profiles
    ai-observability-infra/         Azure/state/identity/budget/IaC ownership
```

| Verified public repository | Source folder | Publication state |
| --- | --- | --- |
| javedkumail/ai-observability-lab | ai-observability-lab | Public, empty; no push |
| javedkumail/ai-agent-workloads | ai-agent-workloads | Public, empty; no push |
| javedkumail/ai-observability-config | ai-observability-config | Public, empty; no push |
| javedkumail/AI-Observability-Infra | ai-observability-infra | Public, empty; no push |

The repositories now exist and contain no files. Each source folder supplies its own README and ignore rules. Keep repository initialization, source review/secret checks and first push as a separate delivery step. Preserve the exact infrastructure repository capitalization in the remote mapping. Recheck remote contents before pushing; if content appears, preserve it and do not force push.

All authored POC source, configuration and documentation belong in the corresponding repository. Installed dependencies, caches, downloaded binaries, secrets, raw test logs with sensitive content and the original handoff are not source to publish. The lab's sanitized evidence is versioned where appropriate. The current workflow draft stays inactive until its inputs and execution are validated.

## Preserve GitLab and support GitHub alongside it

No credential deletion, sign-out, `credential reject`, global helper rewrite, global URL rewrite or GitLab remote replacement is required. Existing GitLab credentials and unrelated repositories remain intact. The current personal lab parent has no Git metadata or remote.

Use a GitHub remote for each new personal repository and repository-local settings for commit identity or any required authentication choice. If the user later wants a GitLab mirror, add a distinct remote named `gitlab` using their supplied URL; push to each destination deliberately. Do not turn on automatic push-to-all behavior.

Windows Git is the default when its authorized GitHub identity is available. WSL is an optional isolated Git environment if the user prefers it or already has the correct personal GitHub authentication there. It is not needed to remove or replace Windows credentials. Check its availability and authenticate securely in that environment before selecting it; do not copy secret files between environments.

GitHub integration discovery reports the tagged plugin installed/enabled, but no GitHub repository tools were exposed for this check. Public metadata/contents were verified through unauthenticated API reads. Authenticated write capability remains unverified. See `../evidence/github-repository-verification-20261028.md` for the evidence. No push is claimed from a public read.
