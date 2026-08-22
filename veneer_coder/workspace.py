"""
Workspace indexing and context summarization for Veneer Spec projects.
"""

from __future__ import annotations

import re
from pathlib import Path


def index_workspace(workspace_dir: Path) -> dict:
    declared_classes = {}
    mapped_routes = []

    vnr_files = list(workspace_dir.glob("**/*.vnr"))

    for vnr_file in vnr_files:
        content = vnr_file.read_text(encoding="utf-8")

        class_matches = re.finditer(
            r"class\s+([A-Za-z0-9_]+)(?:\s+extends\s+([A-Za-z0-9_]+))?\s*\{([^}]+)\}",
            content,
            re.MULTILINE,
        )
        for match in class_matches:
            name = match.group(1)
            parent = match.group(2)
            body = match.group(3)

            props = re.findall(r"bind\s+([A-Za-z0-9_]+)\s*:", body)
            declared_classes[name] = {
                "extends": parent,
                "props": props,
                "file": vnr_file.name,
            }

        reconstruct_matches = re.finditer(
            r"(reconstruct|selector)\s+[\"']([^\"']+)[\"']\s*->\s*([A-Za-z0-9_]+)", content
        )
        for match in reconstruct_matches:
            block_type = match.group(1)
            selector = match.group(2)
            component = match.group(3)

            block_start = match.end()
            block_body = ""
            bracket_count = 0
            for char in content[block_start:]:
                if char == "{":
                    bracket_count += 1
                elif char == "}":
                    bracket_count -= 1
                    if bracket_count <= 0:
                        break
                block_body += char

            url_pattern_match = re.search(r"urlPattern\s*:\s*R?\"([^\"]+)\"", block_body)
            url_pattern = url_pattern_match.group(1) if url_pattern_match else None

            mapped_routes.append({
                "type": block_type,
                "selector": selector,
                "component": component,
                "urlPattern": url_pattern,
                "file": vnr_file.name,
            })

    return {
        "status": "success",
        "workspace_path": str(workspace_dir),
        "files_indexed": [f.name for f in vnr_files],
        "declared_classes": declared_classes,
        "mapped_routes": mapped_routes,
    }
