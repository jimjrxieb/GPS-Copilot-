# Utility Scripts

These are **one-time** or **rarely used** scripts.

---

## Scripts

### `migrate_vector_db_knowledge.py`

**Purpose**: One-time migration script for moving knowledge between vector databases.

**When to use**:
- Migrating from old ChromaDB structure to new
- Moving data between environments
- Rarely needed (maybe once per year)

**Usage**:
```bash
python migrate_vector_db_knowledge.py --dry-run
python migrate_vector_db_knowledge.py
```

---

### `reembed_processed_files.py`

**Purpose**: Re-embed files that are already in the `processed/` directory.

**When to use**:
- Embedding model was upgraded
- Fixing corrupted embeddings
- Rarely needed

**Usage**:
```bash
python reembed_processed_files.py --dry-run
python reembed_processed_files.py
```

---

## Why Here?

These scripts are **utilities** that:
- Are used **very rarely** (maybe once per year)
- Are **one-time** operations (not part of regular workflow)
- Would **clutter** the main HTC directory

---

Last updated: 2025-10-16
