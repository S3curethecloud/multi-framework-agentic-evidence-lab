"""Run the shared benchmark question set against the Strands-style agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from shared.sample_questions import BENCHMARK_QUESTIONS
from strands_lab.agent import run_strands_workflow


def main() -> int:
    reports: List[Dict[str, Any]] = []
    traces: List[Dict[str, Any]] = []
    for question in BENCHMARK_QUESTIONS:
        report, trace = run_strands_workflow(question)
        reports.append(report.model_dump(mode="json"))
        traces.append(trace.model_dump(mode="json"))

    report_path = Path("results/reports/strands_report.json")
    trace_path = Path("results/traces/strands_trace.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(reports, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    trace_path.write_text(json.dumps(traces, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {len(reports)} reports to {report_path}")
    print(f"Wrote {len(traces)} traces to {trace_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
