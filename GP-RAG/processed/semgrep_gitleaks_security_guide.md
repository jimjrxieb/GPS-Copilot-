# Semgrep and GitLeaks Security Analysis Guide

## Semgrep - Static Application Security Testing (SAST)

### Overview
Semgrep is a fast, lightweight static analysis tool that finds bugs, security vulnerabilities, and enforces coding standards across 20+ programming languages. It uses pattern-based rules written in a simple syntax that mirrors the target language.

### Core Capabilities
- **Multi-Language Support**: Python, Java, JavaScript, TypeScript, Go, C/C++, Ruby, PHP, Scala, Kotlin, Swift, Rust, Bash, Docker, YAML, JSON
- **Pattern Matching**: Semantic code search beyond simple regex
- **Custom Rules**: Write organization-specific security patterns
- **CI/CD Integration**: Automated scanning in pipelines
- **Supply Chain Security**: Dependency vulnerability detection

### Common Security Rules and Patterns

#### Python Security Patterns
```python
# Rule: Detect SQL injection vulnerabilities
pattern: |
  cursor.execute($QUERY + $VAR)
message: "Possible SQL injection. Use parameterized queries."
severity: ERROR
languages: [python]

# Rule: Hardcoded secrets
pattern: |
  password = "..."
message: "Hardcoded password detected"
severity: WARNING
```

#### JavaScript/Node.js Security Patterns
```javascript
// Rule: eval() usage
pattern: eval($X)
message: "eval() is dangerous and can lead to code injection"
severity: ERROR

// Rule: Insecure random number generation
pattern: Math.random()
message: "Math.random() is not cryptographically secure. Use crypto.randomBytes()"
severity: WARNING

// Rule: Command injection
pattern: |
  child_process.exec($CMD + $INPUT)
message: "Possible command injection. Validate/sanitize input."
severity: ERROR
```

#### Go Security Patterns
```go
// Rule: Weak cryptographic hash
pattern: |
  md5.New()
message: "MD5 is cryptographically broken. Use SHA-256 or higher."
severity: WARNING

// Rule: SQL injection in Go
pattern: |
  db.Query("SELECT * FROM users WHERE id = " + $ID)
message: "SQL injection vulnerability. Use prepared statements."
severity: ERROR
```

#### Java Security Patterns
```java
// Rule: Insecure deserialization
pattern: |
  ObjectInputStream.readObject()
message: "Unsafe deserialization can lead to RCE. Validate input."
severity: ERROR

// Rule: Path traversal
pattern: |
  new File($PATH)
message: "Potential path traversal. Validate file paths."
severity: WARNING
```

### OWASP Top 10 Coverage
1. **Injection**: SQL, NoSQL, LDAP, OS command injection patterns
2. **Broken Authentication**: Weak session management, hardcoded credentials
3. **Sensitive Data Exposure**: Unencrypted data storage, weak crypto
4. **XML External Entities (XXE)**: Unsafe XML parsing
5. **Broken Access Control**: Missing authorization checks
6. **Security Misconfiguration**: Default passwords, verbose errors
7. **Cross-Site Scripting (XSS)**: Unescaped output, DOM manipulation
8. **Insecure Deserialization**: Unsafe object instantiation
9. **Known Vulnerabilities**: Outdated dependencies
10. **Insufficient Logging**: Missing security event logging

### Custom Rule Creation
```yaml
# Custom rule for API key exposure
rules:
  - id: hardcoded-api-key
    pattern: |
      api_key = "sk-..."
    message: "OpenAI API key hardcoded in source"
    severity: ERROR
    languages: [python, javascript, java]
    metadata:
      cwe: "CWE-798: Use of Hard-coded Credentials"
      owasp: "A2: Broken Authentication"
```

### CI/CD Integration
```yaml
# GitHub Actions
- name: Semgrep Scan
  run: |
    python -m pip install semgrep
    semgrep --config=auto --sarif -o semgrep.sarif

# GitLab CI
semgrep:
  image: returntocorp/semgrep:latest
  script:
    - semgrep --config=auto --json --output=semgrep.json
  artifacts:
    reports:
      sast: semgrep.json
```

## GitLeaks - Secret Detection and Prevention

### Overview
GitLeaks is a secret scanner that detects passwords, API keys, tokens, and other sensitive information in Git repositories, including commit history. It prevents secrets from reaching production by scanning in CI/CD pipelines.

### Core Capabilities
- **Git History Scanning**: Analyze entire repository history
- **Pre-commit Hooks**: Prevent secrets from being committed
- **CI/CD Integration**: Automated pipeline scanning
- **Custom Rules**: Organization-specific secret patterns
- **Allowlisting**: Manage false positives
- **Multiple Output Formats**: JSON, SARIF, CSV

### Common Secret Patterns Detected

#### API Keys and Tokens
```regex
# AWS Access Keys
aws_access_key_id = AKIA[0-9A-Z]{16}
aws_secret_access_key = [0-9a-zA-Z/+]{40}

# GitHub Personal Access Tokens
ghp_[0-9a-zA-Z]{36}
gho_[0-9a-zA-Z]{36}
ghu_[0-9a-zA-Z]{36}

# Slack Tokens
xoxb-[0-9]{11}-[0-9]{11}-[0-9a-zA-Z]{24}
xoxp-[0-9]{11}-[0-9]{11}-[0-9a-zA-Z]{24}

# Google API Keys
AIza[0-9A-Za-z\\-_]{35}

# JWT Tokens
ey[A-Za-z0-9_-]*\.ey[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*

# Database Connection Strings
mongodb://[^:]+:[^@]+@[^/]+/
postgresql://[^:]+:[^@]+@[^/]+/
mysql://[^:]+:[^@]+@[^/]+/
```

