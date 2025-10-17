#!/usr/bin/env python3
"""
Test Script for Jade Troubleshooting Workflow

Tests the LangGraph workflow with a mock Kubernetes environment
"""

import sys
from pathlib import Path

# Add paths
gp_copilot_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from jade_troubleshooting_workflow import JadeTroubleshootingWorkflow

def test_workflow_dry_run():
    """Test workflow with dry run (no actual kubectl commands)"""
    print("="*70)
    print("🧪 TESTING JADE TROUBLESHOOTING WORKFLOW")
    print("="*70)

    print("\n📋 Test Scenario:")
    print("   Project: TEST-PROJECT")
    print("   Namespace: default")
    print("   Expected: Workflow should complete all steps")
    print("   Note: Will fail at kubectl commands (no cluster), but workflow logic will run")

    workflow = JadeTroubleshootingWorkflow()

    print("\n🚀 Running workflow...")

    try:
        result = workflow.run(
            project="TEST-PROJECT",
            namespace="default"
        )

        print("\n✅ Workflow completed!")
        print(f"\nFinal State Keys: {list(result.keys())}")

        if result.get('summary'):
            print(result['summary'])
        else:
            print("\nSummary:")
            print(f"   Crashing pods found: {len(result.get('crashing_pods', []))}")
            print(f"   Patterns detected: {len(result.get('detected_patterns', []))}")
            print(f"   Fixes proposed: {len(result.get('fix_proposals', []))}")
            print(f"   Approval status: {result.get('approval_status', 'N/A')}")

        return True

    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_structure():
    """Test that workflow structure is correctly built"""
    print("\n" + "="*70)
    print("🧪 TESTING WORKFLOW STRUCTURE")
    print("="*70)

    workflow = JadeTroubleshootingWorkflow()

    # Check nodes exist
    expected_nodes = [
        "identify_pods",
        "diagnose_issues",
        "query_knowledge",
        "generate_fixes",
        "await_approval",
        "execute_fixes",
        "validate_fixes",
        "learn_from_results"
    ]

    print("\n✅ Checking workflow nodes...")
    for node in expected_nodes:
        if hasattr(workflow, node):
            print(f"   ✓ {node}")
        else:
            print(f"   ✗ {node} - MISSING!")
            return False

    print("\n✅ All nodes present!")
    return True

def test_pattern_detection():
    """Test pattern detection logic"""
    print("\n" + "="*70)
    print("🧪 TESTING PATTERN DETECTION")
    print("="*70)

    workflow = JadeTroubleshootingWorkflow()

    # Test cases
    test_cases = [
        {
            "logs": "Error: OOMKilled - process terminated",
            "events": [{"reason": "OOMKilled", "message": "Container exceeded memory limit"}],
            "expected": ["memory_limit_exceeded"]
        },
        {
            "logs": "Connection refused on port 5432",
            "events": [],
            "expected": ["dependency_unavailable"]
        },
        {
            "logs": "panic: runtime error: invalid memory address",
            "events": [],
            "expected": ["application_panic"]
        },
        {
            "logs": "No such file or directory: /config/app.yaml",
            "events": [],
            "expected": ["missing_config_or_volume"]
        }
    ]

    print("\n✅ Running pattern detection tests...")
    all_passed = True

    for idx, test in enumerate(test_cases, 1):
        patterns = workflow._detect_patterns(test["logs"], test["events"])
        expected = test["expected"]

        # Check if expected patterns are detected
        passed = all(p in patterns for p in expected)

        if passed:
            print(f"   ✓ Test {idx}: {expected[0]} - Detected: {patterns}")
        else:
            print(f"   ✗ Test {idx}: Expected {expected}, got {patterns}")
            all_passed = False

    if all_passed:
        print("\n✅ All pattern detection tests passed!")
    else:
        print("\n❌ Some pattern detection tests failed")

    return all_passed

def test_fix_generation():
    """Test rule-based fix generation"""
    print("\n" + "="*70)
    print("🧪 TESTING FIX GENERATION")
    print("="*70)

    workflow = JadeTroubleshootingWorkflow()

    # Test pod with memory issue
    pod = {
        'name': 'api-deployment-abc123',
        'namespace': 'default',
        'container': 'api',
        'restart_count': 47,
        'image': 'finance-api:v1.2.3'
    }

    diagnostics = {
        'logs': 'OOMKilled',
        'events': [],
        'patterns': ['memory_limit_exceeded']
    }

    patterns = ['memory_limit_exceeded']
    state = {'project': 'TEST', 'namespace': 'default'}

    print("\n✅ Generating fix for memory_limit_exceeded pattern...")
    fix = workflow._generate_rule_based_fix(pod, diagnostics, patterns, state)

    if fix:
        print(f"   ✓ Root cause: {fix['root_cause']}")
        print(f"   ✓ Solution: {fix['proposed_solution']}")
        print(f"   ✓ Risk level: {fix['risk_level']}")
        print(f"   ✓ Confidence: {fix['confidence']*100}%")
        print(f"   ✓ Command generated: {len(fix['kubectl_command'])} chars")
        print("\n✅ Fix generation successful!")
        return True
    else:
        print("\n❌ Fix generation failed!")
        return False

if __name__ == "__main__":
    print("\n🧪 JADE TROUBLESHOOTING WORKFLOW - TEST SUITE")
    print("="*70)

    results = {
        "Workflow Structure": test_workflow_structure(),
        "Pattern Detection": test_pattern_detection(),
        "Fix Generation": test_fix_generation(),
        "Full Workflow Dry Run": test_workflow_dry_run()
    }

    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)
