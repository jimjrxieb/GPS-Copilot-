"""
Fixer Tools for Jade's Agentic System

These tools wrap our existing fixers and make them available to Jade's
AI decision-making engine for autonomous remediation.

Similar to how Claude Code can Edit files, Jade can Fix vulnerabilities.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.base_registry import ToolRegistry, ToolCategory, ToolSeverity
from fixers import (
    bandit_fixer,
    trivy_fixer,
    gitleaks_fixer,
    terraform_fixer,
    kubernetes_fixer,
)


def register_fixer_tools():
    """Register all fixer tools with the ToolRegistry"""

    @ToolRegistry.register(
        name="fix_python_bandit",
        description="Automatically fix Python security issues found by Bandit",
        category=ToolCategory.FIXER,
        severity=ToolSeverity.MEDIUM,
        parameters={
            "scan_results": {
                "type": "object",
                "description": "Bandit scan results JSON",
                "required": True
            },
            "auto_apply": {
                "type": "boolean",
                "description": "Automatically apply fixes without confirmation",
                "required": False,
                "default": False
            },
            "severity_threshold": {
                "type": "string",
                "description": "Only fix issues at or above this severity (LOW, MEDIUM, HIGH)",
                "required": False,
                "default": "MEDIUM"
            }
        },
        examples=[
            "fix_python_bandit(scan_results=bandit_results, auto_apply=False)",
            "fix_python_bandit(scan_results=bandit_results, severity_threshold='HIGH')",
        ]
    )
    def fix_python_bandit(scan_results: dict, auto_apply: bool = False, severity_threshold: str = "MEDIUM") -> dict:
        """
        Fix Python security issues

        Bandit fixer can fix:
        - Hardcoded passwords → Environment variables
        - Insecure random → secrets.SystemRandom()
        - SQL injection → Parameterized queries
        - Eval usage → ast.literal_eval()
        - Pickle usage → json/safer alternatives

        Returns:
        {
            "fixed": int,
            "skipped": int,
            "details": [...],
            "files_modified": [...]
        }
        """
        return bandit_fixer.apply_fixes(scan_results, auto_apply, severity_threshold)

    @ToolRegistry.register(
        name="fix_dependencies_trivy",
        description="Fix dependency vulnerabilities by upgrading to patched versions",
        category=ToolCategory.FIXER,
        severity=ToolSeverity.HIGH,  # Modifying dependencies is HIGH risk
        parameters={
            "scan_results": {
                "type": "object",
                "description": "Trivy scan results JSON",
                "required": True
            },
            "auto_upgrade": {
                "type": "boolean",
                "description": "Automatically upgrade vulnerable dependencies",
                "required": False,
                "default": False
            },
            "package_manager": {
                "type": "string",
                "description": "Package manager: pip, npm, go, maven",
                "required": False,
                "default": "auto"
            }
        },
        examples=[
            "fix_dependencies_trivy(scan_results=trivy_results, auto_upgrade=False)",
            "fix_dependencies_trivy(scan_results=trivy_results, package_manager='pip')",
        ]
    )
    def fix_dependencies_trivy(scan_results: dict, auto_upgrade: bool = False, package_manager: str = "auto") -> dict:
        """
        Fix dependency vulnerabilities

        Trivy fixer can:
        - Upgrade vulnerable packages to patched versions
        - Pin versions to avoid breaking changes
        - Update lock files (requirements.txt, package-lock.json, go.sum)
        - Generate upgrade report with risk analysis

        ⚠️ HIGH SEVERITY: Requires approval before applying
        """
        return trivy_fixer.upgrade_dependencies(scan_results, auto_upgrade, package_manager)

    @ToolRegistry.register(
        name="fix_secrets_gitleaks",
        description="Remediate hardcoded secrets found by Gitleaks",
        category=ToolCategory.FIXER,
        severity=ToolSeverity.CRITICAL,  # Touching secrets is CRITICAL
        parameters={
            "scan_results": {
                "type": "object",
                "description": "Gitleaks scan results JSON",
                "required": True
            },
            "remediation_strategy": {
                "type": "string",
                "description": "Strategy: env_vars, vault, secrets_manager, remove",
                "required": False,
                "default": "env_vars"
            },
            "rotate_secrets": {
                "type": "boolean",
                "description": "Rotate exposed secrets (requires cloud credentials)",
                "required": False,
                "default": False
            }
        },
        examples=[
            "fix_secrets_gitleaks(scan_results=gitleaks_results, remediation_strategy='env_vars')",
            "fix_secrets_gitleaks(scan_results=gitleaks_results, rotate_secrets=True)",
        ]
    )
    def fix_secrets_gitleaks(scan_results: dict, remediation_strategy: str = "env_vars", rotate_secrets: bool = False) -> dict:
        """
        Remediate hardcoded secrets

        Gitleaks fixer can:
        1. Replace hardcoded secrets with environment variables
        2. Move secrets to HashiCorp Vault
        3. Move secrets to AWS Secrets Manager
        4. Remove secrets from code and git history
        5. Rotate exposed secrets (AWS, GitHub, etc.)

        ⚠️ CRITICAL SEVERITY: Requires explicit approval
        This tool modifies secrets and git history!
        """
        return gitleaks_fixer.remediate_secrets(scan_results, remediation_strategy, rotate_secrets)

    @ToolRegistry.register(
        name="fix_terraform_issues",
        description="Fix Terraform security and compliance issues",
        category=ToolCategory.FIXER,
        severity=ToolSeverity.HIGH,
        parameters={
            "scan_results": {
                "type": "object",
                "description": "Terraform scan results (from OPA, Checkov, or tfsec)",
                "required": True
            },
            "issue_types": {
                "type": "array",
                "description": "Types of issues to fix: encryption, access_control, logging, compliance",
                "required": False,
                "default": ["encryption", "logging"]
            }
        },
        examples=[
            "fix_terraform_issues(scan_results=opa_results)",
            "fix_terraform_issues(scan_results=checkov_results, issue_types=['encryption', 'access_control'])",
        ]
    )
    def fix_terraform_issues(scan_results: dict, issue_types: list = None) -> dict:
        """
        Fix Terraform security issues

        Terraform fixer can fix:
        - Unencrypted resources → Add encryption blocks
        - Public S3 buckets → Add bucket policies
        - Missing logging → Add CloudWatch/CloudTrail
        - Open security groups → Restrict to specific IPs
        - Missing tags → Add compliance tags
        - IAM overpermissions → Apply least privilege

        ⚠️ HIGH SEVERITY: Requires approval before applying
        """
        if issue_types is None:
            issue_types = ["encryption", "logging"]

        return terraform_fixer.apply_fixes(scan_results, issue_types)

    @ToolRegistry.register(
        name="fix_kubernetes_issues",
        description="Fix Kubernetes security and compliance issues",
        category=ToolCategory.FIXER,
        severity=ToolSeverity.HIGH,
        parameters={
            "scan_results": {
                "type": "object",
                "description": "Kubernetes scan results (from OPA, Gatekeeper, or Polaris)",
                "required": True
            },
            "issue_types": {
                "type": "array",
                "description": "Types of issues to fix: pod_security, rbac, network_policy, resource_limits",
                "required": False,
                "default": ["pod_security", "resource_limits"]
            }
        },
        examples=[
            "fix_kubernetes_issues(scan_results=gatekeeper_results)",
            "fix_kubernetes_issues(scan_results=polaris_results, issue_types=['pod_security', 'rbac'])",
        ]
    )
    def fix_kubernetes_issues(scan_results: dict, issue_types: list = None) -> dict:
        """
        Fix Kubernetes security issues

        Kubernetes fixer can fix:
        - Privileged containers → Add security context
        - Missing resource limits → Add requests/limits
        - No network policies → Generate NetworkPolicy
        - Overpermissive RBAC → Apply least privilege
        - Missing pod security standards → Add pod security policies
        - Root containers → Set runAsNonRoot

        ⚠️ HIGH SEVERITY: Requires approval before applying
        """
        if issue_types is None:
            issue_types = ["pod_security", "resource_limits"]

        return kubernetes_fixer.apply_fixes(scan_results, issue_types)

    @ToolRegistry.register(
        name="generate_opa_policy",
        description="Generate OPA policy to prevent specific security violations",
        category=ToolCategory.FIXER,
        severity=ToolSeverity.MEDIUM,
        parameters={
            "violation_pattern": {
                "type": "object",
                "description": "Pattern of violation to prevent (from scan results)",
                "required": True
            },
            "policy_name": {
                "type": "string",
                "description": "Name for the generated policy",
                "required": True
            },
            "policy_type": {
                "type": "string",
                "description": "Type: terraform, kubernetes, cicd",
                "required": True
            }
        },
        examples=[
            "generate_opa_policy(violation_pattern=pattern, policy_name='prevent-public-s3', policy_type='terraform')",
        ]
    )
    def generate_opa_policy(violation_pattern: dict, policy_name: str, policy_type: str) -> dict:
        """
        Generate OPA policy from violation pattern

        This is Jade's "learning" capability:
        1. Scan finds violation
        2. Human fixes it
        3. Jade generates policy to prevent it in future
        4. Policy added to GuidePoint standards

        This is how Jade gets smarter over time.
        """
        from fixers import opa_fixer
        return opa_fixer.generate_policy(violation_pattern, policy_name, policy_type)

    print("✅ Registered 7 fixer tools")
    print("   - fix_python_bandit (MEDIUM severity)")
    print("   - fix_dependencies_trivy (HIGH severity)")
    print("   - fix_secrets_gitleaks (CRITICAL severity)")
    print("   - fix_terraform_issues (HIGH severity)")
    print("   - fix_kubernetes_issues (HIGH severity)")
    print("   - generate_opa_policy (MEDIUM severity)")


if __name__ == "__main__":
    # Test registration
    register_fixer_tools()
    print(ToolRegistry.list_tools(ToolCategory.FIXER))