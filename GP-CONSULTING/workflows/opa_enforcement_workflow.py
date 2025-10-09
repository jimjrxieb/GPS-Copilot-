"""
OPA Policy Enforcement Workflow

Specialized workflow for OPA/Gatekeeper policy development and enforcement.

This workflow:
1. Scans Terraform/Kubernetes with OPA
2. Analyzes violations
3. Generates fixes OR generates new policies
4. Validates policies
5. Deploys to cluster (Gatekeeper) or CI/CD (Terraform)

This is what makes Jade a "policy as code" expert.
"""

import sys
from pathlib import Path
from typing import TypedDict, Literal
from datetime import datetime
import json
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph.graph import StateGraph, END
from tools.base_registry import ToolRegistry
from tools.scanner_tools import register_scanner_tools
from tools.fixer_tools import register_fixer_tools
from tools.validator_tools import register_validator_tools


# ==================== State Definition ====================

class OPAWorkflowState(TypedDict):
    """State for OPA enforcement workflow"""
    # Input
    task: str                           # "enforce opa policy" or "create new policy"
    target_path: str                    # Path to Terraform/K8s files
    policy_type: str                    # "terraform" or "kubernetes"

    # Workflow mode
    mode: str                           # "enforce" or "generate"

    # Scan results
    opa_results: dict                   # OPA scan results
    violations: list                    # List of violations found

    # For enforcement mode
    fixes_applied: list                 # Applied fixes
    rescan_results: dict                # Results after fixes

    # For generation mode
    violation_pattern: dict             # Pattern extracted from violation
    new_policy: dict                    # Generated policy
    policy_tests: list                  # Generated tests
    policy_path: str                    # Where policy was saved

    # Validation
    validation_results: dict            # Policy validation results
    success: bool

    # Metadata
    workflow_id: str
    started_at: str
    ended_at: str


# ==================== Workflow Steps ====================

def step_scan_with_opa(state: OPAWorkflowState) -> OPAWorkflowState:
    """Scan target with OPA policies"""
    print(f"\n🔍 Scanning {state['target_path']} with OPA...")

    policy_bundle = f"{state['policy_type']}-security"

    result = ToolRegistry.execute_tool(
        "scan_iac_opa",
        target_path=state['target_path'],
        policy_bundle=policy_bundle
    )

    state['opa_results'] = result.get('data', {})

    # Extract violations
    violations = []
    opa_data = state['opa_results']

    # OPA results format varies, extract violations
    # This is simplified - real implementation would parse OPA JSON output
    if 'violations' in opa_data:
        violations = opa_data['violations']
    elif 'result' in opa_data:
        # Parse result for deny rules
        for result in opa_data.get('result', []):
            if 'deny' in result:
                violations.extend(result['deny'])

    state['violations'] = violations

    print(f"✅ OPA scan complete: {len(violations)} violations found")

    return state


def step_decide_mode(state: OPAWorkflowState) -> Literal["enforce", "generate"]:
    """
    Decide whether to:
    - enforce: Fix existing violations with known patterns
    - generate: Create new policy for unknown patterns
    """
    # Check if violations can be auto-fixed
    auto_fixable = sum(1 for v in state['violations'] if v.get('fixable', False))

    if auto_fixable > len(state['violations']) / 2:
        # More than half are auto-fixable
        return "enforce"
    else:
        # Generate new policies for unfixable violations
        return "generate"


def step_enforce_policies(state: OPAWorkflowState) -> OPAWorkflowState:
    """Apply fixes for OPA violations"""
    print(f"\n🔧 Enforcing OPA policies...")

    if state['policy_type'] == 'terraform':
        fixer = 'fix_terraform_issues'
    else:
        fixer = 'fix_kubernetes_issues'

    # Apply fixes
    fix_result = ToolRegistry.execute_tool(
        fixer,
        scan_results={'findings': state['violations']},
        issue_types=['all']
    )

    state['fixes_applied'] = fix_result.get('data', {}).get('details', [])

    print(f"✅ Applied {len(state['fixes_applied'])} fixes")

    return state


