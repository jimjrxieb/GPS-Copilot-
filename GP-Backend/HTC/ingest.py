#!/usr/bin/env python3
"""
Unified Knowledge Ingestion for Jade
====================================

Ingests knowledge from multiple formats into RAG + Knowledge Graph.

Supported formats:
- Markdown (.md)
- Text (.txt)
- JSONL conversations ({"messages": [...]})
- JSONL documents ({"doc_id": ..., "text": ...})

Usage:
    # Ingest all files in unprocessed/
    python ingest.py

    # Ingest specific file
    python ingest.py --file unprocessed/my-doc.md

    # Dry run (preview without ingesting)
    python ingest.py --dry-run

    # Build knowledge graph after ingestion
    python ingest.py --build-graph

    # Ingest and build graph in one command
    python ingest.py --all

Examples:
    # Simple: Drop files and ingest
    cp ~/my-docs/*.md unprocessed/
    python ingest.py

    # JSONL training data
    cp ~/cks-training.jsonl unprocessed/jade-knowledge/
    python ingest.py --file unprocessed/jade-knowledge/cks-training.jsonl

    # Full workflow (ingest + build graph)
    python ingest.py --all
"""

import os
import sys
import json
import pickle
import argparse
import networkx as nx
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Force CPU mode to avoid CUDA compatibility issues
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Add GP-AI to path for RAG engine
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-Frontend" / "GP-AI"))
from core.rag_engine import RAGEngine


class UnifiedIngester:
    """Unified ingestion for all knowledge formats"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.rag_engine = None if dry_run else RAGEngine()
        self.stats = {
            "markdown_files": 0,
            "text_files": 0,
            "jsonl_files": 0,
            "conversations_ingested": 0,
            "documents_ingested": 0,
            "total_docs": 0,
            "errors": 0
        }

    # ====================================================================
    # MARKDOWN / TEXT INGESTION (from simple_learn.py)
    # ====================================================================

    def ingest_markdown(self, file_path: Path) -> bool:
        """
        Ingest markdown or text file.

        Returns True if successful, False otherwise.
        """
        try:
            # Read file
            content = file_path.read_text(encoding='utf-8')

            if len(content) < 50:
                print(f"  ⏭️  Skipping {file_path.name} (too short, <50 chars)")
                return False

            # Prepare document
            document = {
                "content": content,
                "metadata": {
                    "source": str(file_path.name),
                    "filename": file_path.name,
                    "type": file_path.suffix,
                    "ingested_at": datetime.now().isoformat()
                },
                "id": f"learned_{file_path.name}_{hash(content)}"
            }

            if not self.dry_run:
                # Add to RAG
                self.rag_engine.add_security_knowledge("docs", [document])
            else:
                print(f"  🔍 [DRY RUN] Would ingest to 'docs' collection")

            print(f"  ✅ Ingested: {file_path.name} ({len(content)} chars)")

            # Update stats
            if file_path.suffix == ".md":
                self.stats["markdown_files"] += 1
            elif file_path.suffix == ".txt":
                self.stats["text_files"] += 1
            self.stats["total_docs"] += 1

            return True

        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
            self.stats["errors"] += 1
            return False

    # ====================================================================
    # JSONL INGESTION (from ingest_jade_knowledge.py)
    # ====================================================================

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

    def ingest_jsonl(self, file_path: Path) -> bool:
        """
        Ingest a single JSONL file (conversations or documents).

        Returns True if successful, False otherwise.
        """
        print(f"\n📂 Processing JSONL: {file_path.name}")

        documents = []
        line_count = 0
        errors_in_file = 0

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
                        errors_in_file += 1
                    except Exception as e:
                        print(f"  ❌ Line {line_num}: Processing error - {e}")
                        errors_in_file += 1

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

            self.stats["jsonl_files"] += 1
            self.stats["total_docs"] += line_count
            self.stats["errors"] += errors_in_file
            print(f"  ✅ Processed {line_count} lines from {file_path.name}")

            return True

        except Exception as e:
            print(f"  ❌ File error: {e}")
            self.stats["errors"] += 1
            return False

    # ====================================================================
    # DIRECTORY PROCESSING
    # ====================================================================

    def ingest_file(self, file_path: Path) -> bool:
        """
        Ingest a single file (auto-detects format).

        Returns True if successful, False otherwise.
        """
        if file_path.suffix in [".md", ".txt"]:
            return self.ingest_markdown(file_path)
        elif file_path.suffix == ".jsonl":
            return self.ingest_jsonl(file_path)
        else:
            print(f"  ⚠️  Unsupported file type: {file_path.suffix}")
            return False

    def ingest_directory(self, directory: Path):
        """Ingest all supported files in directory and subdirectories"""

        # Find all supported files
        markdown_files = list(directory.glob("**/*.md"))
        text_files = list(directory.glob("**/*.txt"))
        jsonl_files = list(directory.glob("**/*.jsonl"))

        all_files = markdown_files + text_files + jsonl_files

        if not all_files:
            print(f"📭 No supported files found in {directory}")
            return

        print(f"\n📚 Found {len(all_files)} files to process:")
        print(f"   - Markdown: {len(markdown_files)}")
        print(f"   - Text: {len(text_files)}")
        print(f"   - JSONL: {len(jsonl_files)}")
        print(f"{'='*60}\n")

        # Process each file
        processed_files = []
        for file_path in sorted(all_files):
            if self.ingest_file(file_path):
                processed_files.append(file_path)

        # Move processed files (if not dry-run and not JSONL)
        if not self.dry_run:
            processed_dir = directory.parent / "processed"
            processed_dir.mkdir(exist_ok=True)

            for file_path in processed_files:
                # Don't move JSONL files (keep them in jade-knowledge/)
                if file_path.suffix != ".jsonl" and file_path.parent.name != "jade-knowledge":
                    dest = processed_dir / file_path.name
                    # Avoid overwriting
                    if dest.exists():
                        dest = processed_dir / f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"
                    file_path.rename(dest)
                    print(f"   📦 Moved to: processed/{dest.name}")

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print ingestion summary"""
        print(f"\n{'='*60}")
        print(f"📊 Ingestion Summary:")
        print(f"{'='*60}")
        print(f"  Markdown files: {self.stats['markdown_files']}")
        print(f"  Text files: {self.stats['text_files']}")
        print(f"  JSONL files: {self.stats['jsonl_files']}")
        print(f"  Conversations: {self.stats['conversations_ingested']}")
        print(f"  Documents: {self.stats['documents_ingested']}")
        print(f"  Total items: {self.stats['total_docs']}")
        print(f"  Errors: {self.stats['errors']}")

        if self.dry_run:
            print(f"\n🔍 DRY RUN MODE - No data was actually ingested")
        else:
            print(f"\n✅ Knowledge successfully ingested into Jade RAG system")


