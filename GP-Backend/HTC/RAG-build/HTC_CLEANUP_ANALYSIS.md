# HTC Directory Cleanup Analysis

**Date**: 2025-10-16
**Status**: 🚨 **NEEDS CONSOLIDATION**

---

## The Problem

**HTC has 14 Python scripts doing overlapping work:**

```
GP-Backend/HTC/
├── simple_learn.py              # Ingests markdown/txt from unprocessed/
├── ingest_jade_knowledge.py     # Ingests JSONL from unprocessed/jade-knowledge/
├── graph_ingest_knowledge.py    # Builds graph relationships from RAG vectors
├── ingest_scan_results.py       # Ingests security scan findings
├── auto_sync.py                 # Auto-watches workspace for changes
├── dynamic_learner.py           # File watcher for unprocessed/ (requires watchdog)
├── migrate_vector_db_knowledge.py  # One-time migration script
├── reembed_processed_files.py   # Re-embeds processed/ files
├── jade.py                      # Legacy orchestrator
├── jade_api.py                  # API interface
├── jade_rag_langgraph.py        # RAG + Graph + LangGraph integration
├── test_auto_sync.py            # Tests auto-sync
├── test_jade_ai.py              # Tests jade.py
└── test_jade_comprehensive.py   # Tests RAG + LangGraph
```

**That's 14 scripts. Most are doing similar things.**

---

## Script Analysis

### Ingestion Scripts (5 scripts doing similar work)

| Script | Purpose | Input | Output | Keep? |
|--------|---------|-------|--------|-------|
| `simple_learn.py` | Ingest `.md`/`.txt` | `unprocessed/*.md` | RAG (docs collection) | ✅ **PRIMARY** |
| `ingest_jade_knowledge.py` | Ingest JSONL (conversations + docs) | `unprocessed/jade-knowledge/*.jsonl` | RAG (cks/compliance/patterns) | ✅ **KEEP** (unique format) |
| `graph_ingest_knowledge.py` | Build graph from RAG vectors | RAG collections | Knowledge Graph | ✅ **KEEP** (graph builder) |
| `ingest_scan_results.py` | Ingest security scans | `GP-DATA/active/scans/` | RAG + Graph | ⚠️ **MOVE TO GP-DATA** |
| `reembed_processed_files.py` | Re-embed processed files | `processed/` | RAG | ❌ **UTILITY - archive** |

### Auto-Learning Scripts (2 scripts doing same thing)

| Script | Purpose | Mechanism | Keep? |
|--------|---------|-----------|-------|
| `auto_sync.py` | Auto-watch workspace | Polling (no deps) | ✅ **KEEP** |
| `dynamic_learner.py` | Auto-watch unprocessed/ | File watcher (needs `watchdog`) | ❌ **DELETE** (redundant) |

### Core/API Scripts (3 scripts - consolidate)

| Script | Purpose | Keep? |
|--------|---------|-------|
| `jade.py` | Legacy orchestrator | ❌ **DEPRECATE** (use jade_rag_langgraph.py) |
| `jade_api.py` | API interface | ⚠️ **EVALUATE** (vs GP-Frontend/GP-AI/api/) |
| `jade_rag_langgraph.py` | RAG + Graph + LangGraph | ✅ **PRIMARY ENGINE** |

### Migration/Utility Scripts (2 scripts - one-time use)

| Script | Purpose | Keep? |
|--------|---------|-------|
| `migrate_vector_db_knowledge.py` | One-time migration | 🗄️ **ARCHIVE** |
| `reembed_processed_files.py` | Re-embed files | 🗄️ **ARCHIVE** |

### Test Scripts (3 scripts - keep)

| Script | Purpose | Keep? |
|--------|---------|-------|
| `test_jade_comprehensive.py` | Full RAG + LangGraph tests | ✅ **KEEP** |
| `test_auto_sync.py` | Auto-sync tests | ✅ **KEEP** |
| `test_jade_ai.py` | Legacy tests | ⚠️ **UPDATE** (test new engine) |

---

## Redundancy Analysis

### Problem 1: Too Many Ingestion Paths

