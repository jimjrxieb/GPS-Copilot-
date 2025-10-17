#!/usr/bin/env python3
"""
Jade Kubernetes Troubleshooting Workflow
LangGraph-based multi-step workflow with human-in-the-loop

Architecture:
1. identify_pods → Find CrashLoopBackOff pods
2. diagnose_issues → Gather logs, events, detect patterns
3. query_knowledge → RAG + Graph lookup for similar issues
4. generate_fixes → LLM generates fix proposals
5. await_approval → Human decision point (conditional routing)
6. execute_fixes → Apply approved fixes
7. validate_fixes → Check if fixes worked
8. learn_from_results → Store in RAG + Graph for future use

Usage:
    from jade_troubleshooting_workflow import JadeTroubleshootingWorkflow

    workflow = JadeTroubleshootingWorkflow()
    result = workflow.run(project="FINANCE", namespace="default")
    print(result['summary'])
"""

import sys
import json
import subprocess
import time
from pathlib import Path
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

# Add paths
gp_copilot_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(gp_copilot_root / "GP-Frontend" / "GP-AI" / "core"))
sys.path.insert(0, str(gp_copilot_root / "GP-Backend" / "james-config"))

try:
    from langgraph.graph import StateGraph, END
except ImportError as e:
    print(f"❌ Missing langgraph: {e}")
    print("Install with: pip install langgraph")
    sys.exit(1)

# Import Jade components
try:
    from rag_engine import rag_engine
    from rag_graph_engine import rag_graph_engine
except ImportError as e:
    print(f"⚠️  RAG components not available: {e}")
    rag_engine = None
    rag_graph_engine = None

try:
    from gp_data_config import GPDataConfig
    gp_config = GPDataConfig()
except ImportError:
    print("⚠️  GP Data Config not available, using defaults")
    gp_config = None


class TroubleshootingState(TypedDict):
    """State object passed through LangGraph workflow"""
    # Input
    project: str
    namespace: str

    # Step 1: Identify
    crashing_pods: List[Dict[str, Any]]

    # Step 2: Diagnose
    diagnostics: Dict[str, Any]
    detected_patterns: List[str]

    # Step 3: Query Knowledge
    rag_context: List[Dict[str, Any]]
    graph_relationships: List[Dict[str, Any]]

    # Step 4: Generate Fixes
    fix_proposals: List[Dict[str, Any]]

    # Step 5: Human Decision
    approval_status: str  # "pending", "approved", "rejected", "need_more_info"
    approved_fixes: List[str]
    human_feedback: str

    # Step 6: Execute
    execution_results: Dict[str, Any]

    # Step 7: Validate
    validation_results: Dict[str, Any]

    # Final
    summary: str
    learned_patterns: List[Dict[str, Any]]


