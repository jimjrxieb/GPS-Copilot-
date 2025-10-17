# GP-AI Agents - Jade's Specialized Tools

**Purpose:** Specialized agents that Jade (our AI assistant) can invoke to perform security tasks

---

## 🧠 Understanding the Architecture

```
┌─────────────────────────────────────────┐
│  YOU (User)                             │
│  "Jade, fix security issues"            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  JADE (jade_orchestrator.py)            │
│  - Main AI brain (LangGraph + RAG)      │
│  - Understands your request             │
│  - Decides which agent to use           │
│  - Coordinates everything               │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌─────────┐ ┌─────────┐ ┌─────────────┐
│ Policy  │ │Troubles.│ │  (Future)   │
│ Agent   │ │ Agent   │ │   Agents    │
└─────────┘ └─────────┘ └─────────────┘
```

**Think of it like:**
- **Jade** = The brain (like you)
- **Agents** = Specialized tools (like hammers, wrenches)
- Jade decides which tool to use for each task

---

## 📁 Current Agents

### 1. **jade_orchestrator.py** (15KB, 406 lines)
**Role:** Jade's Main Brain ✨

**What it does:**
- Receives your requests ("fix security issues", "troubleshoot kubernetes")
- Uses RAG (Retrieval-Augmented Generation) to understand context
- Classifies intent: troubleshoot / scan / fix / explain
- Detects domain: kubernetes / terraform / OPA / secrets / code
- Routes to appropriate specialized agent
- Synthesizes multi-source responses

**Technology:**
- LangGraph for multi-step AI reasoning
- RAG engine for knowledge base access
- LLM for natural language understanding

**When Jade Uses It:**
- Every time you interact with Jade
- This IS Jade

**Example Flow:**
```
You: "Jade, my pod is crashlooping"
Jade Brain (jade_orchestrator):
  1. Query RAG for kubernetes knowledge
  2. Classify: intent=troubleshoot, domain=kubernetes
  3. Route to troubleshooting_agent
  4. Synthesize response with RAG context
```

**Integration:**
- `GP-DATA/simple_rag_query.py` - Knowledge base
- `GP-CONSULTING/agents/` - Specialized workers
- `GP-Backend/jade-config/` - Configuration

---

### 2. **policy_agent.py** (13KB, 345 lines)
**Role:** Security Policy Enforcement Tool 🛡️

**What it does:**
- Scans projects for security policy violations (using OPA)
- Generates automated fixes for violations
- Creates preventive policies (Gatekeeper)
- Handles approval workflow (human-in-the-loop)
- Applies fixes autonomously

**Workflow:**
```
1. Scan → Detect violations (OPA)
2. Generate → Create fixes automatically
3. Approve → Human approval (optional)
4. Fix → Apply changes to code
5. Prevent → Generate Gatekeeper policies
```

**When Jade Uses It:**
- When you ask to scan for policy violations
- When you ask to enforce security policies
- When you want automated compliance fixes

**Example:**
```
You: "Jade, scan this project for OPA violations and fix them"
Jade: [Calls policy_agent.auto_remediate(project_path)]
Policy Agent:
  - Scans with OPA
  - Finds 15 violations
  - Generates fixes
  - Applies fixes
  - Creates preventive policies
```

**Integration:**
- `GP-CONSULTING/GP-POL-AS-CODE/scanners/opa_scanner.py`
- `GP-CONSULTING/GP-POL-AS-CODE/fixers/opa_fixer.py`
- `GP-CONSULTING/GP-POL-AS-CODE/generators/opa_policy_generator.py`
- `GP-DATA/active/` - Stores scan results and fixes

---

### 3. **troubleshooting_agent.py** (18KB, 500+ lines)
**Role:** Kubernetes Troubleshooting Expert 🔍

**What it does:**
- Diagnoses Kubernetes issues (crashloops, networking, RBAC)
- Uses RAG to search troubleshooting knowledge
- Multi-step diagnosis using LangGraph
- Provides step-by-step solutions
- Can interact with live clusters (kubectl)

**Workflow:**
```
1. Understand → Parse error message
2. Query → Search RAG for similar issues
3. Diagnose → Multi-step analysis
4. Solve → Provide fix steps
```

**When Jade Uses It:**
- When you ask about Kubernetes issues
- When troubleshooting pods, services, ingress
- When diagnosing cluster problems

**Example:**
```
You: "Jade, why is my pod stuck in CrashLoopBackOff?"
Jade: [Calls troubleshooting_agent]
Troubleshooting Agent:
  - Queries RAG for CrashLoopBackOff knowledge
  - Analyzes pod logs
  - Checks image pull secrets
  - Suggests fix: "Image not found, check registry"
```

**Integration:**
- `GP-DATA/simple_rag_query.py` - Knowledge base
- LangGraph for multi-step reasoning
- `kubectl` for cluster interaction (future)

---

### 4. **crew_orchestrator.py.future** (27KB, archived)
**Status:** 🚧 **Not Currently Used** 🚧

**Purpose:** Alternative orchestration using CrewAI framework

**Why Archived:**
- Currently using jade_orchestrator (LangGraph)
- CrewAI good for future multi-client scenarios
- Saved for when supporting multiple clients simultaneously

**Future Use Case:**
- Running multiple Jade instances for different clients
- Multi-agent coordination across client boundaries
- Parallel execution of security workflows

