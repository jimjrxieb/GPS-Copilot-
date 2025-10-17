# GP-DATA Path Fixed

**Date:** 2025-10-16
**Issue:** GP-DATA directory was being created in wrong location (`GP-Frontend/GP-DATA` instead of `/home/jimmie/linkops-industries/GP-copilot/GP-DATA`)

## Root Causes Identified

Found **3 files** with incorrect relative paths that created GP-DATA in wrong location:

### 1. `GP-Frontend/GP-AI/config/platform_config.py:136`
**Before:**
```python
def get_data_directory(self) -> Path:
    """Get data storage directory"""
    return Path(os.getenv("JADE_DATA_DIR", "GP-DATA"))
```

**Problem:** Used relative path `"GP-DATA"` which resolved from current working directory

**After:**
```python
def get_data_directory(self) -> Path:
    """Get data storage directory"""
    # Use absolute path to ensure GP-DATA is always at GP-copilot root
    gp_copilot_root = Path(__file__).parent.parent.parent.parent  # GP-Frontend/GP-AI/config -> GP-copilot
    default_path = gp_copilot_root / "GP-DATA"
    return Path(os.getenv("JADE_DATA_DIR", str(default_path)))
```

### 2. `GP-Frontend/GP-AI/core/rag_graph_engine.py:69`
**Before:**
```python
# Default: GP-DATA/knowledge-base/security_graph.pkl
self.graph_path = Path(__file__).parent.parent.parent / "GP-DATA" / "knowledge-base" / "security_graph.pkl"
```

**Problem:** Only went up 3 levels (to `GP-Frontend/`) instead of 4 (to `GP-copilot/`)

**After:**
```python
# Default: GP-DATA/knowledge-base/security_graph.pkl at GP-copilot root
gp_copilot_root = Path(__file__).parent.parent.parent.parent  # GP-Frontend/GP-AI/core -> GP-copilot
self.graph_path = gp_copilot_root / "GP-DATA" / "knowledge-base" / "security_graph.pkl"
```

### 3. sys.path additions in 3 files
**Files affected:**
- `GP-Frontend/GP-AI/agents/troubleshooting_agent.py:30`
- `GP-Frontend/GP-AI/engines/llm_adapter.py:245`
- `GP-Frontend/GP-AI/cli/jade-cli.py:522`

**Before:**
```python
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-DATA"))
```

**After:**
```python
gp_copilot_root = Path(__file__).parent.parent.parent.parent  # GP-Frontend/GP-AI/{dir} -> GP-copilot
sys.path.insert(0, str(gp_copilot_root / "GP-DATA"))
```

## Verification Tests

### Test 1: platform_config.py path resolution
```python
Config file location: /home/jimmie/linkops-industries/GP-copilot/GP-Frontend/GP-AI/config/platform_config.py
GP-copilot root: /home/jimmie/linkops-industries/GP-copilot
GP-DATA path: /home/jimmie/linkops-industries/GP-copilot/GP-DATA
Is absolute: True ✅
Match: True ✅
```

### Test 2: rag_graph_engine.py path resolution
```python
RAG engine file: /home/jimmie/linkops-industries/GP-copilot/GP-Frontend/GP-AI/core/rag_graph_engine.py
GP-copilot root: /home/jimmie/linkops-industries/GP-copilot
Graph path: /home/jimmie/linkops-industries/GP-copilot/GP-DATA/knowledge-base/security_graph.pkl
Is absolute: True ✅
Match: True ✅
```

## Actions Taken

1. ✅ Fixed `platform_config.py` - now returns absolute path to GP-DATA
2. ✅ Fixed `rag_graph_engine.py` - now saves graph to correct location
3. ✅ Fixed sys.path additions in 3 files - now add correct GP-DATA to path
4. ✅ Removed incorrect `GP-Frontend/GP-DATA/` directory
5. ✅ Verified path resolution logic with tests

## Architecture Explanation

### Directory Structure
```
/home/jimmie/linkops-industries/GP-copilot/  ← Root
├── GP-Frontend/
│   └── GP-AI/
│       ├── config/
│       │   └── platform_config.py (4 levels deep)
│       ├── core/
│       │   └── rag_graph_engine.py (4 levels deep)
│       ├── agents/
│       │   └── troubleshooting_agent.py (4 levels deep)
│       ├── engines/
│       │   └── llm_adapter.py (4 levels deep)
│       └── cli/
│           └── jade-cli.py (4 levels deep)
└── GP-DATA/  ← CORRECT location (at root)
    ├── knowledge-base/
    │   ├── security_graph.pkl
    │   └── chroma/
    ├── active/
    │   ├── scans/
    │   ├── fixes/
    │   └── reports/
    └── simple_rag_query.py
```

### Path Resolution Pattern
All files in `GP-Frontend/GP-AI/{subdir}/` are **4 levels deep** from GP-copilot root:

```python
# CORRECT pattern (used everywhere now)
gp_copilot_root = Path(__file__).parent.parent.parent.parent
#                                .parent = {subdir}
#                                       .parent = GP-AI
#                                              .parent = GP-Frontend
#                                                     .parent = GP-copilot ✅
```

### Why It Was Wrong Before

**Incorrect pattern** (only went up 3 levels):
```python
# WRONG - only goes to GP-Frontend/
Path(__file__).parent.parent.parent / "GP-DATA"
#              .parent = {subdir}
#                     .parent = GP-AI
#                            .parent = GP-Frontend ❌
#                                    / "GP-DATA" = GP-Frontend/GP-DATA ❌
```

## Impact

### Before Fix:
- ❌ GP-DATA created in `GP-Frontend/GP-DATA/`
- ❌ Knowledge graph saved to wrong location
- ❌ RAG data split across two locations
- ❌ Confusion about where data lives

### After Fix:
- ✅ GP-DATA always at `/home/jimmie/linkops-industries/GP-copilot/GP-DATA`
- ✅ Knowledge graph in correct location
- ✅ All data centralized in one place
- ✅ Consistent across all modules

## Testing Recommendations

To verify this fix works in practice:

1. **Delete wrong directory** (already done):
   ```bash
   rm -rf /home/jimmie/linkops-industries/GP-copilot/GP-Frontend/GP-DATA
   ```

2. **Test RAG engine**:
   ```bash
   cd /home/jimmie/linkops-industries/GP-copilot
   python3 -c "from GP_Frontend.GP_AI.core.rag_graph_engine import SecurityKnowledgeGraph; g = SecurityKnowledgeGraph()"
   # Should create graph at: GP-DATA/knowledge-base/security_graph.pkl
   ```

3. **Test platform config**:
   ```bash
   python3 -c "from GP_Frontend.GP_AI.config.platform_config import get_config; print(get_config().get_data_directory())"
   # Should print: /home/jimmie/linkops-industries/GP-copilot/GP-DATA
   ```

4. **Verify no new GP-Frontend/GP-DATA created**:
   ```bash
   ls GP-Frontend/GP-DATA 2>/dev/null && echo "❌ STILL BROKEN" || echo "✅ FIXED"
   ```

## Summary

Fixed **5 files** total:
1. `GP-Frontend/GP-AI/config/platform_config.py` - data directory path
2. `GP-Frontend/GP-AI/core/rag_graph_engine.py` - graph file path
3. `GP-Frontend/GP-AI/agents/troubleshooting_agent.py` - sys.path addition
4. `GP-Frontend/GP-AI/engines/llm_adapter.py` - sys.path addition
5. `GP-Frontend/GP-AI/cli/jade-cli.py` - sys.path addition

**Result:** GP-DATA will now **always** be created at GP-copilot root, never in GP-Frontend.
