#!/usr/bin/env python3
"""
Add New Knowledge to Central Vector Store
For adding new knowledge files directly to the central hub
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "GP-RAG"))

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
    from langchain.schema import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    sys.exit(1)

def add_knowledge_to_vector_store():
    """Add new knowledge to the central vector store"""

    print("🔄 Adding new knowledge to central vector store...")

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Connect to central vector store
    central_vector_store_path = Path("/home/jimmie/linkops-industries/GP-copilot/GP-KNOWLEDGE-HUB/vector-store/central-knowledge-db")

    vector_store = Chroma(
        persist_directory=str(central_vector_store_path),
        embedding_function=embeddings
    )

    # Load the new knowledge file
    new_knowledge_file = Path("/home/jimmie/linkops-industries/GP-copilot/GP-KNOWLEDGE-HUB/knowledge-base/policies/gatekeeper_comprehensive_explanation.md")

    if not new_knowledge_file.exists():
        print(f"❌ Knowledge file not found: {new_knowledge_file}")
        return

    print(f"📖 Reading new knowledge: {new_knowledge_file}")

    with open(new_knowledge_file, 'r') as f:
        content = f.read()

    # Create document
    doc = Document(
        page_content=content,
        metadata={
            "source": str(new_knowledge_file),
            "source_type": "Policies",
            "priority": 1,
            "filename": new_knowledge_file.name,
            "domain": "policies"
        }
    )

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = text_splitter.split_documents([doc])
    print(f"📄 Created {len(chunks)} chunks from new knowledge")

    # Add to vector store
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]

    vector_store.add_texts(texts=texts, metadatas=metadatas)

    print(f"✅ Added {len(chunks)} chunks to central vector store")

    # Test retrieval
    print("\n🔍 Testing retrieval of new knowledge...")
    test_query = "What is the difference between Gatekeeper and scanners like Trivy?"
    results = vector_store.similarity_search(test_query, k=3)

    print(f"📊 Found {len(results)} relevant chunks for test query")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result.page_content[:100]}...")

    print("\n🎉 New knowledge successfully added to central vector store!")

if __name__ == "__main__":
    add_knowledge_to_vector_store()