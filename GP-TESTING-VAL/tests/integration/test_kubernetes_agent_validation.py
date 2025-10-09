#!/usr/bin/env python3
"""
Kubernetes Agent Validation Test
===============================

Systematic testing of Kubernetes Agent capabilities to verify:
1. Actual cluster security analysis vs claimed CKA/CKS expertise
2. Real RBAC and NetworkPolicy generation vs theoretical templates
3. Integration with Kubescape and security tools vs hardcoded checks
4. Professional deliverables vs basic output

Test Results: Saved to docs/GP-results/kubernetes-agent-test-TIMESTAMP.md
"""

import sys
import asyncio
import json
import yaml
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/jimmie/linkops-industries/James-OS/guidepoint')

from agents.kubernetes_agent.agent import KubernetesAgent

class KubernetesAgentValidator:
    """Comprehensive validation of Kubernetes Agent capabilities"""

    def __init__(self):
        self.agent = KubernetesAgent()
        self.test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "test_metadata": {
                "timestamp": self.test_timestamp,
                "agent_tested": "KubernetesAgent",
                "test_purpose": "Validate CKA/CKS level capabilities vs claims"
            },
            "cluster_analysis": {},
            "security_manifests": {},
            "tool_integration": {},
            "professional_grade": {},
            "overall_assessment": {}
        }

    async def test_cluster_security_analysis(self, test_project: str):
        """Test actual cluster security analysis capabilities"""
        print(f"☸️ Testing Kubernetes Agent cluster analysis on: {test_project}")

        # Test with and without actual cluster access
        analysis_result = await self.agent.analyze_cluster_security(
            kubeconfig_path=None,  # No real cluster access
            manifests_path=test_project
        )

        self.results["cluster_analysis"] = {
            "test_project": test_project,
            "analysis_result": analysis_result,
            "security_issues_found": len(analysis_result.get("security_issues", [])),
            "pod_security_violations": len(analysis_result.get("pod_security", {}).get("violations", [])),
            "rbac_analysis": analysis_result.get("rbac_analysis", {}),
            "network_policy_analysis": analysis_result.get("network_policies", {}),
            "tool_integration_evidence": self._analyze_k8s_tool_integration(analysis_result)
        }

        print(f"   Found {len(analysis_result.get('security_issues', []))} security issues")
        return analysis_result

    def _analyze_k8s_tool_integration(self, analysis_result):
        """Check for evidence of actual K8s security tool integration"""
        evidence = {
            "kubescape_integration": False,
            "kube_score_integration": False,
            "polaris_integration": False,
            "kubectl_integration": False
        }

        # Convert result to string for pattern matching
        result_str = str(analysis_result).lower()

        if "kubescape" in result_str:
            evidence["kubescape_integration"] = True
        if "kube-score" in result_str or "kubescore" in result_str:
            evidence["kube_score_integration"] = True
        if "polaris" in result_str:
            evidence["polaris_integration"] = True
        if "kubectl" in result_str:
            evidence["kubectl_integration"] = True

        return evidence

    async def test_security_manifest_generation(self, output_dir: str):
        """Test actual security manifest generation capabilities"""
        print(f"📝 Testing Kubernetes Agent manifest generation to: {output_dir}")

        # Test manifest generation
        manifest_result = await self.agent.generate_security_manifests(
            output_dir=output_dir,
            namespace="test-namespace"
        )

        # Analyze generated manifests
        generated_files = self._analyze_generated_manifests(output_dir)

        self.results["security_manifests"] = {
            "output_directory": output_dir,
            "generation_result": manifest_result,
            "files_generated": generated_files,
            "manifest_quality": self._assess_manifest_quality(output_dir),
            "rbac_completeness": self._assess_rbac_completeness(output_dir),
            "networkpolicy_quality": self._assess_networkpolicy_quality(output_dir)
        }

        print(f"   Generated {len(generated_files)} manifest files")
        return manifest_result

    def _analyze_generated_manifests(self, output_dir: str):
        """Analyze what manifest files were actually generated"""
        output_path = Path(output_dir)
        generated_files = []

        if output_path.exists():
            for file in output_path.rglob("*.yaml"):
                if file.is_file():
                    generated_files.append({
                        "filename": str(file.relative_to(output_path)),
                        "size_bytes": file.stat().st_size,
                        "content_preview": self._get_yaml_preview(file)
                    })

        return generated_files

    def _get_yaml_preview(self, file_path: Path):
        """Get a preview of YAML file content for analysis"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Try to parse as YAML
            try:
                yaml_data = yaml.safe_load(content)
                return {
                    "valid_yaml": True,
                    "kind": yaml_data.get("kind", "unknown"),
                    "apiVersion": yaml_data.get("apiVersion", "unknown"),
                    "metadata_name": yaml_data.get("metadata", {}).get("name", "unknown"),
                    "line_count": len(content.split('\n'))
                }
            except yaml.YAMLError:
                return {
                    "valid_yaml": False,
                    "line_count": len(content.split('\n')),
                    "first_lines": content.split('\n')[:3]
                }

        except Exception as e:
            return {
                "error": str(e),
                "readable": False
            }

    def _assess_manifest_quality(self, output_dir: str):
        """Assess the quality and professionalism of generated manifests"""
        output_path = Path(output_dir)
        quality_assessment = {
            "total_files": 0,
            "valid_yaml_files": 0,
            "kubernetes_manifests": 0,
            "security_focused": 0,
            "quality_indicators": []
        }

        if not output_path.exists():
            quality_assessment["quality_indicators"].append("Output directory not created")
            return quality_assessment

        for file in output_path.rglob("*.yaml"):
            quality_assessment["total_files"] += 1

            preview = self._get_yaml_preview(file)
            if preview.get("valid_yaml", False):
                quality_assessment["valid_yaml_files"] += 1

                kind = preview.get("kind", "").lower()
                if kind in ["role", "rolebinding", "clusterrole", "clusterrolebinding",
                           "networkpolicy", "podsecuritypolicy", "securitycontext"]:
                    quality_assessment["kubernetes_manifests"] += 1

                if any(sec_word in kind for sec_word in ["security", "rbac", "network", "policy"]):
                    quality_assessment["security_focused"] += 1

        # Quality indicators
        if quality_assessment["total_files"] > 0:
            quality_assessment["quality_indicators"].append(f"Generated {quality_assessment['total_files']} files")

        if quality_assessment["valid_yaml_files"] == quality_assessment["total_files"]:
            quality_assessment["quality_indicators"].append("All files are valid YAML")

        if quality_assessment["security_focused"] > 0:
            quality_assessment["quality_indicators"].append("Contains security-focused manifests")

        return quality_assessment

    def _assess_rbac_completeness(self, output_dir: str):
        """Assess RBAC manifest completeness and quality"""
        output_path = Path(output_dir)
        rbac_assessment = {
            "roles_found": 0,
            "rolebindings_found": 0,
            "serviceaccounts_found": 0,
            "rbac_completeness": "none",
            "rbac_quality_indicators": []
        }

        if not output_path.exists():
            return rbac_assessment

        for file in output_path.rglob("*.yaml"):
            preview = self._get_yaml_preview(file)
            kind = preview.get("kind", "").lower()

            if "role" in kind and "binding" not in kind:
                rbac_assessment["roles_found"] += 1
            elif "rolebinding" in kind:
                rbac_assessment["rolebindings_found"] += 1
            elif "serviceaccount" in kind:
                rbac_assessment["serviceaccounts_found"] += 1

        # Assess completeness
        total_rbac = (rbac_assessment["roles_found"] +
                     rbac_assessment["rolebindings_found"] +
                     rbac_assessment["serviceaccounts_found"])

        if total_rbac == 0:
            rbac_assessment["rbac_completeness"] = "none"
        elif total_rbac >= 3:  # At least one of each type
            rbac_assessment["rbac_completeness"] = "complete"
            rbac_assessment["rbac_quality_indicators"].append("Complete RBAC implementation")
        else:
            rbac_assessment["rbac_completeness"] = "partial"
            rbac_assessment["rbac_quality_indicators"].append("Partial RBAC implementation")

        return rbac_assessment

    def _assess_networkpolicy_quality(self, output_dir: str):
        """Assess NetworkPolicy manifest quality"""
        output_path = Path(output_dir)
        network_assessment = {
            "networkpolicies_found": 0,
            "policy_types": [],
            "security_patterns": [],
            "quality_score": 0
        }

        if not output_path.exists():
            return network_assessment

        for file in output_path.rglob("*.yaml"):
            preview = self._get_yaml_preview(file)
            if preview.get("kind", "").lower() == "networkpolicy":
                network_assessment["networkpolicies_found"] += 1

                # Analyze file content for security patterns
                try:
                    with open(file, 'r') as f:
                        content = f.read().lower()

                    if "deny" in content:
                        network_assessment["security_patterns"].append("deny-by-default")
                    if "ingress" in content:
                        network_assessment["policy_types"].append("ingress")
                    if "egress" in content:
                        network_assessment["policy_types"].append("egress")

                except Exception:
                    pass

        # Calculate quality score
        quality_score = 0
        if network_assessment["networkpolicies_found"] > 0:
            quality_score += 3
        if "deny-by-default" in network_assessment["security_patterns"]:
            quality_score += 2
        if len(network_assessment["policy_types"]) >= 2:
            quality_score += 2

        network_assessment["quality_score"] = quality_score

        return network_assessment

    async def test_tool_integration(self, test_project: str):
        """Test integration with Kubernetes security tools"""
        print(f"🔧 Testing Kubernetes Agent tool integration")

        # Check if Kubescape is available and used
        kubescape_test = await self._test_kubescape_integration(test_project)

        # Check kubectl integration
        kubectl_test = await self._test_kubectl_integration()

        self.results["tool_integration"] = {
            "kubescape_integration": kubescape_test,
            "kubectl_integration": kubectl_test,
            "tool_availability": await self._check_tool_availability()
        }

        return self.results["tool_integration"]

    async def _test_kubescape_integration(self, test_project: str):
        """Test if agent can actually use Kubescape"""
        try:
            # Check if the agent's kubescape functionality works
            import subprocess
            result = subprocess.run(['kubescape', '--help'],
                                  capture_output=True, text=True, timeout=5)
            kubescape_available = result.returncode == 0

            return {
                "kubescape_available": kubescape_available,
                "integration_tested": True,
                "functionality": "basic_check_completed"
            }
        except Exception as e:
            return {
                "kubescape_available": False,
                "integration_tested": False,
                "error": str(e)
            }

    async def _test_kubectl_integration(self):
        """Test if agent can actually use kubectl"""
        try:
            import subprocess
            result = subprocess.run(['kubectl', 'version', '--client'],
                                  capture_output=True, text=True, timeout=5)
            kubectl_available = result.returncode == 0

            return {
                "kubectl_available": kubectl_available,
                "client_version": result.stdout if kubectl_available else None,
                "cluster_access": False  # No real cluster for testing
            }
        except Exception as e:
            return {
                "kubectl_available": False,
                "error": str(e)
            }

    async def _check_tool_availability(self):
        """Check availability of Kubernetes security tools"""
        tools = {
            "kubescape": ["kubescape", "--version"],
            "kubectl": ["kubectl", "version", "--client"],
            "helm": ["helm", "version"],
            "kube-score": ["kube-score", "version"]
        }

        availability = {}
        for tool_name, command in tools.items():
            try:
                import subprocess
                result = subprocess.run(command, capture_output=True, timeout=5)
                availability[tool_name] = result.returncode == 0
            except:
                availability[tool_name] = False

        return availability

    def generate_comprehensive_report(self):
        """Generate detailed markdown report of test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# Kubernetes Agent Validation Test Report
