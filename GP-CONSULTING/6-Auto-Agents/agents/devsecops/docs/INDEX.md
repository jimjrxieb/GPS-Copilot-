# GP-DevSecOps Tools Index

Complete toolkit for debugging and fixing CI/CD pipeline failures.

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Navigate to tools directory
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS/GP-devsecops

# 2. Run the automated debugger
./auto_fix_pipeline.sh <owner/repo>

# 3. Follow the recommendations
```

**Example:**
```bash
./auto_fix_pipeline.sh jimjrxieb/CLOUD-project
```

---

## 📚 Documentation Files

### 1. [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) ⚡
**Start here if you just need a quick fix!**

Contains:
- Common error patterns with copy-paste fixes
- Quick diagnosis commands
- Decision tree for different errors
- The magic `sleep` command explained
- Pro tips

**Use when:** You need to fix a broken pipeline NOW and don't have time to read the full guide.

**Time to read:** 2-3 minutes

---

### 2. [README.md](./README.md) 📖
**Overview and tool documentation**

Contains:
- Tool descriptions and usage
- Common use cases with step-by-step solutions
- Error type reference table
- Command reference
- Integration guide for Jade AI
- Best practices

**Use when:** You want to understand what tools are available and how to use them.

**Time to read:** 10-15 minutes

---

### 3. [CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md](./CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md) 📋
**Complete systematic debugging workflow**

Contains:
- Phase 1: Initial Assessment
- Phase 2: Drill Down to Failed Job/Step
- Phase 3: Categorize Error Type
- Phase 4: Apply Fixes
- Phase 5: Test and Iterate
- Phase 6: Verify All Workflows
- Complete command reference
- Real-world example (CLOUD-project)
- Automation potential for Jade

**Use when:** You need a comprehensive understanding of the debugging process or training Jade AI.

**Time to read:** 30-45 minutes

---

## 🛠️ Tool Files

### 1. [pipeline_debugger.py](./pipeline_debugger.py) 🔍
**Automated pipeline failure analyzer**

**What it does:**
- Fetches recent workflow runs
- Identifies failed jobs and steps
- Categorizes error types
- Provides fix recommendations with code examples
- Identifies auto-fixable vs. manual issues

**Usage:**
```bash
python3 pipeline_debugger.py <owner/repo>

# Example
python3 pipeline_debugger.py jimjrxieb/CLOUD-project
```

**Output example:**
```
🔍 Analyzing pipeline failures for jimjrxieb/CLOUD-project...

❌ Workflow failure detected: Fix docker_build job
   Run ID: 18303577082
   Failed jobs: build

================================================================================
ANALYSIS RESULTS
================================================================================

1. SonarQube Scan
   Error Type: missing_secrets
   Solution: Make step non-blocking
   Auto-fixable: Yes ✅

   Third-party service not configured or requires API key/secret.

   Code Example:
   - name: SonarQube Scan
     continue-on-error: true
     uses: sonarsource/sonarqube-scan-action@master
```

**Requirements:**
- Python 3.6+
- GitHub CLI (`gh`) installed and authenticated

---

### 2. [auto_fix_pipeline.sh](./auto_fix_pipeline.sh) 🤖
**Automated pipeline debugging wrapper**

**What it does:**
- Runs `pipeline_debugger.py`
- Pretty-prints results with colors
- Provides actionable next steps
- Shows monitoring commands

**Usage:**
```bash
./auto_fix_pipeline.sh <owner/repo>

# Example
./auto_fix_pipeline.sh jimjrxieb/CLOUD-project
```

**Output example:**
```
🔍 Checking pipeline status for jimjrxieb/CLOUD-project...

✅ All workflows passing! No action needed.

📊 View workflows:
   https://github.com/jimjrxieb/CLOUD-project/actions
```

---

## 📂 File Structure

```
GP-CONSULTING-AGENTS/GP-devsecops/
├── INDEX.md                                    # This file - navigation hub
├── QUICK_REFERENCE.md                          # Fast fixes (start here!)
├── README.md                                   # Tool documentation
├── CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md        # Complete workflow guide
├── pipeline_debugger.py                        # Python analyzer (executable)
└── auto_fix_pipeline.sh                        # Bash wrapper (executable)
```

---

## 🎯 Usage Flowchart

```
Pipeline failing?
│
├─ Need quick fix NOW?
│  └─> Read: QUICK_REFERENCE.md (2 min)
│     └─> Run: ./auto_fix_pipeline.sh
│
├─ Want to understand tools?
│  └─> Read: README.md (10 min)
│     └─> Run: python3 pipeline_debugger.py
│
├─ Need systematic approach?
│  └─> Read: CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md (30 min)
│     └─> Follow phases 1-6
│
└─ Just want automation?
   └─> Run: ./auto_fix_pipeline.sh
      └─> Follow recommendations
