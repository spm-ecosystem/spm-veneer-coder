#!/usr/bin/env python3
"""
Standardized Subagent CLI for Veneer Coder.
Allows any external agent (Antigravity, Claude Code) or script to delegate
Veneer Spec generation tasks by passing a JSON payload and receiving a structured JSON response.

Usage:
    python subagent_cli.py --input-json '{"task": "Map search", "html_path": "page.html", "env_dir": "site-x"}'
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from veneer_coder.compiler import SPM_CLI_PATH, ValidationStatus, compile_vnr
from veneer_coder.extraction import extract_code_block
from veneer_coder.ollama import query_ollama


def run_subagent_flow(task_content: str, html_content: str, env_dir: Path, model: str, max_retries: int) -> dict:
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
        f"2. A ```css code block containing the content.css rules.\n"
        f"Make sure to follow the Plural block syntax for customStyles: 'customStyles {{ }}' blocks containing raw string strings."
    )

    current_prompt = base_prompt
    retries_used = 0
    errors_encountered = []

    for iteration in range(1, max_retries + 1):
        retries_used = iteration
        try:
            response = query_ollama(current_prompt, model)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ollama query failed: {e}",
                "retries_used": retries_used,
                "errors": errors_encountered,
            }

        vnr_code = extract_code_block(response, "vnr")
        css_code = extract_code_block(response, "css")

        if not vnr_code:
            err = "Failed to extract VNR block from response"
            errors_encountered.append(err)
            current_prompt = base_prompt + "\n\nCRITICAL: You MUST write your VNR spec within a ```vnr code block."
            continue

        status, err_msg = compile_vnr(vnr_code)
        if status == ValidationStatus.VALID or status == ValidationStatus.UNAVAILABLE:
            env_dir.mkdir(parents=True, exist_ok=True)
            vnr_name = f"{env_dir.name.replace('site-', '')}.vnr"
            vnr_path = env_dir / vnr_name
            css_path = env_dir / "content.css"
            manifest_path = env_dir / "manifest.json"

            vnr_path.write_text(vnr_code, encoding="utf-8")
            css_path.write_text(css_code, encoding="utf-8")

            compilation_log = "Saved VNR and CSS."
            if status == ValidationStatus.VALID and Path(SPM_CLI_PATH).exists():
                cmd = [SPM_CLI_PATH, "compile", str(vnr_path), "-o", str(manifest_path)]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    compilation_log = "Compiled manifest.json successfully."
                else:
                    compilation_log = f"Saved raw files, but manifest.json compilation failed:\n{res.stderr}"

            return {
                "status": "success",
                "vnr_file": str(vnr_path),
                "css_file": str(css_path),
                "manifest_file": str(manifest_path) if Path(SPM_CLI_PATH).exists() else None,
                "retries_used": retries_used,
                "compilation_log": compilation_log,
            }
        else:
            errors_encountered.append(err_msg)
            current_prompt = (
                f"The VNR code you generated failed to compile with error:\n"
                f"```\n{err_msg}\n```\n\n"
                f"Generated VNR:\n"
                f"```vnr\n{vnr_code}\n```\n\n"
                f"Please fix the compiler diagnostics. Rewrite BOTH the complete corrected ```vnr and the ```css blocks."
            )

    return {
        "status": "error",
        "message": "Max compile self-correction retries reached without success.",
        "retries_used": retries_used,
        "errors": errors_encountered,
    }


def main():
    parser = argparse.ArgumentParser(description="Structured JSON subagent delegation interface")
    parser.add_argument("--input-json", help="Direct JSON payload containing task, html_path, and env_dir")
    parser.add_argument("-m", "--model", default="veneer-coder", help="Ollama model to query")
    parser.add_argument("--max-retries", type=int, default=3)

    args = parser.parse_args()

    payload = {}
    if args.input_json:
        try:
            payload = json.loads(args.input_json)
        except Exception as e:
            print(json.dumps({"status": "error", "message": f"Invalid JSON string: {e}"}))
            return 1
    elif not sys.stdin.isatty():
        try:
            payload = json.loads(sys.stdin.read())
        except Exception as e:
            print(json.dumps({"status": "error", "message": f"Invalid JSON from stdin: {e}"}))
            return 1

    if not payload:
        print(
            json.dumps({
                "status": "error",
                "message": "Missing input payload. Pass --input-json or write JSON to stdin.",
            })
        )
        return 1

    task = payload.get("task", "")
    html_path_str = payload.get("html_path", "")
    env_dir_str = payload.get("env_dir", "")

    if not task or not html_path_str or not env_dir_str:
        print(
            json.dumps({
                "status": "error",
                "message": "Missing required fields in payload: 'task', 'html_path', and 'env_dir' are all required.",
            })
        )
        return 1

    html_path = Path(html_path_str)
    env_dir = Path(env_dir_str)

    if not html_path.exists():
        print(
            json.dumps({
                "status": "error",
                "message": f"HTML snapshot file not found: {html_path}",
            })
        )
        return 1

    html_content = html_path.read_text(encoding="utf-8")
    result = run_subagent_flow(task, html_content, env_dir, args.model, args.max_retries)

    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
