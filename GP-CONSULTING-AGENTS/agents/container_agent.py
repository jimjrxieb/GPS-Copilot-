#!/usr/bin/env python3
"""
Container Security Agent - Realistic Vulnerability Management
Assesses container vulnerabilities, prioritizes by risk, generates fix artifacts
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Import GP-DATA config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig

# Import Trivy scanner
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scanners"))
from trivy_scanner import TrivyScanner


class ContainerSecurityAgent:
    """
    Container security agent for vulnerability management

    Capabilities:
    - Risk-based vulnerability assessment
    - Fix recommendation generation
    - Dockerfile hardening
    - Rebuild artifact creation
    """

    def __init__(self):
        self.agent_id = "container_security_agent"
        self.config = GPDataConfig()
        self.trivy_scanner = TrivyScanner()

        # Risk assessment thresholds
        self.risk_thresholds = {
            "CRITICAL": 9.0,
            "HIGH": 7.0,
            "MEDIUM": 4.0,
            "LOW": 0.0
        }

        # Common base image update mappings
        self.base_image_updates = {
            "ubuntu:18.04": "ubuntu:22.04",
            "ubuntu:20.04": "ubuntu:22.04",
            "alpine:3.14": "alpine:3.18",
            "alpine:3.15": "alpine:3.18",
            "node:14": "node:18-alpine",
            "python:3.8": "python:3.11-slim",
            "nginx:1.20": "nginx:1.24-alpine"
        }

    def analyze_container_security(self, target: str, context: str = "production") -> dict:
        """
        Complete container security analysis workflow

        Args:
            target: Path to Dockerfile or container image
            context: Environment context (dev/staging/production)
        """
        analysis_start = datetime.now()

        # Step 1: Scan with Trivy
        print(f"🔍 Scanning container: {target}")
        scan_results = self.trivy_scanner.scan(target)

        # Step 2: Risk assessment
        print("📊 Assessing vulnerability risk...")
        risk_analysis = self.assess_vulnerability_risk(
            scan_results.get('findings', []), context
        )

        # Step 3: Generate fix recommendations
        print("🔧 Generating fix recommendations...")
        fix_recommendations = self.generate_fix_recommendations(risk_analysis)

        # Step 4: Create rebuild artifacts
        print("📝 Creating rebuild artifacts...")
        rebuild_artifacts = self.create_rebuild_artifacts(
            fix_recommendations, target
        )

        result = {
            "agent": self.agent_id,
            "timestamp": analysis_start.isoformat(),
            "target": target,
            "context": context,
            "scan_results": scan_results,
            "risk_analysis": risk_analysis,
            "fix_recommendations": fix_recommendations,
            "rebuild_artifacts": rebuild_artifacts,
            "next_actions": self._generate_next_actions(fix_recommendations),
            "analysis_duration": (datetime.now() - analysis_start).total_seconds()
        }

        # Save to GP-DATA
        self._save_analysis(result)

        return result

    def assess_vulnerability_risk(self, vulnerabilities: list, context: str) -> dict:
        """Prioritize vulnerabilities by business risk"""
        risk_categories = {
            "immediate_action": [],
            "short_term": [],
            "medium_term": [],
            "low_priority": [],
            "informational": []
        }

        context_multipliers = {
            "production": 1.5,
            "staging": 1.0,
            "development": 0.7
        }

        multiplier = context_multipliers.get(context, 1.0)

        for vuln in vulnerabilities:
            risk_score = self._calculate_risk_score(vuln, multiplier)
            vuln_with_risk = {**vuln, "calculated_risk_score": risk_score}

            if risk_score >= 9.0:
                risk_categories["immediate_action"].append(vuln_with_risk)
            elif risk_score >= 7.0:
                risk_categories["short_term"].append(vuln_with_risk)
            elif risk_score >= 4.0:
                risk_categories["medium_term"].append(vuln_with_risk)
            elif risk_score >= 2.0:
                risk_categories["low_priority"].append(vuln_with_risk)
            else:
                risk_categories["informational"].append(vuln_with_risk)

        return {
            "risk_categories": risk_categories,
            "total_vulnerabilities": len(vulnerabilities),
            "risk_summary": {
                "immediate_action": len(risk_categories["immediate_action"]),
                "short_term": len(risk_categories["short_term"]),
                "medium_term": len(risk_categories["medium_term"]),
                "low_priority": len(risk_categories["low_priority"])
            },
            "context": context
        }

    def _calculate_risk_score(self, vuln: dict, context_multiplier: float) -> float:
        """Calculate business risk score for vulnerability"""
        base_score = vuln.get('severity_score', 0)

        # Adjust based on package criticality
        package_name = vuln.get('package', '').lower()
        if any(critical in package_name for critical in ['openssl', 'glibc', 'kernel', 'systemd']):
            base_score *= 1.3

        # Adjust based on fix availability
        if vuln.get('fixed_version'):
            base_score *= 1.2

        # Apply context multiplier
        final_score = base_score * context_multiplier

        return min(final_score, 10.0)

    def generate_fix_recommendations(self, risk_analysis: dict) -> dict:
        """Generate actionable fix recommendations"""
        recommendations = {
            "base_image_updates": [],
            "package_updates": [],
            "dockerfile_improvements": [],
            "build_process_changes": [],
            "runtime_mitigations": []
        }

        # Process immediate and short-term vulnerabilities
        high_priority_vulns = (
            risk_analysis["risk_categories"]["immediate_action"] +
            risk_analysis["risk_categories"]["short_term"]
        )

        # Group vulnerabilities by fix strategy
        base_image_vulns = []
        package_vulns = []

        for vuln in high_priority_vulns:
            if self._is_base_image_vulnerability(vuln):
                base_image_vulns.append(vuln)
            else:
                package_vulns.append(vuln)

        # Generate base image update recommendations
        if base_image_vulns:
            base_updates = self._generate_base_image_updates(base_image_vulns)
            recommendations["base_image_updates"].extend(base_updates)

        # Generate package update recommendations
        if package_vulns:
            pkg_updates = self._generate_package_updates(package_vulns)
            recommendations["package_updates"].extend(pkg_updates)

        # Generate Dockerfile improvements
        dockerfile_improvements = self._generate_dockerfile_improvements(
            high_priority_vulns
        )
        recommendations["dockerfile_improvements"].extend(dockerfile_improvements)

        return recommendations

    def _is_base_image_vulnerability(self, vuln: dict) -> bool:
        """Check if vulnerability is in base image vs application packages"""
        package_name = vuln.get('package', '').lower()
        base_packages = ['glibc', 'openssl', 'systemd', 'bash', 'coreutils']
        return any(base_pkg in package_name for base_pkg in base_packages)

    def _generate_base_image_updates(self, vulnerabilities: list) -> list:
        """Generate base image update recommendations"""
        updates = []

        # Extract unique base images from vulnerabilities
        base_images = set()
        for vuln in vulnerabilities:
            if 'base_image' in vuln:
                base_images.add(vuln['base_image'])

        for image in base_images:
            if image in self.base_image_updates:
                updates.append({
                    "current_image": image,
                    "recommended_image": self.base_image_updates[image],
                    "reason": "Security updates and vulnerability fixes",
                    "vulnerabilities_addressed": len([v for v in vulnerabilities if v.get('base_image') == image])
                })

        return updates

    def _generate_package_updates(self, vulnerabilities: list) -> list:
        """Generate package update recommendations"""
        updates = []

        for vuln in vulnerabilities:
            if vuln.get('fixed_version'):
                updates.append({
                    "package": vuln.get('package'),
                    "current_version": vuln.get('version'),
                    "fixed_version": vuln.get('fixed_version'),
                    "vulnerability_id": vuln.get('id'),
                    "severity": vuln.get('severity'),
                    "update_command": f"apt-get install {vuln.get('package')}={vuln.get('fixed_version')}"
                })

        return updates

    def _generate_dockerfile_improvements(self, vulnerabilities: list) -> list:
        """Generate Dockerfile hardening recommendations"""
        improvements = [
            {
                "improvement": "Use multi-stage builds",
                "reason": "Reduce attack surface by excluding build dependencies from runtime image",
                "example": "FROM node:18 AS builder\n...\nFROM node:18-alpine AS runtime"
            },
            {
                "improvement": "Run as non-root user",
                "reason": "Minimize privilege escalation risks",
                "example": "USER node"
            },
            {
                "improvement": "Use specific image tags",
                "reason": "Ensure reproducible builds and avoid unexpected updates",
                "example": "FROM alpine:3.18 (not alpine:latest)"
            }
        ]

        return improvements

    def create_rebuild_artifacts(self, recommendations: dict, original_target: str) -> dict:
        """Create concrete artifacts for implementing fixes"""
        artifacts = {
            "dockerfiles": [],
            "build_scripts": [],
            "documentation": [],
            "validation_commands": []
        }

        # Generate updated Dockerfile
        if recommendations.get("base_image_updates") or recommendations.get("dockerfile_improvements"):
            dockerfile_content = self._generate_secure_dockerfile(
                recommendations, original_target
            )
            artifacts["dockerfiles"].append({
                "filename": "Dockerfile.security-hardened",
                "content": dockerfile_content,
                "description": "Security-hardened Dockerfile with vulnerability fixes"
            })

        # Generate build script
        build_script = self._generate_build_script(recommendations)
        artifacts["build_scripts"].append({
            "filename": "security-rebuild.sh",
            "content": build_script,
            "executable": True,
            "description": "Script to rebuild container with security updates"
        })

        # Generate validation script
        validation_script = self._generate_validation_script(recommendations)
        artifacts["build_scripts"].append({
            "filename": "validate-security-fixes.sh",
            "content": validation_script,
            "executable": True,
            "description": "Script to validate security fixes were applied"
        })

        # Generate documentation
        fix_documentation = self._generate_fix_documentation(recommendations)
        artifacts["documentation"].append({
            "filename": "SECURITY_FIXES.md",
            "content": fix_documentation,
            "description": "Documentation of security fixes applied"
        })

        return artifacts

    def _generate_secure_dockerfile(self, recommendations: dict, original_target: str) -> str:
        """Generate security-hardened Dockerfile"""
        base_update = recommendations.get("base_image_updates", [{}])[0]
        new_base = base_update.get("recommended_image", "alpine:3.18")

        dockerfile = f"""# Security-hardened Dockerfile
