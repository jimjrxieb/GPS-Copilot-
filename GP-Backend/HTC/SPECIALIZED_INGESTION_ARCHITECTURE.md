# Specialized Ingestion Architecture

**Date**: 2025-10-16
**Status**: 🏗️ **IN PROGRESS**

---

## The Problem

**Current state**: One generic ingester for everything.
- Same chunking strategy for meetings and technical docs
- No metadata extraction (people names, dates, etc.)
- No sanitization (secrets, PII)
- One huge vector store (hard to query specific knowledge)

**Result**: Poor retrieval quality. Meetings mixed with Kubernetes docs.

---

## The Solution

**Specialized ingestion pipelines** per knowledge type:
- Custom chunking (meetings ≠ technical docs)
- Metadata extraction (names, dates, projects)
- Sanitization (remove secrets, PII)
- **Isolated ChromaDB collections** per category

---

## Architecture

### Directory Structure

```
unprocessed/
├── intake/              # Business context (clients, meetings, people)
│   ├── clients/         # Client profiles, requirements
│   ├── meetings/        # Meeting notes, action items
│   └── people/          # People profiles, roles, contacts
│
├── jade-knowledge/      # Technical training data
│   ├── kubernetes/      # K8s concepts, patterns, troubleshooting
│   ├── linux/           # Linux commands, administration
│   ├── aws/             # AWS services, best practices
│   ├── security/        # Security patterns, vulnerabilities
│   └── policy/          # OPA policies, compliance
│
├── projects-docs/       # Project-specific documentation
│   ├── FINANCE-project/
│   ├── LinkOps-MLOps/
│   └── DVWA/
│
└── session-docs/        # Claude Code session summaries
    └── *.md
```

### ChromaDB Collections

```
GP-DATA/jade-knowledge/chroma/
├── clients/            # Client profiles
├── meetings/           # Meeting notes
├── people/             # People profiles
├── kubernetes/         # K8s knowledge
├── linux/              # Linux knowledge
├── aws/                # AWS knowledge
├── security/           # Security patterns
├── policy/             # OPA policies
├── project-finance/    # Project: FINANCE
├── project-mlops/      # Project: LinkOps-MLOps
├── project-dvwa/       # Project: DVWA
└── sessions/           # Claude Code sessions
```

### Specialized Ingesters

```
HTC/ingest/
├── ingest_intake.py             # Clients, meetings, people
├── ingest_technical.py          # Kubernetes, Linux, AWS, security
├── ingest_projects.py           # Project documentation
├── ingest_sessions.py           # Claude Code sessions
└── shared/
    ├── chunking.py              # Chunking strategies
    ├── metadata.py              # Metadata extractors
    ├── sanitization.py          # PII/secrets removal
    └── base_ingester.py         # Base class
```

---

## Ingestion Pipelines

### 1. Intake Ingester (`ingest_intake.py`)

**Input**: `unprocessed/intake/{clients,meetings,people}/`

**Processing**:
1. **Parse structure** (markdown headers, YAML frontmatter)
2. **Extract metadata**:
   - Client name, contact info
   - Meeting date, attendees, action items
   - People names, roles, email
3. **Sanitize**:
   - Detect SSNs, credit cards (remove)
   - Detect emails (mask or keep based on context)
   - Detect phone numbers (mask)
4. **Chunk**:
   - Large chunks (500-1000 tokens)
   - Keep context (meeting notes should stay together)
5. **Add to ChromaDB**:
   - Collection: `clients`, `meetings`, or `people`
   - Metadata: {source, date, people, project, action_items}

**Example**:
```markdown
# Meeting with Acme Corp - 2025-10-16

Attendees: John Smith (john@acme.com), Jane Doe (jane@acme.com)

Discussion:
- Need Kubernetes security audit
- PCI-DSS compliance required
- Timeline: 30 days

Action Items:
- [ ] Schedule security scan (assigned: jimmie@linkops.com)
- [ ] Review compliance gaps (assigned: john@acme.com)
```

