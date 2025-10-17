#!/usr/bin/env python3
"""
GuidePoint Agent API Gateway
=========================

Unified API gateway for accessing specialized security agents.
Routes requests to appropriate agents based on capability domains.

Agent Routing:
- /scanner/* → Scanner Agent (vulnerability detection & remediation)
- /kubernetes/* → Kubernetes Agent (cluster security & RBAC)
- /iac/* → IaC/Policy Agent (Terraform & policy management)
- /devsecops/* → DevSecOps Agent (CI/CD security)
- /consulting/* → Consulting Agent (client engagement)
"""

import os
import sys
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

# Add GuidePoint to path
sys.path.insert(0, '/home/jimmie/linkops-industries/James-OS/guidepoint')

# Import available agents
from agents.scanner_agent.agent import ScannerAgent

# Pydantic models for API
class AnalysisRequest(BaseModel):
    project_path: str
    agent_type: Optional[str] = "scanner"
    options: Optional[Dict[str, Any]] = {}

class RemediationRequest(BaseModel):
    project_path: str
    agent_type: Optional[str] = "scanner"
    auto_approve: Optional[bool] = False

class AgentStatus(BaseModel):
    agent_id: str
    status: str
    capabilities: List[str]
    last_activity: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="GuidePoint Agent Gateway",
    description="Unified API for specialized security agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent registry
class AgentRegistry:
    """Registry of available agents and their capabilities"""

    def __init__(self):
        self.agents = {
            "scanner": {
                "class": ScannerAgent,
                "instance": None,
                "capabilities": [
                    "vulnerability_scanning",
                    "container_security",
                    "dependency_analysis",
                    "automated_remediation"
                ],
                "status": "available"
            }
            # Future agents will be added here:
            # "kubernetes": {...},
            # "iac": {...},
            # "devsecops": {...},
            # "consulting": {...}
        }

    def get_agent(self, agent_type: str):
        """Get or create agent instance"""
        if agent_type not in self.agents:
            raise HTTPException(status_code=404, detail=f"Agent type '{agent_type}' not found")

        agent_config = self.agents[agent_type]

        if agent_config["instance"] is None:
            agent_config["instance"] = agent_config["class"]()

        return agent_config["instance"]

    def get_available_agents(self) -> List[str]:
        """Get list of available agent types"""
        return list(self.agents.keys())

    def get_agent_capabilities(self, agent_type: str) -> List[str]:
        """Get capabilities for specific agent"""
        if agent_type not in self.agents:
            return []
        return self.agents[agent_type]["capabilities"]

# Global agent registry
agent_registry = AgentRegistry()

# API Routes

@app.get("/")
async def root():
    """API gateway status and available agents"""
    return {
        "service": "GuidePoint Agent Gateway",
        "status": "operational",
        "available_agents": agent_registry.get_available_agents(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/agents")
async def list_agents():
    """List all available agents and their capabilities"""
    agents_info = {}

    for agent_type in agent_registry.get_available_agents():
        agents_info[agent_type] = {
            "capabilities": agent_registry.get_agent_capabilities(agent_type),
            "status": "available"
        }

    return {
        "agents": agents_info,
        "total_agents": len(agents_info)
    }

@app.get("/agents/{agent_type}/status")
async def get_agent_status(agent_type: str):
    """Get status of specific agent"""
    try:
        agent = agent_registry.get_agent(agent_type)

        if hasattr(agent, 'get_agent_status'):
            status = agent.get_agent_status()
        else:
            status = {
                "agent_id": agent_type,
                "status": "operational",
                "capabilities": agent_registry.get_agent_capabilities(agent_type)
            }

        return status

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scanner/analyze")
async def scanner_analyze(request: AnalysisRequest):
    """Scanner Agent: Analyze project for vulnerabilities"""
    try:
        # Validate project path
        if not os.path.exists(request.project_path):
            raise HTTPException(status_code=400, detail=f"Project path does not exist: {request.project_path}")

        # Get Scanner Agent
        scanner = agent_registry.get_agent("scanner")

        # Execute analysis
        result = await scanner.analyze_project(request.project_path)

        return {
            "status": "success",
            "agent": "scanner",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/scanner/remediate")
async def scanner_remediate(request: RemediationRequest):
    """Scanner Agent: Execute autonomous remediation"""
    try:
        # Validate project path
        if not os.path.exists(request.project_path):
            raise HTTPException(status_code=400, detail=f"Project path does not exist: {request.project_path}")

        # Get Scanner Agent
        scanner = agent_registry.get_agent("scanner")

        # Execute remediation
        result = await scanner.execute_autonomous_remediation(request.project_path)

        return {
            "status": "success",
            "agent": "scanner",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Remediation failed: {str(e)}")

@app.post("/analyze")
async def universal_analyze(request: AnalysisRequest):
    """Universal analysis endpoint - routes to appropriate agent"""
    try:
        agent_type = request.agent_type or "scanner"

        if agent_type == "scanner":
            return await scanner_analyze(request)
        else:
            raise HTTPException(status_code=501, detail=f"Agent type '{agent_type}' not yet implemented")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/remediate")
async def universal_remediate(request: RemediationRequest):
    """Universal remediation endpoint - routes to appropriate agent"""
    try:
        agent_type = request.agent_type or "scanner"

        if agent_type == "scanner":
            return await scanner_remediate(request)
        else:
            raise HTTPException(status_code=501, detail=f"Agent type '{agent_type}' not yet implemented")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Future agent endpoints will be added here:
# @app.post("/kubernetes/harden")
# @app.post("/iac/analyze")
# @app.post("/devsecops/scan-pipeline")
# @app.post("/consulting/generate-report")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test that we can instantiate Scanner Agent
        scanner = agent_registry.get_agent("scanner")

        return {
            "status": "healthy",
            "agents_operational": len(agent_registry.get_available_agents()),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting GuidePoint Agent Gateway")
    print("Available agents:", agent_registry.get_available_agents())

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )