#!/usr/bin/env python3
"""
Jade Knowledge Ingestion Script
================================

Processes JSONL training data from GP-RAG/unprocessed/jade-knowledge/ into Jade's RAG system.

Supports two JSONL formats:
1. Conversation format (CKS, cloud training):
   {"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}

2. Document chunk format (OPA knowledge):
   {"doc_id": "...", "chunk_id": "...", "title": "...", "text": "...", "metadata": {...}}

Usage:
    python ingest_jade_knowledge.py
    python ingest_jade_knowledge.py --file cks-training1.jsonl
    python ingest_jade_knowledge.py --dry-run
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Force CPU mode to avoid CUDA compatibility issues
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Add GP-AI to path for RAG engine
sys.path.insert(0, str(Path(__file__).parent.parent / "GP-AI"))
from core.rag_engine import RAGEngine


class JadeKnowledgeIngester:
    """Processes JSONL knowledge files into Jade RAG system"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.rag_engine = None if dry_run else RAGEngine()
        self.stats = {
            "files_processed": 0,
            "conversations_ingested": 0,
            "documents_ingested": 0,
            "errors": 0
        }

    def ingest_conversation_format(self, messages: List[Dict], file_name: str, line_num: int) -> Dict[str, Any]:
        """
        Process conversation format JSONL into document.

        Format: {"messages": [{"role": "system", "content": "..."}, ...]}

        Returns document for RAG ingestion.
        """
        system_msg = ""
        user_msg = ""
        assistant_msg = ""

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "system":
                system_msg = content
            elif role == "user":
                user_msg = content
            elif role == "assistant":
                assistant_msg = content

        # Combine into searchable document
        combined_content = f"""
Question: {user_msg}

Answer: {assistant_msg}

Context: {system_msg}
""".strip()

        # Determine knowledge type from file name
        knowledge_type = self._classify_knowledge_type(file_name)

        return {
            "content": combined_content,
            "id": f"{file_name}_{line_num}",
            "metadata": {
                "source": file_name,
                "line": line_num,
                "type": "conversation",
                "knowledge_type": knowledge_type,
                "question": user_msg[:100],  # Truncate for metadata
                "ingested_at": datetime.now().isoformat()
            }
        }

    def ingest_document_format(self, doc: Dict, file_name: str, line_num: int) -> Dict[str, Any]:
        """
        Process document chunk format JSONL into document.

        Format: {"doc_id": "...", "chunk_id": "...", "title": "...", "text": "...", "metadata": {...}}

        Returns document for RAG ingestion.
        """
        doc_id = doc.get("doc_id", f"{file_name}_{line_num}")
        chunk_id = doc.get("chunk_id", doc_id)
        title = doc.get("title", "Untitled")
        text = doc.get("text", "")
        metadata = doc.get("metadata", {})

        # Combine title + text for better searchability
        combined_content = f"{title}\n\n{text}".strip()

        # Determine knowledge type
        knowledge_type = self._classify_knowledge_type(file_name)

        # Merge metadata (convert lists to comma-separated strings for ChromaDB)
        final_metadata = {
            "source": file_name,
            "line": line_num,
            "type": "document",
            "knowledge_type": knowledge_type,
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "title": title,
            "ingested_at": datetime.now().isoformat()
        }
        # ChromaDB only supports str, int, float, bool - convert lists to strings
        for key, value in metadata.items():
            if isinstance(value, list):
                final_metadata[key] = ", ".join(str(v) for v in value)
            elif isinstance(value, (str, int, float, bool)) or value is None:
                final_metadata[key] = value
            else:
                final_metadata[key] = str(value)

        return {
            "content": combined_content,
            "id": chunk_id,
            "metadata": final_metadata
        }

    def _classify_knowledge_type(self, file_name: str) -> str:
        """Determine RAG collection based on file name"""
        file_lower = file_name.lower()

        if "cks" in file_lower or "kubernetes" in file_lower:
            return "cks"
        elif "cloud" in file_lower or "argocd" in file_lower or "helm" in file_lower:
            return "patterns"
        elif "opa" in file_lower or "policy" in file_lower or "rego" in file_lower:
            return "compliance"
        else:
            return "patterns"  # Default

    def ingest_jsonl_file(self, file_path: Path) -> int:
        """
        Ingest a single JSONL file.

        Returns number of lines processed.
        """
        print(f"\n📂 Processing: {file_path.name}")

        documents = []
        line_count = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)

                        # Determine format and process
                        if "messages" in data:
                            # Conversation format
                            doc = self.ingest_conversation_format(
                                data["messages"],
                                file_path.name,
                                line_num
                            )
                            documents.append(doc)
                            self.stats["conversations_ingested"] += 1

                        elif "text" in data or "doc_id" in data:
                            # Document chunk format
                            doc = self.ingest_document_format(
                                data,
                                file_path.name,
                                line_num
                            )
                            documents.append(doc)
                            self.stats["documents_ingested"] += 1

                        else:
                            print(f"  ⚠️  Line {line_num}: Unknown format, skipping")
                            continue

                        line_count += 1

                    except json.JSONDecodeError as e:
                        print(f"  ❌ Line {line_num}: JSON parse error - {e}")
                        self.stats["errors"] += 1
                    except Exception as e:
                        print(f"  ❌ Line {line_num}: Processing error - {e}")
                        self.stats["errors"] += 1

            # Batch ingest to RAG engine
            if documents:
                if not self.dry_run:
                    # Group by knowledge type
                    by_type = {}
                    for doc in documents:
                        ktype = doc["metadata"]["knowledge_type"]
                        if ktype not in by_type:
                            by_type[ktype] = []
                        by_type[ktype].append(doc)

                    # Ingest each type
                    for ktype, docs in by_type.items():
                        print(f"  💾 Ingesting {len(docs)} documents to '{ktype}' collection...")
                        self.rag_engine.add_security_knowledge(ktype, docs)
                else:
                    print(f"  🔍 [DRY RUN] Would ingest {len(documents)} documents")

            self.stats["files_processed"] += 1
            print(f"  ✅ Processed {line_count} lines from {file_path.name}")
            return line_count

        except Exception as e:
            print(f"  ❌ File error: {e}")
            self.stats["errors"] += 1
            return 0

    def ingest_directory(self, directory: Path):
        """Ingest all JSONL files in directory"""
        jsonl_files = sorted(directory.glob("*.jsonl"))

        if not jsonl_files:
            print(f"❌ No JSONL files found in {directory}")
            return

        print(f"📚 Found {len(jsonl_files)} JSONL files in {directory.name}/")
        print(f"{'='*60}")

        for jsonl_file in jsonl_files:
            self.ingest_jsonl_file(jsonl_file)

        print(f"\n{'='*60}")
        print(f"📊 Ingestion Summary:")
        print(f"  Files processed: {self.stats['files_processed']}")
        print(f"  Conversations ingested: {self.stats['conversations_ingested']}")
        print(f"  Documents ingested: {self.stats['documents_ingested']}")
        print(f"  Total items: {self.stats['conversations_ingested'] + self.stats['documents_ingested']}")
        print(f"  Errors: {self.stats['errors']}")

        if self.dry_run:
            print(f"\n🔍 DRY RUN MODE - No data was actually ingested")
        else:
            print(f"\n✅ Knowledge successfully ingested into Jade RAG system")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest Jade knowledge from JSONL files into RAG system"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Process a specific JSONL file (default: process all files)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be ingested without actually ingesting"
    )
    parser.add_argument(
        "--directory",
        type=str,
        default="unprocessed/jade-knowledge",
        help="Directory containing JSONL files (relative to GP-RAG/)"
    )

    args = parser.parse_args()

    # Determine base directory
    script_dir = Path(__file__).parent
    knowledge_dir = script_dir / args.directory

    if not knowledge_dir.exists():
        print(f"❌ Directory not found: {knowledge_dir}")
        sys.exit(1)

    # Initialize ingester
    ingester = JadeKnowledgeIngester(dry_run=args.dry_run)

    # Process single file or entire directory
    if args.file:
        file_path = knowledge_dir / args.file
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        ingester.ingest_jsonl_file(file_path)
    else:
        ingester.ingest_directory(knowledge_dir)


if __name__ == "__main__":
    main()
