"""
Compiler validation and path resolution for spm-cli.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from enum import Enum
from pathlib import Path


class ValidationStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNAVAILABLE = "unavailable"


def resolve_spm_cli() -> str:
    path_lookup = shutil.which("spm")
    if path_lookup:
        return path_lookup
    sibling_path = Path(__file__).resolve().parent.parent.parent / "spm-cli/spm"
    if sibling_path.exists():
        return str(sibling_path)
    return "spm"


SPM_CLI_PATH = resolve_spm_cli()


def compile_vnr(vnr_code: str, spm_binary_path: str | None = None) -> tuple[ValidationStatus, str]:
    """
    Test compiles the Veneer spec using spm-cli to detect syntax errors.
    Returns (ValidationStatus, error_or_info_message).
    
    IMPORTANT: Compiler unavailability is explicitly returned as ValidationStatus.UNAVAILABLE,
    never falsely reported as VALID.
    """
    cli_path = spm_binary_path or SPM_CLI_PATH
    cli_bin = Path(cli_path)

    # Check if binary exists or is in PATH
    if not cli_bin.is_absolute() and not shutil.which(cli_path):
        return ValidationStatus.UNAVAILABLE, f"spm-cli binary not found in PATH or at {cli_path}"
    elif cli_bin.is_absolute() and not cli_bin.exists():
        return ValidationStatus.UNAVAILABLE, f"spm-cli binary not found at {cli_path}"

    with tempfile.NamedTemporaryFile(suffix=".vnr", mode="w+", delete=False, encoding="utf-8") as tmp_vnr:
        tmp_vnr.write(vnr_code)
        tmp_vnr.flush()
        tmp_vnr_path = tmp_vnr.name

    try:
        cmd = [cli_path, "compile", tmp_vnr_path, "-o", "/dev/null"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            return ValidationStatus.VALID, ""
        else:
            err_msg = res.stderr.replace(tmp_vnr_path, "source.vnr")
            return ValidationStatus.INVALID, err_msg.strip()
    except Exception as e:
        return ValidationStatus.UNAVAILABLE, f"Compilation check failed to execute: {e}"
    finally:
        try:
            Path(tmp_vnr_path).unlink()
        except OSError:
            pass


def validate_vnr_semantics(
    vnr_code: str,
    sample_html: str | None = None,
    spm_binary_path: str | None = None,
) -> tuple[ValidationStatus, str]:
    """
    Validates both syntax (via compile_vnr) and semantic correctness (selector precision,
    non-empty reconstruct blocks, HTML selector matching).
    """
    # 1. First run syntax validation
    status, err = compile_vnr(vnr_code, spm_binary_path=spm_binary_path)
    if status != ValidationStatus.VALID:
        return status, err

    semantic_errors = []

    # 2. Check for overly broad nested selectors (e.g. "table table tr", "div div div")
    broad_patterns = [r"table\s+table\s+tr", r"div\s+div\s+div", r"ul\s+ul\s+li"]
    for pattern in broad_patterns:
        if re.search(pattern, vnr_code, re.IGNORECASE):
            clean_p = pattern.replace(r"\s+", " ")
            semantic_errors.append(
                f"Semantic Warning: Overly broad nested selector '{clean_p}' detected. "
                "This matches multiple nesting levels. Use specific class or ID selectors."
            )

    # 3. Check for empty reconstruct blocks (reconstruct declared without bind or child)
    reconstruct_blocks = re.findall(r"reconstruct\s+\"[^\"]+\"\s*->\s*\w+\s*\{([^}]+)\}", vnr_code)
    for block in reconstruct_blocks:
        if "bind" not in block and "child" not in block and "preserve" not in block:
            semantic_errors.append(
                "Semantic Error: 'reconstruct' block is empty or missing 'bind'/'child' prop mappings."
            )

    # 4. If sample_html is provided, test selector matches against HTML
    if sample_html:
        selectors = re.findall(r'selector\s*:\s*"([^"]+)"', vnr_code)
        selectors.extend(re.findall(r'reconstruct\s*"([^"]+)"', vnr_code))

        for sel in selectors:
            if not sel or sel == "self":
                continue
            clean_sel = sel.strip()
            if clean_sel.startswith("#"):
                id_name = clean_sel[1:]
                if f'id="{id_name}"' not in sample_html and f"id='{id_name}'" not in sample_html:
                    semantic_errors.append(f"Semantic Error: ID selector '{clean_sel}' was not found in sample HTML.")
            elif clean_sel.startswith("."):
                class_name = clean_sel[1:]
                if class_name not in sample_html:
                    semantic_errors.append(f"Semantic Error: Class selector '{clean_sel}' was not found in sample HTML.")

    if semantic_errors:
        return ValidationStatus.INVALID, "\n".join(semantic_errors)

    return ValidationStatus.VALID, ""

