#!/usr/bin/env python3
"""
Workspace Indexer for Veneer Spec Projects.
Scans the project workspace to compile a map of declared classes,
mapped routes, and active components to serve as a global context payload
for the subagent.
"""
import argparse
import json
import sys
from pathlib import Path

from veneer_coder.workspace import index_workspace


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
    sys.exit(main())
