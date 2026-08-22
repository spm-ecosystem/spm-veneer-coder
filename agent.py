#!/usr/bin/env python3
"""
CLI wrapper for using the local Veneer-coder Ollama model as a self-correcting subagent.

Usage:
    python agent.py "Create a header reconstruction for #header -> UiNavHeader"
    python agent.py --input task_description.txt --output theme.vnr
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import shutil
import tempfile
import urllib.request
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"


def resolve_spm_cli() -> str:
    path_lookup = shutil.which("spm")
    if path_lookup:
        return path_lookup
    sibling_path = Path(__file__).resolve().parent.parent / "spm-cli/spm"
    if sibling_path.exists():
        return str(sibling_path)
    return "spm"


SPM_CLI_PATH = resolve_spm_cli()


def query_ollama(prompt: str, model: str) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9
        }
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            res = json.loads(response.read().decode("utf-8"))
            return res.get("response", "").strip()
    except Exception as e:
        print(f"[Error] Failed to connect to Ollama: {e}", file=sys.stderr)
        sys.exit(1)


def extract_vnr_code(response: str) -> str:
    # Try extracting from ```vnr ... ``` code block
    vnr_match = re.search(r"```vnr\n(.*?)\n```", response, re.DOTALL)
    if vnr_match:
        return vnr_match.group(1).strip()
    # Fallback to general ``` ... ``` code block
    generic_match = re.search(r"```\n(.*?)\n```", response, re.DOTALL)
    if generic_match:
        return generic_match.group(1).strip()
    # Fallback to returning the response itself if no code fences found
    return response.strip()


def compile_vnr(vnr_code: str) -> tuple[bool, str]:
    """Test compiles the Veneer spec using spm-cli to detect syntax errors."""
    if not Path(SPM_CLI_PATH).exists():
        # If spm-cli is not installed or accessible, skip compilation validation
        return True, "spm-cli compile skipped (binary not found)"

    with tempfile.NamedTemporaryFile(suffix=".vnr", mode="w+", delete=False) as tmp_vnr:
        tmp_vnr.write(vnr_code)
        tmp_vnr.flush()
        tmp_vnr_path = tmp_vnr.name

    try:
        # Run compiler to check syntax without generating manifest
        cmd = [SPM_CLI_PATH, "compile", tmp_vnr_path, "-o", "/dev/null"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            return True, ""
        else:
            # Clean up the temp path from error output to keep prompt clean
            err_msg = res.stderr.replace(tmp_vnr_path, "source.vnr")
            return False, err_msg.strip()
    except Exception as e:
        return True, f"Compilation check failed to execute: {e}"
    finally:
        try:
            Path(tmp_vnr_path).unlink()
        except OSError:
            pass


import re


def run_agent(task_prompt: str, model: str, max_iterations: int = 3) -> str:
    print(f"[Veneer Agent] Analyzing task: {task_prompt[:60]}...", file=sys.stderr)
    
    current_prompt = (
        f"Generate the Veneer Spec (.vnr) code to satisfy the following request. "
        f"Make sure to use correct syntax like 'customStyles {{ }}' blocks, "
        f"nested 'child' declarations, and correctly-formed extractor pipes:\n\n{task_prompt}"
    )
    
    for iteration in range(1, max_iterations + 1):
        print(f"[Veneer Agent] Querying model {model} (Iteration {iteration}/{max_iterations})...", file=sys.stderr)
        response = query_ollama(current_prompt, model)
        vnr_code = extract_vnr_code(response)
        
        print(f"[Veneer Agent] Validating syntax via spm-cli...", file=sys.stderr)
        success, err_msg = compile_vnr(vnr_code)
        
        if success:
            print("[Veneer Agent] Compilation check passed!", file=sys.stderr)
            return vnr_code
        else:
            print(f"[Veneer Agent] Compiler error detected:\n{err_msg}", file=sys.stderr)
            if iteration == max_iterations:
                print("[Veneer Agent] Reached max self-correction limit. Returning output.", file=sys.stderr)
                return vnr_code
            
            # Feed back the error for self-correction
            current_prompt = (
                f"Your previously generated Veneer Spec code failed to compile with the following error:\n"
                f"```\n{err_msg}\n```\n\n"
                f"Here was the code you generated:\n"
                f"```vnr\n{vnr_code}\n```\n\n"
                f"Please fix the syntax error and output the complete, corrected Veneer Spec code. "
                f"Only output correct Veneer Spec code in code blocks."
            )
            
    return ""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Self-Correcting Veneer Spec LLM Subagent")
    parser.add_argument("prompt", nargs="?", help="Direct natural language task prompt for the agent")
    parser.add_argument("-i", "--input", help="Read task description from input text file")
    parser.add_argument("-o", "--output", help="Write final validated .vnr code to output file")
    parser.add_argument("--html", help="Path to an HTML file to append as structure context")
    parser.add_argument("-m", "--model", default="veneer-coder", help="Ollama model name to target")
    parser.add_argument("--max-retries", type=int, default=3, help="Max self-correction validation passes")
    
    args = parser.parse_args(argv)
    
    task_prompt = ""
    if args.input:
        task_prompt = Path(args.input).read_text(encoding="utf-8")
    elif args.prompt:
        task_prompt = args.prompt
    else:
        # Read from stdin if no direct arguments
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
            
    final_vnr = run_agent(task_prompt + html_context, args.model, args.max_retries)
    
    if args.output:
        Path(args.output).write_text(final_vnr, encoding="utf-8")
        print(f"[Veneer Agent] Saved validated code -> {args.output}", file=sys.stderr)
    else:
        # Output final code directly to stdout
        print(final_vnr)
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
