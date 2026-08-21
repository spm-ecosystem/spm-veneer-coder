"""
Preset Registry: each .yaml file under presets/ becomes a selectable preset
by name (the filename, without extension).

To add a new preset, create a new .yaml file. There is no need to modify
any Python code.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from configs import RunConfig

PRESETS_DIR = Path(__file__).parent / "presets"


def list_presets() -> list[str]:
    return sorted(p.stem for p in PRESETS_DIR.glob("*.yaml"))


def load_preset(name: str) -> RunConfig:
    path = PRESETS_DIR / f"{name}.yaml"
    if not path.exists():
        available = ", ".join(list_presets()) or "(no presets found)"
        raise FileNotFoundError(
            f"Preset '{name}' does not exist in {PRESETS_DIR}.\n"
            f"Available presets: {available}"
        )
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return RunConfig.from_dict(name, data)