**Recommendation:** Keep archived until multi-client support needed

---

## 🎯 How Jade Decides Which Agent to Use

### jade_orchestrator.py Decision Logic

**Step 1: Intent Classification**
```python
if "troubleshoot" in request or "why" in request:
    intent = "troubleshoot"
elif "scan" in request or "check" in request:
    intent = "scan"
elif "fix" in request or "remediate" in request:
    intent = "fix"
```

**Step 2: Domain Detection**
```python
if "kubernetes" or "pod" or "deployment":
    domain = "kubernetes"
elif "opa" or "policy":
    domain = "opa"
elif "terraform" or "infrastructure":
    domain = "terraform"
```

**Step 3: Agent Routing**
```python
if intent == "troubleshoot" and domain == "kubernetes":
    → troubleshooting_agent
elif intent == "fix" and domain == "opa":
    → policy_agent
```

---

## 🔧 Adding New Agents

When creating a new specialized agent:

### 1. **Create Agent File**
```python
# GP-AI/agents/my_new_agent.py

class MyNewAgent:
    """
    Specialized tool for [specific task]

    This agent handles:
    - [Capability 1]
    - [Capability 2]
    """

    def execute(self, task_input):
        # Agent logic here
        pass
```

### 2. **Register with Jade**
Update `jade_orchestrator.py`:
```python
from my_new_agent import MyNewAgent

# In route_to_agent():
if domain == "my_domain":
    agent = MyNewAgent()
    return agent.execute(task)
```

### 3. **Update This README**
Document the new agent's purpose and usage

### 4. **Test Integration**
```python
# Test that Jade can call your agent
result = jade_orchestrator.process("Use my new agent")
```

---

## 📚 Integration with Rest of System

### Agents Use These Systems

**GP-DATA (Data Storage):**
- `GP-DATA/active/scans/` - Scan results
- `GP-DATA/active/fixes/` - Fix reports
- `GP-DATA/active/workflows/` - Workflow logs
- `GP-DATA/knowledge-base/` - RAG knowledge

**GP-CONSULTING (Security Tools):**
- `GP-CONSULTING/agents/` - Lower-level workers
- `GP-CONSULTING/scanners/` - Security scanners
- `GP-CONSULTING/fixers/` - Automated fixers

**GP-Backend (Configuration):**
- `GP-Backend/jade-config/` - Shared config
- `GP-Backend/HTC/` - RAG engine

**GP-AI Core:**
- `GP-AI/core/rag_engine.py` - RAG queries
- `GP-AI/core/secrets_manager.py` - Secrets
- `GP-AI/config/` - Configuration

---

## 🎨 Agent Design Principles

### 1. **Single Responsibility**
Each agent does ONE thing well
- policy_agent → Policy enforcement
- troubleshooting_agent → Kubernetes diagnostics
- Don't mix concerns

### 2. **Stateless**
Agents don't store state between calls
- All state in GP-DATA
- Agents are tools, not databases

### 3. **Jade-Aware**
Agents are designed to be called by Jade
- Clear input/output interfaces
- Return structured results
- Handle errors gracefully

### 4. **Human-in-the-Loop**
Support approval workflows when needed
- policy_agent has approval_required flag
- Don't auto-apply destructive changes
- Always provide rollback

---

## 🔍 Debugging Agents

### Check if Agent is Being Called
```bash
# Add logging to jade_orchestrator
print(f"Routing to agent: {agent_name}")
```

### Test Agent Directly
```bash
# Run agent standalone
python GP-AI/agents/policy_agent.py scan /path/to/project

# Run agent with Jade
python GP-AI/agents/jade_orchestrator.py --query "scan for OPA violations"
```

### Check Agent Dependencies
```python
# In agent file, add health check
def health_check():
    return {
        "opa_scanner": OpaScanner().check_tool(),
        "gp_data": Path("GP-DATA").exists()
    }
```

---

## 📊 Agent Metrics (Future)

Track agent usage for optimization:
- Which agents are called most?
- Which agents have highest success rate?
- Which agents need improvement?

**Planned:**
```python
# Log to GP-DATA/active/audit/agent-metrics.json
{
  "agent": "policy_agent",
  "calls": 127,
  "success_rate": 0.94,
  "avg_duration_sec": 3.2
}
```

---

## 🚀 Future Agents (Planned)

**Agents we may add:**

1. **scanner_agent.py**
   - Run Trivy, Bandit, Semgrep
   - Aggregate results
   - Prioritize findings

2. **fixer_agent.py**
   - Apply security patches
   - Update dependencies
   - Create backup snapshots

3. **compliance_agent.py**
   - Check SOC2 compliance
   - Generate audit reports
   - Map controls to evidence

4. **threat_intel_agent.py**
   - Fetch CVE information
   - Check if project affected
   - Suggest mitigations

---

## 📖 Key Takeaways

**Remember:**
- **Jade** = The brain (jade_orchestrator.py)
- **Agents** = Specialized tools Jade uses
- **You** ask Jade, Jade uses agents
- Agents are stateless, focused tools
- Add agents for new specialized capabilities

**Architecture Pattern:**
```
User → Jade (brain) → Agent (tool) → Result
```

**Not This:**
```
User → Agent (wrong - agents aren't meant for direct use)
```

---

**Last Updated:** 2025-10-16
**Status:** 3 active agents, 1 archived for future
**Owner:** Jade AI System
