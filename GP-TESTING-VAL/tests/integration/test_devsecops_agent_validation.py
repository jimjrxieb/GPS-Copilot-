#!/usr/bin/env python3
"""
DevSecOps Agent Validation Test
==============================

Systematic testing of DevSecOps Agent capabilities to verify:
1. Actual CI/CD security analysis vs claimed pipeline expertise
2. Real GitHub Actions/GitLab CI integration vs theoretical templates
3. Security gate implementation vs basic checks
4. Professional DevSecOps deliverable quality

Test Results: Saved to docs/GP-results/devsecops-agent-test-TIMESTAMP.md
"""

import sys
import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/jimmie/linkops-industries/James-OS/guidepoint')

from agents.devsecops_agent.agent import DevSecOpsAgent

class DevSecOpsAgentValidator:
    """Comprehensive validation of DevSecOps Agent capabilities"""

    def __init__(self):
        self.agent = DevSecOpsAgent()
        self.test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "test_metadata": {
                "timestamp": self.test_timestamp,
                "agent_tested": "DevSecOpsAgent",
                "test_purpose": "Validate CI/CD security integration vs claims"
            },
            "pipeline_analysis": {},
            "pipeline_generation": {},
            "security_gates": {},
            "tool_integration": {},
            "professional_grade": {}
        }

    async def test_pipeline_security_analysis(self, test_project: str):
        """Test actual CI/CD pipeline security analysis capabilities"""
        print(f"🚀 Testing DevSecOps Agent pipeline analysis on: {test_project}")

        analysis_result = await self.agent.analyze_pipeline_security(test_project)

        # Analyze what was actually found
        security_gaps = analysis_result.get("security_gaps", [])
        pipeline_files = analysis_result.get("pipeline_files_scanned", [])

        self.results["pipeline_analysis"] = {
            "test_project": test_project,
            "analysis_result": analysis_result,
            "security_gaps_found": len(security_gaps),
            "pipeline_files_scanned": len(pipeline_files),
            "file_coverage": self._analyze_pipeline_file_coverage(test_project, pipeline_files),
            "gap_analysis": self._analyze_security_gaps(security_gaps),
            "ci_cd_detection": self._analyze_cicd_detection(analysis_result)
        }

        print(f"   Found {len(security_gaps)} security gaps")
        print(f"   Scanned {len(pipeline_files)} pipeline files")
        return analysis_result

    def _analyze_pipeline_file_coverage(self, test_project: str, scanned_files: list):
        """Analyze CI/CD pipeline file coverage in the project"""
        project_path = Path(test_project)

        # Count actual CI/CD files in project
        cicd_patterns = [
            ".github/workflows/*.yml",
            ".github/workflows/*.yaml",
            ".gitlab-ci.yml",
            "Jenkinsfile",
            "azure-pipelines.yml",
            "buildspec.yml",
            ".circleci/config.yml"
        ]

        actual_cicd_files = []
        if project_path.exists():
            for pattern in cicd_patterns:
                actual_cicd_files.extend(list(project_path.glob(pattern)))

        return {
            "files_scanned": len(scanned_files),
            "actual_cicd_files_in_project": len(actual_cicd_files),
            "coverage_percentage": (len(scanned_files) / max(1, len(actual_cicd_files))) * 100,
            "cicd_platforms_detected": self._detect_cicd_platforms(actual_cicd_files),
            "scanned_file_paths": scanned_files[:5]  # First 5 for analysis
        }

    def _detect_cicd_platforms(self, cicd_files: list):
        """Detect which CI/CD platforms are present"""
        platforms = []
        for file in cicd_files:
            file_path = str(file)
            if ".github/workflows" in file_path:
                platforms.append("GitHub Actions")
            elif ".gitlab-ci" in file_path:
                platforms.append("GitLab CI")
            elif "Jenkinsfile" in file_path:
                platforms.append("Jenkins")
            elif "azure-pipelines" in file_path:
                platforms.append("Azure DevOps")
            elif "buildspec" in file_path:
                platforms.append("AWS CodeBuild")
            elif ".circleci" in file_path:
                platforms.append("CircleCI")

        return list(set(platforms))

    def _analyze_security_gaps(self, gaps: list):
        """Analyze the quality and specificity of security gaps found"""
        analysis = {
            "severity_distribution": {},
            "gap_categories": {},
            "specificity_indicators": [],
            "quality_score": 0
        }

        for gap in gaps:
            # Analyze severity distribution
            severity = gap.get("severity", "UNKNOWN")
            if severity not in analysis["severity_distribution"]:
                analysis["severity_distribution"][severity] = 0
            analysis["severity_distribution"][severity] += 1

            # Analyze gap categories
            category = gap.get("category", "unknown")
            if category not in analysis["gap_categories"]:
                analysis["gap_categories"][category] = 0
            analysis["gap_categories"][category] += 1

            # Check for specificity indicators
            if gap.get("file"):
                analysis["specificity_indicators"].append("file_location_provided")
            if gap.get("remediation"):
                analysis["specificity_indicators"].append("remediation_guidance")
            if gap.get("security_control"):
                analysis["specificity_indicators"].append("security_control_mapped")

        # Calculate quality score
        quality_score = 0
        if len(gaps) > 0:
            quality_score += 2
        if "remediation_guidance" in analysis["specificity_indicators"]:
            quality_score += 2
        if "security_control_mapped" in analysis["specificity_indicators"]:
            quality_score += 2
        if len(analysis["severity_distribution"]) > 1:
            quality_score += 1

        analysis["quality_score"] = quality_score

        return analysis

    def _analyze_cicd_detection(self, analysis_result):
        """Analyze CI/CD platform detection capabilities"""
        result_str = str(analysis_result).lower()

        detection_evidence = {
            "github_actions_detected": "github" in result_str and "action" in result_str,
            "gitlab_ci_detected": "gitlab" in result_str,
            "jenkins_detected": "jenkins" in result_str,
            "azure_devops_detected": "azure" in result_str and "pipeline" in result_str,
            "security_scanning_detected": any(tool in result_str for tool in ["sast", "dast", "dependency", "container"]),
            "platform_expertise": []
        }

        # Determine platform expertise level
        if detection_evidence["github_actions_detected"]:
            detection_evidence["platform_expertise"].append("GitHub Actions")
        if detection_evidence["gitlab_ci_detected"]:
            detection_evidence["platform_expertise"].append("GitLab CI")
        if detection_evidence["jenkins_detected"]:
            detection_evidence["platform_expertise"].append("Jenkins")

        return detection_evidence

    async def test_pipeline_generation(self, output_dir: str):
        """Test DevSecOps pipeline generation capabilities"""
        print(f"⚙️ Testing DevSecOps Agent pipeline generation to: {output_dir}")

        pipeline_result = await self.agent.implement_devsecops_pipeline(output_dir)

        # Analyze generated pipeline files
        generated_pipelines = self._analyze_generated_pipelines(output_dir)

        self.results["pipeline_generation"] = {
            "output_directory": output_dir,
            "generation_result": pipeline_result,
            "pipelines_generated": generated_pipelines,
            "pipeline_quality": self._assess_pipeline_quality(output_dir),
            "security_integration": self._assess_security_integration(output_dir),
            "platform_coverage": self._assess_platform_coverage(output_dir)
        }

        print(f"   Generated {len(generated_pipelines)} pipeline files")
        return pipeline_result

    def _analyze_generated_pipelines(self, output_dir: str):
        """Analyze what pipeline files were actually generated"""
        output_path = Path(output_dir)
        generated_pipelines = []

        if output_path.exists():
            pipeline_patterns = [
                "**/*.yml",
                "**/*.yaml",
                "**/Jenkinsfile",
                "**/buildspec.yml"
            ]

            for pattern in pipeline_patterns:
                for file in output_path.glob(pattern):
                    if file.is_file():
                        generated_pipelines.append({
                            "filename": str(file.relative_to(output_path)),
                            "size_bytes": file.stat().st_size,
                            "platform": self._identify_pipeline_platform(file),
                            "content_preview": self._get_pipeline_preview(file)
                        })

        return generated_pipelines

    def _identify_pipeline_platform(self, file_path: Path):
        """Identify which CI/CD platform a pipeline file is for"""
        file_str = str(file_path).lower()
        filename = file_path.name.lower()

        if "github" in file_str or filename.endswith((".yml", ".yaml")) and "workflow" in file_str:
            return "GitHub Actions"
        elif filename == ".gitlab-ci.yml":
            return "GitLab CI"
        elif filename == "jenkinsfile":
            return "Jenkins"
        elif "azure-pipelines" in filename:
            return "Azure DevOps"
        elif filename == "buildspec.yml":
            return "AWS CodeBuild"
        else:
            return "Unknown"

    def _get_pipeline_preview(self, file_path: Path):
        """Get a preview of pipeline file content for analysis"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            preview = {
                "line_count": len(content.split('\n')),
                "security_keywords": [],
                "pipeline_stages": [],
                "tool_integrations": []
            }

            content_lower = content.lower()

            # Check for security keywords
            security_keywords = ["security", "scan", "test", "vulnerability", "sast", "dast", "dependency"]
            for keyword in security_keywords:
                if keyword in content_lower:
                    preview["security_keywords"].append(keyword)

            # Check for pipeline stages
            stage_keywords = ["build", "test", "deploy", "stage", "job", "step"]
            for stage in stage_keywords:
                if stage in content_lower:
                    preview["pipeline_stages"].append(stage)

            # Check for tool integrations
            tools = ["trivy", "bandit", "checkov", "safety", "snyk", "sonarqube", "codeql"]
            for tool in tools:
                if tool in content_lower:
                    preview["tool_integrations"].append(tool)

            return preview

        except Exception as e:
            return {
                "error": str(e),
                "readable": False
            }

    def _assess_pipeline_quality(self, output_dir: str):
        """Assess the quality and completeness of generated pipelines"""
        output_path = Path(output_dir)
        quality_assessment = {
            "total_pipeline_files": 0,
            "valid_pipeline_files": 0,
            "platforms_supported": [],
            "quality_indicators": []
        }

        if not output_path.exists():
            quality_assessment["quality_indicators"].append("Output directory not created")
            return quality_assessment

        pipeline_patterns = ["**/*.yml", "**/*.yaml", "**/Jenkinsfile"]
        for pattern in pipeline_patterns:
            for file in output_path.glob(pattern):
                quality_assessment["total_pipeline_files"] += 1

                platform = self._identify_pipeline_platform(file)
                if platform != "Unknown":
                    quality_assessment["platforms_supported"].append(platform)

                preview = self._get_pipeline_preview(file)
                if not preview.get("error"):
                    quality_assessment["valid_pipeline_files"] += 1

        # Remove duplicates
        quality_assessment["platforms_supported"] = list(set(quality_assessment["platforms_supported"]))

        # Quality indicators
        if quality_assessment["total_pipeline_files"] > 0:
            quality_assessment["quality_indicators"].append(f"Generated {quality_assessment['total_pipeline_files']} pipeline files")

        if quality_assessment["valid_pipeline_files"] == quality_assessment["total_pipeline_files"]:
            quality_assessment["quality_indicators"].append("All pipeline files are readable")

        if quality_assessment["platforms_supported"]:
            quality_assessment["quality_indicators"].append(f"Supports platforms: {', '.join(quality_assessment['platforms_supported'])}")

        return quality_assessment

    def _assess_security_integration(self, output_dir: str):
        """Assess security tool integration in generated pipelines"""
        output_path = Path(output_dir)
        security_assessment = {
            "security_tools_integrated": [],
            "security_stages_present": [],
            "security_gates_implemented": False,
            "security_score": 0
        }

        if output_path.exists():
            for file in output_path.rglob("*"):
                if file.is_file():
                    preview = self._get_pipeline_preview(file)

                    # Collect security tools
                    tools = preview.get("tool_integrations", [])
                    security_assessment["security_tools_integrated"].extend(tools)

                    # Check for security stages
                    keywords = preview.get("security_keywords", [])
                    security_assessment["security_stages_present"].extend(keywords)

                    # Check for security gates
                    if any(gate in keywords for gate in ["security", "gate", "approval"]):
                        security_assessment["security_gates_implemented"] = True

        # Remove duplicates
        security_assessment["security_tools_integrated"] = list(set(security_assessment["security_tools_integrated"]))
        security_assessment["security_stages_present"] = list(set(security_assessment["security_stages_present"]))

        # Calculate security score
        score = 0
        score += len(security_assessment["security_tools_integrated"]) * 2  # 2 points per tool
        score += len(security_assessment["security_stages_present"])  # 1 point per security stage
        if security_assessment["security_gates_implemented"]:
            score += 3  # Bonus for security gates

        security_assessment["security_score"] = score

        return security_assessment

    def _assess_platform_coverage(self, output_dir: str):
        """Assess CI/CD platform coverage"""
        output_path = Path(output_dir)
        coverage_assessment = {
            "github_actions": False,
            "gitlab_ci": False,
            "jenkins": False,
            "azure_devops": False,
            "platform_count": 0
        }

        if output_path.exists():
            for file in output_path.rglob("*"):
                if file.is_file():
                    platform = self._identify_pipeline_platform(file)

                    if platform == "GitHub Actions":
                        coverage_assessment["github_actions"] = True
                    elif platform == "GitLab CI":
                        coverage_assessment["gitlab_ci"] = True
                    elif platform == "Jenkins":
                        coverage_assessment["jenkins"] = True
                    elif platform == "Azure DevOps":
                        coverage_assessment["azure_devops"] = True

        coverage_assessment["platform_count"] = sum(1 for platform in
            ["github_actions", "gitlab_ci", "jenkins", "azure_devops"]
            if coverage_assessment[platform])

        return coverage_assessment

    async def test_tool_integration(self, test_project: str):
        """Test integration with DevSecOps tools"""
        print(f"🔧 Testing DevSecOps Agent tool integration")

        # Check tool availability
        tool_availability = await self._check_devsecops_tool_availability()

        # Test Git integration
        git_test = await self._test_git_integration(test_project)

        self.results["tool_integration"] = {
            "tool_availability": tool_availability,
            "git_integration": git_test,
            "integration_summary": self._summarize_devsecops_integration(tool_availability, git_test)
        }

        return self.results["tool_integration"]

    async def _check_devsecops_tool_availability(self):
        """Check availability of DevSecOps tools"""
        tools = {
            "git": ["git", "--version"],
            "docker": ["docker", "--version"],
            "gh": ["gh", "--version"],  # GitHub CLI
            "glab": ["glab", "--version"],  # GitLab CLI
            "jenkins-cli": ["java", "-jar", "jenkins-cli.jar", "--version"]
        }

        availability = {}
        for tool_name, command in tools.items():
            try:
                import subprocess
                result = subprocess.run(command, capture_output=True, timeout=5)
                availability[tool_name] = result.returncode == 0
            except:
                availability[tool_name] = False

        return availability

    async def _test_git_integration(self, test_project: str):
        """Test Git repository integration capabilities"""
        try:
            import subprocess

            # Check if project is a Git repository
            git_status = subprocess.run(['git', 'status'],
                                      cwd=test_project, capture_output=True, timeout=5)
            is_git_repo = git_status.returncode == 0

            git_test = {
                "git_repository_detected": is_git_repo,
                "git_hooks_analyzable": False,
                "branch_analysis": False
            }

            if is_git_repo:
                # Check for Git hooks
                hooks_dir = Path(test_project) / ".git" / "hooks"
                if hooks_dir.exists():
                    hooks = list(hooks_dir.glob("*"))
                    git_test["git_hooks_analyzable"] = len(hooks) > 0

                # Check branch information
                try:
                    branch_result = subprocess.run(['git', 'branch'],
                                                 cwd=test_project, capture_output=True, timeout=5)
                    git_test["branch_analysis"] = branch_result.returncode == 0
                except:
                    pass

            return git_test

        except Exception as e:
            return {
                "git_repository_detected": False,
                "error": str(e)
            }

    def _summarize_devsecops_integration(self, availability: dict, git_test: dict):
        """Summarize DevSecOps tool integration status"""
        available_tools = sum(1 for available in availability.values() if available)
        total_tools = len(availability)

        summary = {
            "tools_available": f"{available_tools}/{total_tools}",
            "git_functional": git_test.get("git_repository_detected", False),
            "integration_score": 0
        }

        # Calculate integration score
        score = 0
        if available_tools > 0:
            score += 2
        if availability.get("git", False):
            score += 2
        if availability.get("docker", False):
            score += 2
        if git_test.get("git_repository_detected", False):
            score += 1

        summary["integration_score"] = score

        return summary

    def generate_comprehensive_report(self):
        """Generate detailed markdown report of test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# DevSecOps Agent Validation Test Report
