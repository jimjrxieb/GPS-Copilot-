#!/usr/bin/env python3
"""
CrewAI Orchestrator - Multi-Agent Security Coordination
======================================================

CrewAI-based coordination layer for GuidePoint specialized security agents.
Orchestrates complex security workflows across multiple domains using CrewAI's
agent coordination and task management capabilities.

Agents Coordinated:
- Scanner Agent: Vulnerability detection & remediation
- Kubernetes Agent: CKA/CKS level cluster security
- IaC/Policy Agent: Infrastructure & Policy as Code
- DevSecOps Agent: CI/CD security automation
- Consulting Agent: Client engagement & reporting
"""

import os
import sys
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Set OpenAI API key for CrewAI
if not os.getenv('OPENAI_API_KEY'):
    # Try to load from James-OS .env file
    env_file = '/home/jimmie/linkops-industries/James-OS/.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    os.environ['OPENAI_API_KEY'] = api_key
                    break

# Add GP-copilot agents to path
GP_COPILOT_BASE = '/home/jimmie/linkops-industries/GP-copilot'
sys.path.insert(0, f'{GP_COPILOT_BASE}/GP-CONSULTING-AGENTS/agents')
sys.path.insert(0, GP_COPILOT_BASE)

# Import specialized agents (commented out - need to verify agent structure)
# from scanner_agent import ScannerAgent
# from kubernetes_agent import KubernetesAgent
# from iac_agent import IaCAgent
# from devsecops_agent import DevSecOpsAgent
# from secrets_agent import SecretsAgent

try:
    from crewai import Agent, Task, Crew, Process
    from crewai.agent import Agent as CrewAgent
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    # Fallback implementation without CrewAI
    class Agent:
        def __init__(self, **kwargs): pass
    class Task:
        def __init__(self, **kwargs): pass
    class Crew:
        def __init__(self, **kwargs): pass
        def kickoff(self): return {"result": "CrewAI not available"}
    class Process:
        sequential = "sequential"

