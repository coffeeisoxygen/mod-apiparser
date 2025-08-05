"""Test TOML configuration loading."""

import sys
from pathlib import Path

# Add src to path so we can import mlogger
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.mlogger import LogConfig, LoggerManager


def test_toml_config():
    """Test loading configuration from TOML file."""
    print("Testing TOML configuration loading...")

    # Test 1: Load from existing TOML file
    print("1. Loading from log_config.toml...")
    config = LogConfig.from_toml_file("log_config.toml")
    print(f"   Level: {config.level}")
    print(f"   To terminal: {config.to_terminal}")
    print(f"   To file: {config.to_file}")
    print(f"   Log path: {config.log_path}")

    # Test 2: Load from non-existent file (should use defaults)
    print("\n2. Loading from non-existent file...")
    config_default = LogConfig.from_toml_file("non_existent.toml")
    print(f"   Level: {config_default.level}")
    print(f"   To terminal: {config_default.to_terminal}")

    # Test 3: Setup logger with TOML config
    print("\n3. Setting up logger with TOML config...")
    manager = LoggerManager(config)
    manager.setup()

    from src.utils.mlogger import logger

    logger.info("✅ TOML configuration loaded successfully!")
    logger.debug("This is a debug message with TOML config")

    print("\n✅ All TOML configuration tests passed!")


if __name__ == "__main__":
    test_toml_config()
