# GP-DATA for Jade - Knowledge Management Guide

> **How Jade learns, remembers, and retrieves your knowledge**

## Overview

GP-DATA is Jade's **memory system**. Everything Jade knows comes from here:
- Scan results → Security knowledge
- Meeting notes → Context about decisions
- Person profiles → Who's who
- Client info → Requirements and compliance

## The Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│  YOU: Drop file in GP-RAG/intake/people/john-smith.md      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                  jade learn
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  GP-RAG/core/dynamic_learner.py                             │
│  • Chunks the markdown file                                 │
│  • Creates embeddings (vector representations)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                  Stores in
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  GP-DATA/knowledge-base/chroma/                             │
│  • people_knowledge collection                              │
│  • Vector embeddings for semantic search                    │
│  • Metadata: filename, category, timestamp                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
              YOU: "Who is John Smith?"
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  GP-AI/core/rag_engine.py                                   │
│  • Searches ChromaDB for "John Smith"                       │
│  • Retrieves top 5 relevant chunks                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                  Context found
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  GP-AI/models/model_manager.py (Qwen2.5-7B)                 │
│  • Injects retrieved chunks into prompt                     │
│  • Generates answer based on YOUR knowledge                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        "John Smith is the CISO at Acme Corp..."
```

## Directory Structure for Jade

```
GP-DATA/
│
├── knowledge-base/              ← JADE'S MAIN KNOWLEDGE SOURCE
│   ├── chroma/                  ← ChromaDB vector database
│   │   ├── people_knowledge/    ← Person profiles (from GP-RAG/intake/people/)
│   │   ├── meeting_knowledge/   ← Meeting notes (from GP-RAG/intake/meetings/)
│   │   ├── client_knowledge/    ← Client info (from GP-RAG/intake/clients/)
│   │   ├── project_knowledge/   ← Project context (from GP-RAG/intake/projects/)
│   │   ├── scan_findings/       ← Security scan results
│   │   ├── documentation/       ← Security docs
│   │   └── compliance_frameworks/ ← Regulatory standards
│   │
│   ├── cks-standards/           ← Kubernetes security knowledge
│   ├── compliance-frameworks/   ← SOC2, PCI-DSS, etc.
│   ├── security-patterns/       ← Best practices
│   └── client-contexts/         ← Client-specific requirements
│
├── active/                      ← CURRENT OPERATIONAL DATA
│   ├── scans/                   ← Latest scan results (auto-ingested to ChromaDB)
│   ├── fixes/                   ← Remediation history
│   ├── reports/                 ← Generated reports
│   └── analysis/                ← AI analysis results
│
├── notes/                       ← YOUR MANUAL NOTES (can be learned)
├── research/                    ← RAG research outputs
└── audit/                       ← Audit logs (for compliance)
```

## ChromaDB Collections

Jade organizes knowledge into **collections** (like database tables):

| Collection | Source | Purpose | Example Query |
|------------|--------|---------|---------------|
| `people_knowledge` | GP-RAG/intake/people/ | Person profiles | "Who is the CISO?" |
| `meeting_knowledge` | GP-RAG/intake/meetings/ | Decisions, action items | "What did we decide about K8s?" |
| `client_knowledge` | GP-RAG/intake/clients/ | Requirements | "What are Acme's compliance needs?" |
| `project_knowledge` | GP-RAG/intake/projects/ | Project context | "What's the goal of Project X?" |
| `scan_findings` | GP-DATA/active/scans/ | Security vulnerabilities | "Show me CRITICAL findings" |
| `documentation` | knowledge-base/security-patterns/ | Best practices | "How to prevent SQL injection?" |
| `compliance_frameworks` | knowledge-base/compliance-frameworks/ | Regulatory standards | "What does SOC2 require?" |

## Dynamic Learning Workflow

### 1. Learn About a Person

```bash
# Create profile
cat > GP-RAG/intake/people/alice-johnson.md << 'EOF'
# Alice Johnson

**Title**: Senior DevOps Engineer
**Email**: alice@company.com
**Specialties**: Kubernetes, Terraform, CI/CD

