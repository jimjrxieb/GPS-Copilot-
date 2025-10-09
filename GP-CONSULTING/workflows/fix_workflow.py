#!/usr/bin/env python3
"""Fix Workflow - Orchestrates all security fixers"""
import sys

def run_fix_workflow(scan_results_path, project_path):
    """Run security fixing workflow"""
    from fixers.apply_all_fixes import main as apply_fixes
    return apply_fixes([scan_results_path, project_path])

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: fix_workflow.py <scan_results.json> <project_path>")
        sys.exit(1)
    run_fix_workflow(sys.argv[1], sys.argv[2])
