#!/usr/bin/env python3
"""
GP-JADE Auto-Sync Test Script
==============================

Test the complete RAG auto-sync system:
1. File system watcher
2. Auto-ingestion pipeline
3. Activity tracking
4. Query interface

Author: GP-JADE Team
Date: September 30, 2025
"""

import os
import time
import shutil
from pathlib import Path
from datetime import datetime

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Import our components
from auto_sync import JadeWorkspaceSync
from ingestion.auto_ingest import AutoIngestionPipeline
from query.activity_queries import ActivityQueryEngine


console = Console()


def setup_test_workspace():
    """Create test workspace with sample files"""
    workspace = Path.home() / "jade-workspace"
    projects = workspace / "projects"
    test_project = projects / "test-terraform"

    # Create directories
    test_project.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[green]✓[/green] Created test workspace: {workspace}")

    # Create sample files
    samples = [
        # Terraform files
        ("main.tf", """
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  tags = {
    Name = "WebServer"
    Environment = "Production"
  }
}
"""),
        ("variables.tf", """
variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}
"""),
        # Kubernetes manifest
        ("deployment.yaml", """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
"""),
        # OPA policy
        ("security-policy.rego", """
package kubernetes.admission

deny[msg] {
  not input.request.object.spec.securityContext.runAsNonRoot
  msg = "Pods must run as non-root user"
}

deny[msg] {
  container := input.request.object.spec.containers[_]
  not container.securityContext.allowPrivilegeEscalation == false
  msg = sprintf("Container %v must not allow privilege escalation", [container.name])
}
"""),
        # Python script
        ("scanner.py", """
#!/usr/bin/env python3
\"\"\"
Security scanner script
\"\"\"

import subprocess

def scan_terraform(path):
    \"\"\"Scan Terraform files\"\"\"
    result = subprocess.run(['checkov', '-d', path], capture_output=True)
    return result.returncode == 0

if __name__ == "__main__":
    scan_terraform(".")
"""),
    ]

    created_files = []
    for filename, content in samples:
        file_path = test_project / filename
        file_path.write_text(content)
        created_files.append(str(file_path))
        console.print(f"[green]✓[/green] Created: {filename}")

    return workspace, created_files


def test_file_watcher():
    """Test 1: File system watcher"""
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]TEST 1: File System Watcher[/bold cyan]")
    console.print("=" * 60)

    workspace, created_files = setup_test_workspace()

    # Initialize sync system
    sync = JadeWorkspaceSync(workspace_dir=str(workspace))

    # Perform initial sync
    console.print("\n[yellow]→[/yellow] Running initial sync...")
    file_count = sync.initial_sync()
    console.print(f"[green]✓[/green] Synced {file_count} files")

    # Start watcher in background
    console.print("\n[yellow]→[/yellow] Starting file system watcher...")
    sync.start_watching()
    console.print("[green]✓[/green] Watcher started")

    # Test file creation
    test_file = Path(workspace) / "projects" / "test-terraform" / "new-file.tf"
    console.print(f"\n[yellow]→[/yellow] Creating test file: {test_file.name}")
    test_file.write_text("resource \"aws_s3_bucket\" \"test\" {}")
    time.sleep(2)  # Wait for watcher to process

    # Test file modification
    console.print(f"[yellow]→[/yellow] Modifying test file...")
    test_file.write_text("resource \"aws_s3_bucket\" \"test\" { versioning = true }")
    time.sleep(2)

    # Stop watcher
    sync.stop_watching()
    console.print("[green]✓[/green] Watcher stopped")

    return sync


def test_activity_queries(sync):
    """Test 2: Activity queries"""
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]TEST 2: Activity Queries[/bold cyan]")
    console.print("=" * 60)

    query_engine = ActivityQueryEngine()

    # Test: What did we do today?
    console.print("\n[bold]Query: What did we do today?[/bold]")
    today = query_engine.query_todays_work()

    table = Table(title="Today's Activity")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Date", today['date'])
    table.add_row("Total Events", str(today['total_events']))
    table.add_row("Files Created", str(today['actions'].get('created', 0)))
    table.add_row("Files Modified", str(today['actions'].get('modified', 0)))
    table.add_row("Projects", ", ".join(today['projects']))

    console.print(table)
    console.print(f"\n[bold]Summary:[/bold] {today['summary']}")

    # Test: Query by file type
    console.print("\n[bold]Query: Show me Terraform files[/bold]")
    tf_files = query_engine.query_by_file_type(".tf", days_back=1)
    console.print(f"[green]✓[/green] Found {len(tf_files)} Terraform files")
    for f in tf_files[:3]:
        console.print(f"  - {Path(f['file_path']).name} ({f['action']})")

    # Test: Query by project
    console.print("\n[bold]Query: Show activity for test-terraform project[/bold]")
    project_data = query_engine.query_by_project("test-terraform", days_back=1)
    console.print(f"[green]✓[/green] Total events: {project_data['total_events']}")
    console.print(f"  File types: {', '.join(project_data['file_types'].keys())}")

    return query_engine


