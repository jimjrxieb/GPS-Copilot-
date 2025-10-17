# Bandit Scanner - Production Grade Python SAST

## Overview

The Bandit scanner is a **production-grade Python SAST (Static Application Security Testing)** tool that detects common security issues in Python code. It's the **first production scanner** in the SecOps CI/CD pipeline.

## Features

✅ **Inherits from SecurityScanner** base class
✅ **Automatic retry** with exponential backoff (3 attempts)
✅ **Timeout protection** (5 minutes default)
✅ **Comprehensive CWE mapping** (50+ Bandit test IDs mapped)
✅ **Finding enrichment** with file hashes for change tracking
✅ **Structured output** with standardized format
✅ **Metrics emission** to separate JSON file
✅ **Graceful error handling** (missing tool, timeouts, invalid output)
✅ **Non-zero exit codes handled** (Bandit returns 1 when issues found)

## Security Checks

The scanner detects:

- **SQL Injection** (CWE-89) - Unsafe SQL query construction
- **Command Injection** (CWE-78) - Shell command execution vulnerabilities
- **Hardcoded Secrets** (CWE-798) - Passwords, API keys in code
- **Insecure Cryptography** (CWE-327) - MD5, SHA1, weak ciphers
- **Unsafe Deserialization** (CWE-502) - Pickle, YAML, Marshal
- **SSL/TLS Issues** (CWE-295) - Certificate validation bypass
- **Weak Random** (CWE-330) - Using `random` instead of `secrets`
- **Path Traversal** (CWE-22) - Unsafe file path handling
- **Error Handling** (CWE-703) - Silent exception swallowing
- And more...

## Installation

```bash
# Install Bandit
pip install bandit

# Verify installation
bandit --version
```

## Usage

### Basic Usage

```bash
# Scan default target (backend/)
cd secops/1-scanners/ci
python3 bandit_scanner.py

# Scan specific directory
python3 bandit_scanner.py ../../backend/app/

# Scan secops itself (dogfooding)
python3 bandit_scanner.py ../..
```

### Advanced Usage

```bash
# Custom timeout (10 minutes)
python3 bandit_scanner.py --timeout 600 /path/to/python/code

# Custom output directory
python3 bandit_scanner.py --output-dir /custom/path /path/to/code

# Get help
python3 bandit_scanner.py --help
```

### Integration with CI/CD

```yaml
# .github/workflows/security.yml
- name: Run Bandit SAST
  run: |
    cd secops/1-scanners/ci
    python3 bandit_scanner.py ../../backend/
```

## Output Format

### Findings File
**Location**: `secops/2-findings/raw/ci/bandit_TIMESTAMP.json`

```json
{
  "findings": [
    {
      "id": "bandit_1",
      "scanner": "bandit",
      "severity": "CRITICAL",
      "confidence": "HIGH",
      "title": "subprocess call with shell=True identified, security issue.",
      "description": "subprocess call with shell=True identified, security issue.",
      "file": "app/routes/api.py",
      "line": 42,
      "code": "subprocess.run(cmd, shell=True)",
      "test_id": "B602",
      "test_name": "subprocess_popen_with_shell_equals_true",
      "cwe": ["CWE-78"],
      "scan_timestamp": "20250110_150000",
      "file_hash": "abc123def456",
      "_original": { /* Full Bandit output */ }
    }
  ],
  "metadata": {
    "scanner": "bandit",
    "scan_timestamp": "2025-01-10T15:00:00",
    "target": "/path/to/code",
    "issue_count": 15,
    "severity_breakdown": {
      "CRITICAL": 2,
      "HIGH": 3,
      "MEDIUM": 7,
      "LOW": 3,
      "INFO": 0
    },
    "metrics": {
      "files_scanned": 47,
      "lines_of_code": 3421,
      "nosec_comments": 5
    }
  }
}
```

### Metrics File
**Location**: `secops/2-findings/raw/metrics/bandit-TIMESTAMP.json`

```json
{
  "scanner_name": "bandit",
  "start_time": "2025-01-10T15:00:00",
  "end_time": "2025-01-10T15:00:12",
  "duration_seconds": 12.5,
  "exit_code": 1,
  "total_issues": 15,
  "severity_breakdown": {
    "CRITICAL": 2,
    "HIGH": 3,
    "MEDIUM": 7,
    "LOW": 3,
    "INFO": 0
  },
  "retry_count": 0,
  "status": "success"
}
```

### Log Files
**Location**: `secops/2-findings/logs/bandit-TIMESTAMP.log`

Contains detailed execution logs for debugging.

## Severity Calculation

The scanner uses an intelligent severity system:

- **CRITICAL**: `HIGH severity + HIGH confidence` (definite issues)
- **HIGH**: `HIGH severity + MEDIUM/LOW confidence`
- **MEDIUM**: `MEDIUM severity` (any confidence)
- **LOW**: `LOW severity` (any confidence)

This ensures the most dangerous findings are prioritized.

## CWE Mapping Coverage

