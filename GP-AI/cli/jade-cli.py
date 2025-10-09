#!/usr/bin/env python3
"""
Jade CLI - Unified Security Workflow Interface
🧠 Brain (GP-AI) + 💪 Muscle (GP-CONSULTING-AGENTS)
"""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # GP-copilot root
sys.path.insert(0, str(Path(__file__).parent.parent))  # GP-AI

try:
    from jade_enhanced import JadeEnhanced
except ImportError:
    try:
        from GP_AI.jade_enhanced import JadeEnhanced
    except ImportError:
        # Fallback - create minimal JadeEnhanced
        JadeEnhanced = None

console = Console()

@click.group()
@click.version_option(version="2.0.0", prog_name="Jade AI Security Consultant")
def cli():
    """
    🤖 Jade - AI Security Consultant CLI

    Brain (GP-AI) orchestrates Muscle (GP-CONSULTING-AGENTS) for
    comprehensive security analysis and remediation.

    Commands:
      chat    - Interactive chat mode with natural language
      agent   - Agentic workflow (LangGraph + RAG + specialized agents)
      query   - Query RAG knowledge base
      learn   - Dynamic learning (sync new knowledge from unprocessed files)
      analyze - Run security workflow
      projects - List available projects
    """
    pass

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--workflow', type=click.Choice(['scan', 'fix', 'full']), default='scan',
              help='Workflow type: scan (security analysis), fix (apply remediations), full (complete pipeline)')
@click.option('--format', type=click.Choice(['table', 'json', 'summary']), default='summary',
              help='Output format')
def analyze(project_path: str, workflow: str, format: str):
    """
    Analyze project with security workflow

    Examples:
        jade analyze /path/to/project --workflow scan
        jade analyze GP-PROJECTS/MyApp --workflow full
    """
    console.print(Panel.fit(
        f"[bold cyan]Jade Security Analysis[/bold cyan]\n"
        f"Project: [green]{project_path}[/green]\n"
        f"Workflow: [yellow]{workflow}[/yellow]",
        border_style="cyan"
    ))

    try:
        jade = JadeEnhanced()

        with console.status("[bold yellow]Running security analysis..."):
            results = jade.execute_security_workflow(project_path, workflow)

        # Display results based on format
        if format == "json":
            import json
            console.print_json(json.dumps(results, indent=2))
        elif format == "table":
            _display_table_results(results)
        else:  # summary
            _display_summary_results(results)

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.argument('question')
@click.option('--project', help='Project context for the query')
def query(question: str, project: str = None):
    """
    Query Jade's security knowledge (RAG)

    Examples:
        jade query "How do I prevent SQL injection in Python?"
        jade query "What did we scan today?"
        jade query "Show me critical findings" --project DVWA
    """
    console.print(Panel.fit(
        f"[bold cyan]Jade Knowledge Query[/bold cyan]\n"
        f"Question: [green]{question}[/green]",
        border_style="cyan"
    ))

    try:
        # Use simple RAG query (no heavy dependencies)
        gp_copilot_root = Path(__file__).resolve().parent.parent.parent
        sys.path.insert(0, str(gp_copilot_root / "GP-DATA"))

        from simple_rag_query import SimpleRAGQuery

        with console.status("[bold yellow]Searching knowledge base..."):
            rag = SimpleRAGQuery()
            results = rag.query_all_collections(question, n_results=5)

        if results:
            console.print(f"\n[bold blue]💡 Found {len(results)} relevant results:[/bold blue]\n")

            for i, result in enumerate(results, 1):
                collection = result.get('collection', 'unknown')
                content = result.get('content', '')
                metadata = result.get('metadata', {})

                # Display result with metadata
                console.print(f"[bold yellow]{i}. [{collection.upper()}][/bold yellow]")

                # Show metadata if available
                if metadata:
                    meta_parts = []
                    if metadata.get('scanner'):
                        meta_parts.append(f"Scanner: {metadata['scanner']}")
                    if metadata.get('severity'):
                        meta_parts.append(f"Severity: {metadata['severity']}")
                    if metadata.get('project'):
                        meta_parts.append(f"Project: {metadata['project']}")
                    if metadata.get('filename'):
                        meta_parts.append(f"File: {metadata['filename']}")

                    if meta_parts:
                        console.print(f"   [dim]{' | '.join(meta_parts)}[/dim]")

                # Show content (truncated)
                max_length = 400
                if len(content) > max_length:
                    console.print(f"   {content[:max_length]}...")
                else:
                    console.print(f"   {content}")

                console.print()  # Blank line
        else:
            console.print("[yellow]No results found in knowledge base.[/yellow]")
            console.print("[yellow]Tip: Try running scans first, or check if auto-sync is running.[/yellow]")

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)

