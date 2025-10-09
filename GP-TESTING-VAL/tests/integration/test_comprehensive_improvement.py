#!/usr/bin/env python3
"""
Comprehensive System Improvement Test
=====================================

Tests the overall system improvement across ALL vulnerability types:
- Container vulnerabilities (Trivy)
- Terraform misconfigurations (Checkov)
- Kubernetes security issues (Kubescape)
- NPM/dependency vulnerabilities (npm-audit)
- Python security issues (Bandit)

Measures actual success rate improvement vs baseline.
"""

import asyncio
import sys
import os
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation_engine.automation.automated_fixes import AutomatedFixEngine
from automation_engine.automation.james_ai_engine import SecurityFinding
import uuid
from datetime import datetime

async def create_realistic_test_environment():
    """Create a realistic multi-technology project environment"""

    test_dir = tempfile.mkdtemp(prefix="comprehensive_test_")

    # Create realistic project structure
    project_files = {
        # Container files
        "Dockerfile": """FROM alpine:3.15
RUN apk add --no-cache curl git
WORKDIR /app
COPY . .
CMD ["./start.sh"]""",

        "docker/app.Dockerfile": """FROM node:16-alpine
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]""",

        # Terraform files
        "main.tf": """resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
  acl    = "public-read"
}

resource "aws_instance" "web" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"

  tags = {
    Name = "HelloWorld"
  }
}""",

        "infrastructure/aws.tf": """resource "aws_instance" "database" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"
  monitoring    = false

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "optional"
  }
}""",

        # Kubernetes files
        "k8s/deployment.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: webapp
        image: nginx:1.14
        ports:
        - containerPort: 80""",

        "manifests/api.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  template:
    spec:
      containers:
      - name: api
        image: python:3.9
        securityContext:
          privileged: true
          allowPrivilegeEscalation: true""",

        # NPM files
        "package.json": """{
  "name": "test-app",
  "version": "1.0.0",
  "dependencies": {
    "lodash": "4.17.4",
    "express": "4.16.0",
    "axios": "0.18.0"
  },
  "devDependencies": {
    "webpack": "4.0.0"
  }
}""",

        "frontend/package.json": """{
  "name": "frontend",
  "dependencies": {
    "react": "16.8.0",
    "jquery": "3.3.1"
  }
}""",

        # Python files
        "app.py": """import subprocess
import os
import sqlite3

# Potential security issues for Bandit to find
def unsafe_command(user_input):
    # Command injection vulnerability
    subprocess.call("echo " + user_input, shell=True)

def sql_injection(query):
    # SQL injection vulnerability
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = " + query)
    return cursor.fetchall()

def hardcoded_password():
    # Hardcoded password
    password = "admin123"
    return password
""",

        # Config files
        "nginx.conf": """server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
    }
}""",
    }

    # Create files
    for file_path, content in project_files.items():
        full_path = Path(test_dir) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)

    return test_dir

