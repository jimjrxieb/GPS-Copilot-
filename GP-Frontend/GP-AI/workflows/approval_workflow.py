"""
GP-JADE Approval State Machine
===============================

Manages the lifecycle of security fix proposals from creation to execution.

State Flow:
proposed → pending → approved → executing → completed
         ↓                ↓
      expired         rejected

Author: GP-JADE Team
Date: October 1, 2025
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
import json

from loguru import logger


class ProposalState(Enum):
    """Proposal lifecycle states"""
    PROPOSED = "proposed"      # Initial state - Jade creates proposal
    PENDING = "pending"        # Waiting for manager review
    APPROVED = "approved"      # Manager approved
    REJECTED = "rejected"      # Manager rejected
    EXECUTING = "executing"    # Currently executing
    COMPLETED = "completed"    # Successfully executed
    FAILED = "failed"          # Execution failed
    EXPIRED = "expired"        # Timeout - auto-expired


class ProposalType(Enum):
    """Types of proposals Jade can make"""
    OPA_POLICY = "opa_policy"
    GATEKEEPER_CONSTRAINT = "gatekeeper_constraint"
    TERRAFORM_FIX = "terraform_fix"
    KUBERNETES_PATCH = "kubernetes_patch"
    SECURITY_CONFIG = "security_config"
    VULNERABILITY_FIX = "vulnerability_fix"


class ProposalPriority(Enum):
    """Priority levels for proposals"""
    CRITICAL = "critical"  # Immediate attention (hardcoded secrets, public data)
    HIGH = "high"          # 24 hours (privileged containers, weak IAM)
    MEDIUM = "medium"      # 1 week (missing monitoring, outdated versions)
    LOW = "low"            # 1 month (documentation, best practices)


@dataclass
class Proposal:
    """A security fix proposal from Jade"""
    id: str
    title: str
    description: str
    proposal_type: str
    priority: str
    state: str

    # Context
    project: str
    file_path: str
    vulnerability: str
    severity: str

    # Proposed changes
    current_content: str
    proposed_content: str
    diff: str

    # Risk assessment
    risk_score: float
    affected_resources: int
    business_impact: str

    # Metadata
    created_at: str
    updated_at: str
    created_by: str = "Jade AI"
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    executed_at: Optional[str] = None
    expires_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Proposal':
        """Create from dictionary"""
        return cls(**data)


class ApprovalDatabase:
    """
    SQLite database for proposal tracking and audit trail
    """

    def __init__(self, db_path: str = "GP-DATA/audit/approval_log.db"):
        self.db_path = db_path
        self._ensure_directory()
        self._init_database()

    def _ensure_directory(self):
        """Ensure database directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Proposals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proposals (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                proposal_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                state TEXT NOT NULL,

                project TEXT NOT NULL,
                file_path TEXT NOT NULL,
                vulnerability TEXT NOT NULL,
                severity TEXT NOT NULL,

                current_content TEXT,
                proposed_content TEXT,
                diff TEXT,

                risk_score REAL,
                affected_resources INTEGER,
                business_impact TEXT,

                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                created_by TEXT NOT NULL,
                reviewed_by TEXT,
                review_notes TEXT,
                executed_at DATETIME,
                expires_at DATETIME
            )
        """)

        # State transitions table (audit trail)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_id TEXT NOT NULL,
                from_state TEXT NOT NULL,
                to_state TEXT NOT NULL,
                changed_by TEXT NOT NULL,
                changed_at DATETIME NOT NULL,
                reason TEXT,
                FOREIGN KEY (proposal_id) REFERENCES proposals(id)
            )
        """)

        # Execution log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_id TEXT NOT NULL,
                started_at DATETIME NOT NULL,
                completed_at DATETIME,
                status TEXT NOT NULL,
                output TEXT,
                error TEXT,
                rollback_performed INTEGER DEFAULT 0,
                FOREIGN KEY (proposal_id) REFERENCES proposals(id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_state ON proposals(state)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority ON proposals(priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_project ON proposals(project)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created ON proposals(created_at)")

        conn.commit()
        conn.close()
        logger.info(f"Approval database initialized: {self.db_path}")

    def insert_proposal(self, proposal: Proposal):
        """Insert new proposal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO proposals VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            proposal.id, proposal.title, proposal.description,
            proposal.proposal_type, proposal.priority, proposal.state,
            proposal.project, proposal.file_path, proposal.vulnerability,
            proposal.severity, proposal.current_content, proposal.proposed_content,
            proposal.diff, proposal.risk_score, proposal.affected_resources,
            proposal.business_impact, proposal.created_at, proposal.updated_at,
            proposal.created_by, proposal.reviewed_by, proposal.review_notes,
            proposal.executed_at, proposal.expires_at
        ))

        conn.commit()
        conn.close()
        logger.info(f"Proposal created: {proposal.id} - {proposal.title}")

    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """Get proposal by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Proposal(**dict(row))
        return None

    def update_proposal_state(self, proposal_id: str, new_state: ProposalState,
                             changed_by: str, reason: Optional[str] = None):
        """Update proposal state and log transition"""
        proposal = self.get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")

        old_state = proposal.state

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update proposal state
        cursor.execute("""
            UPDATE proposals
            SET state = ?, updated_at = ?
            WHERE id = ?
        """, (new_state.value, datetime.now().isoformat(), proposal_id))

        # Log state transition
        cursor.execute("""
            INSERT INTO state_transitions
            (proposal_id, from_state, to_state, changed_by, changed_at, reason)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            proposal_id, old_state, new_state.value, changed_by,
            datetime.now().isoformat(), reason
        ))

        conn.commit()
        conn.close()

        logger.info(f"State transition: {proposal_id} {old_state} → {new_state.value}")

    def list_proposals(self, state: Optional[ProposalState] = None,
                      priority: Optional[ProposalPriority] = None,
                      limit: int = 100) -> List[Proposal]:
        """List proposals with optional filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM proposals WHERE 1=1"
        params = []

        if state:
            query += " AND state = ?"
            params.append(state.value)

        if priority:
            query += " AND priority = ?"
            params.append(priority.value)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [Proposal(**dict(row)) for row in rows]

    def get_audit_trail(self, proposal_id: str) -> List[Dict[str, Any]]:
        """Get complete audit trail for a proposal"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM state_transitions
            WHERE proposal_id = ?
            ORDER BY changed_at ASC
        """, (proposal_id,))

        transitions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return transitions


class ApprovalStateMachine:
    """
    Manages proposal lifecycle and state transitions
    """

    def __init__(self):
        self.db = ApprovalDatabase()

        # Valid state transitions
        self.transitions = {
            ProposalState.PROPOSED: [ProposalState.PENDING, ProposalState.EXPIRED],
            ProposalState.PENDING: [ProposalState.APPROVED, ProposalState.REJECTED, ProposalState.EXPIRED],
            ProposalState.APPROVED: [ProposalState.EXECUTING],
            ProposalState.EXECUTING: [ProposalState.COMPLETED, ProposalState.FAILED],
            ProposalState.FAILED: [ProposalState.PENDING],  # Can retry
            ProposalState.REJECTED: [],  # Terminal state
            ProposalState.COMPLETED: [],  # Terminal state
            ProposalState.EXPIRED: [],   # Terminal state
        }

        logger.info("Approval state machine initialized")

    def create_proposal(self, proposal: Proposal) -> str:
        """Create new proposal in PROPOSED state"""
        proposal.state = ProposalState.PROPOSED.value
        proposal.created_at = datetime.now().isoformat()
        proposal.updated_at = proposal.created_at

        # Set expiration (24 hours for CRITICAL, 7 days for others)
        if proposal.priority == ProposalPriority.CRITICAL.value:
            expires_in = timedelta(hours=24)
        elif proposal.priority == ProposalPriority.HIGH.value:
            expires_in = timedelta(days=1)
        else:
            expires_in = timedelta(days=7)

        proposal.expires_at = (datetime.now() + expires_in).isoformat()

        self.db.insert_proposal(proposal)

        # Auto-transition to PENDING
        self.transition(proposal.id, ProposalState.PENDING, "Jade AI", "Auto-transition")

        return proposal.id

    def transition(self, proposal_id: str, new_state: ProposalState,
                  changed_by: str, reason: Optional[str] = None):
        """Transition proposal to new state"""
        proposal = self.db.get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")

        current_state = ProposalState(proposal.state)

        # Validate transition
        if new_state not in self.transitions[current_state]:
            raise ValueError(
                f"Invalid transition: {current_state.value} → {new_state.value}"
            )

        self.db.update_proposal_state(proposal_id, new_state, changed_by, reason)

    def approve(self, proposal_id: str, approved_by: str, notes: Optional[str] = None):
        """Approve a proposal"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE proposals
            SET reviewed_by = ?, review_notes = ?
            WHERE id = ?
        """, (approved_by, notes, proposal_id))

        conn.commit()
        conn.close()

        self.transition(proposal_id, ProposalState.APPROVED, approved_by, f"Approved: {notes}")
        logger.info(f"Proposal approved: {proposal_id} by {approved_by}")

    def reject(self, proposal_id: str, rejected_by: str, reason: str):
        """Reject a proposal"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE proposals
            SET reviewed_by = ?, review_notes = ?
            WHERE id = ?
        """, (rejected_by, reason, proposal_id))

        conn.commit()
        conn.close()

        self.transition(proposal_id, ProposalState.REJECTED, rejected_by, f"Rejected: {reason}")
        logger.info(f"Proposal rejected: {proposal_id} by {rejected_by}")

    def start_execution(self, proposal_id: str):
        """Mark proposal as executing"""
        self.transition(proposal_id, ProposalState.EXECUTING, "Jade AI", "Starting execution")

    def complete_execution(self, proposal_id: str):
        """Mark proposal as completed"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE proposals
            SET executed_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), proposal_id))

        conn.commit()
        conn.close()

        self.transition(proposal_id, ProposalState.COMPLETED, "Jade AI", "Execution successful")

    def fail_execution(self, proposal_id: str, error: str):
        """Mark proposal as failed"""
        self.transition(proposal_id, ProposalState.FAILED, "Jade AI", f"Execution failed: {error}")

    def check_expired_proposals(self):
        """Check for expired proposals and mark them"""
        now = datetime.now()

        pending_proposals = self.db.list_proposals(state=ProposalState.PENDING, limit=1000)

        for proposal in pending_proposals:
            if proposal.expires_at:
                expires = datetime.fromisoformat(proposal.expires_at)
                if now > expires:
                    self.transition(
                        proposal.id,
                        ProposalState.EXPIRED,
                        "System",
                        f"Expired at {proposal.expires_at}"
                    )
                    logger.warning(f"Proposal expired: {proposal.id}")


def main():
    """Test approval state machine"""
    from rich.console import Console
    from rich.table import Table
    import uuid

    console = Console()

    # Initialize state machine
    sm = ApprovalStateMachine()

    # Create test proposal
    proposal = Proposal(
        id=str(uuid.uuid4()),
        title="Fix hardcoded password in RDS",
        description="Replace hardcoded password with AWS Secrets Manager reference",
        proposal_type=ProposalType.TERRAFORM_FIX.value,
        priority=ProposalPriority.CRITICAL.value,
        state=ProposalState.PROPOSED.value,
        project="guidepoint-security-test",
        file_path="terraform/rds.tf",
        vulnerability="Hardcoded password",
        severity="CRITICAL",
        current_content='password = "GuidePoint2023!"',
        proposed_content='password = data.aws_secretsmanager_secret_version.db_password.secret_string',
        diff="- password = \"GuidePoint2023!\"\n+ password = data.aws_secretsmanager_secret_version.db_password.secret_string",
        risk_score=9.5,
        affected_resources=1,
        business_impact="Client database credentials exposed in code",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )

    # Create proposal
    proposal_id = sm.create_proposal(proposal)
    console.print(f"[green]✓[/green] Created proposal: {proposal_id}")

    # List pending proposals
    pending = sm.db.list_proposals(state=ProposalState.PENDING)
    console.print(f"\n[cyan]Pending proposals:[/cyan] {len(pending)}")

    table = Table(title="Approval Queue")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Priority", style="yellow")
    table.add_column("State", style="green")

    for p in pending[:5]:
        table.add_row(p.id[:8], p.title[:50], p.priority, p.state)

    console.print(table)

    # Get audit trail
    trail = sm.db.get_audit_trail(proposal_id)
    console.print(f"\n[cyan]Audit trail:[/cyan] {len(trail)} transitions")
    for t in trail:
        console.print(f"  {t['from_state']} → {t['to_state']} by {t['changed_by']}")


if __name__ == "__main__":
    main()
