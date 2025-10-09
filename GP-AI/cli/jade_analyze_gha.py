#!/usr/bin/env python3
"""
Jade Analyze GHA - Complete GitHub Actions Security Analysis
Detects discrepancies between security gates and actual scanner findings
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import subprocess
import base64

# Import GHA analyzer
from gha_analyzer import GHAAnalyzer

# Import Jade logger
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "GP-PLATFORM"))
from core.jade_logger import JadeLogger


class JadeGHAAnalyzer:
    """Complete GHA security analysis with discrepancy detection"""

    def __init__(self):
        self.analyzer = GHAAnalyzer()
        self.logger = JadeLogger()
        self.gp_root = Path(__file__).resolve().parent.parent.parent
        self.source_cache = {}  # Cache fetched source files

    def analyze(self, repo: str, run_id: str) -> Dict[str, Any]:
        """Complete analysis workflow"""

        print(f"🔍 Jade GHA Analyzer")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Repository: {repo}")
        print(f"Run ID: {run_id}")
        print()

        # Step 1: Fetch run data
        print("📡 Fetching workflow run details...")
        run_data = self.analyzer.fetch_workflow_run(repo, run_id)
        print(f"   Status: {run_data.get('conclusion', 'Unknown')}")
        print(f"   Branch: {run_data.get('headBranch', 'Unknown')}")
        print(f"   Commit: {run_data.get('headSha', 'Unknown')[:8]}...")
        print()

        # Step 2: Download artifacts
        print("📥 Downloading security scan artifacts...")
        artifacts = self.analyzer.fetch_artifacts(repo, run_id)
        total_size = sum(sum(f.stat().st_size for f in a['files']) for a in artifacts)
        print(f"   ✅ Downloaded {len(artifacts)} artifact(s) ({total_size // 1024} KB)")
        print()

        # Step 3: Parse scanner results
        print("📊 Parsing scanner outputs...")
        consolidated = self.analyzer.parse_scanner_results(artifacts)

        for scanner, findings in consolidated['findings_by_scanner'].items():
            print(f"   ├─ {scanner.upper()}: {len(findings)} finding(s)")
        print()

        # Step 4: Generate summary
        summary = self.analyzer.generate_summary(consolidated)

        # Step 5: Check for security gate discrepancy
        gate_summary = self._find_security_gate_summary(artifacts)
        discrepancy = self._detect_discrepancy(summary, gate_summary)

        if discrepancy:
            print("⚠️  DISCREPANCY DETECTED:")
            print(f"   Security Gate: {gate_summary['total']} findings")
            print(f"   Actual Findings: {summary['total_findings']} findings")
            print(f"   → Your security gate missed {discrepancy['missed_findings']} issue(s)!")
            print()

        # Step 6: Display findings
        self._display_findings(summary)

        # Step 7: Save results
        saved_paths = self._save_results(repo, run_id, run_data, consolidated, summary, discrepancy)

        # Step 8: Generate fix guide if HIGH/CRITICAL findings
        fix_guide_content = None
        if summary['severity_counts']['critical'] > 0 or summary['severity_counts']['high'] > 0:
            fix_guide_path = self._generate_fix_guide(repo, run_id, run_data, summary, consolidated)
            saved_paths['fix_guide'] = str(fix_guide_path)
            print(f"📝 Fix guide: {fix_guide_path}")
            # Read fix guide content for client output
            with open(fix_guide_path, 'r') as f:
                fix_guide_content = f.read()

        # Step 9: Save client-facing output to repo
        client_paths = self._save_client_facing_output(
            repo=repo,
            run_id=run_id,
            run_data=run_data,
            consolidated=consolidated,
            summary=summary,
            discrepancy=discrepancy,
            fix_guide_content=fix_guide_content
        )
        if client_paths:
            saved_paths.update(client_paths)

        print()
        print("="*62)
        print(f"✅ Analysis complete!")
        print(f"📁 Results saved to: GP-DATA/active/")
        print(f"📋 Evidence logged to: {self.logger.log_path}")
        print("="*62)

        return {
            "run_data": run_data,
            "summary": summary,
            "consolidated": consolidated,
            "discrepancy": discrepancy,
            "saved_paths": saved_paths
        }

    def _find_security_gate_summary(self, artifacts: List[Dict]) -> Dict[str, Any]:
        """Find and parse security gate summary if it exists"""
        for artifact in artifacts:
            for file_path in artifact['files']:
                if 'security-summary.json' in str(file_path) or 'gate' in str(file_path).lower():
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            if 'findings' in data or 'status' in data:
                                findings = data.get('findings', {})
                                return {
                                    'total': findings.get('total', 0),
                                    'critical': findings.get('critical', 0),
                                    'high': findings.get('high', 0),
                                    'medium': findings.get('medium', 0),
                                    'low': findings.get('low', 0),
                                    'status': data.get('status', 'UNKNOWN')
                                }
                    except:
                        pass

        return {'total': None, 'status': 'NOT_FOUND'}

    def _detect_discrepancy(self, actual: Dict, gate: Dict) -> Dict[str, Any]:
        """Detect discrepancy between actual findings and security gate"""
        if gate['total'] is None:
            return None

        actual_total = actual['total_findings']
        gate_total = gate['total']

        if actual_total > gate_total:
            return {
                'detected': True,
                'missed_findings': actual_total - gate_total,
                'actual_high': actual['severity_counts']['high'],
                'gate_high': gate.get('high', 0),
                'actual_critical': actual['severity_counts']['critical'],
                'gate_critical': gate.get('critical', 0)
            }

        return None

    def _fetch_source_context(self, repo: str, commit: str, file_path: str, line_number: int, context_lines: int = 5) -> Optional[Dict[str, Any]]:
        """Fetch source code context from GitHub API"""
        cache_key = f"{repo}:{commit}:{file_path}"

        # Check cache first
        if cache_key in self.source_cache:
            content = self.source_cache[cache_key]
        else:
            try:
                # Fetch file content using gh API
                cmd = ["gh", "api", f"repos/{repo}/contents/{file_path}?ref={commit}"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                data = json.loads(result.stdout)

                # Decode base64 content
                content = base64.b64decode(data['content']).decode('utf-8')
                self.source_cache[cache_key] = content
            except Exception as e:
                print(f"Warning: Could not fetch {file_path}: {e}", file=sys.stderr)
                return None

        # Extract lines around the issue
        lines = content.split('\n')
        start_line = max(0, line_number - context_lines - 1)
        end_line = min(len(lines), line_number + context_lines)

        context_lines_data = []
        for i in range(start_line, end_line):
            context_lines_data.append({
                'line_num': i + 1,
                'content': lines[i],
                'is_issue_line': (i + 1 == line_number)
            })

        return {
            'file_path': file_path,
            'line_number': line_number,
            'context': context_lines_data,
            'full_file_lines': len(lines)
        }

    def _display_findings(self, summary: Dict):
        """Display findings summary"""
        risk_level = "🔴 CRITICAL" if summary['risk_score'] > 100 else \
                     "🟠 HIGH" if summary['risk_score'] > 50 else \
                     "🟡 MEDIUM" if summary['risk_score'] > 20 else \
                     "🟢 LOW"

        print(f"Risk Assessment: {risk_level} (Score: {summary['risk_score']})")
        print()
        print(f"Severity Breakdown:")
        print(f"  🔴 Critical: {summary['severity_counts']['critical']}")
        print(f"  🟠 High:     {summary['severity_counts']['high']}")
        print(f"  🟡 Medium:   {summary['severity_counts']['medium']}")
        print(f"  🟢 Low:      {summary['severity_counts']['low']}")
        print()

        if summary['top_issues']:
            print(f"Top Priority Issues:")
            for idx, finding in enumerate(summary['top_issues'][:5], 1):
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(finding.get('severity', 'low'), "⚪")

                print(f"{idx}. {severity_emoji} [{finding.get('scanner', 'unknown').upper()}] {finding.get('title', 'Unknown')}")
                print(f"   └─ {finding.get('file', 'N/A')}")
            print()

    def _save_results(self, repo: str, run_id: str, run_data: Dict,
                     consolidated: Dict, summary: Dict, discrepancy: Dict) -> Dict[str, str]:
        """Save all results to GP-DATA structure"""

        repo_name = repo.split('/')[-1]
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Create directories
        scan_dir = self.gp_root / "GP-DATA" / "active" / "scans" / repo_name / f"run-{run_id}"
        report_dir = self.gp_root / "GP-DATA" / "active" / "reports" / repo_name

        scan_dir.mkdir(parents=True, exist_ok=True)
        report_dir.mkdir(parents=True, exist_ok=True)

        saved_paths = {}

        # Save consolidated results
        consolidated_path = scan_dir / "consolidated-results.json"
        with open(consolidated_path, 'w') as f:
            json.dump({
                "run_data": run_data,
                "consolidated": consolidated,
                "summary": summary,
                "discrepancy": discrepancy,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, default=str)
        saved_paths['consolidated'] = str(consolidated_path)

        # Save analysis report (markdown)
        report_path = report_dir / f"analysis-{run_id}-{timestamp}.md"
        with open(report_path, 'w') as f:
            f.write(self._generate_report_markdown(repo, run_id, run_data, summary, consolidated, discrepancy))
        saved_paths['report'] = str(report_path)

        # Log to evidence
        self.logger.log_action(
            action="analyze_gha",
            target=f"{repo}/{run_id}",
            findings=summary['total_findings'],
            metadata={
                "risk_score": summary['risk_score'],
                "severity_counts": summary['severity_counts'],
                "scanners": list(consolidated['findings_by_scanner'].keys()),
                "discrepancy_detected": discrepancy is not None,
                "saved_to": str(scan_dir)
            }
        )

        print(f"💾 Scan results: {scan_dir}")
        print(f"📄 Analysis report: {report_path}")

        return saved_paths

    def _generate_report_markdown(self, repo: str, run_id: str, run_data: Dict,
                                  summary: Dict, consolidated: Dict, discrepancy: Dict) -> str:
        """Generate markdown analysis report"""

        md = f"""# Security Analysis Report: {repo}