## Background
Alice joined in 2023, previously at Google Cloud.
Expert in Kubernetes security and RBAC.

## Current Projects
- Zero trust network implementation
- Automated compliance scanning
EOF

# Teach Jade
jade learn

# Query
jade query "Who is Alice Johnson?"
# → "Alice Johnson is a Senior DevOps Engineer at company.com,
#     specializing in Kubernetes, Terraform, and CI/CD..."
```

### 2. Learn From Meeting Notes

```bash
# Save meeting
cat > GP-RAG/intake/meetings/2025-10-04-security-standup.md << 'EOF'
# Security Team Standup - Oct 4, 2025

**Attendees**: Alice, Bob, Carol

## Decisions
- Moving to OPA for policy enforcement
- Bob will lead Terraform security review
- Target: Complete by Oct 15

## Action Items
- Alice: Setup OPA cluster (Due: Oct 6)
- Bob: Review all Terraform modules (Due: Oct 10)
EOF

# Learn
jade learn

# Query later
jade query "Who is leading the Terraform review?"
# → "Bob is leading the Terraform security review,
#     targeting completion by October 15..."
```

### 3. Learn Client Requirements

```bash
cat > GP-RAG/intake/clients/acme-corp.md << 'EOF'
# Acme Corporation

**Industry**: Financial Services
**Compliance**: SOC2 Type II, PCI-DSS Level 1

## Security Requirements
1. All data encrypted at rest (AES-256)
2. MFA mandatory for all users
3. Quarterly penetration tests
4. 4-hour incident response SLA

## Tech Stack
- Kubernetes on AWS EKS
- Terraform for infrastructure
- OPA for policy as code
EOF

jade learn

jade query "What are Acme's compliance requirements?"
# → "Acme Corporation requires SOC2 Type II and PCI-DSS Level 1
#     compliance. They mandate AES-256 encryption at rest..."
```

## Automatic Ingestion

### Scan Results

Security scans are **automatically learned**:

```bash
# Run scan
jade scan GP-PROJECTS/MyApp

# Results saved to:
GP-DATA/active/scans/bandit_latest.json
GP-DATA/active/scans/trivy_latest.json

# Auto-sync daemon ingests to ChromaDB:
GP-DATA/knowledge-base/chroma/scan_findings/

# Now queryable:
jade query "What CRITICAL issues did we find in MyApp?"
```

### Auto-Sync Process

```
1. Scan completes → Results saved to GP-DATA/active/scans/
2. auto_sync_daemon.py (runs in background) detects new files
3. Parses JSON, extracts findings
4. Creates embeddings
5. Stores in ChromaDB scan_findings collection
6. Now available for queries!
```

## Querying Jade's Knowledge

### Via CLI

```bash
# Direct query
jade query "Who is responsible for Kubernetes security?"

# Chat mode
jade chat
> "What did we decide about OPA policies?"
> "Show me all CRITICAL vulnerabilities"
> "What are the action items from yesterday's meeting?"
```

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are Acme Corp compliance requirements?"
  }'
```

### Via Python

```python
from GP_AI.core.rag_engine import rag_engine

results = rag_engine.query_knowledge(
    "Who is the lead DevOps engineer?",
    collections=["people_knowledge"]
)

for result in results:
    print(result['content'])
```

## Knowledge Verification

### Check What Jade Knows

```bash
# List all collections
python -c "
import chromadb
client = chromadb.PersistentClient(path='GP-DATA/knowledge-base/chroma')
for col in client.list_collections():
    print(f'{col.name}: {col.count()} chunks')
"

# Example output:
# people_knowledge: 23 chunks
# meeting_knowledge: 45 chunks
# scan_findings: 234 chunks
# documentation: 156 chunks
```

### Test Retrieval

```python
# GP-DATA/test_jade_knowledge.py
from GP_AI.core.rag_engine import rag_engine

# Test person lookup
results = rag_engine.query_knowledge("Alice Johnson", n_results=3)
for r in results:
    print(f"Found in: {r['metadata']['source']}")
    print(f"Content: {r['content'][:200]}")
```

