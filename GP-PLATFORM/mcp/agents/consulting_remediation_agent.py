#!/usr/bin/env python3
"""
GuidePoint Consulting Remediation Agent
Domain-specific agent for client-focused security remediation planning
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
from guidance.kubernetes_planner import kubernetes_planner, SecurityLevel, DeploymentEnvironment
from analysis.risk_quantifier import RiskQuantifier

@dataclass
class RemediationPlan:
    """Client-specific remediation plan with business context"""
    plan_id: str
    client_profile_id: str
    vulnerabilities_addressed: List[Dict[str, Any]]
    business_impact_analysis: Dict[str, Any]
    implementation_strategy: str
    estimated_cost: float
    estimated_timeline_weeks: int
    compliance_alignment: List[str]
    risk_reduction_score: float
    executive_summary: str
    technical_steps: List[Dict[str, Any]]
    created_at: str

class ConsultingRemediationAgent:
    """
    Domain-specific agent for GuidePoint consulting remediation
    Focuses on business-aware security remediation planning
    """

    def __init__(self):
        self.logger = logging.getLogger("guidepoint.remediation")
        self.client_manager = ClientProfileManager()
        self.risk_quantifier = RiskQuantifier()

    async def generate_remediation_plan(
        self,
        client_profile_id: str,
        vulnerabilities: List[Dict[str, Any]],
        priority_strategy: str = "risk_balanced"
    ) -> Dict[str, Any]:
        """
        Generate client-specific remediation plan with business impact analysis

        Args:
            client_profile_id: Client profile identifier
            vulnerabilities: List of vulnerability findings
            priority_strategy: business_critical, compliance_driven, or risk_balanced

        Returns:
            Comprehensive remediation plan with business context
        """

        try:
            # Get client profile for business context
            client_profile = self.client_manager.get_profile(client_profile_id)
            if not client_profile:
                raise ValueError(f"Client profile {client_profile_id} not found")

            # Analyze business impact of vulnerabilities
            business_impact = await self._analyze_business_impact(
                client_profile, vulnerabilities
            )

            # Prioritize vulnerabilities based on strategy
            prioritized_vulns = await self._prioritize_vulnerabilities(
                vulnerabilities, business_impact, priority_strategy, client_profile
            )

            # Generate implementation strategy
            implementation_strategy = await self._create_implementation_strategy(
                client_profile, prioritized_vulns, priority_strategy
            )

            # Calculate cost and timeline estimates
            cost_estimate = await self._calculate_remediation_cost(
                client_profile, prioritized_vulns
            )

            timeline_estimate = await self._estimate_timeline(
                prioritized_vulns, client_profile
            )

            # Generate executive summary
            executive_summary = await self._generate_executive_summary(
                client_profile, business_impact, cost_estimate, timeline_estimate
            )

            # Create technical implementation steps
            technical_steps = await self._generate_technical_steps(
                prioritized_vulns, client_profile
            )

            # Calculate risk reduction score
            risk_reduction = await self._calculate_risk_reduction(
                vulnerabilities, client_profile
            )

            plan = RemediationPlan(
                plan_id=f"REM-{client_profile_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                client_profile_id=client_profile_id,
                vulnerabilities_addressed=prioritized_vulns,
                business_impact_analysis=business_impact,
                implementation_strategy=implementation_strategy,
                estimated_cost=cost_estimate,
                estimated_timeline_weeks=timeline_estimate,
                compliance_alignment=self._identify_compliance_alignment(client_profile),
                risk_reduction_score=risk_reduction,
                executive_summary=executive_summary,
                technical_steps=technical_steps,
                created_at=datetime.now().isoformat()
            )

            self.logger.info(f"Generated remediation plan {plan.plan_id} for client {client_profile.company_name}")

            return asdict(plan)

        except Exception as e:
            self.logger.error(f"Failed to generate remediation plan: {str(e)}")
            raise

    async def _analyze_business_impact(
        self,
        client_profile,
        vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze business impact of vulnerabilities for this specific client"""

        revenue_impact_vulns = []
        compliance_impact_vulns = []
        operational_impact_vulns = []

        for vuln in vulnerabilities:
            # Check if vulnerability affects revenue-generating assets
            if self._affects_revenue_assets(vuln, client_profile):
                revenue_impact_vulns.append(vuln)

            # Check compliance framework impact
            if self._affects_compliance(vuln, client_profile):
                compliance_impact_vulns.append(vuln)

            # Check operational impact
            if self._affects_operations(vuln, client_profile):
                operational_impact_vulns.append(vuln)

        # Calculate potential financial impact
        potential_breach_cost = self.client_manager.calculate_breach_cost(client_profile)
        downtime_cost_per_hour = client_profile.annual_revenue / (365 * 24) if client_profile.annual_revenue else 1000

        return {
            "revenue_impact_vulnerabilities": len(revenue_impact_vulns),
            "compliance_impact_vulnerabilities": len(compliance_impact_vulns),
            "operational_impact_vulnerabilities": len(operational_impact_vulns),
            "estimated_breach_cost": potential_breach_cost,
            "downtime_cost_per_hour": downtime_cost_per_hour,
            "critical_business_systems_affected": self._identify_affected_systems(
                vulnerabilities, client_profile
            ),
            "compliance_frameworks_at_risk": [
                framework.value for framework in client_profile.compliance_frameworks
            ]
        }

    async def _prioritize_vulnerabilities(
        self,
        vulnerabilities: List[Dict[str, Any]],
        business_impact: Dict[str, Any],
        strategy: str,
        client_profile
    ) -> List[Dict[str, Any]]:
        """Prioritize vulnerabilities based on business strategy"""

        prioritized = []

        for vuln in vulnerabilities:
            priority_score = 0

            # Base technical severity (0-40 points)
            severity_map = {"critical": 40, "high": 30, "medium": 20, "low": 10}
            priority_score += severity_map.get(vuln.get("severity", "low"), 10)

            # Business impact scoring (0-40 points)
            if self._affects_revenue_assets(vuln, client_profile):
                priority_score += 30
            if self._affects_compliance(vuln, client_profile):
                priority_score += 25
            if self._affects_operations(vuln, client_profile):
                priority_score += 15

            # Strategy-specific adjustments (0-20 points)
            if strategy == "business_critical":
                if self._affects_revenue_assets(vuln, client_profile):
                    priority_score += 20
            elif strategy == "compliance_driven":
                if self._affects_compliance(vuln, client_profile):
                    priority_score += 20
            elif strategy == "risk_balanced":
                # Balanced approach - no additional weighting
                pass

            vuln["priority_score"] = min(priority_score, 100)
            vuln["business_justification"] = self._generate_business_justification(
                vuln, client_profile
            )
            prioritized.append(vuln)

        # Sort by priority score (highest first)
        return sorted(prioritized, key=lambda x: x["priority_score"], reverse=True)

    async def _create_implementation_strategy(
        self,
        client_profile,
        prioritized_vulns: List[Dict[str, Any]],
        strategy: str
    ) -> str:
        """Create implementation strategy narrative"""

        total_vulns = len(prioritized_vulns)
        critical_vulns = len([v for v in prioritized_vulns if v.get("severity") == "critical"])
        high_vulns = len([v for v in prioritized_vulns if v.get("severity") == "high"])

        strategy_text = f"""
Implementation Strategy for {client_profile.company_name}:

PHASE 1 - Critical Risk Mitigation (Week 1-2):
• Address {critical_vulns} critical vulnerabilities affecting revenue systems
• Focus on {client_profile.critical_assets[0].system_name if client_profile.critical_assets else 'core systems'}
• Implement emergency patches and security controls

PHASE 2 - High Impact Remediation (Week 3-6):
• Resolve {high_vulns} high-severity findings
• Strengthen infrastructure security controls
• Implement monitoring and detection capabilities

PHASE 3 - Comprehensive Hardening (Week 7-12):
• Address remaining medium/low priority vulnerabilities
• Implement defense-in-depth security architecture
• Establish ongoing security maintenance procedures

Business Continuity Considerations:
• All changes tested in non-production environments first
• Rollback procedures documented for each change
• Minimal disruption to {', '.join(client_profile.key_revenue_drivers)}
• Compliance with {', '.join([f.value for f in client_profile.compliance_frameworks])} maintained throughout
        """.strip()

        return strategy_text

    async def _calculate_remediation_cost(
        self,
        client_profile,
        vulnerabilities: List[Dict[str, Any]]
    ) -> float:
        """Calculate realistic remediation cost estimate"""

        # Base costs per vulnerability type
        cost_per_vuln = {
            "critical": 5000,  # Typically requires immediate attention, possible downtime
            "high": 2500,      # Significant remediation effort
            "medium": 1000,    # Standard patching and configuration
            "low": 500         # Minor configuration changes
        }

        total_cost = 0

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            base_cost = cost_per_vuln.get(severity, 500)

            # Adjust for business complexity
            if self._affects_revenue_assets(vuln, client_profile):
                base_cost *= 1.5  # Higher cost due to business impact testing

            if self._affects_compliance(vuln, client_profile):
                base_cost *= 1.3  # Additional compliance validation needed

            total_cost += base_cost

        # Add 20% buffer for project management and contingency
        total_cost *= 1.2

        return round(total_cost, 2)

    async def _estimate_timeline(
        self,
        vulnerabilities: List[Dict[str, Any]],
        client_profile
    ) -> int:
        """Estimate remediation timeline in weeks"""

        # Base time per vulnerability (in hours)
        time_per_vuln = {
            "critical": 16,  # 2 days per critical
            "high": 8,       # 1 day per high
            "medium": 4,     # Half day per medium
            "low": 2         # Quarter day per low
        }

        total_hours = 0

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            base_hours = time_per_vuln.get(severity, 2)

            # Adjust for business complexity
            if self._affects_revenue_assets(vuln, client_profile):
                base_hours *= 1.5  # More testing required

            total_hours += base_hours

        # Convert to weeks (assuming 40 hour work weeks)
        estimated_weeks = max(1, round(total_hours / 40))

        # Add buffer for client coordination and testing
        return min(estimated_weeks + 2, 12)  # Cap at 12 weeks maximum

    async def _generate_executive_summary(
        self,
        client_profile,
        business_impact: Dict[str, Any],
        cost: float,
        timeline: int
    ) -> str:
        """Generate executive summary for leadership"""

        summary = f"""
EXECUTIVE SECURITY REMEDIATION SUMMARY
{client_profile.company_name}

BUSINESS IMPACT:
• {business_impact['revenue_impact_vulnerabilities']} vulnerabilities directly affect revenue-generating systems
• Estimated potential breach cost: ${business_impact['estimated_breach_cost']:,.0f}
• {business_impact['compliance_impact_vulnerabilities']} findings impact compliance with {', '.join(business_impact['compliance_frameworks_at_risk'])}

REMEDIATION INVESTMENT:
• Total remediation cost: ${cost:,.0f}
• Implementation timeline: {timeline} weeks
• ROI: Prevents potential ${business_impact['estimated_breach_cost']:,.0f} breach cost

STRATEGIC RECOMMENDATIONS:
• Prioritize revenue system protection to maintain ${client_profile.annual_revenue:,.0f} annual revenue
• Ensure compliance readiness for upcoming audits
• Implement proactive security monitoring to prevent future incidents

NEXT STEPS:
• Approve remediation plan and budget allocation
• Schedule Phase 1 critical vulnerability remediation
• Establish ongoing security maintenance program
        """.strip()

        return summary

    async def _generate_technical_steps(
        self,
        vulnerabilities: List[Dict[str, Any]],
        client_profile
    ) -> List[Dict[str, Any]]:
        """Generate detailed technical implementation steps"""

        steps = []
        step_number = 1

        # Group vulnerabilities by type for efficient remediation
        vulnerability_groups = self._group_vulnerabilities_by_type(vulnerabilities)

        for group_type, group_vulns in vulnerability_groups.items():
            step = {
                "step_number": step_number,
                "title": f"Remediate {group_type} Vulnerabilities",
                "vulnerabilities_addressed": len(group_vulns),
                "estimated_hours": len(group_vulns) * 4,  # 4 hours per vulnerability
                "business_justification": f"Addresses {len(group_vulns)} {group_type} findings affecting {client_profile.company_name} security posture",
                "technical_actions": self._generate_technical_actions(group_type, group_vulns),
                "validation_steps": self._generate_validation_steps(group_type),
                "rollback_procedure": self._generate_rollback_procedure(group_type)
            }
            steps.append(step)
            step_number += 1

        return steps

    def _affects_revenue_assets(self, vuln: Dict[str, Any], client_profile) -> bool:
        """Check if vulnerability affects revenue-generating assets"""
        vuln_path = vuln.get("file_path", "").lower()
        vuln_resource = vuln.get("resource", "").lower()

        # Check against client's critical revenue systems
        for asset in client_profile.critical_assets:
            if asset.revenue_impact and (
                asset.system_name.lower() in vuln_path or
                asset.system_name.lower() in vuln_resource
            ):
                return True

        # Check for common revenue system indicators
        revenue_indicators = ["api", "gateway", "payment", "billing", "customer", "frontend"]
        return any(indicator in vuln_path or indicator in vuln_resource
                  for indicator in revenue_indicators)

    def _affects_compliance(self, vuln: Dict[str, Any], client_profile) -> bool:
        """Check if vulnerability affects compliance requirements"""
        compliance_controls = {
            "SOC2": ["access_control", "encryption", "monitoring", "backup"],
            "GDPR": ["data_protection", "encryption", "access_control", "audit"],
            "HIPAA": ["encryption", "access_control", "audit", "data_protection"]
        }

        vuln_type = vuln.get("check_name", "").lower()

        for framework in client_profile.compliance_frameworks:
            controls = compliance_controls.get(framework.value, [])
            if any(control in vuln_type for control in controls):
                return True

        return False

    def _affects_operations(self, vuln: Dict[str, Any], client_profile) -> bool:
        """Check if vulnerability affects operational systems"""
        operational_indicators = ["database", "storage", "network", "infrastructure", "deployment"]
        vuln_path = vuln.get("file_path", "").lower()
        vuln_resource = vuln.get("resource", "").lower()

        return any(indicator in vuln_path or indicator in vuln_resource
                  for indicator in operational_indicators)

    def _identify_affected_systems(self, vulnerabilities: List[Dict[str, Any]], client_profile) -> List[str]:
        """Identify which business systems are affected by vulnerabilities"""
        affected_systems = set()

        for vuln in vulnerabilities:
            vuln_path = vuln.get("file_path", "").lower()
            vuln_resource = vuln.get("resource", "").lower()

            for asset in client_profile.critical_assets:
                if (asset.system_name.lower() in vuln_path or
                    asset.system_name.lower() in vuln_resource):
                    affected_systems.add(asset.system_name)

        return list(affected_systems)

    def _generate_business_justification(self, vuln: Dict[str, Any], client_profile) -> str:
        """Generate business justification for addressing this vulnerability"""
        justifications = []

        if self._affects_revenue_assets(vuln, client_profile):
            justifications.append(f"Protects revenue-generating systems worth ${client_profile.annual_revenue:,.0f}/year")

        if self._affects_compliance(vuln, client_profile):
            frameworks = [f.value for f in client_profile.compliance_frameworks]
            justifications.append(f"Required for {', '.join(frameworks)} compliance")

        if self._affects_operations(vuln, client_profile):
            justifications.append("Maintains operational stability and availability")

        return "; ".join(justifications) if justifications else "Improves overall security posture"

    def _identify_compliance_alignment(self, client_profile) -> List[str]:
        """Identify which compliance frameworks this remediation supports"""
        return [framework.value for framework in client_profile.compliance_frameworks]

    async def _calculate_risk_reduction(self, vulnerabilities: List[Dict[str, Any]], client_profile) -> float:
        """Calculate risk reduction score from remediation"""
        total_risk_before = 0
        total_risk_after = 0

        for vuln in vulnerabilities:
            # Calculate risk before remediation
            severity_score = {"critical": 10, "high": 7.5, "medium": 5, "low": 2.5}
            base_risk = severity_score.get(vuln.get("severity", "low"), 2.5)

            # Amplify risk for business-critical systems
            if self._affects_revenue_assets(vuln, client_profile):
                base_risk *= 1.5
            if self._affects_compliance(vuln, client_profile):
                base_risk *= 1.3

            total_risk_before += base_risk

            # Risk after remediation (assumed 90% reduction)
            total_risk_after += base_risk * 0.1

        if total_risk_before == 0:
            return 0

        risk_reduction_percent = ((total_risk_before - total_risk_after) / total_risk_before) * 100
        return round(risk_reduction_percent, 1)

    def _group_vulnerabilities_by_type(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group vulnerabilities by type for efficient remediation"""
        groups = {}

        for vuln in vulnerabilities:
            # Extract vulnerability type from check_name or check_id
            check_name = vuln.get("check_name", "")
            if "container" in check_name.lower():
                group_type = "Container Security"
            elif "network" in check_name.lower() or "ingress" in check_name.lower():
                group_type = "Network Security"
            elif "rbac" in check_name.lower() or "permission" in check_name.lower():
                group_type = "Access Control"
            elif "secret" in check_name.lower() or "credential" in check_name.lower():
                group_type = "Secrets Management"
            else:
                group_type = "Configuration Security"

            if group_type not in groups:
                groups[group_type] = []
            groups[group_type].append(vuln)

        return groups

    def _generate_technical_actions(self, group_type: str, vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Generate technical actions for vulnerability group"""
        actions = []

        if group_type == "Container Security":
            actions = [
                "Update container base images to latest secure versions",
                "Implement security contexts with non-root user enforcement",
                "Add resource limits and security policies",
                "Enable container image scanning in CI/CD pipeline"
            ]
        elif group_type == "Network Security":
            actions = [
                "Implement network segmentation policies",
                "Configure ingress controllers with security headers",
                "Enable TLS encryption for all network communications",
                "Implement network policies for pod-to-pod communication"
            ]
        elif group_type == "Access Control":
            actions = [
                "Implement least-privilege RBAC policies",
                "Remove unnecessary service account permissions",
                "Enable pod security standards enforcement",
                "Audit and rotate service account tokens"
            ]
        elif group_type == "Secrets Management":
            actions = [
                "Migrate hardcoded secrets to Kubernetes Secrets or external vault",
                "Implement secret rotation policies",
                "Enable secret encryption at rest",
                "Audit secret access patterns"
            ]
        else:  # Configuration Security
            actions = [
                "Update security configurations to industry standards",
                "Implement configuration validation policies",
                "Enable security monitoring and alerting",
                "Document security configuration requirements"
            ]

        return actions

    def _generate_validation_steps(self, group_type: str) -> List[str]:
        """Generate validation steps for vulnerability group"""
        base_validation = [
            "Verify fixes in development environment",
            "Run security scans to confirm vulnerability resolution",
            "Test application functionality after changes",
            "Document configuration changes"
        ]

        group_specific = {
            "Container Security": ["Test container startup and runtime behavior"],
            "Network Security": ["Verify network connectivity and TLS certificates"],
            "Access Control": ["Test RBAC permissions and service functionality"],
            "Secrets Management": ["Verify secret accessibility and rotation"],
            "Configuration Security": ["Validate configuration compliance"]
        }

        return base_validation + group_specific.get(group_type, [])

    def _generate_rollback_procedure(self, group_type: str) -> List[str]:
        """Generate rollback procedure for vulnerability group"""
        return [
            "Create backup of current configuration",
            "Document rollback commands and procedures",
            "Test rollback in development environment",
            "Monitor system health after rollback",
            "Notify stakeholders of rollback completion"
        ]