def step_generate_new_policy(state: OPAWorkflowState) -> OPAWorkflowState:
    """
    Generate new OPA policy from violation patterns

    This is Jade's "learning" capability - creating new policies
    from patterns it encounters.
    """
    print(f"\n📝 Generating new OPA policy...")

    # Take first violation as pattern
    if not state['violations']:
        print("   No violations to learn from")
        return state

    violation = state['violations'][0]

    # Extract pattern
    pattern = {
        "resource_type": violation.get('resource_type'),
        "violation_type": violation.get('type'),
        "condition": violation.get('condition'),
        "severity": violation.get('severity', 'MEDIUM'),
    }

    state['violation_pattern'] = pattern

    # Generate policy name
    policy_name = f"deny_{violation.get('resource_type', 'resource')}_{violation.get('type', 'violation')}"
    policy_name = policy_name.replace(' ', '_').lower()

    # Generate OPA policy using fixer tool
    policy_result = ToolRegistry.execute_tool(
        'generate_opa_policy',
        violation_pattern=pattern,
        policy_name=policy_name,
        policy_type=state['policy_type']
    )

    state['new_policy'] = policy_result.get('data', {})

    # Save policy
    policies_dir = Path(__file__).parent.parent / f"GP-POL-AS-CODE/1-POLICIES/opa/{state['policy_type']}"
    policies_dir.mkdir(parents=True, exist_ok=True)

    policy_file = policies_dir / f"{policy_name}.rego"
    policy_file.write_text(state['new_policy'].get('policy_code', ''))

    state['policy_path'] = str(policy_file)

    # Generate tests
    test_file = policies_dir / f"{policy_name}_test.rego"
    test_file.write_text(state['new_policy'].get('test_code', ''))

    print(f"✅ Generated policy: {policy_file}")

    return state


def step_validate_policies(state: OPAWorkflowState) -> OPAWorkflowState:
    """Validate OPA policies"""
    print(f"\n✓ Validating OPA policies...")

    if state['mode'] == 'generate' and state['policy_path']:
        # Validate newly generated policy
        validation = ToolRegistry.execute_tool(
            'validate_opa_policy',
            policy_path=state['policy_path']
        )

        state['validation_results'] = validation.get('data', {})
        state['success'] = validation.get('data', {}).get('valid', False)

    else:
        # Re-scan to verify fixes
        rescan = ToolRegistry.execute_tool(
            'scan_iac_opa',
            target_path=state['target_path'],
            policy_bundle=f"{state['policy_type']}-security"
        )

        state['rescan_results'] = rescan.get('data', {})

        # Compare before/after
        before_count = len(state['violations'])
        after_count = len(rescan.get('data', {}).get('violations', []))

        state['success'] = after_count < before_count

    print(f"✅ Validation complete: {'PASSED' if state['success'] else 'FAILED'}")

    return state


def step_deploy_policy(state: OPAWorkflowState) -> OPAWorkflowState:
    """
    Deploy OPA policy

    For Kubernetes: Convert to Gatekeeper ConstraintTemplate + Constraint
    For Terraform: Add to CI/CD pipeline
    """
    print(f"\n🚀 Deploying OPA policy...")

    if state['policy_type'] == 'kubernetes' and state['mode'] == 'generate':
        # Convert OPA policy to Gatekeeper constraint
        policy_name = Path(state['policy_path']).stem

        # Generate ConstraintTemplate
        constraint_template = {
            "apiVersion": "templates.gatekeeper.sh/v1beta1",
            "kind": "ConstraintTemplate",
            "metadata": {
                "name": policy_name,
                "annotations": {
                    "description": state['violation_pattern'].get('violation_type'),
                    "generated_by": "jade",
                    "generated_at": datetime.now().isoformat(),
                }
            },
            "spec": {
                "crd": {
                    "spec": {
                        "names": {
                            "kind": policy_name.title().replace('_', ''),
                        }
                    }
                },
                "targets": [{
                    "target": "admission.k8s.gatekeeper.sh",
                    "rego": Path(state['policy_path']).read_text()
                }]
            }
        }

        # Save ConstraintTemplate
        gatekeeper_dir = Path(__file__).parent.parent / "GP-POL-AS-CODE/2-AUTOMATION/gatekeeper"
        gatekeeper_dir.mkdir(parents=True, exist_ok=True)

        template_file = gatekeeper_dir / f"{policy_name}-template.yaml"
        template_file.write_text(yaml.dump(constraint_template))

        # Generate Constraint
        constraint = {
            "apiVersion": "constraints.gatekeeper.sh/v1beta1",
            "kind": policy_name.title().replace('_', ''),
            "metadata": {
                "name": f"{policy_name}-constraint"
            },
            "spec": {
                "match": {
                    "kinds": [{"apiGroups": ["*"], "kinds": ["*"]}]
                },
                "parameters": {}
            }
        }

        constraint_file = gatekeeper_dir / f"{policy_name}-constraint.yaml"
        constraint_file.write_text(yaml.dump(constraint))

        print(f"✅ Gatekeeper policy deployed:")
        print(f"   Template: {template_file}")
        print(f"   Constraint: {constraint_file}")

    elif state['policy_type'] == 'terraform':
        # Add to Terraform CI/CD
        cicd_dir = Path(__file__).parent.parent / "GP-POL-AS-CODE/2-AUTOMATION/cicd"
        cicd_dir.mkdir(parents=True, exist_ok=True)

        # Generate GitHub Actions workflow
        workflow = {
            "name": "Terraform OPA Validation",
            "on": ["pull_request"],
            "jobs": {
                "opa_validate": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v2"},
                        {
                            "name": "Run OPA validation",
                            "run": f"opa eval --data GP-POL-AS-CODE/1-POLICIES/opa/terraform --input ${{{{ github.workspace }}}}/terraform --format pretty data"
                        }
                    ]
                }
            }
        }

        workflow_file = cicd_dir / "terraform-opa-validation.yml"
        workflow_file.write_text(yaml.dump(workflow))

        print(f"✅ CI/CD pipeline updated: {workflow_file}")

    return state


