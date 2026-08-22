"""
Systematic benchmark runner for evaluating LLM engines against Veneer Spec test cases.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from veneer_coder.compiler import ValidationStatus, compile_vnr
from veneer_coder.engine import BaseLLMEngine, EngineResponse
from veneer_coder.extraction import extract_vnr_code


@dataclass
class TestCaseResult:
    case_id: str
    name: str
    passed: bool
    compilation_status: str
    latency_ms: float
    tokens_per_second: float | None
    extracted_code: str
    compilation_error: str | None
    failures: list[str]


@dataclass
class BenchmarkReport:
    timestamp: float
    engine_type: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate_pct: float
    avg_latency_ms: float
    avg_tokens_per_sec: float
    results: list[TestCaseResult]

    def to_dict(self) -> dict:
        return asdict(self)


class BenchmarkRunner:
    """Runs systematic benchmarks against any BaseLLMEngine."""

    def __init__(self, engine: BaseLLMEngine, test_cases_file: Path | str | None = None):
        self.engine = engine
        if test_cases_file:
            self.test_cases_path = Path(test_cases_file)
        else:
            self.test_cases_path = Path(__file__).resolve().parent.parent / "tests" / "evals" / "golden_eval_suite.json"

    def load_cases(self) -> list[dict]:
        if not self.test_cases_path.exists():
            raise FileNotFoundError(f"Evaluation suite file not found at: {self.test_cases_path}")
        return json.loads(self.test_cases_path.read_text(encoding="utf-8"))

    def run_case(self, case: dict) -> TestCaseResult:
        prompt = case["prompt"]
        case_id = case["id"]
        case_name = case.get("name", case_id)
        failures = []

        response: EngineResponse = self.engine.generate(prompt)
        raw_text = response.text

        extracted_code = extract_vnr_code(raw_text)
        comp_status, err_msg = compile_vnr(extracted_code)

        # Check compiler requirement
        if case.get("must_compile"):
            if comp_status == ValidationStatus.INVALID:
                failures.append(f"Compilation failed: {err_msg}")
            elif comp_status == ValidationStatus.UNAVAILABLE:
                # Log compilation unavailable as a warning, not failure
                pass

        # Check keyword containment
        must_contain = case.get("must_contain", [])
        for keyword in must_contain:
            if keyword not in raw_text:
                failures.append(f"Missing required keyword: '{keyword}'")

        # Check keyword exclusion
        must_not_contain = case.get("must_not_contain", [])
        for keyword in must_not_contain:
            if keyword in raw_text:
                failures.append(f"Found forbidden keyword: '{keyword}'")

        passed = len(failures) == 0

        return TestCaseResult(
            case_id=case_id,
            name=case_name,
            passed=passed,
            compilation_status=comp_status.value,
            latency_ms=response.latency_ms,
            tokens_per_second=response.tokens_per_second,
            extracted_code=extracted_code,
            compilation_error=err_msg if comp_status == ValidationStatus.INVALID else None,
            failures=failures,
        )

    def run_all(self) -> BenchmarkReport:
        cases = self.load_cases()
        results: list[TestCaseResult] = []

        for case in cases:
            results.append(self.run_case(case))

        total_cases = len(results)
        passed_cases = sum(1 for r in results if r.passed)
        failed_cases = total_cases - passed_cases
        pass_rate = (passed_cases / total_cases * 100.0) if total_cases > 0 else 0.0

        latencies = [r.latency_ms for r in results]
        avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0

        tps_list = [r.tokens_per_second for r in results if r.tokens_per_second is not None]
        avg_tps = (sum(tps_list) / len(tps_list)) if tps_list else 0.0

        return BenchmarkReport(
            timestamp=time.time(),
            engine_type=type(self.engine).__name__,
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            pass_rate_pct=pass_rate,
            avg_latency_ms=avg_latency,
            avg_tokens_per_sec=avg_tps,
            results=results,
        )
