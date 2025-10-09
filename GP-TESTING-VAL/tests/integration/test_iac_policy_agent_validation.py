#!/usr/bin/env python3
"""
IaC/Policy Agent Validation Test
===============================

Systematic testing of IaC/Policy Agent capabilities to verify:
1. Actual infrastructure security analysis vs claimed capabilities
2. Real Terraform/CloudFormation scanning vs theoretical checks
3. Integration with Checkov/TFSec vs hardcoded patterns
4. Policy as Code generation quality

Test Results: Saved to docs/GP-results/iac-policy-agent-test-TIMESTAMP.md
"""

import sys
import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/jimmie/linkops-industries/James-OS/guidepoint')

from agents.iac_policy_agent.agent import IaCPolicyAgent

class IaCPolicyAgentValidator:
    """Comprehensive validation of IaC/Policy Agent capabilities"""

    def __init__(self):
        self.agent = IaCPolicyAgent()
        self.test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "test_metadata": {
                "timestamp": self.test_timestamp,
                "agent_tested": "IaCPolicyAgent",
                "test_purpose": "Validate infrastructure security analysis vs claims"
            },
            "infrastructure_analysis": {},
            "policy_generation": {},
            "tool_integration": {},
            "professional_grade": {},
            "overall_assessment": {}
        }

    async def test_infrastructure_analysis(self, test_project: str):
        """Test actual infrastructure security analysis capabilities"""
        print(f"🏗️ Testing IaC/Policy Agent infrastructure analysis on: {test_project}")

        analysis_result = await self.agent.analyze_infrastructure(test_project)

        # Analyze what was actually scanned and found
        security_findings = analysis_result.get("security_findings", [])
        iac_files = analysis_result.get("iac_files_scanned", [])

        self.results["infrastructure_analysis"] = {
            "test_project": test_project,
            "analysis_result": analysis_result,
            "security_findings_count": len(security_findings),
            "iac_files_scanned": len(iac_files),
            "file_coverage": self._analyze_iac_file_coverage(test_project, iac_files),
            "finding_analysis": self._analyze_security_findings(security_findings),
            "tool_integration_evidence": self._analyze_iac_tool_integration(analysis_result)
        }

        print(f"   Found {len(security_findings)} security findings")
        print(f"   Scanned {len(iac_files)} IaC files")
        return analysis_result

    def _analyze_iac_file_coverage(self, test_project: str, scanned_files: list):
        """Analyze IaC file coverage in the project"""
        project_path = Path(test_project)

        # Count actual IaC files in project
        iac_extensions = ['.tf', '.yaml', '.yml', '.json', '.dockerfile', '.Dockerfile']
        actual_iac_files = []

        if project_path.exists():
            for ext in iac_extensions:
                actual_iac_files.extend(list(project_path.rglob(f"*{ext}")))

        return {
            "files_scanned": len(scanned_files),
            "actual_iac_files_in_project": len(actual_iac_files),
            "coverage_percentage": (len(scanned_files) / max(1, len(actual_iac_files))) * 100,
            "file_types_found": [f.suffix for f in actual_iac_files],
            "scanned_file_paths": scanned_files[:5]  # First 5 for analysis
        }

    def _analyze_security_findings(self, findings: list):
        """Analyze the quality and specificity of security findings"""
        analysis = {
            "severity_distribution": {},
            "finding_types": {},
            "specificity_indicators": [],
            "quality_score": 0
        }

        for finding in findings:
            # Analyze severity distribution
            severity = finding.get("severity", "UNKNOWN")
            if severity not in analysis["severity_distribution"]:
                analysis["severity_distribution"][severity] = 0
            analysis["severity_distribution"][severity] += 1

            # Analyze finding types
            finding_type = finding.get("type", "unknown")
            if finding_type not in analysis["finding_types"]:
                analysis["finding_types"][finding_type] = 0
            analysis["finding_types"][finding_type] += 1

            # Check for specificity indicators
            if finding.get("file"):
                analysis["specificity_indicators"].append("file_location_provided")
            if finding.get("line"):
                analysis["specificity_indicators"].append("line_number_provided")
            if finding.get("remediation"):
                analysis["specificity_indicators"].append("remediation_guidance")

        # Calculate quality score
        quality_score = 0
        if len(findings) > 0:
            quality_score += 2
        if "file_location_provided" in analysis["specificity_indicators"]:
            quality_score += 2
        if "remediation_guidance" in analysis["specificity_indicators"]:
            quality_score += 2
        if len(analysis["severity_distribution"]) > 1:
            quality_score += 1

        analysis["quality_score"] = quality_score

        return analysis

    def _analyze_iac_tool_integration(self, analysis_result):
        """Check for evidence of actual IaC security tool integration"""
        evidence = {
            "checkov_integration": False,
            "tfsec_integration": False,
            "terrascan_integration": False,
            "custom_rules": False
        }

        # Convert result to string for pattern matching
        result_str = str(analysis_result).lower()

        if "checkov" in result_str:
            evidence["checkov_integration"] = True
        if "tfsec" in result_str:
            evidence["tfsec_integration"] = True
        if "terrascan" in result_str:
            evidence["terrascan_integration"] = True
        if "rule" in result_str or "policy" in result_str:
            evidence["custom_rules"] = True

        return evidence

    async def test_policy_generation(self, output_dir: str):
        """Test Policy as Code generation capabilities"""
        print(f"📋 Testing IaC/Policy Agent policy generation to: {output_dir}")

        policy_result = await self.agent.create_security_policies(output_dir)

        # Analyze generated policies
        generated_policies = self._analyze_generated_policies(output_dir)

        self.results["policy_generation"] = {
            "output_directory": output_dir,
            "generation_result": policy_result,
            "policies_generated": generated_policies,
            "policy_quality": self._assess_policy_quality(output_dir),
            "opa_compliance": self._assess_opa_compliance(output_dir),
            "kyverno_compliance": self._assess_kyverno_compliance(output_dir)
        }

        print(f"   Generated {len(generated_policies)} policy files")
        return policy_result

    def _analyze_generated_policies(self, output_dir: str):
        """Analyze what policy files were actually generated"""
        output_path = Path(output_dir)
        generated_policies = []

        if output_path.exists():
            policy_extensions = ['.yaml', '.yml', '.json', '.rego']
            for ext in policy_extensions:
                for file in output_path.rglob(f"*{ext}"):
                    if file.is_file():
                        generated_policies.append({
                            "filename": str(file.relative_to(output_path)),
                            "size_bytes": file.stat().st_size,
                            "extension": ext,
                            "content_preview": self._get_policy_preview(file)
                        })

        return generated_policies

    def _get_policy_preview(self, file_path: Path):
        """Get a preview of policy file content for analysis"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            preview = {
                "line_count": len(content.split('\n')),
                "policy_keywords": [],
                "framework_indicators": []
            }

            content_lower = content.lower()

            # Check for policy keywords
            policy_keywords = ["allow", "deny", "rule", "policy", "violation", "match"]
            for keyword in policy_keywords:
                if keyword in content_lower:
                    preview["policy_keywords"].append(keyword)

            # Check for framework indicators
            frameworks = {
                "opa": ["rego", "package", "import data"],
                "kyverno": ["apiversion: kyverno.io", "policy", "validate"],
                "gatekeeper": ["constrainttemplate", "gatekeeper"]
            }

            for framework, indicators in frameworks.items():
                for indicator in indicators:
                    if indicator in content_lower:
                        preview["framework_indicators"].append(framework)

            return preview

        except Exception as e:
            return {
                "error": str(e),
                "readable": False
            }

    def _assess_policy_quality(self, output_dir: str):
        """Assess the quality and completeness of generated policies"""
        output_path = Path(output_dir)
        quality_assessment = {
            "total_policy_files": 0,
            "valid_policy_files": 0,
            "policy_frameworks": [],
            "quality_indicators": []
        }

        if not output_path.exists():
            quality_assessment["quality_indicators"].append("Output directory not created")
            return quality_assessment

        policy_extensions = ['.yaml', '.yml', '.json', '.rego']
        for ext in policy_extensions:
            for file in output_path.rglob(f"*{ext}"):
                quality_assessment["total_policy_files"] += 1

                preview = self._get_policy_preview(file)
                if not preview.get("error"):
                    quality_assessment["valid_policy_files"] += 1

                    frameworks = preview.get("framework_indicators", [])
                    quality_assessment["policy_frameworks"].extend(frameworks)

        # Remove duplicates
        quality_assessment["policy_frameworks"] = list(set(quality_assessment["policy_frameworks"]))

        # Quality indicators
        if quality_assessment["total_policy_files"] > 0:
            quality_assessment["quality_indicators"].append(f"Generated {quality_assessment['total_policy_files']} policy files")

        if quality_assessment["valid_policy_files"] == quality_assessment["total_policy_files"]:
            quality_assessment["quality_indicators"].append("All policy files are readable")

        if quality_assessment["policy_frameworks"]:
            quality_assessment["quality_indicators"].append(f"Supports frameworks: {', '.join(quality_assessment['policy_frameworks'])}")

        return quality_assessment

    def _assess_opa_compliance(self, output_dir: str):
        """Assess Open Policy Agent (OPA) compliance"""
        output_path = Path(output_dir)
        opa_assessment = {
            "rego_files_found": 0,
            "package_declarations": 0,
            "rule_definitions": 0,
            "opa_compliance": False
        }

        if output_path.exists():
            for file in output_path.rglob("*.rego"):
                opa_assessment["rego_files_found"] += 1

                try:
                    with open(file, 'r') as f:
                        content = f.read().lower()

                    if "package" in content:
                        opa_assessment["package_declarations"] += 1
                    if any(rule_word in content for rule_word in ["allow", "deny", "violation"]):
                        opa_assessment["rule_definitions"] += 1

                except Exception:
                    pass

        # Determine OPA compliance
        opa_assessment["opa_compliance"] = (
            opa_assessment["rego_files_found"] > 0 and
            opa_assessment["package_declarations"] > 0 and
            opa_assessment["rule_definitions"] > 0
        )

        return opa_assessment

    def _assess_kyverno_compliance(self, output_dir: str):
        """Assess Kyverno policy compliance"""
        output_path = Path(output_dir)
        kyverno_assessment = {
            "kyverno_policies_found": 0,
            "policy_rules": 0,
            "validation_rules": 0,
            "kyverno_compliance": False
        }

        if output_path.exists():
            for file in output_path.rglob("*.yaml"):
                try:
                    with open(file, 'r') as f:
                        content = f.read().lower()

                    if "kyverno.io" in content:
                        kyverno_assessment["kyverno_policies_found"] += 1

                        if "rules:" in content:
                            kyverno_assessment["policy_rules"] += 1
                        if "validate:" in content:
                            kyverno_assessment["validation_rules"] += 1

                except Exception:
                    pass

        # Determine Kyverno compliance
        kyverno_assessment["kyverno_compliance"] = (
            kyverno_assessment["kyverno_policies_found"] > 0 and
            kyverno_assessment["policy_rules"] > 0
        )

        return kyverno_assessment

    async def test_tool_integration(self, test_project: str):
        """Test integration with IaC security tools"""
        print(f"🔧 Testing IaC/Policy Agent tool integration")

        # Check tool availability and integration
        tool_availability = await self._check_iac_tool_availability()

        # Test Checkov integration if available
        checkov_test = await self._test_checkov_integration(test_project)

        self.results["tool_integration"] = {
            "tool_availability": tool_availability,
            "checkov_integration": checkov_test,
            "integration_summary": self._summarize_tool_integration(tool_availability, checkov_test)
        }

        return self.results["tool_integration"]

    async def _check_iac_tool_availability(self):
        """Check availability of IaC security tools"""
        tools = {
            "checkov": ["checkov", "--version"],
            "tfsec": ["tfsec", "--version"],
            "terrascan": ["terrascan", "version"],
            "terraform": ["terraform", "--version"]
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

    async def _test_checkov_integration(self, test_project: str):
        """Test if agent can actually use Checkov"""
        try:
            import subprocess

            # Check if Checkov is available
            version_result = subprocess.run(['checkov', '--version'],
                                          capture_output=True, text=True, timeout=5)
            checkov_available = version_result.returncode == 0

            integration_test = {
                "checkov_available": checkov_available,
                "version_info": version_result.stdout if checkov_available else None,
                "integration_tested": False
            }

            if checkov_available:
                # Try running Checkov on test project
                try:
                    scan_result = subprocess.run(
                        ['checkov', '-d', test_project, '--compact', '--quiet'],
                        capture_output=True, text=True, timeout=30
                    )
                    integration_test["integration_tested"] = True
                    integration_test["scan_successful"] = scan_result.returncode in [0, 1]  # 1 = found issues
                    integration_test["output_lines"] = len(scan_result.stdout.split('\n'))
                except Exception as e:
                    integration_test["scan_error"] = str(e)

            return integration_test

        except Exception as e:
            return {
                "checkov_available": False,
                "error": str(e)
            }

    def _summarize_tool_integration(self, availability: dict, checkov_test: dict):
        """Summarize tool integration status"""
        available_tools = sum(1 for available in availability.values() if available)
        total_tools = len(availability)

        summary = {
            "tools_available": f"{available_tools}/{total_tools}",
            "checkov_functional": checkov_test.get("scan_successful", False),
            "integration_score": 0
        }

        # Calculate integration score
        score = 0
        if available_tools > 0:
            score += 2
        if checkov_test.get("checkov_available", False):
            score += 2
        if checkov_test.get("scan_successful", False):
            score += 3

        summary["integration_score"] = score

        return summary

    def generate_comprehensive_report(self):
        """Generate detailed markdown report of test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# IaC/Policy Agent Validation Test Report
