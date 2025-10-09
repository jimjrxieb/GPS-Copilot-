#!/usr/bin/env python3
"""
Check GP-Copilot PRD Progress

Usage:
    python prd_check_progress.py
    python prd_check_progress.py --format json
"""

import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def load_prd():
    """Load PRD JSON file"""
    prd_path = Path(__file__).parent / "GP-COPILOT-PRD.json"
    with open(prd_path) as f:
        return json.load(f)

def check_user_stories(prd):
    """Check user story completion"""
    stories = prd['user_stories']

    total = len(stories)
    done = sum(1 for s in stories if s['status'] == 'DONE')
    in_progress = sum(1 for s in stories if s['status'] == 'IN_PROGRESS')
    pending = sum(1 for s in stories if s['status'] in ['PENDING', 'TODO'])

    table = Table(title="📋 User Stories Progress")
    table.add_column("ID", style="cyan")
    table.add_column("Epic", style="magenta")
    table.add_column("Priority")
    table.add_column("Status")
    table.add_column("Completed")

    for story in stories:
        status_color = {
            'DONE': 'green',
            'IN_PROGRESS': 'yellow',
            'PENDING': 'red',
            'TODO': 'red'
        }.get(story['status'], 'white')

        table.add_row(
            story['id'],
            story['epic'],
            story['priority'],
            f"[{status_color}]{story['status']}[/{status_color}]",
            story.get('completed', 'N/A')
        )

    console.print(table)
    console.print(f"\n[bold]Summary:[/bold] {done}/{total} complete ({done/total*100:.0f}%)")
    console.print(f"  ✅ Done: {done}")
    console.print(f"  🟡 In Progress: {in_progress}")
    console.print(f"  ⬜ Pending: {pending}\n")

    return done, total

def check_metrics(prd):
    """Check success metrics"""
    metrics = prd['success_metrics']

    console.print("[bold cyan]📊 Success Metrics[/bold cyan]\n")

    # Quantitative metrics
    console.print("[bold]Performance Metrics:[/bold]")
    for name, metric in metrics['quantitative']['performance'].items():
        status_icon = {"EXCEEDS": "🟢", "MEETS": "🟡", "BELOW": "🔴"}.get(metric['status'], "⚪")
        console.print(f"  {status_icon} {metric['metric']}: {metric['current']} (target: {metric['target']})")

    console.print("\n[bold]Quality Metrics:[/bold]")
    for name, metric in metrics['quantitative']['quality'].items():
        status_icon = {"EXCEEDS": "🟢", "MEETS": "🟡", "BELOW": "🔴"}.get(metric['status'], "⚪")
        console.print(f"  {status_icon} {metric['metric']}: {metric['current']} (target: {metric['target']})")

    console.print("\n[bold]Intelligence Metrics:[/bold]")
    for name, metric in metrics['quantitative']['intelligence'].items():
        status_icon = {"EXCEEDS": "🟢", "MEETS": "🟡", "BELOW": "🔴"}.get(metric['status'], "⚪")
        console.print(f"  {status_icon} {metric['metric']}: {metric['current']} (target: {metric['target']})")

    # Qualitative metrics
    console.print("\n[bold]Value Proofs:[/bold]")
    for name, metric in metrics['qualitative'].items():
        status_icon = {"DONE": "✅", "IN_PROGRESS": "🟡", "PENDING": "⬜"}.get(metric['status'], "⚪")
        console.print(f"  {status_icon} {metric['requirement']}")
        if 'evidence' in metric:
            console.print(f"      Evidence: {metric['evidence']}")

    console.print()

def check_done_criteria(prd):
    """Check definition of done"""
    criteria = prd['done_criteria']['v1.0_definition_of_done']

    total = len(criteria)
    done = sum(1 for c in criteria if c['status'] == 'DONE')

    console.print("[bold cyan]🎯 Definition of Done[/bold cyan]\n")

    for criterion in criteria:
        status_icon = {"DONE": "✅", "IN_PROGRESS": "🟡", "PENDING": "⬜"}.get(criterion['status'], "⚪")
        console.print(f"  {status_icon} {criterion['criterion']}")
        console.print(f"      Verification: {criterion['verification']}")

    console.print(f"\n[bold]DoD Progress:[/bold] {done}/{total} complete ({done/total*100:.0f}%)\n")

    return done, total

def main():
    """Main function"""
    console.print(Panel.fit(
        "[bold cyan]GP-Copilot PRD Progress Report[/bold cyan]\n"
        "[dim]Generated from GP-COPILOT-PRD.json[/dim]",
        border_style="cyan"
    ))
    console.print()

    prd = load_prd()

    # Check user stories
    us_done, us_total = check_user_stories(prd)

    # Check metrics
    check_metrics(prd)

    # Check done criteria
    dod_done, dod_total = check_done_criteria(prd)

    # Overall summary
    overall_progress = ((us_done / us_total) + (dod_done / dod_total)) / 2 * 100

    console.print(Panel.fit(
        f"[bold green]Overall Progress: {overall_progress:.0f}%[/bold green]\n"
        f"User Stories: {us_done}/{us_total} ({us_done/us_total*100:.0f}%)\n"
        f"Done Criteria: {dod_done}/{dod_total} ({dod_done/dod_total*100:.0f}%)\n\n"
        f"[bold]Status:[/bold] {'✅ READY FOR v1.0 RELEASE' if overall_progress >= 90 else '🟡 IN DEVELOPMENT'}",
        border_style="green" if overall_progress >= 90 else "yellow"
    ))

if __name__ == "__main__":
    main()
