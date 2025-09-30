#!/usr/bin/env python3
"""
Unified Terraform Fixer - Coordinates Multiple Fixes with Proper Parsing
Fixes concurrent modification conflicts by using structured modification approach
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil
from datetime import datetime

# Import proven fix patterns
from kics_remediation_patterns import get_fix_pattern, TERRAFORM_FIX_PATTERNS

class TerraformResource:
    """Represents a Terraform resource with structured parsing"""

    def __init__(self, resource_type: str, resource_name: str, start_line: int, end_line: int, content: str):
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.start_line = start_line
        self.end_line = end_line
        self.content = content
        self.attributes = {}
        self.blocks = {}
        self.modifications = []

    def add_attribute(self, key: str, value: str, source: str = ""):
        """Add or update an attribute at resource level"""
        self.modifications.append({
            "type": "attribute",
            "key": key,
            "value": value,
            "source": source
        })

    def add_block(self, block_type: str, block_content: str, source: str = ""):
        """Add a configuration block at resource level"""
        self.modifications.append({
            "type": "block",
            "block_type": block_type,
            "content": block_content,
            "source": source
        })

    def has_attribute(self, key: str) -> bool:
        """Check if attribute already exists"""
        return key in self.content or any(mod["key"] == key for mod in self.modifications if mod["type"] == "attribute")

    def has_block(self, block_type: str) -> bool:
        """Check if block already exists"""
        return block_type in self.content or any(mod["block_type"] == block_type for mod in self.modifications if mod["type"] == "block")

class ProductionTerraformFixer:
    """Coordinates multiple Terraform fixes to prevent conflicts"""

    def __init__(self):
        self.backup_dir = Path("/home/jimmie/linkops-industries/James-OS/guidepoint/results/backups")
        self.backup_dir.mkdir(exist_ok=True)

    def apply_fixes(self, scan_results: dict, target_path: str) -> dict:
        """Apply production-ready fixes using unified coordination"""
        fixes_applied = []
        errors = []

        # Check if we have intelligence analysis with high-confidence fixes
        if "intelligence_analysis" in scan_results:
            intelligence_fixes = self._apply_intelligence_fixes(
                scan_results["intelligence_analysis"],
                scan_results,
                target_path
            )
            fixes_applied.extend(intelligence_fixes)
        else:
            # Fallback to processing raw Checkov findings
            if "checkov" in scan_results["results"]:
                checkov_fixes = self._fix_checkov_issues(
                    scan_results["results"]["checkov"],
                    target_path
                )
                fixes_applied.extend(checkov_fixes)

        return {
            "fixes_applied": fixes_applied,
            "errors": errors,
            "summary": {
                "total_fixes": len(fixes_applied),
                "total_errors": len(errors)
            }
        }

    def _apply_intelligence_fixes(self, intelligence_analysis: dict, scan_results: dict, target_path: str) -> List[dict]:
        """Apply fixes using intelligence analysis and unified coordination"""
        fixes_applied = []
        fix_recommendations = intelligence_analysis.get("fix_recommendations", [])

        # Filter for high-confidence Terraform fixes
        terraform_fixes = [
            rec for rec in fix_recommendations
            if rec.get("confidence", 0) >= 0.7 and rec.get("scanner") == "checkov"
        ]

        print(f"Applying {len(terraform_fixes)} production-ready fixes using unified coordination...")

        # Group fixes by file to minimize file operations
        files_to_fix = {}
        for recommendation in terraform_fixes:
            vuln_id = recommendation.get("vulnerability_id", "")
            checkov_finding = self._find_checkov_finding(scan_results, vuln_id)

            if checkov_finding:
                file_path = checkov_finding.get("file_abs_path", checkov_finding.get("file_path", ""))
                if file_path and os.path.exists(file_path):
                    if file_path not in files_to_fix:
                        files_to_fix[file_path] = []
                    files_to_fix[file_path].append((vuln_id, recommendation, checkov_finding))

        # Apply all fixes per file using unified coordination
        for file_path, fix_list in files_to_fix.items():
            print(f"  Processing {len(fix_list)} fixes for {os.path.basename(file_path)} with unified coordination...")
            self._create_backup(file_path)

            file_fixes = self._apply_unified_file_fixes(file_path, fix_list)
            fixes_applied.extend(file_fixes)

        return fixes_applied

    def _fix_checkov_issues(self, checkov_results: dict, target_path: str) -> List[dict]:
        """Fix Checkov issues using unified coordination"""
        fixes_applied = []

        findings = checkov_results.get("findings", [])
        if not findings:
            return fixes_applied

        # Group findings by file to minimize file operations
        files_to_fix = {}
        for finding in findings:
            check_id = finding.get("check_id", "")
            file_path = finding.get("file_abs_path", finding.get("file_path", ""))

            # Convert relative path to absolute if needed
            if file_path and not os.path.isabs(file_path):
                file_path = os.path.join(target_path, file_path.lstrip('/'))

            if file_path and os.path.exists(file_path) and check_id:
                if file_path not in files_to_fix:
                    files_to_fix[file_path] = []
                files_to_fix[file_path].append((check_id, finding))

        print(f"Processing {len(files_to_fix)} files with Checkov findings using unified coordination...")

        # Apply fixes per file using unified coordination
        for file_path, fix_list in files_to_fix.items():
            print(f"  Processing {len(fix_list)} fixes for {os.path.basename(file_path)} with unified coordination...")
            self._create_backup(file_path)

            file_fixes = self._apply_unified_checkov_file_fixes(file_path, fix_list)
            fixes_applied.extend(file_fixes)

        return fixes_applied

    def _apply_unified_file_fixes(self, file_path: str, fix_list: List[tuple]) -> List[dict]:
        """Apply multiple fixes to a single file using unified coordination"""
        fixes_applied = []

        with open(file_path, 'r') as f:
            content = f.read()

        # Parse Terraform structure
        resources = self._parse_terraform_resources(content)

        # Plan all modifications across resources
        modification_plan = {}

        for vuln_id, recommendation, checkov_finding in fix_list:
            print(f"    Planning fix for {vuln_id}...")

            # Get proven fix pattern
            fix_pattern = get_fix_pattern(vuln_id)
            if not fix_pattern:
                print(f"      No proven pattern available for {vuln_id}")
                continue

            # Plan the fix modifications
            planned_modifications = self._plan_fix_modifications(vuln_id, fix_pattern, resources, checkov_finding)

            for resource_key, modifications in planned_modifications.items():
                if resource_key not in modification_plan:
                    modification_plan[resource_key] = []
                modification_plan[resource_key].extend(modifications)

                fixes_applied.append({
                    "vulnerability_id": vuln_id,
                    "file_path": file_path,
                    "fix_description": f"Planned {vuln_id} fix for {resource_key}",
                    "confidence": recommendation.get("confidence", 0),
                    "timestamp": datetime.now().isoformat(),
                    "pattern_used": fix_pattern.get("name", vuln_id)
                })

        # Apply all planned modifications in coordinated manner
        if modification_plan:
            new_content = self._apply_coordinated_modifications(content, resources, modification_plan)

            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"  📁 Updated {os.path.basename(file_path)} with {len(fixes_applied)} coordinated fixes")

        return fixes_applied

    def _apply_unified_checkov_file_fixes(self, file_path: str, fix_list: List[tuple]) -> List[dict]:
        """Apply Checkov fixes using unified coordination"""
        fixes_applied = []

        with open(file_path, 'r') as f:
            content = f.read()

        # Parse Terraform structure
        resources = self._parse_terraform_resources(content)

        # Plan all modifications across resources
        modification_plan = {}

        for check_id, finding in fix_list:
            print(f"    Planning fix for {check_id}...")

            # Get proven fix pattern
            fix_pattern = get_fix_pattern(check_id)
            if not fix_pattern:
                print(f"      No proven pattern available for {check_id}")
                continue

            # Plan the fix modifications
            planned_modifications = self._plan_fix_modifications(check_id, fix_pattern, resources, finding)

            for resource_key, modifications in planned_modifications.items():
                if resource_key not in modification_plan:
                    modification_plan[resource_key] = []
                modification_plan[resource_key].extend(modifications)

                fixes_applied.append({
                    "vulnerability_id": check_id,
                    "file_path": file_path,
                    "fix_description": f"Planned {check_id} fix for {resource_key}",
                    "confidence": 0.8,  # High confidence for proven patterns
                    "timestamp": datetime.now().isoformat(),
                    "pattern_used": fix_pattern.get("name", check_id)
                })

        # Apply all planned modifications in coordinated manner
        if modification_plan:
            new_content = self._apply_coordinated_modifications(content, resources, modification_plan)

            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"  📁 Updated {os.path.basename(file_path)} with {len(fixes_applied)} coordinated fixes")

        return fixes_applied

    def _parse_terraform_resources(self, content: str) -> Dict[str, TerraformResource]:
        """Parse Terraform content to identify resources and their structure"""
        resources = {}
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for resource declarations
            resource_match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)
            if resource_match:
                resource_type = resource_match.group(1)
                resource_name = resource_match.group(2)
                start_line = i

                # Find the end of this resource by counting braces
                brace_count = 1
                resource_lines = [lines[i]]
                i += 1

                while i < len(lines) and brace_count > 0:
                    current_line = lines[i]
                    brace_count += current_line.count('{') - current_line.count('}')
                    resource_lines.append(current_line)
                    i += 1

                end_line = i - 1
                resource_content = '\n'.join(resource_lines)

                resource_key = f"{resource_type}.{resource_name}"
                resources[resource_key] = TerraformResource(
                    resource_type, resource_name, start_line, end_line, resource_content
                )
                continue

            i += 1

        return resources

    def _plan_fix_modifications(self, vuln_id: str, pattern: dict, resources: Dict[str, TerraformResource], finding: dict) -> Dict[str, List[dict]]:
        """Plan modifications for a specific vulnerability fix"""
        modifications = {}

        # Target EC2 instances for these specific fixes
        if vuln_id in ["CKV_AWS_8", "CKV_AWS_135", "CKV2_AWS_41", "CKV_AWS_126", "CKV_AWS_79"]:
            for resource_key, resource in resources.items():
                if resource.resource_type == "aws_instance":
                    resource_modifications = []

                    if vuln_id == "CKV_AWS_126" and not resource.has_attribute("monitoring"):
                        resource_modifications.append({
                            "type": "attribute",
                            "key": "monitoring",
                            "value": "true",
                            "source": vuln_id
                        })

                    elif vuln_id == "CKV_AWS_135" and not resource.has_attribute("ebs_optimized"):
                        resource_modifications.append({
                            "type": "attribute",
                            "key": "ebs_optimized",
                            "value": "true",
                            "source": vuln_id
                        })

                    elif vuln_id == "CKV2_AWS_41" and not resource.has_attribute("iam_instance_profile"):
                        resource_modifications.append({
                            "type": "attribute",
                            "key": "iam_instance_profile",
                            "value": "aws_iam_instance_profile.ec2_profile.name",
                            "source": vuln_id
                        })

                    elif vuln_id == "CKV_AWS_79" and not resource.has_block("metadata_options"):
                        resource_modifications.append({
                            "type": "block",
                            "block_type": "metadata_options",
                            "content": """  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
    http_put_response_hop_limit = 1
  }""",
                            "source": vuln_id
                        })

                    elif vuln_id == "CKV_AWS_8" and not resource.has_block("root_block_device"):
                        resource_modifications.append({
                            "type": "block",
                            "block_type": "root_block_device",
                            "content": """  root_block_device {
    encrypted = true
  }""",
                            "source": vuln_id
                        })

                    if resource_modifications:
                        modifications[resource_key] = resource_modifications

        return modifications

    def _apply_coordinated_modifications(self, content: str, resources: Dict[str, TerraformResource], modification_plan: Dict[str, List[dict]]) -> str:
        """Apply all planned modifications in a coordinated manner"""
        lines = content.split('\n')

        # Process modifications from end to beginning to preserve line numbers
        all_modifications = []

        for resource_key, modifications in modification_plan.items():
            if resource_key in resources:
                resource = resources[resource_key]
                for mod in modifications:
                    all_modifications.append((resource.end_line, mod, resource_key))

        # Sort by line number in descending order
        all_modifications.sort(key=lambda x: x[0], reverse=True)

        # Apply modifications
        for line_num, mod, resource_key in all_modifications:
            if mod["type"] == "attribute":
                # Insert attribute before closing brace
                lines.insert(line_num, f"  {mod['key']} = {mod['value']}")
                print(f"      ✅ Added {mod['key']} to {resource_key}")
            elif mod["type"] == "block":
                # Insert block before closing brace
                block_lines = mod["content"].split('\n')
                for i, block_line in enumerate(reversed(block_lines)):
                    lines.insert(line_num, block_line)
                print(f"      ✅ Added {mod['block_type']} block to {resource_key}")

        return '\n'.join(lines)

    def _find_checkov_finding(self, scan_results: dict, vuln_id: str) -> dict:
        """Find the Checkov finding for a specific vulnerability ID"""
        checkov_results = scan_results.get("results", {}).get("checkov", {})
        findings = checkov_results.get("findings", [])

        for finding in findings:
            if finding.get("check_id") == vuln_id:
                return finding
        return None

    def _create_backup(self, file_path: str):
        """Create backup of file before modification"""
        file_obj = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_obj.name}_{timestamp}.backup"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(file_path, backup_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python unified_terraform_fixer.py <scan_results.json> <target_path>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        scan_results = json.load(f)

    fixer = ProductionTerraformFixer()
    results = fixer.apply_fixes(scan_results, sys.argv[2])

    print(f"Applied {results['summary']['total_fixes']} coordinated fixes")
    for fix in results["fixes_applied"]:
        print(f"  - {fix['vulnerability_id']}: {fix['fix_description']} (Pattern: {fix['pattern_used']})")