**Run ID:** {run_id}
**Analyzed:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Branch:** {run_data.get('headBranch', 'Unknown')}
**Commit:** {run_data.get('headSha', 'Unknown')}
**Status:** {run_data.get('conclusion', 'Unknown')}

## Executive Summary

**Total Findings:** {summary['total_findings']}
**Risk Score:** {summary['risk_score']}

**Severity Distribution:**
- 🔴 Critical: {summary['severity_counts']['critical']}
- 🟠 High: {summary['severity_counts']['high']}
- 🟡 Medium: {summary['severity_counts']['medium']}
- 🟢 Low: {summary['severity_counts']['low']}

**Scanners Used:** {', '.join(consolidated['findings_by_scanner'].keys())}

"""

        if discrepancy:
            md += f"""## ⚠️ Security Gate Discrepancy Detected

**ALERT:** The security gate reported different findings than actual scanner output.

- **Security Gate:** {discrepancy.get('missed_findings', 0)} findings missed
- **Gate Status:** May have incorrectly passed
- **Action Required:** Review security gate configuration

"""

        md += """## Top Priority Issues

"""
        for idx, finding in enumerate(summary['top_issues'][:10], 1):
            md += f"""### {idx}. {finding.get('title', 'Unknown')}

- **Severity:** {finding.get('severity', 'unknown').upper()}
- **Scanner:** {finding.get('scanner', 'unknown')}
- **File:** {finding.get('file', 'N/A')}:{finding.get('line', 'N/A')}
- **Description:** {finding.get('description', 'No description')}

