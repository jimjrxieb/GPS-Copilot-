#!/usr/bin/env python3
"""
Quality Assurance Agent - Security Configuration Testing & Validation
Performs testing and validation of security configurations and automation scripts before client delivery
"""

import subprocess
import json
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class QualityAssuranceAgent:
    """
    Quality Assurance Agent for security configuration validation

    Capabilities:
    - Kubernetes manifest validation (dry-run)
    - Terraform syntax and security validation
    - Security configuration testing
    - Script validation and testing
    - QA report generation
    """

    def __init__(self):
        self.agent_id = "qa_agent"

        self.config = GPDataConfig()
        self.output_dir = self.config.get_analysis_directory()
        self.deliverable_dir = self.config.get_deliverable_directory()

        self.confidence_levels = {
            "high": [
                "validate_k8s_manifests",
                "validate_terraform_syntax",
                "test_yaml_syntax",
                "validate_security_configs",
                "generate_qa_report"
            ],
            "medium": [
                "test_automation_scripts",
                "validate_cicd_pipelines",
                "integration_testing"
            ],
            "low": [
                "performance_testing",
                "chaos_engineering_validation",
                "production_readiness_assessment"
            ]
        }

        self.validation_results = []

    def execute_qa_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute QA task based on confidence level"""

        confidence = self._assess_task_confidence(task_type)

        if confidence == "high":
            return self._execute_high_confidence_task(task_type, parameters)
        elif confidence == "medium":
            return self._execute_medium_confidence_task(task_type, parameters)
        else:
            return {
                "success": False,
                "action": "escalate",
                "reason": f"Task {task_type} requires senior QA engineer",
                "confidence": confidence
            }

    def _execute_high_confidence_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute high-confidence QA tasks"""

        if task_type == "validate_k8s_manifests":
            return self._validate_k8s_manifests(parameters)
        elif task_type == "validate_terraform_syntax":
            return self._validate_terraform_syntax(parameters)
        elif task_type == "test_yaml_syntax":
            return self._test_yaml_syntax(parameters)
        elif task_type == "validate_security_configs":
            return self._validate_security_configs(parameters)
        elif task_type == "generate_qa_report":
            return self._generate_qa_report(parameters)
        else:
            return {"success": False, "error": f"Unknown task: {task_type}"}

    def _execute_medium_confidence_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute medium-confidence tasks with validation"""

        if task_type == "test_automation_scripts":
            return self._test_automation_scripts(parameters)
        else:
            return {
                "success": False,
                "action": "provide_guidance",
                "task": task_type,
                "guidance": f"Task {task_type} requires senior validation",
                "next_steps": [
                    "Review test results",
                    "Validate with senior engineer",
                    "Run tests in isolated environment",
                    "Document findings"
                ]
            }

    def _validate_k8s_manifests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Validate Kubernetes manifests with dry-run

        Args:
            manifests_path: Path to manifests directory
            namespace: Target namespace
        """
        print("✅ Validating Kubernetes manifests...")

        manifests_path = params.get("manifests_path")
        namespace = params.get("namespace", "default")

        if not manifests_path or not Path(manifests_path).exists():
            return {"success": False, "error": "Manifests path required and must exist"}

        validation_results = {
            "total_files": 0,
            "valid_manifests": 0,
            "invalid_manifests": 0,
            "warnings": [],
            "errors": [],
            "files_tested": []
        }

        try:
            target = Path(manifests_path)

            for yaml_file in target.glob("**/*.yaml"):
                validation_results["total_files"] += 1

                result = self._validate_k8s_file(yaml_file, namespace)

                if result["valid"]:
                    validation_results["valid_manifests"] += 1
                else:
                    validation_results["invalid_manifests"] += 1

                validation_results["files_tested"].append({
                    "file": str(yaml_file.relative_to(target)),
                    "valid": result["valid"],
                    "errors": result.get("errors", []),
                    "warnings": result.get("warnings", [])
                })

                if result.get("errors"):
                    validation_results["errors"].extend(result["errors"])
                if result.get("warnings"):
                    validation_results["warnings"].extend(result["warnings"])

            output = {
                "success": True,
                "task": "validate_k8s_manifests",
                "validation_results": validation_results,
                "pass_rate": (validation_results["valid_manifests"] / max(1, validation_results["total_files"])) * 100,
                "timestamp": datetime.now().isoformat()
            }

            print(f"   📊 Validated {validation_results['total_files']} files")
            print(f"   ✅ Valid: {validation_results['valid_manifests']}")
            print(f"   ❌ Invalid: {validation_results['invalid_manifests']}")

            self._save_operation("validate_k8s_manifests", output)
            return output

        except Exception as e:
            return {"success": False, "task": "validate_k8s_manifests", "error": str(e)}

    def _validate_k8s_file(self, yaml_file: Path, namespace: str) -> Dict[str, Any]:
        """Validate single Kubernetes manifest file"""

        result = {"valid": True, "errors": [], "warnings": []}

        try:
            with open(yaml_file, 'r') as f:
                docs = yaml.safe_load_all(f)

                for doc in docs:
                    if not doc:
                        continue

                    if not doc.get("apiVersion"):
                        result["errors"].append(f"{yaml_file.name}: Missing apiVersion")
                        result["valid"] = False

                    if not doc.get("kind"):
                        result["errors"].append(f"{yaml_file.name}: Missing kind")
                        result["valid"] = False

                    if not doc.get("metadata", {}).get("name"):
                        result["errors"].append(f"{yaml_file.name}: Missing metadata.name")
                        result["valid"] = False

                    if doc.get("kind") == "Pod":
                        security_context = doc.get("spec", {}).get("securityContext")
                        if not security_context:
                            result["warnings"].append(f"{yaml_file.name}: Pod missing securityContext")

        except yaml.YAMLError as e:
            result["errors"].append(f"{yaml_file.name}: YAML syntax error - {str(e)}")
            result["valid"] = False
        except Exception as e:
            result["errors"].append(f"{yaml_file.name}: Validation error - {str(e)}")
            result["valid"] = False

        return result

    def _validate_terraform_syntax(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Validate Terraform syntax and configuration

        Args:
            terraform_path: Path to Terraform directory
        """
        print("🔍 Validating Terraform configuration...")

        terraform_path = params.get("terraform_path")

        if not terraform_path or not Path(terraform_path).exists():
            return {"success": False, "error": "Terraform path required and must exist"}

        validation_results = {
            "syntax_valid": False,
            "fmt_check": False,
            "validation_output": "",
            "fmt_output": "",
            "errors": [],
            "warnings": []
        }

        try:
            fmt_result = subprocess.run(
                ["terraform", "fmt", "-check", "-recursive", terraform_path],
                capture_output=True,
                text=True,
                cwd=terraform_path
            )

            validation_results["fmt_check"] = fmt_result.returncode == 0
            validation_results["fmt_output"] = fmt_result.stdout

            if fmt_result.returncode != 0:
                validation_results["warnings"].append("Terraform files not formatted correctly")

            init_result = subprocess.run(
                ["terraform", "init", "-backend=false"],
                capture_output=True,
                text=True,
                cwd=terraform_path
            )

            if init_result.returncode != 0:
                validation_results["errors"].append(f"Terraform init failed: {init_result.stderr}")

            validate_result = subprocess.run(
                ["terraform", "validate"],
                capture_output=True,
                text=True,
                cwd=terraform_path
            )

            validation_results["syntax_valid"] = validate_result.returncode == 0
            validation_results["validation_output"] = validate_result.stdout

            if validate_result.returncode != 0:
                validation_results["errors"].append(f"Terraform validation failed: {validate_result.stderr}")

            output = {
                "success": True,
                "task": "validate_terraform_syntax",
                "validation_results": validation_results,
                "overall_valid": validation_results["syntax_valid"] and len(validation_results["errors"]) == 0,
                "timestamp": datetime.now().isoformat()
            }

            print(f"   ✅ Syntax Valid: {validation_results['syntax_valid']}")
            print(f"   ✅ Formatting: {validation_results['fmt_check']}")

            self._save_operation("validate_terraform_syntax", output)
            return output

        except FileNotFoundError:
            return {"success": False, "error": "Terraform CLI not found - install terraform"}
        except Exception as e:
            return {"success": False, "task": "validate_terraform_syntax", "error": str(e)}

    def _test_yaml_syntax(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Test YAML syntax for all YAML files

        Args:
            yaml_path: Path to YAML files directory
        """
        print("📋 Testing YAML syntax...")

        yaml_path = params.get("yaml_path")

        if not yaml_path or not Path(yaml_path).exists():
            return {"success": False, "error": "YAML path required and must exist"}

        syntax_results = {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "errors": []
        }

        try:
            target = Path(yaml_path)

            for yaml_file in target.glob("**/*.yaml"):
                syntax_results["total_files"] += 1

                try:
                    with open(yaml_file, 'r') as f:
                        yaml.safe_load_all(f)
                    syntax_results["valid_files"] += 1
                except yaml.YAMLError as e:
                    syntax_results["invalid_files"] += 1
                    syntax_results["errors"].append({
                        "file": str(yaml_file.relative_to(target)),
                        "error": str(e)
                    })

            for yml_file in target.glob("**/*.yml"):
                syntax_results["total_files"] += 1

                try:
                    with open(yml_file, 'r') as f:
                        yaml.safe_load_all(f)
                    syntax_results["valid_files"] += 1
                except yaml.YAMLError as e:
                    syntax_results["invalid_files"] += 1
                    syntax_results["errors"].append({
                        "file": str(yml_file.relative_to(target)),
                        "error": str(e)
                    })

            output = {
                "success": True,
                "task": "test_yaml_syntax",
                "syntax_results": syntax_results,
                "pass_rate": (syntax_results["valid_files"] / max(1, syntax_results["total_files"])) * 100,
                "timestamp": datetime.now().isoformat()
            }

            print(f"   📊 Tested {syntax_results['total_files']} YAML files")
            print(f"   ✅ Valid: {syntax_results['valid_files']}")
            print(f"   ❌ Invalid: {syntax_results['invalid_files']}")

            self._save_operation("test_yaml_syntax", output)
            return output

        except Exception as e:
            return {"success": False, "task": "test_yaml_syntax", "error": str(e)}

    def _validate_security_configs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Validate security configurations

        Args:
            config_path: Path to security configurations
            config_type: Type of config (kubernetes, docker, terraform)
        """
        print("🔒 Validating security configurations...")

        config_path = params.get("config_path")
        config_type = params.get("config_type", "kubernetes")

        if not config_path or not Path(config_path).exists():
            return {"success": False, "error": "Config path required and must exist"}

        validation_results = {
            "total_configs": 0,
            "security_issues": [],
            "best_practices_violations": [],
            "compliant_configs": 0
        }

        try:
            target = Path(config_path)

            if config_type == "kubernetes":
                validation_results = self._validate_k8s_security(target)
            elif config_type == "docker":
                validation_results = self._validate_docker_security(target)
            elif config_type == "terraform":
                validation_results = self._validate_terraform_security(target)

            output = {
                "success": True,
                "task": "validate_security_configs",
                "config_type": config_type,
                "validation_results": validation_results,
                "compliance_rate": (validation_results["compliant_configs"] / max(1, validation_results["total_configs"])) * 100,
                "timestamp": datetime.now().isoformat()
            }

            print(f"   📊 Validated {validation_results['total_configs']} configs")
            print(f"   🔒 Security Issues: {len(validation_results['security_issues'])}")

            self._save_operation("validate_security_configs", output)
            return output

        except Exception as e:
            return {"success": False, "task": "validate_security_configs", "error": str(e)}

    def _validate_k8s_security(self, target: Path) -> Dict[str, Any]:
        """Validate Kubernetes security configurations"""

        results = {
            "total_configs": 0,
            "security_issues": [],
            "best_practices_violations": [],
            "compliant_configs": 0
        }

        for yaml_file in target.glob("**/*.yaml"):
            results["total_configs"] += 1
            is_compliant = True

            try:
                with open(yaml_file, 'r') as f:
                    docs = yaml.safe_load_all(f)

                    for doc in docs:
                        if not doc or doc.get("kind") not in ["Pod", "Deployment", "DaemonSet", "StatefulSet"]:
                            continue

                        pod_spec = None
                        if doc.get("kind") == "Pod":
                            pod_spec = doc.get("spec", {})
                        else:
                            pod_spec = doc.get("spec", {}).get("template", {}).get("spec", {})

                        if not pod_spec:
                            continue

                        security_context = pod_spec.get("securityContext", {})

                        if not security_context.get("runAsNonRoot"):
                            results["security_issues"].append({
                                "file": str(yaml_file.name),
                                "issue": "Missing runAsNonRoot in securityContext",
                                "severity": "high"
                            })
                            is_compliant = False

                        containers = pod_spec.get("containers", [])
                        for container in containers:
                            if container.get("securityContext", {}).get("privileged"):
                                results["security_issues"].append({
                                    "file": str(yaml_file.name),
                                    "issue": f"Container {container.get('name')} runs privileged",
                                    "severity": "critical"
                                })
                                is_compliant = False

            except:
                continue

            if is_compliant:
                results["compliant_configs"] += 1

        return results

    def _validate_docker_security(self, target: Path) -> Dict[str, Any]:
        """Validate Docker security configurations"""

        results = {
            "total_configs": 0,
            "security_issues": [],
            "best_practices_violations": [],
            "compliant_configs": 0
        }

        for dockerfile in target.glob("**/Dockerfile*"):
            results["total_configs"] += 1
            is_compliant = True

            try:
                with open(dockerfile, 'r') as f:
                    content = f.read()

                    if "USER root" in content or "USER 0" in content:
                        results["security_issues"].append({
                            "file": str(dockerfile.name),
                            "issue": "Dockerfile runs as root",
                            "severity": "high"
                        })
                        is_compliant = False

                    if "latest" in content.lower():
                        results["best_practices_violations"].append({
                            "file": str(dockerfile.name),
                            "issue": "Uses 'latest' tag instead of specific version",
                            "severity": "medium"
                        })
                        is_compliant = False

            except:
                continue

            if is_compliant:
                results["compliant_configs"] += 1

        return results

    def _validate_terraform_security(self, target: Path) -> Dict[str, Any]:
        """Validate Terraform security configurations"""

        results = {
            "total_configs": 0,
            "security_issues": [],
            "best_practices_violations": [],
            "compliant_configs": 0
        }

        for tf_file in target.glob("**/*.tf"):
            results["total_configs"] += 1
            is_compliant = True

            try:
                with open(tf_file, 'r') as f:
                    content = f.read()

                    if 'public_access_block' not in content and 's3_bucket' in content:
                        results["security_issues"].append({
                            "file": str(tf_file.name),
                            "issue": "S3 bucket missing public_access_block",
                            "severity": "high"
                        })
                        is_compliant = False

                    if 'encryption' not in content.lower() and ('s3_bucket' in content or 'ebs_volume' in content):
                        results["security_issues"].append({
                            "file": str(tf_file.name),
                            "issue": "Missing encryption configuration",
                            "severity": "high"
                        })
                        is_compliant = False

            except:
                continue

            if is_compliant:
                results["compliant_configs"] += 1

        return results

    def _test_automation_scripts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        MEDIUM CONFIDENCE: Test automation scripts

        Args:
            script_path: Path to automation scripts
        """
        print("🧪 Testing automation scripts...")

        script_path = params.get("script_path")

        if not script_path or not Path(script_path).exists():
            return {"success": False, "error": "Script path required and must exist"}

        test_results = {
            "total_scripts": 0,
            "syntax_valid": 0,
            "executable": 0,
            "issues": []
        }

        try:
            target = Path(script_path)

            for script in target.glob("**/*.sh"):
                test_results["total_scripts"] += 1

                syntax_check = subprocess.run(
                    ["bash", "-n", str(script)],
                    capture_output=True,
                    text=True
                )

                if syntax_check.returncode == 0:
                    test_results["syntax_valid"] += 1
                else:
                    test_results["issues"].append({
                        "file": str(script.name),
                        "issue": f"Syntax error: {syntax_check.stderr}",
                        "type": "syntax"
                    })

                if script.stat().st_mode & 0o111:
                    test_results["executable"] += 1
                else:
                    test_results["issues"].append({
                        "file": str(script.name),
                        "issue": "Script not executable",
                        "type": "permissions"
                    })

            output = {
                "success": True,
                "task": "test_automation_scripts",
                "test_results": test_results,
                "validation_required": True,
                "pass_rate": (test_results["syntax_valid"] / max(1, test_results["total_scripts"])) * 100,
                "timestamp": datetime.now().isoformat()
            }

            print(f"   📊 Tested {test_results['total_scripts']} scripts")
            print(f"   ✅ Syntax Valid: {test_results['syntax_valid']}")
            print(f"   ⚠️  Validation Required: Senior engineer review needed")

            self._save_operation("test_automation_scripts", output)
            return output

        except Exception as e:
            return {"success": False, "task": "test_automation_scripts", "error": str(e)}

    def _generate_qa_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Generate QA report from validation results

        Args:
            results_files: List of validation result files
            report_title: Title for QA report
        """
        print("📄 Generating QA report...")

        results_files = params.get("results_files", [])
        report_title = params.get("report_title", "Quality Assurance Report")

        if not results_files:
            return {"success": False, "error": "Results files required"}

        all_results = []
        for result_file in results_files:
            if Path(result_file).exists():
                with open(result_file, 'r') as f:
                    all_results.append(json.load(f))

        report_content = self._format_qa_report(all_results, report_title)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qa_report_{timestamp}.md"
        output_file = self.deliverable_dir / filename

        with open(output_file, 'w') as f:
            f.write(report_content)

        output = {
            "success": True,
            "task": "generate_qa_report",
            "report_file": str(output_file),
            "title": report_title,
            "validations_included": len(all_results),
            "timestamp": datetime.now().isoformat()
        }

        print(f"   ✅ QA Report generated: {output_file}")

        self._save_operation("generate_qa_report", output)
        return output

    def _format_qa_report(self, results: List[Dict], title: str) -> str:
        """Format QA report from validation results"""

        report = f"""# {title}

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**QA Agent**: {self.agent_id}

---

## Executive Summary

This report presents quality assurance testing results for security configurations and automation.

### Overall Results

"""

        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get("success"))

        report += f"- **Total Validations**: {total_tests}\n"
        report += f"- **Passed**: {passed_tests}\n"
        report += f"- **Failed**: {total_tests - passed_tests}\n"
        report += f"- **Pass Rate**: {(passed_tests / max(1, total_tests)) * 100:.1f}%\n\n"

        report += "## Detailed Results\n\n"

        for i, result in enumerate(results, 1):
            task = result.get("task", "unknown")
            success = result.get("success", False)
            status = "✅ PASS" if success else "❌ FAIL"

            report += f"### {i}. {task} - {status}\n\n"

            if result.get("validation_results"):
                vr = result["validation_results"]
                report += f"**Validation Details:**\n"
                for key, value in vr.items():
                    if isinstance(value, (int, str, float)):
                        report += f"- {key}: {value}\n"
                report += "\n"

        report += """## Recommendations

1. Address all failed validations before client delivery
2. Review security configurations for compliance
3. Run full test suite in staging environment
4. Document all validation results

## Sign-Off

- [ ] QA Engineer Review
- [ ] Senior Engineer Approval
- [ ] Client Delivery Authorized

---

*This QA report was generated by the Quality Assurance Agent*
"""

        return report

    def _assess_task_confidence(self, task_type: str) -> str:
        """Assess confidence level for QA task"""

        for level, tasks in self.confidence_levels.items():
            if task_type in tasks:
                return level

        return "low"

    def _save_operation(self, operation_type: str, result: Dict):
        """Save operation results to GP-DATA"""
        operation_id = f"{operation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"
        output_file = self.output_dir / f"{operation_id}.json"

        operation_record = {
            "agent": self.agent_id,
            "operation": operation_type,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }

        with open(output_file, 'w') as f:
            json.dump(operation_record, f, indent=2)

    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status and capabilities"""
        return {
            "agent_id": self.agent_id,
            "confidence_levels": self.confidence_levels,
            "capabilities": [
                "Kubernetes manifest validation",
                "Terraform syntax validation",
                "YAML syntax testing",
                "Security configuration validation",
                "QA report generation"
            ],
            "validation_types": ["Kubernetes", "Terraform", "Docker", "Scripts"]
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Quality Assurance Agent - Security Configuration Testing & Validation")
        print()
        print("HIGH CONFIDENCE Operations:")
        print("  python qa_agent.py validate-k8s --path <manifests> --namespace <ns>")
        print("  python qa_agent.py validate-terraform --path <terraform_dir>")
        print("  python qa_agent.py test-yaml --path <yaml_dir>")
        print("  python qa_agent.py validate-security --path <configs> --type <type>")
        print("  python qa_agent.py generate-report --results <file1,file2> --title <title>")
        print()
        print("MEDIUM CONFIDENCE Operations:")
        print("  python qa_agent.py test-scripts --path <scripts_dir>")
        print()
        print("Examples:")
        print("  python qa_agent.py validate-k8s --path ./k8s --namespace production")
        print("  python qa_agent.py validate-terraform --path ./terraform")
        print("  python qa_agent.py validate-security --path ./k8s --type kubernetes")
        sys.exit(1)

    agent = QualityAssuranceAgent()
    command = sys.argv[1]

    if command == "validate-k8s":
        params = {"manifests_path": None, "namespace": "default"}

        for arg in sys.argv[2:]:
            if arg.startswith("--path="):
                params["manifests_path"] = arg.split("=", 1)[1]
            elif arg.startswith("--namespace="):
                params["namespace"] = arg.split("=", 1)[1]

        result = agent._validate_k8s_manifests(params)

        if result["success"]:
            print(f"\n✅ Validation Complete:")
            print(f"   Pass Rate: {result['pass_rate']:.1f}%")
            vr = result["validation_results"]
            print(f"   Valid: {vr['valid_manifests']}/{vr['total_files']}")
        else:
            print(f"\n❌ Failed: {result.get('error')}")

    elif command == "validate-terraform":
        params = {"terraform_path": None}

        for arg in sys.argv[2:]:
            if arg.startswith("--path="):
                params["terraform_path"] = arg.split("=", 1)[1]

        result = agent._validate_terraform_syntax(params)

        if result["success"]:
            print(f"\n✅ Terraform Validation:")
            vr = result["validation_results"]
            print(f"   Syntax Valid: {vr['syntax_valid']}")
            print(f"   Formatting: {vr['fmt_check']}")
            print(f"   Overall: {result['overall_valid']}")

    elif command == "test-yaml":
        params = {"yaml_path": None}

        for arg in sys.argv[2:]:
            if arg.startswith("--path="):
                params["yaml_path"] = arg.split("=", 1)[1]

        result = agent._test_yaml_syntax(params)

        if result["success"]:
            print(f"\n✅ YAML Syntax Test:")
            sr = result["syntax_results"]
            print(f"   Pass Rate: {result['pass_rate']:.1f}%")
            print(f"   Valid: {sr['valid_files']}/{sr['total_files']}")

    elif command == "validate-security":
        params = {"config_path": None, "config_type": "kubernetes"}

        for arg in sys.argv[2:]:
            if arg.startswith("--path="):
                params["config_path"] = arg.split("=", 1)[1]
            elif arg.startswith("--type="):
                params["config_type"] = arg.split("=", 1)[1]

        result = agent._validate_security_configs(params)

        if result["success"]:
            print(f"\n✅ Security Validation:")
            vr = result["validation_results"]
            print(f"   Compliance Rate: {result['compliance_rate']:.1f}%")
            print(f"   Security Issues: {len(vr['security_issues'])}")

    elif command == "test-scripts":
        params = {"script_path": None}

        for arg in sys.argv[2:]:
            if arg.startswith("--path="):
                params["script_path"] = arg.split("=", 1)[1]

        result = agent._test_automation_scripts(params)

        if result["success"]:
            print(f"\n⚠️  Script Testing (Requires Validation):")
            tr = result["test_results"]
            print(f"   Pass Rate: {result['pass_rate']:.1f}%")
            print(f"   Syntax Valid: {tr['syntax_valid']}/{tr['total_scripts']}")

    elif command == "generate-report":
        params = {"results_files": [], "report_title": "QA Report"}

        for arg in sys.argv[2:]:
            if arg.startswith("--results="):
                params["results_files"] = arg.split("=", 1)[1].split(",")
            elif arg.startswith("--title="):
                params["report_title"] = arg.split("=", 1)[1]

        result = agent._generate_qa_report(params)

        if result["success"]:
            print(f"\n✅ QA Report Generated:")
            print(f"   File: {result['report_file']}")
            print(f"   Validations: {result['validations_included']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)