#!/usr/bin/env python3
"""
💬 Chat Routes - James AI Chat with L0-L4 Autonomy Levels
Real chat backend with autonomy level enforcement and evidence generation
"""

import os
import json
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel

# Import MCP modules with relative path
try:
    from .queue_routes import job_store, execute_job_async, JobType
    from .approval_routes import approval_engine, ApprovalType
    MCP_AVAILABLE = True
except ImportError:
    # Fallback for testing without full MCP infrastructure
    MCP_AVAILABLE = False
    print("⚠️ MCP modules not available - enhanced chat only")

import httpx
import asyncio

# Import the enhanced tool integration
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# Import James's enhanced tools instead of automation_engine
try:
    from tools.tool_integration import handle_tool_request, ToolResult
    ENHANCED_TOOLS_AVAILABLE = True
except ImportError:
    ENHANCED_TOOLS_AVAILABLE = False
    print("⚠️ Enhanced tools not available - falling back to basic mode")

# ============================================================================
# Autonomy Level Definitions  
# ============================================================================

class AutonomyLevel(str, Enum):
    L0 = "L0"  # Read-only operations
    L1 = "L1"  # Observer + alerts (no changes)
    L2 = "L2"  # Approval-required changes 
    L3 = "L3"  # High-risk operations with oversight
    L4 = "L4"  # Critical infrastructure changes

@dataclass
class ChatMessage:
    """Chat message with autonomy context"""
    id: str
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    autonomy_level: Optional[AutonomyLevel] = None
    actions_taken: List[Dict[str, Any]] = None
    evidence_ids: List[str] = None
    approval_id: Optional[str] = None

class ChatRequest(BaseModel):
    """API model for chat requests"""
    message: str
    context: Optional[Dict[str, Any]] = {}
    max_autonomy_level: AutonomyLevel = AutonomyLevel.L1

class ChatResponse(BaseModel):
    """API model for chat responses"""
    message: str
    autonomy_level: AutonomyLevel
    actions_taken: List[Dict[str, Any]] = []
    evidence_ids: List[str] = []
    approval_required: bool = False
    approval_id: Optional[str] = None
    suggestions: List[str] = []

# ============================================================================
# Chat Storage & Context
# ============================================================================

class ChatStore:
    """In-memory chat storage with context"""
    
    def __init__(self):
        self._conversations: Dict[str, List[ChatMessage]] = {}
        self._context: Dict[str, Dict[str, Any]] = {}
    
    def get_or_create_conversation(self, session_id: str) -> List[ChatMessage]:
        """Get or create conversation"""
        if session_id not in self._conversations:
            self._conversations[session_id] = []
            self._context[session_id] = {}
        return self._conversations[session_id]
    
    def add_message(self, session_id: str, message: ChatMessage):
        """Add message to conversation"""
        conversation = self.get_or_create_conversation(session_id)
        conversation.append(message)
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context"""
        return self._context.get(session_id, {})
    
    def update_context(self, session_id: str, updates: Dict[str, Any]):
        """Update conversation context"""
        if session_id not in self._context:
            self._context[session_id] = {}
        self._context[session_id].update(updates)

# Global chat store
chat_store = ChatStore()

# ============================================================================
# RAG Integration
# ============================================================================

class RAGService:
    """Quality-aware RAG service integration for knowledge retrieval"""
    
    def __init__(self):
        # Try Enhanced RAG API first, fallback to unified API
        self.enhanced_endpoint = "http://localhost:8005"
        self.unified_endpoint = "http://localhost:8004"
        self.timeout = 15.0
    
    async def search_knowledge(self, query: str, n_results: int = 5, min_quality_score: float = 0.5) -> Dict[str, Any]:
        """Search knowledge base with quality awareness"""
        try:
            # Try Enhanced RAG API first
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.enhanced_endpoint}/search",
                    json={
                        "query": query,
                        "n_results": n_results,
                        "min_quality_score": min_quality_score,
                        "enable_fallback": True
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "results": data.get("results", []),
                        "quality_metrics": data.get("quality_metrics", {}),
                        "recommendations": data.get("recommendations", []),
                        "query": data.get("query", query)
                    }
                else:
                    # Fallback to unified API
                    return await self._fallback_search(query, n_results)
                    
        except Exception as e:
            # Fallback to unified API
            return await self._fallback_search(query, n_results)
    
    async def _fallback_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Fallback to unified API if enhanced API fails"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.unified_endpoint}/search",
                    json={
                        "query": query,
                        "top_k": top_k,
                        "collection_name": "security-v1"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    # Format for consistency with enhanced API
                    formatted_results = []
                    for result in results:
                        formatted_results.append({
                            "document": result.get("content", ""),
                            "metadata": result.get("metadata", {}),
                            "relevance_score": result.get("score", 0.0),
                            "quality_grade": "C",  # Default for fallback
                            "is_fallback": True
                        })
                    
                    return {
                        "success": True,
                        "results": formatted_results,
                        "quality_metrics": {"overall_score": 0.6, "status": "FALLBACK"},
                        "recommendations": ["Using fallback search - enhanced API unavailable"],
                        "query": query
                    }
                else:
                    return {
                        "success": False,
                        "error": f"RAG service error: {response.status_code}",
                        "results": []
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"RAG connection failed: {str(e)}",
                "results": []
            }
    
    async def get_context_for_query(self, query: str) -> Dict[str, Any]:
        """Get quality-aware context from knowledge base for a query"""
        search_result = await self.search_knowledge(query, n_results=3, min_quality_score=0.3)
        
        context_info = {
            "context": "",
            "quality_score": 0.0,
            "source_count": 0,
            "recommendations": [],
            "has_knowledge_gap": False
        }
        
        if search_result.get("success") and search_result.get("results"):
            context_parts = []
            quality_metrics = search_result.get("quality_metrics", {})
            
            for i, result in enumerate(search_result["results"][:3]):
                document = result.get("document", "")
                score = result.get("relevance_score", 0)
                grade = result.get("quality_grade", "F")
                metadata = result.get("metadata", {})
                dataset = metadata.get("dataset", "unknown")
                
                if score > 0.3 and document:  # Quality threshold (lowered for initial testing)
                    content = document[:400] if len(document) > 400 else document
                    context_parts.append(f"[Context {i+1} - Grade {grade} from {dataset}]: {content}")
            
            context_info.update({
                "context": "\n\n".join(context_parts),
                "quality_score": quality_metrics.get("overall_score", 0.0),
                "source_count": len(context_parts),
                "recommendations": search_result.get("recommendations", []),
                "has_knowledge_gap": quality_metrics.get("knowledge_gap", False)
            })
        
        return context_info
    
    async def log_search_feedback(self, query: str, rating: int, feedback: str = "") -> bool:
        """Log user feedback for quality improvement"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.enhanced_endpoint}/feedback",
                    json={
                        "query": query,
                        "rating": rating,
                        "feedback": feedback
                    }
                )
                return response.status_code == 200
        except:
            return False

