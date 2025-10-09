#!/bin/bash
set -e

echo "🤖 GP-JADE Model Setup"
echo "======================"
echo ""
echo "This script downloads Qwen models from Hugging Face"
echo "Models will be cached in: ~/.cache/huggingface/hub/"
echo ""

# Check if running in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Not in virtual environment"
    echo "Run: source ai-env/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N): " continue_anyway
    if [[ ! "$continue_anyway" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Ask which model to download
echo "Available models:"
echo "  1) Qwen2.5-7B-Instruct  (~14GB) - Best quality, slower"
echo "  2) Qwen2.5-3B-Instruct  (~6GB)  - Balanced"
echo "  3) Qwen2.5-1.5B-Instruct (~3GB) - Fastest, lower quality"
echo "  4) All models"
echo ""
read -p "Which model? (1-4) [2]: " model_choice
model_choice=${model_choice:-2}

download_model() {
    MODEL_NAME=$1
    MODEL_SIZE=$2

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📥 Downloading $MODEL_NAME ($MODEL_SIZE)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "This may take 10-30 minutes depending on your connection..."

    python3 << EOF
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import sys

try:
    print("📦 Downloading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("$MODEL_NAME")

    print("📦 Downloading model...")
    model = AutoModelForCausalLM.from_pretrained(
        "$MODEL_NAME",
        torch_dtype=torch.float16,
        device_map="cpu",  # Download to CPU to avoid CUDA issues
        low_cpu_mem_usage=True
    )

    print("")
    print("✅ Model downloaded successfully!")
    print(f"Model: $MODEL_NAME")
    print(f"Cached in: ~/.cache/huggingface/hub/")
    print("")

except Exception as e:
    print(f"❌ Error downloading model: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        echo "✅ $MODEL_NAME download complete"
        return 0
    else
        echo "❌ $MODEL_NAME download failed"
        return 1
    fi
}

# Download selected model(s)
case $model_choice in
    1)
        download_model "Qwen/Qwen2.5-7B-Instruct" "14GB"
        ;;
    2)
        download_model "Qwen/Qwen2.5-3B-Instruct" "6GB"
        ;;
    3)
        download_model "Qwen/Qwen2.5-1.5B-Instruct" "3GB"
        ;;
    4)
        echo "Downloading all models (this will take a while)..."
        download_model "Qwen/Qwen2.5-1.5B-Instruct" "3GB"
        download_model "Qwen/Qwen2.5-3B-Instruct" "6GB"
        download_model "Qwen/Qwen2.5-7B-Instruct" "14GB"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Model setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Models cached in: ~/.cache/huggingface/hub/"
echo ""
echo "Next steps:"
echo "1. Verify installation:  ls -lh ~/.cache/huggingface/hub/"
echo "2. Test Jade:            python3 -c 'from GP_AI.jade_enhanced import JadeEnhanced; jade = JadeEnhanced()'"
echo "3. Run CLI:              bin/jade stats"
echo ""
echo "Note: Models are NOT tracked in git (too large)"
echo "      On new machines, run this script again to download"
echo ""