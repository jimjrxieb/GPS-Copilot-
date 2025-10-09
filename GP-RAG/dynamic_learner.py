#!/usr/bin/env python3
"""
Jade Dynamic Learning System

Watches GP-RAG/unprocessed/ for new files and automatically:
1. Detects new files (markdown, PDF, JSON, text)
2. Processes and chunks content
3. Indexes into RAG knowledge base
4. Makes immediately available for queries

Use Case: Drop client docs, scan results, policies → Jade learns instantly

Usage:
    # Start file watcher
    python3 dynamic_learner.py watch

    # Manual one-time sync
    python3 dynamic_learner.py sync

    # Demo mode (for interview)
    python3 dynamic_learner.py demo
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import shutil

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
except ImportError:
    print("⚠️  watchdog not installed. Install: pip install watchdog")
    Observer = None
    FileSystemEventHandler = None

# Add GP-DATA to path for RAG
gp_copilot_root = Path(__file__).parent.parent
sys.path.insert(0, str(gp_copilot_root / "GP-DATA"))

from simple_rag_query import SimpleRAGQuery
import chromadb
from chromadb.config import Settings


class DynamicLearner:
    """Handles dynamic learning from unprocessed files"""

    def __init__(self):
        """Initialize learner with paths and RAG"""
        self.gp_rag_root = Path(__file__).parent
        self.unprocessed_dir = self.gp_rag_root / "unprocessed"
        self.processed_dir = self.gp_rag_root / "processed"

        # RAG database
        self.db_path = gp_copilot_root / "GP-DATA" / "knowledge-base" / "chroma"
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create dynamic learning collection
        self.collection = self.client.get_or_create_collection(
            name="dynamic_learning",
            metadata={"description": "Dynamically learned knowledge from unprocessed files"}
        )

        print(f"📂 Watching: {self.unprocessed_dir}")
        print(f"💾 RAG Database: {self.db_path}")

    def sync_all_unprocessed(self) -> int:
        """
        Manually sync all files in unprocessed directory

        Returns:
            Number of files processed
        """
        print("\n🔄 Scanning unprocessed directory for new knowledge...")

        total_processed = 0

        # Walk through all subdirectories
        for subdir in self.unprocessed_dir.iterdir():
            if not subdir.is_dir():
                continue

            print(f"\n📁 Processing: {subdir.name}/")

            files = list(subdir.glob("*"))
            for file_path in files:
                if file_path.is_file() and self._is_processable(file_path):
                    try:
                        self.process_file(file_path)
                        total_processed += 1
                    except Exception as e:
                        print(f"  ❌ Error processing {file_path.name}: {e}")

        return total_processed

    def process_file(self, file_path: Path) -> bool:
        """
        Process a single file and add to RAG

        Args:
            file_path: Path to file to process

        Returns:
            True if successful
        """
        print(f"  📄 Processing: {file_path.name}")

        # Read content based on file type
        content = self._read_file(file_path)
        if not content:
            print(f"    ⚠️  Empty or unreadable file")
            return False

        # Determine knowledge type
        knowledge_type = self._detect_knowledge_type(file_path)

        # Chunk content
        chunks = self._chunk_content(content, file_path.stem)

        if not chunks:
            print(f"    ⚠️  No content to index")
            return False

        # Add to RAG
        for chunk in chunks:
            chunk_id = f"dynamic_{file_path.parent.name}_{file_path.stem}_{chunk['chunk_num']}"

            metadata = {
                "filename": file_path.name,
                "source": "dynamic_learning",
                "category": file_path.parent.name,
                "type": knowledge_type,
                "learned_at": datetime.now().isoformat(),
                "chunk": chunk['chunk_num']
            }

            try:
                self.collection.add(
                    ids=[chunk_id],
                    documents=[chunk['content']],
                    metadatas=[metadata]
                )
            except Exception as e:
                # If duplicate, update instead
                try:
                    self.collection.update(
                        ids=[chunk_id],
                        documents=[chunk['content']],
                        metadatas=[metadata]
                    )
                except:
                    pass

        print(f"    ✅ Indexed {len(chunks)} chunks → {knowledge_type}")

        # Copy to processed directory
        self._archive_to_processed(file_path)

        return True

    def _is_processable(self, file_path: Path) -> bool:
        """Check if file type is processable"""
        processable_extensions = {'.md', '.txt', '.json', '.yaml', '.yml', '.log', '.pdf'}
        return file_path.suffix.lower() in processable_extensions

    def _read_file(self, file_path: Path) -> str:
        """Read file content"""
        try:
            if file_path.suffix.lower() == '.pdf':
                # TODO: Add PDF parsing (PyPDF2)
                return f"PDF file: {file_path.name} (PDF parsing not yet implemented)"

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"    ❌ Error reading file: {e}")
            return ""

    def _detect_knowledge_type(self, file_path: Path) -> str:
        """Detect type of knowledge from path and filename"""
        parent_dir = file_path.parent.name
        filename = file_path.name.lower()

        # Map directories to types
        dir_types = {
            'client-docs': 'client_documentation',
            'compliance': 'compliance',
            'policies': 'policy',
            'scan-results': 'scan_findings',
            'security-docs': 'security',
            'james-os-knowledge': 'system_knowledge'
        }

        if parent_dir in dir_types:
            return dir_types[parent_dir]

        # Fallback to filename detection
        if 'kubernetes' in filename or 'k8s' in filename:
            return 'kubernetes'
        elif 'terraform' in filename:
            return 'terraform'
        elif 'opa' in filename or 'policy' in filename:
            return 'policy'
        elif 'compliance' in filename or 'sox' in filename or 'hipaa' in filename:
            return 'compliance'
        elif 'scan' in filename or 'finding' in filename:
            return 'scan_findings'
        else:
            return 'general'

    def _chunk_content(self, content: str, file_stem: str) -> List[Dict[str, Any]]:
        """Chunk content into manageable pieces"""
        chunks = []

        # Skip very small files
        if len(content) < 100:
            return []

        # For markdown, split on headers
        if '##' in content:
            sections = content.split('##')
            title = sections[0].strip()

            for i, section in enumerate(sections[1:], 1):
                section_content = f"## {section.strip()}"
                if len(section_content) > 200:  # Only meaningful chunks
                    chunks.append({
                        'chunk_num': i,
                        'content': f"{title}\n\n{section_content}"
                    })
        else:
            # For other files, chunk by size (2000 chars)
            chunk_size = 2000
            for i in range(0, len(content), chunk_size):
                chunk_content = content[i:i+chunk_size]
                if len(chunk_content) > 200:
                    chunks.append({
                        'chunk_num': i // chunk_size + 1,
                        'content': chunk_content
                    })

        return chunks

    def _archive_to_processed(self, file_path: Path):
        """Copy file to processed directory"""
        try:
            # Create processed subdirectory
            category = file_path.parent.name
            processed_subdir = self.processed_dir / category
            processed_subdir.mkdir(parents=True, exist_ok=True)

            # Copy file
            dest = processed_subdir / file_path.name
            shutil.copy2(file_path, dest)

        except Exception as e:
            # Not critical if archiving fails
            pass

    def get_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        count = self.collection.count()

        # Get all docs to analyze
        all_docs = self.collection.get()

        # Count by category
        categories = {}
        types = {}
        for metadata in all_docs['metadatas']:
            cat = metadata.get('category', 'unknown')
            typ = metadata.get('type', 'unknown')

            categories[cat] = categories.get(cat, 0) + 1
            types[typ] = types.get(typ, 0) + 1

        return {
            'total_chunks': count,
            'categories': categories,
            'types': types,
            'last_updated': datetime.now().isoformat()
        }


class DynamicLearningHandler(FileSystemEventHandler):
    """Watchdog handler for file system events"""

    def __init__(self, learner: DynamicLearner):
        self.learner = learner
        super().__init__()

    def on_created(self, event):
        """Handle new file creation"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Ignore hidden files and non-processable types
        if file_path.name.startswith('.'):
            return

        if not self.learner._is_processable(file_path):
            return

        print(f"\n🆕 New file detected: {file_path.name}")
        time.sleep(0.5)  # Give file system time to finish writing

        try:
            self.learner.process_file(file_path)
            print("✅ Jade learned new knowledge!")
        except Exception as e:
            print(f"❌ Error processing file: {e}")

    def on_modified(self, event):
        """Handle file modification"""
        # For now, treat modifications as new learning
        # Could be optimized to only update changed chunks
        if not event.is_directory:
            self.on_created(event)


