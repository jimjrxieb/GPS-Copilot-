"""
GP-JADE RAG Auto-Sync System
=============================

File system watcher that automatically syncs workspace changes into RAG knowledge base.

Purpose:
- Monitor ~/jade-workspace/projects/** for changes
- Auto-ingest Terraform, Kubernetes, OPA, Python files
- Track metadata: timestamp, author, file type, action type
- Enable queries like "What did we do today?"

Architecture:
- Watchdog monitors file system events
- Event handler triggers ingestion pipeline
- Metadata stored in SQLite (structured) + ChromaDB (semantic)
- Query interface provides time-series and semantic search

Author: GP-JADE Team
Date: September 30, 2025
"""

import os
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from loguru import logger

# File types to monitor
MONITORED_EXTENSIONS = {
    '.tf', '.tfvars',           # Terraform
    '.yaml', '.yml',            # Kubernetes manifests
    '.rego',                    # OPA policies
    '.py',                      # Python scripts
    '.json',                    # Config files
    '.md',                      # Documentation
    '.sh', '.bash',             # Shell scripts
}

# Action types
ACTION_CREATED = "created"
ACTION_MODIFIED = "modified"
ACTION_DELETED = "deleted"
ACTION_MOVED = "moved"


@dataclass
class FileEvent:
    """Represents a file system event with metadata"""
    file_path: str
    action: str  # created, modified, deleted, moved
    timestamp: datetime
    file_type: str  # .tf, .yaml, .rego, etc.
    project: str  # extracted from path
    size_bytes: int
    author: Optional[str] = None  # from git blame if available

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class JadeWorkspaceHandler(FileSystemEventHandler):
    """
    Handles file system events and triggers ingestion pipeline.
    """

    def __init__(self, sync_system: 'JadeWorkspaceSync'):
        super().__init__()
        self.sync_system = sync_system
        logger.info("JadeWorkspaceHandler initialized")

    def on_created(self, event: FileSystemEvent):
        """Handle file creation"""
        if not event.is_directory and self._should_monitor(event.src_path):
            logger.info(f"File created: {event.src_path}")
            self.sync_system.handle_file_event(event.src_path, ACTION_CREATED)

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification"""
        if not event.is_directory and self._should_monitor(event.src_path):
            logger.info(f"File modified: {event.src_path}")
            self.sync_system.handle_file_event(event.src_path, ACTION_MODIFIED)

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion"""
        if not event.is_directory and self._should_monitor(event.src_path):
            logger.info(f"File deleted: {event.src_path}")
            self.sync_system.handle_file_event(event.src_path, ACTION_DELETED)

    def on_moved(self, event: FileSystemEvent):
        """Handle file move/rename"""
        if not event.is_directory and self._should_monitor(event.dest_path):
            logger.info(f"File moved: {event.src_path} -> {event.dest_path}")
            self.sync_system.handle_file_event(event.dest_path, ACTION_MOVED)

    def _should_monitor(self, file_path: str) -> bool:
        """Check if file extension should be monitored"""
        return Path(file_path).suffix.lower() in MONITORED_EXTENSIONS