"""

        md += f"""## Recommendations

"""
        if summary['severity_counts']['critical'] > 0:
            md += f"1. 🚨 **URGENT:** Fix {summary['severity_counts']['critical']} CRITICAL finding(s) immediately\n"
        if summary['severity_counts']['high'] > 0:
            md += f"2. ⚠️ **HIGH Priority:** Address {summary['severity_counts']['high']} HIGH severity finding(s) within 1 week\n"
        if summary['severity_counts']['medium'] > 0:
            md += f"3. 📋 **MEDIUM Priority:** Plan remediation for {summary['severity_counts']['medium']} MEDIUM findings\n"

        return md

    def _generate_fix_guide(self, repo: str, run_id: str, run_data: Dict, summary: Dict, consolidated: Dict) -> Path:
        """Generate fix guide for HIGH/CRITICAL findings with source context"""

        repo_name = repo.split('/')[-1]
        commit_sha = run_data.get('headSha', 'main')

        fix_dir = self.gp_root / "GP-DATA" / "active" / "fixes" / repo_name
        fix_dir.mkdir(parents=True, exist_ok=True)

        fix_path = fix_dir / f"fix-guide-{datetime.now().strftime('%Y%m%d')}.md"

        high_findings = consolidated['findings_by_severity']['high']
        critical_findings = consolidated['findings_by_severity']['critical']

        md = f"""# Security Fix Guide: {repo_name}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Run ID:** {run_id}