@cli.command()
@click.option('--watch', is_flag=True, help='Start file watcher daemon')
def learn(watch: bool):
    """
    Dynamic learning - Sync new knowledge from GP-RAG/unprocessed/

    Drop files into GP-RAG/unprocessed/ subdirectories:
      • client-docs/     - Client documentation
      • compliance/      - Compliance policies
      • policies/        - Security policies
      • scan-results/    - Scan outputs
      • security-docs/   - Security guides

    Jade will automatically chunk, categorize, and index the knowledge.

    Examples:
        jade learn              # One-time sync
        jade learn --watch      # Start file watcher daemon
    """
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-RAG"))
        from dynamic_learner import DynamicLearner, watch_mode
    except ImportError as e:
        console.print(f"[red]❌ Error loading dynamic learner: {e}[/red]")
        console.print("[yellow]Install: pip install watchdog[/yellow]")
        sys.exit(1)

    if watch:
        # Start file watcher
        watch_mode()
    else:
        # One-time sync
        with console.status("[bold yellow]Learning new knowledge..."):
            learner = DynamicLearner()
            total = learner.sync_all_unprocessed()

        console.print(f"\n[green]✅ Processed {total} files[/green]")

        # Show stats
        stats = learner.get_stats()
        console.print(f"\n[bold cyan]📊 Learning Statistics:[/bold cyan]")
        console.print(f"   Total chunks: [green]{stats['total_chunks']}[/green]")

        if stats['categories']:
            console.print(f"\n   By category:")
            for cat, count in stats['categories'].items():
                console.print(f"     • {cat}: [cyan]{count}[/cyan] chunks")

        console.print(f"\n[dim]💡 Try: jade query \"your question about the new knowledge\"[/dim]\n")

