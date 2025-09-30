#!/usr/bin/env python3
"""
Batch update all scanners to use GPDataConfig
"""

from pathlib import Path

# Scanners to update
SCANNERS = [
    "checkov_scanner.py",
    "gitleaks_scanner.py",
    "kube_bench_scanner.py",
    "kube_hunter_scanner.py",
    "npm_audit_scanner.py",
    "opa_scanner.py",
    "polaris_scanner.py",
    "semgrep_scanner.py",
    "tfsec_scanner.py",
    "trivy_scanner.py"
]

# Old hardcoded path pattern
OLD_PATH = 'Path("/home/jimmie/linkops-industries/GP-copilot/GP-DATA/scans")'

# New import to add
NEW_IMPORT = """# Import config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig"""

# New initialization pattern
NEW_INIT = """# Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()"""

def update_scanner(scanner_file: Path):
    """Update a scanner to use GPDataConfig"""
    print(f"Updating {scanner_file.name}...")

    with open(scanner_file, 'r') as f:
        content = f.read()

    # Check if already updated
    if "GPDataConfig" in content:
        print(f"  ✅ Already updated")
        return

    # Add sys import if not present
    if "import sys" not in content:
        content = content.replace(
            "from pathlib import Path",
            "from pathlib import Path\nimport sys"
        )

    # Add config manager import after other imports
    if "from typing import" in content:
        content = content.replace(
            "from typing import",
            f"{NEW_IMPORT}\nfrom typing import"
        )
    elif "from datetime import" in content:
        content = content.replace(
            "from datetime import",
            f"{NEW_IMPORT}\nfrom datetime import"
        )

    # Replace hardcoded path with config manager
    content = content.replace(
        f'self.output_dir = output_dir or {OLD_PATH}',
        f'''# Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()'''
    )

    # Write updated content
    with open(scanner_file, 'w') as f:
        f.write(content)

    print(f"  ✅ Updated successfully")


if __name__ == "__main__":
    scanner_dir = Path(__file__).parent
    updated = 0

    print("🔄 Updating scanners to use GPDataConfig\n")

    for scanner_name in SCANNERS:
        scanner_path = scanner_dir / scanner_name
        if scanner_path.exists():
            update_scanner(scanner_path)
            updated += 1
        else:
            print(f"⚠️  {scanner_name} not found")

    print(f"\n✅ Updated {updated}/{len(SCANNERS)} scanners")