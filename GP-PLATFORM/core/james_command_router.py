#!/usr/bin/env python3
"""
James Command Router - Simple, Fast Security Commands
Routes user commands to appropriate security tools
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import re

# Add GP-copilot to path
GP_COPILOT_BASE = '/home/jimmie/linkops-industries/GP-copilot'
sys.path.append(GP_COPILOT_BASE)
sys.path.append(f'{GP_COPILOT_BASE}/james-config')  # Add james-config for gp_data_config
sys.path.append(str(Path(__file__).parent.parent))  # Add GP-PLATFORM to path

from gp_data_config import GPDataConfig

class JamesCommandRouter:
    def __init__(self):
        self.config = GPDataConfig()
        self.gp_copilot_dir = Path(GP_COPILOT_BASE)
        self.projects_dir = self.gp_copilot_dir / "GP-PROJECTS"

    def route_command(self, command: str) -> dict:
        """Route user command to appropriate action"""
        command = command.strip().lower()

        # Parse scan commands
        if command.startswith("scan "):
            project_name = command.replace("scan ", "").strip()
            return self.scan_project(project_name)

        # Parse status commands
        elif command in ["status", "projects", "list"]:
            return self.list_projects()

        # Parse help commands
        elif command in ["help", "commands"]:
            return self.show_help()

        else:
            return {
                "status": "error",
                "message": f"Unknown command: {command}",
                "suggestion": "Try 'help' for available commands"
            }

    def scan_project(self, project_name: str) -> dict:
        """Scan a specific project"""
        # Find project (case insensitive)
        project_path = None
        if (self.projects_dir / project_name).exists():
            project_path = self.projects_dir / project_name
        else:
            # Try case-insensitive search
            for p in self.projects_dir.iterdir():
                if p.is_dir() and p.name.lower() == project_name.lower():
                    project_path = p
                    break

        if not project_path:
            available = [p.name for p in self.projects_dir.iterdir() if p.is_dir()]
            return {
                "status": "error",
                "message": f"Project '{project_name}' not found",
                "available_projects": available
            }

        print(f"🎯 James scanning {project_path.name}...")

        try:
            # Run scanners via GP-CONSULTING-AGENTS
            cmd = [
                sys.executable,
                str(self.gp_copilot_dir / "GP-CONSULTING-AGENTS" / "scanners" / "run_all_scanners.py"),
                str(project_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                                    env={**subprocess.os.environ, 'PYTHONPATH': GP_COPILOT_BASE})

            if result.returncode == 0:
                # Parse the results from GP-DATA
                scans_dir = Path(self.config.get_scans_directory())
                if scans_dir.exists():
                    json_files = list(scans_dir.glob("*.json"))
                    if json_files:
                        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
                        with open(latest_file) as f:
                            scan_data = json.load(f)

                        return {
                            "status": "success",
                            "project": project_path.name,
                            "scan_results": scan_data,
                            "output": result.stdout,
                            "next_steps": self._suggest_next_steps(scan_data)
                        }

                return {
                    "status": "completed",
                    "project": project_path.name,
                    "output": result.stdout,
                    "message": "Scan completed but no detailed results found"
                }

            else:
                return {
                    "status": "error",
                    "project": project_path.name,
                    "message": "Scanner failed",
                    "error": result.stderr
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "project": project_path.name,
                "message": "Scan timed out after 60 seconds"
            }
        except Exception as e:
            return {
                "status": "error",
                "project": project_path.name,
                "message": f"Unexpected error: {str(e)}"
            }

    def list_projects(self) -> dict:
        """List available projects"""
        projects = []
        if self.projects_dir.exists():
            for p in self.projects_dir.iterdir():
                if p.is_dir():
                    projects.append({
                        "name": p.name,
                        "path": str(p),
                        "size": self._get_project_size(p)
                    })

        return {
            "status": "success",
            "projects": projects,
            "total_count": len(projects)
        }

    def show_help(self) -> dict:
        """Show available commands"""
        commands = {
            "scan <project>": "Run security scan on a project (e.g., 'scan Portfolio')",
            "status": "List all available projects",
            "projects": "List all available projects",
            "help": "Show this help message"
        }

        return {
            "status": "success",
            "available_commands": commands,
            "examples": [
                "scan Portfolio",
                "scan Terraform_CICD_Setup",
                "status",
                "help"
            ]
        }

    def _suggest_next_steps(self, scan_data: dict) -> list:
        """Suggest next steps based on scan results"""
        suggestions = []
        total_issues = scan_data.get("summary", {}).get("total_issues", 0)

        if total_issues == 0:
            suggestions.append("✅ No security issues found - project looks good!")
            suggestions.append("Consider running additional compliance checks")
        elif total_issues < 5:
            suggestions.append("🟡 Low risk - few issues found")
            suggestions.append("Review findings and apply fixes manually")
        elif total_issues < 20:
            suggestions.append("🟠 Medium risk - moderate issues found")
            suggestions.append("Consider running automated fixes")
            suggestions.append("Command: james fix <project>")
        else:
            suggestions.append("🔴 High risk - many issues found")
            suggestions.append("Priority: Review high-severity findings first")
            suggestions.append("Consider comprehensive security review")

        return suggestions

    def _get_project_size(self, project_path: Path) -> str:
        """Get project size estimate"""
        try:
            file_count = len(list(project_path.rglob("*")))
            if file_count < 50:
                return "Small"
            elif file_count < 200:
                return "Medium"
            else:
                return "Large"
        except:
            return "Unknown"

def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python james_command_router.py '<command>'")
        print("Examples:")
        print("  python james_command_router.py 'scan Portfolio'")
        print("  python james_command_router.py 'status'")
        print("  python james_command_router.py 'help'")
        sys.exit(1)

    command = " ".join(sys.argv[1:])
    router = JamesCommandRouter()
    result = router.route_command(command)

    # Pretty print the result
    print("\n" + "="*60)
    print("🤖 JAMES COMMAND RESULT")
    print("="*60)

    if result["status"] == "success":
        if "scan_results" in result:
            # Scan result
            scan_data = result["scan_results"]
            total_issues = scan_data.get("summary", {}).get("total_issues", 0)
            print(f"✅ Scan completed for {result['project']}")
            print(f"📊 Total Issues: {total_issues}")

            if "next_steps" in result:
                print("\n🎯 Recommended Next Steps:")
                for step in result["next_steps"]:
                    print(f"  {step}")

        elif "projects" in result:
            # Project list
            print(f"📁 Found {result['total_count']} projects:")
            for project in result["projects"]:
                print(f"  • {project['name']} ({project['size']})")

        elif "available_commands" in result:
            # Help
            print("📖 Available Commands:")
            for cmd, desc in result["available_commands"].items():
                print(f"  {cmd}: {desc}")

    elif result["status"] == "error":
        print(f"❌ Error: {result['message']}")
        if "available_projects" in result:
            print(f"Available projects: {', '.join(result['available_projects'])}")

    else:
        print(f"⚠️  {result['status'].upper()}: {result.get('message', 'Unknown result')}")

if __name__ == "__main__":
    main()