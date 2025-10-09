#!/usr/bin/env python3
"""
Semgrep Output Normalizer - Convert Semgrep JSON to standardized findings
"""

import json
from typing import List, Dict, Any
from datetime import datetime


def normalize(raw_json: dict, run_id: str, project_id: str) -> List[Dict[str, Any]]:
    """
    Convert Semgrep raw JSON output to normalized findings format.

    Args:
        raw_json: Raw Semgrep JSON output
        run_id: Unique identifier for this scan run
        project_id: Project identifier

    Returns:
        List of normalized finding dictionaries
    """
    findings = []
    timestamp = datetime.now().isoformat()

    try:
        # Semgrep output structure: results array
        results = raw_json.get("results", [])

        for result in results:
            finding = {
                "ts": timestamp,
                "project_id": project_id,
                "tool": "semgrep",
                "run_id": run_id,
                "artifact": result.get("path", "unknown"),
                "type": _determine_finding_type(result),
                "id": result.get("check_id", "unknown"),
                "severity": _map_severity(result.get("extra", {}).get("severity", "INFO")),
                "title": result.get("extra", {}).get("message", "Code Issue Detected"),
                "location": _extract_location(result),
                "status": "open",
                "recommendation": _extract_recommendation(result),
                "evidence_sha256": "",  # Will be filled by evidence system
                "links": _extract_links(result),
                "metadata": {
                    "rule_id": result.get("check_id", ""),
                    "category": result.get("extra", {}).get("metadata", {}).get("category", ""),
                    "subcategory": result.get("extra", {}).get("metadata", {}).get("subcategory", ""),
                    "technology": result.get("extra", {}).get("metadata", {}).get("technology", []),
                    "owasp": result.get("extra", {}).get("metadata", {}).get("owasp", []),
                    "cwe": result.get("extra", {}).get("metadata", {}).get("cwe", []),
                    "confidence": result.get("extra", {}).get("metadata", {}).get("confidence", ""),
                    "impact": result.get("extra", {}).get("metadata", {}).get("impact", ""),
                    "likelihood": result.get("extra", {}).get("metadata", {}).get("likelihood", ""),
                    "start_line": result.get("start", {}).get("line", 0),
                    "end_line": result.get("end", {}).get("line", 0),
                    "start_col": result.get("start", {}).get("col", 0),
                    "end_col": result.get("end", {}).get("col", 0),
                    "lines": result.get("extra", {}).get("lines", "")
                }
            }
            findings.append(finding)

        # Process errors if any
        errors = raw_json.get("errors", [])
        for error in errors:
            error_finding = {
                "ts": timestamp,
                "project_id": project_id,
                "tool": "semgrep",
                "run_id": run_id,
                "artifact": error.get("path", "unknown"),
                "type": "error",
                "id": "SEMGREP_ERROR",
                "severity": "LOW",
                "title": f"Semgrep scan error: {error.get('short_msg', 'Unknown error')}",
                "location": error.get("path", "unknown"),
                "status": "open",
                "recommendation": "Review file for syntax errors or unsupported constructs",
                "evidence_sha256": "",
                "links": [],
                "metadata": {
                    "error_type": error.get("type", ""),
                    "long_msg": error.get("long_msg", ""),
                    "level": error.get("level", "")
                }
            }
            findings.append(error_finding)

    except Exception as e:
        # Create error finding if normalization fails
        error_finding = {
            "ts": timestamp,
            "project_id": project_id,
            "tool": "semgrep",
            "run_id": run_id,
            "artifact": "normalization_error",
            "type": "error",
            "id": "NORMALIZE_ERROR",
            "severity": "MEDIUM",
            "title": f"Semgrep normalization failed: {str(e)}",
            "location": "normalizer",
            "status": "open",
            "recommendation": "Review raw Semgrep output and fix normalizer",
            "evidence_sha256": "",
            "links": [],
            "metadata": {"error": str(e)}
        }
        findings.append(error_finding)

    return findings


