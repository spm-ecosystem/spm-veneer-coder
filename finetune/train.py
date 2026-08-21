"""
Unified training, dataset compilation, model exporting, and stress testing entrypoint.

Usage:
    # 1. Compile the dataset from reference doc
    python finetune/train.py --build-dataset

    # 2. Train a model with a preset
    python finetune/train.py --preset qwen2.5-coder-0.5b
    python finetune/train.py --preset llama3-8b --set training.max_steps=300

    # 3. Export a trained model adapter to GGUF
    python finetune/train.py --export-gguf outputs/qwen2.5-coder-0.5b/v1/adapter --export-output veneer_qwen_gguf

    # 4. Run concurrency stress test against Ollama server
    python finetune/train.py --stress-test --stress-requests 50 --stress-workers 5
"""
from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import json
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

import yaml

from configs import RunConfig
from registry import list_presets, load_preset

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


def parse_overrides(raw_overrides: list[str]) -> dict:
    overrides = {}
    for item in raw_overrides:
        if "=" not in item:
            raise SystemExit(
                f"Invalid --set override: '{item}'. Expected format: section.field=value "
                f"(e.g. --set training.max_steps=200)"
            )
        key, value = item.split("=", 1)
        overrides[key.strip()] = value.strip()
    return overrides


def next_run_dir(output_root: str, preset_name: str) -> Path:
    # Resolve output path relative to workspace root if it's relative
    base = Path(output_root)
    if not base.is_absolute():
        base = WORKSPACE_ROOT / base
    base = base / preset_name
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
    # Heavy machine learning imports deferred to prevent overhead on CPU commands
    from unsloth import FastLanguageModel, is_bfloat16_supported
    from unsloth.chat_templates import get_chat_template
    from datasets import load_dataset
    from trl import SFTTrainer
    from transformers import TrainingArguments

    print(f"[{cfg.preset_name}] Loading base model: {cfg.model.name}")
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

    # Resolve dataset path relative to workspace root if relative
    dataset_path = Path(cfg.dataset.path)
    if not dataset_path.is_absolute():
        dataset_path = WORKSPACE_ROOT / dataset_path

    print(f"[{cfg.preset_name}] Loading dataset: {dataset_path}")
    dataset = load_dataset(cfg.dataset.format, data_files=str(dataset_path), split=cfg.dataset.split)
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

    print(f"[{cfg.preset_name}] Starting training run -> {run_dir}")
    start = time.time()
    trainer_stats = trainer.train()
    duration = time.time() - start
    print(f"[{cfg.preset_name}] Training completed in {duration:.1f}s")

    adapter_dir = run_dir / "adapter"
    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))
    print(f"[{cfg.preset_name}] LoRA adapter saved to {adapter_dir}")

    metadata = {
        "preset": cfg.preset_name,
        "base_model": cfg.model.name,
        "duration_seconds": round(duration, 1),
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "trainer_stats": getattr(trainer_stats, "metrics", None),
    }
    with open(run_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def run_dataset_build() -> None:
    src_file = WORKSPACE_ROOT / "in/veneer-spec-reference.md"
    dest_file = WORKSPACE_ROOT / "dataset.jsonl"

    print(f"[Dataset Compiler] Reading reference from {src_file}")
    if not src_file.exists():
        raise FileNotFoundError(f"Source reference markdown not found at {src_file}")

    with open(src_file, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    blocks = []
    current_h2 = ""
    current_h3 = ""
    pending_context = []
    i = 0

    while i < len(lines):
        line = lines[i]
        h2 = re.match(r"^##\s+(.*)", line)
        h3 = re.match(r"^###\s+(.*)", line)
        if h2 and not line.startswith("###"):
            current_h2 = h2.group(1).strip()
            current_h3 = ""
            pending_context = []
            i += 1
            continue
        if h3:
            current_h3 = h3.group(1).strip()
            pending_context = []
            i += 1
            continue
        if line.strip() == "```vnr":
            i += 1
            code_lines = []
            while i < len(lines) and lines[i].strip() != "```":
                code_lines.append(lines[i])
                i += 1
            code = "\n".join(code_lines).strip("\n")
            ctx_text = " ".join(pending_context).strip()
            blocks.append({
                "h2": current_h2,
                "h3": current_h3,
                "context": ctx_text,
                "code": code,
            })
            pending_context = []
            i += 1
            continue
        stripped = line.strip()
        if stripped and not stripped.startswith("```") and not stripped.startswith("|"):
            pending_context.append(stripped)
            pending_context = pending_context[-6:]
        i += 1

    print(f"[Dataset Compiler] Extracted {len(blocks)} Veneer Spec code blocks")

    system_prompt = (
        "You are an expert assistant for Veneer Spec (.vnr), the declarative "
        "layout-override DSL compiled by spm-cli for the Site Package Manager "
        "(SPM) ecosystem. You write correct, idiomatic .vnr source, explain "
        "what existing .vnr code does, and help debug compiler errors."
    )
    examples = []

    def add(messages):
        examples.append({"messages": [{"role": "system", "content": system_prompt}] + messages})

    explain_templates = [
        "Explain what the following Veneer Spec (.vnr) code does:\n\n```vnr\n{code}\n```",
        "What does this .vnr snippet compile to / achieve? \n\n```vnr\n{code}\n```",
        "Walk me through this Veneer Spec block line by line:\n\n```vnr\n{code}\n```",
        "I found this in a spm-cli theme project. What is it doing?\n\n```vnr\n{code}\n```",
    ]

    generate_templates = [
        "Write a Veneer Spec (.vnr) snippet that does the following: {ctx}",
        "In .vnr syntax, {ctx_lower}",
        "Show me how to accomplish this in Veneer Spec: {ctx}",
        "I'm building an spm-cli theme. {ctx} Give me the .vnr code.",
    ]

    def clean_ctx(c):
        c = c.strip()
        c = re.sub(r"\s+", " ", c)
        return c

    for b in blocks:
        code = b["code"]
        if not code.strip():
            continue
        # Skip error examples in general loops
        if b["h2"].strip().startswith("17."):
            continue
        ctx = clean_ctx(b["context"])
        raw_heading = b["h3"] or b["h2"]
        heading = re.sub(r"^\d+(\.\d+)*\s+", "", raw_heading).strip()

        # 1. Explanations
        explanation = (
            f"This snippet is an example of **{heading}** in Veneer Spec.\n\n"
            + (f"Context: {ctx}\n\n" if ctx else "")
            + "```vnr\n" + code + "\n```\n\n"
            + "When compiled with `spm-cli`, this is lexed, parsed into an AST, "
            "resolved (class inheritance and scoping applied), and emitted into the "
            "target `manifest.json`, following the rules for this construct described "
            "in the Veneer Spec language reference."
        )
        explain_tpls = random.sample(explain_templates, k=2)
        for tpl in explain_tpls:
            user_msg = tpl.format(code=code)
            add([
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": explanation},
            ])

        # 2. Code Generation
        if ctx and len(ctx) > 25:
            ctx_lower = ctx[0].lower() + ctx[1:] if ctx else ctx
            gen_tpls = random.sample(generate_templates, k=2)
            assistant_msg = f"```vnr\n{code}\n```"
            for tpl in gen_tpls:
                user_msg = tpl.format(ctx=ctx, ctx_lower=ctx_lower)
                add([
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": assistant_msg},
                ])

        # 3. Code Completion
        code_lines = code.split("\n")
        if len(code_lines) >= 6:
            cut = max(2, len(code_lines) // 2)
            partial = "\n".join(code_lines[:cut])
            user_msg = (
                "Complete this Veneer Spec snippet in a way that is consistent with "
                f"the `{heading}` construct:\n\n```vnr\n{partial}\n...\n```"
            )
            assistant_msg = f"```vnr\n{code}\n```"
            add([
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": assistant_msg},
            ])

    # 4. Error/Debugging Examples
    err_section_match = text.split("## 17. Common Errors, Anti-Patterns & Fixes")
    if len(err_section_match) > 1:
        err_section = err_section_match[1].split("## 18.")[0]
        subsections = re.split(r"(?=^### 17\.\d)", err_section, flags=re.M)
        for sub in subsections:
            sub_blocks = re.findall(r"```vnr\n(.*?)\n```", sub, re.S)
            bad = next((c for c in sub_blocks if "❌" in c), None)
            good = next((c for c in sub_blocks if "✅" in c), None)
            if not bad or not good:
                continue
            bad_comment_match = re.search(r"//\s*❌\s*(.*)", bad)
            err_desc = bad_comment_match.group(1).strip() if bad_comment_match else "a compile-time error"
            user_msg = (
                "The following Veneer Spec code fails to compile "
                f"({err_desc}). What's wrong, and how do I fix it?\n\n```vnr\n{bad}\n```"
            )
            assistant_msg = (
                f"The problem: {err_desc}.\n\nHere is the corrected version:\n\n```vnr\n{good}\n```"
            )
            add([
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": assistant_msg},
            ])

    # 5. Concept Q&A Pairs
    qa_pairs = [
        ("What are the base extractors available in a Veneer Spec binding expression?",
         "Veneer Spec supports seven base extractors: `text` (textContent of the matched element), "
         "`html` (innerHTML), `attr:<name>` (a named attribute value, e.g. `attr:src`), "
         "`hrefOrOnclick` (resolves a link destination from `href` or a fallback inline `onclick`), "
         "`nextSiblingText` (text content of the immediate next sibling element), `hiddenInputs` "
         "(collects all `<input type=\"hidden\">` descendants as a JSON array string), and `selector` "
         "(generates a unique selector string for the matched element itself)."),
        ("What pipe operations can follow a base extractor in a Veneer Spec bind expression?",
         "Four pipe operations are supported, chained with `|`: `split` (splits a space-separated "
         "string into a JSON array of tokens), `split:<delimiter>` (splits by a custom delimiter and "
         "trims each token), `number` (parses a valid number string into a native JSON number), and "
         "`cleanNumber` (strips currency symbols like `$`, `R$`, `€`), commas, and spacing, then "
         "parses the value into a JSON float number (e.g. `\"$ 1,200.50\"` -> `1200.5`)."),
        ("What is the difference between `number` and `cleanNumber` pipes, and when should each be used?",
         "`number` expects an already-clean numeric string (e.g. quantities, IDs, ratings) and converts "
         "it directly to a JSON number. `cleanNumber` is meant for currency-adjacent values: it first "
         "strips symbols such as `$`, `R$`, `€`, thousands-separator commas, and surrounding whitespace, "
         "then parses the result as a float. Use `number` for plain digits, `cleanNumber` whenever a "
         "price or formatted amount might be present."),
        ("What does `self` mean inside a Veneer Spec bind expression?",
         "`self` refers to the element already matched by the enclosing `selector`, `reconstruct`, or "
         "`child` block — it does not run a new DOM query. Use it to read a property (text, attribute) "
         "of the matched element itself, as opposed to a relative CSS selector which queries inside/among "
         "its descendants or siblings."),
        ("How does Veneer Spec's raw string literal syntax work, and why would you use it?",
         "Raw string literals use C++-style syntax `R\"(content)\"`, or `R\"delim(content)delim\"` with a "
         "custom delimiter when the content itself contains the closing sequence `)\"`. Everything between "
         "the delimiters is treated as a literal, unescaped string — no backslash-escaping needed. This is "
         "primarily used for regular expressions (like `urlPattern`) and inline JSON blocks (like `columns` "
         "or `tagGroups`), which would otherwise require painful escaping of backslashes and quotes."),
        ("How does implicit JSON type deserialization work when Veneer Spec emits property values?",
         "When emitting a property to the manifest JSON, the compiler checks whether the written value "
         "parses as a valid JSON type — a number, boolean, array, or object. If it does, that native JSON "
         "type is emitted (e.g. `mobileColumns: 2;` becomes the number `2`, `showSearch: true;` becomes "
         "the boolean `true`, and a raw-string JSON array becomes a native array). If parsing fails (e.g. "
         "`\"280px\"` or a zip code with a leading zero like `\"02139\"`), the value is emitted as a plain "
         "JSON string instead."),
        ("What is the compile-time cost of `class` declarations in Veneer Spec?",
         "Zero. Classes are resolved entirely at compile time — the resolver builds an inheritance graph, "
         "propagates bound properties and scoping rules from parent to child classes, and checks for "
         "circular dependencies — but classes themselves never appear in the final emitted manifest.json. "
         "Only the resolved bindings on the concrete `selector`, `reconstruct`, or `child` blocks that use "
         "`extends` show up in the output."),
        ("What happens if two Veneer Spec classes in an inheritance chain both declare a binding with the same name?",
         "The child class's binding wins. If a property or `bind` is declared in both a class and the "
         "class it extends (at any depth in the chain), the child's declaration overrides the parent's "
         "when the classes are resolved."),
        ("What is the difference between `selector` and `reconstruct` in Veneer Spec?",
         "`selector` targets an individual legacy element to hide or replace it in place (e.g. a header, "
         "sidebar, or search box) without touching the rest of the page. `reconstruct` is for full-viewport "
         "or full-section overrides — it targets a large container (a catalog feed, comment board, or "
         "whole page), hides its legacy children, and mounts a React layout component inside an isolated "
         "Shadow DOM host, optionally gated by `urlPattern` or `mediaQuery` constraints."),
        ("What two actions can a `selector` block specify, and what does each do?",
         "`hide` sets `display: none !important` on the matched selector, removing it visually without "
         "mounting any component. `replace` hides the legacy element and mounts a React component "
         "(specified via the `->` arrow syntax) in its place, populated with the block's static props "
         "and any `bind` extractions."),
        ("What is the purpose of the `child` keyword in Veneer Spec, and what does it compile to?",
         "`child` defines a nested list of scraped legacy elements that becomes an array-valued prop on "
         "the parent layout component. It declares a name (which becomes the prop key, e.g. `child items` "
         "-> the `items` prop), a `selector` for the list items, and optional bindings (or an extended "
         "class) describing each item's fields. In the manifest, it becomes an entry in the `children` "
         "array with `name`, `selector`, optional `scope`, and a `propsMap`."),
        ("What does the `preserve` block do inside a `reconstruct`, and what's the risk if the slot name doesn't match anything?",
         "`preserve` keeps specific interactive legacy elements (like a comment form, payment iframe, or "
         "chat widget) alive instead of hiding them, reparenting them into a named slot inside the new "
         "React Shadow DOM layout. It maps a slot name to a legacy CSS selector. The target layout "
         "component must contain a host element with `id=\"{slotName}-container\"` for the reparenting to "
         "work — the compiler cannot validate this against the component's internals, so a mismatched slot "
         "name compiles successfully but fails silently at runtime (the legacy node is removed from the "
         "page but never reappears anywhere)."),
        ("What is the default value of `scope` for a `child` block in Veneer Spec, and when is it omitted from the compiled output?",
         "The default scope is `\"container\"`, meaning selectors inside a `child` block query only "
         "descendants of the enclosing `selector`/`reconstruct` container. Because `\"container\"` is the "
         "default, the compiler omits the `scope` key entirely from the emitted manifest when it's either "
         "unset or explicitly set to `\"container\"` — only `scope: \"document\";` (used for elements "
         "physically outside the container, like global pagination) is emitted."),
        ("How does spm-cli handle a directory full of .vnr files during compilation?",
         "Running `spm compile <directory> -o manifest.json` recursively scans all `.vnr` files under the "
         "target path, regardless of file name or nesting depth (Java-style nested packages like "
         "`core/models/`, `layout/headers/`, `pages/gallery/` are fully supported). It concatenates their "
         "source contents and resolves class blueprints globally across the whole tree in a single "
         "compilation pass."),
        ("What is Sibling Class Autoloading in spm-cli, and when does it trigger?",
         "When compiling a single `.vnr` file in isolation (linter mode, e.g. from an editor), if the "
         "compiler encounters a class reference (`extends SomeClass`) that isn't declared in the current "
         "file, it automatically inspects the file's directory and loads sibling `.vnr` files in the "
         "background solely to resolve that class blueprint. This enables accurate background validation "
         "without requiring a full workspace compile, but it only searches the same directory — classes "
         "in unrelated top-level directories won't be found this way."),
        ("What does spm-cli's metadata merge behavior do when recompiling over an existing manifest.json?",
         "During `spm compile`, the CLI parses any preexisting target `manifest.json` and performs a deep "
         "merge on the `theme` block: global metadata fields like `author`, `description`, `targetUrl`, "
         "and `minEngineVersion` already present in the destination file are preserved and merged back "
         "into the newly compiled output, so GitOps-style metadata survives repeated compilations without "
         "manual restoration."),
        ("Why would a Veneer Spec author choose `attr:src` combined with `nextSiblingText` versus a single selector?",
         "`attr:<name>` reads an attribute off the *matched* element (e.g. an `<img>`'s `src`), while "
         "`nextSiblingText` reads the text content of whatever element immediately follows the matched "
         "node in the DOM — useful when a label and its value are adjacent siblings rather than nested "
         "(e.g. `<span class=\"label\">Price</span><span>$19.99</span>`, where matching `.label` and "
         "piping through `nextSiblingText` grabs the price text from the sibling)."),
        ("Give an example of a value that should NOT rely on Veneer Spec's implicit JSON number coercion, and explain why.",
         "An all-digit identifier with no leading zero and no other characters — e.g. a 10-digit phone "
         "number or account number like `\"10023491\"` — will be silently coerced into a JSON number "
         "during emission, which can lose formatting significance or exceed safe-integer precision for "
         "very large values. Values like postal codes with a leading zero (`\"02139\"`) are safe because "
         "the leading zero makes them invalid as a JSON number, so they stay strings; but plain numeric "
         "IDs are not protected this way and should be reviewed if string-preservation matters."),
    ]

    for q, a in qa_pairs:
        add([
            {"role": "user", "content": q},
            {"role": "assistant", "content": a},
        ])

    # Shuffle for better general training
    random.seed(42)
    random.shuffle(examples)

    print(f"[Dataset Compiler] Compiling {len(examples)} instruction-tuning examples...")
    with open(dest_file, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"[Dataset Compiler] Successfully wrote dataset -> {dest_file}")


def run_export_gguf(adapter_path: str, output_name: str, quant_method: str) -> None:
    # Heavy ML imports deferred
    from unsloth import FastLanguageModel

    abs_adapter = Path(adapter_path)
    if not abs_adapter.is_absolute():
        abs_adapter = WORKSPACE_ROOT / abs_adapter

    abs_output = Path(output_name)
    if not abs_output.is_absolute():
        abs_output = WORKSPACE_ROOT / abs_output

    print(f"[Exporter] Loading trained model and adapter from {abs_adapter}...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(abs_adapter),
        max_seq_length=1024,
        load_in_4bit=True,
    )

    print(f"[Exporter] Saving model in GGUF format ({quant_method}) to {abs_output}...")
    model.save_pretrained_gguf(
        str(abs_output),
        tokenizer,
        quantization_method=quant_method,
    )
    print(f"[Exporter] Successfully exported GGUF model!")


def stress_test_worker(task_id: int, model_name: str) -> tuple[int, bool, float, str]:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": f"Reconstruct task {task_id}: map #element-{task_id} to UiComponent{task_id}",
        "stream": False,
        "options": {"temperature": 0.2},
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            res = json.loads(response.read().decode("utf-8"))
            duration = time.time() - start
            return task_id, True, duration, res.get("response", "").strip()
    except Exception as e:
        return task_id, False, time.time() - start, str(e)


def run_stress_test(num_requests: int, max_workers: int, model_name: str) -> None:
    print(f"[Stress Test] Starting test: {num_requests} requests, {max_workers} concurrent workers on model '{model_name}'")

    start_total = time.time()
    successes = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(stress_test_worker, i, model_name)
            for i in range(num_requests)
        ]

        for future in concurrent.futures.as_completed(futures):
            task_id, success, duration, result = future.result()
            if success:
                successes += 1
                output = result.replace("\n", " ")[:80]
                print(f"[SUCCESS] Task {task_id:04d} | Duration: {duration:7.2f}s | Output: {output}...")
            else:
                print(f"[ERROR]   Task {task_id:04d} | Duration: {duration:7.2f}s | Error: {result}")

    total_time = time.time() - start_total
    failures = num_requests - successes
    throughput = num_requests / total_time if total_time > 0 else 0

    print("\n" + "=" * 60)
    print("STRESS TEST SUMMARY")
    print("=" * 60)
    print(f"Total requests : {num_requests}")
    print(f"Successful     : {successes}")
    print(f"Failed         : {failures}")
    print(f"Total duration : {total_time:.2f}s")
    print(f"Throughput     : {throughput:.2f} req/s")
    print("=" * 60)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Unified Veneer Spec Fine-Tuning CLI")

    # Command selectors
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--preset", help="Name of the preset to train (see --list)")
    action_group.add_argument("--list", action="store_true", help="List all available presets and exit")
    action_group.add_argument("--build-dataset", action="store_true", help="Build dataset.jsonl from reference docs")
    action_group.add_argument("--export-gguf", metavar="ADAPTER_PATH", help="Export adapter to GGUF format")
    action_group.add_argument("--stress-test", action="store_true", help="Run Ollama concurrency stress test")

    # Options for train
    parser.add_argument(
        "--set", dest="overrides", action="append", default=[],
        help="Override configuration values (e.g. --set training.max_steps=200)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Dry run configuration verification for the training preset without starting GPU session",
    )

    # Options for GGUF export
    parser.add_argument("--export-output", default="veneer_qwen_gguf", help="Output directory/name for GGUF")
    parser.add_argument("--export-quant", default="q4_k_m", help="GGUF quantization method (default: q4_k_m)")

    # Options for stress test
    parser.add_argument("--stress-requests", type=int, default=100, help="Number of total stress test requests")
    parser.add_argument("--stress-workers", type=int, default=10, help="Max parallel workers for stress test")
    parser.add_argument("--stress-model", default="veneer-coder", help="Ollama model ID to target")

    args = parser.parse_args(argv)

    if args.list:
        presets = list_presets()
        if not presets:
            print("No presets found under presets/")
        for name in presets:
            cfg = load_preset(name)
            desc = f" — {cfg.description}" if cfg.description else ""
            print(f"  {name}{desc}")
        return 0

    if args.build_dataset:
        run_dataset_build()
        return 0

    if args.export_gguf:
        run_export_gguf(args.export_gguf, args.export_output, args.export_quant)
        return 0

    if args.stress_test:
        run_stress_test(args.stress_requests, args.stress_workers, args.stress_model)
        return 0

    # Fallback to Preset Training
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
