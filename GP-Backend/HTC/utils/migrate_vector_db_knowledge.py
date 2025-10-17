#!/usr/bin/env python3
"""
Migrate Curated Knowledge from vector-db to knowledge-base

This script migrates valuable curated knowledge (compliance frameworks and CKS
knowledge) from the old vector-db location to the active knowledge-base, preserving
all metadata and marking them as curated seed knowledge.

Author: GP-Copilot / Claude Code
Date: 2025-10-13
"""

import chromadb
from pathlib import Path
import sys
from datetime import datetime

# Paths
OLD_DB_PATH = "/home/jimmie/linkops-industries/GP-copilot/GP-DATA/vector-db"
NEW_DB_PATH = "/home/jimmie/linkops-industries/GP-copilot/GP-DATA/knowledge-base/chroma"

def migrate_collection(old_client, new_client, collection_name: str, dry_run: bool = False):
    """Migrate a single collection from old to new database"""

    print(f"\n{'='*80}")
    print(f"📦 Migrating Collection: {collection_name}")
    print(f"{'='*80}")

    try:
        # Get source collection
        old_coll = old_client.get_collection(collection_name)
        old_count = old_coll.count()

        print(f"📊 Source documents: {old_count}")

        if old_count == 0:
            print(f"⏭️  Skipping (empty collection)")
            return 0

        # Get all data
        data = old_coll.get(include=["documents", "metadatas", "embeddings"])

        print(f"✅ Retrieved {len(data['ids'])} documents from source")

        # Show sample
        print(f"\n📝 Sample Document:")
        print(f"   ID: {data['ids'][0]}")
        print(f"   Metadata: {data['metadatas'][0]}")
        print(f"   Content Preview: {data['documents'][0][:150]}...")

        if dry_run:
            print(f"\n🔍 DRY RUN: Would migrate {len(data['ids'])} documents")
            print(f"   Target: {NEW_DB_PATH}/{collection_name}")
            return len(data['ids'])

        # Get or create target collection
        new_coll = new_client.get_or_create_collection(
            name=collection_name,
            metadata=old_coll.metadata
        )

        existing_count = new_coll.count()
        print(f"📊 Target collection existing documents: {existing_count}")

        # Prepare data with migration metadata
        migrated_ids = [f"curated_seed_{id}" for id in data['ids']]
        migrated_metadatas = []

        for meta in data['metadatas']:
            new_meta = meta.copy() if meta else {}
            new_meta['source'] = 'curated_seed'
            new_meta['migrated_at'] = datetime.now().isoformat()
            new_meta['original_db'] = 'vector-db'
            migrated_metadatas.append(new_meta)

        # Add to target collection
        print(f"\n⬆️  Uploading to target collection...")
        new_coll.add(
            ids=migrated_ids,
            documents=data['documents'],
            metadatas=migrated_metadatas,
            embeddings=data['embeddings']
        )

        new_count = new_coll.count()
        print(f"✅ Migration complete!")
        print(f"   Before: {existing_count} documents")
        print(f"   After: {new_count} documents")
        print(f"   Added: {new_count - existing_count} documents")

        return len(data['ids'])

    except Exception as e:
        print(f"❌ Error migrating {collection_name}: {e}")
        return 0


def main(dry_run: bool = False):
    """Main migration function"""

    print("="*80)
    print("🚀 GP-Copilot Knowledge Base Migration")
    print("="*80)
    print(f"Source: {OLD_DB_PATH}")
    print(f"Target: {NEW_DB_PATH}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
    print("="*80)

    # Verify paths exist
    if not Path(OLD_DB_PATH).exists():
        print(f"❌ Error: Source database not found at {OLD_DB_PATH}")
        sys.exit(1)

    if not Path(NEW_DB_PATH).exists():
        print(f"❌ Error: Target database not found at {NEW_DB_PATH}")
        sys.exit(1)

    # Connect to databases
    print("\n🔌 Connecting to databases...")
    old_client = chromadb.PersistentClient(path=OLD_DB_PATH)
    new_client = chromadb.PersistentClient(path=NEW_DB_PATH)

    print("✅ Connected successfully")

    # List collections in source
    old_collections = old_client.list_collections()
    print(f"\n📚 Found {len(old_collections)} collections in source database:")
    for coll in old_collections:
        count = coll.count()
        print(f"   - {coll.name}: {count} documents")

    # Migrate each non-empty collection
    total_migrated = 0
    collections_to_migrate = [
        "compliance_frameworks",
        "cks_knowledge"
    ]

    for collection_name in collections_to_migrate:
        migrated_count = migrate_collection(old_client, new_client, collection_name, dry_run)
        total_migrated += migrated_count

    # Summary
    print(f"\n{'='*80}")
    print(f"📊 Migration Summary")
    print(f"{'='*80}")
    print(f"Total documents migrated: {total_migrated}")
    print(f"Collections migrated: {len(collections_to_migrate)}")
    print(f"Mode: {'DRY RUN (no changes made)' if dry_run else 'LIVE MIGRATION (completed)'}")

    if not dry_run:
        print(f"\n✅ Migration completed successfully!")
        print(f"\nℹ️  Next steps:")
        print(f"   1. Verify migrated data:")
        print(f"      python GP-RAG/migrate_vector_db_knowledge.py --verify")
        print(f"   2. Test RAG queries to ensure curated knowledge is accessible")
        print(f"   3. Archive old vector-db:")
        print(f"      mv {OLD_DB_PATH} {OLD_DB_PATH}.archived.{datetime.now().strftime('%Y%m%d')}")
    else:
        print(f"\n🔍 Dry run complete. Run without --dry-run to execute migration.")

    print("="*80)


def verify_migration():
    """Verify migrated data in target database"""

    print("="*80)
    print("🔍 Verifying Migration")
    print("="*80)

    client = chromadb.PersistentClient(path=NEW_DB_PATH)

    # Check for curated seed documents
    collections = ["compliance_frameworks", "cks_knowledge"]

    for coll_name in collections:
        print(f"\n📁 Collection: {coll_name}")
        coll = client.get_collection(coll_name)

        # Get all curated seed documents
        all_data = coll.get(include=["metadatas"])
        curated_docs = [
            (id, meta) for id, meta in zip(all_data['ids'], all_data['metadatas'])
            if meta and meta.get('source') == 'curated_seed'
        ]

        print(f"   Total documents: {coll.count()}")
        print(f"   Curated seed documents: {len(curated_docs)}")

        if curated_docs:
            print(f"\n   ✅ Sample curated document:")
            print(f"      ID: {curated_docs[0][0]}")
            print(f"      Metadata: {curated_docs[0][1]}")

    print(f"\n{'='*80}")
    print("✅ Verification complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate curated knowledge from vector-db to knowledge-base"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making changes"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify migration (check for curated seed documents)"
    )

    args = parser.parse_args()

    if args.verify:
        verify_migration()
    else:
        main(dry_run=args.dry_run)
