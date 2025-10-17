# Phase 2: Application Security Fixes

**Purpose:** Fix code-level vulnerabilities discovered in Phase 1 CI assessment

**When to use:** After Phase 1 CI scans identify code vulnerabilities (Bandit, Semgrep, Gitleaks)

---

## 🎯 Overview

Phase 2 addresses **CI-layer security issues** - vulnerabilities in application source code that were discovered during Phase 1 scanning. This phase provides:

1. **Automated Fixers** - Scripts that automatically remediate common vulnerability patterns
2. **Remediation Database** - Detailed fix instructions mapped to specific scanner findings
3. **Security Advisor** - Intelligent recommendations based on scan results

**Focus Areas:**

**Security Fixes:**
- Hardcoded secrets → Environment variables / secrets management
- SQL injection → Parameterized queries
- XSS vulnerabilities → Input sanitization and output encoding
- Insecure cryptography → Secure algorithms (SHA256+, AES)
- Command injection → Input validation and safe APIs
- Dependency vulnerabilities → Package updates

**Code Quality Fixes (NEW):**
- JavaScript/TypeScript linting → ESLint auto-fixes
- Python linting → Pylint/autopep8/autoflake auto-fixes
- Unused variables/imports → Automatic removal
- Code formatting → PEP 8, consistent style
- Best practices → Auto-applied where possible

---

## 📁 Directory Structure

```
2-App-Sec-Fixes/
├── fixers/                           # Automated fixers
│   ├── fix-hardcoded-secrets.sh      # CWE-798: Migrate to env vars
│   ├── fix-sql-injection.sh          # CWE-89: Parameterized queries
│   ├── fix-command-injection.sh      # CWE-78: Command injection
│   ├── fix-weak-crypto.sh            # CWE-327: Weak cryptography
│   ├── fix-weak-random.sh            # CWE-330: Weak random numbers
│   ├── fix-insecure-requests.sh      # Insecure HTTP requests
│   ├── fix-dependency-vulns.sh       # Dependency vulnerabilities
│   ├── fix-eslint-issues.sh          # ✨ NEW: JavaScript/TypeScript linting
│   └── fix-pylint-issues.sh          # ✨ NEW: Python linting
│
└── remediation/                      # Advisory tools
    ├── remediation_db.py             # Fix database (50+ patterns)
    └── security_advisor.py           # Scanner → Fix mapper
```

**Total: 11 files in 2 directories**

---

## 🔧 Automated Fixers

### 1. Hardcoded Secrets Fixer

**File:** [fixers/fix-hardcoded-secrets.sh](fixers/fix-hardcoded-secrets.sh)

**Fixes:**
- 🔴 **HIGH**: Hardcoded database credentials in source code
- 🔴 **HIGH**: API keys in configuration files
- 🔴 **HIGH**: AWS credentials embedded in code
- **Compliance**: PCI-DSS 8.2.1, CIS Benchmark 5.3

**What it does:**
1. Scans for hardcoded password patterns (excludes `process.env`, `getenv`)
2. Scans for API keys (20+ character strings)
3. Scans for AWS secrets
4. Migrates to environment variables
5. Creates `.env.example` template
6. Updates `.gitignore` to exclude `.env`

**Usage:**
```bash
cd fixers/
./fix-hardcoded-secrets.sh /path/to/project
```

**Example transformation:**
```javascript
// Before (VULNERABLE)
const config = {
  username: 'postgres',
  password: 'admin123',           // Hardcoded!
  apiKey: 'sk_live_abc123xyz'    // Exposed!
};

// After (SECURE)
const config = {
  username: process.env.DB_USERNAME || 'postgres',
  password: process.env.DB_PASSWORD,  // From .env
  apiKey: process.env.PAYMENT_API_KEY // From AWS Secrets Manager
};

// .env file created (NOT committed to git)
DB_USERNAME=postgres
DB_PASSWORD=<your-secure-password>
PAYMENT_API_KEY=<from-secrets-manager>
```