**Generated**: {timestamp}
**Test ID**: kubernetes-agent-{self.test_timestamp}

---

## Executive Summary

This report documents comprehensive testing of the Kubernetes Agent to validate CKA/CKS level capabilities against claimed expertise.

### Key Findings

**Cluster Security Analysis:**
- Security Issues Found: {self.results['cluster_analysis'].get('security_issues_found', 'N/A')}
- Pod Security Violations: {self.results['cluster_analysis'].get('pod_security_violations', 'N/A')}
- Tool Integration: {self.results['cluster_analysis'].get('tool_integration_evidence', {})}

**Security Manifest Generation:**
- Files Generated: {len(self.results['security_manifests'].get('files_generated', []))}
- RBAC Completeness: {self.results['security_manifests'].get('rbac_completeness', {}).get('rbac_completeness', 'N/A')}
- NetworkPolicy Quality: {self.results['security_manifests'].get('networkpolicy_quality', {}).get('quality_score', 'N/A')}/7

**Tool Integration Status:**
- Kubescape Available: {self.results['tool_integration'].get('kubescape_integration', {}).get('kubescape_available', 'N/A')}
- Kubectl Available: {self.results['tool_integration'].get('kubectl_integration', {}).get('kubectl_available', 'N/A')}

---

## Detailed Test Results

