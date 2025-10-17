#!/usr/bin/env python3
"""
Checkov Output Normalizer - Convert Checkov JSON to standardized findings
"""

import json
from typing import List, Dict, Any
from datetime import datetime


def normalize(raw_json: dict, run_id: str, project_id: str) -> List[Dict[str, Any]]:
    """
    Convert Checkov raw JSON output to normalized findings format.

    Args:
        raw_json: Raw Checkov JSON output
        run_id: Unique identifier for this scan run
        project_id: Project identifier

    Returns:
        List of normalized finding dictionaries
    """
    findings = []
    timestamp = datetime.now().isoformat()

    try:
        # Checkov output structure: results.failed_checks, results.passed_checks, etc.
        results = raw_json.get("results", {})

        # Process failed checks (these are the findings we care about)
        failed_checks = results.get("failed_checks", [])

        for check in failed_checks:
            finding = {
                "ts": timestamp,
                "project_id": project_id,
                "tool": "checkov",
                "run_id": run_id,
                "artifact": _extract_artifact_path(check),
                "type": _determine_finding_type(check),
                "id": check.get("check_id", "unknown"),
                "severity": _map_severity(check.get("severity", "MEDIUM")),
                "title": check.get("check_name", "Policy Violation"),
                "location": _extract_location(check),
                "status": "open",
                "recommendation": _extract_recommendation(check),
                "evidence_sha256": "",  # Will be filled by evidence system
                "links": _extract_links(check),
                "metadata": {
                    "framework": check.get("check_type", ""),
                    "resource": check.get("resource", ""),
                    "guideline": check.get("guideline", ""),
                    "description": check.get("description", ""),
                    "short_description": check.get("short_description", ""),
                    "code_block": check.get("code_block", []),
                    "caller_file_path": check.get("caller_file_path", ""),
                    "caller_file_line_range": check.get("caller_file_line_range", []),
                    "fixed_definition": check.get("fixed_definition", "")
                }
            }
            findings.append(finding)

        # Process secrets findings if present
        secrets = results.get("secrets", [])
        for secret in secrets:
            finding = {
                "ts": timestamp,
                "project_id": project_id,
                "tool": "checkov",
                "run_id": run_id,
                "artifact": secret.get("file_path", "unknown"),
                "type": "secret",
                "id": secret.get("check_id", "secret"),
                "severity": "HIGH",  # Secrets are always high severity
                "title": secret.get("check_name", "Exposed Secret"),
                "location": f"{secret.get('file_path', '')}:{secret.get('file_line_range', [''])[0]}",
                "status": "open",
                "recommendation": "Remove or encrypt the exposed secret",
                "evidence_sha256": "",
                "links": [],
                "metadata": {
                    "secret_type": secret.get("check_id", ""),
                    "line_range": secret.get("file_line_range", [])
                }
            }
            findings.append(finding)

    except Exception as e:
        # Create error finding if normalization fails
        error_finding = {
            "ts": timestamp,
            "project_id": project_id,
            "tool": "checkov",
            "run_id": run_id,
            "artifact": "normalization_error",
            "type": "error",
            "id": "NORMALIZE_ERROR",
            "severity": "MEDIUM",
            "title": f"Checkov normalization failed: {str(e)}",
            "location": "normalizer",
            "status": "open",
            "recommendation": "Review raw Checkov output and fix normalizer",
            "evidence_sha256": "",
            "links": [],
            "metadata": {"error": str(e)}
        }
        findings.append(error_finding)

    return findings


def _extract_artifact_path(check: Dict) -> str:
    """Extract the file/resource path from check"""
    file_path = check.get("file_path", "")
    repo_file_path = check.get("repo_file_path", "")

    # Prefer repo_file_path if available, otherwise use file_path
    return repo_file_path or file_path or "unknown"


def _determine_finding_type(check: Dict) -> str:
    """Determine the type of finding based on check metadata"""
    check_type = check.get("check_type", "").lower()
    check_id = check.get("check_id", "").lower()

    if "secret" in check_type or "secret" in check_id:
        return "secret"
    elif any(keyword in check_type for keyword in ["terraform", "cloudformation", "arm", "bicep"]):
        return "iac"
    elif "dockerfile" in check_type or "docker" in check_type:
        return "container"
    elif "kubernetes" in check_type or "k8s" in check_type:
        return "k8s"
    else:
        return "policy"


def _map_severity(severity: str) -> str:
    """Map Checkov severity to standard levels"""
    severity_map = {
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW",
        "INFO": "INFO"
    }
    return severity_map.get(severity.upper(), "MEDIUM")


def _extract_location(check: Dict) -> str:
    """Extract location information from check"""
    file_path = _extract_artifact_path(check)
    line_range = check.get("file_line_range", [])

    if line_range and len(line_range) >= 2:
        return f"{file_path}:{line_range[0]}-{line_range[1]}"
    elif line_range and len(line_range) >= 1:
        return f"{file_path}:{line_range[0]}"
    else:
        return file_path


def _extract_recommendation(check: Dict) -> str:
    """Extract actionable recommendation from check"""
    # Check for fixed definition first
    fixed_def = check.get("fixed_definition")
    if fixed_def:
        return f"Apply the following fix: {fixed_def}"

    # Use guideline if available
    guideline = check.get("guideline")
    if guideline:
        return guideline

    # Fall back to description
    description = check.get("description", "")
    if description:
        return f"Fix policy violation: {description}"

    return "Review and fix the identified policy violation"


def _extract_links(check: Dict) -> List[str]:
    """Extract reference links from check"""
    links = []

    # Add guideline URL if it looks like a URL
    guideline = check.get("guideline", "")
    if guideline and (guideline.startswith("http") or "." in guideline):
        links.append(guideline)

    # Add any other URLs found in description
    description = check.get("description", "")
    if "http" in description:
        # Simple URL extraction - could be enhanced
        import re
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', description)
        links.extend(urls)

    return links[:3]  # Limit to 3 links


if __name__ == "__main__":
    # Test with sample Checkov output
    sample_output = {
        "results": {
            "failed_checks": [
                {
                    "check_id": "CKV_AWS_23",
                    "check_name": "Ensure no security groups allow ingress from 0.0.0.0:0 to port 22",
                    "check_type": "terraform",
                    "file_path": "main.tf",
                    "file_line_range": [10, 15],
                    "resource": "aws_security_group.example",
                    "severity": "HIGH",
                    "description": "Security group allows SSH access from anywhere",
                    "guideline": "https://docs.bridgecrew.io/docs/ensure-no-security-groups-allow-ingress-from-0000-to-port-22"
                }
            ]
        }
    }

    findings = normalize(sample_output, "test-run-123", "test-project")
    print(f"Normalized {len(findings)} findings")
    for finding in findings:
        print(f"- {finding['severity']}: {finding['title']}")