#!/usr/bin/env python3
"""
Scanner Agent Validation Test
============================

Systematic testing of Scanner Agent capabilities to verify:
1. Actual vulnerability detection vs claimed detection
2. Real autonomous remediation vs theoretical capabilities
3. Integration with security tools vs hardcoded patterns
4. Professional reporting vs basic output

Test Results: Saved to docs/GP-results/scanner-agent-test-TIMESTAMP.md
"""

import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/jimmie/linkops-industries/James-OS/guidepoint')

from agents.scanner_agent.agent import ScannerAgent

class ScannerAgentValidator:
    """Comprehensive validation of Scanner Agent capabilities"""

    def __init__(self):
        self.agent = ScannerAgent()
        self.test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "test_metadata": {
                "timestamp": self.test_timestamp,
                "agent_tested": "ScannerAgent",
                "test_purpose": "Validate actual capabilities vs claims"
            },
            "vulnerability_detection": {},
            "autonomous_remediation": {},
            "tool_integration": {},
            "reporting_quality": {},
            "overall_assessment": {}
        }

    async def test_vulnerability_detection(self, test_project: str):
        """Test actual vulnerability detection capabilities"""
        print(f"🔍 Testing Scanner Agent vulnerability detection on: {test_project}")

        detection_result = await self.agent.analyze_project(test_project)

        vulnerabilities = detection_result.get("vulnerabilities", [])

        self.results["vulnerability_detection"] = {
            "test_project": test_project,
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerability_details": vulnerabilities[:5],  # First 5 for analysis
            "detection_method_analysis": self._analyze_detection_methods(vulnerabilities),
            "severity_distribution": self._analyze_severity_distribution(vulnerabilities),
            "file_coverage": self._analyze_file_coverage(detection_result, test_project)
        }

        print(f"   Found {len(vulnerabilities)} vulnerabilities")
        return detection_result

    def _analyze_detection_methods(self, vulnerabilities):
        """Analyze whether detection uses real tools or hardcoded patterns"""
        methods = {}
        for vuln in vulnerabilities:
            source = vuln.get("source", "unknown")
            if source not in methods:
                methods[source] = 0
            methods[source] += 1

        # Check for signs of hardcoded detection
        hardcoded_indicators = []
        if any("hardcoded" in str(v).lower() for v in vulnerabilities):
            hardcoded_indicators.append("Uses hardcoded vulnerability patterns")

        return {
            "detection_sources": methods,
            "hardcoded_indicators": hardcoded_indicators,
            "tool_integration_evidence": self._check_tool_integration_evidence(vulnerabilities)
        }

    def _check_tool_integration_evidence(self, vulnerabilities):
        """Check for evidence of actual security tool integration"""
        evidence = {
            "trivy_integration": False,
            "bandit_integration": False,
            "checkov_integration": False,
            "safety_integration": False
        }

        for vuln in vulnerabilities:
            vuln_str = str(vuln).lower()
            if "trivy" in vuln_str:
                evidence["trivy_integration"] = True
            if "bandit" in vuln_str:
                evidence["bandit_integration"] = True
            if "checkov" in vuln_str:
                evidence["checkov_integration"] = True
            if "safety" in vuln_str:
                evidence["safety_integration"] = True

        return evidence

    def _analyze_severity_distribution(self, vulnerabilities):
        """Analyze severity distribution of found vulnerabilities"""
        severities = {}
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "UNKNOWN")
            if severity not in severities:
                severities[severity] = 0
            severities[severity] += 1

        return severities

    def _analyze_file_coverage(self, detection_result, test_project):
        """Analyze which files were actually scanned"""
        scanned_files = detection_result.get("scanned_files", [])

        # Count actual files in project
        project_path = Path(test_project)
        total_files = 0
        code_files = 0

        if project_path.exists():
            for file in project_path.rglob("*"):
                if file.is_file():
                    total_files += 1
                    if file.suffix in ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.dockerfile']:
                        code_files += 1

        return {
            "files_scanned": len(scanned_files),
            "total_project_files": total_files,
            "code_files_in_project": code_files,
            "coverage_percentage": (len(scanned_files) / max(1, code_files)) * 100
        }

    async def test_autonomous_remediation(self, test_project: str):
        """Test actual autonomous remediation capabilities"""
        print(f"🔧 Testing Scanner Agent autonomous remediation on: {test_project}")

        # Create a backup to verify changes
        import shutil
        backup_dir = f"/tmp/scanner_test_backup_{self.test_timestamp}"
        shutil.copytree(test_project, backup_dir)

        remediation_result = await self.agent.execute_autonomous_remediation(test_project)

        # Analyze what actually changed
        changes_made = self._analyze_actual_changes(test_project, backup_dir)

        self.results["autonomous_remediation"] = {
            "test_project": test_project,
            "remediation_claimed": remediation_result,
            "actual_changes_detected": changes_made,
            "success_rate_claimed": remediation_result.get("success_rate", 0),
            "success_rate_verified": self._calculate_verified_success_rate(changes_made),
            "remediation_effectiveness": self._assess_remediation_effectiveness(changes_made)
        }

        print(f"   Claimed success rate: {remediation_result.get('success_rate', 0)}%")
        print(f"   Verified changes: {len(changes_made.get('modified_files', []))} files")

        return remediation_result

    def _analyze_actual_changes(self, current_dir, backup_dir):
        """Compare current directory with backup to see actual changes"""
        import difflib
        import os

        changes = {
            "modified_files": [],
            "new_files": [],
            "deleted_files": [],
            "change_details": []
        }

        current_path = Path(current_dir)
        backup_path = Path(backup_dir)

        # Find all files in both directories
        current_files = set()
        backup_files = set()

        if current_path.exists():
            for f in current_path.rglob("*"):
                if f.is_file():
                    current_files.add(f.relative_to(current_path))

        if backup_path.exists():
            for f in backup_path.rglob("*"):
                if f.is_file():
                    backup_files.add(f.relative_to(backup_path))

        # Analyze differences
        for file_rel in current_files:
            if file_rel in backup_files:
                # Compare file contents
                current_file = current_path / file_rel
                backup_file = backup_path / file_rel

                try:
                    with open(current_file, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        backup_content = f.read()

                    if current_content != backup_content:
                        changes["modified_files"].append(str(file_rel))

                        # Get diff details
                        diff = list(difflib.unified_diff(
                            backup_content.splitlines(),
                            current_content.splitlines(),
                            fromfile=f"backup/{file_rel}",
                            tofile=f"current/{file_rel}",
                            lineterm=""
                        ))

                        changes["change_details"].append({
                            "file": str(file_rel),
                            "diff_lines": len(diff),
                            "changes_preview": diff[:10]  # First 10 lines of diff
                        })

                except Exception as e:
                    changes["change_details"].append({
                        "file": str(file_rel),
                        "error": f"Could not analyze: {e}"
                    })
            else:
                changes["new_files"].append(str(file_rel))

        # Files that were deleted
        for file_rel in backup_files:
            if file_rel not in current_files:
                changes["deleted_files"].append(str(file_rel))

        return changes

    def _calculate_verified_success_rate(self, changes):
        """Calculate actual success rate based on verified changes"""
        modified_files = len(changes.get("modified_files", []))
        new_files = len(changes.get("new_files", []))

        if modified_files + new_files > 0:
            return 100.0  # If files were actually changed, some remediation occurred
        else:
            return 0.0    # No actual changes detected

    def _assess_remediation_effectiveness(self, changes):
        """Assess the quality and effectiveness of remediation"""
        assessment = {
            "files_actually_modified": len(changes.get("modified_files", [])),
            "new_files_created": len(changes.get("new_files", [])),
            "remediation_scope": "none",
            "quality_indicators": []
        }

        total_changes = assessment["files_actually_modified"] + assessment["new_files_created"]

        if total_changes == 0:
            assessment["remediation_scope"] = "none"
            assessment["quality_indicators"].append("No actual file modifications detected")
        elif total_changes < 5:
            assessment["remediation_scope"] = "limited"
            assessment["quality_indicators"].append("Limited scope of changes")
        else:
            assessment["remediation_scope"] = "comprehensive"
            assessment["quality_indicators"].append("Comprehensive remediation attempted")

        # Analyze change details for quality
        for change in changes.get("change_details", []):
            if change.get("diff_lines", 0) > 0:
                assessment["quality_indicators"].append(f"Substantive changes to {change['file']}")

        return assessment

    async def test_reporting_quality(self, detection_result, remediation_result):
        """Test the quality and professionalism of reporting"""
        print("📋 Testing Scanner Agent reporting quality")

        report_quality = {
            "detection_report_structure": self._analyze_report_structure(detection_result),
            "remediation_report_structure": self._analyze_report_structure(remediation_result),
            "professional_formatting": self._assess_professional_formatting(detection_result, remediation_result),
            "business_value_content": self._assess_business_value_content(detection_result, remediation_result)
        }

        self.results["reporting_quality"] = report_quality
        print(f"   Report structure quality: {report_quality['detection_report_structure']['completeness_score']}/10")

        return report_quality

    def _analyze_report_structure(self, result):
        """Analyze the structure and completeness of reports"""
        expected_fields = [
            "agent_id", "project_path", "timestamp", "vulnerabilities",
            "duration_seconds", "scanned_files"
        ]

        present_fields = []
        missing_fields = []

        for field in expected_fields:
            if field in result:
                present_fields.append(field)
            else:
                missing_fields.append(field)

        return {
            "expected_fields": len(expected_fields),
            "present_fields": len(present_fields),
            "missing_fields": missing_fields,
            "completeness_score": (len(present_fields) / len(expected_fields)) * 10
        }

    def _assess_professional_formatting(self, detection_result, remediation_result):
        """Assess whether reports meet professional consulting standards"""
        indicators = []

        # Check for professional metadata
        if detection_result.get("timestamp"):
            indicators.append("Includes timestamps")
        if detection_result.get("agent_id"):
            indicators.append("Includes agent identification")
        if detection_result.get("duration_seconds"):
            indicators.append("Includes performance metrics")

        # Check for structured data
        vulnerabilities = detection_result.get("vulnerabilities", [])
        if vulnerabilities:
            sample_vuln = vulnerabilities[0]
            if isinstance(sample_vuln, dict):
                indicators.append("Structured vulnerability data")
                if "severity" in sample_vuln:
                    indicators.append("Includes severity classifications")
                if "description" in sample_vuln:
                    indicators.append("Includes vulnerability descriptions")

        return {
            "professional_indicators": indicators,
            "professionalism_score": len(indicators),
            "meets_consulting_standards": len(indicators) >= 4
        }

    def _assess_business_value_content(self, detection_result, remediation_result):
        """Assess whether reports provide business value information"""
        business_indicators = []

        # Check for business-relevant information
        if detection_result.get("vulnerabilities"):
            business_indicators.append("Provides vulnerability inventory")

        if remediation_result.get("success_rate") is not None:
            business_indicators.append("Provides success metrics")

        vulnerabilities = detection_result.get("vulnerabilities", [])
        if any("CRITICAL" in str(v) or "HIGH" in str(v) for v in vulnerabilities):
            business_indicators.append("Includes risk prioritization")

        return {
            "business_indicators": business_indicators,
            "business_value_score": len(business_indicators),
            "executive_ready": len(business_indicators) >= 2
        }

    def generate_comprehensive_report(self):
        """Generate detailed markdown report of test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# Scanner Agent Validation Test Report
**Generated**: {timestamp}
**Test ID**: scanner-agent-{self.test_timestamp}

---

## Executive Summary

This report documents comprehensive testing of the Scanner Agent to validate actual capabilities against claimed functionality.

### Key Findings

**Vulnerability Detection:**
- Vulnerabilities Found: {self.results['vulnerability_detection'].get('vulnerabilities_found', 'N/A')}
- Detection Methods: {list(self.results['vulnerability_detection'].get('detection_method_analysis', {}).get('detection_sources', {}).keys())}
- Tool Integration: {self.results['vulnerability_detection'].get('detection_method_analysis', {}).get('tool_integration_evidence', {})}

**Autonomous Remediation:**
- Claimed Success Rate: {self.results['autonomous_remediation'].get('success_rate_claimed', 'N/A')}%
- Verified Success Rate: {self.results['autonomous_remediation'].get('success_rate_verified', 'N/A')}%
- Files Actually Modified: {self.results['autonomous_remediation'].get('actual_changes_detected', {}).get('modified_files', [])}

**Professional Reporting:**
- Report Completeness: {self.results['reporting_quality'].get('detection_report_structure', {}).get('completeness_score', 'N/A')}/10
- Professional Standards: {self.results['reporting_quality'].get('professional_formatting', {}).get('meets_consulting_standards', False)}
- Business Value: {self.results['reporting_quality'].get('business_value_content', {}).get('executive_ready', False)}

---

## Detailed Test Results

### 1. Vulnerability Detection Analysis

**Test Project**: {self.results['vulnerability_detection'].get('test_project', 'N/A')}

**Detection Results:**
```json
{json.dumps(self.results['vulnerability_detection'], indent=2)}
```

### 2. Autonomous Remediation Analysis

**Remediation Testing:**
```json
{json.dumps(self.results['autonomous_remediation'], indent=2)}
```

### 3. Reporting Quality Assessment

**Professional Reporting Standards:**
```json
{json.dumps(self.results['reporting_quality'], indent=2)}
```

---

## Technical Validation

### Security Tool Integration Status
{self._generate_tool_integration_assessment()}

### Remediation Capability Verification
{self._generate_remediation_assessment()}

### Professional Deliverable Quality
{self._generate_deliverable_assessment()}

---

## Recommendations

{self._generate_recommendations()}

---

## Raw Test Data

**Complete Test Results:**
```json
{json.dumps(self.results, indent=2)}
```

---

*Report generated by Scanner Agent Validation Test*
*Timestamp: {self.test_timestamp}*
"""
        return report

    def _generate_tool_integration_assessment(self):
        """Generate assessment of actual tool integration"""
        evidence = self.results.get('vulnerability_detection', {}).get('detection_method_analysis', {}).get('tool_integration_evidence', {})

        assessment = "**Security Tool Integration Status:**\n\n"

        tools = {
            'trivy_integration': 'Trivy (Container Vulnerability Scanner)',
            'bandit_integration': 'Bandit (Python SAST)',
            'checkov_integration': 'Checkov (IaC Security)',
            'safety_integration': 'Safety (Python Dependency Scanner)'
        }

        for tool_key, tool_name in tools.items():
            status = "✅ INTEGRATED" if evidence.get(tool_key, False) else "❌ NOT DETECTED"
            assessment += f"- {tool_name}: {status}\n"

        hardcoded_indicators = self.results.get('vulnerability_detection', {}).get('detection_method_analysis', {}).get('hardcoded_indicators', [])
        if hardcoded_indicators:
            assessment += f"\n**Hardcoded Detection Patterns Detected:**\n"
            for indicator in hardcoded_indicators:
                assessment += f"- ⚠️ {indicator}\n"

        return assessment

    def _generate_remediation_assessment(self):
        """Generate assessment of remediation capabilities"""
        remediation = self.results.get('autonomous_remediation', {})

        assessment = "**Autonomous Remediation Verification:**\n\n"

        claimed_rate = remediation.get('success_rate_claimed', 0)
        verified_rate = remediation.get('success_rate_verified', 0)

        assessment += f"- **Claimed Success Rate**: {claimed_rate}%\n"
        assessment += f"- **Verified Success Rate**: {verified_rate}%\n"
        assessment += f"- **Accuracy Gap**: {abs(claimed_rate - verified_rate)}%\n\n"

        effectiveness = remediation.get('remediation_effectiveness', {})
        assessment += f"**Remediation Scope**: {effectiveness.get('remediation_scope', 'unknown').title()}\n\n"

        quality_indicators = effectiveness.get('quality_indicators', [])
        if quality_indicators:
            assessment += "**Quality Indicators:**\n"
            for indicator in quality_indicators:
                assessment += f"- {indicator}\n"

        return assessment

    def _generate_deliverable_assessment(self):
        """Generate assessment of professional deliverable quality"""
        reporting = self.results.get('reporting_quality', {})

        assessment = "**Professional Deliverable Quality:**\n\n"

        professional = reporting.get('professional_formatting', {})
        business = reporting.get('business_value_content', {})

        assessment += f"- **Professional Standards Met**: {professional.get('meets_consulting_standards', False)}\n"
        assessment += f"- **Executive Ready**: {business.get('executive_ready', False)}\n"
        assessment += f"- **Professionalism Score**: {professional.get('professionalism_score', 0)}/7\n"
        assessment += f"- **Business Value Score**: {business.get('business_value_score', 0)}/3\n\n"

        indicators = professional.get('professional_indicators', [])
        if indicators:
            assessment += "**Professional Indicators Present:**\n"
            for indicator in indicators:
                assessment += f"- ✅ {indicator}\n"

        return assessment

    def _generate_recommendations(self):
        """Generate actionable recommendations based on test results"""
        recommendations = []

        # Tool integration recommendations
        evidence = self.results.get('vulnerability_detection', {}).get('detection_method_analysis', {}).get('tool_integration_evidence', {})
        missing_tools = [tool for tool, integrated in evidence.items() if not integrated]

        if missing_tools:
            recommendations.append(f"**Integrate Missing Security Tools**: {', '.join(missing_tools)}")

        # Remediation accuracy recommendations
        remediation = self.results.get('autonomous_remediation', {})
        claimed_rate = remediation.get('success_rate_claimed', 0)
        verified_rate = remediation.get('success_rate_verified', 0)

        if abs(claimed_rate - verified_rate) > 10:
            recommendations.append("**Fix Remediation Reporting Accuracy**: Large gap between claimed and verified success rates")

        # Professional reporting recommendations
        reporting = self.results.get('reporting_quality', {})
        if not reporting.get('professional_formatting', {}).get('meets_consulting_standards', False):
            recommendations.append("**Improve Professional Reporting Standards**: Reports do not meet consulting-grade quality")

        if not reporting.get('business_value_content', {}).get('executive_ready', False):
            recommendations.append("**Add Business Value Content**: Reports lack executive-level business impact information")

        if not recommendations:
            recommendations.append("**No Critical Issues Found**: Scanner Agent meets basic functionality requirements")

        recommendations_text = "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))

        return recommendations_text

    async def run_comprehensive_test(self, test_project: str):
        """Run complete validation test suite"""
        print(f"🚀 Starting comprehensive Scanner Agent validation test")
        print(f"   Test project: {test_project}")
        print(f"   Test timestamp: {self.test_timestamp}")

        try:
            # Test 1: Vulnerability Detection
            detection_result = await self.test_vulnerability_detection(test_project)

            # Test 2: Autonomous Remediation
            remediation_result = await self.test_autonomous_remediation(test_project)

            # Test 3: Reporting Quality
            await self.test_reporting_quality(detection_result, remediation_result)

            # Generate comprehensive report
            report = self.generate_comprehensive_report()

            # Save report
            report_path = f"/home/jimmie/linkops-industries/James-OS/guidepoint/docs/GP-results/scanner-agent-test-{self.test_timestamp}.md"
            with open(report_path, 'w') as f:
                f.write(report)

            print(f"✅ Comprehensive test complete")
            print(f"📄 Detailed report saved: {report_path}")

            return {
                "test_completed": True,
                "report_path": report_path,
                "summary": {
                    "vulnerabilities_found": self.results['vulnerability_detection'].get('vulnerabilities_found', 0),
                    "remediation_verified": self.results['autonomous_remediation'].get('success_rate_verified', 0),
                    "professional_grade": self.results['reporting_quality'].get('professional_formatting', {}).get('meets_consulting_standards', False)
                }
            }

        except Exception as e:
            error_report = f"""# Scanner Agent Test FAILED
**Error**: {str(e)}
**Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

The Scanner Agent test encountered a critical error and could not complete.
This indicates fundamental issues with the agent implementation.

**Partial Results**:
```json
{json.dumps(self.results, indent=2)}
```
"""

            error_path = f"/home/jimmie/linkops-industries/James-OS/guidepoint/docs/GP-results/scanner-agent-FAILED-{self.test_timestamp}.md"
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
    """Run Scanner Agent validation test"""

    # Use the existing vulnerable test project
    test_project = "/tmp/targeted_vuln_test"

    validator = ScannerAgentValidator()
    result = await validator.run_comprehensive_test(test_project)

    print("\n" + "="*60)
    print("🔍 SCANNER AGENT VALIDATION COMPLETE")
    print("="*60)

    if result["test_completed"]:
        summary = result["summary"]
        print(f"📊 Vulnerabilities Found: {summary['vulnerabilities_found']}")
        print(f"🔧 Remediation Verified: {summary['remediation_verified']}%")
        print(f"📋 Professional Grade: {summary['professional_grade']}")
        print(f"📄 Detailed Report: {result['report_path']}")
    else:
        print(f"❌ Test Failed: {result['error']}")
        print(f"📄 Error Report: {result['error_report_path']}")

if __name__ == "__main__":
    asyncio.run(main())