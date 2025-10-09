# GP-COPILOT Cleanup & Integration Plan

## 🎯 Objective
Clean up scattered files, consolidate components, and connect **GP-AI (Brain)** to **GP-CONSULTING-AGENTS (Muscle)** for complete agentic workflow.

---

## 📊 Current State Analysis

### Root Directory Clutter (NEEDS CLEANUP)
**23 Markdown files** scattered at root:
- Documentation: `ARCHITECTURE_CLARIFICATION.md`, `SYSTEM_ARCHITECTURE_EXPLAINED.md`, etc.
- Status reports: `DEPLOYMENT_VERIFICATION_COMPLETE.md`, `CLEANUP_REPORT.md`, etc.
- Mixed concerns - need consolidation

**17 Python/Shell scripts** scattered at root:
```
demo_jade_context.py
demonstrate_gatekeeper.py
interview-demo-cli.py
jade_langgraph_demo.py
jade_quick_demo.py
jade_unified_launcher.py
quick-jade-test.py
simple-jade-test.py
test-jade-gatekeeper.py
test-knowledge-retrieval.py
test_jade_gatekeeper_template.py
test_offline_jade.py
test_secrets.py
+ more...
```
**Action:** Move to `GP-TESTING-VAL/` or archive

### Directory Structure
```
GP-copilot/
├── ai-env/              # 7.5GB Python virtual env - KEEP (add to .gitignore)
├── bin/                 # Symlinks to tools - KEEP & DOCUMENT
├── GP-AI/               # ✅ Brain (orchestration)
├── GP-CONSULTING-AGENTS/# ✅ Muscle (execution)
├── GP-DATA/             # ✅ Centralized storage
├── GP-DOCS/             # Move scattered docs HERE
├── GP-GUI/              # Frontend (verify status)
├── GP-KNOWLEDGE-HUB/    # Purpose unclear - investigate
├── GP-PLATFORM/         # Has james-config, mcp, core - IMPORTANT!
├── GP-PROJECTS/         # ✅ Client projects
├── GP-RAG/              # ✅ Knowledge base (77K docs)
├── GP-TESTING-VAL/      # Move test scripts HERE
└── GP-TOOLS/            # ✅ Binaries + download script
```

### Key Findings