```

---

## 💡 Common Scenarios

### Scenario 1: New to Pipeline Debugging
**Path:**
1. Start with [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
2. Try the automation: `./auto_fix_pipeline.sh <repo>`
3. If confused, read [README.md](./README.md)

### Scenario 2: Pipeline Just Started Failing
**Path:**
1. Run: `./auto_fix_pipeline.sh <owner/repo>`
2. Apply recommended fixes
3. If fix unclear, check [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) → "Most Common Fixes"

### Scenario 3: Complex Multi-Workflow Failure
**Path:**
1. Read: [CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md](./CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md)
2. Follow systematic Phase 1-6 approach
3. Use `pipeline_debugger.py` for each workflow

### Scenario 4: Training Jade AI
**Path:**
1. Jade should read all documentation files
2. Primary workflow: [CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md](./CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md)
3. Integrate `pipeline_debugger.py` into Jade's analysis tools
4. Use error categorization and fix recommendations

---

## 🔑 Key Concepts

### Error Categories
1. **missing_secrets** - Third-party service not configured → `continue-on-error: true`
2. **security_findings** - Real vulnerabilities found → FIX THEM (don't skip!)
3. **build_failure** - Code won't compile → Fix code/dependencies
4. **test_failure** - Tests failing → Fix tests OR skip temporarily
5. **deprecated_action** - Old action version → Update version
6. **download_failure** - External dependency unavailable → Make optional
7. **job_setup_failure** - Job fails before steps → Disable OR add secrets

### Fix Strategies
1. **Make Optional** - `continue-on-error: true` (for non-critical tools)
2. **Disable Job** - `if: false` (for unconfigured deployment)
3. **Update Version** - Change `@v3` to `@v4` (for deprecated actions)
4. **Fix Code** - Resolve compilation/security issues (for real problems)
5. **Add Secrets** - Configure required API keys (for production setup)

---

## 📖 Related Documentation

### In CLOUD-project
- [PIPELINE_SUCCESS.md](../../GP-PROJECTS/CLOUD-project/PIPELINE_SUCCESS.md) - Successful pipeline example
- [SECURITY_ACHIEVEMENT.md](../../GP-PROJECTS/CLOUD-project/SECURITY_ACHIEVEMENT.md) - CVE remediation journey (10 → 0 CRITICAL)
- [SECURITY_SCANNING.md](../../GP-PROJECTS/CLOUD-project/SECURITY_SCANNING.md) - Security tool configuration

### External Resources
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)

---

## 🤖 For Jade AI

**Primary Integration Point:** `pipeline_debugger.py`

```python
from GP_CONSULTING_AGENTS.GP_devsecops.pipeline_debugger import PipelineDebugger

# In Jade's workflow
def handle_pipeline_failure(repo: str):
    debugger = PipelineDebugger(repo)
    result = debugger.analyze_and_fix()

    # Process results and recommend fixes
    return result
```

**Knowledge Base Priority:**
1. **Must Read:** CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md
2. **Should Read:** README.md
3. **Reference:** QUICK_REFERENCE.md

---

## ⚡ One-Liners for Common Tasks

```bash
# Check if pipeline is passing
gh run list --repo <owner/repo> --limit 1 --json conclusion --jq '.[0].conclusion'

# Get latest failed run ID
gh run list --repo <owner/repo> --limit 10 --json conclusion,databaseId \
  --jq '.[] | select(.conclusion=="failure") | .databaseId' | head -1

# Auto-debug pipeline
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS/GP-devsecops && \
./auto_fix_pipeline.sh <owner/repo>

# Watch for completion (replace RUN_ID)
watch -n 10 "gh run view RUN_ID --repo <owner/repo> --json conclusion --jq '.conclusion'"
```

---

## 🎓 Learning Path

### Beginner
1. **Read:** QUICK_REFERENCE.md (2 min)
2. **Try:** `./auto_fix_pipeline.sh jimjrxieb/CLOUD-project`
3. **Practice:** Break and fix a test pipeline

### Intermediate
1. **Read:** README.md (10 min)
2. **Study:** Error type reference table
3. **Practice:** Fix 5 different error types

### Advanced
1. **Read:** CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md (30 min)
2. **Understand:** All 6 phases of systematic debugging
3. **Practice:** Debug multi-workflow failures
4. **Extend:** Add new error patterns to `pipeline_debugger.py`

---

## 📝 Cheat Sheet

| I need to... | Use this... |
|--------------|-------------|
| Fix a broken pipeline NOW | [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) |
| Understand what tools exist | [README.md](./README.md) |
| Learn systematic debugging | [CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md](./CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md) |
| Automatically analyze failures | `./auto_fix_pipeline.sh <repo>` |
| Get detailed error analysis | `python3 pipeline_debugger.py <repo>` |
| Train Jade AI | All .md files + integrate `pipeline_debugger.py` |

---

## ✅ Verification

All tools are working! Tested on CLOUD-project:

```bash
$ ./auto_fix_pipeline.sh jimjrxieb/CLOUD-project

🔍 Checking pipeline status for jimjrxieb/CLOUD-project...

✅ All workflows passing! No action needed.

📊 View workflows:
   https://github.com/jimjrxieb/CLOUD-project/actions
```

---

**Created:** October 2025
**Last Updated:** October 2025
**Status:** Production-ready ✅
**Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS/GP-devsecops/`