**Extracted Metadata**:
```python
{
    "source": "meetings/acme-2025-10-16.md",
    "meeting_date": "2025-10-16",
    "client": "Acme Corp",
    "attendees": ["John Smith", "Jane Doe"],
    "action_items": ["Schedule security scan", "Review compliance gaps"],
    "project": "acme-security-audit",
    "topics": ["kubernetes", "security", "pci-dss"]
}
```

---

### 2. Technical Ingester (`ingest_technical.py`)

**Input**: `unprocessed/jade-knowledge/{kubernetes,linux,aws,security,policy}/`

**Processing**:
1. **Detect format** (JSONL conversations, markdown, code snippets)
2. **Extract metadata**:
   - Technology (kubernetes, aws, etc.)
   - Difficulty (beginner, intermediate, advanced)
   - Commands (kubectl, aws cli, etc.)
   - Concepts (RBAC, IAM, etc.)
3. **Sanitize**:
   - Detect API keys, tokens (remove or replace with placeholders)
   - Detect passwords in examples (mask)
4. **Chunk**:
   - Small chunks (200-400 tokens)
   - Code snippets kept intact
   - Q&A pairs kept together
5. **Add to ChromaDB**:
   - Collection: `kubernetes`, `linux`, `aws`, `security`, or `policy`
   - Metadata: {technology, difficulty, commands, concepts}

**Example JSONL**:
```json
{"messages": [
  {"role": "user", "content": "How do I create a Kubernetes secret?"},
  {"role": "assistant", "content": "Use kubectl create secret:\nkubectl create secret generic my-secret --from-literal=password=supersecret"}
]}
```

**Extracted Metadata**:
```python
{
    "source": "kubernetes/cks-training.jsonl",
    "technology": "kubernetes",
    "difficulty": "beginner",
    "commands": ["kubectl create secret"],
    "concepts": ["secrets", "security"],
    "question": "How do I create a Kubernetes secret?"
}
```

---

### 3. Projects Ingester (`ingest_projects.py`)

**Input**: `unprocessed/projects-docs/PROJECT-NAME/`

**Processing**:
1. **Detect project** (from directory name)
2. **Extract metadata**:
   - Project name, description
   - Technologies used (Python, Kubernetes, etc.)
   - Architecture (microservices, monolith)
   - Security findings (from scans)
3. **Sanitize**:
   - Detect hardcoded secrets (flag and remove)
   - Detect internal URLs/IPs (mask)
4. **Chunk**:
   - Medium chunks (300-600 tokens)
   - Keep related sections together (architecture diagram + description)
5. **Add to ChromaDB**:
   - Collection: `project-{name}` (e.g., `project-finance`)
   - Metadata: {project, technologies, architecture, security_findings}

**Example**:
```markdown
# FINANCE Project Architecture

Stack: Python Flask, PostgreSQL, Redis, Kubernetes

Security Findings:
- 3 HIGH: SQL injection vulnerabilities
- 5 MEDIUM: Missing authentication
```

**Extracted Metadata**:
```python
{
    "source": "projects-docs/FINANCE-project/architecture.md",
    "project": "FINANCE",
    "technologies": ["python", "flask", "postgresql", "redis", "kubernetes"],
    "architecture": "microservices",
    "security_findings": {
        "high": 3,
        "medium": 5,
        "critical": 0
    }
}
```

---

### 4. Sessions Ingester (`ingest_sessions.py`)

**Input**: `unprocessed/session-docs/*.md`

**Processing**:
1. **Parse Claude Code session summary**
2. **Extract metadata**:
   - Session date
   - Files changed
   - Tasks completed
   - Technologies involved
   - Key decisions
3. **Sanitize**:
   - Detect API keys in code snippets (mask)
   - Detect secrets in environment variables (remove)
4. **Chunk**:
   - Large chunks (500-1000 tokens)
   - Keep session context together
5. **Add to ChromaDB**:
   - Collection: `sessions`
   - Metadata: {session_date, files_changed, tasks, technologies, decisions}

**Example**:
```markdown
# Session Summary - 2025-10-16

## Tasks Completed:
- Fixed SQL injection in FINANCE project
- Updated Kubernetes deployment with security context
- Added OPA policy for pod security

## Files Changed:
- FINANCE-project/app.py
- FINANCE-project/k8s/deployment.yaml
- GP-CONSULTING/1-POLICIES/opa/pod-security.rego

## Key Decisions:
- Use parameterized queries for all database access
- Enable AppArmor on all pods
- Require security context in OPA policy
```

