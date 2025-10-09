#!/usr/bin/env python3
"""
Jade Interactive Chat Mode
Natural language interface for security operations
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
import json
import re

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-PLATFORM" / "james-config"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-AI"))

try:
    from model_manager import ModelManager
except ImportError:
    ModelManager = None

console = Console()

class JadeChat:
    """Interactive chat interface for Jade"""

    def __init__(self):
        self.console = Console()
        self.gp_copilot_root = Path(__file__).parent.parent.parent
        self.current_project = None

        # Initialize model manager for Qwen2.5
        if ModelManager:
            try:
                self.model_manager = ModelManager()
                self.has_llm = True
            except Exception as e:
                console.print(f"[yellow]⚠️  LLM not available: {e}[/yellow]")
                console.print("[yellow]   Falling back to pattern matching[/yellow]\n")
                self.has_llm = False
        else:
            self.has_llm = False

        # Command mapping patterns
        self.command_patterns = {
            # Project listing
            r"(list|show|display).*(project|repo)": {
                "command": "ls -d GP-PROJECTS/*/",
                "description": "List available projects"
            },

            # Environment/System queries
            r"(do we have|are there|show me).*(pod|container).*running": {
                "command": "kubectl get pods --all-namespaces",
                "description": "Show running pods"
            },
            r"(list|show|get).*(pod|pods)": {
                "command": "kubectl get pods --all-namespaces",
                "description": "List all pods"
            },
            r"(show|get|check).*(deploy|deployment)": {
                "command": "kubectl get deployments --all-namespaces",
                "description": "List deployments"
            },
            r"(show|get|check).*(service|svc)": {
                "command": "kubectl get services --all-namespaces",
                "description": "List services"
            },
            r"cluster.*status|kubernetes.*health": {
                "command": "kubectl get nodes && kubectl get pods --all-namespaces",
                "description": "Check cluster health"
            },

            # Scanning commands
            r"(scan|check|analyze|test|audit).*project.*quick": {
                "command": "PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH ./gp-security scan {project}",
                "description": "Quick security scan"
            },
            r"(scan|check|analyze).*my project": {
                "command": "PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH ./gp-security scan {project}",
                "description": "Security scan"
            },
            r"scan.*advice": {
                "command": "PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH ./gp-security advice {project}",
                "description": "Scan with AI advice"
            },
            r"(scan|check).*fix": {
                "command": "PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH ./gp-security scan-and-fix {project}",
                "description": "Scan and auto-fix"
            },

            # OPA/Policy commands
            r"(check|validate|test).*policy|opa": {
                "command": "PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py {project} terraform-security",
                "description": "OPA policy validation"
            },
            r"(terraform|tf).*plan.*validate": {
                "command": "python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/conftest_gate_agent.py {project}",
                "description": "Terraform plan validation"
            },

            # Automation agent commands
            r"run.*conftest.*agent|conftest.*gate": {
                "command": "python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/conftest_gate_agent.py {project}",
                "description": "Run Conftest Gate Agent"
            },
            r"run.*gatekeeper.*agent": {
                "command": "python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/gatekeeper_audit_agent.py",
                "description": "Run Gatekeeper Audit Agent"
            },
            r"run.*pr.*bot|create.*pr.*fix": {
                "command": "python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/pr_bot_agent.py {project}",
                "description": "Run PR Bot Agent"
            },
            r"run.*patch.*rollout|rollout.*agent": {
                "command": "python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/patch_rollout_agent.py {project}",
                "description": "Run Patch Rollout Agent"
            },
            r"run.*all.*agents|run.*agents": {
                "command": "./gp-security scan {project}",
                "description": "Run all security agents"
            },

            # GUI/Stats commands
            r"(open|launch|start|show).*(gui|interface|dashboard)": {
                "command": "cd GP-GUI && npm start",
                "description": "Launch Jade GUI"
            },
            r"(show|display).*(stats|statistics|status|health)": {
                "command": "jade stats",
                "description": "Show system statistics"
            },

            # Results viewing and analysis
            r"(show|view|display|list).*(result|finding|output|scan)": {
                "action": "show_results",
                "description": "View and summarize recent scan results"
            },
            r"(what|show).*(last|latest|recent).*scan": {
                "action": "show_latest_scan",
                "description": "Show latest scan with AI summary"
            },
            r"(read|analyze|summarize).*(scan|result).*": {
                "action": "analyze_scan_results",
                "description": "Read and analyze scan results with AI"
            },

            # Fixing commands
            r"(run|apply|execute).*(fix|fixer|remediat)": {
                "action": "run_fixer",
                "description": "Run appropriate fixer based on scan results"
            },
            r"fix.*(issue|finding|vulnerability)": {
                "action": "run_fixer",
                "description": "Fix issues found in scans"
            },

            # Help/Commands queries
            r"(what|show|list).*(command|can you do|capability|capabilit|feature|help)": {
                "action": "help",
                "description": "Show available commands and capabilities"
            },
            r"^(help|commands|\?)$": {
                "action": "help",
                "description": "Show help information"
            },

            # Summarize command (special action)
            r"summarize.*": {
                "action": "summarize",
                "description": "Create summary document"
            },

            # Query/Knowledge commands (RAG-powered knowledge chat)
            r"what (did|have) (we|i|you).*(scan|find|discover)": {
                "command": "jade query \"{question}\"",
                "description": "Query scan results"
            },
            r"(show|display|tell) me.*(issue|finding|vulnerability|problem)": {
                "command": "jade query \"{question}\"",
                "description": "Query knowledge base"
            },
            r"(how|what|why|when|where|who).*": {
                "command": "jade query \"{question}\"",
                "description": "Knowledge base query"
            },

            # Project selection
            r"(use|set|select).*(project|repo).*": {
                "action": "set_project",
                "description": "Set current project"
            },
        }

    def run(self):
        """Run interactive chat loop"""
        self.print_welcome()

        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

                if not user_input.strip():
                    continue

                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    console.print("[bold green]👋 Goodbye![/bold green]")
                    break

                # Process command
                self.process_input(user_input)

            except KeyboardInterrupt:
                console.print("\n[bold green]👋 Goodbye![/bold green]")
                break
            except EOFError:
                # Handle EOF gracefully (pipe/redirect/Ctrl+D)
                console.print("\n[bold green]👋 EOF detected. Goodbye![/bold green]")
                break
            except Exception as e:
                console.print(f"[bold red]❌ Error:[/bold red] {e}")

    def print_welcome(self):
        """Print welcome message"""
        welcome = """
