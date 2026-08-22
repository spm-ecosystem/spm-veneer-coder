# Veneer Coder (`spm-veneer-coder`)

`spm-veneer-coder` is a compiler-aware, fine-tuned LLM subagent for generating valid **Veneer Spec (.vnr)** code, CSS rules, and modernizing legacy HTML into React Shadow DOM interfaces.

Rather than acting as a generic conversational LLM, `veneer-coder` is designed as a **specialized coding subagent** that operates within a self-correction loop powered by compiler (`spm-cli`) diagnostic feedback.

---

## Repository Structure

```text
spm-veneer-coder/
├── train.py              # CLI entry point for training & dataset compilation
├── agent.py              # Self-correcting interactive CLI agent wrapper
├── subagent_cli.py       # Programmatic JSON delegation interface for parent agents
├── pyproject.toml        # Package definition and dependencies
├── scripts/              # Helper automation scripts
│   ├── scaffold_env.py   # Automated environment scaffolder
│   └── workspace_indexer.py # Workspace AST context summarizer
├── presets/              # Versioned training configuration profiles
│   ├── qwen2.5-coder-0.5b.yaml
│   ├── qwen2.5-coder-1.5b.yaml
│   ├── qwen2.5-coder-7b.yaml
│   └── llama3-8b.yaml
├── in/                   # Grounded training source datasets & spec references
│   ├── veneer-spec-reference.md
│   └── dataset/
├── veneer_coder/         # Subagent core engine package
│   ├── __init__.py
│   ├── agent.py          # Strict self-correction execution loop
│   ├── compiler.py       # ValidationStatus enum and spm-cli integration
│   ├── extraction.py     # Robust code block extractors
│   ├── ollama.py         # Ollama HTTP API client
│   └── workspace.py      # Workspace indexer logic
├── tests/                # Unit and golden evaluation test suites
│   ├── test_presets_and_train.py
│   ├── test_evals.py
│   └── evals/
└── outputs/              # Versioned model adapters and artifacts
```

---

## Installation & Setup

Ensure you are using **Python 3.10+**. Set up your environment:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install package in editable mode with dev dependencies
pip install -e ".[dev]"
```

---

## Model Training & Dataset Pipeline

`spm-veneer-coder` utilizes `spm-finetune` for dataset compilation and training execution.

### 1. Recompiling the Dataset
Rebuilds `dataset.jsonl` from the authoritative spec reference document and dataset cases in `in/`:
```bash
python train.py compile-dataset --preset presets/qwen2.5-coder-1.5b.yaml --output dataset.jsonl
```

### 2. Listing Presets
View all available configuration presets:
```bash
python train.py --help
```

### 3. Training a Model
To run fine-tuning using a preset profile:
```bash
python train.py train --preset presets/qwen2.5-coder-1.5b.yaml
```

To dry-run and validate configuration resolution without requiring GPU/model loading:
```bash
python train.py train --preset presets/qwen2.5-coder-1.5b.yaml --dry-run
```

---

## Local Subagent & Self-Correction Architecture

The fine-tuned GGUF model runs locally via **Ollama** and wraps execution in a compiler-validated self-correction loop.

```text
        Parent Agent (e.g. Antigravity)
                     │
                     │ task prompt + HTML
                     ▼
             ┌──────────────┐
             │ veneer-coder │
             │  0.5B / 1.5B │
             └──────┬───────┘
                    │
                    │ .vnr
                    ▼
                spm-cli
                    │
                compile
                    │
              ┌─────┴─────┐
              │           │
            valid       error
              │           │
              ▼           └──────► self-correction retry
           output
```

### 1. Registering the Model in Ollama
Build the model in Ollama from compiled GGUF weights:
```bash
ollama create veneer-coder -f outputs/qwen2.5-coder-1.5b/v1/gguf_gguf/Modelfile
```

### 2. Invoking the Interactive Agent
Use `agent.py` to generate Veneer Spec code with strict compilation validation:
```bash
python agent.py "Reconstruct the forum feed: map #forum-posts -> UiTableListPage"
```

If compilation fails, `agent.py` feeds compiler diagnostics back to the model for auto-correction. Reaching max retries without successful compilation raises an explicit error rather than returning invalid code.

### 3. Subagent Delegation (JSON Protocol Interface)
For automated subagent delegation from parent agents, use `subagent_cli.py`:

```bash
python subagent_cli.py --input-json '{"task": "Map search", "html_path": "page.html", "env_dir": "site-x"}'
```

#### Input JSON Schema
```json
{
  "task": "Reconstruct feed to UiModernGridPage mapping items to UiImageCard",
  "html_path": "/path/to/page-snapshot.html",
  "env_dir": "/path/to/environment"
}
```

#### Output JSON Schema (Success)
```json
{
  "status": "success",
  "vnr_file": "/path/to/environment/environment.vnr",
  "css_file": "/path/to/environment/content.css",
  "manifest_file": "/path/to/environment/manifest.json",
  "retries_used": 1,
  "compilation_log": "Compiled manifest.json successfully."
}
```

---

## Testing & Golden Evaluation Suite

Run the unit tests and golden evaluation suite:
```bash
pytest tests/ -v
```

The golden evaluation suite (`tests/evals/golden_eval_suite.json`) evaluates:
- **Compiler Validity:** Ensures generated VNR code compiles cleanly via `spm-cli`.
- **Extractor Recall:** Verifies extractor pipes (`hrefOrOnclick`, `nextSiblingText`, `hiddenInputs`, `selector`).
- **Class Inheritance & Scoping:** Verifies `extends` syntax and property binding.
- **Contrastive Intent:** Validates handling of non-VNR conversational inputs.
