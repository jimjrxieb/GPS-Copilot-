"""
Scan Graph Integrator - Auto-populate RAG Graph from Security Scans

Reads scan results from Trivy, Bandit, Semgrep, etc. and automatically
populates the security knowledge graph with findings.

This creates the "live intelligence" layer where scan results become
graph nodes that can be queried and reasoned about.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

# Import RAG Graph
try:
    from rag_graph_engine import security_graph
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from rag_graph_engine import security_graph


class ScanGraphIntegrator:
    """Integrates security scan results into knowledge graph"""

    def __init__(self, graph=None):
        self.graph = graph if graph else security_graph
        self.supported_scanners = ["bandit", "trivy", "semgrep", "checkov", "gitleaks"]

    def ingest_scan_file(self, scan_file_path: Path, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest a scan result file and add findings to graph.

        Returns:
            Summary dict with counts of nodes/edges added
        """

        if not scan_file_path.exists():
            raise FileNotFoundError(f"Scan file not found: {scan_file_path}")

        # Load scan results
        with open(scan_file_path, 'r') as f:
            scan_data = json.load(f)

        # Detect scanner type
        scanner = self._detect_scanner(scan_data, scan_file_path)

        if scanner not in self.supported_scanners:
            raise ValueError(f"Unsupported scanner: {scanner}")

        # Auto-detect project from scan data or file path
        if not project_id:
            project_id = self._extract_project_id(scan_data, scan_file_path)

        # Parse findings based on scanner type
        findings = self._parse_findings(scan_data, scanner)

        # Add findings to graph
        stats = self._add_findings_to_graph(findings, scanner, project_id)

        print(f"✅ Ingested {scan_file_path.name}")
        print(f"   Scanner: {scanner}")
        print(f"   Project: {project_id}")
        print(f"   Findings: {stats['findings_added']}")
        print(f"   Nodes added: {stats['nodes_added']}")
        print(f"   Edges added: {stats['edges_added']}")

        return stats

    def _detect_scanner(self, scan_data: Dict, file_path: Path) -> str:
        """Detect which scanner produced this scan file"""

        # Check scan_data for tool field
        if "tool" in scan_data:
            return scan_data["tool"].lower()

        # Check filename
        filename_lower = file_path.name.lower()
        for scanner in self.supported_scanners:
            if scanner in filename_lower:
                return scanner

        # Check data structure patterns
        if "results" in scan_data and isinstance(scan_data.get("results"), list):
            # Bandit format
            return "bandit"

        if "Results" in scan_data:
            # Trivy format
            return "trivy"

        if "results" in scan_data and "paths" in scan_data.get("results", {}):
            # Semgrep format
            return "semgrep"

        return "unknown"

    def _extract_project_id(self, scan_data: Dict, file_path: Path) -> str:
        """Extract project ID from scan data or file path"""

        # Try to get from scan data
        if "target" in scan_data:
            target = Path(scan_data["target"])
            # Get last component of path
            return f"project:{target.name}"

        if "scan_context" in scan_data and "project" in scan_data["scan_context"]:
            return f"project:{scan_data['scan_context']['project']}"

        # Fall back to filename pattern
        # e.g., bandit_LinkOps-MLOps_20250924.json -> project:LinkOps-MLOps
        parts = file_path.stem.split("_")
        if len(parts) >= 2:
            return f"project:{parts[1]}"

        return "project:unknown"

    def _parse_findings(self, scan_data: Dict, scanner: str) -> List[Dict[str, Any]]:
        """Parse findings from scan data based on scanner type"""

        if scanner == "bandit":
            return self._parse_bandit(scan_data)
        elif scanner == "trivy":
            return self._parse_trivy(scan_data)
        elif scanner == "semgrep":
            return self._parse_semgrep(scan_data)
        elif scanner == "checkov":
            return self._parse_checkov(scan_data)
        elif scanner == "gitleaks":
            return self._parse_gitleaks(scan_data)
        else:
            return []

    def _parse_bandit(self, scan_data: Dict) -> List[Dict[str, Any]]:
        """Parse Bandit scan results"""

        findings = []

        for finding in scan_data.get("findings", []):
            # Create unique finding ID
            finding_hash = hashlib.md5(
                f"{finding.get('file')}:{finding.get('line')}:{finding.get('test_id')}".encode()
            ).hexdigest()[:8]

            finding_id = f"finding:bandit-{finding_hash}"

            parsed = {
                "finding_id": finding_id,
                "scanner": "bandit",
                "severity": finding.get("severity", "UNKNOWN").upper(),
                "cwe_id": f"CWE-{finding['cwe']}" if finding.get("cwe") else None,
                "file_path": finding.get("file"),
                "line_number": finding.get("line"),
                "description": finding.get("issue", ""),
                "confidence": finding.get("confidence"),
                "test_id": finding.get("test_id"),
                "code": finding.get("code", ""),
            }

            findings.append(parsed)

        return findings

    def _parse_trivy(self, scan_data: Dict) -> List[Dict[str, Any]]:
        """Parse Trivy scan results"""

        findings = []

        for finding in scan_data.get("findings", []):
            # Trivy findings have CVE IDs
            cve_id = finding.get("VulnerabilityID") or finding.get("cve_id")

            finding_hash = hashlib.md5(
                f"{finding.get('PkgName', 'pkg')}:{cve_id}".encode()
            ).hexdigest()[:8]

            finding_id = f"finding:trivy-{finding_hash}"

            # Map Trivy severity to standard
            severity_map = {
                "CRITICAL": "CRITICAL",
                "HIGH": "HIGH",
                "MEDIUM": "MEDIUM",
                "LOW": "LOW",
                "UNKNOWN": "UNKNOWN"
            }

            parsed = {
                "finding_id": finding_id,
                "scanner": "trivy",
                "severity": severity_map.get(finding.get("Severity", "UNKNOWN"), "UNKNOWN"),
                "cve_id": cve_id,
                "cwe_id": finding.get("CweIDs", [None])[0] if finding.get("CweIDs") else None,
                "file_path": finding.get("Target"),
                "description": finding.get("Title", finding.get("Description", "")),
                "package_name": finding.get("PkgName"),
                "installed_version": finding.get("InstalledVersion"),
                "fixed_version": finding.get("FixedVersion"),
            }

            findings.append(parsed)

        return findings

    def _parse_semgrep(self, scan_data: Dict) -> List[Dict[str, Any]]:
        """Parse Semgrep scan results"""

        findings = []

        for finding in scan_data.get("findings", []):
            finding_hash = hashlib.md5(
                f"{finding.get('path')}:{finding.get('start', {}).get('line')}:{finding.get('check_id')}".encode()
            ).hexdigest()[:8]

            finding_id = f"finding:semgrep-{finding_hash}"

            # Extract CWE from metadata if available
            metadata = finding.get("extra", {}).get("metadata", {})
            cwe_list = metadata.get("cwe", [])
            cwe_id = cwe_list[0] if cwe_list else None

            parsed = {
                "finding_id": finding_id,
                "scanner": "semgrep",
                "severity": finding.get("extra", {}).get("severity", "UNKNOWN").upper(),
                "cwe_id": cwe_id,
                "file_path": finding.get("path"),
                "line_number": finding.get("start", {}).get("line"),
                "description": finding.get("extra", {}).get("message", ""),
                "check_id": finding.get("check_id"),
            }

            findings.append(parsed)

        return findings

    def _parse_checkov(self, scan_data: Dict) -> List[Dict[str, Any]]:
        """Parse Checkov scan results"""

        findings = []

        for finding in scan_data.get("findings", []):
            finding_hash = hashlib.md5(
                f"{finding.get('file_path')}:{finding.get('resource')}:{finding.get('check_id')}".encode()
            ).hexdigest()[:8]

            finding_id = f"finding:checkov-{finding_hash}"

            parsed = {
                "finding_id": finding_id,
                "scanner": "checkov",
                "severity": finding.get("severity", "UNKNOWN").upper(),
                "file_path": finding.get("file_path"),
                "description": finding.get("check_name", ""),
                "check_id": finding.get("check_id"),
                "resource": finding.get("resource"),
            }

            findings.append(parsed)

        return findings

    def _parse_gitleaks(self, scan_data: Dict) -> List[Dict[str, Any]]:
        """Parse Gitleaks scan results"""

        findings = []

        for finding in scan_data.get("findings", []):
            finding_hash = hashlib.md5(
                f"{finding.get('File')}:{finding.get('StartLine')}:{finding.get('RuleID')}".encode()
            ).hexdigest()[:8]

            finding_id = f"finding:gitleaks-{finding_hash}"

            parsed = {
                "finding_id": finding_id,
                "scanner": "gitleaks",
                "severity": "HIGH",  # Secrets are always high severity
                "cwe_id": "CWE-798",  # Use of Hard-coded Credentials
                "file_path": finding.get("File"),
                "line_number": finding.get("StartLine"),
                "description": finding.get("Description", "Secret detected"),
                "secret_type": finding.get("RuleID"),
            }

            findings.append(parsed)

        return findings

    def _add_findings_to_graph(self, findings: List[Dict], scanner: str, project_id: str) -> Dict[str, int]:
        """Add parsed findings to knowledge graph"""

        stats = {
            "findings_added": 0,
            "nodes_added": 0,
            "edges_added": 0
        }

        nodes_before = self.graph.graph.number_of_nodes()
        edges_before = self.graph.graph.number_of_edges()

        for finding in findings:
            # Skip if finding already exists
            if finding["finding_id"] in self.graph.graph:
                continue

            # Add finding to graph
            self.graph.add_finding_from_scan(
                finding_id=finding["finding_id"],
                scanner=scanner,
                severity=finding["severity"],
                cwe_id=finding.get("cwe_id"),
                cve_id=finding.get("cve_id"),
                file_path=finding.get("file_path"),
                line_number=finding.get("line_number"),
                description=finding.get("description"),
                project_id=project_id
            )

            stats["findings_added"] += 1

        nodes_after = self.graph.graph.number_of_nodes()
        edges_after = self.graph.graph.number_of_edges()

        stats["nodes_added"] = nodes_after - nodes_before
        stats["edges_added"] = edges_after - edges_before

        # Save graph
        self.graph.save_graph()

        return stats

    def ingest_scan_directory(self, scan_dir: Path, pattern: str = "*.json") -> Dict[str, Any]:
        """
        Ingest all scan files from a directory.

        Returns:
            Summary statistics
        """

        scan_files = list(scan_dir.glob(pattern))

        total_stats = {
            "files_processed": 0,
            "findings_added": 0,
            "nodes_added": 0,
            "edges_added": 0,
            "errors": []
        }

        print(f"📁 Ingesting scans from {scan_dir}")
        print(f"   Found {len(scan_files)} scan files")

        for scan_file in scan_files:
            try:
                stats = self.ingest_scan_file(scan_file)
                total_stats["files_processed"] += 1
                total_stats["findings_added"] += stats["findings_added"]
                total_stats["nodes_added"] += stats["nodes_added"]
                total_stats["edges_added"] += stats["edges_added"]

            except Exception as e:
                print(f"❌ Error processing {scan_file.name}: {e}")
                total_stats["errors"].append({
                    "file": scan_file.name,
                    "error": str(e)
                })

        print(f"\n✅ Ingestion complete!")
        print(f"   Files processed: {total_stats['files_processed']}")
        print(f"   Findings added: {total_stats['findings_added']}")
        print(f"   Nodes added: {total_stats['nodes_added']}")
        print(f"   Edges added: {total_stats['edges_added']}")

        if total_stats["errors"]:
            print(f"   Errors: {len(total_stats['errors'])}")

        return total_stats


