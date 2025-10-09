"""
Scanner Tools for Jade's Agentic System

These tools wrap our existing scanners (Bandit, Trivy, OPA, etc.) and make
them available to Jade's AI decision-making engine.

Similar to how Claude Code can Read files, Jade can Scan projects.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.base_registry import ToolRegistry, ToolCategory, ToolSeverity
from scanners import (
    bandit_scanner,
    trivy_scanner,
    gitleaks_scanner,
    semgrep_scanner,
    checkov_scanner,
)


def register_scanner_tools():
    """Register all scanner tools with the ToolRegistry"""

    @ToolRegistry.register(
        name="scan_python_bandit",
        description="Scan Python code for security vulnerabilities using Bandit (SAST)",
        category=ToolCategory.SCANNER,
        severity=ToolSeverity.SAFE,
        parameters={
            "target_path": {
                "type": "string",
                "description": "Path to Python project or file to scan",
                "required": True
            },
            "output_format": {
                "type": "string",
                "description": "Output format (json or text)",
                "required": False,
                "default": "json"
            }
        },
        examples=[
            "scan_python_bandit(target_path='/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/DVWA')",
            "scan_python_bandit(target_path='GP-AI/', output_format='json')",
        ]
    )
    def scan_python_bandit(target_path: str, output_format: str = "json") -> dict:
        """
        Scan Python code with Bandit

        Returns:
        {
            "findings": [...],
            "summary": {"total": int, "by_severity": {...}},
            "tool": "bandit",
            "target": str,
            "timestamp": str
        }
        """
        return bandit_scanner.scan_directory(target_path, output_format)

    @ToolRegistry.register(
        name="scan_dependencies_trivy",
        description="Scan for vulnerabilities in dependencies, containers, and IaC using Trivy",
        category=ToolCategory.SCANNER,
        severity=ToolSeverity.SAFE,
        parameters={
            "target_path": {
                "type": "string",
                "description": "Path to scan (supports package files, Dockerfiles, Terraform)",
                "required": True
            },
            "scan_type": {
                "type": "string",
                "description": "Type of scan: fs (filesystem), config, image",
                "required": False,
                "default": "fs"
            }
        },
        examples=[
            "scan_dependencies_trivy(target_path='GP-PROJECTS/DVWA')",
            "scan_dependencies_trivy(target_path='Dockerfile', scan_type='config')",
        ]
    )
    def scan_dependencies_trivy(target_path: str, scan_type: str = "fs") -> dict:
        """
        Scan with Trivy for dependency vulnerabilities

        Trivy can scan:
        - Package files (requirements.txt, package.json, go.mod, etc.)
        - Dockerfiles and container images
        - IaC files (Terraform, CloudFormation, Kubernetes)
        """
        return trivy_scanner.scan_target(target_path, scan_type)

    @ToolRegistry.register(
        name="scan_secrets_gitleaks",
        description="Scan for hardcoded secrets, API keys, passwords using Gitleaks",
        category=ToolCategory.SCANNER,
        severity=ToolSeverity.SAFE,
        parameters={
            "target_path": {
                "type": "string",
                "description": "Path to scan for secrets",
                "required": True
            },
            "scan_mode": {
                "type": "string",
                "description": "Mode: detect (full scan) or protect (pre-commit)",
                "required": False,
                "default": "detect"
            }
        },
        examples=[
            "scan_secrets_gitleaks(target_path='GP-PROJECTS/DVWA')",
            "scan_secrets_gitleaks(target_path='.', scan_mode='protect')",
        ]
    )
    def scan_secrets_gitleaks(target_path: str, scan_mode: str = "detect") -> dict:
        """
        Scan for secrets with Gitleaks

        Detects:
        - API keys (AWS, GCP, Azure, GitHub, etc.)
        - Passwords and connection strings
        - Private keys and certificates
        - Generic secrets (high entropy strings)
        """
        return gitleaks_scanner.scan_path(target_path, mode=scan_mode)

    @ToolRegistry.register(
        name="scan_code_semgrep",
        description="Scan code for security patterns and vulnerabilities using Semgrep (SAST)",
        category=ToolCategory.SCANNER,
        severity=ToolSeverity.SAFE,
        parameters={
            "target_path": {
                "type": "string",
                "description": "Path to scan",
                "required": True
            },
            "rules": {
                "type": "string",
                "description": "Rule set to use (auto, p/security-audit, p/owasp-top-10)",
                "required": False,
                "default": "auto"
            }
        },
        examples=[
            "scan_code_semgrep(target_path='GP-PROJECTS/DVWA')",
            "scan_code_semgrep(target_path='GP-AI/', rules='p/security-audit')",
        ]
    )
    def scan_code_semgrep(target_path: str, rules: str = "auto") -> dict:
        """
        Scan code with Semgrep

        Semgrep is language-agnostic and supports:
        - Python, JavaScript, Go, Java, C, etc.
        - Security patterns (SQL injection, XSS, etc.)
        - OWASP Top 10 patterns
        - Custom rules
        """
        return semgrep_scanner.scan_path(target_path, rules)

    @ToolRegistry.register(
        name="scan_iac_checkov",
        description="Scan Infrastructure as Code (Terraform, CloudFormation, Kubernetes) with Checkov",
        category=ToolCategory.SCANNER,
        severity=ToolSeverity.SAFE,
        parameters={
            "target_path": {
                "type": "string",
                "description": "Path to IaC files",
                "required": True
            },
            "framework": {
                "type": "string",
                "description": "Framework: terraform, cloudformation, kubernetes, all",
                "required": False,
                "default": "all"
            }
        },
        examples=[
            "scan_iac_checkov(target_path='GP-PROJECTS/Terraform_CICD_Setup')",
            "scan_iac_checkov(target_path='k8s/', framework='kubernetes')",
        ]
    )
    def scan_iac_checkov(target_path: str, framework: str = "all") -> dict:
        """
        Scan IaC with Checkov

        Checkov checks for:
        - Misconfigurations (public S3 buckets, open security groups)
        - Compliance violations (CIS, PCI-DSS, HIPAA)
        - Best practices (encryption, logging, monitoring)
        """
        return checkov_scanner.scan_iac(target_path, framework)

    # OPA scanner - special case, needs custom implementation
    @ToolRegistry.register(
        name="scan_iac_opa",
        description="Scan Infrastructure as Code against OPA policies (GuidePoint standards)",
        category=ToolCategory.SCANNER,
        severity=ToolSeverity.SAFE,
        parameters={
            "target_path": {
                "type": "string",
                "description": "Path to Terraform or Kubernetes files",
                "required": True
            },
            "policy_bundle": {
                "type": "string",
                "description": "Policy bundle: terraform-security, kubernetes-security, all",
                "required": False,
                "default": "all"
            }
        },
        examples=[
            "scan_iac_opa(target_path='GP-PROJECTS/Terraform_CICD_Setup')",
            "scan_iac_opa(target_path='k8s/', policy_bundle='kubernetes-security')",
        ]
    )
    def scan_iac_opa(target_path: str, policy_bundle: str = "all") -> dict:
        """
        Scan IaC with OPA policies

        This enforces GuidePoint's custom security standards:
        - Terraform security policies
        - Kubernetes security policies
        - Compliance policies (SOC2, ISO27001)
        """
        # Import here to avoid circular dependency
        import sys
        import subprocess
        from pathlib import Path

        opa_policies_path = Path(__file__).parent.parent / "GP-POL-AS-CODE/1-POLICIES/opa"

        if policy_bundle == "terraform-security":
            policy_path = opa_policies_path / "terraform"
        elif policy_bundle == "kubernetes-security":
            policy_path = opa_policies_path / "kubernetes"
        else:
            policy_path = opa_policies_path

        # Run OPA eval
        cmd = [
            "bin/opa", "eval",
            "--data", str(policy_path),
            "--input", target_path,
            "--format", "json",
            "data"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        else:
            return {
                "error": result.stderr,
                "tool": "opa",
                "target": target_path
            }

    print("✅ Registered 7 scanner tools")
    print("   - scan_python_bandit")
    print("   - scan_dependencies_trivy")
    print("   - scan_secrets_gitleaks")
    print("   - scan_code_semgrep")
    print("   - scan_iac_checkov")
    print("   - scan_iac_opa")


if __name__ == "__main__":
    # Test registration
    register_scanner_tools()
    print(ToolRegistry.list_tools(ToolCategory.SCANNER))