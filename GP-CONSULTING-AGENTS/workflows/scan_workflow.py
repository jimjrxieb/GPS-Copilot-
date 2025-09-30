#!/usr/bin/env python3
"""Scan Workflow - Orchestrates all security scanners"""
import sys
from pathlib import Path

def run_scan_workflow(project_path, scanners="all"):
    """Run security scanning workflow"""
    from scanners.run_all_scanners import main as run_all
    return run_all([project_path])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: scan_workflow.py <project_path> [scanner_name]")
        sys.exit(1)
    run_scan_workflow(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "all")