**Extracted Metadata**:
```python
{
    "source": "session-docs/session-2025-10-16.md",
    "session_date": "2025-10-16",
    "files_changed": [
        "FINANCE-project/app.py",
        "FINANCE-project/k8s/deployment.yaml",
        "GP-CONSULTING/1-POLICIES/opa/pod-security.rego"
    ],
    "tasks": [
        "Fixed SQL injection",
        "Updated Kubernetes deployment",
        "Added OPA policy"
    ],
    "technologies": ["python", "kubernetes", "opa"],
    "projects": ["FINANCE"],
    "key_decisions": [
        "Use parameterized queries",
        "Enable AppArmor",
        "Require security context"
    ]
}
```

---

## Chunking Strategies

### Business Context (Intake)
**Size**: 500-1000 tokens (large)
**Why**: Meeting notes need context. Splitting loses meaning.
**Strategy**: Keep sections together (attendees + discussion + action items)

### Technical Knowledge
**Size**: 200-400 tokens (small)
**Why**: Specific queries need specific answers. Q&A pairs stay together.
**Strategy**: Split by concept, but keep code examples intact

### Project Documentation
**Size**: 300-600 tokens (medium)
**Why**: Balance between context and precision
**Strategy**: Split by section, keep architecture diagrams with descriptions

### Session Summaries
**Size**: 500-1000 tokens (large)
**Why**: Sessions tell a story. Need full context.
**Strategy**: Keep session intact, possibly split by task

---

## Metadata Extraction

### Why Metadata Matters

**Without metadata**:
```python
# Query: "Who attended the Acme meeting?"
# Result: Returns chunks about meetings, but no structured data
```

**With metadata**:
```python
# Query: "Who attended the Acme meeting?"
# Filter: metadata['client'] == 'Acme'
# Result: {"attendees": ["John Smith", "Jane Doe"], "date": "2025-10-16"}
```

### Metadata Schema

```python
# Intake metadata
{
    "category": "intake",
    "subcategory": "meetings",  # or "clients", "people"
    "client": "Acme Corp",
    "meeting_date": "2025-10-16",
    "attendees": ["John Smith", "Jane Doe"],
    "action_items": ["Schedule scan", "Review gaps"],
    "topics": ["kubernetes", "security"],
    "project": "acme-security-audit"
}

# Technical metadata
{
    "category": "technical",
    "subcategory": "kubernetes",  # or "linux", "aws", etc.
    "technology": "kubernetes",
    "difficulty": "intermediate",
    "commands": ["kubectl create secret"],
    "concepts": ["secrets", "security", "rbac"],
    "question": "How do I create a secret?"
}

# Project metadata
{
    "category": "project",
    "project": "FINANCE",
    "technologies": ["python", "flask", "postgresql"],
    "architecture": "microservices",
    "security_findings": {"high": 3, "medium": 5}
}

# Session metadata
{
    "category": "session",
    "session_date": "2025-10-16",
    "files_changed": ["app.py", "deployment.yaml"],
    "tasks": ["Fixed SQL injection"],
    "technologies": ["python", "kubernetes"],
    "projects": ["FINANCE"]
}
```

---

## Sanitization

### What to Remove/Mask

1. **Secrets**:
   - API keys: `AKIAIOSFODNN7EXAMPLE` → `[API_KEY_MASKED]`
   - Passwords: `password=supersecret` → `password=[REDACTED]`
   - Tokens: `Bearer eyJhbGc...` → `Bearer [TOKEN_MASKED]`

2. **PII** (Personal Identifiable Information):
   - SSNs: `123-45-6789` → `[SSN_MASKED]`
   - Credit cards: `4111-1111-1111-1111` → `[CC_MASKED]`
   - Emails: `john@acme.com` → Keep (business context) or mask based on rules
   - Phone numbers: `(555) 123-4567` → `[PHONE_MASKED]`

3. **Internal Data**:
   - Internal IPs: `192.168.1.100` → `[IP_MASKED]`
   - Internal URLs: `https://internal.acme.com` → `[INTERNAL_URL]`

