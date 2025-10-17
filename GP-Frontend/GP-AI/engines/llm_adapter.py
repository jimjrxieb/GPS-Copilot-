"""
LLM Adapter - Plug-and-play interface for any LLM
Works with Qwen2.5, DeepSeek, GPT, Claude, etc.
"""

from typing import Optional, Dict, Any
from pathlib import Path


class LLMAdapter:
    """
    Universal adapter for any LLM backend
    Provides consistent interface regardless of model
    """

    def __init__(self, model_type: str = "qwen2.5"):
        """
        Args:
            model_type: "qwen2.5", "deepseek", "gpt4", "claude", etc.
        """
        self.model_type = model_type
        self.model = None
        self.tokenizer = None

    def load(self) -> bool:
        """Load the specified model"""
        if self.model_type == "qwen2.5":
            return self._load_qwen()
        elif self.model_type == "deepseek":
            return self._load_deepseek()
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def _load_qwen(self) -> bool:
        """Load Qwen2.5-7B-Instruct"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch

            model_name = "Qwen/Qwen2.5-7B-Instruct"
            cache_dir = Path.home() / ".cache/huggingface/hub"

            print(f"🚀 Loading {model_name}...")

            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=str(cache_dir),
                trust_remote_code=True
            )

            # Force CPU due to CUDA sm_120 incompatibility (RTX 5080)
            # PyTorch doesn't support Blackwell architecture yet
            device = "cpu"
            print("⚠️  Using CPU - PyTorch CUDA sm_120 not supported yet")
            print("   (RTX 5080 requires PyTorch nightly build)")

            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=str(cache_dir),
                trust_remote_code=True,
                torch_dtype=torch.float32,
                device_map=None,
                low_cpu_mem_usage=True
            )

            self.model = self.model.to("cpu")

            print(f"✅ Qwen2.5-7B loaded on {device}")
            print("   Inference will be slower on CPU but functional")
            return True

        except Exception as e:
            print(f"❌ Failed to load Qwen2.5: {e}")
            return False

    def _load_deepseek(self) -> bool:
        """Load DeepSeek-Coder"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch

            model_name = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"

            print(f"🚀 Loading {model_name}...")

            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )

            device = "cpu"
            if torch.cuda.is_available():
                try:
                    torch.zeros(1).cuda()
                    device = "cuda"
                except Exception:
                    device = "cpu"

            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                low_cpu_mem_usage=True
            )

            if device == "cpu":
                self.model = self.model.to("cpu")

            print(f"✅ DeepSeek-Coder loaded on {device}")
            return True

        except Exception as e:
            print(f"❌ Failed to load DeepSeek: {e}")
            return False

    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.3,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate text from prompt (model-agnostic)

        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            system_prompt: Optional system instructions

        Returns:
            Generated text
        """
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded. Call load() first.")

        # Format prompt based on model
        if self.model_type == "qwen2.5":
            formatted = self._format_qwen_prompt(prompt, system_prompt)
        elif self.model_type == "deepseek":
            formatted = self._format_deepseek_prompt(prompt, system_prompt)
        else:
            formatted = prompt

        # Tokenize
        inputs = self.tokenizer(formatted, return_tensors="pt")

        # Move to same device as model
        device = next(self.model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=self.tokenizer.eos_token_id
        )

        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only new tokens (remove prompt)
        if formatted in generated_text:
            generated_text = generated_text.replace(formatted, "").strip()

        return generated_text

    def _format_qwen_prompt(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Format prompt for Qwen2.5"""
        if system_prompt:
            return f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        else:
            return f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

    def _format_deepseek_prompt(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Format prompt for DeepSeek"""
        if system_prompt:
            return f"### System:\n{system_prompt}\n\n### User:\n{prompt}\n\n### Assistant:\n"
        else:
            return f"### User:\n{prompt}\n\n### Assistant:\n"

    def query_with_rag(
        self,
        question: str,
        rag_results: list,
        max_context_items: int = 5
    ) -> str:
        """
        Generate answer using RAG context

        Args:
            question: User question
            rag_results: Results from RAG query
            max_context_items: Max context items to include

        Returns:
            Generated answer
        """
        # Build context from RAG results
        context = []
        for result in rag_results[:max_context_items]:
            content = result.get('content', '')
            collection = result.get('collection', 'unknown')
            context.append(f"[{collection.upper()}]\n{content}\n")

        context_str = "\n---\n".join(context)

        # Create prompt with context
        system_prompt = """You are Jade, an AI security consultant specializing in cloud security,
Kubernetes, Terraform, and security automation. Provide concise, accurate technical answers
based on the context provided."""

        prompt = f"""Context:
{context_str}

Question: {question}

Provide a concise answer based on the context above. If the context doesn't contain
relevant information, say so."""

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=512,
            temperature=0.3
        )


class RAGQueryEngine:
    """Combines RAG database with LLM for intelligent queries"""

    def __init__(self, model_type: str = "qwen2.5"):
        """
        Args:
            model_type: LLM to use ("qwen2.5", "deepseek", etc.)
        """
        import sys
        from pathlib import Path

        # Add GP-DATA to path (use absolute path)
        gp_copilot_root = Path(__file__).parent.parent.parent.parent  # GP-Frontend/GP-AI/engines -> GP-copilot
        sys.path.insert(0, str(gp_copilot_root / "GP-DATA"))

        from simple_rag_query import SimpleRAGQuery

        self.rag = SimpleRAGQuery()
        self.llm = LLMAdapter(model_type=model_type)
        self.llm_loaded = False

    def lazy_load_llm(self):
        """Load LLM on first use"""
        if not self.llm_loaded:
            print("🔄 Loading LLM (first query)...")
            self.llm_loaded = self.llm.load()
        return self.llm_loaded

    def query(
        self,
        question: str,
        n_rag_results: int = 5,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Query RAG database and optionally use LLM for synthesis

        Args:
            question: User question
            n_rag_results: Number of RAG results to retrieve
            use_llm: Whether to use LLM for answer synthesis

        Returns:
            {
                'rag_results': [...],
                'llm_answer': str or None,
                'stats': {...}
            }
        """
        # Always query RAG first
        rag_results = self.rag.query_all_collections(question, n_results=n_rag_results)

        result = {
            'rag_results': rag_results,
            'llm_answer': None,
            'stats': {
                'rag_results_count': len(rag_results),
                'llm_used': False
            }
        }

        # Use LLM if requested and available
        if use_llm and rag_results:
            if self.lazy_load_llm():
                try:
                    result['llm_answer'] = self.llm.query_with_rag(question, rag_results)
                    result['stats']['llm_used'] = True
                except Exception as e:
                    print(f"⚠️  LLM synthesis failed: {e}")

        return result


# Example usage
if __name__ == "__main__":
    # Test RAG-only (fast, no LLM)
    print("=== RAG-Only Query (Fast) ===\n")
    engine = RAGQueryEngine(model_type="qwen2.5")
    result = engine.query("What is Bandit scanner?", use_llm=False)

    print(f"Found {len(result['rag_results'])} results:")
    for i, r in enumerate(result['rag_results'][:3], 1):
        print(f"{i}. [{r['collection']}] {r['content'][:100]}...")

    print("\n=== RAG + LLM Query (Slow, first time) ===\n")
    result = engine.query("Summarize Bandit security findings", use_llm=True)

    if result['llm_answer']:
        print(f"LLM Answer:\n{result['llm_answer']}")
    else:
        print("LLM not available, showing RAG results only")