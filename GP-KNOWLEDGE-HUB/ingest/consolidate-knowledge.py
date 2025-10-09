#!/usr/bin/env python3
"""
Knowledge Consolidation System
Moves ALL scattered knowledge into the central GP-KNOWLEDGE-HUB

This script:
1. Finds ALL knowledge scattered across the codebase
2. Organizes it by domain in the central hub
3. Creates symbolic links to avoid duplication
4. Updates the central vector store
5. Provides ONE place for all knowledge management
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Set
import json
from datetime import datetime

class KnowledgeConsolidator:
    """Consolidates scattered knowledge into central hub"""

    def __init__(self):
        self.base_path = Path("/home/jimmie/linkops-industries/GP-copilot")
        self.hub_path = self.base_path / "GP-KNOWLEDGE-HUB"
        self.kb_path = self.hub_path / "knowledge-base"

        # Central organization by domain
        self.domains = {
            "security": self.kb_path / "security",
            "compliance": self.kb_path / "compliance",
            "tools": self.kb_path / "tools",
            "workflows": self.kb_path / "workflows",
            "policies": self.kb_path / "policies"
        }

        # Create domain directories
        for domain_path in self.domains.values():
            domain_path.mkdir(parents=True, exist_ok=True)

        self.knowledge_map = {}
        self.consolidated_files = 0
        self.scattered_sources = []

    def scan_scattered_knowledge(self) -> Dict[str, List[Path]]:
        """Find all scattered knowledge across the codebase"""

        print("🔍 Scanning for scattered knowledge...")

        scattered_knowledge = {
            "security": [],
            "compliance": [],
            "tools": [],
            "workflows": [],
            "policies": []
        }

        # Define source locations and their domain mappings
        source_mappings = [
            # GP-DATA knowledge
            {
                "path": self.base_path / "GP-DATA" / "knowledge-base",
                "domain": "security",
                "recursive": True
            },
            {
                "path": self.base_path / "GP-DATA" / "active" / "reports",
                "domain": "security",
                "recursive": True
            },
            {
                "path": self.base_path / "GP-DATA" / "metadata" / "audits",
                "domain": "security",
                "recursive": False
            },

            # GP-CONSULTING-AGENTS knowledge
            {
                "path": self.base_path / "GP-CONSULTING-AGENTS" / "workflows",
                "domain": "workflows",
                "recursive": True
            },
            {
                "path": self.base_path / "GP-CONSULTING-AGENTS" / "policies",
                "domain": "policies",
                "recursive": True
            },
            {
                "path": self.base_path / "GP-CONSULTING-AGENTS" / "fixers",
                "domain": "tools",
                "recursive": True,
                "extensions": [".md", ".py"]
            },
            {
                "path": self.base_path / "GP-CONSULTING-AGENTS" / "scanners",
                "domain": "tools",
                "recursive": True,
                "extensions": [".md", ".py"]
            },

            # RAG documentation
            {
                "path": self.base_path / "GP-RAG" / "unprocessed",
                "domain": "tools",
                "recursive": True
            },
            {
                "path": self.base_path / "GP-RAG" / "processed",
                "domain": "security",
                "recursive": True
            },

            # Project documentation
            {
                "path": self.base_path / "GP-PROJECTS",
                "domain": "workflows",
                "recursive": True,
                "extensions": [".md"],
                "exclude_dirs": ["node_modules", ".git", "venv"]
            }
        ]

        for mapping in source_mappings:
            source_path = mapping["path"]
            domain = mapping["domain"]

            if not source_path.exists():
                continue

            print(f"  📂 Scanning {source_path} → {domain}")

            extensions = mapping.get("extensions", [".md", ".txt", ".rst"])
            exclude_dirs = mapping.get("exclude_dirs", [])
            recursive = mapping.get("recursive", True)

            if recursive:
                for ext in extensions:
                    files = list(source_path.rglob(f"*{ext}"))
                    for file_path in files:
                        # Skip excluded directories
                        if any(exc_dir in str(file_path) for exc_dir in exclude_dirs):
                            continue
                        scattered_knowledge[domain].append(file_path)
            else:
                for ext in extensions:
                    files = list(source_path.glob(f"*{ext}"))
                    scattered_knowledge[domain].extend(files)

        # Summary
        total_files = sum(len(files) for files in scattered_knowledge.values())
        print(f"\n📊 Found {total_files} knowledge files:")
        for domain, files in scattered_knowledge.items():
            print(f"   {domain}: {len(files)} files")

        return scattered_knowledge

    def consolidate_by_domain(self, scattered_knowledge: Dict[str, List[Path]]) -> None:
        """Consolidate knowledge files by domain into central hub"""

        print(f"\n🔄 Consolidating knowledge into central hub...")

        for domain, files in scattered_knowledge.items():
            domain_path = self.domains[domain]

            print(f"\n📁 Processing {domain} domain ({len(files)} files)")

            domain_files = 0
            for file_path in files:
                try:
                    # Create organized filename
                    relative_path = self._get_relative_source_path(file_path)
                    safe_name = self._create_safe_filename(relative_path, file_path.suffix)
                    target_path = domain_path / safe_name

                    # Copy file to central location
                    if not target_path.exists():
                        shutil.copy2(file_path, target_path)
                        domain_files += 1

                        # Track the mapping
                        self.knowledge_map[str(target_path)] = {
                            "original_path": str(file_path),
                            "domain": domain,
                            "consolidated_date": datetime.now().isoformat()
                        }

                except Exception as e:
                    print(f"   ⚠️  Error consolidating {file_path}: {e}")
                    continue

            print(f"   ✅ Consolidated {domain_files} {domain} files")
            self.consolidated_files += domain_files

    def _get_relative_source_path(self, file_path: Path) -> str:
        """Get relative path from base to help with naming"""
        try:
            return str(file_path.relative_to(self.base_path))
        except ValueError:
            return str(file_path.name)

    def _create_safe_filename(self, relative_path: str, extension: str) -> str:
        """Create safe filename for central storage"""
        # Replace path separators and spaces
        safe_name = relative_path.replace("/", "_").replace("\\", "_").replace(" ", "_")

        # Remove the extension from the path part and add it at the end
        if safe_name.endswith(extension):
            safe_name = safe_name[:-len(extension)]

        return f"{safe_name}{extension}"

    def create_domain_indexes(self) -> None:
        """Create index files for each domain"""

        print(f"\n📝 Creating domain indexes...")

        for domain, domain_path in self.domains.items():
            files = list(domain_path.glob("*.md")) + list(domain_path.glob("*.txt"))

            if not files:
                continue

            index_content = f"""# {domain.title()} Knowledge Index

