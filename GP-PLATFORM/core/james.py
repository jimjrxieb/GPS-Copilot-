#!/usr/bin/env python3
"""
James Security Assistant - Main Entry Point
Simple, fast, reliable security operations
"""

import sys
import os
from pathlib import Path

# Add GP-copilot to path
GP_COPILOT_BASE = '/home/jimmie/linkops-industries/GP-copilot'
sys.path.insert(0, f'{GP_COPILOT_BASE}/GP-PLATFORM/core')

from james_command_router import JamesCommandRouter

def main():
    """Main James interface"""
    if len(sys.argv) < 2:
        print("🤖 James Security Assistant")
        print("Usage: python james.py '<command>'")
        print("\nQuick Commands:")
        print("  python james.py 'scan Portfolio'")
        print("  python james.py 'scan Terraform_CICD_Setup'")
        print("  python james.py 'status'")
        print("  python james.py 'help'")
        sys.exit(1)

    # Change to GP-copilot directory
    os.chdir(GP_COPILOT_BASE)

    command = " ".join(sys.argv[1:])
    router = JamesCommandRouter()

    print(f"🤖 James executing: {command}")
    result = router.route_command(command)

    # Return appropriate exit code
    if result["status"] == "success":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()