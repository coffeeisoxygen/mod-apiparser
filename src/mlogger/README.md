# MLogger - Modular Logging System

Sistem logging modular yang sophisticated berdasarkan Loguru dengan fitur-fitur advanced untuk API parser.

## 📋 Daftar Isi

- [Instalasi dan Setup](#instalasi-dan-setup)
- [Kapan Menggunakan Logger Apa](#kapan-menggunakan-logger-apa)
- [Level Logging yang Tepat](#level-logging-yang-tepat)
- [Utility Functions](#utility-functions)
- [Examples dan Best Practices](#examples-dan-best-practices)
- [Konfigurasi](#konfigurasi)
- [Advanced Features](#advanced-features)

## 🚀 Instalasi dan Setup

### Quick Start

```python
from src.mlogger import get_logger

# Logger otomatis setup dari log_config.toml
logger = get_logger(__name__)
logger.info("Logger siap digunakan!")
```

### Manual Setup

```python
from src.mlogger import setup_logging_from_toml, get_logger

# Setup manual jika dibutuhkan
setup_logging_from_toml("path/to/config.toml")
logger = get_logger("my_module")
```

## 🎯 Kapan Menggunakan Logger Apa

### 1. Logger Standar (`get_logger()`)

**Gunakan untuk**: Logging umum dalam aplikasi

```python
from src.mlogger import get_logger

# Logger dengan nama module
logger = get_logger(__name__)

# Logger dengan nama custom
api_logger = get_logger("api_handler")
db_logger = get_logger("database")
```

**Kapan menggunakan**:

- ✅ Logging umum dalam class/function
- ✅ Tracking alur eksekusi program
- ✅ Debugging dan monitoring
- ✅ Error handling standar

### 2. Structured Logging (`create_structured_log()`)

**Gunakan untuk**: Logging dengan metadata yang konsisten

```python
from src.mlogger.utils import create_structured_log

# Log dengan struktur yang konsisten
create_structured_log(
    level="INFO",
    message="User login successful",
    component="auth",
    operation="login",
    user_id="user123",
    request_id="req-456",
    extra_fields={"ip_address": "192.168.1.1"}
)
```

**Kapan menggunakan**:

- ✅ API request/response tracking
- ✅ Business logic operations
- ✅ User actions monitoring
- ✅ System events yang butuh tracing

### 3. Error Logging (`log_error()`)

**Gunakan untuk**: Error handling yang comprehensive

```python
from src.mlogger.utils import log_error

try:
    # kode yang mungkin error
    result = risky_operation()
except Exception as e:
    log_error(
        error=e,
        message="Failed to process API request",
        include_traceback=True,
        extra_context={
            "request_id": "req-123",
            "user_id": "user456"
        }
    )
```

**Kapan menggunakan**:

- ✅ Exception handling
- ✅ API error responses
- ✅ Database operation failures
- ✅ External service call failures

### 4. Performance Logging (`log_performance()`)

**Gunakan untuk**: Monitoring performa operasi

```python
from src.mlogger.utils import log_performance
import time

start = time.time()
# operasi yang ingin dimonitor
process_data()
duration = (time.time() - start) * 1000

log_performance(
    operation="data_processing",
    duration_ms=duration,
    threshold_ms=500,  # warn jika > 500ms
    extra_context={"records_processed": 100}
)
```

**Kapan menggunakan**:

- ✅ API response time monitoring
- ✅ Database query performance
- ✅ File processing operations
- ✅ External API call timing

## 📊 Level Logging yang Tepat

### TRACE

```python
logger.trace("Entering function with params: {}", params)
```

**Gunakan untuk**:

- Function entry/exit dengan parameters
- Detailed debugging information
- Development troubleshooting

### DEBUG

```python
logger.debug("Processing user data: {}", user_id)
```

**Gunakan untuk**:

- Debugging information
- Variable values
- Algorithm steps
- Development information

### INFO

```python
logger.info("User {} logged in successfully", user_id)
logger.info("API request processed: {} records", count)
```

**Gunakan untuk**:

- ✅ Normal application flow
- ✅ Successful operations
- ✅ Business events
- ✅ System status updates

### SUCCESS

```python
logger.success("Data migration completed: {} records processed", total)
```

**Gunakan untuk**:

- ✅ Important successful operations
- ✅ Completed batch processes
- ✅ Successful integrations
- ✅ Achievement notifications

### WARNING

```python
logger.warning("API rate limit approaching: {}/1000 requests", current_count)
logger.warning("Deprecated function used: {}", function_name)
```

**Gunakan untuk**:

- ⚠️ Kondisi yang perlu perhatian
- ⚠️ Deprecated features
- ⚠️ Resource limits approaching
- ⚠️ Unusual but handled conditions

### ERROR

```python
logger.error("Failed to connect to database: {}", str(error))
logger.error("API request failed: status={}, response={}", status, response)
```

**Gunakan untuk**:

- ❌ Application errors
- ❌ Failed operations yang bisa di-recover
- ❌ External service failures
- ❌ Data validation errors

### CRITICAL

```python
logger.critical("Database connection lost - application unstable")
logger.critical("Out of memory - shutting down gracefully")
```

**Gunakan untuk**:

- 🔥 System failures
- 🔥 Application crashes
- 🔥 Security breaches
- 🔥 Data corruption

## 🛠️ Utility Functions

### 1. `sanitize_log_message()`

Membersihkan sensitive data dari log messages:

```python
from src.mlogger.utils import sanitize_log_message

message = "User login: password=secret123, token=abc456"
clean_message = sanitize_log_message(message)
# Result: "User login: password=[REDACTED], token=[REDACTED]"
```

### 2. `get_caller_info()`

Mendapatkan informasi tentang function yang memanggil:

```python
from src.mlogger.utils import get_caller_info

def my_function():
    caller = get_caller_info()
    print(f"Called from: {caller['function']} at line {caller['line']}")
```

### 3. `format_file_size()`

Format ukuran file untuk logging:

```python
from src.mlogger.utils import format_file_size

size = format_file_size(1536000)  # "1.5 MB"
logger.info("Processing file: {} ({})", filename, size)
```

### 4. `validate_log_level()`

Validasi log level:

```python
from src.mlogger.utils import validate_log_level

try:
    level = validate_log_level("info")  # Returns "INFO"
except ValueError as e:
    logger.error("Invalid log level: {}", e)
```

## 📚 Examples dan Best Practices

### API Request Logging

```python
from src.mlogger import get_logger
from src.mlogger.utils import create_structured_log, log_performance
import time

logger = get_logger("api_handler")

async def handle_api_request(request):
    start_time = time.time()
    request_id = generate_request_id()

    # Log incoming request
    create_structured_log(
        level="INFO",
        message="API request received",
        component="api",
        operation="request_received",
        request_id=request_id,
        extra_fields={
            "method": request.method,
            "path": request.url.path,
            "user_agent": request.headers.get("user-agent")
        }
    )

    try:
        # Process request
        result = await process_request(request)

        # Log successful response
        duration = (time.time() - start_time) * 1000
        log_performance(
            operation="api_request",
            duration_ms=duration,
            extra_context={
                "request_id": request_id,
                "status": "success"
            }
        )

        logger.success("API request completed successfully: {}", request_id)
        return result

    except Exception as e:
        log_error(
            error=e,
            message="API request failed",
            extra_context={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path
            }
        )
        raise
```

### Database Operations

```python
from src.mlogger import get_logger
from src.mlogger.utils import log_error, log_performance

db_logger = get_logger("database")

class DatabaseManager:

    async def execute_query(self, query: str, params: tuple = None):
        start_time = time.time()

        db_logger.debug("Executing query: {}", query[:100])  # Truncate for safety

        try:
            result = await self.connection.execute(query, params)

            duration = (time.time() - start_time) * 1000
            log_performance(
                operation="database_query",
                duration_ms=duration,
                threshold_ms=1000,  # Warn if query > 1s
                extra_context={
                    "query_type": query.split()[0].upper(),
                    "affected_rows": getattr(result, 'rowcount', 0)
                }
            )

            db_logger.info("Query executed successfully: {} rows affected",
                          getattr(result, 'rowcount', 0))
            return result

        except Exception as e:
            log_error(
                error=e,
                message="Database query failed",
                extra_context={
                    "query": query[:200],  # Limited for safety
                    "params": str(params) if params else None
                }
            )
            raise
```

### Error Handling Best Practices

```python
from src.mlogger import get_logger
from src.mlogger.utils import log_error, extract_exception_info

logger = get_logger("error_handler")

class APIErrorHandler:

    def handle_validation_error(self, error: ValueError, context: dict):
        """Handle validation errors with appropriate logging"""
        log_error(
            error=error,
            message="Validation failed",
            include_traceback=False,  # No need for traceback on validation errors
            extra_context=context
        )

    def handle_system_error(self, error: Exception, context: dict):
        """Handle system errors with full context"""
        exc_info = extract_exception_info(error)

        log_error(
            error=error,
            message="System error occurred",
            include_traceback=True,
            extra_context={
                **context,
                "exception_details": exc_info
            }
        )

        # For critical system errors
        if isinstance(error, (MemoryError, SystemExit)):
            logger.critical("Critical system error: {}", error)
```

### Background Tasks Logging

```python
from src.mlogger import get_logger
from src.mlogger.utils import create_structured_log

task_logger = get_logger("background_tasks")

async def background_data_sync():
    task_id = generate_task_id()

    create_structured_log(
        level="INFO",
        message="Background sync started",
        component="sync",
        operation="data_sync_start",
        extra_fields={"task_id": task_id}
    )

    try:
        # Process data
        processed_count = await sync_data()

        create_structured_log(
            level="SUCCESS",
            message="Background sync completed",
            component="sync",
            operation="data_sync_complete",
            extra_fields={
                "task_id": task_id,
                "processed_records": processed_count
            }
        )

    except Exception as e:
        log_error(
            error=e,
            message="Background sync failed",
            extra_context={"task_id": task_id}
        )

        # Reschedule if needed
        task_logger.warning("Rescheduling sync task: {}", task_id)
```

## ⚙️ Konfigurasi

### File Konfigurasi (`log_config.toml`)

Sistem menggunakan konfigurasi TOML yang terletak di `log_config.toml`:

```toml
[mlog]
level = "INFO"
intercept = true
exception_hooks = true

[mlog.terminal]
enabled = true
level = "INFO"
format = "simple"
colorize = true

[mlog.file]
enabled = true
base_path = "logs"
name_prefix = "app"
rotation_mb = 10
retention_days = 7

[mlog.file.levels]
info = true     # app_info.log
error = true    # app_error.log
debug = false   # app_debug.log (disabled)
warning = false # app_warning.log (disabled)
```

### Environment-Specific Configuration

```python
# Development
from src.mlogger.config import MLogConfig

dev_config = MLogConfig(
    level="DEBUG",
    terminal=TerminalConfig(level="DEBUG", format="full"),
    file=FileConfig(levels=FileLevelsConfig(debug=True))
)

# Production
prod_config = MLogConfig(
    level="INFO",
    terminal=TerminalConfig(level="WARNING", format="minimal"),
    file=FileConfig(
        levels=FileLevelsConfig(info=True, error=True, debug=False)
    )
)
```

## 🔧 Advanced Features

### Context Binding

```python
from src.mlogger import get_logger

# Logger dengan context yang di-bind
logger = get_logger("api").bind(
    request_id="req-123",
    user_id="user-456"
)

# Semua log dari logger ini akan include context
logger.info("Processing request")  # Includes request_id and user_id
```

### Custom Formatters

```python
# Di konfigurasi TOML
[mlog.formatters]
api_format = "API: {time} | {level} | {message} | Request: {extra[request_id]}"
```

### Sensitive Data Filtering

```python
# Otomatis filter sensitive data
logger.info("User data: password=secret123")  # Output: "User data: password=[REDACTED]"
```

## 🎯 Decision Tree: Kapan Menggunakan Apa

```
┌─ Normal app flow? ──→ get_logger() + INFO/DEBUG
│
├─ Error occurred? ──→ log_error() + ERROR/CRITICAL
│
├─ Performance monitoring? ──→ log_performance()
│
├─ Structured business event? ──→ create_structured_log()
│
├─ API request/response? ──→ Structured logging + performance
│
└─ Background task? ──→ get_logger() + structured logging for key events
```

## 📋 Checklist Quick Reference

### ✅ Untuk Setiap Module/Class

```python
from src.mlogger import get_logger
logger = get_logger(__name__)
```

### ✅ Untuk API Endpoints

```python
from src.mlogger.utils import create_structured_log, log_performance
# Use structured logging + performance monitoring
```

### ✅ Untuk Error Handling

```python
from src.mlogger.utils import log_error
# Use log_error() for comprehensive error logging
```

### ✅ Untuk Background Tasks

```python
# Combine get_logger() + structured logging for important events
```

---

**Happy Logging! 🚀**

Sistem logging ini dirancang untuk memberikan fleksibilitas maksimal sambil tetap mudah digunakan. Ikuti panduan ini untuk mendapatkan logging yang konsisten dan informatif di seluruh aplikasi.
