# Fine-tuning com presets versionados

Antes: cada treino era um `.py` copiado e editado à mão (com comentários
tipo `# MUDANÇA 1`, `# MUDANÇA 2`), sem rastro de qual config gerou qual
adapter. Agora:

```
finetune/
  configs.py       # schema (dataclasses) — o que um preset PODE conter
  registry.py       # carrega presets/*.yaml pelo nome
  train.py          # CLI: resolve preset + overrides, roda o treino, versiona a saída
  presets/
    qwen2.5-coder-0.5b.yaml
    llama3-8b.yaml
```

## Uso

```bash
# ver presets disponíveis
python train.py --list

# treinar com um preset como está
python train.py --preset qwen2.5-coder-0.5b

# treinar variando parâmetros pontuais, sem editar o yaml
python train.py --preset qwen2.5-coder-0.5b \
    --set training.max_steps=300 \
    --set lora.r=32 \
    --set training.learning_rate=1e-4

# só validar a config final (sem GPU, sem carregar modelo)
python train.py --preset llama3-8b --set training.max_steps=50 --dry-run
```

## Criar um preset novo

Copie um `.yaml` existente em `presets/`, mude o que quiser (modelo,
`chat_template`, lora, dataset, hiperparâmetros de treino) e salve com
outro nome de arquivo — o nome do arquivo é o nome do preset. Não precisa
tocar em `train.py`.

## Versionamento das runs

Cada `python train.py --preset X` cria uma pasta nova, nunca sobrescreve:

```
outputs/
  qwen2.5-coder-0.5b/
    v1/
      config.yaml      <- config EXATA usada nessa run (preset + overrides já aplicados)
      metadata.json     <- duração, timestamp, métricas do trainer
      adapter/           <- adapter LoRA + tokenizer salvos
      checkpoints/       <- checkpoints intermediários do Trainer
    v2/
      ...
```

Isso resolve o problema de "esse adapter foi treinado com que r? com que
learning rate?" — está tudo em `config.yaml` dentro da própria pasta da
run.

## Dataset

`dataset.path` no preset aponta pro seu `.jsonl` (schema
`{"messages": [{"role": ..., "content": ...}, ...]}`). Se seu dataset usa
outro schema (ex: ShareGPT `{"from", "value"}`), normalize antes — não
tem mapeamento mágico escondido que pode mascarar erro de parsing como
tinha um dos scripts originais.
