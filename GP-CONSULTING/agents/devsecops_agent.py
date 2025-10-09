#!/usr/bin/env python3
"""
CI/CD Security Analysis Agent - Safe Recommendations
===================================================

Safe CI/CD security analysis agent that:
- Analyzes existing pipelines for security gaps
- Generates actionable security recommendations
- Provides YAML snippets for human implementation
- NO AUTOMATIC PIPELINE MODIFICATION

Maps to job requirement: "Help integrate basic security controls into CI/CD pipelines under senior guidance"
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

# Import GP-DATA config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class SecurityGate(str, Enum):
    SECRETS_SCAN = "secrets_scan"
    DEPENDENCY_SCAN = "dependency_scan"
    SAST_SCAN = "sast_scan"
    CONTAINER_SCAN = "container_scan"
    IAC_SCAN = "iac_scan"
    SBOM_GENERATION = "sbom_generation"


class CICDSecurityAnalysisAgent:
    """
    CI/CD Security Analysis and Recommendation Agent

    Safe capabilities:
    - Pipeline security analysis
    - Security gap identification
    - Integration recommendations
    - YAML snippet generation
    - Implementation guidance

    NO automatic pipeline modification
    """

    def __init__(self):
        self.agent_id = "cicd_security_analyst"
        self.config = GPDataConfig()

        self.capabilities = [
            "pipeline_security_analysis",
            "security_gap_identification",
            "integration_recommendations",
            "yaml_snippet_generation",
            "implementation_guidance"
        ]

        # Security baseline
        self.security_baseline = {
            "mandatory_gates": [
                SecurityGate.SECRETS_SCAN,
                SecurityGate.DEPENDENCY_SCAN,
                SecurityGate.SAST_SCAN
            ],
            "recommended_gates": [
                SecurityGate.CONTAINER_SCAN,
                SecurityGate.IAC_SCAN,
                SecurityGate.SBOM_GENERATION
            ]
        }

    def analyze_pipeline_security(self, project_path: str) -> Dict[str, Any]:
        """Analyze existing CI/CD pipeline security"""
        analysis_start = datetime.now()

        analysis_result = {
            "agent": self.agent_id,
            "project_path": project_path,
            "timestamp": analysis_start.isoformat(),
            "pipelines_found": {},
            "security_gaps": [],
            "maturity_score": 0,
            "recommendations": []
        }

        try:
            print(f"🔍 Analyzing CI/CD security: {project_path}")

            # Discover pipelines
            pipelines = self._discover_pipelines(project_path)
            analysis_result["pipelines_found"] = pipelines

            # Analyze security gaps
            security_gaps = []
            for pipeline_type, files in pipelines.items():
                for pipeline_file in files:
                    gaps = self._analyze_pipeline_file(pipeline_file, pipeline_type)
                    security_gaps.extend(gaps)

            analysis_result["security_gaps"] = security_gaps

            # Calculate maturity
            maturity = self._calculate_maturity(security_gaps, pipelines)
            analysis_result["maturity_score"] = maturity["score"]
            analysis_result["maturity_level"] = maturity["level"]

            # Generate recommendations
            recommendations = self._generate_recommendations(security_gaps, pipelines)
            analysis_result["recommendations"] = recommendations

            print(f"✅ Analysis complete: {len(security_gaps)} gaps found")

        except Exception as e:
            analysis_result["error"] = str(e)
            print(f"❌ Analysis failed: {e}")

        # Save to GP-DATA
        self._save_analysis(analysis_result)

        return analysis_result

    def _discover_pipelines(self, project_path: str) -> Dict[str, List[str]]:
        """Discover existing CI/CD pipeline files"""
        pipelines = {
            "github_actions": [],
            "gitlab_ci": [],
            "jenkins": [],
            "azure_devops": [],
            "circleci": []
        }

        project_path = Path(project_path)

        # GitHub Actions
        github_workflows = project_path / ".github" / "workflows"
        if github_workflows.exists():
            for workflow_file in github_workflows.glob("*.yml"):
                pipelines["github_actions"].append(str(workflow_file))
            for workflow_file in github_workflows.glob("*.yaml"):
                pipelines["github_actions"].append(str(workflow_file))

        # GitLab CI
        gitlab_ci = project_path / ".gitlab-ci.yml"
        if gitlab_ci.exists():
            pipelines["gitlab_ci"].append(str(gitlab_ci))

        # Jenkins
        jenkinsfile = project_path / "Jenkinsfile"
        if jenkinsfile.exists():
            pipelines["jenkins"].append(str(jenkinsfile))

        # Azure DevOps
        azure_pipelines = project_path / "azure-pipelines.yml"
        if azure_pipelines.exists():
            pipelines["azure_devops"].append(str(azure_pipelines))

        # CircleCI
        circleci_config = project_path / ".circleci" / "config.yml"
        if circleci_config.exists():
            pipelines["circleci"].append(str(circleci_config))

        return pipelines

    def _analyze_pipeline_file(self, pipeline_file: str, pipeline_type: str) -> List[Dict]:
        """Analyze pipeline file for security gaps"""
        gaps = []

        try:
            with open(pipeline_file, 'r') as f:
                content = f.read()

            # Check for missing security gates
            if "gitleaks" not in content.lower() and "trufflehog" not in content.lower():
                gaps.append({
                    "type": "missing_security_gate",
                    "severity": "HIGH",
                    "pipeline_file": pipeline_file,
                    "pipeline_type": pipeline_type,
                    "missing_gate": SecurityGate.SECRETS_SCAN,
                    "description": "Missing secrets scanning in pipeline",
                    "recommendation": "Add secrets scanning with gitleaks or trufflehog"
                })

            if "bandit" not in content.lower() and "semgrep" not in content.lower():
                gaps.append({
                    "type": "missing_security_gate",
                    "severity": "HIGH",
                    "pipeline_file": pipeline_file,
                    "pipeline_type": pipeline_type,
                    "missing_gate": SecurityGate.SAST_SCAN,
                    "description": "Missing SAST scanning in pipeline",
                    "recommendation": "Add SAST scanning with bandit or semgrep"
                })

            if "npm audit" not in content.lower() and "safety" not in content.lower():
                gaps.append({
                    "type": "missing_security_gate",
                    "severity": "HIGH",
                    "pipeline_file": pipeline_file,
                    "pipeline_type": pipeline_type,
                    "missing_gate": SecurityGate.DEPENDENCY_SCAN,
                    "description": "Missing dependency scanning in pipeline",
                    "recommendation": "Add dependency scanning with npm audit or safety"
                })

            if "trivy" not in content.lower():
                gaps.append({
                    "type": "missing_security_gate",
                    "severity": "MEDIUM",
                    "pipeline_file": pipeline_file,
                    "pipeline_type": pipeline_type,
                    "missing_gate": SecurityGate.CONTAINER_SCAN,
                    "description": "Missing container scanning in pipeline",
                    "recommendation": "Add container scanning with trivy"
                })

        except Exception as e:
            gaps.append({
                "type": "analysis_error",
                "severity": "LOW",
                "pipeline_file": pipeline_file,
                "description": f"Error analyzing pipeline: {str(e)}"
            })

        return gaps

    def _calculate_maturity(self, gaps: List[Dict], pipelines: Dict) -> Dict:
        """Calculate DevSecOps maturity score"""
        total_pipelines = sum(len(files) for files in pipelines.values())

        if total_pipelines == 0:
            return {"score": 0, "level": "Initial"}

        mandatory_gates = len(self.security_baseline["mandatory_gates"])
        missing_mandatory = len([g for g in gaps if g.get("missing_gate") in self.security_baseline["mandatory_gates"]])

        implemented = mandatory_gates - missing_mandatory
        score = (implemented / mandatory_gates) * 100 if mandatory_gates > 0 else 0

        if score >= 80:
            level = "Managed"
        elif score >= 50:
            level = "Defined"
        elif score >= 30:
            level = "Repeatable"
        else:
            level = "Initial"

        return {"score": round(score, 1), "level": level}

    def _generate_recommendations(self, gaps: List[Dict], pipelines: Dict) -> List[Dict]:
        """Generate security recommendations"""
        recommendations = []

        # Group by severity
        critical_gaps = [g for g in gaps if g.get("severity") == "CRITICAL"]
        high_gaps = [g for g in gaps if g.get("severity") == "HIGH"]

        if critical_gaps:
            recommendations.append({
                "priority": "immediate",
                "category": "Critical Security",
                "action": "Address critical security gaps",
                "gaps": critical_gaps[:3]
            })

        if high_gaps:
            recommendations.append({
                "priority": "high",
                "category": "Security Gates",
                "action": "Add missing security gates",
                "gaps": high_gaps[:5]
            })

        return recommendations

    def generate_security_integration_plan(self, analysis_results: Dict, pipeline_type: str = "github_actions") -> Dict:
        """Generate human-reviewable integration plan"""
        integration_plan = {
            "immediate_actions": [],
            "security_controls": [],
            "yaml_snippets": {},
            "implementation_steps": [],
            "validation_checklist": []
        }

        gaps = analysis_results.get("security_gaps", [])

        # Process high-priority gaps
        for gap in gaps:
            if gap.get("severity") in ["CRITICAL", "HIGH"]:
                missing_gate = gap.get("missing_gate")

                integration_plan["immediate_actions"].append({
                    "priority": gap["severity"],
                    "issue": gap["description"],
                    "recommendation": gap["recommendation"],
                    "pipeline_file": gap.get("pipeline_file")
                })

                # Generate YAML snippet
                if missing_gate:
                    snippet = self._generate_yaml_snippet(missing_gate, pipeline_type)
                    integration_plan["yaml_snippets"][missing_gate] = snippet

        # Generate implementation steps
        integration_plan["implementation_steps"] = self._generate_implementation_steps(gaps)

        # Generate validation checklist
        integration_plan["validation_checklist"] = self._generate_validation_checklist()

        return integration_plan

    def _generate_yaml_snippet(self, security_gate: str, pipeline_type: str) -> Dict:
        """Generate safe YAML snippets for human implementation"""

        if pipeline_type == "github_actions":
            snippets = {
                SecurityGate.SECRETS_SCAN: {
                    "step_name": "Secret Detection",
                    "yaml": """- name: Run Gitleaks Secret Scan
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}""",
                    "notes": "Scans for hardcoded secrets and credentials"
                },
                SecurityGate.DEPENDENCY_SCAN: {
                    "step_name": "Dependency Scan",
                    "yaml": """- name: NPM Security Audit
  run: npm audit --audit-level moderate
  if: hashFiles('**/package.json') != ''""",
                    "notes": "Checks for vulnerable npm dependencies"
                },
                SecurityGate.SAST_SCAN: {
                    "step_name": "SAST Analysis",
                    "yaml": """- name: Python SAST Scan
  run: |
    pip install bandit
    bandit -r . -f json -o bandit-results.json
  if: hashFiles('**/*.py') != ''""",
                    "notes": "Static analysis for Python code"
                },
                SecurityGate.CONTAINER_SCAN: {
                    "step_name": "Container Security",
                    "yaml": """- name: Trivy Container Scan
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    format: 'sarif'
    output: 'trivy-results.sarif'""",
                    "notes": "Scans filesystem and containers for vulnerabilities"
                }
            }
        else:  # gitlab_ci
            snippets = {
                SecurityGate.SECRETS_SCAN: {
                    "step_name": "Secrets Scan",
                    "yaml": """secrets_scan:
  stage: security
  image: zricethezav/gitleaks:latest
  script:
    - gitleaks detect --source . --verbose""",
                    "notes": "Detects hardcoded secrets"
                },
                SecurityGate.DEPENDENCY_SCAN: {
                    "step_name": "Dependency Scan",
                    "yaml": """dependency_scan:
  stage: security
  image: node:18
  script:
    - npm audit --audit-level moderate
  only:
    changes:
      - "**/package.json\"""",
                    "notes": "Scans npm dependencies"
                }
            }

        return snippets.get(security_gate, {"error": "Unknown security gate"})

    def _generate_implementation_steps(self, gaps: List[Dict]) -> List[Dict]:
        """Generate step-by-step implementation guide"""
        return [
            {
                "step": 1,
                "action": "Review current pipeline configuration",
                "details": "Understand existing workflow before adding security controls"
            },
            {
                "step": 2,
                "action": "Test security tools locally",
                "details": "Run recommended scans locally to understand output"
            },
            {
                "step": 3,
                "action": "Add security controls incrementally",
                "details": "Implement one control at a time, test each addition"
            },
            {
                "step": 4,
                "action": "Configure failure thresholds",
                "details": "Set appropriate thresholds based on project maturity"
            },
            {
                "step": 5,
                "action": "Document security controls",
                "details": "Update README with security documentation"
            },
            {
                "step": 6,
                "action": "Monitor and iterate",
                "details": "Review security findings and adjust controls"
            }
        ]

    def _generate_validation_checklist(self) -> List[Dict]:
        """Generate validation checklist"""
        return [
            {"item": "Security tools run successfully", "status": "pending"},
            {"item": "No critical vulnerabilities blocking deployment", "status": "pending"},
            {"item": "Security scan results are actionable", "status": "pending"},
            {"item": "Team understands how to address findings", "status": "pending"},
            {"item": "Documentation updated", "status": "pending"}
        ]

    def _save_analysis(self, analysis: Dict):
        """Save analysis to GP-DATA"""
        analysis_dir = self.config.get_analysis_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cicd_security_analysis_{timestamp}.json"
        output_file = analysis_dir / filename

        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"\n💾 Analysis saved to: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("CI/CD Security Analysis Agent - Safe Recommendations")
        print()
        print("Commands:")
        print("  analyze <project_path>                    - Analyze pipeline security")
        print("  recommend <project_path> <pipeline_type>  - Get integration plan")
        print("  snippet <security_gate> <pipeline_type>   - Get YAML snippet")
        print()
        print("Pipeline Types: github_actions, gitlab_ci")
        print("Security Gates: secrets_scan, dependency_scan, sast_scan, container_scan")
        print()
        print("Examples:")
        print("  python devsecops_agent.py analyze ./my-project")
        print("  python devsecops_agent.py recommend ./my-project github_actions")
        print("  python devsecops_agent.py snippet secrets_scan github_actions")
        sys.exit(1)

    command = sys.argv[1]
    agent = CICDSecurityAnalysisAgent()

    if command == "analyze":
        if len(sys.argv) < 3:
            print("Usage: python devsecops_agent.py analyze <project_path>")
            sys.exit(1)

        project_path = sys.argv[2]
        results = agent.analyze_pipeline_security(project_path)

        print(f"\n{'='*60}")
        print("CI/CD Security Analysis Results")
        print(f"{'='*60}")
        print(f"Project: {results['project_path']}")
        print(f"Maturity: {results.get('maturity_score', 0)}/100 ({results.get('maturity_level', 'Unknown')})")
        print(f"Security Gaps: {len(results['security_gaps'])}")
        print(f"Recommendations: {len(results['recommendations'])}")

    elif command == "recommend":
        if len(sys.argv) < 4:
            print("Usage: python devsecops_agent.py recommend <project_path> <pipeline_type>")
            sys.exit(1)

        project_path = sys.argv[2]
        pipeline_type = sys.argv[3]

        analysis = agent.analyze_pipeline_security(project_path)
        plan = agent.generate_security_integration_plan(analysis, pipeline_type)

        print(f"\n{'='*60}")
        print("Security Integration Plan")
        print(f"{'='*60}")
        print(f"\nImmediate Actions ({len(plan['immediate_actions'])}):")
        for action in plan['immediate_actions'][:3]:
            print(f"  - {action['issue']}")
            print(f"    Fix: {action['recommendation']}")

        print(f"\nYAML Snippets Available:")
        for gate in plan['yaml_snippets'].keys():
            print(f"  - {gate}")

    elif command == "snippet":
        if len(sys.argv) < 4:
            print("Usage: python devsecops_agent.py snippet <security_gate> <pipeline_type>")
            sys.exit(1)

        security_gate = sys.argv[2]
        pipeline_type = sys.argv[3]

        snippet = agent._generate_yaml_snippet(security_gate, pipeline_type)

        print(f"\n{'='*60}")
        print(f"YAML Snippet: {snippet.get('step_name', 'Unknown')}")
        print(f"{'='*60}")
        print(snippet.get('yaml', 'No snippet available'))
        print(f"\nNotes: {snippet.get('notes', 'N/A')}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()