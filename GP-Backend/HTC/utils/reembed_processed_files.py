#!/usr/bin/env python3
"""
Re-embed Processed Files into ChromaDB
========================================

Purpose: Takes files from processed/ directory and embeds them into ChromaDB
         so Jade can retrieve them via RAG.

Problem: Files were processed (sanitized, chunked, metadata created) but
         never embedded into the vector database.

Usage:
    python3 reembed_processed_files.py
    python3 reembed_processed_files.py --dry-run  # Preview only
    python3 reembed_processed_files.py --verify   # Verify after embedding
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import argparse

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core import rag_engine, RAG_ENGINE_AVAILABLE
    if not RAG_ENGINE_AVAILABLE:
        print("❌ RAG engine not available!")
        print("   Check GP-Frontend/GP-AI/core/rag_engine.py exists")
        sys.exit(1)
except ImportError as e:
    print(f"❌ Failed to import RAG engine: {e}")
    sys.exit(1)


class ProcessedFileReembedder:
    """Re-embeds processed files into ChromaDB"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.processed_dir = Path(__file__).parent / "processed"
        self.stats = {
            "files_found": 0,
            "files_embedded": 0,
            "files_skipped": 0,
            "total_chunks": 0,
            "errors": []
        }

        # Knowledge type mapping based on directory structure
        # IMPORTANT: Use SHORT names that match RAG engine's collection_map!
        # RAG engine expects: "patterns", "client", "compliance", "cks", "scans", "docs", "projects"
        self.knowledge_type_map = {
            "james-os-knowledge": "docs",      # System/documentation
            "security-docs": "patterns",       # Security patterns
            "client-docs": "client",           # Client knowledge
            "compliance": "compliance",        # Compliance frameworks
            "cks": "cks",                      # CKS knowledge
            "scan": "scans",                   # Scan findings
            "project": "projects"              # Project context
        }

    def determine_knowledge_type(self, file_path: Path) -> str:
        """Determine knowledge type from file path"""
        path_str = str(file_path).lower()

        # Check parent directory
        for keyword, knowledge_type in self.knowledge_type_map.items():
            if keyword in path_str:
                return knowledge_type

        # Default based on content
        if "security" in path_str or "cve" in path_str or "vulnerability" in path_str:
            return "security_patterns"
        elif "kubernetes" in path_str or "k8s" in path_str:
            return "cks_knowledge"
        else:
            return "documentation"

    def chunk_content(self, content: str, chunk_size: int = 2000) -> List[str]:
        """Split content into chunks for better retrieval"""
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [content]

    def embed_file(self, file_path: Path) -> bool:
        """Embed a single file into ChromaDB"""
        try:
            # Read content
            content = file_path.read_text(encoding='utf-8')

            # Skip very small files
            if len(content.strip()) < 100:
                print(f"  ⏭️  Skipped (too small): {file_path.name}")
                self.stats["files_skipped"] += 1
                return False

            # Determine knowledge type
            knowledge_type = self.determine_knowledge_type(file_path)

            # Chunk content
            chunks = self.chunk_content(content)
            self.stats["total_chunks"] += len(chunks)

            # Create documents for each chunk
            documents = []
            for i, chunk in enumerate(chunks):
                doc = {
                    "content": chunk,
                    "metadata": {
                        "source": str(file_path),
                        "filename": file_path.name,
                        "category": knowledge_type,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "file_size": len(content),
                        "reembedded_at": datetime.now().isoformat()
                    },
                    "id": f"reembed_{file_path.stem}_chunk{i}_{hash(chunk)}"
                }
                documents.append(doc)

            if self.dry_run:
                print(f"  🔍 DRY RUN - Would embed: {file_path.name}")
                print(f"     → {len(chunks)} chunks → {knowledge_type}")
                return False

            # Add to ChromaDB
            rag_engine.add_security_knowledge(knowledge_type, documents)

            print(f"  ✅ Embedded: {file_path.name}")
            print(f"     → {len(chunks)} chunks → {knowledge_type}")

            self.stats["files_embedded"] += 1
            return True

        except Exception as e:
            error_msg = f"Failed to embed {file_path.name}: {str(e)}"
            self.stats["errors"].append(error_msg)
            print(f"  ❌ Error: {error_msg}")
            return False

    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in processed directory"""
        # Get all .md files recursively
        md_files = list(self.processed_dir.rglob("*.md"))

        # Sort by path for consistent ordering
        md_files.sort()

        return md_files

    def run(self):
        """Main execution"""
        print("="*60)
        print("🔄 Re-embedding Processed Files into ChromaDB")
        print("="*60)

        if self.dry_run:
            print("🔍 DRY RUN MODE - No actual embedding will occur\n")
        else:
            print()

        # Find all markdown files
        md_files = self.find_markdown_files()
        self.stats["files_found"] = len(md_files)

        if not md_files:
            print("❌ No markdown files found in processed/")
            return False

        print(f"📂 Found {len(md_files)} markdown files\n")

        # Process each file
        for file_path in md_files:
            # Show relative path
            rel_path = file_path.relative_to(self.processed_dir)
            print(f"Processing: {rel_path}")
            self.embed_file(file_path)
            print()

        # Show summary
        self.print_summary()

        return self.stats["files_embedded"] > 0

    def print_summary(self):
        """Print embedding summary"""
        print("="*60)
        print("📊 EMBEDDING SUMMARY")
        print("="*60)
        print(f"Files found:    {self.stats['files_found']}")
        print(f"Files embedded: {self.stats['files_embedded']}")
        print(f"Files skipped:  {self.stats['files_skipped']}")
        print(f"Total chunks:   {self.stats['total_chunks']}")
        print(f"Errors:         {len(self.stats['errors'])}")

        if self.stats['errors']:
            print("\n❌ ERRORS:")
            for error in self.stats['errors']:
                print(f"   - {error}")

        print("="*60)

    def verify_embedding(self):
        """Verify files were embedded correctly"""
        print("\n" + "="*60)
        print("🔍 VERIFICATION - Testing Retrieval")
        print("="*60)

        # Get RAG stats
        stats = rag_engine.get_stats()
        print(f"\n📊 ChromaDB Status:")
        print(f"   Total documents: {stats['total_documents']}")
        print(f"\n   Collections:")
        for name, count in stats['collections'].items():
            if count > 0:
                print(f"      {name}: {count} documents")

        # Test queries
        test_queries = [
            ("James-OS architecture", "system_knowledge"),
            ("security patterns", "security_patterns"),
            ("Kubernetes security", "cks_knowledge")
        ]

        print(f"\n🔍 Test Queries:")
        for query, knowledge_type in test_queries:
            try:
                results = rag_engine.query_knowledge(query, knowledge_type, n_results=3)
                if results:
                    print(f"\n   ✅ Query: '{query}' (type: {knowledge_type})")
                    print(f"      Found {len(results)} results")
                    if results[0].get('documents'):
                        doc_preview = results[0]['documents'][0][:100]
                        print(f"      Preview: {doc_preview}...")
                else:
                    print(f"\n   ⚠️  Query: '{query}' - No results")
            except Exception as e:
                print(f"\n   ❌ Query: '{query}' - Error: {e}")

        print("\n" + "="*60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Re-embed processed files into ChromaDB for Jade RAG retrieval"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be embedded without actually embedding"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify embedding after completion"
    )

    args = parser.parse_args()

    # Create reembedder
    reembedder = ProcessedFileReembedder(dry_run=args.dry_run)

    # Run embedding
    success = reembedder.run()

    # Verify if requested and successful
    if success and args.verify and not args.dry_run:
        reembedder.verify_embedding()

    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
