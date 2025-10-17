#!/usr/bin/env python3
"""
GitHub Actions Workflow Analyzer
Fetches and analyzes security scan results from GHA pipelines
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import centralized config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "GP-Backend" / "james-config"))
from gp_data_config import GPDataConfig

# Import Jade logger (from GP-AI/core after merge)
from core.jade_logger import JadeLogger

class GHAAnalyzer:
    """Analyzes GitHub Actions workflow security scan results"""

    def __init__(self):
        self.config = GPDataConfig()
        self.logger = JadeLogger()

    def fetch_workflow_run(self, repo: str, run_id: str) -> Dict[str, Any]:
        """Fetch workflow run details using gh CLI"""
        try:
            # Get workflow run details
            cmd = ["gh", "run", "view", run_id, "--repo", repo, "--json",
                   "databaseId,status,conclusion,url,createdAt,headBranch,headSha,event"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            run_data = json.loads(result.stdout)

            # Log the fetch action
            self.logger.log_action(
                action="fetch_gha_run",
                target=f"{repo}/{run_id}",
                metadata={"status": run_data.get("status"), "conclusion": run_data.get("conclusion")}
            )

            return run_data
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to fetch workflow run: {e.stderr}"
            self.logger.log_action(
                action="fetch_gha_run",
                target=f"{repo}/{run_id}",
                error=error_msg
            )
            raise ValueError(error_msg)

    def fetch_artifacts(self, repo: str, run_id: str) -> List[Dict[str, Any]]:
        """Fetch and download artifacts from workflow run"""
        try:
            # List artifacts using gh API
            cmd = ["gh", "api", f"repos/{repo}/actions/runs/{run_id}/artifacts"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            artifacts = data.get("artifacts", [])

            downloaded_artifacts = []

            for artifact in artifacts:
                artifact_name = artifact.get("name")

                # Only download security-related artifacts
                if any(keyword in artifact_name.lower() for keyword in
                       ["security", "scan", "sast", "secret", "container", "infrastructure", "dependency"]):

                    # Download artifact to temp directory
                    download_dir = Path("/tmp") / f"gha-{run_id}-{artifact_name}"

                    # Clean up existing directory to avoid conflicts
                    if download_dir.exists():
                        import shutil
                        shutil.rmtree(download_dir)

                    download_dir.mkdir(parents=True, exist_ok=True)

                    download_cmd = ["gh", "run", "download", run_id,
                                    "--repo", repo, "--name", artifact_name,
                                    "--dir", str(download_dir)]

                    subprocess.run(download_cmd, capture_output=True, text=True, check=True)

                    downloaded_artifacts.append({
                        "name": artifact_name,
                        "path": download_dir,
                        "files": list(download_dir.rglob("*.json"))
                    })

            self.logger.log_action(
                action="download_artifacts",
                target=f"{repo}/{run_id}",
                findings=len(downloaded_artifacts),
                metadata={"artifact_names": [a["name"] for a in downloaded_artifacts]}
            )

            return downloaded_artifacts

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to fetch artifacts: {e.stderr}"
            self.logger.log_action(
                action="download_artifacts",
                target=f"{repo}/{run_id}",
                error=error_msg
            )
            raise ValueError(error_msg)

    def parse_scanner_results(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse all scanner result files and consolidate findings"""

        consolidated = {
            "findings_by_severity": {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            },
            "findings_by_scanner": {},
            "total_findings": 0,
            "scanner_count": 0
        }

        # Track seen findings for deduplication
        seen_findings = set()

        for artifact in artifacts:
            for json_file in artifact["files"]:
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)

                    # Determine scanner type from artifact name and file content
                    scanner_type = self._identify_scanner(artifact["name"], data)

                    if scanner_type not in consolidated["findings_by_scanner"]:
                        consolidated["findings_by_scanner"][scanner_type] = []
                        consolidated["scanner_count"] += 1

                    # Parse findings based on scanner type
                    findings = self._parse_findings(scanner_type, data, str(json_file))

                    for finding in findings:
                        # Create deduplication key (scanner, title, file, line)
                        dedup_key = (
                            finding.get("scanner", "unknown"),
                            finding.get("title", ""),
                            finding.get("file", ""),
                            finding.get("line", 0)
                        )

                        # Skip if already seen
                        if dedup_key in seen_findings:
                            continue

                        seen_findings.add(dedup_key)

                        # Generate and add tags
                        finding['tags'] = self._generate_tags(finding)

                        severity = finding.get("severity", "low").lower()
                        if severity in consolidated["findings_by_severity"]:
                            consolidated["findings_by_severity"][severity].append(finding)

                        consolidated["findings_by_scanner"][scanner_type].append(finding)
                        consolidated["total_findings"] += 1

                except Exception as e:
                    print(f"Warning: Failed to parse {json_file}: {e}", file=sys.stderr)

        return consolidated

    def _identify_scanner(self, artifact_name: str, data: Dict) -> str:
        """Identify scanner type from artifact name or data structure"""
        artifact_lower = artifact_name.lower()

        # Check artifact name first
        if "bandit" in artifact_lower:
            return "bandit"
        elif "semgrep" in artifact_lower:
            return "semgrep"
        elif "trivy" in artifact_lower:
            return "trivy"
        elif "gitleaks" in artifact_lower:
            return "gitleaks"
        elif "trufflehog" in artifact_lower:
            return "trufflehog"
        elif "checkov" in artifact_lower:
            return "checkov"
        elif "tfsec" in artifact_lower:
            return "tfsec"
        elif "kubescape" in artifact_lower:
            return "kubescape"
        elif "safety" in artifact_lower:
            return "safety"
        elif "npm" in artifact_lower:
            return "npm-audit"
        elif "snyk" in artifact_lower:
            return "snyk"
        elif "grype" in artifact_lower:
            return "grype"
        elif "eslint" in artifact_lower:
            return "eslint"
        elif "gosec" in artifact_lower:
            return "gosec"
        elif "kics" in artifact_lower:
            return "kics"

        # Check data structure
        if "queries" in data and "total_counter" in data:
            return "kics"

        if "results" in data:
            if isinstance(data["results"], list) and len(data["results"]) > 0:
                first_result = data["results"][0]
                if "test_id" in first_result or "test_name" in first_result:
                    return "bandit"
                elif "check.id" in str(first_result):
                    return "semgrep"

        if "vulnerabilities" in data:
            return "trivy"

        return "unknown"

    def _parse_findings(self, scanner_type: str, data: Dict, file_path: str) -> List[Dict]:
        """Parse findings based on scanner type"""
        findings = []

        if scanner_type == "bandit":
            for result in data.get("results", []):
                findings.append({
                    "scanner": "bandit",
                    "severity": result.get("issue_severity", "LOW").lower(),
                    "title": result.get("issue_text", "Unknown issue"),
                    "file": result.get("filename", ""),
                    "line": result.get("line_number", 0),
                    "description": result.get("issue_text", ""),
                    "cwe": result.get("issue_cwe", {}).get("id", ""),
                    "confidence": result.get("issue_confidence", "").lower(),
                    "raw": result
                })

        elif scanner_type == "semgrep":
            for result in data.get("results", []):
                findings.append({
                    "scanner": "semgrep",
                    "severity": result.get("extra", {}).get("severity", "INFO").lower(),
                    "title": result.get("check_id", "Unknown"),
                    "file": result.get("path", ""),
                    "line": result.get("start", {}).get("line", 0),
                    "description": result.get("extra", {}).get("message", ""),
                    "cwe": result.get("extra", {}).get("metadata", {}).get("cwe", ""),
                    "owasp": result.get("extra", {}).get("metadata", {}).get("owasp", []),
                    "raw": result
                })

        elif scanner_type == "trivy":
            for vuln in data.get("Results", []):
                for v in vuln.get("Vulnerabilities", []):
                    findings.append({
                        "scanner": "trivy",
                        "severity": v.get("Severity", "UNKNOWN").lower(),
                        "title": v.get("VulnerabilityID", "Unknown"),
                        "file": vuln.get("Target", ""),
                        "description": v.get("Title", ""),
                        "package": v.get("PkgName", ""),
                        "installed_version": v.get("InstalledVersion", ""),
                        "fixed_version": v.get("FixedVersion", ""),
                        "cvss": v.get("CVSS", {}),
                        "raw": v
                    })

        elif scanner_type == "gitleaks":
            for finding in data.get("findings", data.get("results", [])):
                findings.append({
                    "scanner": "gitleaks",
                    "severity": "high",  # Secrets are always high severity
                    "title": finding.get("RuleID", "Secret detected"),
                    "file": finding.get("File", ""),
                    "line": finding.get("StartLine", 0),
                    "description": finding.get("Description", "Secret detected"),
                    "secret_type": finding.get("RuleID", "unknown"),
                    "raw": finding
                })

        elif scanner_type == "checkov":
            for result in data.get("results", {}).get("failed_checks", []):
                findings.append({
                    "scanner": "checkov",
                    "severity": result.get("check_result", {}).get("result", {}).get("severity", "MEDIUM").lower(),
                    "title": result.get("check_id", "Unknown"),
                    "file": result.get("file_path", ""),
                    "line": result.get("file_line_range", [0])[0],
                    "description": result.get("check_name", ""),
                    "guideline": result.get("guideline", ""),
                    "raw": result
                })

        elif scanner_type == "kics":
            for query in data.get("queries", []):
                for file_entry in query.get("files", []):
                    findings.append({
                        "scanner": "kics",
                        "severity": query.get("severity", "MEDIUM").lower(),
                        "title": query.get("query_name", "Unknown"),
                        "file": file_entry.get("file_name", ""),
                        "line": file_entry.get("line", 0),
                        "description": query.get("description", ""),
                        "category": query.get("category", ""),
                        "platform": query.get("platform", ""),
                        "raw": file_entry
                    })

        else:
            # Generic parser for unknown formats
            if "results" in data:
                for item in data["results"]:
                    findings.append({
                        "scanner": scanner_type,
                        "severity": "medium",
                        "title": str(item.get("id", item.get("name", "Unknown"))),
                        "description": str(item),
                        "raw": item
                    })

        return findings

    def _generate_tags(self, finding: Dict) -> List[str]:
        """Generate tags for a finding based on its characteristics"""
        tags = []

        # Scanner-based tags
        scanner = finding.get('scanner', '').lower()
        if scanner:
            tags.append(f"scanner:{scanner}")

        # Severity tags
        severity = finding.get('severity', '').lower()
        if severity in ['critical', 'high']:
            tags.append("priority:urgent")
        elif severity == 'medium':
            tags.append("priority:medium")
        else:
            tags.append("priority:low")

        # Category/Type tags
        category = finding.get('category', '').lower()
        platform = finding.get('platform', '').lower()
        title = finding.get('title', '').lower()
        description = finding.get('description', '').lower()

        # Security domain tags
        if any(kw in title or kw in description for kw in ['secret', 'credential', 'password', 'token', 'key']):
            tags.append("domain:secrets")
        if any(kw in title or kw in description for kw in ['privilege', 'root', 'sudo', 'escalation']):
            tags.append("domain:privilege-escalation")
        if any(kw in title or kw in description for kw in ['injection', 'xss', 'sql', 'command']):
            tags.append("domain:injection")
        if any(kw in title or kw in description for kw in ['crypto', 'encryption', 'hash', 'tls', 'ssl']):
            tags.append("domain:cryptography")
        if any(kw in title or kw in description for kw in ['cve-', 'vulnerability', 'vuln']):
            tags.append("domain:vulnerabilities")

        # File type tags
        file_path = finding.get('file', '').lower()
        if file_path:
            if 'dockerfile' in file_path or file_path.endswith('.dockerfile'):
                tags.append("file-type:dockerfile")
            elif file_path.endswith(('.yaml', '.yml')):
                tags.append("file-type:kubernetes")
            elif file_path.endswith('.py'):
                tags.append("file-type:python")
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                tags.append("file-type:javascript")
            elif file_path.endswith('.tf'):
                tags.append("file-type:terraform")

        # Platform tags
        if platform:
            if 'kubernetes' in platform:
                tags.append("platform:kubernetes")
            elif 'docker' in platform:
                tags.append("platform:docker")
            elif 'terraform' in platform:
                tags.append("platform:terraform")

        # Compliance tags (if applicable)
        if 'pci' in description or 'pci-dss' in description:
            tags.append("compliance:pci-dss")
        if 'hipaa' in description:
            tags.append("compliance:hipaa")
        if 'gdpr' in description:
            tags.append("compliance:gdpr")
        if 'cis' in description or category == 'cis':
            tags.append("compliance:cis")

        # Category tags
        if category:
            tags.append(f"category:{category.replace(' ', '-')}")

        return list(set(tags))  # Remove duplicates

    def generate_summary(self, consolidated: Dict[str, Any]) -> Dict[str, Any]:
        """Generate human-readable summary of findings"""

        summary = {
            "total_findings": consolidated["total_findings"],
            "scanners_used": consolidated["scanner_count"],
            "severity_counts": {
                "critical": len(consolidated["findings_by_severity"]["critical"]),
                "high": len(consolidated["findings_by_severity"]["high"]),
                "medium": len(consolidated["findings_by_severity"]["medium"]),
                "low": len(consolidated["findings_by_severity"]["low"])
            },
            "top_issues": [],
            "risk_score": 0
        }

        # Calculate risk score (weighted by severity)
        summary["risk_score"] = (
            summary["severity_counts"]["critical"] * 10 +
            summary["severity_counts"]["high"] * 5 +
            summary["severity_counts"]["medium"] * 2 +
            summary["severity_counts"]["low"] * 1
        )

        # Get top 10 most critical issues
        all_findings = (
            consolidated["findings_by_severity"]["critical"] +
            consolidated["findings_by_severity"]["high"] +
            consolidated["findings_by_severity"]["medium"]
        )

        summary["top_issues"] = all_findings[:10]

        return summary

    def format_for_llm(self, run_data: Dict, consolidated: Dict, summary: Dict) -> str:
        """Format findings for LLM analysis"""

        prompt = f"""Analyze these security scan results from a GitHub Actions pipeline and explain them to a junior engineer. Prioritize by risk.

**Workflow Run Details:**
- Repository: {run_data.get('url', 'Unknown')}
- Branch: {run_data.get('headBranch', 'Unknown')}
- Commit: {run_data.get('headSha', 'Unknown')}
- Status: {run_data.get('conclusion', 'Unknown')}
- Created: {run_data.get('createdAt', 'Unknown')}

**Security Scan Summary:**
- Total Findings: {summary['total_findings']}
- Scanners Used: {summary['scanners_used']}
- Risk Score: {summary['risk_score']} (higher = more critical)

**Findings by Severity:**
- 🔴 Critical: {summary['severity_counts']['critical']}
- 🟠 High: {summary['severity_counts']['high']}
- 🟡 Medium: {summary['severity_counts']['medium']}
- 🟢 Low: {summary['severity_counts']['low']}

**Top Priority Issues (by severity):**
"""

        for idx, finding in enumerate(summary["top_issues"], 1):
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(finding.get("severity", "low"), "⚪")

            prompt += f"""
{idx}. {severity_emoji} [{finding.get('scanner', 'unknown').upper()}] {finding.get('title', 'Unknown')}
   - Severity: {finding.get('severity', 'unknown').upper()}
   - File: {finding.get('file', 'N/A')}:{finding.get('line', 'N/A')}
   - Description: {finding.get('description', 'No description')}
"""

        prompt += """

**Analysis Instructions:**
1. Explain what these security findings mean in simple terms
2. Prioritize issues by actual risk to the application (not just severity label)
3. For the top 3-5 issues, explain:
   - What is the vulnerability?
   - Why is it dangerous?
   - How can it be exploited?
   - How should it be fixed?
4. Provide a risk assessment and recommended action plan
5. Keep explanations clear and actionable for a junior engineer

Please analyze these findings now:"""

        return prompt