**Output:**
- Backup: `backup/secrets-TIMESTAMP/`
- Report: `GP-DATA/active/2-app-sec-fixes/ci-fixes/fix-hardcoded-secrets-TIMESTAMP.log`

**Next steps:**
1. Copy `.env.example` to `.env`
2. Fill in actual values
3. **For production**: Use AWS Secrets Manager
   ```bash
   aws secretsmanager create-secret --name securebank/prod/db \
     --secret-string '{"username":"admin","password":"..."}'
   ```

---

### 2. SQL Injection Fixer

**File:** [fixers/fix-sql-injection.sh](fixers/fix-sql-injection.sh)

**Fixes:**
- 🔴 **CRITICAL**: SQL injection via string concatenation
- 🔴 **HIGH**: Unsanitized user input in queries
- **Compliance**: PCI-DSS 6.5.1, OWASP A03:2021 (Injection)

**What it does:**
1. Scans for SQL string interpolation (JavaScript: `${var}`)
2. Scans for SQL string formatting (Python: `%s` without `?`)
3. Scans for direct query concatenation (`req.body` + SQL)
4. Creates sanitization helper module (`utils/sql-sanitizer.js`)
5. Creates safe query examples (`examples/safe-queries.js`)
6. Flags files needing manual review

**Usage:**
```bash
cd fixers/
./fix-sql-injection.sh /path/to/backend
```

**Example transformation:**
```javascript
// Before (VULNERABLE - SQL Injection!)
app.get('/user', (req, res) => {
  const userId = req.query.id;
  db.query(`SELECT * FROM users WHERE id = ${userId}`);  // DANGER!
});

// After (SECURE - Parameterized Query)
app.get('/user', (req, res) => {
  const userId = req.query.id;
  db.query('SELECT * FROM users WHERE id = $1', [userId]);  // Safe!
});
```

**Creates helper utilities:**

1. **`utils/sql-sanitizer.js`** - Input validation helpers
   ```javascript
   const { validateInteger, validateEmail, sanitizeSearchInput } = require('./utils/sql-sanitizer');

   if (!validateInteger(userId)) {
     return res.status(400).json({ error: 'Invalid user ID' });
   }
   ```

2. **`examples/safe-queries.js`** - Reference implementations
   - Parameterized queries (PostgreSQL: `$1`, MySQL: `?`)
   - LIKE query sanitization
   - Multiple parameter binding
   - UNSAFE examples (what NOT to do)

**Output:**
- Backup: `backup/sql-injection-TIMESTAMP/`
- Report: `GP-DATA/active/2-app-sec-fixes/ci-fixes/fix-sql-injection-TIMESTAMP.log`

**Supported databases:**
- PostgreSQL: `$1, $2, $3` placeholders
- MySQL: `?` placeholders
- SQLite: `?` placeholders

---

### 3. ESLint Auto-Fixer (NEW)

**File:** [fixers/fix-eslint-issues.sh](fixers/fix-eslint-issues.sh)

**Fixes:**
- ✅ **Auto-fixable (70-90%)**: Formatting, spacing, quotes, semicolons
- ✅ **Auto-fixable**: Unused variables, var → const/let conversion
- ⚠️ **Manual review**: Complex logic issues, security patterns

**What it does:**
1. Finds all JavaScript/TypeScript files
2. Creates ESLint config if missing
3. Runs ESLint with `--fix` flag
4. Auto-fixes formatting and simple issues
5. Reports remaining issues requiring manual fixes

**Usage:**
```bash
cd fixers/
./fix-eslint-issues.sh /path/to/project
```

**Example transformation:**
```javascript
// Before (ISSUES)
var userId = 123                    // Should use const
var userName = "admin";             // Extra semicolon, should use const
function test()                     // Missing space
{                                   // Brace on wrong line
console.log("Debug");               // Inconsistent quotes
}

// After (FIXED)
const userId = 123;                 // ✅ const instead of var
const userName = 'admin';           // ✅ Single quotes, proper semicolon
function test() {                   // ✅ Proper spacing and bracing
  console.log('Debug');             // ✅ Consistent quotes
}
```

