# Jade Chat Fixes Needed

**Issue:** During interview demo, Jade didn't know command paths and couldn't perform basic operations.

## What Needs to Work Perfectly

### 1. **Scan LinkOps-MLOps Project**
```
User: "scan GP-PROJECTS/LinkOps-MLOps"
Jade: *runs full security scan* (bandit, trivy, semgrep, gitleaks)
```

**Required command:**
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH ./gp-security scan GP-PROJECTS/LinkOps-MLOps
```

### 2. **Read and Summarize Scan Results**
```
User: "show me the scan results"
Jade: *reads GP-DATA/active/scans/*.json and summarizes*

Summary:
- Bandit: 12 issues (3 HIGH, 5 MEDIUM, 4 LOW)
- Trivy: 8 vulnerabilities
- Semgrep: 5 findings
- Gitleaks: 2 secrets found
```

**What this needs:**
1. Read all `*_latest.json` from `GP-DATA/active/scans/`
2. Parse JSON
3. Summarize with AI or simple aggregation
4. Display in readable format

### 3. **Run Fixers**
```
User: "run fixers for those issues"
Jade: *runs appropriate fixers based on scan results*

Running:
- bandit_fixer.py for Python issues
- gitleaks_fixer.py for secrets
Summary: 10/12 issues fixed automatically
```

**What this needs:**
1. Detect which scanners found issues
2. Run corresponding fixers:
   - `python GP-CONSULTING-AGENTS/fixers/bandit_fixer.py <scan_results> GP-PROJECTS/LinkOps-MLOps`
   - `python GP-CONSULTING-AGENTS/fixers/gitleaks_fixer.py <scan_results> GP-PROJECTS/LinkOps-MLOps`

### 4. **Knowledge Questions (Learning)**
```
User: "what is OPA?"
Jade: *searches GP-DATA knowledge base* "OPA (Open Policy Agent) is..."

User: "what are kubernetes security best practices?"
Jade: *searches knowledge base and provides answer*
```

**What this needs:**
1. Query GP-DATA ChromaDB collections
2. Retrieve relevant chunks
3. Synthesize answer with LLM

### 5. **Show Available Projects**
```
User: "list projects"
Jade:
GP-PROJECTS/DVWA/
GP-PROJECTS/LinkOps-MLOps/
GP-PROJECTS/Terraform_CICD_Setup/
```

**Command:** `ls -d GP-PROJECTS/*/`

---

## Critical Paths Jade MUST Know

### Scan Commands:
```bash
# Full scan
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH ./gp-security scan <project>

# Individual scanners
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python GP-CONSULTING-AGENTS/scanners/bandit_scanner.py <project>
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python GP-CONSULTING-AGENTS/scanners/trivy_scanner.py <project>
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python GP-CONSULTING-AGENTS/scanners/gitleaks_scanner.py <project>
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python GP-CONSULTING-AGENTS/scanners/semgrep_scanner.py <project>
```

### Fixer Commands:
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python GP-CONSULTING-AGENTS/fixers/bandit_fixer.py <results_json> <project>
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python GP-CONSULTING-AGENTS/fixers/gitleaks_fixer.py <results_json> <project>
```

### OPA Commands:
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py <project> terraform-security
```

### Result Locations:
```
GP-DATA/active/scans/bandit_latest.json
GP-DATA/active/scans/trivy_latest.json
GP-DATA/active/scans/semgrep_latest.json
GP-DATA/active/scans/gitleaks_latest.json
```

---

## Implementation Plan

### Phase 1: Add Missing Handler Methods (REQUIRED)

Add these methods to `jade_chat.py`:

```python
def handle_show_results(self):
    """Show recent scan results with summary"""
    scans_dir = self.gp_copilot_root / "GP-DATA/active/scans"

    # Find all *_latest.json files
    scan_files = list(scans_dir.glob("*_latest.json"))

    if not scan_files:
        console.print("[yellow]No scan results found.[/yellow]")
        console.print("[yellow]Run 'scan my project' first.[/yellow]")
        return

    console.print("\n[bold cyan]📊 Recent Scan Results:[/bold cyan]\n")

    total_issues = 0
    for scan_file in sorted(scan_files):
        try:
            with open(scan_file) as f:
                data = json.load(f)

            scanner = scan_file.stem.replace("_latest", "")
            summary = data.get("summary", {})
            total = summary.get("total", 0)
            total_issues += total

            console.print(f"[green]{scanner.upper()}:[/green] {total} issues")

            # Show by severity if available
            by_severity = summary.get("by_severity", {})
            if by_severity:
                for sev, count in by_severity.items():
                    if count > 0:
                        color = "red" if sev == "HIGH" or sev == "CRITICAL" else "yellow"
                        console.print(f"  [{color}]{sev}:[/{color}] {count}")

        except Exception as e:
            console.print(f"[dim]Error reading {scan_file.name}: {e}[/dim]")

    console.print(f"\n[bold]Total Issues: {total_issues}[/bold]\n")