@cli.command()
@click.argument('target_path')
@click.option('--scanners', '-s', default='bandit,trivy,semgrep', help='Comma-separated list of scanners')
@click.option('--create-pr', is_flag=True, help='Automatically create PR with fixes')
@click.option('--dry-run', is_flag=True, help='Show what would be fixed without applying')
def remediate(target_path: str, scanners: str, create_pr: bool, dry_run: bool):
    """
    Scan and auto-remediate security vulnerabilities

    Workflow:
      1. Scan target with specified scanners
      2. Analyze findings and generate fixes
      3. Apply fixes to code (or show with --dry-run)
      4. Optionally create PR with fixes (--create-pr)

    Examples:
        jade remediate /project                              # Scan + fix
        jade remediate /project --scanners trivy,gitleaks    # Specific scanners
        jade remediate /project --create-pr                  # Auto-create PR
        jade remediate /project --dry-run                    # Preview fixes
    """
    console.print(Panel.fit(
        "[bold cyan]🔧 Jade Remediation Engine[/bold cyan]",
        border_style="cyan"
    ))

    target = Path(target_path)
    if not target.exists():
        console.print(f"[red]❌ Target not found: {target_path}[/red]")
        sys.exit(1)

    console.print(f"\n[bold]Target:[/bold] {target}")
    console.print(f"[bold]Scanners:[/bold] {scanners}")

    if dry_run:
        console.print("[yellow]🔍 Dry run mode - no changes will be applied[/yellow]\n")

    # Step 1: Scan
    with console.status("[bold yellow]Scanning for vulnerabilities...[/bold yellow]"):
        scan_results = {}
        for scanner in scanners.split(','):
            scanner = scanner.strip()
            try:
                scanner_module = Path(__file__).parent.parent.parent / "GP-CONSULTING-AGENTS" / "scanners" / f"{scanner}_scanner.py"
                if scanner_module.exists():
                    # Import and run scanner
                    sys.path.insert(0, str(scanner_module.parent))
                    scanner_class_name = f"{scanner.capitalize()}Scanner"

                    # Dynamic import
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(scanner, scanner_module)
                    scanner_mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(scanner_mod)

                    scanner_instance = getattr(scanner_mod, scanner_class_name)()
                    results = scanner_instance.scan(str(target))
                    scan_results[scanner] = results

                    total = results.get('summary', {}).get('total', 0)
                    console.print(f"  ✓ {scanner}: [yellow]{total}[/yellow] findings")
            except Exception as e:
                console.print(f"  ✗ {scanner}: [red]{e}[/red]")

    # Count total findings
    total_findings = sum(
        r.get('summary', {}).get('total', 0)
        for r in scan_results.values()
    )

    if total_findings == 0:
        console.print("\n[green]✅ No vulnerabilities found! Project is clean.[/green]")
        return

    console.print(f"\n[yellow]Found {total_findings} total findings[/yellow]")

    # Step 2: Generate fixes
    console.print("\n[bold]Generating fixes...[/bold]")

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-CONSULTING-AGENTS" / "fixers"))
        from apply_all_fixes import apply_all_fixes

        # Save scan results to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(scan_results, f)
            scan_file = f.name

        if dry_run:
            console.print("[yellow]Dry run - would apply fixes from:[/yellow]")
            console.print(f"  • UnifiedTerraformFixer")
            console.print(f"  • PythonFixer")
            console.print(f"  • NPMAuditFixer")
            console.print(f"  • TrivyFixer")
            console.print(f"\n[dim]Run without --dry-run to apply fixes[/dim]")
        else:
            fix_results = apply_all_fixes(scan_file, str(target))

            # Show summary
            total_fixes = sum(
                r.get('summary', {}).get('total_fixes', 0)
                for r in fix_results.get('results', {}).values()
                if 'error' not in r
            )

            console.print(f"\n[green]✅ Applied {total_fixes} fixes[/green]")

            # Step 3: Create PR if requested
            if create_pr and total_fixes > 0:
                console.print("\n[bold]Creating pull request...[/bold]")

                # Use git commands to create PR
                try:
                    import subprocess
                    from datetime import datetime

                    branch_name = f"jade-auto-fix-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

                    # Create branch
                    subprocess.run(['git', 'checkout', '-b', branch_name], cwd=target, check=True)

                    # Add files
                    subprocess.run(['git', 'add', '.'], cwd=target, check=True)

                    # Commit
                    commit_msg = f"""🤖 Jade auto-fix: {total_fixes} security vulnerabilities

Findings addressed:
{chr(10).join([f"• {scanner}: {results.get('summary', {}).get('total', 0)} issues" for scanner, results in scan_results.items()])}

Fixes applied:
{chr(10).join([f"• {fixer}" for fixer in fix_results.get('fix_info', {}).get('fixers', [])])}

Generated by Jade Remediation Engine
"""
                    subprocess.run(['git', 'commit', '-m', commit_msg], cwd=target, check=True)

                    # Push (assuming remote is configured)
                    subprocess.run(['git', 'push', '-u', 'origin', branch_name], cwd=target, check=True)

                    console.print(f"[green]✅ Branch created: {branch_name}[/green]")
                    console.print(f"[dim]Use 'gh pr create' to open pull request[/dim]")

                except subprocess.CalledProcessError as e:
                    console.print(f"[yellow]⚠️  Could not create PR: {e}[/yellow]")
                    console.print("[dim]Changes have been applied locally[/dim]")

        # Cleanup
        Path(scan_file).unlink(missing_ok=True)

    except Exception as e:
        console.print(f"[red]❌ Remediation failed: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)

@cli.command()
@click.argument('resource_type', required=False)
@click.option('--namespace', '-n', help='Kubernetes namespace to audit')
@click.option('--policy', '-p', default='all', help='Policy to check (default: all)')
def audit(resource_type: str, namespace: str, policy: str):
    """
    Audit Kubernetes cluster or Terraform against OPA policies

    Supports:
      • Live Kubernetes cluster (via kubectl)
      • Terraform plans (JSON format)
      • Docker images

    Examples:
        jade audit                                    # Audit entire cluster
        jade audit pod --namespace production         # Audit pods in namespace
        jade audit terraform --policy cis-benchmark   # Audit Terraform
    """
    console.print(Panel.fit(
        "[bold cyan]🔍 Jade Audit Engine[/bold cyan]",
        border_style="cyan"
    ))

    if not resource_type:
        resource_type = "cluster"

    console.print(f"\n[bold]Audit Type:[/bold] {resource_type}")
    console.print(f"[bold]Policy:[/bold] {policy}")

    try:
        if resource_type in ['cluster', 'pod', 'deployment', 'service']:
            # Kubernetes audit
            console.print("\n[yellow]🔍 Auditing Kubernetes resources...[/yellow]\n")

            import subprocess

            # Build kubectl command
            cmd = ['kubectl', 'get', resource_type if resource_type != 'cluster' else 'all']
            if namespace:
                cmd.extend(['-n', namespace])
            cmd.extend(['-o', 'json'])

            with console.status("[bold yellow]Fetching resources from cluster...[/bold yellow]"):
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0:
                    console.print(f"[red]❌ kubectl failed: {result.stderr}[/red]")
                    sys.exit(1)

                resources = json.loads(result.stdout)

            # Run OPA evaluation
            opa_policies_dir = Path(__file__).parent.parent.parent / "GP-CONSULTING-AGENTS" / "GP-POL-AS-CODE" / "1-POLICIES"

            # Save resources to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(resources, f)
                resources_file = f.name

            # Find policy file
            if policy == 'all':
                policy_files = list(opa_policies_dir.glob('*.rego'))
            else:
                policy_files = list(opa_policies_dir.glob(f'*{policy}*.rego'))

            if not policy_files:
                console.print(f"[red]❌ No policies found matching: {policy}[/red]")
                sys.exit(1)

            violations = []

            for policy_file in policy_files:
                with console.status(f"[bold yellow]Checking {policy_file.stem}...[/bold yellow]"):
                    opa_cmd = [
                        'opa', 'eval',
                        '--data', str(policy_file),
                        '--input', resources_file,
                        '--format', 'pretty',
                        'data'
                    ]

                    opa_result = subprocess.run(opa_cmd, capture_output=True, text=True)

                    if 'deny' in opa_result.stdout or 'violation' in opa_result.stdout:
                        violations.append({
                            'policy': policy_file.stem,
                            'output': opa_result.stdout
                        })

            # Cleanup
            Path(resources_file).unlink(missing_ok=True)

            # Report
            if violations:
                console.print(f"\n[red]❌ Found {len(violations)} policy violations:[/red]\n")
                for v in violations:
                    console.print(f"[bold red]Policy:[/bold red] {v['policy']}")
                    console.print(f"[dim]{v['output']}[/dim]\n")
            else:
                console.print("\n[green]✅ No violations found! Cluster is compliant.[/green]")

        elif resource_type == 'terraform':
            console.print("\n[yellow]🔍 Auditing Terraform configuration...[/yellow]\n")
            console.print("[dim]Terraform audit coming soon[/dim]")

        else:
            console.print(f"[red]❌ Unknown resource type: {resource_type}[/red]")
            console.print("[dim]Supported: cluster, pod, deployment, service, terraform[/dim]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]❌ Audit failed: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)

@cli.command()
def stats():
    """
    Show Jade system statistics

    Displays:
        - Knowledge base size
        - Available tools
        - System health
    """
    console.print(Panel.fit(
        "[bold cyan]Jade System Statistics[/bold cyan]",
        border_style="cyan"
    ))

    try:
        # Check if JadeEnhanced is available
        if JadeEnhanced is None:
            console.print("[yellow]⚠️  Jade AI engine not available[/yellow]")
            console.print("[yellow]   Running in tools-only mode[/yellow]\n")
            jade = None
        else:
            jade = JadeEnhanced()

        # RAG stats (if available)
        console.print("\n[bold blue]📚 Knowledge Base:[/bold blue]")
        if jade and hasattr(jade, 'rag_engine'):
            try:
                rag_stats = jade.rag_engine.get_stats()
                console.print(f"  Documents: [green]{rag_stats.get('total_documents', 0):,}[/green]")
                console.print(f"  Collections: [green]{rag_stats.get('collections', 0)}[/green]")
            except:
                console.print("  [yellow]Knowledge base not initialized[/yellow]")
        else:
            # Fallback: check ChromaDB directly
            try:
                sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-DATA"))
                from simple_rag_query import SimpleRAGQuery
                rag = SimpleRAGQuery()
                collections = rag.client.list_collections()
                console.print(f"  Collections: [green]{len(collections)}[/green]")
            except:
                console.print("  [yellow]Knowledge base not initialized[/yellow]")

        # Security Tools
        console.print("\n[bold blue]🔧 Security Tools:[/bold blue]")
        tools = {
            "bandit": "Python SAST",
            "trivy": "Container/IaC scanning",
            "semgrep": "Multi-language SAST",
            "gitleaks": "Secrets detection",
            "checkov": "IaC security",
            "tfsec": "Terraform scanning",
            "opa": "Policy enforcement",
            "kubescape": "Kubernetes security"
        }

        for tool, desc in tools.items():
            tool_path = Path(__file__).parent.parent.parent / "bin" / tool
            if tool_path.exists() or tool_path.is_symlink():
                console.print(f"  ✓ [green]{tool:12}[/green] - {desc}")
            else:
                console.print(f"  ✗ [red]{tool:12}[/red] - {desc} (not installed)")

        # Expertise domains (if available)
        console.print("\n[bold blue]🎓 Expertise Domains:[/bold blue]")
        if jade and hasattr(jade, 'expertise'):
            for domain, desc in jade.expertise.items():
                console.print(f"  • {domain.replace('_', ' ').title()}")
        else:
            console.print("  [yellow]Jade AI engine not loaded[/yellow]")

        console.print("\n[green]✅ Jade system operational[/green]")

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def scan(project_path: str):
    """
    Quick security scan (scan-only workflow)

    Alias for: jade analyze PROJECT --workflow scan
    """
    ctx = click.get_current_context()
    ctx.invoke(analyze, project_path=project_path, workflow='scan', format='summary')

@cli.command("scan-policy")
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--fix', is_flag=True, help='Auto-fix violations after scan')
@click.option('--auto', is_flag=True, help='Apply fixes without prompting')
def scan_policy(project_path: str, fix: bool, auto: bool):
    """
    Scan project with OPA policies

    Examples:
        jade scan-policy kubernetes-goat
        jade scan-policy kubernetes-goat --fix
        jade scan-policy kubernetes-goat --fix --auto
    """
    from jade_opa import JadeOPA

    jade_opa = JadeOPA()

    # Run scan
    results = jade_opa.scan_project(project_path, save_results=True)

    if results.get("error"):
        return

    # If --fix flag, run fixer
    if fix and results.get("results_file"):
        jade_opa.fix_violations(
            results["results_file"],
            project_path,
            auto_fix=auto
        )

@cli.command("fix-policy")
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--results', type=click.Path(exists=True), help='Path to scan results JSON')
@click.option('--auto', is_flag=True, help='Apply fixes without prompting')
def fix_policy(project_path: str, results: str, auto: bool):
    """
    Fix OPA policy violations

    If --results not provided, uses latest scan for project.

    Examples:
        jade fix-policy kubernetes-goat
        jade fix-policy kubernetes-goat --results scan_results.json
        jade fix-policy kubernetes-goat --auto
    """
    from jade_opa import JadeOPA

    jade_opa = JadeOPA()

    # Find results file
    if not results:
        project_name = Path(project_path).name
        results_path = jade_opa.get_latest_scan(project_name)
        if not results_path:
            console.print(f"[red]❌ No scan results found for {project_name}[/red]")
            console.print(f"[yellow]Run: jade scan-policy {project_path}[/yellow]")
            return
    else:
        results_path = results

    # Run fixer
    jade_opa.fix_violations(results_path, project_path, auto_fix=auto)

@cli.command()
@click.argument('question', required=False)
def agent(question: str = None):
    """
    Agentic workflow - LangGraph + RAG + specialized agents

    Uses LangGraph to orchestrate multi-step reasoning with:
    - RAG knowledge base queries
    - Specialized troubleshooting agents
    - Multi-domain support (Kubernetes, Terraform, OPA, etc.)

    Examples:
        jade agent "kubernetes pod crashlooping"
        jade agent "terraform state lock error"
        jade agent "how to fix OPA policy errors"

    If no question provided, enters interactive mode.
    """
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
        from jade_orchestrator import JadeOrchestrator
    except ImportError as e:
        console.print(f"[red]❌ Error loading orchestrator: {e}[/red]")
        console.print("[yellow]Install: pip install langgraph langchain-core[/yellow]")
        sys.exit(1)

    if not question:
        # Interactive mode
        console.print("[bold cyan]🤖 Jade Agentic Mode[/bold cyan]")
        console.print("Ask me anything about security, troubleshooting, or infrastructure!\n")
        console.print("[dim]Examples:[/dim]")
        console.print("[dim]  - kubernetes pod crashlooping[/dim]")
        console.print("[dim]  - terraform state lock error[/dim]")
        console.print("[dim]  - how to fix secrets in code[/dim]\n")

        orchestrator = JadeOrchestrator()

        while True:
            try:
                question = click.prompt("You", type=str)
                if question.lower() in ["exit", "quit", "bye"]:
                    console.print("[green]👋 Goodbye![/green]")
                    break

                result = orchestrator.process(question)

                # Display conversation
                for msg in result["conversation"]:
                    if msg["role"] == "ai":
                        console.print(f"[cyan]Jade:[/cyan] {msg['content']}\n")

            except (KeyboardInterrupt, EOFError):
                console.print("\n[green]👋 Goodbye![/green]")
                break
    else:
        # One-shot mode
        with console.status("[bold yellow]Processing with Jade orchestrator..."):
            orchestrator = JadeOrchestrator()
            result = orchestrator.process(question)

        # Display result
        console.print(f"\n[bold cyan]🎯 Intent:[/bold cyan] {result['intent']}")
        console.print(f"[bold cyan]🏷️  Domain:[/bold cyan] {result['domain']}")
        console.print(f"[bold cyan]📚 Knowledge:[/bold cyan] {result['knowledge_count']} documents")
        console.print(f"[bold cyan]🤖 Agent:[/bold cyan] {result['agent_used']}\n")

        if result['analysis']:
            console.print(result['analysis'])

        if result['suggestions']:
            console.print("\n[bold yellow]💡 Suggestions:[/bold yellow]")
            for i, s in enumerate(result['suggestions'], 1):
                console.print(f"  {i}. {s}")

        if result['commands']:
            console.print("\n[bold yellow]🔧 Commands:[/bold yellow]")
            for cmd in result['commands']:
                console.print(f"  [dim]{cmd}[/dim]")

        console.print()

@cli.command()
def chat():
    """
    Interactive chat mode - Natural language interface

    Examples:
        > "I want to scan my project quickly"
        > "Check my Terraform for policy violations"
        > "What security issues did we find?"

    Chat mode uses pattern matching to interpret natural language and execute commands.
    For advanced multi-step reasoning, use 'jade agent' instead.
    """
    try:
        from jade_chat import JadeChat
    except ImportError:
        # Try relative import
        sys.path.insert(0, str(Path(__file__).parent))
        from jade_chat import JadeChat

    chat_instance = JadeChat()
    chat_instance.run()

@cli.command()
def projects():
    """
    List available projects in GP-PROJECTS/
    """
    from pathlib import Path

    # Resolve symlinks to get actual file location
    actual_file = Path(__file__).resolve()
    # Go up from GP-AI/cli/jade-cli.py to GP-copilot root
    gp_copilot_root = actual_file.parent.parent.parent
    projects_dir = gp_copilot_root / "GP-PROJECTS"

    if not projects_dir.exists():
        console.print("[red]GP-PROJECTS directory not found[/red]")
        return

    projects = sorted([p.name for p in projects_dir.iterdir() if p.is_dir()])

    console.print(f"\n[bold cyan]📁 Available Projects ({len(projects)}):[/bold cyan]\n")

    for i, project in enumerate(projects, 1):
        project_path = projects_dir / project
        # Try to get project type
        if (project_path / "main.tf").exists():
            proj_type = "Terraform"
        elif (project_path / "kubernetes").exists() or (project_path / "k8s").exists():
            proj_type = "Kubernetes"
        elif (project_path / "requirements.txt").exists():
            proj_type = "Python"
        elif (project_path / "package.json").exists():
            proj_type = "Node.js"
        else:
            proj_type = "Unknown"

        console.print(f"  {i}. [green]{project}[/green] ({proj_type})")

    console.print(f"\n[dim]Scan with: jade scan GP-PROJECTS/{{project}}[/dim]")
    console.print(f"[dim]Or use chat: jade chat[/dim]\n")

@cli.command("explain-gha")
@click.argument('repo')
@click.argument('run_id')
@click.option('--output', '-o', help='Save detailed results to JSON file', metavar='FILE')
@click.option('--brief', '-b', is_flag=True, help='Show only AI explanation (skip detailed summary)')
def explain_gha(repo: str, run_id: str, output: str, brief: bool):
    """
    Explain GitHub Actions security scan results with AI

    Fetches workflow artifacts, parses scanner outputs, and provides
    AI-powered explanation prioritized by risk for junior engineers.

    Examples:
        jade explain-gha owner/repo 1234567890
        jade explain-gha guidepoint/cloud-project 9876543210 -o analysis.json
        jade explain-gha myorg/myrepo 5555555555 --brief
    """
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "cli"))
        from jade_explain_gha import JadeGHAExplainer

        explainer = JadeGHAExplainer()
        result = explainer.explain(repo, run_id, output)

        # Exit with error code if critical/high findings
        severity_counts = result['summary']['severity_counts']
        if severity_counts['critical'] > 0 or severity_counts['high'] > 0:
            console.print("\n[red]⚠️  Critical or high severity issues found[/red]")
            sys.exit(1)

    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(2)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Analysis interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        import traceback
        if '--debug' in sys.argv:
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(3)

