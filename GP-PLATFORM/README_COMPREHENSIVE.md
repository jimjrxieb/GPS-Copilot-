# GP-PLATFORM - Shared Platform Services & Configuration

## Overview

GP-PLATFORM contains **shared platform components** used across the entire GP-JADE ecosystem. It provides centralized configuration, API gateways, orchestration, and integration services that tie all platform modules together.

**⚠️ CRITICAL**: `james-config/` is used by almost every component. Changes here affect the entire platform.

**Status**: ✅ Production Ready - CRITICAL SHARED COMPONENT
**Size**: ~1.5MB
**Last Updated**: 2025-10-07

---

## Directory Structure

```
GP-PLATFORM/ (~1.5MB)
├── james-config/                   # 🔒 CRITICAL SHARED CONFIGURATION
│   ├── __init__.py
│   ├── gp_data_config.py           # GP-DATA paths and settings
│   └── agent_metadata.py           # Agent configuration metadata
│   📌 Used by: GP-AI, GP-CONSULTING, GP-DATA, gp-security, ALL scanners
│
├── core/                           # 🧠 Platform Core Services
│   ├── james_orchestrator.py       # Main platform orchestrator
│   ├── james_command_router.py     # Command routing and dispatching
│   ├── secrets_manager.py          # Centralized secrets management
│   ├── config.py                   # Platform configuration loader
│   ├── jade_logger.py              # Centralized logging system
│   ├── james.py                    # James AI integration
│   ├── james_ui_integration.py     # UI integration layer
│   ├── main.py                     # Platform entry point
│   ├── main_working.py             # Working configuration snapshot
│   └── SECRETS_README.md           # Secrets management guide
│
├── api/                            # 🌐 API Gateway & Integration
│   ├── agent_gateway.py            # Multi-agent API routing
│   ├── unified/                    # Unified API endpoints
│   │   ├── routes/                 # API route definitions
│   │   └── automation_api.py       # Automation API endpoints
│   ├── mcp/                        # Model Context Protocol integration
│   │   ├── chat_routes.py          # MCP chat endpoints
│   │   ├── metrics_routes.py       # MCP metrics endpoints
│   │   └── queue_routes.py         # MCP queue management
│   └── README.md                   # API documentation
│
├── mcp/                            # 🔌 Model Context Protocol (MCP)
│   ├── server.py                   # MCP server implementation
│   ├── agents/                     # MCP-enabled agents
│   │   ├── client_intelligence_agent.py      # Client analysis
│   │   ├── consulting_remediation_agent.py   # Security remediation
│   │   └── implementation_planning_agent.py  # Implementation planning
│   ├── server/                     # MCP server components
│   ├── tools/                      # MCP tool definitions
│   ├── config/                     # MCP configuration
│   │   └── mcp_config.yaml         # MCP settings
│   └── README.md                   # MCP documentation
│
├── model_client/                   # 🤖 LLM Client Abstraction
│   ├── james_mlops_client.py       # MLOps model client
│   ├── clients/                    # Different LLM client implementations
│   ├── intelligence/               # AI intelligence layer
│   ├── config/                     # Model client configuration
│   │   └── model_client_config.yaml
│   └── README.md                   # Model client docs
│
├── coordination/                   # 🤝 Multi-Agent Coordination
│   ├── crew_orchestrator.py        # CrewAI-based orchestration
│   └── policy_agent.py              # Policy enforcement agent
│
├── workflow/                       # 📋 Workflow Management
│   ├── work_order_processor.py     # Work order processing engine
│   ├── active-projects/            # Active project workflows
│   │   ├── DEMO-CONSTANT-001/
│   │   ├── WO-20250917-DEMO001/
│   │   └── WO-20250917-REALISTIC-001/
│   ├── completed-work/             # Completed workflows archive
│   │   ├── 2025-09-17-WO-*/
│   │   └── 2025-09-17-portfolio-*/
│   ├── inbox/                      # Incoming work orders
│   │   ├── multi-project-assessment.yaml
│   │   └── test-work-order.yaml
│   ├── templates/                  # Workflow templates
│   │   ├── incident-response-template.md
│   │   └── security-assessment-template.md
│   ├── knowledge-base/             # Workflow knowledge
│   ├── learning-data/              # ML training data from workflows
│   ├── james-workflow.log          # Workflow execution logs
│   ├── MENTOR_DEMONSTRATION_SUMMARY.md
│   └── README.md                   # Workflow documentation
│
├── config/                         # ⚙️ Platform Configuration
│   ├── platform-config.yaml        # Main platform config
│   ├── scanners.json               # Scanner configuration
│   ├── opa-policies/               # OPA policy definitions
│   ├── backups/                    # Configuration backups
│   └── README.md                   # Config documentation
│
├── custom_tools/                   # 🛠️ Custom Tool Builders
│   ├── mcp_tool_builder.py         # MCP tool creation utility
│   └── registry/                   # Tool registry
│       ├── checkov/                # Checkov tool definitions
│       ├── semgrep/                # Semgrep tool definitions
│       └── trivy/                  # Trivy tool definitions
│
├── scripts/                        # 📜 Utility Scripts
│   ├── gp_status.py                # Platform status checker
│   ├── import_fix.py               # Import path fixer
│   └── migrate_secrets.py          # Secret migration utility
│
├── docs/                           # 📚 Platform Documentation
│   ├── ARCHITECTURE_UPDATE_COMPLETE.md
│   ├── JAMES_SECURITY_QUICK_REFERENCE.md
│   ├── SCANNER_ARCHITECTURE_DOCUMENTATION.md
│   ├── SECURITY_ARCHITECTURE_GUIDE.md
│   ├── SECURITY_AUTOMATION_WORKFLOW.md
│   ├── WORKFLOW_DOCUMENTATION.md
│   ├── API_WORKFLOW_DIAGRAM.md
│   └── README.md
│
└── README.md                       # This file
```