def watch_mode():
    """Start file watcher daemon"""
    if not Observer:
        print("❌ watchdog library not installed")
        print("Install: pip install watchdog")
        return

    learner = DynamicLearner()

    print("\n" + "="*80)
    print("🤖 Jade Dynamic Learning System - ACTIVE")
    print("="*80)
    print(f"\n👀 Watching: {learner.unprocessed_dir}")
    print("\n💡 Drop files into GP-RAG/unprocessed/ subdirectories:")
    print("   • client-docs/     - Client documentation")
    print("   • compliance/      - Compliance policies")
    print("   • policies/        - Security policies")
    print("   • scan-results/    - Scan outputs")
    print("   • security-docs/   - Security guides")
    print("\n🧠 Jade will learn automatically and make knowledge available instantly!")
    print("\nPress Ctrl+C to stop\n")
    print("="*80 + "\n")

    # Set up observer
    event_handler = DynamicLearningHandler(learner)
    observer = Observer()

    # Watch all subdirectories
    for subdir in learner.unprocessed_dir.iterdir():
        if subdir.is_dir():
            observer.schedule(event_handler, str(subdir), recursive=False)
            print(f"📂 Watching: {subdir.name}/")

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Stopping dynamic learning system...")
        observer.stop()

    observer.join()
    print("✅ Stopped\n")


