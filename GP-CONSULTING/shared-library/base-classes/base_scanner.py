#!/usr/bin/env python3
"""
Base Security Scanner Framework - Production Grade
All scanners inherit from this base class for consistency
"""

import json
import logging
import subprocess
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys


class SecurityScanner(ABC):
    """
    Abstract base class for all security scanners

    Features:
    - Automatic retry with exponential backoff
    - Timeout protection
    - Structured logging (console + file)
    - Metrics emission
    - CWE/CVE enrichment
    - Output validation
    """

    def __init__(self, scan_target: Path, output_dir: Path, timeout: int = 300):
        self.scan_target = Path(scan_target)
        self.output_dir = Path(output_dir)
        self.timeout = timeout
        self.project_root = Path(__file__).parent.parent.parent

        # Setup directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = self.output_dir.parent / 'logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir = self.output_dir.parent / 'metrics'
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = self._setup_logging()

        # Metrics
        self.metrics = {
            'scanner_name': self.get_scanner_name(),
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'exit_code': None,
            'total_issues': 0,
            'severity_breakdown': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0},
            'retry_count': 0,
            'status': 'pending'
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging to console + file"""
        logger = logging.getLogger(self.get_scanner_name())
        logger.setLevel(logging.DEBUG)

        # Console handler (INFO and above)
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console_fmt = logging.Formatter('%(levelname)s - %(message)s')
        console.setFormatter(console_fmt)

        # File handler (DEBUG and above)
        log_file = self.logs_dir / f"{self.get_scanner_name()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_fmt)

        logger.addHandler(console)
        logger.addHandler(file_handler)

        return logger

    def validate_prerequisites(self) -> bool:
        """Check if scanner tool is installed"""
        tool = self.get_tool_name()

        result = subprocess.run(
            ['which', tool],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            self.logger.error(f"{tool} not found in PATH")
            self.logger.info(f"Install with: {self.get_install_instructions()}")
            return False

        self.logger.debug(f"{tool} found at: {result.stdout.strip()}")
        return True

    def run_scan(self) -> bool:
        """
        Run scan with retry logic and exponential backoff
        Returns: True if scan successful, False otherwise
        """
        self.metrics['start_time'] = datetime.now().isoformat()
        start_time = time.time()

        self.logger.info(f"{'='*60}")
        self.logger.info(f"STARTING: {self.get_scanner_name()}")
        self.logger.info(f"Target: {self.scan_target}")
        self.logger.info(f"Timeout: {self.timeout}s")
        self.logger.info(f"{'='*60}")

        # Validate prerequisites
        if not self.validate_prerequisites():
            self.metrics['status'] = 'tool_not_found'
            self._emit_metrics()
            return False

        # Retry logic with exponential backoff
        max_retries = 3
        backoff_base = 2

        for attempt in range(1, max_retries + 1):
            self.metrics['retry_count'] = attempt - 1

            try:
                self.logger.info(f"Attempt {attempt}/{max_retries}")

                # Build command
                output_file = self.output_dir / self.get_output_filename()
                cmd = self.build_command(str(output_file))

                self.logger.debug(f"Command: {' '.join(cmd)}")

                # Execute scan
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=self.project_root
                )

                self.metrics['exit_code'] = result.returncode

                # Log output
                if result.stdout:
                    self.logger.debug(f"STDOUT:\n{result.stdout[:500]}")
                if result.stderr:
                    self.logger.debug(f"STDERR:\n{result.stderr[:500]}")

                # Save STDOUT to output file if it contains JSON
                # Some tools (like Checkov) output to STDOUT instead of a file
                if result.stdout and not output_file.exists():
                    try:
                        # Validate it's JSON before saving
                        json.loads(result.stdout)
                        with open(output_file, 'w') as f:
                            f.write(result.stdout)
                        self.logger.debug(f"Saved STDOUT to: {output_file}")
                    except json.JSONDecodeError:
                        self.logger.debug("STDOUT is not JSON, skipping save")

                # Parse results
                parsed_results = self.parse_results(output_file)

                # Validate output
                if not self._validate_output(parsed_results):
                    raise ValueError("Invalid output format")

                # Save validated results
                self._save_results(output_file, parsed_results)

                # Update metrics
                self._update_metrics(parsed_results)

                # Success
                self.metrics['status'] = 'success'
                self.metrics['end_time'] = datetime.now().isoformat()
                self.metrics['duration_seconds'] = round(time.time() - start_time, 2)

                self.logger.info(f"✅ Scan completed successfully")
                self.logger.info(f"   Total issues: {self.metrics['total_issues']}")
                self.logger.info(f"   Duration: {self.metrics['duration_seconds']}s")

                self._emit_metrics()
                return True

            except subprocess.TimeoutExpired:
                self.logger.warning(f"Scan timeout after {self.timeout}s (attempt {attempt})")

                if attempt < max_retries:
                    wait_time = backoff_base ** attempt
                    self.logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    self.metrics['status'] = 'timeout'
                    self.metrics['end_time'] = datetime.now().isoformat()
                    self._emit_metrics()
                    return False

            except Exception as e:
                self.logger.error(f"Scan failed: {e}", exc_info=True)

                if attempt < max_retries:
                    wait_time = backoff_base ** attempt
                    self.logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    self.metrics['status'] = 'failed'
                    self.metrics['end_time'] = datetime.now().isoformat()
                    self._emit_metrics()
                    return False

        return False

    def _validate_output(self, parsed_results: Dict) -> bool:
        """Validate parsed results have required structure"""
        required_fields = ['findings', 'metadata']

        for field in required_fields:
            if field not in parsed_results:
                self.logger.error(f"Missing required field: {field}")
                return False

        return True

    def _save_results(self, output_file: Path, parsed_results: Dict):
        """Save validated results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(parsed_results, f, indent=2)

        self.logger.info(f"Results saved: {output_file}")

    def _update_metrics(self, parsed_results: Dict):
        """Update metrics from parsed results"""
        findings = parsed_results.get('findings', [])
        self.metrics['total_issues'] = len(findings)

        # Severity breakdown
        for finding in findings:
            severity = finding.get('severity', 'UNKNOWN').upper()
            if severity in self.metrics['severity_breakdown']:
                self.metrics['severity_breakdown'][severity] += 1

    def _emit_metrics(self):
        """Emit metrics to JSON file"""
        metrics_file = self.metrics_dir / f"{self.get_scanner_name()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"

        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)

        self.logger.debug(f"Metrics saved: {metrics_file}")

    # Abstract methods - must be implemented by subclasses

    @abstractmethod
    def get_scanner_name(self) -> str:
        """Return scanner name (e.g., 'bandit', 'semgrep')"""
        pass

    @abstractmethod
    def get_tool_name(self) -> str:
        """Return CLI tool name (e.g., 'bandit', 'semgrep')"""
        pass

    @abstractmethod
    def get_install_instructions(self) -> str:
        """Return installation instructions for the tool"""
        pass

    @abstractmethod
    def get_output_filename(self) -> str:
        """Return output filename (e.g., 'bandit-results.json')"""
        pass

    @abstractmethod
    def build_command(self, output_file: str) -> List[str]:
        """Build scanner command with output file"""
        pass

    @abstractmethod
    def parse_results(self, output_file: Path) -> Dict:
        """
        Parse scanner output and return standardized format:
        {
            'findings': [
                {
                    'severity': 'HIGH',
                    'title': 'SQL Injection',
                    'file': 'app.py',
                    'line': 42,
                    'description': '...',
                    'cwe': ['CWE-89'],
                    'cvss': 7.5
                }
            ],
            'metadata': {
                'scanner': 'bandit',
                'scan_time': '2025-01-09T12:00:00',
                'target': '/path/to/code'
            }
        }
        """
        pass


