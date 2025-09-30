#!/usr/bin/env python3
"""
Jade Enhanced - AI Security Consultant with Full Data Access
Integrates embedded knowledge, scan results, and human-like decision making
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add necessary paths
sys.path.append(str(Path(__file__).parent.parent))

# Import all integration components
from GP_AI.engines import AISecurityEngine, RAGEngine, SecurityReasoningEngine
from GP_AI.integrations.scan_results_integrator import ScanResultsIntegrator
from GP_AI.models import model_manager, gpu_config
from GP_AI.knowledge.comprehensive_jade_prompts import (
    get_comprehensive_security_prompt,
    get_focused_scanner_prompt,
    ANALYSIS_PROFILES
)

class JadeEnhanced:
    """Enhanced Jade with full data access and human-like reasoning"""

    def __init__(self):
        print("🤖 Initializing Enhanced Jade Security Consultant...")

        # Core components
        self.ai_engine = AISecurityEngine()
        self.rag_engine = RAGEngine()
        self.reasoning_engine = SecurityReasoningEngine()
        self.scan_integrator = ScanResultsIntegrator()

        # Knowledge domains
        self.expertise = {
            "security_analysis": "Expert-level vulnerability assessment and risk quantification",
            "compliance": "SOC2, HIPAA, PCI-DSS, CIS framework expertise",
            "kubernetes": "CKS-level Kubernetes security and OPA policy management",
            "cloud": "Multi-cloud security (AWS, Azure, GCP)",
            "devsecops": "CI/CD security integration and automation",
            "incident_response": "Threat detection and incident management"
        }

        print("✅ Enhanced Jade initialized with full data access")

    def analyze_with_context(self, query: str, project: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform human-like analysis with full context awareness
        Integrates: RAG knowledge + Scan Results + Business Context
        """
        print(f"🧠 Analyzing: {query}")

        # 1. Get scan result insights
        scan_insights = self.scan_integrator.generate_insights(project)
        scan_context = self.scan_integrator.to_rag_context()

        # 2. Query RAG knowledge base
        rag_results = self.rag_engine.query_knowledge(query, n_results=5)

        # 3. Get compliance context
        compliance_gaps = {}
        for framework in ["CIS", "SOC2", "HIPAA"]:
            compliance_gaps[framework] = self.scan_integrator.get_compliance_gaps(framework)

        # 4. Aggregate findings data
        aggregated_findings = self.scan_integrator.aggregate_findings(project)

        # 5. Build comprehensive context
        context = {
            "query": query,
            "project": project,
            "timestamp": datetime.now().isoformat(),
            "scan_insights": [
                {
                    "severity": insight.severity,
                    "impact": insight.business_impact,
                    "priority": insight.remediation_priority,
                    "risk_score": insight.risk_score
                }
                for insight in scan_insights[:5]
            ],
            "rag_knowledge": rag_results,
            "compliance_status": compliance_gaps,
            "risk_metrics": {
                "total_findings": aggregated_findings['total_findings'],
                "critical_count": aggregated_findings['by_severity'].get('critical', 0),
                "high_count": aggregated_findings['by_severity'].get('high', 0),
                "risk_score": aggregated_findings['risk_score'],
                "top_risks": aggregated_findings['top_risks'][:3]
            },
            "remediation_available": aggregated_findings['remediation_stats']
        }

        # 6. Generate human-like response
        response = self._generate_intelligent_response(query, context)

        return {
            "response": response,
            "context": context,
            "confidence": self._calculate_confidence(context),
            "recommendations": self._generate_recommendations(context),
            "next_steps": self._suggest_next_steps(context)
        }

    def _generate_intelligent_response(self, query: str, context: Dict[str, Any]) -> str:
        """Generate human-like response based on full context"""

        # Build prompt with all context
        prompt = f"""
As Jade, a senior security consultant with access to real-time scan results and
comprehensive knowledge, provide expert analysis for: {query}

CURRENT SECURITY POSTURE:
- Total Findings: {context['risk_metrics']['total_findings']}
- Critical Issues: {context['risk_metrics']['critical_count']}
- High Issues: {context['risk_metrics']['high_count']}
- Risk Score: {context['risk_metrics']['risk_score']:.1f}

TOP RISKS IDENTIFIED:
{json.dumps(context['risk_metrics']['top_risks'], indent=2)}

COMPLIANCE STATUS:
{json.dumps({k: f"{v['gap_percentage']:.1f}% gap" for k, v in context['compliance_status'].items()}, indent=2)}

AVAILABLE REMEDIATIONS:
- Auto-fixable: {context['remediation_available']['auto_fixable']}
- Manual Required: {context['remediation_available']['manual_required']}

Provide a comprehensive, actionable response that:
1. Directly addresses the query
2. Incorporates the scan findings
3. Considers compliance implications
4. Suggests practical next steps
5. Quantifies business impact where relevant
"""

        # Use model if available, otherwise use pattern-based response
        if model_manager and model_manager.model:
            try:
                response = model_manager.query_security_knowledge(prompt)
                return response
            except Exception as e:
                print(f"⚠️ Model inference failed: {e}")

        # Fallback to intelligent pattern-based response
        return self._pattern_based_response(query, context)

    def _pattern_based_response(self, query: str, context: Dict[str, Any]) -> str:
        """Generate pattern-based response when model unavailable"""

        query_lower = query.lower()
        risk_metrics = context['risk_metrics']

        # Determine query type and generate appropriate response
        if "risk" in query_lower or "security" in query_lower:
            return f"""Based on real-time analysis of your security posture:

**Current Risk Assessment:**
- Risk Score: {risk_metrics['risk_score']:.1f} ({"Critical" if risk_metrics['risk_score'] > 100 else "High" if risk_metrics['risk_score'] > 50 else "Medium"})
- Total Security Findings: {risk_metrics['total_findings']}
- Critical Issues: {risk_metrics['critical_count']} requiring immediate attention
- High Priority Issues: {risk_metrics['high_count']} for scheduled remediation

**Top Security Concerns:**
{self._format_top_risks(risk_metrics['top_risks'])}

**Business Impact:**
- Potential breach cost: ${risk_metrics['critical_count'] * 50000 + risk_metrics['high_count'] * 10000:,}
- Compliance risk multiplier: {max(v['gap_percentage'] for v in context['compliance_status'].values()):.1f}%
- Remediation effort: {context['remediation_available']['auto_fixable']} issues auto-fixable

**Recommendations:**
1. Address {risk_metrics['critical_count']} critical findings within 24 hours
2. Implement automated fixes for {context['remediation_available']['auto_fixable']} issues
3. Schedule remediation for remaining {context['remediation_available']['manual_required']} manual fixes
4. Focus on closing {self._identify_priority_framework(context['compliance_status'])} compliance gaps

This assessment is based on aggregated scan results from multiple security tools and
compliance framework mappings."""

        elif "compliance" in query_lower:
            return self._generate_compliance_response(context)

        elif "remediat" in query_lower or "fix" in query_lower:
            return self._generate_remediation_response(context)

        else:
            # Generic intelligent response
            return self._generate_generic_response(query, context)

    def _format_top_risks(self, risks: List[Dict]) -> str:
        """Format top risks for display"""
        if not risks:
            return "No critical risks identified"

        formatted = []
        for i, risk in enumerate(risks[:3], 1):
            formatted.append(
                f"{i}. [{risk['severity'].upper()}] {risk['type']} - {risk.get('description', 'Security vulnerability detected')[:100]}"
            )
        return "\n".join(formatted)

    def _identify_priority_framework(self, compliance_status: Dict) -> str:
        """Identify which compliance framework needs most attention"""
        max_gap = 0
        priority = "General"

        for framework, status in compliance_status.items():
            if status['gap_percentage'] > max_gap:
                max_gap = status['gap_percentage']
                priority = framework

        return priority

    def _generate_compliance_response(self, context: Dict[str, Any]) -> str:
        """Generate compliance-focused response"""
        compliance = context['compliance_status']

        response = "**Compliance Assessment Summary:**\n\n"
        for framework, status in compliance.items():
            response += f"**{framework} Compliance:**\n"
            response += f"- Gap: {status['gap_percentage']:.1f}%\n"
            response += f"- Non-compliant controls: {len(status['non_compliant_controls'])}\n"
            response += f"- Remediation effort: {status['remediation_effort']}\n\n"

        response += f"""
**Priority Actions:**
1. Address {len(compliance['CIS']['non_compliant_controls'])} CIS control violations
2. Implement {context['remediation_available']['auto_fixable']} automated fixes
3. Document compliance evidence for audit preparation
4. Schedule manual remediation for {context['remediation_available']['manual_required']} findings

**Business Impact:**
- Audit readiness: {"Low" if max(s['gap_percentage'] for s in compliance.values()) > 30 else "High"}
- Compliance risk: ${int(max(s['gap_percentage'] for s in compliance.values()) * 5000)}
- Time to compliance: {compliance['CIS']['remediation_effort']}
"""
        return response

    def _generate_remediation_response(self, context: Dict[str, Any]) -> str:
        """Generate remediation-focused response"""
        rem = context['remediation_available']

        return f"""**Remediation Plan:**

**Immediate Actions Available:**
- {rem['auto_fixable']} issues can be fixed automatically
- {rem['manual_required']} issues require manual intervention
- Total fixes ready: {rem['total_fixes_available']}

**Remediation by Tool:**
{json.dumps(rem['fixes_by_tool'], indent=2)}

**Execution Strategy:**
1. **Phase 1 (Immediate):** Deploy {rem['auto_fixable']} automated fixes
2. **Phase 2 (24-48h):** Address {context['risk_metrics']['critical_count']} critical findings
3. **Phase 3 (Week 1):** Resolve {context['risk_metrics']['high_count']} high-priority issues
4. **Phase 4 (Ongoing):** Implement preventive controls and monitoring

**Expected Risk Reduction:**
- Current risk score: {context['risk_metrics']['risk_score']:.1f}
- Post-remediation estimate: {context['risk_metrics']['risk_score'] * 0.3:.1f}
- Risk reduction: {(1 - 0.3) * 100:.0f}%

This plan prioritizes business-critical issues while maintaining operational stability."""

    def _generate_generic_response(self, query: str, context: Dict[str, Any]) -> str:
        """Generate generic but intelligent response"""
        return f"""Based on comprehensive security analysis:

**Query:** {query}

**Current Security Context:**
- Active findings: {context['risk_metrics']['total_findings']}
- Risk level: {"Critical" if context['risk_metrics']['risk_score'] > 100 else "High" if context['risk_metrics']['risk_score'] > 50 else "Medium"}
- Compliance gaps exist in {len([k for k, v in context['compliance_status'].items() if v['gap_percentage'] > 0])} frameworks
- Remediation options: {context['remediation_available']['total_fixes_available']} fixes available

**Analysis:**
Your environment shows signs of {self._characterize_environment(context)}.
The primary concerns are concentrated in {self._identify_problem_areas(context)}.

**Recommendations:**
1. Focus on {context['risk_metrics']['critical_count'] + context['risk_metrics']['high_count']} high-severity findings
2. Leverage {context['remediation_available']['auto_fixable']} automated fixes
3. Address compliance gaps systematically
4. Implement continuous monitoring

This assessment integrates real-time scan data with security best practices and
compliance requirements."""

    def _characterize_environment(self, context: Dict) -> str:
        """Characterize the security environment"""
        risk_score = context['risk_metrics']['risk_score']

        if risk_score > 100:
            return "significant security exposure requiring immediate attention"
        elif risk_score > 50:
            return "moderate security concerns with systematic weaknesses"
        else:
            return "generally good security posture with minor improvements needed"

    def _identify_problem_areas(self, context: Dict) -> str:
        """Identify main problem areas"""
        problems = []

        if context['risk_metrics']['critical_count'] > 0:
            problems.append("critical vulnerabilities")

        compliance_gaps = [k for k, v in context['compliance_status'].items() if v['gap_percentage'] > 25]
        if compliance_gaps:
            problems.append(f"{', '.join(compliance_gaps)} compliance")

        if context['remediation_available']['manual_required'] > 20:
            problems.append("technical debt")

        return " and ".join(problems) if problems else "configuration hardening"

    def _calculate_confidence(self, context: Dict) -> float:
        """Calculate confidence score based on available data"""
        confidence = 0.5  # Base confidence

        # Increase confidence based on data availability
        if context['risk_metrics']['total_findings'] > 0:
            confidence += 0.2

        if context['rag_knowledge']:
            confidence += 0.15

        if context['scan_insights']:
            confidence += 0.15

        return min(confidence, 1.0)

    def _generate_recommendations(self, context: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Critical findings recommendation
        if context['risk_metrics']['critical_count'] > 0:
            recommendations.append(
                f"IMMEDIATE: Address {context['risk_metrics']['critical_count']} critical findings within 24 hours"
            )

        # Automated fixes
        if context['remediation_available']['auto_fixable'] > 0:
            recommendations.append(
                f"Deploy {context['remediation_available']['auto_fixable']} automated fixes to reduce risk quickly"
            )

        # Compliance gaps
        priority_framework = self._identify_priority_framework(context['compliance_status'])
        if priority_framework != "General":
            recommendations.append(
                f"Close {priority_framework} compliance gaps ({context['compliance_status'][priority_framework]['gap_percentage']:.1f}%)"
            )

        # Risk score based
        if context['risk_metrics']['risk_score'] > 100:
            recommendations.append("Implement emergency response protocol for critical exposure")
        elif context['risk_metrics']['risk_score'] > 50:
            recommendations.append("Schedule security review within 1 week")

        return recommendations

    def _suggest_next_steps(self, context: Dict) -> List[str]:
        """Suggest concrete next steps"""
        steps = []

        # Based on findings
        if context['remediation_available']['auto_fixable'] > 0:
            steps.append("Run: python GP-CONSULTING-AGENTS/auto_remediate.py --apply")

        if context['risk_metrics']['critical_count'] > 0:
            steps.append("Review: GP-DATA/active/scans/*_latest.json for critical findings")

        # Compliance related
        gaps = [k for k, v in context['compliance_status'].items() if v['gap_percentage'] > 30]
        if gaps:
            steps.append(f"Generate compliance report: ./gp-security report --framework={gaps[0]}")

        # General maintenance
        steps.append("Schedule weekly security scan: crontab -e # Add scan automation")

        return steps


def main():
    """Test enhanced Jade"""
    jade = JadeEnhanced()

    # Test queries
    test_queries = [
        "What is our current security risk?",
        "Show compliance gaps for HIPAA",
        "What can be fixed automatically?",
        "Analyze Portfolio project security"
    ]

    for query in test_queries:
        print(f"\n{'=' * 80}")
        print(f"📝 Query: {query}")
        print(f"{'=' * 80}")

        result = jade.analyze_with_context(query, project="Portfolio")

        print(f"\n🤖 Jade's Response:")
        print(result['response'])

        print(f"\n📊 Confidence: {result['confidence']:.1%}")
        print(f"💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"  - {rec}")

        print(f"\n🎯 Next Steps:")
        for step in result['next_steps']:
            print(f"  - {step}")


if __name__ == "__main__":
    main()