---

## Critical Component: james-config/

### ⚠️ WARNING: Platform-Wide Dependency

The `james-config/` directory contains **critical shared configuration** used by:

1. **GP-AI** - RAG engine, model paths, data locations
2. **GP-CONSULTING** - ALL scanner and fixer scripts
3. **GP-DATA** - Data sync scripts, simple_rag_query.py
4. **gp-security** - Main security CLI wrapper
5. **bin/jade-stats** - Observability dashboard
6. **All Python components** - Path resolution

**If you modify james-config/, you MUST test the entire platform!**

### gp_data_config.py

**The single source of truth for all data paths:**

```python
# GP-DATA paths
GP_DATA_ROOT = "/home/jimmie/linkops-industries/GP-copilot/GP-DATA"
ACTIVE_SCANS_DIR = f"{GP_DATA_ROOT}/active/scans"
ACTIVE_REPORTS_DIR = f"{GP_DATA_ROOT}/active/reports"
ACTIVE_FIXES_DIR = f"{GP_DATA_ROOT}/active/fixes"
KNOWLEDGE_BASE_DIR = f"{GP_DATA_ROOT}/knowledge-base"
CHROMADB_PATH = f"{GP_DATA_ROOT}/active/chroma_db"
AUDIT_LOG_PATH = f"{GP_DATA_ROOT}/active/audit"

# Model configuration
DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Platform paths
GP_COPILOT_ROOT = "/home/jimmie/linkops-industries/GP-copilot"
GP_PROJECTS_ROOT = f"{GP_COPILOT_ROOT}/GP-PROJECTS"
```

### agent_metadata.py

**Agent configuration and metadata:**

```python
AGENT_METADATA = {
    "jade": {
        "name": "JADE AI Security Consultant",
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "capabilities": ["scanning", "analysis", "remediation"],
        "api_port": 8000
    },
    "scanners": {
        "bandit": {"severity_levels": ["LOW", "MEDIUM", "HIGH"]},
        "trivy": {"scan_types": ["vuln", "config", "secret"]},
        # ...
    }
}
```

### How Components Use james-config

**GP-AI Integration**:
```python
# GP-AI/core/rag_engine.py
sys.path.insert(0, "GP-PLATFORM/james-config")
from gp_data_config import CHROMADB_PATH, KNOWLEDGE_BASE_DIR

class RAGEngine:
    def __init__(self):
        self.chroma_path = CHROMADB_PATH
        self.kb_path = KNOWLEDGE_BASE_DIR
```

