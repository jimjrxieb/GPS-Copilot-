#!/usr/bin/env python3
"""
ISO 27001:2022 Compliance Mapper
Maps security findings (CWEs, scanner checks) to ISO 27001 controls
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ISO27001Mapper:
    """Maps security findings to ISO 27001:2022 controls"""

    # ISO 27001:2022 has 93 controls across 4 themes and 14 clauses
    TOTAL_CONTROLS = 93

    def __init__(self):
        """Initialize ISO 27001 mapper with CWE and scanner check mappings"""

        # CWE to ISO 27001 control mappings
        self.cwe_mappings = {
            "CWE-78": {
                "controls": ["A.8.8", "A.14.2.1"],
                "control_names": ["Management of technical vulnerabilities", "Secure development policy"],
                "domain": "A.8 - Asset Management, A.14 - System Acquisition",
                "audit_evidence": [
                    "Code review logs showing input validation",
                    "SAST scan results",
                    "Developer security training records",
                    "Command injection prevention policies"
                ],
                "remediation_priority": "HIGH",
                "business_impact": "Command injection can lead to complete system compromise"
            },
            "CWE-89": {
                "controls": ["A.8.8", "A.8.23", "A.14.2.1"],
                "control_names": ["Management of technical vulnerabilities", "Web filtering", "Secure development policy"],
                "domain": "A.8 - Asset Management, A.14 - System Acquisition",
                "audit_evidence": [
                    "Parameterized query implementation",
                    "ORM usage documentation",
                    "SAST scan results clean for SQL injection",
                    "Database access control policies"
                ],
                "remediation_priority": "CRITICAL",
                "business_impact": "SQL injection can expose all customer data including PII/PCI"
            },
            "CWE-798": {
                "controls": ["A.5.15", "A.8.3"],
                "control_names": ["Access control", "Information security awareness"],
                "domain": "A.5 - Organizational Controls, A.8 - Asset Management",
                "audit_evidence": [
                    "No hardcoded credentials in codebase",
                    "Secrets management system (Vault/AWS Secrets Manager)",
                    "Gitleaks scan results clean",
                    "Developer training on credential handling"
                ],
                "remediation_priority": "CRITICAL",
                "business_impact": "Hardcoded credentials lead to unauthorized access"
            },
            "CWE-79": {
                "controls": ["A.8.8", "A.8.23", "A.14.2.1"],
                "control_names": ["Management of technical vulnerabilities", "Web filtering", "Secure development policy"],
                "domain": "A.8 - Asset Management, A.14 - System Acquisition",
                "audit_evidence": [
                    "Auto-escaping enabled in templates",
                    "Content Security Policy headers",
                    "XSS prevention framework usage",
                    "DAST scan results"
                ],
                "remediation_priority": "HIGH",
                "business_impact": "XSS can steal session tokens and user data"
            },
            "CWE-311": {
                "controls": ["A.8.24", "A.8.11"],
                "control_names": ["Use of cryptography", "Data masking"],
                "domain": "A.8 - Asset Management",
                "audit_evidence": [
                    "RDS encryption enabled",
                    "S3 encryption enabled",
                    "TLS 1.2+ for data in transit",
                    "Key management policies"
                ],
                "remediation_priority": "HIGH",
                "business_impact": "Unencrypted data violates PCI-DSS and GDPR"
            },
            "CWE-352": {
                "controls": ["A.8.8", "A.14.2.1"],
                "control_names": ["Management of technical vulnerabilities", "Secure development policy"],
                "domain": "A.8 - Asset Management, A.14 - System Acquisition",
                "audit_evidence": [
                    "CSRF tokens implemented",
                    "SameSite cookie attributes",
                    "Framework CSRF protection enabled"
                ],
                "remediation_priority": "MEDIUM",
                "business_impact": "CSRF can perform unauthorized actions on behalf of users"
            },
            "CWE-295": {
                "controls": ["A.8.24", "A.13.1.1"],
                "control_names": ["Use of cryptography", "Network controls"],
                "domain": "A.8 - Asset Management, A.13 - Communications Security",
                "audit_evidence": [
                    "Certificate validation enabled",
                    "No certificate pinning bypass",
                    "TLS configuration audited"
                ],
                "remediation_priority": "HIGH",
                "business_impact": "Certificate validation bypass enables MITM attacks"
            },
            "CWE-327": {
                "controls": ["A.8.24"],
                "control_names": ["Use of cryptography"],
                "domain": "A.8 - Asset Management",
                "audit_evidence": [
                    "AES-256 or stronger for symmetric encryption",
                    "RSA-2048+ or ECC for asymmetric",
                    "No MD5, SHA1, DES usage",
                    "Cryptographic standards policy"
                ],
                "remediation_priority": "HIGH",
                "business_impact": "Weak cryptography can be broken by attackers"
            },
            "CWE-330": {
                "controls": ["A.8.24"],
                "control_names": ["Use of cryptography"],
                "domain": "A.8 - Asset Management",
                "audit_evidence": [
                    "CSRNG usage (secrets module in Python)",
                    "No predictable random number generation",
                    "Secure token generation"
                ],
                "remediation_priority": "MEDIUM",
                "business_impact": "Weak randomness compromises cryptographic security"
            },
            "CWE-502": {
                "controls": ["A.8.8", "A.14.2.1"],
                "control_names": ["Management of technical vulnerabilities", "Secure development policy"],
                "domain": "A.8 - Asset Management, A.14 - System Acquisition",
                "audit_evidence": [
                    "No pickle usage with untrusted data",
                    "JSON serialization preferred",
                    "Input validation on deserialized data",
                    "Secure deserialization policies"
                ],
                "remediation_priority": "CRITICAL",
                "business_impact": "Deserialization attacks lead to remote code execution"
            },
            "CWE-22": {
                "controls": ["A.8.8", "A.14.2.1"],
                "control_names": ["Management of technical vulnerabilities", "Secure development policy"],
                "domain": "A.8 - Asset Management, A.14 - System Acquisition",
                "audit_evidence": [
                    "Path traversal prevention",
                    "Input validation on file paths",
                    "Chroot/sandboxing"
                ],
                "remediation_priority": "HIGH",
                "business_impact": "Path traversal exposes sensitive files"
            },
            "CWE-94": {
                "controls": ["A.8.8", "A.14.2.1"],
                "control_names": ["Management of technical vulnerabilities", "Secure development policy"],
                "domain": "A.8 - Asset Management, A.14 - System Acquisition",
                "audit_evidence": [
                    "No eval() or exec() with user input",
                    "Template injection prevention",
                    "Code injection testing"
                ],
                "remediation_priority": "CRITICAL",
                "business_impact": "Code injection leads to arbitrary code execution"
            },
            "CWE-601": {
                "controls": ["A.8.8", "A.14.2.1"],
                "control_names": ["Management of technical vulnerabilities", "Secure development policy"],
                "domain": "A.8 - Asset Management, A.14 - System Acquisition",
                "audit_evidence": [
                    "URL redirect whitelist",
                    "Open redirect prevention",
                    "DAST scan results"
                ],
                "remediation_priority": "MEDIUM",
                "business_impact": "Open redirects used in phishing attacks"
            }
        }

        # Scanner-specific check mappings (Checkov, Trivy, etc.)
        self.scanner_mappings = {
            "checkov": {
                "CKV_AWS_157": {
                    "controls": ["A.8.24"],
                    "control_names": ["Use of cryptography"],
                    "description": "RDS encryption not enabled",
                    "remediation_priority": "HIGH"
                },
                "CKV_AWS_20": {
                    "controls": ["A.13.1.3"],
                    "control_names": ["Segregation in networks"],
                    "description": "S3 bucket public access",
                    "remediation_priority": "CRITICAL"
                },
                "CKV_AWS_23": {
                    "controls": ["A.13.1.1", "A.13.1.3"],
                    "control_names": ["Network controls", "Segregation in networks"],
                    "description": "Security group allows unrestricted access",
                    "remediation_priority": "CRITICAL"
                },
                "CKV_AWS_33": {
                    "controls": ["A.8.15"],
                    "control_names": ["Logging"],
                    "description": "KMS key rotation not enabled",
                    "remediation_priority": "MEDIUM"
                },
                "CKV_AWS_50": {
                    "controls": ["A.12.3.1"],
                    "control_names": ["Information backup"],
                    "description": "Lambda missing DLQ",
                    "remediation_priority": "MEDIUM"
                },
                "CKV_AWS_53": {
                    "controls": ["A.13.1.1"],
                    "control_names": ["Network controls"],
                    "description": "S3 bucket missing access logging",
                    "remediation_priority": "HIGH"
                },
                "CKV_AWS_79": {
                    "controls": ["A.8.15"],
                    "control_names": ["Logging"],
                    "description": "CloudWatch log group not encrypted",
                    "remediation_priority": "MEDIUM"
                },
                "CKV_AWS_118": {
                    "controls": ["A.13.1.1"],
                    "control_names": ["Network controls"],
                    "description": "RDS not in private subnet",
                    "remediation_priority": "CRITICAL"
                },
                "CKV_AWS_130": {
                    "controls": ["A.13.1.3"],
                    "control_names": ["Segregation in networks"],
                    "description": "VPC default security group allows traffic",
                    "remediation_priority": "HIGH"
                },
                "CKV_AWS_158": {
                    "controls": ["A.13.1.1"],
                    "control_names": ["Network controls"],
                    "description": "CloudFront without WAF",
                    "remediation_priority": "HIGH"
                },
                "CKV_AWS_19": {
                    "controls": ["A.8.24"],
                    "control_names": ["Use of cryptography"],
                    "description": "S3 bucket missing encryption",
                    "remediation_priority": "HIGH"
                },
                "CKV_AWS_21": {
                    "controls": ["A.12.3.1"],
                    "control_names": ["Information backup"],
                    "description": "S3 versioning not enabled",
                    "remediation_priority": "MEDIUM"
                }
            },
            "trivy": {
                "AVD-AWS-0086": {
                    "controls": ["A.8.24"],
                    "control_names": ["Use of cryptography"],
                    "description": "S3 encryption not enabled"
                },
                "AVD-AWS-0089": {
                    "controls": ["A.13.1.3"],
                    "control_names": ["Segregation in networks"],
                    "description": "Security group allows public access"
                },
                "AVD-AWS-0176": {
                    "controls": ["A.8.24"],
                    "control_names": ["Use of cryptography"],
                    "description": "RDS encryption not enabled"
                }
            },
            "bandit": {
                "B201": {
                    "controls": ["A.8.8", "A.14.2.1"],
                    "control_names": ["Management of technical vulnerabilities", "Secure development policy"],
                    "description": "Flask debug mode enabled"
                },
                "B501": {
                    "controls": ["A.8.24"],
                    "control_names": ["Use of cryptography"],
                    "description": "Weak SSL/TLS configuration"
                },
                "B506": {
                    "controls": ["A.8.24"],
                    "control_names": ["Use of cryptography"],
                    "description": "Unsafe YAML load"
                }
            }
        }

    def enrich_finding(self, finding: Dict) -> Dict:
        """
        Enrich a finding with ISO 27001 compliance data

        Args:
            finding: Security finding dict with CWE or scanner check ID

        Returns:
            Finding enriched with ISO 27001 controls
        """
        enriched = finding.copy()

        # Try CWE mapping first
        if "cwe" in finding and finding["cwe"]:
            cwe = finding["cwe"]
            if cwe in self.cwe_mappings:
                mapping = self.cwe_mappings[cwe]
                enriched["compliance"] = enriched.get("compliance", {})
                enriched["compliance"]["ISO_27001"] = {
                    "controls": mapping["controls"],
                    "control_names": mapping["control_names"],
                    "domain": mapping["domain"],
                    "audit_evidence": mapping["audit_evidence"],
                    "remediation_priority": mapping["remediation_priority"],
                    "business_impact": mapping["business_impact"]
                }
                logger.debug(f"Mapped {cwe} to ISO 27001 controls: {mapping['controls']}")
                return enriched

        # Try scanner-specific mapping
        scanner = finding.get("scanner", "")
        check_id = finding.get("check_id", "") or finding.get("rule_id", "") or finding.get("test_id", "")

        if scanner in self.scanner_mappings:
            scanner_checks = self.scanner_mappings[scanner]
            if check_id in scanner_checks:
                mapping = scanner_checks[check_id]
                enriched["compliance"] = enriched.get("compliance", {})
                enriched["compliance"]["ISO_27001"] = {
                    "controls": mapping["controls"],
                    "control_names": mapping["control_names"],
                    "description": mapping["description"],
                    "remediation_priority": mapping.get("remediation_priority", "MEDIUM")
                }
                logger.debug(f"Mapped {scanner}:{check_id} to ISO 27001 controls: {mapping['controls']}")
                return enriched

        logger.debug(f"No ISO 27001 mapping found for finding: {finding.get('id', 'unknown')}")
        return enriched

    def generate_report(self, findings: List[Dict]) -> Dict:
        """
        Generate ISO 27001 compliance report from findings

        Args:
            findings: List of security findings

        Returns:
            Compliance report dict
        """
        logger.info(f"Generating ISO 27001 compliance report from {len(findings)} findings")

        # Group findings by control
        controls_map = {}
        unmapped_findings = []

        for finding in findings:
            if "compliance" in finding and "ISO_27001" in finding["compliance"]:
                iso_data = finding["compliance"]["ISO_27001"]
                for control in iso_data["controls"]:
                    if control not in controls_map:
                        controls_map[control] = {
                            "control": control,
                            "control_name": iso_data["control_names"][iso_data["controls"].index(control)] if isinstance(iso_data.get("control_names"), list) else iso_data.get("control_names", ""),
                            "status": "FAIL",
                            "finding_count": 0,
                            "findings": [],
                            "remediation_priority": iso_data.get("remediation_priority", "MEDIUM"),
                            "estimated_hours": 0
                        }
                    controls_map[control]["finding_count"] += 1
                    controls_map[control]["findings"].append({
                        "id": finding.get("id", "unknown"),
                        "title": finding.get("title", "") or finding.get("message", ""),
                        "severity": finding.get("severity", "UNKNOWN"),
                        "file": finding.get("file", ""),
                        "line": finding.get("line", "")
                    })
                    # Estimate 2 hours per finding for remediation
                    controls_map[control]["estimated_hours"] += 2
            else:
                unmapped_findings.append(finding)

        # Calculate compliance metrics
        controls_checked = len(controls_map)
        controls_passing = 0  # All controls with findings are failing
        controls_failing = controls_checked

        failing_controls = sorted(
            controls_map.values(),
            key=lambda x: (
                {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(x["remediation_priority"], 0),
                x["finding_count"]
            ),
            reverse=True
        )

        # Calculate compliance score
        # Score = (controls not checked are assumed passing) / total controls
        controls_not_checked = self.TOTAL_CONTROLS - controls_checked
        compliance_score = ((controls_passing + controls_not_checked) / self.TOTAL_CONTROLS) * 100

        report = {
            "framework": "ISO 27001:2022",
            "scan_date": datetime.utcnow().isoformat(),
            "summary": {
                "total_controls": self.TOTAL_CONTROLS,
                "controls_checked": controls_checked,
                "controls_passing": controls_passing,
                "controls_failing": controls_failing,
                "compliance_score": round(compliance_score, 2),
                "total_findings": len(findings),
                "mapped_findings": len(findings) - len(unmapped_findings),
                "unmapped_findings": len(unmapped_findings)
            },
            "failing_controls": failing_controls,
            "remediation_estimate": {
                "total_hours": sum(c["estimated_hours"] for c in controls_map.values()),
                "total_weeks": round(sum(c["estimated_hours"] for c in controls_map.values()) / 40, 1)
            },
            "unmapped_findings_sample": unmapped_findings[:10] if unmapped_findings else []
        }

        logger.info(f"ISO 27001 Compliance: {compliance_score:.1f}% ({controls_failing}/{controls_checked} controls failing)")

        return report


def main():
    """CLI for testing ISO 27001 mapper"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 iso27001_mapper.py <findings.json>")
        sys.exit(1)

    findings_file = Path(sys.argv[1])
    if not findings_file.exists():
        print(f"Error: File not found: {findings_file}")
        sys.exit(1)

    with open(findings_file) as f:
        findings = json.load(f)

    mapper = ISO27001Mapper()

    # Enrich findings
    enriched_findings = [mapper.enrich_finding(f) for f in findings]

    # Generate report
    report = mapper.generate_report(enriched_findings)

    # Output
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()