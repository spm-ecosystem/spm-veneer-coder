#!/usr/bin/env python3
"""
CLI Benchmark Runner for evaluating Veneer Coder inference engines.
Runs systematic evaluation cases against Ollama or custom engines,
displays formatted terminal output, and saves report artifacts.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from veneer_coder.benchmark import BenchmarkRunner
from veneer_coder.engine import MockEngine, OllamaEngine


def main():
    parser = argparse.ArgumentParser(description="Live Engine Benchmark Runner for Veneer Coder")
    parser.add_argument("--engine", choices=["ollama", "mock"], default="ollama", help="LLM engine provider")
    parser.add_argument("--model", default="veneer-coder", help="Ollama model name")
    parser.add_argument("--suite", help="Custom JSON evaluation suite path")
    parser.add_argument("--output", help="Path to save output JSON benchmark report")

    args = parser.parse_args()

    if args.engine == "ollama":
        engine = OllamaEngine(model_name=args.model)
        print(f"🚀 Initializing OllamaEngine (model: '{args.model}')...")
    else:
        engine = MockEngine()
        print("🤖 Initializing MockEngine...")

    runner = BenchmarkRunner(engine=engine, test_cases_file=args.suite)

    print("\n" + "=" * 60)
    print(" 📊 VENEER CODER ENGINE BENCHMARK ")
    print("=" * 60 + "\n")

    report = runner.run_all()

    for res in report.results:
        status_symbol = "✅ PASS" if res.passed else "❌ FAIL"
        comp_info = f"Compile: {res.compilation_status.upper()}"
        tps_info = f"{res.tokens_per_second:.1f} tok/s" if res.tokens_per_second else "N/A tok/s"

        print(f"[{status_symbol}] {res.case_id} — {res.name}")
        print(f"        Latency: {res.latency_ms:.0f}ms | Speed: {tps_info} | {comp_info}")

        if not res.passed:
            for fail in res.failures:
                print(f"        ⚠️  {fail}")
        print("-" * 60)

    print("\n" + "=" * 60)
    print(f" 📈 BENCHMARK SUMMARY ({report.engine_type})")
    print(f" Pass Rate:         {report.pass_rate_pct:.1f}% ({report.passed_cases}/{report.total_cases})")
    print(f" Avg Latency:       {report.avg_latency_ms:.0f} ms")
    if report.avg_tokens_per_sec:
        print(f" Avg Generation:    {report.avg_tokens_per_sec:.1f} tok/sec")
    print("=" * 60 + "\n")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        print(f"💾 Report saved to: {out_path}")
    else:
        # Default report archive
        archive_dir = Path(__file__).resolve().parent.parent / "outputs" / "benchmarks"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = archive_dir / f"benchmark_{args.engine}_{int(time.time())}.json"
        archive_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        print(f"💾 Report saved to: {archive_path}")

    return 0 if report.failed_cases == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