**GP-CONSULTING Scanner Integration**:
```python
# GP-CONSULTING/scanners/bandit_scanner.py
sys.path.insert(0, "GP-PLATFORM/james-config")
from gp_data_config import ACTIVE_SCANS_DIR, GP_PROJECTS_ROOT

def save_results(results):
    output_file = f"{ACTIVE_SCANS_DIR}/bandit_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f)
```

**gp-security CLI Integration**:
```bash
#!/bin/bash
# Set PYTHONPATH to include james-config
export PYTHONPATH="GP-PLATFORM/james-config:$PYTHONPATH"

# Run scanner with configuration
python GP-CONSULTING/scanners/bandit_scanner.py "$@"
```

---

## Core Services

### 1. james_orchestrator.py

**Main platform orchestrator - coordinates all agents and workflows**

```python
from GP_PLATFORM.core.james_orchestrator import JamesOrchestrator

orchestrator = JamesOrchestrator()

# Execute workflow
result = orchestrator.execute_workflow(
    workflow_type="security_scan",
    target="GP-PROJECTS/MyApp",
    scanners=["trivy", "bandit", "gitleaks"]
)

# Result includes: scan results, AI analysis, recommendations
```

**Features**:
- Multi-agent coordination
- Workflow state management
- Error handling and recovery
- Result aggregation

### 2. james_command_router.py

**Command routing and dispatching**

```python
from GP_PLATFORM.core.james_command_router import CommandRouter

router = CommandRouter()

# Register command handlers
router.register("scan", scan_handler)
router.register("fix", fix_handler)
router.register("analyze", analyze_handler)

# Route command
result = router.route("scan GP-PROJECTS/MyApp --scanners trivy,bandit")
```

### 3. secrets_manager.py

**Centralized secrets management**

```python
from GP_PLATFORM.core.secrets_manager import SecretsManager

secrets = SecretsManager()

# Store secret
secrets.store("github_token", "ghp_xxxxxxxxxxxx")

# Retrieve secret
token = secrets.get("github_token")

# List secrets
all_secrets = secrets.list()

# Rotate secret
secrets.rotate("github_token", new_value="ghp_yyyyyyyyyyyy")
```

**Storage**: Encrypted in `GP-DATA/active/audit/secrets.enc`

### 4. jade_logger.py

**Centralized logging and observability**

```python
from GP_PLATFORM.core.jade_logger import get_logger

logger = get_logger()

# Log events
logger.log_event("scan_started", {
    "target": "GP-PROJECTS/MyApp",
    "scanners": ["trivy", "bandit"]
})

# Get stats
stats = logger.get_stats()
print(f"Total events: {stats['total_events']}")
print(f"Error rate: {stats['error_rate']}%")

# Verify integrity
integrity = logger.verify_integrity()
```

**Evidence Log**: `~/.jade/evidence.jsonl` (or `GP-DATA/active/audit/jade-evidence.jsonl`)

---

## API Gateway

### agent_gateway.py

**Multi-agent API routing**

```bash
# Start API gateway
python GP-PLATFORM/api/agent_gateway.py --port 8000

# Routes:
# POST /api/scan - Trigger security scan
# POST /api/analyze - AI analysis
# POST /api/fix - Apply remediation
# GET /api/status - Platform status
# GET /api/agents - List agents
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "target": "GP-PROJECTS/MyApp",
    "scanners": ["trivy", "bandit", "gitleaks"],
    "compliance": ["SOC2", "PCI-DSS"]
  }'
```

### Unified API (`api/unified/`)

**Automation-focused API endpoints**

```python
# api/unified/automation_api.py
from fastapi import FastAPI

app = FastAPI()

@app.post("/automate/scan")
async def automated_scan(project: str, scanners: List[str]):
    # Automated scanning workflow
    pass

@app.post("/automate/remediate")
async def automated_remediation(scan_id: str):
    # Automated fix application
    pass
```

---

## Model Context Protocol (MCP)

### MCP Server (`mcp/server.py`)

**Expose GP-JADE tools via MCP for external integrations**

```bash
# Start MCP server
python GP-PLATFORM/mcp/server.py --port 8100

# Exposes:
# - Security scanning tools
# - AI analysis capabilities
# - Remediation functions
# - Knowledge base queries
```

