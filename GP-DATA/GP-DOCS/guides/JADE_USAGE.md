# 💬 Jade Usage Guide

## Quick Answer: You have 4 projects!

```bash
$ jade projects

📁 Available Projects (4):

  1. DVWA (Damn Vulnerable Web Application)
  2. LinkOps-MLOps
  3. Terraform_CICD_Setup (Terraform)
  4. test-k8s (Kubernetes)
```

---

## Using Jade CLI

### Simple Commands (Easiest)

```bash
# List all projects
jade projects

# Scan a specific project
jade scan GP-PROJECTS/DVWA

# Show system statistics
jade stats
```

### Using gp-security (Unified Scanner)

```bash
# Scan with all tools
./gp-security scan GP-PROJECTS/DVWA

# Scan + get AI advice
./gp-security advice GP-PROJECTS/DVWA

# Scan + auto-fix
./gp-security scan-and-fix GP-PROJECTS/DVWA
```

---

## Using Chat Mode

### Start Chat

```bash
jade chat
```

### Example Session

```
╭────────────────────── Jade Chat ──────────────────────╮
│ 🤖 Jade Interactive Chat                              │
╰────────────────────────────────────────────────────────╯

You: list projects

🤖 Jade: List available projects
Running: jade projects

📁 Available Projects (4):
  1. DVWA
  2. LinkOps-MLOps
  3. Terraform_CICD_Setup
  4. test-k8s

You: scan GP-PROJECTS/DVWA

🤖 Jade: Security scan
Running: ./gp-security scan GP-PROJECTS/DVWA
[scan runs...]
✅ Done

You: show results

🤖 Jade: View recent scan results
Running: ls -lt GP-DATA/active/scans/ | head -10
[results shown...]

You: exit
👋 Goodbye!
```

---

## What You Can Say in Chat Mode

### Project Management
- "list projects"
- "show projects"
- "display projects"

### Scanning
- "scan my project"
- "I want to scan my project quickly"
- "check GP-PROJECTS/DVWA"
- "scan and get advice"
- "scan and fix issues"

### Results
- "show results"
- "display findings"
- "list scans"

### System
- "show stats"
- "show system status"
- "open the GUI"

---

## Common Mistakes

### ❌ WRONG:
```bash
jade chat "list projects"       # doesn't work - no args accepted
```

### ✅ RIGHT:
```bash
jade chat                        # enter interactive mode first
> list projects                  # then type your request
```

---

## When to Use What?

| Task | Use This | Example |
|------|----------|---------|
| Quick project list | `jade projects` | Direct command |
| Simple scan | `jade scan GP-PROJECTS/X` | Direct command |
| Multiple operations | `jade chat` | Interactive mode |
| Unified scanning | `./gp-security scan` | Direct command |
| Natural language | `jade chat` | Interactive mode |

---

## Setup Reminder

If `jade` command is not found:

```bash
# Reload shell config
source ~/.bashrc

# Or restart your terminal
```

---

## Files & Documentation

- **QUICK_COMMANDS.txt** - Quick reference card
- **GP-AI/cli/CHAT_MODE_README.md** - Comprehensive chat mode docs
- **JADE_CHAT_SUMMARY.md** - Implementation summary
- **JADE_USAGE.md** - This file

---

## Need Help?

```bash
jade --help              # Show all commands
jade projects --help     # Help for specific command
jade chat                # Enter interactive mode (type 'exit' to quit)
```

---

**TL;DR:**
- Simple tasks → `jade projects`, `jade scan`, etc.
- Multiple tasks → `jade chat` (interactive)
- Full scans → `./gp-security scan`
