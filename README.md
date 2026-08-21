# Fine-Tuning with Versioned Presets

Previously, each training run required manually copying and editing Python scripts (with comments like `# CHANGE 1`, `# CHANGE 2`), leaving no record of which configuration generated which adapter. Now, everything is structured and versioned:

```
finetune/
  configs.py       # Configuration schemas (dataclasses) defining what a preset can contain
  registry.py      # Dynamic registry loader for presets/*.yaml files
  train.py         # Unified CLI for training, dataset building, GGUF exporting, and stress testing
  presets/         # Training configuration profiles
    qwen2.5-coder-0.5b.yaml
    llama3-8b.yaml
```

## Installation & Setup

Ensure you are using **Python 3.13**. Set up your environment and install the dependencies:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
pip install "unsloth @ git+https://github.com/unslothai/unsloth.git"
pip install datasets trl transformers peft accelerate bitsandbytes xformers
pip install unsloth_zoo
```

## CLI Usage

### 1. Recompiling the Dataset
Rebuilds the `dataset.jsonl` instruction-tuning set from the authoritative spec reference document:
```bash
python finetune/train.py --build-dataset
```

### 2. Listing Presets
View all available configuration presets and their descriptions:
```bash
python finetune/train.py --list
```

### 3. Training a Model
To run training using a specific preset:
```bash
python finetune/train.py --preset qwen2.5-coder-0.5b
```

To run training overriding specific parameters on the fly, without modifying the YAML file:
```bash
python finetune/train.py --preset qwen2.5-coder-0.5b \
    --set training.max_steps=300 \
    --set lora.r=32 \
    --set training.learning_rate=1e-4
```

To dry-run and validate the final resolved configuration (without loading the model or requiring a GPU):
```bash
python finetune/train.py --preset llama3-8b --set training.max_steps=50 --dry-run
```

### 4. Exporting to GGUF
To merge the trained adapter weights with the base model and quantize them into a lightweight GGUF file:
```bash
python finetune/train.py --export-gguf outputs/qwen2.5-coder-0.5b/v1/adapter \
    --export-output veneer_qwen_gguf \
    --export-quant q4_k_m
```

### 5. Concurrency Stress Test
Run concurrent request simulations against your local Ollama server hosting the fine-tuned model:
```bash
python finetune/train.py --stress-test --stress-requests 100 --stress-workers 10 --stress-model veneer-coder
```

---

## Exposing as a Local Subagent (Ollama + Self-Correction)

You can run the fine-tuned model locally via **Ollama** and wrap it in a self-correcting compiler subagent CLI that can be easily integrated into any workspace or automation script.

### 1. Registering the Model in Ollama
Run the following commands to build the model in Ollama from the compiled GGUF weights:
```bash
cd veneer_qwen_gguf_gguf
ollama create veneer-coder -f Modelfile
```

### 2. Invoking the Subagent
Use the provided `finetune/agent.py` script to generate Veneer Spec code. The script:
1. Queries the local `veneer-coder` Ollama model.
2. Extracts the generated code.
3. Automatically runs compilation checks using `spm compile`.
4. If a compiler error is found, it feeds the diagnostics back to the LLM to **auto-correct the code** (up to 3 validation passes).
5. Outputs only validated, compile-passing `.vnr` code.

```bash
# Direct task description via arguments
python finetune/agent.py "Reconstruct the forum feed: map #forum-posts -> UiTableListPage"

# Reading from stdin and saving the validated result to a file
echo "Create a search form replacement for #searchform -> UiSearchBar" | python finetune/agent.py -o search.vnr
```

### 3. Automated QA Environment Scaffolding
To completely scaffold a QA testing environment (generating the `<env>.vnr`, `content.css`, and compiled `manifest.json` from its local `task.md` and `page-snapshot.html` files), run the environment scaffolder:
```bash
python finetune/scaffold_env.py /home/watashi/Projects/spm-qa-test-suite/environments/site-j-stackoverflow
```
The scaffolder automatically:
1. Locates the task brief (`task.md`) and page snapshot HTML in the target folder.
2. Formulates a prompt combining the instructions and raw HTML structure.
3. Queries the local `veneer-coder` model.
4. Extracts both VNR and CSS outputs.
5. Performs local compilation syntax validation and repeats with error feedback for self-correction.
6. Saves the compiled `<env_name>.vnr` and `content.css` files, and triggers the final local compile step producing the resolved `manifest.json`.

---

## Adding New Presets

To create a new training profile:
1. Copy an existing `.yaml` file under `finetune/presets/`.
2. Modify the desired parameters (base model, chat template, LoRA rank, dataset paths, or trainer hyperparameters).
3. Save it under a new filename. The filename automatically determines the preset's CLI name. No changes to `train.py` are needed.

---

## Run Versioning and Artifacts

Every training run automatically generates a versioned subdirectory under the output root, ensuring no output is ever overwritten:
```
outputs/
  qwen2.5-coder-0.5b/
    v1/
      config.yaml      <- The exact resolved configuration used (preset + CLI overrides)
      metadata.json     <- Train duration, timestamp, base model, and loss metrics
      adapter/           <- Saved LoRA adapters and tokenizers
      checkpoints/       <- Intermediate checkpoints generated by the Trainer
    v2/
      ...
```
This guarantees you can always trace any adapter back to the exact parameters that produced it.

---

## Dataset Format

The dataset config `dataset.path` points to a `.jsonl` file containing conversation histories formatted as standard chat messages:
```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```
Non-standard datasets should be normalized beforehand to prevent runtime parsing conflicts.