**Integration Example** (with Claude Desktop):
```json
{
  "mcpServers": {
    "gp-jade": {
      "command": "python",
      "args": ["GP-PLATFORM/mcp/server.py"],
      "env": {
        "PYTHONPATH": "GP-PLATFORM/james-config:$PYTHONPATH"
      }
    }
  }
}
```

### MCP Agents

**client_intelligence_agent.py**
- Client context analysis
- Project profiling
- Compliance requirement mapping

**consulting_remediation_agent.py**
- Security issue remediation
- Fix generation
- Verification

**implementation_planning_agent.py**
- Implementation roadmaps
- Task decomposition
- Timeline estimation

---

## Workflow Management

### work_order_processor.py

**Process security work orders**

```yaml
# workflow/inbox/work-order.yaml
work_order:
  id: WO-20251007-001
  client: Acme Corp
  project: fintech-api
  type: security_assessment
  compliance_frameworks:
    - SOC2
    - PCI-DSS
  scope:
    - code_review
    - infrastructure_scan
    - policy_validation
  deliverables:
    - executive_summary
    - technical_report
    - remediation_plan
```

**Processing**:
```bash
# Process work order
python GP-PLATFORM/workflow/work_order_processor.py \
  --input workflow/inbox/work-order.yaml

# Workflow stages:
# 1. Intake → workflow/active-projects/
# 2. Execution → Scans, analysis, remediation
# 3. Reporting → Generate deliverables
# 4. Completion → workflow/completed-work/
```

### Workflow Templates

**incident-response-template.md**
- Incident response workflow
- Forensics procedures
- Recovery steps

**security-assessment-template.md**
- Security assessment workflow
- Compliance checklists
- Report structure

---

## Configuration

### platform-config.yaml

```yaml
platform:
  name: "GP-JADE Security Platform"
  version: "2.1"

agents:
  jade:
    model: "Qwen/Qwen2.5-7B-Instruct"
    api_port: 8000
    gpu_enabled: true

orchestration:
  max_concurrent_scans: 5
  scan_timeout: 600  # seconds

scanners:
  enabled:
    - bandit
    - trivy
    - semgrep
    - gitleaks
    - checkov
    - tfsec
    - kubescape
    - opa

reporting:
  formats: ["json", "html", "markdown"]
  auto_escalate_critical: true

compliance:
  frameworks: ["SOC2", "PCI-DSS", "HIPAA", "CIS", "NIST"]
```

### scanners.json

```json
{
  "bandit": {
    "command": "bandit",
    "args": ["-r", "-f", "json"],
    "severity_map": {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
  },
  "trivy": {
    "command": "trivy",
    "args": ["fs", "--format", "json"],
    "scan_types": ["vuln", "config", "secret"]
  }
}
```

---

## Utility Scripts

### gp_status.py

**Check platform status**

```bash
python GP-PLATFORM/scripts/gp_status.py

# Output:
# ✅ james-config: OK
# ✅ GP-DATA paths: OK
# ✅ Vector DB: OK (56 documents)
# ✅ Jade AI: Running (Qwen2.5-7B)
# ✅ Scanners: 9/9 available
# ⚠️  GPU: Available (NVIDIA RTX 5080)
```

### migrate_secrets.py

**Migrate secrets to centralized manager**

```bash
python GP-PLATFORM/scripts/migrate_secrets.py \
  --source ~/.secrets \
  --destination GP-DATA/active/audit/secrets.enc
```

---

## Integration Patterns

### Pattern 1: Scanner Integration

```python
# Any scanner script
import sys
sys.path.insert(0, "GP-PLATFORM/james-config")
from gp_data_config import ACTIVE_SCANS_DIR, GP_PROJECTS_ROOT

def scan_project(project_name):
    project_path = f"{GP_PROJECTS_ROOT}/{project_name}"
    # Scan logic...
    output_path = f"{ACTIVE_SCANS_DIR}/scanner_{timestamp}.json"
    save_results(output_path)
```

### Pattern 2: API Integration

```python
# External application
import requests

response = requests.post(
    "http://localhost:8000/api/scan",
    json={"target": "MyApp", "scanners": ["trivy"]}
)

scan_id = response.json()["scan_id"]
```

### Pattern 3: MCP Integration

