#!/usr/bin/env python3
"""
Quick test script for Qwen2.5 7B model
"""

import sys
import torch
from pathlib import Path

print("🧪 Testing Qwen2.5 7B Model Setup...")

# Check GPU
if torch.cuda.is_available():
    print(f"✅ GPU Available: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
else:
    print("⚠️  No GPU detected")

# Try loading model
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name = "Qwen/Qwen2.5-7B-Instruct"
    print(f"\n📦 Loading {model_name}...")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True
    )
    print("✅ Tokenizer loaded")

    # Load model with GPU
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )
    print("✅ Model loaded to GPU")

    # Test inference
    print("\n🤖 Testing inference...")

    # Security-focused test prompt
    prompt = """You are a security expert. Answer concisely.

Question: What are the top 3 Kubernetes security risks?

Answer:"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.3,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract just the answer
    if "Answer:" in response:
        answer = response.split("Answer:")[-1].strip()
    else:
        answer = response.strip()

    print(f"\n💡 Model Response:\n{answer}")

    print("\n✅ SUCCESS! Qwen2.5 7B is operational!")

except Exception as e:
    print(f"\n❌ Model test failed: {e}")
    print("\nPossible causes:")
    print("1. Model still downloading")
    print("2. Insufficient VRAM")
    print("3. Missing dependencies")

    import traceback
    traceback.print_exc()