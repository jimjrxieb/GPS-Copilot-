"""
GP-JADE FastAPI Server
RESTful API for AI Security Analysis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.ai_security_engine import ai_security_engine
from core.rag_engine import rag_engine

# Import approval routes
from api.approval_routes import router as approval_router
# Import secrets routes
from api.secrets_routes import router as secrets_router

app = FastAPI(
    title="GP-JADE AI Security API",
    description="AI-Powered Security Consulting and Analysis",
    version="2.0.0"
)

# Include approval queue routes
app.include_router(approval_router)
# Include secrets management routes
app.include_router(secrets_router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ScanRequest(BaseModel):
    project_path: str = Field(..., description="Path to project to scan")
    client: Optional[str] = Field(None, description="Client name")
    scan_type: str = Field("auto", description="Scan type: auto, terraform, kubernetes")
    depth: str = Field("comprehensive", description="Analysis depth: quick, focused, comprehensive")
    industry: Optional[str] = Field(None, description="Client industry")
    compliance: Optional[List[str]] = Field(None, description="Compliance requirements")

class QueryRequest(BaseModel):
    question: str = Field(..., description="Security question")
    client: Optional[str] = Field(None, description="Client context")
    context: Optional[str] = Field(None, description="Additional context")

class ScanResponse(BaseModel):
    success: bool
    client: Optional[str]
    findings_count: int
    confidence: float
    summary: str
    findings: List[Dict[str, Any]]
    compliance_guidance: Optional[str]

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, bool]
    stats: Dict[str, Any]

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "service": "GP-JADE AI Security API",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check RAG engine
        rag_stats = rag_engine.get_stats()
        rag_healthy = rag_stats.get("total_documents", 0) > 0

        # Check AI engine
        ai_healthy = ai_security_engine is not None

        return HealthResponse(
            status="healthy" if (rag_healthy and ai_healthy) else "degraded",
            services={
                "rag_engine": rag_healthy,
                "ai_engine": ai_healthy,
                "vector_db": rag_healthy
            },
            stats=rag_stats
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")

@app.post("/api/v1/scan", response_model=ScanResponse)
async def scan_project(request: ScanRequest):
    """
    Scan a project for security vulnerabilities
    """
    try:
        # Verify project path exists
        project_path = Path(request.project_path)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail=f"Project path not found: {request.project_path}")

        # Perform AI security analysis
        analysis = await ai_security_engine.analyze_project(
            str(project_path),
            request.client or "unknown",
            analysis_depth=request.depth,
            industry=request.industry,
            compliance_requirements=request.compliance
        )

        # Format findings
        findings = [
            {
                "severity": f.severity,
                "category": f.category,
                "file_path": f.file_path,
                "line_number": f.line_number,
                "description": f.description,
                "impact": f.impact,
                "recommendation": f.recommendation,
                "compliance": f.compliance_frameworks,
                "confidence": f.ai_confidence
            }
            for f in analysis.findings[:20]  # Limit to top 20 findings
        ]

        return ScanResponse(
            success=True,
            client=request.client,
            findings_count=len(analysis.findings),
            confidence=analysis.confidence_score,
            summary=analysis.ai_summary,
            findings=findings,
            compliance_guidance=analysis.compliance_guidance
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

@app.post("/api/v1/query", response_model=QueryResponse)
async def query_expert(request: QueryRequest):
    """
    Query AI security expert with RAG context
    """
    try:
        # Query with RAG context
        response = await ai_security_engine.query_security_expert(
            request.question,
            request.client
        )

        # Get relevant knowledge sources
        sources = rag_engine.query_knowledge(request.question, n_results=3)

        return QueryResponse(
            question=request.question,
            answer=response,
            sources=[
                {
                    "content": s["content"][:200],
                    "collection": s["collection"],
                    "relevance": 1 - s["distance"]
                }
                for s in sources
            ]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/api/v1/ingest")
async def ingest_project(
    project_path: str,
    client: str,
    background_tasks: BackgroundTasks
):
    """
    Ingest project documentation into knowledge base
    """
    try:
        # Verify project exists
        if not Path(project_path).exists():
            raise HTTPException(status_code=404, detail="Project path not found")

        # Run ingestion in background
        background_tasks.add_task(
            rag_engine.ingest_client_project,
            project_path,
            client
        )

        return {
            "status": "ingestion_started",
            "project": project_path,
            "client": client
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.get("/api/v1/knowledge/stats")
async def knowledge_stats():
    """
    Get knowledge base statistics
    """
    try:
        stats = rag_engine.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.post("/api/v1/knowledge/load/{knowledge_type}")
async def load_knowledge(knowledge_type: str):
    """
    Load built-in knowledge bases (cks, compliance)
    """
    try:
        if knowledge_type == "cks":
            rag_engine.load_cks_knowledge()
            return {"status": "success", "type": "cks"}
        elif knowledge_type == "compliance":
            rag_engine.load_compliance_frameworks()
            return {"status": "success", "type": "compliance"}
        else:
            raise HTTPException(status_code=400, detail="Invalid knowledge type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Load failed: {str(e)}")

@app.get("/api/v1/opa/validate")
async def opa_validate(policy: str = "gp.security"):
    """
    Validate OPA connection and policies
    """
    import os
    import httpx

    opa_url = os.getenv("OPA_URL", "http://opa:8181")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{opa_url}/health")
            return {
                "opa_healthy": response.status_code == 200,
                "policy": policy,
                "url": opa_url
            }
    except Exception as e:
        return {
            "opa_healthy": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)