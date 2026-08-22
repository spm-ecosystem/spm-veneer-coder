"""
Code block extraction utilities for Veneer Spec (.vnr), CSS, and other markdown blocks.
"""

from __future__ import annotations

import re


def extract_vnr_code(response: str) -> str:
    """Extract code from ```vnr ... ``` or general ``` ... ``` blocks."""
    vnr_match = re.search(r"```vnr\n(.*?)\n```", response, re.DOTALL)
    if vnr_match:
        return vnr_match.group(1).strip()
    generic_match = re.search(r"```\n(.*?)\n```", response, re.DOTALL)
    if generic_match:
        return generic_match.group(1).strip()
    return response.strip()


def extract_code_block(response: str, lang: str) -> str:
    """Extract code block matching a specific language identifier (e.g. 'vnr', 'css')."""
    pattern = rf"```{lang}\n(.*?)\n```"
    match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    if lang.lower() == "vnr":
        return extract_vnr_code(response)
    return ""
