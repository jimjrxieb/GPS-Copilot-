"""
GP-RAG Core Module
==================

This module provides clean imports from GP-AI core engines (source of truth).

Architecture:
- GP-Frontend/GP-AI/core/         ← Source of truth (RAG engines, graph engine)
- GP-Backend/GP-RAG/core/          ← Import layer (this file)
- GP-Backend/GP-RAG/mlops/         ← ML models (build on top of core)

Usage:
    from GP_RAG.core import rag_engine, RAGEngine, security_graph

Available exports:
- rag_engine: Singleton RAG engine instance (ChromaDB operations)
- RAGEngine: RAG engine class for creating new instances
- security_graph: NetworkX knowledge graph instance
"""

import sys
from pathlib import Path

# Add GP-AI/core to path (source of truth for RAG engines)
gp_ai_core_path = Path(__file__).parent.parent.parent.parent / "GP-Frontend" / "GP-AI" / "core"
sys.path.insert(0, str(gp_ai_core_path))

try:
    # Import RAG engine directly from file
    import rag_engine as rag_engine_module
    rag_engine = rag_engine_module.rag_engine
    RAGEngine = rag_engine_module.RAGEngine
    RAG_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  RAG engine not available: {e}")
    print(f"    Tried: {gp_ai_core_path}/rag_engine.py")
    rag_engine = None
    RAGEngine = None
    RAG_ENGINE_AVAILABLE = False

try:
    # Import knowledge graph directly from file
    import rag_graph_engine as graph_module
    security_graph = graph_module.security_graph
    GRAPH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Knowledge graph not available: {e}")
    print(f"    Tried: {gp_ai_core_path}/rag_graph_engine.py")
    security_graph = None
    GRAPH_AVAILABLE = False

# Public API
__all__ = [
    "rag_engine",
    "RAGEngine",
    "security_graph",
    "RAG_ENGINE_AVAILABLE",
    "GRAPH_AVAILABLE"
]

# Verify at least one engine is available
if not RAG_ENGINE_AVAILABLE and not GRAPH_AVAILABLE:
    print("⚠️  WARNING: No RAG engines available!")
    print("    Check GP-Frontend/GP-AI/core/ exists")
elif RAG_ENGINE_AVAILABLE and GRAPH_AVAILABLE:
    print("✅ GP-RAG core initialized: RAG engine + Knowledge graph available")
elif RAG_ENGINE_AVAILABLE:
    print("✅ GP-RAG core initialized: RAG engine available")
else:
    print("✅ GP-RAG core initialized: Knowledge graph available")