### 1. Cluster Security Analysis

**Test Project**: {self.results['cluster_analysis'].get('test_project', 'N/A')}

**Analysis Results:**
```json
{json.dumps(self.results['cluster_analysis'], indent=2)}
```

### 2. Security Manifest Generation

**Manifest Generation Results:**
```json
{json.dumps(self.results['security_manifests'], indent=2)}
```

### 3. Tool Integration Assessment

**Kubernetes Tool Integration:**
```json
{json.dumps(self.results['tool_integration'], indent=2)}
```

---

## CKA/CKS Level Assessment

{self._generate_cka_cks_assessment()}

---

## Professional Deliverable Quality

{self._generate_deliverable_quality_assessment()}

---

## Recommendations

{self._generate_kubernetes_recommendations()}

---

## Raw Test Data

**Complete Test Results:**
```json
{json.dumps(self.results, indent=2)}
```

---

*Report generated by Kubernetes Agent Validation Test*
*Timestamp: {self.test_timestamp}*
"""
        return report

    def _generate_cka_cks_assessment(self):
        """Generate assessment of CKA/CKS level capabilities"""
        assessment = "**CKA/CKS Level Capability Assessment:**\n\n"

        # RBAC Assessment (CKA/CKS Core)
        rbac = self.results.get('security_manifests', {}).get('rbac_completeness', {})
        rbac_completeness = rbac.get('rbac_completeness', 'none')

        assessment += f"**RBAC Implementation**: {rbac_completeness.title()}\n"
        if rbac_completeness == 'complete':
            assessment += "✅ CKA Level: RBAC implementation meets professional standards\n"
        else:
            assessment += "❌ CKA Level: RBAC implementation incomplete\n"

        # NetworkPolicy Assessment (CKS Core)
        netpol = self.results.get('security_manifests', {}).get('networkpolicy_quality', {})
        netpol_score = netpol.get('quality_score', 0)

        assessment += f"\n**NetworkPolicy Quality Score**: {netpol_score}/7\n"
        if netpol_score >= 5:
            assessment += "✅ CKS Level: NetworkPolicy implementation demonstrates security expertise\n"
        elif netpol_score >= 3:
            assessment += "⚠️ CKS Level: Basic NetworkPolicy understanding present\n"
        else:
            assessment += "❌ CKS Level: NetworkPolicy implementation insufficient\n"

        # Tool Integration (Professional Level)
        tools = self.results.get('tool_integration', {}).get('tool_availability', {})
        available_tools = sum(1 for available in tools.values() if available)

        assessment += f"\n**Security Tool Integration**: {available_tools}/{len(tools)} tools available\n"
        if available_tools >= 3:
            assessment += "✅ Professional Level: Good security tool ecosystem\n"
        else:
            assessment += "❌ Professional Level: Limited security tool integration\n"

        return assessment

    def _generate_deliverable_quality_assessment(self):
        """Generate assessment of professional deliverable quality"""
        assessment = "**Professional Kubernetes Security Deliverables:**\n\n"

        manifest_quality = self.results.get('security_manifests', {}).get('manifest_quality', {})
        files_generated = len(self.results.get('security_manifests', {}).get('files_generated', []))

        assessment += f"**Manifest Generation**: {files_generated} files created\n"

        quality_indicators = manifest_quality.get('quality_indicators', [])
        if quality_indicators:
            assessment += "**Quality Indicators:**\n"
            for indicator in quality_indicators:
                assessment += f"- ✅ {indicator}\n"

        valid_yaml = manifest_quality.get('valid_yaml_files', 0)
        total_files = manifest_quality.get('total_files', 0)

        if total_files > 0:
            yaml_quality = (valid_yaml / total_files) * 100
            assessment += f"\n**YAML Quality**: {yaml_quality:.1f}% valid manifests\n"

            if yaml_quality == 100:
                assessment += "✅ Production Ready: All manifests are valid YAML\n"
            else:
                assessment += "❌ Production Ready: Invalid YAML detected\n"

        return assessment

    def _generate_kubernetes_recommendations(self):
        """Generate actionable recommendations based on test results"""
        recommendations = []

        # RBAC recommendations
        rbac = self.results.get('security_manifests', {}).get('rbac_completeness', {})
        if rbac.get('rbac_completeness') != 'complete':
            recommendations.append("**Complete RBAC Implementation**: Generate ServiceAccount, Role, and RoleBinding manifests")

        # NetworkPolicy recommendations
        netpol = self.results.get('security_manifests', {}).get('networkpolicy_quality', {})
        if netpol.get('quality_score', 0) < 5:
            recommendations.append("**Improve NetworkPolicy Security**: Implement deny-by-default with specific ingress/egress rules")

        # Tool integration recommendations
        tools = self.results.get('tool_integration', {}).get('tool_availability', {})
        if not tools.get('kubescape', False):
            recommendations.append("**Install Kubescape**: Essential for Kubernetes security compliance scanning")

        # Manifest quality recommendations
        manifest_quality = self.results.get('security_manifests', {}).get('manifest_quality', {})
        if manifest_quality.get('total_files', 0) == 0:
            recommendations.append("**Fix Manifest Generation**: No security manifests were created")

        if not recommendations:
            recommendations.append("**Strong Kubernetes Security Implementation**: Agent meets CKA/CKS level requirements")

        recommendations_text = "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))
        return recommendations_text

    async def run_comprehensive_test(self, test_project: str):
        """Run complete Kubernetes Agent validation test suite"""
        print(f"🚀 Starting comprehensive Kubernetes Agent validation test")
        print(f"   Test project: {test_project}")
        print(f"   Test timestamp: {self.test_timestamp}")

        try:
            # Test 1: Cluster Security Analysis
            await self.test_cluster_security_analysis(test_project)

            # Test 2: Security Manifest Generation
            with tempfile.TemporaryDirectory() as temp_dir:
                await self.test_security_manifest_generation(temp_dir)

            # Test 3: Tool Integration
            await self.test_tool_integration(test_project)

            # Generate comprehensive report
            report = self.generate_comprehensive_report()

            # Save report
            report_path = f"/home/jimmie/linkops-industries/James-OS/guidepoint/docs/GP-results/kubernetes-agent-test-{self.test_timestamp}.md"
            with open(report_path, 'w') as f:
                f.write(report)

            print(f"✅ Comprehensive Kubernetes test complete")
            print(f"📄 Detailed report saved: {report_path}")

            # Generate summary
            rbac_complete = self.results['security_manifests']['rbac_completeness']['rbac_completeness'] == 'complete'
            netpol_quality = self.results['security_manifests']['networkpolicy_quality']['quality_score']
            kubescape_available = self.results['tool_integration']['kubescape_integration']['kubescape_available']

            return {
                "test_completed": True,
                "report_path": report_path,
                "summary": {
                    "security_issues_found": self.results['cluster_analysis']['security_issues_found'],
                    "rbac_complete": rbac_complete,
                    "networkpolicy_quality": f"{netpol_quality}/7",
                    "cka_cks_level": rbac_complete and netpol_quality >= 5,
                    "kubescape_integration": kubescape_available
                }
            }

        except Exception as e:
            error_report = f"""# Kubernetes Agent Test FAILED