async def create_comprehensive_vulnerability_set(test_dir):
    """Create a comprehensive set of realistic vulnerability findings"""

    vulnerabilities = [
        # Container vulnerabilities (Trivy)
        SecurityFinding(
            id="trivy-001",
            severity="critical",
            title="alpine:3.15 base image vulnerabilities",
            description="alpine:3.15 contains 12 high-severity vulnerabilities including CVE-2023-1234",
            file_path=os.path.join(test_dir, "Dockerfile"),
            tool="trivy",
            remediation="Update to alpine:3.18"
        ),
        SecurityFinding(
            id="trivy-002",
            severity="high",
            title="node:16-alpine vulnerabilities",
            description="node:16-alpine container has outdated npm packages with known CVEs",
            file_path=os.path.join(test_dir, "docker", "app.Dockerfile"),
            tool="trivy",
            remediation="Update to node:18-alpine"
        ),
        SecurityFinding(
            id="trivy-003",
            severity="medium",
            title="NPM dependency vulnerabilities",
            description="lodash@4.17.4 has CVE-2019-10744, express@4.16.0 has CVE-2022-24999",
            file_path=os.path.join(test_dir, "package.json"),
            tool="trivy",
            remediation="Update vulnerable packages"
        ),

        # Terraform vulnerabilities (Checkov)
        SecurityFinding(
            id="checkov-001",
            severity="high",
            title="S3 bucket publicly accessible",
            description="CKV_AWS_20: S3 bucket has public read access configured",
            file_path=os.path.join(test_dir, "main.tf"),
            tool="checkov",
            remediation="Set ACL to private"
        ),
        SecurityFinding(
            id="checkov-002",
            severity="medium",
            title="EC2 detailed monitoring disabled",
            description="CKV_AWS_126: EC2 instance does not have detailed monitoring enabled",
            file_path=os.path.join(test_dir, "infrastructure", "aws.tf"),
            tool="checkov",
            remediation="Enable detailed monitoring"
        ),
        SecurityFinding(
            id="checkov-003",
            severity="high",
            title="IMDSv2 not enforced",
            description="CKV_AWS_79: EC2 instance metadata service v2 not enforced",
            file_path=os.path.join(test_dir, "infrastructure", "aws.tf"),
            tool="checkov",
            remediation="Set http_tokens to required"
        ),

        # Kubernetes vulnerabilities (Kubescape)
        SecurityFinding(
            id="kubescape-001",
            severity="high",
            title="Container running as privileged",
            description="CKV_K8S_28: Container allows privilege escalation",
            file_path=os.path.join(test_dir, "manifests", "api.yaml"),
            tool="kubescape",
            remediation="Set privileged: false"
        ),
        SecurityFinding(
            id="kubescape-002",
            severity="medium",
            title="Missing security context",
            description="CKV_K8S_20: Container should not run as root user",
            file_path=os.path.join(test_dir, "k8s", "deployment.yaml"),
            tool="kubescape",
            remediation="Add runAsNonRoot: true"
        ),

        # Python security issues (Bandit)
        SecurityFinding(
            id="bandit-001",
            severity="high",
            title="Command injection vulnerability",
            description="Use of shell=True in subprocess call with user input",
            file_path=os.path.join(test_dir, "app.py"),
            tool="bandit",
            remediation="Use subprocess with shell=False"
        ),
        SecurityFinding(
            id="bandit-002",
            severity="medium",
            title="Hardcoded password",
            description="Hardcoded password found in source code",
            file_path=os.path.join(test_dir, "app.py"),
            tool="bandit",
            remediation="Use environment variables"
        ),

        # Web server configuration (Custom)
        SecurityFinding(
            id="nginx-001",
            severity="medium",
            title="Missing security headers",
            description="Nginx configuration missing security headers like X-Frame-Options",
            file_path=os.path.join(test_dir, "nginx.conf"),
            tool="custom",
            remediation="Add security headers"
        )
    ]

    return vulnerabilities