**Fixes applied:**
- **Formatting**: Indentation (2 spaces), line breaks, spacing
- **Quotes**: Convert to single quotes consistently
- **Semicolons**: Add missing semicolons
- **Variables**: `var` → `const`/`let` conversion
- **Unused code**: Remove unused variables/imports
- **Best practices**: Apply ESLint recommended rules

**Output:**
- Backup: `backup/eslint-fixes-TIMESTAMP/`
- Report: `GP-DATA/active/2-app-sec-fixes/ci-fixes/fix-eslint-issues-TIMESTAMP.log`

**Next steps:**
1. Review changes: `git diff`
2. Test application: `npm test`
3. Address remaining issues manually
4. Commit: `git commit -m "fix(lint): ESLint auto-fixes"`

---

### 4. Pylint Auto-Fixer (NEW)

**File:** [fixers/fix-pylint-issues.sh](fixers/fix-pylint-issues.sh)

**Fixes:**
- ✅ **Auto-fixable (50-70%)**: PEP 8 formatting, unused imports
- ✅ **Auto-fixable**: Spacing, indentation, line length
- ⚠️ **Manual review**: Logic errors, complexity issues

**What it does:**
1. Finds all Python files
2. Creates Pylint config if missing
3. Runs `autoflake` to remove unused imports/variables
4. Runs `autopep8` to fix PEP 8 violations
5. Reports remaining issues requiring manual fixes

**Usage:**
```bash
cd fixers/
./fix-pylint-issues.sh /path/to/project
```

**Example transformation:**
```python
# Before (ISSUES)
import os                           # Unused import
import sys
from datetime import datetime       # Unused import

def calculate(x,y,z):               # Missing spaces after commas
  result=x+y+z                      # Missing spaces around operators
  temp = 123                        # Unused variable
  return result

# After (FIXED)
import sys                          # ✅ Unused import removed

def calculate(x, y, z):             # ✅ Proper spacing
    result = x + y + z              # ✅ Spaces around operators, proper indent
    return result                   # ✅ Unused variable removed
```

**Fixes applied:**
- **PEP 8 formatting**: Indentation (4 spaces), line length (max 120)
- **Unused code**: Remove unused imports and variables
- **Spacing**: Proper spacing around operators and commas
- **Line breaks**: Normalize line breaks and blank lines
- **Duplicate keys**: Remove duplicate dictionary keys

**Tools used:**
- `autopep8`: PEP 8 auto-formatter
- `autoflake`: Unused import/variable remover
- `pylint`: Code quality checker

**Output:**
- Backup: `backup/pylint-fixes-TIMESTAMP/`
- Report: `GP-DATA/active/2-app-sec-fixes/ci-fixes/fix-pylint-issues-TIMESTAMP.log`

**Next steps:**
1. Review changes: `git diff`
2. Test application: `pytest`
3. Address remaining issues manually
4. Commit: `git commit -m "fix(lint): Pylint auto-fixes"`

---

## 📚 Remediation Database

**File:** [remediation/remediation_db.py](remediation/remediation_db.py)

**Purpose:** Maps scanner findings to detailed fix instructions

**Coverage:**

| Scanner | Patterns | Example Issues |
|---------|----------|----------------|
| **Bandit** | 4+ rules | B105 (hardcoded password), B113 (no timeout), B108 (insecure temp file) |
| **Semgrep** | 2+ rules | SQL injection, XSS in Django |
| **Gitleaks** | 2+ patterns | AWS keys, generic API keys |
| **Checkov** | 2+ checks | S3 encryption, IMDSv2 |
| **Trivy** | 2+ CVEs | Log4Shell (CVE-2021-44228), container root user |

**Usage:**
```python
from remediation.remediation_db import RemediationDB

db = RemediationDB()

# Get fix for specific Bandit finding
fix = db.get_fix("bandit", "B105")
print(f"Issue: {fix['issue']}")
print(f"Risk: {fix['risk']}")
print(f"Fix:\n{fix['fix']}")
print(f"References: {fix['references']}")

# Get all fixes for a scanner
all_bandit_fixes = db.get_all_fixes_for_scanner("bandit")
```

