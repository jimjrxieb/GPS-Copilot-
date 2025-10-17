#!/usr/bin/env python3
"""
Test Jade AI's ability to answer CKS and GuidePoint questions
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from GP_AI.jade_enhanced import JadeEnhanced
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_cks_questions():
    """Test Jade's CKS knowledge"""
    console.print(Panel.fit(
        "[bold cyan]Testing Jade AI - CKS Knowledge[/bold cyan]",
        border_style="cyan"
    ))
    
    jade = JadeEnhanced()
    
    questions = [
        "What's the difference between Pod Security Policy and Pod Security Standards?",
        "What are the 4Cs of cloud native security?",
        "How do I prevent privilege escalation in Kubernetes containers?",
        "What is the principle of least privilege in Kubernetes RBAC?",
    ]
    
    for q in questions:
        console.print(f"\n[bold cyan]Q:[/bold cyan] {q}")
        console.print("[yellow]→[/yellow] Jade is thinking...")
        
        try:
            response = jade.analyze_with_context(q, project="guidepoint-security-test")
            console.print(f"[green]A:[/green] {response.get('summary', 'No response')}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


def test_guidepoint_knowledge():
    """Test Jade's GuidePoint company context"""
    console.print(Panel.fit(
        "[bold cyan]Testing Jade AI - GuidePoint Context[/bold cyan]",
        border_style="cyan"
    ))
    
    jade = JadeEnhanced()
    
    questions = [
        "What is GuidePoint Security and what do they do?",
        "What are GuidePoint's escalation procedures for CRITICAL findings?",
        "What are GuidePoint's cloud security standards?",
    ]
    
    for q in questions:
        console.print(f"\n[bold cyan]Q:[/bold cyan] {q}")
        console.print("[yellow]→[/yellow] Jade is thinking...")
        
        try:
            response = jade.analyze_with_context(q, project="guidepoint-security-test")
            console.print(f"[green]A:[/green] {response.get('summary', 'No response')}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    try:
        test_cks_questions()
        test_guidepoint_knowledge()
    except Exception as e:
        console.print(f"[bold red]Test failed:[/bold red] {e}")