@cli.command("analyze-gha")
@click.argument('repo')
@click.argument('run_id')
def analyze_gha(repo: str, run_id: str):
    """
    Complete GitHub Actions security analysis with discrepancy detection

    Fetches artifacts, parses all scanners, detects security gate discrepancies,
    generates fix guides, and saves everything to GP-DATA structure.

    This command:
    - Downloads all security scan artifacts
    - Parses results from 15+ scanners (KICS, Trivy, Bandit, etc.)
    - Detects discrepancies between security gate and actual findings
    - Generates detailed fix guides for HIGH/CRITICAL issues
    - Saves results to GP-DATA/active/
    - Logs evidence to jade-gha-evidence.jsonl

    Examples:
        jade analyze-gha owner/repo 1234567890
        jade analyze-gha jimjrxieb/CLOUD-project 18300191954
    """
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "GP-AI" / "cli"))
        from jade_analyze_gha import JadeGHAAnalyzer

        analyzer = JadeGHAAnalyzer()
        result = analyzer.analyze(repo, run_id)

        # Exit with error code if critical/high findings
        severity_counts = result['summary']['severity_counts']
        if severity_counts['critical'] > 0 or severity_counts['high'] > 0:
            console.print("\n[red]⚠️  Critical or high severity issues found[/red]")
            sys.exit(1)

    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(2)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Analysis interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        import traceback
        if '--debug' in sys.argv:
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(3)

