# Linux Docker Compose and historical Windows proof

## Ubuntu Linux x86-64 rootless Compose

Run from the lab repository with Python 3.12. The runner itself and its unit tests use only the standard library; Docker and Compose must already be installed and the existing `rootless` context must be accessible. It refuses a rootful daemon, unsupported memory/CPU quotas, an unsafe runtime location or occupied host ports. It does not install or reconfigure Docker.

```bash
# Use the existing hash-locked Python 3.12 environment in this workspace:
../.runtime/linux-proof/venv/bin/python -m unittest discover -s tests -v
../.runtime/linux-proof/venv/bin/python scripts/prove_linux_backend.py
```

The default runtime root is `../.runtime/linux-proof` and must have mode 0700. A separate private root can be selected with `--runtime-root ../.runtime/linux-proof/review-runs`; it must be outside every public clone beneath `.runtime`. Each invocation creates a private unique directory with command stdout/stderr, command exit/timeout receipts and `result.json`. The stdout summary prints only status, owned run ID and cleanup status. Preserve failed directories; do not publish raw rendered Compose, auth, logs, paths or captures. SIGKILL/host failure can bypass finally cleanup: use only the failed receipt's exact owned `ai-proof-<run-id>` project and private Compose file for recovery, never prune or stop other projects.

The runner renders the existing lab Compose includes privately, keeps immutable base/backend pins and hash-locked workload dependencies, builds a uniquely tagged **local** workload image, validates the real Collector and starts owned containers. All published endpoints bind 127.0.0.1: agent 18080, Jaeger query 16686, application metrics 18889 and Collector internal metrics 18888. Retrieval and OTLP remain on the private container network; their listeners must remain reachable there. No host OTLP or retrieval port is published.

The proof-only Collector config reuses the shared processors and appends trace/metric file exporters with 5 MiB rotation and one backup. Private bind files/directories are 0600/0700. Collector and Jaeger explicitly use container UID/GID 0:0 **inside the required rootless user namespace**, mapping to the invoking host user, so private bind files work without chmod 777. Workloads retain UID/GID 10001:10001. Every container retains CPU/memory/log limits, dropped capabilities, no-new-privileges and a read-only rootfs; temporary files use tmpfs. The runner inspects the actual limits/bindings/image IDs before accepting traffic. Backend safety/config generation is proof-only orchestration; Terraform and shared configuration ownership stay separate.

Implemented acceptance checks require cited deterministic healthy and external W3C requests, null usage, and a retrieval 503 -> typed tool_error with exactly two attempts under 2.5 seconds. Each cohort is queried from Jaeger and must have exactly seven spans with expected names/multiplicity/parent IDs/service/version/environment/schema identity; failed client/server/agent spans must have typed error status. Collector JSONL resource/span/metric allowlists, status text, events/links and explicit submitted-question, baggage, transient-key, document-text and generated-answer canaries are checked. Queried traces, Prometheus/internal metrics and container stdout/stderr are also scanned. No log exporter or controlled operational log handler is configured in this container profile; stdout/stderr checks do not prove log-pipeline delivery or universal PII prevention.

Readiness, HTTP, commands, stop/down and cleanup are bounded. Cleanup in finally removes only the owned project's containers/network/volumes; local built images and private receipts remain for review. Jaeger memory is capped at 1000 traces and the runner restarts it to test prior trace absence. This is a small synthetic cohort, not sustained-load/P6 acceptance, production readiness, Managed parity, paid inference or immutable-registry replay.

**Historical pre-review 8 November boundary:** run `d3f35910e0074a6db6423c6eac0daf95` passed real healthy/fault/external-W3C seven-span Jaeger graphs, Collector file trace/metric exports, metadata identity/allowlists/canaries, bounded fault, actual container loopback/hardening/resources, ephemeral restart and owned cleanup. Prior sandbox denials are historical; host socket/auth work without reconfiguration. Parent fault attempts and the subsequent exemplar assertion failure remain in sanitized evidence. Jaeger 2.22 translates query HTTP status to legacy `http.status_code`; every present modern/legacy value must be integer 503. Collector OTel keys/allowlists are unchanged. SDK exemplars are checked for numeric samples, timestamp/hex correlation IDs and empty filtered labels; whole exports remain canary-scanned. Query responses persist privately before assertions. This is local branch validation, with no new hosted CI or publication. P2.4 still lacks a published workload digest/immutable replay; cloud/model gates remain pending. Project apply is deferred because the existing script links evidence to main; parent publishes then synchronizes. See [sanitized evidence](../evidence/linux-compose-proof.json).

## Independent-review Linux acceptance — 8 November 2026

Final working-tree runner replay `83a8ef9c5e674ec3b347564e9287e3a3` passed after the focused review corrections. Fifty-one standard-library lab tests pass (23 Linux checks, eleven review regressions); Ruff lint/format pass. Private RED/GREEN and runtime receipts are under `../.runtime/linux-proof/review-fixes/`. Earlier runtime successes remain historical; review replay `8922096527344649b438daf94f2a1332` also passed, then `cab03ed4064d4b21b9966a61811f4f76` failed startup on an intervening port-16686 allocation. Its owned containers/networks/volumes were absent after down; port verification correctly failed. No unrelated listener was stopped.

