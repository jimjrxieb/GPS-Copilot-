#!/usr/bin/env python3
"""
📊 Metrics Routes - Evidence-backed metrics for James Edge AI
Aggregates real evidence files from disk, no demo data
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# ============================================================================
# Data Models
# ============================================================================

class MetricsSummary(BaseModel):
    """Metrics summary response"""
    success_total: int
    fail_total: int
    avg_duration_ms: float
    last_24h_count: int
    evidence_files_count: int
    processing_status: Dict[str, Any]
    scanner_stats: Dict[str, Any]

# ============================================================================
# Evidence Aggregation
# ============================================================================

def get_evidence_root_path(tenant: str = "default") -> Path:
    """Get evidence root path"""
    data_root = os.getenv("DATA_ROOT", "./data/tenants")
    return Path(data_root) / tenant / "evidence"

def aggregate_evidence_files(tenant: str = "default") -> Dict[str, Any]:
    """Aggregate metrics from evidence files on disk"""
    evidence_root = get_evidence_root_path(tenant)
    
    if not evidence_root.exists():
        return {
            "success_total": 0,
            "fail_total": 0,
            "total_duration_ms": 0,
            "evidence_count": 0,
            "last_24h_count": 0,
            "scanner_counts": {},
            "evidence_files": []
        }
    
    # Find all evidence JSON files
    evidence_files = list(evidence_root.rglob("*.json"))
    
    success_count = 0
    fail_count = 0
    total_duration = 0
    scanner_counts = {}
    last_24h_count = 0
    evidence_list = []
    
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    for evidence_file in evidence_files:
        try:
            with open(evidence_file, 'r') as f:
                evidence_data = json.load(f)
            
            job_result = evidence_data.get("job_result", {})
            output_data = evidence_data.get("output_data", {})
            
            # Count successes/failures
            status = job_result.get("status", "unknown")
            if status == "completed":
                success_count += 1
            elif status == "failed":
                fail_count += 1
            
            # Aggregate duration
            duration_ms = job_result.get("duration_ms", 0)
            total_duration += duration_ms
            
            # Count by scanner type
            scanner_type = output_data.get("tool", "unknown")
            scanner_counts[scanner_type] = scanner_counts.get(scanner_type, 0) + 1
            
            # Check if within last 24h
            created_at_str = job_result.get("created_at", "")
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    if created_at > cutoff_time:
                        last_24h_count += 1
                except:
                    pass
            
            # Add to evidence list
            evidence_list.append({
                "evidence_id": evidence_data.get("evidence_id"),
                "job_id": job_result.get("job_id"),
                "status": status,
                "tool": scanner_type,
                "duration_ms": duration_ms,
                "created_at": created_at_str,
                "file_path": str(evidence_file)
            })
        
        except Exception as e:
            print(f"Error processing evidence file {evidence_file}: {e}")
            continue
    
    return {
        "success_total": success_count,
        "fail_total": fail_count,
        "total_duration_ms": total_duration,
        "evidence_count": len(evidence_files),
        "last_24h_count": last_24h_count,
        "scanner_counts": scanner_counts,
        "evidence_files": evidence_list
    }

# ============================================================================
# FastAPI Router
# ============================================================================

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/summary")
async def get_metrics_summary(tenant: str = "default") -> MetricsSummary:
    """Get aggregated metrics from evidence files"""
    
    try:
        data = aggregate_evidence_files(tenant)
        
        # Calculate average duration
        avg_duration = 0.0
        if data["evidence_count"] > 0:
            avg_duration = data["total_duration_ms"] / data["evidence_count"]
        
        # Create processing status
        processing_status = {
            "edge_processing": True,
            "local_only": os.getenv("ALLOW_EXTERNAL_EGRESS", "0") == "0",
            "data_egress": False,
            "latency_ms": avg_duration
        }
        
        # Format scanner stats
        scanner_stats = {}
        for tool, count in data["scanner_counts"].items():
            scanner_stats[tool] = {
                "total_runs": count,
                "active": True,  # Assume active if we have recent runs
                "last_run": "recent"  # Could be enhanced with actual timestamps
            }
        
        return MetricsSummary(
            success_total=data["success_total"],
            fail_total=data["fail_total"],
            avg_duration_ms=avg_duration,
            last_24h_count=data["last_24h_count"],
            evidence_files_count=data["evidence_count"],
            processing_status=processing_status,
            scanner_stats=scanner_stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error aggregating metrics: {str(e)}")

@router.get("/evidence")
async def list_evidence_files(
    tenant: str = "default",
    limit: int = 100
):
    """List recent evidence files"""
    
    try:
        data = aggregate_evidence_files(tenant)
        
        # Sort by creation time, most recent first
        evidence_files = sorted(
            data["evidence_files"],
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        
        return {
            "success": True,
            "evidence_files": evidence_files[:limit],
            "total_count": len(evidence_files),
            "summary": {
                "success_total": data["success_total"],
                "fail_total": data["fail_total"],
                "evidence_count": data["evidence_count"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing evidence: {str(e)}")

@router.get("/health")
async def metrics_health():
    """Health check for metrics service"""
    
    evidence_root = get_evidence_root_path()
    
    return {
        "status": "healthy",
        "evidence_root_exists": evidence_root.exists(),
        "evidence_root_path": str(evidence_root),
        "test_mode": os.getenv("TEST") == "1",
        "edge_mode": os.getenv("ALLOW_EXTERNAL_EGRESS", "0") == "0"
    }