### Sanitization Rules

```python
# Rules by category
SANITIZATION_RULES = {
    "intake": {
        "emails": "keep",      # Business context needs emails
        "phones": "mask",      # Mask phone numbers
        "ssn": "remove",       # Always remove SSNs
        "cc": "remove"         # Always remove credit cards
    },
    "technical": {
        "api_keys": "mask",    # Mask API keys in examples
        "passwords": "mask",   # Mask passwords in code
        "secrets": "mask"      # Mask secrets
    },
    "projects": {
        "secrets": "flag",     # Flag hardcoded secrets (security finding!)
        "internal_urls": "mask"
    },
    "sessions": {
        "api_keys": "mask",
        "secrets": "mask"
    }
}
```

---

## Query Strategies

### Query by Category

```python
# Query intake knowledge
results = rag_engine.query(
    "What did we discuss with Acme?",
    collections=["meetings"],
    metadata_filter={"client": "Acme Corp"}
)

# Query technical knowledge
results = rag_engine.query(
    "How do I create a Kubernetes secret?",
    collections=["kubernetes"],
    metadata_filter={"concepts": {"$contains": "secrets"}}
)

# Query project knowledge
results = rag_engine.query(
    "What security findings does FINANCE project have?",
    collections=["project-finance"],
    metadata_filter={"security_findings.high": {"$gt": 0}}
)

# Query session history
results = rag_engine.query(
    "What did I work on yesterday?",
    collections=["sessions"],
    metadata_filter={"session_date": "2025-10-15"}
)
```

---

## Implementation Plan

### Phase 1: Base Infrastructure
1. Create `HTC/ingest/` directory
2. Create `HTC/ingest/shared/` utilities
3. Create base ingester class

### Phase 2: Specialized Ingesters
1. Build `ingest_intake.py`
2. Build `ingest_technical.py`
3. Build `ingest_projects.py`
4. Build `ingest_sessions.py`

### Phase 3: Orchestration
1. Update main `ingest.py` to route to specialized ingesters
2. Auto-detect category from path

### Phase 4: Testing
1. Test each ingester with sample data
2. Verify ChromaDB collections created
3. Test query strategies

---

## Usage

### Ingest Intake Data

```bash
# Put meeting notes in unprocessed/intake/meetings/
cp ~/acme-meeting.md unprocessed/intake/meetings/

# Ingest
python ingest.py

# Automatically routes to ingest_intake.py
# Creates collection: GP-DATA/jade-knowledge/chroma/meetings/
```

### Ingest Technical Knowledge

```bash
# Put Kubernetes training in unprocessed/jade-knowledge/kubernetes/
cp ~/cks-training.jsonl unprocessed/jade-knowledge/kubernetes/

# Ingest
python ingest.py

# Automatically routes to ingest_technical.py
# Creates collection: GP-DATA/jade-knowledge/chroma/kubernetes/
```

### Query Specific Knowledge

```python
from HTC.jade_rag_langgraph import JadeRAGAgent

agent = JadeRAGAgent()

# Query meetings only
result = agent.query(
    "What did we discuss with Acme?",
    collections=["meetings"]
)

# Query Kubernetes knowledge only
result = agent.query(
    "How do I create a secret?",
    collections=["kubernetes"]
)

# Query across multiple collections
result = agent.query(
    "Show me Kubernetes security issues in FINANCE project",
    collections=["kubernetes", "security", "project-finance"]
)
```

---

## Benefits

### Better Retrieval Quality
- **Before**: Query "Acme meeting" returns Kubernetes docs (noise)
- **After**: Query "Acme meeting" only searches `meetings` collection

### Specialized Processing
- **Before**: Same chunking for everything (poor quality)
- **After**: Meeting notes use large chunks, technical docs use small chunks

### Rich Metadata
- **Before**: No metadata, can't filter
- **After**: Filter by client, date, technology, project, etc.

### Security
- **Before**: Secrets in vector store
- **After**: Sanitized before ingestion

---

## Next Steps

1. Create directory structure
2. Build shared utilities (chunking, metadata, sanitization)
3. Build specialized ingesters
4. Update orchestrator
5. Test with real data

---

Last updated: 2025-10-16
