#!/usr/bin/env python3
"""
GP-DATA Configuration Manager
Single source of truth for all data persistence paths
"""

from pathlib import Path
from typing import Optional
import os

class GPDataConfig:
    """
    Centralized configuration for GP-DATA storage paths.

    Benefits:
    - Single point of truth for all data paths
    - Easy migration when restructuring GP-DATA
    - Multi-client ready (future)
    - Environment switching (dev/prod/test)
    """

    def __init__(self, client: str = "guidepoint", environment: str = "active"):
        self.client = client
        self.environment = environment

        # Base GP-DATA path - can be overridden via environment variable
        base = os.environ.get(
            "GP_DATA_ROOT",
            "/home/jimmie/linkops-industries/GP-copilot/GP-DATA"
        )
        self.base_path = Path(base)

    def get_scan_directory(self) -> Path:
        """Get scanner output directory"""
        if self.environment == "active":
            scan_dir = self.base_path / "active" / "scans"
        else:
            # Legacy fallback
            scan_dir = self.base_path / "scans"

        scan_dir.mkdir(parents=True, exist_ok=True)
        return scan_dir

    def get_analysis_directory(self) -> Path:
        """Get James Brain analysis directory"""
        analysis_dir = self.base_path / "active" / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        return analysis_dir

    def get_reports_directory(self) -> Path:
        """Get reports output directory"""
        reports_dir = self.base_path / "active" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        return reports_dir

    def get_fixes_directory(self) -> Path:
        """Get remediation tracking directory"""
        fixes_dir = self.base_path / "active" / "fixes"
        fixes_dir.mkdir(parents=True, exist_ok=True)
        return fixes_dir

    def get_opa_scans_directory(self) -> Path:
        """Get OPA policy scan results directory"""
        opa_dir = self.base_path / "active" / "scans" / "opa"
        opa_dir.mkdir(parents=True, exist_ok=True)
        return opa_dir

    def get_opa_fixes_directory(self) -> Path:
        """Get OPA fix results directory"""
        opa_fixes_dir = self.base_path / "active" / "fixes" / "opa"
        opa_fixes_dir.mkdir(parents=True, exist_ok=True)
        return opa_fixes_dir

    def get_opa_reports_directory(self) -> Path:
        """Get OPA reports directory"""
        opa_reports_dir = self.base_path / "active" / "reports" / "opa"
        opa_reports_dir.mkdir(parents=True, exist_ok=True)
        return opa_reports_dir

    def get_workflows_directory(self) -> Path:
        """Get workflow tracking directory"""
        workflows_dir = self.base_path / "active" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        return workflows_dir

    def get_deliverable_directory(self) -> Path:
        """Get client deliverables directory"""
        deliverable_dir = self.base_path / "active" / "deliverables"
        deliverable_dir.mkdir(parents=True, exist_ok=True)
        return deliverable_dir

    def get_archive_directory(self, subdirectory: Optional[str] = None) -> Path:
        """Get archive directory with optional subdirectory"""
        if subdirectory:
            archive_dir = self.base_path / "archive" / subdirectory
        else:
            archive_dir = self.base_path / "archive"

        archive_dir.mkdir(parents=True, exist_ok=True)
        return archive_dir

    def get_templates_directory(self, template_type: Optional[str] = None) -> Path:
        """Get templates directory (reports, policies, workflows)"""
        if template_type:
            templates_dir = self.base_path / "templates" / template_type
        else:
            templates_dir = self.base_path / "templates"

        templates_dir.mkdir(parents=True, exist_ok=True)
        return templates_dir

    def get_client_directory(self, client_name: Optional[str] = None) -> Path:
        """Get client-specific directory (future multi-client support)"""
        client = client_name or self.client
        client_dir = self.base_path / "clients" / client
        client_dir.mkdir(parents=True, exist_ok=True)
        return client_dir

    # Convenience methods for common paths
    @property
    def scans(self) -> Path:
        """Quick access to scans directory"""
        return self.get_scan_directory()

    @property
    def analysis(self) -> Path:
        """Quick access to analysis directory"""
        return self.get_analysis_directory()

    @property
    def reports(self) -> Path:
        """Quick access to reports directory"""
        return self.get_reports_directory()

    @property
    def fixes(self) -> Path:
        """Quick access to fixes directory"""
        return self.get_fixes_directory()

    @property
    def workflows(self) -> Path:
        """Quick access to workflows directory"""
        return self.get_workflows_directory()

    @property
    def deliverables(self) -> Path:
        """Quick access to deliverables directory"""
        return self.get_deliverable_directory()


# Singleton instance for easy import
gp_data_config = GPDataConfig()


if __name__ == "__main__":
    # Validate configuration
    config = GPDataConfig()

    print("🔧 GP-DATA Configuration")
    print(f"   Base Path: {config.base_path}")
    print(f"   Client: {config.client}")
    print(f"   Environment: {config.environment}")
    print()
    print("📁 Directory Paths:")
    print(f"   Scans: {config.scans}")
    print(f"   Analysis: {config.analysis}")
    print(f"   Reports: {config.reports}")
    print(f"   Fixes: {config.fixes}")
    print(f"   Workflows: {config.workflows}")
    print(f"   Deliverables: {config.deliverables}")
    print()
    print("✅ All directories created successfully")