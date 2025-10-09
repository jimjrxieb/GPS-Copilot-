"""
Comprehensive security tests for evidence system
Tests redaction, path traversal protection, RBAC, and data integrity
"""

import pytest
import json
import tempfile
import hashlib
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open

from mcp.evidence_writer import _redact, EvidenceSession
from mcp.middleware.rbac import TenantRBACMiddleware, generate_tenant_token
from mcp.routes.evidence import safe_join, EVIDENCE_ROOT


class TestRedactionSecurity:
    """Test secret redaction functionality"""

    def test_aws_key_redaction(self):
        """Test AWS access key detection and redaction"""
        test_cases = [
            "AWS key: AKIA1234567890123456",
            "export AWS_ACCESS_KEY_ID=AKIAJKLMNOPQRSTUVWXY",
            "Connection string with AKIA1234567890ABCDEF embedded",
        ]

        for case in test_cases:
            redacted = _redact(case)
            assert "AKIA" not in redacted
            assert "***REDACTED***" in redacted

    def test_github_token_redaction(self):
        """Test GitHub token detection and redaction"""
        test_cases = [
            "github token: ghp_1234567890abcdef1234567890abcdef12345678",
            "Authorization: token ghp_abcdefghijklmnopqrstuvwxyz1234567890",
            "curl -H 'Authorization: Bearer ghp_secrettoken123456789012345678901234567890'",
        ]

        for case in test_cases:
            redacted = _redact(case)
            assert "ghp_" not in redacted
            assert "***REDACTED***" in redacted

    def test_jwt_token_redaction(self):
        """Test JWT token detection and redaction"""
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        redacted = _redact(f"Token: {jwt_token}")
        assert jwt_token not in redacted
        assert "***REDACTED***" in redacted

    def test_openai_key_redaction(self):
        """Test OpenAI API key detection and redaction"""
        openai_key = "sk-1234567890abcdef1234567890abcdef1234567890abcdef"

        redacted = _redact(f"OPENAI_API_KEY={openai_key}")
        assert openai_key not in redacted
        assert "***REDACTED***" in redacted

    def test_password_field_redaction(self):
        """Test password field redaction"""
        test_cases = [
            'password: "secretpass123"',
            '"password": "admin123"',
            "password=mysecretpassword",
            "token: secrettoken123",
            '"token": "bearer_token_here"',
        ]

        for case in test_cases:
            redacted = _redact(case)
            # Passwords should be redacted but structure preserved
            assert "***REDACTED***" in redacted
            assert "password" in redacted.lower() or "token" in redacted.lower()

    def test_recursive_redaction(self):
        """Test redaction works on nested data structures"""
        session = EvidenceSession("test", "test", "test")

        test_data = {
            "config": {
                "aws_key": "AKIA1234567890123456",
                "database": {
                    "password": "secretpass123",
                    "connection": "postgres://user:secretpass@localhost/db"
                }
            },
            "logs": [
                "INFO: Starting with token ghp_1234567890abcdef1234567890abcdef12345678",
                "ERROR: Authentication failed for JWT eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.abc123"
            ]
        }

        redacted = session._redact_recursive(test_data)

        # Verify nested redaction
        assert "AKIA" not in str(redacted)
        assert "ghp_" not in str(redacted)
        assert "eyJhbGciOiJIUzI1NiJ9" not in str(redacted)
        assert "***REDACTED***" in str(redacted)

    def test_non_secret_preservation(self):
        """Test that non-secret data is preserved"""
        normal_text = "This is a normal log message with no secrets"
        redacted = _redact(normal_text)
        assert redacted == normal_text

    def test_empty_and_none_handling(self):
        """Test edge cases for redaction"""
        assert _redact("") == ""
        assert _redact(None) is None
        assert _redact(123) == 123  # Non-string types should pass through


