"""
Configuration schema for training profiles.

Each preset (under presets/*.yaml) is validated against this schema. This prevents
common errors found in hand-written training scripts such as incorrect, missing,
or inconsistently spelled configuration keys.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ModelConfig:
    name: str  # ex: "unsloth/Qwen2.5-Coder-0.5B-Instruct"
    chat_template: str  # ex: "qwen-2.5", "llama-3"
    max_seq_length: int = 1024
    load_in_4bit: bool = True
    dtype: Optional[str] = None  # None = auto-detect (fp16/bf16)


@dataclass
class LoraConfig:
    r: int = 16
    lora_alpha: int = 16
    lora_dropout: float = 0.0
    bias: str = "none"
    target_modules: list = field(
        default_factory=lambda: [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ]
    )
    use_gradient_checkpointing: str = "unsloth"
    use_rslora: bool = False
    random_state: int = 3407


@dataclass
class DatasetConfig:
    path: str = "dataset.jsonl"
    format: str = "json"       # passado pro load_dataset()
    split: str = "train"
    messages_field: str = "messages"
    num_proc: int = 2
    packing: bool = False
    # Optional mapping, only used if the dataset is not already in {"role", "content"} format
    # e.g., {"from": "role", "value": "content"} for ShareGPT schema
    field_mapping: Optional[dict] = None


@dataclass
class TrainingConfig:
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 8
    warmup_steps: int = 5
    max_steps: int = 100
    num_train_epochs: Optional[float] = None  # se setado, ignora max_steps
    learning_rate: float = 2e-4
    logging_steps: int = 1
    optim: str = "adamw_8bit"
    weight_decay: float = 0.01
    lr_scheduler_type: str = "linear"
    seed: int = 3407


@dataclass
class RunConfig:
    """Um preset completo de treinamento."""
    preset_name: str
    description: str = ""
    output_root: str = "outputs"
    model: ModelConfig = field(default_factory=ModelConfig)
    lora: LoraConfig = field(default_factory=LoraConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)

    @staticmethod
    def from_dict(preset_name: str, data: dict[str, Any]) -> "RunConfig":
        return RunConfig(
            preset_name=preset_name,
            description=data.get("description", ""),
            output_root=data.get("output_root", "outputs"),
            model=ModelConfig(**data.get("model", {})),
            lora=LoraConfig(**data.get("lora", {})),
            dataset=DatasetConfig(**data.get("dataset", {})),
            training=TrainingConfig(**data.get("training", {})),
        )

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    def apply_overrides(self, overrides: dict[str, Any]) -> "RunConfig":
        """
        Aplica overrides no formato 'secao.campo=valor', ex:
        {'training.max_steps': 200, 'lora.r': 32}
        Retorna uma nova RunConfig (não muta a original).
        """
        new = dataclasses.replace(self)
        for section in ("model", "lora", "dataset", "training"):
            setattr(new, section, dataclasses.replace(getattr(self, section)))

        for dotted_key, value in overrides.items():
            if "." not in dotted_key:
                raise ValueError(
                    f"Invalid override '{dotted_key}': use 'section.field=value' "
                    f"(e.g. training.max_steps=200)"
                )
            section, field_name = dotted_key.split(".", 1)
            target = getattr(new, section, None)
            if target is None:
                raise ValueError(f"Unknown configuration section: '{section}'")
            if not hasattr(target, field_name):
                raise ValueError(f"Unknown configuration field: '{section}.{field_name}'")
            current_value = getattr(target, field_name)
            cast_value = _cast_like(value, current_value)
            setattr(target, field_name, cast_value)
        return new


def _cast_like(value: Any, reference: Any) -> Any:
    """Converts a CLI string parameter to the same type as the reference value (int/float/bool/etc.)."""
    if not isinstance(value, str):
        return value
    if isinstance(reference, bool):
        return value.strip().lower() in ("1", "true", "yes", "y", "on")
    if isinstance(reference, int):
        return int(value)
    if isinstance(reference, float):
        return float(value)
    return value