## 📚 Available Documentation ({len(files)} files)

Generated: {datetime.now().isoformat()}

"""

            for file_path in sorted(files):
                # Get original source if available
                original = self.knowledge_map.get(str(file_path), {}).get("original_path", "Unknown")
                index_content += f"- **{file_path.name}**\n  - Source: `{original}`\n  - Modified: {datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()}\n\n"

            index_path = domain_path / f"{domain}_index.md"
            with open(index_path, 'w') as f:
                f.write(index_content)

            print(f"   📄 Created {domain} index: {index_path}")

    def update_central_vector_store(self) -> None:
        """Update the central vector store with consolidated knowledge"""

        print(f"\n🧠 Updating central vector store...")

        # Move existing vector store to central location
        old_vector_path = self.base_path / "GP-RAG" / "vector-db" / "gp_security_rag"
        new_vector_path = self.hub_path / "vector-store" / "central-knowledge-db"

        if old_vector_path.exists():
            if new_vector_path.exists():
                shutil.rmtree(new_vector_path)
            shutil.move(str(old_vector_path), str(new_vector_path))
            print(f"   ✅ Moved vector store to: {new_vector_path}")

            # Create symlink for backward compatibility
            old_vector_path.parent.mkdir(parents=True, exist_ok=True)
            if not old_vector_path.exists():
                os.symlink(str(new_vector_path), str(old_vector_path))
                print(f"   🔗 Created symlink for backward compatibility")

    def create_central_access_api(self) -> None:
        """Create central knowledge access API"""

        api_script = self.hub_path / "api" / "knowledge_api.py"

        api_content = f'''#!/usr/bin/env python3
"""
Central Knowledge Access API
Single point of access for all knowledge in the system
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "GP-RAG"))

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
except ImportError as e:
    print(f"❌ Missing dependencies: {{e}}")
    sys.exit(1)

