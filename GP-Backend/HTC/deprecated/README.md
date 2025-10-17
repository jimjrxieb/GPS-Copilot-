# Deprecated Scripts

⚠️ **These scripts have been replaced by `ingest.py`**

---

## Migration Guide

### Old → New

| Old Script | New Command | Notes |
|------------|-------------|-------|
| `simple_learn.py` | `python ../ingest.py` | Auto-detects markdown/txt files |
| `ingest_jade_knowledge.py` | `python ../ingest.py` | Auto-detects JSONL files |
| `graph_ingest_knowledge.py` | `python ../ingest.py --build-graph` | Builds knowledge graph |
| `jade.py` | Use `jade_rag_langgraph.py` instead | Legacy orchestrator |
| `dynamic_learner.py` | Use `auto_sync.py` instead | File watcher (no watchdog needed) |

---

## Why Deprecated?

These scripts were **consolidated** into a single unified ingester:
- **Simpler UX**: One command instead of 3-5
- **Auto-detection**: Automatically detects file format (.md, .txt, .jsonl)
- **Unified interface**: Consistent flags and output
- **Easier maintenance**: Single codebase to maintain

---

## Still Work?

✅ **Yes, these scripts still function** (backward compatible).

They've been moved here for reference but can still be run:

```bash
# Old way (still works)
python deprecated/simple_learn.py

# New way (recommended)
python ingest.py
```

---

## Should I Use These?

❌ **No.** Use `../ingest.py` instead.

These are kept for:
- **Reference** - If you need to see old implementation
- **Backward compatibility** - If you have scripts that call them
- **Debugging** - If something breaks in the new ingester

---

## When Will They Be Removed?

**Not soon.** They'll remain here indefinitely for backward compatibility.

---

Last updated: 2025-10-16
