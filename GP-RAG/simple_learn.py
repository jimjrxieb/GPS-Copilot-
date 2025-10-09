#!/usr/bin/env python3
"""
Simple Learning Script - Drop files in unprocessed/ and run this

No dependencies needed, works with existing RAG engine.
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent / "GP-AI" / "core"))

from rag_engine import rag_engine

def learn_from_unprocessed():
    """Process all files in unprocessed directory"""

    unprocessed_dir = Path(__file__).parent / "unprocessed"
    processed_dir = Path(__file__).parent / "processed"
    processed_dir.mkdir(exist_ok=True)

    if not unprocessed_dir.exists():
        print(f"❌ Directory not found: {unprocessed_dir}")
        return

    # Find all markdown and text files
    files = list(unprocessed_dir.glob("*.md")) + \
            list(unprocessed_dir.glob("*.txt")) + \
            list(unprocessed_dir.glob("**/*.md")) + \
            list(unprocessed_dir.glob("**/*.txt"))

    if not files:
        print(f"📭 No files found in {unprocessed_dir}")
        return

    print(f"📚 Found {len(files)} files to learn from")

    processed_count = 0

    for file_path in files:
        try:
            # Read file
            content = file_path.read_text(encoding='utf-8')

            if len(content) < 50:
                print(f"⏭️  Skipping {file_path.name} (too short)")
                continue

            # Add to RAG
            documents = [{
                "content": content,
                "metadata": {
                    "source": str(file_path.relative_to(unprocessed_dir)),
                    "filename": file_path.name,
                    "type": file_path.suffix
                },
                "id": f"learned_{file_path.name}_{hash(content)}"
            }]

            rag_engine.add_security_knowledge("docs", documents)

            print(f"✅ Learned from: {file_path.name}")
            processed_count += 1

            # Move to processed
            dest = processed_dir / file_path.name
            file_path.rename(dest)
            print(f"   Moved to: processed/{file_path.name}")

        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")

    print(f"\n✅ Learning complete! Processed {processed_count}/{len(files)} files")

    # Show stats
    stats = rag_engine.get_stats()
    print(f"\n📊 RAG Stats:")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Collections: {list(stats['collections'].keys())}")

if __name__ == "__main__":
    print("=" * 80)
    print("Simple RAG Learning - Process unprocessed files")
    print("=" * 80)
    learn_from_unprocessed()