#### Cryptographic Keys
```regex
# RSA Private Keys
-----BEGIN RSA PRIVATE KEY-----
-----BEGIN OPENSSH PRIVATE KEY-----
-----BEGIN PGP PRIVATE KEY BLOCK-----

# DSA Private Keys
-----BEGIN DSA PRIVATE KEY-----

# EC Private Keys
-----BEGIN EC PRIVATE KEY-----
```

#### Configuration Files
```bash
# .env files
DATABASE_PASSWORD=secretpassword123
REDIS_PASSWORD=anothersecret
JWT_SECRET=supersecretjwtkey

# Docker environment
-e MYSQL_ROOT_PASSWORD=rootpass
--env PASSWORD=mysecret

# Kubernetes secrets (base64 encoded)
data:
  password: c2VjcmV0cGFzc3dvcmQ=  # secretpassword
```

### GitLeaks Configuration
```toml
# .gitleaks.toml
[extend]
useDefault = true

[[rules]]
id = "custom-api-key"
description = "Custom API Key Pattern"
regex = '''custom-api-[a-zA-Z0-9]{32}'''
keywords = ["custom-api"]

[[rules]]
id = "internal-token"
description = "Internal Service Token"
regex = '''int_[a-zA-Z0-9]{24}'''
keywords = ["int_"]

[allowlist]
description = "Allowlist for false positives"
commits = ["commit-hash-to-ignore"]
paths = [
  '''tests/fixtures/.*''',
  '''docs/examples/.*''',
]
regexes = [
  '''password.*=.*test''',
  '''key.*=.*dummy''',
]
```

### Integration Patterns

#### Pre-commit Hook
```bash
# Install pre-commit hook
echo '#!/bin/sh\ngitleaks detect --verbose --redact --source="." || exit 1' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

#### CI/CD Pipeline
```yaml
# GitHub Actions
- name: GitLeaks Scan
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}

# Jenkins Pipeline
stage('Secret Scan') {
  steps {
    sh 'gitleaks detect --source=. --verbose --report-format=json --report-path=gitleaks.json'
    archiveArtifacts artifacts: 'gitleaks.json'
  }
}
```

#### Docker Integration
```dockerfile
# Multi-stage build with secret scanning
FROM ghcr.io/gitleaks/gitleaks:latest as secret-scanner
COPY . /scan
WORKDIR /scan
RUN gitleaks detect --source=. --verbose || exit 1

FROM node:16-alpine as app
COPY --from=secret-scanner /scan /app
```

### Remediation Strategies

#### Immediate Actions
1. **Rotate Compromised Credentials**: Change passwords, regenerate API keys
2. **Revoke Access**: Disable compromised accounts/tokens
3. **Audit Usage**: Check logs for unauthorized access
4. **Git History Cleanup**: Use git-filter-repo or BFG to remove secrets

#### Prevention Measures
1. **Environment Variables**: Store secrets in env vars, not code
2. **Secret Management**: Use Vault, AWS Secrets Manager, Azure Key Vault
3. **CI/CD Integration**: Block commits containing secrets
4. **Developer Training**: Educate on secure coding practices
5. **Regular Scanning**: Schedule periodic repository scans

#### Git History Cleanup
```bash
# Remove secret from Git history
git filter-repo --invert-paths --path-regex 'config/secrets\.py'

# Remove specific string from history
git filter-repo --replace-text <(echo 'sk-1234567890abcdef==>REDACTED')

# Use BFG Repo-Cleaner
java -jar bfg.jar --replace-text passwords.txt my-repo.git
```

## GP-Copilot Integration Patterns

### Semgrep Integration
When Semgrep findings are detected, Jade should:

1. **Vulnerability Classification**:
   - **ERROR**: Immediate fix required, block deployment
   - **WARNING**: Schedule remediation, continue with monitoring
   - **INFO**: Code quality improvement, include in backlog

2. **Language-Specific Guidance**:
   - **Python**: Recommend secure alternatives (parameterized queries, secrets management)
   - **JavaScript**: Provide secure coding patterns (input validation, XSS prevention)
   - **Java**: Suggest secure frameworks and libraries
   - **Go**: Recommend crypto/secure packages

3. **OWASP Mapping**:
   - Map findings to OWASP Top 10 categories
   - Provide remediation based on vulnerability class
   - Generate compliance reports for security audits

### GitLeaks Integration
When secrets are detected, Jade should:

1. **Immediate Response**:
   - **API Keys/Tokens**: Generate rotation procedures
   - **Database Credentials**: Provide secure configuration examples
   - **Cryptographic Keys**: Recommend key management solutions

2. **Impact Assessment**:
   - Analyze potential blast radius of exposed secrets
   - Check for related resources that might be compromised
   - Recommend monitoring and audit procedures

3. **Remediation Automation**:
   - Generate secure environment variable configurations
   - Provide secret management integration code
   - Create cleanup scripts for Git history

### Cross-Tool Correlation
Jade should correlate findings between tools:
- **Semgrep + GitLeaks**: If code has both hardcoded secrets AND injection vulnerabilities
- **Trivy + Semgrep**: Container vulnerabilities + application code issues
- **Checkov + GitLeaks**: Infrastructure misconfigurations + exposed credentials

### Escalation Criteria
- **Critical**: Exposed production credentials, RCE vulnerabilities
- **High**: Authentication bypasses, sensitive data exposure
- **Medium**: Injection vulnerabilities, weak cryptography
- **Low**: Code quality issues, informational findings

This comprehensive knowledge enables Jade to provide expert-level guidance on application security scanning, secret management, and secure coding practices.