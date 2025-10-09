#!/usr/bin/env python3
"""
Jade Agent Orchestrator - LangGraph Integration

This orchestrator ties together:
1. RAG knowledge base (GP-DATA/simple_rag_query.py)
2. Specialized agents (GP-CONSULTING-AGENTS/agents/)
3. LangGraph workflow for multi-step reasoning

Instead of duplicating functionality, this acts as the "brain" that routes
tasks to the right specialized agent based on intent classification.
"""

import sys
from pathlib import Path
from typing import TypedDict, Annotated, List, Dict, Any, Optional
import json

# Add paths
gp_copilot_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(gp_copilot_root / "GP-DATA"))
sys.path.insert(0, str(gp_copilot_root / "GP-CONSULTING-AGENTS" / "agents"))
sys.path.insert(0, str(gp_copilot_root / "GP-PLATFORM" / "james-config"))

try:
    from langgraph.graph import StateGraph, END
    from langchain_core.messages import HumanMessage, AIMessage
except ImportError as e:
    print(f"❌ Missing langgraph: {e}")
    sys.exit(1)

from simple_rag_query import SimpleRAGQuery

# Import specialized agents (existing infrastructure)
try:
    from kubernetes_troubleshooter import KubernetesTroubleshootingAgent
except ImportError:
    KubernetesTroubleshootingAgent = None
    print("⚠️  kubernetes_troubleshooter not available")


class JadeState(TypedDict):
    """Orchestrator state"""
    # Input
    user_query: str

    # Intent classification
    intent: str  # "troubleshoot", "scan", "fix", "query_knowledge", "explain"
    domain: str  # "kubernetes", "terraform", "opa", "secrets", "code", "general"

    # Data collection
    knowledge_results: List[Dict[str, Any]]
    agent_results: Dict[str, Any]

    # Response
    analysis: str
    suggestions: List[str]
    commands: List[str]

    # Conversation
    messages: Annotated[list, lambda x, y: x + y]


