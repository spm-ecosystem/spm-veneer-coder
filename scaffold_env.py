#!/usr/bin/env python3
"""
Scaffolding automation script to generate correct VNR and CSS for a QA environment
using the local Veneer-coder Ollama model with compiler self-correction.

Usage:
    python scaffold_env.py /home/watashi/Projects/spm-qa-test-suite/environments/site-j-stackoverflow
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from veneer_coder.compiler import SPM_CLI_PATH, ValidationStatus, compile_vnr
from veneer_coder.extraction import extract_code_block
from veneer_coder.ollama import query_ollama


def scaffold_environment(env_path: Path, model: str, max_retries: int = 3) -> None:
    print(f"[Scaffolder] Analyzing environment: {env_path.name}", file=sys.stderr)

    task_file = env_path / "task.md"
    html_file = next(env_path.glob("**/page-snapshot.html"), None)
    if not html_file:
        html_file = next(env_path.glob("**/*.html"), None)

    if not html_file:
        print(f"[Error] No page snapshot HTML found in {env_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[Scaffolder] Found HTML snapshot: {html_file.name}", file=sys.stderr)

    html_content = html_file.read_text(encoding="utf-8")
    task_content = (
        task_file.read_text(encoding="utf-8")
        if task_file.exists()
        else "Create a modern Veneer Spec layout override for the page structure."
    )

    html_lines = html_content.splitlines()
    if len(html_lines) > 2000:
        print(
            f"[Warning] Snapshot HTML is very large ({len(html_lines)} lines). Truncating to fit context window...",
            file=sys.stderr,
        )
        html_content = "\n".join(html_lines[:1500]) + "\n\n<!-- ... [HTML TRUNCATED FOR CONTEXT SIZE] ... -->"

    base_prompt = (
        f"You are a Veneer Spec (.vnr) generator subagent. Your task is to analyze "
        f"the provided task brief and HTML structure of a legacy web page, then write "
        f"a correct, compile-passing `.vnr` spec and a accompanying `content.css` stylesheet.\n\n"
        f"### TASK BRIEF:\n"
        f"{task_content}\n\n"
        f"### TARGET HTML STRUCTURE:\n"
        f"```html\n{html_content}\n```\n\n"
        f"### OUTPUT FORMAT:\n"
        f"Write your response using exactly two code blocks:\n"
        f"1. A ```vnr code block containing the complete Veneer Spec code.\n"
        f"2. A ```css code block containing the content.css rules (like custom variables or styles).\n"
        f"Make sure to follow the Plural block syntax for customStyles: 'customStyles {{ }}' blocks containing raw string strings."
    )

    current_prompt = base_prompt

    for iteration in range(1, max_retries + 1):
        print(f"[Scaffolder] Querying Ollama (Iteration {iteration}/{max_retries})...", file=sys.stderr)
        response = query_ollama(current_prompt, model)

        vnr_code = extract_code_block(response, "vnr")
        css_code = extract_code_block(response, "css")

        if not vnr_code:
            print("[Error] Failed to extract any VNR block from the model's response.", file=sys.stderr)
            current_prompt = base_prompt + "\n\nCRITICAL: You MUST write your VNR spec within a ```vnr code block."
            continue

        print("[Scaffolder] Checking VNR syntax via spm-cli...", file=sys.stderr)
        status, err_msg = compile_vnr(vnr_code)

        if status == ValidationStatus.VALID or status == ValidationStatus.UNAVAILABLE:
            print("[Scaffolder] Success! VNR code compiled successfully.", file=sys.stderr)

            vnr_name = f"{env_path.name.replace('site-', '')}.vnr"
            vnr_dest = env_path / vnr_name
            css_dest = env_path / "content.css"

            vnr_dest.write_text(vnr_code, encoding="utf-8")
            css_dest.write_text(css_code, encoding="utf-8")

            print(f"[Scaffolder] Saved spec -> {vnr_dest}", file=sys.stderr)
            print(f"[Scaffolder] Saved style -> {css_dest}", file=sys.stderr)

            if status == ValidationStatus.VALID and Path(SPM_CLI_PATH).exists():
                print("[Scaffolder] Compiling manifest.json...", file=sys.stderr)
                cmd = [SPM_CLI_PATH, "compile", str(vnr_dest), "-o", str(env_path / "manifest.json")]
                subprocess.run(cmd, capture_output=True, text=True)
                print("[Scaffolder] Compilation complete!", file=sys.stderr)

            return
        else:
            print(f"[Scaffolder] Compiler error detected:\n{err_msg}", file=sys.stderr)
            if iteration == max_retries:
                print("[Error] Max retries reached. Scaffolding failed.", file=sys.stderr)
                sys.exit(1)

            current_prompt = (
                f"The VNR code you generated failed to compile with error:\n"
                f"```\n{err_msg}\n```\n\n"
                f"Generated VNR:\n"
                f"```vnr\n{vnr_code}\n```\n\n"
                f"Please fix the compiler diagnostics. Rewrite BOTH the complete corrected ```vnr and the ```css blocks."
            )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Self-Correcting VNR/CSS Scaffolding Agent")
    parser.add_argument("env_dir", help="Path to the QA environment folder")
    parser.add_argument("-m", "--model", default="veneer-coder", help="Ollama model name to target")
    parser.add_argument("--max-retries", type=int, default=3, help="Max self-correction validation passes")

    args = parser.parse_args(argv)

    env_path = Path(args.env_dir).resolve()
    if not env_path.is_dir():
        print(f"[Error] Environment folder does not exist: {env_path}", file=sys.stderr)
        return 1

    scaffold_environment(env_path, args.model, args.max_retries)
    return 0


if __name__ == "__main__":
    sys.exit(main())
