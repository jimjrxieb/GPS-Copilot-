#!/usr/bin/env python3
"""
Jade Troubleshooting Agent - LangGraph Agentic Workflow

This agent can autonomously troubleshoot infrastructure issues by:
1. Understanding user intent
2. Querying knowledge base (RAG)
3. Inspecting environment (kubectl, terraform, etc.)
4. Reasoning about root cause
5. Suggesting fixes with approval workflow
"""

import sys
import subprocess
from pathlib import Path
from typing import TypedDict, Annotated, List, Dict, Any
from datetime import datetime
import json

try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install: pip install langgraph langchain-core")
    sys.exit(1)

# Add GP-DATA to path for RAG query
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-DATA"))
from simple_rag_query import SimpleRAGQuery


class TroubleshootingState(TypedDict):
    """Agent state for troubleshooting workflow"""
    # User inputs
    user_query: str
    user_approval: bool

    # Agent understanding
    intent: str  # "diagnose", "fix", "query_knowledge", "inspect_environment"
    domain: str  # "kubernetes", "terraform", "opa", "general"

    # Investigation data
    environment_info: Dict[str, Any]
    knowledge_results: List[Dict[str, Any]]
    error_logs: str

    # Reasoning
    analysis: str
    root_cause: str
    suggested_fix: str
    fix_command: str

    # Execution
    execution_result: str
    success: bool

    # Conversation history
    messages: Annotated[list, lambda x, y: x + y]