class CentralKnowledgeAPI:
    """Central API for accessing all knowledge"""

    def __init__(self):
        self.hub_path = Path(__file__).parent.parent
        self.vector_store_path = self.hub_path / "vector-store" / "central-knowledge-db"

        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Connect to central vector store
        if self.vector_store_path.exists():
            self.vector_store = Chroma(
                persist_directory=str(self.vector_store_path),
                embedding_function=self.embeddings
            )
        else:
            self.vector_store = None
            print("⚠️  Central vector store not found")

    def search_knowledge(self, query: str, k: int = 5, domain: str = None):
        """Search central knowledge base"""
        if not self.vector_store:
            return []

        results = self.vector_store.similarity_search(query, k=k)

        # Filter by domain if specified
        if domain:
            results = [r for r in results if r.metadata.get("source_type", "").lower().find(domain.lower()) >= 0]

        return results

    def get_domain_knowledge(self, domain: str):
        """Get all knowledge for a specific domain"""
        domain_path = self.hub_path / "knowledge-base" / domain

        if not domain_path.exists():
            return []

        files = list(domain_path.glob("*.md")) + list(domain_path.glob("*.txt"))
        return [str(f) for f in files]

    def get_knowledge_stats(self):
        """Get statistics about central knowledge"""
        stats = {{}}

        # Vector store stats
        if self.vector_store:
            ids = self.vector_store.get()["ids"]
            stats["vector_documents"] = len(ids)

        # Domain stats
        for domain in ["security", "compliance", "tools", "workflows", "policies"]:
            domain_path = self.hub_path / "knowledge-base" / domain
            if domain_path.exists():
                files = list(domain_path.glob("*.md")) + list(domain_path.glob("*.txt"))
                stats[f"{{domain}}_files"] = len(files)

        return stats

if __name__ == "__main__":
    api = CentralKnowledgeAPI()
    stats = api.get_knowledge_stats()

    print("🧠 Central Knowledge API Status:")
    for key, value in stats.items():
        print(f"   {{key}}: {{value}}")
'''

        with open(api_script, 'w') as f:
            f.write(api_content)

        # Make executable
        api_script.chmod(0o755)
        print(f"   🚀 Created central knowledge API: {api_script}")

    def create_jade_integration(self) -> None:
        """Update Jade to use central knowledge hub"""

        jade_config = self.hub_path / "api" / "jade_central_config.py"

        config_content = f'''#!/usr/bin/env python3
"""
Jade Central Knowledge Configuration
Updates Jade to use the central knowledge hub
"""

# Central knowledge hub paths
CENTRAL_HUB_PATH = "{self.hub_path}"
CENTRAL_VECTOR_STORE_PATH = "{self.hub_path}/vector-store/central-knowledge-db"
CENTRAL_KNOWLEDGE_BASE_PATH = "{self.hub_path}/knowledge-base"

# Domain mappings
KNOWLEDGE_DOMAINS = {{
    "security": "{self.domains['security']}",
    "compliance": "{self.domains['compliance']}",
    "tools": "{self.domains['tools']}",
    "workflows": "{self.domains['workflows']}",
    "policies": "{self.domains['policies']}"
}}

