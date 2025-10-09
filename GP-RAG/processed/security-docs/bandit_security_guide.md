# Bandit Python Security Analysis Tool

## Overview
Bandit is a security linter specifically designed for Python code. It analyzes Python source code for common security issues.

## Key Security Checks

### B101: assert_used
- **Risk**: Medium
- **Description**: Use of assert detected. Assert statements are removed when Python is optimized.
- **Fix**: Replace assert with proper error handling

### B102: exec_used
- **Risk**: High
- **Description**: Use of exec detected
- **Fix**: Avoid exec() or validate input thoroughly

### B103: set_bad_file_permissions
- **Risk**: High
- **Description**: chmod setting a permissive mask
- **Fix**: Use restrictive file permissions (0o600, 0o644)

### B105: hardcoded_password_string
- **Risk**: Medium
- **Description**: Possible hardcoded password
- **Fix**: Use environment variables or secure credential storage

### B106: hardcoded_password_funcarg
- **Risk**: Medium
- **Description**: Possible hardcoded password in function arguments
- **Fix**: Pass passwords securely, not as literals

### B108: hardcoded_tmp_directory
- **Risk**: Medium
- **Description**: Probable insecure usage of temp file/directory
- **Fix**: Use tempfile module with secure defaults

### B110: try_except_pass
- **Risk**: Low
- **Description**: Try, Except, Pass detected
- **Fix**: Handle exceptions properly, log errors

### B201: flask_debug_true
- **Risk**: High
- **Description**: Flask app appears to run with debug=True
- **Fix**: Never run Flask in debug mode in production

### B301: pickle_usage
- **Risk**: Medium
- **Description**: Pickle and modules that wrap it can be unsafe
- **Fix**: Use JSON or other safe serialization formats

### B501: request_with_no_cert_validation
- **Risk**: High
- **Description**: Requests call with verify=False disabling SSL certificate checks
- **Fix**: Always verify SSL certificates

### B506: yaml_load
- **Risk**: Medium
- **Description**: Use of yaml.load() can execute arbitrary code
- **Fix**: Use yaml.safe_load() instead

## Common Remediation Patterns

### Secure File Operations
```python
# Bad
os.chmod('/tmp/file', 0o777)

# Good
os.chmod('/tmp/file', 0o600)
```

### Secure Password Handling
```python
# Bad
password = "hardcoded_password"

# Good
password = os.environ.get('PASSWORD')
```

### Secure HTTPS Requests
```python
# Bad
requests.get(url, verify=False)

# Good
requests.get(url, verify=True)
```

## Integration with GP-Copilot

When Bandit findings are detected, Jade should:
1. Identify the security pattern violated
2. Reference this knowledge base for remediation
3. Apply automated fixes where safe
4. Escalate complex issues requiring manual review

## Compliance Mapping

- **CIS Python Secure Coding**: Covers secure coding practices
- **OWASP Top 10**: Addresses injection flaws, broken authentication
- **SOC2**: Supports logical access controls (CC6.1)