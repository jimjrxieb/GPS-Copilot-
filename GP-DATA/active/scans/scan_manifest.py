#!/usr/bin/env python3
"""
Scan Manifest Manager - Track and correlate multi-tool security scans

Provides:
- Scan session tracking across multiple tools
- Historical scan comparison
- Finding correlation and deduplication
- James Brain integration metadata
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib


class ScanManifest:
    """Manage scan sessions and cross-tool correlation"""

    def __init__(self, data_root: Optional[Path] = None):
        if data_root is None:
            data_root = Path("/home/jimmie/linkops-industries/GP-copilot/GP-DATA")

        self.data_root = Path(data_root)
        self.manifest_dir = self.data_root / "scans" / "manifests"
        self.manifest_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, target: str, scanners: List[str], metadata: Optional[Dict] = None) -> str:
        """Create a new scan session"""
        session_id = self._generate_session_id(target)
        timestamp = datetime.now().isoformat()

        session = {
            "session_id": session_id,
            "target": target,
            "timestamp": timestamp,
            "scanners_requested": scanners,
            "scanners_completed": [],
            "status": "in_progress",
            "results": {},
            "metadata": metadata or {},
            "total_findings": 0,
            "severity_breakdown": {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0
            }
        }

        self._save_manifest(session)
        return session_id

    def update_session(self, session_id: str, scanner: str, result_file: str, summary: Dict):
        """Update session with scanner results"""
        manifest = self._load_manifest(session_id)

        if scanner not in manifest["scanners_completed"]:
            manifest["scanners_completed"].append(scanner)

        manifest["results"][scanner] = {
            "result_file": result_file,
            "summary": summary,
            "completed_at": datetime.now().isoformat()
        }

        # Update totals
        if "total" in summary:
            manifest["total_findings"] += summary["total"]

        if "severity_breakdown" in summary:
            for severity, count in summary["severity_breakdown"].items():
                if severity in manifest["severity_breakdown"]:
                    manifest["severity_breakdown"][severity] += count

        # Check if all scanners completed
        if set(manifest["scanners_completed"]) == set(manifest["scanners_requested"]):
            manifest["status"] = "completed"
            manifest["completed_at"] = datetime.now().isoformat()

        self._save_manifest(manifest)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve scan session"""
        return self._load_manifest(session_id)

    def list_sessions(self, target: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """List recent scan sessions"""
        sessions = []

        for manifest_file in sorted(self.manifest_dir.glob("*.json"), reverse=True)[:limit * 2]:
            try:
                with open(manifest_file, 'r') as f:
                    session = json.load(f)

                if target is None or session.get("target") == target:
                    sessions.append(session)

                if len(sessions) >= limit:
                    break
            except Exception:
                continue

        return sessions

    def compare_sessions(self, session_id1: str, session_id2: str) -> Dict:
        """Compare two scan sessions to track progress"""
        session1 = self.get_session(session_id1)
        session2 = self.get_session(session_id2)

        if not session1 or not session2:
            raise ValueError("One or both sessions not found")

        comparison = {
            "session1": {
                "id": session_id1,
                "timestamp": session1["timestamp"],
                "findings": session1["total_findings"],
                "severity": session1["severity_breakdown"]
            },
            "session2": {
                "id": session_id2,
                "timestamp": session2["timestamp"],
                "findings": session2["total_findings"],
                "severity": session2["severity_breakdown"]
            },
            "delta": {
                "findings_change": session2["total_findings"] - session1["total_findings"],
                "severity_changes": {}
            }
        }

        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            count1 = session1["severity_breakdown"].get(severity, 0)
            count2 = session2["severity_breakdown"].get(severity, 0)
            comparison["delta"]["severity_changes"][severity] = count2 - count1

        return comparison

    def _generate_session_id(self, target: str) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_hash = hashlib.md5(target.encode()).hexdigest()[:8]
        return f"scan_session_{timestamp}_{target_hash}"

    def _save_manifest(self, manifest: Dict):
        """Save manifest to disk"""
        manifest_file = self.manifest_dir / f"{manifest['session_id']}.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)

    def _load_manifest(self, session_id: str) -> Optional[Dict]:
        """Load manifest from disk"""
        manifest_file = self.manifest_dir / f"{session_id}.json"
        if not manifest_file.exists():
            return None

        with open(manifest_file, 'r') as f:
            return json.load(f)


if __name__ == "__main__":
    # Example usage
    manager = ScanManifest()

    # Create session
    session_id = manager.create_session(
        target="/home/jimmie/project",
        scanners=["bandit", "opa", "trivy"],
        metadata={"project": "portfolio", "environment": "production"}
    )

    print(f"Created scan session: {session_id}")

    # Simulate scanner completion
    manager.update_session(
        session_id=session_id,
        scanner="bandit",
        result_file="bandit_project_20250924.json",
        summary={
            "total": 12,
            "severity_breakdown": {"HIGH": 2, "MEDIUM": 5, "LOW": 5}
        }
    )

    # Get session
    session = manager.get_session(session_id)
    print(f"\nSession status: {session['status']}")
    print(f"Total findings: {session['total_findings']}")
    print(f"Severity breakdown: {session['severity_breakdown']}")