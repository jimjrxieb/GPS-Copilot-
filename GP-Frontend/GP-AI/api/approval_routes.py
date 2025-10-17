"""
FastAPI routes for approval queue management
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from approval.state_machine import (
    ApprovalStateMachine,
    Proposal,
    ProposalState,
    ProposalPriority,
    ProposalType
)

router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])

# Initialize state machine
state_machine = ApprovalStateMachine()


class ApprovalRequest(BaseModel):
    """Request model for approvals"""
    approved_by: str
    notes: Optional[str] = None


class RejectionRequest(BaseModel):
    """Request model for rejections"""
    rejected_by: str
    reason: str


@router.get("/pending")
async def get_pending_approvals():
    """Get all pending approval proposals"""
    try:
        proposals = state_machine.db.list_proposals(
            state=ProposalState.PENDING,
            limit=100
        )

        return {
            "success": True,
            "count": len(proposals),
            "proposals": [p.to_dict() for p in proposals]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{proposal_id}")
async def get_proposal(proposal_id: str):
    """Get a specific proposal by ID"""
    try:
        proposal = state_machine.db.get_proposal(proposal_id)

        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")

        return {
            "success": True,
            "proposal": proposal.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{proposal_id}/approve")
async def approve_proposal(proposal_id: str, request: ApprovalRequest):
    """Approve a proposal"""
    try:
        # Validate proposal exists
        proposal = state_machine.db.get_proposal(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")

        # Approve the proposal
        state_machine.approve(
            proposal_id=proposal_id,
            approved_by=request.approved_by,
            notes=request.notes
        )

        # Start execution
        state_machine.start_execution(proposal_id)

        return {
            "success": True,
            "message": "Proposal approved and execution started",
            "proposal_id": proposal_id,
            "approved_by": request.approved_by
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{proposal_id}/reject")
async def reject_proposal(proposal_id: str, request: RejectionRequest):
    """Reject a proposal"""
    try:
        # Validate proposal exists
        proposal = state_machine.db.get_proposal(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")

        # Reject the proposal
        state_machine.reject(
            proposal_id=proposal_id,
            rejected_by=request.rejected_by,
            reason=request.reason
        )

        return {
            "success": True,
            "message": "Proposal rejected",
            "proposal_id": proposal_id,
            "rejected_by": request.rejected_by
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{proposal_id}/audit")
async def get_audit_trail(proposal_id: str):
    """Get audit trail for a proposal"""
    try:
        # Validate proposal exists
        proposal = state_machine.db.get_proposal(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")

        # Get audit trail
        trail = state_machine.db.get_audit_trail(proposal_id)

        return {
            "success": True,
            "proposal_id": proposal_id,
            "trail": trail
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_all_proposals(
    state: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 100
):
    """Get all proposals with optional filters"""
    try:
        # Parse state and priority if provided
        state_filter = ProposalState(state) if state else None
        priority_filter = ProposalPriority(priority) if priority else None

        proposals = state_machine.db.list_proposals(
            state=state_filter,
            priority=priority_filter,
            limit=limit
        )

        return {
            "success": True,
            "count": len(proposals),
            "filters": {
                "state": state,
                "priority": priority,
                "limit": limit
            },
            "proposals": [p.to_dict() for p in proposals]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid filter value: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{proposal_id}/execute")
async def execute_proposal(proposal_id: str):
    """Manually trigger execution of an approved proposal"""
    try:
        # Validate proposal exists and is approved
        proposal = state_machine.db.get_proposal(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")

        if proposal.state != ProposalState.APPROVED.value:
            raise HTTPException(
                status_code=400,
                detail=f"Proposal must be approved before execution (current state: {proposal.state})"
            )

        # Start execution
        state_machine.start_execution(proposal_id)

        # TODO: Implement actual execution logic
        # For now, just mark as completed
        state_machine.complete_execution(proposal_id)

        return {
            "success": True,
            "message": "Proposal executed successfully",
            "proposal_id": proposal_id
        }
    except HTTPException:
        raise
    except Exception as e:
        state_machine.fail_execution(proposal_id, str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-expired")
async def check_expired_proposals():
    """Check and mark expired proposals"""
    try:
        state_machine.check_expired_proposals()

        return {
            "success": True,
            "message": "Expired proposals checked and updated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_approval_stats():
    """Get summary statistics for approval queue"""
    try:
        pending = state_machine.db.list_proposals(state=ProposalState.PENDING, limit=1000)
        approved = state_machine.db.list_proposals(state=ProposalState.APPROVED, limit=1000)
        rejected = state_machine.db.list_proposals(state=ProposalState.REJECTED, limit=1000)
        completed = state_machine.db.list_proposals(state=ProposalState.COMPLETED, limit=1000)
        failed = state_machine.db.list_proposals(state=ProposalState.FAILED, limit=1000)

        # Count by priority
        critical_count = len([p for p in pending if p.priority == ProposalPriority.CRITICAL.value])
        high_count = len([p for p in pending if p.priority == ProposalPriority.HIGH.value])
        medium_count = len([p for p in pending if p.priority == ProposalPriority.MEDIUM.value])
        low_count = len([p for p in pending if p.priority == ProposalPriority.LOW.value])

        return {
            "success": True,
            "stats": {
                "by_state": {
                    "pending": len(pending),
                    "approved": len(approved),
                    "rejected": len(rejected),
                    "completed": len(completed),
                    "failed": len(failed)
                },
                "by_priority": {
                    "critical": critical_count,
                    "high": high_count,
                    "medium": medium_count,
                    "low": low_count
                },
                "total_proposals": len(pending) + len(approved) + len(rejected) + len(completed) + len(failed)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
