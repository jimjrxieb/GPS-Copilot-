# 💬 Jade Chat Mode - Natural Language Interface

**TL;DR:** Talk to Jade like you're talking to Claude Code!

```bash
jade chat
> "I want to scan my project quickly"
🤖 Jade: Running: ./gp-security scan GP-PROJECTS/MyProject
[scan output...]
```

---

## What is Chat Mode?

**Jade Chat Mode** is an interactive terminal chatbot that interprets natural language requests and executes security operations automatically.

**Think of it like:**
- This Claude Code interface, but for Jade
- Qwen2.5 interpreting your requests and running commands
- "Alexa/Siri for security workflows"

---

## Quick Start

### 1. Start Chat Mode

```bash
cd /home/jimmie/linkops-industries/GP-copilot
jade chat
```

or via symlink:

```bash
bin/jade chat
```

### 2. Talk to Jade

```bash
You: I want to scan my project quickly
🤖 Jade: Quick security scan
Running: ./gp-security scan GP-PROJECTS/YourProject
[scan output...]
✅ Done

You: What security issues did we find?
🤖 Jade: Query knowledge base
Running: jade query "What security issues did we find?"
[query results...]
✅ Done

You: exit
👋 Goodbye!
```

---

## Natural Language Examples

### Scanning Commands

| **Say this...** | **Jade runs...** |
|----------------|------------------|
| "I want to scan my project quickly" | `./gp-security scan {project}` |
| "Scan my project" | `./gp-security scan {project}` |
| "Check my project for vulnerabilities" | `./gp-security scan {project}` |
| "Scan and get advice" | `./gp-security advice {project}` |
| "Scan and fix issues" | `./gp-security scan-and-fix {project}` |

### Policy/Compliance Commands

| **Say this...** | **Jade runs...** |
|----------------|------------------|
| "Check my Terraform for policy violations" | `python opa_scanner.py {project} terraform-security` |
| "Validate OPA policies" | `python opa_scanner.py {project} terraform-security` |
| "Test Terraform plan" | `python conftest_gate_agent.py {project}` |

### Knowledge Base Queries

| **Say this...** | **Jade runs...** |
|----------------|------------------|
| "What security issues did we find?" | `jade query "What security issues did we find?"` |
| "Show me HIGH severity findings" | `jade query "Show me HIGH severity findings"` |
| "How do I prevent SQL injection?" | `jade query "How do I prevent SQL injection?"` |

### GUI/System Commands

| **Say this...** | **Jade runs...** |
|----------------|------------------|
| "Open the GUI" | `cd GP-GUI && npm start` |
| "Show system statistics" | `jade stats` |
| "Show latest scan results" | `cat GP-DATA/active/scans/opa_latest.json \| jq '.summary'` |

---

## How It Works

### Architecture

```
You (natural language)
    ↓
Jade Chat (jade_chat.py)
    ↓
Intent Classification
    ├─ Qwen2.5 LLM (if available) → Probabilistic interpretation
    └─ Pattern Matching (fallback) → Regex-based rules
    ↓
Command Mapping
    ↓
Shell Execution (subprocess)
    ↓
Results Display (rich console)
```

### Two-Tier Interpretation

1. **Primary: Qwen2.5 LLM** (if available)
   - Uses local Qwen2.5-7B-Instruct model
   - Probabilistic natural language understanding
   - Maps input → command with confidence score
   - Requires: `ModelManager` from `GP-PLATFORM/james-config`

2. **Fallback: Pattern Matching** (always available)
   - Regex-based pattern matching
   - Fast, deterministic
   - Works offline without LLM

### Project Detection

Jade automatically detects project paths:

```bash
You: scan GP-PROJECTS/Terraform_CICD_Setup
🤖 Jade detects: project = "GP-PROJECTS/Terraform_CICD_Setup"

You: scan my project
🤖 Jade prompts: Which project? [default: GP-PROJECTS/]

You: set project GP-PROJECTS/MyApp
🤖 Jade: ✅ Current project set to: GP-PROJECTS/MyApp
```

---

## Command Patterns

### Pattern Matching Rules

