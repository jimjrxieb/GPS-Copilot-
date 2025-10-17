#!/usr/bin/env python3
"""
Base Ingester Class
===================

Base class for all specialized ingesters with common functionality.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

# Force CPU mode
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Add GP-AI to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "GP-Frontend" / "GP-AI"))
from core.rag_engine import RAGEngine


class BaseIngester(ABC):
    """Base class for specialized ingesters"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.rag_engine = None if dry_run else RAGEngine()
        self.stats = {
            "files_processed": 0,
            "documents_ingested": 0,
            "errors": 0,
            "sanitizations": 0
        }

        # Path to jade-knowledge ChromaDB
        self.chroma_base = Path(__file__).parent.parent.parent.parent.parent / "GP-DATA" / "jade-knowledge" / "chroma"
        self.chroma_base.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def get_category(self) -> str:
        """Return the category name (e.g., 'intake', 'technical')"""
        pass

    @abstractmethod
    def get_subcategories(self) -> List[str]:
        """Return list of subcategories (e.g., ['clients', 'meetings', 'people'])"""
        pass

    @abstractmethod
    def process_file(self, file_path: Path, subcategory: str) -> List[Dict[str, Any]]:
        """
        Process a single file and return list of documents.

        Returns:
            List of documents with structure:
            {
                "content": "...",
                "id": "...",
                "metadata": {...}
            }
        """
        pass

    def get_collection_name(self, subcategory: str) -> str:
        """Get ChromaDB collection name for subcategory"""
        return subcategory.lower().replace(" ", "-")

    def ingest_documents(self, documents: List[Dict[str, Any]], collection: str):
        """Ingest documents to ChromaDB collection"""
        if not documents:
            return

        if not self.dry_run:
            print(f"  💾 Ingesting {len(documents)} documents to '{collection}' collection...")
            self.rag_engine.add_security_knowledge(collection, documents)
        else:
            print(f"  🔍 [DRY RUN] Would ingest {len(documents)} documents to '{collection}'")

        self.stats["documents_ingested"] += len(documents)

    def ingest_file(self, file_path: Path, subcategory: str) -> bool:
        """
        Ingest a single file.

        Returns True if successful, False otherwise.
        """
        try:
            print(f"\n📂 Processing: {file_path.name} ({subcategory})")

            # Process file (implemented by subclass)
            documents = self.process_file(file_path, subcategory)

            if not documents:
                print(f"  ⚠️  No documents generated from {file_path.name}")
                return False

            # Get collection name
            collection = self.get_collection_name(subcategory)

            # Ingest to ChromaDB
            self.ingest_documents(documents, collection)

            self.stats["files_processed"] += 1
            print(f"  ✅ Processed {file_path.name} → {len(documents)} documents")

            return True

        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
            self.stats["errors"] += 1
            return False

    def ingest_directory(self, directory: Path):
        """Ingest all files in directory (organized by subcategory)"""

        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return

        print(f"\n{'='*60}")
        print(f"📚 Ingesting from: {directory.name}/")
        print(f"   Category: {self.get_category()}")
        print(f"   Subcategories: {', '.join(self.get_subcategories())}")
        print(f"{'='*60}\n")

        # Process each subcategory
        for subcategory in self.get_subcategories():
            subcat_dir = directory / subcategory
            if not subcat_dir.exists():
                print(f"⏭️  Skipping {subcategory}/ (not found)")
                continue

            # Find all markdown files
            files = list(subcat_dir.glob("*.md")) + list(subcat_dir.glob("*.txt"))

            if not files:
                print(f"📭 No files in {subcategory}/")
                continue

            print(f"\n📁 Processing {subcategory}/ ({len(files)} files)")

            for file_path in sorted(files):
                self.ingest_file(file_path, subcategory)

        self.print_summary()

    def print_summary(self):
        """Print ingestion summary"""
        print(f"\n{'='*60}")
        print(f"📊 {self.get_category().title()} Ingestion Summary:")
        print(f"{'='*60}")
        print(f"  Files processed: {self.stats['files_processed']}")
        print(f"  Documents ingested: {self.stats['documents_ingested']}")
        print(f"  Sanitizations: {self.stats['sanitizations']}")
        print(f"  Errors: {self.stats['errors']}")

        if self.dry_run:
            print(f"\n🔍 DRY RUN MODE - No data was actually ingested")
        else:
            print(f"\n✅ Knowledge successfully ingested into Jade RAG system")
            print(f"   ChromaDB location: {self.chroma_base}")
