#!/usr/bin/env python3
"""
Trivy Output Normalizer - Convert Trivy JSON to standardized findings
"""

import json
from typing import List, Dict, Any
from datetime import datetime


def normalize(raw_json: dict, run_id: str, project_id: str) -> List[Dict[str, Any]]:
    """
    Convert Trivy raw JSON output to normalized findings format.

    Args:
        raw_json: Raw Trivy JSON output
        run_id: Unique identifier for this scan run
        project_id: Project identifier

    Returns:
        List of normalized finding dictionaries
    """
    findings = []
    timestamp = datetime.now().isoformat()

    try:
        # Handle Trivy v2 format with Results array
        results = raw_json.get("Results", [])
        if not results:
            # Handle older format or empty results
            return findings

        for result in results:
            target = result.get("Target", "unknown")
            result_type = result.get("Type", "unknown")

            # Process vulnerabilities
            vulnerabilities = result.get("Vulnerabilities", [])
            for vuln in vulnerabilities:
                finding = {
                    "ts": timestamp,
                    "project_id": project_id,
                    "tool": "trivy",
                    "run_id": run_id,
                    "artifact": target,
                    "type": "vuln",
                    "id": vuln.get("VulnerabilityID", "unknown"),
                    "severity": _normalize_severity(vuln.get("Severity", "UNKNOWN")),
                    "title": vuln.get("Title", vuln.get("VulnerabilityID", "Unknown Vulnerability")),
                    "location": f"{target}",
                    "status": "open",
                    "recommendation": _extract_recommendation(vuln),
                    "evidence_sha256": "",  # Will be filled by evidence system
                    "links": _extract_links(vuln),
                    "metadata": {
                        "package_name": vuln.get("PkgName", ""),
                        "installed_version": vuln.get("InstalledVersion", ""),
                        "fixed_version": vuln.get("FixedVersion", ""),
                        "cvss_score": _extract_cvss_score(vuln),
                        "published_date": vuln.get("PublishedDate", ""),
                        "last_modified": vuln.get("LastModifiedDate", "")
                    }
                }
                findings.append(finding)

            # Process misconfigurations
            misconfigs = result.get("Misconfigurations", [])
            for misconfig in misconfigs:
                finding = {
                    "ts": timestamp,
                    "project_id": project_id,
                    "tool": "trivy",
                    "run_id": run_id,
                    "artifact": target,
                    "type": "misconfig",
                    "id": misconfig.get("ID", "unknown"),
                    "severity": _normalize_severity(misconfig.get("Severity", "UNKNOWN")),
                    "title": misconfig.get("Title", "Configuration Issue"),
                    "location": f"{target}:{misconfig.get('CauseMetadata', {}).get('StartLine', '')}",
                    "status": "open",
                    "recommendation": misconfig.get("Resolution", "Review configuration"),
                    "evidence_sha256": "",
                    "links": [misconfig.get("PrimaryURL", "")] if misconfig.get("PrimaryURL") else [],
                    "metadata": {
                        "check_type": misconfig.get("Type", ""),
                        "namespace": misconfig.get("Namespace", ""),
                        "query": misconfig.get("Query", ""),
                        "message": misconfig.get("Message", "")
                    }
                }
                findings.append(finding)

            # Process secrets
            secrets = result.get("Secrets", [])
            for secret in secrets:
                finding = {
                    "ts": timestamp,
                    "project_id": project_id,
                    "tool": "trivy",
                    "run_id": run_id,
                    "artifact": target,
                    "type": "secret",
                    "id": secret.get("RuleID", "unknown"),
                    "severity": "HIGH",  # Secrets are always high severity
                    "title": secret.get("Title", "Exposed Secret"),
                    "location": f"{target}:{secret.get('StartLine', '')}",
                    "status": "open",
                    "recommendation": "Remove or encrypt the exposed secret",
                    "evidence_sha256": "",
                    "links": [],
                    "metadata": {
                        "category": secret.get("Category", ""),
                        "match": secret.get("Match", ""),
                        "start_line": secret.get("StartLine", ""),
                        "end_line": secret.get("EndLine", "")
                    }
                }
                findings.append(finding)

    except Exception as e:
        # Create error finding if normalization fails
        error_finding = {
            "ts": timestamp,
            "project_id": project_id,
            "tool": "trivy",
            "run_id": run_id,
            "artifact": "normalization_error",
            "type": "error",
            "id": "NORMALIZE_ERROR",
            "severity": "MEDIUM",
            "title": f"Trivy normalization failed: {str(e)}",
            "location": "normalizer",
            "status": "open",
            "recommendation": "Review raw Trivy output and fix normalizer",
            "evidence_sha256": "",
            "links": [],
            "metadata": {"error": str(e)}
        }
        findings.append(error_finding)

    return findings


def _normalize_severity(severity: str) -> str:
    """Normalize Trivy severity to standard levels"""
    severity_map = {
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW",
        "NEGLIGIBLE": "INFO",
        "UNKNOWN": "UNKNOWN"
    }
    return severity_map.get(severity.upper(), "UNKNOWN")


def _extract_recommendation(vuln: Dict) -> str:
    """Extract actionable recommendation from vulnerability"""
    if vuln.get("FixedVersion"):
        package = vuln.get("PkgName", "package")
        fixed_version = vuln.get("FixedVersion")
        return f"Update {package} to version {fixed_version} or later"

    return vuln.get("Description", "Review vulnerability details and apply appropriate fixes")


def _extract_links(vuln: Dict) -> List[str]:
    """Extract reference links from vulnerability"""
    links = []

    if vuln.get("PrimaryURL"):
        links.append(vuln["PrimaryURL"])

    if vuln.get("References"):
        for ref in vuln["References"]:
            if isinstance(ref, str):
                links.append(ref)
            elif isinstance(ref, dict) and ref.get("URL"):
                links.append(ref["URL"])

    return links[:5]  # Limit to 5 links to prevent bloat


def _extract_cvss_score(vuln: Dict) -> float:
    """Extract CVSS score from vulnerability"""
    cvss = vuln.get("CVSS", {})

    # Try different CVSS versions
    for version in ["nvd", "redhat", "amazon"]:
        if version in cvss and "V3Score" in cvss[version]:
            return float(cvss[version]["V3Score"])
        if version in cvss and "V2Score" in cvss[version]:
            return float(cvss[version]["V2Score"])

    return 0.0


if __name__ == "__main__":
    # Test with sample Trivy output
    sample_output = {
        "Results": [
            {
                "Target": "package-lock.json",
                "Type": "npm",
                "Vulnerabilities": [
                    {
                        "VulnerabilityID": "CVE-2024-12345",
                        "Severity": "CRITICAL",
                        "Title": "Example vulnerability",
                        "PkgName": "example-package",
                        "InstalledVersion": "1.0.0",
                        "FixedVersion": "1.2.3",
                        "PrimaryURL": "https://nvd.nist.gov/vuln/detail/CVE-2024-12345"
                    }
                ]
            }
        ]
    }

    findings = normalize(sample_output, "test-run-123", "test-project")
    print(f"Normalized {len(findings)} findings")
    for finding in findings:
        print(f"- {finding['severity']}: {finding['title']}")