# CLI interface
if __name__ == "__main__":
    import sys

    print("=" * 80)
    print("Scan Graph Integrator - Populate RAG Graph from Scans")
    print("=" * 80)

    integrator = ScanGraphIntegrator()

    # Check for command line args
    if len(sys.argv) > 1:
        scan_path = Path(sys.argv[1])

        if scan_path.is_file():
            # Ingest single file
            print(f"\n📄 Ingesting single scan file: {scan_path}")
            stats = integrator.ingest_scan_file(scan_path)

        elif scan_path.is_dir():
            # Ingest directory
            print(f"\n📁 Ingesting scan directory: {scan_path}")
            stats = integrator.ingest_scan_directory(scan_path)

        else:
            print(f"❌ Path not found: {scan_path}")
            sys.exit(1)

    else:
        # Default: ingest GP-DATA/active/scans
        default_scan_dir = Path(__file__).parent.parent.parent / "GP-DATA" / "active" / "scans"

        if default_scan_dir.exists():
            print(f"\n📁 Ingesting default scan directory: {default_scan_dir}")
            stats = integrator.ingest_scan_directory(default_scan_dir)
        else:
            print(f"❌ Default scan directory not found: {default_scan_dir}")
            print(f"\nUsage: python {Path(__file__).name} <scan_file_or_directory>")
            sys.exit(1)

    print("\n📊 Final Graph Stats:")
    graph_stats = security_graph.get_stats()
    print(f"   Total nodes: {graph_stats['total_nodes']}")
    print(f"   Total edges: {graph_stats['total_edges']}")
    print(f"   Node types: {graph_stats['node_types']}")