#### ✅ **GP-TOOLS EXISTS** (You were right!)
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-TOOLS/`
- **Contains:**
  - `binaries/` - gitleaks (7MB), kubescape (171MB), tfsec (39MB)
  - `download-binaries.sh` - Script to download tools on new machines
  - `configs/` - Tool configurations
  - `scripts/` - Helper scripts

#### ✅ **bin/ Directory** (Symlink Hub)
All tools are symlinked here for easy PATH access:
```
bin/bandit      → ~/.pyenv/shims/bandit
bin/checkov     → ~/.local/bin/checkov
bin/gitleaks    → ../GP-TOOLS/binaries/gitleaks
bin/gp-jade     → ../GP-AI/cli/gp-jade.py
bin/kubescape   → ../GP-TOOLS/binaries/kubescape
bin/opa         → /usr/local/bin/opa
bin/semgrep     → ~/.local/bin/semgrep
bin/tfsec       → ../GP-TOOLS/binaries/tfsec
bin/trivy       → ~/bin/trivy
```

#### ✅ **GP-PLATFORM** (Shared Infrastructure)
**Purpose:** Cross-cutting infrastructure used by both Brain and Muscle
```
GP-PLATFORM/
├── james-config/        # Configuration management
├── core/                # Core utilities
├── api/                 # API infrastructure
├── mcp/                 # MCP (Model Context Protocol?)
├── workflow/            # Workflow utilities
├── model_client/        # LLM client abstraction
├── config/              # System configuration
└── scripts/             # Utility scripts
```
**Status:** Needs investigation - likely shared by GP-AI and GP-CONSULTING-AGENTS

#### ❌ **requirements.txt** (INCOMPLETE)
Current requirements.txt only has:
```txt
PyYAML>=6.0
pathlib2>=2.3.7
pytest>=7.0.0
pytest-cov>=4.0.0
```

**Missing critical deps:**
- torch, transformers (LLM)
- langchain, langgraph (orchestration)
- chromadb, sentence-transformers (RAG)
- fastapi, uvicorn (API)

#### ✅ **Qwen Models** (Already Downloaded)
- Qwen2.5-7B-Instruct (14GB)
- Qwen2.5-3B-Instruct (6GB)
- Qwen2.5-1.5B-Instruct (3GB)
- Location: `~/.cache/huggingface/hub/`

---

## 🧹 Cleanup Actions

### 1. Archive Test/Demo Scripts
**Move to `GP-TESTING-VAL/demos/`:**
```bash
mkdir -p GP-TESTING-VAL/demos
mv demo_jade_context.py GP-TESTING-VAL/demos/
mv demonstrate_gatekeeper.py GP-TESTING-VAL/demos/
mv interview-demo-cli.py GP-TESTING-VAL/demos/
mv jade_langgraph_demo.py GP-TESTING-VAL/demos/
mv jade_quick_demo.py GP-TESTING-VAL/demos/
mv jade_unified_launcher.py GP-TESTING-VAL/demos/
mv quick-jade-test.py GP-TESTING-VAL/demos/
mv simple-jade-test.py GP-TESTING-VAL/demos/
```

**Move to `GP-TESTING-VAL/tests/`:**
```bash
mkdir -p GP-TESTING-VAL/tests
mv test-jade-gatekeeper.py GP-TESTING-VAL/tests/
mv test-knowledge-retrieval.py GP-TESTING-VAL/tests/
mv test_jade_gatekeeper_template.py GP-TESTING-VAL/tests/
mv test_offline_jade.py GP-TESTING-VAL/tests/
mv test_secrets.py GP-TESTING-VAL/tests/
mv test_ui_endpoints.sh GP-TESTING-VAL/tests/
mv test-pod.yaml GP-TESTING-VAL/tests/
```

### 2. Consolidate Documentation
**Move to `GP-DOCS/`:**
```bash
mkdir -p GP-DOCS/architecture
mkdir -p GP-DOCS/deployment
mkdir -p GP-DOCS/reports

# Architecture docs
mv ARCHITECTURE_CLARIFICATION.md GP-DOCS/architecture/
mv SYSTEM_ARCHITECTURE_EXPLAINED.md GP-DOCS/architecture/
mv OPA_VS_SCANNERS_EXPLAINED.md GP-DOCS/architecture/

# Deployment docs
mv DEPLOYMENT-SUCCESS.md GP-DOCS/deployment/
mv DEPLOYMENT_VERIFICATION_COMPLETE.md GP-DOCS/deployment/
mv DEPLOYMENT_READINESS_CHECKLIST.md GP-DOCS/deployment/
mv DOCKER-SETUP-COMPLETE.md GP-DOCS/deployment/
mv README-DOCKER.md GP-DOCS/deployment/

# Status reports
mv CLEANUP_REPORT.md GP-DOCS/reports/
mv ARCHITECTURAL_CLEANUP_COMPLETE.md GP-DOCS/reports/
mv CENTRALIZED_KNOWLEDGE_COMPLETE.md GP-DOCS/reports/
mv FINAL_CENTRALIZATION_COMPLETE.md GP-DOCS/reports/
mv INTEGRATION_COMPLETE.md GP-DOCS/reports/
mv OFFLINE_SYSTEM_COMPLETE.md GP-DOCS/reports/
mv WORKFLOW_VERIFIED_COMPLETE.md GP-DOCS/reports/
mv TEST_RESULTS_SUMMARY.md GP-DOCS/reports/
mv TOOL_PATHS_FIXED.md GP-DOCS/reports/
mv ENDPOINT_VERIFICATION.md GP-DOCS/reports/
```

**Keep at root:**
- `README.md` - Main project README
- `LICENSE` - License file
- `.gitignore` - Git configuration
- `.dockerignore` - Docker configuration
- `docker-compose.yml` - Docker orchestration
- `requirements.txt` - Python dependencies (will update)
- `ARCHITECTURE_CLARIFICATION.md` - Key reference (or move to GP-DOCS and symlink)

### 3. Update .gitignore
```gitignore
# Python
ai-env/
__pycache__/
*.pyc
*.pyo
*.egg-info/

