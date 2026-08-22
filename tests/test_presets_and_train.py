from pathlib import Path
import json
import yaml
import pytest
from unittest.mock import patch, MagicMock

from spm_finetune.cli.main import main
from spm_finetune.config.resolver import load_preset_with_overrides
from spm_finetune.dataset.markdown import MarkdownDatasetLoader
from spm_finetune.core.models import DatasetSpec


PRESET_DIR = Path(__file__).resolve().parent.parent / "presets"
IN_DATASET_DIR = Path(__file__).resolve().parent.parent / "in" / "dataset"


def test_preset_files_exist():
    expected_presets = [
        "qwen2.5-coder-0.5b.yaml",
        "qwen2.5-coder-1.5b.yaml",
        "qwen2.5-coder-7b.yaml",
        "llama3-8b.yaml",
    ]
    for preset_name in expected_presets:
        preset_file = PRESET_DIR / preset_name
        assert preset_file.exists(), f"Preset file {preset_name} missing"


@pytest.mark.parametrize(
    "preset_name",
    [
        "qwen2.5-coder-0.5b.yaml",
        "qwen2.5-coder-1.5b.yaml",
        "qwen2.5-coder-7b.yaml",
        "llama3-8b.yaml",
    ],
)
def test_preset_loading_and_validation(preset_name):
    preset_path = PRESET_DIR / preset_name
    req = load_preset_with_overrides(str(preset_path))
    assert req.model.repository
    assert req.dataset.path == "in"
    assert req.dataset.format == "composite"
    assert req.backend.name == "unsloth"
    assert req.strategy.type == "lora"
    assert req.output_dir.startswith("outputs/")


def test_cli_list(capsys):
    rc = main(["list"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Available presets:" in captured.out
    assert "qwen2.5-coder-0.5b" in captured.out


@pytest.mark.parametrize(
    "preset_name",
    [
        "qwen2.5-coder-0.5b.yaml",
        "qwen2.5-coder-1.5b.yaml",
        "qwen2.5-coder-7b.yaml",
        "llama3-8b.yaml",
    ],
)
def test_cli_validate(preset_name, capsys):
    preset_path = str(PRESET_DIR / preset_name)
    rc = main(["validate", "--preset", preset_path])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Configuration validation successful:" in captured.out


def test_markdown_dataset_compilation(tmp_path):
    output_file = tmp_path / "compiled_dataset.jsonl"
    preset_path = str(PRESET_DIR / "qwen2.5-coder-0.5b.yaml")
    rc = main(["compile-dataset", "--preset", preset_path, "--output", str(output_file)])
    assert rc == 0
    assert output_file.exists()

    lines = [json.loads(line) for line in output_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) > 100, f"Expected dataset compilation to yield >100 entries, got {len(lines)}"
    for entry in lines:
        assert "messages" in entry
        assert len(entry["messages"]) >= 2
        roles = [m["role"] for m in entry["messages"]]
        assert "user" in roles
        assert "assistant" in roles


@patch("spm_finetune.core.runner.ExperimentRunner.run")
def test_cli_train_invocation(mock_run, tmp_path):
    mock_result = MagicMock()
    mock_result.status.value = "completed"
    mock_result.run_dir = tmp_path / "runs" / "run-1"
    mock_run.return_value = mock_result

    preset_path = str(PRESET_DIR / "qwen2.5-coder-0.5b.yaml")
    rc = main(["train", "--preset", preset_path, "--set", "hyperparameters.max_steps=1"])
    assert rc == 0
    assert mock_run.called
    exp_arg = mock_run.call_args[0][0]
    assert exp_arg.request.hyperparameters["max_steps"] == 1
    assert exp_arg.request.backend.name == "unsloth"
