"""Tests for environment setup functionality.

Test structure mirrors the source structure:
- scripts/env_input.py -> tests/scripts/test_env_input.py
"""

import base64
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet
from scripts.env_input import app, create_base_env_content, generate_secure_keys
from typer.testing import CliRunner

# Test marks for organization
pytestmark = pytest.mark.unit


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_env_dir():
    """Temporary directory for environment files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        yield temp_path


@pytest.fixture
def mock_env_files(temp_env_dir):
    """Mock ENV_FILES to use temporary directory."""
    mock_files = {
        "base": temp_env_dir / ".env",
        "dev": temp_env_dir / ".env.dev",
        "prod": temp_env_dir / ".env.prod",
        "test": temp_env_dir / ".env.test",
        "example": temp_env_dir / ".env.example",
    }
    with (
        patch("scripts.env_input.ENV_FILES", mock_files),
        patch("scripts.env_input.BASE_DIR", temp_env_dir),
    ):
        yield mock_files


class TestKeyGeneration:
    """Test secure key generation."""

    def test_generate_secure_keys_returns_all_required_keys(self):
        """Test that all required keys are generated."""
        keys = generate_secure_keys()

        expected_keys = {
            "fernet_key",
            "jwt_secret_dev",
            "jwt_secret_prod",
            "jwt_secret_test",
            "security_secret_dev",
            "security_secret_prod",
            "security_secret_test",
        }

        assert set(keys.keys()) == expected_keys

        # Verify all keys are non-empty strings
        for value in keys.values():
            assert isinstance(value, str)
            assert len(value) > 0

    def test_generate_secure_keys_creates_unique_keys(self):
        """Test that multiple generations create unique keys."""
        keys1 = generate_secure_keys()
        keys2 = generate_secure_keys()

        # All keys should be different (except test keys which are predictable)
        for key in [
            "jwt_secret_dev",
            "jwt_secret_prod",
            "security_secret_dev",
            "security_secret_prod",
        ]:
            assert keys1[key] != keys2[key]

        # Test keys should be predictable/same
        assert keys1["jwt_secret_test"] == keys2["jwt_secret_test"]
        assert keys1["security_secret_test"] == keys2["security_secret_test"]

    def test_fernet_key_is_valid_base64(self):
        """Test that Fernet key is valid base64."""
        keys = generate_secure_keys()
        fernet_key = keys["fernet_key"]

        # Should be valid base64
        try:
            base64.urlsafe_b64decode(fernet_key)
        except Exception:
            pytest.fail("Fernet key is not valid base64")

        # Should be valid Fernet key
        try:
            Fernet(fernet_key.encode())
        except Exception:
            pytest.fail("Generated key is not valid for Fernet")


class TestEnvironmentFileCreation:
    """Test environment file creation."""

    def test_create_base_env_content_contains_required_sections(self):
        """Test that base environment file contains all required sections."""
        keys = generate_secure_keys()
        content = create_base_env_content(keys)

        required_sections = [
            "APPLICATION SETTINGS",
            "SECURITY & ENCRYPTION",
            "JWT TOKEN SETTINGS",
            "FILE PATHS",
            "PRODUCTION SECURITY",
        ]

        for section in required_sections:
            assert section in content

    def test_create_base_env_content_uses_provided_keys(self):
        """Test that environment content uses the provided keys."""
        test_keys = {
            "security_secret_dev": "test-security-key",
            "jwt_secret_dev": "test-jwt-key",
        }

        content = create_base_env_content(test_keys)

        assert "SECURITY_SECRET_KEY=test-security-key" in content
        assert "JWT_SECRET_KEY=test-jwt-key" in content

    def test_create_base_env_content_has_proper_format(self):
        """Test that environment file has proper format."""
        keys = generate_secure_keys()
        content = create_base_env_content(keys)

        lines = content.split("\n")

        # Should have comments (lines starting with #)
        comment_lines = [line for line in lines if line.startswith("#")]
        assert len(comment_lines) > 0

        # Should have key=value pairs
        config_lines = [
            line for line in lines if "=" in line and not line.startswith("#")
        ]
        assert len(config_lines) > 0

        # Check some specific required config keys
        config_content = "\n".join(config_lines)
        required_configs = [
            "APP_DEBUG=",
            "APP_ENV=",
            "APP_SERVICE=",
            "SECURITY_SECRET_KEY=",
            "JWT_SECRET_KEY=",
        ]

        for config in required_configs:
            assert config in config_content


class TestCLICommands:
    """Test CLI commands."""

    def test_show_info_command_success(self, runner):
        """Test show-info command runs successfully."""
        result = runner.invoke(app, ["show-info"])
        assert result.exit_code == 0
        assert "Environment Files Status" in result.stdout

    def test_show_info_shows_missing_files(self, runner, mock_env_files):
        """Test show-info correctly identifies missing files."""
        # Ensure all files are removed to simulate missing files
        for path in mock_env_files.values():
            if path.exists():
                path.unlink()
        result = runner.invoke(app, ["show-info"])
        assert result.exit_code == 0
        assert "❌ MISSING" in result.stdout

    def test_show_info_shows_existing_files(self, runner, mock_env_files):
        """Test show-info correctly identifies existing files."""
        # Create one file
        mock_env_files["dev"].touch()

        result = runner.invoke(app, ["show-info"])
        assert result.exit_code == 0
        assert "✅ EXISTS" in result.stdout

    def test_validate_command_fails_with_missing_files(self, runner, mock_env_files):
        """Test validate command fails when files are missing."""
        # Ensure files don't exist in temp directory
        for path in mock_env_files.values():
            if path.exists():
                path.unlink()

        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 1
        assert "Validation failed" in result.stdout

    def test_validate_command_succeeds_with_all_files(self, runner, mock_env_files):
        """Test validate command succeeds when all files exist."""
        # Create all required files (excluding example)
        for name, path in mock_env_files.items():
            if name != "example":
                path.touch()

        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 0
        assert "All environment files present" in result.stdout

    @patch("scripts.env_input.generate_secure_keys")
    def test_env_setup_command_creates_files(self, mock_keys, runner, mock_env_files):
        """Test env-setup command creates environment files."""
        # Mock key generation
        mock_keys.return_value = {
            "fernet_key": "test-fernet",
            "jwt_secret_dev": "test-jwt-dev",
            "jwt_secret_prod": "test-jwt-prod",
            "jwt_secret_test": "test-jwt-test",
            "security_secret_dev": "test-sec-dev",
            "security_secret_prod": "test-sec-prod",
            "security_secret_test": "test-sec-test",
        }

        result = runner.invoke(app, ["env-setup"])
        assert result.exit_code == 0
        assert "Environment setup completed successfully" in result.stdout

        # Check that files were created
        for name, path in mock_env_files.items():
            if name not in ["example"]:  # Don't check example file
                assert path.exists(), f"{name} file should be created"

    def test_env_setup_command_prompts_for_overwrite(self, runner, mock_env_files):
        """Test env-setup prompts when files exist."""
        # Create existing file
        mock_env_files["dev"].touch()

        # Test declining overwrite
        result = runner.invoke(app, ["env-setup"], input="n\n")
        assert result.exit_code == 1
        assert "cancelled by user" in result.stdout

    def test_clean_command_removes_files(self, runner, mock_env_files):
        """Test clean command removes environment files."""
        # Create some files
        mock_env_files["dev"].touch()
        mock_env_files["prod"].touch()

        # Confirm removal
        result = runner.invoke(app, ["clean"], input="y\n")
        assert result.exit_code == 0
        assert "Removed" in result.stdout

        # Files should be gone
        assert not mock_env_files["dev"].exists()
        assert not mock_env_files["prod"].exists()

    def test_clean_command_can_be_cancelled(self, runner, mock_env_files):
        """Test clean command can be cancelled."""
        # Create file
        mock_env_files["dev"].touch()

        # Decline removal
        result = runner.invoke(app, ["clean"], input="n\n")
        assert result.exit_code == 0
        assert "cancelled" in result.stdout

        # File should still exist
        assert mock_env_files["dev"].exists()


# class TestFailFastBehavior:
#     """Test fail-fast behavior."""

#     def test_env_setup_fails_fast_on_exception(self, runner):
#         """Test that env-setup fails fast on any exception."""
#         with patch(
#             "scripts.env_input.generate_secure_keys",
#             side_effect=Exception("Test error"),
#         ):
#             result = runner.invoke(app, ["env-setup"])
#             assert result.exit_code == 1
#             # Accept either error message variant
#             assert (
#                 "Environment setup failed" in result.stdout
#                 or "cancelled by user" in result.stdout
#             )

#     def test_validate_fails_fast_on_missing_files(self, runner):
#         """Test that validate fails immediately when files are missing."""
#         result = runner.invoke(app, ["validate"])
#         assert result.exit_code == 1
# Should not proceed with other operations


class TestDirectoryStructure:
    """Test directory structure creation."""

    @patch("scripts.env_input.generate_secure_keys")
    def test_env_setup_creates_secrets_directory(
        self, mock_keys, runner, mock_env_files
    ):
        """Test that env-setup creates secrets directory structure."""
        mock_keys.return_value = generate_secure_keys()

        result = runner.invoke(app, ["env-setup"])
        assert result.exit_code == 0

        # Check secrets directory structure
        secrets_dir = mock_env_files["base"].parent / "secrets"
        keys_dir = secrets_dir / "keys"

        assert secrets_dir.exists()
        assert keys_dir.exists()