class TestPathTraversalSecurity:
    """Test path traversal protection"""

    def test_basic_traversal_blocked(self):
        """Test basic ../ path traversal is blocked"""
        with pytest.raises(Exception):
            safe_join(Path("/safe/root"), "default", "../../../etc/passwd")

    def test_encoded_traversal_blocked(self):
        """Test URL-encoded path traversal is blocked"""
        with pytest.raises(Exception):
            safe_join(Path("/safe/root"), "default", "..%2F..%2F..%2Fetc%2Fpasswd")

    def test_double_encoded_traversal_blocked(self):
        """Test double-encoded path traversal is blocked"""
        with pytest.raises(Exception):
            safe_join(Path("/safe/root"), "default", "..%252F..%252F..%252Fetc%252Fpasswd")

    def test_absolute_path_blocked(self):
        """Test absolute paths are blocked"""
        with pytest.raises(Exception):
            safe_join(Path("/safe/root"), "default", "/etc/passwd")

    def test_symlink_traversal_blocked(self):
        """Test symlink-based traversal is blocked"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            root_path = temp_path / "evidence_root"
            root_path.mkdir()

            # Create symlink that points outside
            symlink_path = root_path / "malicious_link"
            symlink_path.symlink_to("/etc")

            with pytest.raises(Exception):
                safe_join(root_path, "default", "malicious_link/passwd")

    def test_valid_paths_allowed(self):
        """Test valid paths within tenant boundary are allowed"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            tenant_path = root_path / "default" / "evidence"
            tenant_path.mkdir(parents=True)

            # Valid paths should work
            result = safe_join(root_path, "default", "evidence/2025/09/15/test.json")
            expected = tenant_path / "2025/09/15/test.json"
            assert result.resolve() == expected.resolve()

    def test_tenant_isolation(self):
        """Test tenants cannot access each other's data"""
        with pytest.raises(Exception):
            safe_join(Path("/evidence"), "tenant_a", "../tenant_b/secret.json")


class TestRBACMiddleware:
    """Test RBAC middleware functionality"""

    def test_token_generation(self):
        """Test tenant token generation"""
        secret = "test_secret_key_12345"
        tenant = "test_tenant"

        token1 = generate_tenant_token(tenant, secret)
        token2 = generate_tenant_token(tenant, secret)

        # Same inputs should produce same token
        assert token1 == token2

        # Different tenants should produce different tokens
        token3 = generate_tenant_token("different_tenant", secret)
        assert token1 != token3

    def test_token_validation(self):
        """Test token validation logic"""
        middleware = TenantRBACMiddleware(None)
        secret = "test_secret_123"
        tenant = "test_tenant"

        valid_token = generate_tenant_token(tenant, secret)

        # Mock environment variable
        with patch.dict('os.environ', {'EVIDENCE_DEFAULT_SECRET': secret}):
            assert middleware.validate_tenant_token(tenant, valid_token)
            assert not middleware.validate_tenant_token(tenant, "invalid_token")
            assert not middleware.validate_tenant_token("wrong_tenant", valid_token)

    def test_missing_headers_rejected(self):
        """Test requests with missing headers are rejected"""
        from main import app
        client = TestClient(app)

        # Request without auth headers should be rejected
        response = client.get("/mcp/evidence/list?tenant=default")
        assert response.status_code in [401, 403]

    def test_bypass_paths_allowed(self):
        """Test bypass paths work without authentication"""
        from main import app
        client = TestClient(app)

        # Health check should work without auth
        response = client.get("/healthz")
        assert response.status_code == 200


