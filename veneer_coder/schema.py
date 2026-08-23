"""
Component schema loader and prompt grounding provider.
"""

from __future__ import annotations

import re
from pathlib import Path

SPECS_FILE = Path(__file__).resolve().parent.parent / "in/dataset/component_specs_verified.md"

_SCHEMA_CACHE: dict[str, str] = {}


def load_component_schemas() -> dict[str, str]:
    """Parses component_specs_verified.md into a map of ComponentName -> Schema Text."""
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE:
        return _SCHEMA_CACHE

    if not SPECS_FILE.exists():
        return {}

    content = SPECS_FILE.read_text(encoding="utf-8")
    sections = re.split(r"^# React component specification:\s*", content, flags=re.MULTILINE)

    schemas = {}
    for section in sections:
        if not section.strip():
            continue
        lines = section.strip().split("\n")
        comp_name = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        schemas[comp_name] = body

    _SCHEMA_CACHE = schemas
    return _SCHEMA_CACHE


def get_grounding_prompt(task_prompt: str, target_components: list[str] | None = None) -> str:
    """
    Generates component schema grounding context for the model's prompt.
    If target_components is not specified, auto-detects mentioned components or returns key specs.
    """
    schemas = load_component_schemas()
    if not schemas:
        return ""

    selected = []
    if target_components:
        for comp in target_components:
            if comp in schemas:
                selected.append((comp, schemas[comp]))
    else:
        # Auto-detect mentioned components in task_prompt
        for comp, body in schemas.items():
            if comp.lower() in task_prompt.lower():
                selected.append((comp, body))

        # If none detected, provide key reference schemas
        if not selected:
            for key in ["UiTableListPage", "UiNavHeader", "UiSearchBar", "UiModernGridPage"]:
                if key in schemas:
                    selected.append((key, schemas[key]))

    if not selected:
        return ""

    context_blocks = []
    for comp, body in selected:
        context_blocks.append(f"### Component Reference Schema: {comp}\n{body}")

    return "\n\n".join(context_blocks)
