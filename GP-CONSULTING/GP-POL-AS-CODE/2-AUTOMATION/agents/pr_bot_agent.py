#!/usr/bin/env python3
"""
PR Bot Agent
Step 2: Automated Fix Proposals - Opens PRs Against Helm/Kustomize Sources

When Gatekeeper audit finds violations, this bot:
1. Analyzes violations from audit report
2. Generates fixes using opa_fixer.py
3. Creates git branch with fixes
4. Opens PR with detailed remediation plan
"""

import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import sys

# Import OPA fixer
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fixers"))
from opa_fixer import OpaFixer


class PRBotAgent:
    """
    Automated PR bot for security fixes.

    Workflow:
    1. Read Gatekeeper audit violations
    2. Generate fixes using OpaFixer
    3. Create git branch
    4. Commit fixes
    5. Push and create PR
    """

    def __init__(self, repo_path: Path, git_remote: str = "origin"):
        self.repo_path = repo_path
        self.git_remote = git_remote
        self.git_path = self._find_git()
        self.fixer = OpaFixer()

        if not self.repo_path.exists():
            raise RuntimeError(f"Repository not found: {self.repo_path}")

    def _find_git(self) -> str:
        """Locate git binary"""
        if shutil.which("git"):
            return "git"
        raise RuntimeError("git not installed")

    def _git(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run git command in repo"""
        return subprocess.run(
            [self.git_path] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

    def analyze_audit_violations(self, audit_file: Path) -> List[Dict]:
        """
        Parse Gatekeeper audit violations from JSON or text report

        Returns list of violations with fix metadata
        """
        if not audit_file.exists():
            raise FileNotFoundError(f"Audit file not found: {audit_file}")

        # Try parsing as JSON first
        try:
            audit_data = json.loads(audit_file.read_text())
            return audit_data.get("violations", [])
        except json.JSONDecodeError:
            # Fall back to text parsing (from gatekeeper_audit_agent.py)
            violations = []
            lines = audit_file.read_text().splitlines()

            # Simple text parsing (enhance as needed)
            for line in lines:
                if "Resource:" in line:
                    # Extract resource info
                    # Example: "  Resource: Deployment/nginx"
                    parts = line.split("/")
                    if len(parts) == 2:
                        kind, name = parts[0].strip().split()[-1], parts[1].strip()
                        violations.append({
                            "resource": {"kind": kind, "name": name}
                        })

            return violations

    def generate_fixes(self, violations: List[Dict]) -> Dict[Path, str]:
        """
        Generate fixes for violations

        Returns:
            {Path("path/to/file.yaml"): "fixed_content", ...}
        """
        fixes = {}

        for violation in violations:
            resource = violation.get("resource", {})
            resource_kind = resource.get("kind", "")
            resource_name = resource.get("name", "")
            constraint_kind = violation.get("constraint_kind", "")

            # Find resource file in repo
            resource_file = self._find_resource_file(resource_kind, resource_name)
            if not resource_file:
                print(f"⚠️  Could not find file for {resource_kind}/{resource_name}")
                continue

            # Apply fix using OpaFixer
            fixed_content = self._apply_fix(resource_file, constraint_kind)
            if fixed_content:
                fixes[resource_file] = fixed_content

        return fixes

    def _find_resource_file(self, kind: str, name: str) -> Optional[Path]:
        """
        Search for Kubernetes resource file in repo

        Looks in common locations: manifests/, helm/, kustomize/
        """
        search_dirs = [
            self.repo_path / "manifests",
            self.repo_path / "helm",
            self.repo_path / "kustomize",
            self.repo_path / "k8s",
            self.repo_path  # root
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            # Search for YAML files containing the resource
            for yaml_file in search_dir.rglob("*.yaml"):
                try:
                    content = yaml_file.read_text()
                    if f"kind: {kind}" in content and f"name: {name}" in content:
                        return yaml_file
                except Exception:
                    continue

            for yaml_file in search_dir.rglob("*.yml"):
                try:
                    content = yaml_file.read_text()
                    if f"kind: {kind}" in content and f"name: {name}" in content:
                        return yaml_file
                except Exception:
                    continue

        return None

    def _apply_fix(self, resource_file: Path, constraint_kind: str) -> Optional[str]:
        """Apply OpaFixer to resource file"""
        try:
            import yaml

            # Read current content
            content = yaml.safe_load(resource_file.read_text())

            # Map constraint kind to fix strategy
            fix_applied = False

            if "DenyPrivileged" in constraint_kind:
                # Remove privileged flag
                for container in content.get("spec", {}).get("template", {}).get("spec", {}).get("containers", []):
                    if container.get("securityContext", {}).get("privileged"):
                        container.setdefault("securityContext", {})["privileged"] = False
                        fix_applied = True

            elif "RequireNonRoot" in constraint_kind:
                # Add runAsNonRoot
                spec = content.get("spec", {}).get("template", {}).get("spec", {})
                spec.setdefault("securityContext", {})["runAsNonRoot"] = True
                fix_applied = True

            elif "RequireResourceLimits" in constraint_kind:
                # Add resource limits
                for container in content.get("spec", {}).get("template", {}).get("spec", {}).get("containers", []):
                    container.setdefault("resources", {})
                    container["resources"].setdefault("limits", {})
                    container["resources"]["limits"].setdefault("cpu", "500m")
                    container["resources"]["limits"].setdefault("memory", "512Mi")
                    container["resources"].setdefault("requests", {})
                    container["resources"]["requests"].setdefault("cpu", "100m")
                    container["resources"]["requests"].setdefault("memory", "128Mi")
                fix_applied = True

            if fix_applied:
                return yaml.dump(content, default_flow_style=False, sort_keys=False)

        except Exception as e:
            print(f"Error applying fix to {resource_file}: {e}")

        return None

    def create_pr(self, fixes: Dict[Path, str], violations: List[Dict]) -> bool:
        """
        Create PR with fixes

        1. Create branch
        2. Apply fixes
        3. Commit
        4. Push
        5. Create PR (using gh CLI)
        """
        if not fixes:
            print("No fixes to apply")
            return False

        # Create branch
        branch_name = f"gatekeeper-auto-fix-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        result = self._git(["checkout", "-b", branch_name])
        if result.returncode != 0:
            print(f"Failed to create branch: {result.stderr}")
            return False

        # Apply fixes
        for file_path, fixed_content in fixes.items():
            file_path.write_text(fixed_content)
            self._git(["add", str(file_path)])

        # Commit
        commit_msg = f"""🤖 Auto-fix Gatekeeper violations

Fixed {len(fixes)} resources:
{chr(10).join([f"- {f.name}" for f in fixes.keys()])}

Violations addressed:
{chr(10).join([f"- {v.get('constraint_kind', 'Unknown')}" for v in violations[:5]])}

Generated by PR Bot Agent
"""
        result = self._git(["commit", "-m", commit_msg])
        if result.returncode != 0:
            print(f"Failed to commit: {result.stderr}")
            return False

        # Push
        result = self._git(["push", "-u", self.git_remote, branch_name])
        if result.returncode != 0:
            print(f"Failed to push: {result.stderr}")
            return False

        # Create PR using gh CLI
        if shutil.which("gh"):
            pr_body = f"""## Automated Security Fixes

This PR addresses {len(violations)} Gatekeeper policy violations found in the daily audit.

### Fixed Resources
{chr(10).join([f"- `{f.relative_to(self.repo_path)}`" for f in fixes.keys()])}

### Violations Fixed
{chr(10).join([f"- **{v.get('constraint_kind', 'Unknown')}**: {v.get('message', '')}" for v in violations[:10]])}

### Testing
- [ ] Review changes
- [ ] Test in dev/staging environment
- [ ] Verify Gatekeeper audit passes

---
🤖 Generated by [PR Bot Agent](https://github.com/linkops-industries/GP-copilot)
"""
            subprocess.run(
                ["gh", "pr", "create", "--title", f"🤖 Auto-fix Gatekeeper violations ({len(fixes)} resources)", "--body", pr_body],
                cwd=self.repo_path
            )

        print(f"✅ PR created: {branch_name}")
        return True


def main():
    """CLI entrypoint"""
    import sys

    if len(sys.argv) < 3:
        print("Usage: pr_bot_agent.py <repo_path> <audit_file>")
        sys.exit(1)

    repo_path = Path(sys.argv[1])
    audit_file = Path(sys.argv[2])

    agent = PRBotAgent(repo_path)

    # Analyze violations
    violations = agent.analyze_audit_violations(audit_file)
    print(f"[PR Bot] Found {len(violations)} violations")

    # Generate fixes
    fixes = agent.generate_fixes(violations)
    print(f"[PR Bot] Generated {len(fixes)} fixes")

    # Create PR
    if fixes:
        success = agent.create_pr(fixes, violations)
        sys.exit(0 if success else 1)
    else:
        print("No fixes to apply")
        sys.exit(0)


if __name__ == "__main__":
    main()