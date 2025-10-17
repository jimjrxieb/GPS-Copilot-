#!/usr/bin/env python3
"""
GuidePoint Client Intelligence Agent
Domain-specific agent for client meeting analysis and business intelligence
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# Import GuidePoint automation components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'automation_engine'))

from clients.client_profiler import ClientProfileManager
from intelligence.meeting_processor import meeting_processor, MeetingType
from intelligence.knowledge_integrator import knowledge_integrator
from analysis.risk_quantifier import RiskQuantifier

@dataclass
class SecurityPostureAnalysis:
    """Client security posture analysis result"""
    analysis_id: str
    client_profile_id: str
    overall_risk_score: float
    business_impact_assessment: Dict[str, Any]
    compliance_status: Dict[str, Any]
    technology_stack_risks: List[Dict[str, Any]]
    revenue_protection_recommendations: List[str]
    executive_insights: List[str]
    priority_actions: List[Dict[str, Any]]
    created_at: str

@dataclass
class ExecutiveReport:
    """Executive report for C-suite consumption"""
    report_id: str
    client_profile_id: str
    report_type: str
    executive_summary: str
    key_findings: List[str]
    business_impact: Dict[str, Any]
    investment_recommendations: List[Dict[str, Any]]
    risk_mitigation_roadmap: List[Dict[str, Any]]
    compliance_readiness: Dict[str, Any]
    next_steps: List[str]
    appendix_technical_details: Dict[str, Any]
    created_at: str

class ClientIntelligenceAgent:
    """
    Domain-specific agent for GuidePoint client intelligence
    Focuses on business context analysis and executive communication
    """

    def __init__(self):
        self.logger = logging.getLogger("guidepoint.intelligence")
        self.client_manager = ClientProfileManager()
        self.risk_quantifier = RiskQuantifier()

    async def analyze_security_posture(
        self,
        client_profile_id: str,
        scan_results: Dict[str, Any],
        business_priorities: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze client security posture with business context

        Args:
            client_profile_id: Client profile identifier
            scan_results: Security scan results from tools
            business_priorities: Current business priorities to consider

        Returns:
            Comprehensive security posture analysis
        """

        try:
            # Get client profile for business context
            client_profile = self.client_manager.get_profile(client_profile_id)
            if not client_profile:
                raise ValueError(f"Client profile {client_profile_id} not found")

            # Extract vulnerabilities from scan results
            vulnerabilities = self._extract_vulnerabilities(scan_results)

            # Calculate overall risk score
            risk_score = await self._calculate_overall_risk_score(
                vulnerabilities, client_profile
            )

            # Analyze business impact
            business_impact = await self._analyze_business_impact(
                vulnerabilities, client_profile, business_priorities or []
            )

            # Assess compliance status
            compliance_status = await self._assess_compliance_status(
                vulnerabilities, client_profile
            )

            # Analyze technology stack risks
            tech_risks = await self._analyze_technology_risks(
                vulnerabilities, client_profile
            )

            # Generate revenue protection recommendations
            revenue_recommendations = await self._generate_revenue_protection_recommendations(
                vulnerabilities, client_profile
            )

            # Generate executive insights
            executive_insights = await self._generate_executive_insights(
                risk_score, business_impact, client_profile
            )

            # Determine priority actions
            priority_actions = await self._determine_priority_actions(
                vulnerabilities, business_impact, client_profile
            )

            analysis = SecurityPostureAnalysis(
                analysis_id=f"SPA-{client_profile_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                client_profile_id=client_profile_id,
                overall_risk_score=risk_score,
                business_impact_assessment=business_impact,
                compliance_status=compliance_status,
                technology_stack_risks=tech_risks,
                revenue_protection_recommendations=revenue_recommendations,
                executive_insights=executive_insights,
                priority_actions=priority_actions,
                created_at=datetime.now().isoformat()
            )

            self.logger.info(f"Completed security posture analysis {analysis.analysis_id} for {client_profile.company_name}")

            return asdict(analysis)

        except Exception as e:
            self.logger.error(f"Failed to analyze security posture: {str(e)}")
            raise

    async def process_meeting_intelligence(
        self,
        client_name: str,
        meeting_notes: str,
        meeting_type: str,
        participants: List[str] = None
    ) -> Dict[str, Any]:
        """
        Process meeting notes and extract actionable consulting insights

        Args:
            client_name: Name of client company
            meeting_notes: Raw meeting notes text
            meeting_type: Type of meeting (security_assessment, follow_up, etc.)
            participants: List of meeting participants

        Returns:
            Processed meeting intelligence with actionable insights
        """

        try:
            # Create meeting metadata
            meeting_metadata = {
                "client_name": client_name,
                "type": meeting_type,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "participants": participants or [],
                "duration_minutes": 60  # Default estimate
            }

            # Process meeting notes through intelligence engine
            meeting_analysis = meeting_processor.process_meeting_notes(
                meeting_notes, meeting_metadata
            )

            # Integrate insights into knowledge base
            integration_results = knowledge_integrator.integrate_meeting_analysis(
                meeting_analysis
            )

            # Extract business intelligence
            business_intelligence = await self._extract_business_intelligence(
                meeting_analysis, client_name
            )

            # Generate follow-up recommendations
            follow_up_recommendations = await self._generate_follow_up_recommendations(
                meeting_analysis, business_intelligence
            )

            # Create action items for James
            james_action_items = await self._create_james_action_items(
                meeting_analysis, business_intelligence
            )

            result = {
                "meeting_id": meeting_analysis.meeting_id,
                "processing_summary": {
                    "key_topics_extracted": len(meeting_analysis.key_topics),
                    "action_items_identified": len(meeting_analysis.action_items),
                    "security_concerns_found": len(meeting_analysis.security_concerns),
                    "insights_generated": len(meeting_analysis.extracted_insights)
                },
                "business_intelligence": business_intelligence,
                "follow_up_recommendations": follow_up_recommendations,
                "james_action_items": james_action_items,
                "knowledge_integration": {
                    "entries_added": integration_results["knowledge_entries_added"],
                    "patterns_identified": integration_results["patterns_identified"],
                    "learning_opportunities": integration_results["learning_opportunities"]
                },
                "client_insights": await self._generate_client_insights(meeting_analysis, client_name)
            }

            self.logger.info(f"Processed meeting intelligence for {client_name}: {meeting_analysis.meeting_id}")

            return result

        except Exception as e:
            self.logger.error(f"Failed to process meeting intelligence: {str(e)}")
            raise

    async def generate_executive_report(
        self,
        client_profile_id: str,
        scan_session_id: str,
        report_type: str
    ) -> Dict[str, Any]:
        """
        Generate executive-ready security report with business intelligence

        Args:
            client_profile_id: Client profile identifier
            scan_session_id: Security scan session to report on
            report_type: Type of report (ciso_brief, board_summary, compliance_audit, business_case)

        Returns:
            Executive report tailored for leadership consumption
        """

        try:
            # Get client profile and scan results
            client_profile = self.client_manager.get_profile(client_profile_id)
            if not client_profile:
                raise ValueError(f"Client profile {client_profile_id} not found")

            # TODO: Retrieve scan results from database using scan_session_id
            # For now, simulate with empty results
            scan_results = {}
            vulnerabilities = []

            # Generate report content based on type
            if report_type == "ciso_brief":
                report_content = await self._generate_ciso_brief(
                    client_profile, vulnerabilities, scan_session_id
                )
            elif report_type == "board_summary":
                report_content = await self._generate_board_summary(
                    client_profile, vulnerabilities, scan_session_id
                )
            elif report_type == "compliance_audit":
                report_content = await self._generate_compliance_audit(
                    client_profile, vulnerabilities, scan_session_id
                )
            elif report_type == "business_case":
                report_content = await self._generate_business_case(
                    client_profile, vulnerabilities, scan_session_id
                )
            else:
                raise ValueError(f"Unknown report type: {report_type}")

            report = ExecutiveReport(
                report_id=f"RPT-{report_type.upper()}-{client_profile_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                client_profile_id=client_profile_id,
                report_type=report_type,
                **report_content,
                created_at=datetime.now().isoformat()
            )

            self.logger.info(f"Generated {report_type} report {report.report_id} for {client_profile.company_name}")

            return asdict(report)

        except Exception as e:
            self.logger.error(f"Failed to generate executive report: {str(e)}")
            raise

    async def _calculate_overall_risk_score(
        self,
        vulnerabilities: List[Dict[str, Any]],
        client_profile
    ) -> float:
        """Calculate overall risk score considering business context"""

        if not vulnerabilities:
            return 0.0

        # Base technical risk calculation
        severity_weights = {"critical": 10, "high": 7, "medium": 4, "low": 1}
        total_technical_risk = sum(
            severity_weights.get(vuln.get("severity", "low"), 1)
            for vuln in vulnerabilities
        )

        # Business impact multipliers
        business_multiplier = 1.0

        # Increase risk for revenue-impacting vulnerabilities
        revenue_vulns = [v for v in vulnerabilities if self._affects_revenue_systems(v, client_profile)]
        if revenue_vulns:
            business_multiplier += 0.3

        # Increase risk for compliance-impacting vulnerabilities
        compliance_vulns = [v for v in vulnerabilities if self._affects_compliance_systems(v, client_profile)]
        if compliance_vulns:
            business_multiplier += 0.2

        # Risk tolerance adjustment
        if hasattr(client_profile, 'risk_tolerance'):
            if client_profile.risk_tolerance.value == "LOW":
                business_multiplier += 0.2
            elif client_profile.risk_tolerance.value == "HIGH":
                business_multiplier -= 0.1

        # Calculate final score (0-100 scale)
        if len(vulnerabilities) > 0:
            risk_score = min((total_technical_risk * business_multiplier) / len(vulnerabilities) * 10, 100)
        else:
            risk_score = 0.0

        return round(risk_score, 1)

    async def _analyze_business_impact(
        self,
        vulnerabilities: List[Dict[str, Any]],
        client_profile,
        business_priorities: List[str]
    ) -> Dict[str, Any]:
        """Analyze business impact of security findings"""

        # Calculate potential financial impact
        potential_breach_cost = self.client_manager.calculate_breach_cost(client_profile)
        downtime_cost_per_hour = client_profile.annual_revenue / (365 * 24) if client_profile.annual_revenue and client_profile.annual_revenue > 0 else 1000

        # Identify business-critical vulnerabilities
        revenue_critical_vulns = [v for v in vulnerabilities if self._affects_revenue_systems(v, client_profile)]
        compliance_critical_vulns = [v for v in vulnerabilities if self._affects_compliance_systems(v, client_profile)]

        # Assess impact on business priorities
        priority_impact = {}
        for priority in business_priorities:
            priority_impact[priority] = self._assess_priority_impact(priority, vulnerabilities, client_profile)

        return {
            "potential_breach_cost": potential_breach_cost,
            "downtime_cost_per_hour": downtime_cost_per_hour,
            "revenue_critical_vulnerabilities": len(revenue_critical_vulns),
            "compliance_critical_vulnerabilities": len(compliance_critical_vulns),
            "business_priority_impact": priority_impact,
            "affected_revenue_streams": self._identify_affected_revenue_streams(vulnerabilities, client_profile),
            "customer_impact_risk": self._assess_customer_impact_risk(vulnerabilities, client_profile),
            "competitive_disadvantage_risk": self._assess_competitive_risk(vulnerabilities, client_profile)
        }

    async def _assess_compliance_status(
        self,
        vulnerabilities: List[Dict[str, Any]],
        client_profile
    ) -> Dict[str, Any]:
        """Assess compliance status across required frameworks"""

        compliance_status = {}

        for framework in client_profile.compliance_frameworks:
            framework_vulns = [v for v in vulnerabilities if self._affects_compliance_framework(v, framework)]

            # Calculate compliance score (0-100)
            if framework_vulns:
                critical_findings = len([v for v in framework_vulns if v.get("severity") == "critical"])
                high_findings = len([v for v in framework_vulns if v.get("severity") == "high"])

                # Scoring: 100 - (critical*20 + high*10)
                score = max(0, 100 - (critical_findings * 20 + high_findings * 10))
            else:
                score = 100

            compliance_status[framework.value] = {
                "compliance_score": score,
                "findings_count": len(framework_vulns),
                "critical_gaps": critical_findings if framework_vulns else 0,
                "remediation_priority": "HIGH" if score < 70 else "MEDIUM" if score < 90 else "LOW",
                "estimated_audit_readiness_weeks": self._estimate_audit_readiness(score)
            }

        return compliance_status

    async def _analyze_technology_risks(
        self,
        vulnerabilities: List[Dict[str, Any]],
        client_profile
    ) -> List[Dict[str, Any]]:
        """Analyze risks specific to client's technology stack"""

        tech_risks = []

        for tech in client_profile.technology_stack:
            tech_vulns = [v for v in vulnerabilities if tech.lower() in str(v).lower()]

            if tech_vulns:
                risk_level = self._calculate_tech_risk_level(tech_vulns)
                business_impact = self._assess_tech_business_impact(tech, client_profile)

                tech_risks.append({
                    "technology": tech,
                    "vulnerabilities_found": len(tech_vulns),
                    "risk_level": risk_level,
                    "business_impact": business_impact,
                    "immediate_actions_required": len([v for v in tech_vulns if v.get("severity") in ["critical", "high"]]),
                    "recommendations": self._generate_tech_recommendations(tech, tech_vulns)
                })

        return sorted(tech_risks, key=lambda x: x["vulnerabilities_found"], reverse=True)

    async def _generate_revenue_protection_recommendations(
        self,
        vulnerabilities: List[Dict[str, Any]],
        client_profile
    ) -> List[str]:
        """Generate recommendations focused on protecting revenue streams"""

        recommendations = []

        # Identify revenue-critical vulnerabilities
        revenue_vulns = [v for v in vulnerabilities if self._affects_revenue_systems(v, client_profile)]

        if revenue_vulns:
            critical_revenue_vulns = [v for v in revenue_vulns if v.get("severity") == "critical"]

            if critical_revenue_vulns:
                recommendations.append(
                    f"IMMEDIATE: Address {len(critical_revenue_vulns)} critical vulnerabilities affecting "
                    f"revenue systems to protect ${client_profile.annual_revenue:,.0f} annual revenue"
                )

            # API security recommendations
            api_vulns = [v for v in revenue_vulns if "api" in str(v).lower()]
            if api_vulns:
                recommendations.append(
                    f"Strengthen API security controls - {len(api_vulns)} vulnerabilities found in "
                    f"revenue-generating API infrastructure"
                )

            # Customer-facing system recommendations
            customer_vulns = [v for v in revenue_vulns if self._is_customer_facing(v, client_profile)]
            if customer_vulns:
                recommendations.append(
                    f"Secure customer-facing systems - {len(customer_vulns)} vulnerabilities could "
                    f"impact {client_profile.customer_base_size:,} customers"
                )

        # Revenue diversification security
        for revenue_driver in client_profile.key_revenue_drivers:
            driver_vulns = [v for v in vulnerabilities if revenue_driver.lower() in str(v).lower()]
            if driver_vulns:
                recommendations.append(
                    f"Protect {revenue_driver} revenue stream - {len(driver_vulns)} security gaps identified"
                )

        return recommendations[:5]  # Top 5 recommendations

    async def _generate_executive_insights(
        self,
        risk_score: float,
        business_impact: Dict[str, Any],
        client_profile
    ) -> List[str]:
        """Generate executive-level insights about security posture"""

        insights = []

        # Risk level insight
        if risk_score >= 70:
            insights.append(
                f"Security risk level is HIGH ({risk_score}/100) - immediate executive attention required"
            )
        elif risk_score >= 40:
            insights.append(
                f"Security risk level is MEDIUM ({risk_score}/100) - planned remediation recommended"
            )
        else:
            insights.append(
                f"Security risk level is LOW ({risk_score}/100) - maintain current security posture"
            )

        # Financial impact insight
        breach_cost = business_impact.get("potential_breach_cost", 0)
        if client_profile.annual_revenue and client_profile.annual_revenue > 0 and breach_cost > client_profile.annual_revenue * 0.1:  # More than 10% of annual revenue
            insights.append(
                f"Potential breach cost (${breach_cost:,.0f}) represents significant financial risk - "
                f"{breach_cost/client_profile.annual_revenue*100:.1f}% of annual revenue" if client_profile.annual_revenue and client_profile.annual_revenue > 0 else f"${breach_cost:,.0f} potential breach cost"
            )

        # Revenue protection insight
        revenue_vulns = business_impact.get("revenue_critical_vulnerabilities", 0)
        if revenue_vulns > 0:
            insights.append(
                f"{revenue_vulns} vulnerabilities directly threaten revenue-generating systems - "
                f"prioritize remediation to maintain business continuity"
            )

        # Compliance insight
        compliance_gaps = sum(1 for framework in client_profile.compliance_frameworks
                            if business_impact.get("compliance_critical_vulnerabilities", 0) > 0)
        if compliance_gaps > 0:
            insights.append(
                f"Compliance gaps identified affecting {compliance_gaps} required frameworks - "
                f"audit readiness may be compromised"
            )

        # Competitive advantage insight
        competitive_risk = business_impact.get("competitive_disadvantage_risk", "LOW")
        if competitive_risk in ["HIGH", "CRITICAL"]:
            insights.append(
                f"Security vulnerabilities may impact competitive position - "
                f"customer trust and market differentiation at risk"
            )

        return insights

    async def _determine_priority_actions(
        self,
        vulnerabilities: List[Dict[str, Any]],
        business_impact: Dict[str, Any],
        client_profile
    ) -> List[Dict[str, Any]]:
        """Determine priority actions based on business impact"""

        actions = []

        # Critical vulnerability action
        critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
        if critical_vulns:
            actions.append({
                "priority": 1,
                "action": f"Address {len(critical_vulns)} critical vulnerabilities",
                "timeline": "24-48 hours",
                "business_justification": "Prevents potential security incidents affecting business operations",
                "estimated_effort": "High",
                "risk_if_delayed": "Critical systems compromise, potential downtime"
            })

        # Revenue system protection action
        revenue_vulns = business_impact.get("revenue_critical_vulnerabilities", 0)
        if revenue_vulns > 0:
            actions.append({
                "priority": 2,
                "action": f"Secure revenue-generating systems",
                "timeline": "1 week",
                "business_justification": f"Protects ${client_profile.annual_revenue:,.0f} annual revenue",
                "estimated_effort": "Medium",
                "risk_if_delayed": "Revenue loss, customer impact"
            })

        # Compliance readiness action
        compliance_vulns = business_impact.get("compliance_critical_vulnerabilities", 0)
        if compliance_vulns > 0:
            frameworks = [f.value for f in client_profile.compliance_frameworks]
            actions.append({
                "priority": 3,
                "action": "Ensure compliance readiness",
                "timeline": "2-4 weeks",
                "business_justification": f"Maintains {', '.join(frameworks)} compliance status",
                "estimated_effort": "Medium",
                "risk_if_delayed": "Audit findings, regulatory penalties"
            })

        return sorted(actions, key=lambda x: x["priority"])

    # Helper methods for business context analysis

    def _extract_vulnerabilities(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract vulnerabilities from scan results"""
        vulnerabilities = []

        # Extract from different tool results
        if "trivy_results" in scan_results:
            vulnerabilities.extend(scan_results["trivy_results"].get("vulnerabilities", []))

        if "checkov_results" in scan_results:
            vulnerabilities.extend(scan_results["checkov_results"].get("failed_checks", []))

        if "kubescape_results" in scan_results:
            vulnerabilities.extend(scan_results["kubescape_results"].get("results", []))

        return vulnerabilities

    def _affects_revenue_systems(self, vuln: Dict[str, Any], client_profile) -> bool:
        """Check if vulnerability affects revenue-generating systems"""
        vuln_text = str(vuln).lower()

        # Check against client's critical revenue assets
        for asset in client_profile.critical_assets:
            if asset.revenue_impact and asset.system_name.lower() in vuln_text:
                return True

        # Check against revenue drivers
        for driver in client_profile.key_revenue_drivers:
            if driver.lower() in vuln_text:
                return True

        # Common revenue system indicators
        revenue_indicators = ["api", "gateway", "payment", "billing", "customer", "frontend", "web"]
        return any(indicator in vuln_text for indicator in revenue_indicators)

    def _affects_compliance_systems(self, vuln: Dict[str, Any], client_profile) -> bool:
        """Check if vulnerability affects compliance-required systems"""
        vuln_text = str(vuln).lower()

        compliance_indicators = [
            "encryption", "access_control", "audit", "logging", "monitoring",
            "backup", "data_protection", "authentication", "authorization"
        ]

        return any(indicator in vuln_text for indicator in compliance_indicators)

    def _affects_compliance_framework(self, vuln: Dict[str, Any], framework) -> bool:
        """Check if vulnerability affects specific compliance framework"""
        framework_controls = {
            "SOC2": ["access_control", "encryption", "monitoring", "backup", "logging"],
            "GDPR": ["data_protection", "encryption", "access_control", "audit", "consent"],
            "HIPAA": ["encryption", "access_control", "audit", "data_protection", "authentication"],
            "PCI_DSS": ["encryption", "access_control", "monitoring", "network_security", "authentication"]
        }

        controls = framework_controls.get(framework.value, [])
        vuln_text = str(vuln).lower()

        return any(control in vuln_text for control in controls)

    def _is_customer_facing(self, vuln: Dict[str, Any], client_profile) -> bool:
        """Check if vulnerability affects customer-facing systems"""
        vuln_text = str(vuln).lower()

        # Check against client's customer-facing assets
        for asset in client_profile.critical_assets:
            if asset.customer_facing and asset.system_name.lower() in vuln_text:
                return True

        customer_indicators = ["frontend", "web", "ui", "portal", "dashboard", "api", "gateway"]
        return any(indicator in vuln_text for indicator in customer_indicators)

    def _assess_priority_impact(self, priority: str, vulnerabilities: List[Dict[str, Any]], client_profile) -> str:
        """Assess impact on specific business priority"""
        priority_vulns = [v for v in vulnerabilities if priority.lower() in str(v).lower()]

        if not priority_vulns:
            return "No direct impact identified"

        critical_count = len([v for v in priority_vulns if v.get("severity") == "critical"])

        if critical_count > 0:
            return f"HIGH - {critical_count} critical vulnerabilities may impact {priority}"
        elif len(priority_vulns) > 5:
            return f"MEDIUM - {len(priority_vulns)} vulnerabilities may affect {priority}"
        else:
            return f"LOW - {len(priority_vulns)} minor vulnerabilities related to {priority}"

    def _identify_affected_revenue_streams(self, vulnerabilities: List[Dict[str, Any]], client_profile) -> List[str]:
        """Identify which revenue streams are affected by vulnerabilities"""
        affected_streams = []

        for driver in client_profile.key_revenue_drivers:
            driver_vulns = [v for v in vulnerabilities if driver.lower() in str(v).lower()]
            if driver_vulns:
                affected_streams.append(f"{driver} ({len(driver_vulns)} vulnerabilities)")

        return affected_streams

    def _assess_customer_impact_risk(self, vulnerabilities: List[Dict[str, Any]], client_profile) -> str:
        """Assess risk of customer impact from vulnerabilities"""
        customer_vulns = [v for v in vulnerabilities if self._is_customer_facing(v, client_profile)]

        if not customer_vulns:
            return "LOW"

        critical_customer_vulns = [v for v in customer_vulns if v.get("severity") == "critical"]

        if critical_customer_vulns:
            return "CRITICAL"
        elif len(customer_vulns) > 5:
            return "HIGH"
        else:
            return "MEDIUM"

    def _assess_competitive_risk(self, vulnerabilities: List[Dict[str, Any]], client_profile) -> str:
        """Assess competitive disadvantage risk from security vulnerabilities"""
        # High-impact vulnerabilities that could affect competitive position
        competitive_vulns = [v for v in vulnerabilities
                           if v.get("severity") in ["critical", "high"] and
                           (self._affects_revenue_systems(v, client_profile) or
                            self._is_customer_facing(v, client_profile))]

        if len(competitive_vulns) >= 5:
            return "CRITICAL"
        elif len(competitive_vulns) >= 2:
            return "HIGH"
        elif len(competitive_vulns) >= 1:
            return "MEDIUM"
        else:
            return "LOW"

    def _calculate_tech_risk_level(self, tech_vulns: List[Dict[str, Any]]) -> str:
        """Calculate risk level for specific technology"""
        critical_count = len([v for v in tech_vulns if v.get("severity") == "critical"])
        high_count = len([v for v in tech_vulns if v.get("severity") == "high"])

        if critical_count > 0:
            return "CRITICAL"
        elif high_count > 2:
            return "HIGH"
        elif len(tech_vulns) > 5:
            return "MEDIUM"
        else:
            return "LOW"

    def _assess_tech_business_impact(self, tech: str, client_profile) -> str:
        """Assess business impact of technology-specific vulnerabilities"""
        # Check if technology is critical to revenue streams
        for driver in client_profile.key_revenue_drivers:
            if tech.lower() in driver.lower():
                return "Revenue Critical"

        # Check if technology handles critical assets
        for asset in client_profile.critical_assets:
            if tech.lower() in asset.business_function.lower():
                return "Business Critical"

        return "Operational Impact"

    def _generate_tech_recommendations(self, tech: str, tech_vulns: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for technology-specific vulnerabilities"""
        recommendations = []

        if tech.lower() == "kubernetes":
            recommendations.extend([
                "Implement Pod Security Standards",
                "Enable network policies",
                "Update to latest stable version",
                "Implement RBAC best practices"
            ])
        elif tech.lower() == "postgresql":
            recommendations.extend([
                "Enable encryption at rest",
                "Implement connection security",
                "Update to latest security patch",
                "Configure audit logging"
            ])
        elif tech.lower() == "redis":
            recommendations.extend([
                "Enable authentication",
                "Configure TLS encryption",
                "Implement access controls",
                "Update to latest version"
            ])
        else:
            recommendations.extend([
                f"Update {tech} to latest secure version",
                f"Review {tech} security configuration",
                f"Implement {tech} monitoring and alerting"
            ])

        return recommendations[:3]  # Top 3 recommendations

    def _estimate_audit_readiness(self, compliance_score: float) -> int:
        """Estimate weeks needed to achieve audit readiness"""
        if compliance_score >= 90:
            return 2
        elif compliance_score >= 70:
            return 6
        elif compliance_score >= 50:
            return 12
        else:
            return 20

    # Meeting intelligence processing methods

    async def _extract_business_intelligence(self, meeting_analysis, client_name: str) -> Dict[str, Any]:
        """Extract business intelligence from meeting analysis"""

        business_topics = [topic for topic in meeting_analysis.key_topics
                         if any(keyword in topic.lower()
                               for keyword in ["revenue", "business", "customer", "compliance", "budget"])]

        technical_requirements = [topic for topic in meeting_analysis.key_topics
                                if any(keyword in topic.lower()
                                      for keyword in ["kubernetes", "security", "infrastructure", "compliance"])]

        decision_points = [action for action in meeting_analysis.action_items
                         if any(keyword in action.get("description", "").lower()
                               for keyword in ["approve", "budget", "decide", "authorize"])]

        return {
            "business_context_topics": business_topics,
            "technical_requirements": technical_requirements,
            "key_decision_points": decision_points,
            "budget_discussions": self._extract_budget_info(meeting_analysis),
            "timeline_commitments": self._extract_timeline_info(meeting_analysis),
            "stakeholder_concerns": self._extract_stakeholder_concerns(meeting_analysis),
            "competitive_factors": self._extract_competitive_factors(meeting_analysis)
        }

    async def _generate_follow_up_recommendations(self, meeting_analysis, business_intelligence: Dict[str, Any]) -> List[str]:
        """Generate follow-up recommendations based on meeting analysis"""

        recommendations = []

        # Technical follow-ups
        if business_intelligence["technical_requirements"]:
            recommendations.append(
                f"Schedule technical deep-dive to address {len(business_intelligence['technical_requirements'])} "
                f"identified technical requirements"
            )

        # Decision follow-ups
        if business_intelligence["key_decision_points"]:
            recommendations.append(
                f"Prepare decision support materials for {len(business_intelligence['key_decision_points'])} "
                f"pending decisions"
            )

        # Security assessment follow-up
        security_concerns = len(meeting_analysis.security_concerns)
        if security_concerns > 0:
            recommendations.append(
                f"Conduct comprehensive security assessment to address {security_concerns} identified concerns"
            )

        return recommendations

    async def _create_james_action_items(self, meeting_analysis, business_intelligence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create specific action items for James AI"""

        james_actions = []

        # Security scan action
        if meeting_analysis.security_concerns:
            james_actions.append({
                "action": "Execute comprehensive security scan",
                "priority": "High",
                "timeline": "24 hours",
                "deliverable": "Security assessment report with business impact analysis"
            })

        # Compliance analysis action
        compliance_keywords = ["soc2", "gdpr", "hipaa", "compliance", "audit"]
        if any(keyword in " ".join(meeting_analysis.key_topics).lower() for keyword in compliance_keywords):
            james_actions.append({
                "action": "Generate compliance readiness analysis",
                "priority": "Medium",
                "timeline": "48 hours",
                "deliverable": "Compliance gap analysis and remediation plan"
            })

        # Cost analysis action
        if business_intelligence["budget_discussions"]:
            james_actions.append({
                "action": "Prepare cost-benefit analysis",
                "priority": "Medium",
                "timeline": "1 week",
                "deliverable": "Investment analysis with ROI projections"
            })

        return james_actions

    async def _generate_client_insights(self, meeting_analysis, client_name: str) -> List[str]:
        """Generate insights about the client based on meeting analysis"""

        insights = []

        # Technical maturity insight
        tech_keywords = ["kubernetes", "ci/cd", "automation", "devops"]
        tech_mentions = sum(1 for topic in meeting_analysis.key_topics
                          if any(keyword in topic.lower() for keyword in tech_keywords))

        if tech_mentions >= 3:
            insights.append(f"{client_name} demonstrates high technical maturity with advanced infrastructure")
        elif tech_mentions >= 1:
            insights.append(f"{client_name} shows moderate technical sophistication")
        else:
            insights.append(f"{client_name} may benefit from technical guidance and education")

        # Security awareness insight
        security_mentions = len(meeting_analysis.security_concerns)
        if security_mentions >= 5:
            insights.append(f"{client_name} has strong security awareness with detailed concern identification")
        elif security_mentions >= 2:
            insights.append(f"{client_name} demonstrates basic security awareness")
        else:
            insights.append(f"{client_name} may need security education and awareness building")

        return insights

    def _extract_budget_info(self, meeting_analysis) -> List[str]:
        """Extract budget-related information from meeting"""
        budget_info = []

        for topic in meeting_analysis.key_topics:
            if any(keyword in topic.lower() for keyword in ["budget", "cost", "investment", "$", "price"]):
                budget_info.append(topic)

        return budget_info

    def _extract_timeline_info(self, meeting_analysis) -> List[str]:
        """Extract timeline-related information from meeting"""
        timeline_info = []

        for topic in meeting_analysis.key_topics:
            if any(keyword in topic.lower() for keyword in ["timeline", "deadline", "week", "month", "quarter"]):
                timeline_info.append(topic)

        return timeline_info

    def _extract_stakeholder_concerns(self, meeting_analysis) -> List[str]:
        """Extract stakeholder concerns from meeting"""
        concerns = meeting_analysis.security_concerns.copy()

        # Add other concerns from key topics
        concern_keywords = ["concern", "worry", "issue", "problem", "challenge"]
        for topic in meeting_analysis.key_topics:
            if any(keyword in topic.lower() for keyword in concern_keywords):
                concerns.append(topic)

        return concerns

    def _extract_competitive_factors(self, meeting_analysis) -> List[str]:
        """Extract competitive factors mentioned in meeting"""
        competitive_factors = []

        competitive_keywords = ["competitor", "market", "advantage", "differentiation", "customer retention"]
        for topic in meeting_analysis.key_topics:
            if any(keyword in topic.lower() for keyword in competitive_keywords):
                competitive_factors.append(topic)

        return competitive_factors

    # Executive report generation methods

    async def _generate_ciso_brief(self, client_profile, vulnerabilities: List[Dict[str, Any]], scan_session_id: str) -> Dict[str, Any]:
        """Generate CISO-focused security brief"""

        critical_vulns = len([v for v in vulnerabilities if v.get("severity") == "critical"])
        high_vulns = len([v for v in vulnerabilities if v.get("severity") == "high"])

        return {
            "executive_summary": f"""
CISO Security Brief - {client_profile.company_name}

IMMEDIATE ATTENTION REQUIRED:
• {critical_vulns} critical vulnerabilities requiring immediate remediation
• {high_vulns} high-severity findings impacting security posture
• Risk to {', '.join([f.value for f in client_profile.compliance_frameworks])} compliance status

BUSINESS IMPACT:
• Potential exposure of {client_profile.customer_base_size:,} customer records
• Risk to ${client_profile.annual_revenue:,.0f} annual revenue
• Compliance audit readiness compromised

RECOMMENDED ACTIONS:
• Immediate patching of critical vulnerabilities (24-48 hours)
• Enhanced monitoring for affected systems
• Compliance gap remediation planning
            """.strip(),

            "key_findings": [
                f"{critical_vulns} critical security vulnerabilities identified",
                f"Revenue-generating systems affected by security gaps",
                f"Compliance frameworks at risk: {', '.join([f.value for f in client_profile.compliance_frameworks])}",
                f"Customer data exposure risk identified"
            ],

            "business_impact": {
                "revenue_at_risk": client_profile.annual_revenue * 0.15,  # 15% revenue impact estimate
                "customers_affected": client_profile.customer_base_size,
                "compliance_status": "At Risk",
                "reputation_impact": "High"
            },

            "investment_recommendations": [
                {
                    "recommendation": "Emergency security remediation",
                    "investment": 50000,
                    "timeline": "1 month",
                    "roi": "Prevents potential $2M+ breach cost"
                }
            ],

            "risk_mitigation_roadmap": [
                {
                    "phase": "Immediate (Week 1)",
                    "actions": ["Critical vulnerability patching", "Enhanced monitoring"],
                    "investment": "$25,000"
                },
                {
                    "phase": "Short-term (Month 1)",
                    "actions": ["Compliance gap remediation", "Security process improvements"],
                    "investment": "$25,000"
                }
            ],

            "compliance_readiness": {
                "overall_status": "Needs Improvement",
                "frameworks_at_risk": len(client_profile.compliance_frameworks),
                "estimated_readiness_timeline": "8 weeks"
            },

            "next_steps": [
                "Approve emergency remediation budget",
                "Schedule weekly security review meetings",
                "Implement continuous security monitoring"
            ],

            "appendix_technical_details": {
                "scan_session_id": scan_session_id,
                "total_vulnerabilities": len(vulnerabilities),
                "severity_breakdown": {
                    "critical": critical_vulns,
                    "high": high_vulns,
                    "medium": len([v for v in vulnerabilities if v.get("severity") == "medium"]),
                    "low": len([v for v in vulnerabilities if v.get("severity") == "low"])
                }
            }
        }

    async def _generate_board_summary(self, client_profile, vulnerabilities: List[Dict[str, Any]], scan_session_id: str) -> Dict[str, Any]:
        """Generate board-level executive summary"""

        potential_breach_cost = self.client_manager.calculate_breach_cost(client_profile)

        return {
            "executive_summary": f"""
BOARD SECURITY SUMMARY - {client_profile.company_name}

STRATEGIC RISK OVERVIEW:
Current security posture presents material risk to business operations and shareholder value.

KEY BUSINESS IMPACTS:
• Potential breach cost: ${potential_breach_cost:,.0f} (15-20% of annual revenue)
• Customer trust and competitive position at risk
• Regulatory compliance gaps identified
• Operational continuity threatened

INVESTMENT RECOMMENDATION:
Immediate security investment of $100,000 to protect $25M+ in enterprise value.

BOARD DECISION REQUIRED:
Authorize comprehensive security remediation program within 30 days.
            """.strip(),

            "key_findings": [
                "Material cybersecurity risk to enterprise value identified",
                "Immediate action required to protect customer trust",
                "Compliance gaps threaten regulatory standing",
                "Competitive disadvantage from security vulnerabilities"
            ],

            "business_impact": {
                "enterprise_value_at_risk": potential_breach_cost,
                "customer_retention_risk": "High",
                "market_position_impact": "Negative",
                "regulatory_risk": "Significant"
            },

            "investment_recommendations": [
                {
                    "recommendation": "Comprehensive security program",
                    "investment": 100000,
                    "timeline": "6 months",
                    "roi": f"Protects ${potential_breach_cost:,.0f} in potential losses"
                }
            ],

            "risk_mitigation_roadmap": [
                {
                    "phase": "Crisis Prevention (Month 1)",
                    "actions": ["Emergency vulnerability remediation"],
                    "investment": "$50,000"
                },
                {
                    "phase": "Strategic Enhancement (Months 2-6)",
                    "actions": ["Security architecture upgrade", "Compliance program"],
                    "investment": "$50,000"
                }
            ],

            "compliance_readiness": {
                "regulatory_risk": "High",
                "audit_readiness": "Not Ready",
                "remediation_timeline": "3-6 months"
            },

            "next_steps": [
                "Board approval for security investment",
                "Executive sponsor assignment",
                "Quarterly security review establishment"
            ],

            "appendix_technical_details": {
                "executive_risk_score": 75,
                "business_continuity_impact": "High",
                "customer_impact_potential": "Significant"
            }
        }

    async def _generate_compliance_audit(self, client_profile, vulnerabilities: List[Dict[str, Any]], scan_session_id: str) -> Dict[str, Any]:
        """Generate compliance audit report"""

        compliance_gaps = len([v for v in vulnerabilities if self._affects_compliance_systems(v, client_profile)])

        return {
            "executive_summary": f"""
COMPLIANCE AUDIT SUMMARY - {client_profile.company_name}

COMPLIANCE STATUS:
{len(client_profile.compliance_frameworks)} frameworks assessed with {compliance_gaps} gaps identified.

AUDIT READINESS:
Current state requires 6-12 weeks remediation before audit-ready status.

REGULATORY RISK:
Moderate to high risk of audit findings without immediate remediation.

REMEDIATION INVESTMENT:
$75,000 recommended investment to achieve full compliance readiness.
            """.strip(),

            "key_findings": [
                f"{compliance_gaps} compliance gaps identified across frameworks",
                "Audit readiness timeline extended due to security findings",
                "Documentation gaps in security controls implementation",
                "Process improvements required for compliance maintenance"
            ],

            "business_impact": {
                "audit_risk": "High",
                "regulatory_penalty_risk": "$50,000 - $500,000",
                "certification_timeline_delay": "3-6 months",
                "customer_contract_impact": "Potential delays"
            },

            "investment_recommendations": [
                {
                    "recommendation": "Compliance remediation program",
                    "investment": 75000,
                    "timeline": "3 months",
                    "roi": "Avoids audit findings and regulatory penalties"
                }
            ],

            "risk_mitigation_roadmap": [
                {
                    "phase": "Gap Remediation (Month 1)",
                    "actions": ["Critical control implementation"],
                    "investment": "$35,000"
                },
                {
                    "phase": "Process Enhancement (Months 2-3)",
                    "actions": ["Documentation completion", "Process automation"],
                    "investment": "$40,000"
                }
            ],

            "compliance_readiness": {
                "soc2_readiness": "60% - Needs improvement",
                "gdpr_readiness": "70% - Nearly compliant",
                "overall_timeline": "12 weeks to audit-ready"
            },

            "next_steps": [
                "Engage compliance consultant",
                "Implement gap remediation plan",
                "Schedule pre-audit assessment"
            ],

            "appendix_technical_details": {
                "frameworks_assessed": [f.value for f in client_profile.compliance_frameworks],
                "controls_tested": compliance_gaps + 50,  # Estimate total controls
                "gaps_identified": compliance_gaps
            }
        }

    async def _generate_business_case(self, client_profile, vulnerabilities: List[Dict[str, Any]], scan_session_id: str) -> Dict[str, Any]:
        """Generate business case for security investment"""

        investment_amount = 150000
        potential_savings = self.client_manager.calculate_breach_cost(client_profile)
        roi_percentage = ((potential_savings - investment_amount) / investment_amount) * 100 if investment_amount > 0 else 0

        return {
            "executive_summary": f"""
SECURITY INVESTMENT BUSINESS CASE - {client_profile.company_name}

INVESTMENT PROPOSAL:
$150,000 comprehensive security enhancement program

BUSINESS VALUE:
• Protects ${potential_savings:,.0f} in potential breach costs
• ROI: {roi_percentage:.0f}% return on investment
• Competitive advantage through security leadership
• Customer trust and retention protection

PAYBACK PERIOD:
Investment pays for itself within 6 months through risk reduction.

RECOMMENDATION:
Approve full security enhancement program for maximum business protection.
            """.strip(),

            "key_findings": [
                f"Security investment ROI of {roi_percentage:.0f}% identified",
                "Competitive advantage opportunity through security leadership",
                "Customer trust enhancement through security improvements",
                "Operational efficiency gains from security automation"
            ],

            "business_impact": {
                "revenue_protection": client_profile.annual_revenue,
                "customer_retention_value": client_profile.customer_base_size * 10000,  # $10K per customer
                "competitive_advantage": "Significant",
                "operational_efficiency": "20% improvement"
            },

            "investment_recommendations": [
                {
                    "recommendation": "Comprehensive security platform",
                    "investment": investment_amount,
                    "timeline": "6 months",
                    "roi": f"{roi_percentage:.0f}% ROI within 12 months"
                }
            ],

            "risk_mitigation_roadmap": [
                {
                    "phase": "Foundation (Months 1-2)",
                    "actions": ["Core security infrastructure"],
                    "investment": "$75,000"
                },
                {
                    "phase": "Enhancement (Months 3-6)",
                    "actions": ["Advanced security capabilities"],
                    "investment": "$75,000"
                }
            ],

            "compliance_readiness": {
                "certification_value": "$500,000 annual contract value",
                "market_differentiation": "Top 10% security posture",
                "customer_acquisition": "15% increase projected"
            },

            "next_steps": [
                "Approve investment budget",
                "Select implementation partner",
                "Define success metrics and timeline"
            ],

            "appendix_technical_details": {
                "cost_benefit_analysis": {
                    "investment": investment_amount,
                    "potential_savings": potential_savings,
                    "net_benefit": potential_savings - investment_amount,
                    "payback_months": 6
                }
            }
        }