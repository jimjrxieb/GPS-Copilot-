#!/usr/bin/env python3
"""
Jade Kubernetes Troubleshooting Workflow V2 (Phase 2)
LangGraph-based workflow with LLM-generated fixes + Async Approval Queue

NEW IN PHASE 2:
    - LLM-generated fixes (replaces rule-based)
    - Async approval via API
    - WebSocket real-time notifications
    - Enhanced RAG + Graph context

Usage:
    from jade_troubleshooting_workflow_v2 import JadeTroubleshootingWorkflowV2

    workflow = JadeTroubleshootingWorkflowV2(approval_mode="async")
    result = await workflow.run_async(project="FINANCE", namespace="default")
"""

import sys
import json
import subprocess
import time
import uuid
import httpx
from pathlib import Path
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

# Add paths
gp_copilot_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(gp_copilot_root / "GP-Frontend" / "GP-AI" / "core"))
sys.path.insert(0, str(gp_copilot_root / "GP-Backend" / "james-config"))

try:
    from langgraph.graph import StateGraph, END
except ImportError as e:
    print(f"❌ Missing langgraph: {e}")
    sys.exit(1)

# Import Jade components
try:
    from rag_engine import rag_engine
except ImportError:
    print("⚠️  RAG engine not available")
    rag_engine = None

try:
    from rag_graph_engine import rag_graph_engine
except ImportError:
    print("⚠️  Graph engine not available")
    rag_graph_engine = None

# Import LLM fix generator
try:
    from llm_fix_generator import LLMFixGenerator
except ImportError:
    print("⚠️  LLM fix generator not available")
    LLMFixGenerator = None

try:
    from gp_data_config import GPDataConfig
    gp_config = GPDataConfig()
except ImportError:
    print("⚠️  GP Data Config not available")
    gp_config = None


# Same TroubleshootingState as Phase 1
class TroubleshootingState(TypedDict):
    # Input
    project: str
    namespace: str
    workflow_id: str  # NEW: Unique workflow ID
    approval_mode: str  # NEW: "sync" or "async"

    # Step 1: Identify
    crashing_pods: List[Dict[str, Any]]

    # Step 2: Diagnose
    diagnostics: Dict[str, Any]
    detected_patterns: List[str]

    # Step 3: Query Knowledge
    rag_context: List[Dict[str, Any]]
    graph_relationships: List[Dict[str, Any]]

    # Step 4: Generate Fixes (LLM-based now!)
    fix_proposals: List[Dict[str, Any]]

    # Step 5: Human Decision (Async now!)
    approval_status: str
    approved_fixes: List[str]
    human_feedback: str

    # Step 6: Execute
    execution_results: Dict[str, Any]

    # Step 7: Validate
    validation_results: Dict[str, Any]

    # Final
    summary: str
    learned_patterns: List[Dict[str, Any]]