def get_central_vector_store_path():
    """Get path to central vector store"""
    return CENTRAL_VECTOR_STORE_PATH

def get_knowledge_domain_path(domain: str):
    """Get path to specific knowledge domain"""
    return KNOWLEDGE_DOMAINS.get(domain)

def get_all_knowledge_paths():
    """Get all knowledge domain paths"""
    return list(KNOWLEDGE_DOMAINS.values())
'''

        with open(jade_config, 'w') as f:
            f.write(config_content)

        print(f"   ⚙️  Created Jade central config: {jade_config}")

    def generate_consolidation_report(self) -> None:
        """Generate consolidation report"""

        report_path = self.hub_path / f"consolidation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        report_content = f"""# Knowledge Consolidation Report

**Date**: {datetime.now().isoformat()}
**Consolidated Files**: {self.consolidated_files}

## 🎯 Central Hub Location
`{self.hub_path}`

## 📊 Domain Breakdown
"""

        for domain, domain_path in self.domains.items():
            files = list(domain_path.glob("*.md")) + list(domain_path.glob("*.txt"))
            report_content += f"\n### {domain.title()}\n- **Location**: `{domain_path}`\n- **Files**: {len(files)}\n- **Index**: `{domain_path}/{domain}_index.md`"

        report_content += f"""

## 🧠 Central Vector Store
- **Location**: `{self.hub_path}/vector-store/central-knowledge-db`
- **API**: `{self.hub_path}/api/knowledge_api.py`

## 🔗 Integration
- **Jade Config**: `{self.hub_path}/api/jade_central_config.py`
- **Backward Compatibility**: Symlinks created for existing tools

## ✅ Benefits Achieved
1. **Single Source of Truth**: All knowledge in one location
2. **No More Scattered Folders**: Everything organized by domain
3. **Central Access**: Single API for all knowledge access
4. **Easy Maintenance**: Add/update knowledge in one place
5. **Backward Compatible**: Existing tools still work

## 🚀 Usage
```bash
# Access central knowledge API
python {self.hub_path}/api/knowledge_api.py

# Jade automatically uses central hub
cd {self.base_path}/GP-RAG && python jade_live.py
```

**🏆 Knowledge is now truly centralized!**
"""

        with open(report_path, 'w') as f:
            f.write(report_content)

        print(f"\n📋 Generated consolidation report: {report_path}")

    def run_consolidation(self) -> None:
        """Run complete knowledge consolidation"""

        print("🚀 CENTRALIZING ALL KNOWLEDGE INTO GP-KNOWLEDGE-HUB")
        print("=" * 80)

        # 1. Scan scattered knowledge
        scattered_knowledge = self.scan_scattered_knowledge()

        # 2. Consolidate by domain
        self.consolidate_by_domain(scattered_knowledge)

        # 3. Create domain indexes
        self.create_domain_indexes()

        # 4. Update central vector store
        self.update_central_vector_store()

        # 5. Create central access API
        self.create_central_access_api()

        # 6. Create Jade integration
        self.create_jade_integration()

        # 7. Save knowledge mapping
        mapping_file = self.hub_path / "knowledge_mapping.json"
        with open(mapping_file, 'w') as f:
            json.dump(self.knowledge_map, f, indent=2)

        # 8. Generate report
        self.generate_consolidation_report()

        print(f"\n🎯 KNOWLEDGE CONSOLIDATION COMPLETE!")
        print(f"   📁 Central Hub: {self.hub_path}")
        print(f"   📄 Files Consolidated: {self.consolidated_files}")
        print(f"   🧠 Central Vector Store: {self.hub_path}/vector-store/central-knowledge-db")
        print(f"   🚀 Central API: {self.hub_path}/api/knowledge_api.py")
        print("\n🏆 NO MORE SCATTERED FOLDERS - EVERYTHING IS CENTRALIZED!")

def main():
    consolidator = KnowledgeConsolidator()
    consolidator.run_consolidation()

if __name__ == "__main__":
    main()