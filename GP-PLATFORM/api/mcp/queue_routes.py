#!/usr/bin/env python3
"""
⚡ Queue Routes - Job Queue Management for James Edge AI
Real job execution with evidence file generation
"""

import os
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel

# ============================================================================
# Data Models
# ============================================================================

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobType(str, Enum):
    SECURITY_SCAN = "security_scan"
    TRIVY_SCAN = "trivy_scan"
    KUBESCAPE_SCAN = "kubescape_scan"
    CHECKOV_SCAN = "checkov_scan"
    KUBE_BENCH = "kube_bench"

@dataclass
class JobResult:
    """Job execution result"""
    job_id: str
    status: JobStatus
    evidence_id: str
    output_summary: str
    stdout_sha256: str
    duration_ms: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class JobRequest(BaseModel):
    """API model for job requests"""
    type: JobType
    title: str
    description: str = ""
    target: Optional[str] = None  # target file/directory/image
    parameters: Dict[str, Any] = {}

class JobResponse(BaseModel):
    """API model for job responses"""
    job_id: str
    status: JobStatus
    evidence_id: Optional[str] = None
    message: str

# ============================================================================
# Evidence Storage
# ============================================================================

def get_evidence_path(tenant: str = "default") -> Path:
    """Get evidence storage path"""
    data_root = os.getenv("DATA_ROOT", "./data/tenants")
    base_path = Path(data_root) / tenant / "evidence"
    
    # Create date-based directory structure
    today = datetime.now()
    date_path = base_path / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
    date_path.mkdir(parents=True, exist_ok=True)
    
    return date_path

def write_evidence_file(evidence_id: str, job_result: JobResult, output_data: dict) -> str:
    """Write evidence file to disk"""
    evidence_path = get_evidence_path()
    evidence_file = evidence_path / f"{evidence_id}.json"
    
    evidence_data = {
        "evidence_id": evidence_id,
        "job_result": asdict(job_result),
        "output_data": output_data,
        "metadata": {
            "generated_by": "james-ms-006-executor",
            "edge_processing": True,
            "local_only": True
        }
    }
    
    with open(evidence_file, 'w') as f:
        json.dump(evidence_data, f, indent=2, default=str)
    
    return str(evidence_file)

# ============================================================================
# Job Queue Storage (In-Memory for Demo)
# ============================================================================

class JobStore:
    """In-memory job storage"""
    
    def __init__(self):
        self._jobs: Dict[str, JobResult] = {}
        self._counter = 0
    
    def create_job(self, job_type: JobType, title: str, description: str = "") -> str:
        """Create new job and return ID"""
        job_id = f"job_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        evidence_id = f"ev-{uuid.uuid4().hex[:12]}"
        
        job = JobResult(
            job_id=job_id,
            status=JobStatus.QUEUED,
            evidence_id=evidence_id,
            output_summary="",
            stdout_sha256="",
            duration_ms=0,
            created_at=datetime.now()
        )
        
        self._jobs[job_id] = job
        return job_id
    
    def get_job(self, job_id: str) -> Optional[JobResult]:
        """Get job by ID"""
        return self._jobs.get(job_id)
    
    def update_job(self, job_id: str, **updates) -> bool:
        """Update job fields"""
        if job_id not in self._jobs:
            return False
        
        job = self._jobs[job_id]
        for key, value in updates.items():
            if hasattr(job, key):
                setattr(job, key, value)
        
        return True
    
    def list_jobs(self, limit: int = 50) -> List[JobResult]:
        """List recent jobs"""
        jobs = sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)
        return jobs[:limit]

# Global job store
job_store = JobStore()

# ============================================================================
# Tool Execution
# ============================================================================

