"""
RAG (Retrieval-Augmented Generation) Engine for GP-Copilot
GPU-Accelerated Knowledge Management for Security Consulting
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import torch

class RAGEngine:
    """High-performance RAG system for security knowledge"""

    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "GP-DATA" / "vector-db"
        self.db_path.mkdir(exist_ok=True)

        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Initialize embedding model with GPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🚀 Initializing embeddings on {self.device}")

        self.embedding_model = SentenceTransformer(
            'all-MiniLM-L6-v2',
            device=self.device
        )

        # Initialize collections
        self.init_collections()

    def init_collections(self):
        """Initialize ChromaDB collections for different knowledge types"""

        # Security patterns collection
        self.security_patterns = self.client.get_or_create_collection(
            name="security_patterns",
            metadata={"description": "Security best practices and vulnerability patterns"}
        )

        # Client knowledge collection
        self.client_knowledge = self.client.get_or_create_collection(
            name="client_knowledge",
            metadata={"description": "Client-specific documentation and context"}
        )

        # Compliance frameworks collection
        self.compliance_frameworks = self.client.get_or_create_collection(
            name="compliance_frameworks",
            metadata={"description": "SOC2, CIS, PCI-DSS compliance requirements"}
        )

        # CKS knowledge collection
        self.cks_knowledge = self.client.get_or_create_collection(
            name="cks_knowledge",
            metadata={"description": "Kubernetes security and CKS exam content"}
        )

        print(f"✅ Initialized {len(self.client.list_collections())} knowledge collections")

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Generate embeddings for documents using GPU"""
        embeddings = self.embedding_model.encode(
            documents,
            convert_to_tensor=True,
            device=self.device,
            show_progress_bar=True
        )

        # Convert to list for ChromaDB
        return embeddings.cpu().numpy().tolist()

    def add_security_knowledge(self, knowledge_type: str, documents: List[Dict[str, Any]]):
        """Add security knowledge to appropriate collection"""

        collection_map = {
            "patterns": self.security_patterns,
            "client": self.client_knowledge,
            "compliance": self.compliance_frameworks,
            "cks": self.cks_knowledge
        }

        collection = collection_map.get(knowledge_type)
        if not collection:
            print(f"❌ Unknown knowledge type: {knowledge_type}")
            return

        # Prepare documents for embedding
        texts = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        ids = [doc.get("id", f"{knowledge_type}_{i}") for i, doc in enumerate(documents)]

        # Generate embeddings
        print(f"📝 Embedding {len(texts)} documents...")
        embeddings = self.embed_documents(texts)

        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

        print(f"✅ Added {len(documents)} documents to {knowledge_type} collection")

    def query_knowledge(self, query: str, knowledge_type: str = "all", n_results: int = 5) -> List[Dict[str, Any]]:
        """Query knowledge base for relevant information"""

        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_tensor=True,
            device=self.device
        ).cpu().numpy().tolist()

        results = []

        if knowledge_type == "all":
            collections = [
                self.security_patterns,
                self.client_knowledge,
                self.compliance_frameworks,
                self.cks_knowledge
            ]
        else:
            collection_map = {
                "patterns": self.security_patterns,
                "client": self.client_knowledge,
                "compliance": self.compliance_frameworks,
                "cks": self.cks_knowledge
            }
            collections = [collection_map.get(knowledge_type, self.security_patterns)]

        # Query each collection
        for collection in collections:
            try:
                result = collection.query(
                    query_embeddings=query_embedding,
                    n_results=n_results
                )

                for i in range(len(result["documents"][0])):
                    results.append({
                        "content": result["documents"][0][i],
                        "metadata": result["metadatas"][0][i] if result["metadatas"] else {},
                        "distance": result["distances"][0][i] if result["distances"] else 0,
                        "collection": collection.name
                    })
            except Exception as e:
                print(f"Error querying {collection.name}: {e}")

        # Sort by relevance (lower distance is better)
        results.sort(key=lambda x: x["distance"])

        return results[:n_results]

    def ingest_client_project(self, project_path: str, client_name: str):
        """Ingest client project documentation for context"""
        project_path = Path(project_path)

        if not project_path.exists():
            print(f"❌ Project path not found: {project_path}")
            return

        # Clear existing client data first
        try:
            # Get existing documents for this client
            existing = self.client_knowledge.get(where={"client": client_name})
            if existing and existing["ids"]:
                self.client_knowledge.delete(ids=existing["ids"])
                print(f"🧹 Cleared {len(existing['ids'])} existing documents for {client_name}")
        except Exception as e:
            print(f"Note: Could not clear existing data: {e}")

        documents = []

        # Scan for documentation files
        for ext in ["*.md", "*.txt", "*.yaml", "*.yml", "README*"]:
            for file_path in project_path.rglob(ext):
                try:
                    # Try multiple encodings
                    content = None
                    for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                        try:
                            content = file_path.read_text(encoding=encoding)
                            break
                        except UnicodeDecodeError:
                            continue

                    if content is None:
                        print(f"⚠️  Could not decode {file_path}")
                        continue

                    # Skip empty or very small files
                    if len(content) < 50:
                        continue

                    documents.append({
                        "content": content[:5000],  # Limit content size
                        "metadata": {
                            "client": client_name,
                            "file": str(file_path.relative_to(project_path)),
                            "type": file_path.suffix
                        },
                        "id": f"{client_name}_{file_path.relative_to(project_path).as_posix().replace('/', '_')}_{hash(content)}"
                    })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        if documents:
            self.add_security_knowledge("client", documents)
            print(f"✅ Ingested {len(documents)} documents for client: {client_name}")
        else:
            print(f"⚠️  No documents found for client: {client_name}")

    def load_cks_knowledge(self):
        """Load CKS best practices into knowledge base"""
        cks_knowledge = [
            {
                "content": "Pod Security Standards: Enforce restricted policy to prevent privileged containers, require non-root users, and block privilege escalation. Use Pod Security Admission controller or OPA Gatekeeper.",
                "metadata": {"topic": "Pod Security Standards", "framework": "CKS"},
                "id": "cks_pss_001"
            },
            {
                "content": "Network Policies: Implement default-deny NetworkPolicy for all namespaces. Allow only required ingress/egress traffic. Use Calico or Cilium for advanced network policies.",
                "metadata": {"topic": "Network Policies", "framework": "CKS"},
                "id": "cks_network_001"
            },
            {
                "content": "RBAC Best Practices: Follow least privilege principle. Avoid cluster-admin bindings. Use RoleBindings over ClusterRoleBindings when possible. Audit RBAC regularly.",
                "metadata": {"topic": "RBAC", "framework": "CKS"},
                "id": "cks_rbac_001"
            },
            {
                "content": "Secret Management: Never hardcode secrets. Use external secret operators (Sealed Secrets, External Secrets Operator). Enable encryption at rest for etcd.",
                "metadata": {"topic": "Secrets", "framework": "CKS"},
                "id": "cks_secrets_001"
            },
            {
                "content": "Image Security: Scan images with Trivy or Snyk. Use image signing with Cosign. Implement admission controllers to block vulnerable images. Use distroless or minimal base images.",
                "metadata": {"topic": "Image Security", "framework": "CKS"},
                "id": "cks_images_001"
            }
        ]

        self.add_security_knowledge("cks", cks_knowledge)
        print("✅ Loaded CKS knowledge base")

    def load_compliance_frameworks(self):
        """Load compliance framework requirements"""
        compliance_docs = [
            {
                "content": "SOC2 Type II: Requires continuous monitoring, access controls, encryption at rest and in transit, incident response procedures, and regular security assessments.",
                "metadata": {"framework": "SOC2", "type": "overview"},
                "id": "soc2_001"
            },
            {
                "content": "CIS Kubernetes Benchmark: Control plane security, worker node security, RBAC policies, network policies, pod security policies, logging and monitoring.",
                "metadata": {"framework": "CIS", "type": "kubernetes"},
                "id": "cis_k8s_001"
            },
            {
                "content": "PCI-DSS: Cardholder data protection, network segmentation, access control measures, regular security testing, encryption requirements.",
                "metadata": {"framework": "PCI-DSS", "type": "overview"},
                "id": "pci_001"
            }
        ]

        self.add_security_knowledge("compliance", compliance_docs)
        print("✅ Loaded compliance frameworks")

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        stats = {
            "collections": {},
            "total_documents": 0,
            "device": self.device
        }

        for collection in self.client.list_collections():
            count = collection.count()
            stats["collections"][collection.name] = count
            stats["total_documents"] += count

        return stats

# Global RAG engine instance
rag_engine = RAGEngine()

if __name__ == "__main__":
    print("🧪 Testing RAG Engine...")

    # Load knowledge bases
    rag_engine.load_cks_knowledge()
    rag_engine.load_compliance_frameworks()

    # Test query
    test_query = "What are Kubernetes pod security best practices?"
    results = rag_engine.query_knowledge(test_query, knowledge_type="cks", n_results=3)

    print(f"\n🔍 Query: {test_query}")
    print(f"📚 Found {len(results)} relevant documents:")

    for i, result in enumerate(results, 1):
        print(f"\n{i}. Collection: {result['collection']}")
        print(f"   Relevance: {1 - result['distance']:.2%}")
        print(f"   Content: {result['content'][:200]}...")

    # Display stats
    stats = rag_engine.get_stats()
    print(f"\n📊 RAG System Stats:")
    print(f"Device: {stats['device']}")
    print(f"Total Documents: {stats['total_documents']}")
    for collection, count in stats['collections'].items():
        print(f"  {collection}: {count} documents")