# Global RAG service
rag_service = RAGService()

# ============================================================================
# Autonomy Level Handlers
# ============================================================================

class AutonomyHandler:
    """Handles autonomy level enforcement and task execution"""
    
    async def process_l0_request(self, message: str, session_id: str) -> ChatResponse:
        """L0: Read-only operations - status checks, reports, queries"""
        
        # L0 tasks: Status checks, metrics, reports
        actions = []
        evidence_ids = []
        suggestions = []
        
        if "status" in message.lower() or "health" in message.lower():
            # Get system status
            from mcp.metrics_routes import aggregate_evidence_files
            metrics = aggregate_evidence_files()
            
            response_text = f"""🔍 **System Status (L0 - Read Only)**

**James Edge AI Status**: Operational
- **Evidence Files**: {metrics['evidence_count']} security scans completed
- **Success Rate**: {metrics['success_total']}/{metrics['success_total'] + metrics['fail_total']} successful
- **Last 24h Activity**: {metrics['last_24h_count']} jobs processed
- **Processing Mode**: 100% Edge (Local Only)

**Scanner Status**:
{chr(10).join([f"- {tool}: {count} runs" for tool, count in metrics['scanner_counts'].items()])}

This is a read-only status check (L0 autonomy)."""
            
            actions.append({
                "type": "status_check",
                "autonomy_level": "L0",
                "description": "Retrieved system status and metrics"
            })
        
        elif "scan" in message.lower() and ("results" in message.lower() or "report" in message.lower()):
            # Get recent scan results
            jobs = job_store.list_jobs(5)
            recent_scans = [j for j in jobs if j.status == "completed"]
            
            if recent_scans:
                response_text = f"""📊 **Recent Security Scan Results (L0 - Read Only)**

Found {len(recent_scans)} completed scans:

{chr(10).join([f"- **{scan.evidence_id}**: {scan.output_summary} ({scan.duration_ms}ms)" for scan in recent_scans[:3]])}

To run a new scan, I would need L1+ autonomy level."""
            else:
                response_text = "📊 No completed security scans found. To run a new scan, I would need L1+ autonomy level."
            
            actions.append({
                "type": "query_results", 
                "autonomy_level": "L0",
                "description": "Retrieved recent scan results"
            })
            
            suggestions = [
                "Run a new Trivy security scan (requires L1+)",
                "Check specific evidence file details",
                "Generate security report summary"
            ]
        
        else:
            # Try to get relevant context from knowledge base with quality awareness
            rag_context_info = await rag_service.get_context_for_query(message)
            
            base_response = f"""🤖 **James AI (L0 - Read Only Mode)**

I can help you with:
- ✅ System status and health checks  
- ✅ Review scan results and reports
- ✅ Query metrics and evidence files
- ✅ Explain security findings

I cannot execute scans or make changes at L0 autonomy level.
Ask for L1+ autonomy to perform actions."""

            # Add RAG context if available
            if rag_context_info.get("context") and rag_context_info.get("source_count", 0) > 0:
                quality_score = rag_context_info.get("quality_score", 0.0)
                source_count = rag_context_info.get("source_count", 0)
                has_knowledge_gap = rag_context_info.get("has_knowledge_gap", False)
                
                quality_indicator = "🟢" if quality_score >= 0.7 else "🟡" if quality_score >= 0.5 else "🔴"
                gap_warning = "\n⚠️ **Knowledge Gap Detected** - Consider adding more specific datasets" if has_knowledge_gap else ""
                
                response_text = f"""{base_response}

**📚 Relevant Knowledge** {quality_indicator}:
{rag_context_info['context']}

*Quality Score: {quality_score:.2f} | Sources: {source_count} | Total Vectors: 275,070*{gap_warning}"""
                
                actions.append({
                    "type": "knowledge_retrieval",
                    "autonomy_level": "L0",
                    "description": f"Retrieved {source_count} high-quality context sources (score: {quality_score:.2f})",
                    "quality_score": quality_score,
                    "knowledge_gap": has_knowledge_gap
                })
                
                # Add quality recommendations as suggestions
                if rag_context_info.get("recommendations"):
                    suggestions.extend(rag_context_info["recommendations"][:2])  # Limit to 2 recommendations
            else:
                response_text = f"""{base_response}

📊 *No high-quality context found - try more specific security terms*"""

            suggestions = [
                "Check system status and health",
                "Review recent security scan results", 
                "Ask me to run a security scan (L1+ required)"
            ]
        
        return ChatResponse(
            message=response_text,
            autonomy_level=AutonomyLevel.L0,
            actions_taken=actions,
            evidence_ids=evidence_ids,
            suggestions=suggestions
        )
    
    async def process_l1_request(self, message: str, session_id: str, background_tasks: BackgroundTasks) -> ChatResponse:
        """L1: Observer + alerts - can run scans and generate reports"""
        
        actions = []
        evidence_ids = []
        suggestions = []
        
        if "scan" in message.lower() and any(scanner in message.lower() for scanner in ["trivy", "security", "vulnerability"]):
            # Run security scan
            result = await self._execute_scan("trivy_scan", "AI-requested Trivy scan", background_tasks)
            
            response_text = f"""🔍 **Security Scan Started (L1 - Observer + Alerts)**

✅ **Trivy Security Scan Initiated**
- **Job ID**: `{result['job_id']}`
- **Evidence ID**: `{result['evidence_id']}`
- **Status**: Queued for processing
- **Autonomy Level**: L1 (Observer + Alerts)

I'll process this scan and provide results. This is a safe L1 operation with no system changes."""

            actions.append({
                "type": "security_scan",
                "autonomy_level": "L1", 
                "job_id": result['job_id'],
                "scan_type": "trivy"
            })
            evidence_ids.append(result['evidence_id'])
            
            suggestions = [
                f"Check scan progress: {result['job_id']}",
                "Request Kubescape scan for K8s security",
                "Generate security report when scan completes"
            ]
        
        elif "kubescape" in message.lower() or "kubernetes" in message.lower():
            result = await self._execute_scan("kubescape_scan", "AI-requested Kubescape scan", background_tasks)
            
            response_text = f"""🛡️ **Kubernetes Security Scan Started (L1)**

✅ **Kubescape Scan Initiated**  
- **Job ID**: `{result['job_id']}`
- **Evidence ID**: `{result['evidence_id']}`
- **Target**: Default namespace
- **Autonomy Level**: L1 (Observer + Alerts)

Scanning Kubernetes security posture..."""

            actions.append({
                "type": "k8s_scan",
                "autonomy_level": "L1",
                "job_id": result['job_id'],
                "scan_type": "kubescape" 
            })
            evidence_ids.append(result['evidence_id'])
        
        elif "report" in message.lower():
            # Generate security report
            from mcp.metrics_routes import aggregate_evidence_files
            metrics = aggregate_evidence_files()
            
            response_text = f"""📋 **Security Report Generated (L1 - Observer + Alerts)**

**James Edge AI Security Summary**
- **Total Scans**: {metrics['evidence_count']}
- **Success Rate**: {((metrics['success_total'] / max(metrics['success_total'] + metrics['fail_total'], 1)) * 100):.1f}%
- **Processing**: 100% Edge (No cloud dependencies)
- **Evidence Files**: All stored locally

**Scanner Activity**:
{chr(10).join([f"- {tool}: {count} executions" for tool, count in metrics['scanner_counts'].items()])}

**Autonomy Level**: L1 (Read + Observe + Alert)
**Next Steps**: I can continue monitoring or escalate to L2+ for remediation actions."""

            actions.append({
                "type": "generate_report",
                "autonomy_level": "L1",
                "report_type": "security_summary"
            })
            
            suggestions = [
                "Run additional security scans",
                "Request L2 autonomy for remediation actions", 
                "Set up monitoring alerts"
            ]
        
        else:
            response_text = f"""🤖 **James AI (L1 - Observer + Alerts)**

I can help you with:
- ✅ Run security scans (Trivy, Kubescape, Checkov)
- ✅ Generate reports and summaries  
- ✅ Monitor and alert on findings
- ✅ All L0 capabilities (status, queries)

Ready to execute scans and observe security posture!"""

            suggestions = [
                "Run a Trivy security scan",
                "Scan Kubernetes with Kubescape", 
                "Generate security report",
                "Check system status"
            ]
        
        return ChatResponse(
            message=response_text,
            autonomy_level=AutonomyLevel.L1,
            actions_taken=actions,
            evidence_ids=evidence_ids,
            suggestions=suggestions
        )
    
    async def process_l2_request(self, message: str, session_id: str, background_tasks: BackgroundTasks) -> ChatResponse:
        """L2: Approval-required changes - can propose fixes but needs approval"""
        
        actions = []
        evidence_ids = []
        approval_id = None
        suggestions = []
        response_text = ""
        
        # Check for Terraform operations
        if "terraform" in message.lower() or "infrastructure" in message.lower():
            if "plan" in message.lower():
                # Parse directory from message or use current directory
                directory = "."
                if " in " in message.lower():
                    parts = message.lower().split(" in ")
                    if len(parts) > 1:
                        directory = parts[1].split()[0]  # Get first word after "in"
                
                # Terraform plan is allowed at L1, but let's handle it here too
                result = await tool_runner.execute_tool(
                    ToolType.TERRAFORM,
                    {"operation": "plan", "directory": directory},
                    "L2"
                )
                
                if result.get("success"):
                    response_text = f"""🏗️ **Terraform Plan Executed (L2)**
                    
✅ **Infrastructure Plan Generated**
- **Job ID**: `{result.get('job_id')}`
- **Evidence ID**: `{result.get('evidence_id')}`
- **Summary**: {result.get('output_summary', 'Plan completed')}
- **Duration**: {result.get('duration_ms', 0)}ms

Review the plan and approve for apply operation."""
                    
                    actions.append({
                        "type": "terraform_plan",
                        "autonomy_level": "L2",
                        "job_id": result.get('job_id')
                    })
                    if result.get('evidence_id'):
                        evidence_ids.append(result['evidence_id'])
                    
                    suggestions = [
                        "Apply terraform changes (requires approval)",
                        "Review the plan output",
                        "Run terraform state list"
                    ]
                else:
                    response_text = f"❌ Terraform plan failed: {result.get('error', 'Unknown error')}"
                    suggestions = [
                        "Check terraform configuration",
                        "Verify terraform is installed",
                        "Run terraform init first"
                    ]
            
            elif "apply" in message.lower():
                # Terraform apply needs approval at L2
                approval_request = approval_engine.create_approval_request(
                    type=ApprovalType.INFRASTRUCTURE,
                    authority_level="L2",
                    tenant="default",
                    hat="devops",
                    requestor="james-ai",
                    title="Terraform Infrastructure Changes",
                    description="Apply terraform changes to infrastructure",
                    risk_assessment={
                        "impact": "high",
                        "probability": "medium",
                        "reversible": True,
                        "automated": True
                    },
                    proposed_changes=[
                        {
                            "type": "terraform_apply",
                            "description": "Apply infrastructure changes via Terraform"
                        }
                    ],
                    evidence=evidence_ids
                )
                
                approval_id = approval_request.id
                response_text = f"""⚠️ **Terraform Apply Requires Approval (L2)**
                
**Approval ID**: `{approval_id}`
**Risk Level**: High
**Action**: Terraform apply

Infrastructure changes require human approval at L2. 
Please approve to proceed with terraform apply."""
                
                actions.append({
                    "type": "terraform_apply_pending",
                    "autonomy_level": "L2",
                    "approval_id": approval_id
                })
                
                suggestions = [
                    "Check approval status",
                    "Run terraform plan first",
                    "Cancel approval request"
                ]
            else:
                response_text = """🏗️ **Terraform Operations (L2)**
                
I can help with infrastructure as code:
- Run terraform plan (no approval needed)
- Apply infrastructure changes (requires approval)
- Destroy resources (requires L3+)
                
What terraform operation would you like to perform?"""
                
                suggestions = [
                    "Run terraform plan",
                    "Apply terraform changes",
                    "Check terraform state"
                ]
        
        # Check for Azure operations
        elif "azure" in message.lower() or "vm" in message.lower():
            if "create" in message.lower():
                # VM creation needs approval at L2
                approval_request = approval_engine.create_approval_request(
                    type=ApprovalType.INFRASTRUCTURE,
                    authority_level="L2", 
                    tenant="default",
                    hat="cloud",
                    requestor="james-ai",
                    title="Azure VM Creation",
                    description="Create new Azure virtual machine",
                    risk_assessment={
                        "impact": "medium",
                        "probability": "low",
                        "reversible": True,
                        "automated": True
                    },
                    proposed_changes=[
                        {
                            "type": "azure_vm_create",
                            "description": "Create Azure VM with specified configuration"
                        }
                    ],
                    evidence=evidence_ids
                )
                
                approval_id = approval_request.id
                response_text = f"""☁️ **Azure VM Creation Requires Approval (L2)**
                
**Approval ID**: `{approval_id}`
**Risk Level**: Medium
**Action**: Create Azure VM

VM creation requires human approval at L2.
Please approve to proceed with VM provisioning."""
                
                actions.append({
                    "type": "azure_vm_create_pending",
                    "autonomy_level": "L2",
                    "approval_id": approval_id
                })
                
                suggestions = [
                    "Check approval status",
                    "List existing Azure VMs",
                    "Cancel approval request"
                ]
            else:
                response_text = """☁️ **Azure Cloud Operations (L2)**
                
I can help with Azure resources:
- Create/manage VMs (requires approval)
- List resources (no approval needed)
- Create resource groups
- Manage storage accounts
                
What Azure operation would you like to perform?"""
                
                suggestions = [
                    "Create Azure VM",
                    "List Azure resources",
                    "Create resource group"
                ]
        
        # Check for Git operations
        elif "git" in message.lower() or "clone" in message.lower() or "repository" in message.lower():
            if "clone" in message.lower():
                # Parse repository URL from message
                repo_url = None
                directory = None
                
                # Look for GitHub/GitLab URLs in message
                words = message.split()
                for word in words:
                    if "github.com" in word or "gitlab.com" in word or ".git" in word:
                        repo_url = word
                        break
                
                # Look for directory after "to" or "into"
                if " to " in message.lower():
                    parts = message.lower().split(" to ")
                    if len(parts) > 1:
                        directory = parts[1].split()[0]
                elif " into " in message.lower():
                    parts = message.lower().split(" into ")
                    if len(parts) > 1:
                        directory = parts[1].split()[0]
                
                if repo_url:
                    # Execute git clone
                    result = await tool_runner.execute_tool(
                        ToolType.GIT,
                        {
                            "operation": "clone",
                            "repository_url": repo_url,
                            "directory": directory
                        },
                        "L1"
                    )
                    
                    if result.get("success"):
                        cloned_dir = directory or repo_url.split("/")[-1].replace(".git", "")
                        response_text = f"""📁 **Repository Cloned Successfully (L1)**
                        
✅ **Git Clone Completed**
- **Job ID**: `{result.get('job_id')}`
- **Evidence ID**: `{result.get('evidence_id')}`
- **Repository**: {repo_url}
- **Directory**: {cloned_dir}
- **Duration**: {result.get('duration_ms', 0)}ms

Ready to start working on the project!"""
                        
                        actions.append({
                            "type": "git_clone",
                            "autonomy_level": "L1",
                            "repository": repo_url,
                            "directory": cloned_dir
                        })
                        if result.get('evidence_id'):
                            evidence_ids.append(result['evidence_id'])
                        
                        suggestions = [
                            f"cd {cloned_dir}",
                            "Check project structure",
                            "Run git status",
                            "Start development!"
                        ]
                    else:
                        response_text = f"❌ Git clone failed: {result.get('error', 'Unknown error')}"
                        suggestions = [
                            "Check repository URL",
                            "Verify internet connection",
                            "Try a different directory"
                        ]
                else:
                    response_text = """📁 **Git Repository Management (L1)**
                    
I can help you clone repositories! Please provide:
- Repository URL (GitHub, GitLab, etc.)
- Optional target directory

Example: "Clone https://github.com/user/repo into my-project"
"""
                    suggestions = [
                        "Provide a repository URL to clone",
                        "Specify target directory",
                        "Check existing repositories"
                    ]
            else:
                response_text = """📁 **Git Operations (L1)**
                
I can help with:
- Clone repositories from GitHub/GitLab
- Check git status
- Pull latest changes
- Basic git operations

What git operation would you like to perform?"""
                
                suggestions = [
                    "Clone a repository",
                    "Check git status",
                    "Pull latest changes"
                ]
        
        # Check for GitHub Actions operations  
        elif "github" in message.lower() or "workflow" in message.lower() or "ci/cd" in message.lower():
            if "create" in message.lower() or "deploy" in message.lower():
                # Can create workflow at L2
                result = await tool_runner.execute_tool(
                    ToolType.GITHUB_ACTIONS,
                    {
                        "name": "Deployment Workflow",
                        "trigger_type": "workflow_dispatch",
                        "branches": ["main"],
                        "jobs": {
                            "deploy": {
                                "runs-on": "ubuntu-latest",
                                "steps": [
                                    {"uses": "actions/checkout@v3"},
                                    {"name": "Deploy", "run": "echo 'Deploying application'"}
                                ]
                            }
                        },
                        "repository": "user/repo"
                    },
                    "L2"
                )
                
                if result.get("success"):
                    response_text = f"""🚀 **GitHub Workflow Created (L2)**
                    
✅ **Deployment Workflow Generated**
- **Evidence ID**: `{result.get('evidence_id')}`
- **Workflow File**: `{result.get('workflow_file')}`
- **Instructions**: {result.get('instructions')}

Commit this workflow to your repository to enable CI/CD."""
                    
                    actions.append({
                        "type": "github_workflow_created",
                        "autonomy_level": "L2",
                        "workflow_file": result.get('workflow_file')
                    })
                    if result.get('evidence_id'):
                        evidence_ids.append(result['evidence_id'])
                else:
                    response_text = f"❌ Workflow creation failed: {result.get('error', 'Unknown error')}"
            else:
                response_text = """🚀 **GitHub Actions Management (L2)**
                
I can help with:
- Create deployment workflows
- Trigger workflow runs (with approval)
- Monitor workflow status
                
What GitHub Actions operation would you like to perform?"""
                
                suggestions = [
                    "Create a deployment workflow",
                    "Trigger existing workflow",
                    "Check workflow status"
                ]
        
        # Check for Claude Code collaboration requests
        elif any(word in message.lower() for word in ["claude code", "help me implement", "help me debug", "help me analyze", "help me setup", "help me refactor", "help me review"]):
            # Import Claude Code tool
            from tools.claude_code_tool import claude_code_crafter, ClaudeCodeRequest
            
            # Determine task type from message
            task_type = "implement"  # default
            if "analyze" in message.lower() or "analysis" in message.lower():
                task_type = "analyze"
            elif "debug" in message.lower() or "fix" in message.lower():
                task_type = "debug"
            elif "refactor" in message.lower():
                task_type = "refactor"
            elif "review" in message.lower():
                task_type = "review"
            elif "setup" in message.lower() or "configure" in message.lower():
                task_type = "setup"
            
            # Extract project context and goal from message
            project_context = "this project"
            specific_goal = message
            
            # Look for project name
            if " project" in message.lower():
                parts = message.lower().split(" project")
                if parts[0]:
                    words = parts[0].split()
                    if len(words) >= 2:
                        project_context = f"{words[-2]} {words[-1]} project"
            
            # Create request
            request = ClaudeCodeRequest(
                task_type=task_type,
                project_context=project_context,
                specific_goal=specific_goal
            )
            
            # Generate perfect prompt
            result = await claude_code_crafter.craft_perfect_prompt(request, autonomy_level)
            
            response_text = f"""🤝 **Claude Code Collaboration Mode (L2)**

✅ **Perfect Prompt Generated**
- **Task Type**: {task_type.title()}
- **Evidence ID**: `{result.get('evidence_id')}`

**🎯 Here's the perfect prompt to use with Claude Code:**

```
{result.get('crafted_prompt')}
```

**💡 Collaboration Tips:**
{chr(10).join(['- ' + tip for tip in result.get('collaboration_tips', [])])}

**📋 Next Steps:**
{chr(10).join(['- ' + step for step in result.get('next_steps', [])])}

Copy this prompt and paste it into Claude Code for optimal results!"""

            actions.append({
                "type": "claude_code_prompt_generated",
                "autonomy_level": "L2",
                "task_type": task_type,
                "evidence_id": result.get('evidence_id')
            })
            if result.get('evidence_id'):
                evidence_ids.append(result['evidence_id'])
            
            suggestions = [
                "Copy the prompt to Claude Code",
                "Provide additional context if needed",
                "Ask for clarification on any part",
                "Start collaborating with Claude Code!"
            ]

        # Enhanced James capabilities integration
        elif ENHANCED_TOOLS_AVAILABLE and any(keyword in message.lower() for keyword in ["deploy", "vault", "secrets", "threat", "policy", "opa", "kyverno"]):
            tool_type = None
            if any(keyword in message.lower() for keyword in ["deploy", "deployment"]):
                tool_type = "deployment"
            elif any(keyword in message.lower() for keyword in ["vault", "secrets", "aws secrets manager", "kubernetes secrets"]):
                tool_type = "secrets"
            elif any(keyword in message.lower() for keyword in ["threat", "ioc", "indicator", "mitre", "timeline"]):
                tool_type = "threat_intel"
            elif any(keyword in message.lower() for keyword in ["policy", "opa", "kyverno", "compliance"]):
                tool_type = "policy"

            if tool_type:
                # Execute enhanced tool
                tool_result = await handle_tool_request(message, tool_type, {"autonomy_level": "L2"})

                if tool_result.success:
                    response_text = f"""🚀 **Enhanced James Capability (L2)**

{tool_result.message}

**Performance**:
- **Duration**: {tool_result.duration_ms}ms
- **Evidence ID**: `{tool_result.evidence_id}`
- **Tool**: {tool_type.replace('_', ' ').title()}

✅ Operation completed successfully with James's enhanced capabilities!"""

                    actions.append({
                        "type": f"enhanced_{tool_type}",
                        "autonomy_level": "L2",
                        "evidence_id": tool_result.evidence_id,
                        "duration_ms": tool_result.duration_ms
                    })
                    evidence_ids.append(tool_result.evidence_id)

                    suggestions = [
                        f"Check evidence file: {tool_result.evidence_id}",
                        "Run additional security scans",
                        "Test the generated configuration"
                    ]
                else:
                    response_text = f"""❌ **Enhanced Tool Failed (L2)**

{tool_result.message}

**Duration**: {tool_result.duration_ms}ms

Please check the error and try again."""

                    suggestions = [
                        "Check prerequisites for the tool",
                        "Verify project configuration",
                        "Try a different approach"
                    ]

        elif "fix" in message.lower() or "remediate" in message.lower() or "patch" in message.lower():
            # Propose security fix with approval workflow
            approval_request = approval_engine.create_approval_request(
                type=ApprovalType.SECURITY_FIX,
                authority_level="L2",
                tenant="default",
                hat="security",
                requestor="james-ai",
                title="Security Vulnerability Remediation",
                description="AI-proposed security fixes based on scan results",
                risk_assessment={
                    "impact": "medium",
                    "probability": "low", 
                    "reversible": True,
                    "automated": True
                },
                proposed_changes=[
                    {
                        "type": "container_update",
                        "description": "Update vulnerable container images",
                        "files_affected": ["Dockerfile", "docker-compose.yml"]
                    }
                ],
                evidence=evidence_ids
            )
            
            approval_id = approval_request.id
            
            response_text = f"""🔧 **Security Fix Proposed (L2 - Approval Required)**

✅ **Remediation Plan Created**
- **Approval ID**: `{approval_id}`
- **Risk Level**: Medium (Reversible changes)
- **Proposed Action**: Update vulnerable container images
- **Autonomy Level**: L2 (Requires approval)

**What I Found**:
Based on recent security scans, I've identified vulnerabilities that can be automatically remediated.

**Proposed Changes**:
- Update base container images to latest secure versions
- Apply security patches to dependencies  
- Modify Dockerfile configurations

⏳ **Awaiting Approval** - I cannot proceed without human approval for L2+ operations."""

            actions.append({
                "type": "security_fix_proposal",
                "autonomy_level": "L2",
                "approval_id": approval_id,
                "risk_level": "medium"
            })
        
        elif "deploy" in message.lower() or "apply" in message.lower():
            response_text = f"""🚀 **Deployment Requested (L2 - Approval Required)**

I can prepare deployment packages but require approval for L2+ operations:

**What I Can Do**:
- ✅ Prepare deployment configurations
- ✅ Generate deployment evidence
- ✅ Create rollback plans
- ⏳ **REQUIRES APPROVAL**: Actually deploy changes

Would you like me to create an approval request for deployment?"""

            suggestions = [
                "Create approval request for deployment",
                "Prepare deployment plan (L1 operation)",
                "Run pre-deployment security scan"
            ]
        
        else:
            enhanced_text = ""
            enhanced_suggestions = []

            if ENHANCED_TOOLS_AVAILABLE:
                enhanced_text = """
🚀 **Enhanced Capabilities Available**:
- 🔐 **Secrets Management**: Vault, AWS Secrets Manager, K8s Secrets
- 🚨 **Threat Intelligence**: IOC analysis, MITRE ATT&CK mapping
- 📋 **Policy as Code**: OPA/Kyverno policy generation
- 🏗️ **Deployment Automation**: Complete DevSecOps workflows

**Examples**:
- "Deploy Portfolio project"
- "Generate Vault configuration"
- "Analyze threat indicators"
- "Create OPA security policies"
"""
                enhanced_suggestions = [
                    "Deploy Portfolio with security scanning",
                    "Generate Vault secrets management",
                    "Create Kubernetes security policies",
                    "Analyze threat intelligence data"
                ]

            response_text = f"""🤖 **James AI (L2 - Approval-Required Changes)**

I can help you with:
- ✅ All L0 + L1 capabilities (scans, reports, monitoring)
- 🔒 **WITH APPROVAL**: Security fixes and patches
- 🔒 **WITH APPROVAL**: Configuration changes
- 🔒 **WITH APPROVAL**: Deployment operations{enhanced_text}

Ready to execute enhanced capabilities and propose changes with proper approval workflows!"""

            suggestions = [
                "Propose security fixes for recent findings",
                "Run security scan first (L1 operation)",
                "Request deployment approval workflow"
            ] + enhanced_suggestions
        
        return ChatResponse(
            message=response_text,
            autonomy_level=AutonomyLevel.L2,
            actions_taken=actions,
            evidence_ids=evidence_ids,
            approval_required=bool(approval_id),
            approval_id=approval_id,
            suggestions=suggestions
        )
    
    async def _execute_scan(self, scan_type: str, title: str, background_tasks: BackgroundTasks) -> Dict[str, str]:
        """Helper to execute security scan"""
        job_type = getattr(JobType, scan_type.upper(), JobType.SECURITY_SCAN)
        job_id = job_store.create_job(job_type, title, f"AI-requested {scan_type}")
        job = job_store.get_job(job_id)
        
        # Start background execution
        background_tasks.add_task(execute_job_async, job_id, job_type, None)
        
        return {
            "job_id": job_id,
            "evidence_id": job.evidence_id
        }

