# Complete Jade Map - Where Everything Lives

## The Question You're Asking

> "Is `ai_security_engine.py` where all the actions, commands, knowledge, and LangGraph live?"

**Short Answer**: No! Each component lives in its own specialized place. Let me show you exactly where everything is.

---

## 🗺️ The Complete Map

### **Entry Points** (How users interact)

#### 1. `jade chat` → `GP-AI/cli/jade_chat.py`
**What it contains**:
```python
Lines 50-180:  Pattern matching rules
Lines 235-260: Input processing
Lines 284-327: Optional LLM intent recognition
Lines 329-359: Command execution
```

**What happens**:
```
User: "scan my project"
  ↓
Matches pattern: r"(scan|check).*project"
  ↓
Executes: PYTHONPATH=... ./gp-security scan {project}
  ↓
Displays results
```

**Contains**:
- ✅ Pattern matching (natural language → commands)
- ✅ Command execution (subprocess calls)
- ✅ User interaction loop
- ❌ NOT the AI reasoning
- ❌ NOT the actual scanning
- ❌ NOT LangGraph (that's elsewhere)

---

#### 2. `jade scan/query/agent` → `GP-AI/cli/jade-cli.py`
**What it contains**:
```python
Lines 89-161:  query() command - RAG queries
Lines 213-367: remediate() command - Auto-fix
Lines 369-484: audit() command - OPA policy checks
Lines 556-635: agent() command - Calls LangGraph orchestrator
Lines 637-658: chat() command - Launches jade_chat.py
```

**What happens**:
```bash
$ jade agent "k8s pod crashloop"
  ↓
Calls agents/jade_orchestrator.py (LangGraph)
  ↓
Multi-step reasoning
  ↓
Returns solution
```

**Contains**:
- ✅ CLI command routing (Click framework)
- ✅ Calls to other components
- ✅ Output formatting
- ❌ NOT the AI logic itself

---

### **AI Intelligence** (The Brain)

#### 3. `GP-AI/core/ai_security_engine.py` ← **YOU ARE HERE**
**What it contains**:
```python
Lines 1-50:   Imports, setup, dataclasses
Lines 45-100: AISecurityEngine class init
Lines 102-200: analyze_project() - Main analysis
Lines 202-300: query_security_expert() - RAG queries
Lines 302-400: Security assessment logic
Lines 402-500: Compliance mapping
```

**What happens**:
```python
# Called by CLI or API
engine = AISecurityEngine()
result = engine.analyze_project("/path/to/project", "ClientName")

# Internally does:
1. Get scan results from GP-DATA
2. Query RAG for context
3. Apply security reasoning
4. Call LLM for analysis
5. Generate remediation
6. Return enriched findings
```

**Contains**:
- ✅ Security analysis orchestration
- ✅ RAG context integration
- ✅ Vulnerability assessment
- ✅ Compliance mapping
- ✅ Remediation generation
- ❌ NOT the LLM itself (calls models/)
- ❌ NOT the RAG database (calls rag_engine)
- ❌ NOT LangGraph (that's in agents/)

**This is the ORCHESTRATOR** - it coordinates all the pieces!

---

#### 4. `GP-AI/core/rag_engine.py`
**What it contains**:
```python
RAG (Retrieval-Augmented Generation) Engine
- Vector database (ChromaDB)
- Semantic search
- Knowledge ingestion
- Context retrieval
```

**What happens**:
```python
# When you ask a question
rag_engine.query_knowledge("How to fix SQL injection?")
  ↓
Searches ChromaDB vector database
  ↓
Returns top 5 relevant documents
  ↓
Passes to LLM as context
```

**Contains**:
- ✅ Vector database interface
- ✅ Semantic search
- ✅ Document embedding
- ✅ Knowledge ingestion
- ❌ NOT the actual knowledge (stored in GP-DATA)

---

#### 5. `GP-AI/core/security_reasoning.py`
**What it contains**:
```python
Security-specific logic (non-AI)
- CVE severity calculation
- CVSS score parsing
- Risk assessment algorithms
- Compliance framework mapping
```

**What happens**:
```python
# Fast, deterministic logic
reasoning = SecurityReasoningEngine()
severity = reasoning.calculate_cvss_score(cve_data)
risk = reasoning.assess_risk(finding)
```

**Contains**:
- ✅ Security algorithms
- ✅ Risk scoring
- ✅ Compliance rules
- ❌ NOT AI/LLM (pure logic)

---

### **LLM & Models** (The Language Brain)

#### 6. `GP-AI/models/model_manager.py`
**What it contains**:
```python
LLM lifecycle management
- Model loading (Qwen2.5-7B)
- GPU/CPU detection
- Inference API
- Token generation
```

**What happens**:
```python
# When AI needs to generate text
from models.model_manager import ModelManager

manager = ModelManager()
response = manager.generate(
    prompt="Explain this vulnerability: ...",
    max_tokens=500
)
```

**Contains**:
- ✅ Hugging Face model loading
- ✅ GPU configuration
- ✅ Text generation
- ✅ Model caching
- ❌ NOT the security logic (that's in core/)

---

### **Agents & Workflows** (Autonomous Intelligence)

#### 7. `GP-AI/agents/jade_orchestrator.py` ← **LANGGRAPH LIVES HERE!**
**What it contains**:
```python
LangGraph-based multi-step reasoning
- Intent classification
- Domain detection (k8s, terraform, opa)
- Tool selection
- Multi-turn conversations
- Agentic workflows
```

**What happens**:
```bash
$ jade agent "kubernetes pod crashloop"
  ↓
jade-cli.py calls jade_orchestrator.py
  ↓
Orchestrator uses LangGraph:
  1. Classify intent → "troubleshoot"
  2. Detect domain → "kubernetes"
  3. Load troubleshooting_agent
  4. Execute kubectl commands
  5. Query RAG for k8s knowledge
  6. Synthesize solution
  ↓
Returns multi-step diagnosis
```

**Contains**:
- ✅ **LANGGRAPH** - Multi-step reasoning
- ✅ State machine workflows
- ✅ Agent orchestration
- ✅ Multi-turn conversations
- ❌ NOT called by jade chat (too heavy)

---

#### 8. `GP-AI/agents/troubleshooting_agent.py`
**What it contains**:
```python
Domain-specific troubleshooting
- Kubernetes debugging
- Terraform validation
- OPA policy resolution
- Error log analysis
```

**Contains**:
- ✅ Specialized agents
- ✅ Domain knowledge
- ✅ Tool execution

---

### **Configuration & Knowledge**

#### 9. `GP-AI/config/jade_prompts.py`
**What it contains**:
```python
System prompts for LLM
- Security expert persona
- Analysis templates
- Output formatting instructions
```

**Contains**:
- ✅ LLM system prompts
- ✅ Reasoning templates
- ❌ NOT the knowledge base (that's in GP-DATA)

---

#### 10. `GP-AI/config/routing_config.json`
**What it contains**:
```json
{
  "intents": {
    "scan": {"agent": "security_scanner"},
    "debug": {"agent": "troubleshooting"}
  }
}
```

**Contains**:
- ✅ Intent routing rules
- ✅ Agent mappings

---

### **Data Storage** (Not in GP-AI!)

#### 11. `GP-DATA/` ← **KNOWLEDGE & RESULTS LIVE HERE**
```
GP-DATA/
├── active/scans/          # Latest scan results
├── knowledge-base/        # Documentation
├── chromadb/              # Vector database
└── metadata/              # Scan metadata
```

**Contains**:
- ✅ All scan results
- ✅ All documentation
- ✅ Vector embeddings
- ✅ Historical data

**NOT in GP-AI** - GP-AI just reads from here!

---

## 🔄 Complete Flow Example

### Example: "I want to scan my project"

```
┌─────────────────────────────────────────────────────────────────┐
│ YOU: "I want to scan my project"                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│ GP-AI/cli/jade_chat.py                                           │
│ - Pattern matches: r"(scan|check).*project"                     │
│ - Prompts for project name                                      │
│ - Builds command: ./gp-security scan GP-PROJECTS/MyApp          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│ gp-security (shell script)                                       │
│ - Calls GP-CONSULTING-AGENTS/scanners/                          │
│   - bandit_scanner.py                                            │
│   - trivy_scanner.py                                             │
│   - semgrep_scanner.py                                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│ Scanners write results to:                                      │
│ GP-DATA/active/scans/bandit_latest.json                         │
│ GP-DATA/active/scans/trivy_latest.json                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│ GP-DATA/auto_sync_daemon.py (background)                        │
│ - Detects new files                                             │
│ - Ingests into ChromaDB                                         │
│ - Creates vector embeddings                                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│ jade chat (if you ask "what did we find?")                      │
│ - Calls GP-AI/core/rag_engine.py                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│ GP-AI/core/rag_engine.py                                         │
│ - Queries ChromaDB: "show latest scan results"                  │
│ - Retrieves top 5 relevant documents                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│ GP-AI/core/ai_security_engine.py                                 │
│ - Takes RAG context                                              │
│ - Takes scan results                                             │
│ - Calls security_reasoning.py for analysis                      │
│ - Calls models/model_manager.py for LLM generation              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│ GP-AI/models/model_manager.py                                    │
│ - Loads Qwen2.5-7B                                               │
│ - Injects prompt from config/jade_prompts.py                    │
│ - Generates response                                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│ Response flows back through:                                     │
│ ai_security_engine → rag_engine → jade_chat → YOU               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📦 What Lives Where - Quick Reference

| Component | File | Purpose |
|-----------|------|---------|
| **Natural language input** | `cli/jade_chat.py` | Pattern matching, command mapping |
| **Direct commands** | `cli/jade-cli.py` | CLI routing, subcommands |
| **AI orchestration** | `core/ai_security_engine.py` | Coordinates all AI components |
| **RAG/Knowledge** | `core/rag_engine.py` | Vector search, context retrieval |
| **Security logic** | `core/security_reasoning.py` | Risk scoring, CVSS, compliance |
| **LLM inference** | `models/model_manager.py` | Qwen2.5-7B, text generation |
| **LangGraph agents** | `agents/jade_orchestrator.py` | Multi-step reasoning, agentic workflows |
| **Specialized agents** | `agents/troubleshooting_agent.py` | K8s, Terraform, OPA debugging |
| **System prompts** | `config/jade_prompts.py` | LLM instructions |
| **Intent routing** | `config/routing_config.json` | Command → agent mapping |
| **Scan results** | `GP-DATA/active/scans/` | Scanner outputs |
| **Knowledge base** | `GP-DATA/knowledge-base/` | Documentation, guides |
| **Vector DB** | `GP-DATA/chromadb/` | Embeddings for RAG |

---

## 🎯 To Answer Your Specific Questions

### Q: "Is this where jade chat actions go?"
**A**: No! `ai_security_engine.py` is the **orchestrator**.
- **Actions** (pattern matching) → `cli/jade_chat.py`
- **Execution** (running commands) → `cli/jade_chat.py` + `gp-security` script
- **Analysis** (AI reasoning) → `core/ai_security_engine.py` ← YOU ARE HERE

### Q: "Is this where commands go?"
**A**: No! Commands are defined in:
- `cli/jade-cli.py` - Direct commands (`jade scan`, `jade query`)
- `cli/jade_chat.py` - Natural language mapping

### Q: "Is this where knowledge goes?"
**A**: No! Knowledge is stored in:
- `GP-DATA/knowledge-base/` - Documentation files
- `GP-DATA/chromadb/` - Vector embeddings
- `core/rag_engine.py` - Accesses the knowledge

### Q: "Is this where LangGraph goes?"
**A**: No! LangGraph is in:
- `agents/jade_orchestrator.py` - Multi-step reasoning
- Only used by `jade agent` command, not regular chat

---

## 💡 Think of It Like a Restaurant

| Component | Restaurant Analogy |
|-----------|-------------------|
| `jade_chat.py` | **Waiter** - Takes your order, translates to kitchen |
| `jade-cli.py` | **Menu** - Shows available dishes (commands) |
| `ai_security_engine.py` | **Head Chef** - Coordinates the kitchen |
| `rag_engine.py` | **Recipe Book** - Stores knowledge |
| `model_manager.py` | **Sous Chef** - Does the actual cooking (LLM) |
| `jade_orchestrator.py` | **Kitchen Manager** - Complex multi-course meals |
| `security_reasoning.py` | **Nutrition Calculator** - Deterministic logic |
| `GP-DATA/` | **Pantry** - Where ingredients (data) are stored |

---

## 🚀 For Learning & Interviews

### When explaining to interviewers:

**Bad** ❌:
> "Everything is in ai_security_engine.py"

**Good** ✅:
> "We have clear separation of concerns:
> - **CLI layer** handles user interaction
> - **Core engines** orchestrate AI reasoning
> - **RAG engine** retrieves relevant knowledge
> - **Model manager** handles LLM inference
> - **Agents** handle complex multi-step workflows
> - **GP-DATA** stores all results and knowledge
>
> This makes each component independently testable and scalable."

---

## 📚 Next Steps for Learning

1. **Read in this order**:
   - `cli/jade_chat.py` - See how natural language is handled
   - `core/rag_engine.py` - Understand knowledge retrieval
   - `core/ai_security_engine.py` - See how it all comes together
   - `agents/jade_orchestrator.py` - Learn LangGraph workflows
   - `models/model_manager.py` - Understand LLM loading

2. **Trace a complete flow**:
   - Set a breakpoint in `jade_chat.py`
   - Type "scan my project"
   - Follow the execution path

3. **Experiment**:
   - Add a new pattern to `jade_chat.py`
   - Add a new prompt to `config/jade_prompts.py`
   - Try different LLMs in `models/model_manager.py`

---

**Status**: Now you understand the complete architecture! 🎉