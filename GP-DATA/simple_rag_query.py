#!/usr/bin/env python3
"""
Simple RAG Query - Lightweight version without heavy dependencies
For use in jade query command
"""

from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings


class SimpleRAGQuery:
    """Lightweight RAG query without embeddings"""

    def __init__(self):
        # Use GP-DATA knowledge base
        self.db_path = Path(__file__).parent / "knowledge-base" / "chroma"
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=False
            )
        )

    def query_all_collections(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Query all collections and return results"""
        all_results = []

        # Get all collections
        collections = self.client.list_collections()

        for collection_info in collections:
            try:
                collection = self.client.get_collection(collection_info.name)

                # Query collection
                results = collection.query(
                    query_texts=[query],
                    n_results=n_results
                )

                # Format results
                if results['documents'] and results['documents'][0]:
                    for i, doc in enumerate(results['documents'][0]):
                        metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                        distance = results['distances'][0][i] if results.get('distances') else 1.0

                        all_results.append({
                            'collection': collection_info.name,
                            'content': doc,
                            'metadata': metadata,
                            'distance': distance
                        })

            except Exception as e:
                # Skip collections that fail
                continue

        # Sort by distance (lower is better)
        all_results.sort(key=lambda x: x.get('distance', 1.0))

        return all_results[:n_results]

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG database statistics"""
        collections = self.client.list_collections()

        stats = {
            'total_collections': len(collections),
            'collections': {}
        }

        for collection_info in collections:
            try:
                collection = self.client.get_collection(collection_info.name)
                count = collection.count()
                stats['collections'][collection_info.name] = count
            except:
                stats['collections'][collection_info.name] = 0

        return stats


def main():
    """Simple test"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python simple_rag_query.py 'your query here'")
        sys.exit(1)

    query = ' '.join(sys.argv[1:])

    rag = SimpleRAGQuery()
    results = rag.query_all_collections(query, n_results=5)

    if results:
        print(f"\n✅ Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result['collection'].upper()}]")
            print(f"   {result['content'][:200]}...")
            print()
    else:
        print("\n❌ No results found")


if __name__ == "__main__":
    main()
