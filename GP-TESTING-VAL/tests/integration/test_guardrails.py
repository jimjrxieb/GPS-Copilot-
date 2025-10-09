"""
Unit tests for scope guard and guardrails enforcement
Tests all security scenarios for client engagement operations
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch

from mcp.scope_guard import (
    ScopeGuard, ScopeViolationType, ScopeArtifact, ScopeViolation,
    create_scope_guard, validate_scope_artifact
)

class TestScopeGuardBasics:
    """Test basic scope guard functionality"""

    def setup_method(self):
        """Setup test configuration"""
        self.test_config = {
            "risky_operations": [
                "nmap", "kubectl-apply", "terraform-apply", "kubectl-*"
            ],
            "scope_artifact_required": "scope.json",
            "scope_schema": {
                "required_fields": [
                    "client_name", "engagement_id", "approver_name", "approver_email",
                    "ticket_id", "window_start", "window_end", "targets", "operations",
                    "emergency_contact"
                ]
            },
            "default_settings": {
                "max_window_hours": 8,
                "require_dry_run": True
            },
            "environment_rules": {
                "production": {
                    "require_dual_approval": True,
                    "max_window_hours": 4
                },
                "staging": {
                    "require_dual_approval": False,
                    "max_window_hours": 8
                }
            }
        }

        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        import yaml
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()

        self.guard = ScopeGuard(Path(self.temp_config.name))

    def teardown_method(self):
        """Cleanup temporary files"""
        Path(self.temp_config.name).unlink()

    def test_risky_operation_detection(self):
        """Test detection of risky operations"""
        # Direct matches
        assert self.guard._is_risky_operation("nmap")
        assert self.guard._is_risky_operation("kubectl-apply")
        assert self.guard._is_risky_operation("terraform-apply")

        # Pattern matches
        assert self.guard._is_risky_operation("kubectl-delete")
        assert self.guard._is_risky_operation("kubectl-patch")

        # Safe operations
        assert not self.guard._is_risky_operation("echo")
        assert not self.guard._is_risky_operation("cat")
        assert not self.guard._is_risky_operation("ls")

    def test_safe_operations_allowed(self):
        """Test that safe operations are allowed without scope"""
        is_authorized, violation = self.guard.validate_operation("echo", "test")
        assert is_authorized
        assert violation is None

        is_authorized, violation = self.guard.validate_operation("cat", "/etc/passwd")
        assert is_authorized
        assert violation is None

class TestScopeViolations:
    """Test scope violation scenarios"""

    def setup_method(self):
        """Setup test environment"""
        self.guard = create_scope_guard()

    def test_missing_scope_artifact(self):
        """Test blocking operations without scope artifact"""
        is_authorized, violation = self.guard.validate_operation("nmap", "192.168.1.1")

        assert not is_authorized
        assert violation is not None
        assert violation.violation_type == ScopeViolationType.MISSING_SCOPE
        assert "requires scope artifact" in violation.message
        assert "scope.json" in violation.suggestion

    def test_invalid_scope_format(self):
        """Test blocking operations with malformed scope"""
        invalid_scope = {
            "client_name": "TestClient"
            # Missing required fields
        }

        is_authorized, violation = self.guard.validate_operation(
            "nmap", "192.168.1.1", invalid_scope
        )

        assert not is_authorized
        assert violation.violation_type == ScopeViolationType.INVALID_SCOPE_FORMAT
        assert "Invalid scope artifact format" in violation.message

    def test_expired_maintenance_window(self):
        """Test blocking operations outside maintenance window"""
        # Create scope with expired window
        expired_scope = {
            "client_name": "TestClient",
            "engagement_id": "test-engagement-001",
            "approver_name": "John Doe",
            "approver_email": "john.doe@company.com",
            "ticket_id": "JIRA-12345",
            "window_start": (datetime.now() - timedelta(hours=5)).isoformat(),
            "window_end": (datetime.now() - timedelta(hours=1)).isoformat(),
            "targets": {
                "ip_addresses": ["192.168.1.1"]
            },
            "operations": ["nmap"],
            "emergency_contact": "+1-555-1234"
        }

        is_authorized, violation = self.guard.validate_operation(
            "nmap", "192.168.1.1", expired_scope
        )

        assert not is_authorized
        assert violation.violation_type == ScopeViolationType.EXPIRED_WINDOW
        assert "outside maintenance window" in violation.message

    def test_unauthorized_operation(self):
        """Test blocking unauthorized operations"""
        # Create scope that doesn't include kubectl-apply
        scope = self._create_valid_scope(operations=["nmap", "kubectl-get"])

        is_authorized, violation = self.guard.validate_operation(
            "kubectl-apply", "default", scope
        )

        assert not is_authorized
        assert violation.violation_type == ScopeViolationType.UNAUTHORIZED_OPERATION
        assert "not in authorized list" in violation.message

    def test_unauthorized_target(self):
        """Test blocking operations on unauthorized targets"""
        # Create scope for specific IP range
        scope = self._create_valid_scope(
            targets={"ip_addresses": ["192.168.1.1", "192.168.1.2"]}
        )

        # Try to scan unauthorized IP
        is_authorized, violation = self.guard.validate_operation(
            "nmap", "10.0.0.1", scope
        )

        assert not is_authorized
        assert violation.violation_type == ScopeViolationType.UNAUTHORIZED_TARGET
        assert "not in authorized scope" in violation.message

    def test_dual_approval_required(self):
        """Test dual approval requirement for production"""
        scope = self._create_valid_scope(
            environment="production",
            dual_approved=False,
            targets={"namespaces": ["production"]},  # Ensure target is authorized
            operations=["kubectl-apply"]  # Ensure operation is authorized
        )

        # Mock environment rules to require dual approval
        self.guard.config["environment_rules"] = {
            "production": {"require_dual_approval": True}
        }

        is_authorized, violation = self.guard.validate_operation(
            "kubectl-apply", "production", scope, environment="production"
        )

        assert not is_authorized
        assert violation.violation_type == ScopeViolationType.DUAL_APPROVAL_REQUIRED

    def _create_valid_scope(self, **overrides):
        """Create valid scope artifact for testing"""
        base_scope = {
            "client_name": "TestClient",
            "engagement_id": "test-engagement-001",
            "approver_name": "John Doe",
            "approver_email": "john.doe@company.com",
            "ticket_id": "JIRA-12345",
            "window_start": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "window_end": (datetime.now() + timedelta(hours=2)).isoformat(),
            "targets": {
                "ip_addresses": ["192.168.1.1"],
                "cidr_blocks": ["10.0.0.0/24"],
                "namespaces": ["default", "staging"]
            },
            "operations": ["nmap", "kubectl-apply", "kubectl-get"],
            "emergency_contact": "+1-555-1234",
            "environment": "staging",
            "dual_approved": False
        }

        base_scope.update(overrides)
        return base_scope

class TestTargetAuthorization:
    """Test target authorization logic"""

    def setup_method(self):
        self.guard = create_scope_guard()

    def test_ip_address_authorization(self):
        """Test IP address authorization"""
        scope = ScopeArtifact(
            client_name="TestClient",
            engagement_id="test-001",
            approver_name="John Doe",
            approver_email="john@company.com",
            ticket_id="JIRA-123",
            window_start=datetime.now(),
            window_end=datetime.now() + timedelta(hours=2),
            targets={
                "ip_addresses": ["192.168.1.1", "192.168.1.2"],
                "cidr_blocks": ["10.0.0.0/24"]
            },
            operations=["nmap"],
            emergency_contact="+1-555-1234"
        )

        # Authorized IPs
        assert self.guard._is_target_authorized("192.168.1.1", scope)
        assert self.guard._is_target_authorized("192.168.1.2", scope)
        assert self.guard._is_target_authorized("10.0.0.50", scope)  # In CIDR

        # Unauthorized IPs
        assert not self.guard._is_target_authorized("172.16.0.1", scope)
        assert not self.guard._is_target_authorized("192.168.2.1", scope)

    def test_hostname_authorization(self):
        """Test hostname authorization"""
        scope = ScopeArtifact(
            client_name="TestClient",
            engagement_id="test-001",
            approver_name="John Doe",
            approver_email="john@company.com",
            ticket_id="JIRA-123",
            window_start=datetime.now(),
            window_end=datetime.now() + timedelta(hours=2),
            targets={
                "hostnames": ["app.client.com", "db.client.com"]
            },
            operations=["nmap"],
            emergency_contact="+1-555-1234"
        )

        # Authorized hostnames
        assert self.guard._is_target_authorized("app.client.com", scope)
        assert self.guard._is_target_authorized("db.client.com", scope)

        # Unauthorized hostnames
        assert not self.guard._is_target_authorized("evil.hacker.com", scope)
        assert not self.guard._is_target_authorized("app.competitor.com", scope)

    def test_namespace_authorization(self):
        """Test Kubernetes namespace authorization"""
        scope = ScopeArtifact(
            client_name="TestClient",
            engagement_id="test-001",
            approver_name="John Doe",
            approver_email="john@company.com",
            ticket_id="JIRA-123",
            window_start=datetime.now(),
            window_end=datetime.now() + timedelta(hours=2),
            targets={
                "namespaces": ["default", "staging", "monitoring"]
            },
            operations=["kubectl-get"],
            emergency_contact="+1-555-1234"
        )

        # Authorized namespaces
        assert self.guard._is_target_authorized("default", scope)
        assert self.guard._is_target_authorized("staging", scope)
        assert self.guard._is_target_authorized("monitoring", scope)

        # Unauthorized namespaces
        assert not self.guard._is_target_authorized("production", scope)
        assert not self.guard._is_target_authorized("kube-system", scope)

class TestValidAuthorizations:
    """Test scenarios that should be authorized"""

    def setup_method(self):
        self.guard = create_scope_guard()

    def test_valid_network_scan(self):
        """Test authorized network scan"""
        scope = {
            "client_name": "SecureCorpLtd",
            "engagement_id": "pentest-2025-001",
            "approver_name": "Jane Smith",
            "approver_email": "jane.smith@company.com",
            "ticket_id": "JIRA-9876",
            "window_start": (datetime.now() - timedelta(minutes=10)).isoformat(),
            "window_end": (datetime.now() + timedelta(hours=3)).isoformat(),
            "targets": {
                "cidr_blocks": ["192.168.1.0/24"],
                "ip_addresses": ["10.0.0.100"]
            },
            "operations": ["nmap", "nmap-scan"],
            "emergency_contact": "security@securecorp.com"
        }

        # Should be authorized
        is_authorized, violation = self.guard.validate_operation(
            "nmap", "192.168.1.50", scope
        )

        assert is_authorized
        assert violation is None

    def test_valid_kubernetes_operation(self):
        """Test authorized kubectl operation"""
        scope = {
            "client_name": "KubernetesClient",
            "engagement_id": "k8s-audit-2025-002",
            "approver_name": "Bob Wilson",
            "approver_email": "bob.wilson@company.com",
            "ticket_id": "SNOW-5555",
            "window_start": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "window_end": (datetime.now() + timedelta(hours=4)).isoformat(),
            "targets": {
                "namespaces": ["default", "kube-system", "monitoring"]
            },
            "operations": ["kubectl-get", "kubectl-describe", "kubectl-apply"],
            "emergency_contact": "+1-800-HELP",
            "environment": "staging",
            "dual_approved": False
        }

        # Should be authorized for staging (no dual approval required)
        is_authorized, violation = self.guard.validate_operation(
            "kubectl-get", "default", scope, environment="staging"
        )

        assert is_authorized
        assert violation is None

    def test_wildcard_operations(self):
        """Test wildcard operation authorization"""
        scope = {
            "client_name": "AdminClient",
            "engagement_id": "admin-2025-003",
            "approver_name": "Admin User",
            "approver_email": "admin@company.com",
            "ticket_id": "ADMIN-1111",
            "window_start": (datetime.now() - timedelta(minutes=15)).isoformat(),
            "window_end": (datetime.now() + timedelta(hours=1)).isoformat(),
            "targets": {
                "namespaces": ["*"]
            },
            "operations": ["*"],  # All operations allowed
            "emergency_contact": "admin@company.com"
        }

        # Any operation should be authorized
        is_authorized, violation = self.guard.validate_operation(
            "kubectl-delete", "any-namespace", scope
        )

        assert is_authorized
        assert violation is None

class TestScopeArtifactGeneration:
    """Test scope artifact template generation"""

    def setup_method(self):
        self.guard = create_scope_guard()

    def test_scope_template_generation(self):
        """Test generation of scope artifact templates"""
        template = self.guard.generate_scope_template("TestClient", "vulnerability_assessment")

        # Check required fields are present
        assert template["client_name"] == "TestClient"
        assert "vulnerability_assessment" in template["engagement_id"]
        assert "REQUIRED:" in template["approver_name"]
        assert "targets" in template
        assert "operations" in template
        assert isinstance(template["targets"]["cidr_blocks"], list)
        assert isinstance(template["operations"], list)

    def test_scope_artifact_validation_helper(self):
        """Test scope artifact validation helper function"""
        # Valid scope
        valid_scope = {
            "client_name": "TestClient",
            "engagement_id": "test-001",
            "approver_name": "John Doe",
            "approver_email": "john@company.com",
            "ticket_id": "JIRA-123",
            "window_start": datetime.now().isoformat(),
            "window_end": (datetime.now() + timedelta(hours=2)).isoformat(),
            "targets": {"ip_addresses": ["192.168.1.1"]},
            "operations": ["nmap"],
            "emergency_contact": "+1-555-1234"
        }

        is_valid, message = validate_scope_artifact(valid_scope)
        assert is_valid
        assert "valid" in message

        # Invalid scope
        invalid_scope = {"client_name": "TestClient"}

        is_valid, message = validate_scope_artifact(invalid_scope)
        assert not is_valid
        assert "Missing required field" in message

class TestViolationLogging:
    """Test violation logging and evidence generation"""

    def test_violation_logging(self):
        """Test logging of scope violations"""
        guard = create_scope_guard()

        violation = ScopeViolation(
            violation_type=ScopeViolationType.MISSING_SCOPE,
            operation="nmap",
            target="192.168.1.1",
            message="Test violation message",
            suggestion="Test suggestion",
            timestamp=datetime.now()
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            evidence_path = Path(temp_dir)
            log_entry = guard.log_violation(violation, evidence_path)

            # Check log entry format
            log_data = json.loads(log_entry)
            assert log_data["violation_type"] == "missing_scope_artifact"
            assert log_data["operation"] == "nmap"
            assert log_data["severity"] == "HIGH"
            assert log_data["blocked"] is True

            # Check file was created
            violation_file = evidence_path / "scope_violations.jsonl"
            assert violation_file.exists()

            # Check file content
            with open(violation_file) as f:
                logged_data = json.loads(f.read().strip())
                assert logged_data == log_data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])