# Models (too large for git)
*.bin
*.safetensors
*.gguf
.cache/huggingface/

# Vector databases
**/vector-store/
**/jade_vector_db/
**/vector-db/
*.chroma

# Data
GP-DATA/active/*.json
GP-DATA/archive/

# IDE
.vscode/
.idea/
*.swp

# Logs
*.log
training_*.log

# Environment
.env
.env.local

# Temporary
/tmp/
*.tmp
```

### 4. Update requirements.txt (Complete Dependencies)
```txt
# Core LLM & AI
torch>=2.6.0
transformers>=4.36.0
accelerate>=0.25.0
bitsandbytes>=0.42.0

# LangChain & LangGraph
langchain>=0.3.0
langchain-community>=0.3.0
langchain-core>=0.3.0
langgraph>=0.2.0

# RAG & Embeddings
sentence-transformers>=2.2.2
chromadb>=0.4.22
faiss-cpu>=1.7.4

# API & Web
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.0.0
httpx>=0.26.0

# Security Tools Integration
python-jose[cryptography]>=3.4.0
pyyaml>=6.0.1
requests>=2.31.0
jinja2>=3.1.3

# Data Processing
numpy>=1.24.0
pandas>=2.0.0
python-dateutil>=2.8.2

# CLI & UI
rich>=13.7.0
click>=8.1.7
prompt-toolkit>=3.0.43

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.23.0

# Development
black>=24.0.0
flake8>=7.0.0
mypy>=1.8.0

# Kubernetes
kubernetes>=28.1.0
```

---

## 🔗 Integration Tasks

### Task 1: Connect GP-AI to GP-CONSULTING-AGENTS

**File:** `GP-AI/jade_enhanced.py`

**Add method:**
```python
def execute_security_workflow(self, project_path: str, workflow_type: str = "full") -> Dict[str, Any]:
    """
    Execute complete security workflow
    Brain (GP-AI) orchestrates Muscle (GP-CONSULTING-AGENTS)
    """
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent / "GP-CONSULTING-AGENTS"))

    from workflows.full_workflow import EnhancedSecurityWorkflow
    from workflows.scan_workflow import run_scan_workflow
    from workflows.fix_workflow import run_fix_workflow

    print(f"🧠 Brain: Analyzing {project_path} with RAG context...")

    # Get RAG context for project
    project_type = self._detect_project_type(project_path)
    context = self.rag_engine.query_knowledge(
        f"Security best practices for {project_type}",
        n_results=5
    )

    print(f"💪 Muscle: Executing {workflow_type} workflow...")

    if workflow_type == "full":
        workflow = EnhancedSecurityWorkflow()
        results = workflow.execute_complete_workflow(Path(project_path).name)
    elif workflow_type == "scan":
        results = run_scan_workflow(project_path)
    elif workflow_type == "fix":
        scan_results = self.scan_integrator.get_latest_scan(project_path)
        results = run_fix_workflow(scan_results, project_path)

    print("🧠 Brain: Analyzing results with security expertise...")
    analysis = self.analyze_with_context(
        f"Analyze scan results and provide recommendations:\n{json.dumps(results, indent=2)}",
        project=project_path
    )

    return {
        "project": project_path,
        "workflow_type": workflow_type,
        "rag_context": context,
        "workflow_results": results,
        "ai_analysis": analysis,
        "timestamp": datetime.now().isoformat()
    }

def _detect_project_type(self, project_path: str) -> str:
    """Detect project type for RAG context"""
    path = Path(project_path)
    if (path / "terraform").exists() or list(path.glob("*.tf")):
        return "terraform"
    elif (path / "kubernetes").exists() or list(path.glob("*.yaml")):
        return "kubernetes"
    elif (path / "Dockerfile").exists():
        return "docker"
    elif (path / "requirements.txt").exists():
        return "python"
    else:
        return "general"
```

### Task 2: Update API Endpoints

**File:** `GP-AI/api/main.py`

**Update `/api/v1/scan` endpoint (line 101):**
```python
@app.post("/api/v1/scan", response_model=ScanResponse)
async def scan_project(request: ScanRequest):
    """
    Execute full security workflow: Brain + Muscle
    """
    try:
        from jade_enhanced import JadeEnhanced

        jade = JadeEnhanced()
        results = jade.execute_security_workflow(
            request.project_path,
            workflow_type="full" if request.depth == "comprehensive" else "scan"
        )

        # Format response
        workflow_results = results["workflow_results"]
        scan_results = workflow_results.get("scan_results", {})

        findings = []
        for tool, tool_results in scan_results.items():
            for finding in tool_results.get("findings", [])[:20]:
                findings.append({
                    "severity": finding.get("severity", "unknown"),
                    "category": tool,
                    "file_path": finding.get("file", "unknown"),
                    "line_number": finding.get("line", 0),
                    "description": finding.get("title", ""),
                    "impact": finding.get("impact", ""),
                    "recommendation": finding.get("recommendation", ""),
                    "compliance": finding.get("compliance", []),
                    "confidence": finding.get("confidence", 0.8)
                })

        return ScanResponse(
            success=True,
            client=request.client,
            findings_count=len(findings),
            confidence=results.get("ai_analysis", {}).get("confidence", 0.9),
            summary=results.get("ai_analysis", {}).get("summary", "Scan complete"),
            findings=findings,
            compliance_guidance=results.get("ai_analysis", {}).get("compliance", None)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")
```

### Task 3: Create Unified CLI

**File:** `GP-AI/cli/jade-cli.py` (NEW)

```python
#!/usr/bin/env python3
"""
Jade CLI - Unified Security Workflow Interface
Brain (GP-AI) + Muscle (GP-CONSULTING-AGENTS)
"""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from jade_enhanced import JadeEnhanced

console = Console()

@click.group()
def cli():
    """🤖 Jade - AI Security Consultant CLI"""
    pass

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--workflow', type=click.Choice(['scan', 'fix', 'full']), default='full')
def analyze(project_path: str, workflow: str):
    """Analyze project with full security workflow"""
    console.print(f"\n🤖 [bold green]Jade Security Analysis[/bold green]")
    console.print(f"📁 Project: {project_path}")
    console.print(f"⚙️  Workflow: {workflow}\n")

    jade = JadeEnhanced()

    with console.status("[bold yellow]Running security analysis..."):
        results = jade.execute_security_workflow(project_path, workflow)

    # Display results
    console.print("\n✅ [bold green]Analysis Complete[/bold green]\n")

    # Findings summary
    workflow_results = results.get("workflow_results", {})
    scan_results = workflow_results.get("scan_results", {})

    table = Table(title="Security Findings")
    table.add_column("Tool", style="cyan")
    table.add_column("Findings", style="magenta")
    table.add_column("Critical", style="red")

    for tool, tool_results in scan_results.items():
        findings = tool_results.get("findings", [])
        critical = len([f for f in findings if f.get("severity") == "CRITICAL"])
        table.add_row(tool, str(len(findings)), str(critical))

    console.print(table)

    # AI Analysis
    ai_analysis = results.get("ai_analysis", {})
    if ai_analysis:
        console.print(f"\n🧠 [bold blue]AI Analysis:[/bold blue]")
        console.print(ai_analysis.get("summary", "No analysis available"))

@cli.command()
@click.argument('question')
def query(question: str):
    """Query Jade's security knowledge (RAG)"""
    console.print(f"\n🤖 [bold green]Jade Knowledge Query[/bold green]")
    console.print(f"❓ Question: {question}\n")

    jade = JadeEnhanced()

    with console.status("[bold yellow]Searching knowledge base..."):
        answer = jade.analyze_with_context(question)

    console.print(f"\n💡 [bold blue]Answer:[/bold blue]")
    console.print(answer)

@cli.command()
def stats():
    """Show Jade system statistics"""
    jade = JadeEnhanced()

    console.print("\n🤖 [bold green]Jade System Statistics[/bold green]\n")

    # RAG stats
    rag_stats = jade.rag_engine.get_stats()
    console.print(f"📚 Knowledge Base: {rag_stats.get('total_documents', 0):,} documents")
    console.print(f"🗃️  Collections: {rag_stats.get('collections', 0)}")

    # Tools status
    console.print("\n🔧 Security Tools:")
    tools = ["bandit", "trivy", "semgrep", "gitleaks", "checkov", "tfsec"]
    for tool in tools:
        console.print(f"  ✓ {tool}")

if __name__ == "__main__":
    cli()
```

**Symlink to bin:**
```bash
ln -sf /home/jimmie/linkops-industries/GP-copilot/GP-AI/cli/jade-cli.py /home/jimmie/linkops-industries/GP-copilot/bin/jade
chmod +x /home/jimmie/linkops-industries/GP-copilot/GP-AI/cli/jade-cli.py
```

### Task 4: Create Setup Scripts

**File:** `setup-models.sh` (NEW - Root level)

```bash
#!/bin/bash
set -e

echo "🤖 GP-JADE Model Setup"
echo "======================"
echo ""
echo "This will download Qwen models (~14GB for 7B, ~6GB for 3B)"
echo ""
read -p "Which model? (3b/7b) [7b]: " model_choice
model_choice=${model_choice:-7b}

if [ "$model_choice" == "7b" ]; then
    MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"
    echo "📥 Downloading Qwen2.5-7B-Instruct (~14GB)..."
elif [ "$model_choice" == "3b" ]; then
    MODEL_NAME="Qwen/Qwen2.5-3B-Instruct"
    echo "📥 Downloading Qwen2.5-3B-Instruct (~6GB)..."
else
    echo "❌ Invalid choice. Use '3b' or '7b'"
    exit 1
fi

python3 -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

print('Downloading tokenizer...')
tokenizer = AutoTokenizer.from_pretrained('$MODEL_NAME')

print('Downloading model...')
model = AutoModelForCausalLM.from_pretrained(
    '$MODEL_NAME',
    torch_dtype=torch.float16,
    device_map='cpu'
)

print('✅ Model downloaded to ~/.cache/huggingface/')
print(f'Model path: {model.config._name_or_path}')
"

echo ""
echo "✅ Setup complete!"
echo "Model cached in: ~/.cache/huggingface/hub/"
```

**File:** `setup-environment.sh` (NEW - Root level)

```bash
#!/bin/bash
set -e

echo "🤖 GP-JADE Environment Setup"
echo "============================"
echo ""

# 1. Create virtual environment
if [ ! -d "ai-env" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv ai-env
else
    echo "✅ Virtual environment already exists"
fi

# 2. Activate and install dependencies
echo "📥 Installing Python dependencies..."
source ai-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Download security tool binaries
echo ""
echo "🔧 Downloading security tools..."
cd GP-TOOLS
bash download-binaries.sh
cd ..

# 4. Verify bin symlinks
echo ""
echo "🔗 Verifying tool symlinks..."
ls -lh bin/

# 5. Test installations
echo ""
echo "✅ Testing tool installations..."
bin/gitleaks version || echo "⚠️  Gitleaks not working"
bin/trivy version || echo "⚠️  Trivy not working"
bin/semgrep --version || echo "⚠️  Semgrep not working"
bin/bandit --version || echo "⚠️  Bandit not working"

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: source ai-env/bin/activate"
echo "2. Run: bash setup-models.sh  # Download Qwen models"
echo "3. Run: bin/jade stats        # Verify Jade is working"
```

---

## 📝 Final Directory Structure (After Cleanup)

```
GP-copilot/
├── README.md                          # Main documentation
├── LICENSE                            # License
├── requirements.txt                   # Complete Python deps
├── setup-environment.sh               # Environment setup
├── setup-models.sh                    # Model download
├── docker-compose.yml                 # Docker orchestration
├── .gitignore                         # Updated gitignore
│
├── ai-env/                            # Python venv (gitignored)
├── bin/                               # Tool symlinks (keep)
│
├── GP-AI/                             # 🧠 BRAIN (Orchestration)
│   ├── jade_enhanced.py               # Main Jade interface (UPDATED)
│   ├── api/main.py                    # FastAPI server (UPDATED)
│   ├── cli/
│   │   ├── jade-cli.py                # Unified CLI (NEW)
│   │   └── gp-jade.py                 # Original CLI
│   ├── engines/                       # AI engines
│   ├── integrations/                  # Scan/tool integrations
│   ├── models/                        # Model management
│   └── knowledge/                     # Prompts & context
│
├── GP-CONSULTING-AGENTS/              # 💪 MUSCLE (Execution)
│   ├── workflows/
│   │   ├── full_workflow.py           # Complete 7-step workflow
│   │   ├── scan_workflow.py           # Scanner orchestration
│   │   └── fix_workflow.py            # Fixer orchestration
│   ├── scanners/                      # 11 security scanners
│   ├── fixers/                        # Remediation tools
│   ├── agents/                        # 15 specialist agents
│   └── GP-POL-AS-CODE/                # OPA/Gatekeeper policies
│
├── GP-PLATFORM/                       # 🔧 Shared Infrastructure
│   ├── james-config/                  # Configuration
│   ├── core/                          # Core utilities
│   ├── api/                           # API utilities
│   ├── mcp/                           # Model Context Protocol
│   └── workflow/                      # Workflow utilities
│
├── GP-RAG/                            # 📚 Knowledge Base
│   ├── core/jade_engine.py            # RAG engine
│   ├── tools/ingest.py                # Knowledge ingestion
│   └── vector-store/                  # 77K+ documents (gitignored)
│
├── GP-DATA/                           # 💾 Data Storage
│   ├── active/                        # Current scan results
│   ├── archive/                       # Historical data
│   ├── knowledge-base/                # Documentation
│   └── metadata/                      # Tracking data
│
├── GP-TOOLS/                          # 🛠️ Security Tools
│   ├── binaries/                      # Tool binaries (gitignored)
│   ├── download-binaries.sh           # Download script
│   ├── configs/                       # Tool configs
│   └── scripts/                       # Helper scripts
│
├── GP-DOCS/                           # 📖 Documentation (CLEANED)
│   ├── architecture/                  # Architecture docs
│   ├── deployment/                    # Deployment guides
│   └── reports/                       # Status reports
│
├── GP-TESTING-VAL/                    # 🧪 Tests & Demos (CLEANED)
│   ├── demos/                         # Demo scripts
│   └── tests/                         # Test scripts
│
├── GP-PROJECTS/                       # 👔 Client Projects
└── GP-GUI/                            # 🖥️ Frontend UI
```

---

## ✅ Completion Checklist

- [ ] Move test/demo scripts to GP-TESTING-VAL
- [ ] Move documentation to GP-DOCS
- [ ] Update .gitignore
- [ ] Update requirements.txt with complete dependencies
- [ ] Create setup-environment.sh
- [ ] Create setup-models.sh
- [ ] Update GP-AI/jade_enhanced.py with workflow integration
- [ ] Update GP-AI/api/main.py endpoints
- [ ] Create GP-AI/cli/jade-cli.py
- [ ] Symlink jade-cli.py to bin/jade
- [ ] Test end-to-end workflow
- [ ] Create updated README.md
- [ ] Final git commit and push

---

## 🚀 Usage After Cleanup

```bash
# First time setup on new machine
bash setup-environment.sh
bash setup-models.sh

# Daily usage
source ai-env/bin/activate
jade analyze /path/to/project --workflow full
jade query "How do I prevent privilege escalation in Kubernetes?"
jade stats
```

---

## 📊 Impact Summary

**Before:**
- 40+ files scattered at root
- Unclear relationship between components
- Incomplete dependencies
- No unified CLI
- Brain and Muscle disconnected

**After:**
- Clean root directory (5-10 essential files)
- Clear architecture: Brain (GP-AI) + Muscle (GP-CONSULTING-AGENTS)
- Complete dependencies
- Unified CLI interface
- Full agentic workflow integration
- Easy deployment to new machines