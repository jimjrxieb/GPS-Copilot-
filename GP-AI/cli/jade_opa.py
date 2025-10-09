#!/usr/bin/env python3
"""
Jade OPA Integration
Connects Jade to OPA policy scanning and auto-fixing
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Add config to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-PLATFORM" / "james-config"))
from gp_data_config import GPDataConfig

console = Console()

class JadeOPA:
    """Jade's OPA policy scanning and fixing interface"""

    def __init__(self):
        self.config = GPDataConfig()
        self.opa_bin = Path(__file__).parent.parent.parent / "bin" / "opa"
        self.policies_dir = Path(__file__).parent.parent.parent / "GP-CONSULTING" / "GP-POL-AS-CODE" / "1-POLICIES" / "opa"
        self.fixer_path = Path(__file__).parent.parent.parent / "GP-CONSULTING" / "GP-POL-AS-CODE" / "2-AUTOMATION" / "fixers" / "opa_fixer.py"

    def scan_project(self, project_path: str, save_results: bool = True) -> Dict[str, Any]:
        """
        Scan project with OPA policies

        Args:
            project_path: Path to project to scan
            save_results: Save results to GP-DATA

        Returns:
            Scan results dictionary
        """
        console.print(f"[cyan]🔍 Scanning {project_path} with OPA policies...[/cyan]\n")

        project_path = Path(project_path).resolve()
        if not project_path.exists():
            console.print(f"[red]❌ Project not found: {project_path}[/red]")
            return {"error": "Project not found"}

        # Find all YAML/Terraform files
        manifests = list(project_path.rglob("*.yaml")) + \
                   list(project_path.rglob("*.yml")) + \
                   list(project_path.rglob("*.tf"))

        console.print(f"[dim]Found {len(manifests)} manifest files[/dim]")

        # Scan each manifest
        all_violations = []
        for manifest in manifests:
            violations = self._scan_file(manifest)
            if violations:
                all_violations.extend(violations)

        # Build results
        results = {
            "scan_date": datetime.now().isoformat(),
            "project": str(project_path),
            "total_files": len(manifests),
            "total_violations": len(all_violations),
            "violations": all_violations
        }

        # Save results
        if save_results and all_violations:
            results_path = self._save_results(results, project_path.name)
            results["results_file"] = str(results_path)
            console.print(f"\n[green]💾 Results saved: {results_path}[/green]")

        # Display summary
        self._display_summary(results)

        return results

    def _scan_file(self, manifest_path: Path) -> List[Dict]:
        """Scan single file with OPA"""
        violations = []

        try:
            # Run OPA eval for each policy
            for policy_file in self.policies_dir.glob("*.rego"):
                cmd = [
                    str(self.opa_bin),
                    "eval",
                    "--data", str(policy_file),
                    "--input", str(manifest_path),
                    "--format", "json",
                    "data"
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    try:
                        data = json.loads(result.stdout)
                        # Extract violations from OPA output
                        violations.extend(self._parse_opa_output(data, manifest_path, policy_file.stem))
                    except json.JSONDecodeError:
                        pass

        except Exception as e:
            console.print(f"[dim]⚠️  Error scanning {manifest_path.name}: {e}[/dim]")

        return violations

    def _parse_opa_output(self, data: Dict, manifest_path: Path, policy_name: str) -> List[Dict]:
        """Parse OPA eval output to extract violations"""
        violations = []

        # OPA eval returns: {"result": [{"expressions": [{"value": {...}}]}]}
        if "result" not in data:
            return violations

        for result in data["result"]:
            for expr in result.get("expressions", []):
                value = expr.get("value", {})

                # Check for violations in various formats
                if isinstance(value, dict):
                    # Format 1: {policy_name: {"violations": [...]}}
                    for key, val in value.items():
                        if isinstance(val, dict) and "violations" in val:
                            for v in val["violations"]:
                                violations.append({
                                    "file": str(manifest_path.relative_to(Path.cwd())),
                                    "policy": policy_name,
                                    "message": v.get("msg", "Policy violation"),
                                    "severity": v.get("severity", "medium"),
                                    "resource": v.get("resource", manifest_path.name),
                                    "metadata": v
                                })

                    # Format 2: {"violations": [...]} directly
                    if "violations" in value:
                        for v in value["violations"]:
                            violations.append({
                                "file": str(manifest_path.relative_to(Path.cwd())),
                                "policy": policy_name,
                                "message": v.get("msg", "Policy violation"),
                                "severity": v.get("severity", "medium"),
                                "resource": v.get("resource", manifest_path.name),
                                "metadata": v
                            })

        return violations

    def _save_results(self, results: Dict, project_name: str) -> Path:
        """Save scan results to GP-DATA"""
        opa_scans_dir = self.config.get_opa_scans_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = opa_scans_dir / f"{project_name}_opa_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        return results_file

    def _display_summary(self, results: Dict):
        """Display scan results summary"""
        violations = results.get("violations", [])

        if not violations:
            console.print("\n[green]✅ No policy violations found![/green]")
            return

        # Count by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for v in violations:
            severity = v.get("severity", "medium").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1

        # Display summary table
        table = Table(title="OPA Policy Violations", box=box.ROUNDED)
        table.add_column("Severity", style="bold")
        table.add_column("Count", justify="right")

        if severity_counts["critical"] > 0:
            table.add_row("[red]CRITICAL[/red]", f"[red]{severity_counts['critical']}[/red]")
        if severity_counts["high"] > 0:
            table.add_row("[orange1]HIGH[/orange1]", f"[orange1]{severity_counts['high']}[/orange1]")
        if severity_counts["medium"] > 0:
            table.add_row("[yellow]MEDIUM[/yellow]", f"[yellow]{severity_counts['medium']}[/yellow]")
        if severity_counts["low"] > 0:
            table.add_row("[dim]LOW[/dim]", f"[dim]{severity_counts['low']}[/dim]")

        console.print()
        console.print(table)
        console.print()

        # Show top violations
        console.print("[bold]Top Violations:[/bold]")
        for i, v in enumerate(violations[:5], 1):
            severity_color = {"critical": "red", "high": "orange1", "medium": "yellow", "low": "dim"}.get(
                v.get("severity", "medium").lower(), "white"
            )
            console.print(f"  {i}. [{severity_color}]{v.get('severity', 'MEDIUM').upper()}[/{severity_color}]: {v.get('message', 'Unknown')}")
            console.print(f"     [dim]File: {v.get('file', 'unknown')}[/dim]")

        if len(violations) > 5:
            console.print(f"  [dim]... and {len(violations) - 5} more[/dim]")

    def fix_violations(self, results_path: str, project_path: str, auto_fix: bool = False) -> Dict[str, Any]:
        """
        Apply OPA fixer to violations

        Args:
            results_path: Path to OPA scan results JSON
            project_path: Path to project to fix
            auto_fix: If True, apply fixes without prompting

        Returns:
            Fix report dictionary
        """
        console.print(f"\n[cyan]🔧 Analyzing violations for auto-fix...[/cyan]\n")

        # Load scan results
        with open(results_path) as f:
            results = json.load(f)

        violations = results.get("violations", [])
        if not violations:
            console.print("[yellow]No violations to fix[/yellow]")
            return {"status": "no_violations"}

        # Categorize violations
        fixable, manual = self._categorize_violations(violations)

        console.print(f"[green]✅ {len(fixable)} violations can be auto-fixed[/green]")
        console.print(f"[yellow]⚠️  {len(manual)} need manual review[/yellow]\n")

        # Show what would be fixed
        if fixable:
            console.print("[bold]Fixable Violations:[/bold]")
            for i, v in enumerate(fixable[:10], 1):
                console.print(f"  {i}. {v.get('message', 'Unknown')}")
                console.print(f"     [dim]{v.get('file', 'unknown')}[/dim]")
            if len(fixable) > 10:
                console.print(f"  [dim]... and {len(fixable) - 10} more[/dim]")

        if manual:
            console.print(f"\n[bold]Manual Review Required:[/bold]")
            for i, v in enumerate(manual[:5], 1):
                console.print(f"  {i}. [{v.get('severity', 'medium').upper()}] {v.get('message', 'Unknown')}")
            if len(manual) > 5:
                console.print(f"  [dim]... and {len(manual) - 5} more[/dim]")

        # Prompt for fix if not auto_fix
        if not auto_fix:
            console.print()
            response = console.input(f"[bold cyan]Apply {len(fixable)} auto-fixes? (y/N):[/bold cyan] ")
            if response.lower() != 'y':
                console.print("[yellow]Skipping fixes[/yellow]")
                return {"status": "skipped"}

        # Run OPA fixer
        console.print("\n[cyan]🔧 Running OPA fixer...[/cyan]\n")

        try:
            # Set PYTHONPATH for james-config
            import os
            env = os.environ.copy()
            pythonpath = str(Path(__file__).parent.parent.parent / "GP-PLATFORM" / "james-config")
            env["PYTHONPATH"] = f"{pythonpath}:{env.get('PYTHONPATH', '')}"

            cmd = [
                sys.executable,
                str(self.fixer_path),
                results_path,
                project_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, env=env)

            console.print(result.stdout)

            if result.returncode == 0:
                console.print("\n[green]✅ Fixes applied successfully![/green]")
                return {"status": "success", "fixes_applied": len(fixable)}
            else:
                console.print(f"\n[red]❌ Fixer failed: {result.stderr}[/red]")
                return {"status": "failed", "error": result.stderr}

        except Exception as e:
            console.print(f"\n[red]❌ Error running fixer: {e}[/red]")
            return {"status": "error", "error": str(e)}

    def _categorize_violations(self, violations: List[Dict]) -> tuple:
        """Categorize violations into fixable vs manual review"""
        fixable = []
        manual = []

        # Keywords that indicate auto-fixable violations
        fixable_patterns = [
            "privileged", "runasnonroot", "runasuser", "readonly", "readonlyrootfilesystem",
            "resource", "limit", "request", "hostnetwork", "hostpath",
            "label", "namespace", "imagepullpolicy", "latest"
        ]

        # Keywords that require manual review
        manual_patterns = [
            "rbac", "wildcard", "clusterrole", "rolebinding",
            "secret", "hardcoded", "encryption"
        ]

        for v in violations:
            message = v.get("message", "").lower()
            policy = v.get("policy", "").lower()

            # Check if manual review required
            if any(pattern in message or pattern in policy for pattern in manual_patterns):
                manual.append(v)
            # Check if auto-fixable
            elif any(pattern in message or pattern in policy for pattern in fixable_patterns):
                fixable.append(v)
            else:
                # Default to manual review if uncertain
                manual.append(v)

        return fixable, manual

    def get_latest_scan(self, project_name: Optional[str] = None) -> Optional[Path]:
        """Get latest OPA scan results for a project"""
        opa_scans_dir = self.config.get_opa_scans_directory()

        if project_name:
            scans = list(opa_scans_dir.glob(f"{project_name}_opa_*.json"))
        else:
            scans = list(opa_scans_dir.glob("*_opa_*.json"))

        if not scans:
            return None

        return max(scans, key=lambda p: p.stat().st_mtime)


def main():
    """CLI entry point for testing"""
    import click

    @click.group()
    def cli():
        """Jade OPA Integration"""
        pass

    @cli.command()
    @click.argument('project_path')
    def scan(project_path):
        """Scan project with OPA policies"""
        jade_opa = JadeOPA()
        jade_opa.scan_project(project_path)

    @cli.command()
    @click.argument('results_path')
    @click.argument('project_path')
    @click.option('--auto-fix', is_flag=True, help='Apply fixes without prompting')
    def fix(results_path, project_path, auto_fix):
        """Fix OPA violations"""
        jade_opa = JadeOPA()
        jade_opa.fix_violations(results_path, project_path, auto_fix)

    cli()


if __name__ == "__main__":
    main()
