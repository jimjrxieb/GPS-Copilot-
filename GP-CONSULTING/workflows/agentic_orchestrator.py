"""
Agentic Orchestrator for Jade

This is the brain of Jade's autonomous security engineering capabilities.
It uses LangGraph to coordinate multi-step workflows: scan → analyze → fix → verify → learn

Comparison to Claude Code:
- Claude Code: User asks "fix line 50" → Claude reads, edits, verifies
- Jade: User asks "fix terraform security" → Jade scans, analyzes, decides, fixes, verifies

This is what makes Jade "agentic" instead of just a chatbot.
"""

import sys
from pathlib import Path
from typing import TypedDict, Annotated, Sequence, Literal
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolExecutor
except ImportError:
    print("⚠️  LangGraph not installed. Install with: pip install langgraph")
    sys.exit(1)

# Tool registry
from tools.base_registry import ToolRegistry, ToolCategory
from tools.scanner_tools import register_scanner_tools
from tools.fixer_tools import register_fixer_tools
from tools.validator_tools import register_validator_tools

# AI model
from GP_PLATFORM.james_config.ai_config import get_ai_client


# ==================== State Definition ====================

class AgentState(TypedDict):
    """
    State that flows through the workflow

    This is like a context object that each step can read and update.
    Similar to Redux state in frontend development.
    """
    # User input
    task: str                           # "scan terraform and fix security issues"
    target_path: str                    # Path to scan/fix

    # Workflow state
    current_step: str                   # Current step in workflow
    steps_completed: list               # History of completed steps

    # Scan results
    scan_results: dict                  # Results from scanners
    scan_tool_used: str                 # Which scanner was used

    # Analysis
    ai_analysis: dict                   # AI's analysis of scan results
    decision: str                       # AI's decision: fix_auto, fix_with_approval, report_only
    reasoning: str                      # AI's reasoning for decision

    # Fixes
    fixes_proposed: list                # List of proposed fixes
    fixes_applied: list                 # List of applied fixes
    fix_results: dict                   # Results of fix application

    # Verification
    verification_results: dict          # Results of re-scan after fixes
    success: bool                       # Did workflow succeed?

    # Learning
    patterns_learned: list              # New patterns to save for future

    # Metadata
    workflow_id: str                    # Unique ID for this workflow
    started_at: str                     # Timestamp
    ended_at: str                       # Timestamp

    # Approval workflow
    requires_approval: bool             # Does this need human approval?
    approval_status: str                # pending, approved, rejected
    approval_message: str               # Message for human


# ==================== AI Decision Engine ====================

