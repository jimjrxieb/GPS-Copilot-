#!/usr/bin/env python3
"""
Simple Knowledge Retrieval Test
Test the central vector store directly without Jade initialization
"""

import sys
from pathlib import Path

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    sys.exit(1)

def test_knowledge_retrieval():
    """Test knowledge retrieval from central store"""

    print("🔍 Testing Central Knowledge Retrieval")
    print("=" * 50)

    # Initialize embeddings
    print("📡 Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Connect to central vector store (using direct path)
    central_db_path = "/home/jimmie/linkops-industries/GP-copilot/GP-KNOWLEDGE-HUB/vector-store/central-knowledge-db"

    print(f"🧠 Connecting to central knowledge base: {central_db_path}")

    try:
        vector_store = Chroma(
            persist_directory=central_db_path,
            embedding_function=embeddings
        )

        # Check document count
        ids = vector_store.get()["ids"]
        print(f"✅ Connected! Found {len(ids)} documents in central knowledge base")

        # Test Gatekeeper-related queries
        test_queries = [
            "What is the difference between Gatekeeper and scanners like Trivy?",
            "How does Gatekeeper work with Kubernetes admission controllers?",
            "What are ConstraintTemplates in Gatekeeper?",
            "OPA vs Gatekeeper relationship"
        ]

        print(f"\n🔍 Testing {len(test_queries)} Gatekeeper queries...")

        for i, query in enumerate(test_queries, 1):
            print(f"\n📋 Query {i}: {query}")
            print("-" * 60)

            try:
                # Search for relevant documents
                results = vector_store.similarity_search(query, k=3)

                print(f"📚 Found {len(results)} relevant documents:")

                for j, doc in enumerate(results, 1):
                    metadata = doc.metadata
                    source_type = metadata.get('source_type', 'Unknown')
                    filename = metadata.get('filename', 'Unknown')

                    print(f"   {j}. Source: {filename} ({source_type})")
                    print(f"      Content: {doc.page_content[:150].strip()}...")

                    # Check if this contains Gatekeeper knowledge
                    content_lower = doc.page_content.lower()
                    if 'gatekeeper' in content_lower:
                        print(f"      ✅ Contains Gatekeeper content")
                    elif any(term in content_lower for term in ['admission controller', 'opa', 'policy']):
                        print(f"      🎯 Contains related policy content")
                    else:
                        print(f"      ⚠️  General security content")

            except Exception as e:
                print(f"   ❌ Error searching for query: {e}")

        print(f"\n🎯 Knowledge Retrieval Test Complete!")
        print(f"📊 Central knowledge base is accessible with {len(ids)} documents")

        # Check if we have good Gatekeeper coverage
        gatekeeper_query = "Gatekeeper admission controller policy"
        gatekeeper_results = vector_store.similarity_search(gatekeeper_query, k=5)
        gatekeeper_count = len([r for r in gatekeeper_results if 'gatekeeper' in r.page_content.lower()])

        print(f"🔍 Gatekeeper knowledge coverage: {gatekeeper_count}/5 results contain Gatekeeper content")

        if gatekeeper_count >= 3:
            print("✅ Good Gatekeeper knowledge coverage")
        else:
            print("⚠️  Limited Gatekeeper knowledge - consider adding more content")

    except Exception as e:
        print(f"❌ Failed to connect to knowledge base: {e}")
        print("💡 This might be due to ChromaDB lock - try again in a moment")

if __name__ == "__main__":
    test_knowledge_retrieval()