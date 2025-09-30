#!/usr/bin/env python3
"""
Secrets Management Agent - HashiCorp Vault, AWS Secrets Manager, K8s Secrets
Assists with configuring and implementing secrets management solutions
"""

import subprocess
import json
import base64
import yaml
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class SecretsManagementAgent:
    """
    Secrets Management Agent for Kubernetes secrets, ConfigMaps, and secret scanning

    Capabilities:
    - Create and manage Kubernetes secrets
    - Scan for hardcoded secrets in code
    - Generate secure secret templates
    - Validate secret references
    - Secret rotation guidance
    """

    def __init__(self):
        self.agent_id = "secrets_management_agent"
        self.kubectl_path = self._find_kubectl()

        self.config = GPDataConfig()
        self.output_dir = self.config.get_analysis_directory()

        self.confidence_levels = {
            "high": [
                "create_k8s_secret",
                "create_configmap",
                "scan_for_hardcoded_secrets",
                "generate_secret_templates",
                "validate_secret_references"
            ],
            "medium": [
                "setup_sealed_secrets",
                "configure_secret_rotation",
                "implement_secret_injection",
                "aws_secrets_manager_basic"
            ],
            "low": [
                "vault_cluster_setup",
                "vault_policies_advanced",
                "secret_encryption_keys",
                "multi_cloud_secrets"
            ]
        }

        self.secret_templates = self._load_secret_templates()

    def execute_secrets_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute secrets management task based on confidence level"""

        confidence = self._assess_task_confidence(task_type)

        if confidence == "high":
            return self._execute_high_confidence_task(task_type, parameters)
        elif confidence == "medium":
            return self._execute_medium_confidence_task(task_type, parameters)
        else:
            return {
                "success": False,
                "action": "escalate",
                "reason": f"Task {task_type} requires senior guidance",
                "confidence": confidence
            }

    def _execute_high_confidence_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute high-confidence secrets management tasks"""

        if task_type == "create_k8s_secret":
            return self._create_kubernetes_secret(parameters)
        elif task_type == "create_configmap":
            return self._create_configmap(parameters)
        elif task_type == "scan_for_hardcoded_secrets":
            return self._scan_hardcoded_secrets(parameters)
        elif task_type == "generate_secret_templates":
            return self._generate_secret_templates(parameters)
        elif task_type == "validate_secret_references":
            return self._validate_secret_references(parameters)
        else:
            return {"success": False, "error": f"Unknown task: {task_type}"}

    def _execute_medium_confidence_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute medium-confidence tasks with guidance"""

        return {
            "success": False,
            "action": "provide_guidance",
            "task": task_type,
            "guidance": f"Task {task_type} requires senior review - implementation guidance provided",
            "next_steps": [
                "Review generated configuration",
                "Validate with senior engineer",
                "Test in non-production environment",
                "Document implementation"
            ]
        }

    def _create_kubernetes_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Create Kubernetes secret with secure practices

        Args:
            name: Secret name
            namespace: Target namespace
            type: Secret type (Opaque, kubernetes.io/tls, etc.)
            data: Key-value pairs to store
        """
        print(f"🔐 Creating Kubernetes secret...")

        secret_name = params.get("name")
        namespace = params.get("namespace", "default")
        secret_type = params.get("type", "Opaque")
        data = params.get("data", {})

        if not secret_name or not data:
            return {"success": False, "error": "Secret name and data required"}

        encoded_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                encoded_data[key] = base64.b64encode(value.encode()).decode()
            else:
                encoded_data[key] = base64.b64encode(str(value).encode()).decode()

        secret_manifest = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": secret_name,
                "namespace": namespace,
                "labels": {
                    "managed-by": "secrets-agent",
                    "created": datetime.now().strftime("%Y-%m-%d")
                }
            },
            "type": secret_type,
            "data": encoded_data
        }

        try:
            result = self._kubectl_apply(secret_manifest)
            if result["success"]:
                output = {
                    "success": True,
                    "task": "create_k8s_secret",
                    "secret_name": secret_name,
                    "namespace": namespace,
                    "keys": list(data.keys()),
                    "verification_command": f"kubectl get secret {secret_name} -n {namespace} -o yaml",
                    "usage_example": self._generate_secret_usage_example(secret_name, list(data.keys()))
                }

                print(f"   ✅ Secret '{secret_name}' created in namespace '{namespace}'")
                print(f"   Keys: {', '.join(data.keys())}")

                self._save_operation("create_k8s_secret", output)
                return output
            else:
                return {"success": False, "task": "create_k8s_secret", "error": result["error"]}

        except Exception as e:
            return {"success": False, "task": "create_k8s_secret", "error": str(e)}

    def _create_configmap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Create ConfigMap for non-sensitive configuration data

        Args:
            name: ConfigMap name
            namespace: Target namespace
            data: Key-value configuration data
            from_file: Optional file path to load data from
        """
        print(f"📋 Creating ConfigMap...")

        cm_name = params.get("name")
        namespace = params.get("namespace", "default")
        data = params.get("data", {})
        from_file = params.get("from_file")

        if not cm_name:
            return {"success": False, "error": "ConfigMap name required"}

        configmap_data = {}

        if from_file:
            file_path = Path(from_file)
            if file_path.exists():
                with open(file_path, 'r') as f:
                    configmap_data[file_path.name] = f.read()
            else:
                return {"success": False, "error": f"File not found: {from_file}"}
        else:
            configmap_data = data

        if not configmap_data:
            return {"success": False, "error": "ConfigMap data or file required"}

        cm_manifest = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": cm_name,
                "namespace": namespace,
                "labels": {
                    "managed-by": "secrets-agent",
                    "created": datetime.now().strftime("%Y-%m-%d")
                }
            },
            "data": configmap_data
        }

        try:
            result = self._kubectl_apply(cm_manifest)
            if result["success"]:
                output = {
                    "success": True,
                    "task": "create_configmap",
                    "configmap_name": cm_name,
                    "namespace": namespace,
                    "keys": list(configmap_data.keys()),
                    "verification_command": f"kubectl get configmap {cm_name} -n {namespace} -o yaml"
                }

                print(f"   ✅ ConfigMap '{cm_name}' created in namespace '{namespace}'")

                self._save_operation("create_configmap", output)
                return output
            else:
                return {"success": False, "task": "create_configmap", "error": result["error"]}

        except Exception as e:
            return {"success": False, "task": "create_configmap", "error": str(e)}

    def _scan_hardcoded_secrets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Scan for hardcoded secrets in code and configuration files

        Args:
            path: Target directory to scan
            extensions: File extensions to scan (default: .yaml, .yml, .json, .py, .js, .env)
        """
        print(f"🔍 Scanning for hardcoded secrets...")

        target_path = params.get("path", ".")
        file_extensions = params.get("extensions", [".yaml", ".yml", ".json", ".py", ".js", ".env"])

        findings = []
        target = Path(target_path)

        secret_patterns = {
            "password": [r'password\s*[=:]\s*["\']([^"\']+)["\']', r'pwd\s*[=:]\s*["\']([^"\']+)["\']'],
            "api_key": [r'api[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', r'apikey\s*[=:]\s*["\']([^"\']+)["\']'],
            "token": [r'token\s*[=:]\s*["\']([^"\']+)["\']', r'auth[_-]?token\s*[=:]\s*["\']([^"\']+)["\']'],
            "secret": [r'secret\s*[=:]\s*["\']([^"\']+)["\']', r'client[_-]?secret\s*[=:]\s*["\']([^"\']+)["\']'],
            "key": [r'private[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', r'secret[_-]?key\s*[=:]\s*["\']([^"\']+)["\']']
        }

        files_scanned = 0

        try:
            for ext in file_extensions:
                for file_path in target.glob(f"**/*{ext}"):
                    if file_path.is_file():
                        files_scanned += 1
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()

                                for secret_type, patterns in secret_patterns.items():
                                    for pattern in patterns:
                                        matches = re.finditer(pattern, content, re.IGNORECASE)
                                        for match in matches:
                                            findings.append({
                                                "file": str(file_path.relative_to(target)),
                                                "line": content[:match.start()].count('\n') + 1,
                                                "secret_type": secret_type,
                                                "pattern_matched": pattern,
                                                "severity": "high",
                                                "recommendation": f"Move {secret_type} to Kubernetes Secret or environment variable"
                                            })
                        except (UnicodeDecodeError, PermissionError):
                            continue

            output = {
                "success": True,
                "task": "scan_hardcoded_secrets",
                "target_path": target_path,
                "findings": findings,
                "total_findings": len(findings),
                "files_scanned": files_scanned,
                "recommendations": self._generate_secret_remediation_recommendations(findings)
            }

            print(f"   📊 Scanned {files_scanned} files")
            print(f"   🔴 Found {len(findings)} potential hardcoded secrets")

            self._save_operation("scan_hardcoded_secrets", output)
            return output

        except Exception as e:
            return {"success": False, "task": "scan_hardcoded_secrets", "error": str(e)}

    def _generate_secret_templates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Generate secure secret management templates

        Args:
            type: Template type (kubernetes, docker, terraform)
            secret_types: List of secret types to generate (database, api_keys, certificates)
        """
        print(f"📝 Generating secret templates...")

        template_type = params.get("type", "kubernetes")
        secret_types = params.get("secret_types", ["database", "api_keys", "certificates"])

        templates = {}

        if template_type == "kubernetes":
            templates = self._generate_kubernetes_secret_templates(secret_types)
        elif template_type == "docker":
            templates = self._generate_docker_secret_templates(secret_types)
        elif template_type == "terraform":
            templates = self._generate_terraform_secret_templates(secret_types)

        output = {
            "success": True,
            "task": "generate_secret_templates",
            "template_type": template_type,
            "templates": templates,
            "usage_instructions": self._generate_template_usage_instructions(template_type)
        }

        print(f"   ✅ Generated {len(templates)} {template_type} secret templates")

        self._save_operation("generate_secret_templates", output)
        return output

    def _validate_secret_references(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Validate that secret references in manifests are correct

        Args:
            path: Path to manifests directory
            namespace: Kubernetes namespace to check
        """
        print(f"✅ Validating secret references...")

        manifests_path = params.get("path")
        namespace = params.get("namespace", "default")

        if not manifests_path:
            return {"success": False, "error": "Manifests path required"}

        validation_results = []
        target = Path(manifests_path)

        try:
            existing_secrets = self._get_existing_secrets(namespace)

            for yaml_file in target.glob("**/*.yaml"):
                with open(yaml_file, 'r') as f:
                    try:
                        docs = yaml.safe_load_all(f)
                        for doc in docs:
                            if not doc:
                                continue

                            secret_refs = self._extract_secret_references(doc)

                            for ref in secret_refs:
                                secret_name = ref["secret_name"]
                                key = ref.get("key")

                                if secret_name in existing_secrets:
                                    if key and key not in existing_secrets[secret_name]:
                                        validation_results.append({
                                            "file": str(yaml_file.relative_to(target)),
                                            "issue": "missing_key",
                                            "secret_name": secret_name,
                                            "missing_key": key,
                                            "available_keys": existing_secrets[secret_name]
                                        })
                                    else:
                                        validation_results.append({
                                            "file": str(yaml_file.relative_to(target)),
                                            "status": "valid",
                                            "secret_name": secret_name,
                                            "key": key
                                        })
                                else:
                                    validation_results.append({
                                        "file": str(yaml_file.relative_to(target)),
                                        "issue": "missing_secret",
                                        "secret_name": secret_name,
                                        "recommendation": f"Create secret: kubectl create secret generic {secret_name}"
                                    })

                    except yaml.YAMLError:
                        continue

            issues = [r for r in validation_results if r.get("issue")]
            valid_refs = [r for r in validation_results if r.get("status") == "valid"]

            output = {
                "success": True,
                "task": "validate_secret_references",
                "namespace": namespace,
                "total_references": len(validation_results),
                "valid_references": len(valid_refs),
                "issues_found": len(issues),
                "validation_results": validation_results,
                "summary": {
                    "missing_secrets": len([i for i in issues if i.get("issue") == "missing_secret"]),
                    "missing_keys": len([i for i in issues if i.get("issue") == "missing_key"])
                }
            }

            print(f"   📊 Validated {len(validation_results)} secret references")
            print(f"   ✅ Valid: {len(valid_refs)}")
            print(f"   ❌ Issues: {len(issues)}")

            self._save_operation("validate_secret_references", output)
            return output

        except Exception as e:
            return {"success": False, "task": "validate_secret_references", "error": str(e)}

    def _generate_kubernetes_secret_templates(self, secret_types: List[str]) -> Dict[str, Any]:
        """Generate Kubernetes secret templates"""

        templates = {}

        if "database" in secret_types:
            templates["database_secret.yaml"] = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {"name": "database-credentials", "namespace": "default"},
                "type": "Opaque",
                "data": {
                    "username": "<base64-encoded-username>",
                    "password": "<base64-encoded-password>",
                    "host": "<base64-encoded-host>",
                    "port": "<base64-encoded-port>"
                }
            }

        if "api_keys" in secret_types:
            templates["api_secret.yaml"] = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {"name": "api-credentials", "namespace": "default"},
                "type": "Opaque",
                "data": {
                    "api_key": "<base64-encoded-api-key>",
                    "api_secret": "<base64-encoded-api-secret>"
                }
            }

        if "certificates" in secret_types:
            templates["tls_secret.yaml"] = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {"name": "tls-credentials", "namespace": "default"},
                "type": "kubernetes.io/tls",
                "data": {
                    "tls.crt": "<base64-encoded-certificate>",
                    "tls.key": "<base64-encoded-private-key>"
                }
            }

        return templates

    def _generate_docker_secret_templates(self, secret_types: List[str]) -> Dict[str, Any]:
        """Generate Docker secret templates"""

        templates = {}

        if "database" in secret_types:
            templates["db_credentials.txt"] = "username=admin\npassword=secret123\nhost=localhost\nport=5432"

        if "api_keys" in secret_types:
            templates["api_keys.txt"] = "api_key=your-api-key\napi_secret=your-api-secret"

        return templates

    def _generate_terraform_secret_templates(self, secret_types: List[str]) -> Dict[str, Any]:
        """Generate Terraform secret templates"""

        templates = {}

        if "database" in secret_types:
            templates["database_secret.tf"] = """
resource "aws_secretsmanager_secret" "database" {
  name = "database-credentials"
  description = "Database credentials"
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id = aws_secretsmanager_secret.database.id
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password
    host = var.db_host
    port = var.db_port
  })
}
"""

        return templates

    def _generate_template_usage_instructions(self, template_type: str) -> Dict[str, Any]:
        """Generate usage instructions for templates"""

        instructions = {}

        if template_type == "kubernetes":
            instructions = {
                "encode_values": "echo -n 'myvalue' | base64",
                "apply_secret": "kubectl apply -f secret.yaml",
                "verify": "kubectl get secret <secret-name> -o yaml",
                "use_in_pod": "Reference secret in pod spec using env or volumeMount"
            }
        elif template_type == "docker":
            instructions = {
                "create_secret": "docker secret create my_secret secret.txt",
                "list_secrets": "docker secret ls",
                "use_in_service": "docker service create --secret my_secret myapp"
            }

        return instructions

    def _generate_secret_usage_example(self, secret_name: str, keys: List[str]) -> str:
        """Generate usage example for secret in pod"""

        return f"""
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: {keys[0].upper()}
      valueFrom:
        secretKeyRef:
          name: {secret_name}
          key: {keys[0]}
"""

    def _generate_secret_remediation_recommendations(self, findings: List[Dict]) -> List[str]:
        """Generate recommendations for hardcoded secrets"""

        recommendations = []

        if findings:
            recommendations.append("Move all hardcoded secrets to Kubernetes Secrets")
            recommendations.append("Use environment variables to inject secrets into applications")
            recommendations.append("Implement secret rotation policies")
            recommendations.append("Add pre-commit hooks to prevent secret commits")
            recommendations.append("Use tools like git-secrets or gitleaks in CI/CD")

        return recommendations

    def _get_existing_secrets(self, namespace: str) -> Dict[str, List[str]]:
        """Get existing secrets and their keys from namespace"""

        try:
            cmd = [self.kubectl_path, "get", "secrets", "-n", namespace, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                secrets_data = json.loads(result.stdout)
                secrets = {}

                for item in secrets_data.get("items", []):
                    name = item["metadata"]["name"]
                    keys = list(item.get("data", {}).keys())
                    secrets[name] = keys

                return secrets
        except:
            pass

        return {}

    def _extract_secret_references(self, manifest: Dict) -> List[Dict]:
        """Extract secret references from Kubernetes manifest"""

        refs = []

        if not manifest:
            return refs

        def find_secret_refs(obj, path=""):
            if isinstance(obj, dict):
                if "secretKeyRef" in obj:
                    refs.append({
                        "secret_name": obj["secretKeyRef"].get("name"),
                        "key": obj["secretKeyRef"].get("key"),
                        "path": path
                    })
                elif "secretName" in obj:
                    refs.append({
                        "secret_name": obj["secretName"],
                        "path": path
                    })

                for key, value in obj.items():
                    find_secret_refs(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_secret_refs(item, f"{path}[{i}]")

        find_secret_refs(manifest)
        return refs

    def _kubectl_apply(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Kubernetes manifest using kubectl"""

        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(manifest, f)
                temp_file = f.name

            cmd = [self.kubectl_path, "apply", "-f", temp_file]
            result = subprocess.run(cmd, capture_output=True, text=True)

            Path(temp_file).unlink()

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _find_kubectl(self) -> str:
        """Find kubectl binary"""
        import shutil
        kubectl = shutil.which("kubectl")
        if not kubectl:
            raise RuntimeError("kubectl not found - install kubectl to use secrets agent")
        return kubectl

    def _assess_task_confidence(self, task_type: str) -> str:
        """Assess confidence level for secrets management task"""

        for level, tasks in self.confidence_levels.items():
            if task_type in tasks:
                return level

        return "low"

    def _load_secret_templates(self) -> Dict[str, Any]:
        """Load predefined secret templates"""
        return {
            "database": {"username": "", "password": "", "host": "", "port": ""},
            "api_credentials": {"api_key": "", "api_secret": ""},
            "tls_certificate": {"tls.crt": "", "tls.key": ""}
        }

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
            "supported_platforms": ["Kubernetes", "Docker", "AWS Secrets Manager (basic)"],
            "secret_types": ["Database credentials", "API keys", "TLS certificates", "Generic secrets"]
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Secrets Management Agent - Kubernetes Secrets & Secret Scanning")
        print()
        print("HIGH CONFIDENCE Operations:")
        print("  python secrets_agent.py create-secret --name <name> --namespace <ns> --key=value ...")
        print("  python secrets_agent.py create-configmap --name <name> --namespace <ns> --key=value ...")
        print("  python secrets_agent.py scan-secrets --path <directory> [--extensions .yaml,.json]")
        print("  python secrets_agent.py generate-templates --type kubernetes --secrets database,api_keys")
        print("  python secrets_agent.py validate-refs --path <manifests> --namespace <ns>")
        print()
        print("Examples:")
        print("  python secrets_agent.py create-secret --name db-creds --namespace prod --username=admin --password=secret123")
        print("  python secrets_agent.py scan-secrets --path ./src")
        print("  python secrets_agent.py validate-refs --path ./k8s --namespace production")
        sys.exit(1)

    agent = SecretsManagementAgent()
    command = sys.argv[1]

    if command == "create-secret":
        params = {"name": None, "namespace": "default", "data": {}}

        for arg in sys.argv[2:]:
            if arg.startswith("--name="):
                params["name"] = arg.split("=", 1)[1]
            elif arg.startswith("--namespace="):
                params["namespace"] = arg.split("=", 1)[1]
            elif "=" in arg and arg.startswith("--"):
                key, value = arg[2:].split("=", 1)
                params["data"][key] = value

        result = agent._create_kubernetes_secret(params)

        if result["success"]:
            print(f"\n✅ Secret created successfully")
            print(f"   Verify: {result['verification_command']}")
            print(f"\n   Usage Example:")
            print(result['usage_example'])
        else:
            print(f"\n❌ Failed: {result.get('error')}")

    elif command == "create-configmap":
        params = {"name": None, "namespace": "default", "data": {}}

        for arg in sys.argv[2:]:
            if arg.startswith("--name="):
                params["name"] = arg.split("=", 1)[1]
            elif arg.startswith("--namespace="):
                params["namespace"] = arg.split("=", 1)[1]
            elif "=" in arg and arg.startswith("--"):
                key, value = arg[2:].split("=", 1)
                params["data"][key] = value

        result = agent._create_configmap(params)

        if result["success"]:
            print(f"\n✅ ConfigMap created")
            print(f"   Verify: {result['verification_command']}")

    elif command == "scan-secrets":
        params = {"path": ".", "extensions": [".yaml", ".yml", ".json", ".py", ".js", ".env"]}

        for arg in sys.argv[2:]:
            if arg.startswith("--path="):
                params["path"] = arg.split("=", 1)[1]
            elif arg.startswith("--extensions="):
                exts = arg.split("=", 1)[1].split(",")
                params["extensions"] = exts

        result = agent._scan_hardcoded_secrets(params)

        if result["success"]:
            print(f"\n📊 Scan Results:")
            print(f"   Files scanned: {result['files_scanned']}")
            print(f"   Secrets found: {result['total_findings']}")

            if result['findings']:
                print(f"\n   🔴 Findings:")
                for finding in result['findings'][:5]:
                    print(f"   - {finding['file']}:{finding['line']} - {finding['secret_type']}")

                print(f"\n   Recommendations:")
                for rec in result['recommendations']:
                    print(f"   - {rec}")

    elif command == "generate-templates":
        params = {"type": "kubernetes", "secret_types": ["database"]}

        for arg in sys.argv[2:]:
            if arg.startswith("--type="):
                params["type"] = arg.split("=", 1)[1]
            elif arg.startswith("--secrets="):
                params["secret_types"] = arg.split("=", 1)[1].split(",")

        result = agent._generate_secret_templates(params)

        if result["success"]:
            print(f"\n📝 Generated Templates:")
            for template_name, template_content in result['templates'].items():
                print(f"\n   {template_name}:")
                print(yaml.dump(template_content, default_flow_style=False, indent=2))

    elif command == "validate-refs":
        params = {"path": None, "namespace": "default"}

        for arg in sys.argv[2:]:
            if arg.startswith("--path="):
                params["path"] = arg.split("=", 1)[1]
            elif arg.startswith("--namespace="):
                params["namespace"] = arg.split("=", 1)[1]

        result = agent._validate_secret_references(params)

        if result["success"]:
            print(f"\n✅ Validation Results:")
            print(f"   Total references: {result['total_references']}")
            print(f"   Valid: {result['valid_references']}")
            print(f"   Issues: {result['issues_found']}")

            if result['summary']['missing_secrets'] > 0:
                print(f"\n   Missing secrets: {result['summary']['missing_secrets']}")
            if result['summary']['missing_keys'] > 0:
                print(f"   Missing keys: {result['summary']['missing_keys']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)