# CWE Mapping Reference (Bandit test IDs → CWE)
CWE_MAPPINGS = {
    'B608': ['CWE-89'],   # SQL injection
    'B105': ['CWE-798'],  # Hardcoded password
    'B106': ['CWE-798'],  # Hardcoded password function arg
    'B107': ['CWE-798'],  # Hardcoded password default arg
    'B110': ['CWE-703'],  # Try except pass
    'B201': ['CWE-78'],   # Flask debug
    'B301': ['CWE-502'],  # Pickle
    'B303': ['CWE-327'],  # MD5
    'B304': ['CWE-327'],  # SHA1
    'B307': ['CWE-78'],   # eval
    'B311': ['CWE-330'],  # random
    'B324': ['CWE-327'],  # hashlib
    'B501': ['CWE-295'],  # request_with_no_cert_validation
    'B502': ['CWE-295'],  # ssl_with_bad_version
    'B602': ['CWE-78'],   # subprocess_popen_with_shell_equals_true
    'B609': ['CWE-78'],   # linux_commands_wildcard_injection
    'B610': ['CWE-89'],   # django_extra_used
}


def enrich_with_cwe(finding: Dict, test_id: str) -> Dict:
    """Enrich finding with CWE mapping"""
    if test_id in CWE_MAPPINGS:
        finding['cwe'] = CWE_MAPPINGS[test_id]
    return finding
