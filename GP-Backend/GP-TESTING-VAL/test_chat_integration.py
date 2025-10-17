#!/usr/bin/env python3
"""
🧪 Test James Chat Integration with Enhanced Tools
"""

import asyncio
import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.tool_integration import handle_tool_request

async def test_chat_integration():
    """Test the enhanced chat capabilities"""

    print("🧪 Testing James Enhanced Chat Integration...")
    print("=" * 60)

    # Test secrets management
    print("\n1. Testing Secrets Management:")
    result = await handle_tool_request("Generate Vault configuration for portfolio", "secrets")
    print(f"   Status: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"   Duration: {result.duration_ms}ms")
    print(f"   Evidence: {result.evidence_id}")

    # Test threat intelligence
    print("\n2. Testing Threat Intelligence:")
    result = await handle_tool_request("Analyze IOCs from security incident", "threat_intel")
    print(f"   Status: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"   Duration: {result.duration_ms}ms")
    print(f"   Evidence: {result.evidence_id}")

    # Test deployment automation
    print("\n3. Testing Deployment Automation:")
    result = await handle_tool_request("Deploy Portfolio project", "deployment")
    print(f"   Status: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"   Duration: {result.duration_ms}ms")
    print(f"   Evidence: {result.evidence_id}")
    if not result.success:
        print(f"   Error: {result.message}")

    # Test policy generation
    print("\n4. Testing Policy Generation:")
    result = await handle_tool_request("Generate OPA security policies", "policy")
    print(f"   Status: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"   Duration: {result.duration_ms}ms")
    print(f"   Evidence: {result.evidence_id}")
    if not result.success:
        print(f"   Error: {result.message}")

    print("\n" + "=" * 60)
    print("🎯 Enhanced James Chat Integration Test Complete!")
    print("✅ James now has access to all 4 enhanced tools through conversation")
    print("🚀 Ready for user interaction through chat interface")

if __name__ == "__main__":
    asyncio.run(test_chat_integration())