**Current state (confusing)**:
```
Want to learn something? You have 5 choices:
1. simple_learn.py (for markdown/txt)
2. ingest_jade_knowledge.py (for JSONL)
3. ingest_scan_results.py (for scans)
4. auto_sync.py (for workspace files)
5. dynamic_learner.py (for unprocessed/)
```

**Should be (simple)**:
```
Want to learn something? You have 2 choices:
1. Drop file in unprocessed/ → Run simple_learn.py
2. Let auto_sync.py watch workspace (background daemon)
```

### Problem 2: Scan Ingestion in Wrong Place

**Current**: `HTC/ingest_scan_results.py` ingests scans
**Should be**: `GP-DATA/sync/ingest_scan_results.py` (closer to scan data)

**Why?** HTC is for **document learning**, not scan processing.

### Problem 3: Legacy Scripts Confusing Users

**jade.py** (legacy) vs **jade_rag_langgraph.py** (new)
- Users don't know which to use
- Documentation points to both
- Should deprecate `jade.py`

### Problem 4: Duplicate Auto-Learning

**auto_sync.py** (polling, no deps) vs **dynamic_learner.py** (file watcher, needs `watchdog`)
- Both watch for file changes
- `auto_sync.py` is simpler and has no dependencies
- `dynamic_learner.py` is redundant

---

## Consolidation Plan

### Phase 1: Simplify Ingestion (Primary Goal)

**Create: `GP-Backend/HTC/ingest.py` (unified ingestion)**

```python
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
"""

from pathlib import Path
import argparse
from typing import List, Dict

from core.rag_engine import rag_engine
from graph_ingest_knowledge import KnowledgeGraphBuilder


class UnifiedIngester:
    """Unified ingestion for all knowledge formats"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            "markdown_files": 0,
            "jsonl_files": 0,
            "total_documents": 0,
            "errors": 0
        }

    def ingest_markdown(self, file_path: Path):
        """Ingest markdown/txt file"""
        # Implementation from simple_learn.py
        pass

    def ingest_jsonl(self, file_path: Path):
        """Ingest JSONL file (conversations or documents)"""
        # Implementation from ingest_jade_knowledge.py
        pass

    def ingest_directory(self, directory: Path):
        """Ingest all supported files in directory"""
        for file in directory.rglob("*"):
            if file.suffix in [".md", ".txt"]:
                self.ingest_markdown(file)
            elif file.suffix == ".jsonl":
                self.ingest_jsonl(file)

    def build_knowledge_graph(self):
        """Build knowledge graph from RAG vectors"""
        print("\n🏗️  Building knowledge graph...")
        builder = KnowledgeGraphBuilder(dry_run=self.dry_run)
        builder.build_graph()


def main():
    parser = argparse.ArgumentParser(description="Unified knowledge ingestion")
    parser.add_argument("--file", type=str, help="Ingest specific file")
    parser.add_argument("--dry-run", action="store_true", help="Preview without ingesting")
    parser.add_argument("--build-graph", action="store_true", help="Build knowledge graph after ingestion")
    args = parser.parse_args()

    ingester = UnifiedIngester(dry_run=args.dry_run)

    if args.file:
        file_path = Path(args.file)
        if file_path.suffix in [".md", ".txt"]:
            ingester.ingest_markdown(file_path)
        elif file_path.suffix == ".jsonl":
            ingester.ingest_jsonl(file_path)
    else:
        unprocessed_dir = Path(__file__).parent / "unprocessed"
        ingester.ingest_directory(unprocessed_dir)

    if args.build_graph:
        ingester.build_knowledge_graph()


if __name__ == "__main__":
    main()
```

