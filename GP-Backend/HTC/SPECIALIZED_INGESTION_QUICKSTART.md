# Specialized Ingestion Quick Start

**Status**: ✅ **Phase 1 Complete** (Intake Ingester)

---

## What's New?

**Before**: One generic ingester for everything
**Now**: Specialized ingesters per knowledge type with:
- Custom chunking strategies
- Metadata extraction
- Sanitization (PII/secrets)
- Dedicated ChromaDB collections

---

## Directory Structure

```
unprocessed/
├── intake/              # Business context → ingest_intake.py
│   ├── clients/         # Client profiles
│   ├── meetings/        # Meeting notes
│   └── people/          # People profiles
│
├── jade-knowledge/      # Technical knowledge → ingest_technical.py (TODO)
│   ├── kubernetes/
│   ├── linux/
│   ├── aws/
│   └── security/
│
├── projects-docs/       # Project docs → ingest_projects.py (TODO)
│   └── PROJECT-NAME/
│
└── session-docs/        # Claude sessions → ingest_sessions.py (TODO)
```

---

## Phase 1: Intake Ingester ✅

### What It Does

Ingests business context with **large chunks** (preserve context) and **rich metadata**:

**Clients**:
- Extract: Client name, industry, contact info
- Sanitize: Keep emails, mask phones
- Collection: `clients`

**Meetings**:
- Extract: Date, attendees, action items, topics
- Sanitize: Keep emails (business context), mask SSN/CC
- Collection: `meetings`

**People**:
- Extract: Name, role, company
- Sanitize: Keep business contact info
- Collection: `people`

---

## Usage

### 1. Create Meeting Note

```bash
# Create file in unprocessed/intake/meetings/
cat > unprocessed/intake/meetings/acme-2025-10-16.md <<EOF
# Meeting with Acme Corp - 2025-10-16

**Attendees**:
- John Smith (john@acme.com, CTO)
- Jane Doe (jane@acme.com, Security Lead)

## Discussion
Need Kubernetes security audit for PCI-DSS compliance.

## Action Items
- [ ] Schedule kick-off (assigned: jimmie@linkops.com)
- [ ] Get AWS access (assigned: john@acme.com)
EOF
```

### 2. Ingest (Dry Run)

```bash
cd /home/jimmie/linkops-industries/GP-copilot/GP-Backend/HTC

# Preview what would be ingested
python ingest/ingest_intake.py --dry-run
```

**Output**:
```
============================================================
📚 Ingesting from: intake/
   Category: intake
   Subcategories: clients, meetings, people
============================================================

📁 Processing meetings/ (1 files)

📂 Processing: acme-2025-10-16.md (meetings)
  🔍 [DRY RUN] Would ingest 1 documents to 'meetings'
  ✅ Processed acme-2025-10-16.md → 1 documents

============================================================
📊 Intake Ingestion Summary:
============================================================
  Files processed: 1
  Documents ingested: 1
  Sanitizations: 0
  Errors: 0

🔍 DRY RUN MODE - No data was actually ingested
```

### 3. Ingest (For Real)

```bash
# Actually ingest to ChromaDB
python ingest/ingest_intake.py
```

**Result**:
- ✅ Ingested to: `GP-DATA/jade-knowledge/chroma/meetings/`
- ✅ Metadata extracted: Date, attendees, action items, client
- ✅ Large chunks (preserves context)

---

## What Gets Extracted?

### Meeting Note Example

**Input** (`meetings/acme-2025-10-16.md`):
```markdown
# Meeting with Acme Corp - 2025-10-16

Attendees: John Smith (john@acme.com), Jane Doe

Discussion:
- Need Kubernetes security audit
- PCI-DSS compliance required

Action Items:
- [ ] Schedule scan (assigned: jimmie@linkops.com)
```

**Extracted Metadata**:
```python
{
    "category": "intake",
    "subcategory": "meetings",
    "source": "acme-2025-10-16.md",
    "meeting_date": "2025-10-16",
    "client": "Acme Corp",
    "attendees": ["John Smith", "Jane Doe"],
    "action_items": ["Schedule scan"],
    "topics": ["kubernetes", "security", "pci-dss"],
    "ingested_at": "2025-10-16T15:30:00"
}
```