**Priority:** HIGH/CRITICAL findings only

## Summary

- 🔴 **CRITICAL:** {len(critical_findings)} finding(s)
- 🟠 **HIGH:** {len(high_findings)} finding(s)

---

"""

        all_priority = critical_findings + high_findings

        for idx, finding in enumerate(all_priority, 1):
            severity = finding.get('severity', 'unknown').upper()
            md += f"""## Issue {idx}: {finding.get('title', 'Unknown')}

### 🔴 Severity: {severity}

**Category:** {finding.get('category', finding.get('scanner', 'General'))}
**File:** `{finding.get('file', 'N/A')}`:{finding.get('line', 'N/A')}

"""
            # Add tags if present
            tags = finding.get('tags', [])
            if tags:
                md += f"**Tags:** {', '.join(f'`{tag}`' for tag in tags)}\n\n"

            md += f"""### Description

{finding.get('description', 'No description available')}

"""
            # Fetch and display source context
            file_path = finding.get('file', '')
            line_num = finding.get('line', 0)
            if file_path and line_num:
                context = self._fetch_source_context(repo, commit_sha, file_path, line_num, context_lines=3)
                if context:
                    md += """### Current Code

"""
                    # Determine file type for syntax highlighting
                    file_ext = Path(file_path).suffix
                    lang_map = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                               '.yaml': 'yaml', '.yml': 'yaml', '.json': 'json',
                               '.sh': 'bash', '.Dockerfile': 'dockerfile', '': 'dockerfile'}
                    lang = lang_map.get(file_ext, lang_map.get(Path(file_path).name, 'text'))

                    md += f"```{lang}\n"
                    for ctx_line in context['context']:
                        prefix = ">>> " if ctx_line['is_issue_line'] else "    "
                        md += f"{prefix}{ctx_line['line_num']:3}: {ctx_line['content']}\n"
                    md += "```\n\n"

            md += """### Risk

"""
            if 'user' in finding.get('title', '').lower():
                md += """- **Privilege Escalation:** Container running as root increases attack surface
- **Impact:** Compromised container = root access to host
- **Exploitability:** High if container is breached
"""
            elif 'privilege' in finding.get('title', '').lower():
                md += """- **Privilege Escalation:** Processes can gain elevated privileges
- **Impact:** Attackers can escalate from limited user to root
- **Exploitability:** High in multi-tenant environments
"""
            else:
                md += f"- High severity security issue requiring immediate attention\n"

            md += f"""
### Recommended Fix

"""
            if 'dockerfile' in finding.get('file', '').lower():
                md += """```dockerfile
# Add before CMD/ENTRYPOINT
RUN addgroup -g 1001 appuser && adduser -u 1001 -G appuser -s /bin/sh -D appuser
RUN chown -R appuser:appuser /app
USER appuser
```
"""
            elif 'deployment' in finding.get('file', '').lower() or 'yaml' in finding.get('file', '').lower():
                md += """```yaml
securityContext:
  allowPrivilegeEscalation: false
  runAsNonRoot: true
  runAsUser: 1001
  capabilities:
    drop:
      - ALL
  readOnlyRootFilesystem: true
```
"""
            else:
                md += "Review scanner documentation for specific remediation steps.\n"

            md += f"""
### Verification

```bash
# After applying fix, verify:
# 1. Re-run security scan
# 2. Check finding is resolved
# 3. Test application functionality
```

