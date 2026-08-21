from unsloth import FastLanguageModel

# Carrega o seu adapter recém-treinado junto com o base
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "outputs/qwen2.5-coder-0.5b/v2/adapter", 
    max_seq_length = 1024,
    load_in_4bit = True,
)

# Exporta e salva localmente no formato GGUF (quantização q4_k_m é excelente e leve)
model.save_pretrained_gguf(
    "veneer_qwen_gguf", 
    tokenizer, 
    quantization_method = "q4_k_m"
)