class JadeTroubleshootingAgent:
    """Agentic troubleshooting workflow"""

    def __init__(self):
        """Initialize agent with tools and workflow"""
        self.rag = SimpleRAGQuery()
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(TroubleshootingState)

        # Add nodes
        workflow.add_node("classify_intent", self.classify_intent)
        workflow.add_node("query_knowledge", self.query_knowledge)
        workflow.add_node("inspect_environment", self.inspect_environment)
        workflow.add_node("analyze_issue", self.analyze_issue)
        workflow.add_node("suggest_fix", self.suggest_fix)
        workflow.add_node("request_approval", self.request_approval)
        workflow.add_node("execute_fix", self.execute_fix)
        workflow.add_node("verify_fix", self.verify_fix)

        # Define edges
        workflow.set_entry_point("classify_intent")

        # Intent routing
        workflow.add_conditional_edges(
            "classify_intent",
            self.route_by_intent,
            {
                "query_knowledge": "query_knowledge",
                "diagnose": "inspect_environment",
                "fix": "inspect_environment",
            }
        )

        # Knowledge query path
        workflow.add_edge("query_knowledge", END)

        # Diagnosis path
        workflow.add_edge("inspect_environment", "query_knowledge")
        workflow.add_edge("analyze_issue", "suggest_fix")

        # Fix path
        workflow.add_conditional_edges(
            "suggest_fix",
            self.should_execute_fix,
            {
                "request_approval": "request_approval",
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "request_approval",
            self.check_approval,
            {
                "execute": "execute_fix",
                "cancel": END
            }
        )

        workflow.add_edge("execute_fix", "verify_fix")
        workflow.add_edge("verify_fix", END)

        return workflow

    # ========== NODE FUNCTIONS ==========

    def classify_intent(self, state: TroubleshootingState) -> TroubleshootingState:
        """Classify user intent from query"""
        query_lower = state["user_query"].lower()

        # Detect domain
        if any(k in query_lower for k in ["pod", "kubernetes", "k8s", "kubectl", "deploy"]):
            state["domain"] = "kubernetes"
        elif any(k in query_lower for k in ["terraform", "tf", "state", "plan", "apply"]):
            state["domain"] = "terraform"
        elif any(k in query_lower for k in ["opa", "rego", "policy"]):
            state["domain"] = "opa"
        else:
            state["domain"] = "general"

        # Detect intent
        if any(k in query_lower for k in ["fix", "resolve", "repair"]):
            state["intent"] = "fix"
        elif any(k in query_lower for k in ["why", "diagnose", "troubleshoot", "what's wrong"]):
            state["intent"] = "diagnose"
        elif any(k in query_lower for k in ["how to", "what is", "explain"]):
            state["intent"] = "query_knowledge"
        else:
            # Default: if mentions error/issue, diagnose; otherwise query knowledge
            if any(k in query_lower for k in ["error", "fail", "issue", "problem", "crash"]):
                state["intent"] = "diagnose"
            else:
                state["intent"] = "query_knowledge"

        state["messages"].append(
            AIMessage(content=f"🎯 Intent: {state['intent']} | Domain: {state['domain']}")
        )

        return state

    def query_knowledge(self, state: TroubleshootingState) -> TroubleshootingState:
        """Query RAG knowledge base"""
        query = state["user_query"]

        # Add domain context to query
        if state["domain"] != "general":
            query = f"{state['domain']} {query}"

        results = self.rag.query_all_collections(query, n_results=3)
        state["knowledge_results"] = results

        # Format knowledge for display
        knowledge_summary = "\n\n".join([
            f"**{i+1}. [{r['collection'].upper()}] {r['metadata'].get('filename', 'unknown')}**\n{r['content'][:500]}..."
            for i, r in enumerate(results)
        ])

        state["messages"].append(
            AIMessage(content=f"📚 Knowledge retrieved:\n\n{knowledge_summary}")
        )

        return state

    def inspect_environment(self, state: TroubleshootingState) -> TroubleshootingState:
        """Inspect environment based on domain"""
        domain = state["domain"]
        env_info = {}

        if domain == "kubernetes":
            # Check pods
            try:
                result = subprocess.run(
                    ["kubectl", "get", "pods", "--all-namespaces"],
                    capture_output=True, text=True, timeout=10
                )
                env_info["pods"] = result.stdout if result.returncode == 0 else result.stderr

                # Check for failing pods
                failing = subprocess.run(
                    ["kubectl", "get", "pods", "--all-namespaces", "--field-selector=status.phase!=Running,status.phase!=Succeeded"],
                    capture_output=True, text=True, timeout=10
                )
                env_info["failing_pods"] = failing.stdout

            except Exception as e:
                env_info["error"] = str(e)

        elif domain == "terraform":
            # Check terraform state
            try:
                result = subprocess.run(
                    ["terraform", "version"],
                    capture_output=True, text=True, timeout=5
                )
                env_info["terraform_version"] = result.stdout
            except Exception as e:
                env_info["error"] = str(e)

        state["environment_info"] = env_info
        state["messages"].append(
            AIMessage(content=f"🔍 Environment inspection:\n```\n{json.dumps(env_info, indent=2)}\n```")
        )

        return state

    def analyze_issue(self, state: TroubleshootingState) -> TroubleshootingState:
        """Analyze issue using environment data + knowledge"""
        # Simple rule-based analysis (would use LLM in production)
        analysis = []

        env_info = state.get("environment_info", {})
        knowledge = state.get("knowledge_results", [])

        if state["domain"] == "kubernetes":
            failing_pods = env_info.get("failing_pods", "")
            if failing_pods and failing_pods.strip():
                analysis.append("❌ Found failing pods in cluster")
                # Extract pod info
                lines = failing_pods.split("\n")
                if len(lines) > 1:
                    analysis.append(f"Pod details:\n{failing_pods}")
            else:
                analysis.append("✅ No failing pods detected")

        # Add knowledge-based insights
        if knowledge:
            analysis.append(f"\n📚 Found {len(knowledge)} relevant knowledge articles")
            for i, k in enumerate(knowledge[:2], 1):
                analysis.append(f"{i}. {k['metadata'].get('filename', 'unknown')}")

        state["analysis"] = "\n".join(analysis)
        state["messages"].append(
            AIMessage(content=f"🧠 Analysis:\n{state['analysis']}")
        )

        return state

    def suggest_fix(self, state: TroubleshootingState) -> TroubleshootingState:
        """Suggest fix based on analysis"""
        # Extract fix from knowledge or use heuristics
        domain = state["domain"]
        knowledge = state.get("knowledge_results", [])

        suggested_fix = "Based on analysis:\n\n"
        fix_command = None

        if domain == "kubernetes":
            env_info = state.get("environment_info", {})
            failing_pods = env_info.get("failing_pods", "")

            if "CrashLoopBackOff" in failing_pods:
                suggested_fix += "**Issue:** Pod in CrashLoopBackOff\n"
                suggested_fix += "**Recommended actions:**\n"
                suggested_fix += "1. Check pod logs: `kubectl logs <pod-name> -n <namespace> --previous`\n"
                suggested_fix += "2. Check pod events: `kubectl describe pod <pod-name> -n <namespace>`\n"
                suggested_fix += "3. Common causes: OOMKilled, Image pull error, Application crash\n"
            elif "ImagePullBackOff" in failing_pods:
                suggested_fix += "**Issue:** Image pull failure\n"
                suggested_fix += "**Fix:** Check image name and registry credentials\n"
                fix_command = "kubectl get pods --all-namespaces | grep ImagePullBackOff"

        elif domain == "terraform":
            query_lower = state["user_query"].lower()
            if "state lock" in query_lower:
                suggested_fix += "**Issue:** Terraform state lock conflict\n"
                suggested_fix += "**Fix:** Release the lock\n"
                fix_command = "terraform force-unlock <LOCK_ID>"

                # Try to extract fix from knowledge
                for k in knowledge:
                    if "force-unlock" in k["content"].lower():
                        suggested_fix += f"\n📚 From knowledge base:\n{k['content'][:300]}...\n"
                        break

        # Add knowledge-based suggestions
        if knowledge and not fix_command:
            top_knowledge = knowledge[0]
            suggested_fix += f"\n📚 Relevant documentation:\n{top_knowledge['content'][:400]}...\n"

        state["suggested_fix"] = suggested_fix
        state["fix_command"] = fix_command or "No automatic fix available"

        state["messages"].append(
            AIMessage(content=f"💡 Suggested fix:\n{suggested_fix}\n\n**Command:** `{state['fix_command']}`")
        )

        return state

    def request_approval(self, state: TroubleshootingState) -> TroubleshootingState:
        """Request user approval for fix"""
        state["messages"].append(
            AIMessage(content=f"⚠️  Ready to execute: `{state['fix_command']}`\n\nApprove? (yes/no)")
        )
        return state

    def execute_fix(self, state: TroubleshootingState) -> TroubleshootingState:
        """Execute approved fix"""
        fix_command = state["fix_command"]

        # For safety, only execute read-only commands automatically
        # Write commands require manual execution
        safe_commands = ["kubectl get", "kubectl describe", "terraform show", "terraform plan"]

        is_safe = any(fix_command.startswith(cmd) for cmd in safe_commands)

        if is_safe:
            try:
                result = subprocess.run(
                    fix_command.split(),
                    capture_output=True, text=True, timeout=30
                )
                state["execution_result"] = result.stdout if result.returncode == 0 else result.stderr
                state["success"] = result.returncode == 0
            except Exception as e:
                state["execution_result"] = f"Error: {e}"
                state["success"] = False
        else:
            state["execution_result"] = f"⚠️  Write operation requires manual execution:\n\n{fix_command}\n\nCopy and run this command manually for safety."
            state["success"] = False

        state["messages"].append(
            AIMessage(content=f"🔧 Execution result:\n```\n{state['execution_result']}\n```")
        )

        return state

    def verify_fix(self, state: TroubleshootingState) -> TroubleshootingState:
        """Verify fix was successful"""
        if state["success"]:
            state["messages"].append(
                AIMessage(content="✅ Fix applied successfully!")
            )
        else:
            state["messages"].append(
                AIMessage(content="❌ Fix requires manual intervention. See suggested command above.")
            )
        return state

    # ========== ROUTING FUNCTIONS ==========

    def route_by_intent(self, state: TroubleshootingState) -> str:
        """Route based on classified intent"""
        return state["intent"]

    def should_execute_fix(self, state: TroubleshootingState) -> str:
        """Decide if fix requires approval"""
        if state["fix_command"] and state["fix_command"] != "No automatic fix available":
            return "request_approval"
        return "end"

    def check_approval(self, state: TroubleshootingState) -> str:
        """Check if user approved fix"""
        return "execute" if state.get("user_approval", False) else "cancel"

    # ========== PUBLIC API ==========

    def troubleshoot(self, user_query: str, auto_approve: bool = False) -> Dict[str, Any]:
        """
        Main entry point for troubleshooting

        Args:
            user_query: User's question or issue description
            auto_approve: Auto-approve safe fixes (default: False)

        Returns:
            Dict with analysis, suggestions, and results
        """
        # Initialize state
        initial_state = {
            "user_query": user_query,
            "user_approval": auto_approve,
            "intent": "",
            "domain": "",
            "environment_info": {},
            "knowledge_results": [],
            "error_logs": "",
            "analysis": "",
            "root_cause": "",
            "suggested_fix": "",
            "fix_command": "",
            "execution_result": "",
            "success": False,
            "messages": [HumanMessage(content=user_query)]
        }

        # Run workflow
        final_state = self.app.invoke(initial_state)

        return {
            "intent": final_state["intent"],
            "domain": final_state["domain"],
            "analysis": final_state.get("analysis", ""),
            "suggested_fix": final_state.get("suggested_fix", ""),
            "fix_command": final_state.get("fix_command", ""),
            "execution_result": final_state.get("execution_result", ""),
            "success": final_state.get("success", False),
            "conversation": [
                {"role": "human" if isinstance(m, HumanMessage) else "ai", "content": m.content}
                for m in final_state["messages"]
            ]
        }


def main():
    """CLI interface for testing"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python jade_troubleshooting_agent.py 'your question here'")
        print("\nExamples:")
        print("  python jade_troubleshooting_agent.py 'terraform state lock error'")
        print("  python jade_troubleshooting_agent.py 'kubernetes pod crashlooping'")
        print("  python jade_troubleshooting_agent.py 'how to fix OPA policy evaluation error'")
        sys.exit(1)

    query = ' '.join(sys.argv[1:])

    print("🤖 Jade Troubleshooting Agent Starting...\n")

    agent = JadeTroubleshootingAgent()
    result = agent.troubleshoot(query)

    print("\n" + "="*80)
    print("📋 TROUBLESHOOTING RESULT")
    print("="*80)

    print(f"\n🎯 Intent: {result['intent']}")
    print(f"🏷️  Domain: {result['domain']}")

    if result['analysis']:
        print(f"\n🧠 Analysis:\n{result['analysis']}")

    if result['suggested_fix']:
        print(f"\n💡 Suggested Fix:\n{result['suggested_fix']}")

    if result['fix_command']:
        print(f"\n🔧 Command:\n{result['fix_command']}")

    if result['execution_result']:
        print(f"\n📊 Execution Result:\n{result['execution_result']}")

    print("\n" + "="*80)
    print(f"Status: {'✅ SUCCESS' if result['success'] else '⚠️  MANUAL ACTION REQUIRED'}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