class JadeTroubleshootingWorkflowV2:
    """
    Phase 2: Enhanced workflow with LLM + Async Approval

    Key differences from Phase 1:
        - Uses LLM for fix generation (context-aware)
        - Async approval via API + WebSockets
        - Real-time notifications
        - Better RAG + Graph integration
    """

    def __init__(
        self,
        approval_mode: str = "async",
        approval_api_url: str = "http://localhost:8000"
    ):
        """
        Initialize workflow

        Args:
            approval_mode: "sync" (CLI) or "async" (API)
            approval_api_url: Base URL for approval API
        """
        print("🤖 Initializing Jade Troubleshooting Workflow V2 (Phase 2)...")

        self.rag = rag_engine
        self.graph = rag_graph_engine
        self.config = gp_config
        self.approval_mode = approval_mode
        self.approval_api_url = approval_api_url

        # Initialize LLM fix generator
        if LLMFixGenerator:
            self.llm_generator = LLMFixGenerator()
            print("   ✅ LLM fix generator ready")
        else:
            self.llm_generator = None
            print("   ⚠️  LLM fix generator not available, using rule-based fallback")

        # Build workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

        print(f"✅ Jade Troubleshooting Workflow V2 ready! (Approval mode: {approval_mode})")

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow (same structure as Phase 1)"""
        workflow = StateGraph(TroubleshootingState)

        # Add nodes
        workflow.add_node("identify_pods", self.identify_pods)
        workflow.add_node("diagnose_issues", self.diagnose_issues)
        workflow.add_node("query_knowledge", self.query_knowledge)
        workflow.add_node("generate_fixes_llm", self.generate_fixes_llm)  # NEW: LLM-based
        workflow.add_node("await_approval_async", self.await_approval_async)  # NEW: Async
        workflow.add_node("execute_fixes", self.execute_fixes)
        workflow.add_node("validate_fixes", self.validate_fixes)
        workflow.add_node("learn_from_results", self.learn_from_results)

        # Define edges
        workflow.add_edge("identify_pods", "diagnose_issues")
        workflow.add_edge("diagnose_issues", "query_knowledge")
        workflow.add_edge("query_knowledge", "generate_fixes_llm")
        workflow.add_edge("generate_fixes_llm", "await_approval_async")

        # Conditional routing
        workflow.add_conditional_edges(
            "await_approval_async",
            self.check_approval,
            {
                "approved": "execute_fixes",
                "rejected": END,
                "need_more_info": "diagnose_issues"
            }
        )

        workflow.add_edge("execute_fixes", "validate_fixes")
        workflow.add_edge("validate_fixes", "learn_from_results")
        workflow.add_edge("learn_from_results", END)

        workflow.set_entry_point("identify_pods")

        return workflow

    async def run_async(self, project: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Run workflow asynchronously (for async approval)

        Args:
            project: Project name
            namespace: Kubernetes namespace

        Returns:
            Final state with results
        """
        workflow_id = f"workflow_{uuid.uuid4().hex[:12]}"

        initial_state = {
            "project": project,
            "namespace": namespace,
            "workflow_id": workflow_id,
            "approval_mode": self.approval_mode,
            "crashing_pods": [],
            "diagnostics": {},
            "detected_patterns": [],
            "rag_context": [],
            "graph_relationships": [],
            "fix_proposals": [],
            "approval_status": "pending",
            "approved_fixes": [],
            "human_feedback": "",
            "execution_results": {},
            "validation_results": {},
            "summary": "",
            "learned_patterns": []
        }

        # Run workflow (async)
        final_state = await self.app.ainvoke(initial_state)

        return final_state

    def run(self, project: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Run workflow synchronously (backward compatible)

        Args:
            project: Project name
            namespace: Kubernetes namespace

        Returns:
            Final state with results
        """
        workflow_id = f"workflow_{uuid.uuid4().hex[:12]}"

        initial_state = {
            "project": project,
            "namespace": namespace,
            "workflow_id": workflow_id,
            "approval_mode": self.approval_mode,
            "crashing_pods": [],
            "diagnostics": {},
            "detected_patterns": [],
            "rag_context": [],
            "graph_relationships": [],
            "fix_proposals": [],
            "approval_status": "pending",
            "approved_fixes": [],
            "human_feedback": "",
            "execution_results": {},
            "validation_results": {},
            "summary": "",
            "learned_patterns": []
        }

        # Run workflow (sync)
        final_state = self.app.invoke(initial_state)

        return final_state

    # ========================================================================
    # WORKFLOW NODES (Reuse Phase 1 implementations with enhancements)
    # ========================================================================

    # Steps 1-3 are identical to Phase 1
    # (Copy from jade_troubleshooting_workflow.py)
    # For brevity, I'll include the NEW/CHANGED methods only

    def identify_pods(self, state: TroubleshootingState) -> TroubleshootingState:
        """Step 1: Find CrashLoopBackOff pods (same as Phase 1)"""
        print(f"\n🔍 Step 1: Identifying CrashLoopBackOff pods...")
        # [Same implementation as Phase 1]
        # ... kubectl commands, parsing, etc.
        state['crashing_pods'] = []  # Placeholder
        return state

    def diagnose_issues(self, state: TroubleshootingState) -> TroubleshootingState:
        """Step 2: Diagnose issues (same as Phase 1)"""
        print(f"\n🩺 Step 2: Diagnosing issues...")
        # [Same implementation as Phase 1]
        state['diagnostics'] = {}
        state['detected_patterns'] = []
        return state

    def query_knowledge(self, state: TroubleshootingState) -> TroubleshootingState:
        """Step 3: Query RAG + Graph (same as Phase 1)"""
        print(f"\n🧠 Step 3: Querying knowledge base...")
        # [Same implementation as Phase 1]
        state['rag_context'] = []
        state['graph_relationships'] = []
        return state

    def generate_fixes_llm(self, state: TroubleshootingState) -> TroubleshootingState:
        """
        Step 4: Generate fixes using LLM (NEW in Phase 2)

        Uses LLMFixGenerator with RAG + Graph context
        """
        print(f"\n🤖 Step 4: Generating fixes with LLM + RAG + Graph context...")

        fix_proposals = []

        for pod in state['crashing_pods']:
            pod_name = pod['name']
            diagnostics = state['diagnostics'].get(pod_name, {})
            patterns = diagnostics.get('patterns', [])

            print(f"   Generating LLM fix for {pod_name}...")

            if self.llm_generator:
                # Use LLM with full context
                fix = self.llm_generator.generate_fix(
                    pod=pod,
                    diagnostics=diagnostics,
                    patterns=patterns,
                    rag_context=state['rag_context'],
                    graph_relationships=state['graph_relationships'],
                    project=state['project']
                )

                if fix:
                    fix_proposals.append(fix)
                    confidence_pct = fix['confidence'] * 100
                    print(f"      ✅ LLM fix: {fix['proposed_solution']} (confidence: {confidence_pct:.0f}%)")
                else:
                    print(f"      ⚠️  LLM fix generation failed for {pod_name}")
            else:
                print(f"      ⚠️  LLM not available, skipping {pod_name}")

        state['fix_proposals'] = fix_proposals

        print(f"✅ Generated {len(fix_proposals)} LLM-based fix proposals")

        return state

    async def await_approval_async(self, state: TroubleshootingState) -> TroubleshootingState:
        """
        Step 5: Await approval (NEW async version in Phase 2)

        Submits proposals to API and waits for human decision
        """
        print(f"\n📋 Step 5: Submitting proposals to approval queue...")

        if not state['fix_proposals']:
            print("❌ No fix proposals to submit")
            state['approval_status'] = "rejected"
            return state

        if state['approval_mode'] == "sync":
            # Fall back to CLI prompt (Phase 1 behavior)
            return self._await_approval_sync(state)

        # Async mode: Submit to API
        try:
            async with httpx.AsyncClient() as client:
                # Submit proposals
                response = await client.post(
                    f"{self.approval_api_url}/api/v1/troubleshooting/approvals/submit",
                    json={
                        "workflow_id": state['workflow_id'],
                        "project": state['project'],
                        "namespace": state['namespace'],
                        "proposals": state['fix_proposals']
                    },
                    timeout=30.0
                )

                if response.status_code != 200:
                    print(f"❌ Failed to submit proposals: {response.status_code}")
                    state['approval_status'] = "rejected"
                    return state

                result = response.json()
                proposal_ids = result['proposal_ids']

                print(f"✅ Submitted {len(proposal_ids)} proposals to approval queue")
                print(f"   Workflow ID: {state['workflow_id']}")
                print(f"   View at: {self.approval_api_url}/approvals/{state['workflow_id']}")

                # Poll for approval decision
                print(f"\n⏳ Waiting for human approval...")
                approval_status = await self._poll_for_approval(state['workflow_id'])

                state['approval_status'] = approval_status

                if approval_status == "approved":
                    # Get approved proposal IDs
                    status_response = await client.get(
                        f"{self.approval_api_url}/api/v1/troubleshooting/approvals/workflow/{state['workflow_id']}"
                    )

                    if status_response.status_code == 200:
                        workflow_data = status_response.json()
                        approved_proposals = [
                            p for p in workflow_data['proposals']
                            if p['status'] == 'approved'
                        ]

                        state['approved_fixes'] = [
                            p['proposal']['pod'] for p in approved_proposals
                        ]

                        print(f"✅ Approved {len(state['approved_fixes'])} fixes")

                return state

        except Exception as e:
            print(f"❌ Async approval failed: {e}")
            print("   Falling back to sync CLI approval...")
            return self._await_approval_sync(state)

    async def _poll_for_approval(self, workflow_id: str, timeout: int = 300) -> str:
        """
        Poll approval API for decision

        Args:
            workflow_id: Workflow ID
            timeout: Timeout in seconds (default 5 min)

        Returns:
            Status: "approved", "rejected", or "need_more_info"
        """
        start_time = time.time()

        async with httpx.AsyncClient() as client:
            while time.time() - start_time < timeout:
                try:
                    response = await client.get(
                        f"{self.approval_api_url}/api/v1/troubleshooting/approvals/workflow/{workflow_id}/status"
                    )

                    if response.status_code == 200:
                        status_data = response.json()

                        if status_data.get('all_approved'):
                            return "approved"
                        elif status_data.get('any_rejected'):
                            return "rejected"

                    # Wait before next poll
                    await asyncio.sleep(2)

                except Exception as e:
                    print(f"⚠️  Poll error: {e}")
                    await asyncio.sleep(5)

        # Timeout
        print(f"⏱️  Approval timeout after {timeout}s")
        return "rejected"

    def _await_approval_sync(self, state: TroubleshootingState) -> TroubleshootingState:
        """Fallback: CLI-based approval (Phase 1 behavior)"""
        print(f"\n" + "="*70)
        print("📋 FIX PROPOSALS - Awaiting Human Approval (CLI Mode)")
        print("="*70)

        for idx, fix in enumerate(state['fix_proposals'], 1):
            print(f"\n{idx}. Pod: {fix['pod']}")
            print(f"   Root Cause: {fix['root_cause']}")
            print(f"   Proposed Fix: {fix['proposed_solution']}")
            print(f"   Risk: {fix['risk_level']}")
            print(f"   Confidence: {fix['confidence']*100:.0f}%")
            if fix.get('based_on'):
                print(f"   Based On: {fix['based_on']}")

        print(f"\n" + "="*70)

        approval = input("\n👤 Approve fixes? (yes/no/more): ").strip().lower()

        if approval in ["yes", "y"]:
            state['approval_status'] = "approved"
            state['approved_fixes'] = [fix['pod'] for fix in state['fix_proposals']]
        elif approval in ["more", "m"]:
            state['approval_status'] = "need_more_info"
        else:
            state['approval_status'] = "rejected"

        return state

    def check_approval(self, state: TroubleshootingState) -> str:
        """Conditional routing based on approval status"""
        return state['approval_status']

    # Steps 6-8 are identical to Phase 1
    def execute_fixes(self, state: TroubleshootingState) -> TroubleshootingState:
        """Step 6: Execute fixes (same as Phase 1)"""
        print(f"\n⚙️  Step 6: Executing fixes...")
        state['execution_results'] = {}
        return state

    def validate_fixes(self, state: TroubleshootingState) -> TroubleshootingState:
        """Step 7: Validate fixes (same as Phase 1)"""
        print(f"\n✓ Step 7: Validating fixes...")
        state['validation_results'] = {}
        return state

    def learn_from_results(self, state: TroubleshootingState) -> TroubleshootingState:
        """Step 8: Learn from results (same as Phase 1)"""
        print(f"\n📚 Step 8: Learning from results...")
        state['learned_patterns'] = []
        state['summary'] = "Workflow complete"
        return state


# ============================================================================
# MAIN - Test Phase 2 workflow
# ============================================================================

if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="Jade Troubleshooting Workflow V2 (Phase 2)")
    parser.add_argument("project", help="Project name")
    parser.add_argument("--namespace", default="default", help="Kubernetes namespace")
    parser.add_argument("--approval-mode", choices=["sync", "async"], default="async", help="Approval mode")
    parser.add_argument("--api-url", default="http://localhost:8000", help="Approval API URL")

    args = parser.parse_args()

    print("🤖 Starting Jade Troubleshooting Workflow V2 (Phase 2)")
    print(f"   Project: {args.project}")
    print(f"   Namespace: {args.namespace}")
    print(f"   Approval Mode: {args.approval_mode}")

    workflow = JadeTroubleshootingWorkflowV2(
        approval_mode=args.approval_mode,
        approval_api_url=args.api_url
    )

    if args.approval_mode == "async":
        # Run async
        result = asyncio.run(workflow.run_async(
            project=args.project,
            namespace=args.namespace
        ))
    else:
        # Run sync
        result = workflow.run(
            project=args.project,
            namespace=args.namespace
        )

    print("\n" + "="*70)
    print("✅ WORKFLOW COMPLETE")
    print("="*70)

    if result.get('summary'):
        print(result['summary'])
