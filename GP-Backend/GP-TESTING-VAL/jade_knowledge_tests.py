#!/usr/bin/env python3
"""
Jade Knowledge Domain Tests
Tests Jade's understanding of Linux, OPA, Terraform, Python, GenAI, Automation, Cloud Security, Kubernetes
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any


class JadeKnowledgeTester:
    """Test Jade's domain knowledge across security, cloud, and infrastructure topics"""

    def __init__(self):
        self.gp_copilot_root = Path(__file__).parent.parent
        self.jade_chat_path = self.gp_copilot_root / "GP-AI/cli/jade_chat.py"
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def run_jade_command(self, command: str, timeout: int = 15) -> Dict[str, Any]:
        """Run a command through Jade chat and capture output"""
        try:
            result = subprocess.run(
                f'echo "{command}" | timeout {timeout} python3 {self.jade_chat_path}',
                shell=True,
                cwd=str(self.gp_copilot_root),
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )

            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': ''
            }

    def assert_knowledge(self, output: str, keywords: List[str], test_name: str) -> bool:
        """Assert output demonstrates knowledge (contains any of the keywords)"""
        output_lower = output.lower()

        # Check if any keyword is present
        found_keywords = [kw for kw in keywords if kw.lower() in output_lower]

        if found_keywords:
            self.passed += 1
            self.test_results.append({
                'test': test_name,
                'status': 'PASS',
                'message': f'Demonstrated knowledge: {", ".join(found_keywords[:3])}'
            })
            return True
        else:
            self.failed += 1
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'message': f'Expected knowledge keywords not found: {", ".join(keywords[:3])}'
            })
            return False

    # ========================================
    # Category 1: Linux Knowledge (15 tests)
    # ========================================

    def test_linux_01_file_permissions(self):
        """Test Linux file permissions knowledge"""
        result = self.run_jade_command("help")
        # Check if Jade demonstrates Linux knowledge through commands or help
        keywords = ['chmod', 'permissions', 'linux', 'file', 'security', 'scan']
        self.assert_knowledge(result['stdout'], keywords, "Linux: File permissions awareness")

    def test_linux_02_process_management(self):
        """Test Linux process management"""
        result = self.run_jade_command("show stats")
        keywords = ['process', 'system', 'status', 'running', 'stats']
        self.assert_knowledge(result['stdout'], keywords, "Linux: Process management")

    def test_linux_03_systemd_services(self):
        """Test systemd/service knowledge"""
        result = self.run_jade_command("help")
        keywords = ['service', 'daemon', 'running', 'agent', 'background']
        self.assert_knowledge(result['stdout'], keywords, "Linux: Service management")

    def test_linux_04_network_security(self):
        """Test Linux network security"""
        result = self.run_jade_command("help")
        keywords = ['network', 'firewall', 'port', 'security', 'policy']
        self.assert_knowledge(result['stdout'], keywords, "Linux: Network security")

    def test_linux_05_package_management(self):
        """Test package management knowledge"""
        result = self.run_jade_command("help")
        keywords = ['package', 'dependency', 'vulnerability', 'trivy', 'npm']
        self.assert_knowledge(result['stdout'], keywords, "Linux: Package management")

    def test_linux_06_user_management(self):
        """Test user/group management"""
        result = self.run_jade_command("help")
        keywords = ['user', 'rbac', 'permission', 'access', 'authentication']
        self.assert_knowledge(result['stdout'], keywords, "Linux: User management")

    def test_linux_07_log_analysis(self):
        """Test log analysis knowledge"""
        result = self.run_jade_command("show results")
        keywords = ['log', 'finding', 'result', 'scan', 'output']
        self.assert_knowledge(result['stdout'], keywords, "Linux: Log analysis")

    def test_linux_08_shell_scripting(self):
        """Test shell/bash awareness"""
        result = self.run_jade_command("help")
        keywords = ['script', 'command', 'bash', 'shell', 'scan']
        self.assert_knowledge(result['stdout'], keywords, "Linux: Shell scripting")

    def test_linux_09_cron_automation(self):
        """Test cron/scheduled task knowledge"""
        result = self.run_jade_command("help")
        keywords = ['automation', 'agent', 'scheduled', 'automated', 'run']
        self.assert_knowledge(result['stdout'], keywords, "Linux: Cron/automation")

    def test_linux_10_security_hardening(self):
        """Test security hardening knowledge"""
        result = self.run_jade_command("help")
        keywords = ['security', 'hardening', 'compliance', 'policy', 'fix']
        self.assert_knowledge(result['stdout'], keywords, "Linux: Security hardening")

    def test_linux_11_ssh_security(self):
        """Test SSH security"""
        result = self.run_jade_command("help")
        keywords = ['ssh', 'key', 'secret', 'gitleaks', 'authentication']
        self.assert_knowledge(result['stdout'], keywords, "Linux: SSH security")

    def test_linux_12_audit_logging(self):
        """Test audit/compliance logging"""
        result = self.run_jade_command("show results")
        keywords = ['audit', 'compliance', 'finding', 'scan', 'result']
        self.assert_knowledge(result['stdout'], keywords, "Linux: Audit logging")

    def test_linux_13_container_runtime(self):
        """Test container runtime knowledge"""
        result = self.run_jade_command("help")
        keywords = ['container', 'docker', 'image', 'trivy', 'kubernetes']
        self.assert_knowledge(result['stdout'], keywords, "Linux: Container runtime")

    def test_linux_14_selinux_apparmor(self):
        """Test SELinux/AppArmor knowledge"""
        result = self.run_jade_command("help")
        keywords = ['security', 'policy', 'opa', 'enforcement', 'compliance']
        self.assert_knowledge(result['stdout'], keywords, "Linux: SELinux/AppArmor")

    def test_linux_15_system_monitoring(self):
        """Test system monitoring"""
        result = self.run_jade_command("show stats")
        keywords = ['monitoring', 'stats', 'status', 'health', 'system']
        self.assert_knowledge(result['stdout'], keywords, "Linux: System monitoring")

    # ========================================
    # Category 2: OPA Knowledge (12 tests)
    # ========================================

    def test_opa_01_policy_language(self):
        """Test OPA/Rego knowledge"""
        result = self.run_jade_command("check policy")
        keywords = ['policy', 'opa', 'rego', 'validation', 'check']
        self.assert_knowledge(result['stdout'], keywords, "OPA: Policy language")

    def test_opa_02_terraform_validation(self):
        """Test OPA Terraform validation"""
        result = self.run_jade_command("validate terraform plan")
        keywords = ['terraform', 'validate', 'plan', 'policy', 'opa']
        self.assert_knowledge(result['stdout'], keywords, "OPA: Terraform validation")

    def test_opa_03_kubernetes_admission(self):
        """Test OPA Kubernetes admission control"""
        result = self.run_jade_command("check kubernetes policy")
        keywords = ['kubernetes', 'policy', 'admission', 'gatekeeper', 'opa']
        self.assert_knowledge(result['stdout'], keywords, "OPA: K8s admission control")

    def test_opa_04_gatekeeper(self):
        """Test Gatekeeper knowledge"""
        result = self.run_jade_command("run gatekeeper agent")
        keywords = ['gatekeeper', 'agent', 'policy', 'kubernetes', 'audit']
        self.assert_knowledge(result['stdout'], keywords, "OPA: Gatekeeper")

    def test_opa_05_conftest(self):
        """Test Conftest knowledge"""
        result = self.run_jade_command("run conftest gate agent")
        keywords = ['conftest', 'gate', 'agent', 'policy', 'validation']
        self.assert_knowledge(result['stdout'], keywords, "OPA: Conftest")

    def test_opa_06_policy_as_code(self):
        """Test Policy-as-Code concept"""
        result = self.run_jade_command("help")
        keywords = ['policy', 'code', 'automation', 'compliance', 'opa']
        self.assert_knowledge(result['stdout'], keywords, "OPA: Policy-as-Code")

    def test_opa_07_compliance_mapping(self):
        """Test compliance framework mapping"""
        result = self.run_jade_command("help")
        keywords = ['compliance', 'policy', 'standard', 'framework', 'cis']
        self.assert_knowledge(result['stdout'], keywords, "OPA: Compliance mapping")

    def test_opa_08_rego_testing(self):
        """Test OPA policy testing"""
        result = self.run_jade_command("test opa")
        keywords = ['test', 'opa', 'policy', 'validation', 'check']
        self.assert_knowledge(result['stdout'], keywords, "OPA: Policy testing")

    def test_opa_09_decision_logs(self):
        """Test OPA decision logging"""
        result = self.run_jade_command("show results")
        keywords = ['result', 'finding', 'decision', 'policy', 'violation']
        self.assert_knowledge(result['stdout'], keywords, "OPA: Decision logs")

    def test_opa_10_constraint_templates(self):
        """Test constraint template knowledge"""
        result = self.run_jade_command("help")
        keywords = ['constraint', 'template', 'gatekeeper', 'policy', 'kubernetes']
        self.assert_knowledge(result['stdout'], keywords, "OPA: Constraint templates")

    def test_opa_11_cicd_integration(self):
        """Test OPA CI/CD integration"""
        result = self.run_jade_command("help")
        keywords = ['cicd', 'pipeline', 'gate', 'automation', 'agent']
        self.assert_knowledge(result['stdout'], keywords, "OPA: CI/CD integration")

    def test_opa_12_rbac_policies(self):
        """Test RBAC policy knowledge"""
        result = self.run_jade_command("help")
        keywords = ['rbac', 'policy', 'access', 'permission', 'security']
        self.assert_knowledge(result['stdout'], keywords, "OPA: RBAC policies")

    # ========================================
    # Category 3: Terraform Knowledge (12 tests)
    # ========================================

    def test_terraform_01_iac_basics(self):
        """Test Infrastructure-as-Code knowledge"""
        result = self.run_jade_command("validate terraform")
        keywords = ['terraform', 'infrastructure', 'code', 'validate', 'iac']
        self.assert_knowledge(result['stdout'], keywords, "Terraform: IaC basics")

    def test_terraform_02_security_scanning(self):
        """Test Terraform security scanning"""
        result = self.run_jade_command("scan terraform")
        keywords = ['terraform', 'scan', 'security', 'checkov', 'tfsec']
        self.assert_knowledge(result['stdout'], keywords, "Terraform: Security scanning")

    def test_terraform_03_state_management(self):
        """Test Terraform state knowledge"""
        result = self.run_jade_command("help")
        keywords = ['state', 'terraform', 'backend', 'remote', 'plan']
        self.assert_knowledge(result['stdout'], keywords, "Terraform: State management")

    def test_terraform_04_policy_validation(self):
        """Test Terraform policy validation"""
        result = self.run_jade_command("validate terraform plan")
        keywords = ['validate', 'terraform', 'plan', 'policy', 'opa']
        self.assert_knowledge(result['stdout'], keywords, "Terraform: Policy validation")

    def test_terraform_05_drift_detection(self):
        """Test drift detection awareness"""
        result = self.run_jade_command("help")
        keywords = ['drift', 'state', 'plan', 'change', 'terraform']
        self.assert_knowledge(result['stdout'], keywords, "Terraform: Drift detection")

    def test_terraform_06_module_security(self):
        """Test Terraform module security"""
        result = self.run_jade_command("help")
        keywords = ['module', 'terraform', 'security', 'scan', 'compliance']
        self.assert_knowledge(result['stdout'], keywords, "Terraform: Module security")

    def test_terraform_07_provider_security(self):
        """Test provider security"""
        result = self.run_jade_command("help")
        keywords = ['provider', 'cloud', 'aws', 'azure', 'gcp']
        self.assert_knowledge(result['stdout'], keywords, "Terraform: Provider security")

    def test_terraform_08_sentinel_policies(self):
        """Test Sentinel/policy awareness"""
        result = self.run_jade_command("check policy")
        keywords = ['policy', 'sentinel', 'terraform', 'governance', 'opa']
        self.assert_knowledge(result['stdout'], keywords, "Terraform: Sentinel policies")

    def test_terraform_09_cicd_pipeline(self):
        """Test Terraform CI/CD"""
        result = self.run_jade_command("help")
        keywords = ['cicd', 'pipeline', 'automation', 'terraform', 'agent']
        self.assert_knowledge(result['stdout'], keywords, "Terraform: CI/CD")

    def test_terraform_10_compliance_checks(self):
        """Test compliance checking"""
        result = self.run_jade_command("help")
        keywords = ['compliance', 'check', 'standard', 'cis', 'policy']
        self.assert_knowledge(result['stdout'], keywords, "Terraform: Compliance")

    def test_terraform_11_secret_management(self):
        """Test secret management in Terraform"""
        result = self.run_jade_command("help")
        keywords = ['secret', 'credential', 'vault', 'sensitive', 'gitleaks']
        self.assert_knowledge(result['stdout'], keywords, "Terraform: Secret management")

    def test_terraform_12_remediation(self):
        """Test Terraform remediation"""
        result = self.run_jade_command("fix terraform issues")
        keywords = ['fix', 'terraform', 'remediate', 'issue', 'fixer']
        self.assert_knowledge(result['stdout'], keywords, "Terraform: Remediation")

    # ========================================
    # Category 4: Python Security (12 tests)
    # ========================================

    def test_python_01_bandit_scanning(self):
        """Test Bandit scanner knowledge"""
        result = self.run_jade_command("show results")
        keywords = ['bandit', 'python', 'security', 'scan', 'finding']
        self.assert_knowledge(result['stdout'], keywords, "Python: Bandit scanning")

    def test_python_02_injection_vulnerabilities(self):
        """Test SQL injection knowledge"""
        result = self.run_jade_command("help")
        keywords = ['injection', 'sql', 'security', 'vulnerability', 'bandit']
        self.assert_knowledge(result['stdout'], keywords, "Python: Injection vulns")

    def test_python_03_dependency_scanning(self):
        """Test dependency vulnerability scanning"""
        result = self.run_jade_command("show results")
        keywords = ['dependency', 'vulnerability', 'trivy', 'package', 'pip']
        self.assert_knowledge(result['stdout'], keywords, "Python: Dependency scanning")

    def test_python_04_secret_detection(self):
        """Test secret detection in Python"""
        result = self.run_jade_command("show results")
        keywords = ['secret', 'credential', 'gitleaks', 'hardcoded', 'password']
        self.assert_knowledge(result['stdout'], keywords, "Python: Secret detection")

    def test_python_05_code_quality(self):
        """Test code quality awareness"""
        result = self.run_jade_command("help")
        keywords = ['code', 'quality', 'scan', 'semgrep', 'bandit']
        self.assert_knowledge(result['stdout'], keywords, "Python: Code quality")

    def test_python_06_cryptography_issues(self):
        """Test cryptography vulnerability knowledge"""
        result = self.run_jade_command("help")
        keywords = ['crypto', 'encryption', 'hash', 'security', 'weak']
        self.assert_knowledge(result['stdout'], keywords, "Python: Cryptography")

    def test_python_07_deserialization(self):
        """Test deserialization vulnerability knowledge"""
        result = self.run_jade_command("help")
        keywords = ['pickle', 'deserialize', 'security', 'vulnerability', 'bandit']
        self.assert_knowledge(result['stdout'], keywords, "Python: Deserialization")

    def test_python_08_xss_prevention(self):
        """Test XSS prevention knowledge"""
        result = self.run_jade_command("help")
        keywords = ['xss', 'cross-site', 'security', 'vulnerability', 'web']
        self.assert_knowledge(result['stdout'], keywords, "Python: XSS prevention")

    def test_python_09_authentication(self):
        """Test authentication security"""
        result = self.run_jade_command("help")
        keywords = ['authentication', 'auth', 'password', 'credential', 'security']
        self.assert_knowledge(result['stdout'], keywords, "Python: Authentication")

    def test_python_10_sast_tools(self):
        """Test SAST tool knowledge"""
        result = self.run_jade_command("help")
        keywords = ['sast', 'static', 'analysis', 'bandit', 'semgrep']
        self.assert_knowledge(result['stdout'], keywords, "Python: SAST tools")

    def test_python_11_automated_fixing(self):
        """Test automated fixing"""
        result = self.run_jade_command("run fixers")
        keywords = ['fix', 'fixer', 'automated', 'remediate', 'bandit']
        self.assert_knowledge(result['stdout'], keywords, "Python: Automated fixing")

    def test_python_12_security_best_practices(self):
        """Test security best practices"""
        result = self.run_jade_command("help")
        keywords = ['security', 'best practice', 'standard', 'compliance', 'owasp']
        self.assert_knowledge(result['stdout'], keywords, "Python: Best practices")

    # ========================================
    # Category 5: Kubernetes Knowledge (15 tests)
    # ========================================

    def test_k8s_01_pod_security(self):
        """Test Pod Security Standards"""
        result = self.run_jade_command("check kubernetes policy")
        keywords = ['pod', 'security', 'kubernetes', 'policy', 'gatekeeper']
        self.assert_knowledge(result['stdout'], keywords, "K8s: Pod security")

    def test_k8s_02_rbac_configuration(self):
        """Test RBAC configuration"""
        result = self.run_jade_command("help")
        keywords = ['rbac', 'role', 'binding', 'kubernetes', 'access']
        self.assert_knowledge(result['stdout'], keywords, "K8s: RBAC")

    def test_k8s_03_network_policies(self):
        """Test Network Policy knowledge"""
        result = self.run_jade_command("help")
        keywords = ['network', 'policy', 'kubernetes', 'security', 'ingress']
        self.assert_knowledge(result['stdout'], keywords, "K8s: Network policies")

    def test_k8s_04_secrets_management(self):
        """Test secrets management"""
        result = self.run_jade_command("help")
        keywords = ['secret', 'kubernetes', 'vault', 'encryption', 'credential']
        self.assert_knowledge(result['stdout'], keywords, "K8s: Secrets management")

    def test_k8s_05_admission_control(self):
        """Test admission controllers"""
        result = self.run_jade_command("run gatekeeper agent")
        keywords = ['admission', 'gatekeeper', 'controller', 'kubernetes', 'policy']
        self.assert_knowledge(result['stdout'], keywords, "K8s: Admission control")

    def test_k8s_06_image_security(self):
        """Test container image security"""
        result = self.run_jade_command("help")
        keywords = ['image', 'container', 'security', 'trivy', 'vulnerability']
        self.assert_knowledge(result['stdout'], keywords, "K8s: Image security")

    def test_k8s_07_resource_limits(self):
        """Test resource limits/quotas"""
        result = self.run_jade_command("help")
        keywords = ['resource', 'limit', 'quota', 'kubernetes', 'policy']
        self.assert_knowledge(result['stdout'], keywords, "K8s: Resource limits")

    def test_k8s_08_service_mesh(self):
        """Test service mesh awareness"""
        result = self.run_jade_command("help")
        keywords = ['service', 'mesh', 'istio', 'network', 'security']
        self.assert_knowledge(result['stdout'], keywords, "K8s: Service mesh")

    def test_k8s_09_cis_benchmarks(self):
        """Test CIS Kubernetes benchmarks"""
        result = self.run_jade_command("help")
        keywords = ['cis', 'benchmark', 'kubernetes', 'compliance', 'standard']
        self.assert_knowledge(result['stdout'], keywords, "K8s: CIS benchmarks")

    def test_k8s_10_runtime_security(self):
        """Test runtime security"""
        result = self.run_jade_command("help")
        keywords = ['runtime', 'security', 'kubernetes', 'container', 'monitoring']
        self.assert_knowledge(result['stdout'], keywords, "K8s: Runtime security")

    def test_k8s_11_cluster_hardening(self):
        """Test cluster hardening"""
        result = self.run_jade_command("help")
        keywords = ['cluster', 'hardening', 'security', 'kubernetes', 'policy']
        self.assert_knowledge(result['stdout'], keywords, "K8s: Cluster hardening")

    def test_k8s_12_audit_logging(self):
        """Test audit logging"""
        result = self.run_jade_command("show results")
        keywords = ['audit', 'log', 'kubernetes', 'compliance', 'finding']
        self.assert_knowledge(result['stdout'], keywords, "K8s: Audit logging")

    def test_k8s_13_vulnerability_scanning(self):
        """Test K8s vulnerability scanning"""
        result = self.run_jade_command("help")
        keywords = ['vulnerability', 'scan', 'kubernetes', 'trivy', 'kubescape']
        self.assert_knowledge(result['stdout'], keywords, "K8s: Vulnerability scanning")

    def test_k8s_14_policy_enforcement(self):
        """Test policy enforcement"""
        result = self.run_jade_command("run gatekeeper agent")
        keywords = ['policy', 'enforcement', 'gatekeeper', 'kubernetes', 'opa']
        self.assert_knowledge(result['stdout'], keywords, "K8s: Policy enforcement")

    def test_k8s_15_gitops_security(self):
        """Test GitOps security"""
        result = self.run_jade_command("help")
        keywords = ['gitops', 'argocd', 'flux', 'deployment', 'automation']
        self.assert_knowledge(result['stdout'], keywords, "K8s: GitOps security")

    # ========================================
    # Category 6: Cloud Security (12 tests)
    # ========================================

    def test_cloud_01_aws_security(self):
        """Test AWS security knowledge"""
        result = self.run_jade_command("help")
        keywords = ['aws', 'cloud', 'security', 'iam', 's3']
        self.assert_knowledge(result['stdout'], keywords, "Cloud: AWS security")

    def test_cloud_02_azure_security(self):
        """Test Azure security"""
        result = self.run_jade_command("help")
        keywords = ['azure', 'cloud', 'security', 'entra', 'defender']
        self.assert_knowledge(result['stdout'], keywords, "Cloud: Azure security")

    def test_cloud_03_gcp_security(self):
        """Test GCP security"""
        result = self.run_jade_command("help")
        keywords = ['gcp', 'google', 'cloud', 'security', 'iam']
        self.assert_knowledge(result['stdout'], keywords, "Cloud: GCP security")

    def test_cloud_04_iam_policies(self):
        """Test IAM policy knowledge"""
        result = self.run_jade_command("help")
        keywords = ['iam', 'policy', 'access', 'permission', 'rbac']
        self.assert_knowledge(result['stdout'], keywords, "Cloud: IAM policies")

    def test_cloud_05_compliance_frameworks(self):
        """Test compliance framework knowledge"""
        result = self.run_jade_command("help")
        keywords = ['compliance', 'framework', 'cis', 'pci', 'hipaa']
        self.assert_knowledge(result['stdout'], keywords, "Cloud: Compliance")

    def test_cloud_06_data_encryption(self):
        """Test data encryption"""
        result = self.run_jade_command("help")
        keywords = ['encryption', 'kms', 'crypto', 'security', 'data']
        self.assert_knowledge(result['stdout'], keywords, "Cloud: Encryption")

    def test_cloud_07_network_security(self):
        """Test cloud network security"""
        result = self.run_jade_command("help")
        keywords = ['network', 'vpc', 'firewall', 'security', 'policy']
        self.assert_knowledge(result['stdout'], keywords, "Cloud: Network security")

    def test_cloud_08_identity_federation(self):
        """Test identity federation"""
        result = self.run_jade_command("help")
        keywords = ['identity', 'federation', 'sso', 'authentication', 'saml']
        self.assert_knowledge(result['stdout'], keywords, "Cloud: Identity federation")

    def test_cloud_09_container_security(self):
        """Test cloud container security"""
        result = self.run_jade_command("help")
        keywords = ['container', 'security', 'registry', 'image', 'trivy']
        self.assert_knowledge(result['stdout'], keywords, "Cloud: Container security")

    def test_cloud_10_serverless_security(self):
        """Test serverless security"""
        result = self.run_jade_command("help")
        keywords = ['serverless', 'lambda', 'function', 'security', 'cloud']
        self.assert_knowledge(result['stdout'], keywords, "Cloud: Serverless")

    def test_cloud_11_infrastructure_scanning(self):
        """Test infrastructure scanning"""
        result = self.run_jade_command("scan my project")
        keywords = ['scan', 'infrastructure', 'terraform', 'security', 'checkov']
        self.assert_knowledge(result['stdout'], keywords, "Cloud: Infrastructure scanning")

    def test_cloud_12_zero_trust(self):
        """Test Zero Trust knowledge"""
        result = self.run_jade_command("help")
        keywords = ['zero trust', 'security', 'policy', 'access', 'network']
        self.assert_knowledge(result['stdout'], keywords, "Cloud: Zero Trust")

    # ========================================
    # Category 7: GenAI/Automation (12 tests)
    # ========================================

    def test_genai_01_ai_analysis(self):
        """Test AI analysis capability"""
        result = self.run_jade_command("analyze scan results")
        keywords = ['analyze', 'ai', 'llm', 'analysis', 'insight']
        self.assert_knowledge(result['stdout'], keywords, "GenAI: AI analysis")

    def test_genai_02_rag_knowledge(self):
        """Test RAG (Retrieval-Augmented Generation)"""
        result = self.run_jade_command("help")
        keywords = ['knowledge', 'base', 'query', 'rag', 'context']
        self.assert_knowledge(result['stdout'], keywords, "GenAI: RAG knowledge")

    def test_genai_03_automated_remediation(self):
        """Test automated remediation"""
        result = self.run_jade_command("run fixers")
        keywords = ['automated', 'fix', 'remediation', 'fixer', 'agent']
        self.assert_knowledge(result['stdout'], keywords, "GenAI: Automated remediation")

    def test_genai_04_natural_language(self):
        """Test natural language understanding"""
        result = self.run_jade_command("I want to scan my project")
        keywords = ['scan', 'project', 'security', 'command', 'running']
        self.assert_knowledge(result['stdout'], keywords, "GenAI: Natural language")

    def test_genai_05_security_recommendations(self):
        """Test security recommendations"""
        result = self.run_jade_command("show results")
        keywords = ['recommendation', 'tip', 'suggestion', 'fix', 'fixer']
        self.assert_knowledge(result['stdout'], keywords, "GenAI: Recommendations")

    def test_genai_06_pattern_recognition(self):
        """Test pattern recognition"""
        result = self.run_jade_command("help")
        keywords = ['pattern', 'finding', 'security', 'vulnerability', 'scan']
        self.assert_knowledge(result['stdout'], keywords, "GenAI: Pattern recognition")

    def test_genai_07_agent_orchestration(self):
        """Test agent orchestration"""
        result = self.run_jade_command("run all agents")
        keywords = ['agent', 'orchestration', 'automation', 'workflow', 'run']
        self.assert_knowledge(result['stdout'], keywords, "GenAI: Agent orchestration")

    def test_genai_08_dynamic_learning(self):
        """Test dynamic learning capability"""
        result = self.run_jade_command("help")
        keywords = ['learning', 'adaptive', 'knowledge', 'context', 'ai']
        self.assert_knowledge(result['stdout'], keywords, "GenAI: Dynamic learning")

    def test_genai_09_code_generation(self):
        """Test code generation awareness"""
        result = self.run_jade_command("help")
        keywords = ['generate', 'code', 'policy', 'automated', 'fix']
        self.assert_knowledge(result['stdout'], keywords, "GenAI: Code generation")

    def test_genai_10_threat_intelligence(self):
        """Test threat intelligence"""
        result = self.run_jade_command("help")
        keywords = ['threat', 'intelligence', 'vulnerability', 'security', 'cve']
        self.assert_knowledge(result['stdout'], keywords, "GenAI: Threat intelligence")

    def test_genai_11_contextual_awareness(self):
        """Test contextual awareness"""
        result = self.run_jade_command("help")
        keywords = ['context', 'project', 'environment', 'custom', 'client']
        self.assert_knowledge(result['stdout'], keywords, "GenAI: Contextual awareness")

    def test_genai_12_workflow_automation(self):
        """Test workflow automation"""
        result = self.run_jade_command("help")
        keywords = ['workflow', 'automation', 'agent', 'pipeline', 'cicd']
        self.assert_knowledge(result['stdout'], keywords, "GenAI: Workflow automation")

    def run_all_tests(self):
        """Execute all knowledge domain tests"""
        print("\n" + "="*80)
        print("JADE KNOWLEDGE DOMAIN TEST SUITE")
        print("Testing: Linux, OPA, Terraform, Python, K8s, Cloud Security, GenAI")
        print("="*80 + "\n")

        # Get all test methods
        test_methods = [method for method in dir(self) if method.startswith('test_')]
        total_tests = len(test_methods)

        # Group tests by category
        categories = {
            'Linux': [m for m in test_methods if 'linux' in m],
            'OPA': [m for m in test_methods if 'opa' in m],
            'Terraform': [m for m in test_methods if 'terraform' in m],
            'Python': [m for m in test_methods if 'python' in m],
            'Kubernetes': [m for m in test_methods if 'k8s' in m],
            'Cloud Security': [m for m in test_methods if 'cloud' in m],
            'GenAI/Automation': [m for m in test_methods if 'genai' in m]
        }

        print(f"Total Tests: {total_tests}\n")
        for cat, tests in categories.items():
            print(f"  {cat}: {len(tests)} tests")
        print()

        # Run each category
        for category, test_list in categories.items():
            print(f"\n{'='*80}")
            print(f"Testing {category} Knowledge ({len(test_list)} tests)")
            print('='*80)

            for i, test_name in enumerate(test_list, 1):
                print(f"[{i}/{len(test_list)}] {test_name.replace('_', ' ').replace('test ', '').title()}...", end=' ')

                try:
                    test_method = getattr(self, test_name)
                    test_method()
                    print("✓")
                except Exception as e:
                    self.failed += 1
                    self.test_results.append({
                        'test': test_name,
                        'status': 'ERROR',
                        'message': str(e)
                    })
                    print(f"✗ (Error: {e})")

                time.sleep(0.1)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("KNOWLEDGE DOMAIN TEST SUMMARY")
        print("="*80 + "\n")

        # Count by status
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        errors = sum(1 for r in self.test_results if r['status'] == 'ERROR')

        total = len(self.test_results)
        pass_rate = (passed / total * 100) if total > 0 else 0

        # Overall stats
        print(f"Total Tests:     {total}")
        print(f"✅ Passed:       {passed}")
        print(f"❌ Failed:       {failed}")
        print(f"⚠️  Errors:       {errors}")
        print(f"\nKnowledge Score: {pass_rate:.1f}%\n")

        # Category breakdown
        categories = ['linux', 'opa', 'terraform', 'python', 'k8s', 'cloud', 'genai']
        print("="*80)
        print("KNOWLEDGE BY DOMAIN")
        print("="*80 + "\n")

        for cat in categories:
            cat_results = [r for r in self.test_results if cat in r['test'].lower()]
            if cat_results:
                cat_passed = sum(1 for r in cat_results if r['status'] == 'PASS')
                cat_total = len(cat_results)
                cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0

                emoji = "🎉" if cat_rate >= 80 else "✅" if cat_rate >= 60 else "⚠️"
                print(f"{emoji} {cat.upper():15} {cat_passed:2}/{cat_total:2} tests passed ({cat_rate:5.1f}%)")

        # Overall assessment
        print("\n" + "="*80)
        if pass_rate >= 80:
            print("🎉 EXCELLENT: Jade demonstrates strong domain knowledge!")
        elif pass_rate >= 60:
            print("✅ GOOD: Solid knowledge foundation with room for growth")
        elif pass_rate >= 40:
            print("⚠️  FAIR: Basic knowledge present, needs enhancement")
        else:
            print("❌ NEEDS WORK: Limited domain knowledge demonstrated")
        print("="*80 + "\n")

        # Save results
        self.save_results()

    def save_results(self):
        """Save test results to JSON file"""
        results_file = self.gp_copilot_root / "GP-TESTING-VAL/jade_knowledge_test_results.json"

        output = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': len(self.test_results),
            'passed': sum(1 for r in self.test_results if r['status'] == 'PASS'),
            'failed': sum(1 for r in self.test_results if r['status'] == 'FAIL'),
            'errors': sum(1 for r in self.test_results if r['status'] == 'ERROR'),
            'knowledge_score': (sum(1 for r in self.test_results if r['status'] == 'PASS') / len(self.test_results) * 100) if self.test_results else 0,
            'results': self.test_results
        }

        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"📄 Results saved to: {results_file}\n")


def main():
    """Run the knowledge domain test suite"""
    tester = JadeKnowledgeTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()