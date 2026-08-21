#!/usr/bin/env python3
"""
Workspace Indexer for Veneer Spec Projects.
Scans the project workspace to compile a map of declared classes,
mapped routes, and active components to serve as a global context payload
for the subagent.
"""
import re
import json
import argparse
from pathlib import Path


def index_workspace(workspace_dir: Path) -> dict:
    declared_classes = {}
    mapped_routes = []
    
    # 1. Scan for VNR files
    vnr_files = list(workspace_dir.glob("**/*.vnr"))
    
    for vnr_file in vnr_files:
        content = vnr_file.read_text(encoding="utf-8")
        
        # Extract classes and their inheritance
        # e.g., class Name extends Parent {
        class_matches = re.finditer(
            r"class\s+([A-Za-z0-9_]+)(?:\s+extends\s+([A-Za-z0-9_]+))?\s*\{([^}]+)\}",
            content,
            re.MULTILINE
        )
        for match in class_matches:
            name = match.group(1)
            parent = match.group(2)
            body = match.group(3)
            
            # Find bound properties
            props = re.findall(r"bind\s+([A-Za-z0-9_]+)\s*:", body)
            declared_classes[name] = {
                "extends": parent,
                "props": props,
                "file": vnr_file.name
            }
            
        # Extract reconstructs and targets
        reconstruct_matches = re.finditer(
            r"(reconstruct|selector)\s+[\"']([^\"']+)[\"']\s*->\s*([A-Za-z0-9_]+)",
            content
        )
        for match in reconstruct_matches:
            block_type = match.group(1)
            selector = match.group(2)
            component = match.group(3)
            
            # Extract urlPattern if present inside the block
            # We look downstream from the match to find urlPattern: "..."
            block_start = match.end()
            # Simple bracket match lookup
            block_body = ""
            bracket_count = 0
            for char in content[block_start:]:
                if char == '{':
                    bracket_count += 1
                elif char == '}':
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
                "file": vnr_file.name
            })
            
    return {
        "status": "success",
        "workspace_path": str(workspace_dir),
        "files_indexed": [f.name for f in vnr_files],
        "declared_classes": declared_classes,
        "mapped_routes": mapped_routes
    }


def main():
    parser = argparse.ArgumentParser(description="Static AST indexer for Veneer projects")
    parser.add_argument("workspace_dir", help="Project folder containing VNR files")
    
    args = parser.parse_args()
    ws_path = Path(args.workspace_dir).resolve()
    
    if not ws_path.is_dir():
        print(json.dumps({"status": "error", "message": f"Not a directory: {ws_path}"}))
        return 1
        
    result = index_workspace(ws_path)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    main()
