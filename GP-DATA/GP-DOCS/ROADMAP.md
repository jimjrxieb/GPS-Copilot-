# 🗺️ GP-COPILOT DEVELOPMENT ROADMAP

**Last Updated:** September 30, 2025
**Current Phase:** Phase 2 - Approval Workflow (Phase 1 Complete!)

---

## 📋 DEVELOPMENT PHASES

### ✅ Phase 0: Foundation (COMPLETE)
**Status:** 100% Complete
**Duration:** Completed Sept 2025

- [x] Electron GUI framework
- [x] FastAPI server (port 8000)
- [x] Jade AI engine (Qwen2.5 7B)
- [x] Static RAG system
- [x] Security scanners (11 tools)
- [x] Workflow orchestration
- [x] Git integration basics

**Key Achievement:** Monolithic desktop architecture established.

---

### ✅ Phase 1: RAG Auto-Sync System (COMPLETE)
**Status:** 100% Complete
**Priority:** CRITICAL
**Duration:** 1 day (September 30, 2025)
**Completion Date:** September 30, 2025

#### Core Features Built:

- [x] **File System Watcher** (`GP-RAG/auto_sync.py`)
  - ✅ Monitor ~/jade-workspace/projects/**
  - ✅ Detect Git changes, new files, deletions
  - ✅ Trigger on: .tf, .yaml, .yml, .rego, .py, .md, .json
  - ✅ Real-time detection (<2 seconds)

- [x] **Auto-Ingestion Pipeline** (`GP-RAG/ingestion/auto_ingest.py`)
  - ✅ Parse detected files with type-specific parsers
  - ✅ Extract metadata (timestamp, author, type, project)
  - ✅ Embed with sentence-transformers (CPU mode)
  - ✅ Store in ChromaDB with rich metadata

- [x] **Metadata Tracking** (Built into `auto_sync.py` ActivityDatabase)
  - ✅ Track: file type, project, timestamp, author
  - ✅ Track: action type (created, modified, deleted, moved)
  - ✅ Track: policy type (OPA, Gatekeeper, Terraform)
  - ✅ SQLite time-series database with indexes

- [x] **Activity Database** (Built into `auto_sync.py` ActivityDatabase)
  - ✅ SQLite for structured queries
  - ✅ ChromaDB for semantic search (via AutoIngestionPipeline)
  - ✅ Combined queries for "What did we do today?"

- [x] **Query Interface** (`GP-RAG/query/activity_queries.py`)
  - ✅ query_todays_work() / query_weekly_work()
  - ✅ query_by_file_type(action_type, timeframe)
  - ✅ query_by_project(project_name, timeframe)
  - ✅ query_policy_changes(timeframe)
  - ✅ query_terraform_changes(timeframe)
  - ✅ semantic_search() for content queries
  - ✅ query_trend_analysis() for time-series

- [x] **File Parsers** (`GP-RAG/ingestion/parsers.py`)
  - ✅ parse_terraform() - Extract resources, variables
  - ✅ parse_kubernetes() - Extract manifests, security contexts
  - ✅ parse_opa() - Extract policies, deny rules
  - ✅ parse_python() - Extract functions, classes
  - ✅ parse_markdown() / parse_json()

#### Testing Checklist:

- [x] Sync 5+ files and verify ingestion works
- [x] Query "what did we do today?" - accurate results
- [x] File watcher triggers within 2 seconds (tested)
- [x] Works offline (no network dependencies)

#### Success Metrics (All Met):

- ✅ **Query Speed:** <2 seconds (achieved <1 second)
- ✅ **Accuracy:** 100% of tracked files in results
- ✅ **Coverage:** All file types (.tf, .yaml, .rego, .py, .md, .json)
- ✅ **Latency:** <2 seconds from file save to RAG update

**Key Achievement:** "What did we do today?" fully functional!

---

### 🔥 Phase 2: Approval Workflow (NEXT)
**Status:** 0% Complete
**Priority:** HIGH
**Est. Duration:** 2-3 weeks
**Start Date:** ~October 20, 2025

#### Core Features to Build:

- [ ] **Approval State Machine** (`GP-AI/approval/state_machine.py`)
  - States: proposed → pending → approved → executing → completed
  - Rejection handling with notes
  - Timeout handling (auto-expire old proposals)

- [ ] **Approval Queue API** (`GP-AI/api/main.py` - new endpoints)
  - POST /api/v1/proposals - Create new proposal
  - GET /api/v1/proposals - List pending
  - POST /api/v1/proposals/{id}/approve
  - POST /api/v1/proposals/{id}/reject
  - GET /api/v1/proposals/{id}/status

- [ ] **GUI Approval Queue** (`GP-GUI/public/approval-queue.html`)
  - List view of pending proposals
  - Detail view with diff viewer
  - Approve/Reject buttons
  - Filter by type, priority, project
  - Batch approval for similar issues

- [ ] **Visual Diff Viewer** (`GP-GUI/public/js/diff-viewer.js`)
  - Side-by-side diff for policies
  - Syntax highlighting for REGO, YAML, Terraform
  - Risk assessment display
  - Affected resources count

- [ ] **Execution Pipeline** (`GP-AI/approval/executor.py`)
  - Execute approved actions safely
  - Rollback on failure
  - Log all executions
  - Update RAG with actions taken

- [ ] **Audit Log** (`GP-DATA/audit/approval_log.db`)
  - Track all approvals/rejections
  - Who, what, when, why
  - Compliance evidence trail
  - Export to CSV/PDF

#### Testing Checklist:

- [ ] Propose 50 fixes, approve/reject mix
- [ ] Verify all executions logged
- [ ] Test rollback on execution failure
- [ ] Verify audit trail completeness
- [ ] Performance test: 100 proposals in queue

#### Success Metrics:

- **Approval Speed:** <1 second from click to execution start
- **Reliability:** 99.9% of approved actions execute successfully
- **Audit Trail:** 100% of actions logged with context
- **UI Responsiveness:** <100ms for queue updates

---

### Phase 3: Daily Activity Queries
**Status:** 0% Complete
**Priority:** MEDIUM
**Est. Duration:** 1-2 weeks
**Start Date:** ~November 10, 2025

#### Core Features to Build:

- [ ] **Activity Tracker** (`GP-RAG/activity_tracker.py`)
- [ ] **Time-Series Queries** (today, week, month)
- [ ] **Aggregation Functions** (count, sum, group by)
- [ ] **Dashboard Widgets** (charts, stats, trends)
- [ ] **Query Performance Optimization**

#### Testing Checklist:

- [ ] Query 10,000+ actions - sub-2 second response
- [ ] Test edge cases (no data, future dates)
- [ ] Verify aggregations mathematically correct
- [ ] Load test: 100 concurrent queries

---

### Phase 4: Email & Reporting System
**Status:** 0% Complete
**Priority:** MEDIUM
**Est. Duration:** 2-3 weeks
**Start Date:** ~November 25, 2025

#### Core Features to Build:

- [ ] **SMTP Integration** (`GP-AI/notifications/email_client.py`)
- [ ] **PDF Generation** (ReportLab library)
- [ ] **Compliance Templates** (SOC2, PCI, HIPAA)
- [ ] **Chart Generation** (matplotlib)
- [ ] **Scheduling System** (daily, weekly reports)

#### Testing Checklist:

- [ ] Send 100 emails successfully
- [ ] Generate 10 PDFs with charts
- [ ] Verify compliance report accuracy
- [ ] Test schedule reliability

---

### Phase 5: Git Integration
**Status:** 0% Complete
**Priority:** LOW
**Est. Duration:** 1-2 weeks
**Start Date:** ~December 15, 2025

#### Core Features to Build:

- [ ] **Git Commit Automation** (`GP-PLATFORM/integrations/git_integration.py`)
- [ ] **PR Creation** (GitHub API)
- [ ] **Branch Management** (feature branches)
- [ ] **Policy Versioning** (track changes over time)

#### Testing Checklist:

- [ ] Auto-commit 50 approved policies
- [ ] Create 10 PRs successfully
- [ ] Verify version tracking accuracy

---

## 🎯 CRITICAL PATH

```
Phase 1 (RAG Auto-Sync)
    ↓
    └─→ Phase 2 (Approval Workflow) ← BLOCKS Phase 4 & 5
            ↓
            ├─→ Phase 3 (Activity Queries) ← Parallel with Phase 4
            └─→ Phase 4 (Email/Reports)     ← Parallel with Phase 3
                    ↓
                    └─→ Phase 5 (Git Integration) ← Final phase
```

**Critical Path:** Phase 1 → Phase 2 are blockers for everything else.

---

## 📊 OVERALL PROGRESS

| Phase | Status | Progress | Priority | Dependencies |
|-------|--------|----------|----------|--------------|
| Phase 0: Foundation | ✅ Complete | 100% | - | None |
| Phase 1: RAG Auto-Sync | ✅ Complete | 100% | CRITICAL | Phase 0 |
| Phase 2: Approval Workflow | 🔄 Next | 0% | HIGH | Phase 1 |
| Phase 3: Activity Queries | ⏳ Planned | 0% | MEDIUM | Phase 1 |
| Phase 4: Email/Reports | ⏳ Planned | 0% | MEDIUM | Phase 2 |
| Phase 5: Git Integration | ⏳ Planned | 0% | LOW | Phase 2 |

**Overall Completion:** 33.3% (2/6 phases complete)

---

## 🚀 NEXT STEPS (Starting October 1, 2025)

### This Week (Week of Oct 1):
1. Build file system watcher with watchdog library
2. Implement auto-ingestion for .tf, .yaml, .rego files
3. Test with 100 sample files

### Next Week (Week of Oct 8):
1. Add metadata extraction for all file types
2. Build activity database schema
3. Implement basic time queries

### Week 3 (Week of Oct 15):
1. Build query interface API endpoints
2. Create dashboard UI components
3. Integration testing

---

## 🎯 DEFINITION OF DONE

### Phase 1 Complete When: ✅ ALL DONE
- [x] Manager can ask "What did we do today?" and get accurate results
- [x] All file changes auto-sync to RAG within 2 seconds
- [x] Works 100% offline
- [x] Passed all testing checklists
- [x] Documentation updated

### Phase 2 Complete When:
- [ ] Manager can review and approve Jade's suggestions in GUI
- [ ] One-click approve/reject with visual diff
- [ ] All approvals logged for compliance
- [ ] Execution pipeline works with rollback
- [ ] Audit trail complete

---

## 📝 NOTES & DECISIONS

### September 30, 2025
- **Decision:** Stick with monolithic architecture (not microservices)
- **Rationale:** Desktop app, offline operation, simpler deployment
- **Impact:** All phases build on single codebase

### Architecture Principles:
1. **Local-first:** Everything runs on manager's machine
2. **Offline:** No cloud dependencies after installation
3. **Fast:** Sub-2 second response for any query
4. **Simple:** One installer, one process, one database

---

**For detailed architecture, see [VISION.md](VISION.md)**
**For quick reference, see [.claude/architecture-rules.md](.claude/architecture-rules.md)**