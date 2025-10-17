"""
AI Model Manager for GP-Copilot
Handles download, loading, and inference for security AI models
"""

import os
import torch
from pathlib import Path
from typing import Optional, Dict, Any
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
    BitsAndBytesConfig
)
from .gpu_config import gpu_config

class ModelManager:
    """Manages AI model lifecycle for security analysis"""

    def __init__(self):
        # GP-DATA is at project root, not inside GP-AI/
        self.models_path = Path(__file__).parent.parent.parent / "GP-DATA" / "ai-models"
        self.models_path.mkdir(parents=True, exist_ok=True)

        self.tokenizer = None
        self.model = None
        self.pipeline = None

        self.model_config = gpu_config.get_model_config()
        self.allocation = gpu_config.model_allocation

    def download_model(self, force_download: bool = False) -> bool:
        """Download DeepSeek-Coder-V2-Lite 16B model (code-specialized)"""
        # Use DeepSeek-Coder instead of Qwen for better code analysis
        model_name = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
        local_path = self.models_path / "deepseek-coder-v2-lite-instruct"

        print(f"📦 Downloading {model_name} (Code-Specialized Model)...")
        print("💡 DeepSeek-Coder outperforms GPT-4 on code tasks!")

        try:
            # Configure quantization for memory efficiency
            # DeepSeek-Coder-V2-Lite is 16B, use 4-bit quantization for 16GB GPU
            quantization_config = None
            print("⚡ Enabling 4-bit quantization for 16GB GPU")
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )

            # Download tokenizer
            print("📝 Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=str(local_path),
                trust_remote_code=True
            )

            # Download model
            print("🧠 Downloading model weights...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=str(local_path),
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto" if torch.cuda.is_available() else None,
                quantization_config=quantization_config,
                low_cpu_mem_usage=True
            )

            print(f"✅ Model downloaded to {local_path}")
            return True

        except Exception as e:
            print(f"❌ Model download failed: {e}")
            return False

    def load_model(self) -> bool:
        """Load the model for inference"""
        # Use DeepSeek-Coder for superior code analysis
        model_name = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"

        try:
            print(f"🚀 Loading {model_name} (16B Code-Specialized)...")
            print("💡 Optimized for Terraform, Kubernetes, OPA, and security code analysis")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )

            # Configure 4-bit quantization for 16GB GPU
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )

            # Load model with optimized settings
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
                quantization_config=quantization_config,
                low_cpu_mem_usage=True
            )

            print(f"✅ DeepSeek-Coder loaded to GPU successfully")
            print(f"🎮 VRAM Usage: ~10GB (4-bit quantized)")
            print(f"⚡ Ready for advanced code analysis!")
            return True

        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            print(f"💡 Fallback: Using pattern-based analysis")
            return False

    def generate_security_analysis(self, code_content: str, file_type: str = "terraform") -> str:
        """Generate security analysis for code content"""
        if not self.model or not self.tokenizer:
            return "❌ Model not loaded"

        # Create security analysis prompt
        prompt = self._create_security_prompt(code_content, file_type)

        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.1,  # Low temperature for consistent security analysis
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract only the generated part
            analysis = response[len(prompt):].strip()
            return analysis

        except Exception as e:
            return f"❌ Analysis failed: {e}"

    def _create_security_prompt(self, code_content: str, file_type: str) -> str:
        """Create specialized security analysis prompt"""

        if file_type == "terraform":
            prompt = f"""You are a senior security consultant specializing in Infrastructure as Code (IaC) security. Analyze the following Terraform configuration for security vulnerabilities and compliance issues.

Focus on:
- Hardcoded credentials and secrets
- Overpermissive access controls (0.0.0.0/0, wildcard permissions)
- Missing encryption configurations
- Public access to sensitive resources
- IAM policy issues
- Network security misconfigurations

Terraform code:
```
{code_content[:2000]}  # Limit context size
```

Provide a concise security analysis with:
1. Critical issues found
2. Compliance framework violations (CIS, SOC2, PCI-DSS)
3. Specific recommendations for remediation

Analysis:"""

        elif file_type == "kubernetes":
            prompt = f"""You are a Certified Kubernetes Security (CKS) expert. Analyze the following Kubernetes YAML for security issues according to Pod Security Standards and CKS best practices.

Focus on:
- Pod Security Standards violations
- Privileged containers and capabilities
- Missing security contexts
- Network policy gaps
- RBAC misconfigurations
- Secret management issues

Kubernetes YAML:
```
{code_content[:2000]}
```

Provide CKS-focused security analysis with specific recommendations.

Analysis:"""

        else:
            prompt = f"""You are a security consultant. Analyze the following code for security vulnerabilities:

```
{code_content[:2000]}
```

Provide security recommendations:"""

        return prompt

    def query_security_knowledge(self, question: str, context: Optional[str] = None) -> str:
        """Answer security questions using the model"""
        if not self.model or not self.tokenizer:
            return "❌ Model not loaded"

        # Create knowledge query prompt
        prompt = f"""You are a senior security consultant with expertise in:
- Kubernetes Security (CKS)
- Infrastructure as Code (Terraform, CloudFormation)
- DevSecOps and CI/CD security
- Compliance frameworks (SOC2, PCI-DSS, CIS, NIST)
- Cloud security (AWS, Azure, GCP)

Question: {question}

{f"Context: {context}" if context else ""}

Provide a detailed, professional answer:"""

        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=256,
                    temperature=0.2,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract only the generated part
            answer = response[len(prompt):].strip()
            return answer

        except Exception as e:
            return f"❌ Query failed: {e}"

    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status"""
        return {
            "model_loaded": self.model is not None,
            "model_name": "DeepSeek-Coder-V2-Lite-Instruct-16B",
            "model_type": "Code-Specialized LLM",
            "vram_allocated": "~10GB",
            "device": str(self.model_config.get("device", "cpu")),
            "quantization": "4-bit (NF4)",
            "strengths": "Terraform, Kubernetes, OPA, Python, Security Analysis"
        }

# Global model manager instance
model_manager = ModelManager()

# Auto-load model on import - DISABLED (loads async on first query to avoid blocking FastAPI startup)
# Large models (16B) take 5-10 minutes to load and would block the API
# Model will be loaded lazily on first inference request
if __name__ != "__main__":
    print("💡 DeepSeek-Coder will load on first inference request (lazy loading)")
    print("   This prevents blocking FastAPI startup (16B model takes ~5 min to load)")
    # try:
    #     print("🚀 Auto-loading DeepSeek-Coder-V2 (16B Code-Specialized)...")
    #     if model_manager.load_model():
    #         print("✅ DeepSeek-Coder auto-loaded successfully")
    #     else:
    #         print("⚠️  Model auto-load failed - will use fallback pattern analysis")
    # except Exception as e:
    #     print(f"⚠️  Model auto-load error: {e} - using fallback")

if __name__ == "__main__":
    # Test model download and loading
    print("🧪 Testing Model Manager...")

    if model_manager.download_model():
        if model_manager.load_model():
            status = model_manager.get_model_status()
            print(f"📊 Model Status: {status}")

            # Test query
            test_answer = model_manager.query_security_knowledge("What are the top 3 Kubernetes security risks?")
            print(f"🤖 Test Query Result: {test_answer}")
        else:
            print("❌ Model loading failed")
    else:
        print("❌ Model download failed")