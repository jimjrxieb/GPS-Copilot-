# CLI Files Audit - Current State

**Date**: 2025-10-07
**Purpose**: Understand all CLI entry points before consolidation

---

## Current CLI Files

### 1. jade-cli.py (851 LOC) - **PRIMARY KEEPER**
**Framework**: Click (modern, professional)
**Commands**:
- `jade analyze <project>` - Security workflow (scan/fix/full)
- `jade query <question>` - RAG knowledge query
- `jade chat` - Interactive mode (calls jade_chat.py)
- `jade agent` - Agentic workflow
- `jade learn` - Knowledge sync
- `jade projects` - List projects

**Status**: ✅ KEEP - Modern Click-based CLI with good structure
**Dependencies**: JadeEnhanced (orchestrator)

---

### 2. gp-jade.py (341 LOC) - **DELETE/MERGE**
**Framework**: argparse (old-school)
**Commands**:
- `gp-jade scan <target>` - Security scan
- Uses `ai_security_engine` directly (async)

**Status**: ❌ DELETE - Redundant with jade-cli.py
**Reason**: Older implementation, duplicates `jade analyze`

---

### 3. jade_chat.py (789 LOC) - **KEEP AS MODULE**
**Framework**: Rich Console (interactive)
**Purpose**: Interactive chat interface
**Features**:
- Pattern-based command recognition
- LLM intent classification (if ModelManager available)
- Project context management
- Natural language → structured commands

**Status**: ✅ KEEP - Called by `jade chat` subcommand
**Use**: Import as module, not standalone CLI

---

### 4. jade_analyze_gha.py (847 LOC) - **KEEP AS MODULE**
**Purpose**: GitHub Actions security analysis
**Features**:
- Fetches GHA workflow runs
- Downloads scan artifacts
- Parses multi-scanner results (KICS, Trivy, Checkov, etc.)
- Detects security gate discrepancies
- **THIS IS THE MONEY SHOT** (consolidator bug detection)

**Status**: ✅ KEEP - Core product functionality
**Use**: Import as module, expose via `jade analyze-gha` subcommand

---

### 5. jade_explain_gha.py (206 LOC) - **MERGE INTO jade_analyze_gha.py**
**Purpose**: Simplified GHA analysis
**Features**: Subset of jade_analyze_gha.py

**Status**: ⚠️ MERGE - Combine with jade_analyze_gha.py
**Reason**: Redundant functionality, simpler version of #4

---

### 6. simple_gha_explainer.py (244 LOC) - **DELETE**
**Purpose**: GHA analysis without AI
**Features**: Basic pattern matching, no LLM

**Status**: ❌ DELETE - Obsolete
**Reason**: jade_analyze_gha.py has fallback mode already

---

### 7. gha_analyzer.py (575 LOC) - **KEEP AS LIBRARY**
**Purpose**: Core GHA parsing logic
**Classes**: `GHAAnalyzer` (used by #4, #5, #6)

**Status**: ✅ KEEP - Shared library module
**Use**: Imported by jade_analyze_gha.py

---

## Symlinks in bin/

```bash
bin/jade -> GP-AI/cli/jade-cli.py          ✅ KEEP
bin/gp-jade -> GP-AI/cli/gp-jade.py        ❌ DELETE
bin/jade-stats                              ✅ KEEP (separate tool)
```

---

## Target Architecture

### Unified jade CLI

```bash
jade                    # Main entry point (jade-cli.py)
├── scan <project>      # Security scan (NEW: merge from gp-jade)
├── analyze-gha <repo> <run_id>  # GHA analysis (from jade_analyze_gha.py)
├── chat                # Interactive mode (uses jade_chat.py)
├── query <question>    # RAG query (existing)
├── projects            # List projects (existing)
├── agent <task>        # Agentic workflow (existing)
└── stats               # Statistics (separate bin/jade-stats)
```

### File Structure After Consolidation

```
GP-AI/cli/
├── jade-cli.py              # ✅ MAIN CLI (add scan, analyze-gha subcommands)
├── jade_chat.py             # ✅ KEEP (module for chat subcommand)
├── jade_analyze_gha.py      # ✅ KEEP (module for analyze-gha subcommand)
├── gha_analyzer.py          # ✅ KEEP (library for GHA parsing)
└── CLI_AUDIT.md             # This file

DELETED:
├── gp-jade.py               # ❌ DELETE (merged into jade-cli.py scan)
├── jade_explain_gha.py      # ❌ DELETE (merged into jade_analyze_gha.py)
└── simple_gha_explainer.py  # ❌ DELETE (obsolete)
```

---

## Implementation Plan

### Step 1: Add `scan` subcommand to jade-cli.py
Merge functionality from gp-jade.py:
```python
@cli.command()
@click.argument('project_path')
@click.option('--scanners', '-s', multiple=True, help='Specific scanners to run')
def scan(project_path: str, scanners: tuple):
    """Run security scan on project"""
    # Merged from gp-jade.py
```

### Step 2: Add `analyze-gha` subcommand to jade-cli.py
Import JadeGHAAnalyzer from jade_analyze_gha.py:
```python
@cli.command()
@click.argument('repo')
@click.argument('run_id')
@click.option('--output', '-o', help='Output file path')
def analyze_gha(repo: str, run_id: str, output: str):
    """Analyze GitHub Actions security scan"""
    from jade_analyze_gha import JadeGHAAnalyzer
    analyzer = JadeGHAAnalyzer()
    results = analyzer.analyze(repo, run_id)
    # ... display results
```

### Step 3: Clean up symlinks
```bash
rm bin/gp-jade
# Keep bin/jade -> GP-AI/cli/jade-cli.py
```

### Step 4: Delete redundant files
```bash
rm GP-AI/cli/gp-jade.py
rm GP-AI/cli/jade_explain_gha.py
rm GP-AI/cli/simple_gha_explainer.py
```

---

## Expected Result

**Before**: 7 CLI files, 3 symlinks, confusion
**After**: 1 main CLI, 3 support modules, clarity

**User Experience**:
```bash
# One command to rule them all
jade --help

# Clear, organized subcommands
jade scan GP-PROJECTS/MyApp
jade analyze-gha jimjrxieb/CLOUD-project 18300191954
jade chat
jade query "Show me critical findings"
```

**Clean. Simple. Professional.**

---

**Next**: Implement consolidation