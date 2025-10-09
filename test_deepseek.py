#!/usr/bin/env python3
"""
Test DeepSeek-Coder-V2 with Gatekeeper automation questions
"""

import sys
sys.path.insert(0, "GP-AI")

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

print("🚀 Loading DeepSeek-Coder-V2-Lite-Instruct...")

model_name = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# Load model
print("📦 Loading model with 4-bit quantization...")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
    quantization_config=quantization_config,
    low_cpu_mem_usage=True
)

print("✅ Model loaded successfully!")
print(f"🎮 Device: {model.device}")

# Test with Gatekeeper question
question = """Write a Gatekeeper ConstraintTemplate in YAML that enforces pods must have securityContext.runAsNonRoot=true. Include:
1. The ConstraintTemplate definition
2. A Constraint to use it
3. Example violation that would be blocked

Be specific and include working YAML."""

prompt = f"""<|im_start|>system
You are an expert in Kubernetes security and Open Policy Agent (OPA) Gatekeeper. Provide accurate, working code examples.<|im_end|>
<|im_start|>user
{question}<|im_end|>
<|im_start|>assistant
"""

print("\n" + "="*80)
print("🤖 DeepSeek-Coder Response:")
print("="*80 + "\n")

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=1024,
        temperature=0.1,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id
    )

response = tokenizer.decode(outputs[0], skip_special_tokens=True)
answer = response[len(prompt):].strip()

print(answer)
print("\n" + "="*80)