def _determine_finding_type(result: Dict) -> str:
    """Determine the type of finding based on result metadata"""
    metadata = result.get("extra", {}).get("metadata", {})
    category = metadata.get("category", "").lower()
    subcategory = metadata.get("subcategory", "").lower()

    # Check for secrets
    if "secret" in category or "secret" in subcategory:
        return "secret"

    # Check for security issues
    if "security" in category:
        return "security"

    # Check for specific vulnerability types
    if any(vuln_type in subcategory for vuln_type in [
        "injection", "xss", "csrf", "auth", "crypto", "deserialization"
    ]):
        return "vulnerability"

    # Check for performance issues
    if "performance" in category:
        return "performance"

    # Check for code quality
    if "correctness" in category or "best-practice" in category:
        return "quality"

    return "code_issue"


def _map_severity(severity: str) -> str:
    """Map Semgrep severity to standard levels"""
    severity_map = {
        "ERROR": "CRITICAL",
        "WARNING": "HIGH",
        "INFO": "MEDIUM",
        "EXPERIMENT": "LOW"
    }
    return severity_map.get(severity.upper(), "MEDIUM")


def _extract_location(result: Dict) -> str:
    """Extract location information from result"""
    path = result.get("path", "")
    start = result.get("start", {})
    end = result.get("end", {})

    start_line = start.get("line", 0)
    end_line = end.get("line", 0)

    if start_line and end_line:
        if start_line == end_line:
            return f"{path}:{start_line}"
        else:
            return f"{path}:{start_line}-{end_line}"

    return path


def _extract_recommendation(result: Dict) -> str:
    """Extract actionable recommendation from result"""
    extra = result.get("extra", {})
    message = extra.get("message", "")

    # Check for fix suggestions in metadata
    metadata = extra.get("metadata", {})
    fix_regex = metadata.get("fix_regex", {})
    if fix_regex:
        return f"Apply fix: {fix_regex.get('replacement', 'See rule documentation')}"

    # Use the message as recommendation
    if message:
        return f"Fix: {message}"

    return "Review and fix the identified code issue"


def _extract_links(result: Dict) -> List[str]:
    """Extract reference links from result"""
    links = []

    extra = result.get("extra", {})
    metadata = extra.get("metadata", {})

    # Add references from metadata
    references = metadata.get("references", [])
    for ref in references:
        if isinstance(ref, str) and ref.startswith("http"):
            links.append(ref)
        elif isinstance(ref, dict) and ref.get("url"):
            links.append(ref["url"])

    # Add source if it's a URL
    source = metadata.get("source", "")
    if source and source.startswith("http"):
        links.append(source)

    # Add OWASP links if available
    owasp_categories = metadata.get("owasp", [])
    for owasp in owasp_categories:
        if isinstance(owasp, str) and ":" in owasp:
            # Convert OWASP category to URL
            owasp_clean = owasp.replace(":", "").replace(" ", "-").lower()
            links.append(f"https://owasp.org/www-project-top-ten/2017/{owasp_clean}")

    return links[:5]  # Limit to 5 links


if __name__ == "__main__":
    # Test with sample Semgrep output
    sample_output = {
        "results": [
            {
                "check_id": "python.django.security.injection.sql.django-sql-injection",
                "path": "views.py",
                "start": {"line": 42, "col": 12},
                "end": {"line": 42, "col": 45},
                "extra": {
                    "message": "Detected SQL query that is tainted by user-controllable data",
                    "severity": "ERROR",
                    "metadata": {
                        "category": "security",
                        "subcategory": "vuln",
                        "technology": ["django"],
                        "owasp": ["A03:2021 - Injection"],
                        "cwe": ["CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')"],
                        "confidence": "HIGH",
                        "references": ["https://owasp.org/www-project-top-ten/2017/A1_2017-Injection"]
                    }
                }
            }
        ]
    }

    findings = normalize(sample_output, "test-run-123", "test-project")
    print(f"Normalized {len(findings)} findings")
    for finding in findings:
        print(f"- {finding['severity']}: {finding['title']}")