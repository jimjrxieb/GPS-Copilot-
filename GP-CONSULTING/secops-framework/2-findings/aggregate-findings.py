#!/usr/bin/env python3
"""
SecOps Phase 2: REPORT - Aggregate Security Findings
Aggregates raw scanner outputs into unified compliance reports
"""

import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any

# Compliance framework mappings
PCI_DSS_MAPPING = {
    'encryption_at_rest': '3.4 - Render PAN unreadable (encryption)',
    'public_database': '1.2.1 - Restrict inbound/outbound traffic',
    'hardcoded_credentials': '8.2.1 - Strong authentication',
    'cvv_storage': '3.2.2 - Do not store CVV2/CVC2/CID',
    'pin_storage': '3.2.3 - Do not store PIN/PIN block',
    'no_mfa': '8.3.1 - Multi-factor authentication',
    'insufficient_logging': '10.1 - Implement audit trails',
    'public_s3_bucket': '1.2.1 - Restrict public access',
    'no_encryption_transit': '4.1 - Encrypt transmission of cardholder data',
    'weak_password_policy': '8.2.3 - Password complexity requirements'
}

SOC2_MAPPING = {
    'encryption_at_rest': 'CC6.1 - Logical and physical access controls',
    'public_database': 'CC6.6 - Network security',
    'hardcoded_credentials': 'CC6.1 - Credential management',
    'insufficient_logging': 'CC7.2 - Monitoring activities',
    'no_mfa': 'CC6.1 - Multi-factor authentication'
}

CIS_MAPPING = {
    'public_database': '4.1 - Ensure no DB instances are publicly accessible',
    'encryption_at_rest': '2.3.1 - Ensure RDS encryption is enabled',
    'public_s3_bucket': '2.1.1 - Ensure S3 bucket access logging is enabled',
    'no_mfa': '1.2 - Ensure MFA is enabled for all IAM users'
}

CVSS_SEVERITY = {
    'CRITICAL': {'min': 9.0, 'max': 10.0},
    'HIGH': {'min': 7.0, 'max': 8.9},
    'MEDIUM': {'min': 4.0, 'max': 6.9},
    'LOW': {'min': 0.1, 'max': 3.9}
}

