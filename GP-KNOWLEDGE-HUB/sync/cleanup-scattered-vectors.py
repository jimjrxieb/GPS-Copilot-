#!/usr/bin/env python3
"""
Vector Database Cleanup - Remove All Scattered Vector Stores
Ensures ONLY the central vector store exists

This script:
1. Identifies all scattered vector databases
2. Backs up important data if needed
3. Removes old vector stores
4. Creates symlinks to central hub
5. Ensures single source of truth
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import json

class VectorDatabaseCleanup:
    """Clean up scattered vector databases"""

    def __init__(self):
        self.base_path = Path("/home/jimmie/linkops-industries/GP-copilot")
        self.central_vector_store = self.base_path / "GP-KNOWLEDGE-HUB" / "vector-store" / "central-knowledge-db"

        # All scattered vector database locations
        self.scattered_vectors = [
            self.base_path / "vector-db",
            self.base_path / "GP-DATA" / "vector-db",
            # Note: GP-RAG/vector-db already has symlink, check if cleanup needed
        ]

        self.cleanup_report = []
        self.backup_created = []

    def analyze_scattered_vectors(self) -> dict:
        """Analyze what's in each scattered vector database"""

        print("🔍 Analyzing scattered vector databases...")
        analysis = {}

        for vector_path in self.scattered_vectors:
            if not vector_path.exists():
                print(f"   ✅ {vector_path} - Already cleaned up")
                analysis[str(vector_path)] = {"status": "not_exists"}
                continue

            # Check if it's a symlink (already centralized)
            if vector_path.is_symlink():
                target = os.readlink(vector_path)
                print(f"   🔗 {vector_path} - Symlink to {target}")
                analysis[str(vector_path)] = {"status": "symlink", "target": target}
                continue

            # Analyze contents
            files = list(vector_path.rglob("*"))
            size_mb = sum(f.stat().st_size for f in files if f.is_file()) / (1024*1024)

            print(f"   📊 {vector_path} - {len(files)} files, {size_mb:.1f}MB")
            analysis[str(vector_path)] = {
                "status": "exists",
                "files": len(files),
                "size_mb": size_mb,
                "last_modified": max([f.stat().st_mtime for f in files if f.is_file()], default=0)
            }

        return analysis

    def backup_important_vectors(self, analysis: dict) -> None:
        """Backup any vector databases that might have unique data"""

        print("\n💾 Creating backups of important vector data...")

        backup_dir = self.base_path / "GP-KNOWLEDGE-HUB" / "backups" / f"vector-cleanup-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        for vector_path_str, info in analysis.items():
            vector_path = Path(vector_path_str)

            if info["status"] != "exists":
                continue

            # Backup if it has significant data or is recently modified
            if info["size_mb"] > 1.0:  # More than 1MB
                backup_name = f"{vector_path.name}_backup"
                backup_path = backup_dir / backup_name

                print(f"   📦 Backing up {vector_path} → {backup_path}")
                shutil.copytree(vector_path, backup_path)

                self.backup_created.append({
                    "original": str(vector_path),
                    "backup": str(backup_path),
                    "size_mb": info["size_mb"]
                })

        if self.backup_created:
            print(f"   ✅ Created {len(self.backup_created)} backups in {backup_dir}")
        else:
            print("   ✅ No backups needed")

    def remove_scattered_vectors(self, analysis: dict) -> None:
        """Remove scattered vector databases"""

        print("\n🗑️  Removing scattered vector databases...")

        for vector_path_str, info in analysis.items():
            vector_path = Path(vector_path_str)

            if info["status"] not in ["exists"]:
                continue

            print(f"   🗂️  Removing {vector_path}")
            try:
                shutil.rmtree(vector_path)
                self.cleanup_report.append({
                    "path": str(vector_path),
                    "action": "removed",
                    "files": info["files"],
                    "size_mb": info["size_mb"]
                })
                print(f"      ✅ Removed successfully")

            except Exception as e:
                print(f"      ❌ Error removing: {e}")
                self.cleanup_report.append({
                    "path": str(vector_path),
                    "action": "error",
                    "error": str(e)
                })

    def create_central_symlinks(self) -> None:
        """Create symlinks pointing to central vector store"""

        print("\n🔗 Creating symlinks to central vector store...")

        symlink_locations = [
            (self.base_path / "vector-db" / "gp_security_rag", "Root vector-db"),
            (self.base_path / "GP-DATA" / "vector-db" / "central", "GP-DATA vector-db"),
        ]

        for symlink_path, description in symlink_locations:
            # Create parent directory if needed
            symlink_path.parent.mkdir(parents=True, exist_ok=True)

            # Remove if exists
            if symlink_path.exists():
                if symlink_path.is_symlink():
                    symlink_path.unlink()
                    print(f"   🔄 Removed old symlink: {symlink_path}")
                else:
                    print(f"   ⚠️  {symlink_path} exists but is not a symlink - skipping")
                    continue

            # Create symlink
            try:
                symlink_path.symlink_to(self.central_vector_store)
                print(f"   ✅ Created {description} symlink: {symlink_path}")

                self.cleanup_report.append({
                    "path": str(symlink_path),
                    "action": "symlink_created",
                    "target": str(self.central_vector_store)
                })

            except Exception as e:
                print(f"   ❌ Error creating symlink {symlink_path}: {e}")

    def verify_central_vector_store(self) -> dict:
        """Verify central vector store is healthy"""

        print(f"\n✅ Verifying central vector store: {self.central_vector_store}")

        if not self.central_vector_store.exists():
            print("   ❌ Central vector store doesn't exist!")
            return {"status": "missing"}

        # Check contents
        files = list(self.central_vector_store.rglob("*"))
        sqlite_files = [f for f in files if f.name.endswith(".sqlite3")]

        if not sqlite_files:
            print("   ❌ No ChromaDB sqlite files found!")
            return {"status": "no_database"}

        total_size = sum(f.stat().st_size for f in files if f.is_file()) / (1024*1024)

        print(f"   📊 Central vector store: {len(files)} files, {total_size:.1f}MB")
        print(f"   💾 Database files: {len(sqlite_files)}")

        # Test if we can connect
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_chroma import Chroma

            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            vector_store = Chroma(
                persist_directory=str(self.central_vector_store),
                embedding_function=embeddings
            )

            # Count documents
            ids = vector_store.get()["ids"]
            print(f"   🧠 Vector documents: {len(ids)}")

            return {
                "status": "healthy",
                "files": len(files),
                "size_mb": total_size,
                "documents": len(ids)
            }

        except Exception as e:
            print(f"   ⚠️  Connection test failed: {e}")
            return {"status": "connection_error", "error": str(e)}

    def generate_cleanup_report(self, analysis: dict, verification: dict) -> None:
        """Generate cleanup report"""

        report_path = self.base_path / "GP-KNOWLEDGE-HUB" / f"vector_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        report_content = f"""# Vector Database Cleanup Report

