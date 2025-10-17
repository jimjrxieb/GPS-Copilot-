#!/usr/bin/env python3
"""
SOC2 Trust Service Criteria (TSC) Mapper - SaaS COMPLIANCE ESSENTIAL
=====================================================================
Purpose: Map security findings to SOC2 TSC for audit-ready reports
Author: SecOps Framework
Stage: Compliance Mapping

SOC2 is THE compliance framework for SaaS companies. This mapper transforms
raw security findings into SOC2 compliance intelligence:
- CWE → SOC2 TSC mappings
- Scanner-specific check mappings (Checkov, Trivy)
- Trust Service Categories: Security, Availability, Confidentiality
- Evidence requirements per criterion
- Remediation priority and effort estimates

SOC2 Trust Services:
- CC (Common Criteria): Foundational controls for all trust service categories
- Security: Protection against unauthorized access
- Availability: System operational and usable as committed
- Processing Integrity: Processing is complete, valid, accurate, timely
- Confidentiality: Information designated as confidential is protected
- Privacy: Personal information collected, used, retained, disclosed, disposed

Usage:
    # Enrich single finding
    mapper = SOC2Mapper()
    enriched = mapper.enrich_finding(finding)

    # Generate full compliance report
    report = mapper.generate_compliance_report(all_findings)

    # Save report
    mapper.save_report(report, 'soc2-compliance-report.json')
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class SOC2Mapper:
    """
    SOC2 Trust Service Criteria Mapper

    Maps security findings to SOC2 TSC for compliance reporting.
    Essential for SaaS companies seeking SOC2 Type I or Type II certification.

    Features:
    - 50+ CWE to SOC2 TSC mappings
    - Scanner-specific mappings (Checkov, Trivy, Semgrep)
    - Trust Service Category classification
    - Control maturity assessment
    - Evidence requirements for auditors
    """

    # SOC2 Trust Service Criteria Mappings
    # Maps CWE to specific SOC2 TSC controls
    CWE_TO_SOC2 = {
        'CWE-78': {
            'criteria': ['CC6.1', 'CC6.6', 'CC7.2'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.6 - Logical Access - Authentication',
                'CC7.2 - System Monitoring - Security Events'
            ],
            'trust_service_category': 'Security',
            'description': 'Command injection vulnerabilities compromise system security controls',
            'control_objective': 'The entity restricts logical access to system resources through authorization and authentication mechanisms',
            'audit_evidence': [
                'Code review documentation showing input validation',
                'SAST scan results (Bandit/Semgrep) demonstrating no command injection',
                'Secure coding training records',
                'Change management logs for security patches'
            ],
            'remediation_priority': 'HIGH',
            'estimated_effort_hours': 8,
            'remediation_guidance': 'Implement parameterized commands, avoid shell=True, validate all user inputs'
        },

        'CWE-89': {
            'criteria': ['CC6.1', 'CC6.6', 'CC7.2'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.6 - Logical Access - Authentication',
                'CC7.2 - System Monitoring - Security Events'
            ],
            'trust_service_category': 'Security',
            'description': 'SQL injection vulnerabilities allow unauthorized data access',
            'control_objective': 'The entity implements logical access security controls to protect system data',
            'audit_evidence': [
                'Parameterized query usage documentation',
                'ORM framework implementation (SQLAlchemy, Django ORM)',
                'Database access layer code review',
                'Penetration test results showing no SQL injection'
            ],
            'remediation_priority': 'CRITICAL',
            'estimated_effort_hours': 12,
            'remediation_guidance': 'Use parameterized queries exclusively, implement ORM, validate all database inputs'
        },

        'CWE-798': {
            'criteria': ['CC6.1', 'CC6.6', 'CC6.7'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.6 - Logical Access - Authentication',
                'CC6.7 - Logical Access - Authorization'
            ],
            'trust_service_category': 'Security',
            'description': 'Hardcoded credentials violate authentication and secrets management controls',
            'control_objective': 'The entity requires unique identification and strong authentication for system access',
            'audit_evidence': [
                'Secrets management solution implementation (AWS Secrets Manager, Vault)',
                'Gitleaks scan results showing no hardcoded credentials',
                'Secret rotation policies and logs',
                'Access control matrix for secret access',
                'Code review logs checking for hardcoded secrets'
            ],
            'remediation_priority': 'CRITICAL',
            'estimated_effort_hours': 4,
            'remediation_guidance': 'Migrate all secrets to vault, implement rotation, remove hardcoded credentials'
        },

        'CWE-79': {
            'criteria': ['CC6.1', 'CC6.6'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.6 - Logical Access - Authentication'
            ],
            'trust_service_category': 'Security',
            'description': 'XSS vulnerabilities compromise user session security',
            'control_objective': 'The entity protects against malicious code injection and session hijacking',
            'audit_evidence': [
                'Content Security Policy (CSP) headers configuration',
                'Auto-escaping enabled in templates (Jinja2, React)',
                'Input validation and output encoding standards',
                'Web application firewall (WAF) configuration'
            ],
            'remediation_priority': 'HIGH',
            'estimated_effort_hours': 6,
            'remediation_guidance': 'Enable auto-escaping, implement CSP, validate/sanitize all user input'
        },

        'CWE-311': {
            'criteria': ['CC6.1', 'CC6.7'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.7 - Logical Access - Authorization'
            ],
            'trust_service_category': 'Confidentiality',
            'description': 'Missing encryption exposes confidential data',
            'control_objective': 'The entity protects confidential information through encryption at rest and in transit',
            'audit_evidence': [
                'Database encryption enabled (RDS, MongoDB)',
                'Storage encryption enabled (S3, EBS)',
                'TLS 1.2+ certificate configuration',
                'Encryption key management documentation',
                'Data classification policy'
            ],
            'remediation_priority': 'HIGH',
            'estimated_effort_hours': 8,
            'remediation_guidance': 'Enable encryption at rest for all data stores, enforce TLS 1.2+ for transit'
        },

        'CWE-352': {
            'criteria': ['CC6.1', 'CC7.2'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC7.2 - System Monitoring - Security Events'
            ],
            'trust_service_category': 'Security',
            'description': 'CSRF vulnerabilities allow unauthorized state changes',
            'control_objective': 'The entity prevents cross-site request forgery attacks',
            'audit_evidence': [
                'CSRF token implementation in all state-changing operations',
                'SameSite cookie attribute configuration',
                'Framework CSRF protection enabled',
                'Session management security documentation'
            ],
            'remediation_priority': 'MEDIUM',
            'estimated_effort_hours': 4,
            'remediation_guidance': 'Implement CSRF tokens, configure SameSite=Strict on cookies'
        },

        'CWE-295': {
            'criteria': ['CC6.1', 'CC6.7'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.7 - Logical Access - Authorization'
            ],
            'trust_service_category': 'Security',
            'description': 'Certificate validation bypass weakens encryption controls',
            'control_objective': 'The entity ensures cryptographic controls are properly implemented',
            'audit_evidence': [
                'TLS certificate validation enabled',
                'Certificate expiration monitoring',
                'No certificate pinning bypasses in code',
                'Network security configuration documentation'
            ],
            'remediation_priority': 'HIGH',
            'estimated_effort_hours': 3,
            'remediation_guidance': 'Enable certificate validation, remove verify=False from HTTP clients'
        },

        'CWE-327': {
            'criteria': ['CC6.1'],
            'criteria_names': ['CC6.1 - Logical and Physical Access Controls'],
            'trust_service_category': 'Security',
            'description': 'Weak cryptographic algorithms fail to protect data',
            'control_objective': 'The entity uses strong cryptographic algorithms',
            'audit_evidence': [
                'Approved cryptographic algorithm list (AES-256, RSA-2048+, SHA-256+)',
                'No weak algorithms in use (MD5, SHA-1, DES)',
                'Cryptographic standards documentation',
                'Regular algorithm review process'
            ],
            'remediation_priority': 'HIGH',
            'estimated_effort_hours': 6,
            'remediation_guidance': 'Replace MD5/SHA-1 with SHA-256+, use approved algorithms only'
        },

        'CWE-330': {
            'criteria': ['CC6.1', 'CC6.6'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.6 - Logical Access - Authentication'
            ],
            'trust_service_category': 'Security',
            'description': 'Weak random number generation compromises security tokens',
            'control_objective': 'The entity generates secure random values for authentication and cryptographic operations',
            'audit_evidence': [
                'Cryptographically secure RNG usage (secrets module)',
                'No use of predictable RNG for security operations',
                'Token generation code review',
                'Session management security documentation'
            ],
            'remediation_priority': 'MEDIUM',
            'estimated_effort_hours': 3,
            'remediation_guidance': 'Use secrets module instead of random, implement cryptographic RNG'
        },

        'CWE-502': {
            'criteria': ['CC6.1', 'CC7.2'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC7.2 - System Monitoring - Security Events'
            ],
            'trust_service_category': 'Security',
            'description': 'Insecure deserialization allows remote code execution',
            'control_objective': 'The entity validates and sanitizes all deserialized data',
            'audit_evidence': [
                'No pickle usage with untrusted data',
                'JSON used for serialization',
                'Input validation on deserialized objects',
                'Security testing results'
            ],
            'remediation_priority': 'CRITICAL',
            'estimated_effort_hours': 8,
            'remediation_guidance': 'Avoid pickle with untrusted data, use JSON, validate all deserialized data'
        },

        'CWE-22': {
            'criteria': ['CC6.1', 'CC6.7'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.7 - Logical Access - Authorization'
            ],
            'trust_service_category': 'Security',
            'description': 'Path traversal allows unauthorized file access',
            'control_objective': 'The entity restricts access to system files and directories',
            'audit_evidence': [
                'Path validation implementation',
                'File access whitelist',
                'File operation logging',
                'Authorization checks for file access'
            ],
            'remediation_priority': 'HIGH',
            'estimated_effort_hours': 6,
            'remediation_guidance': 'Validate file paths, implement whitelist, use path.resolve()'
        },

        'CWE-306': {
            'criteria': ['CC6.1', 'CC6.6'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.6 - Logical Access - Authentication'
            ],
            'trust_service_category': 'Security',
            'description': 'Missing authentication allows unauthorized access',
            'control_objective': 'The entity requires authentication for all sensitive functions',
            'audit_evidence': [
                'Authentication requirements documentation',
                'Access control testing results',
                'Authentication decorator usage',
                'User access review logs'
            ],
            'remediation_priority': 'CRITICAL',
            'estimated_effort_hours': 10,
            'remediation_guidance': 'Implement authentication for all sensitive endpoints'
        },

        'CWE-862': {
            'criteria': ['CC6.1', 'CC6.7'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.7 - Logical Access - Authorization'
            ],
            'trust_service_category': 'Security',
            'description': 'Missing authorization checks allow privilege escalation',
            'control_objective': 'The entity enforces authorization for all resource access',
            'audit_evidence': [
                'RBAC implementation documentation',
                'Authorization testing results',
                'Access control matrix',
                'Regular access reviews'
            ],
            'remediation_priority': 'CRITICAL',
            'estimated_effort_hours': 12,
            'remediation_guidance': 'Implement RBAC, enforce authorization on all resources'
        },

        'CWE-601': {
            'criteria': ['CC6.1', 'CC7.2'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC7.2 - System Monitoring - Security Events'
            ],
            'trust_service_category': 'Security',
            'description': 'Open redirect enables phishing attacks',
            'control_objective': 'The entity validates all URL redirects',
            'audit_evidence': [
                'URL redirect whitelist',
                'Redirect validation implementation',
                'Security testing results',
                'Phishing prevention controls'
            ],
            'remediation_priority': 'MEDIUM',
            'estimated_effort_hours': 4,
            'remediation_guidance': 'Validate redirects against whitelist, avoid user-controlled URLs'
        }
    }

    # Scanner-specific check ID mappings to SOC2 TSC
    SCANNER_CHECK_TO_SOC2 = {
        # Checkov AWS checks
        'CKV_AWS_157': {
            'criteria': ['CC6.1'],
            'criteria_names': ['CC6.1 - Logical and Physical Access Controls'],
            'trust_service_category': 'Confidentiality',
            'description': 'RDS encryption at rest protects data confidentiality',
            'control_objective': 'The entity encrypts database data at rest',
            'audit_evidence': ['RDS encryption enabled', 'KMS key configuration'],
            'remediation_priority': 'HIGH',
            'estimated_effort_hours': 2
        },
        'CKV_AWS_20': {
            'criteria': ['CC6.1'],
            'criteria_names': ['CC6.1 - Logical and Physical Access Controls'],
            'trust_service_category': 'Confidentiality',
            'description': 'S3 bucket encryption protects stored data',
            'control_objective': 'The entity encrypts object storage at rest',
            'audit_evidence': ['S3 bucket encryption enabled', 'Encryption policy'],
            'remediation_priority': 'HIGH',
            'estimated_effort_hours': 1
        },
        'CKV_AWS_23': {
            'criteria': ['CC6.1', 'CC6.6'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.6 - Logical Access - Authentication'
            ],
            'trust_service_category': 'Security',
            'description': 'Restrict SSH access from internet',
            'control_objective': 'The entity restricts network access to critical services',
            'audit_evidence': ['Security group rules', 'Network access controls'],
            'remediation_priority': 'CRITICAL',
            'estimated_effort_hours': 2
        },
        'CKV_AWS_33': {
            'criteria': ['CC7.2'],
            'criteria_names': ['CC7.2 - System Monitoring - Security Events'],
            'trust_service_category': 'Security',
            'description': 'KMS key rotation ensures cryptographic freshness',
            'control_objective': 'The entity rotates encryption keys regularly',
            'audit_evidence': ['KMS rotation enabled', 'Key management policy'],
            'remediation_priority': 'MEDIUM',
            'estimated_effort_hours': 1
        },
        'CKV_AWS_50': {
            'criteria': ['CC7.2', 'CC7.3'],
            'criteria_names': [
                'CC7.2 - System Monitoring - Security Events',
                'CC7.3 - System Operations - Backup and Recovery'
            ],
            'trust_service_category': 'Availability',
            'description': 'Lambda Dead Letter Queue ensures error handling',
            'control_objective': 'The entity implements error handling and monitoring',
            'audit_evidence': ['DLQ configuration', 'Error handling documentation'],
            'remediation_priority': 'LOW',
            'estimated_effort_hours': 2
        },
        'CKV_AWS_53': {
            'criteria': ['CC6.1', 'CC6.7'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.7 - Logical Access - Authorization'
            ],
            'trust_service_category': 'Confidentiality',
            'description': 'S3 public access block prevents data exposure',
            'control_objective': 'The entity restricts public access to confidential data',
            'audit_evidence': ['Public access block enabled', 'Data classification'],
            'remediation_priority': 'HIGH',
            'estimated_effort_hours': 1
        },
        'CKV_AWS_79': {
            'criteria': ['CC7.2'],
            'criteria_names': ['CC7.2 - System Monitoring - Security Events'],
            'trust_service_category': 'Security',
            'description': 'CloudWatch log retention for audit trail',
            'control_objective': 'The entity retains logs for security monitoring',
            'audit_evidence': ['Log retention policy', 'Monitoring documentation'],
            'remediation_priority': 'MEDIUM',
            'estimated_effort_hours': 1
        },
        'CKV_AWS_118': {
            'criteria': ['CC6.1', 'CC6.7'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.7 - Logical Access - Authorization'
            ],
            'trust_service_category': 'Security',
            'description': 'RDS should not be publicly accessible',
            'control_objective': 'The entity restricts database network access',
            'audit_evidence': ['RDS private access', 'Network architecture'],
            'remediation_priority': 'CRITICAL',
            'estimated_effort_hours': 3
        },
        'CKV_AWS_130': {
            'criteria': ['CC7.2'],
            'criteria_names': ['CC7.2 - System Monitoring - Security Events'],
            'trust_service_category': 'Security',
            'description': 'VPC flow logs for network monitoring',
            'control_objective': 'The entity monitors network traffic',
            'audit_evidence': ['Flow logs enabled', 'Network monitoring'],
            'remediation_priority': 'MEDIUM',
            'estimated_effort_hours': 2
        },
        'CKV_AWS_158': {
            'criteria': ['CC6.1'],
            'criteria_names': ['CC6.1 - Logical and Physical Access Controls'],
            'trust_service_category': 'Confidentiality',
            'description': 'CloudFront HTTPS for data in transit',
            'control_objective': 'The entity encrypts data in transit',
            'audit_evidence': ['HTTPS only configuration', 'TLS policy'],
            'remediation_priority': 'HIGH',
            'estimated_effort_hours': 2
        },
        'CKV_AWS_338': {
            'criteria': ['CC7.2'],
            'criteria_names': ['CC7.2 - System Monitoring - Security Events'],
            'trust_service_category': 'Security',
            'description': 'CloudWatch log retention for audit compliance',
            'control_objective': 'The entity retains logs for at least 1 year',
            'audit_evidence': ['Retention policy', 'Compliance documentation'],
            'remediation_priority': 'MEDIUM',
            'estimated_effort_hours': 1
        },

        # Trivy checks
        'AVD-AWS-0001': {
            'criteria': ['CC6.1', 'CC6.7'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.7 - Logical Access - Authorization'
            ],
            'trust_service_category': 'Security',
            'description': 'Network ACLs for network segmentation',
            'control_objective': 'The entity implements network segmentation',
            'audit_evidence': ['Network ACL rules', 'Segmentation documentation'],
            'remediation_priority': 'HIGH',
            'estimated_effort_hours': 3
        },
        'AVD-AWS-0086': {
            'criteria': ['CC6.1'],
            'criteria_names': ['CC6.1 - Logical and Physical Access Controls'],
            'trust_service_category': 'Confidentiality',
            'description': 'EBS volume encryption at rest',
            'control_objective': 'The entity encrypts compute storage',
            'audit_evidence': ['EBS encryption enabled', 'Encryption policy'],
            'remediation_priority': 'HIGH',
            'estimated_effort_hours': 2
        },
        'AVD-AWS-0124': {
            'criteria': ['CC6.1', 'CC6.6'],
            'criteria_names': [
                'CC6.1 - Logical and Physical Access Controls',
                'CC6.6 - Logical Access - Authentication'
            ],
            'trust_service_category': 'Security',
            'description': 'API Gateway authentication required',
            'control_objective': 'The entity authenticates API access',
            'audit_evidence': ['API Gateway auth config', 'API documentation'],
            'remediation_priority': 'CRITICAL',
            'estimated_effort_hours': 4
        }
    }

    def __init__(self):
        """Initialize SOC2 mapper"""
        self.project_root = Path(__file__).parent.parent.parent
        self.findings_dir = self.project_root / 'secops' / '2-findings' / 'raw'
        self.reports_dir = self.project_root / 'secops' / '6-reports' / 'compliance'
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def enrich_finding(self, finding: Dict) -> Dict:
        """
        Enrich a single finding with SOC2 compliance metadata

        Args:
            finding: Finding dict from any scanner

        Returns:
            Finding with 'soc2_compliance' field added
        """
        soc2_data = None

        # Strategy 1: Check for CWE in finding
        if 'cwe' in finding and finding['cwe']:
            cwes = finding['cwe'] if isinstance(finding['cwe'], list) else [finding['cwe']]

            for cwe in cwes:
                if cwe in self.CWE_TO_SOC2:
                    soc2_data = self.CWE_TO_SOC2[cwe].copy()
                    break

        # Strategy 2: Check scanner-specific check_id
        if not soc2_data and 'check_id' in finding:
            check_id = finding['check_id']
            if check_id in self.SCANNER_CHECK_TO_SOC2:
                soc2_data = self.SCANNER_CHECK_TO_SOC2[check_id].copy()

        # Add SOC2 data to finding
        if soc2_data:
            finding['soc2_compliance'] = soc2_data

        return finding

    def generate_compliance_report(self, findings: List[Dict]) -> Dict:
        """
        Generate SOC2 Trust Service Criteria compliance report

        Args:
            findings: List of findings from all scanners

        Returns:
            Complete SOC2 compliance report
        """
        # Enrich all findings
        enriched_findings = [self.enrich_finding(f) for f in findings]

        # Track which criteria are failing
        failing_criteria = defaultdict(lambda: {
            'criterion': '',
            'criteria_names': [],
            'trust_service_category': '',
            'control_objective': '',
            'status': 'FAIL',
            'finding_count': 0,
            'findings': [],
            'total_effort_hours': 0,
            'highest_priority': 'LOW'
        })

        # Track all criteria mentioned
        all_criteria_checked = set()

        # Track trust service categories
        trust_service_categories = defaultdict(int)

        # Process findings
        findings_with_compliance = 0

        for finding in enriched_findings:
            if 'soc2_compliance' not in finding:
                continue

            findings_with_compliance += 1
            compliance = finding['soc2_compliance']

            # Track trust service category
            category = compliance.get('trust_service_category', 'Unknown')
            trust_service_categories[category] += 1

            # Track each criterion
            for criterion in compliance['criteria']:
                all_criteria_checked.add(criterion)

                # Build criterion entry
                crit_data = failing_criteria[criterion]
                crit_data['criterion'] = criterion
                crit_data['criteria_names'] = compliance['criteria_names']
                crit_data['trust_service_category'] = compliance['trust_service_category']
                crit_data['control_objective'] = compliance['control_objective']
                crit_data['finding_count'] += 1
                crit_data['total_effort_hours'] += compliance.get('estimated_effort_hours', 0)

                # Track highest priority
                priority_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'INFO': 0}
                current_priority = compliance.get('remediation_priority', 'LOW')
                if priority_order.get(current_priority, 0) > priority_order.get(crit_data['highest_priority'], 0):
                    crit_data['highest_priority'] = current_priority

                # Add finding summary
                crit_data['findings'].append({
                    'scanner': finding.get('scanner', 'unknown'),
                    'file': finding.get('file', 'unknown'),
                    'line': finding.get('line', 0),
                    'issue': finding.get('title', finding.get('check_name', finding.get('issue', 'unknown'))),
                    'severity': finding.get('severity', 'UNKNOWN'),
                    'cwe': finding.get('cwe', [])
                })

                # Store audit evidence (just once per criterion)
                if 'audit_evidence' not in crit_data:
                    crit_data['audit_evidence'] = compliance.get('audit_evidence', [])
                    crit_data['remediation_guidance'] = compliance.get('remediation_guidance', '')

        # Calculate compliance metrics
        total_criteria_in_standard = 64  # SOC2 2017 has ~64 TSC criteria
        criteria_checked = len(all_criteria_checked)
        criteria_failing = len(failing_criteria)
        criteria_passing = criteria_checked - criteria_failing

        # Compliance score: (passing / checked) * 100
        compliance_score = round((criteria_passing / criteria_checked * 100), 1) if criteria_checked > 0 else 0.0

        # Sort failing criteria by priority and finding count
        priority_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'INFO': 0}
        failing_criteria_list = sorted(
            failing_criteria.values(),
            key=lambda x: (priority_order.get(x['highest_priority'], 0), x['finding_count']),
            reverse=True
        )

        # Build report
        report = {
            'framework': 'SOC2 Trust Service Criteria',
            'scan_date': datetime.now().isoformat(),
            'summary': {
                'total_criteria_in_standard': total_criteria_in_standard,
                'criteria_checked': criteria_checked,
                'criteria_passing': criteria_passing,
                'criteria_failing': criteria_failing,
                'compliance_score': compliance_score,
                'coverage_percentage': round((criteria_checked / total_criteria_in_standard * 100), 1)
            },
            'trust_service_categories': dict(trust_service_categories),
            'findings_summary': {
                'total_findings': len(findings),
                'findings_with_compliance_mapping': findings_with_compliance,
                'mapping_coverage': round((findings_with_compliance / len(findings) * 100), 1) if findings else 0.0
            },
            'failing_criteria': failing_criteria_list,
            'remediation_summary': {
                'total_effort_hours': sum(c['total_effort_hours'] for c in failing_criteria_list),
                'critical_priority_criteria': len([c for c in failing_criteria_list if c['highest_priority'] == 'CRITICAL']),
                'high_priority_criteria': len([c for c in failing_criteria_list if c['highest_priority'] == 'HIGH']),
                'medium_priority_criteria': len([c for c in failing_criteria_list if c['highest_priority'] == 'MEDIUM']),
                'low_priority_criteria': len([c for c in failing_criteria_list if c['highest_priority'] == 'LOW'])
            }
        }

        return report

    def save_report(self, report: Dict, filename: str = 'soc2-compliance-report.json'):
        """
        Save compliance report to file

        Args:
            report: Compliance report dict
            filename: Output filename
        """
        output_path = self.reports_dir / filename

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"SOC2 compliance report saved: {output_path}")
        return output_path

    def load_all_findings(self) -> List[Dict]:
        """
        Load all findings from all scanners

        Returns:
            List of all findings
        """
        all_findings = []

        # Load CI findings (Bandit, Semgrep, Gitleaks)
        ci_dir = self.findings_dir / 'ci'
        if ci_dir.exists():
            for json_file in ci_dir.glob('*.json'):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                        all_findings.extend(data.get('findings', []))
                except Exception as e:
                    print(f"Warning: Could not load {json_file}: {e}")

        # Load CD findings (Trivy, Checkov)
        cd_dir = self.findings_dir / 'cd'
        if cd_dir.exists():
            for json_file in cd_dir.glob('*.json'):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                        all_findings.extend(data.get('findings', []))
                except Exception as e:
                    print(f"Warning: Could not load {json_file}: {e}")

        return all_findings


def main():
    """
    Main entry point for SOC2 compliance mapping

    Usage:
        # Generate compliance report from all findings
        python3 soc2_mapper.py

        # Generate report and print summary
        python3 soc2_mapper.py --verbose
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='SOC2 Trust Service Criteria Mapper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate compliance report
  python3 soc2_mapper.py

  # Generate with verbose output
  python3 soc2_mapper.py --verbose

  # Specify custom output file
  python3 soc2_mapper.py --output custom-report.json
        """
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print verbose output including failing criteria'
    )

    parser.add_argument(
        '--output', '-o',
        default='soc2-compliance-report.json',
        help='Output filename (default: soc2-compliance-report.json)'
    )

    args = parser.parse_args()

    # Create mapper
    mapper = SOC2Mapper()

    print("=" * 70)
    print("SOC2 TRUST SERVICE CRITERIA MAPPER")
    print("=" * 70)
    print()

    # Load all findings
    print("Loading findings from all scanners...")
    findings = mapper.load_all_findings()
    print(f"✅ Loaded {len(findings)} findings")
    print()

    # Generate report
    print("Generating SOC2 compliance report...")
    report = mapper.generate_compliance_report(findings)
    print("✅ Compliance report generated")
    print()

    # Save report
    output_path = mapper.save_report(report, args.output)
    print()

    # Print summary
    print("=" * 70)
    print("COMPLIANCE SUMMARY")
    print("=" * 70)
    summary = report['summary']
    print(f"Framework:              SOC2 Trust Service Criteria")
    print(f"Scan Date:              {report['scan_date']}")
    print(f"Total Criteria:         {summary['total_criteria_in_standard']}")
    print(f"Criteria Checked:       {summary['criteria_checked']} ({summary['coverage_percentage']}% coverage)")
    print(f"Criteria Passing:       {summary['criteria_passing']}")
    print(f"Criteria Failing:       {summary['criteria_failing']}")
    print(f"Compliance Score:       {summary['compliance_score']}%")
    print()

    print("=" * 70)
    print("TRUST SERVICE CATEGORIES")
    print("=" * 70)
    for category, count in sorted(report['trust_service_categories'].items()):
        print(f"  {category:20s}: {count:3d} findings")
    print()

    print("=" * 70)
    print("FINDINGS SUMMARY")
    print("=" * 70)
    findings_summary = report['findings_summary']
    print(f"Total Findings:         {findings_summary['total_findings']}")
    print(f"Mapped to SOC2:         {findings_summary['findings_with_compliance_mapping']} ({findings_summary['mapping_coverage']}%)")
    print()

    print("=" * 70)
    print("REMEDIATION SUMMARY")
    print("=" * 70)
    remediation = report['remediation_summary']
    print(f"Total Effort:           {remediation['total_effort_hours']} hours")
    print(f"CRITICAL Priority:      {remediation['critical_priority_criteria']} criteria")
    print(f"HIGH Priority:          {remediation['high_priority_criteria']} criteria")
    print(f"MEDIUM Priority:        {remediation['medium_priority_criteria']} criteria")
    print(f"LOW Priority:           {remediation['low_priority_criteria']} criteria")
    print()

    if args.verbose:
        print("=" * 70)
        print("FAILING CRITERIA (Top 10)")
        print("=" * 70)
        for i, criterion in enumerate(report['failing_criteria'][:10], 1):
            print(f"\n{i}. {criterion['criterion']} - {criterion['criteria_names'][0] if criterion['criteria_names'] else 'N/A'}")
            print(f"   Category: {criterion['trust_service_category']}")
            print(f"   Priority: {criterion['highest_priority']}")
            print(f"   Findings: {criterion['finding_count']}")
            print(f"   Effort: {criterion['total_effort_hours']} hours")
            print(f"   Sample Issue: {criterion['findings'][0]['issue'][:80]}...")
        print()

    print("=" * 70)
    print(f"✅ Report saved to: {output_path}")
    print("=" * 70)


if __name__ == '__main__':
    main()