**Generated**: {timestamp}
**Test ID**: devsecops-agent-{self.test_timestamp}

---

## Executive Summary

This report documents comprehensive testing of the DevSecOps Agent to validate CI/CD security integration capabilities against claimed functionality.

### Key Findings

**Pipeline Security Analysis:**
- Security Gaps Found: {self.results['pipeline_analysis'].get('security_gaps_found', 'N/A')}
- Pipeline Files Scanned: {self.results['pipeline_analysis'].get('pipeline_files_scanned', 'N/A')}
- File Coverage: {self.results['pipeline_analysis'].get('file_coverage', {}).get('coverage_percentage', 'N/A'):.1f}%
- CI/CD Platform Detection: {self.results['pipeline_analysis'].get('ci_cd_detection', {}).get('platform_expertise', [])}

**Pipeline Generation:**
- Pipelines Generated: {len(self.results['pipeline_generation'].get('pipelines_generated', []))}
- Platform Coverage: {self.results['pipeline_generation'].get('platform_coverage', {}).get('platform_count', 'N/A')}/4
- Security Score: {self.results['pipeline_generation'].get('security_integration', {}).get('security_score', 'N/A')}

**Tool Integration Status:**
- Available Tools: {self.results['tool_integration'].get('integration_summary', {}).get('tools_available', 'N/A')}
- Git Integration: {self.results['tool_integration'].get('integration_summary', {}).get('git_functional', 'N/A')}
- Integration Score: {self.results['tool_integration'].get('integration_summary', {}).get('integration_score', 'N/A')}/7

