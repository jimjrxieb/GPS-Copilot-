#!/usr/bin/env python3
"""
Test AI Orchestrator with real vulnerability data
"""

import asyncio
import json
from core.ai_orchestrator import ai_orchestrator, generate_concrete_security_fix

async def test_meta_prompting():
    """Test James's meta-prompting capabilities with real vulnerability"""

    # Use actual vulnerability from our earlier analysis
    terraform_vulnerability = {
        "check_id": "CKV_AWS_126",
        "description": "Ensure that detailed monitoring is enabled for EC2 instances",
        "file_path": "/home/jimmie/linkops-industries/Terraform-CICD-Setup/main.tf",
        "resource": "aws_instance.web_server",
        "severity": "low",
        "project": "Terraform-CICD-Setup"
    }

    k8s_vulnerability = {
        "check_id": "CKV_K8S_23",
        "description": "Minimize the admission of containers with allowPrivilegeEscalation",
        "file_path": "/home/jimmie/linkops-industries/Portfolio/k8s/base/deployment-chroma.yaml",
        "resource": "Deployment/chroma-deployment",
        "severity": "high",
        "project": "Portfolio"
    }

    print("🤖 James AI Orchestrator Test")
    print("=" * 50)

    # Test 1: Terraform vulnerability fix
    print("\n📋 Test 1: Generate concrete Terraform fix")
    terraform_result = await generate_concrete_security_fix(terraform_vulnerability)

    print(f"✅ Template Used: {terraform_result.template_used}")
    print(f"✅ Success: {terraform_result.success}")
    print(f"✅ Validation Passed: {terraform_result.validation_passed}")

    if terraform_result.extracted_data:
        print("✅ Extracted Commands:")
        for cmd in terraform_result.extracted_data.get("fix_commands", []):
            print(f"   └─ {cmd}")

    print(f"\n📝 Response Preview:")
    print(terraform_result.response_received[:300] + "...")

    # Test 2: K8s vulnerability fix
    print("\n📋 Test 2: Generate concrete Kubernetes fix")
    k8s_result = await generate_concrete_security_fix(k8s_vulnerability)

    print(f"✅ Template Used: {k8s_result.template_used}")
    print(f"✅ Success: {k8s_result.success}")
    print(f"✅ Validation Passed: {k8s_result.validation_passed}")

    if k8s_result.extracted_data:
        print("✅ Extracted Commands:")
        for cmd in k8s_result.extracted_data.get("fix_commands", []):
            print(f"   └─ {cmd}")

    # Test 3: Show available prompt templates
    print("\n📚 Available Prompt Templates:")
    templates = ai_orchestrator.get_prompt_templates()
    for template in templates:
        print(f"   └─ {template.name} ({template.strategy.value})")

    # Test 4: Show interaction history
    print("\n📈 Recent AI Interactions:")
    history = await ai_orchestrator.get_interaction_history(limit=5)
    for interaction in history:
        status = "✅" if interaction.success else "❌"
        print(f"   {status} {interaction.tool_name} - {interaction.template_used}")

    print("\n🎯 Meta-Prompting Test Complete")
    print(f"   └─ Templates Available: {len(templates)}")
    print(f"   └─ Interactions Recorded: {len(history)}")
    print(f"   └─ Ready for AI orchestration!")

if __name__ == "__main__":
    asyncio.run(test_meta_prompting())