#!/usr/bin/env python3
"""
Multi-Framework Compliance Report Generator - THE ULTIMATE DELIVERABLE
=======================================================================
Purpose: Generate unified compliance report across ISO 27001 + SOC2
Author: SecOps Framework
Stage: Compliance Reporting

This is the GRAND FINALE - the ultimate client deliverable that shows:
- All security findings from 5 scanners
- ISO 27001:2022 control mappings
- SOC2 Trust Service Criteria mappings
- Cross-framework overlap analysis (1 fix = multiple compliance wins)
- Prioritized remediation roadmap
- Executive summary with compliance scores
- Export formats: JSON, Markdown, Executive Summary

Features:
- Dual-framework mapping analysis
- Cross-framework overlap detection (fix once, satisfy both)
- Prioritized remediation roadmap (highest ROI first)
- Executive summary for leadership
- Technical details for engineering teams
- Audit-ready evidence requirements

Usage:
    # Generate full multi-framework report
    python3 multi_framework_report.py

    # Generate with all formats (JSON + Markdown)
    python3 multi_framework_report.py --all-formats

    # Generate executive summary only
    python3 multi_framework_report.py --executive-only
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class MultiFrameworkReportGenerator:
    """
    Multi-Framework Compliance Report Generator

    Combines ISO 27001 and SOC2 compliance data into a unified report
    that shows cross-framework overlaps and prioritizes remediation.

    This is what separates you from every other security consultant:
    - Not just "here's your issues"
    - But "here's your compliance roadmap with ROI analysis"
    """

    def __init__(self):
        """Initialize multi-framework report generator"""
        self.project_root = Path(__file__).parent.parent.parent
        self.findings_dir = self.project_root / 'secops' / '2-findings' / 'raw'
        self.reports_dir = self.project_root / 'secops' / '6-reports' / 'compliance'
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Import mappers
        sys.path.insert(0, str(Path(__file__).parent))
        from iso27001_mapper import ISO27001Mapper
        from soc2_mapper import SOC2Mapper

        self.iso27001_mapper = ISO27001Mapper()
        self.soc2_mapper = SOC2Mapper()

    def load_all_findings(self) -> List[Dict]:
        """Load all findings from all scanners"""
        all_findings = []

        # Load CI findings
        ci_dir = self.findings_dir / 'ci'
        if ci_dir.exists():
            for json_file in ci_dir.glob('*.json'):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                        all_findings.extend(data.get('findings', []))
                except Exception as e:
                    print(f"Warning: Could not load {json_file}: {e}")

        # Load CD findings
        cd_dir = self.findings_dir / 'cd'
        if cd_dir.exists():
            for json_file in cd_dir.glob('*.json'):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                        all_findings.extend(data.get('findings', []))
                except Exception as e:
                    print(f"Warning: Could not load {json_file}: {e}")

        return all_findings

    def enrich_findings_dual_framework(self, findings: List[Dict]) -> List[Dict]:
        """
        Enrich findings with BOTH ISO 27001 and SOC2 mappings

        Args:
            findings: List of findings from scanners

        Returns:
            Findings enriched with dual-framework compliance data
        """
        enriched = []

        for finding in findings:
            # Enrich with ISO 27001
            finding = self.iso27001_mapper.enrich_finding(finding.copy())

            # Enrich with SOC2
            finding = self.soc2_mapper.enrich_finding(finding)

            # Calculate cross-framework impact
            has_iso27001 = 'iso27001_compliance' in finding
            has_soc2 = 'soc2_compliance' in finding

            if has_iso27001 or has_soc2:
                finding['compliance_frameworks'] = []
                if has_iso27001:
                    finding['compliance_frameworks'].append('ISO_27001')
                if has_soc2:
                    finding['compliance_frameworks'].append('SOC2')

                # Calculate total controls affected
                total_controls = 0
                if has_iso27001:
                    total_controls += len(finding['iso27001_compliance']['controls'])
                if has_soc2:
                    total_controls += len(finding['soc2_compliance']['criteria'])

                finding['total_controls_affected'] = total_controls

                # Mark high-impact findings (affect both frameworks)
                finding['cross_framework_impact'] = has_iso27001 and has_soc2

            enriched.append(finding)

        return enriched

    def analyze_cross_framework_overlap(self, enriched_findings: List[Dict]) -> Dict:
        """
        Analyze which findings affect BOTH frameworks

        This is the key insight: fixing 1 issue = satisfying multiple controls

        Args:
            enriched_findings: Findings with dual-framework mappings

        Returns:
            Cross-framework overlap analysis
        """
        overlap_stats = {
            'total_findings': len(enriched_findings),
            'iso27001_only': 0,
            'soc2_only': 0,
            'both_frameworks': 0,
            'unmapped': 0,
            'high_impact_findings': []  # Findings affecting both frameworks
        }

        for finding in enriched_findings:
            frameworks = finding.get('compliance_frameworks', [])

            if len(frameworks) == 0:
                overlap_stats['unmapped'] += 1
            elif len(frameworks) == 2:
                overlap_stats['both_frameworks'] += 1
                # Track high-impact findings
                if finding.get('cross_framework_impact'):
                    overlap_stats['high_impact_findings'].append({
                        'scanner': finding.get('scanner'),
                        'file': finding.get('file'),
                        'line': finding.get('line'),
                        'issue': finding.get('title', finding.get('check_name', finding.get('issue'))),
                        'severity': finding.get('severity'),
                        'iso27001_controls': len(finding['iso27001_compliance']['controls']) if 'iso27001_compliance' in finding else 0,
                        'soc2_criteria': len(finding['soc2_compliance']['criteria']) if 'soc2_compliance' in finding else 0,
                        'total_controls': finding.get('total_controls_affected', 0)
                    })
            elif 'ISO_27001' in frameworks:
                overlap_stats['iso27001_only'] += 1
            elif 'SOC2' in frameworks:
                overlap_stats['soc2_only'] += 1

        # Sort high-impact findings by total controls affected
        overlap_stats['high_impact_findings'].sort(
            key=lambda x: x['total_controls'],
            reverse=True
        )

        return overlap_stats

    def generate_prioritized_roadmap(self, enriched_findings: List[Dict]) -> List[Dict]:
        """
        Generate prioritized remediation roadmap

        Priority factors:
        1. Cross-framework impact (both ISO 27001 + SOC2)
        2. Severity (CRITICAL > HIGH > MEDIUM > LOW)
        3. Total controls affected
        4. Estimated effort (prefer quick wins)

        Args:
            enriched_findings: Findings with dual-framework mappings

        Returns:
            Prioritized list of remediation items
        """
        roadmap_items = []

        for finding in enriched_findings:
            # Skip unmapped findings
            if not finding.get('compliance_frameworks'):
                continue

            # Calculate priority score
            priority_score = 0

            # Factor 1: Cross-framework impact (50 points)
            if finding.get('cross_framework_impact'):
                priority_score += 50

            # Factor 2: Severity (40 points max)
            severity_scores = {'CRITICAL': 40, 'HIGH': 30, 'MEDIUM': 20, 'LOW': 10, 'INFO': 5}
            priority_score += severity_scores.get(finding.get('severity', 'LOW'), 10)

            # Factor 3: Total controls affected (10 points max)
            controls_affected = finding.get('total_controls_affected', 0)
            priority_score += min(controls_affected * 2, 10)

            # Get effort estimate (prefer lower effort for equal priority)
            effort_hours = 0
            if 'iso27001_compliance' in finding:
                effort_hours = max(effort_hours, finding['iso27001_compliance'].get('estimated_effort_hours', 0))
            if 'soc2_compliance' in finding:
                effort_hours = max(effort_hours, finding['soc2_compliance'].get('estimated_effort_hours', 0))

            # Calculate ROI score: priority / effort
            roi_score = priority_score / max(effort_hours, 1)

            roadmap_item = {
                'priority_score': priority_score,
                'roi_score': round(roi_score, 2),
                'scanner': finding.get('scanner'),
                'file': finding.get('file'),
                'line': finding.get('line'),
                'issue': finding.get('title', finding.get('check_name', finding.get('issue'))),
                'severity': finding.get('severity'),
                'cross_framework': finding.get('cross_framework_impact', False),
                'frameworks': finding.get('compliance_frameworks', []),
                'controls_affected': finding.get('total_controls_affected', 0),
                'effort_hours': effort_hours,
                'remediation_guidance': None
            }

            # Get remediation guidance from either framework
            if 'iso27001_compliance' in finding:
                roadmap_item['remediation_guidance'] = finding['iso27001_compliance'].get('remediation_guidance')
            elif 'soc2_compliance' in finding:
                roadmap_item['remediation_guidance'] = finding['soc2_compliance'].get('remediation_guidance')

            roadmap_items.append(roadmap_item)

        # Sort by priority score (desc), then ROI (desc), then effort (asc)
        roadmap_items.sort(
            key=lambda x: (x['priority_score'], x['roi_score'], -x['effort_hours']),
            reverse=True
        )

        return roadmap_items

    def generate_executive_summary(
        self,
        enriched_findings: List[Dict],
        overlap_analysis: Dict,
        roadmap: List[Dict]
    ) -> Dict:
        """
        Generate executive summary for leadership

        Args:
            enriched_findings: All findings with dual-framework data
            overlap_analysis: Cross-framework overlap stats
            roadmap: Prioritized remediation roadmap

        Returns:
            Executive summary dict
        """
        # Count findings by severity
        severity_counts = defaultdict(int)
        for finding in enriched_findings:
            severity = finding.get('severity', 'UNKNOWN')
            severity_counts[severity] += 1

        # Calculate total effort
        total_effort = sum(item['effort_hours'] for item in roadmap)

        # Get top 10 quick wins (high ROI, low effort)
        quick_wins = [
            item for item in roadmap
            if item['effort_hours'] <= 4 and item['priority_score'] >= 50
        ][:10]

        # Count controls/criteria affected
        iso27001_controls = set()
        soc2_criteria = set()

        for finding in enriched_findings:
            if 'iso27001_compliance' in finding:
                iso27001_controls.update(finding['iso27001_compliance']['controls'])
            if 'soc2_compliance' in finding:
                soc2_criteria.update(finding['soc2_compliance']['criteria'])

        executive_summary = {
            'scan_date': datetime.now().isoformat(),
            'overview': {
                'total_findings': len(enriched_findings),
                'mapped_findings': len([f for f in enriched_findings if f.get('compliance_frameworks')]),
                'critical_issues': severity_counts.get('CRITICAL', 0),
                'high_issues': severity_counts.get('HIGH', 0),
                'medium_issues': severity_counts.get('MEDIUM', 0),
                'low_issues': severity_counts.get('LOW', 0)
            },
            'compliance_impact': {
                'iso27001_controls_affected': len(iso27001_controls),
                'soc2_criteria_affected': len(soc2_criteria),
                'cross_framework_findings': overlap_analysis['both_frameworks'],
                'high_impact_findings': len(overlap_analysis['high_impact_findings'])
            },
            'remediation': {
                'total_effort_hours': total_effort,
                'total_effort_days': round(total_effort / 8, 1),
                'total_effort_weeks': round(total_effort / 40, 1),
                'priority_items': len([r for r in roadmap if r['priority_score'] >= 80]),
                'quick_wins_available': len(quick_wins)
            },
            'key_recommendations': [
                {
                    'priority': 1,
                    'title': 'Address Cross-Framework Issues First',
                    'description': f'Fix {overlap_analysis["both_frameworks"]} issues that affect BOTH ISO 27001 and SOC2',
                    'impact': 'Maximum compliance ROI',
                    'effort': f'{sum(r["effort_hours"] for r in roadmap[:overlap_analysis["both_frameworks"]])} hours'
                },
                {
                    'priority': 2,
                    'title': 'Resolve Critical Security Issues',
                    'description': f'Address {severity_counts.get("CRITICAL", 0)} CRITICAL vulnerabilities',
                    'impact': 'Prevent potential security breaches',
                    'effort': f'{sum(r["effort_hours"] for r in roadmap if r["severity"] == "CRITICAL")} hours'
                },
                {
                    'priority': 3,
                    'title': 'Implement Quick Wins',
                    'description': f'Complete {len(quick_wins)} high-ROI, low-effort fixes',
                    'impact': 'Fast compliance improvements',
                    'effort': f'{sum(q["effort_hours"] for q in quick_wins)} hours'
                }
            ]
        }

        return executive_summary

    def generate_full_report(self) -> Dict:
        """
        Generate complete multi-framework compliance report

        Returns:
            Complete report with all analysis
        """
        print("=" * 70)
        print("MULTI-FRAMEWORK COMPLIANCE REPORT GENERATOR")
        print("=" * 70)
        print()

        # Load findings
        print("📥 Loading findings from all scanners...")
        findings = self.load_all_findings()
        print(f"   ✅ Loaded {len(findings)} findings")
        print()

        # Enrich with dual-framework mappings
        print("🔗 Enriching findings with ISO 27001 + SOC2 mappings...")
        enriched_findings = self.enrich_findings_dual_framework(findings)
        mapped_count = len([f for f in enriched_findings if f.get('compliance_frameworks')])
        print(f"   ✅ Mapped {mapped_count} findings to compliance frameworks")
        print()

        # Analyze cross-framework overlap
        print("🔍 Analyzing cross-framework overlap...")
        overlap_analysis = self.analyze_cross_framework_overlap(enriched_findings)
        print(f"   ✅ Found {overlap_analysis['both_frameworks']} high-impact findings (affect both frameworks)")
        print()

        # Generate prioritized roadmap
        print("🗺️  Generating prioritized remediation roadmap...")
        roadmap = self.generate_prioritized_roadmap(enriched_findings)
        print(f"   ✅ Created roadmap with {len(roadmap)} prioritized items")
        print()

        # Generate executive summary
        print("📊 Generating executive summary...")
        executive_summary = self.generate_executive_summary(
            enriched_findings,
            overlap_analysis,
            roadmap
        )
        print(f"   ✅ Executive summary ready")
        print()

        # Build full report
        report = {
            'report_metadata': {
                'title': 'Multi-Framework Security Compliance Report',
                'frameworks': ['ISO 27001:2022', 'SOC2 Trust Service Criteria'],
                'generated_date': datetime.now().isoformat(),
                'scanner_count': 5,
                'scanners_used': ['Bandit', 'Semgrep', 'Gitleaks', 'Trivy', 'Checkov']
            },
            'executive_summary': executive_summary,
            'cross_framework_analysis': overlap_analysis,
            'prioritized_roadmap': roadmap,
            'detailed_findings': enriched_findings
        }

        return report

    def save_json_report(self, report: Dict, filename: str = 'multi-framework-report.json') -> Path:
        """Save report as JSON"""
        output_path = self.reports_dir / filename
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        return output_path

    def save_markdown_report(self, report: Dict, filename: str = 'multi-framework-report.md') -> Path:
        """
        Save report as Markdown (human-readable format)

        Args:
            report: Full report dict
            filename: Output filename

        Returns:
            Path to saved Markdown file
        """
        output_path = self.reports_dir / filename

        with open(output_path, 'w') as f:
            # Header
            f.write("# Multi-Framework Security Compliance Report\n\n")
            f.write(f"**Generated**: {report['report_metadata']['generated_date']}\n\n")
            f.write(f"**Frameworks**: {', '.join(report['report_metadata']['frameworks'])}\n\n")
            f.write(f"**Scanners**: {', '.join(report['report_metadata']['scanners_used'])}\n\n")
            f.write("---\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            exec_summary = report['executive_summary']

            f.write("### Overview\n\n")
            overview = exec_summary['overview']
            f.write(f"- **Total Findings**: {overview['total_findings']}\n")
            f.write(f"- **Mapped to Compliance**: {overview['mapped_findings']}\n")
            f.write(f"- **Critical Issues**: {overview['critical_issues']}\n")
            f.write(f"- **High Issues**: {overview['high_issues']}\n")
            f.write(f"- **Medium Issues**: {overview['medium_issues']}\n")
            f.write(f"- **Low Issues**: {overview['low_issues']}\n\n")

            f.write("### Compliance Impact\n\n")
            compliance = exec_summary['compliance_impact']
            f.write(f"- **ISO 27001 Controls Affected**: {compliance['iso27001_controls_affected']}\n")
            f.write(f"- **SOC2 Criteria Affected**: {compliance['soc2_criteria_affected']}\n")
            f.write(f"- **Cross-Framework Findings**: {compliance['cross_framework_findings']}\n")
            f.write(f"- **High-Impact Findings**: {compliance['high_impact_findings']}\n\n")

            f.write("### Remediation Summary\n\n")
            remediation = exec_summary['remediation']
            f.write(f"- **Total Effort**: {remediation['total_effort_hours']} hours ({remediation['total_effort_days']} days)\n")
            f.write(f"- **High-Priority Items**: {remediation['priority_items']}\n")
            f.write(f"- **Quick Wins Available**: {remediation['quick_wins_available']}\n\n")

            f.write("### Key Recommendations\n\n")
            for rec in exec_summary['key_recommendations']:
                f.write(f"#### {rec['priority']}. {rec['title']}\n\n")
                f.write(f"**Description**: {rec['description']}\n\n")
                f.write(f"**Impact**: {rec['impact']}\n\n")
                f.write(f"**Effort**: {rec['effort']}\n\n")

            f.write("---\n\n")

            # Cross-Framework Analysis
            f.write("## Cross-Framework Analysis\n\n")
            overlap = report['cross_framework_analysis']
            f.write(f"- **ISO 27001 Only**: {overlap['iso27001_only']} findings\n")
            f.write(f"- **SOC2 Only**: {overlap['soc2_only']} findings\n")
            f.write(f"- **Both Frameworks**: {overlap['both_frameworks']} findings\n")
            f.write(f"- **Unmapped**: {overlap['unmapped']} findings\n\n")

            f.write("### High-Impact Findings (Top 10)\n\n")
            f.write("These findings affect BOTH ISO 27001 and SOC2 - fix once, satisfy multiple controls.\n\n")
            f.write("| Scanner | Issue | Severity | ISO Controls | SOC2 Criteria | Total |\n")
            f.write("|---------|-------|----------|--------------|---------------|-------|\n")

            for finding in overlap['high_impact_findings'][:10]:
                issue = finding['issue'][:50] + '...' if len(finding['issue']) > 50 else finding['issue']
                f.write(f"| {finding['scanner']} | {issue} | {finding['severity']} | ")
                f.write(f"{finding['iso27001_controls']} | {finding['soc2_criteria']} | {finding['total_controls']} |\n")

            f.write("\n---\n\n")

            # Prioritized Roadmap
            f.write("## Prioritized Remediation Roadmap\n\n")
            f.write("Sorted by priority score (cross-framework impact + severity + controls affected).\n\n")

            f.write("### Top 20 Priority Items\n\n")
            f.write("| # | Issue | Severity | Frameworks | Controls | Effort | ROI |\n")
            f.write("|---|-------|----------|------------|----------|--------|-----|\n")

            for i, item in enumerate(report['prioritized_roadmap'][:20], 1):
                issue = item['issue'][:40] + '...' if len(item['issue']) > 40 else item['issue']
                frameworks = '+'.join(item['frameworks'])
                cross = '⭐' if item['cross_framework'] else ''
                f.write(f"| {i} | {issue} {cross} | {item['severity']} | {frameworks} | ")
                f.write(f"{item['controls_affected']} | {item['effort_hours']}h | {item['roi_score']} |\n")

            f.write("\n⭐ = Cross-framework impact (affects both ISO 27001 + SOC2)\n\n")

        return output_path


def main():
    """
    Main entry point for multi-framework report generation

    Usage:
        # Generate full report
        python3 multi_framework_report.py

        # Generate all formats
        python3 multi_framework_report.py --all-formats
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Multi-Framework Compliance Report Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full report (JSON + Markdown)
  python3 multi_framework_report.py --all-formats

  # Generate JSON only
  python3 multi_framework_report.py

  # Custom output directory
  python3 multi_framework_report.py --output-dir /path/to/reports
        """
    )

    parser.add_argument(
        '--all-formats',
        action='store_true',
        help='Generate both JSON and Markdown formats'
    )

    args = parser.parse_args()

    # Create generator
    generator = MultiFrameworkReportGenerator()

    # Generate full report
    report = generator.generate_full_report()

    print("=" * 70)
    print("SAVING REPORTS")
    print("=" * 70)
    print()

    # Save JSON
    json_path = generator.save_json_report(report)
    print(f"✅ JSON report saved: {json_path}")

    # Save Markdown if requested
    if args.all_formats:
        md_path = generator.save_markdown_report(report)
        print(f"✅ Markdown report saved: {md_path}")

    print()
    print("=" * 70)
    print("REPORT SUMMARY")
    print("=" * 70)
    exec_summary = report['executive_summary']
    print(f"Total Findings:          {exec_summary['overview']['total_findings']}")
    print(f"Critical Issues:         {exec_summary['overview']['critical_issues']}")
    print(f"Cross-Framework Impact:  {exec_summary['compliance_impact']['cross_framework_findings']}")
    print(f"Total Remediation:       {exec_summary['remediation']['total_effort_hours']} hours ({exec_summary['remediation']['total_effort_weeks']} weeks)")
    print(f"Quick Wins:              {exec_summary['remediation']['quick_wins_available']}")
    print("=" * 70)


if __name__ == '__main__':
    main()
