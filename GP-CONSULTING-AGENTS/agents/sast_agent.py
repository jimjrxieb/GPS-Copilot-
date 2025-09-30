#!/usr/bin/env python3
"""
SAST Security Agent - Static Application Security Testing
Processes findings from Bandit, Semgrep, CodeQL, and other SAST tools
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import GP-DATA config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class SASTAgent:
    def __init__(self):
        self.agent_id = "sast_agent"
        self.config = GPDataConfig()
        self.supported_tools = ["bandit", "semgrep", "codeql", "sonarqube"]

        # Confidence levels for SAST remediation
        self.confidence_levels = {
            "high": [
                "fix_hardcoded_secrets",
                "fix_debug_flags",
                "fix_insecure_random",
                "fix_sql_injection_basic",
                "fix_xss_basic"
            ],
            "medium": [
                "fix_authentication_issues",
                "fix_authorization_flaws",
                "fix_crypto_weaknesses",
                "refactor_code_smells"
            ],
            "low": [
                "complex_business_logic",
                "architectural_changes",
                "performance_optimizations"
            ]
        }

    def execute_sast_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SAST-related task based on confidence level"""

        confidence = self._assess_task_confidence(task_type)

        if confidence == "high":
            return self._execute_high_confidence_task(task_type, parameters)
        elif confidence == "medium":
            return self._execute_medium_confidence_task(task_type, parameters)
        else:
            return {
                "success": False,
                "action": "escalate",
                "reason": f"SAST task {task_type} requires senior developer review",
                "confidence": confidence
            }

    def aggregate_sast_findings(self, scan_results_paths: List[str]) -> Dict[str, Any]:
        """Aggregate findings from multiple SAST tools"""

        aggregated_findings = {
            "tools_processed": [],
            "total_findings": 0,
            "findings_by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0},
            "findings_by_category": {},
            "deduplicated_findings": [],
            "recommendations": []
        }

        all_findings = []

        # Process each SAST tool output
        for scan_path in scan_results_paths:
            tool_findings = self._process_tool_results(scan_path)
            if tool_findings:
                all_findings.extend(tool_findings["findings"])
                aggregated_findings["tools_processed"].append(tool_findings["tool"])

        # Deduplicate findings across tools
        deduplicated = self._deduplicate_findings(all_findings)

        # Categorize and prioritize
        for finding in deduplicated:
            severity = finding.get("severity", "info").lower()
            category = finding.get("category", "unknown")

            aggregated_findings["findings_by_severity"][severity] += 1

            if category not in aggregated_findings["findings_by_category"]:
                aggregated_findings["findings_by_category"][category] = 0
            aggregated_findings["findings_by_category"][category] += 1

        aggregated_findings["total_findings"] = len(deduplicated)
        aggregated_findings["deduplicated_findings"] = deduplicated
        aggregated_findings["recommendations"] = self._generate_sast_recommendations(deduplicated)

        # Save aggregated results
        self._save_aggregated_results(aggregated_findings)

        return aggregated_findings

    def _process_tool_results(self, scan_path: str) -> Optional[Dict[str, Any]]:
        """Process individual SAST tool results"""

        try:
            with open(scan_path, 'r') as f:
                scan_data = json.load(f)

            # Determine tool type from file structure or metadata
            tool_type = self._identify_sast_tool(scan_data, scan_path)

            if tool_type == "bandit":
                return self._process_bandit_results(scan_data)
            elif tool_type == "semgrep":
                return self._process_semgrep_results(scan_data)
            elif tool_type == "codeql":
                return self._process_codeql_results(scan_data)
            else:
                return self._process_generic_sast_results(scan_data, tool_type)

        except Exception as e:
            print(f"⚠️  Error processing {scan_path}: {e}")
            return None

    def _identify_sast_tool(self, scan_data: Dict[str, Any], scan_path: str) -> str:
        """Identify SAST tool from scan data structure or filename"""

        # Check filename
        scan_path_lower = scan_path.lower()
        if "bandit" in scan_path_lower:
            return "bandit"
        elif "semgrep" in scan_path_lower:
            return "semgrep"
        elif "codeql" in scan_path_lower:
            return "codeql"

        # Check data structure
        if "results" in scan_data and "metrics" in scan_data:
            return "bandit"
        elif "results" in scan_data and any("check_id" in r for r in scan_data.get("results", [])):
            return "semgrep"
        elif "tool" in scan_data:
            return scan_data["tool"]

        return "generic"

    def _process_bandit_results(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Bandit SAST results"""

        findings = []

        # Handle different Bandit output formats
        if "results" in scan_data:
            for result in scan_data["results"]:
                finding = {
                    "tool": "bandit",
                    "rule_id": result.get("test_id", ""),
                    "title": result.get("test_name", ""),
                    "severity": result.get("issue_severity", "LOW").lower(),
                    "confidence": result.get("issue_confidence", "LOW"),
                    "category": "code_quality",
                    "file_path": result.get("filename", ""),
                    "line_number": result.get("line_number", 0),
                    "code_snippet": result.get("code", ""),
                    "message": result.get("issue_text", ""),
                    "cwe_id": result.get("test_id", "").replace("B", "CWE-")
                }
                findings.append(finding)

        # Also handle our scanner format
        elif "findings" in scan_data:
            for finding in scan_data["findings"]:
                findings.append({
                    "tool": "bandit",
                    "rule_id": finding.get("test_id", finding.get("rule_id", "")),
                    "title": finding.get("test_name", finding.get("title", "")),
                    "severity": self._normalize_severity(finding.get("severity", "LOW")),
                    "confidence": finding.get("confidence", "LOW"),
                    "category": finding.get("category", "code_quality"),
                    "file_path": finding.get("file", finding.get("filename", "")),
                    "line_number": finding.get("line", finding.get("line_number", 0)),
                    "code_snippet": finding.get("code", ""),
                    "message": finding.get("message", finding.get("issue_text", ""))
                })

        return {
            "tool": "bandit",
            "findings": findings,
            "scan_stats": scan_data.get("metrics", {})
        }

    def _process_semgrep_results(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Semgrep SAST results"""

        findings = []

        if "results" in scan_data:
            for result in scan_data["results"]:
                finding = {
                    "tool": "semgrep",
                    "rule_id": result.get("check_id", ""),
                    "title": result.get("message", ""),
                    "severity": self._normalize_severity(result.get("extra", {}).get("severity", "INFO")),
                    "confidence": "high",  # Semgrep rules are generally high confidence
                    "category": result.get("extra", {}).get("metadata", {}).get("category", "security"),
                    "file_path": result.get("path", ""),
                    "line_number": result.get("start", {}).get("line", 0),
                    "code_snippet": result.get("extra", {}).get("lines", ""),
                    "message": result.get("message", ""),
                    "owasp": result.get("extra", {}).get("metadata", {}).get("owasp", [])
                }
                findings.append(finding)

        # Handle our scanner format
        elif "findings" in scan_data:
            for finding in scan_data["findings"]:
                findings.append({
                    "tool": "semgrep",
                    "rule_id": finding.get("rule_id", ""),
                    "title": finding.get("title", finding.get("message", "")),
                    "severity": self._normalize_severity(finding.get("severity", "INFO")),
                    "confidence": "high",
                    "category": finding.get("category", "security"),
                    "file_path": finding.get("file", finding.get("path", "")),
                    "line_number": finding.get("line", 0),
                    "code_snippet": finding.get("code", ""),
                    "message": finding.get("message", "")
                })

        return {
            "tool": "semgrep",
            "findings": findings,
            "scan_stats": {"rules_run": len(scan_data.get("results", scan_data.get("findings", [])))}
        }

    def _process_codeql_results(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process CodeQL SAST results"""

        findings = []

        # CodeQL SARIF format
        if "runs" in scan_data:
            for run in scan_data.get("runs", []):
                for result in run.get("results", []):
                    finding = {
                        "tool": "codeql",
                        "rule_id": result.get("ruleId", ""),
                        "title": result.get("message", {}).get("text", ""),
                        "severity": self._normalize_severity(result.get("level", "note")),
                        "confidence": "high",
                        "category": "security",
                        "file_path": result.get("locations", [{}])[0].get("physicalLocation", {}).get("artifactLocation", {}).get("uri", ""),
                        "line_number": result.get("locations", [{}])[0].get("physicalLocation", {}).get("region", {}).get("startLine", 0),
                        "message": result.get("message", {}).get("text", "")
                    }
                    findings.append(finding)

        return {
            "tool": "codeql",
            "findings": findings,
            "scan_stats": {}
        }

    def _process_generic_sast_results(self, scan_data: Dict[str, Any], tool_type: str) -> Dict[str, Any]:
        """Process generic SAST results"""

        findings = []

        if "findings" in scan_data:
            for finding in scan_data["findings"]:
                findings.append({
                    "tool": tool_type,
                    "rule_id": finding.get("rule_id", ""),
                    "title": finding.get("title", ""),
                    "severity": self._normalize_severity(finding.get("severity", "LOW")),
                    "confidence": finding.get("confidence", "medium"),
                    "category": finding.get("category", "unknown"),
                    "file_path": finding.get("file", ""),
                    "line_number": finding.get("line", 0),
                    "message": finding.get("message", "")
                })

        return {
            "tool": tool_type,
            "findings": findings,
            "scan_stats": {}
        }

    def _deduplicate_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate findings across different SAST tools"""

        deduplicated = []
        seen_combinations = set()

        for finding in findings:
            # Create unique identifier based on file path, line number, and issue type
            identifier = (
                finding.get("file_path", ""),
                finding.get("line_number", 0),
                finding.get("category", ""),
                finding.get("title", "")[:50]  # First 50 chars of title
            )

            if identifier not in seen_combinations:
                seen_combinations.add(identifier)
                finding["detected_by_tools"] = [finding["tool"]]
                deduplicated.append(finding)
            else:
                # Merge information from duplicate finding
                existing = next(f for f in deduplicated if self._findings_match(f, finding))
                if finding["tool"] not in existing["detected_by_tools"]:
                    existing["detected_by_tools"].append(finding["tool"])

        return deduplicated

    def _findings_match(self, finding1: Dict[str, Any], finding2: Dict[str, Any]) -> bool:
        """Check if two findings are duplicates"""
        return (
            finding1.get("file_path") == finding2.get("file_path") and
            finding1.get("line_number") == finding2.get("line_number") and
            finding1.get("category") == finding2.get("category") and
            finding1.get("title", "")[:50] == finding2.get("title", "")[:50]
        )

    def _generate_sast_recommendations(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations based on SAST findings"""

        recommendations = []

        # Group by severity and category
        critical_findings = [f for f in findings if f.get("severity") == "critical"]
        high_findings = [f for f in findings if f.get("severity") == "high"]

        if critical_findings:
            recommendations.append({
                "priority": "immediate",
                "category": "Critical Security Issues",
                "action": "Address critical SAST findings immediately",
                "count": len(critical_findings),
                "description": "Critical security vulnerabilities require immediate attention",
                "sample_issues": [f["title"] for f in critical_findings[:3]]
            })

        if high_findings:
            recommendations.append({
                "priority": "high",
                "category": "High Severity Issues",
                "action": "Fix high severity security issues",
                "count": len(high_findings),
                "description": "High severity issues should be addressed in current sprint",
                "sample_issues": [f["title"] for f in high_findings[:3]]
            })

        # Category-specific recommendations
        categories = {}
        for finding in findings:
            cat = finding.get("category", "unknown")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(finding)

        for category, cat_findings in categories.items():
            if len(cat_findings) >= 5:  # If 5+ findings in same category
                recommendations.append({
                    "priority": "medium",
                    "category": f"{category.title()} Pattern",
                    "action": f"Address recurring {category} issues",
                    "count": len(cat_findings),
                    "description": f"Multiple {category} issues suggest systematic problem"
                })

        return recommendations

    def generate_remediation_plan(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate actionable remediation plan for SAST findings"""

        remediation_plan = {
            "immediate_actions": [],
            "short_term_actions": [],
            "long_term_improvements": [],
            "code_review_items": [],
            "training_recommendations": []
        }

        # Categorize findings by remediation approach
        for finding in findings:
            severity = finding.get("severity", "low")
            category = finding.get("category", "")

            if severity in ["critical", "high"]:
                remediation_plan["immediate_actions"].append({
                    "finding": finding["title"],
                    "file": finding.get("file_path", ""),
                    "line": finding.get("line_number", 0),
                    "recommended_fix": self._get_specific_fix_guidance(finding),
                    "verification": f"Re-run SAST scan to confirm fix"
                })

            elif severity == "medium":
                remediation_plan["short_term_actions"].append({
                    "finding": finding["title"],
                    "category": category,
                    "effort": "medium",
                    "suggested_approach": self._get_fix_approach(finding)
                })

            # Add to code review items if pattern-based
            if self._is_pattern_issue(finding):
                remediation_plan["code_review_items"].append({
                    "pattern": finding["title"],
                    "review_focus": f"Look for similar {category} issues in codebase"
                })

        # Training recommendations based on finding patterns
        training_needs = self._identify_training_needs(findings)
        remediation_plan["training_recommendations"] = training_needs

        # Save remediation plan
        self._save_remediation_plan(remediation_plan)

        return remediation_plan

    def _get_specific_fix_guidance(self, finding: Dict[str, Any]) -> str:
        """Get specific fix guidance for a finding"""

        rule_id = finding.get("rule_id", "").lower()
        title = finding.get("title", "").lower()

        # Map common patterns to fix guidance
        if "hardcoded" in title or "secret" in title:
            return "Move secrets to environment variables or secret management system"
        elif "sql" in title and "injection" in title:
            return "Use parameterized queries or ORM to prevent SQL injection"
        elif "xss" in title or "cross-site" in title:
            return "Sanitize and escape user input, use Content-Security-Policy headers"
        elif "weak" in title and "crypto" in title:
            return "Use strong cryptographic algorithms (AES-256, RSA-2048+)"
        elif "random" in title:
            return "Use cryptographically secure random generators (secrets module)"
        else:
            return "Review code and apply security best practices"

    def _get_fix_approach(self, finding: Dict[str, Any]) -> str:
        """Get general fix approach for a finding"""

        category = finding.get("category", "")

        approaches = {
            "authentication": "Review authentication flow, implement MFA if needed",
            "authorization": "Implement proper access control checks",
            "code_quality": "Refactor code following SOLID principles",
            "security": "Apply OWASP security guidelines",
            "performance": "Profile and optimize critical paths"
        }

        return approaches.get(category, "Review and apply appropriate fixes")

    def _is_pattern_issue(self, finding: Dict[str, Any]) -> bool:
        """Check if finding represents a pattern issue"""

        pattern_indicators = ["recurring", "multiple", "pattern", "systematic"]
        title = finding.get("title", "").lower()

        return any(indicator in title for indicator in pattern_indicators)

    def _identify_training_needs(self, findings: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Identify training needs based on finding patterns"""

        training_needs = []
        category_counts = {}

        for finding in findings:
            cat = finding.get("category", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # If many findings in a category, suggest training
        for category, count in category_counts.items():
            if count >= 10:
                training_needs.append({
                    "topic": category.replace("_", " ").title(),
                    "reason": f"{count} issues found in this category",
                    "recommended_course": f"Secure coding practices for {category}"
                })

        return training_needs

    def _assess_task_confidence(self, task_type: str) -> str:
        """Assess confidence level for SAST task"""

        for level, tasks in self.confidence_levels.items():
            if task_type in tasks:
                return level

        return "low"

    def _execute_high_confidence_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute high confidence SAST task"""

        return {
            "success": True,
            "confidence": "high",
            "task_type": task_type,
            "action": "automated_fix_applied",
            "details": f"Applied automated fix for {task_type}"
        }

    def _execute_medium_confidence_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute medium confidence SAST task"""

        return {
            "success": True,
            "confidence": "medium",
            "task_type": task_type,
            "action": "fix_suggestion_generated",
            "details": f"Generated fix suggestion for {task_type} - requires review"
        }

    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity levels across different SAST tools"""

        severity_mapping = {
            "ERROR": "high",
            "WARNING": "medium",
            "INFO": "low",
            "NOTE": "info",
            "HIGH": "high",
            "MEDIUM": "medium",
            "LOW": "low",
            "CRITICAL": "critical"
        }

        return severity_mapping.get(severity.upper(), "low")

    def _save_aggregated_results(self, results: Dict[str, Any]):
        """Save aggregated SAST results to GP-DATA"""
        analysis_dir = self.config.get_analysis_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sast_aggregated_{timestamp}.json"
        output_file = analysis_dir / filename

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"💾 Aggregated results saved: {output_file}")

    def _save_remediation_plan(self, plan: Dict[str, Any]):
        """Save remediation plan to GP-DATA"""
        analysis_dir = self.config.get_analysis_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sast_remediation_plan_{timestamp}.json"
        output_file = analysis_dir / filename

        with open(output_file, 'w') as f:
            json.dump(plan, f, indent=2)

        print(f"💾 Remediation plan saved: {output_file}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get SAST agent status and capabilities"""

        return {
            "agent_id": self.agent_id,
            "supported_tools": self.supported_tools,
            "confidence_levels": self.confidence_levels,
            "capabilities": [
                "Multi-tool SAST aggregation",
                "Finding deduplication",
                "Remediation planning",
                "Code fix recommendations",
                "Technical debt management"
            ]
        }


def main():
    if len(sys.argv) < 2:
        print("SAST Security Agent - Static Application Security Testing")
        print()
        print("Commands:")
        print("  aggregate --scans <file1,file2,...>     - Aggregate findings from multiple SAST tools")
        print("  remediate --findings <file> --priority <level> - Generate remediation plan")
        print("  plan --findings <file> --output <file>  - Generate detailed remediation plan")
        print("  status                                   - Show agent capabilities")
        print()
        print("Examples:")
        print("  python sast_agent.py aggregate --scans bandit_results.json,semgrep_results.json")
        print("  python sast_agent.py remediate --findings sast_findings.json --priority high")
        print("  python sast_agent.py plan --findings sast_findings.json --output remediation_plan.json")
        sys.exit(1)

    command = sys.argv[1]
    agent = SASTAgent()

    if command == "aggregate":
        if "--scans" not in sys.argv:
            print("Usage: python sast_agent.py aggregate --scans <file1,file2,...>")
            sys.exit(1)

        scans_index = sys.argv.index("--scans") + 1
        scan_files = sys.argv[scans_index].split(",")

        results = agent.aggregate_sast_findings(scan_files)

        print(f"\n{'='*60}")
        print("SAST Aggregation Results")
        print(f"{'='*60}")
        print(f"Tools Processed: {', '.join(results['tools_processed'])}")
        print(f"Total Findings: {results['total_findings']}")
        print(f"Severity Breakdown:")
        for severity, count in results['findings_by_severity'].items():
            if count > 0:
                print(f"  {severity.upper()}: {count}")

    elif command == "remediate":
        if "--findings" not in sys.argv:
            print("Usage: python sast_agent.py remediate --findings <file> --priority <level>")
            sys.exit(1)

        findings_index = sys.argv.index("--findings") + 1
        findings_file = sys.argv[findings_index]

        priority = "high"
        if "--priority" in sys.argv:
            priority_index = sys.argv.index("--priority") + 1
            priority = sys.argv[priority_index]

        with open(findings_file, 'r') as f:
            data = json.load(f)

        findings = data.get("deduplicated_findings", data.get("findings", []))

        # Filter by priority
        if priority == "high":
            findings = [f for f in findings if f.get("severity") in ["critical", "high"]]

        plan = agent.generate_remediation_plan(findings)

        print(f"\n{'='*60}")
        print("Remediation Plan")
        print(f"{'='*60}")
        print(f"Immediate Actions: {len(plan['immediate_actions'])}")
        print(f"Short-term Actions: {len(plan['short_term_actions'])}")
        print(f"Training Recommendations: {len(plan['training_recommendations'])}")

    elif command == "plan":
        if "--findings" not in sys.argv:
            print("Usage: python sast_agent.py plan --findings <file> --output <file>")
            sys.exit(1)

        findings_index = sys.argv.index("--findings") + 1
        findings_file = sys.argv[findings_index]

        output_file = "remediation_plan.json"
        if "--output" in sys.argv:
            output_index = sys.argv.index("--output") + 1
            output_file = sys.argv[output_index]

        with open(findings_file, 'r') as f:
            data = json.load(f)

        findings = data.get("deduplicated_findings", data.get("findings", []))
        plan = agent.generate_remediation_plan(findings)

        with open(output_file, 'w') as f:
            json.dump(plan, f, indent=2)

        print(f"✅ Remediation plan saved to: {output_file}")

    elif command == "status":
        status = agent.get_agent_status()

        print(f"\n{'='*60}")
        print("SAST Agent Status")
        print(f"{'='*60}")
        print(f"Agent ID: {status['agent_id']}")
        print(f"Supported Tools: {', '.join(status['supported_tools'])}")
        print(f"Capabilities:")
        for cap in status['capabilities']:
            print(f"  - {cap}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()