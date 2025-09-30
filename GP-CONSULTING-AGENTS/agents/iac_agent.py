#!/usr/bin/env python3
"""
Infrastructure as Code Security Agent
Assists with secure IaC template development and review
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Import GP-DATA config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig

# Import existing scanners
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scanners"))
from checkov_scanner import CheckovScanner


class IaCSecurityAgent:
    """
    IaC Security Agent for template development and review

    Capabilities:
    - IaC security analysis
    - Secure template generation
    - Fix validation
    - Security documentation
    """

    def __init__(self):
        self.agent_id = "iac_security_agent"
        self.config = GPDataConfig()
        self.checkov_scanner = CheckovScanner()

    def analyze_iac_security(self, target_path: str) -> Dict:
        """Comprehensive IaC security analysis"""
        analysis_start = datetime.now()

        # Detect IaC frameworks
        iac_context = self._detect_iac_frameworks(Path(target_path))

        # Run Checkov scan
        print(f"🔍 Scanning IaC files with Checkov...")
        scan_results = {}
        if iac_context["total_iac_files"] > 0:
            scan_results["checkov"] = self.checkov_scanner.scan(target_path)

        # Prioritize findings
        prioritized_findings = self._prioritize_iac_findings(scan_results)

        # Generate recommendations
        template_recommendations = self._generate_template_recommendations(
            prioritized_findings, iac_context
        )

        result = {
            "agent": self.agent_id,
            "timestamp": analysis_start.isoformat(),
            "target": target_path,
            "iac_context": iac_context,
            "scan_results": scan_results,
            "prioritized_findings": prioritized_findings,
            "template_recommendations": template_recommendations,
            "analysis_duration": (datetime.now() - analysis_start).total_seconds()
        }

        # Save to GP-DATA
        self._save_analysis(result)

        return result

    def _detect_iac_frameworks(self, target: Path) -> Dict:
        """Detect which IaC frameworks are present"""
        context = {
            "terraform_files": [str(f) for f in target.glob("**/*.tf")],
            "tfvars_files": [str(f) for f in target.glob("**/*.tfvars")],
            "cloudformation_files": [],
            "arm_template_files": [],
            "total_iac_files": 0
        }

        # Detect CloudFormation templates
        for json_file in target.glob("**/*.json"):
            try:
                with open(json_file, 'r') as f:
                    content = json.load(f)
                    if "AWSTemplateFormatVersion" in content or "Resources" in content:
                        context["cloudformation_files"].append(str(json_file))
            except:
                continue

        # Detect ARM templates
        for json_file in target.glob("**/*.json"):
            try:
                with open(json_file, 'r') as f:
                    content = json.load(f)
                    if "$schema" in content and "deploymentTemplate" in str(content.get("$schema", "")):
                        context["arm_template_files"].append(str(json_file))
            except:
                continue

        context["total_iac_files"] = (
            len(context["terraform_files"]) +
            len(context["cloudformation_files"]) +
            len(context["arm_template_files"])
        )

        return context

    def _prioritize_iac_findings(self, scan_results: Dict) -> List[Dict]:
        """Prioritize findings by severity"""
        findings = []

        if "checkov" in scan_results:
            checkov_findings = scan_results["checkov"].get("findings", [])
            for finding in checkov_findings:
                findings.append({
                    "scanner": "checkov",
                    "severity": finding.get("severity", "UNKNOWN"),
                    "rule_id": finding.get("id", ""),
                    "resource": finding.get("resource", ""),
                    "description": finding.get("description", ""),
                    "file_path": finding.get("file_path", ""),
                    "line_range": finding.get("line_range", [])
                })

        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}
        findings.sort(key=lambda x: severity_order.get(x["severity"], 5))

        return findings

    def _generate_template_recommendations(self, findings: List[Dict], iac_context: Dict) -> List[Dict]:
        """Generate template improvement recommendations"""
        recommendations = []

        # Group findings by resource type
        findings_by_resource = {}
        for finding in findings:
            resource = finding.get("resource", "unknown")
            if resource not in findings_by_resource:
                findings_by_resource[resource] = []
            findings_by_resource[resource].append(finding)

        # Generate recommendations for each resource type
        for resource_type, resource_findings in findings_by_resource.items():
            if len(iac_context["terraform_files"]) > 0:
                rec = self._generate_terraform_recommendation(resource_type, resource_findings)
                recommendations.append(rec)

        return recommendations

    def _generate_terraform_recommendation(self, resource_type: str, findings: List[Dict]) -> Dict:
        """Generate Terraform-specific recommendation"""
        return {
            "resource_type": resource_type,
            "findings_count": len(findings),
            "severity_breakdown": {
                "critical": len([f for f in findings if f["severity"] == "CRITICAL"]),
                "high": len([f for f in findings if f["severity"] == "HIGH"]),
                "medium": len([f for f in findings if f["severity"] == "MEDIUM"])
            },
            "recommendation": f"Review and harden {resource_type} configuration",
            "affected_files": list(set([f["file_path"] for f in findings]))
        }

    def generate_secure_templates(self, findings: List[Dict], template_type: str = "terraform") -> Dict:
        """Generate secure IaC templates"""
        generated_templates = {
            "security_fixes": [],
            "secure_modules": [],
            "documentation_snippets": []
        }

        # Group findings by resource type
        findings_by_resource = {}
        for finding in findings:
            resource = finding.get("resource", "unknown")
            if resource not in findings_by_resource:
                findings_by_resource[resource] = []
            findings_by_resource[resource].append(finding)

        # Generate fixes for common resource types
        for resource_type, resource_findings in findings_by_resource.items():
            if "s3" in resource_type.lower():
                fix = self._generate_s3_fix()
                generated_templates["security_fixes"].append(fix)
            elif "security_group" in resource_type.lower():
                fix = self._generate_security_group_fix()
                generated_templates["security_fixes"].append(fix)

        return generated_templates

    def _generate_s3_fix(self) -> Dict:
        """Generate secure S3 bucket template"""
        return {
            "resource_type": "aws_s3_bucket",
            "template": """resource "aws_s3_bucket" "secure_bucket" {
  bucket = var.bucket_name
  tags   = var.tags
}