Replay `93617e4df9244ea991aaa5f450130e43` also passed before a final envelope-edge correction. A new RED/GREEN regression now rejects an empty metrics envelope even alongside valid records; every export envelope must be nonempty.

Before the first healthy request, bounded Compose exec probes retrieval `/healthz` at port 8080 inside its existing private network namespace. Each raw backend response is saved privately before requiring exactly one trace with the requested API trace ID, including W3C. Healthy/W3C graphs require HTTP 200 for ask/tool/retrieve, reject error markers/status and unexpected HTTP codes, and require successful agent outcome with three steps and one tool call. Fault semantics and strict conflicting legacy/modern 503 rejection remain.

After all cohorts, stop application producers, fetch Prometheus/internal metrics while Collector is running, and poll boundedly for exact exported span IDs/names/multiplicity/service ownership and nonempty operation calls/duration metrics from both services. Stop Collector before the final scan; inspect final container logs and frozen trace/metric files. Final replay reconciled all 21 cohort spans. Reject nonempty instrumentation-scope attributes and scan the unique question marker independently of the full question, plus API key, baggage, every synthetic document text and generated answer across all six surfaces. Numeric metric exemplars retain strict metadata-only validation.

Docker/Compose commands use their own Linux sessions/process groups. Timeouts and cancellation terminate only that owned group with bounded TERM/KILL, reap the direct child and retain private stdout/stderr. SIGTERM and Ctrl-C route through final project cleanup. Cleanup retries down and always attempts all three label-scoped inspections, even if down fails; persistent owned resources, failed inspection or unreleased expected ports fail the proof. No prune. SIGKILL, host failure, or repeated forced interruption can bypass final cleanup; use the exact receipt project for recovery. Local images/private receipts are intentionally retained. This proves neither a log-export pipeline nor universal PII prevention.

No commit/push/merge or new hosted lab CI was performed. Parent-only infrastructure validation/publication at `62f079f9c9a25e0c83f202931bd30bca18959a3a` and supplied passing branch CI `42433363253` are separate from this runner and main CI; no deployment workflow ran. Project safe dry-run passes; live sync remains deferred because feature-only evidence would link to main. P2.4 still lacks a workload registry digest/immutable replay; historical Windows/CRLF/case-path receipts and cloud/model gates remain separate.

## Historical native Windows profile

Run from the personal-ai-observability parent workspace with Python 3.12 and the existing hash-locked workload environment. Do not use cloud credentials or live documents.

```powershell
# Fresh environment only:
py -3.12 -m venv ai-agent-workloads/.venv
ai-agent-workloads/.venv/Scripts/python.exe -m pip install --require-hashes -r ai-agent-workloads/requirements-dev.lock.txt

# Download/extract verified packages if absent:
python ai-observability-lab/scripts/install_local_backends.py

# One-shot start, traffic, export/backend assertions, stop and restart proof:
ai-agent-workloads/.venv/Scripts/python.exe ai-observability-lab/scripts/prove_local_backend.py
```

The runner verifies the downloaded archive hashes and compares each executable to its archive. It binds only loopback, refuses existing listeners, starts Jaeger and Collector, runs separate Uvicorn agent/retrieval servers, then stops only its own child processes/threads in finally blocks. It never changes Docker, credentials, Git configuration or Azure. Native Windows processes are not container-isolated; use this small synthetic cohort on the local machine only.

Ports: Jaeger OTLP gRPC 14317, query HTTP 16686 and gRPC 16685; Collector OTLP HTTP 14318, application metrics 18889 and internal metrics 18888; agent 18080 and retrieval 18081. Do not expose or forward these ports. Readiness and cleanup are bounded; a failing check exits nonzero rather than claiming completion. Abruptly killing the parent process can bypass finally cleanup; preserve its terminal until it finishes and investigate only its recorded owned PIDs if interrupted.

The deterministic model returns unknown/null token usage. A healthy request must produce the exact seven-span graph across two services; a synthetic 503 dependency fault must end as tool_error within bounds, with two attempts. The proof fetches actual Jaeger data after Collector ingestion, checks resources and capture allowlists in Collector JSONL, inspects metric labels and checks synthetic input/baggage/key/document canaries across the specified exported and queried surfaces plus controlled operation logs. It does not establish a universal PII filter, token budget, all fault resilience or production readiness.

Proof-only file exporters are injected into a private copy of the native Collector config under .runtime/local-proof/<run-id>. Their files are bounded by 5 MiB rotation plus one backup. Raw captures, process logs, generated paths and runtime authentication stay outside public source. The command prints the run-folder ID and writes result.json there. Publish a reviewed sanitized summary separately, not the raw directory.

Jaeger uses at most 1000 traces in memory. All data is ephemeral; the runner restarts Jaeger and expects the earlier trace to be absent (404 or an empty result). Collector queues/retries are bounded but not durable. After completion, no owned service remains listening. The small proof does not measure sustained-load retention, performance, outage loss or the P6 coverage target.

The query currently uses Jaeger 2.22's pinned internal HTTP JSON endpoint, suitable for this bounded proof; it is not a stable production monitoring adapter. A future SRE integration must select a supported/versioned read API. Container Compose remains a separate profile; native backend success does not prove Compose or Docker availability.