Defined in [jade_chat.py:51-80](GP-AI/cli/jade_chat.py#L51-80):

```python
self.command_patterns = {
    r"(scan|check|analyze).*project.*quick": {
        "command": "./gp-security scan {project}",
        "description": "Quick security scan"
    },
    r"(check|validate|test).*policy|opa": {
        "command": "PYTHONPATH=... python opa_scanner.py {project} terraform-security",
        "description": "OPA policy validation"
    },
    # ... more patterns
}
```

### Adding New Patterns

Edit [jade_chat.py](GP-AI/cli/jade_chat.py) and add to `self.command_patterns`:

```python
r"your regex pattern here": {
    "command": "shell command here",
    "description": "what it does"
}
```

---

## Integration with Qwen2.5

### Model Configuration

Jade Chat uses [ModelManager](GP-PLATFORM/james-config/model_manager.py) to interface with Qwen2.5:

```python
self.model_manager = ModelManager()
response = self.model_manager.generate(
    prompt=intent_classification_prompt,
    max_tokens=200,
    temperature=0.3  # Low temp for deterministic commands
)
```

### LLM Prompt Structure

```
You are Jade, an AI security consultant. Interpret this user request and map it to a shell command.

User request: "I want to scan my project quickly"
Current project: GP-PROJECTS/MyProject

Available commands:
1. ./gp-security scan <project>
2. jade query "<question>"
...

Respond with JSON:
{
  "command": "the shell command to run",
  "explanation": "brief explanation",
  "confidence": 0.0 to 1.0
}
```

### Confidence Threshold

- **≥ 0.5**: Execute command
- **< 0.5**: Fall back to pattern matching

---

## Use Cases

### 1. Quick Scans During Development

```bash
You: scan my current project
🤖 Jade: ./gp-security scan GP-PROJECTS/MyApp
[scan runs...]
```

### 2. CI/CD Integration

```bash
You: validate terraform before commit
🤖 Jade: python conftest_gate_agent.py GP-PROJECTS/TerraformApp
[validation runs...]
```

### 3. Incident Response

```bash
You: what critical vulnerabilities did we find today?
🤖 Jade: jade query "what critical vulnerabilities did we find today?"
[RAG search...]
```

### 4. Knowledge Queries

```bash
You: how do I fix CVE-2024-12345?
🤖 Jade: jade query "how do I fix CVE-2024-12345?"
[RAG + AI analysis...]
```

---

## Comparison: Chat vs Commands

### Traditional Commands

```bash
# Long, verbose, hard to remember
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  GP-PROJECTS/Terraform_CICD_Setup terraform-security
```

### Chat Mode

```bash
jade chat
> "check terraform policies"
[Jade runs the long command for you]
```

**Benefits:**
- ✅ No need to remember long commands
- ✅ Natural language → less cognitive load
- ✅ Discoverable (just ask!)
- ✅ Beginner-friendly

---

## Advanced Usage

### Set Default Project

```bash
You: set project GP-PROJECTS/MyMainProject
🤖 Jade: ✅ Current project set to: GP-PROJECTS/MyMainProject

# Now all scan commands use this project by default
You: scan
🤖 Jade: ./gp-security scan GP-PROJECTS/MyMainProject
```

### Chain Commands (Future)

Not implemented yet, but planned:

```bash
You: scan my project, fix HIGH issues, and create a PR
🤖 Jade:
  1. ./gp-security scan GP-PROJECTS/MyProject
  2. python pr_bot_agent.py --severity HIGH
  3. gh pr create ...
```

---

## Troubleshooting

### Chat Mode Not Starting

**Error:** `ModuleNotFoundError: No module named 'jade_chat'`

**Fix:**
```bash
# Ensure jade_chat.py is executable
chmod +x GP-AI/cli/jade_chat.py

# Verify symlink
ls -la bin/jade
# Should point to: GP-AI/cli/jade-cli.py
```

### LLM Not Available

**Warning:** `⚠️  LLM not available: ...`

This is normal! Chat mode falls back to pattern matching. To enable LLM:

1. Ensure Qwen2.5 model is downloaded:
   ```bash
   huggingface-cli download Qwen/Qwen2.5-7B-Instruct
   ```

2. Verify `ModelManager` is accessible:
   ```bash
   PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python -c "from model_manager import ModelManager; print('OK')"
   ```

### Pattern Not Recognized

**Output:** `🤔 I'm not sure how to help with that.`

**Fix:** Add a new pattern to [jade_chat.py](GP-AI/cli/jade_chat.py) or rephrase your request:

```bash
# Instead of:
You: do a scan

# Try:
You: scan my project
```

---

## Related Documentation

- **QUICK_COMMANDS.txt** - Quick command reference (now includes chat mode!)
- **COMMAND_REFERENCE.md** - Comprehensive command documentation
- **JADE_INTEGRATION_GUIDE.md** - How Jade makes decisions
- **jade-cli.py** - Main CLI implementation
- **jade_chat.py** - Chat mode implementation
- **model_manager.py** - Qwen2.5 interface

---

## Future Enhancements

- [ ] Multi-turn conversations (context retention)
- [ ] Command chaining ("scan, fix, PR")
- [ ] Voice input (Whisper integration)
- [ ] GUI chat window (Electron)
- [ ] Slack/Discord bot integration
- [ ] Approval workflow integration ("do you want to proceed?")

---

## Why This Exists

You said:

> "where is the chatbox window in terminal like claude code? i want to say this ->[ "I want to scan my project quickly"] and this happens in the background. → [./gp-security scan GP-PROJECTS/{project}]. like the qwen2.5. i think thats why i choose that first. its where i got the idea"

**This is that chatbox!** 🎉

Like Claude Code, but for Jade security workflows. Natural language → automated security operations.

---

**🚀 Try it now:**

```bash
cd /home/jimmie/linkops-industries/GP-copilot
jade chat
```
