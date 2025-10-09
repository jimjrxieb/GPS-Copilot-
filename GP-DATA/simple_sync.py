#!/usr/bin/env python3
"""
Simple Sync - Manually sync scans and docs to RAG without file watching
Uses ChromaDB's built-in embeddings instead of sentence-transformers
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import chromadb
from chromadb.config import Settings


def sync_knowledge_base():
    """Sync GP-RAG/processed/security-docs/ to troubleshooting collection"""
    print("🔄 Syncing knowledge base (troubleshooting guides) to RAG...")

    # Initialize ChromaDB
    db_path = Path(__file__).parent / "knowledge-base" / "chroma"
    db_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )

    # Get or create troubleshooting collection
    collection = client.get_or_create_collection(
        name="troubleshooting",
        metadata={"description": "Troubleshooting guides for K8s, Terraform, OPA, IaC"}
    )

    # Path to knowledge base
    gp_copilot_root = Path(__file__).parent.parent
    knowledge_dir = gp_copilot_root / "GP-RAG" / "processed" / "security-docs"

    if not knowledge_dir.exists():
        print(f"⚠️  Knowledge base not found: {knowledge_dir}")
        return 0

    # Get all markdown files
    md_files = list(knowledge_dir.glob("*.md"))
    synced_count = 0

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip very small files
            if len(content) < 100:
                continue

            # Chunk large files (split on ## headers)
            chunks = []
            if '##' in content:
                sections = content.split('##')
                title = sections[0].strip()
                for i, section in enumerate(sections[1:], 1):
                    chunk_content = f"## {section.strip()}"
                    if len(chunk_content) > 200:  # Only meaningful chunks
                        chunks.append({
                            'id': f"{md_file.stem}_chunk_{i}",
                            'content': f"{title}\n\n{chunk_content}",
                            'metadata': {
                                'filename': md_file.name,
                                'source': 'knowledge-base',
                                'chunk': i,
                                'type': detect_knowledge_type(md_file.name)
                            }
                        })
            else:
                # Small file, add as single document
                chunks.append({
                    'id': md_file.stem,
                    'content': content,
                    'metadata': {
                        'filename': md_file.name,
                        'source': 'knowledge-base',
                        'type': detect_knowledge_type(md_file.name)
                    }
                })

            # Add chunks to collection
            for chunk in chunks:
                collection.add(
                    ids=[chunk['id']],
                    documents=[chunk['content']],
                    metadatas=[chunk['metadata']]
                )
                synced_count += 1

            print(f"  ✅ {md_file.name} ({len(chunks)} chunks)")

        except Exception as e:
            print(f"  ❌ Failed to sync {md_file.name}: {e}")
            continue

    print(f"\n✅ Synced {synced_count} knowledge chunks from {len(md_files)} files\n")
    return synced_count


def detect_knowledge_type(filename):
    """Detect knowledge type from filename"""
    if 'kubernetes' in filename or 'k8s' in filename:
        return 'kubernetes'
    elif 'terraform' in filename:
        return 'terraform'
    elif 'opa' in filename:
        return 'opa'
    elif 'troubleshoot' in filename:
        return 'troubleshooting'
    elif 'security' in filename:
        return 'security'
    else:
        return 'general'


def sync_scans_to_rag():
    """Sync existing scan files to RAG"""
    print("🔄 Syncing scans to RAG...")

    # Initialize ChromaDB
    db_path = Path(__file__).parent / "knowledge-base" / "chroma"
    db_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )

    # Get or create scan_findings collection
    collection = client.get_or_create_collection(
        name="scan_findings",
        metadata={"description": "Security scan findings"}
    )

    scans_dir = Path(__file__).parent / "active" / "scans"
    if not scans_dir.exists():
        print(f"⚠️  Scans directory not found: {scans_dir}")
        return 0

    # Get all JSON files (skip _latest.json symlinks)
    scan_files = [f for f in scans_dir.glob("*.json") if '_latest' not in f.name]
    scan_files = sorted(scan_files, key=lambda x: x.stat().st_mtime, reverse=True)[:20]  # Latest 20

    synced_count = 0

    for scan_file in scan_files:
        try:
            with open(scan_file, 'r') as f:
                scan_data = json.load(f)

            # Detect scanner
            scanner = detect_scanner(scan_file.name)
            project = scan_data.get('project', scan_file.stem.split('_')[0] if '_' in scan_file.stem else 'unknown')
            timestamp = scan_data.get('timestamp', datetime.now().isoformat())

            # Extract findings
            findings = extract_findings(scan_data, scanner)

            if not findings:
                continue

            # Add to collection (limit to 10 findings per scan file to avoid overload)
            for i, finding in enumerate(findings[:10]):
                doc_id = f"{scanner}_{scan_file.stem}_{i}"
                content = finding_to_text(finding, scanner, project)
                metadata = {
                    "scanner": scanner,
                    "project": project,
                    "timestamp": timestamp,
                    "severity": str(finding.get("severity", "UNKNOWN")),
                    "file": str(finding.get("file", "")),
                    "scan_file": scan_file.name
                }

                collection.add(
                    ids=[doc_id],
                    documents=[content],
                    metadatas=[metadata]
                )

            synced_count += len(findings[:10])
            print(f"  ✅ {scan_file.name}: {min(len(findings), 10)} findings")

        except Exception as e:
            print(f"  ❌ Error syncing {scan_file.name}: {e}")

    print(f"\n✅ Synced {synced_count} findings from {len(scan_files)} scan files\n")
    return synced_count


def sync_docs_to_rag():
    """Sync documentation files to RAG"""
    print("🔄 Syncing documentation to RAG...")

    # Initialize ChromaDB
    db_path = Path(__file__).parent / "knowledge-base" / "chroma"
    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )

    # Get or create documentation collection
    collection = client.get_or_create_collection(
        name="documentation",
        metadata={"description": "Project documentation"}
    )

    docs_dir = Path(__file__).parent.parent / "GP-DOCS"
    if not docs_dir.exists():
        print(f"⚠️  Docs directory not found: {docs_dir}")
        return 0

    # Get all markdown files
    doc_files = list(docs_dir.rglob("*.md"))
    doc_files = sorted(doc_files, key=lambda x: x.stat().st_mtime, reverse=True)[:30]  # Latest 30

    synced_count = 0

    for doc_file in doc_files:
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                continue

            doc_id = f"doc_{doc_file.stem}"
            metadata = {
                "filename": doc_file.name,
                "path": str(doc_file.relative_to(Path(__file__).parent.parent)),
                "category": doc_file.parent.name,
                "timestamp": datetime.now().isoformat()
            }

            # Truncate very long docs
            if len(content) > 5000:
                content = content[:5000] + "\n...[truncated]"

            collection.add(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata]
            )

            synced_count += 1
            print(f"  ✅ {doc_file.name}")

        except Exception as e:
            print(f"  ❌ Error syncing {doc_file.name}: {e}")

    print(f"\n✅ Synced {synced_count} documentation files\n")
    return synced_count


def detect_scanner(filename: str) -> str:
    """Detect scanner from filename"""
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
    return 'unknown'


def extract_findings(scan_data: dict, scanner: str) -> list:
    """Extract findings from scan data"""
    findings = []

    if scanner == 'bandit':
        findings = scan_data.get('results', [])
    elif scanner == 'trivy':
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
        findings = scan_data.get('findings', scan_data.get('results', []))

    return findings


def finding_to_text(finding: dict, scanner: str, project: str) -> str:
    """Convert finding to searchable text"""
    severity = finding.get('severity', finding.get('Severity', 'UNKNOWN'))
    title = finding.get('title', finding.get('Title', finding.get('issue_text', '')))
    description = finding.get('description', finding.get('Description', ''))
    file_path = finding.get('file', finding.get('filename', finding.get('Target', '')))
    line = finding.get('line_number', finding.get('line', finding.get('Line', 0)))

    text_parts = [
        f"Scanner: {scanner}",
        f"Project: {project}",
        f"Severity: {severity}",
        f"Title: {title}" if title else "",
        f"Description: {description}" if description else "",
        f"File: {file_path}" if file_path else "",
        f"Line: {line}" if line else "",
    ]

    return " | ".join([p for p in text_parts if p])


def main():
    """Run simple sync"""
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║  🤖 Simple Sync - Populate RAG Database                      ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    total_scans = sync_scans_to_rag()
    total_docs = sync_docs_to_rag()
    total_knowledge = sync_knowledge_base()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ Total synced: {total_scans + total_docs + total_knowledge} documents")
    print("   - Scan findings:", total_scans)
    print("   - Documentation:", total_docs)
    print("   - Troubleshooting knowledge:", total_knowledge)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\n💡 Now try:")
    print("   jade query \"what security issues did we find\"")
    print("   jade query \"how to fix crashloopbackoff\"")
    print("   jade query \"terraform state lock troubleshooting\"\n")


if __name__ == "__main__":
    main()
