# 🎯 CLAUDE CODE ARCHITECTURE RULES

**READ THIS BEFORE EVERY SESSION**

---

## ⚡ QUICK REFERENCE

### What We're Building:
**Jade = AI Junior Cloud Security Engineer for Desktop**

### What We're NOT Building:
- ❌ Microservices
- ❌ Cloud services
- ❌ Multi-tenant SaaS
- ❌ Web applications

---

## 🏗️ ARCHITECTURE: MONOLITHIC DESKTOP APP

```
Manager's Workstation (Offline)
    ↓
Electron GUI (Desktop)
    ↓ IPC
FastAPI (localhost:8000)
    ↓ Python imports
Jade AI + RAG + Scanners (All local)
    ↓ subprocess
Binary tools (bandit, trivy, etc)
    ↓ File I/O
Local filesystem (~/jade-workspace/)
```

**Everything runs on ONE machine. No network. No cloud.**

---

## ✅ ALLOWED PATTERNS

1. **Direct Python imports** between components
2. **Subprocess calls** to security tools
3. **Local file system** for all storage
4. **HTTP only** between Electron GUI ↔ FastAPI
5. **Single FastAPI server** on localhost:8000

---

## ❌ FORBIDDEN PATTERNS

1. **NO microservice APIs** between scanners
2. **NO network calls** except GUI→API
3. **NO cloud dependencies** ever
4. **NO separation** of scanners into services
5. **NO Docker/K8s** for deployment (desktop installer only)

---

## 🎯 CURRENT PRIORITIES (Read from VISION.md)

Phase 1: RAG Auto-Sync
Phase 2: Approval Workflow
Phase 3: Activity Queries
Phase 4: Email/Reporting
Phase 5: Git Integration

---

## 📍 KEY FILES

- **VISION.md** - Complete architecture & roadmap
- **GP-AI/api/main.py** - FastAPI server (port 8000)
- **GP-GUI/src/main.js** - Electron main process
- **GP-RAG/** - RAG engine (needs auto-sync)
- **GP-CONSULTING-AGENTS/scanners/** - Security tools

---

## 🔥 CRITICAL REMINDERS

1. **Manager's question:** "What did we do today?"
   - This requires RAG auto-sync + activity tracking

2. **Approval workflow** is THE core feature
   - Manager reviews Jade's suggestions
   - One-click approve/reject
   - Auto-execute on approval

3. **Everything stays local**
   - No cloud APIs
   - No external dependencies
   - Works 100% offline

---

## 💡 THE USE CASE

Manager works with Jade like a junior engineer:

```
Manager: "Scan our Terraform repos"
Jade: "Found 23 issues, created 9 OPA policies"
Manager: [Reviews in GUI, clicks Approve]
Jade: "Applied to dev, committed to Git, emailed team"
Manager: "What did we do today?"
Jade: "9 policies, 23 scans, 47 fixes"
```

---

**When in doubt, check VISION.md**

**No scope creep. No microservices. Build what's in VISION.md.**