**Example fix entry:**
```python
"B105": {
    "issue": "Hardcoded password",
    "risk": "Credentials exposed in source code",
    "severity": "high",
    "fix": """
Use environment variables or secrets management:

# Bad:
password = "admin123"

# Good:
import os
password = os.environ.get('DB_PASSWORD')

# Better (with fallback):
from dotenv import load_dotenv
load_dotenv()
password = os.environ.get('DB_PASSWORD')
if not password:
    raise ValueError("DB_PASSWORD not set")
""",
    "references": ["https://12factor.net/config"]
}
```

**Supported vulnerability types:**
- **CWE-798**: Hardcoded credentials
- **CWE-89**: SQL injection
- **CWE-79**: Cross-site scripting (XSS)
- **CWE-327**: Weak cryptography (MD5, SHA1)
- **CWE-330**: Weak random number generation
- **CWE-78**: Command injection
- And 20+ more patterns...

---

## 🤖 Security Advisor

**File:** [remediation/security_advisor.py](remediation/security_advisor.py)

**Purpose:** Analyzes scan results and provides actionable remediation advice

**Features:**
- Loads Phase 1 scan results from `GP-DATA/active/1-sec-assessment/`
- Maps findings to remediation database
- Generates prioritized fix recommendations
- Exports comprehensive security advice reports

**Usage:**

```bash
# Analyze specific scan file
python3 remediation/security_advisor.py

# Or import programmatically
from remediation.security_advisor import SecurityAdvisor

advisor = SecurityAdvisor()

# Get advice for specific project
advice = advisor.provide_advice_for_project("/path/to/project")

print(f"Total Issues: {advice['summary']['total_issues']}")
print(f"Critical: {advice['summary']['critical']}")
print(f"High: {advice['summary']['high']}")
```

**Supported scanners:**
- ✅ Bandit (Python SAST)
- ✅ Semgrep (Multi-language SAST)
- ✅ Gitleaks (Secrets detection)
- ✅ Checkov (IaC security)
- ✅ Trivy (Container/dependency scanning)

**Output format:**
```json
{
  "project": "/path/to/project",
  "timestamp": "2025-10-14T15:30:00",
  "scanners": {
    "bandit": {
      "recommendations": [
        {
          "file": "backend/api/auth.py",
          "line": 42,
          "issue_id": "B105",
          "severity": "HIGH",
          "issue": "Hardcoded password string",
          "risk": "Credentials exposed in source code",
          "fix": "Use environment variables...",
          "references": ["https://12factor.net/config"]
        }
      ]
    }
  },
  "summary": {
    "total_issues": 15,
    "critical": 3,
    "high": 7,
    "medium": 4,
    "low": 1
  }
}
```

**Report location:**
`GP-DATA/active/2-app-sec-fixes/security_advice_TIMESTAMP.json`

---

## 🔄 Complete Phase 2 Workflow

### Step 1: Review Phase 1 CI Findings

```bash
# Check what vulnerabilities were found
ls -lh ~/linkops-industries/GP-copilot/GP-DATA/active/1-sec-assessment/ci-findings/

# Review specific scanner results
cat GP-DATA/active/1-sec-assessment/ci-findings/bandit_*.json | jq '.summary.severity_breakdown'
cat GP-DATA/active/1-sec-assessment/ci-findings/gitleaks_*.json | jq '.findings | length'
```

### Step 2: Get Remediation Advice

```bash
cd 2-App-Sec-Fixes/remediation/
python3 security_advisor.py

# Review recommendations
cat ~/linkops-industries/GP-copilot/GP-DATA/active/2-app-sec-fixes/security_advice_*.json
```

### Step 3: Apply Automated Fixes

```bash
cd ../fixers/

# Security fixes
./fix-hardcoded-secrets.sh /path/to/project
./fix-sql-injection.sh /path/to/project

# Code quality fixes (linting - NEW)
./fix-eslint-issues.sh /path/to/project
./fix-pylint-issues.sh /path/to/project
```

### Step 4: Manual Remediation

For issues requiring manual fixes:

