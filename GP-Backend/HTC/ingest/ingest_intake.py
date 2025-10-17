#!/usr/bin/env python3
"""
Intake Ingester
===============

Specialized ingester for business context:
- Clients (profiles, requirements)
- Meetings (notes, action items)
- People (profiles, roles, contacts)

Features:
- Large chunks (preserve context)
- Extract metadata (names, dates, action items)
- Sanitize PII (based on rules)
- Dedicated ChromaDB collections
"""

import os
import sys
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from shared.base_ingester import BaseIngester
from shared.chunking import Chunker
from shared.sanitization import Sanitizer


class IntakeIngester(BaseIngester):
    """Ingester for business context (clients, meetings, people)"""

    def __init__(self, dry_run: bool = False):
        super().__init__(dry_run)
        self.chunker = Chunker("large")  # Large chunks for context
        self.sanitizer = Sanitizer("intake")

    def get_category(self) -> str:
        return "intake"

    def get_subcategories(self) -> List[str]:
        return ["clients", "meetings", "people"]

    def extract_frontmatter(self, text: str) -> tuple[Optional[Dict[str, Any]], str]:
        """
        Extract YAML frontmatter from markdown.

        Returns:
            (frontmatter_dict, content_without_frontmatter)
        """
        # Check for YAML frontmatter (between --- markers)
        frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
        match = frontmatter_pattern.match(text)

        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1))
                content = text[match.end():]
                return frontmatter, content
            except yaml.YAMLError:
                return None, text

        return None, text

    def extract_meeting_metadata(self, text: str, frontmatter: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extract metadata from meeting notes.

        Looks for:
        - Meeting date
        - Client name
        - Attendees
        - Action items
        - Topics discussed
        """
        metadata = {
            "category": "intake",
            "subcategory": "meetings"
        }

        # Get from frontmatter if available
        if frontmatter:
            metadata.update(frontmatter)

        # Extract date from title or content
        # Pattern: "Meeting with X - 2025-10-16" or "Date: 2025-10-16"
        date_pattern = re.compile(r'(?:Meeting.*?-\s*|\bDate:\s*)(\d{4}-\d{2}-\d{2})')
        date_match = date_pattern.search(text)
        if date_match and "meeting_date" not in metadata:
            metadata["meeting_date"] = date_match.group(1)

        # Extract client name
        # Pattern: "Meeting with X" or "Client: X"
        client_pattern = re.compile(r'(?:Meeting with|Client:)\s*([A-Z][a-zA-Z\s&]+?)(?:\s*-|\n|$)')
        client_match = client_pattern.search(text)
        if client_match and "client" not in metadata:
            metadata["client"] = client_match.group(1).strip()

        # Extract attendees
        # Pattern: "Attendees: John Smith (john@email.com), Jane Doe"
        attendees_pattern = re.compile(r'Attendees?:\s*(.+?)(?:\n\n|\n#)', re.DOTALL)
        attendees_match = attendees_pattern.search(text)
        if attendees_match and "attendees" not in metadata:
            attendees_text = attendees_match.group(1)
            # Split by comma and extract names
            attendees = [name.split('(')[0].strip() for name in attendees_text.split(',')]
            metadata["attendees"] = attendees[:10]  # Limit to 10

        # Extract action items
        # Pattern: "Action Items:" followed by bullet points or checkboxes
        action_items_pattern = re.compile(r'Action Items?:\s*\n((?:[-*]\s*\[[ x]\]\s*.+?\n|[-*]\s*.+?\n)+)', re.IGNORECASE)
        action_items_match = action_items_pattern.search(text)
        if action_items_match and "action_items" not in metadata:
            action_items_text = action_items_match.group(1)
            # Extract each action item
            action_items = re.findall(r'[-*]\s*(?:\[[ x]\]\s*)?(.+)', action_items_text)
            metadata["action_items"] = action_items[:10]  # Limit to 10

        # Extract topics (common keywords)
        topics = []
        topic_keywords = ["kubernetes", "security", "compliance", "pci-dss", "soc2", "aws", "terraform", "opa"]
        for keyword in topic_keywords:
            if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
                topics.append(keyword.lower())
        if topics:
            metadata["topics"] = topics

        return metadata

    def extract_client_metadata(self, text: str, frontmatter: Optional[Dict] = None) -> Dict[str, Any]:
        """Extract metadata from client profile"""
        metadata = {
            "category": "intake",
            "subcategory": "clients"
        }

        if frontmatter:
            metadata.update(frontmatter)

        # Extract client name from title
        # Pattern: "# Client Name" or "Client: Name"
        name_pattern = re.compile(r'(?:^#\s*([A-Z][a-zA-Z\s&]+)|Client:\s*([A-Z][a-zA-Z\s&]+))')
        name_match = name_pattern.search(text)
        if name_match and "client_name" not in metadata:
            metadata["client_name"] = (name_match.group(1) or name_match.group(2)).strip()

        # Extract industry
        industry_pattern = re.compile(r'Industry:\s*(.+?)(?:\n|$)')
        industry_match = industry_pattern.search(text)
        if industry_match and "industry" not in metadata:
            metadata["industry"] = industry_match.group(1).strip()

        return metadata

    def extract_people_metadata(self, text: str, frontmatter: Optional[Dict] = None) -> Dict[str, Any]:
        """Extract metadata from people profile"""
        metadata = {
            "category": "intake",
            "subcategory": "people"
        }

        if frontmatter:
            metadata.update(frontmatter)

        # Extract person name
        name_pattern = re.compile(r'(?:^#\s*([A-Z][a-zA-Z\s]+)|Name:\s*([A-Z][a-zA-Z\s]+))')
        name_match = name_pattern.search(text)
        if name_match and "person_name" not in metadata:
            metadata["person_name"] = (name_match.group(1) or name_match.group(2)).strip()

        # Extract role
        role_pattern = re.compile(r'(?:Role|Title):\s*(.+?)(?:\n|$)')
        role_match = role_pattern.search(text)
        if role_match and "role" not in metadata:
            metadata["role"] = role_match.group(1).strip()

        # Extract company
        company_pattern = re.compile(r'Company:\s*(.+?)(?:\n|$)')
        company_match = company_pattern.search(text)
        if company_match and "company" not in metadata:
            metadata["company"] = company_match.group(1).strip()

        return metadata

    def process_file(self, file_path: Path, subcategory: str) -> List[Dict[str, Any]]:
        """
        Process a single file and return list of documents.

        Args:
            file_path: Path to file
            subcategory: "clients", "meetings", or "people"

        Returns:
            List of documents with content and metadata
        """
        # Read file
        text = file_path.read_text(encoding='utf-8')

        # Extract frontmatter
        frontmatter, content = self.extract_frontmatter(text)

        # Sanitize content
        sanitized_content, findings = self.sanitizer.sanitize(content)

        if findings:
            print(f"  🔒 Sanitized {len(findings)} sensitive items")
            self.stats["sanitizations"] += len(findings)

        # Extract metadata based on subcategory
        if subcategory == "meetings":
            metadata = self.extract_meeting_metadata(sanitized_content, frontmatter)
        elif subcategory == "clients":
            metadata = self.extract_client_metadata(sanitized_content, frontmatter)
        elif subcategory == "people":
            metadata = self.extract_people_metadata(sanitized_content, frontmatter)
        else:
            metadata = {"category": "intake", "subcategory": subcategory}

        # Add file metadata
        metadata["source"] = str(file_path.name)
        metadata["ingested_at"] = datetime.now().isoformat()

        # Chunk content (large chunks for context)
        chunks = self.chunker.chunk_text(sanitized_content, preserve_structure=True)

        # Create documents
        documents = []
        for i, chunk in enumerate(chunks):
            doc = {
                "content": chunk,
                "id": f"{file_path.stem}_chunk_{i}_{hash(chunk) % 10000}",
                "metadata": metadata.copy()
            }
            doc["metadata"]["chunk_index"] = i
            doc["metadata"]["total_chunks"] = len(chunks)
            documents.append(doc)

        return documents


def main():
    """Test the intake ingester"""
    import argparse

    parser = argparse.ArgumentParser(description="Ingest intake knowledge (clients, meetings, people)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without ingesting")
    args = parser.parse_args()

    # Get path to unprocessed/intake/
    script_dir = Path(__file__).parent.parent
    intake_dir = script_dir / "unprocessed" / "intake"

    if not intake_dir.exists():
        print(f"❌ Directory not found: {intake_dir}")
        print(f"   Creating it now...")
        intake_dir.mkdir(parents=True, exist_ok=True)
        (intake_dir / "clients").mkdir(exist_ok=True)
        (intake_dir / "meetings").mkdir(exist_ok=True)
        (intake_dir / "people").mkdir(exist_ok=True)
        print(f"✅ Created intake directory structure")
        return

    # Create ingester
    ingester = IntakeIngester(dry_run=args.dry_run)

    # Ingest
    ingester.ingest_directory(intake_dir)


if __name__ == "__main__":
    main()
