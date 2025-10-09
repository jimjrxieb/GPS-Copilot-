# GP-Config - Platform Configuration Hub

This directory contains all configuration files for the GP-Copilot security platform.

## Configuration Files

### platform-config.yaml
Main platform configuration including:
- Data persistence paths
- Scanner defaults
- OPA settings
- Reporting configuration
- Integration settings
- Security policies
- Performance tuning
- Logging configuration

### scanners.json
Detailed scanner configurations:
- Individual scanner settings (Trivy, Bandit, Semgrep, Checkov, Gitleaks, OPA)
- Scan profiles (quick, comprehensive, compliance, secrets)
- Scheduling options
- Custom scanner definitions

## Usage

### Reading Configuration in Python
```python
import yaml
import json
from pathlib import Path

# Load platform config
with open('GP-CONFIG-OPS/GP-config/platform-config.yaml', 'r') as f:
    platform_config = yaml.safe_load(f)

# Load scanner config
with open('GP-CONFIG-OPS/GP-config/scanners.json', 'r') as f:
    scanner_config = json.load(f)
```

### Environment Variables
Override any configuration using environment variables:
- `GP_DATA_ROOT` - Override data storage location
- `GP_ENVIRONMENT` - Set environment (production/staging/development)
- `GP_LOG_LEVEL` - Override logging level

## Configuration Hierarchy

1. **Default Values** - Built into code
2. **Configuration Files** - This directory
3. **Environment Variables** - Runtime overrides
4. **Command Line Arguments** - Highest priority

## Best Practices

1. **Never commit secrets** - Use environment variables for sensitive data
2. **Version control** - All changes should be tracked in git
3. **Test changes** - Validate configuration before deploying
4. **Document changes** - Update this README when adding new configs

## File Formats

- **YAML** (.yaml) - Human-readable configuration
- **JSON** (.json) - Machine-readable, strict validation
- **TOML** (.toml) - Simple configuration (future)

## Validation

Run configuration validation:
```bash
python3 ../gp_status.py --validate-config
```

## Policy as Code

OPA policies are stored separately in:
`GP-CONSULTING-AGENTS/policies/opa/`

These configs reference the policy location but don't contain the policies themselves.