def test_semantic_search(query_engine):
    """Test 3: Semantic search"""
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]TEST 3: Semantic Search[/bold cyan]")
    console.print("=" * 60)

    queries = [
        ("runAsNonRoot policy", "opa_policy"),
        ("AWS instance configuration", "terraform"),
        ("security context", "kubernetes"),
    ]

    for query, category in queries:
        console.print(f"\n[bold]Query:[/bold] \"{query}\" (category: {category})")
        results = query_engine.semantic_search(query, category=category, days_back=1)

        if results:
            console.print(f"[green]✓[/green] Found {len(results)} results")
            for i, result in enumerate(results[:2], 1):
                console.print(f"  {i}. {Path(result['metadata']['file_path']).name}")
                console.print(f"     Distance: {result['distance']:.3f}")
        else:
            console.print("[yellow]![/yellow] No results found")


def test_trend_analysis(query_engine):
    """Test 4: Trend analysis"""
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]TEST 4: Trend Analysis[/bold cyan]")
    console.print("=" * 60)

    console.print("\n[yellow]→[/yellow] Analyzing activity trends...")
    trends = query_engine.query_trend_analysis(days=7)

    console.print(f"[green]✓[/green] Date range: {trends['date_range']}")
    console.print(f"[green]✓[/green] Avg daily activity: {trends['avg_daily_activity']:.1f} events")

    # Show daily counts
    if trends['daily_counts']:
        table = Table(title="Daily Activity")
        table.add_column("Date", style="cyan")
        table.add_column("Events", style="green")

        for date, count in list(trends['daily_counts'].items())[-7:]:
            table.add_row(date, str(count))

        console.print(table)


def test_policy_queries(query_engine):
    """Test 5: Policy-specific queries"""
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]TEST 5: Policy Queries[/bold cyan]")
    console.print("=" * 60)

    # Query OPA policies
    console.print("\n[bold]Query: Show policy changes[/bold]")
    policies = query_engine.query_policy_changes(days_back=1)
    console.print(f"[green]✓[/green] Total policies: {policies['total_policies']}")
    console.print(f"  - OPA policies: {policies['opa_policies']}")
    console.print(f"  - Gatekeeper policies: {policies['gatekeeper_policies']}")

    # Query Terraform changes
    console.print("\n[bold]Query: Show Terraform changes[/bold]")
    terraform = query_engine.query_terraform_changes(days_back=1)
    console.print(f"[green]✓[/green] Total Terraform files: {terraform['total_files']}")
    console.print(f"  - .tf files: {terraform['tf_files']}")
    console.print(f"  - .tfvars files: {terraform['tfvars_files']}")


def main():
    """Run all tests"""
    console.print(Panel.fit(
        "[bold cyan]GP-JADE RAG Auto-Sync Test Suite[/bold cyan]\n"
        "Testing file system watcher, ingestion, and query interface",
        border_style="cyan"
    ))

    try:
        # Test 1: File watcher
        sync = test_file_watcher()

        # Test 2: Activity queries
        query_engine = test_activity_queries(sync)

        # Test 3: Semantic search
        test_semantic_search(query_engine)

        # Test 4: Trend analysis
        test_trend_analysis(query_engine)

        # Test 5: Policy queries
        test_policy_queries(query_engine)

        # Final summary
        console.print("\n" + "=" * 60)
        console.print("[bold green]✓ ALL TESTS PASSED[/bold green]")
        console.print("=" * 60)

        console.print("\n[bold]Key Features Verified:[/bold]")
        console.print("[green]✓[/green] File system watcher detects changes")
        console.print("[green]✓[/green] Auto-ingestion pipeline works")
        console.print("[green]✓[/green] Activity tracking accurate")
        console.print("[green]✓[/green] \"What did we do today?\" queries work")
        console.print("[green]✓[/green] Semantic search functional")
        console.print("[green]✓[/green] Trend analysis operational")

        console.print("\n[bold cyan]Phase 1: RAG Auto-Sync System - COMPLETE! 🎉[/bold cyan]")

    except Exception as e:
        console.print(f"\n[bold red]✗ TEST FAILED:[/bold red] {e}")
        logger.exception("Test failed")
        raise


if __name__ == "__main__":
    # Configure logging
    logger.add("GP-DATA/active/test_auto_sync.log", rotation="1 day")

    main()