1. **Review remediation database**
   ```python
   from remediation.remediation_db import RemediationDB
   db = RemediationDB()
   fix = db.get_fix("bandit", "B113")  # Request without timeout
   print(fix['fix'])
   ```

2. **Apply recommended fixes**
3. **Test thoroughly**

### Step 5: Validate Fixes

Re-run Phase 1 CI scanners to verify fixes:

```bash
cd ../../1-Security-Assessment/ci-scanners/

# Re-scan with same scanners
python3 bandit_scanner.py --target /path/to/project
python3 semgrep_scanner.py --target /path/to/project
python3 gitleaks_scanner.py --target /path/to/project

# Compare before/after
diff GP-DATA/active/1-sec-assessment/ci-findings/bandit_BEFORE.json \
     GP-DATA/active/1-sec-assessment/ci-findings/bandit_AFTER.json
```

### Step 6: Generate Fix Report

```bash
# Compare findings count
echo "Before fixes:"
jq '.summary.severity_breakdown' GP-DATA/active/1-sec-assessment/ci-findings/bandit_BEFORE.json

echo "After fixes:"
jq '.summary.severity_breakdown' GP-DATA/active/1-sec-assessment/ci-findings/bandit_AFTER.json
```

---

## 🔗 Integration with Other Phases

### ← From Phase 1: Security Assessment

**Input:** CI scan results
```
GP-DATA/active/1-sec-assessment/ci-findings/
├── bandit_TIMESTAMP.json      # Python vulnerabilities
├── semgrep_TIMESTAMP.json     # Multi-language issues
└── gitleaks_TIMESTAMP.json    # Hardcoded secrets
```

**Trigger:** High/Critical findings in code-level scans

---

### → To Phase 3: Hardening

After fixing code vulnerabilities, proceed to infrastructure hardening:

```bash
cd ../3-Hardening/

# Apply infrastructure fixes
./fixers/fix-kubernetes-security.sh
./fixers/fix-rds-encryption.sh
```

---

### → To Phase 5: Compliance-Audit

Track remediation progress for compliance:

```bash
cd ../5-Compliance-Audit/validators/

# Generate before/after comparison
python3 compare-results.py \
  --before GP-DATA/active/1-sec-assessment/ci-findings/ \
  --after GP-DATA/active/1-sec-assessment/ci-findings-after-fixes/
```

---

## 📊 Metrics and Reporting

### Effectiveness Metrics

**Vulnerability Reduction Rate:**
```
(Findings Before - Findings After) / Findings Before × 100
```

Example:
```bash
# Before: 45 HIGH vulnerabilities
# After: 3 HIGH vulnerabilities
# Reduction: (45 - 3) / 45 × 100 = 93.3% reduction
```

**Time to Remediate:**
```
Time from vulnerability discovery → Fix deployed to production
```

**Regression Rate:**
```
Fixed issues that reappear / Total fixed issues × 100
```

### Generate Compliance Report

```bash
cd ../5-Compliance-Audit/validators/
./generate-compliance-report.sh --framework pci-dss --phase 2

# Outputs:
# - PCI-DSS 6.5.1 (Injection flaws): PASS
# - PCI-DSS 8.2.1 (Hardcoded credentials): PASS
```

---

## 🎯 Best Practices

### 1. Prioritize by Severity

**Fix order:**
1. 🔴 **CRITICAL** (secrets, RCE) - Immediate action
2. 🔴 **HIGH** (SQL injection, XSS) - Within 24 hours
3. 🟠 **MEDIUM** (weak crypto, no timeout) - Within 1 week
4. 🟡 **LOW** (assert usage) - Next sprint

### 2. Test Thoroughly

```bash
# After applying fixes, run:
1. Unit tests
2. Integration tests
3. Security re-scan
4. Manual code review
```

### 3. Commit Fixes Separately

```bash
# One commit per vulnerability type
git commit -m "fix(security): Remove hardcoded credentials (CWE-798)"
git commit -m "fix(security): Use parameterized queries (CWE-89)"
```

### 4. Document False Positives