class SecurityEngineerReasoning:
    """
    AI-powered decision making for security engineering

    This is what makes Jade "think" like a junior security engineer.
    It analyzes scan results and decides what to do next.
    """

    def __init__(self, ai_client):
        self.ai_client = ai_client

    def analyze_scan_results(self, scan_results: dict, target_path: str) -> dict:
        """
        Analyze scan results and make decision

        Decision tree:
        1. CRITICAL issues? → Fix immediately (with approval)
        2. Compliance violations? → Check against client requirements
        3. Quick wins (auto-fixable)? → Apply now
        4. Complex issues? → Create work items for human

        Returns:
        {
            "decision": "fix_auto" | "fix_with_approval" | "report_only",
            "reasoning": "Explanation of decision",
            "priority_issues": [...],
            "auto_fixable": [...],
            "needs_human": [...]
        }
        """
        findings = scan_results.get("findings", [])
        summary = scan_results.get("summary", {})

        # Count by severity
        critical = summary.get("by_severity", {}).get("CRITICAL", 0)
        high = summary.get("by_severity", {}).get("HIGH", 0)
        medium = summary.get("by_severity", {}).get("MEDIUM", 0)
        low = summary.get("by_severity", {}).get("LOW", 0)

        # Build prompt for AI reasoning
        prompt = f"""You are Jade, a junior cloud security engineer. Analyze these security scan results and decide what to do.

Scan Results Summary:
- Target: {target_path}
- Total Issues: {summary.get('total', 0)}
- Critical: {critical}
- High: {high}
- Medium: {medium}
- Low: {low}

Sample Findings (first 5):
{json.dumps(findings[:5], indent=2)}

Your Task:
1. Identify which issues can be auto-fixed safely
2. Identify which issues need human approval before fixing
3. Identify which issues are too complex and need human investigation
4. Make a recommendation: fix_auto, fix_with_approval, or report_only

Provide your response in JSON format:
{{
    "decision": "fix_auto|fix_with_approval|report_only",
    "reasoning": "Your reasoning here",
    "priority_issues": ["issue_id1", "issue_id2"],
    "auto_fixable": ["issue_id3", "issue_id4"],
    "needs_human": ["issue_id5"]
}}
"""

        # Get AI decision
        try:
            response = self.ai_client.chat.completions.create(
                model="Qwen/Qwen2.5-7B-Instruct",
                messages=[
                    {"role": "system", "content": "You are Jade, a security engineer AI. Analyze scan results and make decisions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent decisions
            )

            # Parse response
            response_text = response.choices[0].message.content
            # Extract JSON from response (AI might wrap it in markdown)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                decision = json.loads(json_match.group())
            else:
                # Fallback if AI doesn't return JSON
                decision = {
                    "decision": "report_only",
                    "reasoning": "Could not parse AI response",
                    "priority_issues": [],
                    "auto_fixable": [],
                    "needs_human": []
                }

            return decision

        except Exception as e:
            # Fallback to safe default
            return {
                "decision": "report_only",
                "reasoning": f"Error in AI reasoning: {str(e)}",
                "priority_issues": [],
                "auto_fixable": [],
                "needs_human": []
            }


# ==================== Workflow Steps ====================

def step_scan(state: AgentState) -> AgentState:
    """
    Step 1: Scan the target with appropriate scanner

    Based on target path, choose the right scanner:
    - Python files → Bandit
    - Terraform → OPA + Checkov
    - Kubernetes → Gatekeeper + Polaris
    - Dependencies → Trivy
    - Secrets → Gitleaks
    """
    print(f"\n🔍 Step 1: Scanning {state['target_path']}...")

    target_path = Path(state['target_path'])

    # Determine which scanner to use
    if target_path.suffix == '.py' or (target_path / 'setup.py').exists():
        scanner = "scan_python_bandit"
    elif (target_path / 'main.tf').exists() or target_path.suffix == '.tf':
        scanner = "scan_iac_opa"
    elif target_path.suffix in ['.yaml', '.yml']:
        # Check if it's Kubernetes
        with open(target_path) as f:
            content = f.read()
            if 'kind:' in content and 'apiVersion:' in content:
                scanner = "scan_iac_checkov"
            else:
                scanner = "scan_code_semgrep"
    else:
        # Default to comprehensive scan
        scanner = "scan_dependencies_trivy"

    # Execute scanner
    result = ToolRegistry.execute_tool(scanner, target_path=str(state['target_path']))

    state['scan_results'] = result.get('data', {})
    state['scan_tool_used'] = scanner
    state['current_step'] = 'scan'
    state['steps_completed'].append('scan')

    print(f"✅ Scan complete: {state['scan_results'].get('summary', {}).get('total', 0)} issues found")

    return state


def step_analyze(state: AgentState) -> AgentState:
    """
    Step 2: AI analyzes scan results and makes decision

    This is where Jade "thinks" about what to do next.
    """
    print(f"\n🧠 Step 2: Analyzing scan results...")

    # Get AI client
    ai_client = get_ai_client()
    reasoning_engine = SecurityEngineerReasoning(ai_client)

    # Analyze results
    analysis = reasoning_engine.analyze_scan_results(
        state['scan_results'],
        state['target_path']
    )

    state['ai_analysis'] = analysis
    state['decision'] = analysis['decision']
    state['reasoning'] = analysis['reasoning']
    state['current_step'] = 'analyze'
    state['steps_completed'].append('analyze')

    # Determine if approval needed
    if analysis['decision'] == 'fix_with_approval':
        state['requires_approval'] = True
        state['approval_status'] = 'pending'
        state['approval_message'] = f"Jade wants to fix {len(analysis.get('auto_fixable', []))} issues. Approve?"

    print(f"✅ Analysis complete: Decision = {state['decision']}")
    print(f"   Reasoning: {state['reasoning'][:100]}...")

    return state


def step_decide_next(state: AgentState) -> Literal["fix", "report", "wait_approval"]:
    """
    Decision node: What to do next based on AI analysis?

    This is a LangGraph conditional edge that routes the workflow.
    """
    decision = state['decision']

    if decision == 'fix_auto':
        return "fix"
    elif decision == 'fix_with_approval':
        if state['approval_status'] == 'approved':
            return "fix"
        else:
            return "wait_approval"
    else:
        return "report"


def step_fix(state: AgentState) -> AgentState:
    """
    Step 3: Apply fixes based on AI decision
    """
    print(f"\n🔧 Step 3: Applying fixes...")

    # Get auto-fixable issues from analysis
    auto_fixable = state['ai_analysis'].get('auto_fixable', [])

    if not auto_fixable:
        print("   No auto-fixable issues found")
        state['current_step'] = 'fix'
        state['steps_completed'].append('fix')
        return state

    # Determine which fixer to use based on scanner
    scanner_to_fixer = {
        'scan_python_bandit': 'fix_python_bandit',
        'scan_dependencies_trivy': 'fix_dependencies_trivy',
        'scan_secrets_gitleaks': 'fix_secrets_gitleaks',
        'scan_iac_opa': 'fix_terraform_issues',
        'scan_iac_checkov': 'fix_terraform_issues',
    }

    fixer = scanner_to_fixer.get(state['scan_tool_used'])

    if not fixer:
        print(f"   No fixer available for {state['scan_tool_used']}")
        state['current_step'] = 'fix'
        state['steps_completed'].append('fix')
        return state

    # Apply fixes
    fix_result = ToolRegistry.execute_tool(
        fixer,
        scan_results=state['scan_results'],
        auto_apply=True  # AI already decided it's safe
    )

    state['fix_results'] = fix_result.get('data', {})
    state['fixes_applied'] = fix_result.get('data', {}).get('details', [])
    state['current_step'] = 'fix'
    state['steps_completed'].append('fix')

    print(f"✅ Fixes applied: {len(state['fixes_applied'])} fixes")

    return state


def step_verify(state: AgentState) -> AgentState:
    """
    Step 4: Verify fixes by re-scanning
    """
    print(f"\n✓ Step 4: Verifying fixes...")

    # Re-scan with same scanner
    rescan_result = ToolRegistry.execute_tool(
        state['scan_tool_used'],
        target_path=state['target_path']
    )

    after_results = rescan_result.get('data', {})

    # Compare before/after
    verification = ToolRegistry.execute_tool(
        'verify_fix_effectiveness',
        before_results=state['scan_results'],
        after_results=after_results
    )

    state['verification_results'] = verification.get('data', {})
    state['success'] = verification.get('data', {}).get('success', False)
    state['current_step'] = 'verify'
    state['steps_completed'].append('verify')

    print(f"✅ Verification complete: {verification.get('data', {}).get('issues_fixed', 0)} issues fixed")
    print(f"   Effectiveness: {verification.get('data', {}).get('effectiveness_score', 0):.1%}")

    return state


def step_learn(state: AgentState) -> AgentState:
    """
    Step 5: Learn from this workflow for future use

    Save successful patterns to GP-DATA for RAG retrieval.
    """
    print(f"\n📚 Step 5: Learning from workflow...")

    # Extract patterns from successful fixes
    patterns = []

    if state['success'] and state['fixes_applied']:
        for fix in state['fixes_applied']:
            pattern = {
                "issue_type": fix.get('issue_type'),
                "fix_pattern": fix.get('fix_applied'),
                "target_type": state['scan_tool_used'],
                "effectiveness": state['verification_results'].get('effectiveness_score'),
                "timestamp": datetime.now().isoformat(),
            }
            patterns.append(pattern)

    state['patterns_learned'] = patterns
    state['current_step'] = 'learn'
    state['steps_completed'].append('learn')

    # Save to GP-DATA (placeholder - would integrate with GP-DATA sync)
    from pathlib import Path
    learning_dir = Path(__file__).parent.parent.parent / "GP-DATA/active/learning"
    learning_dir.mkdir(parents=True, exist_ok=True)

    learning_file = learning_dir / f"workflow_{state['workflow_id']}.json"
    learning_file.write_text(json.dumps({
        "workflow_id": state['workflow_id'],
        "task": state['task'],
        "patterns": patterns,
        "success": state['success'],
        "timestamp": datetime.now().isoformat(),
    }, indent=2))

    print(f"✅ Learned {len(patterns)} patterns")

    return state


def step_report(state: AgentState) -> AgentState:
    """
    Final step: Generate report
    """
    print(f"\n📊 Step 6: Generating report...")

    state['current_step'] = 'report'
    state['steps_completed'].append('report')
    state['ended_at'] = datetime.now().isoformat()

    # Generate summary report
    report = {
        "workflow_id": state['workflow_id'],
        "task": state['task'],
        "target": state['target_path'],
        "duration": f"{state['started_at']} to {state['ended_at']}",
        "steps_completed": state['steps_completed'],
        "scan_summary": state['scan_results'].get('summary', {}),
        "decision": state['decision'],
        "reasoning": state['reasoning'],
        "fixes_applied": len(state.get('fixes_applied', [])),
        "success": state.get('success', False),
        "verification": state.get('verification_results', {}),
        "patterns_learned": len(state.get('patterns_learned', [])),
    }

    # Save report
    from pathlib import Path
    reports_dir = Path(__file__).parent.parent.parent / "GP-DATA/active/reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_file = reports_dir / f"workflow_{state['workflow_id']}.json"
    report_file.write_text(json.dumps(report, indent=2))

    print(f"✅ Report saved: {report_file}")

    return state


# ==================== Build Workflow Graph ====================

def create_workflow_graph():
    """
    Build the LangGraph workflow

    This defines the flow: scan → analyze → decide → fix → verify → learn → report
    """
    # Register all tools
    register_scanner_tools()
    register_fixer_tools()
    register_validator_tools()

    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("scan", step_scan)
    workflow.add_node("analyze", step_analyze)
    workflow.add_node("fix", step_fix)
    workflow.add_node("verify", step_verify)
    workflow.add_node("learn", step_learn)
    workflow.add_node("report", step_report)

    # Add edges
    workflow.set_entry_point("scan")
    workflow.add_edge("scan", "analyze")

    # Conditional edge based on decision
    workflow.add_conditional_edges(
        "analyze",
        step_decide_next,
        {
            "fix": "fix",
            "report": "report",
            "wait_approval": "report",  # For now, just report. Later add approval node
        }
    )

    workflow.add_edge("fix", "verify")
    workflow.add_edge("verify", "learn")
    workflow.add_edge("learn", "report")
    workflow.add_edge("report", END)

    return workflow.compile()


# ==================== Public API ====================

def run_autonomous_workflow(task: str, target_path: str) -> dict:
    """
    Main entry point for autonomous security engineering workflow

    Usage:
        result = run_autonomous_workflow(
            task="scan and fix terraform security issues",
            target_path="GP-PROJECTS/Terraform_CICD_Setup"
        )

    Returns workflow report.
    """
    import uuid

    # Initialize state
    initial_state = {
        "task": task,
        "target_path": target_path,
        "current_step": "init",
        "steps_completed": [],
        "scan_results": {},
        "scan_tool_used": "",
        "ai_analysis": {},
        "decision": "",
        "reasoning": "",
        "fixes_proposed": [],
        "fixes_applied": [],
        "fix_results": {},
        "verification_results": {},
        "success": False,
        "patterns_learned": [],
        "workflow_id": str(uuid.uuid4())[:8],
        "started_at": datetime.now().isoformat(),
        "ended_at": "",
        "requires_approval": False,
        "approval_status": "approved",  # Auto-approve for now
        "approval_message": "",
    }

    # Create and run workflow
    print(f"\n{'='*60}")
    print(f"🤖 Jade Autonomous Security Engineering Workflow")
    print(f"{'='*60}")
    print(f"Task: {task}")
    print(f"Target: {target_path}")
    print(f"Workflow ID: {initial_state['workflow_id']}")
    print(f"{'='*60}\n")

    workflow = create_workflow_graph()
    final_state = workflow.invoke(initial_state)

    print(f"\n{'='*60}")
    print(f"✅ Workflow Complete")
    print(f"{'='*60}\n")

    return final_state


if __name__ == "__main__":
    # Test the workflow
    result = run_autonomous_workflow(
        task="Scan Terraform project for security issues",
        target_path="GP-PROJECTS/Terraform_CICD_Setup"
    )

    print(f"\nFinal Result:")
    print(f"  Success: {result['success']}")
    print(f"  Steps: {' → '.join(result['steps_completed'])}")
    print(f"  Issues Fixed: {len(result.get('fixes_applied', []))}")