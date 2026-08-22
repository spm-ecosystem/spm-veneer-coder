#!/usr/bin/env python3
"""
CLI wrapper for using the local Veneer-coder Ollama model as a self-correcting subagent.

Usage:
    python agent.py "Create a header reconstruction for #header -> UiNavHeader"
    python agent.py --input task_description.txt --output theme.vnr
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from veneer_coder.agent import run_agent, VeneerAgentError
from veneer_coder.compiler import SPM_CLI_PATH, ValidationStatus, compile_vnr
from veneer_coder.extraction import extract_vnr_code
from veneer_coder.ollama import query_ollama


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Self-Correcting Veneer Spec LLM Subagent")
    parser.add_argument("prompt", nargs="?", help="Direct natural language task prompt for the agent")
    parser.add_argument("-i", "--input", help="Read task description from input text file")
    parser.add_argument("-o", "--output", help="Write final validated .vnr code to output file")
    parser.add_argument("--html", help="Path to an HTML file to append as structure context")
    parser.add_argument("-m", "--model", default="veneer-coder", help="Ollama model name to target")
    parser.add_argument("--max-retries", type=int, default=3, help="Max self-correction validation passes")
    parser.add_argument("--non-strict", action="store_true", help="Allow returning unvalidated code on max retries")

    args = parser.parse_args(argv)

    task_prompt = ""
    if args.input:
        task_prompt = Path(args.input).read_text(encoding="utf-8")
    elif args.prompt:
        task_prompt = args.prompt
    else:
        if not sys.stdin.isatty():
            task_prompt = sys.stdin.read()

    if not task_prompt.strip():
        parser.print_help()
        return 1

    html_context = ""
    if args.html:
        html_path = Path(args.html)
        if html_path.exists():
            html_content = html_path.read_text(encoding="utf-8")
            html_context = (
                f"\n\nHere is the target HTML structure for context:\n"
                f"```html\n{html_content}\n```"
            )
        else:
            print(f"[Warning] HTML file not found: {args.html}", file=sys.stderr)

    try:
        final_vnr = run_agent(
            task_prompt + html_context,
            model=args.model,
            max_iterations=args.max_retries,
            strict=not args.non_strict,
        )
    except VeneerAgentError as e:
        print(f"[Veneer Agent Error] {e}", file=sys.stderr)
        return 1

    if args.output:
        Path(args.output).write_text(final_vnr, encoding="utf-8")
        print(f"[Veneer Agent] Saved validated code -> {args.output}", file=sys.stderr)
    else:
        print(final_vnr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