class JadeOrchestrator:
    """
    Jade's orchestration brain using LangGraph

    Routes user queries to:
    - RAG knowledge base
    - Specialized troubleshooting agents
    - Scanners and fixers
    """

    def __init__(self):
        """Initialize orchestrator with RAG and agents"""
        print("🤖 Initializing Jade Orchestrator...")

        # RAG knowledge base
        self.rag = SimpleRAGQuery()

        # Specialized agents (lazy load)
        self._k8s_troubleshooter = None

        # Build workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

        print("✅ Jade Orchestrator ready!")

    @property
    def k8s_troubleshooter(self):
        """Lazy load kubernetes troubleshooter"""
        if self._k8s_troubleshooter is None and KubernetesTroubleshootingAgent:
            self._k8s_troubleshooter = KubernetesTroubleshootingAgent()
        return self._k8s_troubleshooter

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(JadeState)

        # Add nodes
        workflow.add_node("classify", self.classify_intent)
        workflow.add_node("query_rag", self.query_rag)
        workflow.add_node("route_to_agent", self.route_to_agent)
        workflow.add_node("synthesize_response", self.synthesize_response)

        # Define flow
        workflow.set_entry_point("classify")

        # After classification, always query RAG first
        workflow.add_edge("classify", "query_rag")

        # After RAG, decide if we need a specialized agent
        workflow.add_conditional_edges(
            "query_rag",
            self.should_use_agent,
            {
                "use_agent": "route_to_agent",
                "skip_agent": "synthesize_response"
            }
        )

        # After agent, synthesize
        workflow.add_edge("route_to_agent", "synthesize_response")
        workflow.add_edge("synthesize_response", END)

        return workflow

    # ========== WORKFLOW NODES ==========

    def classify_intent(self, state: JadeState) -> JadeState:
        """Classify user intent and domain"""
        query = state["user_query"].lower()

        # Detect domain (what system/technology)
        if any(k in query for k in ["pod", "kubernetes", "k8s", "kubectl", "deploy", "service", "crashloop"]):
            state["domain"] = "kubernetes"
        elif any(k in query for k in ["terraform", "tf", "state", "plan", "apply", "hcl"]):
            state["domain"] = "terraform"
        elif any(k in query for k in ["opa", "rego", "policy", "gatekeeper", "conftest"]):
            state["domain"] = "opa"
        elif any(k in query for k in ["secret", "credential", "password", "token", "api key"]):
            state["domain"] = "secrets"
        elif any(k in query for k in ["python", "code", "sql injection", "xss", "bandit"]):
            state["domain"] = "code"
        else:
            state["domain"] = "general"

        # Detect intent (what action)
        if any(k in query for k in ["troubleshoot", "diagnose", "debug", "why", "failing", "crash", "error"]):
            state["intent"] = "troubleshoot"
        elif any(k in query for k in ["scan", "analyze", "check", "audit", "test"]):
            state["intent"] = "scan"
        elif any(k in query for k in ["fix", "resolve", "repair", "remediate"]):
            state["intent"] = "fix"
        elif any(k in query for k in ["how to", "what is", "explain", "tell me about"]):
            state["intent"] = "explain"
        else:
            # Default based on domain
            if state["domain"] in ["kubernetes", "terraform", "opa"]:
                state["intent"] = "troubleshoot"
            else:
                state["intent"] = "explain"

        msg = f"🎯 **Intent:** {state['intent']} | **Domain:** {state['domain']}"
        state["messages"].append(AIMessage(content=msg))

        return state

    def query_rag(self, state: JadeState) -> JadeState:
        """Query RAG knowledge base"""
        query = state["user_query"]

        # Add domain context
        if state["domain"] != "general":
            query = f"{state['domain']} {query}"

        # Query RAG
        results = self.rag.query_all_collections(query, n_results=3)
        state["knowledge_results"] = results

        if results:
            msg = f"📚 **Knowledge Base:** Found {len(results)} relevant documents"
            state["messages"].append(AIMessage(content=msg))

        return state

    def route_to_agent(self, state: JadeState) -> JadeState:
        """Route to specialized agent based on domain + intent"""
        domain = state["domain"]
        intent = state["intent"]

        agent_result = {"agent": "none", "output": "No specialized agent available"}

        # Kubernetes troubleshooting
        if domain == "kubernetes" and intent == "troubleshoot":
            if self.k8s_troubleshooter:
                # Extract pod info from query if present
                query = state["user_query"]

                # Try to detect pod name/namespace from query
                # For now, just document that agent exists
                agent_result = {
                    "agent": "kubernetes_troubleshooter",
                    "status": "available",
                    "message": "Kubernetes troubleshooting agent available. Can diagnose: CrashLoopBackOff, ImagePullBackOff, OOMKilled, ConfigMap issues",
                    "usage": "For specific pod: diagnose_crashloopbackoff(namespace, pod_name)"
                }

                msg = "🤖 **Agent:** Kubernetes Troubleshooter available"
                state["messages"].append(AIMessage(content=msg))
            else:
                agent_result = {
                    "agent": "kubernetes_troubleshooter",
                    "status": "unavailable",
                    "message": "Kubernetes troubleshooter not loaded"
                }

        # Future: Add routing for other agents
        # - terraform_agent (IaC troubleshooting)
        # - secrets_agent (Secret detection/rotation)
        # - sast_agent (Code security)
        # - etc.

        state["agent_results"] = agent_result
        return state

    def synthesize_response(self, state: JadeState) -> JadeState:
        """Synthesize final response from RAG + agent results"""
        analysis = []
        suggestions = []
        commands = []

        # Add knowledge base insights
        knowledge = state.get("knowledge_results", [])
        if knowledge:
            analysis.append("## 📚 Knowledge Base Insights\n")
            for i, k in enumerate(knowledge[:3], 1):
                filename = k["metadata"].get("filename", "unknown")
                content_preview = k["content"][:300].replace("\n", " ")
                analysis.append(f"{i}. **{filename}**")
                analysis.append(f"   {content_preview}...\n")

        # Add agent insights
        agent_result = state.get("agent_results", {})
        if agent_result.get("agent") != "none":
            analysis.append("\n## 🤖 Specialized Agent\n")
            analysis.append(f"**Agent:** {agent_result['agent']}")
            analysis.append(f"**Status:** {agent_result.get('status', 'unknown')}")
            if agent_result.get("message"):
                analysis.append(f"**Info:** {agent_result['message']}\n")

        # Generate suggestions based on domain/intent
        domain = state["domain"]
        intent = state["intent"]

        if domain == "kubernetes" and intent == "troubleshoot":
            suggestions.append("Check pod status: `kubectl get pods --all-namespaces`")
            suggestions.append("Describe failing pod: `kubectl describe pod <pod-name> -n <namespace>`")
            suggestions.append("Check logs: `kubectl logs <pod-name> -n <namespace> --previous`")

            if self.k8s_troubleshooter:
                suggestions.append("🤖 Or use: `python GP-CONSULTING-AGENTS/agents/kubernetes_troubleshooter.py`")

        elif domain == "terraform" and intent == "troubleshoot":
            # Check knowledge for terraform fixes
            terraform_knowledge = [k for k in knowledge if "terraform" in k["content"].lower()]
            if terraform_knowledge and "state lock" in state["user_query"].lower():
                suggestions.append("Fix state lock: `terraform force-unlock <LOCK_ID>`")
                suggestions.append("Prevent locks: Use remote backend with locking (S3 + DynamoDB)")

            commands.append("terraform validate")
            commands.append("terraform plan")

        elif intent == "explain":
            suggestions.append("Refer to knowledge base articles above for detailed explanations")

        # Build final response
        state["analysis"] = "\n".join(analysis)
        state["suggestions"] = suggestions
        state["commands"] = commands

        # Create final message
        final_msg = []

        if state["analysis"]:
            final_msg.append(state["analysis"])

        if suggestions:
            final_msg.append("\n## 💡 Suggested Actions\n")
            for i, s in enumerate(suggestions, 1):
                final_msg.append(f"{i}. {s}")

        if commands:
            final_msg.append("\n## 🔧 Commands\n")
            for cmd in commands:
                final_msg.append(f"```bash\n{cmd}\n```")

        state["messages"].append(AIMessage(content="\n".join(final_msg)))

        return state

    # ========== ROUTING DECISIONS ==========

    def should_use_agent(self, state: JadeState) -> str:
        """Decide if we should route to a specialized agent"""
        domain = state["domain"]
        intent = state["intent"]

        # Use agent for troubleshooting kubernetes, terraform, or fixing issues
        if intent in ["troubleshoot", "fix"] and domain in ["kubernetes", "terraform", "opa"]:
            return "use_agent"

        # Otherwise just use RAG knowledge
        return "skip_agent"

    # ========== PUBLIC API ==========

    def process(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point for processing user queries

        Args:
            user_query: User's question or request

        Returns:
            Dict with analysis, suggestions, and conversation
        """
        initial_state = {
            "user_query": user_query,
            "intent": "",
            "domain": "",
            "knowledge_results": [],
            "agent_results": {},
            "analysis": "",
            "suggestions": [],
            "commands": [],
            "messages": [HumanMessage(content=user_query)]
        }

        final_state = self.app.invoke(initial_state)

        return {
            "intent": final_state["intent"],
            "domain": final_state["domain"],
            "analysis": final_state["analysis"],
            "suggestions": final_state["suggestions"],
            "commands": final_state["commands"],
            "knowledge_count": len(final_state.get("knowledge_results", [])),
            "agent_used": final_state.get("agent_results", {}).get("agent", "none"),
            "conversation": [
                {
                    "role": "human" if isinstance(m, HumanMessage) else "ai",
                    "content": m.content
                }
                for m in final_state["messages"]
            ]
        }


def main():
    """CLI interface"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python jade_orchestrator.py 'your question'")
        print("\nExamples:")
        print("  python jade_orchestrator.py 'kubernetes pod crashlooping'")
        print("  python jade_orchestrator.py 'terraform state lock error'")
        print("  python jade_orchestrator.py 'how to fix OPA policy errors'")
        sys.exit(1)

    query = ' '.join(sys.argv[1:])

    print("🤖 Jade Orchestrator Processing...\n")

    orchestrator = JadeOrchestrator()
    result = orchestrator.process(query)

    print("\n" + "="*80)
    print("📋 JADE RESPONSE")
    print("="*80)

    print(f"\n🎯 Intent: {result['intent']}")
    print(f"🏷️  Domain: {result['domain']}")
    print(f"📚 Knowledge: {result['knowledge_count']} documents")
    print(f"🤖 Agent: {result['agent_used']}")

    print("\n" + "-"*80)
    print(result['analysis'])

    if result['suggestions']:
        print("\n💡 Suggestions:")
        for i, s in enumerate(result['suggestions'], 1):
            print(f"  {i}. {s}")

    if result['commands']:
        print("\n🔧 Commands:")
        for cmd in result['commands']:
            print(f"  {cmd}")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
