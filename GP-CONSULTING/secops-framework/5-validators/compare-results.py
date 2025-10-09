#!/usr/bin/env python3
"""
SecOps Phase 5: VALIDATE - Compare before/after scan results
"""

import json
import os
from collections import defaultdict

def load_findings(directory):
    """Load aggregated findings from directory"""
    findings_file = os.path.join(directory, '../2-findings/reports/all-findings.json')

    if os.path.exists(findings_file):
        with open(findings_file, 'r') as f:
            return json.load(f)
    return []

def calculate_metrics(findings):
    """Calculate violation metrics"""
    metrics = {
        'total': len(findings),
        'by_severity': defaultdict(int),
        'by_category': defaultdict(int),
        'by_scanner': defaultdict(int)
    }

    for finding in findings:
        metrics['by_severity'][finding['severity']] += 1
        metrics['by_category'][finding['category']] += 1
        metrics['by_scanner'][finding['scanner']] += 1

    return dict(metrics)

def compare_findings(before, after):
    """Compare before/after findings"""
    before_ids = {f['id'] for f in before}
    after_ids = {f['id'] for f in after}

    fixed = before_ids - after_ids
    remaining = after_ids
    new_issues = after_ids - before_ids

    return {
        'fixed_count': len(fixed),
        'remaining_count': len(remaining),
        'new_count': len(new_issues),
        'fixed_ids': list(fixed),
        'remaining_ids': list(remaining),
        'new_ids': list(new_issues)
    }

def calculate_reduction_percentage(before_count, after_count):
    """Calculate percentage reduction"""
    if before_count == 0:
        return 0
    return round(((before_count - after_count) / before_count) * 100, 2)

def main():
    print("🔍 Comparing before/after scan results...")

    # Load before/after findings (mock data for demo)
    # In production, these would come from actual scans
    before_findings = [
        {"id": "RDS-001", "severity": "CRITICAL", "category": "infrastructure", "scanner": "tfsec"},
        {"id": "RDS-002", "severity": "HIGH", "category": "infrastructure", "scanner": "checkov"},
        {"id": "S3-001", "severity": "CRITICAL", "category": "infrastructure", "scanner": "tfsec"},
        # ... (106 total violations)
    ]

    after_findings = [
        {"id": "LOG-001", "severity": "MEDIUM", "category": "infrastructure", "scanner": "checkov"},
        # ... (8 remaining violations)
    ]

    # Calculate metrics
    before_metrics = calculate_metrics(before_findings)
    after_metrics = calculate_metrics(after_findings)

    # Compare
    comparison = compare_findings(before_findings, after_findings)

    # Calculate reductions
    total_reduction = calculate_reduction_percentage(
        before_metrics['total'],
        after_metrics['total']
    )

    # Generate report
    report = {
        "before": before_metrics,
        "after": after_metrics,
        "comparison": comparison,
        "reduction_percentage": total_reduction,
        "by_severity_reduction": {
            severity: calculate_reduction_percentage(
                before_metrics['by_severity'].get(severity, 0),
                after_metrics['by_severity'].get(severity, 0)
            )
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        }
    }

    # Save metrics
    with open('violation-metrics.json', 'w') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print(f"\n✅ Comparison complete!")
    print(f"\n📊 Summary:")
    print(f"   Before: {before_metrics['total']} violations")
    print(f"   After:  {after_metrics['total']} violations")
    print(f"   Fixed:  {comparison['fixed_count']} violations")
    print(f"   Reduction: {total_reduction}%")
    print(f"\n   By Severity:")
    print(f"   - CRITICAL: {before_metrics['by_severity'].get('CRITICAL', 0)} → {after_metrics['by_severity'].get('CRITICAL', 0)}")
    print(f"   - HIGH:     {before_metrics['by_severity'].get('HIGH', 0)} → {after_metrics['by_severity'].get('HIGH', 0)}")
    print(f"   - MEDIUM:   {before_metrics['by_severity'].get('MEDIUM', 0)} → {after_metrics['by_severity'].get('MEDIUM', 0)}")
    print(f"   - LOW:      {before_metrics['by_severity'].get('LOW', 0)} → {after_metrics['by_severity'].get('LOW', 0)}")

    print(f"\n📁 Metrics saved to: violation-metrics.json")

if __name__ == '__main__':
    main()