class KnowledgeGraphBuilder:
    """Builds knowledge graph from RAG vectors (from graph_ingest_knowledge.py)"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.rag_engine = RAGEngine()

        # Load existing graph
        gp_copilot_root = Path(__file__).parent.parent.parent
        self.graph_file = gp_copilot_root / "GP-DATA" / "knowledge-base" / "security_graph.pkl"
        self.load_graph()

        self.stats = {
            "nodes_added": 0,
            "edges_added": 0,
            "relationships_created": 0
        }

    def load_graph(self):
        """Load existing knowledge graph or create new one"""
        if self.graph_file.exists():
            print(f"📂 Loading existing knowledge graph from {self.graph_file.name}")
            with open(self.graph_file, 'rb') as f:
                data = pickle.load(f)
                self.graph = data['graph']
                self.node_types = data.get('node_types', {})
            print(f"   Loaded: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        else:
            print(f"📂 Creating new knowledge graph")
            self.graph = nx.MultiDiGraph()
            self.node_types = {}

    def save_graph(self):
        """Save knowledge graph to disk"""
        if self.dry_run:
            print(f"🔍 [DRY RUN] Would save graph to {self.graph_file}")
            return

        self.graph_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.graph_file, 'wb') as f:
            pickle.dump({
                'graph': self.graph,
                'node_types': self.node_types,
                'last_updated': datetime.now().isoformat()
            }, f)
        print(f"💾 Saved knowledge graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")

    def build_graph(self):
        """Main graph building pipeline"""
        print(f"\n{'='*60}")
        print(f"🏗️  Building Knowledge Graph from RAG Vectors")
        print(f"{'='*60}")

        # Note: Full implementation from graph_ingest_knowledge.py
        # For now, just save the current graph state
        self.save_graph()

        print(f"\n📊 Knowledge Graph Summary:")
        print(f"  Total nodes: {self.graph.number_of_nodes()}")
        print(f"  Total edges: {self.graph.number_of_edges()}")

        if self.dry_run:
            print(f"\n🔍 DRY RUN MODE - No changes saved")
        else:
            print(f"\n✅ Knowledge graph updated")


def main():
    parser = argparse.ArgumentParser(
        description="Unified knowledge ingestion for Jade",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest all files in unprocessed/
  python ingest.py

  # Ingest specific file
  python ingest.py --file unprocessed/my-doc.md

  # Preview without ingesting
  python ingest.py --dry-run

  # Ingest and build knowledge graph
  python ingest.py --all

  # Just build knowledge graph (no ingestion)
  python ingest.py --build-graph
        """
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Ingest specific file (default: process all files in unprocessed/)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be ingested without actually ingesting"
    )
    parser.add_argument(
        "--build-graph",
        action="store_true",
        help="Build knowledge graph from RAG vectors after ingestion"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Ingest all files AND build knowledge graph (equivalent to --build-graph)"
    )

    args = parser.parse_args()

    # Set build_graph flag if --all is specified
    if args.all:
        args.build_graph = True

    print("=" * 60)
    print("Unified Knowledge Ingestion for Jade")
    print("=" * 60)

    # Determine base directory
    script_dir = Path(__file__).parent
    unprocessed_dir = script_dir / "unprocessed"

    if not unprocessed_dir.exists():
        print(f"❌ Directory not found: {unprocessed_dir}")
        print(f"   Creating it now...")
        unprocessed_dir.mkdir(parents=True, exist_ok=True)

    # Initialize ingester
    ingester = UnifiedIngester(dry_run=args.dry_run)

    # Process single file or entire directory
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        print(f"📄 Processing single file: {file_path.name}\n")
        ingester.ingest_file(file_path)
        ingester.print_summary()
    else:
        print(f"📁 Processing directory: {unprocessed_dir}\n")
        ingester.ingest_directory(unprocessed_dir)

    # Build knowledge graph if requested
    if args.build_graph:
        print(f"\n{'='*60}")
        builder = KnowledgeGraphBuilder(dry_run=args.dry_run)
        builder.build_graph()


if __name__ == "__main__":
    main()