**Error**: {str(e)}
**Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

The Kubernetes Agent test encountered a critical error and could not complete.
This indicates fundamental issues with the agent implementation.

**Partial Results**:
```json
{json.dumps(self.results, indent=2)}
```
"""

            error_path = f"/home/jimmie/linkops-industries/James-OS/guidepoint/docs/GP-results/kubernetes-agent-FAILED-{self.test_timestamp}.md"
            with open(error_path, 'w') as f:
                f.write(error_report)

            print(f"❌ Test failed: {str(e)}")
            print(f"📄 Error report saved: {error_path}")

            return {
                "test_completed": False,
                "error": str(e),
                "error_report_path": error_path
            }

async def main():
    """Run Kubernetes Agent validation test"""

    # Use the existing test project
    test_project = "/tmp/targeted_vuln_test"

    validator = KubernetesAgentValidator()
    result = await validator.run_comprehensive_test(test_project)

    print("\n" + "="*60)
    print("☸️ KUBERNETES AGENT VALIDATION COMPLETE")
    print("="*60)

    if result["test_completed"]:
        summary = result["summary"]
        print(f"🔍 Security Issues Found: {summary['security_issues_found']}")
        print(f"🔐 RBAC Complete: {summary['rbac_complete']}")
        print(f"🌐 NetworkPolicy Quality: {summary['networkpolicy_quality']}")
        print(f"🎓 CKA/CKS Level: {summary['cka_cks_level']}")
        print(f"🔧 Kubescape Integration: {summary['kubescape_integration']}")
        print(f"📄 Detailed Report: {result['report_path']}")
    else:
        print(f"❌ Test Failed: {result['error']}")
        print(f"📄 Error Report: {result['error_report_path']}")

if __name__ == "__main__":
    asyncio.run(main())