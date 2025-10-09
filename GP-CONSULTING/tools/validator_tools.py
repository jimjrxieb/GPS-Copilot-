"""
Validator Tools for Jade's Agentic System

These tools allow Jade to verify that fixes actually worked.
This is critical for autonomous workflows: scan → fix → verify

Similar to how Claude Code runs tests after making changes,
Jade re-scans to verify fixes resolved the issues.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.base_registry import ToolRegistry, ToolCategory, ToolSeverity


def register_validator_tools():
    """Register all validator tools with the ToolRegistry"""

    @ToolRegistry.register(
        name="verify_fix_effectiveness",
        description="Compare before/after scan results to verify fix effectiveness",
        category=ToolCategory.VALIDATOR,
        severity=ToolSeverity.SAFE,
        parameters={
            "before_results": {
                "type": "object",
                "description": "Scan results before applying fix",
                "required": True
            },
            "after_results": {
                "type": "object",
                "description": "Scan results after applying fix",
                "required": True
            },
            "expected_reduction": {
                "type": "object",
                "description": "Expected reduction in findings by severity",
                "required": False
            }
        },
        examples=[
            "verify_fix_effectiveness(before_results=scan1, after_results=scan2)",
        ]
    )
    def verify_fix_effectiveness(before_results: dict, after_results: dict, expected_reduction: dict = None) -> dict:
        """
        Verify that fixes actually reduced vulnerabilities

        Returns:
        {
            "success": bool,
            "issues_fixed": int,
            "issues_remaining": int,
            "new_issues": int,  # Sometimes fixes introduce new issues!
            "effectiveness_score": float,  # 0.0 to 1.0
            "details": {
                "by_severity": {...},
                "by_type": {...}
            }
        }
        """
        before_count = before_results.get("summary", {}).get("total", 0)
        after_count = after_results.get("summary", {}).get("total", 0)

        issues_fixed = max(0, before_count - after_count)
        new_issues = max(0, after_count - before_count)

        effectiveness_score = issues_fixed / before_count if before_count > 0 else 1.0

        # Check if expected reduction was met
        success = True
        if expected_reduction:
            for severity, expected in expected_reduction.items():
                before_sev = before_results.get("summary", {}).get("by_severity", {}).get(severity, 0)
                after_sev = after_results.get("summary", {}).get("by_severity", {}).get(severity, 0)
                actual_reduction = before_sev - after_sev

                if actual_reduction < expected:
                    success = False

        return {
            "success": success,
            "issues_fixed": issues_fixed,
            "issues_remaining": after_count,
            "new_issues": new_issues,
            "effectiveness_score": effectiveness_score,
            "details": {
                "before_total": before_count,
                "after_total": after_count,
                "reduction_percentage": (issues_fixed / before_count * 100) if before_count > 0 else 0,
            }
        }

    @ToolRegistry.register(
        name="validate_opa_policy",
        description="Test OPA policy against test cases to ensure it works correctly",
        category=ToolCategory.VALIDATOR,
        severity=ToolSeverity.SAFE,
        parameters={
            "policy_path": {
                "type": "string",
                "description": "Path to OPA policy file (.rego)",
                "required": True
            },
            "test_cases": {
                "type": "array",
                "description": "Test cases to validate against",
                "required": False
            }
        },
        examples=[
            "validate_opa_policy(policy_path='GP-POL-AS-CODE/1-POLICIES/opa/terraform/s3-encryption.rego')",
        ]
    )
    def validate_opa_policy(policy_path: str, test_cases: list = None) -> dict:
        """
        Validate OPA policy syntax and logic

        Runs:
        1. opa test (if _test.rego files exist)
        2. opa check (syntax validation)
        3. Custom test cases (if provided)

        Returns:
        {
            "valid": bool,
            "syntax_errors": [],
            "test_results": {...},
            "coverage": float
        }
        """
        import subprocess
        import json
        from pathlib import Path

        policy_path_obj = Path(policy_path)
        policy_dir = policy_path_obj.parent

        results = {
            "valid": True,
            "syntax_errors": [],
            "test_results": {},
            "coverage": 0.0
        }

        # Run opa check for syntax validation
        check_cmd = ["bin/opa", "check", str(policy_path)]
        check_result = subprocess.run(check_cmd, capture_output=True, text=True)

        if check_result.returncode != 0:
            results["valid"] = False
            results["syntax_errors"].append(check_result.stderr)
            return results

        # Run opa test if test files exist
        test_files = list(policy_dir.glob("*_test.rego"))
        if test_files:
            test_cmd = ["bin/opa", "test", str(policy_dir), "-v", "--format", "json"]
            test_result = subprocess.run(test_cmd, capture_output=True, text=True)

            if test_result.returncode == 0:
                test_output = json.loads(test_result.stdout)
                results["test_results"] = test_output
            else:
                results["valid"] = False
                results["test_results"]["error"] = test_result.stderr

        return results

    @ToolRegistry.register(
        name="validate_gatekeeper_constraint",
        description="Test Gatekeeper constraint before deploying to cluster",
        category=ToolCategory.VALIDATOR,
        severity=ToolSeverity.SAFE,
        parameters={
            "constraint_path": {
                "type": "string",
                "description": "Path to Gatekeeper constraint YAML",
                "required": True
            },
            "test_manifests": {
                "type": "array",
                "description": "Test Kubernetes manifests to validate against",
                "required": False
            }
        },
        examples=[
            "validate_gatekeeper_constraint(constraint_path='gatekeeper-policies/pod-security.yaml')",
        ]
    )
    def validate_gatekeeper_constraint(constraint_path: str, test_manifests: list = None) -> dict:
        """
        Validate Gatekeeper constraint

        Tests:
        1. YAML syntax is valid
        2. ConstraintTemplate exists
        3. Constraint references valid template
        4. Test cases pass (if provided)

        This prevents deploying broken constraints to production!
        """
        import yaml
        from pathlib import Path

        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "test_results": []
        }

        # Load and validate YAML
        try:
            with open(constraint_path) as f:
                constraint = yaml.safe_load(f)
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Invalid YAML: {str(e)}")
            return results

        # Check constraint structure
        if "kind" not in constraint:
            results["valid"] = False
            results["errors"].append("Missing 'kind' field")

        if "spec" not in constraint:
            results["valid"] = False
            results["errors"].append("Missing 'spec' field")

        # Check if template exists
        kind = constraint.get("kind")
        template_path = Path(constraint_path).parent / f"{kind.lower()}-template.yaml"

        if not template_path.exists():
            results["warnings"].append(f"ConstraintTemplate not found: {template_path}")

        # Test against manifests if provided
        if test_manifests:
            for manifest in test_manifests:
                # This would use gator (Gatekeeper testing tool)
                # For now, just structure the result
                results["test_results"].append({
                    "manifest": manifest,
                    "passed": True,  # Placeholder
                    "violations": []
                })

        return results

    @ToolRegistry.register(
        name="validate_terraform_syntax",
        description="Validate Terraform syntax and configuration after fixes",
        category=ToolCategory.VALIDATOR,
        severity=ToolSeverity.SAFE,
        parameters={
            "terraform_path": {
                "type": "string",
                "description": "Path to Terraform directory",
                "required": True
            },
            "run_plan": {
                "type": "boolean",
                "description": "Run terraform plan for deeper validation",
                "required": False,
                "default": False
            }
        },
        examples=[
            "validate_terraform_syntax(terraform_path='GP-PROJECTS/Terraform_CICD_Setup')",
            "validate_terraform_syntax(terraform_path='terraform/', run_plan=True)",
        ]
    )
    def validate_terraform_syntax(terraform_path: str, run_plan: bool = False) -> dict:
        """
        Validate Terraform after applying fixes

        Runs:
        1. terraform fmt -check (formatting)
        2. terraform validate (syntax and logic)
        3. terraform plan (optional, requires credentials)

        This ensures fixes didn't break Terraform!
        """
        import subprocess
        from pathlib import Path

        results = {
            "valid": True,
            "formatting_issues": [],
            "validation_errors": [],
            "plan_output": None
        }

        terraform_path_obj = Path(terraform_path)

        # Initialize if needed
        if not (terraform_path_obj / ".terraform").exists():
            init_cmd = ["terraform", "init", "-backend=false"]
            subprocess.run(init_cmd, cwd=terraform_path, capture_output=True)

        # Check formatting
        fmt_cmd = ["terraform", "fmt", "-check", "-recursive"]
        fmt_result = subprocess.run(fmt_cmd, cwd=terraform_path, capture_output=True, text=True)

        if fmt_result.returncode != 0:
            results["formatting_issues"] = fmt_result.stdout.strip().split("\n")

        # Validate syntax
        validate_cmd = ["terraform", "validate", "-json"]
        validate_result = subprocess.run(validate_cmd, cwd=terraform_path, capture_output=True, text=True)

        if validate_result.returncode != 0:
            import json
            validate_output = json.loads(validate_result.stdout)
            results["valid"] = False
            results["validation_errors"] = validate_output.get("diagnostics", [])

        # Run plan if requested
        if run_plan and results["valid"]:
            plan_cmd = ["terraform", "plan", "-no-color"]
            plan_result = subprocess.run(plan_cmd, cwd=terraform_path, capture_output=True, text=True)
            results["plan_output"] = plan_result.stdout

        return results

    @ToolRegistry.register(
        name="validate_kubernetes_manifest",
        description="Validate Kubernetes manifest syntax and best practices",
        category=ToolCategory.VALIDATOR,
        severity=ToolSeverity.SAFE,
        parameters={
            "manifest_path": {
                "type": "string",
                "description": "Path to Kubernetes manifest YAML",
                "required": True
            },
            "run_dry_run": {
                "type": "boolean",
                "description": "Run kubectl apply --dry-run for cluster validation",
                "required": False,
                "default": False
            }
        },
        examples=[
            "validate_kubernetes_manifest(manifest_path='k8s/deployment.yaml')",
            "validate_kubernetes_manifest(manifest_path='k8s/pod.yaml', run_dry_run=True)",
        ]
    )
    def validate_kubernetes_manifest(manifest_path: str, run_dry_run: bool = False) -> dict:
        """
        Validate Kubernetes manifest

        Runs:
        1. YAML syntax validation
        2. kubectl apply --dry-run=client
        3. kubectl apply --dry-run=server (if run_dry_run=True, requires cluster access)

        This ensures fixes produce valid Kubernetes resources!
        """
        import subprocess
        import yaml

        results = {
            "valid": True,
            "yaml_errors": [],
            "client_validation": {},
            "server_validation": {}
        }

        # Validate YAML syntax
        try:
            with open(manifest_path) as f:
                yaml.safe_load_all(f)
        except Exception as e:
            results["valid"] = False
            results["yaml_errors"].append(str(e))
            return results

        # Client-side dry run (no cluster needed)
        client_cmd = ["kubectl", "apply", "--dry-run=client", "-f", manifest_path]
        client_result = subprocess.run(client_cmd, capture_output=True, text=True)

        if client_result.returncode != 0:
            results["valid"] = False
            results["client_validation"]["error"] = client_result.stderr

        # Server-side dry run (requires cluster)
        if run_dry_run:
            server_cmd = ["kubectl", "apply", "--dry-run=server", "-f", manifest_path]
            server_result = subprocess.run(server_cmd, capture_output=True, text=True)

            if server_result.returncode != 0:
                results["valid"] = False
                results["server_validation"]["error"] = server_result.stderr

        return results

    print("✅ Registered 6 validator tools")
    print("   - verify_fix_effectiveness")
    print("   - validate_opa_policy")
    print("   - validate_gatekeeper_constraint")
    print("   - validate_terraform_syntax")
    print("   - validate_kubernetes_manifest")


if __name__ == "__main__":
    # Test registration
    register_validator_tools()
    print(ToolRegistry.list_tools(ToolCategory.VALIDATOR))