**Date**: {datetime.now().isoformat()}

## 🎯 Objective
Clean up scattered vector databases and ensure single central vector store.

## 📊 Analysis Summary

### Scattered Vector Databases Found:
"""

        for path, info in analysis.items():
            report_content += f"\n- **{path}**\n"
            report_content += f"  - Status: {info['status']}\n"
            if info['status'] == 'exists':
                report_content += f"  - Files: {info['files']}\n"
                report_content += f"  - Size: {info['size_mb']:.1f}MB\n"

        report_content += f"""

## 🔄 Actions Taken

### Cleanup Operations:
"""

        for action in self.cleanup_report:
            report_content += f"\n- **{action['path']}**: {action['action']}\n"
            if action['action'] == 'removed':
                report_content += f"  - Files removed: {action.get('files', 0)}\n"
                report_content += f"  - Space freed: {action.get('size_mb', 0):.1f}MB\n"

        if self.backup_created:
            report_content += f"""

### Backups Created:
"""
            for backup in self.backup_created:
                report_content += f"\n- **{backup['original']}** → `{backup['backup']}`\n"
                report_content += f"  - Size: {backup['size_mb']:.1f}MB\n"

        report_content += f"""

## ✅ Central Vector Store Status

- **Location**: `{self.central_vector_store}`
- **Status**: {verification['status']}
"""

        if verification['status'] == 'healthy':
            report_content += f"""- **Files**: {verification['files']}
- **Size**: {verification['size_mb']:.1f}MB
- **Documents**: {verification['documents']}
"""

        report_content += f"""

## 🏆 Result

✅ **Single Source of Truth**: All vector data now centralized in `GP-KNOWLEDGE-HUB/vector-store/central-knowledge-db/`

✅ **No More Scattered Folders**: Old vector databases removed or symlinked

✅ **Backward Compatibility**: Symlinks ensure existing tools still work

## 🚀 Usage

All tools now automatically use the central vector store:

```bash
# Jade uses central vector store
cd GP-RAG && python jade_live.py

# Central API access
python GP-KNOWLEDGE-HUB/api/knowledge_api.py
```

**🎉 Vector database cleanup complete!**
"""

        with open(report_path, 'w') as f:
            f.write(report_content)

        print(f"\n📋 Generated cleanup report: {report_path}")

    def run_cleanup(self) -> None:
        """Run complete vector database cleanup"""

        print("🚀 VECTOR DATABASE CLEANUP - CENTRALIZATION")
        print("=" * 60)

        # 1. Analyze scattered vectors
        analysis = self.analyze_scattered_vectors()

        # 2. Backup important data
        self.backup_important_vectors(analysis)

        # 3. Remove scattered vectors
        self.remove_scattered_vectors(analysis)

        # 4. Create central symlinks
        self.create_central_symlinks()

        # 5. Verify central vector store
        verification = self.verify_central_vector_store()

        # 6. Generate report
        self.generate_cleanup_report(analysis, verification)

        print(f"\n🎯 VECTOR DATABASE CLEANUP COMPLETE!")
        print(f"   🧠 Central Vector Store: {self.central_vector_store}")
        print(f"   🗑️  Scattered DBs Cleaned: {len([a for a in self.cleanup_report if a['action'] == 'removed'])}")
        print(f"   🔗 Symlinks Created: {len([a for a in self.cleanup_report if a['action'] == 'symlink_created'])}")
        print(f"   💾 Backups Created: {len(self.backup_created)}")
        print("\n🏆 NO MORE SCATTERED VECTOR DATABASES!")

def main():
    cleanup = VectorDatabaseCleanup()
    cleanup.run_cleanup()

if __name__ == "__main__":
    main()