**Generated**: {timestamp}
**Test ID**: iac-policy-agent-{self.test_timestamp}

---

## Executive Summary

This report documents comprehensive testing of the IaC/Policy Agent to validate infrastructure security analysis capabilities against claimed functionality.

### Key Findings

**Infrastructure Analysis:**
- Security Findings: {self.results['infrastructure_analysis'].get('security_findings_count', 'N/A')}
- IaC Files Scanned: {self.results['infrastructure_analysis'].get('iac_files_scanned', 'N/A')}
- File Coverage: {self.results['infrastructure_analysis'].get('file_coverage', {}).get('coverage_percentage', 'N/A'):.1f}%
- Tool Integration: {self.results['infrastructure_analysis'].get('tool_integration_evidence', {})}

**Policy Generation:**
- Policies Generated: {len(self.results['policy_generation'].get('policies_generated', []))}
- OPA Compliance: {self.results['policy_generation'].get('opa_compliance', {}).get('opa_compliance', 'N/A')}
- Kyverno Compliance: {self.results['policy_generation'].get('kyverno_compliance', {}).get('kyverno_compliance', 'N/A')}

**Tool Integration Status:**
- Available Tools: {self.results['tool_integration'].get('integration_summary', {}).get('tools_available', 'N/A')}
- Checkov Functional: {self.results['tool_integration'].get('integration_summary', {}).get('checkov_functional', 'N/A')}
- Integration Score: {self.results['tool_integration'].get('integration_summary', {}).get('integration_score', 'N/A')}/7

