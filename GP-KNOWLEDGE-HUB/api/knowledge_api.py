#!/usr/bin/env python3
"""
Central Knowledge Access API
Single point of access for all knowledge in the system
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "GP-RAG"))

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    sys.exit(1)

class CentralKnowledgeAPI:
    """Central API for accessing all knowledge"""

    def __init__(self):
        self.hub_path = Path(__file__).parent.parent
        self.vector_store_path = self.hub_path / "vector-store" / "central-knowledge-db"

        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Connect to central vector store
        if self.vector_store_path.exists():
            self.vector_store = Chroma(
                persist_directory=str(self.vector_store_path),
                embedding_function=self.embeddings
            )
        else:
            self.vector_store = None
            print("⚠️  Central vector store not found")

    def search_knowledge(self, query: str, k: int = 5, domain: str = None):
        """Search central knowledge base"""
        if not self.vector_store:
            return []

        results = self.vector_store.similarity_search(query, k=k)

        # Filter by domain if specified
        if domain:
            results = [r for r in results if r.metadata.get("source_type", "").lower().find(domain.lower()) >= 0]

        return results

    def get_domain_knowledge(self, domain: str):
        """Get all knowledge for a specific domain"""
        domain_path = self.hub_path / "knowledge-base" / domain

        if not domain_path.exists():
            return []

        files = list(domain_path.glob("*.md")) + list(domain_path.glob("*.txt"))
        return [str(f) for f in files]

    def get_knowledge_stats(self):
        """Get statistics about central knowledge"""
        stats = {}

        # Vector store stats
        if self.vector_store:
            ids = self.vector_store.get()["ids"]
            stats["vector_documents"] = len(ids)

        # Domain stats
        for domain in ["security", "compliance", "tools", "workflows", "policies"]:
            domain_path = self.hub_path / "knowledge-base" / domain
            if domain_path.exists():
                files = list(domain_path.glob("*.md")) + list(domain_path.glob("*.txt"))
                stats[f"{domain}_files"] = len(files)

        return stats

if __name__ == "__main__":
    api = CentralKnowledgeAPI()
    stats = api.get_knowledge_stats()

    print("🧠 Central Knowledge API Status:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