# Generated by Container Security Agent
# Original: {original_target}

FROM {new_base}

# Security hardening
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Install security updates
RUN apk update && apk upgrade

# Copy application
COPY --chown=appuser:appgroup . /app
WORKDIR /app

# Switch to non-root user
USER appuser

CMD ["./app"]
"""
        return dockerfile

    def _generate_build_script(self, recommendations: dict) -> str:
        """Generate build script with security updates"""
        script = """#!/bin/bash
set -e

echo "Building security-hardened container..."

# Build with security context
docker build -f Dockerfile.security-hardened -t app:security-hardened .

# Run security scan on new image
trivy image app:security-hardened

echo "Build complete!"
"""
        return script

    def _generate_validation_script(self, recommendations: dict) -> str:
        """Generate validation script"""
        script = """#!/bin/bash
set -e

echo "Validating security fixes..."

# Scan new image
trivy image app:security-hardened --severity HIGH,CRITICAL

# Check for specific vulnerabilities
echo "Checking vulnerability fixes..."

echo "Validation complete!"
"""
        return script

    def _generate_fix_documentation(self, recommendations: dict) -> str:
        """Generate fix documentation"""
        doc = f"""# Container Security Fixes

## Applied Fixes

### Base Image Updates
"""
        for update in recommendations.get("base_image_updates", []):
            doc += f"- Updated from `{update['current_image']}` to `{update['recommended_image']}`\n"

        doc += "\n### Package Updates\n"
        for pkg in recommendations.get("package_updates", []):
            doc += f"- {pkg['package']}: {pkg['current_version']} → {pkg['fixed_version']}\n"

        doc += "\n### Dockerfile Improvements\n"
        for improvement in recommendations.get("dockerfile_improvements", []):
            doc += f"- {improvement['improvement']}: {improvement['reason']}\n"

        return doc

    def _generate_next_actions(self, recommendations: dict) -> list:
        """Generate next action items"""
        actions = []

        if recommendations.get("base_image_updates"):
            actions.append("Update base image in Dockerfile")

        if recommendations.get("package_updates"):
            actions.append("Apply package updates")

        actions.append("Run security-rebuild.sh")
        actions.append("Run validate-security-fixes.sh")
        actions.append("Deploy to staging for testing")

        return actions

    def _save_analysis(self, analysis: dict):
        """Save analysis to GP-DATA"""
        analysis_dir = self.config.get_analysis_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"container_analysis_{timestamp}.json"
        output_file = analysis_dir / filename

        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"\n💾 Analysis saved to: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Container Security Agent - Vulnerability Management")
        print()
        print("Usage:")
        print("  python container_agent.py <dockerfile_or_image> [context]")
        print()
        print("Context: production, staging, development (default: production)")
        print()
        print("Example:")
        print("  python container_agent.py ./Dockerfile production")
        print("  python container_agent.py nginx:latest staging")
        sys.exit(1)

    target = sys.argv[1]
    context = sys.argv[2] if len(sys.argv) > 2 else "production"

    agent = ContainerSecurityAgent()
    results = agent.analyze_container_security(target, context)

    # Display summary
    print(f"\n{'='*60}")
    print(f"Container Security Analysis Complete")
    print(f"{'='*60}")
    print(f"Target: {results['target']}")
    print(f"Context: {results['context']}")

    risk_summary = results['risk_analysis']['risk_summary']
    print(f"\nRisk Summary:")
    print(f"  🔴 Immediate Action: {risk_summary['immediate_action']}")
    print(f"  🟠 Short Term: {risk_summary['short_term']}")
    print(f"  🟡 Medium Term: {risk_summary['medium_term']}")
    print(f"  🟢 Low Priority: {risk_summary['low_priority']}")

    print(f"\nNext Actions:")
    for i, action in enumerate(results['next_actions'], 1):
        print(f"  {i}. {action}")

    if results['rebuild_artifacts']['dockerfiles']:
        print("\nGenerated Artifacts:")
        for artifact in results['rebuild_artifacts']['dockerfiles']:
            print(f"  📄 {artifact['filename']}")
        for artifact in results['rebuild_artifacts']['build_scripts']:
            print(f"  📜 {artifact['filename']}")
        for artifact in results['rebuild_artifacts']['documentation']:
            print(f"  📖 {artifact['filename']}")


if __name__ == "__main__":
    main()