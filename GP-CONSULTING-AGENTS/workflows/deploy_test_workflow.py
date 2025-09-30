#!/usr/bin/env python3
"""Deploy & Test Workflow - CKS-level cluster testing"""
import sys

def run_deploy_test_workflow(project_path):
    """Run deploy and test workflow"""
    from agents.kubernetes_agent.deploy_and_test import main as deploy_test
    return deploy_test([project_path])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: deploy_test_workflow.py <project_path>")
        sys.exit(1)
    run_deploy_test_workflow(sys.argv[1])
