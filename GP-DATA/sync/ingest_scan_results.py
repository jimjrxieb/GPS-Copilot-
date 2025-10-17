#!/usr/bin/env python3
"""
Scan Results Ingestion - Add ALL GP-DATA Scan Results to RAG + Graph
=====================================================================

Ingests scan findings from GP-DATA/active/scans/ into:
1. ChromaDB (vector embeddings for semantic search)
2. Knowledge Graph (relationships between CVEs, CWEs, findings)

This will add ~18,000+ findings to the RAG system!

Usage:
    python ingest_scan_results.py
    python ingest_scan_results.py --limit 100  # Only first 100 scans
    python ingest_scan_results.py --dry-run
"""

import os
import sys
import json
import pickle
import argparse
import networkx as nx
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Force CPU mode
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-Frontend" / "GP-AI"))
from core.rag_engine import RAGEngine


class ScanResultsIngester:
    """Ingests scan results into RAG + Knowledge Graph"""

    def __init__(self, dry_run: bool = False, limit: int = None):
        self.dry_run = dry_run
        self.limit = limit
        self.rag_engine = None if dry_run else RAGEngine()

        # Load knowledge graph - use calculated absolute path
        gp_copilot_root = Path(__file__).parent.parent.parent
        self.graph_file = gp_copilot_root / "GP-DATA" / "knowledge-base" / "security_graph.pkl"
        self.load_graph()

        # Track used IDs to prevent duplicates
        self.used_ids = set()
        self.id_counter = 0

        self.stats = {
            "scan_files_processed": 0,
            "findings_ingested": 0,
            "graph_nodes_added": 0,
            "graph_edges_added": 0,
            "errors": 0
        }

    def load_graph(self):
        """Load existing knowledge graph"""
        if self.graph_file.exists():
            with open(self.graph_file, 'rb') as f:
                data = pickle.load(f)
                self.graph = data['graph']
                self.node_types = data.get('node_types', {})
            print(f"📂 Loaded graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        else:
            self.graph = nx.MultiDiGraph()
            self.node_types = {}
            print(f"📂 Created new graph")

    def save_graph(self):
        """Save knowledge graph"""
        if self.dry_run:
            return

        with open(self.graph_file, 'wb') as f:
            pickle.dump({
                'graph': self.graph,
                'node_types': self.node_types,
                'last_updated': datetime.now().isoformat()
            }, f)

    def parse_scan_result(self, scan_file: Path) -> List[Dict[str, Any]]:
        """Parse scan result file and extract findings"""
        try:
            with open(scan_file) as f:
                data = json.load(f)

            findings = []

            # Handle different scan formats
            if isinstance(data, dict):
                # Bandit format
                if 'results' in data:
                    for result in data['results']:
                        findings.append({
                            'scanner': 'bandit',
                            'severity': result.get('issue_severity', 'MEDIUM'),
                            'confidence': result.get('issue_confidence', 'MEDIUM'),
                            'cwe': result.get('issue_cwe', {}).get('id', 'unknown'),
                            'title': result.get('issue_text', ''),
                            'file': result.get('filename', ''),
                            'line': result.get('line_number', 0),
                            'code': result.get('code', ''),
                            'test_id': result.get('test_id', '')
                        })

                # Trivy format
                elif 'Results' in data:
                    for result in data['Results']:
                        for vuln in result.get('Vulnerabilities', []):
                            findings.append({
                                'scanner': 'trivy',
                                'severity': vuln.get('Severity', 'UNKNOWN'),
                                'cve': vuln.get('VulnerabilityID', ''),
                                'package': vuln.get('PkgName', ''),
                                'version': vuln.get('InstalledVersion', ''),
                                'fixed_version': vuln.get('FixedVersion', ''),
                                'title': vuln.get('Title', ''),
                                'description': vuln.get('Description', ''),
                                'references': vuln.get('References', [])
                            })

                # Semgrep format
                elif 'findings' in data:
                    for finding in data['findings']:
                        findings.append({
                            'scanner': 'semgrep',
                            'severity': finding.get('severity', 'INFO'),
                            'rule_id': finding.get('rule_id', ''),
                            'message': finding.get('message', ''),
                            'file': finding.get('path', ''),
                            'line': finding.get('line', 0)
                        })

                # Generic format
                elif 'Issues' in data:
                    findings = data['Issues']

            return findings

        except Exception as e:
            print(f"  ❌ Error parsing {scan_file.name}: {e}")
            self.stats["errors"] += 1
            return []

    def finding_to_document(self, finding: Dict, scan_file: Path) -> Dict[str, Any]:
        """Convert finding to RAG document"""
        scanner = finding.get('scanner', 'unknown')

        # Create searchable content
        if scanner == 'bandit':
            content = f"""
Security Finding: {finding.get('title', 'Unknown')}

Scanner: Bandit
Severity: {finding['severity']}
Confidence: {finding.get('confidence', 'MEDIUM')}
CWE: {finding.get('cwe', 'N/A')}
Test ID: {finding.get('test_id', '')}

File: {finding.get('file', '')}
Line: {finding.get('line', 0)}

Code:
{finding.get('code', '')}

Scan: {scan_file.name}
""".strip()

        elif scanner == 'trivy':
            content = f"""
Vulnerability: {finding.get('title', 'Unknown')}

Scanner: Trivy
CVE: {finding.get('cve', '')}
Severity: {finding['severity']}
Package: {finding.get('package', '')} ({finding.get('version', '')})
Fixed Version: {finding.get('fixed_version', 'N/A')}

Description:
{finding.get('description', '')[:500]}

Scan: {scan_file.name}
""".strip()

        else:
            content = json.dumps(finding, indent=2)

        # Generate guaranteed unique ID using counter
        self.id_counter += 1
        unique_id = f"scan_{scan_file.stem}_{self.id_counter:08d}"

        # Ensure no duplicates
        while unique_id in self.used_ids:
            self.id_counter += 1
            unique_id = f"scan_{scan_file.stem}_{self.id_counter:08d}"

        self.used_ids.add(unique_id)

        return {
            'content': content,
            'id': unique_id,
            'metadata': {
                'scanner': scanner,
                'severity': finding.get('severity', 'UNKNOWN'),
                'scan_file': scan_file.name,
                'scan_date': scan_file.stem.split('_')[-1] if '_' in scan_file.stem else 'unknown',
                'type': 'scan_finding',
                'cve': finding.get('cve', ''),
                'cwe': finding.get('cwe', ''),
                'ingested_at': datetime.now().isoformat()
            }
        }

    def add_finding_to_graph(self, finding: Dict, scan_file: Path):
        """Add finding to knowledge graph with relationships"""
        if self.dry_run:
            self.stats["graph_nodes_added"] += 1
            return

        finding_id = f"{scan_file.stem}_{hash(str(finding)) % 1000000}"

        # Add finding node
        self.graph.add_node(
            finding_id,
            type='finding',
            scanner=finding.get('scanner', 'unknown'),
            severity=finding.get('severity', 'UNKNOWN'),
            scan_date=scan_file.stem
        )
        self.stats["graph_nodes_added"] += 1

        # Link to CVE if exists
        cve = finding.get('cve', '')
        if cve and cve.startswith('CVE-'):
            if not self.graph.has_node(cve):
                self.graph.add_node(cve, type='cve')
            self.graph.add_edge(finding_id, cve, type='instance_of')
            self.stats["graph_edges_added"] += 1

        # Link to CWE if exists
        cwe = finding.get('cwe', '')
        if cwe and 'CWE-' in str(cwe):
            cwe_id = f"CWE-{cwe}" if not str(cwe).startswith('CWE-') else str(cwe)
            if not self.graph.has_node(cwe_id):
                self.graph.add_node(cwe_id, type='cwe')
            self.graph.add_edge(finding_id, cwe_id, type='categorized_as')
            self.stats["graph_edges_added"] += 1

    def ingest_scan_file(self, scan_file: Path):
        """Ingest single scan file"""
        print(f"  📄 Processing: {scan_file.name}")

        findings = self.parse_scan_result(scan_file)

        if not findings:
            return

        # Convert findings to documents
        documents = []
        for finding in findings:
            doc = self.finding_to_document(finding, scan_file)
            documents.append(doc)

            # Add to graph
            self.add_finding_to_graph(finding, scan_file)

        # Batch ingest to RAG
        if not self.dry_run and documents:
            try:
                self.rag_engine.add_security_knowledge('scans', documents)
            except Exception as e:
                print(f"    ❌ RAG ingestion error: {e}")
                self.stats["errors"] += 1

        self.stats["scan_files_processed"] += 1
        self.stats["findings_ingested"] += len(findings)

        print(f"    ✅ Ingested {len(findings)} findings")

    def ingest_all_scans(self):
        """Ingest all scan results from GP-DATA"""
        gp_copilot_root = Path(__file__).parent.parent.parent
        scan_dir = gp_copilot_root / "GP-DATA" / "active" / "scans"

        if not scan_dir.exists():
            print(f"❌ Scan directory not found: {scan_dir}")
            return

        # Find all scan JSON files
        scan_files = list(scan_dir.rglob('*.json'))

        if self.limit:
            scan_files = scan_files[:self.limit]

        print(f"\n{'='*60}")
        print(f"🔍 Ingesting Scan Results from GP-DATA")
        print(f"{'='*60}")
        print(f"  Scan files found: {len(scan_files)}")
        if self.limit:
            print(f"  Limit: {self.limit} files")
        print()

        # Process each scan file
        for scan_file in scan_files:
            try:
                self.ingest_scan_file(scan_file)
            except Exception as e:
                print(f"  ❌ Error processing {scan_file.name}: {e}")
                self.stats["errors"] += 1

        # Save graph
        if not self.dry_run:
            print(f"\n💾 Saving knowledge graph...")
            self.save_graph()

        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 Scan Ingestion Summary:")
        print(f"{'='*60}")
        print(f"  Scan files processed: {self.stats['scan_files_processed']}")
        print(f"  Findings ingested: {self.stats['findings_ingested']}")
        print(f"  Graph nodes added: {self.stats['graph_nodes_added']}")
        print(f"  Graph edges added: {self.stats['graph_edges_added']}")
        print(f"  Errors: {self.stats['errors']}")

        if not self.dry_run:
            print(f"\n  Final graph size:")
            print(f"    Total nodes: {self.graph.number_of_nodes()}")
            print(f"    Total edges: {self.graph.number_of_edges()}")

        if self.dry_run:
            print(f"\n🔍 DRY RUN MODE - No changes saved")
        else:
            print(f"\n✅ Scan results ingested into RAG + Knowledge Graph")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest scan results from GP-DATA into RAG + Knowledge Graph"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be ingested"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of scan files to process (for testing)"
    )

    args = parser.parse_args()

    ingester = ScanResultsIngester(dry_run=args.dry_run, limit=args.limit)
    ingester.ingest_all_scans()


if __name__ == "__main__":
    main()
