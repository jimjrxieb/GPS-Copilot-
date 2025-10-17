#!/usr/bin/env python3
"""
Scan Results Integrator for Jade
Provides real-time access to security scan results for human-like decision making
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

# Add paths for integration
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "GP-Backend" / "james-config"))

from gp_data_config import GPDataConfig

@dataclass
class ScanInsight:
    """Structured scan insight for AI processing"""
    tool: str
    severity: str
    finding_type: str
    count: int
    risk_score: float
    business_impact: str
    remediation_priority: str
    context: Dict[str, Any]

class ScanResultsIntegrator:
    """Integrates scan results from GP-DATA for Jade's decision making"""

    def __init__(self):
        self.config = GPDataConfig()
        self.scan_dir = self.config.get_scan_directory()
        self.fixes_dir = self.config.get_fixes_directory()

        # Tool severity weights for risk calculation
        self.severity_weights = {
            "critical": 10.0,
            "high": 7.5,
            "medium": 5.0,
            "low": 2.5,
            "info": 1.0
        }

        # Business impact multipliers
        self.impact_multipliers = {
            "production": 3.0,
            "staging": 2.0,
            "development": 1.0,
            "test": 0.5
        }

    def get_recent_scans(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get all scan results from the last N hours"""
        recent_scans = []
        cutoff_time = datetime.now() - timedelta(hours=hours)

        for scan_file in self.scan_dir.glob("*.json"):
            try:
                with open(scan_file, 'r') as f:
                    scan_data = json.load(f)

                # Parse timestamp
                if 'timestamp' in scan_data:
                    scan_time = datetime.fromisoformat(scan_data['timestamp'].replace('Z', '+00:00'))
                    if scan_time > cutoff_time:
                        scan_data['file_path'] = str(scan_file)
                        recent_scans.append(scan_data)
            except Exception as e:
                continue

        return sorted(recent_scans, key=lambda x: x.get('timestamp', ''), reverse=True)

    def get_scan_by_tool(self, tool: str) -> Optional[Dict[str, Any]]:
        """Get the latest scan result for a specific tool"""
        pattern = f"{tool}_latest.json"
        latest_file = self.scan_dir / pattern

        if latest_file.exists():
            with open(latest_file, 'r') as f:
                return json.load(f)

        # Fallback to most recent scan file
        tool_scans = list(self.scan_dir.glob(f"{tool}_*.json"))
        if tool_scans:
            latest = max(tool_scans, key=lambda p: p.stat().st_mtime)
            with open(latest, 'r') as f:
                return json.load(f)

        return None

    def aggregate_findings(self, project: Optional[str] = None) -> Dict[str, Any]:
        """Aggregate all findings for intelligent analysis"""
        aggregated = {
            "total_findings": 0,
            "by_severity": {},
            "by_tool": {},
            "risk_score": 0.0,
            "top_risks": [],
            "remediation_stats": {},
            "project": project
        }

        all_scans = self.get_recent_scans(hours=168)  # Last week

        for scan in all_scans:
            if project and scan.get('target') and project not in str(scan.get('target')):
                continue

            tool = scan.get('tool', 'unknown')
            findings = scan.get('findings', [])

            # Initialize tool entry
            if tool not in aggregated['by_tool']:
                aggregated['by_tool'][tool] = {
                    "count": 0,
                    "severities": {}
                }

            # Process findings
            for finding in findings:
                severity = finding.get('severity', 'info').lower()

                # Update counts
                aggregated['total_findings'] += 1
                aggregated['by_tool'][tool]['count'] += 1

                # Update severity breakdown
                if severity not in aggregated['by_severity']:
                    aggregated['by_severity'][severity] = 0
                aggregated['by_severity'][severity] += 1

                if severity not in aggregated['by_tool'][tool]['severities']:
                    aggregated['by_tool'][tool]['severities'][severity] = 0
                aggregated['by_tool'][tool]['severities'][severity] += 1

                # Calculate risk contribution
                risk_contribution = self.severity_weights.get(severity, 1.0)
                aggregated['risk_score'] += risk_contribution

                # Track top risks
                if severity in ['critical', 'high']:
                    aggregated['top_risks'].append({
                        "tool": tool,
                        "severity": severity,
                        "type": finding.get('type', 'Unknown'),
                        "description": finding.get('description', '')[:200]
                    })

        # Limit top risks
        aggregated['top_risks'] = aggregated['top_risks'][:10]

        # Check for fixes
        aggregated['remediation_stats'] = self._get_remediation_stats(project)

        return aggregated

    def _get_remediation_stats(self, project: Optional[str] = None) -> Dict[str, Any]:
        """Get remediation statistics from fixes directory"""
        stats = {
            "total_fixes_available": 0,
            "auto_fixable": 0,
            "manual_required": 0,
            "fixes_by_tool": {}
        }

        for fix_file in self.fixes_dir.glob("*_fixes_*.json"):
            try:
                with open(fix_file, 'r') as f:
                    fixes = json.load(f)

                if project and project not in str(fix_file):
                    continue

                tool = fix_file.stem.split('_')[0]

                if tool not in stats['fixes_by_tool']:
                    stats['fixes_by_tool'][tool] = 0

                if isinstance(fixes, list):
                    stats['total_fixes_available'] += len(fixes)
                    stats['fixes_by_tool'][tool] += len(fixes)

                    for fix in fixes:
                        if fix.get('auto_fixable', False):
                            stats['auto_fixable'] += 1
                        else:
                            stats['manual_required'] += 1
            except:
                continue

        return stats

    def generate_insights(self, project: Optional[str] = None) -> List[ScanInsight]:
        """Generate human-like insights from scan data"""
        insights = []
        aggregated = self.aggregate_findings(project)

        # Critical finding insight
        critical_count = aggregated['by_severity'].get('critical', 0)
        if critical_count > 0:
            insights.append(ScanInsight(
                tool="aggregate",
                severity="critical",
                finding_type="security",
                count=critical_count,
                risk_score=critical_count * 10.0,
                business_impact=f"${critical_count * 50000:,} potential breach cost",
                remediation_priority="IMMEDIATE",
                context={"requires_executive_notification": True}
            ))

        # High-risk pattern detection
        high_count = aggregated['by_severity'].get('high', 0)
        if high_count > 5:
            insights.append(ScanInsight(
                tool="pattern_analysis",
                severity="high",
                finding_type="systemic",
                count=high_count,
                risk_score=high_count * 7.5,
                business_impact="Systemic security weakness detected",
                remediation_priority="24-48 hours",
                context={"pattern": "Multiple high-severity issues indicate architectural concerns"}
            ))

        # Tool-specific insights
        for tool, data in aggregated['by_tool'].items():
            if data['count'] > 10:
                insights.append(ScanInsight(
                    tool=tool,
                    severity="aggregate",
                    finding_type=f"{tool}_findings",
                    count=data['count'],
                    risk_score=sum(
                        self.severity_weights.get(sev, 1) * count
                        for sev, count in data['severities'].items()
                    ),
                    business_impact=f"{tool} indicates significant exposure",
                    remediation_priority="Scheduled remediation",
                    context=data['severities']
                ))

        # Remediation readiness
        rem_stats = aggregated['remediation_stats']
        if rem_stats['auto_fixable'] > 0:
            insights.append(ScanInsight(
                tool="remediation_engine",
                severity="info",
                finding_type="positive",
                count=rem_stats['auto_fixable'],
                risk_score=-rem_stats['auto_fixable'] * 2,  # Negative = risk reduction
                business_impact=f"{rem_stats['auto_fixable']} issues can be auto-fixed",
                remediation_priority="Ready for automation",
                context=rem_stats
            ))

        return sorted(insights, key=lambda x: x.risk_score, reverse=True)

    def get_compliance_gaps(self, framework: str = "CIS") -> Dict[str, Any]:
        """Analyze scan results against compliance frameworks"""
        gaps = {
            "framework": framework,
            "compliant_controls": [],
            "non_compliant_controls": [],
            "gap_percentage": 0.0,
            "remediation_effort": "Unknown"
        }

        # Map findings to compliance controls
        all_findings = self.aggregate_findings()

        # CIS control mapping (simplified)
        if framework == "CIS":
            control_violations = {
                "CIS-1": all_findings['by_severity'].get('critical', 0) > 0,
                "CIS-2": all_findings['by_tool'].get('bandit', {}).get('count', 0) > 10,
                "CIS-3": all_findings['by_tool'].get('trivy', {}).get('count', 0) > 5,
                "CIS-4": all_findings['by_tool'].get('gitleaks', {}).get('count', 0) > 0,
                "CIS-5": all_findings['by_severity'].get('high', 0) > 20
            }

            for control, violated in control_violations.items():
                if violated:
                    gaps['non_compliant_controls'].append(control)
                else:
                    gaps['compliant_controls'].append(control)

            total_controls = len(control_violations)
            compliant = len(gaps['compliant_controls'])
            gaps['gap_percentage'] = ((total_controls - compliant) / total_controls) * 100

            # Estimate effort
            if gaps['gap_percentage'] > 50:
                gaps['remediation_effort'] = "High (2-4 weeks)"
            elif gaps['gap_percentage'] > 25:
                gaps['remediation_effort'] = "Medium (1-2 weeks)"
            else:
                gaps['remediation_effort'] = "Low (< 1 week)"

        return gaps

    def to_rag_context(self) -> List[Dict[str, Any]]:
        """Convert scan results to RAG-compatible context for Jade"""
        contexts = []

        # Add aggregated insights
        insights = self.generate_insights()
        for insight in insights[:5]:  # Top 5 insights
            contexts.append({
                "content": f"Security Insight: {insight.finding_type} - {insight.business_impact}. Priority: {insight.remediation_priority}",
                "metadata": {
                    "source": "scan_analysis",
                    "severity": insight.severity,
                    "risk_score": insight.risk_score
                }
            })

        # Add compliance context
        for framework in ["CIS", "SOC2", "PCI-DSS"]:
            gaps = self.get_compliance_gaps(framework)
            if gaps['gap_percentage'] > 0:
                contexts.append({
                    "content": f"{framework} Compliance: {gaps['gap_percentage']:.1f}% gap. {len(gaps['non_compliant_controls'])} controls need attention. Effort: {gaps['remediation_effort']}",
                    "metadata": {
                        "source": "compliance_analysis",
                        "framework": framework
                    }
                })

        return contexts


# Singleton instance for easy import
scan_integrator = ScanResultsIntegrator()

if __name__ == "__main__":
    # Test the integrator
    integrator = ScanResultsIntegrator()

    print("🔍 Analyzing recent scans...")
    insights = integrator.generate_insights()

    print(f"\n📊 Generated {len(insights)} insights:")
    for insight in insights:
        print(f"  - {insight.severity}: {insight.business_impact} (Risk: {insight.risk_score:.1f})")

    print("\n📋 Compliance Analysis:")
    for framework in ["CIS"]:
        gaps = integrator.get_compliance_gaps(framework)
        print(f"  {framework}: {gaps['gap_percentage']:.1f}% gap, Effort: {gaps['remediation_effort']}")

    print("\n🤖 RAG Context Generated:")
    contexts = integrator.to_rag_context()
    for ctx in contexts[:3]:
        print(f"  - {ctx['content'][:100]}...")