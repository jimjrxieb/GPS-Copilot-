# GP-TESTING-VAL: Testing & Validation Suite

> **Purpose**: Integration tests, demos, and validation scripts for the GP platform

## What's Here

This directory contains:
- **Integration tests** - End-to-end testing
- **Demo scripts** - For interviews and presentations
- **Validation tests** - Verify component functionality
- **Test fixtures** - Sample data and configurations

## Structure

```
GP-TESTING-VAL/
├── demos/                      # Demo scripts for presentations
│   ├── jade_quick_demo.py      # Quick Jade demo
│   ├── interview-demo-cli.py   # CLI demo for interviews
│   └── demonstrate_gatekeeper.py # OPA/Gatekeeper demo
│
├── tests/                      # Test suites
│   ├── integration/            # Integration tests
│   ├── e2e/                    # End-to-end tests
│   └── automation_engine/      # Automation tests
│
├── test_terraform/             # Terraform test fixtures
├── test_simple/                # Simple test cases
│
└── *.py                        # Individual test scripts
    ├── simple_integration_test.py
    ├── test_portfolio_scan.py
    └── test_real_project.py
```

## Quick Start

### Run Integration Tests
```bash
# All integration tests
pytest tests/integration/

# Specific test
python simple_integration_test.py
```

### Run Demos (For Interviews)
```bash
# Quick Jade demo
python demos/jade_quick_demo.py

# Full interview demo
python demos/interview-demo-cli.py
```

### Validate Components
```bash
# Test RAG consulting
python test_guidepoint_rag_consulting.py

# Test scanner integration
python test_portfolio_scan.py
```

## Test Categories

### 1. Integration Tests (`tests/integration/`)
- Component interaction testing
- Scanner pipeline validation
- RAG integration tests

### 2. E2E Tests (`tests/e2e/`)
- Full workflow validation
- User journey testing
- Performance benchmarks

### 3. Demo Scripts (`demos/`)
**For interviews and presentations**:
- `jade_quick_demo.py` - 2-minute Jade overview
- `interview-demo-cli.py` - Full CLI walkthrough
- `demonstrate_gatekeeper.py` - OPA policy enforcement

### 4. Validation Tests (Root `*.py`)
- Individual component tests
- Security scanner validation
- Feature verification

## Running Tests

### All Tests
```bash
pytest GP-TESTING-VAL/
```

### Integration Only
```bash
pytest GP-TESTING-VAL/tests/integration/
```

### Specific Test
```bash
python GP-TESTING-VAL/test_real_project.py
```

### Demo Mode (No Assertions)
```bash
python GP-TESTING-VAL/demos/jade_quick_demo.py
```

## Test Fixtures

### Terraform Test Cases
```
test_terraform/
└── main.tf          # Sample Terraform with intentional issues
```

### Kubernetes Test Cases
```
evidence-test-pod-fixed.yaml    # Fixed pod configuration
```

### Configuration Files
```
test_policy_as_code.json        # OPA policy test config
test_secrets_config.json        # Secrets detection test
```

## For Interviews

### Quick Demo (5 minutes)
```bash
python demos/jade_quick_demo.py
```
Shows:
- Jade chat interface
- Security scanning
- RAG knowledge queries

### Full Demo (15 minutes)
```bash
python demos/interview-demo-cli.py
```
Shows:
- Complete platform capabilities
- Integration with all components
- Real-world use cases

## Test Coverage

| Component | Test Files | Coverage |
|-----------|------------|----------|
| Jade Chat | `test_chat_integration.py` | ✅ |
| RAG Engine | `test_guidepoint_rag_consulting.py` | ✅ |
| Scanners | `test_portfolio_scan.py` | ✅ |
| Fixers | `test_james_enhanced_analyzer.py` | ✅ |
| Policy as Code | `test_policy_as_code.json` | ✅ |
| E2E Workflows | `tests/e2e/` | ✅ |

## Best Practices

### Writing New Tests

```python
# tests/integration/test_new_feature.py
import pytest

def test_new_feature():
    """Test new feature integration"""
    # Setup
    # Execute
    # Assert
    pass
```

### Writing Demos

```python
# demos/demo_new_feature.py
from rich.console import Console

console = Console()

def demo_feature():
    """Demo for interviews"""
    console.print("[bold]Feature Demo[/bold]")
    # Show feature without assertions
    # Focus on visual output
```

## Continuous Integration

These tests run automatically on:
- Pull requests
- Main branch commits
- Release tags

```yaml
# .github/workflows/test.yml
- run: pytest GP-TESTING-VAL/
```

## Related Components

- **GP-AI** - Tested by RAG/chat integration tests
- **GP-CONSULTING-AGENTS** - Tested by scanner validation
- **GP-DATA** - Tested by data pipeline tests

---

**Status**: ✅ Production Ready
**Last Updated**: 2025-10-04