async def test_comprehensive_system_improvement():
    """Test overall system improvement across all vulnerability types"""

    print("\n" + "="*70)
    print("    COMPREHENSIVE SYSTEM IMPROVEMENT ASSESSMENT")
    print("="*70 + "\n")

    # Create test environment
    test_dir = await create_realistic_test_environment()
    vulnerabilities = await create_comprehensive_vulnerability_set(test_dir)

    fix_engine = AutomatedFixEngine()

    try:
        print(f"📝 Created realistic test environment with {len(vulnerabilities)} vulnerabilities")
        print(f"📁 Test project: {test_dir}")
        print()

        # Test results tracking
        results_by_tool = {}
        results_by_type = {}
        overall_results = {
            "total_vulnerabilities": len(vulnerabilities),
            "successful_fixes": 0,
            "failed_fixes": 0,
            "manual_fixes": 0,
            "placeholder_fixes": 0,
            "real_command_fixes": 0
        }

        # Test each vulnerability
        for vuln in vulnerabilities:
            tool = vuln.tool
            vuln_type = f"{tool}_{vuln.severity}"

            if tool not in results_by_tool:
                results_by_tool[tool] = {"total": 0, "success": 0, "fail": 0, "manual": 0}
            if vuln_type not in results_by_type:
                results_by_type[vuln_type] = {"total": 0, "success": 0}

            results_by_tool[tool]["total"] += 1
            results_by_type[vuln_type]["total"] += 1

            print(f"🔍 Testing: {vuln.tool} | {vuln.title[:50]}...")

            try:
                # Test tool-specific routing
                detected_pattern = fix_engine._get_tool_specific_pattern(vuln)
                print(f"   🎯 Routed to: {detected_pattern}")

                # Generate fix
                fixes = await fix_engine._generate_fixes_for_finding(vuln, test_dir)

                if fixes:
                    fix = fixes[0]

                    # Analyze fix quality
                    if fix.status.value == "manual_required":
                        results_by_tool[tool]["manual"] += 1
                        overall_results["manual_fixes"] += 1
                        print(f"   ⚠️ Manual fix required")

                    elif fix.commands:
                        # Check if commands are real or placeholder
                        real_commands = [cmd for cmd in fix.commands
                                       if not any(placeholder in cmd.lower()
                                                for placeholder in ["echo", "manual", "file path not available"])]

                        if real_commands:
                            results_by_tool[tool]["success"] += 1
                            results_by_type[vuln_type]["success"] += 1
                            overall_results["successful_fixes"] += 1
                            overall_results["real_command_fixes"] += 1
                            print(f"   ✅ Generated {len(real_commands)} real commands")

                        else:
                            overall_results["placeholder_fixes"] += 1
                            print(f"   ⚠️ Generated placeholder commands")
                    else:
                        results_by_tool[tool]["fail"] += 1
                        overall_results["failed_fixes"] += 1
                        print(f"   ❌ No commands generated")

                else:
                    results_by_tool[tool]["fail"] += 1
                    overall_results["failed_fixes"] += 1
                    print(f"   ❌ No fixes generated")

            except Exception as e:
                results_by_tool[tool]["fail"] += 1
                overall_results["failed_fixes"] += 1
                print(f"   💥 Error: {str(e)[:60]}...")

        # Calculate comprehensive results
        print(f"\n📊 COMPREHENSIVE RESULTS BREAKDOWN")
        print("=" * 50)

        # Overall success rate
        total_vulns = overall_results["total_vulnerabilities"]
        successful = overall_results["successful_fixes"]
        overall_success_rate = (successful / total_vulns) * 100

        print(f"Overall Success Rate: {overall_success_rate:.1f}% ({successful}/{total_vulns})")
        print(f"Real Command Generation: {overall_results['real_command_fixes']}")
        print(f"Manual Fixes Required: {overall_results['manual_fixes']}")
        print(f"Placeholder Fixes: {overall_results['placeholder_fixes']}")
        print(f"Complete Failures: {overall_results['failed_fixes']}")
        print()

        # Results by scanning tool
        print("Results by Scanning Tool:")
        print("-" * 30)
        for tool, results in results_by_tool.items():
            tool_success_rate = (results["success"] / results["total"]) * 100 if results["total"] > 0 else 0
            print(f"{tool:12} | {tool_success_rate:5.1f}% | {results['success']}/{results['total']} | Manual: {results['manual']}")

        print()

        # Results by vulnerability type
        print("Results by Vulnerability Type:")
        print("-" * 35)
        for vuln_type, results in results_by_type.items():
            type_success_rate = (results["success"] / results["total"]) * 100 if results["total"] > 0 else 0
            print(f"{vuln_type:20} | {type_success_rate:5.1f}% | {results['success']}/{results['total']}")

        print()

        # Assessment
        print("🎯 SYSTEM ASSESSMENT")
        print("=" * 25)

        if overall_success_rate >= 80:
            assessment = "✅ PRODUCTION READY"
        elif overall_success_rate >= 65:
            assessment = "⚠️ GOOD PROGRESS - Minor gaps to address"
        elif overall_success_rate >= 50:
            assessment = "🔧 SIGNIFICANT IMPROVEMENT - More work needed"
        else:
            assessment = "❌ NEEDS MAJOR WORK"

        print(f"Status: {assessment}")
        print(f"Recommendation: {'Deploy with confidence' if overall_success_rate >= 80 else 'Continue targeted improvements'}")

        return overall_success_rate, results_by_tool, results_by_type

    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)

async def main():
    """Run comprehensive system assessment"""

    print("🚀 COMPREHENSIVE GUIDEPOINT IMPROVEMENT ASSESSMENT")
    print("=" * 60)
    print("Testing improved system against realistic vulnerability set...")

    overall_rate, tool_results, type_results = await test_comprehensive_system_improvement()

    print(f"\n🏆 FINAL ASSESSMENT")
    print("=" * 30)
    print(f"Overall System Success Rate: {overall_rate:.1f}%")
    print(f"Baseline (before improvements): ~55.6%")
    print(f"Improvement: +{overall_rate - 55.6:.1f} percentage points")

    if overall_rate >= 80:
        print("✅ READY FOR PRODUCTION DEPLOYMENT")
        return True
    elif overall_rate >= 65:
        print("⚠️ READY FOR LIMITED DEPLOYMENT WITH MONITORING")
        return True
    else:
        print("🔧 CONTINUE DEVELOPMENT - SIGNIFICANT GAPS REMAIN")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)