def step_report(state: OPAWorkflowState) -> OPAWorkflowState:
    """Generate final report"""
    print(f"\n📊 Generating report...")

    state['ended_at'] = datetime.now().isoformat()

    report = {
        "workflow_id": state['workflow_id'],
        "task": state['task'],
        "target": state['target_path'],
        "mode": state['mode'],
        "policy_type": state['policy_type'],
        "violations_found": len(state['violations']),
        "fixes_applied": len(state.get('fixes_applied', [])),
        "new_policies_generated": 1 if state.get('new_policy') else 0,
        "success": state['success'],
        "duration": f"{state['started_at']} to {state['ended_at']}",
    }

    # Save report
    reports_dir = Path(__file__).parent.parent.parent / "GP-DATA/active/reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_file = reports_dir / f"opa_workflow_{state['workflow_id']}.json"
    report_file.write_text(json.dumps(report, indent=2))

    print(f"✅ Report saved: {report_file}")

    return state


# ==================== Build Workflow ====================

def create_opa_workflow():
    """Build OPA enforcement workflow graph"""

    register_scanner_tools()
    register_fixer_tools()
    register_validator_tools()

    workflow = StateGraph(OPAWorkflowState)

    # Add nodes
    workflow.add_node("scan", step_scan_with_opa)
    workflow.add_node("enforce", step_enforce_policies)
    workflow.add_node("generate", step_generate_new_policy)
    workflow.add_node("validate", step_validate_policies)
    workflow.add_node("deploy", step_deploy_policy)
    workflow.add_node("report", step_report)

    # Add edges
    workflow.set_entry_point("scan")

    # Conditional routing
    workflow.add_conditional_edges(
        "scan",
        step_decide_mode,
        {
            "enforce": "enforce",
            "generate": "generate",
        }
    )

    workflow.add_edge("enforce", "validate")
    workflow.add_edge("generate", "validate")
    workflow.add_edge("validate", "deploy")
    workflow.add_edge("deploy", "report")
    workflow.add_edge("report", END)

    return workflow.compile()


# ==================== Public API ====================

def run_opa_workflow(task: str, target_path: str, policy_type: str = "terraform") -> dict:
    """
    Run OPA enforcement workflow

    Usage:
        # Enforce existing policies
        run_opa_workflow(
            task="enforce opa terraform policies",
            target_path="GP-PROJECTS/Terraform_CICD_Setup",
            policy_type="terraform"
        )

        # Generate new policy from violations
        run_opa_workflow(
            task="create opa policy for kubernetes violations",
            target_path="k8s/",
            policy_type="kubernetes"
        )
    """
    import uuid

    initial_state = {
        "task": task,
        "target_path": target_path,
        "policy_type": policy_type,
        "mode": "enforce" if "enforce" in task.lower() else "generate",
        "opa_results": {},
        "violations": [],
        "fixes_applied": [],
        "rescan_results": {},
        "violation_pattern": {},
        "new_policy": {},
        "policy_tests": [],
        "policy_path": "",
        "validation_results": {},
        "success": False,
        "workflow_id": str(uuid.uuid4())[:8],
        "started_at": datetime.now().isoformat(),
        "ended_at": "",
    }

    print(f"\n{'='*60}")
    print(f"🛡️  Jade OPA Policy Enforcement Workflow")
    print(f"{'='*60}")
    print(f"Task: {task}")
    print(f"Target: {target_path}")
    print(f"Policy Type: {policy_type}")
    print(f"Mode: {initial_state['mode']}")
    print(f"{'='*60}\n")

    workflow = create_opa_workflow()
    final_state = workflow.invoke(initial_state)

    print(f"\n{'='*60}")
    print(f"✅ OPA Workflow Complete")
    print(f"{'='*60}\n")

    return final_state


if __name__ == "__main__":
    # Test OPA workflow
    result = run_opa_workflow(
        task="Enforce OPA policies on Terraform",
        target_path="GP-PROJECTS/Terraform_CICD_Setup",
        policy_type="terraform"
    )

    print(f"\nFinal Result:")
    print(f"  Success: {result['success']}")
    print(f"  Mode: {result['mode']}")
    print(f"  Violations: {len(result['violations'])}")
    print(f"  Fixes: {len(result.get('fixes_applied', []))}")