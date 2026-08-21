"""
Entrypoint único de treinamento.

Uso:
    python train.py --preset qwen2.5-coder-0.5b
    python train.py --preset llama3-8b --set training.max_steps=300 --set lora.r=32
    python train.py --list

Cada execução cria uma pasta versionada nova:
    outputs/<preset>/v1/
    outputs/<preset>/v2/
    ...
dentro dela ficam: o adapter treinado, o tokenizer, o config.yaml
exatamente como foi usado (preset + overrides já aplicados) e um
metadata.json com timestamp/duração/preset base — pra você sempre
saber depois "com que config esse adapter foi gerado".
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
from pathlib import Path

import yaml

from configs import RunConfig
from registry import list_presets, load_preset


def parse_overrides(raw_overrides: list[str]) -> dict:
    overrides = {}
    for item in raw_overrides:
        if "=" not in item:
            raise SystemExit(
                f"--set inválido: '{item}'. Formato esperado: secao.campo=valor "
                f"(ex: --set training.max_steps=200)"
            )
        key, value = item.split("=", 1)
        overrides[key.strip()] = value.strip()
    return overrides


def next_run_dir(output_root: str, preset_name: str) -> Path:
    base = Path(output_root) / preset_name
    base.mkdir(parents=True, exist_ok=True)
    existing = [
        int(p.name[1:]) for p in base.glob("v*")
        if p.is_dir() and p.name[1:].isdigit()
    ]
    next_version = max(existing, default=0) + 1
    run_dir = base / f"v{next_version}"
    run_dir.mkdir(parents=True)
    return run_dir


def save_run_config(cfg: RunConfig, run_dir: Path) -> None:
    with open(run_dir / "config.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg.to_dict(), f, sort_keys=False, allow_unicode=True)


def run_training(cfg: RunConfig, run_dir: Path) -> None:
    # Import pesado só acontece aqui dentro (não em --list, não em testes de
    # config), então listar presets ou validar overrides não exige GPU/unsloth
    # instalado.
    from unsloth import FastLanguageModel, is_bfloat16_supported
    from unsloth.chat_templates import get_chat_template
    from datasets import load_dataset
    from trl import SFTTrainer
    from transformers import TrainingArguments

    print(f"[{cfg.preset_name}] carregando modelo: {cfg.model.name}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=cfg.model.name,
        max_seq_length=cfg.model.max_seq_length,
        dtype=cfg.model.dtype,
        load_in_4bit=cfg.model.load_in_4bit,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=cfg.lora.r,
        target_modules=cfg.lora.target_modules,
        lora_alpha=cfg.lora.lora_alpha,
        lora_dropout=cfg.lora.lora_dropout,
        bias=cfg.lora.bias,
        use_gradient_checkpointing=cfg.lora.use_gradient_checkpointing,
        random_state=cfg.lora.random_state,
        use_rslora=cfg.lora.use_rslora,
        loftq_config=None,
    )

    tokenizer = get_chat_template(tokenizer, chat_template=cfg.model.chat_template)

    def formatting_prompts_func(examples):
        conversations = examples[cfg.dataset.messages_field]
        texts = [
            tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=False)
            for convo in conversations
        ]
        return {"text": texts}

    print(f"[{cfg.preset_name}] carregando dataset: {cfg.dataset.path}")
    dataset = load_dataset(cfg.dataset.format, data_files=cfg.dataset.path, split=cfg.dataset.split)
    dataset = dataset.map(formatting_prompts_func, batched=True)

    training_kwargs = dict(
        per_device_train_batch_size=cfg.training.per_device_train_batch_size,
        gradient_accumulation_steps=cfg.training.gradient_accumulation_steps,
        warmup_steps=cfg.training.warmup_steps,
        learning_rate=cfg.training.learning_rate,
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=cfg.training.logging_steps,
        optim=cfg.training.optim,
        weight_decay=cfg.training.weight_decay,
        lr_scheduler_type=cfg.training.lr_scheduler_type,
        seed=cfg.training.seed,
        output_dir=str(run_dir / "checkpoints"),
    )
    if cfg.training.num_train_epochs is not None:
        training_kwargs["num_train_epochs"] = cfg.training.num_train_epochs
    else:
        training_kwargs["max_steps"] = cfg.training.max_steps

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=cfg.model.max_seq_length,
        dataset_num_proc=cfg.dataset.num_proc,
        packing=cfg.dataset.packing,
        args=TrainingArguments(**training_kwargs),
    )

    print(f"[{cfg.preset_name}] iniciando treino -> {run_dir}")
    start = time.time()
    trainer_stats = trainer.train()
    duration = time.time() - start
    print(f"[{cfg.preset_name}] treino finalizado em {duration:.1f}s")

    adapter_dir = run_dir / "adapter"
    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))
    print(f"[{cfg.preset_name}] adapter salvo em {adapter_dir}")

    metadata = {
        "preset": cfg.preset_name,
        "base_model": cfg.model.name,
        "duration_seconds": round(duration, 1),
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "trainer_stats": getattr(trainer_stats, "metrics", None),
    }
    with open(run_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Treino com presets versionados")
    parser.add_argument("--preset", help="Nome do preset (ver --list)")
    parser.add_argument(
        "--set", dest="overrides", action="append", default=[],
        help="Override no formato secao.campo=valor (repetível)",
    )
    parser.add_argument("--list", action="store_true", help="Lista presets disponíveis e sai")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Só resolve/valida a config e mostra o que seria usado, sem treinar",
    )
    args = parser.parse_args(argv)

    if args.list:
        presets = list_presets()
        if not presets:
            print("Nenhum preset encontrado em presets/")
        for name in presets:
            cfg = load_preset(name)
            desc = f" — {cfg.description}" if cfg.description else ""
            print(f"  {name}{desc}")
        return 0

    if not args.preset:
        parser.error("--preset é obrigatório (ou use --list para ver as opções)")

    cfg = load_preset(args.preset)
    overrides = parse_overrides(args.overrides)
    if overrides:
        cfg = cfg.apply_overrides(overrides)

    if args.dry_run:
        print(yaml.safe_dump(cfg.to_dict(), sort_keys=False, allow_unicode=True))
        return 0

    run_dir = next_run_dir(cfg.output_root, cfg.preset_name)
    save_run_config(cfg, run_dir)
    run_training(cfg, run_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
