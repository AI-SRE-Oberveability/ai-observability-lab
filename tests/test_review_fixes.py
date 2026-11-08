"""Focused independent-review regressions; captured shapes sanitized in memory."""

import copy
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prove_linux_backend as p


def fixture():
    # Reduced actual Jaeger 2.22 healthy tags from private d3f35910 query:
    # legacy integer HTTP 200 and agent success/3 steps/1 call. No raw query.
    from test_linux_proof import trace

    t = trace()
    for s in t["spans"]:
        n = s["operationName"]
        if n in {"POST /v1/ask", "tool.retrieve", "POST /v1/retrieve"}:
            s["tags"].append({"key": "http.status_code", "value": 200})
        if n == "agent.invoke":
            s["tags"] += [
                {"key": k, "value": v}
                for k, v in {
                    "lab.outcome": "success",
                    "lab.steps": 3,
                    "lab.tool.calls": 1,
                }.items()
            ]
    return t


def exports(folder, t):
    resources = []
    for service in ("policy-agent", "policy-retrieval"):
        resource = {
            "attributes": [
                {"key": k, "value": {"stringValue": v}}
                for k, v in {"service.name": service, **p.IDENTITY}.items()
            ]
        }
        spans = [
            {"traceId": s["traceID"], "spanId": s["spanID"], "name": s["operationName"]}
            for s in t["spans"]
            if t["processes"][s["processID"]]["serviceName"] == service
        ]
        resources.append(
            {"resource": resource, "scopeSpans": [{"scope": {}, "spans": spans}]}
        )
    metrics = [
        {
            "resource": r["resource"],
            "scopeMetrics": [
                {
                    "scope": {},
                    "metrics": [
                        {
                            "name": n,
                            "sum": {
                                "dataPoints": [
                                    {
                                        "asInt": "1",
                                        "attributes": [
                                            {
                                                "key": "lab.operation",
                                                "value": {
                                                    "stringValue": "ask"
                                                    if i == 0
                                                    else "retrieve"
                                                },
                                            }
                                        ],
                                    }
                                ]
                            },
                        }
                        for n in ("lab.operation.calls", "lab.operation.duration")
                    ],
                }
            ],
        }
        for i, r in enumerate(resources)
    ]
    (folder / "capture").mkdir()
    (folder / "capture/traces.jsonl").write_text(
        json.dumps({"resourceSpans": resources}) + "\n"
    )
    (folder / "capture/metrics.jsonl").write_text(
        json.dumps({"resourceMetrics": metrics}) + "\n"
    )
    (folder / "containers.log").write_text("")
    for n in ("Prometheus", "Collector-internal"):
        (folder / (n + ".txt")).write_text("lab_operation")