---

## Detailed Test Results

### 1. CI/CD Pipeline Security Analysis

**Test Project**: {self.results['pipeline_analysis'].get('test_project', 'N/A')}

**Analysis Results:**
```json
{json.dumps(self.results['pipeline_analysis'], indent=2)}
```

### 2. DevSecOps Pipeline Generation

**Pipeline Generation Results:**
```json
{json.dumps(self.results['pipeline_generation'], indent=2)}
```

### 3. Tool Integration Assessment

**DevSecOps Tool Integration:**
```json
{json.dumps(self.results['tool_integration'], indent=2)}
```

---

## DevSecOps Capability Assessment

{self._generate_devsecops_assessment()}

---

## Security Pipeline Quality Assessment

{self._generate_security_pipeline_assessment()}

---

## Recommendations

{self._generate_devsecops_recommendations()}

---

## Raw Test Data

**Complete Test Results:**
```json
{json.dumps(self.results, indent=2)}
```

---

*Report generated by DevSecOps Agent Validation Test*
*Timestamp: {self.test_timestamp}*
"""
        return report

    def _generate_devsecops_assessment(self):
        """Generate assessment of DevSecOps capabilities"""
        assessment = "**DevSecOps Pipeline Security Capability:**\n\n"

        analysis = self.results.get('pipeline_analysis', {})
        gaps_found = analysis.get('security_gaps_found', 0)
        files_scanned = analysis.get('pipeline_files_scanned', 0)
        coverage = analysis.get('file_coverage', {})

        assessment += f"**Security Gaps Identified**: {gaps_found} pipeline security issues\n"
        assessment += f"**Pipeline Coverage**: {files_scanned} files scanned ({coverage.get('coverage_percentage', 0):.1f}% of CI/CD files)\n"

        # Platform expertise assessment
        cicd_detection = analysis.get('ci_cd_detection', {})
        platforms = cicd_detection.get('platform_expertise', [])

        if platforms:
            assessment += f"**Platform Expertise**: {', '.join(platforms)}\n"
            assessment += "✅ CI/CD Platform Detection: Functional\n"
        else:
            assessment += "❌ CI/CD Platform Detection: No platform expertise detected\n"

        # Gap analysis quality
        gap_analysis = analysis.get('gap_analysis', {})
        quality_score = gap_analysis.get('quality_score', 0)

        assessment += f"\n**Gap Analysis Quality**: {quality_score}/7\n"
        if quality_score >= 5:
            assessment += "✅ Professional Grade: High-quality security gap analysis\n"
        elif quality_score >= 3:
            assessment += "⚠️ Professional Grade: Adequate security gap analysis\n"
        else:
            assessment += "❌ Professional Grade: Poor quality security gap analysis\n"

        return assessment

    def _generate_security_pipeline_assessment(self):
        """Generate assessment of security pipeline generation quality"""
        assessment = "**DevSecOps Pipeline Generation Quality:**\n\n"

        pipeline_gen = self.results.get('pipeline_generation', {})
        pipelines_count = len(pipeline_gen.get('pipelines_generated', []))

        assessment += f"**Pipelines Generated**: {pipelines_count} files\n"

        if pipelines_count == 0:
            assessment += "❌ Pipeline Generation: No pipelines created\n"
            return assessment

        # Platform coverage
        platform_coverage = pipeline_gen.get('platform_coverage', {})
        platform_count = platform_coverage.get('platform_count', 0)

        assessment += f"**Platform Coverage**: {platform_count}/4 major CI/CD platforms\n"

        platforms = []
        if platform_coverage.get('github_actions'):
            platforms.append("GitHub Actions")
        if platform_coverage.get('gitlab_ci'):
            platforms.append("GitLab CI")
        if platform_coverage.get('jenkins'):
            platforms.append("Jenkins")
        if platform_coverage.get('azure_devops'):
            platforms.append("Azure DevOps")

        if platforms:
            assessment += f"**Supported Platforms**: {', '.join(platforms)}\n"

        # Security integration
        security_integration = pipeline_gen.get('security_integration', {})
        security_score = security_integration.get('security_score', 0)
        tools_integrated = security_integration.get('security_tools_integrated', [])

        assessment += f"**Security Integration Score**: {security_score}\n"
        if tools_integrated:
            assessment += f"**Security Tools Integrated**: {', '.join(tools_integrated)}\n"
            assessment += "✅ Professional Grade: Security tools properly integrated\n"
        else:
            assessment += "❌ Professional Grade: No security tools integrated\n"

        return assessment

    def _generate_devsecops_recommendations(self):
        """Generate actionable recommendations based on test results"""
        recommendations = []

        # Tool integration recommendations
        tool_integration = self.results.get('tool_integration', {})
        available_tools = tool_integration.get('tool_availability', {})

        if not available_tools.get('git', False):
            recommendations.append("**Install Git**: Essential for DevSecOps workflow automation")

        if not available_tools.get('docker', False):
            recommendations.append("**Install Docker**: Required for containerized security scanning")

        # Pipeline analysis recommendations
        analysis = self.results.get('pipeline_analysis', {})
        coverage = analysis.get('file_coverage', {}).get('coverage_percentage', 0)

        if coverage < 50:
            recommendations.append("**Improve Pipeline Coverage**: Currently analyzing only {:.1f}% of CI/CD files".format(coverage))

        # Pipeline generation recommendations
        pipeline_gen = self.results.get('pipeline_generation', {})
        if len(pipeline_gen.get('pipelines_generated', [])) == 0:
            recommendations.append("**Fix Pipeline Generation**: No CI/CD pipelines were created")

        platform_coverage = pipeline_gen.get('platform_coverage', {}).get('platform_count', 0)
        if platform_coverage < 2:
            recommendations.append("**Expand Platform Support**: Add support for more CI/CD platforms")

        security_score = pipeline_gen.get('security_integration', {}).get('security_score', 0)
        if security_score < 5:
            recommendations.append("**Integrate Security Tools**: Add SAST, DAST, and dependency scanning")

        if not recommendations:
            recommendations.append("**Strong DevSecOps Implementation**: Agent meets CI/CD security requirements")

        recommendations_text = "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))
        return recommendations_text

    async def run_comprehensive_test(self, test_project: str):
        """Run complete DevSecOps Agent validation test suite"""
        print(f"🚀 Starting comprehensive DevSecOps Agent validation test")
        print(f"   Test project: {test_project}")
        print(f"   Test timestamp: {self.test_timestamp}")

        try:
            # Test 1: Pipeline Security Analysis
            await self.test_pipeline_security_analysis(test_project)

            # Test 2: Pipeline Generation
            with tempfile.TemporaryDirectory() as temp_dir:
                await self.test_pipeline_generation(temp_dir)

            # Test 3: Tool Integration
            await self.test_tool_integration(test_project)

            # Generate comprehensive report
            report = self.generate_comprehensive_report()

            # Save report
            report_path = f"/home/jimmie/linkops-industries/James-OS/guidepoint/docs/GP-results/devsecops-agent-test-{self.test_timestamp}.md"
            with open(report_path, 'w') as f:
                f.write(report)

            print(f"✅ Comprehensive DevSecOps test complete")
            print(f"📄 Detailed report saved: {report_path}")

            # Generate summary
            gaps_found = self.results['pipeline_analysis']['security_gaps_found']
            pipelines_generated = len(self.results['pipeline_generation']['pipelines_generated'])
            security_score = self.results['pipeline_generation']['security_integration']['security_score']
            platform_count = self.results['pipeline_generation']['platform_coverage']['platform_count']

            return {
                "test_completed": True,
                "report_path": report_path,
                "summary": {
                    "security_gaps_found": gaps_found,
                    "pipelines_generated": pipelines_generated,
                    "security_score": security_score,
                    "platform_coverage": f"{platform_count}/4",
                    "devsecops_capability": pipelines_generated > 0 or gaps_found > 0,
                    "professional_grade": security_score >= 5 and platform_count >= 2
                }
            }

        except Exception as e:
            error_report = f"""# DevSecOps Agent Test FAILED