The scanner includes comprehensive CWE mappings for 50+ Bandit test IDs:

| Category | Bandit Test IDs | CWE |
|----------|----------------|-----|
| SQL Injection | B608, B610, B611 | CWE-89 |
| Command Injection | B601, B602-B607, B609 | CWE-78 |
| Hardcoded Secrets | B105, B106, B107 | CWE-798 |
| Weak Crypto | B303, B304, B313-B320, B324 | CWE-327 |
| Insecure Deserialize | B301, B302, B506 | CWE-502 |
| SSL/TLS Issues | B501-B505, B507 | CWE-295 |
| Weak Random | B311, B321 | CWE-330 |
| Path Traversal | B310, B609 | CWE-22 |
| Error Handling | B110, B112 | CWE-703 |
| Temp File Issues | B306, B325 | CWE-377 |

## Error Handling

The scanner gracefully handles:

### Missing Tool
```
ERROR - bandit not found in PATH
INFO - Install with: pip install bandit
```

### Timeout
```
WARNING - Scan timeout after 300s (attempt 1)
INFO - Retrying in 2s...
```

### Invalid Output
```
ERROR - Failed to parse Bandit output: Invalid JSON
```

### Non-Zero Exit Codes
Bandit returns exit code 1 when issues are found. The scanner treats this as **success** and parses the results normally.

## Acceptance Criteria

✅ **Inherits from SecurityScanner** - All abstract methods implemented
✅ **Handles missing tool** - Shows install instructions
✅ **Retry logic works** - 3 attempts with exponential backoff (2s, 4s, 8s)
✅ **Timeout protection** - Terminates after 5 minutes
✅ **CWE mapping applied** - 50+ test IDs mapped
✅ **Output JSON validated** - All required fields present
✅ **Metrics emitted** - Separate file with scan statistics
✅ **Standalone execution** - `python3 bandit_scanner.py <target>`
✅ **Exit code 0** - Returns success even when issues found

## Integration with SecOps Pipeline

The Bandit scanner is the **first scanner** in the CI stage:

```
CI → CD → Runtime → Policies → Monitor
│
└─ Bandit (Python SAST) ← YOU ARE HERE
   ├─ Semgrep (Multi-language SAST)
   ├─ Gitleaks (Secret scanning)
   └─ npm audit (Dependency scanning)
```

### Run All CI Scanners

```bash
cd secops/1-scanners
python3 run_all_scanners.py
```

## Performance

- **Speed**: ~3 seconds for 50,000 LOC
- **Memory**: Low overhead (~100MB)
- **Scalability**: Linear with code size

## Troubleshooting

### Issue: `bandit: command not found`
**Solution**: Install Bandit: `pip install bandit`

### Issue: `Scan timeout after 300s`
**Solution**: Increase timeout: `--timeout 600`

### Issue: `Permission denied` on output directory
**Solution**: Ensure write permissions: `chmod +w secops/2-findings/raw/ci/`

### Issue: No findings generated
**Solution**: Check that target contains `.py` files

## Testing

### Test on Secops Itself (Dogfooding)

```bash
cd secops/1-scanners/ci
python3 bandit_scanner.py ../..

# Expected output:
# INFO - ✅ Scan completed successfully
# INFO -    Total issues: 58
# INFO -    Duration: 2.98s
```

### Validate Output

```bash
# Check findings exist
ls -la ../../2-findings/raw/ci/bandit_*.json

# Check metrics exist
ls -la ../../2-findings/raw/metrics/bandit-*.json

# View severity distribution
python3 -c "
import json
data = json.load(open('../../2-findings/raw/ci/bandit_*.json'))
print(data['metadata']['severity_breakdown'])
"
```

## Architecture

```
bandit_scanner.py
│
├─ Inherits: SecurityScanner (base_scanner.py)
│  ├─ validate_prerequisites()
│  ├─ run_scan() with retry logic
│  ├─ _emit_metrics()
│  └─ _setup_logging()
│
├─ Implements:
│  ├─ get_scanner_name() → "bandit"
│  ├─ get_tool_name() → "bandit"
│  ├─ get_install_instructions() → "pip install bandit"
│  ├─ get_output_filename() → "bandit_TIMESTAMP.json"
│  ├─ build_command() → ["bandit", "-r", ...]
│  └─ parse_results() → Enriched findings
│
└─ Custom Methods:
   ├─ _calculate_file_hash() → SHA256 tracking
   └─ BANDIT_CWE_MAP → 50+ CWE mappings
```

## Contributing

To add new CWE mappings:

1. Find the Bandit test ID (e.g., `B999`)
2. Identify the CWE (e.g., `CWE-123`)
3. Add to `BANDIT_CWE_MAP` in `bandit_scanner.py`:

```python
BANDIT_CWE_MAP = {
    'B999': ['CWE-123'],  # New security check
    # ...
}
```

## References

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [CWE Database](https://cwe.mitre.org/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [PCI-DSS Requirement 6.5](https://www.pcisecuritystandards.org/)

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-10-10
**Maintainer**: SecOps Team