class GuidePointCrewOrchestrator:
    """
    Multi-agent security coordination using CrewAI

    Orchestrates complex security workflows by coordinating specialized agents:
    1. Scanner Agent for vulnerability detection and remediation
    2. Kubernetes Agent for cluster security hardening
    3. IaC/Policy Agent for infrastructure and policy security
    4. DevSecOps Agent for CI/CD security automation
    5. Consulting Agent for client reporting and engagement
    """

    def __init__(self):
        self.orchestrator_id = "guidepoint_crew_orchestrator"

        # Initialize specialized agents
        self.scanner_agent = ScannerAgent()
        self.kubernetes_agent = KubernetesAgent()
        self.iac_policy_agent = IaCPolicyAgent()
        self.devsecops_agent = DevSecOpsAgent()
        self.secrets_agent = SecretsAgent()

        # Track orchestration history
        self.orchestration_history = []

        # CrewAI agents (if available)
        self.crew_agents = {}
        self.crew = None

        if CREWAI_AVAILABLE:
            self._initialize_crew_agents()

    def _initialize_crew_agents(self):
        """Initialize CrewAI agents with specialized roles"""

        # Scanner Agent for CrewAI
        self.crew_agents['scanner'] = Agent(
            role='Security Scanner Specialist',
            goal='Detect and remediate vulnerabilities across all technology stacks',
            backstory="""You are an expert security scanner with deep knowledge of vulnerability
            detection and autonomous remediation. You excel at finding security issues in containers,
            dependencies, code, and infrastructure, and can automatically fix many common vulnerabilities.""",
            verbose=True,
            allow_delegation=True
        )

        # Kubernetes Agent for CrewAI
        self.crew_agents['kubernetes'] = Agent(
            role='Kubernetes Security Expert',
            goal='Secure Kubernetes clusters with CKA/CKS level expertise',
            backstory="""You are a Certified Kubernetes Administrator (CKA) and Certified Kubernetes
            Security Specialist (CKS) with expertise in cluster hardening, RBAC policies, network
            security, and Pod Security Standards. You ensure Kubernetes deployments meet enterprise
            security requirements.""",
            verbose=True,
            allow_delegation=True
        )

        # IaC/Policy Agent for CrewAI
        self.crew_agents['iac_policy'] = Agent(
            role='Infrastructure & Policy Security Specialist',
            goal='Secure infrastructure through code and policy enforcement',
            backstory="""You are an expert in Infrastructure as Code (IaC) security and Policy as Code
            implementation. You secure Terraform, CloudFormation, and Kubernetes manifests while
            implementing OPA/Kyverno policies for automated security enforcement.""",
            verbose=True,
            allow_delegation=True
        )

        # DevSecOps Agent for CrewAI
        self.crew_agents['devsecops'] = Agent(
            role='DevSecOps Pipeline Specialist',
            goal='Integrate security into CI/CD pipelines with automation',
            backstory="""You are a DevSecOps expert who integrates security seamlessly into development
            workflows. You implement security gates, automate security testing, and ensure that security
            is built into every stage of the software delivery pipeline.""",
            verbose=True,
            allow_delegation=True
        )

    async def execute_comprehensive_security_assessment(self, project_path: str, client_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute comprehensive multi-agent security assessment

        This is the flagship workflow that demonstrates the power of coordinated agents:
        1. Scanner Agent discovers and remediates vulnerabilities
        2. Kubernetes Agent secures cluster configurations
        3. IaC/Policy Agent validates infrastructure security
        4. DevSecOps Agent implements CI/CD security gates
        5. Results consolidated into executive reporting
        """
        assessment_start = datetime.now()

        orchestration_result = {
            "orchestration_id": f"security-assessment-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "project_path": project_path,
            "client_requirements": client_requirements or {},
            "timestamp": assessment_start.isoformat(),
            "agent_results": {},
            "consolidated_findings": {},
            "executive_summary": {},
            "crewai_coordination": CREWAI_AVAILABLE
        }

        try:
            print(f"🚀 GuidePoint Crew Orchestrator executing comprehensive assessment: {project_path}")

            # Phase 1: Parallel vulnerability and infrastructure discovery
            print(f"\n📊 Phase 1: Multi-Agent Security Discovery")

            # Run agents in parallel for efficiency
            scanner_task = self.scanner_agent.analyze_project(project_path)
            iac_task = self.iac_policy_agent.analyze_infrastructure(project_path)
            k8s_task = self._analyze_kubernetes_if_present(project_path)
            devsecops_task = self.devsecops_agent.analyze_pipeline_security(project_path)

            # Await all parallel tasks
            scanner_result, iac_result, k8s_result, devsecops_result = await asyncio.gather(
                scanner_task, iac_task, k8s_task, devsecops_task, return_exceptions=True
            )

            # Store agent results
            orchestration_result["agent_results"] = {
                "scanner": scanner_result if not isinstance(scanner_result, Exception) else {"error": str(scanner_result)},
                "iac_policy": iac_result if not isinstance(iac_result, Exception) else {"error": str(iac_result)},
                "kubernetes": k8s_result if not isinstance(k8s_result, Exception) else {"error": str(k8s_result)},
                "devsecops": devsecops_result if not isinstance(devsecops_result, Exception) else {"error": str(devsecops_result)}
            }

            # Phase 2: Autonomous remediation coordination
            print(f"\n🔧 Phase 2: Coordinated Security Remediation")

            remediation_results = {}

            # Scanner Agent autonomous remediation
            if isinstance(scanner_result, dict) and scanner_result.get("vulnerabilities"):
                print("Scanner Agent executing autonomous remediation...")
                scanner_remediation = await self.scanner_agent.execute_autonomous_remediation(project_path)
                remediation_results["scanner"] = scanner_remediation

            # DevSecOps pipeline implementation
            if isinstance(devsecops_result, dict) and devsecops_result.get("security_gaps"):
                print("DevSecOps Agent implementing security pipeline...")
                pipeline_implementation = await self.devsecops_agent.implement_devsecops_pipeline(project_path)
                remediation_results["devsecops"] = pipeline_implementation

            # IaC security policies
            if isinstance(iac_result, dict) and iac_result.get("security_findings"):
                print("IaC/Policy Agent generating security policies...")
                policy_creation = await self.iac_policy_agent.create_security_policies(
                    f"{project_path}/generated_policies"
                )
                remediation_results["iac_policy"] = policy_creation

            # Kubernetes hardening (if applicable)
            if isinstance(k8s_result, dict) and k8s_result.get("security_issues"):
                print("Kubernetes Agent generating security manifests...")
                k8s_hardening = await self.kubernetes_agent.generate_security_manifests(
                    f"{project_path}/k8s_security", namespace="default"
                )
                remediation_results["kubernetes"] = k8s_hardening

            orchestration_result["remediation_results"] = remediation_results

            # Phase 3: Consolidation and reporting
            print(f"\n📋 Phase 3: Executive Reporting and Consolidation")

            consolidated_findings = self._consolidate_security_findings(orchestration_result["agent_results"])
            orchestration_result["consolidated_findings"] = consolidated_findings

            executive_summary = self._generate_executive_summary(
                consolidated_findings, remediation_results, client_requirements
            )
            orchestration_result["executive_summary"] = executive_summary

            # CrewAI coordination (if available)
            if CREWAI_AVAILABLE:
                crew_result = await self._execute_crewai_coordination(orchestration_result)
                orchestration_result["crew_coordination"] = crew_result

            print(f"✅ GuidePoint Crew Orchestrator assessment complete")
            print(f"   Total vulnerabilities: {consolidated_findings.get('total_vulnerabilities', 0)}")
            print(f"   Security domains covered: {len(consolidated_findings.get('security_domains', []))}")
            print(f"   Remediation success rate: {consolidated_findings.get('remediation_success_rate', 0):.1f}%")

            self.orchestration_history.append(orchestration_result)

        except Exception as e:
            orchestration_result["error"] = str(e)
            print(f"❌ GuidePoint Crew Orchestrator failed: {e}")

        orchestration_result["duration_seconds"] = (datetime.now() - assessment_start).total_seconds()
        return orchestration_result

    async def _analyze_kubernetes_if_present(self, project_path: str) -> Dict[str, Any]:
        """Analyze Kubernetes configurations if present"""
        project_path_obj = Path(project_path)

        # Check for Kubernetes manifests
        k8s_files = []
        for pattern in ["**/*.yaml", "**/*.yml"]:
            for file_path in project_path_obj.glob(pattern):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if any(keyword in content for keyword in ["apiVersion:", "kind:", "metadata:"]):
                            k8s_files.append(str(file_path))
                except:
                    continue

        if k8s_files:
            # Use Kubernetes agent to analyze manifests
            return await self.kubernetes_agent.analyze_cluster_security(
                kubeconfig_path=None,
                manifests_path=str(project_path)
            )
        else:
            return {"message": "No Kubernetes manifests found", "security_issues": []}

    def _consolidate_security_findings(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate findings from all agents into unified view"""
        consolidated = {
            "total_vulnerabilities": 0,
            "security_domains": [],
            "critical_findings": [],
            "high_findings": [],
            "medium_findings": [],
            "remediation_success_rate": 0,
            "compliance_status": {},
            "by_agent": {}
        }

        total_remediations = 0
        successful_remediations = 0

        for agent_name, result in agent_results.items():
            if isinstance(result, dict) and not result.get("error"):
                agent_summary = {
                    "vulnerabilities_found": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0
                }

                # Scanner Agent results
                if agent_name == "scanner":
                    vulns = result.get("vulnerabilities", [])
                    agent_summary["vulnerabilities_found"] = len(vulns)
                    consolidated["security_domains"].append("Application Security")
                    consolidated["security_domains"].append("Container Security")

                    for vuln in vulns:
                        severity = vuln.get("severity", "MEDIUM").upper()
                        if severity == "CRITICAL":
                            consolidated["critical_findings"].append(vuln)
                            agent_summary["critical"] += 1
                        elif severity == "HIGH":
                            consolidated["high_findings"].append(vuln)
                            agent_summary["high"] += 1
                        else:
                            consolidated["medium_findings"].append(vuln)
                            agent_summary["medium"] += 1

                # IaC/Policy Agent results
                elif agent_name == "iac_policy":
                    findings = result.get("security_findings", [])
                    agent_summary["vulnerabilities_found"] = len(findings)
                    consolidated["security_domains"].append("Infrastructure Security")

                    for finding in findings:
                        severity = finding.get("severity", "MEDIUM").upper()
                        if severity == "CRITICAL":
                            consolidated["critical_findings"].append(finding)
                            agent_summary["critical"] += 1
                        elif severity == "HIGH":
                            consolidated["high_findings"].append(finding)
                            agent_summary["high"] += 1

                # Kubernetes Agent results
                elif agent_name == "kubernetes":
                    violations = result.get("pod_security", {}).get("violations", [])
                    agent_summary["vulnerabilities_found"] = len(violations)
                    consolidated["security_domains"].append("Kubernetes Security")

                    for violation in violations:
                        consolidated["high_findings"].append(violation)
                        agent_summary["high"] += 1

                # DevSecOps Agent results
                elif agent_name == "devsecops":
                    gaps = result.get("security_gaps", [])
                    agent_summary["vulnerabilities_found"] = len(gaps)
                    consolidated["security_domains"].append("CI/CD Security")

                    for gap in gaps:
                        severity = gap.get("severity", "MEDIUM").upper()
                        if severity == "CRITICAL":
                            consolidated["critical_findings"].append(gap)
                            agent_summary["critical"] += 1
                        elif severity == "HIGH":
                            consolidated["high_findings"].append(gap)
                            agent_summary["high"] += 1

                consolidated["by_agent"][agent_name] = agent_summary
                consolidated["total_vulnerabilities"] += agent_summary["vulnerabilities_found"]

        # Calculate overall remediation success rate
        if total_remediations > 0:
            consolidated["remediation_success_rate"] = (successful_remediations / total_remediations) * 100

        # Remove duplicates from security domains
        consolidated["security_domains"] = list(set(consolidated["security_domains"]))

        return consolidated

    def _generate_executive_summary(self, findings: Dict[str, Any], remediation_results: Dict[str, Any],
                                  client_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary for stakeholder consumption"""

        total_vulns = findings.get("total_vulnerabilities", 0)
        critical_count = len(findings.get("critical_findings", []))
        high_count = len(findings.get("high_findings", []))

        # Calculate risk score
        risk_score = min(100, (critical_count * 20) + (high_count * 10) + (total_vulns * 2))

        if risk_score >= 80:
            risk_level = "CRITICAL"
        elif risk_score >= 60:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Count successful remediations across all result types
        total_remediations = 0
        for result in remediation_results.values():
            if isinstance(result, dict):
                # Different agents use different keys for tracking work done
                total_remediations += len(result.get("files_modified", []))
                total_remediations += len(result.get("files_created", []))
                total_remediations += len(result.get("policies_created", []))
                total_remediations += result.get("manifests_generated", 0)
                total_remediations += result.get("issues_remediated", 0)

        return {
            "assessment_date": datetime.now().strftime("%Y-%m-%d"),
            "project_security_posture": {
                "overall_risk_score": risk_score,
                "risk_level": risk_level,
                "total_vulnerabilities": total_vulns,
                "critical_vulnerabilities": critical_count,
                "high_vulnerabilities": high_count
            },
            "security_coverage": {
                "domains_assessed": findings.get("security_domains", []),
                "agents_deployed": len([a for a in ["scanner", "kubernetes", "iac_policy", "devsecops"]]),
                "comprehensive_coverage": len(findings.get("security_domains", [])) >= 3
            },
            "remediation_summary": {
                "autonomous_fixes_applied": total_remediations,
                "manual_review_required": critical_count + high_count,
                "security_policies_generated": len(remediation_results.get("iac_policy", {}).get("policies_created", [])),
                "pipeline_security_implemented": "devsecops" in remediation_results
            },
            "business_impact": {
                "estimated_hours_saved": total_remediations * 2,  # 2 hours per automated fix
                "consultant_cost_avoided": total_remediations * 150,  # $150/hour consultant rate
                "security_debt_reduced": f"{min(100, (total_remediations / max(1, total_vulns)) * 100):.1f}%"
            },
            "next_steps": self._generate_next_steps(critical_count, high_count, remediation_results),
            "compliance_readiness": {
                "soc2_readiness": "PARTIAL" if total_vulns < 10 else "NOT_READY",
                "iso27001_readiness": "PARTIAL" if critical_count == 0 else "NOT_READY",
                "gdpr_readiness": "REVIEW_REQUIRED"
            }
        }

    def _generate_next_steps(self, critical_count: int, high_count: int, remediation_results: Dict) -> List[str]:
        """Generate actionable next steps based on assessment results"""
        next_steps = []

        if critical_count > 0:
            next_steps.append(f"🚨 IMMEDIATE: Address {critical_count} critical vulnerabilities within 24 hours")

        if high_count > 0:
            next_steps.append(f"⚠️ HIGH PRIORITY: Remediate {high_count} high-severity issues within 72 hours")

        if "devsecops" in remediation_results:
            next_steps.append("✅ Review and deploy the generated CI/CD security pipeline")

        if "iac_policy" in remediation_results:
            next_steps.append("✅ Implement the generated security policies in your infrastructure")

        if "kubernetes" in remediation_results:
            next_steps.append("✅ Apply Kubernetes security manifests to production cluster")

        next_steps.append("📊 Schedule follow-up security assessment in 30 days")
        next_steps.append("📋 Consider security awareness training for development team")

        return next_steps

    async def _execute_crewai_coordination(self, orchestration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CrewAI-based agent coordination (if available)"""
        if not CREWAI_AVAILABLE:
            return {"status": "CrewAI not available"}

        try:
            # Create tasks for CrewAI coordination
            tasks = []

            # Security Assessment Task
            security_task = Task(
                description=f"""Coordinate comprehensive security assessment for project: {orchestration_result['project_path']}

                Review results from all specialized agents:
                - Scanner Agent findings: {len(orchestration_result['agent_results'].get('scanner', {}).get('vulnerabilities', []))} vulnerabilities
                - Kubernetes security issues: {len(orchestration_result['agent_results'].get('kubernetes', {}).get('security_issues', []))} issues
                - Infrastructure security findings: {len(orchestration_result['agent_results'].get('iac_policy', {}).get('security_findings', []))} findings
                - DevSecOps gaps: {len(orchestration_result['agent_results'].get('devsecops', {}).get('security_gaps', []))} gaps

                Provide strategic coordination recommendations for maximum security impact.""",
                expected_output="A detailed security coordination report with prioritized recommendations, risk assessment, and strategic guidance for addressing findings across all security domains. Include specific next steps and coordination strategies between agents.",
                agent=self.crew_agents['scanner']
            )
            tasks.append(security_task)

            # Create and execute crew
            crew = Crew(
                agents=list(self.crew_agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )

            crew_result = crew.kickoff()

            return {
                "status": "success",
                "coordination_result": str(crew_result),
                "agents_coordinated": len(self.crew_agents),
                "tasks_completed": len(tasks)
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status and capabilities"""
        return {
            "orchestrator_id": self.orchestrator_id,
            "available_agents": {
                "scanner": bool(self.scanner_agent),
                "kubernetes": bool(self.kubernetes_agent),
                "iac_policy": bool(self.iac_policy_agent),
                "devsecops": bool(self.devsecops_agent),
                "secrets": bool(self.secrets_agent)
            },
            "crewai_available": CREWAI_AVAILABLE,
            "orchestrations_completed": len(self.orchestration_history),
            "supported_workflows": [
                "comprehensive_security_assessment",
                "vulnerability_remediation_workflow",
                "infrastructure_hardening_workflow",
                "devsecops_implementation_workflow"
            ]
        }


# CLI interface for Crew Orchestrator
async def main():
    """CLI interface for GuidePoint Crew Orchestrator"""
    if len(sys.argv) < 2:
        print("Usage: python crew_orchestrator.py <command> [options]")
        print("Commands:")
        print("  assess <project_path>     - Execute comprehensive security assessment")
        print("  status                   - Show orchestrator status")
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        orchestrator = GuidePointCrewOrchestrator()
        status = orchestrator.get_orchestrator_status()
        print(f"🎭 GuidePoint Crew Orchestrator Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        return

    orchestrator = GuidePointCrewOrchestrator()

    if command == "assess":
        if len(sys.argv) != 3:
            print("Usage: python crew_orchestrator.py assess <project_path>")
            sys.exit(1)

        project_path = sys.argv[2]
        if not os.path.exists(project_path):
            print(f"Error: Project path {project_path} does not exist")
            sys.exit(1)

        print("🚀 GUIDEPOINT CREW ORCHESTRATOR")
        print("=" * 50)
        result = await orchestrator.execute_comprehensive_security_assessment(project_path)

        print(f"\n📊 Assessment Results:")
        executive_summary = result.get('executive_summary', {})
        posture = executive_summary.get('project_security_posture', {})
        print(f"Overall risk score: {posture.get('overall_risk_score', 0)}/100")
        print(f"Risk level: {posture.get('risk_level', 'UNKNOWN')}")
        print(f"Total vulnerabilities: {posture.get('total_vulnerabilities', 0)}")

        coverage = executive_summary.get('security_coverage', {})
        print(f"Security domains: {len(coverage.get('domains_assessed', []))}")
        print(f"Comprehensive coverage: {coverage.get('comprehensive_coverage', False)}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())