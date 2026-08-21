"""
Registro de presets: cada arquivo .yaml em presets/ vira um preset
selecionável por nome (o nome do arquivo, sem extensão).

Adicionar um preset novo = adicionar um .yaml novo. Não precisa tocar
em código Python.
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
        available = ", ".join(list_presets()) or "(nenhum preset encontrado)"
        raise FileNotFoundError(
            f"Preset '{name}' não existe em {PRESETS_DIR}.\n"
            f"Presets disponíveis: {available}"
        )
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return RunConfig.from_dict(name, data)
