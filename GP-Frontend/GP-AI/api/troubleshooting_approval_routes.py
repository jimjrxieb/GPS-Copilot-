#!/usr/bin/env python3
"""
Troubleshooting Workflow Approval Queue API

FastAPI routes for managing fix proposal approvals with WebSocket notifications

Features:
    - Submit fix proposals for approval
    - Get pending proposals
    - Approve/reject/request more info
    - WebSocket real-time notifications
    - Audit trail for all decisions
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import json
import uuid

router = APIRouter(prefix="/api/v1/troubleshooting/approvals", tags=["troubleshooting_approvals"])

# In-memory approval queue (replace with database in production)
approval_queue: Dict[str, Dict[str, Any]] = {}

# WebSocket connections (proposal_id -> list of websockets)
websocket_connections: Dict[str, List[WebSocket]] = {}


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class FixProposal(BaseModel):
    """Fix proposal model"""
    pod: str
    namespace: str
    container: str
    project: str
    root_cause: str
    proposed_solution: str
    kubectl_command: str
    risk_level: str  # LOW, MEDIUM, HIGH
    confidence: float  # 0.0-1.0
    rollback_plan: str
    pattern_detected: str
    solution_id: str
    based_on: Optional[str] = None
    diagnostics: Optional[Dict[str, Any]] = None


class FixProposalBatch(BaseModel):
    """Batch of fix proposals"""
    workflow_id: str
    project: str
    namespace: str
    proposals: List[FixProposal]
    summary: Optional[str] = None


class ApprovalDecision(BaseModel):
    """Approval decision model"""
    decision: str  # "approved", "rejected", "need_more_info"
    approved_by: str
    feedback: Optional[str] = None


class ProposalStatus(BaseModel):
    """Proposal status response"""
    proposal_id: str
    status: str
    timestamp: str
    approved_by: Optional[str] = None
    feedback: Optional[str] = None


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/submit")
async def submit_fix_proposals(batch: FixProposalBatch):
    """
    Submit a batch of fix proposals for approval

    Args:
        batch: FixProposalBatch with workflow_id and list of proposals

    Returns:
        Success response with proposal IDs
    """
    try:
        proposal_ids = []

        for proposal in batch.proposals:
            # Generate unique ID
            proposal_id = f"fix_{uuid.uuid4().hex[:12]}"

            # Store in queue
            approval_queue[proposal_id] = {
                "id": proposal_id,
                "workflow_id": batch.workflow_id,
                "project": batch.project,
                "namespace": batch.namespace,
                "proposal": proposal.dict(),
                "status": "pending",
                "submitted_at": datetime.now().isoformat(),
                "approved_by": None,
                "approved_at": None,
                "feedback": None
            }

            proposal_ids.append(proposal_id)

        # Notify WebSocket listeners
        await broadcast_update(batch.workflow_id, {
            "event": "proposals_submitted",
            "workflow_id": batch.workflow_id,
            "proposal_ids": proposal_ids,
            "count": len(proposal_ids)
        })

        return {
            "success": True,
            "workflow_id": batch.workflow_id,
            "proposal_ids": proposal_ids,
            "count": len(proposal_ids),
            "message": f"Submitted {len(proposal_ids)} proposals for approval"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit proposals: {str(e)}")


@router.get("/pending")
async def get_pending_proposals(project: Optional[str] = None):
    """
    Get all pending fix proposals

    Args:
        project: Optional project filter

    Returns:
        List of pending proposals
    """
    try:
        pending = [
            p for p in approval_queue.values()
            if p["status"] == "pending" and (not project or p["project"] == project)
        ]

        # Sort by risk level (HIGH first)
        risk_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        pending.sort(key=lambda p: risk_order.get(p["proposal"]["risk_level"], 3))

        return {
            "success": True,
            "count": len(pending),
            "proposals": pending
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending proposals: {str(e)}")


@router.get("/workflow/{workflow_id}")
async def get_workflow_proposals(workflow_id: str):
    """
    Get all proposals for a specific workflow

    Args:
        workflow_id: Workflow ID

    Returns:
        List of proposals for this workflow
    """
    try:
        workflow_proposals = [
            p for p in approval_queue.values()
            if p["workflow_id"] == workflow_id
        ]

        if not workflow_proposals:
            return {
                "success": True,
                "workflow_id": workflow_id,
                "count": 0,
                "proposals": [],
                "message": "No proposals found for this workflow"
            }

        return {
            "success": True,
            "workflow_id": workflow_id,
            "count": len(workflow_proposals),
            "proposals": workflow_proposals
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow proposals: {str(e)}")


@router.get("/{proposal_id}")
async def get_proposal(proposal_id: str):
    """
    Get a specific proposal by ID

    Args:
        proposal_id: Proposal ID

    Returns:
        Proposal details
    """
    if proposal_id not in approval_queue:
        raise HTTPException(status_code=404, detail="Proposal not found")

    return {
        "success": True,
        "proposal": approval_queue[proposal_id]
    }


@router.post("/{proposal_id}/decide")
async def make_decision(proposal_id: str, decision: ApprovalDecision):
    """
    Make a decision on a proposal (approve/reject/need_more_info)

    Args:
        proposal_id: Proposal ID
        decision: ApprovalDecision with decision and metadata

    Returns:
        Success response
    """
    if proposal_id not in approval_queue:
        raise HTTPException(status_code=404, detail="Proposal not found")

    proposal = approval_queue[proposal_id]

    if proposal["status"] != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Proposal already {proposal['status']}"
        )

    # Update proposal
    proposal["status"] = decision.decision
    proposal["approved_by"] = decision.approved_by
    proposal["approved_at"] = datetime.now().isoformat()
    proposal["feedback"] = decision.feedback

    # Notify WebSocket listeners
    await broadcast_update(proposal["workflow_id"], {
        "event": "decision_made",
        "proposal_id": proposal_id,
        "decision": decision.decision,
        "approved_by": decision.approved_by
    })

    return {
        "success": True,
        "proposal_id": proposal_id,
        "decision": decision.decision,
        "message": f"Proposal {decision.decision}"
    }


@router.post("/workflow/{workflow_id}/approve_all")
async def approve_all_workflow(workflow_id: str, approved_by: str):
    """
    Approve all proposals in a workflow

    Args:
        workflow_id: Workflow ID
        approved_by: User who approved

    Returns:
        Success response with count
    """
    try:
        workflow_proposals = [
            p for p in approval_queue.values()
            if p["workflow_id"] == workflow_id and p["status"] == "pending"
        ]

        for proposal in workflow_proposals:
            proposal["status"] = "approved"
            proposal["approved_by"] = approved_by
            proposal["approved_at"] = datetime.now().isoformat()

        # Notify WebSocket listeners
        await broadcast_update(workflow_id, {
            "event": "batch_approved",
            "workflow_id": workflow_id,
            "count": len(workflow_proposals),
            "approved_by": approved_by
        })

        return {
            "success": True,
            "workflow_id": workflow_id,
            "count": len(workflow_proposals),
            "message": f"Approved {len(workflow_proposals)} proposals"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve all: {str(e)}")


@router.post("/workflow/{workflow_id}/reject_all")
async def reject_all_workflow(workflow_id: str, rejected_by: str, reason: str):
    """
    Reject all proposals in a workflow

    Args:
        workflow_id: Workflow ID
        rejected_by: User who rejected
        reason: Rejection reason

    Returns:
        Success response with count
    """
    try:
        workflow_proposals = [
            p for p in approval_queue.values()
            if p["workflow_id"] == workflow_id and p["status"] == "pending"
        ]

        for proposal in workflow_proposals:
            proposal["status"] = "rejected"
            proposal["approved_by"] = rejected_by
            proposal["approved_at"] = datetime.now().isoformat()
            proposal["feedback"] = reason

        # Notify WebSocket listeners
        await broadcast_update(workflow_id, {
            "event": "batch_rejected",
            "workflow_id": workflow_id,
            "count": len(workflow_proposals),
            "rejected_by": rejected_by,
            "reason": reason
        })

        return {
            "success": True,
            "workflow_id": workflow_id,
            "count": len(workflow_proposals),
            "message": f"Rejected {len(workflow_proposals)} proposals"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject all: {str(e)}")


@router.get("/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """
    Get status summary for a workflow

    Args:
        workflow_id: Workflow ID

    Returns:
        Status summary
    """
    try:
        workflow_proposals = [
            p for p in approval_queue.values()
            if p["workflow_id"] == workflow_id
        ]

        if not workflow_proposals:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Count by status
        status_counts = {}
        for proposal in workflow_proposals:
            status = proposal["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        # Check if all approved
        all_approved = all(p["status"] == "approved" for p in workflow_proposals)
        any_rejected = any(p["status"] == "rejected" for p in workflow_proposals)

        return {
            "success": True,
            "workflow_id": workflow_id,
            "total": len(workflow_proposals),
            "status_counts": status_counts,
            "all_approved": all_approved,
            "any_rejected": any_rejected,
            "ready_for_execution": all_approved
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@router.websocket("/ws/{workflow_id}")
async def websocket_endpoint(websocket: WebSocket, workflow_id: str):
    """
    WebSocket endpoint for real-time proposal updates

    Args:
        websocket: WebSocket connection
        workflow_id: Workflow ID to monitor

    Sends:
        - proposals_submitted: When new proposals are submitted
        - decision_made: When a decision is made on a proposal
        - batch_approved: When all proposals are approved
        - batch_rejected: When all proposals are rejected
    """
    await websocket.accept()

    # Add to connections
    if workflow_id not in websocket_connections:
        websocket_connections[workflow_id] = []
    websocket_connections[workflow_id].append(websocket)

    try:
        # Send initial status
        workflow_proposals = [
            p for p in approval_queue.values()
            if p["workflow_id"] == workflow_id
        ]

        await websocket.send_json({
            "event": "connected",
            "workflow_id": workflow_id,
            "timestamp": datetime.now().isoformat(),
            "current_proposals": len(workflow_proposals)
        })

        # Keep connection alive and listen for client messages
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()

            # Client can send "ping" to keep connection alive
            if data == "ping":
                await websocket.send_json({
                    "event": "pong",
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        # Remove from connections
        if workflow_id in websocket_connections:
            websocket_connections[workflow_id].remove(websocket)
            if not websocket_connections[workflow_id]:
                del websocket_connections[workflow_id]


async def broadcast_update(workflow_id: str, message: Dict[str, Any]):
    """
    Broadcast update to all WebSocket connections for a workflow

    Args:
        workflow_id: Workflow ID
        message: Message to broadcast
    """
    if workflow_id not in websocket_connections:
        return

    # Add timestamp
    message["timestamp"] = datetime.now().isoformat()

    # Send to all connected clients
    disconnected = []

    for websocket in websocket_connections[workflow_id]:
        try:
            await websocket.send_json(message)
        except Exception:
            # Mark for removal
            disconnected.append(websocket)

    # Remove disconnected clients
    for websocket in disconnected:
        websocket_connections[workflow_id].remove(websocket)

    if not websocket_connections[workflow_id]:
        del websocket_connections[workflow_id]


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.delete("/workflow/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """
    Delete all proposals for a workflow (cleanup)

    Args:
        workflow_id: Workflow ID

    Returns:
        Success response
    """
    try:
        # Find and delete all proposals for this workflow
        to_delete = [
            pid for pid, p in approval_queue.items()
            if p["workflow_id"] == workflow_id
        ]

        for pid in to_delete:
            del approval_queue[pid]

        return {
            "success": True,
            "workflow_id": workflow_id,
            "deleted_count": len(to_delete),
            "message": f"Deleted {len(to_delete)} proposals"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")


@router.get("/stats/summary")
async def get_approval_stats():
    """
    Get summary statistics for approval queue

    Returns:
        Statistics summary
    """
    try:
        total = len(approval_queue)
        pending = len([p for p in approval_queue.values() if p["status"] == "pending"])
        approved = len([p for p in approval_queue.values() if p["status"] == "approved"])
        rejected = len([p for p in approval_queue.values() if p["status"] == "rejected"])
        need_more_info = len([p for p in approval_queue.values() if p["status"] == "need_more_info"])

        # Count by risk level
        high_risk = len([
            p for p in approval_queue.values()
            if p["proposal"]["risk_level"] == "HIGH" and p["status"] == "pending"
        ])
        medium_risk = len([
            p for p in approval_queue.values()
            if p["proposal"]["risk_level"] == "MEDIUM" and p["status"] == "pending"
        ])
        low_risk = len([
            p for p in approval_queue.values()
            if p["proposal"]["risk_level"] == "LOW" and p["status"] == "pending"
        ])

        return {
            "success": True,
            "stats": {
                "total": total,
                "by_status": {
                    "pending": pending,
                    "approved": approved,
                    "rejected": rejected,
                    "need_more_info": need_more_info
                },
                "pending_by_risk": {
                    "high": high_risk,
                    "medium": medium_risk,
                    "low": low_risk
                },
                "active_workflows": len(set(p["workflow_id"] for p in approval_queue.values())),
                "active_websockets": len(websocket_connections)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
