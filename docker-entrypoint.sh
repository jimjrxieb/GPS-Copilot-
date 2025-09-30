#!/bin/bash
set -e

echo "🚀 Starting GP-JADE AI Security Engine..."

# Check for GPU
if command -v nvidia-smi &> /dev/null; then
    echo "✅ GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "⚠️  No GPU detected - running in CPU mode"
fi

# Initialize vector database directory
echo "📦 Initializing vector database..."
mkdir -p /app/GP-DATA/vector-db

# Check if vector database exists
if [ -d "/app/GP-DATA/vector-db/chroma.sqlite3" ]; then
    echo "✅ Existing vector database found"
else
    echo "📝 Creating new vector database..."
fi

# Test OPA connection
echo "🔗 Checking OPA connection..."
if curl -s http://opa:8181/health > /dev/null 2>&1; then
    echo "✅ OPA is reachable"
else
    echo "⚠️  OPA not reachable yet - will retry on startup"
fi

# Download/verify Qwen2.5-7B model (will use cache if exists)
echo "🧠 Preparing AI model..."
python3 -c "
import sys
sys.path.append('/app')
from transformers import AutoTokenizer
import torch

model_name = 'Qwen/Qwen2.5-7B-Instruct'
print(f'📥 Checking model: {model_name}')

try:
    # This will download on first run, use cache on subsequent runs
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    print('✅ Model ready (cached or downloaded)')
except Exception as e:
    print(f'⚠️  Model preparation: {e}')
    print('Model will be downloaded on first use')
"

# Initialize RAG engine and load knowledge bases
echo "🧠 Initializing RAG engine..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/GP-AI')

try:
    from engines.rag_engine import rag_engine

    # Load built-in knowledge bases
    print('📚 Loading CKS knowledge base...')
    rag_engine.load_cks_knowledge()

    print('📚 Loading compliance frameworks...')
    rag_engine.load_compliance_frameworks()

    # Display stats
    stats = rag_engine.get_stats()
    print(f'✅ RAG Engine initialized:')
    print(f'   Device: {stats[\"device\"]}')
    print(f'   Collections: {len(stats[\"collections\"])}')
    print(f'   Total Documents: {stats[\"total_documents\"]}')

except Exception as e:
    print(f'⚠️  RAG engine initialization: {e}')
    import traceback
    traceback.print_exc()
" || echo "⚠️  RAG initialization failed - will retry"

echo "✅ GP-JADE initialization complete"
echo "🎯 Starting application..."

# Execute the CMD
exec "$@"