async def execute_trivy_scan(job_id: str, target: str = None) -> dict:
    """Execute Trivy security scan using real TrivyRunner"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.trivy_runner import TrivyRunner
    import hashlib

    # Use Portfolio as default target
    if not target:
        target = "/home/jimmie/linkops-industries/Portfolio"

    start_time = time.time()

    try:
        # Initialize TrivyRunner
        trivy_runner = TrivyRunner()

        # Determine scan type based on target
        if target.endswith(('.json', '.js', '.ts', '.py', 'package.json', 'requirements.txt')):
            # Filesystem scan for dependency files
            result = await trivy_runner.scan_filesystem(
                path=target,
                tenant="default",
                repo="portfolio",
                env="dev"
            )
        elif ':' in target and ('/' in target or target.count(':') == 1):
            # Container image scan
            result = await trivy_runner.scan_image(
                image=target,
                tenant="default",
                repo="portfolio",
                env="dev"
            )
        else:
            # Default to filesystem scan
            result = await trivy_runner.scan_filesystem(
                path=target,
                tenant="default",
                repo="portfolio",
                env="dev"
            )

        # Extract relevant data from OutputEnvelope result
        output_str = json.dumps(result, indent=2)
        stdout_hash = hashlib.sha256(output_str.encode()).hexdigest()

        return {
            "stdout": output_str,
            "stderr": "",
            "returncode": result.get("return_code", 0),
            "stdout_sha256": stdout_hash,
            "duration_ms": result.get("duration_ms", int((time.time() - start_time) * 1000)),
            "tool": "trivy",
            "target": target
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": 1,
            "stdout_sha256": "",
            "duration_ms": int((time.time() - start_time) * 1000),
            "tool": "trivy",
            "target": target,
            "error": str(e)
        }

async def execute_kubescape_scan(job_id: str, target: str = None) -> dict:
    """Execute Kubescape security scan using real KubescapeRunner"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.kubescape_runner import KubescapeRunner
    import hashlib

    # Use Portfolio K8s manifests as default target
    if not target:
        target = "/home/jimmie/linkops-industries/Portfolio/k8s"

    start_time = time.time()

    try:
        # Initialize KubescapeRunner
        kubescape_runner = KubescapeRunner()

        # Check if target is a directory with YAML files or a cluster scan
        if os.path.isdir(target) or target.endswith(('.yaml', '.yml')):
            # YAML file scan
            result = await kubescape_runner.scan_yaml(
                yaml_path=target,
                framework="nsa",
                tenant="default",
                repo="portfolio",
                env="dev"
            )
        else:
            # Cluster scan
            result = await kubescape_runner.scan_cluster(
                framework="nsa",
                namespace=None,
                tenant="default",
                cluster="portfolio",
                env="dev"
            )

        # Extract relevant data from OutputEnvelope result
        output_str = json.dumps(result, indent=2)
        stdout_hash = hashlib.sha256(output_str.encode()).hexdigest()

        return {
            "stdout": output_str,
            "stderr": "",
            "returncode": result.get("return_code", 0),
            "stdout_sha256": stdout_hash,
            "duration_ms": result.get("duration_ms", int((time.time() - start_time) * 1000)),
            "tool": "kubescape",
            "target": target
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": 1,
            "stdout_sha256": "",
            "duration_ms": int((time.time() - start_time) * 1000),
            "tool": "kubescape",
            "target": target,
            "error": str(e)
        }