---

## Detailed Test Results

### 1. Infrastructure Security Analysis

**Test Project**: {self.results['infrastructure_analysis'].get('test_project', 'N/A')}

**Analysis Results:**
```json
{json.dumps(self.results['infrastructure_analysis'], indent=2)}
```

### 2. Policy as Code Generation

**Policy Generation Results:**
```json
{json.dumps(self.results['policy_generation'], indent=2)}
```

### 3. Tool Integration Assessment

**IaC Security Tool Integration:**
```json
{json.dumps(self.results['tool_integration'], indent=2)}
```

---

## Infrastructure Security Assessment

{self._generate_infrastructure_assessment()}

---

## Policy as Code Quality Assessment

{self._generate_policy_assessment()}

---

## Recommendations

{self._generate_iac_recommendations()}

---

## Raw Test Data

**Complete Test Results:**
```json
{json.dumps(self.results, indent=2)}
```

---

*Report generated by IaC/Policy Agent Validation Test*
*Timestamp: {self.test_timestamp}*
"""
        return report

    def _generate_infrastructure_assessment(self):
        """Generate assessment of infrastructure security analysis capabilities"""
        assessment = "**Infrastructure Security Analysis Capability:**\n\n"

        analysis = self.results.get('infrastructure_analysis', {})
        findings_count = analysis.get('security_findings_count', 0)
        files_scanned = analysis.get('iac_files_scanned', 0)
        coverage = analysis.get('file_coverage', {})

        assessment += f"**Security Findings**: {findings_count} issues identified\n"
        assessment += f"**File Coverage**: {files_scanned} files scanned ({coverage.get('coverage_percentage', 0):.1f}% of IaC files)\n"

        # Tool integration assessment
        tool_evidence = analysis.get('tool_integration_evidence', {})
        integrated_tools = [tool for tool, integrated in tool_evidence.items() if integrated]

        if integrated_tools:
            assessment += f"**Integrated Tools**: {', '.join(integrated_tools)}\n"
            assessment += "✅ Security Tool Integration: Present\n"
        else:
            assessment += "❌ Security Tool Integration: No evidence of tool integration\n"

        # Finding quality assessment
        finding_analysis = analysis.get('finding_analysis', {})
        quality_score = finding_analysis.get('quality_score', 0)

        assessment += f"\n**Finding Quality Score**: {quality_score}/7\n"
        if quality_score >= 5:
            assessment += "✅ Professional Grade: High-quality security findings\n"
        elif quality_score >= 3:
            assessment += "⚠️ Professional Grade: Adequate security findings\n"
        else:
            assessment += "❌ Professional Grade: Poor quality security findings\n"

        return assessment

    def _generate_policy_assessment(self):
        """Generate assessment of Policy as Code generation quality"""
        assessment = "**Policy as Code Generation Quality:**\n\n"

        policy_gen = self.results.get('policy_generation', {})
        policies_count = len(policy_gen.get('policies_generated', []))

        assessment += f"**Policies Generated**: {policies_count} files\n"

        if policies_count == 0:
            assessment += "❌ Policy Generation: No policies created\n"
            return assessment

        # Framework compliance
        opa_compliance = policy_gen.get('opa_compliance', {}).get('opa_compliance', False)
        kyverno_compliance = policy_gen.get('kyverno_compliance', {}).get('kyverno_compliance', False)

        assessment += f"**OPA Compliance**: {'✅ Yes' if opa_compliance else '❌ No'}\n"
        assessment += f"**Kyverno Compliance**: {'✅ Yes' if kyverno_compliance else '❌ No'}\n"

        if opa_compliance or kyverno_compliance:
            assessment += "✅ Professional Grade: Policy frameworks properly implemented\n"
        else:
            assessment += "❌ Professional Grade: No standard policy frameworks detected\n"

        # Policy quality
        quality = policy_gen.get('policy_quality', {})
        frameworks = quality.get('policy_frameworks', [])

        if frameworks:
            assessment += f"**Supported Frameworks**: {', '.join(frameworks)}\n"

        return assessment

    def _generate_iac_recommendations(self):
        """Generate actionable recommendations based on test results"""
        recommendations = []

        # Tool integration recommendations
        tool_integration = self.results.get('tool_integration', {})
        available_tools = tool_integration.get('tool_availability', {})

        if not available_tools.get('checkov', False):
            recommendations.append("**Install Checkov**: Essential for comprehensive IaC security scanning")

        if not available_tools.get('tfsec', False):
            recommendations.append("**Install TFSec**: Terraform-specific security scanner")

        # Analysis capability recommendations
        analysis = self.results.get('infrastructure_analysis', {})
        coverage = analysis.get('file_coverage', {}).get('coverage_percentage', 0)

        if coverage < 50:
            recommendations.append("**Improve File Coverage**: Currently scanning only {:.1f}% of IaC files".format(coverage))

        # Policy generation recommendations
        policy_gen = self.results.get('policy_generation', {})
        if len(policy_gen.get('policies_generated', [])) == 0:
            recommendations.append("**Fix Policy Generation**: No policies were created")

        opa_compliance = policy_gen.get('opa_compliance', {}).get('opa_compliance', False)
        kyverno_compliance = policy_gen.get('kyverno_compliance', {}).get('kyverno_compliance', False)

        if not opa_compliance and not kyverno_compliance:
            recommendations.append("**Implement Policy Frameworks**: Add OPA/Kyverno policy generation")

        if not recommendations:
            recommendations.append("**Strong IaC Security Implementation**: Agent meets infrastructure security requirements")

        recommendations_text = "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))
        return recommendations_text

    async def run_comprehensive_test(self, test_project: str):
        """Run complete IaC/Policy Agent validation test suite"""
        print(f"🚀 Starting comprehensive IaC/Policy Agent validation test")
        print(f"   Test project: {test_project}")
        print(f"   Test timestamp: {self.test_timestamp}")

        try:
            # Test 1: Infrastructure Analysis
            await self.test_infrastructure_analysis(test_project)

            # Test 2: Policy Generation
            with tempfile.TemporaryDirectory() as temp_dir:
                await self.test_policy_generation(temp_dir)

            # Test 3: Tool Integration
            await self.test_tool_integration(test_project)

            # Generate comprehensive report
            report = self.generate_comprehensive_report()

            # Save report
            report_path = f"/home/jimmie/linkops-industries/James-OS/guidepoint/docs/GP-results/iac-policy-agent-test-{self.test_timestamp}.md"
            with open(report_path, 'w') as f:
                f.write(report)

            print(f"✅ Comprehensive IaC/Policy test complete")
            print(f"📄 Detailed report saved: {report_path}")

            # Generate summary
            findings_count = self.results['infrastructure_analysis']['security_findings_count']
            policies_generated = len(self.results['policy_generation']['policies_generated'])
            tool_integration_score = self.results['tool_integration']['integration_summary']['integration_score']

            return {
                "test_completed": True,
                "report_path": report_path,
                "summary": {
                    "security_findings": findings_count,
                    "policies_generated": policies_generated,
                    "tool_integration_score": f"{tool_integration_score}/7",
                    "iac_capability": findings_count > 0 or policies_generated > 0,
                    "professional_grade": tool_integration_score >= 5
                }
            }

        except Exception as e:
            error_report = f"""# IaC/Policy Agent Test FAILED
