#!/usr/bin/env python3
"""
Secrets Agent Validation Test
============================

Systematic testing of Secrets Agent capabilities to verify:
1. Actual hardcoded secret detection vs claimed GitLeaks integration
2. Real secret vulnerability assessment vs theoretical patterns
3. GitLeaks tool integration vs hardcoded detection
4. Professional secret remediation guidance

Test Results: Saved to docs/GP-results/secrets-agent-test-TIMESTAMP.md
"""

import sys
import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/jimmie/linkops-industries/James-OS/guidepoint')

from agents.secrets_agent.agent import SecretsAgent

class SecretsAgentValidator:
    """Comprehensive validation of Secrets Agent capabilities"""

    def __init__(self):
        self.agent = SecretsAgent()
        self.test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "test_metadata": {
                "timestamp": self.test_timestamp,
                "agent_tested": "SecretsAgent",
                "test_purpose": "Validate hardcoded secret detection vs claims"
            },
            "secret_detection": {},
            "secret_remediation": {},
            "tool_integration": {},
            "professional_grade": {}
        }

    async def test_secret_detection(self, test_project: str):
        """Test actual secret detection capabilities"""
        print(f"🔐 Testing Secrets Agent secret detection on: {test_project}")

        # Create test files with known secrets for validation
        test_secrets_dir = await self._create_test_secrets(test_project)

        detection_result = await self.agent.analyze_secrets(test_project)

        # Analyze what was actually found
        secrets_found = detection_result.get("secrets_found", [])

        self.results["secret_detection"] = {
            "test_project": test_project,
            "test_secrets_created": test_secrets_dir,
            "detection_result": detection_result,
            "secrets_found": len(secrets_found),
            "secret_details": secrets_found[:5],  # First 5 for analysis
            "detection_accuracy": self._analyze_detection_accuracy(secrets_found, test_secrets_dir),
            "tool_integration_evidence": self._analyze_secret_tool_integration(detection_result),
            "risk_assessment_quality": self._analyze_risk_assessment(detection_result)
        }

        print(f"   Found {len(secrets_found)} secrets")
        return detection_result

    async def _create_test_secrets(self, test_project: str):
        """Create test files with known secrets for detection validation"""
        test_secrets = {
            "api_key_test.py": 'API_KEY = "sk-1234567890abcdef1234567890abcdef"',
            "aws_credentials.json": '{"aws_access_key_id": "AKIAIOSFODNN7EXAMPLE", "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"}',
            "database_config.yml": 'password: "super_secret_password_123"',
            "github_token.env": 'GITHUB_TOKEN=ghp_1234567890abcdef1234567890abcdef12345678',
            "private_key.pem": '''-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC7...
-----END PRIVATE KEY-----'''
        }

        test_dir = Path(test_project) / "test_secrets"
        test_dir.mkdir(exist_ok=True)

        created_files = []
        for filename, content in test_secrets.items():
            file_path = test_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)
            created_files.append(str(file_path))

        return {
            "test_directory": str(test_dir),
            "files_created": created_files,
            "secret_types": list(test_secrets.keys())
        }

    def _analyze_detection_accuracy(self, secrets_found: list, test_secrets_info: dict):
        """Analyze detection accuracy against known test secrets"""
        test_files = test_secrets_info.get("files_created", [])
        test_dir = test_secrets_info.get("test_directory", "")

        accuracy_analysis = {
            "test_secrets_created": len(test_files),
            "test_secrets_detected": 0,
            "false_positives": 0,
            "detection_rate": 0.0,
            "detected_in_test_files": []
        }

        for secret in secrets_found:
            secret_file = secret.get("file", "")

            # Check if detected secret is in our test files
            if test_dir in secret_file:
                accuracy_analysis["test_secrets_detected"] += 1
                accuracy_analysis["detected_in_test_files"].append(secret_file)
            else:
                # Secrets found outside test files (could be legitimate or false positives)
                accuracy_analysis["false_positives"] += 1

        # Calculate detection rate
        if accuracy_analysis["test_secrets_created"] > 0:
            accuracy_analysis["detection_rate"] = (
                accuracy_analysis["test_secrets_detected"] /
                accuracy_analysis["test_secrets_created"]
            ) * 100

        return accuracy_analysis

    def _analyze_secret_tool_integration(self, detection_result):
        """Check for evidence of actual secret detection tool integration"""
        evidence = {
            "gitleaks_integration": False,
            "trufflesuite_integration": False,
            "detect_secrets_integration": False,
            "custom_patterns": False
        }

        # Convert result to string for pattern matching
        result_str = str(detection_result).lower()

        if "gitleaks" in result_str:
            evidence["gitleaks_integration"] = True
        if "truffle" in result_str:
            evidence["trufflesuite_integration"] = True
        if "detect-secrets" in result_str or "detect_secrets" in result_str:
            evidence["detect_secrets_integration"] = True
        if "pattern" in result_str or "rule" in result_str:
            evidence["custom_patterns"] = True

        return evidence

    def _analyze_risk_assessment(self, detection_result):
        """Analyze the quality of risk assessment and business impact analysis"""
        risk_assessment = detection_result.get("risk_assessment", {})
        compliance_status = detection_result.get("compliance_status", {})

        analysis = {
            "risk_assessment_present": bool(risk_assessment),
            "compliance_analysis_present": bool(compliance_status),
            "business_impact_calculated": bool(risk_assessment.get("business_impact")),
            "risk_scoring": bool(risk_assessment.get("risk_score")),
            "quality_score": 0
        }

        # Calculate quality score
        score = 0
        if analysis["risk_assessment_present"]:
            score += 2
        if analysis["compliance_analysis_present"]:
            score += 2
        if analysis["business_impact_calculated"]:
            score += 2
        if analysis["risk_scoring"]:
            score += 1

        analysis["quality_score"] = score

        return analysis

    async def test_secret_remediation(self, test_project: str):
        """Test secret remediation capabilities"""
        print(f"🔧 Testing Secrets Agent remediation capabilities")

        remediation_result = await self.agent.execute_autonomous_remediation(test_project)

        # Analyze remediation actions and quality
        self.results["secret_remediation"] = {
            "test_project": test_project,
            "remediation_result": remediation_result,
            "actions_taken": len(remediation_result.get("actions_taken", [])),
            "manual_actions_required": len(remediation_result.get("manual_actions_required", [])),
            "remediation_quality": self._analyze_remediation_quality(remediation_result),
            "gitignore_generation": self._analyze_gitignore_generation(remediation_result),
            "env_template_generation": self._analyze_env_template_generation(remediation_result)
        }

        print(f"   Automated actions: {self.results['secret_remediation']['actions_taken']}")
        print(f"   Manual actions required: {self.results['secret_remediation']['manual_actions_required']}")
        return remediation_result

    def _analyze_remediation_quality(self, remediation_result):
        """Analyze the quality and comprehensiveness of remediation actions"""
        actions_taken = remediation_result.get("actions_taken", [])
        manual_actions = remediation_result.get("manual_actions_required", [])

        quality_analysis = {
            "automated_actions_count": len(actions_taken),
            "manual_actions_count": len(manual_actions),
            "remediation_scope": "none",
            "quality_indicators": []
        }

        total_actions = quality_analysis["automated_actions_count"] + quality_analysis["manual_actions_count"]

        if total_actions == 0:
            quality_analysis["remediation_scope"] = "none"
            quality_analysis["quality_indicators"].append("No remediation actions provided")
        elif total_actions < 3:
            quality_analysis["remediation_scope"] = "basic"
            quality_analysis["quality_indicators"].append("Basic remediation guidance")
        else:
            quality_analysis["remediation_scope"] = "comprehensive"
            quality_analysis["quality_indicators"].append("Comprehensive remediation plan")

        # Check for specific remediation types
        actions_str = str(actions_taken).lower()
        if "gitignore" in actions_str:
            quality_analysis["quality_indicators"].append("GitIgnore pattern generation")
        if "environment" in actions_str or "env" in actions_str:
            quality_analysis["quality_indicators"].append("Environment variable template")
        if manual_actions:
            quality_analysis["quality_indicators"].append("Manual intervention guidance")

        return quality_analysis

    def _analyze_gitignore_generation(self, remediation_result):
        """Analyze GitIgnore pattern generation quality"""
        actions_taken = remediation_result.get("actions_taken", [])

        gitignore_analysis = {
            "gitignore_generated": False,
            "patterns_count": 0,
            "pattern_quality": "none"
        }

        for action in actions_taken:
            if isinstance(action, dict) and "gitignore" in str(action).lower():
                gitignore_analysis["gitignore_generated"] = True

                details = action.get("details", [])
                if isinstance(details, list):
                    gitignore_analysis["patterns_count"] = len(details)

                    if gitignore_analysis["patterns_count"] > 10:
                        gitignore_analysis["pattern_quality"] = "comprehensive"
                    elif gitignore_analysis["patterns_count"] > 5:
                        gitignore_analysis["pattern_quality"] = "adequate"
                    else:
                        gitignore_analysis["pattern_quality"] = "basic"

        return gitignore_analysis

    def _analyze_env_template_generation(self, remediation_result):
        """Analyze environment variable template generation quality"""
        actions_taken = remediation_result.get("actions_taken", [])

        env_analysis = {
            "env_template_generated": False,
            "variables_count": 0,
            "template_quality": "none"
        }

        for action in actions_taken:
            if isinstance(action, dict) and ("environment" in str(action).lower() or "env" in str(action).lower()):
                env_analysis["env_template_generated"] = True

                details = action.get("details", [])
                if isinstance(details, list):
                    env_analysis["variables_count"] = len(details)

                    if env_analysis["variables_count"] > 5:
                        env_analysis["template_quality"] = "comprehensive"
                    elif env_analysis["variables_count"] > 2:
                        env_analysis["template_quality"] = "adequate"
                    else:
                        env_analysis["template_quality"] = "basic"

        return env_analysis

    async def test_tool_integration(self, test_project: str):
        """Test integration with secret detection tools"""
        print(f"🔧 Testing Secrets Agent tool integration")

        # Check tool availability
        tool_availability = await self._check_secret_tool_availability()

        # Test GitLeaks integration specifically
        gitleaks_test = await self._test_gitleaks_integration(test_project)

        self.results["tool_integration"] = {
            "tool_availability": tool_availability,
            "gitleaks_integration": gitleaks_test,
            "integration_summary": self._summarize_secret_tool_integration(tool_availability, gitleaks_test)
        }

        return self.results["tool_integration"]

    async def _check_secret_tool_availability(self):
        """Check availability of secret detection tools"""
        tools = {
            "gitleaks": ["gitleaks", "version"],
            "trufflesuite": ["truffle", "--version"],
            "detect-secrets": ["detect-secrets", "--version"],
            "git": ["git", "--version"]
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

    async def _test_gitleaks_integration(self, test_project: str):
        """Test if agent can actually use GitLeaks"""
        try:
            import subprocess

            # Check if GitLeaks is available
            version_result = subprocess.run(['gitleaks', 'version'],
                                          capture_output=True, text=True, timeout=5)
            gitleaks_available = version_result.returncode == 0

            integration_test = {
                "gitleaks_available": gitleaks_available,
                "version_info": version_result.stdout if gitleaks_available else None,
                "scan_tested": False
            }

            if gitleaks_available:
                # Try running GitLeaks on test project
                try:
                    scan_result = subprocess.run(
                        ['gitleaks', 'detect', '--source', test_project, '--no-git'],
                        capture_output=True, text=True, timeout=30
                    )
                    integration_test["scan_tested"] = True
                    integration_test["scan_exit_code"] = scan_result.returncode
                    integration_test["scan_output_lines"] = len(scan_result.stdout.split('\n'))
                    integration_test["scan_successful"] = scan_result.returncode in [0, 1]  # 1 = found secrets
                except Exception as e:
                    integration_test["scan_error"] = str(e)

            return integration_test

        except Exception as e:
            return {
                "gitleaks_available": False,
                "error": str(e)
            }

    def _summarize_secret_tool_integration(self, availability: dict, gitleaks_test: dict):
        """Summarize secret detection tool integration status"""
        available_tools = sum(1 for available in availability.values() if available)
        total_tools = len(availability)

        summary = {
            "tools_available": f"{available_tools}/{total_tools}",
            "gitleaks_functional": gitleaks_test.get("scan_successful", False),
            "integration_score": 0
        }

        # Calculate integration score
        score = 0
        if available_tools > 0:
            score += 2
        if availability.get("gitleaks", False):
            score += 3
        if gitleaks_test.get("scan_successful", False):
            score += 2

        summary["integration_score"] = score

        return summary

    def generate_comprehensive_report(self):
        """Generate detailed markdown report of test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# Secrets Agent Validation Test Report
**Generated**: {timestamp}
**Test ID**: secrets-agent-{self.test_timestamp}

---

## Executive Summary

This report documents comprehensive testing of the Secrets Agent to validate hardcoded secret detection capabilities against claimed GitLeaks integration.

### Key Findings

**Secret Detection:**
- Secrets Found: {self.results['secret_detection'].get('secrets_found', 'N/A')}
- Detection Accuracy: {self.results['secret_detection'].get('detection_accuracy', {}).get('detection_rate', 'N/A'):.1f}%
- Tool Integration: {self.results['secret_detection'].get('tool_integration_evidence', {})}

**Secret Remediation:**
- Automated Actions: {self.results['secret_remediation'].get('actions_taken', 'N/A')}
- Manual Actions Required: {self.results['secret_remediation'].get('manual_actions_required', 'N/A')}
- Remediation Scope: {self.results['secret_remediation'].get('remediation_quality', {}).get('remediation_scope', 'N/A')}

**Tool Integration Status:**
- Available Tools: {self.results['tool_integration'].get('integration_summary', {}).get('tools_available', 'N/A')}
- GitLeaks Functional: {self.results['tool_integration'].get('integration_summary', {}).get('gitleaks_functional', 'N/A')}
- Integration Score: {self.results['tool_integration'].get('integration_summary', {}).get('integration_score', 'N/A')}/7

---

## Detailed Test Results

### 1. Secret Detection Analysis

**Test Project**: {self.results['secret_detection'].get('test_project', 'N/A')}

**Detection Results:**
```json
{json.dumps(self.results['secret_detection'], indent=2)}
```

### 2. Secret Remediation Analysis

**Remediation Results:**
```json
{json.dumps(self.results['secret_remediation'], indent=2)}
```

### 3. Tool Integration Assessment

**Secret Detection Tool Integration:**
```json
{json.dumps(self.results['tool_integration'], indent=2)}
```

---

## Secret Detection Capability Assessment

{self._generate_detection_capability_assessment()}

---

## Secret Remediation Quality Assessment

{self._generate_remediation_quality_assessment()}

---

## Recommendations

{self._generate_secrets_recommendations()}

---

## Raw Test Data

**Complete Test Results:**
```json
{json.dumps(self.results, indent=2)}
```

---

*Report generated by Secrets Agent Validation Test*
*Timestamp: {self.test_timestamp}*
"""
        return report

    def _generate_detection_capability_assessment(self):
        """Generate assessment of secret detection capabilities"""
        assessment = "**Secret Detection Capability Assessment:**\n\n"

        detection = self.results.get('secret_detection', {})
        secrets_found = detection.get('secrets_found', 0)
        accuracy = detection.get('detection_accuracy', {})

        assessment += f"**Secrets Detected**: {secrets_found} hardcoded secrets found\n"
        assessment += f"**Detection Accuracy**: {accuracy.get('detection_rate', 0):.1f}% of test secrets detected\n"

        # Tool integration assessment
        tool_evidence = detection.get('tool_integration_evidence', {})
        if tool_evidence.get('gitleaks_integration'):
            assessment += "✅ GitLeaks Integration: Detected\n"
        else:
            assessment += "❌ GitLeaks Integration: No evidence of GitLeaks usage\n"

        # Risk assessment quality
        risk_quality = detection.get('risk_assessment_quality', {})
        risk_score = risk_quality.get('quality_score', 0)

        assessment += f"\n**Risk Assessment Quality**: {risk_score}/7\n"
        if risk_score >= 5:
            assessment += "✅ Professional Grade: Comprehensive risk assessment\n"
        elif risk_score >= 3:
            assessment += "⚠️ Professional Grade: Basic risk assessment\n"
        else:
            assessment += "❌ Professional Grade: No risk assessment provided\n"

        return assessment

    def _generate_remediation_quality_assessment(self):
        """Generate assessment of secret remediation quality"""
        assessment = "**Secret Remediation Quality Assessment:**\n\n"

        remediation = self.results.get('secret_remediation', {})
        actions_taken = remediation.get('actions_taken', 0)
        manual_actions = remediation.get('manual_actions_required', 0)

        assessment += f"**Automated Actions**: {actions_taken} remediation actions\n"
        assessment += f"**Manual Actions Required**: {manual_actions} actions need human intervention\n"

        # Remediation scope
        quality = remediation.get('remediation_quality', {})
        scope = quality.get('remediation_scope', 'none')

        assessment += f"**Remediation Scope**: {scope.title()}\n"

        if scope == "comprehensive":
            assessment += "✅ Professional Grade: Comprehensive remediation guidance\n"
        elif scope == "basic":
            assessment += "⚠️ Professional Grade: Basic remediation guidance\n"
        else:
            assessment += "❌ Professional Grade: No remediation guidance provided\n"

        # Specific remediation features
        gitignore = remediation.get('gitignore_generation', {})
        env_template = remediation.get('env_template_generation', {})

        if gitignore.get('gitignore_generated'):
            assessment += f"**GitIgnore Patterns**: {gitignore.get('patterns_count', 0)} patterns generated\n"

        if env_template.get('env_template_generated'):
            assessment += f"**Environment Template**: {env_template.get('variables_count', 0)} variables templated\n"

        return assessment

    def _generate_secrets_recommendations(self):
        """Generate actionable recommendations based on test results"""
        recommendations = []

        # Tool integration recommendations
        tool_integration = self.results.get('tool_integration', {})
        available_tools = tool_integration.get('tool_availability', {})

        if not available_tools.get('gitleaks', False):
            recommendations.append("**Install GitLeaks**: Essential for comprehensive secret scanning")

        # Detection accuracy recommendations
        detection = self.results.get('secret_detection', {})
        accuracy = detection.get('detection_accuracy', {}).get('detection_rate', 0)

        if accuracy < 50:
            recommendations.append("**Improve Detection Accuracy**: Currently detecting only {:.1f}% of test secrets".format(accuracy))

        # Risk assessment recommendations
        risk_quality = detection.get('risk_assessment_quality', {}).get('quality_score', 0)
        if risk_quality < 5:
            recommendations.append("**Enhance Risk Assessment**: Add business impact and compliance analysis")

        # Remediation recommendations
        remediation = self.results.get('secret_remediation', {})
        scope = remediation.get('remediation_quality', {}).get('remediation_scope', 'none')

        if scope == 'none':
            recommendations.append("**Implement Remediation Guidance**: No remediation actions provided")

        if not remediation.get('gitignore_generation', {}).get('gitignore_generated'):
            recommendations.append("**Add GitIgnore Generation**: Prevent future secret commits")

        if not recommendations:
            recommendations.append("**Strong Secret Management Implementation**: Agent meets secret detection requirements")

        recommendations_text = "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))
        return recommendations_text

    async def run_comprehensive_test(self, test_project: str):
        """Run complete Secrets Agent validation test suite"""
        print(f"🚀 Starting comprehensive Secrets Agent validation test")
        print(f"   Test project: {test_project}")
        print(f"   Test timestamp: {self.test_timestamp}")

        try:
            # Test 1: Secret Detection
            await self.test_secret_detection(test_project)

            # Test 2: Secret Remediation
            await self.test_secret_remediation(test_project)

            # Test 3: Tool Integration
            await self.test_tool_integration(test_project)

            # Generate comprehensive report
            report = self.generate_comprehensive_report()

            # Save report
            report_path = f"/home/jimmie/linkops-industries/James-OS/guidepoint/docs/GP-results/secrets-agent-test-{self.test_timestamp}.md"
            with open(report_path, 'w') as f:
                f.write(report)

            print(f"✅ Comprehensive Secrets test complete")
            print(f"📄 Detailed report saved: {report_path}")

            # Generate summary
            secrets_found = self.results['secret_detection']['secrets_found']
            detection_rate = self.results['secret_detection']['detection_accuracy']['detection_rate']
            gitleaks_functional = self.results['tool_integration']['integration_summary']['gitleaks_functional']
            remediation_scope = self.results['secret_remediation']['remediation_quality']['remediation_scope']

            return {
                "test_completed": True,
                "report_path": report_path,
                "summary": {
                    "secrets_found": secrets_found,
                    "detection_rate": f"{detection_rate:.1f}%",
                    "gitleaks_integration": gitleaks_functional,
                    "remediation_scope": remediation_scope,
                    "secrets_capability": secrets_found > 0 or gitleaks_functional,
                    "professional_grade": detection_rate >= 80 and remediation_scope in ['comprehensive', 'basic']
                }
            }

        except Exception as e:
            error_report = f"""# Secrets Agent Test FAILED
**Error**: {str(e)}
**Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

The Secrets Agent test encountered a critical error and could not complete.
This indicates fundamental issues with the agent implementation.

**Partial Results**:
```json
{json.dumps(self.results, indent=2)}
```
"""

            error_path = f"/home/jimmie/linkops-industries/James-OS/guidepoint/docs/GP-results/secrets-agent-FAILED-{self.test_timestamp}.md"
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
    """Run Secrets Agent validation test"""

    # Use the existing test project
    test_project = "/tmp/targeted_vuln_test"

    validator = SecretsAgentValidator()
    result = await validator.run_comprehensive_test(test_project)

    print("\n" + "="*60)
    print("🔐 SECRETS AGENT VALIDATION COMPLETE")
    print("="*60)

    if result["test_completed"]:
        summary = result["summary"]
        print(f"🔍 Secrets Found: {summary['secrets_found']}")
        print(f"🎯 Detection Rate: {summary['detection_rate']}")
        print(f"🔧 GitLeaks Integration: {summary['gitleaks_integration']}")
        print(f"🛠️ Remediation Scope: {summary['remediation_scope']}")
        print(f"🔐 Secrets Capability: {summary['secrets_capability']}")
        print(f"👔 Professional Grade: {summary['professional_grade']}")
        print(f"📄 Detailed Report: {result['report_path']}")
    else:
        print(f"❌ Test Failed: {result['error']}")
        print(f"📄 Error Report: {result['error_report_path']}")

if __name__ == "__main__":
    asyncio.run(main())