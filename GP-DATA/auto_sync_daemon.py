#!/usr/bin/env python3
"""
GP-Copilot Auto-Sync Daemon
Automatically syncs scan results and documentation to RAG
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add GP-AI to path
sys.path.insert(0, str(Path(__file__).parent.parent / "GP-AI"))
sys.path.insert(0, str(Path(__file__).parent.parent / "GP-PLATFORM" / "james-config"))

from engines.rag_engine import RAGEngine


class ScanSyncHandler(FileSystemEventHandler):
    """Watches GP-DATA/active/scans/ and syncs to RAG"""

    def __init__(self, rag_engine: RAGEngine):
        self.rag = rag_engine
        self.gp_data_root = Path(__file__).parent
        self.processed_files = set()

    def on_created(self, event):
        """Handle new scan file"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process JSON files (scan results)
        if file_path.suffix != '.json':
            return

        # Skip _latest.json symlinks (processed with original file)
        if '_latest.json' in file_path.name:
            return

        # Avoid duplicate processing
        if file_path in self.processed_files:
            return

        print(f"\n🔍 New scan detected: {file_path.name}")
        self.sync_scan_to_rag(file_path)

    def on_modified(self, event):
        """Handle modified scan file"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process JSON files
        if file_path.suffix != '.json':
            return

        # Skip _latest.json symlinks
        if '_latest.json' in file_path.name:
            return

        print(f"\n🔄 Scan updated: {file_path.name}")
        self.sync_scan_to_rag(file_path)

    def sync_scan_to_rag(self, scan_file: Path):
        """Parse scan JSON and index findings into RAG"""
        try:
            # Read scan results
            with open(scan_file, 'r') as f:
                scan_data = json.load(f)

            # Extract metadata
            scanner_name = self.detect_scanner(scan_file.name)
            timestamp = scan_data.get('timestamp', datetime.now().isoformat())
            project = scan_data.get('project', 'unknown')

            # Extract findings
            findings = self.extract_findings(scan_data, scanner_name)

            if not findings:
                print(f"  ⚠️  No findings to index")
                return

            # Prepare documents for RAG
            documents = []
            for i, finding in enumerate(findings):
                # Create searchable text from finding
                content = self.finding_to_text(finding, scanner_name, project)

                documents.append({
                    "id": f"{scanner_name}_{scan_file.stem}_{i}",
                    "content": content,
                    "metadata": {
                        "scanner": scanner_name,
                        "project": project,
                        "timestamp": timestamp,
                        "severity": finding.get("severity", "UNKNOWN"),
                        "file": finding.get("file", ""),
                        "line": finding.get("line", 0),
                        "cwe": finding.get("cwe", ""),
                        "scan_file": str(scan_file.name)
                    }
                })

            # Add to RAG
            print(f"  📝 Indexing {len(documents)} findings into RAG...")
            self.rag.add_security_knowledge("scans", documents)
            print(f"  ✅ Synced to RAG: {len(documents)} findings")

            # Mark as processed
            self.processed_files.add(scan_file)

        except Exception as e:
            print(f"  ❌ Error syncing scan: {e}")

    def detect_scanner(self, filename: str) -> str:
        """Detect scanner type from filename"""
        if 'bandit' in filename:
            return 'bandit'
        elif 'trivy' in filename:
            return 'trivy'
        elif 'semgrep' in filename:
            return 'semgrep'
        elif 'gitleaks' in filename:
            return 'gitleaks'
        elif 'opa' in filename:
            return 'opa'
        elif 'checkov' in filename:
            return 'checkov'
        else:
            return 'unknown'

    def extract_findings(self, scan_data: Dict, scanner: str) -> List[Dict]:
        """Extract findings from scan data (scanner-specific)"""
        findings = []

        if scanner == 'bandit':
            findings = scan_data.get('results', [])
        elif scanner == 'trivy':
            # Trivy has nested structure
            for result in scan_data.get('Results', []):
                findings.extend(result.get('Vulnerabilities', []))
        elif scanner == 'semgrep':
            findings = scan_data.get('results', [])
        elif scanner == 'gitleaks':
            findings = scan_data.get('findings', [])
        elif scanner == 'opa':
            violations = scan_data.get('violations', [])
            findings = [{'violation': v} for v in violations]
        elif scanner == 'checkov':
            findings = scan_data.get('results', {}).get('failed_checks', [])
        else:
            # Generic extraction
            findings = scan_data.get('findings', scan_data.get('results', []))

        return findings

    def finding_to_text(self, finding: Dict, scanner: str, project: str) -> str:
        """Convert finding to searchable text"""

        # Extract common fields
        severity = finding.get('severity', finding.get('Severity', 'UNKNOWN'))
        title = finding.get('title', finding.get('Title', finding.get('issue_text', '')))
        description = finding.get('description', finding.get('Description', ''))
        file_path = finding.get('file', finding.get('filename', finding.get('Target', '')))
        line = finding.get('line_number', finding.get('line', finding.get('Line', 0)))
        cwe = finding.get('cwe', finding.get('CweIDs', []))

        # Build searchable text
        text_parts = [
            f"Scanner: {scanner}",
            f"Project: {project}",
            f"Severity: {severity}",
            f"Title: {title}" if title else "",
            f"Description: {description}" if description else "",
            f"File: {file_path}" if file_path else "",
            f"Line: {line}" if line else "",
            f"CWE: {cwe}" if cwe else "",
        ]

        # Add vulnerability/CVE info for Trivy
        if 'VulnerabilityID' in finding:
            text_parts.append(f"CVE: {finding['VulnerabilityID']}")
            text_parts.append(f"Package: {finding.get('PkgName', '')}")

        # Add policy info for OPA
        if 'violation' in finding:
            text_parts.append(f"Policy Violation: {finding['violation']}")

        return " | ".join([p for p in text_parts if p])


class DocsSyncHandler(FileSystemEventHandler):
    """Watches GP-DOCS/ and syncs to RAG"""

    def __init__(self, rag_engine: RAGEngine):
        self.rag = rag_engine
        self.processed_files = set()

    def on_created(self, event):
        """Handle new documentation file"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process markdown files
        if file_path.suffix != '.md':
            return

        print(f"\n📄 New doc detected: {file_path.name}")
        self.sync_doc_to_rag(file_path)

    def on_modified(self, event):
        """Handle modified documentation file"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if file_path.suffix != '.md':
            return

        print(f"\n🔄 Doc updated: {file_path.name}")
        self.sync_doc_to_rag(file_path)

    def sync_doc_to_rag(self, doc_file: Path):
        """Read markdown and index into RAG"""
        try:
            # Read document
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip empty files
            if not content.strip():
                return

            # Prepare document for RAG
            doc = {
                "id": f"doc_{doc_file.stem}",
                "content": content,
                "metadata": {
                    "filename": doc_file.name,
                    "path": str(doc_file.relative_to(Path(__file__).parent.parent)),
                    "type": "documentation",
                    "timestamp": datetime.now().isoformat(),
                    "category": doc_file.parent.name  # e.g., "reports", "architecture"
                }
            }

            print(f"  📝 Indexing document into RAG...")
            self.rag.add_security_knowledge("docs", [doc])
            print(f"  ✅ Synced to RAG: {doc_file.name}")

            self.processed_files.add(doc_file)

        except Exception as e:
            print(f"  ❌ Error syncing doc: {e}")


class AutoSyncDaemon:
    """Main auto-sync daemon"""

    def __init__(self):
        self.gp_copilot_root = Path(__file__).parent.parent
        self.gp_data_root = self.gp_copilot_root / "GP-DATA"
        self.gp_docs_root = self.gp_copilot_root / "GP-DOCS"

        # Initialize RAG engine
        print("🚀 Initializing RAG Engine...")
        self.rag = RAGEngine()

        # Initialize file watchers
        self.observers = []

    def start(self):
        """Start watching directories"""
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║  🤖 GP-Copilot Auto-Sync Daemon                              ║")
        print("╚════════════════════════════════════════════════════════════════╝\n")

        # Watch GP-DATA/active/scans/
        scans_dir = self.gp_data_root / "active" / "scans"
        if scans_dir.exists():
            print(f"👀 Watching: {scans_dir}")
            scan_handler = ScanSyncHandler(self.rag)
            scan_observer = Observer()
            scan_observer.schedule(scan_handler, str(scans_dir), recursive=False)
            scan_observer.start()
            self.observers.append(scan_observer)
        else:
            print(f"⚠️  Scans directory not found: {scans_dir}")

        # Watch GP-DOCS/
        if self.gp_docs_root.exists():
            print(f"👀 Watching: {self.gp_docs_root}")
            docs_handler = DocsSyncHandler(self.rag)
            docs_observer = Observer()
            docs_observer.schedule(docs_handler, str(self.gp_docs_root), recursive=True)
            docs_observer.start()
            self.observers.append(docs_observer)
        else:
            print(f"⚠️  Docs directory not found: {self.gp_docs_root}")

        print("\n✅ Auto-sync daemon started!")
        print("   - New scans will be indexed automatically")
        print("   - Documentation updates will sync to RAG")
        print("\n💡 Press Ctrl+C to stop\n")

        # Run initial sync
        self.initial_sync()

        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping auto-sync daemon...")
            for observer in self.observers:
                observer.stop()
                observer.join()
            print("✅ Stopped gracefully\n")

    def initial_sync(self):
        """Perform initial sync of existing files"""
        print("🔄 Performing initial sync...\n")

        # Sync existing scans
        scans_dir = self.gp_data_root / "active" / "scans"
        if scans_dir.exists():
            scan_files = list(scans_dir.glob("*.json"))
            # Skip _latest.json files
            scan_files = [f for f in scan_files if '_latest.json' not in f.name]

            if scan_files:
                print(f"📊 Found {len(scan_files)} existing scan files")
                handler = ScanSyncHandler(self.rag)
                for scan_file in scan_files[:10]:  # Limit to 10 most recent
                    handler.sync_scan_to_rag(scan_file)

        # Sync existing docs
        if self.gp_docs_root.exists():
            doc_files = list(self.gp_docs_root.rglob("*.md"))
            if doc_files:
                print(f"\n📚 Found {len(doc_files)} existing documentation files")
                handler = DocsSyncHandler(self.rag)
                for doc_file in doc_files[:20]:  # Limit to 20 docs
                    handler.sync_doc_to_rag(doc_file)

        print("\n✅ Initial sync complete!\n")


def main():
    """Entry point"""
    daemon = AutoSyncDaemon()
    daemon.start()


if __name__ == "__main__":
    main()
