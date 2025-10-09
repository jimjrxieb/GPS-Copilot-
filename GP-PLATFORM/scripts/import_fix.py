#!/usr/bin/env python3
"""
Import Path Fix for Categorical Architecture
===========================================

Fixes import paths after reorganization into categorical structure.
"""

import sys
import os
from pathlib import Path

def setup_categorical_imports():
    """Add categorical directories to Python path"""
    base_path = Path(__file__).parent

    # Add categorical directories to path
    categorical_dirs = [
        'GP-CORE-PLATFORM-ARCHITECTURE',
        'GP-SEC-INTEL-ANALYSIS',
        'GP-SEC-TOOLS-EXECUTION',
        'GP-CONSULTING-AGENTS',
        'GP-CONFIG-OPS',
        'GP-TESTING-VAL'
    ]

    for cat_dir in categorical_dirs:
        cat_path = str(base_path / cat_dir)
        if cat_path not in sys.path:
            sys.path.insert(0, cat_path)

    # Add base path
    if str(base_path) not in sys.path:
        sys.path.insert(0, str(base_path))

    print(f"Added {len(categorical_dirs)} categorical directories to Python path")

def test_imports():
    """Test critical imports after path setup"""
    results = {}

    # Test automation_engine
    try:
        from automation_engine.automation.remediation.container_image_updater import ContainerImageUpdater
        results['automation_engine'] = 'SUCCESS'
    except Exception as e:
        results['automation_engine'] = f'FAILED: {e}'

    # Test scanner agent
    try:
        from agents.scanner_agent.agent import ScannerAgent
        results['scanner_agent'] = 'SUCCESS'
    except Exception as e:
        results['scanner_agent'] = f'FAILED: {e}'

    # Test coordination
    try:
        from coordination.crew_orchestrator import CrewOrchestrator
        results['coordination'] = 'SUCCESS'
    except Exception as e:
        results['coordination'] = f'FAILED: {e}'

    # Test workflow
    try:
        from workflow.work_order_processor import WorkOrderProcessor
        results['workflow'] = 'SUCCESS'
    except Exception as e:
        results['workflow'] = f'FAILED: {e}'

    return results

if __name__ == "__main__":
    setup_categorical_imports()

    print("Testing imports after categorical path setup...")
    results = test_imports()

    for component, status in results.items():
        if 'SUCCESS' in status:
            print(f"✅ {component}: {status}")
        else:
            print(f"❌ {component}: {status}")

    success_count = sum(1 for r in results.values() if 'SUCCESS' in r)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100

    print(f"\nImport Success Rate: {success_rate:.1f}% ({success_count}/{total_count})")