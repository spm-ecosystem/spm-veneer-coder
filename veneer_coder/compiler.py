"""
Compiler validation and path resolution for spm-cli.
"""

from __future__ import annotations

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