If a finding is a false positive, document it:

```python
# .bandit
[bandit]
exclude: /test/

# Suppress specific finding
password = "default_for_testing"  # nosec B105 - Test fixture only
```

### 5. Automate in CI/CD

```yaml
# .github/workflows/security-fixes.yml
name: Security Fixes

on: [push]

jobs:
  fix-and-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Apply Security Fixes
        run: |
          cd GP-CONSULTING/2-App-Sec-Fixes/fixers/
          ./fix-hardcoded-secrets.sh .
          ./fix-sql-injection.sh .

      - name: Validate Fixes
        run: |
          cd GP-CONSULTING/1-Security-Assessment/ci-scanners/
          python3 bandit_scanner.py --target .

      - name: Fail if vulnerabilities remain
        run: |
          HIGH_COUNT=$(jq '.summary.severity_breakdown.HIGH' GP-DATA/active/1-sec-assessment/ci-findings/bandit_*.json)
          if [ "$HIGH_COUNT" -gt 0 ]; then
            echo "❌ $HIGH_COUNT HIGH vulnerabilities remain!"
            exit 1
          fi
```

---

## 🛠️ Troubleshooting

### Fixer Script Errors

**Problem:** `fix-hardcoded-secrets.sh` doesn't find backend directory

**Solution:**
```bash
# Script auto-detects project root by searching for backend/
# If your structure is different, set PROJECT_ROOT manually:
export PROJECT_ROOT=/path/to/project
./fix-hardcoded-secrets.sh
```

---

### Python Import Errors

**Problem:** `ModuleNotFoundError: No module named 'remediation'`

**Solution:**
```bash
# Run from GP-CONSULTING directory
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING
python3 2-App-Sec-Fixes/remediation/security_advisor.py

# Or add to PYTHONPATH
export PYTHONPATH=/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING:$PYTHONPATH
```

---

### Secrets Still in Git History

**Problem:** Secrets removed from code but still in git history

**Solution:**
```bash
# Use git filter-branch to remove from history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/file-with-secret' \
  --prune-empty --tag-name-filter cat -- --all

# Force push (⚠️ Coordinate with team!)
git push origin --force --all

# Or use BFG Repo-Cleaner (faster)
bfg --delete-files config/secrets.json
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

---

### Parameterized Queries Not Working

**Problem:** Syntax errors after applying SQL injection fix

**Solution:**
```javascript
// Check placeholder syntax for your database:

// PostgreSQL
db.query('SELECT * FROM users WHERE id = $1', [userId]);

// MySQL/SQLite
db.query('SELECT * FROM users WHERE id = ?', [userId]);

// Multiple parameters
// PostgreSQL
db.query('INSERT INTO users (name, email) VALUES ($1, $2)', [name, email]);

// MySQL
db.query('INSERT INTO users (name, email) VALUES (?, ?)', [name, email]);
```

---

## 📖 Additional Resources

- **[Remediation Database](remediation/remediation_db.py)** - 50+ fix patterns
- **[Security Advisor](remediation/security_advisor.py)** - Automated recommendations
- **[Hardcoded Secrets Fixer](fixers/fix-hardcoded-secrets.sh)** - CWE-798 remediation
- **[SQL Injection Fixer](fixers/fix-sql-injection.sh)** - CWE-89 remediation

**External References:**
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [PCI-DSS 6.5 Requirements](https://www.pcisecuritystandards.org/)
- [12-Factor App Config](https://12factor.net/config)

---

## 🔄 Next Phase

Once code-level vulnerabilities are remediated:

**→ [Phase 3: Hardening](../3-Hardening/README.md)** - Secure infrastructure configurations and apply runtime enforcement

**→ [Phase 5: Compliance-Audit](../5-Compliance-Audit/README.md)** - Generate compliance reports and track remediation progress

---

**Phase 2 Version:** 2.0 (Clean)
**Last Updated:** 2025-10-14
**Files:** 5 (2 fixers + 2 advisory tools + README)
**Empty Directories Removed:** 3 (docs, reports, validation)
**Status:** ✅ Production-Ready