## Best Practices

### 1. Organize by Category

Use GP-RAG intake categories correctly:
- **people/** - Individual person profiles
- **meetings/** - Meeting notes, standups
- **clients/** - Client requirements, context
- **projects/** - Project goals, architecture
- **policies/** - Custom organizational policies
- **docs/** - General documentation

### 2. Use Consistent Formats

```markdown
# Person Template
**Title**:
**Email**:
**Specialties**:

## Background
## Current Projects

# Meeting Template
**Date**: YYYY-MM-DD
**Attendees**:
## Decisions
## Action Items

# Client Template
**Industry**:
**Compliance**:
## Requirements
## Tech Stack
```

### 3. Keep Files Focused

One person per file, one meeting per file. This improves chunking and retrieval accuracy.

### 4. Include Searchable Keywords

Use terms people will search for:
- Names, titles, emails
- Project names
- Technology keywords (Kubernetes, Terraform, etc.)
- Dates and deadlines

## Maintenance

### Backup ChromaDB

```bash
# Automatic backup
cp -r GP-DATA/knowledge-base/chroma GP-DATA/knowledge-base/chroma_backup_$(date +%Y%m%d)

# Or use provided script
python GP-DATA/backup_chromadb.py
```

### Clear Old Knowledge

```python
# Clear specific collection
import chromadb
client = chromadb.PersistentClient(path='GP-DATA/knowledge-base/chroma')
client.delete_collection("old_collection_name")
```

### Re-sync All Knowledge

```bash
# Re-ingest everything
python GP-DATA/simple_sync.py --rebuild
```

## Troubleshooting

### "Jade doesn't remember what I taught"

```bash
# 1. Check file was processed
ls GP-RAG/processed/

# 2. Check ChromaDB has it
python -c "
import chromadb
client = chromadb.PersistentClient(path='GP-DATA/knowledge-base/chroma')
col = client.get_collection('people_knowledge')
print(f'Total chunks: {col.count()}')
"

# 3. Test retrieval
jade query "exact text from your file"
```

### "Auto-sync not working"

```bash
# Check daemon is running
ps aux | grep auto_sync

# Start manually
python GP-DATA/auto_sync_daemon.py &

# Check logs
tail -f GP-DATA/auto_sync.log
```

### "Wrong answers from queries"

- Make files more specific
- Use clearer keywords
- Check which collection is being searched
- Verify embeddings are working

## Integration Points

### GP-RAG → GP-DATA
```
GP-RAG/intake/people/alice.md
  ↓ (jade learn)
GP-DATA/knowledge-base/chroma/people_knowledge/
```

### GP-CONSULTING-AGENTS → GP-DATA
```
Scanners run
  ↓
GP-DATA/active/scans/*.json
  ↓ (auto-sync)
GP-DATA/knowledge-base/chroma/scan_findings/
```

### GP-AI ← GP-DATA
```
User query
  ↓
GP-AI/core/rag_engine.py
  ↓
GP-DATA/knowledge-base/chroma/ (search)
  ↓
Context returned to LLM
```

## Advanced Features

### Custom Collections

```python
# Create specialized collection
from GP_AI.core.rag_engine import rag_engine

rag_engine.create_collection(
    name="threat_intelligence",
    metadata={"category": "security"}
)
```

### Filtered Queries

```python
# Search specific collections only
results = rag_engine.query_knowledge(
    "SQL injection",
    collections=["documentation", "scan_findings"]
)
```

### Temporal Queries

```python
# Find recent information
results = rag_engine.query_knowledge(
    "meeting decisions",
    where={"timestamp": {"$gt": "2025-10-01"}}
)
```

---

**Status**: ✅ Production Ready for Jade Dynamic Learning
**Last Updated**: 2025-10-04

**Related Docs**:
- [GP-RAG/README.md](../GP-RAG/README.md) - Dynamic learning intake
- [GP-AI/COMPLETE_JADE_MAP.md](../GP-AI/COMPLETE_JADE_MAP.md) - How Jade works
- [GP-DATA/README.md](README.md) - Full GP-DATA architecture