# 🤖 Jade Interactive Chat

Welcome to Jade's conversational interface!

**Examples:**
- "I want to scan my project quickly"
- "Check my Terraform for policy violations"
- "What security issues did we find?"
- "Show me HIGH severity findings"
- "Open the GUI"

**Commands:**
- `exit` or `quit` to exit
- `set project GP-PROJECTS/MyApp` to set working project

**Current Project:** {project}
        """.format(project=self.current_project or "None (will prompt)")

        console.print(Panel(Markdown(welcome), border_style="cyan", title="[bold]Jade Chat[/bold]"))

    def process_input(self, user_input: str):
        """Process user input and execute appropriate command"""

        # First try LLM-based interpretation
        if self.has_llm:
            result = self.interpret_with_llm(user_input)
            if result:
                self.execute_command(result['command'], result.get('explanation', ''))
                return

        # Fall back to pattern matching
        result = self.interpret_with_patterns(user_input)
        if result:
            action = result.get('action')
            if action == 'set_project':
                self.handle_set_project(user_input)
            elif action == 'summarize':
                self.handle_summarize(user_input)
            elif action == 'help':
                self.show_help()
            elif action == 'show_results':
                self.handle_show_results()
            elif action == 'show_latest_scan':
                self.handle_show_latest_scan()
            elif action == 'analyze_scan_results':
                self.handle_analyze_scan_results(user_input)
            elif action == 'run_fixer':
                self.handle_run_fixer(user_input)
            else:
                self.execute_command(result['command'], result.get('description', ''))
        else:
            # Smart fallback: Route unrecognized input to RAG knowledge query
            self.handle_knowledge_query(user_input)

    def interpret_with_patterns(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Interpret user input using regex patterns"""
        user_input_lower = user_input.lower()

        for pattern, result in self.command_patterns.items():
            if re.search(pattern, user_input_lower):
                # Substitute project
                command = result.get('command', '')
                if '{project}' in command:
                    project = self.get_project_from_input(user_input) or self.current_project
                    if not project:
                        project = self.prompt_for_project()
                    command = command.format(project=project)
                elif '{question}' in command:
                    command = command.format(question=user_input)

                return {
                    'command': command,
                    'description': result.get('description', ''),
                    'action': result.get('action')
                }

        return None

    def interpret_with_llm(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Interpret user input using Qwen2.5 LLM"""
        try:
            prompt = f"""You are Jade, an AI security consultant. Interpret this user request and map it to a shell command.

User request: "{user_input}"

Current project: {self.current_project or "None"}

Available commands:
1. PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH ./gp-security scan <project> - Quick security scan
2. PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH ./gp-security advice <project> - Scan with AI advice
3. PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH ./gp-security scan-and-fix <project> - Scan and auto-fix
4. jade query "<question>" - Query knowledge base
5. jade stats - Show system statistics
6. PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python GP-CONSULTING-AGENTS/.../opa_scanner.py <project> terraform-security - OPA policy check

Respond with JSON:
{{
  "command": "the shell command to run",
  "explanation": "brief explanation of what this does",
  "confidence": 0.0 to 1.0
}}

If confidence < 0.5, return null.
"""

            response = self.model_manager.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.3
            )

            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                if result.get('confidence', 0) >= 0.5:
                    return result

        except Exception as e:
            console.print(f"[dim]LLM interpretation failed: {e}[/dim]")

        return None

    def execute_command(self, command: str, explanation: str = ""):
        """Execute shell command and display output"""
        console.print(f"\n[bold blue]🤖 Jade:[/bold blue] {explanation}")
        console.print(f"[dim]Running: {command}[/dim]\n")

        try:
            # Change to GP-copilot root directory
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.gp_copilot_root),
                capture_output=True,
                text=True,
                timeout=300
            )

            # Display output
            if result.stdout:
                console.print(result.stdout)
            if result.stderr:
                console.print(f"[yellow]{result.stderr}[/yellow]")

            if result.returncode != 0:
                console.print(f"[red]❌ Command failed with exit code {result.returncode}[/red]")
            else:
                console.print("[green]✅ Done[/green]")

        except subprocess.TimeoutExpired:
            console.print("[red]❌ Command timed out after 5 minutes[/red]")
        except Exception as e:
            console.print(f"[red]❌ Error executing command: {e}[/red]")

    def get_project_from_input(self, user_input: str) -> Optional[str]:
        """Extract project path from user input"""
        # Look for GP-PROJECTS/... pattern
        match = re.search(r'GP-PROJECTS/[\w\-_/]+', user_input)
        if match:
            return match.group()

        # Look for absolute paths
        match = re.search(r'/[\w\-_/]+', user_input)
        if match:
            return match.group()

        return None

    def prompt_for_project(self) -> str:
        """Prompt user for project path"""
        project = Prompt.ask(
            "[bold cyan]Which project?[/bold cyan]",
            default=self.current_project or "GP-PROJECTS/"
        )
        self.current_project = project
        return project

    def handle_set_project(self, user_input: str):
        """Handle setting current project"""
        project = self.get_project_from_input(user_input)
        if project:
            self.current_project = project
            console.print(f"[green]✅ Current project set to:[/green] {project}")
        else:
            self.prompt_for_project()

    def handle_show_results(self):
        """Show recent scan results with summary"""
        scans_dir = self.gp_copilot_root / "GP-DATA/active/scans"

        if not scans_dir.exists():
            console.print("[yellow]⚠️  Scans directory not found.[/yellow]")
            console.print(f"[yellow]   Expected: {scans_dir}[/yellow]")
            return

        # Find all *_latest.json files
        scan_files = list(scans_dir.glob("*_latest.json"))

        if not scan_files:
            console.print("\n[yellow]📊 No scan results found.[/yellow]")
            console.print("[yellow]   Run 'scan my project' first.[/yellow]\n")
            return

        console.print("\n[bold cyan]📊 Recent Scan Results:[/bold cyan]\n")

        total_issues = 0
        results_summary = []

        for scan_file in sorted(scan_files):
            try:
                with open(scan_file) as f:
                    data = json.load(f)

                scanner = scan_file.stem.replace("_latest", "")
                summary = data.get("summary", {})
                total = summary.get("total", 0)
                total_issues += total

                console.print(f"[bold green]{scanner.upper()}:[/bold green] {total} issues")

                # Show by severity if available
                by_severity = summary.get("by_severity", {})
                if by_severity:
                    for sev, count in sorted(by_severity.items(), reverse=True):
                        if count > 0:
                            if sev in ["CRITICAL", "HIGH"]:
                                color = "red"
                            elif sev == "MEDIUM":
                                color = "yellow"
                            else:
                                color = "blue"
                            console.print(f"  [{color}]{sev}:[/{color}] {count}")

                results_summary.append({
                    "scanner": scanner,
                    "total": total,
                    "by_severity": by_severity
                })

            except Exception as e:
                console.print(f"[dim]Error reading {scan_file.name}: {e}[/dim]")

        console.print(f"\n[bold]Total Issues Found: {total_issues}[/bold]")

        if total_issues > 0:
            console.print(f"\n[cyan]💡 Tip: Use 'run fixers' to automatically fix issues[/cyan]\n")
        else:
            console.print(f"\n[green]✅ No security issues found![/green]\n")

    def handle_show_latest_scan(self):
        """Show latest scan with detailed breakdown"""
        self.handle_show_results()

    def handle_analyze_scan_results(self, user_input: str):
        """Read and analyze scan results with AI"""
        console.print("\n[bold cyan]🤖 Analyzing Scan Results...[/bold cyan]\n")

        # First show the results
        self.handle_show_results()

        # If LLM available, provide AI insights
        if self.has_llm:
            scans_dir = self.gp_copilot_root / "GP-DATA/active/scans"
            scan_files = list(scans_dir.glob("*_latest.json"))

            if not scan_files:
                return

            console.print("\n[bold blue]🧠 AI Insights:[/bold blue]")
            console.print("[dim]Analyzing patterns and risks...[/dim]\n")

            # Collect all findings
            all_findings = []
            for scan_file in scan_files:
                try:
                    with open(scan_file) as f:
                        data = json.load(f)
                    findings = data.get("findings", [])[:5]  # Top 5 from each scanner
                    all_findings.extend(findings)
                except:
                    pass

            if all_findings:
                findings_text = "\n".join([str(f) for f in all_findings[:10]])

                prompt = f"""You are Jade, a security consultant. Analyze these security findings and provide insights:

{findings_text}

Provide:
1. Most critical issues (top 3)
2. Common patterns observed
3. Recommended next steps

Keep response concise (3-4 sentences)."""

                try:
                    analysis = self.model_manager.generate(prompt, max_tokens=300, temperature=0.3)
                    console.print(analysis)
                    console.print()
                except Exception as e:
                    console.print(f"[yellow]AI analysis unavailable: {e}[/yellow]\n")
        else:
            console.print("\n[yellow]💡 AI analysis requires LLM. Run with model loaded for insights.[/yellow]\n")

    def handle_run_fixer(self, user_input: str):
        """Run appropriate fixer based on scan results"""
        project = self.current_project or self.prompt_for_project()

        console.print(f"\n[bold cyan]🔧 Running Fixers for {project}...[/bold cyan]\n")

        scans_dir = self.gp_copilot_root / "GP-DATA/active/scans"

        if not scans_dir.exists():
            console.print("[yellow]⚠️  No scan results found. Run scans first.[/yellow]\n")
            return

        # Map scanners to fixers
        fixer_map = {
            "bandit": "GP-CONSULTING-AGENTS/fixers/bandit_fixer.py",
            "gitleaks": "GP-CONSULTING-AGENTS/fixers/gitleaks_fixer.py",
            "trivy": "GP-CONSULTING-AGENTS/fixers/trivy_fixer.py",
            "semgrep": "GP-CONSULTING-AGENTS/fixers/semgrep_fixer.py",
        }

        fixers_run = 0

        for scanner, fixer_path in fixer_map.items():
            scan_file = scans_dir / f"{scanner}_latest.json"

            if scan_file.exists():
                # Check if there are actually issues to fix
                try:
                    with open(scan_file) as f:
                        data = json.load(f)
                    total = data.get("summary", {}).get("total", 0)

                    if total == 0:
                        console.print(f"[dim]{scanner}: No issues to fix[/dim]")
                        continue

                except:
                    pass

                console.print(f"[green]▶ Running {scanner} fixer...[/green]")

                cmd = f"PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python {fixer_path} {scan_file} {project}"

                # Execute fixer
                try:
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        cwd=str(self.gp_copilot_root),
                        capture_output=True,
                        text=True,
                        timeout=120
                    )

                    if result.returncode == 0:
                        console.print(f"  [green]✅ {scanner} fixer completed[/green]")
                        if result.stdout:
                            # Show summary line if available
                            lines = result.stdout.strip().split('\n')
                            if lines:
                                console.print(f"  [dim]{lines[-1]}[/dim]")
                        fixers_run += 1
                    else:
                        console.print(f"  [yellow]⚠️  {scanner} fixer had warnings[/yellow]")

                except subprocess.TimeoutExpired:
                    console.print(f"  [red]❌ {scanner} fixer timed out[/red]")
                except Exception as e:
                    console.print(f"  [red]❌ Error: {e}[/red]")
            else:
                console.print(f"[dim]{scanner}: No scan results found[/dim]")

        console.print(f"\n[bold]Fixers Run: {fixers_run}[/bold]")

        if fixers_run > 0:
            console.print(f"[cyan]💡 Tip: Re-scan project to verify fixes[/cyan]\n")
        else:
            console.print(f"[yellow]No fixers were executed. Run scans first.[/yellow]\n")

    def handle_summarize(self, user_input: str):
        """Handle summarize command - saves summary to GP-DOCS/jadechat-summaries"""
        from datetime import datetime
        import json

        console.print("\n[bold cyan]📝 Creating Summary...[/bold cyan]")

        # Extract what to summarize from user input
        topic = user_input.replace("summarize", "").strip()

        if not topic:
            console.print("[yellow]💡 What would you like me to summarize?[/yellow]")
            console.print("[yellow]   Examples:[/yellow]")
            console.print("[yellow]   - summarize latest scan results[/yellow]")
            console.print("[yellow]   - summarize security findings[/yellow]")
            console.print("[yellow]   - summarize this conversation[/yellow]")
            return

        # Query RAG for relevant information
        console.print(f"[dim]Searching for: {topic}[/dim]")

        try:
            # Use simple RAG query
            gp_copilot_root = Path(__file__).resolve().parent.parent.parent
            sys.path.insert(0, str(gp_copilot_root / "GP-DATA"))

            from simple_rag_query import SimpleRAGQuery

            rag = SimpleRAGQuery()
            results = rag.query_all_collections(topic, n_results=10)

            # Generate summary content
            timestamp = datetime.now()
            filename = f"summary_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
            filepath = gp_copilot_root / "GP-DOCS" / "jadechat-summaries" / filename

            # Build summary document
            summary_content = f"""# Jade Chat Summary: {topic.title()}

**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Query:** {topic}
**Sources:** {len(results)} documents

---

## Summary

"""

            if results:
                summary_content += f"Found {len(results)} relevant documents:\n\n"

                for i, result in enumerate(results, 1):
                    collection = result.get('collection', 'unknown')
                    content = result.get('content', '')
                    metadata = result.get('metadata', {})

                    summary_content += f"### {i}. [{collection.upper()}]\n\n"

                    # Add metadata
                    if metadata:
                        if metadata.get('filename'):
                            summary_content += f"**File:** {metadata['filename']}\n\n"
                        elif metadata.get('scanner'):
                            summary_content += f"**Scanner:** {metadata['scanner']} | "
                            summary_content += f"**Severity:** {metadata.get('severity', 'N/A')} | "
                            summary_content += f"**Project:** {metadata.get('project', 'N/A')}\n\n"

                    # Add content (truncated)
                    max_length = 500
                    if len(content) > max_length:
                        summary_content += f"{content[:max_length]}...\n\n"
                    else:
                        summary_content += f"{content}\n\n"

                    summary_content += "---\n\n"

                # Add footer
                summary_content += f"""
## Notes

This summary was automatically generated by Jade based on RAG query results.

**Total Documents Analyzed:** {len(results)}
**Knowledge Collections Searched:** scan_findings, documentation, security_patterns, compliance_frameworks

---

*Generated by Jade Chat - GuidePoint Security Copilot*
"""
            else:
                summary_content += "No relevant information found in knowledge base.\n\n"
                summary_content += "Try:\n"
                summary_content += "- Running scans first\n"
                summary_content += "- Using different search terms\n"
                summary_content += "- Checking if auto-sync is running\n"

            # Write summary file
            with open(filepath, 'w') as f:
                f.write(summary_content)

            console.print(f"\n[green]✅ Summary saved to:[/green]")
            console.print(f"[cyan]   {filepath}[/cyan]")
            console.print(f"\n[dim]View with: cat {filepath}[/dim]\n")

        except Exception as e:
            console.print(f"[red]❌ Error creating summary: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")

    def handle_knowledge_query(self, user_input: str):
        """Route knowledge questions to RAG query system"""
        console.print(f"[dim]🧠 Searching knowledge base...[/dim]\n")

        try:
            # Use jade query command
            gp_copilot_root = self.gp_copilot_root
            sys.path.insert(0, str(gp_copilot_root / "GP-DATA"))

            from simple_rag_query import SimpleRAGQuery
            rag = SimpleRAGQuery()

            # Query all collections
            results = rag.query_all_collections(user_input, n_results=3)

            if results and len(results) > 0:
                console.print(f"[green]💡 Found {len(results)} relevant results:[/green]\n")

                for i, result in enumerate(results[:3], 1):
                    metadata = result.get('metadata', {})
                    content = result.get('content', '')[:300]  # First 300 chars

                    collection = metadata.get('collection', 'UNKNOWN')
                    source = metadata.get('source', metadata.get('filename', 'Unknown'))

                    console.print(f"[bold]{i}. [{collection.upper()}][/bold]")
                    console.print(f"   File: [cyan]{source}[/cyan]")
                    console.print(f"   {content}...")
                    console.print()
            else:
                console.print("[yellow]🤔 No direct matches found in knowledge base.[/yellow]")
                console.print("[yellow]   Try: 'scan my project', 'check policy', or 'help'[/yellow]")

        except Exception as e:
            console.print(f"[yellow]⚠️  Knowledge query unavailable: {e}[/yellow]")
            console.print("[yellow]   Try: 'scan my project', 'check policy', 'show results', or 'help'[/yellow]")

    def show_help(self):
        """Display help information with all available commands"""
        console.print("\n[bold cyan]🤖 Jade Chat - Available Commands[/bold cyan]\n")

        # Organize commands by category
        categories = {
            "Security Scans": [
                ("scan my project", "Run security scan (bandit, trivy, semgrep, gitleaks)"),
                ("scan [project-name]", "Scan specific project"),
                ("quick scan DVWA", "Quick scan example"),
            ],
            "Policy & Compliance": [
                ("check policy on my project", "Run OPA policy validation"),
                ("validate terraform plan", "Validate Terraform with conftest"),
                ("run conftest gate agent on [path]", "Run conftest gate agent"),
                ("run gatekeeper agent", "Run gatekeeper audit agent"),
            ],
            "Automation Agents": [
                ("run pr bot agent on [project]", "Create PR with fixes"),
                ("run patch rollout agent on [project]", "Deploy patches"),
                ("run all agents", "Run all security automation"),
            ],
            "Results & Reports": [
                ("show results", "View recent scan results"),
                ("show latest findings", "Display recent findings"),
                ("summarize [topic]", "Create summary document in GP-DOCS/jadechat-summaries"),
            ],
            "Project Management": [
                ("list projects", "Show available projects"),
                ("set project to [name]", "Set active project"),
                ("use project [name]", "Switch to project"),
            ],
            "System": [
                ("show stats", "Display system statistics"),
                ("launch gui", "Open Jade web interface"),
                ("help", "Show this help message"),
            ]
        }

        for category, commands in categories.items():
            console.print(f"[bold yellow]{category}:[/bold yellow]")
            for cmd, desc in commands:
                console.print(f"  [green]'{cmd}'[/green]")
                console.print(f"    → {desc}")
            console.print()

        console.print("[bold cyan]💡 Tips:[/bold cyan]")
        console.print("  • Natural language works! Try: 'I want to scan my project quickly'")
        console.print("  • Current project: [green]GP-PROJECTS/[/green][yellow]{self.current_project}[/yellow]")
        console.print("  • Use 'quit' or 'exit' to leave chat mode")
        console.print("  • All scans save to: [cyan]GP-DATA/active/scans/[/cyan]")
        console.print("  • Query knowledge: [cyan]jade query \"your question\"[/cyan]\n")


def main():
    """Entry point for jade chat command"""
    chat = JadeChat()
    chat.run()


if __name__ == "__main__":
    main()
