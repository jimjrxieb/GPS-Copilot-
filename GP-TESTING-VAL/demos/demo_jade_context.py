#!/usr/bin/env python3
"""
Demo: Jade's Contextual Tool Awareness
Shows how Jade analyzes projects and selects appropriate security tools
"""

import sys
from pathlib import Path

# Add GP-AI to path
sys.path.append(str(Path(__file__).parent / "GP-AI"))

from tool_registry import jade_tool_registry
from comprehensive_jade_prompts import get_comprehensive_security_prompt

def demo_jade_contextual_awareness():
    """Demonstrate Jade's complete contextual awareness"""

    print("🎯 **JADE CONTEXTUAL TOOL AWARENESS DEMO**")
    print("=" * 60)

    # Test project path
    project_path = "/home/jimmie/linkops-industries/GP-copilot"

    print(f"\n📁 **Analyzing Project:** {project_path}")
    print("-" * 40)

    # 1. Project Context Analysis
    print("\n🔍 **STEP 1: Project Discovery**")
    context = jade_tool_registry.analyze_project_context(project_path)

    print(f"Detected Technologies: {', '.join(context['detected_technologies'])}")
    print(f"Project Type: {context['execution_pattern'].replace('_', ' ').title()}")
    print(f"Total Files: {sum(context['file_analysis'].values()):,}")

    # Show file breakdown
    print(f"\nFile Analysis:")
    for pattern, count in sorted(context['file_analysis'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {pattern}: {count:,} files")

    # 2. Tool Strategy
    print(f"\n🎯 **STEP 2: Security Tool Strategy**")
    strategy = jade_tool_registry.get_scan_strategy(context, {
        "compliance": ["SOC2", "CIS"],
        "industry": "fintech"
    })

    print(f"Primary Scanners: {', '.join(strategy['primary_scanners'])}")
    print(f"Execution Order: {' → '.join(strategy['execution_order'][:5])}...")
    print(f"Total Tools: {len(strategy['execution_order'])}")

    # 3. Tool Availability Check
    print(f"\n✅ **STEP 3: Available Tools**")
    availability = jade_tool_registry.validate_tool_availability()
    available_tools = [tool for tool, available in availability.items() if available]
    missing_tools = [tool for tool, available in availability.items() if not available]

    print(f"Available ({len(available_tools)}): {', '.join(available_tools)}")
    print(f"Missing ({len(missing_tools)}): {', '.join(missing_tools[:5])}{'...' if len(missing_tools) > 5 else ''}")

    # 4. Jade's Reasoning
    print(f"\n🧠 **STEP 4: Jade's Reasoning**")
    reasoning = jade_tool_registry.generate_jade_reasoning(context, strategy)
    print(reasoning)

    # 5. Contextual Prompting
    print(f"\n💬 **STEP 5: Contextual Prompt Generation**")
    comprehensive_prompt = get_comprehensive_security_prompt(
        project_path=project_path,
        client_name="LinkOps",
        analysis_depth="comprehensive",
        industry="fintech",
        compliance_requirements=["SOC2", "PCI-DSS"]
    )

    # Show first part of the prompt
    prompt_preview = comprehensive_prompt[:800] + "..."
    print("Generated Comprehensive Prompt (preview):")
    print("-" * 40)
    print(prompt_preview)

    # 6. Demonstration Examples
    print(f"\n🎭 **STEP 6: Contextual Decision Examples**")
    print("-" * 40)

    examples = [
        ("*.tf files detected", "→ Run tfsec + checkov for Terraform security"),
        ("*.yaml files detected", "→ Run kubescape + cks_agent for K8s security"),
        ("*.py files detected", "→ Run bandit for Python SAST analysis"),
        ("Dockerfile found", "→ Run trivy + container_agent for container security"),
        ("package.json found", "→ Run npm audit for dependency scanning"),
        ("Large codebase (150K+ files)", "→ Execute comprehensive multi-tool analysis"),
        ("Fintech industry", "→ Focus on SOC2/PCI-DSS compliance requirements"),
        ("Infrastructure focus", "→ Prioritize IaC scanners over application tools")
    ]

    for condition, action in examples:
        print(f"  {condition:<30} {action}")

    print(f"\n🏆 **RESULT: Jade has complete contextual awareness!**")
    print("Jade can now reason about:")
    print("  • Which tools to run based on project content")
    print("  • Optimal execution order for efficiency")
    print("  • Compliance requirements and tool mapping")
    print("  • Resource availability and fallback strategies")
    print("  • Industry-specific security priorities")

if __name__ == "__main__":
    demo_jade_contextual_awareness()