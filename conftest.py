"""
ParkSmart Pytest Configuration & Telemetry Hook.
Outputs strict JSON telemetry on stdout matching the required schema.
"""

import json
import os
import sys
import time

_test_results = []
_start_time = None


def pytest_sessionstart(session):
    global _start_time, _test_results
    _start_time = time.time()
    _test_results = []


def pytest_runtest_logreport(report):
    """Captures each test report."""
    if report.when == "call" or (report.when == "setup" and report.failed):
        error_msg = None
        if report.failed:
            if hasattr(report, "longreprtext") and report.longreprtext:
                error_msg = report.longreprtext.strip()
            elif hasattr(report, "longrepr") and report.longrepr:
                error_msg = str(report.longrepr).strip()
            else:
                error_msg = "Test failed"

        status = "passed" if report.passed else ("failed" if report.failed else "skipped")
        _test_results.append({
            "nodeid": report.nodeid,
            "name": report.nodeid.split("::")[-1],
            "status": status,
            "duration": round(report.duration, 4),
            "error": error_msg
        })


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Architecture-prescribed terminal-summary hook emitting strict JSON telemetry."""
    # Suppress pytest's built-in summaries
    terminalreporter.summary_stats = lambda: None
    terminalreporter.summary_failures = lambda: None
    terminalreporter.summary_errors = lambda: None
    terminalreporter.summary_warnings = lambda: None
    terminalreporter.short_test_summary = lambda: None

    total_duration = round(time.time() - (_start_time or time.time()), 4)
    passed_count = sum(1 for t in _test_results if t["status"] == "passed")
    failed_count = sum(1 for t in _test_results if t["status"] == "failed")
    total_count = len(_test_results)

    telemetry = {
        "tests": _test_results,
        "passed": passed_count,
        "failed": failed_count,
        "total": total_count,
        "intentional_bugs": 4,
        "duration": total_duration,
        "summary": {
            "passed": passed_count,
            "failed": failed_count,
            "total": total_count,
            "intentional_bug_count": 4,
            "intentional_bugs": 4,
            "total_duration": total_duration
        }
    }

    terminalreporter._tw.line(json.dumps(telemetry, indent=2))
