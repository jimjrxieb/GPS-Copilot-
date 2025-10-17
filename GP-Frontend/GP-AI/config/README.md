# GP-AI Configuration Files

**Purpose:** Configuration management for Jade AI and security platform

---

## 📁 Configuration Files

### 1. **platform_config.py** (Python Config) ⭐ PRIMARY
**Purpose:** Python-based configuration with secrets management

**Features:**
- ✅ Secrets management (AWS, GitHub, Docker credentials)
- ✅ Dynamic GP-DATA path (won't break if repo moves)
- ✅ Environment variable overrides
- ✅ Validation methods
- ✅ Singleton pattern for consistent access

**Usage:**
```python
from config.platform_config import get_config

config = get_config()

# Get secrets
aws_creds = config.get_aws_credentials()
github_token = config.get_github_token()

# Get paths (dynamic, not hardcoded)
data_dir = config.get_data_directory()
# Returns: /home/jimmie/linkops-industries/GP-copilot/GP-DATA

# Check validation
status = config.get_validation_status()
# Returns: {"aws": True, "github": False, ...}
```

**When to Use:**
- ✅ When you need secrets/credentials
- ✅ When you need dynamic paths
- ✅ In Python code
- ✅ For environment-specific config

**DO NOT:**
- ❌ Hardcode credentials here (use secrets manager)
- ❌ Hardcode absolute paths (use dynamic calculation)

---

### 2. **platform-config.yaml** (YAML Config) ⚠️ SECONDARY
**Purpose:** Declarative YAML configuration for defaults

**Content:**
- Platform metadata (name, version, environment)
- Data path defaults (⚠️ currently hardcoded)
- Scanner settings (enabled scanners, timeouts)
- OPA configuration
- Reporting settings
- Integration toggles (GitHub, Slack, Email)
- Security settings
- Logging configuration

**When to Use:**
- ✅ For non-sensitive defaults
- ✅ When you want declarative config
- ✅ For scanner/tool settings
- ✅ For feature flags

**DO NOT:**
- ❌ Put secrets here (use platform_config.py)
- ❌ Rely on hardcoded paths (they break portability)

**Status:** ⚠️ **Overlaps with platform_config.py** - May consolidate in future

---

### 3. **scanners.json** (Scanner Tool Config)
**Purpose:** Scanner tool definitions and metadata

**Content:**
```json
{
  "trivy": {
    "command": "trivy fs",
    "output_format": "json",
    "severity": ["HIGH", "CRITICAL"]
  },
  "bandit": {
    "command": "bandit",
    "output_format": "json"
  }
}
```

**When to Use:**
- ✅ Defining scanner tool commands
- ✅ Scanner-specific settings
- ✅ Output format configuration

**Note:** May overlap with platform-config.yaml scanners section

---

### 4. **jade_prompts.py** (AI Prompt Templates)
**Purpose:** System prompts and templates for Jade AI

**Content:**
- System prompts for different contexts
- RAG query templates
- Agent instruction templates
- Response formatting templates

**Example:**
```python
SYSTEM_PROMPT = """
You are Jade, a security assistant specialized in:
- Cloud security (AWS, Azure, GCP)
- Kubernetes security
- OPA policy enforcement
- Automated remediation
"""

RAG_QUERY_TEMPLATE = """
Given the following context: {context}
User question: {question}
Provide a detailed answer...
"""
```

**When to Use:**
- ✅ Modifying Jade's behavior/personality
- ✅ Updating RAG query formats
- ✅ Changing agent instructions

---

### 5. **routing_config.json** (Request Routing)
**Purpose:** Configure how requests are routed to agents

**Content:**
```json
{
  "intents": {
    "troubleshoot": ["troubleshooting_agent"],
    "scan": ["policy_agent", "scanner_agent"],
    "fix": ["policy_agent", "fixer_agent"]
  },
  "domains": {
    "kubernetes": ["troubleshooting_agent"],
    "opa": ["policy_agent"],
    "terraform": ["iac_agent"]
  }
}
```

**When to Use:**
- ✅ Adding new agents
- ✅ Changing routing logic
- ✅ Intent/domain mappings

---

## 🎯 Configuration Hierarchy

**Priority Order (highest to lowest):**

1. **Environment Variables** (highest priority)
   ```bash
   export JADE_DATA_DIR="/custom/path/GP-DATA"
   export AWS_ACCESS_KEY="..."
   ```

2. **Secrets Manager** (for credentials)
   ```python
   config.get_aws_credentials()  # From secrets manager
   ```

3. **platform_config.py** (Python defaults)
   ```python
   config.get_data_directory()  # Dynamic calculation
   ```

4. **platform-config.yaml** (YAML defaults)
   ```yaml
   data:
     base_path: "/home/jimmie/..."
   ```

**Rule:** More specific beats more general

---

## 🔧 Common Configuration Tasks

### Add New Secret
```python
# In platform_config.py, add getter method:
def get_new_service_token(self) -> Optional[str]:
    """Get new service token from secrets manager"""
    return self.sm.get_secret("new_service_token")

# Usage:
token = get_config().get_new_service_token()
```

### Change Scanner Settings
```yaml
# In platform-config.yaml:
scanners:
  enabled:
    - trivy
    - bandit
    - your_new_scanner
  timeout_seconds: 600  # Increase timeout
```

### Update Jade Prompts
```python
# In jade_prompts.py:
SYSTEM_PROMPT = """
You are Jade, now also an expert in:
- New domain
- New capability
"""
```

### Add Agent Routing
```json
// In routing_config.json:
{
  "intents": {
    "new_intent": ["new_agent"]
  }
}
```

---

## ⚠️ Current Issues & Recommendations

### Issue 1: Config Duplication
**Problem:** platform_config.py and platform-config.yaml both provide configuration

**Options:**
- **A (Recommended):** Use Python (platform_config.py) as primary, delete YAML
- **B:** Use Python for secrets/sensitive, YAML for defaults only
- **C:** Keep both but document which has priority

**Current Status:** Both exist, no clear hierarchy

### Issue 2: Hardcoded Paths in YAML
**Problem:** platform-config.yaml has hardcoded paths like:
```yaml
data:
  base_path: "/home/jimmie/linkops-industries/GP-copilot/GP-DATA"
```

**Solution:** Use environment variables:
```yaml
data:
  base_path: "${JADE_DATA_DIR:-/home/jimmie/linkops-industries/GP-copilot/GP-DATA}"
```

Or just rely on Python config (which has dynamic paths)

### Issue 3: Scanner Config Split
**Problem:** Scanner config in both scanners.json AND platform-config.yaml

**Recommendation:** Pick one location

---

## 🚀 Best Practices

### 1. Never Hardcode Secrets
```python
# ❌ BAD
AWS_KEY = "AKIAXXX..."

# ✅ GOOD
from config.platform_config import get_config
aws_key = get_config().get_aws_access_key()
```

### 2. Never Hardcode Absolute Paths
```python
# ❌ BAD
gp_data = Path("/home/jimmie/linkops-industries/GP-copilot/GP-DATA")

# ✅ GOOD
from config.platform_config import get_config
gp_data = get_config().get_data_directory()
```

### 3. Use Environment Variables for Overrides
```bash
# Override in production
export JADE_ENV=production
export JADE_DATA_DIR=/production/data
export LOG_LEVEL=WARNING
```

### 4. Validate Configuration
```python
config = get_config()
status = config.get_validation_status()

if not status["aws"]:
    print("⚠️ AWS not configured")
```

---

## 📚 Related Files

- **Secrets Manager:** `GP-AI/core/secrets_manager.py`
- **GP-DATA Config:** `GP-Backend/jade-config/gp_data_config.py`
- **Jade Orchestrator:** `GP-AI/agents/jade_orchestrator.py`

---

## 🔍 Debugging Configuration

### Check What Config is Being Used
```python
from config.platform_config import get_config

config = get_config()
print(f"Data dir: {config.get_data_directory()}")
print(f"Environment: {config.get_environment()}")
print(f"Log level: {config.get_log_level()}")
print(f"Validation: {config.get_validation_status()}")
```

### Check Environment Variables
```bash
env | grep JADE
env | grep AWS
env | grep LOG_LEVEL
```

### Test Dynamic Paths
```python
from pathlib import Path
from config.platform_config import get_config

gp_data = get_config().get_data_directory()
print(f"GP-DATA: {gp_data}")
print(f"Exists: {gp_data.exists()}")
print(f"Is absolute: {gp_data.is_absolute()}")
```

---

## 📖 Summary

### Which Config File to Use?

| Need | Use This |
|------|----------|
| Secrets/credentials | `platform_config.py` |
| Dynamic paths | `platform_config.py` |
| Scanner settings | `scanners.json` or `platform-config.yaml` |
| AI prompts | `jade_prompts.py` |
| Agent routing | `routing_config.json` |
| Feature flags | `platform-config.yaml` |

### Primary vs Secondary

**Primary (Use First):**
- `platform_config.py` - For sensitive + dynamic config
- `jade_prompts.py` - For AI behavior
- `routing_config.json` - For agent routing

**Secondary (Use for Defaults):**
- `platform-config.yaml` - For non-sensitive defaults
- `scanners.json` - For scanner metadata

---

**Last Updated:** 2025-10-16
**Status:** Multiple config files exist, consolidation recommended
**Recommendation:** Use platform_config.py as primary source of truth
