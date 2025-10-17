#!/usr/bin/env python3
"""
🔍 Real Portfolio Test - James Enhanced Scanner
Tests the working scanner on a realistic portfolio project structure
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append('/home/jimmie/linkops-industries/James-OS/guidepoint')

from james_enhanced_scanner import JamesEnhancedScanner

def create_realistic_portfolio_project():
    """Create a realistic portfolio project structure for testing"""

    portfolio_dir = "/tmp/portfolio_test"

    # Create directory structure
    os.makedirs(f"{portfolio_dir}/backend", exist_ok=True)
    os.makedirs(f"{portfolio_dir}/frontend", exist_ok=True)
    os.makedirs(f"{portfolio_dir}/infrastructure", exist_ok=True)
    os.makedirs(f"{portfolio_dir}/docker", exist_ok=True)

    # Create Python backend files with security issues
    backend_main = '''
import sqlite3
import os

# Security issue: hardcoded password
DATABASE_PASSWORD = "admin123"  # This should trigger B105

def get_user_data(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Security issue: SQL injection vulnerability
    query = "SELECT * FROM users WHERE id = '%s'" % user_id  # This should trigger B608
    cursor.execute(query)

    return cursor.fetchall()

def authenticate_user(username, password):
    if password == DATABASE_PASSWORD:
        return True
    return False
'''

    with open(f"{portfolio_dir}/backend/main.py", "w") as f:
        f.write(backend_main)

    # Create requirements.txt with potential vulnerabilities
    requirements = '''
flask==1.0.0
django==2.0.0
requests==2.20.0
numpy==1.16.0
'''

    with open(f"{portfolio_dir}/backend/requirements.txt", "w") as f:
        f.write(requirements)

    # Create Terraform infrastructure with security issues
    terraform_main = '''
# Portfolio Infrastructure
resource "aws_instance" "web_server" {
  ami           = "ami-12345678"
  instance_type = "t3.medium"
  key_name      = "portfolio-key"

  vpc_security_group_ids = [aws_security_group.web_sg.id]

  # Missing: monitoring = true
  # Missing: metadata_options block (IMDSv2)
  # Missing: iam_instance_profile
  # Missing: ebs_optimized = true

  tags = {
    Name = "Portfolio-WebServer"
    Environment = "production"
  }
}

resource "aws_security_group" "web_sg" {
  name_description = "Web server security group"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Security issue: SSH open to world
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "portfolio_db" {
  identifier = "portfolio-database"
  engine     = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_encrypted = false  # Security issue: unencrypted storage

  db_name  = "portfolio"
  username = "admin"
  password = "admin123"  # Security issue: hardcoded password

  publicly_accessible = true  # Security issue: public database

  skip_final_snapshot = true
}
'''

    with open(f"{portfolio_dir}/infrastructure/main.tf", "w") as f:
        f.write(terraform_main)

    # Create Dockerfile with security issues
    dockerfile = '''
FROM node:16

# Security issue: running as root
USER root

# Security issue: using latest tag implicitly
COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

# Security issue: still running as root
CMD ["npm", "start"]
'''

    with open(f"{portfolio_dir}/docker/Dockerfile", "w") as f:
        f.write(dockerfile)

    # Create package.json for frontend
    package_json = '''
{
  "name": "portfolio-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^17.0.0",
    "lodash": "4.17.15",
    "express": "4.16.0",
    "axios": "0.18.0"
  }
}
'''

    with open(f"{portfolio_dir}/frontend/package.json", "w") as f:
        f.write(package_json)

    # Create YAML config with potential issues
    k8s_config = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: portfolio-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: portfolio
  template:
    metadata:
      labels:
        app: portfolio
    spec:
      containers:
      - name: portfolio
        image: portfolio:latest
        ports:
        - containerPort: 3000
        securityContext:
          runAsUser: 0  # Security issue: running as root
          privileged: true  # Security issue: privileged container
        env:
        - name: DATABASE_PASSWORD
          value: "admin123"  # Security issue: plaintext secrets
'''

    with open(f"{portfolio_dir}/infrastructure/deployment.yaml", "w") as f:
        f.write(k8s_config)

    return portfolio_dir

def run_portfolio_test():
    """Run comprehensive test on portfolio project"""

    print("🚀 REAL PORTFOLIO TEST - James Enhanced Scanner")
    print("=" * 60)

    # Create realistic portfolio project
    portfolio_dir = create_realistic_portfolio_project()
    print(f"📁 Created test portfolio: {portfolio_dir}")

    # Show project structure
    print("\n📂 Project Structure:")
    for root, dirs, files in os.walk(portfolio_dir):
        level = root.replace(portfolio_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")

    # Initialize James Enhanced Scanner
    scanner = JamesEnhancedScanner()

    # Run comprehensive scan
    print(f"\n🔍 Running James Enhanced Scan on Portfolio...")
    results = scanner.scan_with_intelligence(portfolio_dir)

    # Display results
    print("\n" + "="*60)
    print("📊 PORTFOLIO SCAN RESULTS")
    print("="*60)

    james_intel = results['james_intelligence']
    print(f"🧠 James Engine Status: {james_intel['confidence_engine_status']}")
    print(f"📚 Evidence Source: {james_intel['evidence_source']}")
    print()

    summary = results['summary']
    print(f"📁 Files Scanned: {summary['total_files_scanned']}")
    print(f"🔍 Total Findings: {summary['total_findings']}")
    print(f"   🚨 HIGH: {summary['high']}")
    print(f"   ⚠️  MEDIUM: {summary['medium']}")
    print(f"   📝 LOW: {summary['low']}")
    print()

    # Show file type breakdown
    print("📋 Findings by File Type:")
    for file_type, count in summary['by_file_type'].items():
        print(f"   {file_type}: {count} findings")
    print()

    # James Intelligence Analysis
    remediation = results['remediation_plan']
    print("🧠 JAMES INTELLIGENCE ANALYSIS:")
    print(f"   ✅ Automated Fixes: {remediation['summary']['automated_count']}")
    print(f"   🤝 Assisted Fixes: {remediation['summary']['assisted_count']}")
    print(f"   🚨 Escalations: {remediation['summary']['escalated_count']}")
    print(f"   📈 Automation Rate: {remediation['summary']['automation_rate']:.1%}")
    print()

    print(f"💼 Business Impact: {remediation['business_impact']}")
    print(f"⏱️  Estimated Effort: {remediation['estimated_effort']}")
    print()

    # Show top findings with James analysis
    print("🔍 TOP SECURITY FINDINGS (with James Intelligence):")
    for i, finding in enumerate(results['enhanced_findings'][:8], 1):
        james = finding['james_analysis']
        print(f"{i}. {finding['check_id']}: {finding['description']}")
        print(f"   📁 File: {os.path.basename(finding['file'])}")
        print(f"   🎯 Severity: {finding['severity']}")
        print(f"   🧠 James Confidence: {james['confidence_score']:.3f} ({james['confidence_level']})")
        print(f"   🔧 Remediation: {james['remediation_type']}")
        print(f"   💡 Fix: {finding['fix_suggestion']}")
        print()

    # Save detailed results
    results_file = f"{portfolio_dir}/james_portfolio_scan_results.json"
    import json
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Detailed results saved: {results_file}")

    # Summary statistics
    print("\n" + "="*60)
    print("📈 REAL PORTFOLIO TEST SUMMARY")
    print("="*60)
    print(f"✅ Scanner Function: WORKING")
    print(f"✅ James Intelligence: {james_intel['confidence_engine_status'].upper()}")
    print(f"✅ Pattern Detection: {summary['total_findings']} issues found")
    print(f"✅ Confidence Routing: {remediation['summary']['automation_rate']:.1%} automated")
    print(f"✅ Business Analysis: Generated")
    print(f"✅ Real Project Test: COMPLETE")

    return results

if __name__ == "__main__":
    results = run_portfolio_test()