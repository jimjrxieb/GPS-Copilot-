# GP-PLATFORM: Shared Platform Components

> **Purpose**: Platform-wide shared utilities, configuration, and integration points

## Overview

GP-PLATFORM contains components used across the entire GuidePoint Security platform:
- **james-config/** - Critical shared configuration (⚠️ DO NOT MODIFY without understanding dependencies)
- **API Gateway** - Unified API entry point
- **MCP Integration** - Model Context Protocol support
- **Core Services** - Platform orchestration

## Structure

```
GP-PLATFORM/
├── README.md                    # This file
│
├── james-config/                🔒 CRITICAL SHARED CONFIG
│   ├── gp_data_config.py        # GP-DATA paths and settings
│   └── agent_metadata.py        # Agent configuration
│   ⚠️  Used by: GP-AI, GP-CONSULTING-AGENTS, GP-DATA, gp-security
│
├── api/                         # API Gateway
│   ├── agent_gateway.py         # Multi-agent API routing
│   ├── unified/                 # Unified API endpoints
│   └── mcp/                     # MCP integration
│
├── core/                        # Platform core
│   ├── james_orchestrator.py   # Main platform orchestrator
│   ├── james_command_router.py # Command routing
│   ├── secrets_manager.py      # Secrets management
│   └── config.py                # Platform configuration
│
├── mcp/                         # Model Context Protocol
│   ├── server.py                # MCP server
│   ├── agents/                  # MCP-enabled agents
│   ├── tools/                   # MCP tool definitions
│   └── config/                  # MCP configuration
│
├── model_client/                # LLM Client Abstraction
│   ├── clients/                 # Different LLM clients
│   ├── intelligence/            # AI intelligence layer
│   └── james_mlops_client.py   # MLOps client
│
├── coordination/                # Multi-agent coordination
│   ├── crew_orchestrator.py    # CrewAI orchestration
│   └── policy_agent.py          # Policy enforcement
│
├── config/                      # Platform configuration
│   ├── platform-config.yaml    # Main config file
│   ├── scanners.json            # Scanner configuration
│   └── opa-policies/            # OPA policy definitions
│
├── workflow/                    # Workflow management
│   ├── work_order_processor.py # Work order processing
│   ├── templates/               # Workflow templates
│   └── knowledge-base/          # Workflow knowledge
│
├── custom_tools/                # Custom tool builders
│   ├── mcp_tool_builder.py     # MCP tool creation
│   └── registry/                # Tool registry
│
├── scripts/                     # Utility scripts
│   ├── gp_status.py             # Platform status check
│   └── migrate_secrets.py       # Secret migration
│
└── docs/                        # Platform documentation
    ├── ARCHITECTURE_UPDATE_COMPLETE.md
    ├── SECURITY_ARCHITECTURE_GUIDE.md
    └── WORKFLOW_DOCUMENTATION.md
```

## Critical: james-config/

⚠️ **IMPORTANT**: `james-config/` is used by almost every component!

### gp_data_config.py

```python
# Defines paths for GP-DATA
GP_DATA_ROOT = "/home/jimmie/linkops-industries/GP-copilot/GP-DATA"
ACTIVE_SCANS_DIR = f"{GP_DATA_ROOT}/active/scans"
KNOWLEDGE_BASE_DIR = f"{GP_DATA_ROOT}/knowledge-base"
CHROMADB_PATH = f"{KNOWLEDGE_BASE_DIR}/chroma"
```

**Used by**:
- GP-AI (RAG engine, scanners)
- GP-CONSULTING-AGENTS (all scanners)
- gp-security script
- GP-DATA sync scripts

**⚠️  Changing this breaks the entire platform!**

## Usage

### Check Platform Status

```bash
python GP-PLATFORM/scripts/gp_status.py
```

### Access API Gateway

```bash
# Start unified API
python GP-PLATFORM/api/unified/server.py

# Access at http://localhost:8000
```

### MCP Integration

```bash
# Start MCP server
python GP-PLATFORM/mcp/server.py
```

### Workflow Processing

```bash
# Process work orders
python GP-PLATFORM/workflow/work_order_processor.py
```

## Integration Points

### GP-AI Integration

```python
# GP-AI imports james-config
from GP_PLATFORM.james_config import gp_data_config

# Uses paths from config
scan_dir = gp_data_config.ACTIVE_SCANS_DIR
```

### GP-CONSULTING-AGENTS Integration

```python
# Scanners import config
sys.path.insert(0, "GP-PLATFORM/james-config")
from gp_data_config import GP_DATA_ROOT, ACTIVE_SCANS_DIR

# Save results to configured path
with open(f"{ACTIVE_SCANS_DIR}/bandit_latest.json", "w") as f:
    json.dump(results, f)
```

### gp-security Script Integration

```bash
# Sets PYTHONPATH to james-config
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python scanners/bandit_scanner.py
```

## Key Components

### 1. james_orchestrator.py

Main platform orchestrator - coordinates all agents and workflows.

### 2. agent_gateway.py

API gateway that routes requests to appropriate agents/services.

### 3. secrets_manager.py

Centralized secrets management (API keys, credentials, etc.).

### 4. MCP Server

Model Context Protocol support for external integrations.

## Configuration

### platform-config.yaml

```yaml
platform:
  name: "GuidePoint Security Platform"
  version: "2.0"
  
agents:
  jade:
    model: "Qwen/Qwen2.5-7B-Instruct"
    api_port: 8000
    
scanners:
  enabled: ["bandit", "trivy", "semgrep", "gitleaks", "opa"]
```

## Best Practices

### 1. Never Modify james-config/ Directly

Always understand dependencies first:

```bash
# Check who uses it
grep -r "from gp_data_config" GP-*/ --include="*.py"
grep -r "james-config" . --include="*.py"
```

### 2. Use Centralized Config

Don't hardcode paths - use james-config:

```python
# ❌ Bad
scan_dir = "/home/user/GP-DATA/active/scans"

# ✅ Good
from gp_data_config import ACTIVE_SCANS_DIR
scan_dir = ACTIVE_SCANS_DIR
```

### 3. Test Platform-Wide Changes

If you modify james-config or core components:

```bash
# Test all dependent systems
jade scan GP-PROJECTS/test
python GP-CONSULTING-AGENTS/scanners/bandit_scanner.py --test
python GP-DATA/simple_sync.py --verify
```

## For Interviews

**Show centralized configuration**:
> "We use GP-PLATFORM/james-config for centralized configuration. This ensures consistency across all components - if we need to change GP-DATA paths, we change it once and all scanners, AI components, and scripts automatically use the new paths."

**Show MCP integration**:
> "We support the Model Context Protocol for external integrations, making it easy to expose our security tools to other AI systems."

## Troubleshooting

### Import errors from james-config

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH

# Or add to script
sys.path.insert(0, "GP-PLATFORM/james-config")
```

### Platform status check

```bash
python GP-PLATFORM/scripts/gp_status.py
```

## Related

- **GP-AI** - Uses james-config for paths
- **GP-CONSULTING-AGENTS** - All scanners use james-config
- **GP-DATA** - Paths defined in james-config
- **gp-security** - Sets PYTHONPATH to james-config

---

**Status**: ✅ Production Ready - CRITICAL COMPONENT
**Last Updated**: 2025-10-04

⚠️ **WARNING**: This directory contains critical shared configuration. Test thoroughly before making changes.