resource "aws_s3_bucket_encryption_configuration" "bucket_encryption" {
  bucket = aws_s3_bucket.secure_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "bucket_pab" {
  bucket = aws_s3_bucket.secure_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "bucket_versioning" {
  bucket = aws_s3_bucket.secure_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}""",
            "improvements": [
                "Added server-side encryption",
                "Blocked public access",
                "Enabled versioning",
                "Used separate resources (Terraform 4.x pattern)"
            ]
        }

    def _generate_security_group_fix(self) -> Dict:
        """Generate secure security group template"""
        return {
            "resource_type": "aws_security_group",
            "template": """resource "aws_security_group" "secure_sg" {
  name_prefix = var.name_prefix
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTPS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    description = "HTTPS outbound"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}""",
            "improvements": [
                "Removed overly permissive 0.0.0.0/0 ingress",
                "Added specific port restrictions",
                "Implemented least-privilege principle"
            ]
        }

    def validate_iac_fixes(self, original_path: str, fixed_path: str) -> Dict:
        """Validate IaC fixes"""
        print("🔍 Validating IaC security fixes...")

        # Scan original
        original_results = {}
        if Path(original_path).exists():
            original_results = self.checkov_scanner.scan(original_path)

        # Scan fixed
        fixed_results = {}
        if Path(fixed_path).exists():
            fixed_results = self.checkov_scanner.scan(fixed_path)

        # Compare
        validation = self._compare_scan_results(original_results, fixed_results)

        result = {
            "validation_timestamp": datetime.now().isoformat(),
            "original_path": original_path,
            "fixed_path": fixed_path,
            "original_findings": len(original_results.get("findings", [])),
            "fixed_findings": len(fixed_results.get("findings", [])),
            "improvement_summary": validation,
            "validation_success": validation["issues_resolved"] > 0
        }

        return result

    def _compare_scan_results(self, original: Dict, fixed: Dict) -> Dict:
        """Compare scan results"""
        original_findings = original.get("findings", [])
        fixed_findings = fixed.get("findings", [])

        original_critical = len([f for f in original_findings if f.get("severity") == "CRITICAL"])
        fixed_critical = len([f for f in fixed_findings if f.get("severity") == "CRITICAL"])

        original_high = len([f for f in original_findings if f.get("severity") == "HIGH"])
        fixed_high = len([f for f in fixed_findings if f.get("severity") == "HIGH"])

        issues_resolved = len(original_findings) - len(fixed_findings)

        return {
            "issues_resolved": issues_resolved,
            "critical_issues_resolved": original_critical - fixed_critical,
            "high_issues_resolved": original_high - fixed_high,
            "remaining_critical_issues": fixed_critical,
            "remaining_high_issues": fixed_high,
            "overall_improvement": (issues_resolved / max(1, len(original_findings))) * 100
        }

    def create_security_documentation(self, analysis_results: Dict) -> Dict:
        """Generate IaC security documentation"""
        doc_content = self._generate_security_guide(analysis_results)

        return {
            "documentation_files": [
                {
                    "filename": "IAC_SECURITY_GUIDE.md",
                    "content": doc_content,
                    "description": "IaC security guide"
                }
            ],
            "generated_at": datetime.now().isoformat()
        }

    def _generate_security_guide(self, analysis: Dict) -> str:
        """Generate security guide content"""
        total_findings = len(analysis.get("prioritized_findings", []))

        doc = f"""# Infrastructure as Code Security Guide

## Analysis Summary
- **Target**: {analysis.get('target', 'N/A')}
- **Total Findings**: {total_findings}
- **IaC Files**: {analysis.get('iac_context', {}).get('total_iac_files', 0)}

## Security Findings

### Critical Issues
"""
        critical_findings = [f for f in analysis.get("prioritized_findings", []) if f["severity"] == "CRITICAL"]
        for finding in critical_findings[:5]:
            doc += f"- {finding.get('description', 'Unknown issue')} ({finding.get('file_path', 'N/A')})\n"

        doc += """
### High Priority Issues
"""
        high_findings = [f for f in analysis.get("prioritized_findings", []) if f["severity"] == "HIGH"]
        for finding in high_findings[:5]:
            doc += f"- {finding.get('description', 'Unknown issue')} ({finding.get('file_path', 'N/A')})\n"

        doc += """
## Recommendations

1. Review and address all CRITICAL findings immediately
2. Implement security best practices for identified resource types
3. Enable encryption and access controls
4. Follow least-privilege principles
5. Use infrastructure testing and validation

## Next Steps

1. Apply recommended security fixes
2. Run validation scans
3. Update security documentation
4. Implement continuous IaC security scanning
"""
        return doc

    def _save_analysis(self, analysis: Dict):
        """Save analysis to GP-DATA"""
        analysis_dir = self.config.get_analysis_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"iac_security_analysis_{timestamp}.json"
        output_file = analysis_dir / filename

        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"\n💾 Analysis saved to: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("IaC Security Agent - Infrastructure as Code Security")
        print()
        print("Commands:")
        print("  analyze <target_path>                  - Analyze IaC security")
        print("  generate <findings_file>               - Generate secure templates")
        print("  validate <original_path> <fixed_path>  - Validate fixes")
        print("  document <analysis_file>               - Generate documentation")
        print()
        print("Examples:")
        print("  python iac_agent.py analyze ./terraform")
        print("  python iac_agent.py validate ./original ./fixed")
        sys.exit(1)

    command = sys.argv[1]
    agent = IaCSecurityAgent()

    if command == "analyze":
        if len(sys.argv) < 3:
            print("Usage: python iac_agent.py analyze <target_path>")
            sys.exit(1)

        target_path = sys.argv[2]
        results = agent.analyze_iac_security(target_path)

        print(f"\n{'='*60}")
        print("IaC Security Analysis Complete")
        print(f"{'='*60}")
        print(f"Target: {results['target']}")
        print(f"IaC Files: {results['iac_context']['total_iac_files']}")
        print(f"Findings: {len(results['prioritized_findings'])}")

    elif command == "validate":
        if len(sys.argv) < 4:
            print("Usage: python iac_agent.py validate <original_path> <fixed_path>")
            sys.exit(1)

        original_path = sys.argv[2]
        fixed_path = sys.argv[3]
        results = agent.validate_iac_fixes(original_path, fixed_path)

        print(f"\n{'='*60}")
        print("IaC Fix Validation Complete")
        print(f"{'='*60}")
        print(f"Issues Resolved: {results['improvement_summary']['issues_resolved']}")
        print(f"Improvement: {results['improvement_summary']['overall_improvement']:.1f}%")

    elif command == "generate":
        if len(sys.argv) < 3:
            print("Usage: python iac_agent.py generate <findings_file>")
            sys.exit(1)

        findings_file = sys.argv[2]
        with open(findings_file, 'r') as f:
            analysis = json.load(f)

        findings = analysis.get("prioritized_findings", [])
        templates = agent.generate_secure_templates(findings)

        print(f"\n{'='*60}")
        print("Secure Templates Generated")
        print(f"{'='*60}")
        print(f"Security Fixes: {len(templates['security_fixes'])}")

    elif command == "document":
        if len(sys.argv) < 3:
            print("Usage: python iac_agent.py document <analysis_file>")
            sys.exit(1)

        analysis_file = sys.argv[2]
        with open(analysis_file, 'r') as f:
            analysis = json.load(f)

        docs = agent.create_security_documentation(analysis)

        print(f"\n{'='*60}")
        print("Documentation Generated")
        print(f"{'='*60}")
        for doc in docs["documentation_files"]:
            print(f"- {doc['filename']}: {doc['description']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()