---

"""

        md += f"""## Next Steps

1. **Apply fixes** following the guidance above
2. **Test changes** in dev/staging environment
3. **Re-run security scan** to verify resolution
4. **Commit changes** with descriptive message
5. **Monitor** for any regressions

## Commands

```bash
# Re-scan after fixes
jade analyze-gha {repo} <new-run-id>

# View evidence log
grep "analyze_gha" ~/.jade/evidence.jsonl | jq
```
"""

        with open(fix_path, 'w') as f:
            f.write(md)

        return fix_path

    def _find_local_repo(self, repo_name: str) -> Optional[Path]:
        """Find local clone of the repository"""
        # Extract just the repo name from owner/repo format
        if '/' in repo_name:
            repo_name = repo_name.split('/')[-1]

        # Common locations to search
        search_paths = [
            self.gp_root / "GP-PROJECTS" / repo_name,
            Path.home() / "projects" / repo_name,
            Path.cwd() / repo_name,
        ]

        for path in search_paths:
            if path.exists() and (path / ".git").exists():
                return path

        return None

    def _save_client_facing_output(self, repo: str, run_id: str, run_data: Dict,
                                   consolidated: Dict, summary: Dict, discrepancy: Dict,
                                   fix_guide_content: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Save curated security results to client's repository"""

        repo_name = repo.split('/')[-1]
        repo_path = self._find_local_repo(repo_name)

        if not repo_path:
            print(f"\n⚠️  Could not find local repo for {repo_name}")
            print(f"   Client-facing results NOT saved to repo")
            return None

        client_dir = repo_path / "GP-COPILOT"

        try:
            # Create directory structure
            (client_dir / "scans/latest").mkdir(parents=True, exist_ok=True)
            (client_dir / "reports").mkdir(parents=True, exist_ok=True)
            (client_dir / "fixes").mkdir(parents=True, exist_ok=True)

            saved_files = {}

            # 1. Save consolidated findings (JSON)
            consolidated_path = client_dir / "scans/latest/consolidated-results.json"
            with open(consolidated_path, 'w') as f:
                json.dump({
                    "scan_id": run_id,
                    "timestamp": datetime.now().isoformat(),
                    "repository": repo,
                    "commit": run_data.get('headSha', 'unknown'),
                    "branch": run_data.get('headBranch', 'unknown'),
                    "summary": summary['severity_counts'],
                    "risk_score": summary['risk_score'],
                    "findings_by_severity": {
                        "critical": consolidated['findings_by_severity']['critical'],
                        "high": consolidated['findings_by_severity']['high'],
                        "medium": consolidated['findings_by_severity']['medium'],
                        "low": consolidated['findings_by_severity']['low']
                    },
                    "scanners_used": list(consolidated['findings_by_scanner'].keys()),
                    "discrepancy": discrepancy
                }, f, indent=2, default=str)
            saved_files['client_consolidated'] = str(consolidated_path)

            # 2. Generate and save executive summary
            exec_summary = self._generate_executive_summary(summary, consolidated, discrepancy)
            exec_path = client_dir / "reports/executive-summary.md"
            with open(exec_path, 'w') as f:
                f.write(exec_summary)
            saved_files['client_exec_summary'] = str(exec_path)

            # 3. Generate and save analysis report
            analysis_report = self._generate_report_markdown(repo, run_id, run_data, summary, consolidated, discrepancy)
            analysis_path = client_dir / "reports/latest-analysis.md"
            with open(analysis_path, 'w') as f:
                f.write(analysis_report)
            saved_files['client_analysis'] = str(analysis_path)

            # 4. Save fix guide if provided
            if fix_guide_content:
                fix_path = client_dir / "fixes/active-fixes.md"
                with open(fix_path, 'w') as f:
                    f.write(fix_guide_content)
                saved_files['client_fixes'] = str(fix_path)
            else:
                # Remove old fixes if all resolved
                fix_path = client_dir / "fixes/active-fixes.md"
                if fix_path.exists():
                    fix_path.unlink()

            # 5. Generate client dashboard (README.md)
            dashboard = self._generate_client_dashboard(summary, consolidated, run_id, repo, run_data)
            dashboard_path = client_dir / "README.md"
            with open(dashboard_path, 'w') as f:
                f.write(dashboard)
            saved_files['client_dashboard'] = str(dashboard_path)

            # 6. Create .gitignore
            gitignore_path = client_dir / ".gitignore"
            with open(gitignore_path, 'w') as f:
                f.write("""# GP-Copilot - Exclude sensitive scanner data
scans/latest/raw/
*.log
*.tmp
""")

            print(f"\n📦 Client-facing output saved to: {client_dir}")
            print(f"   └─ Dashboard: {dashboard_path.relative_to(repo_path)}")
            print(f"   └─ Executive Summary: {exec_path.relative_to(repo_path)}")
            print(f"   └─ Analysis Report: {analysis_path.relative_to(repo_path)}")
            if fix_guide_content:
                print(f"   └─ Fix Guide: {fix_path.relative_to(repo_path)}")

            return saved_files

        except Exception as e:
            print(f"\n⚠️  Error saving client-facing output: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_executive_summary(self, summary: Dict, consolidated: Dict, discrepancy: Dict) -> str:
        """Generate executive summary for non-technical stakeholders"""
        severity_counts = summary['severity_counts']
        risk_score = summary['risk_score']

        # Risk level assessment
        if risk_score >= 80:
            risk_level = "🔴 CRITICAL"
            risk_desc = "Immediate action required"
        elif risk_score >= 50:
            risk_level = "🟠 HIGH"
            risk_desc = "Should be addressed soon"
        elif risk_score >= 30:
            risk_level = "🟡 MEDIUM"
            risk_desc = "Plan for resolution"
        else:
            risk_level = "🟢 LOW"
            risk_desc = "Minimal risk"

        md = f"""# Executive Security Summary

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Risk Level:** {risk_level}
**Risk Score:** {risk_score}/100

## Quick Overview

{risk_desc}

### Findings Breakdown

- 🔴 **Critical:** {severity_counts['critical']} issue(s)
- 🟠 **High:** {severity_counts['high']} issue(s)
- 🟡 **Medium:** {severity_counts['medium']} issue(s)
- 🟢 **Low:** {severity_counts['low']} issue(s)

**Total:** {summary['total_findings']} security issues detected

"""

        # Discrepancy alert
        if discrepancy and discrepancy.get('detected'):
            md += f"""## ⚠️ Security Gate Discrepancy

**ALERT:** The security gate may have incorrectly reported the scan status.

- **Security Gate Reported:** {discrepancy.get('missed_findings', 0)} fewer findings
- **Actual Findings:** {summary['total_findings']} issues detected
- **Recommendation:** Review security gate configuration

"""

        # Priority actions
        md += "## Priority Actions\n\n"

        priority_findings = (
            consolidated['findings_by_severity']['critical'] +
            consolidated['findings_by_severity']['high']
        )

        if priority_findings:
            md += "### Immediate Attention Required\n\n"
            for i, finding in enumerate(priority_findings[:5], 1):
                md += f"{i}. **{finding.get('title', 'Unknown')}** ({finding.get('file', 'N/A')})\n"
                md += f"   - Severity: {finding.get('severity', 'unknown').upper()}\n"
                desc = finding.get('description', 'No description')[:100]
                md += f"   - Risk: {desc}...\n\n"
        else:
            md += "✅ No critical or high severity issues detected.\n\n"

        # Next steps
        md += "\n## Next Steps\n\n"
        if priority_findings:
            md += "1. Review detailed findings in `reports/latest-analysis.md`\n"
            md += "2. Apply fixes from `fixes/active-fixes.md`\n"
            md += "3. Re-scan after fixes to verify resolution\n"
            md += "4. Monitor security dashboard for ongoing issues\n"
        else:
            md += "1. Review medium/low findings for continuous improvement\n"
            md += "2. Maintain current security posture\n"
            md += "3. Schedule next security review\n"
            md += "4. Consider implementing additional security controls\n"

        md += "\n---\n\n*Generated by GP-Copilot Security Analysis*\n"

        return md

    def _generate_client_dashboard(self, summary: Dict, consolidated: Dict, run_id: str, repo: str, run_data: Dict) -> str:
        """Generate README.md dashboard with live security status"""
        severity_counts = summary['severity_counts']
        risk_score = summary['risk_score']
        scanners = ", ".join(consolidated['findings_by_scanner'].keys())

        # Status badge
        if severity_counts['critical'] > 0 or severity_counts['high'] > 0:
            status_badge = "![Security](https://img.shields.io/badge/security-needs%20attention-red)"
        elif severity_counts['medium'] > 0:
            status_badge = "![Security](https://img.shields.io/badge/security-good-yellow)"
        else:
            status_badge = "![Security](https://img.shields.io/badge/security-excellent-green)"

        today = datetime.now().strftime("%Y--%m--%d")
        risk_color = "red" if risk_score >= 50 else "yellow" if risk_score >= 30 else "green"

        dashboard = f"""# Security Dashboard

{status_badge}
![Last Scan](https://img.shields.io/badge/last%20scan-{today}-blue)
![Risk Score](https://img.shields.io/badge/risk%20score-{risk_score}-{risk_color})

## Current Security Posture

| Severity | Count | Status |
|----------|-------|--------|
| 🔴 Critical | {severity_counts['critical']} | {"⚠️ Action Required" if severity_counts['critical'] > 0 else "✅ Clear"} |
| 🟠 High | {severity_counts['high']} | {"⚠️ Action Required" if severity_counts['high'] > 0 else "✅ Clear"} |
| 🟡 Medium | {severity_counts['medium']} | {"📋 Review" if severity_counts['medium'] > 0 else "✅ Clear"} |
| 🟢 Low | {severity_counts['low']} | {"📋 Review" if severity_counts['low'] > 0 else "✅ Clear"} |

**Total Findings:** {summary['total_findings']}
**Risk Score:** {risk_score}/100
**Scanners Used:** {scanners}
**Last Scan:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Scan ID:** {run_id}

## Quick Links

- 📊 [Executive Summary](reports/executive-summary.md) - For leadership
- 📋 [Detailed Analysis](reports/latest-analysis.md) - Full technical report
{"- 🔧 [Fix Recommendations](fixes/active-fixes.md) - Step-by-step fixes" if severity_counts['critical'] > 0 or severity_counts['high'] > 0 else ""}
- 📦 [Raw Data](scans/latest/consolidated-results.json) - JSON export

## What is GP-Copilot?

GP-Copilot is an automated security analysis tool that:
- ✅ Analyzes your code for security vulnerabilities
- ✅ Parses multiple security scanners (KICS, Trivy, Checkov, etc.)
- ✅ Provides actionable fix recommendations
- ✅ Tracks security posture over time

## How to Use

### View Latest Results
```bash
# See findings summary
cat GP-COPILOT/reports/executive-summary.md

# See detailed analysis
cat GP-COPILOT/reports/latest-analysis.md
```

### Apply Fixes
```bash
# If HIGH/CRITICAL findings exist:
cat GP-COPILOT/fixes/active-fixes.md
# Follow the step-by-step instructions
```

### Re-scan After Fixes
```bash
# Commit your fixes, push, and wait for CI/CD to re-run
git add .
git commit -m "Security fixes applied"
git push

# GP-Copilot will automatically update this dashboard
```

---

*This dashboard is automatically updated by GP-Copilot after each security scan.*
"""

        return dashboard


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Jade Analyze GHA - Complete GitHub Actions security analysis with discrepancy detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a workflow run
  jade analyze-gha owner/repo 1234567890

  # Analyze and save to custom location
  jade analyze-gha owner/repo 1234567890
        """
    )

    parser.add_argument("repo", help="Repository in format 'owner/repo'")
    parser.add_argument("run_id", help="GitHub Actions workflow run ID")

    args = parser.parse_args()

    try:
        analyzer = JadeGHAAnalyzer()
        result = analyzer.analyze(args.repo, args.run_id)

        # Exit with error code if critical/high findings
        severity_counts = result['summary']['severity_counts']
        if severity_counts['critical'] > 0 or severity_counts['high'] > 0:
            sys.exit(1)

    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()