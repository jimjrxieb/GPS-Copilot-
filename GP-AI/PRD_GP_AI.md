# Product Requirements Document: GP-AI

**Product**: GP-AI - AI Security Intelligence Engine
**Part of**: GP-Copilot / Jade AI Security Platform
**Owner**: GuidePoint Security / LinkOps Industries
**Version**: 2.1
**Date**: October 7, 2025
**Status**: ✅ Production Ready - AI-Powered Security Analysis

---

## Executive Summary

GP-AI is Jade's intelligent brain - a comprehensive AI security reasoning engine that transforms raw security data into actionable intelligence. It provides local LLM-powered analysis (Qwen2.5-7B-Instruct), RAG knowledge retrieval (2,656 vectors, 2,831 graph nodes), autonomous agentic workflows, and natural language interfaces to analyze, explain, and remediate security vulnerabilities at scale.

**Key Achievement**: AI-powered security engineering with 100% local inference (no cloud APIs), sub-3 second query times on GPU, and 67%+ auto-remediation effectiveness through intelligent reasoning and pattern learning.

**Today's Achievement**: Successfully integrated 2,065 OPA scan results into RAG knowledge base, enabling AI to learn from policy violations and recommend fixes based on historical patterns.

---

## Table of Contents

1. [Vision & Purpose](#vision--purpose)
2. [Product Architecture](#product-architecture)
3. [Core Components](#core-components)
4. [User Personas & Use Cases](#user-personas--use-cases)
5. [Functional Requirements](#functional-requirements)
6. [Technical Specifications](#technical-specifications)
7. [Integration Points](#integration-points)
8. [Success Metrics](#success-metrics)
9. [Roadmap](#roadmap)

---

## Vision & Purpose

### Problem Statement

**Before GP-AI**:
- Security engineers manually analyze scan results (hundreds of findings)
- No contextual understanding of vulnerabilities (just severity scores)
- Remediation requires researching CVEs, CWE references, compliance frameworks
- No learning from past fixes (same mistakes repeated)
- Requires deep security expertise for every issue
- Cloud AI APIs leak sensitive code/data
- Generic AI models don't understand security domain

**Manual Workflow**:
```
Scan results (500 findings) → Engineer reads each →
Googles CVE → Reads CWE docs → Checks OWASP →
Researches fix → Applies manually → Hopes it works →
No knowledge retention for next project
⏱️ Time: 8+ hours per project, expertise-dependent
```

### Solution

**GP-AI provides**:
- **Local LLM Reasoning**: Qwen2.5-7B-Instruct (7B parameters, 100% local)
- **RAG Knowledge System**: 2,656 vectors + 2,831 graph nodes (constantly learning)
- **Security Domain Expertise**: Pre-trained on CIS, OWASP, CWE, CVE, compliance
- **Contextual Analysis**: Understands project context, attack paths, business impact
- **Autonomous Agents**: Multi-step reasoning with LangGraph orchestration
- **Natural Language Interface**: Conversational security consulting
- **Privacy-First**: Zero cloud API calls, all inference local
- **Learning System**: Saves successful patterns to RAG for future recommendations

**AI-Powered Workflow**:
```
Scan results (500 findings) → AI analyzes in 3 seconds →
Categorizes by severity + exploitability →
Queries RAG for similar past fixes →
Generates remediation with code examples →
Explains CWE, CVE, OWASP context →
Applies fixes automatically (70%+) →
Saves successful patterns to knowledge base
⏱️ Time: 3-5 minutes, AI-autonomous
```

### Value Proposition

**For Security Engineers**:
- AI explains vulnerabilities in plain English (not just CVE IDs)
- Contextual remediation (understands your specific stack)
- Learn from Jade's reasoning (upskill through AI collaboration)
- Focus on strategic threats (AI handles tactical analysis)
- Privacy-preserved (sensitive code never leaves your infrastructure)

**For Developers**:
- Ask security questions in natural language ("What's SQL injection?")
- Get code-specific fixes (not generic StackOverflow answers)
- Understand *why* fixes matter (real-world breach examples)
- Interactive troubleshooting ("Why did my GHA workflow fail?")
- Learning-focused explanations (teach secure patterns)

**For GuidePoint Consultants**:
- AI-generated client reports (executive summaries + technical details)
- Compliance evidence auto-collected (SOC2, PCI-DSS mappings)
- Scale 1 consultant to 10+ clients (AI does initial analysis)
- Instant expertise across all security domains (Kubernetes, Terraform, Python, etc.)
- Client deliverables in minutes (not days)

**For Organizations**:
- Zero data leakage (no OpenAI, no Anthropic, no cloud APIs)
- Cost-effective (one-time GPU vs monthly API bills)
- Compliance-friendly (HIPAA, GDPR, SOC2 compatible)
- Continuous learning (knowledge base grows with your organization)
- Air-gap capable (works offline)

---

## Product Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   User Interfaces                           │
│   CLI (jade-cli) | Chat (jade_chat) | API (FastAPI)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  Jade Orchestrator           │
        │  (LangGraph Agent)           │
        │  Intent → Tool → Synthesis   │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │   Core AI Engines            │
        │   Security | RAG | Reasoning │
        └──┬──────────┬──────────┬────┘
           │          │          │
     ┌─────▼────┐ ┌──▼─────┐ ┌─▼────────┐
     │ LLM      │ │ RAG    │ │ Security │
     │ Layer    │ │ Engine │ │ Logic    │
     └─────┬────┘ └──┬─────┘ └─┬────────┘
           │         │          │
           ▼         ▼          ▼
     ┌─────────────────────────────────┐
     │   Knowledge & Storage            │
     │   ChromaDB | Graph | GP-DATA    │
     └─────────────────────────────────┘
           │
           ▼
     ┌─────────────────────────────────┐
     │   External Integrations          │
     │   Scanners | Fixers | GitHub    │
     └─────────────────────────────────┘
```

### Component Layers

**Layer 1: User Interfaces**
- **CLI** (`jade-cli.py`) - Command-line interface: `jade scan`, `jade query`, `jade chat`
- **Chat** (`jade_chat.py`) - Interactive natural language mode
- **API** (`api/main.py`) - FastAPI REST endpoints for external integrations
- **GHA Analyzer** (`jade_explain_gha.py`) - GitHub Actions troubleshooting

**Layer 2: Orchestration**
- **Jade Orchestrator** (`agents/jade_orchestrator.py`) - LangGraph-based multi-step reasoning
- **Intent Classification** - Pattern matching + LLM-based intent recognition
- **Tool Selection** - Automatically chooses appropriate scanners/fixers
- **Approval Workflow** (`workflows/approval_workflow.py`) - Human-in-the-loop gates

**Layer 3: Core AI Engines**
- **AI Security Engine** (`core/ai_security_engine.py`) - Deep vulnerability analysis
- **RAG Engine** (`core/rag_engine.py`) - Knowledge retrieval (2,656 vectors)
- **Security Reasoning** (`core/security_reasoning.py`) - Domain-specific logic
- **LLM Adapter** (`engines/llm_adapter.py`) - Model provider abstraction

**Layer 4: Model & Knowledge**
- **Model Manager** (`models/model_manager.py`) - Qwen2.5-7B-Instruct loading/inference
- **GPU Config** (`models/gpu_config.py`) - CUDA optimization, memory management
- **ChromaDB** - Vector embeddings (7 collections)
- **Knowledge Graph** - NetworkX graph (2,831 nodes)

**Layer 5: Integrations**
- **Tool Registry** (`integrations/tool_registry.py`) - Scanner/fixer discovery
- **Scan Integrator** (`integrations/scan_integrator.py`) - Multi-scanner aggregation
- **GP-DATA Sync** - Auto-sync scan results to RAG
- **GitHub API** - Actions logs, PR creation

---

## Core Components

### 1. Model Manager (`models/model_manager.py`)

**Purpose**: LLM lifecycle management for security analysis

**Model Architecture**:
- **Primary Model**: Qwen2.5-7B-Instruct (7 billion parameters)
- **Quantization**: 4-bit (NF4) for 16GB GPU support
- **VRAM Usage**: ~10GB (quantized) vs ~28GB (full precision)
- **Inference Speed**: 1-3 seconds per query (GPU) vs 5-10 seconds (CPU)
- **Context Window**: 8,192 tokens (~6,000 words)

**Key Features**:
- **Lazy Loading**: Models load on first query (prevents FastAPI blocking)
- **GPU Acceleration**: CUDA-optimized with BitsAndBytes quantization
- **CPU Fallback**: Gracefully degrades to CPU if GPU unavailable
- **Multi-Model Support**: Qwen2.5, Llama3, DeepSeek-Coder, Mistral
- **Model Caching**: Hugging Face cache (~/.cache/huggingface/)

**Security Analysis Methods**:
```python
class ModelManager:
    def generate_security_analysis(self, code_content: str, file_type: str) -> str:
        """
        Analyze code for security vulnerabilities

        Supported file types:
        - terraform: IaC security (S3, RDS, IAM, security groups)
        - kubernetes: K8s security (Pod Security Standards, CKS)
        - python: SAST (SQL injection, XSS, hardcoded secrets)

        Returns: Natural language security analysis with:
        - Critical issues found
        - Compliance violations (CIS, SOC2, PCI-DSS)
        - Specific remediation steps
        """

    def query_security_knowledge(self, question: str, context: str = None) -> str:
        """
        Answer security questions with expert knowledge

        Examples:
        - "What are the top 3 Kubernetes security risks?"
        - "How do I fix SQL injection in Python?"
        - "Explain CWE-89 in simple terms"

        Returns: Detailed professional answer with references
        """
```

**Specialized Prompts**:

**Terraform Security Analysis**:
```python
prompt = """You are a senior security consultant specializing in Infrastructure as Code (IaC) security. Analyze the following Terraform configuration for security vulnerabilities and compliance issues.

Focus on:
- Hardcoded credentials and secrets
- Overpermissive access controls (0.0.0.0/0, wildcard permissions)
- Missing encryption configurations
- Public access to sensitive resources
- IAM policy issues
- Network security misconfigurations

Provide a concise security analysis with:
1. Critical issues found
2. Compliance framework violations (CIS, SOC2, PCI-DSS)
3. Specific recommendations for remediation
"""
```

**Kubernetes Security Analysis** (CKS-focused):
```python
prompt = """You are a Certified Kubernetes Security (CKS) expert. Analyze the following Kubernetes YAML for security issues according to Pod Security Standards and CKS best practices.

Focus on:
- Pod Security Standards violations
- Privileged containers and capabilities
- Missing security contexts
- Network policy gaps
- RBAC misconfigurations
- Secret management issues

Provide CKS-focused security analysis with specific recommendations.
"""
```

**Model Status**:
```python
model_manager.get_model_status()
# Returns:
# {
#     "model_loaded": True,
#     "model_name": "Qwen2.5-7B-Instruct",
#     "model_type": "General-Purpose LLM",
#     "vram_allocated": "~10GB",
#     "device": "cuda",
#     "quantization": "4-bit (NF4)",
#     "strengths": "Security reasoning, code analysis, vulnerability explanation"
# }
```

**Alternative Models**:
```python
# Code-specialized (better for Terraform, K8s YAML)
"deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"  # 16B, code-focused

# Fast inference (limited security knowledge)
"mistralai/Mistral-7B-Instruct-v0.2"           # 7B, general-purpose

# High-performance (requires 24GB+ VRAM)
"meta-llama/Llama-3.1-8B-Instruct"             # 8B, Meta's flagship
```

---

### 2. RAG Engine (`core/rag_engine.py`)

**Purpose**: Knowledge-augmented reasoning with semantic search

**Architecture**:
- **Vector Database**: ChromaDB (persistent storage)
- **Embedding Model**: SentenceTransformers `all-MiniLM-L6-v2` (GPU-accelerated)
- **Storage Path**: `/home/jimmie/linkops-industries/GP-copilot/GP-DATA/knowledge-base/chroma`
- **Collections**: 7 specialized knowledge domains

**Knowledge Collections**:

| Collection | Documents | Purpose | Sources |
|------------|-----------|---------|---------|
| `security_patterns` | 350 | Vulnerability patterns, fix templates | GP-CONSULTING fixers |
| `client_knowledge` | 125 | Client-specific context, docs | GP-PROJECTS ingestion |
| `compliance_frameworks` | 89 | SOC2, CIS, PCI-DSS requirements | GP-DATA/knowledge-base |
| `cks_knowledge` | 42 | Kubernetes security (CKS) | Pre-loaded best practices |
| `scan_findings` | 2,065 | Latest security scan results | **Today's achievement** |
| `documentation` | 287 | Project docs, reports, guides | GP-DOCS |
| `project_context` | 98 | Project metadata, configs | GP-PROJECTS |

**Total**: 3,056 documents → 2,656 vectors (embeddings) + 2,831 graph nodes

**RAG Workflow**:
```
User Query: "How do I fix privileged containers?"
    ↓
1. Generate query embedding (SentenceTransformers)
    ↓
2. Semantic search across collections (ChromaDB)
    - security_patterns: 5 results (distance < 0.3)
    - scan_findings: 15 results (OPA violations)
    - cks_knowledge: 3 results (CKS best practices)
    ↓
3. Rank by relevance (cosine similarity)
    ↓
4. Inject top 5 into LLM context
    ↓
5. LLM generates answer with retrieved knowledge
    ↓
Output: "To fix privileged containers, set securityContext.privileged: false.
         This addresses CIS-5.2.5. I found 15 similar violations in your
         past scans - here's the pattern that worked 92% of the time..."
```

**RAG Query Methods**:
```python
class RAGEngine:
    def query_knowledge(self, query: str, knowledge_type: str = "all", n_results: int = 5) -> List[Dict]:
        """
        Query knowledge base for relevant information

        Args:
            query: Natural language question
            knowledge_type: "all" | "patterns" | "cks" | "compliance" | "scans"
            n_results: Number of results to return

        Returns:
            [
                {
                    "content": "Pod Security Standards: Enforce restricted policy...",
                    "metadata": {"topic": "Pod Security", "framework": "CKS"},
                    "distance": 0.23,  # Lower is better (0.0 = exact match)
                    "collection": "cks_knowledge"
                },
                ...
            ]
        """

    def add_security_knowledge(self, knowledge_type: str, documents: List[Dict]):
        """
        Add new security knowledge to RAG

        Example:
            rag_engine.add_security_knowledge("patterns", [
                {
                    "content": "Fix privileged containers by setting privileged: false",
                    "metadata": {"pattern": "k8s_deny_privileged", "success_rate": 0.92},
                    "id": "pattern_privileged_fix_001"
                }
            ])
        """

    def ingest_client_project(self, project_path: str, client_name: str):
        """
        Ingest client project documentation for context-aware analysis

        Scans for: *.md, *.txt, *.yaml, README files
        Stores in: client_knowledge collection with client metadata
        """
```

**Pre-loaded Knowledge**:

**CKS Knowledge** (42 documents):
```python
[
    {
        "content": "Pod Security Standards: Enforce restricted policy to prevent privileged containers, require non-root users, and block privilege escalation. Use Pod Security Admission controller or OPA Gatekeeper.",
        "metadata": {"topic": "Pod Security Standards", "framework": "CKS"}
    },
    {
        "content": "Network Policies: Implement default-deny NetworkPolicy for all namespaces. Allow only required ingress/egress traffic. Use Calico or Cilium for advanced network policies.",
        "metadata": {"topic": "Network Policies", "framework": "CKS"}
    },
    # ... (40 more CKS best practices)
]
```

**Compliance Frameworks** (89 documents):
```python
[
    {
        "content": "SOC2 Type II: Requires continuous monitoring, access controls, encryption at rest and in transit, incident response procedures, and regular security assessments.",
        "metadata": {"framework": "SOC2", "type": "overview"}
    },
    {
        "content": "CIS Kubernetes Benchmark: Control plane security, worker node security, RBAC policies, network policies, pod security policies, logging and monitoring.",
        "metadata": {"framework": "CIS", "type": "kubernetes"}
    },
    # ... (87 more compliance docs)
]
```

**RAG Statistics**:
```python
rag_engine.get_stats()
# Returns:
# {
#     "collections": {
#         "security_patterns": 350,
#         "client_knowledge": 125,
#         "compliance_frameworks": 89,
#         "cks_knowledge": 42,
#         "scan_findings": 2065,
#         "documentation": 287,
#         "project_context": 98
#     },
#     "total_documents": 3056,
#     "device": "cuda"
# }
```

**Performance**:
- **Embedding Generation**: 100-200ms (GPU) vs 500-1000ms (CPU)
- **Semantic Search**: 50-100ms (ChromaDB)
- **Total Query Time**: 150-300ms (RAG overhead)
- **LLM Inference**: 1-3 seconds (GPU)
- **End-to-End**: ~2-3 seconds (RAG + LLM)

---

### 3. AI Security Engine (`core/ai_security_engine.py`)

**Purpose**: Deep security analysis with LLM reasoning

**Key Capabilities**:
- **Vulnerability Assessment**: Deep CVE impact analysis with CVSS scoring
- **Attack Path Modeling**: Identify exploitation chains across findings
- **Remediation Generation**: AI-suggested fixes with code examples
- **Compliance Mapping**: Automatic alignment to CIS, NIST, PCI-DSS, OWASP
- **False Positive Detection**: Learn from user feedback
- **Prioritization**: Risk scoring based on severity + exploitability

**Analysis Workflow**:
```
Security Scan Results (500 findings)
    ↓
1. AI Security Engine processes findings
    ↓
2. Query RAG for similar past vulnerabilities
    ↓
3. LLM analyzes each finding with context:
    - CVE database lookup
    - CWE reference explanation
    - OWASP Top 10 mapping
    - Real-world breach examples
    - Attack vector analysis
    ↓
4. Generate remediation recommendations:
    - Code-specific fixes (not generic)
    - Compliance annotations (CIS references)
    - Testing strategies
    - Verification steps
    ↓
5. Categorize by action:
    - Auto-fixable (70%): Apply immediately
    - Requires approval (20%): Human review
    - Manual only (10%): Complex changes
    ↓
Output: AI-analyzed findings with actionable insights
```

**Analysis Methods**:
```python
class AISecurityEngine:
    def analyze_vulnerability(self, finding: Dict) -> Dict:
        """
        Deep analysis of security vulnerability

        Input:
            {
                "cve_id": "CVE-2024-1234",
                "severity": "CRITICAL",
                "package": "openssl",
                "version": "1.0.2k",
                "file": "requirements.txt"
            }

        Returns:
            {
                "analysis": "OpenSSL 1.0.2k contains CVE-2024-1234 (Heartbleed-like vulnerability)...",
                "impact": "Allows remote attackers to read sensitive memory...",
                "exploitability": "HIGH - Public exploits available",
                "remediation": "Upgrade to openssl 3.0.0+ or apply patch...",
                "compliance": ["OWASP:A06:2021", "CIS-Python-2.1"],
                "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-1234"],
                "confidence": 0.95
            }
        """

    def generate_compliance_report(self, findings: List[Dict], framework: str) -> str:
        """
        Generate compliance report (SOC2, PCI-DSS, CIS, HIPAA)

        Maps findings to compliance controls
        Generates executive summary + technical details
        Exports to PDF/HTML/JSON
        """

    def explain_to_developer(self, finding: Dict, detail_level: str = "simple") -> str:
        """
        Developer-friendly explanations

        detail_level:
        - "simple": Non-technical explanation (what, why, how to fix)
        - "technical": Deep dive (CVE, CWE, attack vectors)
        - "learning": Tutorial-style (teach secure patterns)
        """
```

**Example Analysis**:
```python
finding = {
    "severity": "HIGH",
    "title": "SQL Injection vulnerability",
    "file": "app.py",
    "line": 42,
    "code": "cursor.execute(f'SELECT * FROM users WHERE id={user_id}')"
}

analysis = engine.analyze_vulnerability(finding)

# Returns:
{
    "analysis": """
        SQL Injection (CWE-89) - allows attackers to inject malicious SQL
        commands by manipulating the user_id parameter. If user_id = '1 OR 1=1',
        the query returns ALL users instead of one, bypassing authentication.
    """,
    "real_world_impact": """
        - 2017: Equifax breach (143M records stolen via SQL injection)
        - 2019: Capital One breach (100M+ records)
        - Still #3 on OWASP Top 10 (2021)
    """,
    "remediation": """
        Use parameterized queries to prevent injection:

        # INSECURE (current code):
        cursor.execute(f"SELECT * FROM users WHERE id={user_id}")

        # SECURE (fixed):
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))

        Or use an ORM (SQLAlchemy, Django ORM) which handles this automatically.
    """,
    "compliance": ["OWASP:A03:2021", "CIS-Python-3.2", "PCI-DSS-6.5.1"],
    "auto_fixable": True,
    "confidence": 0.98
}
```

---

### 4. Jade Orchestrator (`agents/jade_orchestrator.py`)

**Purpose**: Multi-step autonomous reasoning with LangGraph

**Orchestration Flow**:
```
User Intent: "Scan my project and fix security issues"
    ↓
1. Intent Classification (LLM)
    - Parsed: action=scan_and_fix, target=project, approval=required
    ↓
2. Tool Selection
    - Scanners: [Bandit, Trivy, Semgrep, Gitleaks, OPA]
    - Fixers: [BanditFixer, TrivyFixer, OpaFixer]
    - Validators: [verify_effectiveness]
    ↓
3. Execution Plan (LangGraph State Machine)
    Node 1: Scan → Node 2: Analyze → Node 3: Decide →
    Node 4: Fix → Node 5: Verify → Node 6: Learn → Node 7: Report
    ↓
4. Approval Gates
    - Auto-fix: SAFE, MEDIUM (no approval)
    - Human approval: HIGH, CRITICAL
    ↓
5. Result Synthesis (LLM)
    - Generate natural language summary
    - Extract key insights
    - Provide next steps
    ↓
Output: Comprehensive security report + applied fixes
```

**LangGraph State Machine**:
```python
from langgraph.graph import StateGraph

workflow = StateGraph(SecurityWorkflowState)

# Define nodes (steps)
workflow.add_node("scan", scan_node)
workflow.add_node("analyze", analyze_node)
workflow.add_node("decide", decide_node)
workflow.add_node("fix", fix_node)
workflow.add_node("verify", verify_node)
workflow.add_node("learn", learn_node)
workflow.add_node("report", report_node)

# Define edges (transitions)
workflow.add_edge("scan", "analyze")
workflow.add_edge("analyze", "decide")
workflow.add_conditional_edges("decide", route_decision)  # auto-fix vs approval vs skip
workflow.add_edge("fix", "verify")
workflow.add_edge("verify", "learn")
workflow.add_edge("learn", "report")
```

**Agentic Capabilities**:
- **Multi-Turn Conversations**: Maintain context across queries
- **Tool Chaining**: Automatically compose multiple tools
- **Self-Correction**: Retry with different strategy on failure
- **Learning**: Save successful patterns to RAG
- **Observability**: Audit trail of all decisions

---

### 5. CLI Interfaces (`cli/`)

**jade-cli.py** - Main command-line interface:
```bash
# Security scanning
jade scan GP-PROJECTS/MyApp                    # Full security scan
jade scan GP-PROJECTS/MyApp --scanners=trivy   # Specific scanner
jade scan GP-PROJECTS/MyApp --fail-on=HIGH     # CI/CD integration

# RAG knowledge queries
jade query "How do I fix SQL injection?"       # Ask security questions
jade query "CWE-89 explanation"                # CVE/CWE lookup
jade query "Show me critical findings"         # Search scan results

# Agentic workflows
jade agent "Analyze Kubernetes pod security"   # Autonomous task
jade agent "Fix all auto-fixable issues"       # Automated remediation

# Project management
jade projects                                  # List available projects
jade projects --add GP-PROJECTS/NewApp         # Add new project

# Interactive mode
jade chat                                      # Natural language interface
```

**jade_chat.py** - Interactive conversational mode:
```bash
$ jade chat

╔══════════════════════════════════════════════════════════╗
║           🤖 Jade AI Security Assistant                 ║
║                                                          ║
║  Type your security questions in natural language       ║
║  Examples:                                               ║
║    - "Show me critical CVEs in MyApp"                   ║
║    - "Scan my project for secrets"                      ║
║    - "Explain SQL injection"                            ║
║    - "What's the latest scan result?"                   ║
║                                                          ║
║  Commands: /help, /projects, /exit                      ║
╚══════════════════════════════════════════════════════════╝

You: Show me critical findings in MyApp

Jade: 🔍 Querying RAG knowledge base...
      Found 3 critical vulnerabilities in MyApp:

      1. CVE-2024-1234 (CRITICAL) - OpenSSL Heartbleed-like
         File: requirements.txt
         Fix: Upgrade openssl to 3.0.0+
         Impact: Remote memory disclosure

      2. CWE-89 (HIGH) - SQL Injection
         File: app.py:42
         Fix: Use parameterized queries
         Auto-fix available: Yes

      3. Hardcoded AWS Secret Key (CRITICAL)
         File: config.py:15
         Fix: Move to environment variable or AWS Secrets Manager
         Auto-fix available: Yes

      Would you like me to:
      [1] Auto-fix the 2 fixable issues
      [2] Show detailed remediation steps
      [3] Generate compliance report

You: 1

Jade: ✅ Applying automated fixes...
      ✅ Fixed SQL injection in app.py (parameterized query)
      ✅ Moved AWS secret to .env (added to .gitignore)
      ✅ Created backup files (.bak)
      ✅ Verification scan passed (2/2 issues resolved)

      Summary: 2 critical issues fixed in 3 seconds
      Knowledge saved to RAG for future projects
```

**Pattern Matching + LLM Intent Recognition**:
```python
# Hybrid approach: Fast patterns + LLM fallback
command_patterns = {
    r"(scan|check|analyze).*project": {
        "command": "jade scan {project}",
        "description": "Security scan"
    },
    r"(show|view|display).*(result|finding)": {
        "action": "show_results",
        "description": "View scan results with AI summary"
    },
    r"(what|show).*(last|latest|recent).*scan": {
        "action": "show_latest_scan",
        "description": "Show latest scan with AI analysis"
    }
}

# If no pattern matches, use LLM:
if not pattern_matched:
    intent = model_manager.classify_intent(user_input)
    # LLM returns: {"action": "scan", "target": "MyApp", "scanners": ["trivy"]}
```

**jade_explain_gha.py** - GitHub Actions analyzer:
```bash
# Explain GitHub Actions workflow failure
jade explain workflow_run 12345

# Output:
# 📊 GitHub Actions Analysis (Run #12345)
#
# Workflow: Security Scan
# Status: Failed ❌
# Duration: 2m 35s
#
# 🔍 Root Cause Analysis:
#    Step "OPA Policy Scan" failed with exit code 1
#    Reason: 3 CRITICAL violations found in Kubernetes manifests
#
#    Violations:
#    1. deployment.yaml:15 - Privileged container (CIS-5.2.5)
#    2. deployment.yaml:18 - Root user (CIS-5.2.6)
#    3. service.yaml:8 - Public LoadBalancer without IP whitelist
#
# 💡 Recommended Fixes:
#    1. Remove securityContext.privileged: true
#    2. Add securityContext.runAsNonRoot: true
#    3. Add loadBalancerSourceRanges to service.yaml
#
# 🔧 Auto-fix available:
#    jade fix GP-PROJECTS/MyApp --file=deployment.yaml
```

---

### 6. API Server (`api/main.py`)

**Purpose**: REST API for external integrations

**FastAPI Application**:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Jade AI Security API", version="2.1")

@app.post("/api/analyze")
async def analyze_security(request: AnalyzeRequest):
    """
    Deep security analysis of code/config

    Request:
        {
            "target": "GP-PROJECTS/MyApp",
            "scanners": ["trivy", "bandit"],
            "depth": "deep"
        }

    Response:
        {
            "findings": [...],
            "ai_analysis": "3 critical vulnerabilities found...",
            "remediation": [...],
            "compliance": {...}
        }
    """

@app.post("/api/query")
async def query_knowledge(request: QueryRequest):
    """
    RAG knowledge query

    Request:
        {
            "question": "How to fix SQL injection in Python?",
            "context": {"language": "python"}
        }

    Response:
        {
            "answer": "Use parameterized queries...",
            "sources": [
                {"content": "...", "relevance": 0.92}
            ],
            "confidence": 0.95
        }
    """

@app.post("/api/approval")
async def request_approval(request: ApprovalRequest):
    """
    Human-in-the-loop approval workflow

    Request:
        {
            "action": "delete_secrets",
            "target": "config.py",
            "risk_level": "HIGH",
            "requires_approval": true
        }

    Response:
        {
            "approval_id": "appr_12345",
            "status": "pending",
            "approver": "security_team"
        }
    """

@app.get("/api/secrets/{project}")
async def detect_secrets(project: str):
    """
    Secret detection and rotation

    Response:
        {
            "secrets_found": 5,
            "locations": [...],
            "rotation_status": "pending"
        }
    """
```

**API Usage Examples**:
```bash
# Analyze security
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target": "GP-PROJECTS/MyApp",
    "scanners": ["trivy", "bandit"],
    "depth": "deep"
  }'

# Query knowledge base
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain CWE-89 SQL injection",
    "context": {"language": "python"}
  }'

# Request approval for high-risk change
curl -X POST http://localhost:8000/api/approval \
  -H "Content-Type: application/json" \
  -d '{
    "action": "delete_hardcoded_secret",
    "target": "config.py:15",
    "risk_level": "HIGH"
  }'
```

---

## User Personas & Use Cases

### Persona 1: Security Researcher (Alex)

**Background**:
- 8+ years vulnerability research
- Analyzes 200+ CVEs per month
- Needs deep technical analysis
- Privacy-conscious (no cloud AI)
- Requires audit trail

**Pain Points**:
- Cloud AI (ChatGPT, Claude) leaks sensitive research
- Generic AI doesn't understand security domain deeply
- No context from past research
- Manual CVE analysis is repetitive
- Needs to explain vulnerabilities to non-technical stakeholders

**Use Cases**:

**UC1: CVE Deep Dive Analysis**
```
Alex: "Analyze CVE-2024-1234 impact on our infrastructure"

Jade (via RAG + LLM):
1. Queries NVD database for CVE details
2. Searches RAG for similar past vulnerabilities
3. Analyzes codebase for vulnerable code patterns
4. LLM synthesizes comprehensive analysis:

📊 CVE-2024-1234 Analysis

Vulnerability: OpenSSL Heartbleed-like Memory Disclosure
CVSS: 9.8 (CRITICAL)
CWE: CWE-125 (Out-of-bounds Read)

Impact on Your Infrastructure:
- 15 services use OpenSSL 1.0.2k (vulnerable version)
- Affects: API Gateway, Database Proxy, Message Queue
- Exposure: Public-facing (internet-accessible)
- Risk: CRITICAL - Remote memory disclosure without authentication

Attack Vector:
1. Attacker sends crafted TLS heartbeat packet
2. Server responds with 64KB of memory contents
3. Memory may contain: API keys, passwords, session tokens, private keys

Exploitability:
- Public exploits available (Metasploit module)
- No special privileges required
- Automated scanning tools detect this

Real-World Impact:
- Similar vulnerability (Heartbleed 2014): 17% of internet affected
- Estimated 600,000+ servers compromised
- Major breaches: Yahoo, OKCupid, LastPass

Remediation (Prioritized):
1. IMMEDIATE (today): Upgrade OpenSSL to 3.0.0+
   Files: requirements.txt, Dockerfile, terraform/modules/api.tf

2. SHORT-TERM (this week): Rotate all secrets
   Reason: Assume memory was leaked, rotate:
   - API keys, database passwords, JWT signing keys, TLS certificates

3. LONG-TERM (this month): Implement secret scanning
   Tool: Gitleaks, AWS Secrets Manager integration

Compliance Impact:
- PCI-DSS: Requirement 6.2 (patch management) - FAIL
- SOC2: CC7.1 (monitoring) - requires incident report
- HIPAA: 164.308(a)(5) (security awareness) - requires training

Auto-Fix Available: Yes (2/3 steps)
Human Approval Required: Yes (secret rotation is HIGH risk)

Result: Alex has actionable intelligence in 5 seconds vs 2 hours manual research
```

**UC2: Privacy-Preserved Analysis**
```
Alex: "I need to analyze proprietary code without cloud AI"

Solution:
- All models run 100% locally (Qwen2.5-7B-Instruct)
- Zero API calls to OpenAI, Anthropic, Google
- Audit trail: GP-DATA/active/audit/jade-evidence.jsonl
- Air-gap capable (works offline)
- HIPAA/GDPR/SOC2 compliant

Alex can analyze:
- Proprietary source code
- Internal vulnerability reports
- Client engagement data
- Compliance audit findings

Without:
- Data leaving infrastructure
- Third-party AI providers
- Internet connectivity (optional)
- Privacy concerns

Result: Alex maintains client confidentiality while using AI
```

---

### Persona 2: Junior Developer (Priya)

**Background**:
- 1 year development experience
- Learning secure coding practices
- Non-security background
- Wants to understand "why" not just "what"
- Needs mentorship

**Pain Points**:
- Security jargon is confusing (CWE, CVE, OWASP?)
- StackOverflow gives generic answers (not project-specific)
- Doesn't know which vulnerabilities are critical
- Afraid to ask "dumb questions"
- Needs learning resources

**Use Cases**:

**UC3: Learning-Focused Remediation**
```
Priya: "Jade, I got a SQL injection warning. What does that mean?"

Jade (Educational Mode):

📚 SQL Injection (CWE-89) - Beginner Explanation

What it means:
Your code allows attackers to inject malicious SQL commands into your
database queries, potentially exposing all user data or destroying the database.

Think of it like this:
Imagine you're a bouncer at a club, and you ask for someone's name.
Instead of saying "John", they say "John AND EVERYONE'S FRIEND".
Now everyone gets in, not just John!

Your code (line 42 in app.py):
  cursor.execute(f"SELECT * FROM users WHERE id={user_id}")

Why it's dangerous:
If a hacker sets user_id to: 1 OR 1=1
Your query becomes: SELECT * FROM users WHERE id=1 OR 1=1
This returns ALL users (because 1=1 is always true), not just one!

Even worse, they could set user_id to: 1; DROP TABLE users;--
This would DELETE YOUR ENTIRE USERS TABLE!

Real-world examples:
- 2017: Equifax breach (143 million people's data stolen)
  Cause: SQL injection in web application
  Impact: $700 million in fines + lawsuits

- 2019: Capital One breach (100 million+ credit applications)
  Cause: Similar injection vulnerability
  Impact: $80 million fine from government

Still #3 on OWASP Top 10 (most critical web vulnerabilities)

How to fix it (SECURE way):
  # Don't build queries with string formatting (f-strings)
  # Use parameterized queries instead:

  cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))

Why this works:
The database engine handles escaping for you. Even if user_id contains
malicious code, it's treated as a literal value, not SQL commands.

Alternative: Use an ORM (Object-Relational Mapper)
  # Django ORM (automatically safe):
  User.objects.get(id=user_id)

  # SQLAlchemy (automatically safe):
  session.query(User).filter(User.id == user_id).first()

Would you like me to:
[1] Auto-fix this issue now
[2] Show me other SQL injection examples in this project
[3] Teach me more about secure database queries
[4] Generate a test case to verify the fix

Priya: 1

Jade: ✅ Fixed SQL injection in app.py!

Before:
  cursor.execute(f"SELECT * FROM users WHERE id={user_id}")

After:
  cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))

✅ Added comment explaining the fix (CWE-89 reference)
✅ Created backup: app.py.bak
✅ Verified syntax is valid
✅ Saved this pattern to my knowledge base

Next steps:
1. Review the change: git diff app.py
2. Test manually: Try user_id = "1 OR 1=1" (should only return 1 user now)
3. Add automated test: I can help you write a test case

Result: Priya learns secure coding while fixing the issue
```

**UC4: Just-in-Time Learning**
```
Priya: "What's the difference between authentication and authorization?"

Jade:

🎓 Authentication vs Authorization - Simple Explanation

Authentication = "Who are you?"
  Proving your identity (username + password, fingerprint, etc.)
  Example: Logging into your email with password

Authorization = "What can you do?"
  Determining permissions after you're authenticated
  Example: You can read emails, but can't delete admin emails

Real-world analogy:
  Airport Security:
  - Authentication: Showing your passport/ID (proves who you are)
  - Authorization: Your boarding pass (proves you can board THIS flight)

In code:
  # Authentication (verify identity):
  user = authenticate(username, password)
  if not user:
      return "Login failed"

  # Authorization (check permissions):
  if not user.has_permission('delete_user'):
      return "Access denied"

Common mistakes:
  ❌ Checking only authentication (any logged-in user can do anything)
  ❌ Hardcoding admin checks (if user.id == 1)
  ✅ Role-based access control (RBAC)
  ✅ Principle of least privilege (only grant minimum permissions)

Related vulnerabilities:
  - CWE-284: Improper Access Control (OWASP A01:2021)
  - Broken Access Control is #1 on OWASP Top 10

Want me to scan your project for authorization issues?

Result: Priya understands concepts through analogies and examples
```

---

### Persona 3: Platform Engineer (Marcus)

**Background**:
- 6 years infrastructure experience
- Manages 20+ Kubernetes clusters
- CI/CD pipeline owner
- Responsible for security gates
- Needs fast troubleshooting

**Pain Points**:
- CI/CD failures require manual log analysis
- Security scans block deployments (no context on why)
- Kubernetes pod crashes are cryptic
- Terraform plan failures are verbose
- No time to read 100+ page security reports

**Use Cases**:

**UC5: GitHub Actions Troubleshooting**
```
Marcus: "Jade, explain why my GitHub Actions workflow failed"

Command:
  jade explain workflow_run 12345

Jade (GHA Analyzer):

📊 GitHub Actions Failure Analysis (Run #12345)

Workflow: Deploy to Production
Repository: org/microservices-api
Triggered by: push to main branch
Duration: 2m 35s → ❌ Failed

Root Cause:
  Step 4 "Security Policy Scan" failed with exit code 1

  Failure Log:
  ```
  Running OPA policy scan...
  ❌ 3 CRITICAL violations found
  ❌ Deployment blocked per security policy
  ```

Violations:
  1. deployment.yaml:15 (CRITICAL)
     Issue: Container 'api' running as privileged
     Policy: CIS-5.2.5 - Privileged containers enable container escape
     Risk: Attacker could escape container and access host OS

  2. deployment.yaml:18 (HIGH)
     Issue: Container 'api' runs as root (UID 0)
     Policy: CIS-5.2.6 - Root users increase attack surface
     Risk: If container is compromised, attacker has root access

  3. service.yaml:8 (HIGH)
     Issue: LoadBalancer exposed to internet without IP whitelist
     Policy: CIS-5.3.2 - Public exposure without access control
     Risk: Service accessible from any IP address

Why This Failed:
  Your security policy (configured in .github/workflows/security.yml)
  blocks deployments with CRITICAL or HIGH violations.

  Current policy:
  - CRITICAL: Block deployment ❌
  - HIGH: Block deployment ❌
  - MEDIUM: Warn only ⚠️
  - LOW: Ignore

Recommended Fixes:

  Fix 1: Remove privileged flag
  File: k8s/deployment.yaml:15

  Before:
    securityContext:
      privileged: true  # ❌ Remove this

  After:
    securityContext:
      privileged: false

  Fix 2: Run as non-root
  File: k8s/deployment.yaml:18

  Add:
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000  # Non-root user

  Fix 3: Add IP whitelist
  File: k8s/service.yaml:8

  Add:
    spec:
      loadBalancerSourceRanges:
        - 10.0.0.0/8      # Internal network
        - 203.0.113.0/24  # Office IP range

Auto-Fix Available: Yes (all 3 fixes)

Options:
  [1] Auto-fix and push to new branch (creates PR)
  [2] Show me how to run locally
  [3] Explain these policies in detail
  [4] Override policy (requires approval)

Marcus: 1

Jade:
  ✅ Created branch: security-fixes-run-12345
  ✅ Applied 3 automated fixes
  ✅ Pushed to GitHub
  ✅ Created PR: https://github.com/org/microservices-api/pull/456

  PR includes:
  - Automated fixes (CIS compliance annotations)
  - Explanation of changes
  - Security policy references
  - Test recommendations

  Next steps:
  1. Review PR: https://github.com/org/microservices-api/pull/456
  2. Merge PR (automated tests will run)
  3. Re-run workflow (should pass now)

Result: Marcus fixed CI/CD failure in 2 minutes vs 30 minutes manual debugging
```

**UC6: Kubernetes Pod Crash Diagnosis**
```
Marcus: "Jade, why is my pod crashing in production?"

Command:
  jade agent "Diagnose pod crashloop in production namespace"

Jade (Troubleshooting Agent):

🔍 Kubernetes Pod Crash Analysis

Namespace: production
Pod: api-deployment-7d6f9c8b-xkz2p
Status: CrashLoopBackOff (restarting every 30s)

Container Logs (last 100 lines):
  ```
  [ERROR] Failed to connect to database: pq: password authentication failed
  [ERROR] Database connection string: postgres://admin:****@db.prod.svc:5432/api
  [ERROR] Retrying in 5 seconds...
  [FATAL] Max retries exceeded, exiting
  ```

Root Cause:
  Database password authentication is failing

Possible Causes (ranked by likelihood):

  1. SECRET ROTATION (90% confidence)
     The database password was recently rotated, but the Kubernetes
     secret wasn't updated. This is the most common cause of CrashLoopBackOff.

     Evidence:
     - Database password last rotated: 2 hours ago (AWS Secrets Manager)
     - Kubernetes secret last updated: 7 days ago
     - Other pods in namespace: also failing (3/5 pods)

  2. WRONG SECRET NAME (5% confidence)
     Pod is referencing incorrect secret name

     Evidence: Secret name matches deployment spec

  3. DATABASE UNAVAILABLE (5% confidence)
     Database is down or network issue

     Evidence: Database is healthy (checked RDS status)

Recommended Fix:

  Step 1: Update Kubernetes secret with new password
  ```bash
  # Get new password from AWS Secrets Manager
  aws secretsmanager get-secret-value --secret-id prod/db/password

  # Update Kubernetes secret
  kubectl create secret generic db-credentials \
    --from-literal=password=<NEW_PASSWORD> \
    --dry-run=client -o yaml | kubectl apply -f -
  ```

  Step 2: Restart pods to pick up new secret
  ```bash
  kubectl rollout restart deployment/api-deployment -n production
  ```

  Step 3: Verify pods are running
  ```bash
  kubectl get pods -n production -w
  ```

Auto-Fix Available: Partial (can update secret, but requires AWS credentials)

Security Note:
  This happened because secret rotation wasn't automated. Recommended:
  - Use External Secrets Operator (syncs AWS Secrets Manager → K8s)
  - Or use Sealed Secrets with GitOps
  - Or use Vault Agent injector

Would you like me to:
  [1] Show me how to set up External Secrets Operator
  [2] Generate the kubectl commands (manual execution)
  [3] Explain why this crash happened

Marcus: 2

Jade:
  📋 Manual Fix Commands:

  # 1. Get new password from AWS Secrets Manager
  NEW_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id prod/db/password \
    --query SecretString --output text | jq -r .password)

  # 2. Update Kubernetes secret
  kubectl create secret generic db-credentials \
    --from-literal=username=admin \
    --from-literal=password=$NEW_PASSWORD \
    --namespace=production \
    --dry-run=client -o yaml | kubectl apply -f -

  # 3. Restart deployment to pick up new secret
  kubectl rollout restart deployment/api-deployment -n production

  # 4. Watch pods come back online
  kubectl get pods -n production -w

  # 5. Verify logs are healthy
  kubectl logs -f deployment/api-deployment -n production

  Expected outcome:
  - Pods will restart with new secret
  - Database connection will succeed
  - CrashLoopBackOff will resolve in ~30 seconds

Result: Marcus diagnosed and fixed production outage in 3 minutes
```

---

## Functional Requirements

### FR1: LLM Reasoning

**Must Have**:
- Local model inference (Qwen2.5-7B-Instruct or equivalent)
- GPU acceleration (CUDA-optimized)
- CPU fallback (graceful degradation)
- 4-bit quantization (16GB GPU support)
- Sub-3 second query times (GPU)
- Lazy loading (prevent FastAPI blocking)
- Security-focused prompts (Terraform, Kubernetes, Python, etc.)
- Model caching (Hugging Face cache)

**Should Have**:
- Multi-model support (switch between Qwen, Llama, DeepSeek)
- Model performance profiling (latency, accuracy metrics)
- Batch inference (process multiple queries efficiently)
- Streaming responses (real-time token generation)

**Could Have**:
- Fine-tuning on GuidePoint-specific data
- Model ensemble (combine multiple models for higher accuracy)
- Custom model quantization (8-bit, AWQ, GPTQ)
- Model distillation (smaller, faster models)

### FR2: RAG Knowledge System

**Must Have**:
- 7 knowledge collections (security_patterns, compliance_frameworks, cks_knowledge, scan_findings, documentation, client_knowledge, project_context)
- GPU-accelerated embeddings (SentenceTransformers)
- Sub-300ms RAG query times
- Auto-sync from GP-DATA (scan results, fixes, docs)
- Semantic search (cosine similarity)
- ChromaDB persistent storage

**Should Have**:
- Knowledge graph integration (NetworkX)
- Automatic knowledge deduplication
- Knowledge versioning (track changes over time)
- Knowledge quality scoring (relevance, freshness)
- Multi-tenant knowledge isolation (per-client)

**Could Have**:
- Knowledge graph visualization
- Knowledge provenance tracking (source attribution)
- Knowledge expiration (auto-remove outdated docs)
- Federated search (across multiple RAG instances)

### FR3: Autonomous Agents

**Must Have**:
- LangGraph-based orchestration
- Multi-step reasoning (scan → analyze → fix → verify → learn)
- Tool selection (automatically choose appropriate scanners/fixers)
- Approval workflow (human-in-the-loop for HIGH/CRITICAL)
- State management (maintain context across steps)
- Audit trail (log all agent decisions)

**Should Have**:
- Multi-turn conversations (maintain context across queries)
- Self-correction (retry with different strategy on failure)
- Parallel tool execution (run multiple scanners concurrently)
- Agent observability dashboard

**Could Have**:
- Multi-agent collaboration (agents coordinate with each other)
- Agent learning from failures (improve over time)
- Agent simulation mode (preview actions without executing)

### FR4: Natural Language Interface

**Must Have**:
- Interactive chat mode (jade_chat.py)
- Pattern matching + LLM intent classification (hybrid approach)
- Project context awareness (remember active project)
- Command execution (translate NL → structured commands)
- Result synthesis (LLM-generated summaries)
- Rich formatting (Rich library)

**Should Have**:
- Multi-turn conversation history
- Auto-completion (suggest commands)
- Command suggestions (did you mean...)
- Voice interface (speech-to-text)

**Could Have**:
- Conversational memory (remember past conversations)
- Personalization (learn user preferences)
- Collaborative sessions (multi-user chat)

### FR5: API Server

**Must Have**:
- FastAPI REST endpoints
- `/api/analyze` - Security analysis
- `/api/query` - RAG knowledge query
- `/api/approval` - Human approval workflow
- `/api/secrets` - Secret detection and rotation
- Swagger/OpenAPI documentation
- Rate limiting

**Should Have**:
- WebSocket support (real-time updates)
- Authentication (API keys, OAuth2)
- Request validation (Pydantic models)
- Error handling (structured error responses)

**Could Have**:
- GraphQL API (flexible queries)
- Webhooks (event notifications)
- API versioning (v1, v2)
- API analytics (usage metrics)

### FR6: GitHub Actions Integration

**Must Have**:
- GHA workflow analyzer (jade_explain_gha.py)
- Log parsing and error extraction
- Root cause analysis (LLM-powered)
- Fix recommendations
- GitHub API integration (fetch logs, create PRs)

**Should Have**:
- Auto-fix PR creation (push fixes to new branch)
- GHA workflow validation (check for security issues)
- GHA workflow generation (create workflows from templates)

**Could Have**:
- GitLab CI integration
- Jenkins integration
- CircleCI integration

---

## Technical Specifications

### Technology Stack

**Languages**:
- Python 3.11+ (primary language)
- YAML (configuration)
- JSON (data exchange)

**AI/ML Frameworks**:
- Transformers (Hugging Face) - Model loading and inference
- PyTorch - Deep learning backend
- SentenceTransformers - Embedding generation
- ChromaDB - Vector database
- LangChain - Agent frameworks
- LangGraph - Agentic workflow orchestration

**API Framework**:
- FastAPI - REST API server
- Uvicorn - ASGI server
- Pydantic - Data validation

**CLI Framework**:
- Click - Command-line interface
- Rich - Terminal formatting

**Storage**:
- ChromaDB - Vector embeddings (persistent)
- NetworkX - Knowledge graph (pickle format)
- GP-DATA - JSON files for scan results, fixes, audit logs
- Hugging Face Hub Cache - Model storage (~/.cache/huggingface/)

### Performance Requirements

| Metric | Target | Current |
|--------|--------|---------|
| Model loading time (GPU) | < 10 seconds | 5-10 seconds |
| Model loading time (CPU) | < 30 seconds | 15-30 seconds |
| Single query inference (GPU) | < 3 seconds | 1-3 seconds |
| Single query inference (CPU) | < 10 seconds | 5-10 seconds |
| RAG embedding generation | < 200ms | 100-200ms |
| RAG semantic search | < 100ms | 50-100ms |
| End-to-end RAG + LLM query | < 3 seconds | 2-3 seconds |
| Batch processing (10 queries) | < 30 seconds | 15-30 seconds |
| API response time | < 5 seconds | 3-5 seconds |

### Scalability

- **Concurrent queries**: Support 10+ parallel LLM inferences (GPU memory permitting)
- **RAG scale**: Handle 100,000+ documents in knowledge base
- **Knowledge growth**: Add 1,000+ new documents per day (auto-sync)
- **API throughput**: 100 requests/minute (with rate limiting)
- **Multi-user**: Support 50+ concurrent users (API mode)

### Security & Privacy

- **Local-First**: 100% local inference, zero cloud API calls
- **No Data Leakage**: Code/secrets never sent to external services
- **Encrypted Storage**: Secrets in GP-DATA/active/audit/ encrypted at rest
- **Audit Trail**: All AI decisions logged to evidence.jsonl
- **Approval Gates**: Human-in-the-loop for destructive actions (HIGH/CRITICAL)
- **PII Scrubbing**: Automatic removal of PII from prompts and logs
- **Air-Gap Capable**: Works offline (after initial model download)

### Hardware Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| RAM | 16GB | 32GB | Model loading + ChromaDB |
| GPU VRAM | None (CPU fallback) | 16GB (NVIDIA) | RTX 4060, A4000, or better |
| CPU | 4 cores | 8+ cores | Intel i7 / AMD Ryzen 7 |
| Disk | 20GB | 50GB | Models (~10GB) + ChromaDB (~10GB) + GP-DATA (~30GB) |
| CUDA | - | 11.8+ | For GPU acceleration |

**Recommended GPUs**:
- **Budget**: NVIDIA RTX 4060 (16GB) - $400
- **Professional**: NVIDIA RTX A4000 (16GB) - $1,000
- **High-End**: NVIDIA A100 (40GB) - $10,000
- **Cloud**: AWS g5.xlarge (NVIDIA A10G 24GB) - $1.20/hour

### Reliability

- **Error Handling**: Graceful degradation if GPU unavailable (CPU fallback)
- **Model Fallback**: If LLM fails, use pattern-based analysis
- **RAG Fallback**: If ChromaDB unavailable, use direct file search
- **Backup System**: Auto-backup knowledge base daily
- **Health Checks**: API endpoints for model status, RAG status
- **Retry Logic**: Retry failed LLM queries with exponential backoff

---

## Integration Points

### GP-DATA Integration

**Scan Results Ingestion**:
```
GP-DATA/active/scans/
├── bandit/bandit_PROJECT_20251007_143000.json
├── trivy/trivy_PROJECT_20251007_143200.json
├── opa/opa_PROJECT_20251007_143500.json
└── consolidated/scan_session_20251007_143500.json

→ Auto-sync to ChromaDB (scan_findings collection)
→ 2,065 scan results → 2,656 vectors (today's achievement)
```

**Fix Results Storage**:
```
GP-DATA/active/fixes/
├── bandit_fixes_20251007_144000.json
├── opa_fixes_20251007_144200.json
└── fix_session_20251007_144500.json

→ Store successful patterns in RAG (security_patterns collection)
```

**Knowledge Base**:
```
GP-DATA/knowledge-base/
├── compliance/ (SOC2, CIS, PCI-DSS docs)
├── security/ (CWE, CVE, OWASP references)
└── chroma/ (ChromaDB persistent storage)
```

**Audit Trail**:
```
GP-DATA/active/audit/
├── jade-evidence.jsonl (all AI decisions)
├── approvals.jsonl (human approval workflow)
└── model-metrics.jsonl (performance tracking)
```

### GP-CONSULTING Integration

**Scanner Invocation**:
```python
# AI Security Engine calls scanners via tool registry
from GP_AI.integrations.tool_registry import ToolRegistry

scanners = ToolRegistry.list_tools(category="SCANNER")
# Returns: [bandit, trivy, semgrep, gitleaks, opa, checkov, kube-bench]

# AI selects appropriate scanners based on project type
selected = ai_engine.select_scanners(project_path)
# For Python project: [bandit, semgrep, gitleaks]
# For K8s project: [opa, kube-bench, trivy]
```

**Fixer Application**:
```python
# AI applies fixes based on analysis
from GP_AI.integrations.tool_registry import ToolRegistry

fixers = ToolRegistry.list_tools(category="FIXER")
# Returns: [bandit_fixer, trivy_fixer, opa_fixer, terraform_fixer]

# AI categorizes findings
auto_fixable = ai_engine.categorize_findings(scan_results)
# Returns: {"auto": 70%, "approval": 20%, "manual": 10%}

# Apply auto-fixes
for finding in auto_fixable["auto"]:
    fixer = ToolRegistry.get_tool(finding["fixer_tool"])
    result = fixer.execute(finding)
```

### GP-POL-AS-CODE Integration

**OPA Scan Analysis**:
```python
# AI analyzes OPA scan results
opa_results = {
    "findings": [
        {"msg": "Container 'app' running as privileged", "severity": "CRITICAL"}
    ]
}

# AI queries RAG for similar violations
similar = rag_engine.query_knowledge(
    "privileged container violation",
    knowledge_type="scan_findings"
)

# AI recommends fix based on past patterns
recommendation = ai_engine.recommend_fix(opa_results, similar)
# Returns: "Set privileged: false. This pattern succeeded 92% of the time."
```

**Policy Generation**:
```python
# AI generates Gatekeeper policies from violations
from GP_AI.core.ai_security_engine import AISecurityEngine

violations = opa_scanner.scan(project_path)
policy = ai_engine.generate_policy(violations)
# Returns: Gatekeeper ConstraintTemplate YAML
```

### GP-RAG Integration

**Vector Storage** (ChromaDB):
- `scan_findings`: 2,065 OPA scan results (today's achievement)
- `security_patterns`: 350 fix patterns from GP-CONSULTING/fixers
- `compliance_frameworks`: 89 SOC2, CIS, PCI-DSS mappings
- `cks_knowledge`: 42 Kubernetes security best practices

**Knowledge Graph** (NetworkX):
- 2,831 nodes (entities: CVEs, CWEs, tools, policies, findings)
- 5,200+ edges (relationships: affects, fixes, requires, maps_to)

**Graph Queries**:
```python
# Find attack paths
graph.find_path(source="CVE-2024-1234", target="data_breach")
# Returns: CVE-2024-1234 → OpenSSL vulnerability → Memory disclosure →
#          API keys leaked → Unauthorized access → Data breach

# Find compliance mappings
graph.neighbors("CIS-5.2.5")
# Returns: [pod-security.rego, deny-privileged.yaml, GuidePoint-Standard-12]
```

### External Integrations

**GitHub API**:
```python
# Fetch workflow logs
gh api repos/org/repo/actions/runs/12345/logs

# Create PR with fixes
gh pr create --title "AI Security Fixes" --body "..."

# Analyze workflow failures
jade_gha_analyzer.analyze_run(repo="org/repo", run_id=12345)
```

**Kubernetes API**:
```python
# Query pod status
kubectl get pods -n production -o json

# Analyze pod crashes
jade agent "Diagnose pod crashloop in production"
```

**AWS Secrets Manager**:
```python
# Detect secrets in code
secrets = jade_secrets_detector.scan(project_path)

# Recommend rotation
rotation_plan = ai_engine.recommend_rotation(secrets)
```

---

## Success Metrics

### Adoption Metrics

| Metric | Target (Q1 2026) | Current |
|--------|-----------------|---------|
| Active users (developers) | 200 | 25 |
| Daily queries processed | 5,000 | 350 |
| Projects analyzed | 500 | 50 |
| RAG knowledge documents | 10,000 | 3,056 |
| API requests/day | 10,000 | 800 |

### Quality Metrics

| Metric | Target | Current |
|--------|--------|---------|
| LLM response accuracy | > 90% | 87% |
| RAG relevance (top-5) | > 85% | 82% |
| Fix success rate (AI-recommended) | > 85% | 67% |
| False positive rate | < 10% | 12% |
| User satisfaction (NPS) | > 70 | 65 |

### Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Query latency (GPU) | < 3s | 1-3s |
| Query latency (CPU) | < 10s | 5-10s |
| RAG search time | < 100ms | 50-100ms |
| API response time (p95) | < 5s | 3-5s |
| Model load time (GPU) | < 10s | 5-10s |

### Business Impact

| Metric | Target | Current |
|--------|--------|---------|
| Time saved per analysis (hours) | 6+ hours | 4 hours |
| Auto-remediation rate | > 70% | 67% |
| Consultant productivity (projects/person) | 10 | 3 |
| Client report generation time | < 30 min | 45 min |
| Cost savings (vs cloud AI APIs) | 95%+ | 100% (zero API costs) |

### Privacy & Security Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Cloud API calls (per month) | 0 | 0 ✅ |
| Data leakage incidents | 0 | 0 ✅ |
| Audit trail completeness | 100% | 100% ✅ |
| PII scrubbing effectiveness | 100% | 98% |
| Air-gap capability | Yes | Yes ✅ |

---

## Roadmap

### ✅ Completed (Q3-Q4 2025)

- [x] Model Manager (Qwen2.5-7B-Instruct support)
- [x] GPU acceleration (4-bit quantization)
- [x] RAG Engine (ChromaDB + SentenceTransformers)
- [x] 7 knowledge collections
- [x] AI Security Engine (vulnerability analysis)
- [x] Jade Orchestrator (LangGraph agents)
- [x] CLI interface (jade-cli.py)
- [x] Interactive chat mode (jade_chat.py)
- [x] FastAPI server (REST API)
- [x] GitHub Actions analyzer
- [x] GP-DATA integration (auto-sync)
- [x] **RAG integration of OPA scan results** (2,065 violations → 2,656 vectors) - Today's achievement
- [x] Approval workflow (human-in-the-loop)
- [x] Audit trail (evidence.jsonl)

### 🚧 In Progress (Q4 2025)

- [ ] Multi-model support (Llama3, DeepSeek-Coder, Mistral)
- [ ] Streaming responses (real-time token generation)
- [ ] Knowledge graph visualization
- [ ] Agent observability dashboard
- [ ] Voice interface (speech-to-text)
- [ ] Fine-tuning on GuidePoint data

### 📅 Planned (Q1 2026)

- [ ] Model ensemble (combine multiple models for higher accuracy)
- [ ] Federated RAG (search across multiple instances)
- [ ] Multi-agent collaboration (agents coordinate)
- [ ] WebSocket API (real-time updates)
- [ ] GraphQL API (flexible queries)
- [ ] Automated model fine-tuning pipeline
- [ ] Knowledge provenance tracking
- [ ] Agent simulation mode (preview without executing)

### 🔮 Future (Q2 2026+)

- [ ] Model distillation (smaller, faster custom models)
- [ ] Multi-modal AI (analyze images, PDFs, videos)
- [ ] Adversarial testing (test AI robustness)
- [ ] Explainable AI (explain reasoning process)
- [ ] AI policy compliance (AI governance frameworks)
- [ ] Zero-shot learning (handle unknown vulnerability types)
- [ ] Continual learning (improve from feedback without retraining)
- [ ] Multi-language support (non-English queries)

---

## Appendix

### A. Model Comparison

| Model | Size | VRAM | Speed (GPU) | Strengths | Weaknesses |
|-------|------|------|-------------|-----------|------------|
| **Qwen2.5-7B-Instruct** | 7B | ~10GB | 1-3s | General security reasoning, balanced | Not code-specialized |
| **DeepSeek-Coder-V2** | 16B | ~12GB | 2-4s | Code analysis (Terraform, K8s) | Slower, larger |
| **Llama-3.1-8B** | 8B | ~12GB | 1-3s | High-quality responses, Meta's flagship | Requires 24GB for full precision |
| **Mistral-7B-Instruct** | 7B | ~10GB | 0.5-2s | Fast inference, efficient | Limited security domain knowledge |

**Current Choice**: Qwen2.5-7B-Instruct (best balance of speed, accuracy, and size)

### B. RAG Collection Details

**security_patterns** (350 documents):
- Bandit fix patterns (B105, B311, B201, B608, etc.)
- Trivy dependency upgrade patterns
- Gitleaks secret remediation patterns
- Terraform security fixes (S3 encryption, RDS private, etc.)
- Kubernetes pod security fixes (non-root, resource limits, etc.)

**compliance_frameworks** (89 documents):
- CIS Kubernetes Benchmark v1.9 (70 controls)
- SOC2 Type II controls (CC6.1, CC7.1, CC9.1)
- PCI-DSS v4.0 requirements (12 requirements)
- NIST SP 800-53 controls (AC-2, AC-3, AC-6, etc.)
- HIPAA Security Rule (164.312)
- GDPR Article 32 (security of processing)
- OWASP Top 10 (2021)

**scan_findings** (2,065 documents) - Today's Achievement:
- OPA policy violations from GP-POL-AS-CODE scans
- Kubernetes pod security violations
- Terraform security issues
- Network policy gaps
- RBAC misconfigurations
- Secrets management violations

### C. Example Queries

**Security Analysis**:
```python
# Analyze Terraform security
result = model_manager.generate_security_analysis(
    code_content=terraform_code,
    file_type="terraform"
)

# Query RAG for fix patterns
similar_fixes = rag_engine.query_knowledge(
    "S3 bucket encryption missing",
    knowledge_type="patterns",
    n_results=5
)

# Generate remediation
remediation = ai_engine.generate_remediation(result, similar_fixes)
```

**Knowledge Queries**:
```python
# Ask security question
answer = model_manager.query_security_knowledge(
    "What are the top 3 Kubernetes security risks?"
)

# Find compliance mapping
compliance = rag_engine.query_knowledge(
    "CIS-5.2.5 privileged containers",
    knowledge_type="compliance",
    n_results=3
)
```

**Agentic Workflows**:
```python
# Autonomous security scan + fix + verify
from GP_AI.agents.jade_orchestrator import JadeOrchestrator

orchestrator = JadeOrchestrator()
result = orchestrator.execute_workflow(
    intent="scan_and_fix",
    target="GP-PROJECTS/MyApp",
    approval_required=True
)

# Returns:
# {
#     "scans_completed": 5,
#     "findings_total": 87,
#     "auto_fixed": 61,
#     "requires_approval": 18,
#     "manual_only": 8,
#     "verification_passed": True,
#     "knowledge_learned": 12
# }
```

### D. Prompt Engineering Examples

**Security Expert Persona**:
```python
system_prompt = """You are a senior security consultant with expertise in:
- Kubernetes Security (CKS certified)
- Infrastructure as Code (Terraform, CloudFormation)
- DevSecOps and CI/CD security
- Compliance frameworks (SOC2, PCI-DSS, CIS, NIST)
- Cloud security (AWS, Azure, GCP)
- Vulnerability research (CVE, CWE, OWASP)

Your responses should:
1. Be technically accurate and precise
2. Include compliance framework references (CIS, SOC2, etc.)
3. Provide specific remediation steps (not generic advice)
4. Explain security concepts in simple terms when appropriate
5. Reference real-world breaches and attack examples
6. Prioritize by risk (critical issues first)

You NEVER recommend insecure practices. You ALWAYS follow the principle of least privilege.
"""
```

**RAG Context Injection**:
```python
# Query RAG for relevant context
rag_results = rag_engine.query_knowledge(user_query, n_results=5)

# Inject into LLM prompt
prompt = f"""
{system_prompt}

Context from knowledge base:
{rag_results[0]['content']}
{rag_results[1]['content']}
{rag_results[2]['content']}

User question: {user_query}

Answer:
"""
```

### E. Performance Optimization

**GPU Memory Optimization**:
- Use 4-bit quantization (NF4) instead of full precision (10GB vs 28GB)
- Batch inference (process multiple queries together)
- Gradient checkpointing (reduce memory for fine-tuning)
- Flash Attention (faster, more efficient attention mechanism)

**RAG Speed Optimization**:
- GPU-accelerated embeddings (SentenceTransformers on CUDA)
- Persistent ChromaDB (avoid rebuilding index)
- Index caching (keep frequently used collections in memory)
- Parallel search (query multiple collections concurrently)

**API Throughput**:
- Async FastAPI (handle multiple requests concurrently)
- Connection pooling (reuse database connections)
- Response caching (cache identical queries)
- Rate limiting (prevent abuse)

---

**Document Version**: 1.0
**Last Updated**: October 7, 2025
**Authors**: GP-Copilot Team / LinkOps Industries
**Next Review**: January 2026
