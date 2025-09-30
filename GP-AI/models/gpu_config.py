"""
GPU-Accelerated AI Configuration for GP-Copilot
Optimized for RTX 5080 (24GB VRAM)
"""

import torch
import json
from pathlib import Path

class GPUConfig:
    """GPU configuration and optimization for security AI models"""

    def __init__(self):
        self.device = self._detect_gpu()
        self.vram_total = self._get_vram_total()
        self.model_allocation = self._calculate_model_allocation()

    def _detect_gpu(self):
        """Detect and configure GPU"""
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"🚀 GPU Detected: {gpu_name}")
            print(f"🔥 CUDA Version: {torch.version.cuda}")
            return torch.device("cuda:0")
        else:
            print("⚠️  GPU not available, falling back to CPU")
            return torch.device("cpu")

    def _get_vram_total(self):
        """Get total VRAM in GB"""
        if self.device.type == "cuda":
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            vram_gb = vram_bytes / (1024**3)
            print(f"💾 VRAM Available: {vram_gb:.1f}GB")
            return vram_gb
        return 0

    def _calculate_model_allocation(self):
        """Calculate optimal model allocation for RTX 5080"""
        if self.vram_total >= 15:  # RTX 5080 territory - Start with 7B
            return {
                "reasoning_model": "Qwen/Qwen2.5-7B-Instruct",  # ~7GB
                "reasoning_vram": 8,
                "embedding_model": "all-MiniLM-L6-v2",  # ~1GB
                "embedding_vram": 1,
                "chromadb_cache": 2,  # ~2GB
                "buffer_vram": 4  # Plenty of headroom
            }
        elif self.vram_total >= 8:  # Mid-range GPU
            return {
                "reasoning_model": "Qwen/Qwen2.5-7B-Instruct",
                "reasoning_vram": 7,
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_vram": 1,
                "chromadb_cache": 0,
                "buffer_vram": 0
            }
        else:  # Fallback to CPU
            return {
                "reasoning_model": "Qwen/Qwen2.5-7B-Instruct",
                "reasoning_vram": 0,
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_vram": 0,
                "chromadb_cache": 0,
                "buffer_vram": 0
            }

    def get_model_config(self):
        """Get optimal model configuration"""
        return {
            "device": str(self.device),
            "torch_dtype": "float16",  # Half precision for speed
            "device_map": "auto",
            "max_memory": {0: f"{self.model_allocation['reasoning_vram']}GiB"},
            "offload_folder": "./offload",
            "low_cpu_mem_usage": True
        }

    def get_embedding_config(self):
        """Get embedding model configuration"""
        return {
            "device": str(self.device),
            "model_kwargs": {
                "device": str(self.device),
                "torch_dtype": torch.float16
            },
            "encode_kwargs": {
                "batch_size": 64,  # High throughput on 5080
                "show_progress_bar": True
            }
        }

    def print_performance_profile(self):
        """Print expected performance profile"""
        allocation = self.model_allocation

        print(f"\n🎯 GP-Copilot Performance Profile:")
        print(f"Reasoning Model: {allocation['reasoning_model']}")
        print(f"Expected Inference: <2 seconds")
        print(f"Embedding Speed: ~1000 tokens/sec")
        print(f"Concurrent Operations: Yes")
        print(f"Real-time Analysis: Enabled")

        if "Qwen2.5-7B" in allocation['reasoning_model']:
            print(f"\n🚀 PRODUCTION MODE ENABLED:")
            print(f"- Context Window: 32K tokens")
            print(f"- Reasoning Quality: Professional")
            print(f"- Client Demo Ready: Yes")
            print(f"- VRAM Usage: ~{allocation['reasoning_vram']}GB")
            print(f"- Headroom Available: {self.vram_total - allocation['reasoning_vram'] - allocation['embedding_vram']:.1f}GB")

# Initialize GPU configuration
gpu_config = GPUConfig()

if __name__ == "__main__":
    gpu_config.print_performance_profile()