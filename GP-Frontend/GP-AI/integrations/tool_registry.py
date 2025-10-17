"""
Jade AI Tool Registry & Contextual Awareness
Gives Jade complete knowledge of available security tools and execution patterns
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class SecurityTool:
    """Security tool definition with capabilities and execution info"""
    name: str
    binary_path: str
    file_patterns: List[str]
    output_format: str
    command_template: str
    description: str
    categories: List[str]
    compliance_frameworks: List[str] = None
    dependencies: List[str] = None

class JadeToolRegistry:
    """Jade's contextual awareness of security tool ecosystem"""

    def __init__(self):
        self.tools = {}
        self.project_contexts = {}
        self.execution_patterns = {}

        self._initialize_tool_registry()
        self._load_execution_patterns()

    def _initialize_tool_registry(self):
        """Initialize Jade's knowledge of available security tools"""

        # Terraform Security Tools
        self.tools["terraform"] = {
            "tfsec": SecurityTool(
                name="tfsec",
                binary_path="/home/jimmie/bin/tfsec",
                file_patterns=["*.tf", "*.tfvars"],
                output_format="json",
                command_template="tfsec {project_path} --format json --out {output_file}",
                description="Terraform security scanner for AWS, Azure, GCP",
                categories=["iac", "security", "terraform"],
                compliance_frameworks=["CIS", "SOC2"]
            ),
            "checkov": SecurityTool(
                name="checkov",
                binary_path="/home/jimmie/.local/bin/checkov",
                file_patterns=["*.tf", "*.yaml", "*.yml", "*.json"],
                output_format="json",
                command_template="checkov -d {project_path} -o json --output-file {output_file}",
                description="Multi-cloud IaC security and compliance scanner",
                categories=["iac", "compliance", "terraform", "kubernetes"],
                compliance_frameworks=["CIS", "SOC2", "PCI-DSS", "HIPAA"]
            ),
            "terraform_validate": SecurityTool(
                name="terraform_validate",
                binary_path="/usr/bin/terraform",
                file_patterns=["*.tf"],
                output_format="text",
                command_template="terraform validate {project_path}",
                description="Terraform syntax and configuration validation",
                categories=["iac", "validation", "terraform"]
            )
        }

        # Kubernetes Security Tools
        self.tools["kubernetes"] = {
            "kubescape": SecurityTool(
                name="kubescape",
                binary_path="/home/jimmie/bin/kubescape",
                file_patterns=["*.yaml", "*.yml"],
                output_format="json",
                command_template="kubescape scan {project_path} --format json --output {output_file}",
                description="Kubernetes security posture scanner with CKS focus",
                categories=["kubernetes", "security", "cks"],
                compliance_frameworks=["CIS", "NSA-CISA", "SOC2"]
            ),
            "kube_bench": SecurityTool(
                name="kube_bench",
                binary_path="/home/jimmie/bin/kube-bench",
                file_patterns=["*.yaml", "*.yml"],
                output_format="json",
                command_template="kube-bench run --json --outputfile {output_file}",
                description="CIS Kubernetes Benchmark security checker",
                categories=["kubernetes", "cis", "benchmark"],
                compliance_frameworks=["CIS"]
            ),
            "polaris": SecurityTool(
                name="polaris",
                binary_path="/home/jimmie/bin/polaris",
                file_patterns=["*.yaml", "*.yml"],
                output_format="json",
                command_template="polaris audit --audit-path {project_path} --format json > {output_file}",
                description="Kubernetes best practices and security validator",
                categories=["kubernetes", "best-practices", "security"]
            ),
            "opa": SecurityTool(
                name="opa",
                binary_path="/home/jimmie/bin/opa",
                file_patterns=["*.yaml", "*.yml", "*.rego"],
                output_format="json",
                command_template="opa test {project_path} --format json",
                description="Open Policy Agent for Kubernetes policy enforcement",
                categories=["kubernetes", "policy", "governance"]
            )
        }

        # Application Security Tools
        self.tools["application"] = {
            "bandit": SecurityTool(
                name="bandit",
                binary_path="/home/jimmie/.local/bin/bandit",
                file_patterns=["*.py"],
                output_format="json",
                command_template="bandit -r {project_path} -f json -o {output_file}",
                description="Python application security scanner",
                categories=["python", "security", "sast"],
                compliance_frameworks=["OWASP"]
            ),
            "semgrep": SecurityTool(
                name="semgrep",
                binary_path="/home/jimmie/bin/semgrep",
                file_patterns=["*.py", "*.js", "*.go", "*.java", "*.tf"],
                output_format="json",
                command_template="semgrep --config=auto {project_path} --json --output {output_file}",
                description="Multi-language static analysis security scanner",
                categories=["sast", "security", "multilang"],
                compliance_frameworks=["OWASP"]
            ),
            "npm_audit": SecurityTool(
                name="npm_audit",
                binary_path="/usr/bin/npm",
                file_patterns=["package.json", "package-lock.json"],
                output_format="json",
                command_template="npm audit --json > {output_file}",
                description="Node.js dependency vulnerability scanner",
                categories=["nodejs", "dependencies", "sca"]
            )
        }

        # Secret Detection Tools
        self.tools["secrets"] = {
            "gitleaks": SecurityTool(
                name="gitleaks",
                binary_path="/home/jimmie/bin/gitleaks",
                file_patterns=["*"],
                output_format="json",
                command_template="gitleaks detect --source {project_path} --report-format json --report-path {output_file}",
                description="Git secrets and credential scanner",
                categories=["secrets", "credentials", "git"]
            ),
            "trufflehog": SecurityTool(
                name="trufflehog",
                binary_path="/home/jimmie/bin/trufflehog",
                file_patterns=["*"],
                output_format="json",
                command_template="trufflehog filesystem {project_path} --json > {output_file}",
                description="High-entropy secret detection scanner",
                categories=["secrets", "credentials", "entropy"]
            )
        }

        # GP-CONSULTING-AGENTS Integration
        self.tools["agents"] = {
            "cks_agent": SecurityTool(
                name="cks_agent",
                binary_path="/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS/agents/cks_agent.py",
                file_patterns=["*.yaml", "*.yml"],
                output_format="json",
                command_template="python3 {binary_path} --analyze {project_path} --output {output_file}",
                description="CKS-certified Kubernetes security analysis agent",
                categories=["kubernetes", "cks", "agent"],
                compliance_frameworks=["CIS", "CKS"]
            ),
            "container_agent": SecurityTool(
                name="container_agent",
                binary_path="/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS/agents/container_agent.py",
                file_patterns=["Dockerfile", "*.dockerfile", "docker-compose.yml"],
                output_format="json",
                command_template="python3 {binary_path} --scan {project_path} --output {output_file}",
                description="Container security analysis specialist agent",
                categories=["container", "docker", "agent"]
            ),
            "devsecops_agent": SecurityTool(
                name="devsecops_agent",
                binary_path="/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS/agents/devsecops_agent.py",
                file_patterns=["*"],
                output_format="json",
                command_template="python3 {binary_path} --project {project_path} --output {output_file}",
                description="DevSecOps pipeline security analysis agent",
                categories=["devsecops", "pipeline", "agent"]
            )
        }

        # Container Security Tools
        self.tools["container"] = {
            "trivy": SecurityTool(
                name="trivy",
                binary_path="/home/jimmie/bin/trivy",
                file_patterns=["Dockerfile", "*.dockerfile", "docker-compose.yml"],
                output_format="json",
                command_template="trivy fs {project_path} --format json --output {output_file}",
                description="Container and filesystem vulnerability scanner",
                categories=["container", "vulnerability", "docker"]
            ),
            "hadolint": SecurityTool(
                name="hadolint",
                binary_path="/home/jimmie/bin/hadolint",
                file_patterns=["Dockerfile", "*.dockerfile"],
                output_format="json",
                command_template="hadolint {dockerfile_path} --format json > {output_file}",
                description="Dockerfile best practices and security linter",
                categories=["container", "docker", "best-practices"]
            )
        }

    def _load_execution_patterns(self):
        """Load Jade's execution patterns for different project types"""

        self.execution_patterns = {
            "fintech_startup": {
                "priority_tools": ["checkov", "bandit", "gitleaks", "npm_audit"],
                "compliance_focus": ["SOC2", "PCI-DSS"],
                "scan_depth": "comprehensive",
                "auto_fix": False
            },
            "kubernetes_platform": {
                "priority_tools": ["kubescape", "kube_bench", "polaris", "trivy"],
                "compliance_focus": ["CIS", "NSA-CISA"],
                "scan_depth": "cks_focused",
                "auto_fix": True
            },
            "infrastructure_code": {
                "priority_tools": ["tfsec", "checkov", "terraform_validate"],
                "compliance_focus": ["CIS", "SOC2"],
                "scan_depth": "comprehensive",
                "auto_fix": False
            },
            "application_security": {
                "priority_tools": ["semgrep", "bandit", "npm_audit", "gitleaks"],
                "compliance_focus": ["OWASP"],
                "scan_depth": "comprehensive",
                "auto_fix": True
            }
        }

    def analyze_project_context(self, project_path: str) -> Dict[str, Any]:
        """Jade analyzes project to understand what tools to use"""

        project_path = Path(project_path)
        context = {
            "project_type": [],
            "detected_technologies": [],
            "recommended_tools": [],
            "file_analysis": {},
            "execution_pattern": None
        }

        # File pattern analysis
        for tech_category, tools in self.tools.items():
            for tool_name, tool in tools.items():
                for pattern in tool.file_patterns:
                    matches = list(project_path.rglob(pattern))
                    if matches:
                        context["file_analysis"][pattern] = len(matches)
                        if tech_category not in context["project_type"]:
                            context["project_type"].append(tech_category)
                        if tool_name not in context["recommended_tools"]:
                            context["recommended_tools"].append(tool_name)

        # Technology detection
        if any(project_path.rglob("*.tf")):
            context["detected_technologies"].append("terraform")
        if any(project_path.rglob("*.yaml")) or any(project_path.rglob("*.yml")):
            context["detected_technologies"].append("kubernetes")
        if any(project_path.rglob("*.py")):
            context["detected_technologies"].append("python")
        if any(project_path.rglob("package.json")):
            context["detected_technologies"].append("nodejs")
        if any(project_path.rglob("Dockerfile")):
            context["detected_technologies"].append("docker")

        # Determine execution pattern
        if "terraform" in context["detected_technologies"]:
            context["execution_pattern"] = "infrastructure_code"
        elif "kubernetes" in context["detected_technologies"]:
            context["execution_pattern"] = "kubernetes_platform"
        elif "python" in context["detected_technologies"] or "nodejs" in context["detected_technologies"]:
            context["execution_pattern"] = "application_security"
        else:
            context["execution_pattern"] = "general_security"

        return context

    def get_scan_strategy(self, project_context: Dict[str, Any], client_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """Jade determines optimal scanning strategy"""

        execution_pattern = project_context.get("execution_pattern", "general_security")
        pattern_config = self.execution_patterns.get(execution_pattern, {})

        strategy = {
            "primary_scanners": [],
            "secondary_scanners": [],
            "execution_order": [],
            "output_correlation": [],
            "compliance_mapping": [],
            "expected_runtime": "5-10 minutes"
        }

        # Primary scanners based on project type
        recommended_tools = project_context.get("recommended_tools", [])
        priority_tools = pattern_config.get("priority_tools", [])

        for tool_name in priority_tools:
            if tool_name in recommended_tools:
                strategy["primary_scanners"].append(tool_name)

        # Secondary scanners for comprehensive coverage
        all_recommended = set(recommended_tools) - set(strategy["primary_scanners"])
        strategy["secondary_scanners"] = list(all_recommended)

        # Execution order (secrets first, then tech-specific, then general)
        secrets_tools = ["gitleaks", "trufflehog"]
        strategy["execution_order"] = (
            [t for t in secrets_tools if t in strategy["primary_scanners"]] +
            [t for t in strategy["primary_scanners"] if t not in secrets_tools] +
            [t for t in strategy["secondary_scanners"]]
        )

        # Compliance mapping
        if client_requirements:
            required_frameworks = client_requirements.get("compliance", [])
            for framework in required_frameworks:
                framework_tools = self._get_tools_for_compliance(framework)
                strategy["compliance_mapping"].extend(framework_tools)

        return strategy

    def _get_tools_for_compliance(self, framework: str) -> List[str]:
        """Get tools that support specific compliance framework"""
        supporting_tools = []

        for category, tools in self.tools.items():
            for tool_name, tool in tools.items():
                if tool.compliance_frameworks and framework in tool.compliance_frameworks:
                    supporting_tools.append(tool_name)

        return supporting_tools

    def generate_jade_reasoning(self, project_context: Dict[str, Any], scan_strategy: Dict[str, Any]) -> str:
        """Generate Jade's reasoning explanation for the user"""

        reasoning = f"""🧠 **Jade's Project Analysis & Strategy**

**Project Assessment:**
• Detected technologies: {', '.join(project_context['detected_technologies'])}
• Project type: {project_context['execution_pattern'].replace('_', ' ').title()}
• Files analyzed: {sum(project_context['file_analysis'].values())} across {len(project_context['file_analysis'])} patterns

**Scanning Strategy:**
• Primary scanners: {', '.join(scan_strategy['primary_scanners'])}
• Execution order: {' → '.join(scan_strategy['execution_order'][:3])}{'...' if len(scan_strategy['execution_order']) > 3 else ''}
• Expected runtime: {scan_strategy['expected_runtime']}

**Reasoning:**
I'll start with secret detection to catch credentials early, then run technology-specific scanners for deep analysis, followed by cross-cutting security tools for comprehensive coverage.

The results will be correlated across tools and mapped to relevant compliance frameworks for actionable insights."""

        return reasoning

    def get_tool_by_name(self, tool_name: str) -> Optional[SecurityTool]:
        """Get tool definition by name"""
        for category, tools in self.tools.items():
            if tool_name in tools:
                return tools[tool_name]
        return None

    def get_available_tools(self) -> Dict[str, List[str]]:
        """Get all available tools by category"""
        return {category: list(tools.keys()) for category, tools in self.tools.items()}

    def validate_tool_availability(self) -> Dict[str, bool]:
        """Check which tools are actually available on the system"""
        availability = {}

        for category, tools in self.tools.items():
            for tool_name, tool in tools.items():
                binary_exists = os.path.exists(tool.binary_path) or os.path.isfile(tool.binary_path)
                availability[tool_name] = binary_exists

        return availability

# Global tool registry instance
jade_tool_registry = JadeToolRegistry()

if __name__ == "__main__":
    # Test the tool registry
    print("🔧 Testing Jade Tool Registry...")

    # Test project analysis
    test_project = "/home/jimmie/linkops-industries/GP-copilot"
    context = jade_tool_registry.analyze_project_context(test_project)
    print(f"\n📊 Project Context: {context}")

    # Test scan strategy
    strategy = jade_tool_registry.get_scan_strategy(context)
    print(f"\n🎯 Scan Strategy: {strategy}")

    # Test Jade reasoning
    reasoning = jade_tool_registry.generate_jade_reasoning(context, strategy)
    print(f"\n{reasoning}")

    # Test tool availability
    availability = jade_tool_registry.validate_tool_availability()
    available_tools = [tool for tool, available in availability.items() if available]
    print(f"\n✅ Available Tools: {available_tools}")