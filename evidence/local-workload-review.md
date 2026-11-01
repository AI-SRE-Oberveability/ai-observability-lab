# P1.1 local workload review

1 November 2026, Asia/Dubai. Reviewed policy-agent/retrieval code, typed models, two OpenAPI contracts, allowlisted telemetry, versioned synthetic evaluations, real-HTTP tests, pinned development requirements, Compose and native-backend installer.

Baseline: 18 tests passed in 27.70 seconds on Python 3.12.9; one Starlette TestClient/httpx deprecation. Versions: FastAPI 0.162.0, Starlette 1.10.0, HTTPX 0.28.1, Uvicorn 0.54.0, OpenTelemetry SDK 1.45.1, pytest 9.2.0. The sandboxed listener run was interrupted after fixture failures; the authorized loopback run completed. This is local HTTP/in-memory exporter evidence, not backend proof.

Findings and treatment:

- The previously missing CI dependency input is now supplied as requirements-dev.lock.txt and installed with hash verification by active CI. No dependency migration is needed to begin this local cohort.
- The deprecation is limited to one auth/control test importing TestClient. Reuse the existing Uvicorn loopback fixture with HTTPX instead; retain all assertions and locked versions.
- Existing code enforces three workflow steps, two tool attempts, a total deadline, bounded response documents/bytes and sanitized typed failures. Model usage remains null. Authentication and fault switches are explicit.
- Instrumentation is explicit custom lab schema v1.0.0 with fixed names, two service identities, no baggage and no automatic exception events. Seven-span healthy graph and metadata-only fields pass in-memory assertions. Exported/backend data must still be checked.
- The backend configuration is container-oriented (service DNS and listeners). Add a separate native Windows profile binding every listener to 127.0.0.1, with pinned binaries and bounded in-memory storage; do not replace container settings.
- Provide a one-shot owned-process proof runner with port conflict refusal, readiness/deadlines, finally-based cleanup and restart/ephemeral retention checks. No arbitrary process killing or machine-wide Docker/credential changes.
- Remaining limits: no production request-byte/connection admission control, live token enforcement, durable telemetry/storage, resource isolation equivalent to containers, live model, APIM or Managed claim. These are not supplied by this local proof. Use synthetic data and loopback access only.

Next: remove the test warning, validate the native configurations, then retrieve actual Collector-exported traces from the pinned Jaeger backend and inspect capture surfaces. Cloud/APIM/Managed work remains gated.