**ChromaDB Collection**: `meetings`

**Query Later**:
```python
# Query all Acme meetings
results = rag_engine.query(
    "What did we discuss with Acme?",
    collections=["meetings"],
    metadata_filter={"client": "Acme Corp"}
)

# Query action items
results = rag_engine.query(
    "What are my action items?",
    collections=["meetings"],
    metadata_filter={"action_items": {"$contains": "jimmie@linkops.com"}}
)
```

---

## Sanitization

### What Gets Sanitized?

**Intake Rules** (clients, meetings, people):
- ✅ **Keep**: Emails (business context needs them)
- 🔒 **Mask**: Phone numbers → `[PHONE_MASKED]`
- ❌ **Remove**: SSNs, credit cards

**Example**:

**Input**:
```
Contact: John Smith
Email: john@acme.com
Phone: (555) 123-4567
SSN: 123-45-6789
```

**After Sanitization**:
```
Contact: John Smith
Email: john@acme.com
Phone: [PHONE_MASKED]
SSN:
```

---

## Chunking Strategy

**Intake**: Large chunks (1000 tokens ≈ 750 words)

**Why?** Meeting notes need context. Splitting "Attendees" from "Discussion" loses meaning.

**Example**:

**Small chunks (bad for meetings)**:
```
Chunk 1: "Attendees: John, Jane"
Chunk 2: "Discussion: Need security audit"
```
Query "Who discussed security audit?" → Can't connect attendees to discussion!

**Large chunks (good for meetings)**:
```
Chunk 1: "Attendees: John, Jane\n\nDiscussion: Need security audit"
```
Query "Who discussed security audit?" → Returns John and Jane!

---

## File Structure

```
HTC/ingest/
├── shared/
│   ├── base_ingester.py       # Base class for all ingesters
│   ├── chunking.py             # Chunking strategies (small/medium/large)
│   ├── sanitization.py         # PII/secrets removal
│   └── __init__.py
│
├── ingest_intake.py            # ✅ Clients, meetings, people
├── ingest_technical.py         # 🚧 TODO: Kubernetes, Linux, AWS
├── ingest_projects.py          # 🚧 TODO: Project documentation
├── ingest_sessions.py          # 🚧 TODO: Claude Code sessions
└── __init__.py
```

---

## Templates

### Meeting Note Template

```markdown
---
client: Acme Corp
meeting_date: 2025-10-16
project: acme-security-audit
---

# Meeting with Acme Corp - 2025-10-16

**Attendees**:
- John Smith (john@acme.com, CTO)
- Jane Doe (jane@acme.com, Security Lead)
- Your Name (you@company.com, Role)

## Discussion

[What was discussed]

## Action Items

- [ ] Action 1 (assigned: person@email.com)
- [ ] Action 2 (assigned: person@email.com)

## Next Steps

[What happens next]

**Next Meeting**: YYYY-MM-DD at HH:MM
```

### Client Profile Template

```markdown
---
client_name: Acme Corp
industry: Technology
---

# Acme Corp

**Industry**: Technology
**Website**: https://acme.com
**Contact**: John Smith (CTO)

## Overview

[Company description]

## Current Projects

1. Security Audit (2025-10-16 - 2025-11-15)

## Key Contacts

- John Smith (CTO) - john@acme.com
- Jane Doe (Security Lead) - jane@acme.com
```

### People Profile Template

```markdown
---
person_name: John Smith
role: CTO
company: Acme Corp
---

# John Smith

**Role**: CTO
**Company**: Acme Corp
**Email**: john@acme.com

## Background

[Background info]

## Projects

- Acme Security Audit (2025)
```

---

## Testing

### Test 1: Dry Run (Preview)

```bash
python ingest/ingest_intake.py --dry-run
```

Shows what would be ingested without actually ingesting.

### Test 2: Ingest Sample Data