class ReviewFixes(unittest.TestCase):
    def test_privacy(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d)
            t = fixture()
            exports(f, t)
            for signal, key, scope in [
                ("traces", "resourceSpans", "scopeSpans"),
                ("metrics", "resourceMetrics", "scopeMetrics"),
            ]:
                path = f / "capture" / (signal + ".jsonl")
                original = path.read_text()
                data = json.loads(original)
                data[key][0][scope][0]["scope"]["attributes"] = [
                    {"key": "question", "value": {"stringValue": "marker"}}
                ]
                path.write_text(json.dumps(data))
                with (
                    patch.object(p, "http", return_value="lab_operation"),
                    self.assertRaises(ValueError),
                ):
                    p.capture(f, [t], ["full question marker"])
                path.write_text(original)
            for surface in (
                "Jaeger queries",
                "traces",
                "metrics",
                "Prometheus",
                "Collector internal",
                "container logs",
            ):
                with self.subTest(surface=surface), self.assertRaises(ValueError):
                    p.canaries(
                        {surface: "marker"},
                        p.privacy_values(
                            "key",
                            "full question marker",
                            "marker",
                            "baggage",
                            ["answer"],
                            ["document"],
                        ),
                    )

    def test_timeout_descendant(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d)
            marker = f / "survived"
            code = (
                "import subprocess,time,sys; subprocess.Popen([sys.executable,'-c',"
                + repr(
                    "import time; from pathlib import Path; time.sleep(1); Path("
                    + repr(str(marker))
                    + ").write_text('bad')"
                )
                + "]); print('started',flush=True); time.sleep(20)"
            )
            with self.assertRaises(ValueError):
                p.Commands(f, dict(os.environ), "ai-proof-test").run(
                    [sys.executable, "-c", code], 0.15
                )
            time.sleep(1.2)
            self.assertFalse(marker.exists())
            self.assertIn("started", (f / "command-001.stdout").read_text())

    def test_cleanup(self):
        class Commands:
            project = "ai-proof-test"

            def __init__(self, persistent=False):
                self.downs = 0
                self.inspects = 0
                self.persistent = persistent

            def compose(self, *args, **kw):
                self.downs += 1
                if self.downs == 1:
                    raise ValueError("down timeout")

            def run(self, args, **kw):
                self.inspects += 1
                return "owned" if self.persistent or self.downs < 2 else ""

        c = Commands()
        with patch.object(p, "ports_free", return_value=True):
            self.assertIn("absent", p.cleanup(c))
            self.assertEqual(c.downs, 2)
            self.assertGreaterEqual(c.inspects, 6)
            c = Commands(True)
            with self.assertRaises(ValueError):
                p.cleanup(c)
            self.assertGreaterEqual(c.inspects, 6)

    def test_binding(self):
        t = fixture()
        self.assertEqual(p.queried_trace({"data": [t]}, t["traceID"]), t)
        for data in ([t, t], [{**t, "traceID": "2" * 32}]):
            with self.assertRaises(ValueError):
                p.queried_trace({"data": data}, t["traceID"])

    def test_success(self):
        t = fixture()
        p.graph(t, True)
        for key, value in [
            ("error", True),
            ("otel.status_code", "ERROR"),
            ("http.response.status_code", 503),
            ("lab.outcome", "tool_error"),
            ("lab.tool.calls", 2),
            ("lab.steps", 99),
        ]:
            bad = copy.deepcopy(t)
            target = next(
                s
                for s in bad["spans"]
                if s["operationName"]
                == ("agent.invoke" if key.startswith("lab.") else "POST /v1/ask")
            )
            target["tags"].append({"key": key, "value": value})
            with self.subTest(key=key), self.assertRaises(ValueError):
                p.graph(bad, True)

    def test_success_rejects_unexpected_http_on_internal_span(self):
        value = fixture()
        target = next(s for s in value["spans"] if s["operationName"] == "model.plan")
        target["tags"].append({"key": "http.status_code", "value": 503})
        with self.assertRaises(ValueError):
            p.graph(value, True)

    def test_completeness(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d)
            t = fixture()
            exports(f, t)
            with patch.object(p, "http", return_value="lab_operation"):
                p.capture(f, [t], ["secret"])
                for signal, key, mutate in [
                    ("metrics", "resourceMetrics", lambda x: []),
                    ("metrics", "resourceMetrics", lambda x: x[:1]),
                    ("traces", "resourceSpans", lambda x: x[:1]),
                    (
                        "traces",
                        "resourceSpans",
                        lambda x: [
                            {
                                **x[0],
                                "scopeSpans": [
                                    {"spans": [x[0]["scopeSpans"][0]["spans"][0]]}
                                ],
                            }
                        ],
                    ),
                ]:
                    path = f / "capture" / (signal + ".jsonl")
                    original = path.read_text()
                    data = json.loads(original)
                    data[key] = mutate(data[key])
                    path.write_text(json.dumps(data))
                    with self.subTest(signal=signal), self.assertRaises(ValueError):
                        p.capture(f, [t], ["secret"])
                    path.write_text(original)

    def test_empty_envelope_alongside_valid_metrics(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            value = fixture()
            exports(folder, value)
            with (folder / "capture/metrics.jsonl").open("a") as stream:
                stream.write("{}\n")
            with self.assertRaises(ValueError):
                p.capture(folder, [value], ["secret"])

    def test_cleanup_failure_overrides_pass_report(self):
        report = {"status": "passed"}
        with patch.object(p, "cleanup", side_effect=ValueError("resources persist")):
            p.finish_cleanup(object(), report)
        self.assertEqual(report["status"], "failed")
        self.assertIn("persist", report["cleanup"])

    def test_freeze_order(self):
        events = []

        class Commands:
            def compose(self, *args, **kwargs):
                events.append(args)
                return "final logs"

        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            with (
                patch.object(p, "http", return_value="lab_operation"),
                patch.object(
                    p, "capture", side_effect=[ValueError("incomplete"), {}]
                ) as scan,
            ):
                p.freeze_exports(Commands(), folder, [], "key")
            self.assertEqual(events[0], ("stop", "-t", "10", "agent", "retrieval"))
            self.assertEqual(scan.call_count, 2)
            self.assertEqual(events[-2], ("stop", "-t", "10", "collector"))
            self.assertEqual(events[-1], ("logs", "--no-color"))
            self.assertEqual((folder / "containers.log").read_text(), "final logs")

    def test_readiness(self):
        calls = []

        class Commands:
            def compose(self, *args, **kwargs):
                calls.append(args)
                return "ok"

        p.retrieval_ready(Commands())
        self.assertEqual(calls[0][:4], ("exec", "-T", "retrieval", "python"))
        self.assertIn("127.0.0.1:8080/healthz", calls[0][-1])