async def execute_checkov_scan(job_id: str, target: str = None) -> dict:
    """Execute Checkov security scan using real CheckovRunner"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.checkov_runner import CheckovRunner
    import hashlib

    # Use Portfolio as default target
    if not target:
        target = "/home/jimmie/linkops-industries/Portfolio"

    start_time = time.time()

    try:
        # Initialize CheckovRunner
        checkov_runner = CheckovRunner()

        # Run Checkov scan
        result = await checkov_runner.scan_iac(
            path=target,
            tenant="default",
            repo="portfolio",
            env="dev"
        )

        # Extract relevant data from OutputEnvelope result
        output_str = json.dumps(result, indent=2)
        stdout_hash = hashlib.sha256(output_str.encode()).hexdigest()

        return {
            "stdout": output_str,
            "stderr": "",
            "returncode": result.get("return_code", 0),
            "stdout_sha256": stdout_hash,
            "duration_ms": result.get("duration_ms", int((time.time() - start_time) * 1000)),
            "tool": "checkov",
            "target": target
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": 1,
            "stdout_sha256": "",
            "duration_ms": int((time.time() - start_time) * 1000),
            "tool": "checkov",
            "target": target,
            "error": str(e)
        }

async def execute_job_async(job_id: str, job_type: JobType, target: str = None):
    """Execute job asynchronously"""

    # Update job to running
    job_store.update_job(job_id, status=JobStatus.RUNNING, started_at=datetime.now())

    try:
        # Execute based on job type using real tools
        if job_type == JobType.TRIVY_SCAN:
            output_data = await execute_trivy_scan(job_id, target)
        elif job_type == JobType.KUBESCAPE_SCAN:
            output_data = await execute_kubescape_scan(job_id, target)
        elif job_type == JobType.CHECKOV_SCAN:
            output_data = await execute_checkov_scan(job_id, target)
        elif job_type == JobType.SECURITY_SCAN:
            # Comprehensive security scan - run Trivy by default
            output_data = await execute_trivy_scan(job_id, target)
        else:
            # Fallback for unknown job types
            output_data = {
                "stdout": f"Unsupported job type: {job_type}",
                "stderr": f"Job type {job_type} not implemented",
                "returncode": 1,
                "stdout_sha256": "unknown",
                "duration_ms": 100,
                "tool": job_type.value,
                "target": target or "default",
                "error": f"Job type {job_type} not implemented"
            }
        
        # Update job with results
        job = job_store.get_job(job_id)
        if job:
            job_store.update_job(
                job_id,
                status=JobStatus.COMPLETED if output_data["returncode"] == 0 else JobStatus.FAILED,
                completed_at=datetime.now(),
                output_summary=f"Processed {len(output_data['stdout'])} bytes",
                stdout_sha256=output_data["stdout_sha256"],
                duration_ms=output_data["duration_ms"],
                error_message=output_data.get("error")
            )
            
            # Write evidence file
            updated_job = job_store.get_job(job_id)
            write_evidence_file(job.evidence_id, updated_job, output_data)
    
    except Exception as e:
        job_store.update_job(
            job_id,
            status=JobStatus.FAILED,
            completed_at=datetime.now(),
            error_message=str(e)
        )

# ============================================================================
# FastAPI Router
# ============================================================================

router = APIRouter(prefix="/mcp/queue", tags=["queue"])

@router.post("/create")
async def create_job(
    request: JobRequest,
    background_tasks: BackgroundTasks,
    tenant: str = Header("default", alias="X-Tenant")
):
    """Create and queue a new job"""
    
    try:
        # Create job
        job_id = job_store.create_job(request.type, request.title, request.description)
        
        # Start background execution
        background_tasks.add_task(
            execute_job_async, 
            job_id, 
            request.type, 
            request.target
        )
        
        job = job_store.get_job(job_id)
        
        return JobResponse(
            job_id=job_id,
            status=job.status,
            evidence_id=job.evidence_id,
            message=f"Job '{request.title}' queued successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{job_id}")
async def get_job(job_id: str):
    """Get job status and results"""
    
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "success": True,
        "job": {
            "job_id": job.job_id,
            "status": job.status,
            "evidence_id": job.evidence_id,
            "output_summary": job.output_summary,
            "duration_ms": job.duration_ms,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message
        }
    }

@router.get("/")
async def list_jobs(limit: int = 50):
    """List recent jobs"""
    
    jobs = job_store.list_jobs(limit)
    
    return {
        "success": True,
        "jobs": [
            {
                "job_id": job.job_id,
                "status": job.status,
                "evidence_id": job.evidence_id,
                "output_summary": job.output_summary,
                "duration_ms": job.duration_ms,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error_message": job.error_message
            }
            for job in jobs
        ],
        "count": len(jobs)
    }