def _display_table_results(results: dict):
    """Display results in table format"""
    workflow_results = results.get('workflow_results', {})
    scan_results = workflow_results.get('scan_results', {})

    if not scan_results:
        console.print("[yellow]No scan results available[/yellow]")
        return

    table = Table(title="Security Findings", show_header=True, header_style="bold cyan")
    table.add_column("Tool", style="cyan")
    table.add_column("Findings", justify="right", style="magenta")
    table.add_column("Critical", justify="right", style="red")
    table.add_column("High", justify="right", style="yellow")

    for tool, tool_results in scan_results.items():
        if isinstance(tool_results, dict):
            findings = tool_results.get("findings", [])
            critical = len([f for f in findings if f.get("severity", "").upper() == "CRITICAL"])
            high = len([f for f in findings if f.get("severity", "").upper() == "HIGH"])
            table.add_row(tool, str(len(findings)), str(critical), str(high))

    console.print(table)

def _display_summary_results(results: dict):
    """Display results in summary format"""
    console.print(f"\n[bold green]✅ Analysis Complete[/bold green]\n")

    # Project info
    console.print(f"[bold]Project:[/bold] {results.get('project', 'unknown')}")
    console.print(f"[bold]Type:[/bold] {results.get('project_type', 'unknown')}")
    console.print(f"[bold]Workflow:[/bold] {results.get('workflow_type', 'unknown')}")
    console.print(f"[bold]Status:[/bold] {results.get('status', 'unknown')}\n")

    # Summary
    summary = results.get('summary', 'No summary available')
    console.print(f"[bold blue]📊 Summary:[/bold blue]")
    console.print(f"  {summary}\n")

    # AI Analysis
    ai_analysis = results.get('ai_analysis', {})
    if ai_analysis:
        response = ai_analysis.get('response', '')
        if response:
            console.print(f"[bold blue]🤖 Jade's Analysis:[/bold blue]")
            console.print(Panel(response, border_style="blue"))

        # Recommendations
        recommendations = ai_analysis.get('recommendations', [])
        if recommendations:
            console.print(f"\n[bold green]💡 Recommendations:[/bold green]")
            for rec in recommendations:
                console.print(f"  • {rec}")

        # Next steps
        next_steps = ai_analysis.get('next_steps', [])
        if next_steps:
            console.print(f"\n[bold yellow]🎯 Next Steps:[/bold yellow]")
            for step in next_steps:
                console.print(f"  • {step}")

if __name__ == "__main__":
    cli()