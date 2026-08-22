"""
Live engine evaluation test suite.
Evaluates the trained Ollama model systematically when invoked with pytest -m live.
Offline unit tests ignore live calls by default.
"""

from __future__ import annotations

import pytest

from veneer_coder.benchmark import BenchmarkRunner
from veneer_coder.engine import MockEngine, OllamaEngine


def test_mock_engine_benchmark():
    """Offline test verifying BenchmarkRunner logic using MockEngine."""
    engine = MockEngine()
    runner = BenchmarkRunner(engine=engine)
    report = runner.run_all()

    assert report.total_cases > 0
    assert report.engine_type == "MockEngine"
    assert report.avg_latency_ms > 0


@pytest.mark.live
def test_live_ollama_engine_benchmark():
    """Live test running systematic benchmarks against local Ollama instance."""
    engine = OllamaEngine(model_name="veneer-coder")
    runner = BenchmarkRunner(engine=engine)
    report = runner.run_all()

    assert report.total_cases >= 4
    assert report.pass_rate_pct >= 50.0, f"Live engine benchmark pass rate too low: {report.pass_rate_pct}%"
