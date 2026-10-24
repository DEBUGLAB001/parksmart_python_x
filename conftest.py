"""
ParkSmart Pytest Configuration & Telemetry Hook.
Emits strictly valid JSON telemetry matching the DEBUG//LAB exact schema.
"""

import json
import os
import sys
import time

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

_start_time = None


def pytest_sessionstart(session):
    global _start_time
    _start_time = time.time()


def pytest_report_teststatus(report, config):
    """Suppresses progress dots and 'F' characters from output."""
    category = report.outcome
    return category, "", ""


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Emits exact DEBUG//LAB formatted JSON summary."""
    # Suppress pytest's built-in summaries
    terminalreporter.summary_stats = lambda: None
    terminalreporter.summary_failures = lambda: None
    terminalreporter.summary_errors = lambda: None
    terminalreporter.summary_warnings = lambda: None
    terminalreporter.short_test_summary = lambda: None

    stats = terminalreporter.stats or {}
    passed_reports = [r for r in stats.get("passed", []) if r.when == "call"]
    failed_reports = [
        r for r in (stats.get("failed", []) + stats.get("error", []))
        if r.when in ("call", "setup")
    ]

    telemetry = {}

    for rep in passed_reports:
        test_name = rep.nodeid.split("::")[-1]
        exec_ms = max(1, int(round(rep.duration * 1000)))
        telemetry[test_name] = {
            "Status": "passed",
            "Execution time": f"{exec_ms}ms"
        }

    for rep in failed_reports:
        test_name = rep.nodeid.split("::")[-1]
        exec_ms = max(1, int(round(rep.duration * 1000)))

        err_msg = "Test failed"
        raw_err = getattr(rep, "longreprtext", None) or str(getattr(rep, "longrepr", ""))
        if raw_err:
            lines = [line.strip() for line in raw_err.splitlines() if line.strip().startswith("E   ")]
            if lines:
                err_msg = lines[0].replace("E   AssertionError: ", "").replace("E   ", "").strip()
            else:
                err_msg = raw_err.strip().splitlines()[-1].strip()

        telemetry[test_name] = {
            "Status": "failed",
            "Execution time": f"{exec_ms}ms",
            "Error": err_msg
        }

    total_time_ms = max(1, int(round((time.time() - (_start_time or time.time())) * 1000)))

    telemetry["Passed"] = len(passed_reports)
    telemetry["Failed"] = len(failed_reports)
    telemetry["Total bugs"] = 4
    telemetry["Total Execution time"] = f"{total_time_ms}ms"

    # Emit strict JSON telemetry
    terminalreporter._tw.line(json.dumps(telemetry, indent=2))