class JadeTroubleshootingWorkflow:
    """
    LangGraph-based Kubernetes troubleshooting workflow

    Combines RAG (semantic search), Knowledge Graph (pattern matching),
    and LLM (reasoning) to diagnose and fix CrashLoopBackOff pods.
    """

    def __init__(self):
        """Initialize workflow with RAG, Graph, and LLM components"""
        print("🤖 Initializing Jade Troubleshooting Workflow...")

        self.rag = rag_engine
        self.graph = rag_graph_engine
        self.config = gp_config

        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

        print("✅ Jade Troubleshooting Workflow ready!")

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow with all nodes and edges"""
        workflow = StateGraph(TroubleshootingState)

        # Add nodes (steps in the workflow)
        workflow.add_node("identify_pods", self.identify_pods)
        workflow.add_node("diagnose_issues", self.diagnose_issues)
        workflow.add_node("query_knowledge", self.query_knowledge)
        workflow.add_node("generate_fixes", self.generate_fixes)
        workflow.add_node("await_approval", self.await_approval)
        workflow.add_node("execute_fixes", self.execute_fixes)
        workflow.add_node("validate_fixes", self.validate_fixes)
        workflow.add_node("learn_from_results", self.learn_from_results)

        # Define edges (workflow flow)
        workflow.add_edge("identify_pods", "diagnose_issues")
        workflow.add_edge("diagnose_issues", "query_knowledge")
        workflow.add_edge("query_knowledge", "generate_fixes")
        workflow.add_edge("generate_fixes", "await_approval")

        # Conditional edge based on human approval
        workflow.add_conditional_edges(
            "await_approval",
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

    def run(self, project: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Run the full troubleshooting workflow

        Args:
            project: Project name (e.g., "FINANCE")
            namespace: Kubernetes namespace

        Returns:
            Final state with summary and results
        """
        initial_state = {
            "project": project,
            "namespace": namespace,
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

        # Run workflow
        final_state = self.app.invoke(initial_state)

        return final_state

    # ========================================================================
    # WORKFLOW NODES
    # ========================================================================

    def identify_pods(self, state: TroubleshootingState) -> TroubleshootingState:
        """
        Step 1: Find all pods in CrashLoopBackOff state

        Actions:
            - kubectl get pods -n {namespace} -o json
            - Filter for CrashLoopBackOff status

        Output:
            - state['crashing_pods']: List of pod metadata
        """
        print(f"\n🔍 Step 1: Identifying CrashLoopBackOff pods in {state['namespace']}...")

        try:
            cmd = f"kubectl get pods -n {state['namespace']} -o json"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                print(f"⚠️  kubectl command failed: {result.stderr}")
                state['crashing_pods'] = []
                return state

            pods_data = json.loads(result.stdout)
            crashing_pods = []

            for item in pods_data.get('items', []):
                pod_name = item['metadata']['name']
                pod_namespace = item['metadata']['namespace']

                for container in item.get('status', {}).get('containerStatuses', []):
                    waiting = container.get('state', {}).get('waiting', {})
                    reason = waiting.get('reason', '')

                    if reason == 'CrashLoopBackOff':
                        crashing_pods.append({
                            'name': pod_name,
                            'namespace': pod_namespace,
                            'container': container['name'],
                            'restart_count': container.get('restartCount', 0),
                            'image': container['image'],
                            'crash_reason': waiting.get('message', 'Unknown')
                        })

            state['crashing_pods'] = crashing_pods
            print(f"✅ Found {len(crashing_pods)} crashing pods")

            for pod in crashing_pods:
                print(f"   - {pod['name']} (restarts: {pod['restart_count']})")

        except subprocess.TimeoutExpired:
            print("❌ kubectl command timed out")
            state['crashing_pods'] = []
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse kubectl output: {e}")
            state['crashing_pods'] = []
        except Exception as e:
            print(f"❌ Error identifying pods: {e}")
            state['crashing_pods'] = []

        return state

    def diagnose_issues(self, state: TroubleshootingState) -> TroubleshootingState:
        """
        Step 2: Gather diagnostic information and detect patterns

        Actions:
            - kubectl logs {pod} --tail=50
            - kubectl get events for pod
            - Pattern detection (OOMKilled, connection refused, etc.)

        Output:
            - state['diagnostics']: Logs and events per pod
            - state['detected_patterns']: List of detected issue patterns
        """
        print(f"\n🩺 Step 2: Diagnosing issues for {len(state['crashing_pods'])} pods...")

        diagnostics = {}
        all_patterns = []

        for pod in state['crashing_pods']:
            pod_name = pod['name']
            namespace = pod['namespace']

            print(f"   Diagnosing {pod_name}...")

            # Get logs
            logs_cmd = f"kubectl logs {pod_name} -n {namespace} --tail=50 2>&1"
            logs_result = subprocess.run(logs_cmd, shell=True, capture_output=True, text=True, timeout=30)
            logs = logs_result.stdout

            # Get events
            events_cmd = f"kubectl get events -n {namespace} --field-selector involvedObject.name={pod_name} -o json 2>&1"
            events_result = subprocess.run(events_cmd, shell=True, capture_output=True, text=True, timeout=30)

            try:
                events_json = json.loads(events_result.stdout)
                events = events_json.get('items', [])
            except:
                events = []

            # Detect patterns
            patterns = self._detect_patterns(logs, events)

            diagnostics[pod_name] = {
                'logs': logs,
                'events': events,
                'patterns': patterns,
                'restart_count': pod['restart_count']
            }

            all_patterns.extend(patterns)
            print(f"      Detected patterns: {', '.join(patterns) if patterns else 'None'}")

        state['diagnostics'] = diagnostics
        state['detected_patterns'] = list(set(all_patterns))

        print(f"✅ Diagnosis complete. Unique patterns: {', '.join(state['detected_patterns'])}")

        return state

    def query_knowledge(self, state: TroubleshootingState) -> TroubleshootingState:
        """
        Step 3: Query RAG and Knowledge Graph for similar issues

        Actions:
            - RAG semantic search for similar past issues
            - Graph traversal for pattern → solution mappings

        Output:
            - state['rag_context']: Similar past issues
            - state['graph_relationships']: Known solution patterns
        """
        print(f"\n🧠 Step 3: Querying knowledge base for similar issues...")

        rag_results = []
        graph_relationships = []

        # RAG queries for each detected pattern
        if self.rag:
            for pattern in state['detected_patterns']:
                query = f"Kubernetes pod CrashLoopBackOff {pattern} fix solution"
                print(f"   RAG query: '{query}'")

                try:
                    results = self.rag.query_knowledge(query, n_results=3)
                    rag_results.extend(results)
                    print(f"      Found {len(results)} similar issues")
                except Exception as e:
                    print(f"      ⚠️  RAG query failed: {e}")

            # Project-specific query
            project_query = f"CrashLoopBackOff issues in {state['project']} project"
            print(f"   RAG query: '{project_query}'")
            try:
                project_results = self.rag.query_knowledge(project_query, n_results=5)
                rag_results.extend(project_results)
                print(f"      Found {len(project_results)} project-specific issues")
            except Exception as e:
                print(f"      ⚠️  Project query failed: {e}")

        # Knowledge Graph queries
        if self.graph:
            for pattern in state['detected_patterns']:
                pattern_node = f"k8s_pattern_{pattern}"
                print(f"   Graph query: '{pattern_node}' → has_solution")

                try:
                    relationships = self.graph.get_relationships(
                        pattern_node,
                        relationship_type="has_solution"
                    )
                    graph_relationships.extend(relationships)
                    print(f"      Found {len(relationships)} known solutions")
                except Exception as e:
                    print(f"      ⚠️  Graph query failed: {e}")

        state['rag_context'] = rag_results
        state['graph_relationships'] = graph_relationships

        print(f"✅ Knowledge query complete: {len(rag_results)} RAG results, {len(graph_relationships)} graph patterns")

        return state

    def generate_fixes(self, state: TroubleshootingState) -> TroubleshootingState:
        """
        Step 4: Generate fix proposals using LLM + RAG + Graph context

        Actions:
            - Build context-rich prompts for each pod
            - Generate fix proposals with risk assessment

        Output:
            - state['fix_proposals']: List of fix proposals with commands
        """
        print(f"\n🔧 Step 4: Generating fix proposals...")

        fix_proposals = []

        for pod in state['crashing_pods']:
            pod_name = pod['name']
            diagnostics = state['diagnostics'].get(pod_name, {})
            patterns = diagnostics.get('patterns', [])

            print(f"   Generating fix for {pod_name}...")

            # For MVP, use rule-based fixes (later: LLM)
            fix = self._generate_rule_based_fix(pod, diagnostics, patterns, state)

            if fix:
                fix_proposals.append(fix)
                print(f"      ✅ Fix generated: {fix['proposed_solution']}")

        state['fix_proposals'] = fix_proposals

        print(f"✅ Generated {len(fix_proposals)} fix proposals")

        return state

    def await_approval(self, state: TroubleshootingState) -> TroubleshootingState:
        """
        Step 5: Present fix proposals to human and await decision

        Actions:
            - Display fix proposals with risk levels
            - Wait for human approval/rejection/more info

        Output:
            - state['approval_status']: approved/rejected/need_more_info
            - state['approved_fixes']: List of approved pod names
        """
        print(f"\n" + "="*70)
        print("📋 FIX PROPOSALS - Awaiting Human Approval")
        print("="*70)

        if not state['fix_proposals']:
            print("❌ No fix proposals generated")
            state['approval_status'] = "rejected"
            return state

        for idx, fix in enumerate(state['fix_proposals'], 1):
            print(f"\n{idx}. Pod: {fix['pod']}")
            print(f"   Container: {fix.get('container', 'unknown')}")
            print(f"   Namespace: {fix['namespace']}")
            print(f"   Root Cause: {fix['root_cause']}")
            print(f"   Proposed Fix: {fix['proposed_solution']}")
            print(f"   Risk Level: {fix['risk_level']}")
            print(f"   Confidence: {fix['confidence']*100:.0f}%")
            print(f"   Command: {fix['kubectl_command'][:80]}...")
            if fix.get('based_on'):
                print(f"   Based On: {fix['based_on']}")

        print(f"\n" + "="*70)

        # In production, this would be async via API
        # For MVP, use CLI input
        approval = input("\n👤 Approve fixes? (yes/no/more): ").strip().lower()

        if approval in ["yes", "y"]:
            state['approval_status'] = "approved"
            state['approved_fixes'] = [fix['pod'] for fix in state['fix_proposals']]
            print(f"✅ Approved {len(state['approved_fixes'])} fixes")
        elif approval in ["more", "m", "info"]:
            state['approval_status'] = "need_more_info"
            print("🔄 Requesting more information...")
        else:
            state['approval_status'] = "rejected"
            print("❌ Fixes rejected")

        return state

    def check_approval(self, state: TroubleshootingState) -> str:
        """
        Conditional routing based on approval status

        Routes:
            - "approved" → execute_fixes
            - "rejected" → END
            - "need_more_info" → diagnose_issues (loop back)
        """
        return state['approval_status']

    def execute_fixes(self, state: TroubleshootingState) -> TroubleshootingState:
        """
        Step 6: Execute approved fixes via kubectl commands

        Actions:
            - Run kubectl commands for approved fixes
            - Capture success/failure for each

        Output:
            - state['execution_results']: Success/failure per pod
        """
        print(f"\n⚙️  Step 6: Executing {len(state['approved_fixes'])} approved fixes...")

        execution_results = {}

        for fix in state['fix_proposals']:
            pod_name = fix['pod']

            if pod_name not in state['approved_fixes']:
                continue

            print(f"   Executing fix for {pod_name}...")

            try:
                cmd = fix['kubectl_command']
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                success = result.returncode == 0

                execution_results[pod_name] = {
                    'success': success,
                    'output': result.stdout,
                    'error': result.stderr,
                    'fix_applied': fix['proposed_solution']
                }

                if success:
                    print(f"      ✅ Fix applied successfully")
                else:
                    print(f"      ❌ Fix failed: {result.stderr[:100]}")

            except subprocess.TimeoutExpired:
                execution_results[pod_name] = {
                    'success': False,
                    'error': 'Command timed out'
                }
                print(f"      ❌ Fix timed out")
            except Exception as e:
                execution_results[pod_name] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"      ❌ Fix failed: {e}")

        state['execution_results'] = execution_results

        success_count = sum(1 for r in execution_results.values() if r['success'])
        print(f"✅ Executed {success_count}/{len(execution_results)} fixes successfully")

        return state

    def validate_fixes(self, state: TroubleshootingState) -> TroubleshootingState:
        """
        Step 7: Validate that fixes resolved the issues

        Actions:
            - Wait for pods to restart (10 seconds)
            - Check if pods are now Running

        Output:
            - state['validation_results']: Fixed status per pod
        """
        print(f"\n✓ Step 7: Validating fixes (waiting 10 seconds for pods to restart)...")
        time.sleep(10)

        validation_results = {}

        for pod_name in state['approved_fixes']:
            namespace = state['namespace']

            print(f"   Validating {pod_name}...")

            try:
                cmd = f"kubectl get pod {pod_name} -n {namespace} -o json"
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    pod_data = json.loads(result.stdout)
                    phase = pod_data.get('status', {}).get('phase', 'Unknown')

                    # Check if still crashing
                    is_crashing = False
                    for container in pod_data.get('status', {}).get('containerStatuses', []):
                        waiting = container.get('state', {}).get('waiting', {})
                        if waiting.get('reason') == 'CrashLoopBackOff':
                            is_crashing = True
                            break

                    fixed = (phase == 'Running' and not is_crashing)

                    validation_results[pod_name] = {
                        'fixed': fixed,
                        'phase': phase,
                        'is_crashing': is_crashing
                    }

                    if fixed:
                        print(f"      ✅ Pod is now Running")
                    else:
                        print(f"      ⚠️  Pod phase: {phase}, still crashing: {is_crashing}")
                else:
                    validation_results[pod_name] = {
                        'fixed': False,
                        'error': result.stderr
                    }
                    print(f"      ❌ Failed to validate: {result.stderr[:50]}")

            except Exception as e:
                validation_results[pod_name] = {
                    'fixed': False,
                    'error': str(e)
                }
                print(f"      ❌ Validation error: {e}")

        state['validation_results'] = validation_results

        fixed_count = sum(1 for v in validation_results.values() if v.get('fixed', False))
        print(f"✅ Validation complete: {fixed_count}/{len(validation_results)} pods fixed")

        return state

    def learn_from_results(self, state: TroubleshootingState) -> TroubleshootingState:
        """
        Step 8: Store results in RAG + Knowledge Graph for future learning

        Actions:
            - Store successful fixes in RAG (action_history collection)
            - Update Knowledge Graph with pattern → solution relationships
            - Generate final summary

        Output:
            - state['summary']: Human-readable summary
            - state['learned_patterns']: Patterns learned this session
        """
        print(f"\n📚 Step 8: Learning from results...")

        learned_patterns = []

        # Calculate metrics
        total_pods = len(state['crashing_pods'])
        diagnosed_pods = len(state['diagnostics'])
        fixes_proposed = len(state['fix_proposals'])
        fixes_approved = len(state['approved_fixes'])
        fixes_executed = len(state['execution_results'])
        fixes_successful = sum(1 for v in state['validation_results'].values() if v.get('fixed', False))

        # Store in RAG
        if self.rag and fixes_executed > 0:
            action_doc = {
                'action': 'troubleshoot_crashloopbackoff',
                'project': state['project'],
                'namespace': state['namespace'],
                'timestamp': datetime.now().isoformat(),
                'pods_affected': total_pods,
                'patterns_detected': state['detected_patterns'],
                'fixes_proposed': fixes_proposed,
                'fixes_approved': fixes_approved,
                'fixes_successful': fixes_successful,
                'success_rate': fixes_successful / fixes_executed if fixes_executed > 0 else 0,
                'fix_details': state['fix_proposals']
            }

            try:
                # Store as document in action_history collection
                doc_text = json.dumps(action_doc, indent=2)
                self.rag.add_to_collection('action_history', [doc_text])
                print(f"   ✅ Stored action in RAG (action_history collection)")
            except Exception as e:
                print(f"   ⚠️  Failed to store in RAG: {e}")

        # Update Knowledge Graph
        if self.graph:
            for fix in state['fix_proposals']:
                pod_name = fix['pod']

                # Only learn from successful fixes
                if state['validation_results'].get(pod_name, {}).get('fixed', False):
                    pattern = fix.get('pattern_detected', 'unknown')
                    solution = fix.get('solution_id', 'unknown')

                    try:
                        self.graph.add_relationship(
                            f"k8s_pattern_{pattern}",
                            f"solution_{solution}",
                            "has_solution",
                            metadata={
                                'project': state['project'],
                                'success': True,
                                'timestamp': datetime.now().isoformat()
                            }
                        )

                        learned_patterns.append({
                            'pattern': pattern,
                            'solution': solution,
                            'success': True
                        })

                        print(f"   ✅ Added graph relationship: {pattern} → {solution}")
                    except Exception as e:
                        print(f"   ⚠️  Failed to update graph: {e}")

        state['learned_patterns'] = learned_patterns

        # Generate summary
        summary_lines = [
            f"\n{'='*70}",
            f"🎯 TROUBLESHOOTING SUMMARY - {state['project']} Project",
            f"{'='*70}",
            f"\n📊 Metrics:",
            f"   • Crashing pods found: {total_pods}",
            f"   • Pods diagnosed: {diagnosed_pods}",
            f"   • Patterns detected: {len(state['detected_patterns'])}",
            f"   • Fixes proposed: {fixes_proposed}",
            f"   • Fixes approved: {fixes_approved}",
            f"   • Fixes executed: {fixes_executed}",
            f"   • Fixes successful: {fixes_successful}",
            f"   • Success rate: {fixes_successful/fixes_executed*100:.0f}%" if fixes_executed > 0 else "   • Success rate: N/A",
            f"\n🔍 Detected Patterns:",
        ]

        for pattern in state['detected_patterns']:
            summary_lines.append(f"   • {pattern}")

        if fixes_successful > 0:
            summary_lines.append(f"\n✅ Successfully Fixed Pods:")
            for pod_name, result in state['validation_results'].items():
                if result.get('fixed', False):
                    fix = next((f for f in state['fix_proposals'] if f['pod'] == pod_name), {})
                    summary_lines.append(f"   • {pod_name}: {fix.get('proposed_solution', 'Fixed')}")

        if learned_patterns:
            summary_lines.append(f"\n📚 Learned Patterns:")
            for lp in learned_patterns:
                summary_lines.append(f"   • {lp['pattern']} → {lp['solution']}")

        summary_lines.append(f"\n{'='*70}\n")

        state['summary'] = "\n".join(summary_lines)

        print(state['summary'])

        return state

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _detect_patterns(self, logs: str, events: List[Dict]) -> List[str]:
        """
        Detect crash patterns from logs and events

        Patterns:
            - memory_limit_exceeded (OOMKilled)
            - dependency_unavailable (connection refused)
            - permission_issue (permission denied)
            - missing_config_or_volume (no such file)
            - application_panic (panic, fatal error)
            - port_conflict (address already in use)
        """
        patterns = []

        logs_lower = logs.lower()

        # Check events for OOMKilled
        for event in events:
            reason = event.get('reason', '')
            message = event.get('message', '')

            if reason == 'OOMKilled' or 'OOMKilled' in message:
                patterns.append('memory_limit_exceeded')
            if 'BackOff' in reason:
                patterns.append('crash_backoff')

        # Check logs for patterns
        if 'oomkilled' in logs_lower or 'out of memory' in logs_lower:
            patterns.append('memory_limit_exceeded')

        if 'connection refused' in logs_lower or 'connection timeout' in logs_lower:
            patterns.append('dependency_unavailable')

        if 'permission denied' in logs_lower or 'forbidden' in logs_lower:
            patterns.append('permission_issue')

        if 'no such file' in logs_lower or 'cannot find' in logs_lower:
            patterns.append('missing_config_or_volume')

        if 'panic:' in logs or 'fatal' in logs_lower or 'segmentation fault' in logs_lower:
            patterns.append('application_panic')

        if 'address already in use' in logs_lower or 'port.*in use' in logs_lower:
            patterns.append('port_conflict')

        # Return unique patterns
        return list(set(patterns))

    def _generate_rule_based_fix(
        self,
        pod: Dict[str, Any],
        diagnostics: Dict[str, Any],
        patterns: List[str],
        state: TroubleshootingState
    ) -> Optional[Dict[str, Any]]:
        """
        Generate fix using rule-based logic (MVP approach)

        Later: Replace with LLM-generated fixes using RAG + Graph context
        """
        pod_name = pod['name']
        namespace = pod['namespace']
        container = pod['container']

        # Rule-based fixes for common patterns
        if 'memory_limit_exceeded' in patterns:
            # Get deployment name (strip replica hash)
            deployment_name = '-'.join(pod_name.split('-')[:-2])

            return {
                'pod': pod_name,
                'namespace': namespace,
                'container': container,
                'root_cause': 'Memory limit exceeded (OOMKilled). Container requires more memory than allocated.',
                'proposed_solution': 'Increase memory limit from current to 512Mi',
                'kubectl_command': f"kubectl patch deployment {deployment_name} -n {namespace} -p '{{\"spec\":{{\"template\":{{\"spec\":{{\"containers\":[{{\"name\":\"{container}\",\"resources\":{{\"limits\":{{\"memory\":\"512Mi\"}},\"requests\":{{\"memory\":\"384Mi\"}}}}}}]}}}}}}}}'",
                'risk_level': 'LOW',
                'confidence': 0.85,
                'based_on': 'Common pattern: OOMKilled → increase memory',
                'rollback_plan': f"kubectl patch deployment {deployment_name} -n {namespace} -p '{{\"spec\":{{\"template\":{{\"spec\":{{\"containers\":[{{\"name\":\"{container}\",\"resources\":{{\"limits\":{{\"memory\":\"256Mi\"}}}}}}]}}}}}}}}'",
                'pattern_detected': 'memory_limit_exceeded',
                'solution_id': 'increase_memory_512Mi'
            }

        elif 'dependency_unavailable' in patterns:
            deployment_name = '-'.join(pod_name.split('-')[:-2])

            return {
                'pod': pod_name,
                'namespace': namespace,
                'container': container,
                'root_cause': 'Dependency service unavailable (connection refused). Service may not be ready.',
                'proposed_solution': 'Add readiness probe and increase initialDelaySeconds',
                'kubectl_command': f"kubectl patch deployment {deployment_name} -n {namespace} -p '{{\"spec\":{{\"template\":{{\"spec\":{{\"containers\":[{{\"name\":\"{container}\",\"readinessProbe\":{{\"httpGet\":{{\"path\":\"/health\",\"port\":8080}},\"initialDelaySeconds\":30,\"periodSeconds\":10}}}}]}}}}}}}}'",
                'risk_level': 'MEDIUM',
                'confidence': 0.70,
                'based_on': 'Connection refused often means dependency not ready',
                'rollback_plan': f"kubectl rollout undo deployment {deployment_name} -n {namespace}",
                'pattern_detected': 'dependency_unavailable',
                'solution_id': 'add_readiness_probe'
            }

        elif 'missing_config_or_volume' in patterns:
            return {
                'pod': pod_name,
                'namespace': namespace,
                'container': container,
                'root_cause': 'Missing configuration file or volume mount',
                'proposed_solution': 'Manual investigation required - check ConfigMap/Secret mounts',
                'kubectl_command': f"echo 'Manual fix required: kubectl describe pod {pod_name} -n {namespace}'",
                'risk_level': 'HIGH',
                'confidence': 0.50,
                'based_on': 'Missing file errors require manual investigation',
                'rollback_plan': 'N/A - manual fix',
                'pattern_detected': 'missing_config_or_volume',
                'solution_id': 'manual_investigation'
            }

        else:
            # Generic fix for unknown patterns
            return {
                'pod': pod_name,
                'namespace': namespace,
                'container': container,
                'root_cause': 'Unknown crash pattern. Check logs manually.',
                'proposed_solution': 'Recommend manual investigation',
                'kubectl_command': f"kubectl logs {pod_name} -n {namespace} --tail=100",
                'risk_level': 'LOW',
                'confidence': 0.30,
                'based_on': 'Generic troubleshooting approach',
                'rollback_plan': 'N/A',
                'pattern_detected': 'unknown',
                'solution_id': 'manual_logs_check'
            }


# ============================================================================
# MAIN - Test workflow
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Jade Kubernetes Troubleshooting Workflow")
    parser.add_argument("project", help="Project name (e.g., FINANCE)")
    parser.add_argument("--namespace", default="default", help="Kubernetes namespace")

    args = parser.parse_args()

    print("🤖 Starting Jade Troubleshooting Workflow")
    print(f"   Project: {args.project}")
    print(f"   Namespace: {args.namespace}")

    workflow = JadeTroubleshootingWorkflow()
    result = workflow.run(project=args.project, namespace=args.namespace)

    print("\n" + "="*70)
    print("✅ WORKFLOW COMPLETE")
    print("="*70)

    if result.get('summary'):
        print(result['summary'])