def main():
    """CLI entry point for GHA analysis"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze GitHub Actions security scan results")
    parser.add_argument("repo", help="Repository in format 'owner/repo'")
    parser.add_argument("run_id", help="Workflow run ID")
    parser.add_argument("--save", "-s", help="Save results to file", metavar="FILE")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM analysis, just show parsed results")

    args = parser.parse_args()

    analyzer = GHAAnalyzer()

    print(f"🔍 Fetching workflow run {args.run_id} from {args.repo}...")
    run_data = analyzer.fetch_workflow_run(args.repo, args.run_id)

    print(f"📥 Downloading artifacts...")
    artifacts = analyzer.fetch_artifacts(args.repo, args.run_id)
    print(f"   Found {len(artifacts)} security-related artifacts")

    print(f"🔬 Parsing scanner results...")
    consolidated = analyzer.parse_scanner_results(artifacts)

    print(f"📊 Generating summary...")
    summary = analyzer.generate_summary(consolidated)

    # Display summary
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           SECURITY SCAN RESULTS SUMMARY                      ║
╚══════════════════════════════════════════════════════════════╝

Repository: {args.repo}
Run ID: {args.run_id}
Status: {run_data.get('conclusion', 'Unknown')}

Total Findings: {summary['total_findings']}
Risk Score: {summary['risk_score']}

Severity Breakdown:
  🔴 Critical: {summary['severity_counts']['critical']}
  🟠 High:     {summary['severity_counts']['high']}
  🟡 Medium:   {summary['severity_counts']['medium']}
  🟢 Low:      {summary['severity_counts']['low']}

Scanners Used: {consolidated['scanner_count']}
""")

    # Save results if requested
    if args.save:
        output = {
            "run_data": run_data,
            "consolidated": consolidated,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        with open(args.save, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"💾 Results saved to {args.save}")

    # Generate LLM prompt
    if not args.no_llm:
        print("\n" + "="*60)
        print("LLM ANALYSIS PROMPT")
        print("="*60 + "\n")
        llm_prompt = analyzer.format_for_llm(run_data, consolidated, summary)
        print(llm_prompt)
        print("\n" + "="*60)
        print("\n💡 Copy the above prompt and paste it to Jade for AI-powered analysis")
        print("   Or use: jade chat \"<paste prompt here>\"")


if __name__ == "__main__":
    main()