def handle_show_latest_scan(self):
    """Show latest scan with detailed breakdown"""
    self.handle_show_results()  # Reuse for now


def handle_analyze_scan_results(self, user_input: str):
    """Read and analyze scan results with AI"""
    self.handle_show_results()

    if self.has_llm:
        console.print("\n[bold cyan]🤖 AI Analysis:[/bold cyan]")
        console.print("[dim]Analyzing findings...[/dim]\n")

        # TODO: Use LLM to provide insights
        console.print("[yellow]AI analysis coming soon - requires LLM integration[/yellow]")


def handle_run_fixer(self, user_input: str):
    """Run appropriate fixer based on scan results"""
    project = self.current_project or self.prompt_for_project()

    console.print(f"\n[bold cyan]🔧 Running Fixers for {project}...[/bold cyan]\n")

    scans_dir = self.gp_copilot_root / "GP-DATA/active/scans"

    # Map scanners to fixers
    fixer_map = {
        "bandit": "GP-CONSULTING-AGENTS/fixers/bandit_fixer.py",
        "gitleaks": "GP-CONSULTING-AGENTS/fixers/gitleaks_fixer.py",
        "trivy": "GP-CONSULTING-AGENTS/fixers/trivy_fixer.py",
        "semgrep": "GP-CONSULTING-AGENTS/fixers/semgrep_fixer.py",
    }

    for scanner, fixer_path in fixer_map.items():
        scan_file = scans_dir / f"{scanner}_latest.json"

        if scan_file.exists():
            console.print(f"[green]Running {scanner} fixer...[/green]")

            cmd = f"PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python {fixer_path} {scan_file} {project}"

            self.execute_command(cmd, f"Fixing {scanner} issues")
        else:
            console.print(f"[dim]No {scanner} results found, skipping[/dim]")
```

### Phase 2: Test with LinkOps-MLOps

```bash
# Start jade chat
python GP-AI/cli/jade_chat.py

# Test conversation
You: set project GP-PROJECTS/LinkOps-MLOps
You: scan my project
You: show results
You: run fixers
```

### Phase 3: Add Knowledge Base Query

```python
def handle_knowledge_query(self, question: str):
    """Query knowledge base for answers"""
    try:
        from GP_DATA.simple_rag_query import SimpleRAGQuery

        rag = SimpleRAGQuery()
        results = rag.query_all_collections(question, n_results=5)

        console.print(f"\n[bold cyan]🧠 Knowledge Base Results:[/bold cyan]\n")

        for i, result in enumerate(results, 1):
            content = result.get('content', '')
            console.print(f"[green]{i}.[/green] {content[:200]}...\n")

        # Use LLM to synthesize answer
        if self.has_llm and results:
            combined = "\n\n".join([r.get('content', '') for r in results])

            prompt = f"""Based on this information, answer the question: {question}

Information:
{combined[:2000]}

Answer:"""

            answer = self.model_manager.generate(prompt, max_tokens=300)
            console.print(f"\n[bold blue]🤖 Jade's Answer:[/bold blue]\n{answer}\n")

    except Exception as e:
        console.print(f"[red]Error querying knowledge base: {e}[/red]")
```

---

## Testing Checklist

- [ ] List projects works
- [ ] Scan GP-PROJECTS/LinkOps-MLOps works
- [ ] Show scan results works and displays summary
- [ ] Run fixers works
- [ ] Knowledge queries work (what is OPA?)
- [ ] Can handle kubernetes questions
- [ ] Can handle cloud security questions
- [ ] Paths are always correct (no "command not found")

---

## Quick Fix Summary

**The embarrassment was caused by:**
1. Jade not knowing where commands are
2. Can't read/summarize scan results
3. Can't run fixers automatically
4. No knowledge base queries

**Fix with:**
1. All commands use full paths with PYTHONPATH
2. Add `handle_show_results()` to read JSON files
3. Add `handle_run_fixer()` to run fixers
4. Add `handle_knowledge_query()` for Q&A

**Test script:**
```bash
cd /home/jimmie/linkops-industries/GP-copilot
python GP-AI/cli/jade_chat.py
```

Then in chat:
```
list projects
set project GP-PROJECTS/LinkOps-MLOps
scan my project
show results
what is OPA?
quit
```

All of these MUST work perfectly.