# Local workload review and backend proof plan

1 November 2026, Asia/Dubai. Scope: deterministic synthetic local services only; Azure remains disabled. PR #21 was merged at the reviewed CI-passing head. Existing GitHub credentials are reused; GitLab/global Git configuration is preserved.

1. Review application/contracts, locked dependencies and known deprecation; classify actual gaps and run the current baseline. Record P1.1 before corrections.
2. Validate request/response examples, authentication, typed outcomes and bounds. Correct only demonstrated local acceptance gaps; keep a real model and APIM outside this phase.
3. Select a working local runner. Prefer existing Compose if available; otherwise use verified pinned Windows Collector/Jaeger binaries with explicit loopback-only configuration. Refuse occupied ports and manage only child processes started by the runner.
4. Exercise healthy and bounded fault requests across separate HTTP agent/retrieval listeners. Export OTLP through the real Collector, retrieve the trace from Jaeger and compare the seven-span graph and two service/version identities.
5. Inspect the actual exported trace/metrics surfaces and controlled operational logs for synthetic canaries, key leakage, event/baggage content and high-cardinality labels. State the exact capture surfaces checked and unknowns.
6. Stop all owned services, verify ports are released, restart the runner and demonstrate ephemeral trace retention. Keep raw process logs and generated runtime settings outside public repositories.
7. Record sanitized machine-readable evidence and source versions, update HLD/tracker/Project after each coherent step, publish review PRs and collect CI conclusions. New PRs remain open until separately authorized to merge.

Acceptance claims remain separate: a passing in-memory test is not backend ingestion; HTTP 200 is not a successful domain outcome; file presence is not a live control. Existing architecture, cloud/live-model/Managed gates and resource ownership remain intact.
