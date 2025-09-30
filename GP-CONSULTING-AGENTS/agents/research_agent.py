#!/usr/bin/env python3
"""
Research & Documentation Agent - Cloud Security Research and Documentation
Researches and documents cloud security best practices, tools, and emerging threats
"""

import subprocess
import json
import sys
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class ResearchDocumentationAgent:
    """
    Research & Documentation Agent for cloud security intelligence

    Capabilities:
    - CVE and security advisory research
    - Documentation generation from findings
    - Best practices compilation
    - Knowledge base maintenance
    - Technical report generation
    """

    def __init__(self):
        self.agent_id = "research_documentation_agent"

        self.config = GPDataConfig()
        self.output_dir = self.config.get_analysis_directory()
        self.docs_dir = self.config.get_deliverable_directory()

        self.confidence_levels = {
            "high": [
                "fetch_cve_data",
                "generate_documentation",
                "create_security_guide",
                "compile_best_practices",
                "format_technical_report"
            ],
            "medium": [
                "threat_intelligence_research",
                "tool_comparison_analysis",
                "emerging_threat_analysis"
            ],
            "low": [
                "predictive_threat_modeling",
                "custom_framework_development",
                "advanced_research_synthesis"
            ]
        }

        self.documentation_templates = self._load_documentation_templates()

    def execute_research_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task based on confidence level"""

        confidence = self._assess_task_confidence(task_type)

        if confidence == "high":
            return self._execute_high_confidence_task(task_type, parameters)
        elif confidence == "medium":
            return self._execute_medium_confidence_task(task_type, parameters)
        else:
            return {
                "success": False,
                "action": "escalate",
                "reason": f"Task {task_type} requires senior researcher guidance",
                "confidence": confidence
            }

    def _execute_high_confidence_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute high-confidence research tasks"""

        if task_type == "fetch_cve_data":
            return self._fetch_cve_data(parameters)
        elif task_type == "generate_documentation":
            return self._generate_documentation(parameters)
        elif task_type == "create_security_guide":
            return self._create_security_guide(parameters)
        elif task_type == "compile_best_practices":
            return self._compile_best_practices(parameters)
        elif task_type == "format_technical_report":
            return self._format_technical_report(parameters)
        else:
            return {"success": False, "error": f"Unknown task: {task_type}"}

    def _execute_medium_confidence_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute medium-confidence tasks with validation"""

        if task_type == "threat_intelligence_research":
            return self._threat_intelligence_research(parameters)
        elif task_type == "tool_comparison_analysis":
            return self._tool_comparison_analysis(parameters)
        else:
            return {
                "success": False,
                "action": "provide_guidance",
                "task": task_type,
                "guidance": f"Task {task_type} requires expert validation",
                "next_steps": [
                    "Review generated research",
                    "Validate sources and findings",
                    "Cross-reference with industry standards",
                    "Get senior researcher approval"
                ]
            }

    def _fetch_cve_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Fetch CVE data from NVD API

        Args:
            cve_id: Specific CVE ID (e.g., CVE-2024-1234)
            keyword: Search keyword
            days: Number of days to look back
        """
        print(f"🔍 Fetching CVE data...")

        cve_id = params.get("cve_id")
        keyword = params.get("keyword")
        days_back = params.get("days", 7)

        cve_data = []

        try:
            if cve_id:
                url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("vulnerabilities"):
                        for vuln in data["vulnerabilities"]:
                            cve_data.append(self._parse_cve_entry(vuln))
                else:
                    return {"success": False, "error": f"NVD API returned {response.status_code}"}

            elif keyword:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)

                url = f"https://services.nvd.nist.gov/rest/json/cves/2.0"
                params_api = {
                    "keywordSearch": keyword,
                    "pubStartDate": start_date.strftime("%Y-%m-%dT00:00:00.000"),
                    "pubEndDate": end_date.strftime("%Y-%m-%dT23:59:59.999")
                }

                response = requests.get(url, params=params_api, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    for vuln in data.get("vulnerabilities", []):
                        cve_data.append(self._parse_cve_entry(vuln))
                else:
                    return {"success": False, "error": f"NVD API returned {response.status_code}"}

            output = {
                "success": True,
                "task": "fetch_cve_data",
                "cve_count": len(cve_data),
                "cve_data": cve_data,
                "search_criteria": {
                    "cve_id": cve_id,
                    "keyword": keyword,
                    "days_back": days_back
                },
                "timestamp": datetime.now().isoformat()
            }

            print(f"   ✅ Found {len(cve_data)} CVE entries")

            self._save_operation("fetch_cve_data", output)
            return output

        except requests.RequestException as e:
            return {"success": False, "task": "fetch_cve_data", "error": f"API request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "task": "fetch_cve_data", "error": str(e)}

    def _parse_cve_entry(self, vuln_data: Dict) -> Dict:
        """Parse CVE entry from NVD API response"""

        cve = vuln_data.get("cve", {})
        cve_id = cve.get("id")

        descriptions = cve.get("descriptions", [])
        description = next((d["value"] for d in descriptions if d.get("lang") == "en"), "No description available")

        metrics = cve.get("metrics", {})
        cvss_v3 = metrics.get("cvssMetricV31", [{}])[0] if metrics.get("cvssMetricV31") else {}
        cvss_data = cvss_v3.get("cvssData", {})

        return {
            "cve_id": cve_id,
            "description": description,
            "published_date": cve.get("published"),
            "last_modified": cve.get("lastModified"),
            "cvss_score": cvss_data.get("baseScore"),
            "cvss_severity": cvss_data.get("baseSeverity"),
            "cvss_vector": cvss_data.get("vectorString"),
            "references": [ref.get("url") for ref in cve.get("references", [])[:5]]
        }

    def _generate_documentation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Generate documentation from findings

        Args:
            findings_file: Path to findings JSON
            doc_type: Type of documentation (security_report, best_practices, technical_guide)
            title: Document title
        """
        print(f"📝 Generating documentation...")

        findings_file = params.get("findings_file")
        doc_type = params.get("doc_type", "security_report")
        title = params.get("title", "Security Documentation")

        if not findings_file or not Path(findings_file).exists():
            return {"success": False, "error": "Findings file required and must exist"}

        try:
            with open(findings_file, 'r') as f:
                findings_data = json.load(f)

            if doc_type == "security_report":
                doc_content = self._generate_security_report(findings_data, title)
            elif doc_type == "best_practices":
                doc_content = self._generate_best_practices_doc(findings_data, title)
            elif doc_type == "technical_guide":
                doc_content = self._generate_technical_guide(findings_data, title)
            else:
                return {"success": False, "error": f"Unknown doc_type: {doc_type}"}

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{doc_type}_{timestamp}.md"
            output_file = self.docs_dir / filename

            with open(output_file, 'w') as f:
                f.write(doc_content)

            output = {
                "success": True,
                "task": "generate_documentation",
                "doc_type": doc_type,
                "output_file": str(output_file),
                "title": title,
                "word_count": len(doc_content.split()),
                "timestamp": datetime.now().isoformat()
            }

            print(f"   ✅ Generated {doc_type}: {output_file}")

            self._save_operation("generate_documentation", output)
            return output

        except Exception as e:
            return {"success": False, "task": "generate_documentation", "error": str(e)}

    def _generate_security_report(self, findings: Dict, title: str) -> str:
        """Generate security report from findings"""

        report = f"""# {title}

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Agent**: {self.agent_id}

---

## Executive Summary

This report presents security findings and recommendations based on automated analysis.

### Key Findings

"""

        if isinstance(findings, dict):
            if "findings" in findings:
                critical_count = len([f for f in findings["findings"] if f.get("severity") == "CRITICAL"])
                high_count = len([f for f in findings["findings"] if f.get("severity") == "HIGH"])

                report += f"- **Critical Issues**: {critical_count}\n"
                report += f"- **High Priority Issues**: {high_count}\n"
                report += f"- **Total Findings**: {len(findings['findings'])}\n\n"

        report += """## Detailed Findings

### Critical Issues

"""

        if isinstance(findings, dict) and "findings" in findings:
            critical_findings = [f for f in findings["findings"] if f.get("severity") == "CRITICAL"]

            for i, finding in enumerate(critical_findings[:5], 1):
                report += f"""#### {i}. {finding.get('id', 'Unknown')}

- **Severity**: {finding.get('severity')}
- **Description**: {finding.get('description', 'N/A')}
- **Location**: {finding.get('file_path', 'N/A')}
- **Recommendation**: {finding.get('recommendation', 'Review and remediate')}

"""

        report += """## Recommendations

1. Address all critical and high-severity findings immediately
2. Implement security best practices outlined in this report
3. Regular security scanning and monitoring
4. Security awareness training for development teams

## Next Steps

1. Review findings with security team
2. Prioritize remediation based on risk
3. Implement fixes and validation
4. Schedule follow-up security assessment

---

*This report was automatically generated by the Research & Documentation Agent.*
"""

        return report

    def _generate_best_practices_doc(self, findings: Dict, title: str) -> str:
        """Generate best practices documentation"""

        doc = f"""# {title}

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Security Best Practices

### 1. Container Security

- Use minimal base images (e.g., Alpine, distroless)
- Run containers as non-root users
- Implement read-only root filesystems
- Drop all unnecessary capabilities
- Regular vulnerability scanning

### 2. Kubernetes Security

- Enable Pod Security Standards (restricted profile)
- Implement NetworkPolicies for microsegmentation
- Use RBAC with least-privilege principle
- Enable audit logging
- Regular security assessments

### 3. Secrets Management

- Never hardcode secrets in code or configuration
- Use dedicated secrets management (Vault, AWS Secrets Manager)
- Implement secret rotation policies
- Encrypt secrets at rest and in transit
- Audit secret access

### 4. CI/CD Security

- Implement security gates in pipelines
- Scan for vulnerabilities before deployment
- Use signed container images
- Implement least-privilege service accounts
- Regular pipeline security audits

### 5. Infrastructure as Code

- Scan IaC templates before deployment
- Use policy-as-code frameworks
- Implement secure defaults
- Version control all infrastructure
- Regular compliance scanning

---

*Best practices compiled from industry standards and security frameworks.*
"""

        return doc

    def _generate_technical_guide(self, findings: Dict, title: str) -> str:
        """Generate technical implementation guide"""

        guide = f"""# {title}

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Technical Implementation Guide

### Prerequisites

- kubectl access to Kubernetes cluster
- Appropriate RBAC permissions
- Security scanning tools installed

### Implementation Steps

#### Step 1: Security Assessment

```bash
# Run comprehensive security scan
./run_security_scan.sh

# Review findings
cat scan_results.json
```

#### Step 2: Apply Security Configurations

```bash
# Apply Pod Security Standards
kubectl apply -f pod-security-standards.yaml

# Apply NetworkPolicies
kubectl apply -f network-policies/

# Configure RBAC
kubectl apply -f rbac/
```

#### Step 3: Validation

```bash
# Verify security configurations
kubectl get psp,networkpolicies,roles,rolebindings

# Test security controls
./validate_security.sh
```

### Troubleshooting

**Issue**: Pods failing with security context errors

**Solution**: Review Pod Security Standards and adjust securityContext

**Issue**: Network connectivity blocked

**Solution**: Review NetworkPolicy rules and add necessary allow rules

---

*Technical guide generated from security findings and best practices.*
"""

        return guide

    def _create_security_guide(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Create security implementation guide

        Args:
            topic: Security topic (kubernetes, container, iac, cicd)
            format: Output format (markdown, pdf, html)
        """
        print(f"📚 Creating security guide...")

        topic = params.get("topic", "kubernetes")
        output_format = params.get("format", "markdown")

        guides = {
            "kubernetes": self._kubernetes_security_guide(),
            "container": self._container_security_guide(),
            "iac": self._iac_security_guide(),
            "cicd": self._cicd_security_guide()
        }

        if topic not in guides:
            return {"success": False, "error": f"Unknown topic: {topic}"}

        guide_content = guides[topic]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{topic}_security_guide_{timestamp}.md"
        output_file = self.docs_dir / filename

        with open(output_file, 'w') as f:
            f.write(guide_content)

        output = {
            "success": True,
            "task": "create_security_guide",
            "topic": topic,
            "output_file": str(output_file),
            "format": output_format,
            "word_count": len(guide_content.split()),
            "timestamp": datetime.now().isoformat()
        }

        print(f"   ✅ Created {topic} security guide: {output_file}")

        self._save_operation("create_security_guide", output)
        return output

    def _kubernetes_security_guide(self) -> str:
        """Generate Kubernetes security guide"""

        return """# Kubernetes Security Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing Kubernetes security best practices.

## Security Controls

### 1. Pod Security Standards

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 2. NetworkPolicy - Default Deny

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### 3. RBAC - Least Privilege

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
```

## Implementation Checklist

- [ ] Enable Pod Security Standards
- [ ] Implement default-deny NetworkPolicies
- [ ] Configure RBAC with least privilege
- [ ] Enable audit logging
- [ ] Regular security scanning

---

*GuidePoint Security - Kubernetes Security Guide*
"""

    def _container_security_guide(self) -> str:
        """Generate container security guide"""

        return """# Container Security Best Practices

## Secure Dockerfile Patterns

### Minimal Base Image

```dockerfile
FROM alpine:3.18

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy application
COPY --chown=appuser:appgroup . /app
WORKDIR /app

# Run as non-root
USER appuser

CMD ["./app"]
```

### Multi-Stage Build

```dockerfile
# Build stage
FROM golang:1.21 AS builder
WORKDIR /build
COPY . .
RUN go build -o app

# Runtime stage
FROM alpine:3.18
RUN adduser -S appuser
COPY --from=builder --chown=appuser /build/app /app
USER appuser
CMD ["/app"]
```

## Security Scanning

```bash
# Scan with Trivy
trivy image myapp:latest

# Scan with Grype
grype myapp:latest
```

---

*GuidePoint Security - Container Security Guide*
"""

    def _iac_security_guide(self) -> str:
        """Generate IaC security guide"""

        return """# Infrastructure as Code Security Guide

## Terraform Security Best Practices

### Secure S3 Bucket

```hcl
resource "aws_s3_bucket" "secure" {
  bucket = var.bucket_name

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "secure" {
  bucket = aws_s3_bucket.secure.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

## Security Scanning

```bash
# Scan with Checkov
checkov -d ./terraform

# Scan with tfsec
tfsec ./terraform
```

---

*GuidePoint Security - IaC Security Guide*
"""

    def _cicd_security_guide(self) -> str:
        """Generate CI/CD security guide"""

        return """# CI/CD Pipeline Security Guide

## GitHub Actions Security Gates

```yaml
name: Security Pipeline

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Secret Scanning
        uses: gitleaks/gitleaks-action@v2

      - name: Dependency Scanning
        run: |
          pip install safety
          safety check

      - name: SAST
        run: |
          pip install bandit
          bandit -r . -f json -o bandit-report.json

      - name: Container Scanning
        run: |
          docker build -t app:latest .
          trivy image app:latest
```

## Security Best Practices

1. Implement security gates that fail builds
2. Scan secrets before commits
3. Vulnerability scanning on all dependencies
4. Container image scanning before push
5. Use signed images in production

---

*GuidePoint Security - CI/CD Security Guide*
"""

    def _compile_best_practices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Compile best practices from multiple sources

        Args:
            domain: Security domain (cloud, kubernetes, container, iac)
        """
        print(f"📋 Compiling best practices...")

        domain = params.get("domain", "cloud")

        best_practices = {
            "cloud": self._cloud_best_practices(),
            "kubernetes": self._kubernetes_best_practices(),
            "container": self._container_best_practices(),
            "iac": self._iac_best_practices()
        }

        if domain not in best_practices:
            return {"success": False, "error": f"Unknown domain: {domain}"}

        practices_content = best_practices[domain]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{domain}_best_practices_{timestamp}.md"
        output_file = self.docs_dir / filename

        with open(output_file, 'w') as f:
            f.write(practices_content)

        output = {
            "success": True,
            "task": "compile_best_practices",
            "domain": domain,
            "output_file": str(output_file),
            "practices_count": len(practices_content.split('\n### ')),
            "timestamp": datetime.now().isoformat()
        }

        print(f"   ✅ Compiled {domain} best practices: {output_file}")

        self._save_operation("compile_best_practices", output)
        return output

    def _cloud_best_practices(self) -> str:
        """Cloud security best practices"""
        return """# Cloud Security Best Practices

## 1. Identity & Access Management
- Implement least-privilege access
- Enable MFA for all users
- Regular access reviews
- Use service accounts for automation

## 2. Data Protection
- Encrypt data at rest and in transit
- Implement data classification
- Regular backup and recovery testing
- Data loss prevention controls

## 3. Network Security
- Implement network segmentation
- Use private subnets for sensitive workloads
- Enable VPC flow logs
- Web application firewalls

## 4. Monitoring & Logging
- Centralized logging
- Real-time alerting
- Security information and event management (SIEM)
- Regular log reviews

## 5. Compliance
- Regular compliance audits
- Automated compliance scanning
- Policy-as-code implementation
- Compliance reporting

---

*Compiled from CIS Benchmarks, AWS Well-Architected Framework, and industry standards*
"""

    def _kubernetes_best_practices(self) -> str:
        """Kubernetes security best practices"""
        return """# Kubernetes Security Best Practices

## 1. Pod Security
- Enforce Pod Security Standards
- Run as non-root
- Read-only root filesystem
- Drop unnecessary capabilities

## 2. Network Security
- Default-deny NetworkPolicies
- Service mesh for mTLS
- Ingress security controls
- Network policy validation

## 3. RBAC
- Least-privilege roles
- No cluster-admin in production
- Regular RBAC audits
- Service account automation

## 4. Secrets Management
- External secrets operators
- Secret encryption at rest
- Secret rotation policies
- No secrets in environment variables

## 5. Runtime Security
- Container runtime security
- Image scanning and signing
- Admission controllers
- Security context enforcement

---

*Compiled from NSA/CISA Kubernetes Hardening Guide and CIS Benchmarks*
"""

    def _container_best_practices(self) -> str:
        """Container security best practices"""
        return """# Container Security Best Practices

## 1. Image Security
- Minimal base images
- Regular vulnerability scanning
- Image signing and verification
- Private registry usage

## 2. Build Security
- Multi-stage builds
- No secrets in images
- Dependency pinning
- Build-time security scanning

## 3. Runtime Security
- Non-root users
- Resource limits
- Security contexts
- Runtime protection

## 4. Registry Security
- Private registries
- Access controls
- Vulnerability scanning
- Image retention policies

---

*Compiled from Docker Security Best Practices and NIST Container Security Guide*
"""

    def _iac_best_practices(self) -> str:
        """IaC security best practices"""
        return """# Infrastructure as Code Security Best Practices

## 1. Code Security
- Version control all IaC
- Code review requirements
- Automated security scanning
- Policy-as-code validation

## 2. State Management
- Encrypted state files
- Remote state backends
- State locking
- Access controls

## 3. Secrets Management
- No hardcoded secrets
- External secret references
- Secret scanning in CI/CD
- Encrypted variable files

## 4. Testing & Validation
- Pre-deployment validation
- Dry-run execution
- Security policy testing
- Compliance scanning

---

*Compiled from Terraform Security Best Practices and CloudFormation Guidelines*
"""

    def _threat_intelligence_research(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        MEDIUM CONFIDENCE: Threat intelligence research

        Args:
            threat_type: Type of threat (ransomware, apt, vulnerability)
            timeframe: Timeframe for research (7, 30, 90 days)
        """
        print(f"🔍 Researching threat intelligence...")

        threat_type = params.get("threat_type", "vulnerability")
        timeframe = params.get("timeframe", 30)

        # This would integrate with threat intel feeds in production
        # For now, provide structured guidance

        intel_report = {
            "success": True,
            "task": "threat_intelligence_research",
            "threat_type": threat_type,
            "timeframe_days": timeframe,
            "research_summary": f"Threat intelligence research for {threat_type} over {timeframe} days",
            "sources": [
                "MITRE ATT&CK",
                "NVD CVE Database",
                "CISA Known Exploited Vulnerabilities",
                "Threat intel feeds (requires integration)"
            ],
            "recommendations": [
                f"Monitor {threat_type} trends",
                "Implement detection rules",
                "Update security controls",
                "Review incident response procedures"
            ],
            "next_steps": [
                "Integrate with threat intel feeds",
                "Automate IOC collection",
                "Create detection signatures",
                "Validate with security team"
            ],
            "timestamp": datetime.now().isoformat()
        }

        print(f"   ⚠️  Research compiled - requires expert validation")

        self._save_operation("threat_intelligence_research", intel_report)
        return intel_report

    def _tool_comparison_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        MEDIUM CONFIDENCE: Security tool comparison analysis

        Args:
            category: Tool category (sast, dast, container_scanning, iac_scanning)
        """
        print(f"⚖️  Analyzing security tools...")

        category = params.get("category", "container_scanning")

        tool_comparisons = {
            "container_scanning": {
                "tools": ["Trivy", "Grype", "Clair", "Snyk"],
                "comparison": {
                    "Trivy": {"accuracy": "High", "speed": "Fast", "ease_of_use": "Easy"},
                    "Grype": {"accuracy": "High", "speed": "Fast", "ease_of_use": "Easy"},
                    "Clair": {"accuracy": "Medium", "speed": "Medium", "ease_of_use": "Complex"},
                    "Snyk": {"accuracy": "High", "speed": "Fast", "ease_of_use": "Easy"}
                },
                "recommendation": "Trivy for comprehensive scanning, Grype for speed"
            },
            "iac_scanning": {
                "tools": ["Checkov", "tfsec", "Terrascan", "KICS"],
                "comparison": {
                    "Checkov": {"coverage": "Extensive", "speed": "Medium", "policies": "Many"},
                    "tfsec": {"coverage": "Good", "speed": "Fast", "policies": "Focused"},
                    "Terrascan": {"coverage": "Good", "speed": "Medium", "policies": "Many"},
                    "KICS": {"coverage": "Extensive", "speed": "Slow", "policies": "Many"}
                },
                "recommendation": "Checkov for comprehensive coverage, tfsec for speed"
            }
        }

        if category not in tool_comparisons:
            return {"success": False, "error": f"Unknown category: {category}"}

        comparison_data = tool_comparisons[category]

        output = {
            "success": True,
            "task": "tool_comparison_analysis",
            "category": category,
            "tools_analyzed": comparison_data["tools"],
            "comparison": comparison_data["comparison"],
            "recommendation": comparison_data["recommendation"],
            "validation_required": True,
            "timestamp": datetime.now().isoformat()
        }

        print(f"   ✅ Tool comparison complete - validation recommended")

        self._save_operation("tool_comparison_analysis", output)
        return output

    def _format_technical_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Format technical report with citations

        Args:
            content: Report content
            title: Report title
            include_citations: Include source citations
        """
        print(f"📄 Formatting technical report...")

        content = params.get("content", "")
        title = params.get("title", "Technical Report")
        include_citations = params.get("include_citations", True)

        if not content:
            return {"success": False, "error": "Report content required"}

        formatted_report = f"""# {title}

**Date**: {datetime.now().strftime("%Y-%m-%d")}
**Author**: Research & Documentation Agent
**Classification**: Internal

---

## Executive Summary

{content}

## Technical Details

{content}

## Recommendations

Based on the analysis, the following recommendations are provided:

1. Implement security controls as outlined
2. Validate configurations before deployment
3. Regular security assessments
4. Continuous monitoring

"""

        if include_citations:
            formatted_report += """
## References

1. NIST Cybersecurity Framework
2. CIS Benchmarks
3. MITRE ATT&CK Framework
4. OWASP Security Guidelines
5. Cloud Security Alliance Best Practices

"""

        formatted_report += f"""
---

*Report generated by Research & Documentation Agent on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"technical_report_{timestamp}.md"
        output_file = self.docs_dir / filename

        with open(output_file, 'w') as f:
            f.write(formatted_report)

        output = {
            "success": True,
            "task": "format_technical_report",
            "output_file": str(output_file),
            "title": title,
            "word_count": len(formatted_report.split()),
            "includes_citations": include_citations,
            "timestamp": datetime.now().isoformat()
        }

        print(f"   ✅ Report formatted: {output_file}")

        self._save_operation("format_technical_report", output)
        return output

    def _assess_task_confidence(self, task_type: str) -> str:
        """Assess confidence level for research task"""

        for level, tasks in self.confidence_levels.items():
            if task_type in tasks:
                return level

        return "low"

    def _load_documentation_templates(self) -> Dict[str, str]:
        """Load documentation templates"""
        return {
            "security_report": "## Security Report\n\n{content}",
            "best_practices": "## Best Practices\n\n{content}",
            "technical_guide": "## Technical Guide\n\n{content}"
        }

    def _save_operation(self, operation_type: str, result: Dict):
        """Save operation results to GP-DATA"""
        operation_id = f"{operation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"
        output_file = self.output_dir / f"{operation_id}.json"

        operation_record = {
            "agent": self.agent_id,
            "operation": operation_type,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }

        with open(output_file, 'w') as f:
            json.dump(operation_record, f, indent=2)

    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status and capabilities"""
        return {
            "agent_id": self.agent_id,
            "confidence_levels": self.confidence_levels,
            "capabilities": [
                "CVE and security advisory research",
                "Documentation generation from findings",
                "Security guide creation",
                "Best practices compilation",
                "Technical report formatting"
            ],
            "output_formats": ["Markdown", "JSON", "HTML (planned)"]
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Research & Documentation Agent - Cloud Security Research")
        print()
        print("HIGH CONFIDENCE Operations:")
        print("  python research_agent.py fetch-cve --cve-id <CVE-ID>")
        print("  python research_agent.py fetch-cve --keyword <keyword> --days <days>")
        print("  python research_agent.py generate-doc --findings <file> --type <type>")
        print("  python research_agent.py create-guide --topic <topic>")
        print("  python research_agent.py compile-practices --domain <domain>")
        print()
        print("MEDIUM CONFIDENCE Operations:")
        print("  python research_agent.py threat-intel --type <threat_type> --days <days>")
        print("  python research_agent.py tool-compare --category <category>")
        print()
        print("Examples:")
        print("  python research_agent.py fetch-cve --keyword kubernetes --days 30")
        print("  python research_agent.py create-guide --topic kubernetes")
        print("  python research_agent.py compile-practices --domain cloud")
        sys.exit(1)

    agent = ResearchDocumentationAgent()
    command = sys.argv[1]

    if command == "fetch-cve":
        params = {"cve_id": None, "keyword": None, "days": 7}

        for arg in sys.argv[2:]:
            if arg.startswith("--cve-id="):
                params["cve_id"] = arg.split("=", 1)[1]
            elif arg.startswith("--keyword="):
                params["keyword"] = arg.split("=", 1)[1]
            elif arg.startswith("--days="):
                params["days"] = int(arg.split("=", 1)[1])

        result = agent._fetch_cve_data(params)

        if result["success"]:
            print(f"\n✅ CVE Data Retrieved:")
            print(f"   Count: {result['cve_count']}")
            for cve in result['cve_data'][:3]:
                print(f"\n   {cve['cve_id']}: {cve['description'][:100]}...")
                print(f"   Severity: {cve['cvss_severity']} ({cve['cvss_score']})")
        else:
            print(f"\n❌ Failed: {result.get('error')}")

    elif command == "create-guide":
        params = {"topic": "kubernetes", "format": "markdown"}

        for arg in sys.argv[2:]:
            if arg.startswith("--topic="):
                params["topic"] = arg.split("=", 1)[1]
            elif arg.startswith("--format="):
                params["format"] = arg.split("=", 1)[1]

        result = agent._create_security_guide(params)

        if result["success"]:
            print(f"\n✅ Security Guide Created:")
            print(f"   File: {result['output_file']}")
            print(f"   Topic: {result['topic']}")
            print(f"   Word Count: {result['word_count']}")

    elif command == "compile-practices":
        params = {"domain": "cloud"}

        for arg in sys.argv[2:]:
            if arg.startswith("--domain="):
                params["domain"] = arg.split("=", 1)[1]

        result = agent._compile_best_practices(params)

        if result["success"]:
            print(f"\n✅ Best Practices Compiled:")
            print(f"   File: {result['output_file']}")
            print(f"   Domain: {result['domain']}")

    elif command == "threat-intel":
        params = {"threat_type": "vulnerability", "timeframe": 30}

        for arg in sys.argv[2:]:
            if arg.startswith("--type="):
                params["threat_type"] = arg.split("=", 1)[1]
            elif arg.startswith("--days="):
                params["timeframe"] = int(arg.split("=", 1)[1])

        result = agent._threat_intelligence_research(params)

        if result["success"]:
            print(f"\n⚠️  Threat Intelligence Research:")
            print(f"   Type: {result['threat_type']}")
            print(f"   Sources: {', '.join(result['sources'])}")
            print(f"\n   Recommendations:")
            for rec in result['recommendations']:
                print(f"   - {rec}")

    elif command == "tool-compare":
        params = {"category": "container_scanning"}

        for arg in sys.argv[2:]:
            if arg.startswith("--category="):
                params["category"] = arg.split("=", 1)[1]

        result = agent._tool_comparison_analysis(params)

        if result["success"]:
            print(f"\n✅ Tool Comparison:")
            print(f"   Category: {result['category']}")
            print(f"   Tools: {', '.join(result['tools_analyzed'])}")
            print(f"   Recommendation: {result['recommendation']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)