# 🧠 James-OS Unified Brain Architecture

## Executive Summary
Consolidating ms-001 (GenAI) and ms-006 (Agentic) into a single unified brain service that combines reasoning with execution.

## Current Problems
1. **Duplicate APIs**: `/api/routes/`, `ms-001`, `ms-006` all have chat endpoints
2. **Split Brain**: GenAI and Agentic separated when they should work together
3. **Complex Communication**: Too many hops between services
4. **Redundant Code**: Multiple implementations of similar functionality

## Proposed Solution: Unified Brain

### Architecture
```
ms-brain-unified/
├── genai/           # Reasoning Layer (from ms-001)
│   ├── llm/         # LLM management (GPT-4, Ollama)
│   ├── rag/         # RAG engine (378K vectors)
│   ├── crewai/      # Multi-agent orchestration
│   ├── langgraph/   # Workflow orchestration
│   └── tensorflow/  # ML processing
├── agentic/         # Execution Layer (from ms-006)
│   ├── tools/       # MCP tools (Terraform, Azure, Git)
│   ├── evidence/    # SHA256 evidence generation
│   ├── autonomy/    # L0-L4 enforcement
│   └── approval/    # Approval workflows
├── contracts/       # Shared interfaces
│   ├── types.py     # Common types (AutonomyLevel, Evidence)
│   └── schemas.py   # Pydantic models
└── api/            # Unified API
    └── main.py     # Single entry point

Support Services (remain separate):
- ms-004-rag: Vector storage (called by brain)
- ms-005-mlops: Testing/evaluation
- ms-007-voice: Voice interface
- ms-008-desktop-ui: Admin dashboard
- ms-009-desktop-agent: System tray agent
```

### Data Flow
```
User Request
    ↓
Unified Brain API (:8000)
    ↓
GenAI Layer (Reasoning)
    ├── LLM: Understands intent
    ├── RAG: Retrieves context
    ├── CrewAI: Multi-agent planning
    └── LangGraph: Workflow orchestration
    ↓
Agentic Layer (Execution)
    ├── Autonomy Check (L0-L4)
    ├── Tool Execution
    ├── Evidence Generation
    └── Approval Gates (L2+)
    ↓
Response to User
```

## Implementation Steps

### Phase 1: Create Unified Structure
```bash
# 1. Create new unified brain
mkdir -p ms-brain-unified/{genai,agentic,contracts,api}

# 2. Copy GenAI components
cp -r ms-001-chatbox/engine/* ms-brain-unified/genai/
cp -r ms-001-chatbox/memory ms-brain-unified/genai/
cp -r ms-001-chatbox/voice ms-brain-unified/genai/

# 3. Copy Agentic components  
cp -r ms-006-executor/tools ms-brain-unified/agentic/
cp -r ms-006-executor/mcp ms-brain-unified/agentic/
```

### Phase 2: Update Imports
```python
# Before (in ms-001 files):
from engine.llm_manager import LLMManager

# After (in unified brain):
from genai.llm_manager import LLMManager

# Before (in ms-006 files):
from tools.tool_runner import ToolRunner

# After (in unified brain):
from agentic.tools.tool_runner import ToolRunner
```

### Phase 3: Create Unified API
```python
# ms-brain-unified/api/main.py
from fastapi import FastAPI
from genai import ConversationHandler
from agentic import ToolRunner

class UnifiedBrain:
    def __init__(self):
        self.genai = ConversationHandler()
        self.agentic = ToolRunner()
    
    async def process(self, message: str, autonomy: str):
        # GenAI understands and plans
        plan = await self.genai.understand(message)
        
        # Agentic executes if needed
        if plan.needs_tools:
            result = await self.agentic.execute(plan, autonomy)
            response = await self.genai.format(result)
        else:
            response = plan.response
        
        return response
```

### Phase 4: Remove Duplicates
```bash
# Remove old/duplicate code
rm -rf api/routes/chat.py api/routes/agent.py
rm -rf pipeline/ pipeline_backup_*/
rm -rf ms-004-rag_backup_*/

# Archive (don't delete) current services
mv ms-001-chatbox archive/ms-001-chatbox-legacy
mv ms-006-executor archive/ms-006-executor-legacy
```

### Phase 5: Update Service Connections
```python
# Update ms-007-voice/main.py
BRAIN_URL = "http://localhost:8000"  # Was :8001 and :8006

# Update ms-008-desktop-ui/src/services/
API_BASE = "http://localhost:8000"  # Unified endpoint
```

## Benefits

1. **Single Brain**: One service handles both reasoning and execution
2. **Cleaner Architecture**: No artificial separation between thinking and doing
3. **Better Performance**: Fewer network hops, shared memory
4. **Easier Maintenance**: One codebase for the brain
5. **Clear Contracts**: Shared types between components

## Migration Checklist

- [ ] Stop current services (ms-001, ms-006)
- [ ] Create ms-brain-unified structure
- [ ] Copy GenAI components from ms-001
- [ ] Copy Agentic components from ms-006
- [ ] Update all imports
- [ ] Create unified API
- [ ] Test unified brain
- [ ] Update other services to use :8000
- [ ] Remove/archive old code
- [ ] Update CLAUDE.md documentation

## Service Ports After Migration

| Service | Old Ports | New Port | Description |
|---------|-----------|----------|-------------|
| Unified Brain | 8001, 8006 | **8000** | GenAI + Agentic |
| RAG | 8004 | 8004 | No change |
| MLOps | 8005 | 8005 | No change |
| Voice | 8007 | 8007 | No change |
| Desktop UI | 1420 | 1420 | No change |

## Testing
```bash
# Test unified brain
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "x-autonomy-level: L1" \
  -d '{"message": "Run a security scan"}'

# Should handle both reasoning and execution in one service
```

## Rollback Plan
If issues arise, the original services are archived and can be restored:
```bash
mv archive/ms-001-chatbox-legacy ms-001-chatbox
mv archive/ms-006-executor-legacy ms-006-executor
```

---
Ready to proceed with consolidation? This will create a cleaner, more maintainable architecture.