```python
# MCP client
from mcp import Client

client = Client("http://localhost:8100")
result = client.call_tool("security_scan", {
    "project": "MyApp",
    "scanners": ["bandit", "semgrep"]
})
```

---

## Best Practices

### 1. Never Hardcode Paths

```python
# ❌ Bad
scan_dir = "/home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/scans"

# ✅ Good
from gp_data_config import ACTIVE_SCANS_DIR
scan_dir = ACTIVE_SCANS_DIR
```

### 2. Always Test Platform-Wide Changes

```bash
# After modifying james-config
jade scan GP-PROJECTS/test-project
python GP-CONSULTING/scanners/bandit_scanner.py GP-PROJECTS/test-project
python GP-DATA/simple_sync.py --verify
python GP-PLATFORM/scripts/gp_status.py
```

### 3. Use Centralized Logging

```python
from GP_PLATFORM.core.jade_logger import get_logger

logger = get_logger()
logger.log_event("custom_action", {"detail": "value"})
```

### 4. Handle Secrets Properly

```python
from GP_PLATFORM.core.secrets_manager import SecretsManager

secrets = SecretsManager()
api_key = secrets.get("api_key")  # Never hardcode!
```

---

## Troubleshooting

### Import Errors from james-config

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="GP-PLATFORM/james-config:$PYTHONPATH"

# Or add to script
import sys
sys.path.insert(0, "GP-PLATFORM/james-config")
```

### Platform Status Check

```bash
python GP-PLATFORM/scripts/gp_status.py
```

### API Gateway Won't Start

```bash
# Check if port is in use
lsof -i :8000

# Start on different port
python GP-PLATFORM/api/agent_gateway.py --port 8001
```

### MCP Server Issues

```bash
# Check MCP config
cat GP-PLATFORM/mcp/config/mcp_config.yaml

# Verify MCP installation
python -c "import mcp; print(mcp.__version__)"
```

---

## Performance & Scalability

### Current Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| **Config Load** | <10ms | james-config import |
| **API Response** | ~200ms | Simple scan trigger |
| **Workflow Processing** | ~5-10s | Full work order |
| **MCP Tool Call** | ~300ms | Including network overhead |

### Scaling Considerations

- **Multi-threading**: Work order processor supports concurrent scans
- **Queue System**: MCP queue routes for async processing
- **Load Balancing**: API gateway can run multiple instances
- **Caching**: Configuration caching reduces I/O

---

## Future Enhancements

### Planned Features

- [ ] **Distributed Orchestration**: Multi-node coordination
- [ ] **Advanced Workflow Engine**: BPMN-based workflows
- [ ] **Enhanced MCP Tools**: More tool exposures
- [ ] **Real-Time Metrics**: Prometheus/Grafana integration
- [ ] **Plugin System**: Dynamic plugin loading
- [ ] **RBAC**: Role-based access control for API
- [ ] **Audit Compliance**: SOC2 audit trail automation

---

## Related Components

- **[GP-AI/](../GP-AI/)** - Uses james-config for paths and models
- **[GP-CONSULTING/](../GP-CONSULTING/)** - All scanners use james-config
- **[GP-DATA/](../GP-DATA/)** - Paths defined in james-config
- **[gp-security](../gp-security)** - Sets PYTHONPATH to james-config
- **[bin/jade-stats](../bin/jade-stats)** - Uses core/jade_logger.py

---

## Quick Reference

```bash
# Check platform status
python GP-PLATFORM/scripts/gp_status.py

# Start API gateway
python GP-PLATFORM/api/agent_gateway.py

# Start MCP server
python GP-PLATFORM/mcp/server.py

# Process work order
python GP-PLATFORM/workflow/work_order_processor.py --input workflow/inbox/order.yaml

# Migrate secrets
python GP-PLATFORM/scripts/migrate_secrets.py

# Verify james-config usage
grep -r "from gp_data_config" . --include="*.py"
```

---

**Status**: ✅ Production Ready - CRITICAL SHARED COMPONENT
**Last Updated**: 2025-10-07
**Size**: ~1.5MB
**⚠️ WARNING**: Contains critical shared configuration. Test thoroughly before making changes.
**Maintained by**: LinkOps Industries - JADE AI Security Platform Team