**Error**: {str(e)}
**Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

The IaC/Policy Agent test encountered a critical error and could not complete.
This indicates fundamental issues with the agent implementation.

**Partial Results**:
```json
{json.dumps(self.results, indent=2)}
```
"""

            error_path = f"/home/jimmie/linkops-industries/James-OS/guidepoint/docs/GP-results/iac-policy-agent-FAILED-{self.test_timestamp}.md"
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
    """Run IaC/Policy Agent validation test"""

    # Use the existing test project
    test_project = "/tmp/targeted_vuln_test"

    validator = IaCPolicyAgentValidator()
    result = await validator.run_comprehensive_test(test_project)

    print("\n" + "="*60)
    print("🏗️ IAC/POLICY AGENT VALIDATION COMPLETE")
    print("="*60)

    if result["test_completed"]:
        summary = result["summary"]
        print(f"🔍 Security Findings: {summary['security_findings']}")
        print(f"📋 Policies Generated: {summary['policies_generated']}")
        print(f"🔧 Tool Integration: {summary['tool_integration_score']}")
        print(f"🏗️ IaC Capability: {summary['iac_capability']}")
        print(f"👔 Professional Grade: {summary['professional_grade']}")
        print(f"📄 Detailed Report: {result['report_path']}")
    else:
        print(f"❌ Test Failed: {result['error']}")
        print(f"📄 Error Report: {result['error_report_path']}")

if __name__ == "__main__":
    asyncio.run(main())