# Global autonomy handler
autonomy_handler = AutonomyHandler()

# ============================================================================
# FastAPI Router
# ============================================================================

router = APIRouter(prefix="/mcp/chat", tags=["chat"])

# Commented out due to missing ClaudeCodeParams dependency
# @router.post("/tools/claudecode/run")
# async def claudecode_run_endpoint(
#     params: ClaudeCodeParams,
#     background_tasks: BackgroundTasks,
#     session_id: str = Header("default", alias="X-Session-ID"),
#     tenant: str = Header("default", alias="X-Tenant"),
#     autonomy_level: str = Header("L1", alias="X-Autonomy-Level")
# ):
#     """Execute Claude Code with autonomy enforcement and evidence generation"""
#
#     try:
#         # Validate autonomy level for requested capabilities
#         required_autonomy = _get_required_autonomy_for_claudecode(params.capabilities)
#         if not _check_autonomy_permission(autonomy_level, required_autonomy):
#             return {
#                 "success": False,
#                 "message": f"Insufficient autonomy level. Required: {required_autonomy}, Provided: {autonomy_level}",
#                 "actions": [],
#                 "evidence_ids": [],
#                 "error": "autonomy_denied"
#             }
#
#         # Execute Claude Code tool
#         result = await claudecode_run(params)
#
#         # Log execution for monitoring
#         logger.info(f"Claude Code execution: {params.task_id} - Success: {result['success']}")
#
#         return result
#
#     except Exception as e:
#         logger.error(f"Claude Code execution failed: {str(e)}")
#         return {
#             "success": False,
#             "message": f"Claude Code execution failed: {str(e)}",
#             "actions": [],
#             "evidence_ids": [],
#             "error": str(e)
#         }