**Benefits**:
- **One script** instead of 3
- **Auto-detects** file format
- **Simpler UX**: `python ingest.py` (that's it!)

### Phase 2: Move Scan Ingestion

**Move**: `HTC/ingest_scan_results.py` → `GP-DATA/sync/ingest_scan_results.py`

**Reason**: Scan ingestion is data pipeline work, not document learning.

### Phase 3: Deprecate Legacy

**Deprecate**:
- `jade.py` → Use `jade_rag_langgraph.py` instead
- `dynamic_learner.py` → Use `auto_sync.py` instead

**Action**: Add deprecation warnings, update README

### Phase 4: Archive Utilities

**Move to `HTC/utils/`**:
- `migrate_vector_db_knowledge.py` (one-time migration)
- `reembed_processed_files.py` (rarely used)

---

## Proposed Directory Structure

### BEFORE (Current - Confusing):

```
HTC/
├── simple_learn.py               # 👈 Learn markdown
├── ingest_jade_knowledge.py      # 👈 Learn JSONL
├── graph_ingest_knowledge.py     # 👈 Build graph
├── ingest_scan_results.py        # 👈 Ingest scans (wrong place!)
├── auto_sync.py                  # 👈 Auto-watch workspace
├── dynamic_learner.py            # 👈 Auto-watch unprocessed (redundant!)
├── jade.py                       # 👈 Legacy orchestrator
├── jade_api.py                   # 👈 API interface
├── jade_rag_langgraph.py         # 👈 New engine
├── migrate_vector_db_knowledge.py  # 👈 One-time utility
├── reembed_processed_files.py    # 👈 Rarely used
└── test_*.py                     # Tests
```

**Problem**: 11 scripts, hard to know which to use

---

### AFTER (Proposed - Simple):

```
HTC/
├── ingest.py                     # ⭐ UNIFIED INGESTION (replaces 3 scripts)
├── auto_sync.py                  # ⭐ AUTO-WATCH WORKSPACE
├── jade_rag_langgraph.py         # ⭐ CORE ENGINE
├── jade_api.py                   # ⭐ API INTERFACE
├── test_*.py                     # Tests
├── utils/                        # Utilities (rarely used)
│   ├── migrate_vector_db.py      # One-time migration
│   └── reembed_files.py          # Re-embedding utility
├── deprecated/                   # Legacy (kept for reference)
│   ├── jade.py                   # Old orchestrator
│   ├── dynamic_learner.py        # Old file watcher
│   ├── simple_learn.py           # Replaced by ingest.py
│   ├── ingest_jade_knowledge.py  # Merged into ingest.py
│   └── graph_ingest_knowledge.py # Merged into ingest.py
└── unprocessed/                  # Drop zone
    ├── *.md, *.txt               # Markdown/text docs
    └── *.jsonl                   # JSONL knowledge
```

**Benefits**:
- **4 primary scripts** (vs 11)
- **Clear purpose** for each
- **Backward compatible** (deprecated/ folder for reference)

---

## User Experience Comparison

### BEFORE (Confusing):

```bash
# User wants to learn from a document
# Which script do I use???

python simple_learn.py              # For markdown?
python ingest_jade_knowledge.py     # For JSONL?
python graph_ingest_knowledge.py    # After ingestion?
python auto_sync.py &               # Or this?
```

**User is confused. 4 scripts to understand.**

---

### AFTER (Simple):

```bash
# User wants to learn from a document
# ONE SCRIPT FOR EVERYTHING

python ingest.py                    # Auto-detects format, ingests everything
python ingest.py --build-graph      # Also builds knowledge graph

# Or background daemon
python auto_sync.py &               # Auto-watches workspace
```

**User is happy. 1 script to understand.**

---

## Updated README

### Quick Start (New)

```markdown
## Quick Start 🚀

### 1. Learn from Documents

Drop your files (markdown, text, JSONL) into `unprocessed/`:

```bash
cp ~/my-docs/*.md HTC/unprocessed/
python HTC/ingest.py
```

That's it! Auto-detects format and ingests to RAG + Knowledge Graph.

### 2. Auto-Watch Workspace (Optional)

```bash
python HTC/auto_sync.py &
```

Watches `~/jade-workspace/` and auto-ingests changes.

### 3. Query Knowledge

```python
from HTC.jade_rag_langgraph import JadeRAGAgent

agent = JadeRAGAgent()
result = agent.query("What is our security policy?")
print(result['response'])
```

---

## Files Explained

| File | Purpose | When to Use |
|------|---------|-------------|
| `ingest.py` | **Unified ingestion** for all formats | Drop files in `unprocessed/` and run this |
| `auto_sync.py` | **Auto-watch** workspace for changes | Background daemon for automatic learning |
| `jade_rag_langgraph.py` | **Core engine** (RAG + Graph + LangGraph) | Query knowledge, reasoning workflows |
| `jade_api.py` | **API interface** | REST API for Jade |

**That's it. 4 files, all you need.**

---

## Migration Needed?

**No breaking changes.** Old scripts moved to `deprecated/` and still work.

But update your scripts to use:
- `ingest.py` instead of `simple_learn.py` or `ingest_jade_knowledge.py`
- `jade_rag_langgraph.py` instead of `jade.py`
```

---

## Implementation Steps

### Step 1: Create Unified Ingester

1. Create `HTC/ingest.py` merging:
   - `simple_learn.py` (markdown ingestion)
   - `ingest_jade_knowledge.py` (JSONL ingestion)
   - `graph_ingest_knowledge.py` (graph building)

2. Test with:
   ```bash
   python ingest.py --dry-run
   ```

### Step 2: Move Scan Ingestion

```bash
mv HTC/ingest_scan_results.py GP-DATA/sync/ingest_scan_results.py
```

### Step 3: Deprecate Legacy

```bash
mkdir HTC/deprecated
mv HTC/jade.py HTC/deprecated/
mv HTC/dynamic_learner.py HTC/deprecated/
mv HTC/simple_learn.py HTC/deprecated/
mv HTC/ingest_jade_knowledge.py HTC/deprecated/
mv HTC/graph_ingest_knowledge.py HTC/deprecated/
```

Add deprecation warnings to each file.

### Step 4: Archive Utilities

```bash
mkdir HTC/utils
mv HTC/migrate_vector_db_knowledge.py HTC/utils/
mv HTC/reembed_processed_files.py HTC/utils/
```

### Step 5: Update Documentation

- Update `HTC/README.md` with simplified architecture
- Update root README references
- Add migration guide

---

## Testing Plan

### Test 1: Unified Ingester

```bash
# Test markdown ingestion
echo "# Test Doc" > unprocessed/test.md
python ingest.py --dry-run
# Should detect markdown and preview ingestion

# Test JSONL ingestion
echo '{"messages":[{"role":"user","content":"test"}]}' > unprocessed/test.jsonl
python ingest.py --dry-run
# Should detect JSONL and preview ingestion

# Test full ingestion
python ingest.py
# Should ingest both files

# Test graph building
python ingest.py --build-graph
# Should build knowledge graph
```

### Test 2: Backward Compatibility

```bash
# Old scripts should still work (with deprecation warning)
python deprecated/simple_learn.py
# Should print: "⚠️ DEPRECATED: Use 'ingest.py' instead"
# But still function correctly
```

### Test 3: Auto-Sync

```bash
# Start auto-sync
python auto_sync.py &

# Make workspace change
echo "# New File" > ~/jade-workspace/test.md

# Wait 30 seconds
# Should auto-ingest
```

---

## Breaking Changes?

**None.** This is backward compatible.

Old scripts moved to `deprecated/` and still work (with warnings).

Users can migrate at their own pace.

---

## Benefits Summary

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Primary scripts** | 11 | 4 | **63% reduction** |
| **Ingestion paths** | 5 | 1 | **80% simpler** |
| **Steps to learn** | "Drop file → Which script? → Run script → Build graph?" | "Drop file → `python ingest.py`" | **4 steps → 1 step** |
| **User confusion** | High (which script?) | Low (one script) | **Clear purpose** |
| **Maintenance** | 11 files to maintain | 4 files to maintain | **63% less work** |

---

## Decision: Do This?

**Recommendation**: ✅ **YES, consolidate**

**Reason**: The current setup is confusing with 11+ scripts. Consolidating to 4 primary scripts makes HTC:
- **Simpler** for users (one ingestion script)
- **Clearer** purpose for each script
- **Easier** to maintain (fewer files)
- **Backward compatible** (no breaking changes)

**Effort**: ~2-3 hours to consolidate and test

**Impact**: Dramatically improves UX and maintainability

---

## Next Step

**Ask user**: "Should I consolidate HTC scripts into this simplified structure?"

If yes:
1. Create `ingest.py` (unified ingester)
2. Move deprecated scripts
3. Update README
4. Test everything

If no:
- Document current architecture better
- Add usage guide for each script
