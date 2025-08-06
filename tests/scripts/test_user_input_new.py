import yaml
import pytest
from typer.testing import CliRunner
from scripts.user_input_new import app, AdminUserInput, save_admin_to_yaml

pytestmark = pytest.mark.unit

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def temp_secrets_dir(tmp_path, monkeypatch):
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    monkeypatch.setattr("scripts.user_input_new.Path", lambda *a, **k: tmp_path)
    return secrets_dir

def test_admin_user_input_validation_success():
    user = AdminUserInput(
        username="adminuser",
        email="admin@example.com",
        name="Admin User",
        password="securepass"
    )
    assert user.username == "adminuser"
    assert user.is_active is True
    assert user.is_superuser is True

def test_admin_user_input_validation_fail():
    with pytest.raises(Exception):
        AdminUserInput(
            username="a",  # too short
            email="not-an-email",
            name="A",
            password="123"
        )

def test_save_admin_to_yaml_creates_file(tmp_path, monkeypatch):
    # Patch Path to use tmp_path as base_dir
    monkeypatch.setattr("scripts.user_input_new.Path", lambda *a, **k: tmp_path)
    user = AdminUserInput(
        username="admin",
        email="admin@example.com",
        name="Admin",
        password="password123"
    )
    save_admin_to_yaml(user, env="dev")
    yaml_file = tmp_path / "secrets" / "dev_users.yaml"
    assert yaml_file.exists()
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    assert any(u["username"] == "admin" for u in data["users"])

def test_save_admin_to_yaml_updates_existing(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.user_input_new.Path", lambda *a, **k: tmp_path)
    secrets = tmp_path / "secrets"
    secrets.mkdir()
    yaml_file = secrets / "dev_users.yaml"
    # Prepopulate with a user
    with open(yaml_file, "w") as f:
        yaml.dump({"users": [{"username": "admin", "email": "old@mail.com", "name": "Old", "password": "x", "is_active": True, "is_superuser": True}]}, f)
    user = AdminUserInput(
        username="admin",
        email="new@mail.com",
        name="New Name",
        password="newpass"
    )
    save_admin_to_yaml(user, env="dev")
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    assert any(u["email"] == "new@mail.com" for u in data["users"])

def test_create_admin_command_interactive(monkeypatch, runner, tmp_path):
    # Patch Path to use tmp_path as base_dir
    monkeypatch.setattr("scripts.user_input_new.Path", lambda *a, **k: tmp_path)
    inputs = "\n".join(["admin", "admin@example.com", "Administrator", "password123"])
    result = runner.invoke(app, ["create-admin"], input=inputs)
    assert result.exit_code == 0
    assert "created successfully" in result.stdout

def test_create_admin_command_with_options(monkeypatch, runner, tmp_path):
    monkeypatch.setattr("scripts.user_input_new.Path", lambda *a, **k: tmp_path)
    result = runner.invoke(
        app,
        [
            "create-admin",
            "--username", "admin2",
            "--email", "admin2@example.com",
            "--name", "Admin Two",
            "--password", "password456",
            "--env", "test"
        ]
    )
    assert result.exit_code == 0
    assert "created successfully" in result.stdout
    yaml_file = tmp_path / "secrets" / "test_users.yaml"
    assert yaml_file.exists()

def test_show_info_command(monkeypatch, runner, tmp_path):
    monkeypatch.setattr("scripts.user_input_new.Path", lambda *a, **k: tmp_path)
    secrets = tmp_path / "secrets"
    secrets.mkdir()
    # Create dev_users.yaml with one user
    with open(secrets / "dev_users.yaml", "w") as f:
        yaml.dump({"users": [{"username": "admin", "email": "admin@example.com", "name": "Admin", "password": "x", "is_active": True, "is_superuser": True}]}, f)
    result = runner.invoke(app, ["show-info"])
    assert result.exit_code == 0
    assert "DEV Environment" in result.stdout
    assert "admin@example.com" in result.stdout