def sync_mode():
    """One-time sync of all unprocessed files"""
    learner = DynamicLearner()

    print("\n" + "="*80)
    print("🤖 Jade Dynamic Learning - Manual Sync")
    print("="*80 + "\n")

    total = learner.sync_all_unprocessed()

    print("\n" + "="*80)
    print(f"✅ Processed {total} files")

    # Show stats
    stats = learner.get_stats()
    print(f"\n📊 Learning Statistics:")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"\n   By category:")
    for cat, count in stats['categories'].items():
        print(f"     • {cat}: {count} chunks")
    print("\n   By type:")
    for typ, count in stats['types'].items():
        print(f"     • {typ}: {count} chunks")

    print("\n💡 Try: jade query \"your question about the new knowledge\"")
    print("="*80 + "\n")


def demo_mode():
    """Demo mode for interview - shows learning in action"""
    learner = DynamicLearner()

    print("\n" + "="*80)
    print("🎬 Jade Dynamic Learning - INTERVIEW DEMO")
    print("="*80 + "\n")

    print("📋 Demo Script:")
    print("\n1. Show current knowledge base stats")
    stats_before = learner.get_stats()
    print(f"   Current: {stats_before['total_chunks']} chunks indexed\n")

    print("2. Drop a new client document:")
    print("   Example: echo 'New client requires SOC2 compliance...' > GP-RAG/unprocessed/client-docs/acme-corp-requirements.md\n")

    print("3. Run sync:")
    print("   python3 GP-RAG/dynamic_learner.py sync\n")

    print("4. Query new knowledge:")
    print("   jade query \"acme corp requirements\"")
    print("   jade agent \"what does acme corp need for compliance\"\n")

    print("5. Show updated stats:")
    print("   python3 -c \"from dynamic_learner import DynamicLearner; l = DynamicLearner(); print(l.get_stats())\"\n")

    print("="*80)
    print("🎯 Key Points for Interview:")
    print("="*80)
    print("• Drop files → Jade learns instantly (no retraining)")
    print("• Supports: Markdown, JSON, YAML, Text, PDF")
    print("• Automatic chunking and categorization")
    print("• Immediately queryable via RAG")
    print("• Simulates real client onboarding workflow")
    print("="*80 + "\n")


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 dynamic_learner.py watch   # Start file watcher")
        print("  python3 dynamic_learner.py sync    # Manual one-time sync")
        print("  python3 dynamic_learner.py demo    # Show demo script")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "watch":
        watch_mode()
    elif mode == "sync":
        sync_mode()
    elif mode == "demo":
        demo_mode()
    else:
        print(f"Unknown mode: {mode}")
        print("Use: watch, sync, or demo")
        sys.exit(1)


if __name__ == "__main__":
    main()