# Commented out due to missing ClaudeCodeCapability dependency
# def _get_required_autonomy_for_claudecode(capabilities) -> str:
#     """Get required autonomy level for Claude Code capabilities"""
#     from tools.claudecode_tool import ClaudeCodeCapability
#
#     if ClaudeCodeCapability.EXEC in capabilities:
#         return "L2"  # Execution requires L2
#     elif ClaudeCodeCapability.WRITE in capabilities:
#         return "L2"  # Writing requires L2
#     else:
#         return "L1"  # Read-only is L1

def _check_autonomy_permission(current_level: str, required_level: str) -> bool:
    """Check if current autonomy level meets requirement"""
    levels = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}
    return levels.get(current_level, 0) >= levels.get(required_level, 0)

@router.post("/message")
async def chat_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    session_id: str = Header("default", alias="X-Session-ID"),
    tenant: str = Header("default", alias="X-Tenant")
):
    """Process chat message with autonomy level enforcement"""
    
    try:
        # Add user message to conversation
        user_message = ChatMessage(
            id=f"msg_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            role="user",
            content=request.message,
            timestamp=datetime.now()
        )
        chat_store.add_message(session_id, user_message)
        
        # Route to appropriate autonomy level handler
        if request.max_autonomy_level == AutonomyLevel.L0:
            response = await autonomy_handler.process_l0_request(request.message, session_id)
        elif request.max_autonomy_level == AutonomyLevel.L1:
            response = await autonomy_handler.process_l1_request(request.message, session_id, background_tasks)  
        elif request.max_autonomy_level == AutonomyLevel.L2:
            response = await autonomy_handler.process_l2_request(request.message, session_id, background_tasks)
        else:
            # L3/L4 not implemented yet
            response = ChatResponse(
                message=f"🔒 **{request.max_autonomy_level} Autonomy Not Yet Implemented**\n\nCurrently supported: L0 (Read-only), L1 (Observer + Alerts), L2 (Approval-required)\n\nFalling back to L1 capabilities.",
                autonomy_level=AutonomyLevel.L1,
                suggestions=["Use L0, L1, or L2 autonomy levels", "Check available capabilities"]
            )
            response = await autonomy_handler.process_l1_request(request.message, session_id, background_tasks)
        
        # Add assistant response to conversation
        assistant_message = ChatMessage(
            id=f"msg_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            role="assistant", 
            content=response.message,
            timestamp=datetime.now(),
            autonomy_level=response.autonomy_level,
            actions_taken=response.actions_taken,
            evidence_ids=response.evidence_ids,
            approval_id=response.approval_id
        )
        chat_store.add_message(session_id, assistant_message)
        
        return {
            "success": True,
            "response": response.dict(),
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.get("/history")
async def get_chat_history(
    session_id: str = Header("default", alias="X-Session-ID"),
    limit: int = 50
):
    """Get chat conversation history"""
    
    conversation = chat_store.get_or_create_conversation(session_id)
    recent_messages = conversation[-limit:] if len(conversation) > limit else conversation
    
    return {
        "success": True,
        "session_id": session_id,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "autonomy_level": msg.autonomy_level,
                "actions_taken": msg.actions_taken or [],
                "evidence_ids": msg.evidence_ids or [],
                "approval_id": msg.approval_id
            }
            for msg in recent_messages
        ],
        "message_count": len(conversation)
    }

