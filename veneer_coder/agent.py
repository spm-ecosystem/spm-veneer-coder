"""
Self-correcting agent execution loop.
"""

from __future__ import annotations

import sys
from veneer_coder.compiler import ValidationStatus, compile_vnr
from veneer_coder.extraction import extract_vnr_code
from veneer_coder.ollama import query_ollama


class VeneerAgentError(RuntimeError):
    """Raised when Veneer agent fails to produce valid, compile-passing VNR code."""
    pass


def run_agent(
    task_prompt: str,
    model: str = "veneer-coder",
    max_iterations: int = 3,
    strict: bool = True,
) -> str:
    """
    Executes a self-correcting generation loop.
    
    If strict is True (default), reaching max_iterations without successful compilation
    raises a VeneerAgentError, ensuring invalid code is never returned as success.
    """
    print(f"[Veneer Agent] Analyzing task: {task_prompt[:60]}...", file=sys.stderr)

    current_prompt = (
        f"Generate the Veneer Spec (.vnr) code to satisfy the following request. "
        f"Make sure to use correct syntax like 'customStyles {{ }}' blocks, "
        f"nested 'child' declarations, and correctly-formed extractor pipes:\n\n{task_prompt}"
    )

    last_err_msg = ""
    vnr_code = ""

    for iteration in range(1, max_iterations + 1):
        print(f"[Veneer Agent] Querying model {model} (Iteration {iteration}/{max_iterations})...", file=sys.stderr)
        response = query_ollama(current_prompt, model)
        vnr_code = extract_vnr_code(response)

        print(f"[Veneer Agent] Validating syntax via spm-cli...", file=sys.stderr)
        status, err_msg = compile_vnr(vnr_code)

        if status == ValidationStatus.VALID:
            print("[Veneer Agent] Compilation check passed!", file=sys.stderr)
            return vnr_code
        elif status == ValidationStatus.UNAVAILABLE:
            print(f"[Veneer Agent] Compiler unavailable: {err_msg}", file=sys.stderr)
            if strict:
                raise VeneerAgentError(f"Compilation validation unavailable: {err_msg}")
            return vnr_code
        else:
            # ValidationStatus.INVALID
            last_err_msg = err_msg
            print(f"[Veneer Agent] Compiler error detected:\n{err_msg}", file=sys.stderr)

            if iteration < max_iterations:
                current_prompt = (
                    f"Your previously generated Veneer Spec code failed to compile with the following error:\n"
                    f"```\n{err_msg}\n```\n\n"
                    f"Here was the code you generated:\n"
                    f"```vnr\n{vnr_code}\n```\n\n"
                    f"Please fix the syntax error and output the complete, corrected Veneer Spec code. "
                    f"Only output correct Veneer Spec code in code blocks."
                )

    # Max iterations reached without successful compilation
    error_detail = (
        f"Failed to generate valid Veneer Spec code after {max_iterations} attempts.\n"
        f"Final compiler error:\n{last_err_msg}"
    )
    if strict:
        raise VeneerAgentError(error_detail)

    print(f"[Veneer Agent] WARNING: Strict validation disabled. Returning unvalidated code.", file=sys.stderr)
    return vnr_code