def load_scanner_results(raw_dir: str) -> Dict[str, Any]:
    """Load all scanner JSON results"""
    results = {}

    scanner_files = {
        'tfsec': 'tfsec-results.json',
        'checkov': 'checkov-results.json',
        'bandit': 'bandit-results.json',
        'trivy_backend': 'trivy-backend-results.json',
        'trivy_frontend': 'trivy-frontend-results.json',
        'gitleaks': 'gitleaks-results.json',
        'semgrep': 'semgrep-results.json',
        'opa': 'opa-test-results.json',
        'conftest': 'conftest-results.json'
    }

    for scanner, filename in scanner_files.items():
        filepath = os.path.join(raw_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    results[scanner] = json.load(f)
                print(f"✅ Loaded {scanner} results")
            except json.JSONDecodeError:
                print(f"⚠️  Failed to parse {scanner} results")
                results[scanner] = {}
        else:
            print(f"⚠️  {scanner} results not found")
            results[scanner] = {}

    return results

def parse_tfsec(data: Dict) -> List[Dict]:
    """Parse tfsec results"""
    findings = []
    if not data or 'results' not in data:
        return findings

    for result in data.get('results', []):
        severity = result.get('severity') or 'MEDIUM'
        severity = severity.upper() if isinstance(severity, str) else 'MEDIUM'

        findings.append({
            'id': result.get('rule_id', 'TFSEC-UNKNOWN'),
            'severity': severity,
            'title': result.get('description', 'Terraform security issue'),
            'description': result.get('long_id', ''),
            'location': f"{result.get('location', {}).get('filename', 'unknown')}:{result.get('location', {}).get('start_line', 0)}",
            'scanner': 'tfsec',
            'category': 'infrastructure'
        })

    return findings

def parse_checkov(data: Dict) -> List[Dict]:
    """Parse Checkov results"""
    findings = []
    if not data:
        return findings

    for result in data.get('results', {}).get('failed_checks', []):
        # Handle None severity
        severity = result.get('severity') or 'MEDIUM'
        severity = severity.upper() if isinstance(severity, str) else 'MEDIUM'

        # Handle None description
        description = result.get('description') or result.get('check_name', '')

        findings.append({
            'id': result.get('check_id', 'CHECKOV-UNKNOWN'),
            'severity': severity,
            'title': result.get('check_name', 'Policy violation'),
            'description': description,
            'location': f"{result.get('file_path', 'unknown')}:{result.get('file_line_range', [0])[0]}",
            'scanner': 'checkov',
            'category': 'infrastructure'
        })

    return findings

def parse_bandit(data: Dict) -> List[Dict]:
    """Parse Bandit results"""
    findings = []
    if not data or 'results' not in data:
        return findings

    for result in data.get('results', []):
        severity = result.get('issue_severity') or 'MEDIUM'
        severity = severity.upper() if isinstance(severity, str) else 'MEDIUM'

        findings.append({
            'id': result.get('test_id', 'BANDIT-UNKNOWN'),
            'severity': severity,
            'title': result.get('issue_text', 'Python security issue'),
            'description': result.get('issue_text', ''),
            'location': f"{result.get('filename', 'unknown')}:{result.get('line_number', 0)}",
            'scanner': 'bandit',
            'category': 'code'
        })

    return findings

def parse_trivy(data: Dict, component: str) -> List[Dict]:
    """Parse Trivy results"""
    findings = []
    if not data or 'Results' not in data:
        return findings

    for result in data.get('Results', []):
        for vuln in result.get('Vulnerabilities', []) or []:
            severity = vuln.get('Severity') or 'MEDIUM'
            severity = severity.upper() if isinstance(severity, str) else 'MEDIUM'

            findings.append({
                'id': vuln.get('VulnerabilityID', 'CVE-UNKNOWN'),
                'severity': severity,
                'title': vuln.get('Title', 'Container vulnerability'),
                'description': vuln.get('Description', ''),
                'location': f"{component}:{vuln.get('PkgName', 'unknown')}",
                'scanner': 'trivy',
                'category': 'container'
            })

    return findings

def parse_gitleaks(data: Dict) -> List[Dict]:
    """Parse Gitleaks results"""
    findings = []
    if not data:
        return findings

    for result in data if isinstance(data, list) else []:
        findings.append({
            'id': f"SECRET-{result.get('RuleID', 'UNKNOWN')}",
            'severity': 'HIGH',
            'title': f"Hardcoded secret: {result.get('Description', 'Unknown')}",
            'description': result.get('Match', ''),
            'location': f"{result.get('File', 'unknown')}:{result.get('StartLine', 0)}",
            'scanner': 'gitleaks',
            'category': 'secrets'
        })

    return findings

def parse_semgrep(data: Dict) -> List[Dict]:
    """Parse Semgrep results"""
    findings = []
    if not data or 'results' not in data:
        return findings

    for result in data.get('results', []):
        extra = result.get('extra', {}) or {}
        severity = extra.get('severity') or 'MEDIUM'
        severity = severity.upper() if isinstance(severity, str) else 'MEDIUM'
        message = extra.get('message', 'Code security issue')

        findings.append({
            'id': result.get('check_id', 'SEMGREP-UNKNOWN'),
            'severity': severity,
            'title': message,
            'description': message,
            'location': f"{result.get('path', 'unknown')}:{result.get('start', {}).get('line', 0)}",
            'scanner': 'semgrep',
            'category': 'code'
        })

    return findings

def deduplicate_findings(findings: List[Dict]) -> List[Dict]:
    """Remove duplicate findings across scanners"""
    seen = set()
    unique_findings = []

    for finding in findings:
        # Create a unique key based on location and title
        key = f"{finding['location']}:{finding['title']}"
        if key not in seen:
            seen.add(key)
            unique_findings.append(finding)

    return unique_findings

def map_to_compliance(finding: Dict) -> Dict:
    """Map finding to compliance frameworks"""
    compliance = {}

    # Simple keyword matching for demo
    title_lower = finding['title'].lower()

    if 'encrypt' in title_lower or 'encryption' in title_lower:
        compliance['pci_dss'] = PCI_DSS_MAPPING.get('encryption_at_rest', '')
        compliance['soc2'] = SOC2_MAPPING.get('encryption_at_rest', '')
        compliance['cis'] = CIS_MAPPING.get('encryption_at_rest', '')

    if 'public' in title_lower and 'database' in title_lower:
        compliance['pci_dss'] = PCI_DSS_MAPPING.get('public_database', '')
        compliance['soc2'] = SOC2_MAPPING.get('public_database', '')
        compliance['cis'] = CIS_MAPPING.get('public_database', '')

    if 'secret' in title_lower or 'credential' in title_lower or 'password' in title_lower:
        compliance['pci_dss'] = PCI_DSS_MAPPING.get('hardcoded_credentials', '')
        compliance['soc2'] = SOC2_MAPPING.get('hardcoded_credentials', '')

    if 'cvv' in title_lower or 'cvc' in title_lower:
        compliance['pci_dss'] = PCI_DSS_MAPPING.get('cvv_storage', '')

    if 'pin' in title_lower:
        compliance['pci_dss'] = PCI_DSS_MAPPING.get('pin_storage', '')

    finding['compliance'] = compliance
    return finding

def calculate_statistics(findings: List[Dict]) -> Dict:
    """Calculate finding statistics"""
    stats = {
        'total': len(findings),
        'by_severity': defaultdict(int),
        'by_category': defaultdict(int),
        'by_scanner': defaultdict(int)
    }

    for finding in findings:
        stats['by_severity'][finding['severity']] += 1
        stats['by_category'][finding['category']] += 1
        stats['by_scanner'][finding['scanner']] += 1

    return dict(stats)

def generate_security_audit_md(findings: List[Dict], stats: Dict, output_dir: str):
    """Generate SECURITY-AUDIT.md report"""
    report_path = os.path.join(output_dir, 'SECURITY-AUDIT.md')

    with open(report_path, 'w') as f:
        f.write("# Security Audit Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Findings:** {stats['total']}\n\n")

        f.write("## Executive Summary\n\n")
        f.write("| Severity | Count |\n")
        f.write("|----------|-------|\n")
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = stats['by_severity'].get(severity, 0)
            f.write(f"| {severity} | {count} |\n")

        f.write("\n## Findings by Category\n\n")
        f.write("| Category | Count |\n")
        f.write("|----------|-------|\n")
        for category, count in stats['by_category'].items():
            f.write(f"| {category.upper()} | {count} |\n")

        f.write("\n## Top 10 Critical Findings\n\n")
        critical_findings = [f for f in findings if f['severity'] in ['CRITICAL', 'HIGH']]
        for i, finding in enumerate(critical_findings[:10], 1):
            f.write(f"### {i}. {finding['title']}\n")
            f.write(f"- **Severity:** {finding['severity']}\n")
            f.write(f"- **Location:** `{finding['location']}`\n")
            f.write(f"- **Scanner:** {finding['scanner']}\n")
            if finding.get('compliance', {}).get('pci_dss'):
                f.write(f"- **PCI-DSS:** {finding['compliance']['pci_dss']}\n")
            f.write("\n")

    print(f"✅ Generated: {report_path}")

def generate_pci_dss_violations_md(findings: List[Dict], output_dir: str):
    """Generate PCI-DSS-VIOLATIONS.md report"""
    report_path = os.path.join(output_dir, 'PCI-DSS-VIOLATIONS.md')

    pci_findings = [f for f in findings if f.get('compliance', {}).get('pci_dss')]

    with open(report_path, 'w') as f:
        f.write("# PCI-DSS Compliance Violations\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total PCI-DSS Violations:** {len(pci_findings)}\n\n")

        f.write("## Violations by Requirement\n\n")

        by_requirement = defaultdict(list)
        for finding in pci_findings:
            req = finding['compliance']['pci_dss']
            by_requirement[req].append(finding)

        for req, req_findings in sorted(by_requirement.items()):
            f.write(f"### {req}\n")
            f.write(f"**Count:** {len(req_findings)}\n\n")
            for finding in req_findings:
                f.write(f"- **{finding['title']}** ({finding['severity']})\n")
                f.write(f"  - Location: `{finding['location']}`\n")
            f.write("\n")

    print(f"✅ Generated: {report_path}")

def generate_all_findings_json(findings: List[Dict], output_dir: str):
    """Generate all-findings.json"""
    output_path = os.path.join(output_dir, 'all-findings.json')

    with open(output_path, 'w') as f:
        json.dump(findings, f, indent=2)

    print(f"✅ Generated: {output_path}")

def main():
    print("🔍 SecOps Phase 2: REPORT - Aggregating findings...")
    print("═══════════════════════════════════════════════════════")

    raw_dir = 'raw'
    output_dir = 'reports'
    os.makedirs(output_dir, exist_ok=True)

    # Load scanner results
    print("\n→ Loading scanner results...")
    scanner_data = load_scanner_results(raw_dir)

    # Parse findings
    print("\n→ Parsing findings...")
    all_findings = []
    all_findings.extend(parse_tfsec(scanner_data.get('tfsec', {})))
    all_findings.extend(parse_checkov(scanner_data.get('checkov', {})))
    all_findings.extend(parse_bandit(scanner_data.get('bandit', {})))
    all_findings.extend(parse_trivy(scanner_data.get('trivy_backend', {}), 'backend'))
    all_findings.extend(parse_trivy(scanner_data.get('trivy_frontend', {}), 'frontend'))
    all_findings.extend(parse_gitleaks(scanner_data.get('gitleaks', {})))
    all_findings.extend(parse_semgrep(scanner_data.get('semgrep', {})))

    # Deduplicate
    print("\n→ Deduplicating findings...")
    unique_findings = deduplicate_findings(all_findings)

    # Map to compliance
    print("\n→ Mapping to compliance frameworks...")
    for finding in unique_findings:
        map_to_compliance(finding)

    # Calculate statistics
    print("\n→ Calculating statistics...")
    stats = calculate_statistics(unique_findings)

    # Generate reports
    print("\n→ Generating reports...")
    generate_security_audit_md(unique_findings, stats, output_dir)
    generate_pci_dss_violations_md(unique_findings, output_dir)
    generate_all_findings_json(unique_findings, output_dir)

    print("\n✅ Aggregation complete!")
    print(f"\n📊 Summary:")
    print(f"   - Total findings: {stats['total']}")
    print(f"   - Critical: {stats['by_severity'].get('CRITICAL', 0)}")
    print(f"   - High: {stats['by_severity'].get('HIGH', 0)}")
    print(f"   - Medium: {stats['by_severity'].get('MEDIUM', 0)}")
    print(f"   - Low: {stats['by_severity'].get('LOW', 0)}")
    print(f"\n📁 Reports saved to: {output_dir}/")

if __name__ == '__main__':
    main()