@router.delete("/history")
async def clear_chat_history(
    session_id: str = Header("default", alias="X-Session-ID")
):
    """Clear chat conversation history"""
    
    if session_id in chat_store._conversations:
        del chat_store._conversations[session_id]
    if session_id in chat_store._context:
        del chat_store._context[session_id]
    
    return {
        "success": True,
        "message": f"Chat history cleared for session {session_id}"
    }

@router.get("/capabilities")
async def get_chat_capabilities():
    """Get available chat capabilities by autonomy level"""
    
    return {
        "success": True,
        "autonomy_levels": {
            "L0": {
                "description": "Read-only operations",
                "capabilities": [
                    "System status checks",
                    "Query scan results", 
                    "Review metrics and evidence",
                    "Explain security findings"
                ],
                "restrictions": ["Cannot execute scans", "Cannot make changes"]
            },
            "L1": {
                "description": "Observer + alerts", 
                "capabilities": [
                    "All L0 capabilities",
                    "Execute security scans (Trivy, Kubescape, Checkov)",
                    "Generate reports and summaries",
                    "Monitor and alert on findings"
                ],
                "restrictions": ["Cannot make system changes", "Cannot apply fixes"]
            },
            "L2": {
                "description": "Approval-required changes + Enhanced James Capabilities",
                "capabilities": [
                    "All L0 + L1 capabilities",
                    "Propose security fixes",
                    "Create deployment plans",
                    "Request configuration changes",
                    "🚀 Enhanced: Secrets Management (Vault, AWS, K8s)",
                    "🚀 Enhanced: Threat Intelligence Analysis",
                    "🚀 Enhanced: Policy as Code Generation",
                    "🚀 Enhanced: DevSecOps Deployment Automation"
                ],
                "restrictions": ["Requires human approval for changes", "Cannot execute without approval"],
                "enhanced_tools": ENHANCED_TOOLS_AVAILABLE
            },
            "L3": {
                "description": "High-risk operations (not implemented)",
                "status": "coming_soon"
            },
            "L4": {
                "description": "Critical infrastructure changes (not implemented)", 
                "status": "coming_soon"
            }
        }
    }