class ActivityDatabase:
    """
    SQLite database for structured activity tracking.
    Stores metadata for fast time-series queries.
    """

    def __init__(self, db_path: str = "GP-DATA/active/activity.db"):
        self.db_path = db_path
        self._ensure_directory()
        self._init_database()

    def _ensure_directory(self):
        """Ensure database directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # File events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                file_type TEXT NOT NULL,
                project TEXT NOT NULL,
                size_bytes INTEGER,
                author TEXT,
                indexed INTEGER DEFAULT 0
            )
        """)

        # Daily summary table (pre-aggregated for performance)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_summaries (
                date DATE PRIMARY KEY,
                total_events INTEGER DEFAULT 0,
                files_created INTEGER DEFAULT 0,
                files_modified INTEGER DEFAULT 0,
                files_deleted INTEGER DEFAULT 0,
                projects_touched TEXT,
                last_updated DATETIME
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON file_events(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_action ON file_events(action)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_project ON file_events(project)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_type ON file_events(file_type)")

        conn.commit()
        conn.close()
        logger.info(f"Activity database initialized: {self.db_path}")

    def insert_event(self, event: FileEvent):
        """Insert file event into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO file_events
            (file_path, action, timestamp, file_type, project, size_bytes, author)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event.file_path,
            event.action,
            event.timestamp.isoformat(),
            event.file_type,
            event.project,
            event.size_bytes,
            event.author
        ))

        conn.commit()
        conn.close()
        logger.debug(f"Event stored: {event.action} - {event.file_path}")

    def query_daily_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Query daily summary statistics.

        Args:
            date: Date string (YYYY-MM-DD) or None for today

        Returns:
            Dictionary with daily statistics
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get counts by action type
        cursor.execute("""
            SELECT
                action,
                COUNT(*) as count
            FROM file_events
            WHERE DATE(timestamp) = ?
            GROUP BY action
        """, (date,))

        actions = {row[0]: row[1] for row in cursor.fetchall()}

        # Get file type breakdown
        cursor.execute("""
            SELECT
                file_type,
                COUNT(*) as count
            FROM file_events
            WHERE DATE(timestamp) = ?
            GROUP BY file_type
            ORDER BY count DESC
        """, (date,))

        file_types = {row[0]: row[1] for row in cursor.fetchall()}

        # Get projects touched
        cursor.execute("""
            SELECT DISTINCT project
            FROM file_events
            WHERE DATE(timestamp) = ?
        """, (date,))

        projects = [row[0] for row in cursor.fetchall()]

        conn.close()

        return {
            "date": date,
            "total_events": sum(actions.values()),
            "files_created": actions.get(ACTION_CREATED, 0),
            "files_modified": actions.get(ACTION_MODIFIED, 0),
            "files_deleted": actions.get(ACTION_DELETED, 0),
            "files_moved": actions.get(ACTION_MOVED, 0),
            "file_types": file_types,
            "projects_touched": projects,
            "summary": self._generate_summary_text(actions, file_types, projects)
        }

    def _generate_summary_text(self, actions: Dict, file_types: Dict, projects: List) -> str:
        """Generate human-readable summary text"""
        parts = []

        if actions.get(ACTION_CREATED, 0) > 0:
            parts.append(f"{actions[ACTION_CREATED]} files created")
        if actions.get(ACTION_MODIFIED, 0) > 0:
            parts.append(f"{actions[ACTION_MODIFIED]} files modified")
        if actions.get(ACTION_DELETED, 0) > 0:
            parts.append(f"{actions[ACTION_DELETED]} files deleted")

        summary = ", ".join(parts) if parts else "No activity"

        if file_types:
            top_type = max(file_types.items(), key=lambda x: x[1])
            summary += f" (mostly {top_type[0]} files)"

        if projects:
            summary += f" across {len(projects)} project(s)"

        return summary


class JadeWorkspaceSync:
    """
    Main RAG Auto-Sync System.

    Monitors workspace directories and automatically syncs changes into RAG.
    Provides query interface for "What did we do today?" functionality.
    """

    def __init__(self, workspace_dir: str = "~/jade-workspace", enable_ingestion: bool = True):
        self.workspace_dir = Path(workspace_dir).expanduser()
        self.activity_db = ActivityDatabase()
        self.observer = Observer()
        self.event_handler = JadeWorkspaceHandler(self)

        # Initialize ingestion pipeline
        self.enable_ingestion = enable_ingestion
        if enable_ingestion:
            from ingestion.auto_ingest import AutoIngestionPipeline
            self.ingestion_pipeline = AutoIngestionPipeline()
            logger.info("Auto-ingestion pipeline enabled")
        else:
            self.ingestion_pipeline = None

        logger.info(f"JadeWorkspaceSync initialized: {self.workspace_dir}")

    def start_watching(self, watch_dirs: Optional[List[str]] = None):
        """
        Start watching directories for changes.

        Args:
            watch_dirs: List of directories to watch (relative to workspace_dir)
                       If None, watches entire workspace
        """
        if watch_dirs is None:
            watch_dirs = ["projects"]

        for watch_dir in watch_dirs:
            full_path = self.workspace_dir / watch_dir

            if not full_path.exists():
                logger.warning(f"Watch directory does not exist: {full_path}")
                logger.info(f"Creating directory: {full_path}")
                full_path.mkdir(parents=True, exist_ok=True)

            self.observer.schedule(
                self.event_handler,
                str(full_path),
                recursive=True
            )
            logger.info(f"Watching: {full_path}")

        self.observer.start()
        logger.info("File system watcher started")

    def stop_watching(self):
        """Stop watching file system"""
        self.observer.stop()
        self.observer.join()
        logger.info("File system watcher stopped")

    def handle_file_event(self, file_path: str, action: str):
        """
        Process file system event and update RAG.

        Args:
            file_path: Absolute path to file
            action: Type of action (created, modified, deleted, moved)
        """
        try:
            path_obj = Path(file_path)

            # Extract metadata
            event = FileEvent(
                file_path=str(path_obj),
                action=action,
                timestamp=datetime.now(),
                file_type=path_obj.suffix.lower(),
                project=self._extract_project(path_obj),
                size_bytes=path_obj.stat().st_size if path_obj.exists() else 0
            )

            # Store in activity database
            self.activity_db.insert_event(event)

            # Trigger ingestion pipeline
            if self.ingestion_pipeline and path_obj.exists():
                try:
                    self.ingestion_pipeline.ingest_file(file_path, action)
                except Exception as e:
                    logger.error(f"Ingestion failed for {file_path}: {e}")

            logger.debug(f"Processed event: {action} - {file_path}")

        except Exception as e:
            logger.error(f"Error handling file event: {e}")

    def _extract_project(self, file_path: Path) -> str:
        """
        Extract project name from file path.

        Example: ~/jade-workspace/projects/terraform-infra/main.tf
                 -> "terraform-infra"
        """
        try:
            relative = file_path.relative_to(self.workspace_dir)
            if len(relative.parts) >= 2:
                return relative.parts[1]  # projects/PROJECT_NAME/...
            return "unknown"
        except ValueError:
            return "external"

    def query_todays_work(self) -> Dict[str, Any]:
        """
        Query today's activity - answers "What did we do today?"

        Returns:
            Dictionary with today's statistics and summary
        """
        return self.activity_db.query_daily_summary()

    def query_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query activity for a date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of daily summaries
        """
        summaries = []
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            summary = self.activity_db.query_daily_summary(date_str)
            summaries.append(summary)
            current += timedelta(days=1)

        return summaries

    def initial_sync(self, scan_dirs: Optional[List[str]] = None):
        """
        Perform initial sync of existing files in workspace.

        Args:
            scan_dirs: List of directories to scan (relative to workspace_dir)
                      If None, scans entire workspace
        """
        if scan_dirs is None:
            scan_dirs = ["projects"]

        logger.info("Starting initial workspace sync...")
        file_count = 0

        for scan_dir in scan_dirs:
            full_path = self.workspace_dir / scan_dir

            if not full_path.exists():
                logger.warning(f"Scan directory does not exist: {full_path}")
                continue

            # Recursively find all monitored files
            for file_path in full_path.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in MONITORED_EXTENSIONS:
                    self.handle_file_event(str(file_path), ACTION_CREATED)
                    file_count += 1

        logger.info(f"Initial sync complete: {file_count} files indexed")
        return file_count


def main():
    """
    Main entry point for testing the auto-sync system.
    """
    # Configure logging
    logger.add("GP-DATA/active/auto_sync.log", rotation="1 day", retention="30 days")

    # Initialize sync system
    sync = JadeWorkspaceSync()

    # Perform initial sync
    sync.initial_sync()

    # Start watching
    sync.start_watching()

    try:
        logger.info("RAG Auto-Sync running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping RAG Auto-Sync...")
        sync.stop_watching()


if __name__ == "__main__":
    main()