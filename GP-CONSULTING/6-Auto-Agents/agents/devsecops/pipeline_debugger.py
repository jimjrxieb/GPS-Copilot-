#!/usr/bin/env python3
"""
Pipeline Debugger - Systematically debug and fix failing GitHub Actions pipelines

This module provides automated debugging capabilities for CI/CD pipeline failures.
It follows the workflow documented in CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md
"""

import re
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FixRecommendation:
    """Recommendation for fixing a pipeline failure"""
    solution: str
    yaml_change: Optional[str] = None
    auto_fixable: bool = False
    explanation: str = ""
    code_example: Optional[str] = None


@dataclass
class ErrorAnalysis:
    """Analysis of a pipeline error"""
    error_type: str
    failed_step: str
    evidence: str
    log_excerpt: str
    recommendation: FixRecommendation


class PipelineDebugger:
    """Systematically debug and fix failing GitHub Actions pipelines"""

    def __init__(self, repo: str):
        """
        Initialize debugger for a repository

        Args:
            repo: GitHub repository in format "owner/repo"
        """
        self.repo = repo

    def analyze_and_fix(self) -> Dict:
        """
        Main workflow to analyze pipeline failures and recommend fixes

        Returns:
            Dictionary containing analysis results and fix recommendations
        """
        # Phase 1: Assessment
        recent_runs = self._get_recent_runs()
        failed_runs = [r for r in recent_runs if r.get('conclusion') == 'failure']

        if not failed_runs:
            return {
                'status': 'all_passing',
                'action': 'none',
                'message': '✅ All workflows passing!'
            }

        # Phase 2: Drill down
        latest_failure = failed_runs[0]
        run_id = latest_failure['databaseId']

        failed_jobs = self._get_failed_jobs(run_id)

        if not failed_jobs:
            return {
                'status': 'unknown_failure',
                'run_id': run_id,
                'message': 'Run failed but no failed jobs found. Check manually.'
            }

        # Get detailed step information for each failed job
        analyses = []
        for job in failed_jobs:
            failed_steps = self._get_failed_steps(run_id, job['name'])

            for step in failed_steps:
                # Phase 3: Categorize error
                error_analysis = self._categorize_error(step, job['name'])

                analyses.append(error_analysis)

        return {
            'status': 'failure_detected',
            'run_id': run_id,
            'workflow': latest_failure.get('displayTitle', 'Unknown'),
            'failed_jobs': [j['name'] for j in failed_jobs],
            'analyses': [self._analysis_to_dict(a) for a in analyses],
            'next_steps': self._generate_next_steps(analyses)
        }

    def _get_recent_runs(self, limit: int = 5) -> List[Dict]:
        """Get recent workflow runs"""
        try:
            cmd = [
                'gh', 'run', 'list',
                '--repo', self.repo,
                '--limit', str(limit),
                '--json', 'conclusion,databaseId,displayTitle,workflowName'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error getting runs: {e}")
            return []

    def _get_failed_jobs(self, run_id: int) -> List[Dict]:
        """Get jobs that failed in a run"""
        try:
            cmd = [
                'gh', 'run', 'view', str(run_id),
                '--repo', self.repo,
                '--json', 'jobs'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            jobs = data.get('jobs', [])
            return [j for j in jobs if j.get('conclusion') == 'failure']
        except subprocess.CalledProcessError as e:
            print(f"Error getting jobs: {e}")
            return []

    def _get_failed_steps(self, run_id: int, job_name: str) -> List[Dict]:
        """Get steps that failed in a job"""
        try:
            cmd = [
                'gh', 'run', 'view', str(run_id),
                '--repo', self.repo,
                '--json', 'jobs'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            for job in data.get('jobs', []):
                if job.get('name') == job_name:
                    steps = job.get('steps', [])
                    failed = [s for s in steps if s.get('conclusion') == 'failure']

                    # Get logs for failed steps
                    for step in failed:
                        step['logs'] = self._get_step_logs(run_id, job_name, step['name'])

                    return failed

            return []
        except subprocess.CalledProcessError as e:
            print(f"Error getting steps: {e}")
            return []

    def _get_step_logs(self, run_id: int, job_name: str, step_name: str) -> str:
        """Get logs for a specific step (simplified - gets full failed logs)"""
        try:
            cmd = [
                'gh', 'run', 'view', str(run_id),
                '--repo', self.repo,
                '--log-failed'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            # Return last 1000 characters for analysis
            return result.stdout[-1000:] if result.stdout else ""
        except subprocess.CalledProcessError:
            return ""

    def _categorize_error(self, failed_step: Dict, job_name: str) -> ErrorAnalysis:
        """Categorize error type based on step name and logs"""

        step_name = failed_step.get('name', 'Unknown')
        logs = failed_step.get('logs', '')

        # Error pattern matching
        error_patterns = {
            'missing_secrets': {
                'patterns': [
                    r'Connection timeout',
                    r'Authentication failed',
                    r'Secret.*not found',
                    r'failed to query server',
                    r'401 Unauthorized'
                ],
                'recommendation': FixRecommendation(
                    solution='Make step non-blocking',
                    yaml_change='continue-on-error: true',
                    auto_fixable=True,
                    explanation='Third-party service not configured or requires API key/secret.',
                    code_example='''- name: {step_name}
  continue-on-error: true  # Won't fail pipeline if service unavailable
  uses: some-action@v1
  env:
    API_KEY: ${{{{ secrets.API_KEY }}}}'''
                )
            },
            'security_findings': {
                'patterns': [
                    r'(\d+) CRITICAL vulnerabilities',
                    r'Security scan.*failed',
                    r'Vulnerabilities found'
                ],
                'recommendation': FixRecommendation(
                    solution='Fix vulnerabilities - DO NOT SKIP',
                    auto_fixable=False,
                    explanation='Real security issues found. Must fix code/dependencies. See SECURITY_ACHIEVEMENT.md for CVE remediation workflow.',
                    code_example='# Upgrade dependencies to fix CVEs\n# Example: Spring Boot 2.x → 3.x migration'
                )
            },
            'build_failure': {
                'patterns': [
                    r'cannot find symbol',
                    r'compilation failed',
                    r'package.*does not exist',
                    r'BUILD FAILURE'
                ],
                'recommendation': FixRecommendation(
                    solution='Fix code/compilation issues',
                    auto_fixable=False,
                    explanation='Code compilation error. Check imports, dependencies, breaking changes.',
                    code_example='# Common fixes:\n# 1. Update imports (javax.* → jakarta.*)\n# 2. Fix deprecated APIs\n# 3. Update dependency versions in pom.xml/package.json'
                )
            },
            'test_failure': {
                'patterns': [
                    r'Tests failed',
                    r'maven-surefire-plugin.*failed',
                    r'Test.*FAILED',
                    r'npm.*test.*failed'
                ],
                'recommendation': FixRecommendation(
                    solution='Fix failing tests OR skip temporarily',
                    yaml_change='-DskipTests flag (Maven) or --passWithNoTests (npm)',
                    auto_fixable=True,
                    explanation='Tests failing. Temporary: skip tests. Proper fix: debug and fix test code.',
                    code_example='# Temporary fix:\nmvn package -DskipTests\n\n# Proper fix:\n# 1. Run tests locally: mvn test\n# 2. Debug failures\n# 3. Fix test code'
                )
            },
            'deprecated_action': {
                'patterns': [
                    r'uses a deprecated version',
                    r'deprecated.*action'
                ],
                'recommendation': FixRecommendation(
                    solution='Update action version',
                    auto_fixable=True,
                    explanation='GitHub Action version is deprecated.',
                    code_example='# Change:\n- uses: actions/upload-artifact@v3\n# To:\n- uses: actions/upload-artifact@v4'
                )
            },
            'download_failure': {
                'patterns': [
                    r'Failed to download',
                    r'404 Not Found',
                    r'curl.*failed',
                    r'Connection refused'
                ],
                'recommendation': FixRecommendation(
                    solution='Make download step non-blocking',
                    yaml_change='continue-on-error: true',
                    auto_fixable=True,
                    explanation='External dependency download failed. Making optional if alternative exists.',
                    code_example='''- name: Install Optional Tool
  continue-on-error: true
  run: |
    curl -LO https://example.com/tool.zip
    unzip tool.zip'''
                )
            },
            'job_setup_failure': {
                'patterns': [
                    r'Set up job.*failed',
                    r'Runner.*failed'
                ],
                'recommendation': FixRecommendation(
                    solution='Disable job or configure required secrets',
                    yaml_change='if: false',
                    auto_fixable=True,
                    explanation='Job failing before steps run. Usually missing secrets or runner config.',
                    code_example='''# Option 1: Disable job
{job_name}:
  if: false  # Disable until secrets configured
  runs-on: ubuntu-latest

# Option 2: Add required secrets via:
# gh secret set SECRET_NAME --body "value" --repo owner/repo'''
                )
            }
        }

        # Check each pattern category
        for error_type, config in error_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, logs, re.IGNORECASE) or re.search(pattern, step_name, re.IGNORECASE):
                    recommendation = config['recommendation']

                    # Customize code example with actual step/job name
                    if recommendation.code_example:
                        code_example = recommendation.code_example.replace('{step_name}', step_name)
                        code_example = code_example.replace('{job_name}', job_name)
                        recommendation.code_example = code_example

                    return ErrorAnalysis(
                        error_type=error_type,
                        failed_step=step_name,
                        evidence=pattern,
                        log_excerpt=logs[-500:],  # Last 500 chars
                        recommendation=recommendation
                    )

        # Unknown error type
        return ErrorAnalysis(
            error_type='unknown',
            failed_step=step_name,
            evidence='No matching pattern',
            log_excerpt=logs[-500:],
            recommendation=FixRecommendation(
                solution='Manual investigation required',
                auto_fixable=False,
                explanation='Error type not recognized. Review logs manually.',
                code_example='# Run: gh run view <run-id> --repo owner/repo --log-failed'
            )
        )

    def _analysis_to_dict(self, analysis: ErrorAnalysis) -> Dict:
        """Convert ErrorAnalysis to dictionary"""
        return {
            'error_type': analysis.error_type,
            'failed_step': analysis.failed_step,
            'evidence': analysis.evidence,
            'log_excerpt': analysis.log_excerpt,
            'recommendation': {
                'solution': analysis.recommendation.solution,
                'yaml_change': analysis.recommendation.yaml_change,
                'auto_fixable': analysis.recommendation.auto_fixable,
                'explanation': analysis.recommendation.explanation,
                'code_example': analysis.recommendation.code_example
            }
        }

    def _generate_next_steps(self, analyses: List[ErrorAnalysis]) -> List[str]:
        """Generate actionable next steps"""
        steps = []

        # Categorize by fixability
        auto_fixable = [a for a in analyses if a.recommendation.auto_fixable]
        manual_fixes = [a for a in analyses if not a.recommendation.auto_fixable]

        if auto_fixable:
            steps.append("🔧 Auto-fixable issues found:")
            for analysis in auto_fixable:
                steps.append(f"  - {analysis.failed_step}: {analysis.recommendation.solution}")
                if analysis.recommendation.yaml_change:
                    steps.append(f"    Change: {analysis.recommendation.yaml_change}")

        if manual_fixes:
            steps.append("\n⚠️ Requires manual fixes:")
            for analysis in manual_fixes:
                steps.append(f"  - {analysis.failed_step}: {analysis.recommendation.solution}")

        # Priority guidance
        if any(a.error_type == 'security_findings' for a in analyses):
            steps.append("\n🚨 PRIORITY: Fix security vulnerabilities first!")

        if any(a.error_type == 'build_failure' for a in analyses):
            steps.append("\n⚠️ Fix build failures before addressing optional tools")

        return steps


def main():
    """CLI interface for pipeline debugger"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pipeline_debugger.py <owner/repo>")
        print("Example: python pipeline_debugger.py jimjrxieb/CLOUD-project")
        sys.exit(1)

    repo = sys.argv[1]
    debugger = PipelineDebugger(repo)

    print(f"🔍 Analyzing pipeline failures for {repo}...\n")

    result = debugger.analyze_and_fix()

    if result['status'] == 'all_passing':
        print("✅ All workflows passing! No action needed.")
        return

    print(f"❌ Workflow failure detected: {result.get('workflow', 'Unknown')}")
    print(f"   Run ID: {result['run_id']}")
    print(f"   Failed jobs: {', '.join(result['failed_jobs'])}\n")

    print("=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)

    for i, analysis in enumerate(result['analyses'], 1):
        print(f"\n{i}. {analysis['failed_step']}")
        print(f"   Error Type: {analysis['error_type']}")
        print(f"   Solution: {analysis['recommendation']['solution']}")
        print(f"   Auto-fixable: {'Yes ✅' if analysis['recommendation']['auto_fixable'] else 'No ⚠️'}")
        print(f"\n   {analysis['recommendation']['explanation']}")

        if analysis['recommendation']['code_example']:
            print(f"\n   Code Example:")
            for line in analysis['recommendation']['code_example'].split('\n'):
                print(f"   {line}")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)

    for step in result['next_steps']:
        print(step)

    print("\n📚 See CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md for complete guide")


if __name__ == '__main__':
    main()
