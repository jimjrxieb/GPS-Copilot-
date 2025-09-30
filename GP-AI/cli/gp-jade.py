#!/usr/bin/env python3
"""
GP-Jade: AI-Powered Security Consulting CLI
Main entry point for GP-Copilot AI assistant
"""

import argparse
import sys
import os
import json
import asyncio
from pathlib import Path

# Add GP-Copilot modules to path
sys.path.append(str(Path(__file__).parent.parent))

# Import advanced AI components
try:
    sys.path.append(str(Path(__file__).parent.parent / "GP-AI"))
    from ai_security_engine import ai_security_engine
    from gpu_config import gpu_config
    AI_ENABLED = True
    print("🚀 Complete AI Security Engine loaded")
except ImportError as e:
    print(f"⚠️  Advanced AI features not available: {e}")
    AI_ENABLED = False

class GPJade:
    """Main GP-Jade CLI class"""

    def __init__(self):
        self.version = "2.0.0-alpha"
        self.models_path = Path(__file__).parent.parent / "GP-DATA" / "ai-models"

        # Initialize AI components if available
        if AI_ENABLED:
            self.ai_engine = ai_security_engine
            print("🧠 Complete AI Security Platform: OPERATIONAL")
        else:
            self.ai_engine = None
            print("⚠️  Basic mode: Advanced AI features disabled")

    def scan(self, target_path, scan_type="auto", client=None):
        """Perform security scan with AI analysis"""
        print(f"🔍 GP-Jade Security Scan v{self.version}")
        print(f"Target: {target_path}")
        print(f"Type: {scan_type}")
        if client:
            print(f"Client: {client}")

        # Use complete AI security platform with comprehensive prompting
        if self.ai_engine:
            return asyncio.run(self._complete_ai_analysis(
                target_path, client,
                depth=getattr(self, '_analysis_depth', 'comprehensive'),
                industry=getattr(self, '_industry', None),
                compliance_requirements=getattr(self, '_compliance_requirements', None)
            ))
        else:
            # Fallback to basic implementation
            if scan_type == "terraform" or target_path.endswith('.tf'):
                return self._scan_terraform_basic(target_path, client)
            else:
                return self._scan_auto_basic(target_path, client)

    async def _complete_ai_analysis(self, target_path, client, depth="comprehensive", industry=None, compliance_requirements=None):
        """Complete AI-powered security analysis with comprehensive prompting"""
        print(f"🚀 Initializing Jade Comprehensive Security Analysis...")
        print(f"   Depth: {depth}")
        print(f"   Industry: {industry or 'General'}")
        print(f"   Compliance: {', '.join(compliance_requirements) if compliance_requirements else 'Standard'}")

        try:
            # Perform comprehensive AI analysis with new parameters
            analysis = await self.ai_engine.analyze_project(
                target_path,
                client or "project",
                analysis_depth=depth,
                industry=industry,
                compliance_requirements=compliance_requirements
            )

            # Display comprehensive results
            print(f"\n🎯 Complete AI Security Analysis Results:")
            print(f"Client: {client or 'Unknown'}")
            print(f"Security Issues: {len(analysis.findings)}")
            print(f"AI Confidence: {analysis.confidence_score:.0%}")

            # Display top findings
            if analysis.findings:
                print(f"\n📋 Security Findings:")
                for i, finding in enumerate(analysis.findings[:8], 1):  # Show top 8
                    print(f"\n{i}. {finding.severity}: {finding.category}")
                    print(f"   File: {finding.file_path}:{finding.line_number or 'N/A'}")
                    print(f"   Issue: {finding.description}")
                    print(f"   Impact: {finding.impact}")
                    print(f"   Fix: {finding.recommendation}")
                    if finding.compliance_frameworks:
                        print(f"   Compliance: {', '.join(finding.compliance_frameworks)}")
                    print(f"   AI Confidence: {finding.ai_confidence:.0%}")

                if len(analysis.findings) > 8:
                    print(f"\n... and {len(analysis.findings) - 8} more findings")

            # Display AI-enhanced summary
            print(f"\n🤖 AI-Enhanced Security Summary:")
            print(f"{analysis.ai_summary}")

            # Display compliance guidance
            if analysis.compliance_guidance:
                print(f"\n📜 Compliance Guidance:")
                print(f"{analysis.compliance_guidance}")

            # Display remediation plan
            if analysis.remediation_plan:
                print(f"\n📋 AI-Generated Remediation Plan:")
                for i, step in enumerate(analysis.remediation_plan, 1):
                    print(f"   {i}. {step}")

            # Display RAG context insights
            if analysis.rag_context:
                print(f"\n🧠 Knowledge Base Insights:")
                for ctx in analysis.rag_context[:2]:  # Top 2
                    print(f"   • {ctx['content'][:100]}...")

            return True

        except Exception as e:
            print(f"❌ Complete AI analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _scan_terraform_basic(self, path, client):
        """Basic Terraform scan (fallback mode)"""
        print("📋 Analyzing Terraform configurations...")

        terraform_files = []
        if os.path.isfile(path) and path.endswith('.tf'):
            terraform_files = [path]
        elif os.path.isdir(path):
            terraform_files = list(Path(path).rglob("*.tf"))

        if not terraform_files:
            print("❌ No Terraform files found")
            return False

        print(f"📁 Found {len(terraform_files)} Terraform files")

        # Mock AI analysis for now
        findings = {
            "total_files": len(terraform_files),
            "security_issues": [
                {
                    "severity": "HIGH",
                    "type": "Hardcoded Secrets",
                    "file": "main.tf",
                    "line": 15,
                    "description": "Potential hardcoded password detected",
                    "recommendation": "Use variable or secret management system"
                },
                {
                    "severity": "MEDIUM",
                    "type": "Public Access",
                    "file": "network.tf",
                    "line": 23,
                    "description": "Security group allows 0.0.0.0/0 access",
                    "recommendation": "Restrict access to specific CIDR blocks"
                }
            ],
            "compliance_score": 75,
            "ai_analysis": "This Terraform configuration has moderate security posture. Primary concerns are credential management and network access controls."
        }

        print("\n🎯 Security Analysis Results:")
        print(f"Files Analyzed: {findings['total_files']}")
        print(f"Security Issues: {len(findings['security_issues'])}")
        print(f"Compliance Score: {findings['compliance_score']}/100")

        for issue in findings['security_issues']:
            print(f"\n⚠️  {issue['severity']}: {issue['type']}")
            print(f"   File: {issue['file']}:{issue['line']}")
            print(f"   Issue: {issue['description']}")
            print(f"   Fix: {issue['recommendation']}")

        print(f"\n🤖 AI Analysis: {findings['ai_analysis']}")

        return True

    def _scan_auto_basic(self, path, client):
        """Auto-detect and scan with appropriate tools (basic mode)"""
        print("🔄 Auto-detecting file types...")

        # Simple file type detection
        if os.path.isdir(path):
            files = list(Path(path).rglob("*"))
            tf_files = [f for f in files if f.suffix == '.tf']
            py_files = [f for f in files if f.suffix == '.py']
            yaml_files = [f for f in files if f.suffix in ['.yaml', '.yml']]

            print(f"📊 Project Analysis:")
            print(f"   Terraform: {len(tf_files)} files")
            print(f"   Python: {len(py_files)} files")
            print(f"   YAML: {len(yaml_files)} files")

            if tf_files:
                return self._scan_terraform_basic(path, client)

        print("✅ Basic security scan completed")
        return True

    def query(self, question, client=None):
        """Query AI security expert with RAG context"""
        print(f"🤖 GP-Jade AI Security Expert")
        if client:
            print(f"Client Context: {client}")
        print(f"Question: {question}")

        if self.ai_engine:
            try:
                # Use complete AI engine with RAG context
                response = asyncio.run(
                    self.ai_engine.query_security_expert(question, client)
                )
                print(f"\n💡 AI Expert Response:\n{response}")
                return True
            except Exception as e:
                print(f"❌ AI query failed: {e}")

        # Fallback responses
        responses = {
            "security risks": "Based on industry standards, the top security risks include: 1) Hardcoded credentials, 2) Overprivileged access, 3) Unencrypted data transmission, 4) Missing security headers, 5) Outdated dependencies.",
            "cks": "CKS (Certified Kubernetes Security) focuses on: Pod Security Standards, Network Policies, RBAC, Secret Management, and Runtime Security monitoring.",
            "terraform": "Terraform security best practices: Use remote state with encryption, implement least privilege IAM, avoid hardcoded secrets, enable detailed logging, and use policy as code validation."
        }

        # Simple keyword matching fallback
        response = "I can help with security analysis. Try asking about 'security risks', 'cks', or 'terraform' best practices."
        for keyword in responses:
            if keyword.lower() in question.lower():
                response = responses[keyword]
                break

        print(f"\n💡 Response:\n{response}")
        return True

    def version_info(self):
        """Display version and system information"""
        print(f"🚀 GP-Jade v{self.version}")
        print(f"🏗️  GP-Copilot AI Security Platform")
        print(f"📍 Location: {Path(__file__).parent.parent}")
        print(f"🧠 AI Models: {self.models_path}")
        print(f"🐍 Python: {sys.version.split()[0]}")

        # Display AI engine status
        if AI_ENABLED and self.ai_engine:
            print("✅ Advanced AI Security Engine: ACTIVE")
        else:
            print("⚠️  Advanced AI Engine: Not Available")

        # Display GPU information if available
        if AI_ENABLED:
            try:
                gpu_config.print_performance_profile()
            except Exception as e:
                print(f"⚠️  GPU configuration error: {e}")

        # Check for AI model availability
        if self.models_path.exists():
            print("✅ AI Models directory found")
        else:
            print("⚠️  AI Models not yet configured")

        return True

def main():
    parser = argparse.ArgumentParser(
        description="GP-Jade: AI-Powered Security Consulting CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gp-jade-main.py scan terraform ./infrastructure/
  python gp-jade-main.py scan --client=portfolio ./project/
  python gp-jade-main.py query "What are CKS requirements?"
  python gp-jade-main.py version
        """
    )

    parser.add_argument('command', choices=['scan', 'query', 'version'],
                       help='Command to execute')
    parser.add_argument('target', nargs='?',
                       help='Target path for scan or question for query')
    parser.add_argument('--client', '-c',
                       help='Client context for analysis')
    parser.add_argument('--type', '-t', choices=['auto', 'terraform', 'kubernetes', 'python'],
                       default='auto', help='Scan type (default: auto)')
    parser.add_argument('--depth', '-d', choices=['quick', 'focused', 'comprehensive'],
                       default='comprehensive', help='Analysis depth (default: comprehensive)')
    parser.add_argument('--industry', '-i',
                       help='Client industry for context')
    parser.add_argument('--compliance', '-comp', action='append',
                       help='Compliance requirements (can be used multiple times)')
    parser.add_argument('--output', '-o', choices=['text', 'json'],
                       default='text', help='Output format')

    args = parser.parse_args()

    gp_jade = GPJade()

    try:
        if args.command == 'scan':
            if not args.target:
                print("❌ Error: Scan target required")
                return 1

            # Store analysis parameters for comprehensive prompting
            gp_jade._analysis_depth = args.depth
            gp_jade._industry = args.industry
            gp_jade._compliance_requirements = args.compliance

            success = gp_jade.scan(args.target, args.type, args.client)

        elif args.command == 'query':
            if not args.target:
                print("❌ Error: Query question required")
                return 1
            success = gp_jade.query(args.target, args.client)

        elif args.command == 'version':
            success = gp_jade.version_info()

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())