**Error**: {str(e)}
**Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

The DevSecOps Agent test encountered a critical error and could not complete.
This indicates fundamental issues with the agent implementation.

**Partial Results**:
```json
{json.dumps(self.results, indent=2)}
```
"""

            error_path = f"/home/jimmie/linkops-industries/James-OS/guidepoint/docs/GP-results/devsecops-agent-FAILED-{self.test_timestamp}.md"
            with open(error_path, 'w') as f:
                f.write(error_report)

            print(f"❌ Test failed: {str(e)}")
            print(f"📄 Error report saved: {error_path}")

            return {
                "test_completed": False,
                "error": str(e),
                "error_report_path": error_path
            }

async def main():
    """Run DevSecOps Agent validation test"""

    # Use the existing test project
    test_project = "/tmp/targeted_vuln_test"

    validator = DevSecOpsAgentValidator()
    result = await validator.run_comprehensive_test(test_project)

    print("\n" + "="*60)
    print("🚀 DEVSECOPS AGENT VALIDATION COMPLETE")
    print("="*60)

    if result["test_completed"]:
        summary = result["summary"]
        print(f"🔍 Security Gaps Found: {summary['security_gaps_found']}")
        print(f"⚙️ Pipelines Generated: {summary['pipelines_generated']}")
        print(f"🛡️ Security Score: {summary['security_score']}")
        print(f"🌐 Platform Coverage: {summary['platform_coverage']}")
        print(f"🚀 DevSecOps Capability: {summary['devsecops_capability']}")
        print(f"👔 Professional Grade: {summary['professional_grade']}")
        print(f"📄 Detailed Report: {result['report_path']}")
    else:
        print(f"❌ Test Failed: {result['error']}")
        print(f"📄 Error Report: {result['error_report_path']}")

if __name__ == "__main__":
    asyncio.run(main())