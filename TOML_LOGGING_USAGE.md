# Contoh Penggunaan Logging dengan TOML Configuration

## 1. Setup Logging dari TOML (Recommended)

```python
from src.utils.mlogger import setup_logging_from_toml, logger

# Load konfigurasi dari log_config.toml
setup_logging_from_toml()

# Sekarang bisa langsung pakai logger
logger.info("Application started")
logger.debug("Debug information")
logger.warning("This is a warning")
logger.error("Error occurred")
```

## 2. Setup Logging dengan Parameter Langsung

```python
from src.utils.mlogger import setup_logging, logger

# Setup dengan parameter langsung
setup_logging(
    level="DEBUG",
    to_terminal=True,
    to_file=True,
    log_path="logs"
)

logger.info("Logging configured programmatically")
```

## 3. Setup Manual dengan LogConfig dan LoggerManager

```python
from src.utils.mlogger import LogConfig, LoggerManager, logger

# Konfigurasi manual
config = LogConfig(
    level="INFO",
    to_terminal=True,
    to_file=True,
    bind_context={"service": "api-parser", "version": "1.0.0"}
)

manager = LoggerManager(config)
manager.setup()

logger.info("Manual setup complete")
```

## 4. Menggunakan Decorators dan Context Managers

```python
from src.utils.mlogger import LoggerManager

@LoggerManager.log_traced(level="INFO", timing=True)
def process_data(data):
    return data.upper()

# Context manager untuk profiling
with LoggerManager.log_block("data processing"):
    result = process_data("hello world")
```

## 5. File log_config.toml

Buat file `log_config.toml` di root project:

```toml
[logging]
level = "INFO"
to_terminal = true
to_file = true
log_path = "logs"
name_prefix = "app"
size_mb = 10
retention_days = 7
intercept = true

[logging.bind_context]
service = "mod-apiparser"
version = "1.0.0"
```

## Keuntungan Menggunakan TOML Configuration

1. **Separation of Concerns**: Konfigurasi terpisah dari kode
2. **Environment-specific**: Bisa pakai file berbeda untuk dev/prod
3. **Fallback to Defaults**: Jika file tidak ada atau field missing, akan pakai default
4. **Type Safe**: Validasi otomatis untuk semua field
5. **Easy to Read**: Format TOML sangat mudah dibaca dan diedit