```bash
# Create test meeting
echo "# Meeting with Test Client - 2025-10-16

Attendees: Alice, Bob

Discussion: Test meeting for ingester
" > unprocessed/intake/meetings/test.md

# Ingest
python ingest/ingest_intake.py

# Check result
# → Should create collection: GP-DATA/jade-knowledge/chroma/meetings/
```

---

## Next Steps

### Phase 2: Technical Ingester (TODO)

**Purpose**: Ingest Kubernetes, Linux, AWS, security knowledge

**Features**:
- **Small chunks** (200-400 tokens for Q&A)
- **Metadata**: Technology, difficulty, commands, concepts
- **Sanitization**: Mask API keys, passwords in examples
- **Collections**: `kubernetes`, `linux`, `aws`, `security`

**Usage**:
```bash
# Drop Kubernetes training
cp ~/cks-training.jsonl unprocessed/jade-knowledge/kubernetes/

# Ingest
python ingest/ingest_technical.py
```

### Phase 3: Projects Ingester (TODO)

**Purpose**: Ingest project-specific documentation

**Features**:
- **Medium chunks** (300-600 tokens)
- **Metadata**: Project, technologies, architecture, security findings
- **Sanitization**: Flag hardcoded secrets (security finding!)
- **Collections**: `project-finance`, `project-mlops`, etc.

**Usage**:
```bash
# Drop project docs
cp -r ~/FINANCE-project-docs/ unprocessed/projects-docs/FINANCE-project/

# Ingest
python ingest/ingest_projects.py
```

### Phase 4: Sessions Ingester (TODO)

**Purpose**: Ingest Claude Code session summaries

**Features**:
- **Large chunks** (sessions tell a story)
- **Metadata**: Session date, files changed, tasks, technologies
- **Sanitization**: Mask API keys in code snippets
- **Collections**: `sessions`

**Usage**:
```bash
# Drop session summary
cp ~/session-summary.md unprocessed/session-docs/

# Ingest
python ingest/ingest_sessions.py
```

---

## Benefits

### Better Retrieval Quality

**Before**: Generic ingestion
```python
query("What did we discuss with Acme?")
# Returns: Kubernetes docs, code examples, random stuff (noise!)
```

**After**: Specialized ingestion
```python
query("What did we discuss with Acme?", collections=["meetings"])
# Returns: Only meeting notes with Acme! Clean results!
```

### Rich Metadata

**Before**: No metadata
```python
# Can't filter by date, client, or topics
```

**After**: Rich metadata
```python
# Filter by anything!
rag_engine.query(
    "Show me action items from last week",
    collections=["meetings"],
    metadata_filter={
        "meeting_date": {"$gte": "2025-10-09"},
        "action_items": {"$ne": None}
    }
)
```

### Security

**Before**: Secrets in vector store
```
Meeting notes: "AWS key: AKIAIOSFODNN7EXAMPLE"
→ Stored in ChromaDB (security risk!)
```

**After**: Sanitized before ingestion
```
Meeting notes: "AWS key: [API_KEY_MASKED]"
→ Stored safely in ChromaDB
```

---

## Summary

**Phase 1 (Complete)**: ✅ Intake Ingester
- Business context (clients, meetings, people)
- Large chunks (preserve context)
- Rich metadata (dates, attendees, action items)
- Sanitization (PII/secrets)
- Dedicated collections

**Phase 2-4 (TODO)**:
- Technical ingester (Kubernetes, Linux, AWS)
- Projects ingester (project documentation)
- Sessions ingester (Claude Code sessions)

**Architecture**:
- Shared utilities (chunking, sanitization, base class)
- Specialized processing per knowledge type
- Isolated ChromaDB collections

---

**Documentation**:
- Architecture: [SPECIALIZED_INGESTION_ARCHITECTURE.md](SPECIALIZED_INGESTION_ARCHITECTURE.md)
- This quick start: [SPECIALIZED_INGESTION_QUICKSTART.md](SPECIALIZED_INGESTION_QUICKSTART.md)

---

Last updated: 2025-10-16