class TestDataIntegrity:
    """Test data integrity and verification"""

    def test_sha256_integrity_verification(self):
        """Test SHA256 hash generation and verification"""
        test_data = "This is test evidence data"
        expected_hash = hashlib.sha256(test_data.encode()).hexdigest()

        # Test evidence session generates correct hashes
        with tempfile.TemporaryDirectory() as temp_dir:
            session = EvidenceSession("test", "test", "test")
            session.base_path = Path(temp_dir) / "session"
            session.base_path.mkdir(parents=True)

            artifact_path, artifact_hash = session.write_artifact("test.txt", test_data)

            assert artifact_hash == expected_hash

    def test_evidence_tampering_detection(self):
        """Test that tampered evidence can be detected"""
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence_file = Path(temp_dir) / "evidence.json"

            # Create evidence with hash
            original_data = {"test": "data", "timestamp": "2025-09-15"}
            original_content = json.dumps(original_data)
            original_hash = hashlib.sha256(original_content.encode()).hexdigest()

            evidence_file.write_text(original_content)

            # Verify original hash matches
            current_hash = hashlib.sha256(evidence_file.read_bytes()).hexdigest()
            assert current_hash == original_hash

            # Tamper with evidence
            tampered_data = {"test": "modified", "timestamp": "2025-09-15"}
            evidence_file.write_text(json.dumps(tampered_data))

            # Verify hash no longer matches
            tampered_hash = hashlib.sha256(evidence_file.read_bytes()).hexdigest()
            assert tampered_hash != original_hash

    def test_concurrent_index_access(self):
        """Test atomic index operations prevent corruption"""
        # This would require threading/multiprocessing to test properly
        # For now, verify the locking mechanism exists
        from evidence_sidecar.main import EvidenceSidecar

        sidecar = EvidenceSidecar("/tmp/input", "/tmp/output", "test")

        # Verify atomic operations exist
        assert hasattr(sidecar, 'locked_index_file')
        assert hasattr(sidecar, 'atomic_write_json')
        assert hasattr(sidecar, 'atomic_append_jsonl')


class TestSecurityConfiguration:
    """Test security configuration and settings"""

    def test_file_extension_allowlist(self):
        """Test only allowed file extensions can be served"""
        from mcp.routes.evidence import ALLOWED_EXTENSIONS

        # Known safe extensions should be allowed
        assert '.json' in ALLOWED_EXTENSIONS
        assert '.txt' in ALLOWED_EXTENSIONS
        assert '.md' in ALLOWED_EXTENSIONS

        # Dangerous extensions should not be allowed
        assert '.exe' not in ALLOWED_EXTENSIONS
        assert '.sh' not in ALLOWED_EXTENSIONS
        assert '.php' not in ALLOWED_EXTENSIONS

    def test_max_response_size_enforced(self):
        """Test maximum response size is enforced"""
        from mcp.routes.evidence import MAX_RESPONSE_SIZE

        # Should have reasonable limit (not unlimited)
        assert MAX_RESPONSE_SIZE > 0
        assert MAX_RESPONSE_SIZE <= 10 * 1024 * 1024  # Max 10MB


def test_full_security_workflow():
    """Integration test for complete security workflow"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Create evidence session with sensitive data
        session = EvidenceSession("secure_tenant", "security_agent", "sec_task_001")
        session.base_path = Path(temp_dir) / "session"
        session.base_path.mkdir(parents=True)

        # 2. Write metadata with secrets (should be redacted)
        session.write_meta({
            "autonomy_level": "L2",
            "aws_credentials": "AKIA1234567890123456",
            "github_token": "ghp_secrettoken123456789012345678901234567890"
        })

        # 3. Write log with secrets (should be redacted)
        session.append_log('stdout', {
            'message': 'Connecting with JWT eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.test',
            'level': 'info'
        })

        # 4. Write artifact (should have integrity hash)
        artifact_path, artifact_hash = session.write_artifact(
            'scan_results.json',
            '{"vulnerabilities": ["CVE-2023-1234"], "secret": "ghp_anothersecret123"}'
        )

        # 5. Finalize session
        result = session.finalize()

        # 6. Verify security measures
        # Check that secrets were redacted in logs
        log_file = session.base_path / "stdout.jsonl"
        log_content = log_file.read_text()
        assert "eyJhbGciOiJIUzI1NiJ9" not in log_content  # JWT redacted
        assert "***REDACTED***" in log_content

        # Check that artifacts have integrity hashes
        assert artifact_hash is not None
        assert len(artifact_hash) == 64  # SHA256 length

        # Check that metadata was redacted
        meta_file = session.base_path / "meta.json"
        meta_content = meta_file.read_text()
        assert "AKIA1234567890123456" not in meta_content  # AWS key redacted
        assert "ghp_secrettoken" not in meta_content  # GitHub token redacted

        # 7. Verify evidence structure is maintained
        assert result['evidence_session'] is not None
        assert len(result['files']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])