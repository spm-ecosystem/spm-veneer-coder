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

from veneer_coder.compiler import SPM_CLI_PATH, ValidationStatus, validate_vnr_semantics
from veneer_coder.extraction import extract_code_block
from veneer_coder.ollama import query_ollama
from veneer_coder.schema import get_grounding_prompt


def run_subagent_flow(task_content: str, html_content: str, env_dir: Path, model: str, max_retries: int) -> dict:
    grounding_prompt = get_grounding_prompt(task_content)
    grounding_block = f"\n\n### COMPONENT REFERENCE SCHEMAS:\n{grounding_prompt}" if grounding_prompt else ""

    base_prompt = (
        f"You are a Veneer Spec (.vnr) generator subagent. Your task is to analyze "
        f"the provided task brief and HTML structure of a legacy web page, then write "
        f"a correct, compile-passing `.vnr` spec and an accompanying `content.css` stylesheet.\n\n"
        f"### TASK BRIEF:\n"
        f"{task_content}\n\n"
        f"### TARGET HTML STRUCTURE:\n"
        f"```html\n{html_content}\n```"
        f"{grounding_block}\n\n"
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

        if not css_code and "customStyles" in vnr_code:
            err = "VNR spec contains customStyles but missing ```css code block in output"
            errors_encountered.append(err)
            current_prompt = base_prompt + f"\n\nYour previous VNR code contained customStyles, but you omitted the ```css code block. Please provide both the ```vnr and ```css code blocks."
            continue

        # Perform full syntax and semantic validation
        val_status, val_msg = validate_vnr_semantics(vnr_code, sample_html=html_content)

        if val_status == ValidationStatus.VALID:
            # Write results
            vnr_path = env_dir / "generated.vnr"
            css_path = env_dir / "content.css"
            try:
                vnr_path.write_text(vnr_code, encoding="utf-8")
                css_path.write_text(css_code or "/* No custom CSS */", encoding="utf-8")
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to write output files: {e}",
                    "retries_used": retries_used,
                    "errors": errors_encountered,
                }

            return {
                "status": "success",
                "vnr_file": str(vnr_path),
                "css_file": str(css_path),
                "retries_used": retries_used,
                "errors_encountered": errors_encountered,
            }
        else:
            errors_encountered.append(f"Validation failed (Iteration {iteration}): {val_msg}")
            current_prompt = (
                f"{base_prompt}\n\n"
                f"CRITICAL FIX REQUIRED:\n"
                f"Your previous attempt generated the following Veneer Spec:\n"
                f"```vnr\n{vnr_code}\n```\n\n"
                f"However, validation failed with the following error message:\n"
                f"{val_msg}\n\n"
                f"Please fix this error and generate a valid `.vnr` spec and `.css` stylesheet."
            )

    return {
        "status": "failed",
        "message": f"Failed to generate valid Veneer Spec after {max_retries} retries.",
        "retries_used": retries_used,
        "errors": errors_encountered,
    }


def main():
    parser = argparse.ArgumentParser(description="Subagent CLI for Veneer Coder")
    parser.add_argument("--input-json", help="JSON payload string or path to JSON file")
    parser.add_argument("--model", default="qwen2.5-coder:7b-instruct-q4_K_M", help="Ollama model to use")
    parser.add_argument("--max-retries", type=int, default=3, help="Max retry attempts on compilation failure")
    args = parser.parse_args()

    if not args.input_json:
        parser.print_help()
        sys.exit(1)

    try:
        input_path = Path(args.input_json)
        if input_path.exists():
            payload = json.loads(input_path.read_text(encoding="utf-8"))
        else:
            payload = json.loads(args.input_json)
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Failed to parse input JSON: {e}"}))
        sys.exit(1)

    task_content = payload.get("task", "")
    html_content = payload.get("html", "")
    html_path_str = payload.get("html_path", "")
    env_dir_str = payload.get("env_dir", ".")

    env_dir = Path(env_dir_str)
    env_dir.mkdir(parents=True, exist_ok=True)

    if not html_content and html_path_str:
        hp = Path(html_path_str)
        if hp.exists():
            html_content = hp.read_text(encoding="utf-8")

    res = run_subagent_flow(task_content, html_content, env_dir, args.model, args.max_retries)
    print(json.dumps(res, indent=2))
    if res.get("status") != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
