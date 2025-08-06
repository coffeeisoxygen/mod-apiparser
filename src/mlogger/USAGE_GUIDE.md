# MLogger Usage Guide - Panduan Praktis

Panduan praktis penggunaan MLogger untuk berbagai skenario dalam aplikasi mod-apiparser.

## 🎯 Quick Reference - Kapan Menggunakan Apa

### Ringkasan Cepat

| Situasi | Utility yang Digunakan | Level | Contoh |
|---------|------------------------|-------|---------|
| Log biasa dalam function | `get_logger()` | INFO/DEBUG | `logger.info("Processing data")` |
| Error handling | `log_error()` | ERROR/CRITICAL | `log_error(e, "API failed")` |
| API request/response | `create_structured_log()` | INFO | Dengan request_id, user_id |
| Performance monitoring | `log_performance()` | INFO/WARNING | Database query, API response time |
| Background tasks | `get_logger()` + structured | INFO/SUCCESS | Batch processing, sync tasks |
| Security events | `create_structured_log()` | WARNING/ERROR | Login attempts, auth failures |

## 📋 Panduan Detail per Skenario

### 1. Logging dalam Controller/Handler API

```python
from src.mlogger import get_logger
from src.mlogger.utils import create_structured_log, log_performance
import time

# Setup logger untuk module
logger = get_logger(__name__)

class UserController:

    async def get_user(self, user_id: str, request_id: str):
        start_time = time.time()

        # Log incoming request dengan struktur
        create_structured_log(
            level="INFO",
            message="Get user request received",
            component="user_controller",
            operation="get_user",
            user_id=user_id,
            request_id=request_id
        )

        try:
            # Business logic
            user = await self.user_service.get_by_id(user_id)

            # Log successful operation
            duration = (time.time() - start_time) * 1000
            log_performance(
                operation="get_user_api",
                duration_ms=duration,
                extra_context={
                    "user_id": user_id,
                    "request_id": request_id
                }
            )

            logger.success("User retrieved successfully: {}", user_id)
            return user

        except UserNotFound as e:
            # Business error - tidak perlu traceback
            logger.warning("User not found: {}", user_id)
            raise

        except Exception as e:
            # System error - perlu traceback lengkap
            log_error(
                error=e,
                message="Failed to retrieve user",
                extra_context={
                    "user_id": user_id,
                    "request_id": request_id
                }
            )
            raise
```

### 2. Service Layer Logging

```python
from src.mlogger import get_logger
from src.mlogger.utils import log_error

logger = get_logger(__name__)

class UserService:

    async def create_user(self, user_data: dict):
        logger.info("Creating new user with email: {}", user_data.get("email"))

        try:
            # Validation
            await self.validate_user_data(user_data)
            logger.debug("User data validation passed")

            # Save to database
            user = await self.user_repository.create(user_data)
            logger.success("User created successfully: {}", user.id)

            return user

        except ValidationError as e:
            # Business validation error
            logger.warning("User validation failed: {}", str(e))
            raise

        except IntegrityError as e:
            # Database constraint error
            logger.error("User creation failed - duplicate email: {}",
                        user_data.get("email"))
            raise

        except Exception as e:
            # Unexpected system error
            log_error(
                error=e,
                message="Unexpected error during user creation",
                extra_context={"user_email": user_data.get("email")}
            )
            raise
```

### 3. Database Repository Logging

```python
from src.mlogger import get_logger
from src.mlogger.utils import log_performance, log_error
import time

logger = get_logger(__name__)

class UserRepository:

    async def find_by_email(self, email: str):
        start_time = time.time()

        logger.debug("Searching user by email: {}", email)

        try:
            query = "SELECT * FROM users WHERE email = ?"
            result = await self.db.fetch_one(query, (email,))

            # Log performance
            duration = (time.time() - start_time) * 1000
            log_performance(
                operation="db_find_user_by_email",
                duration_ms=duration,
                threshold_ms=100,  # Warn if > 100ms
                extra_context={"email": email}
            )

            if result:
                logger.debug("User found: {}", email)
            else:
                logger.debug("User not found: {}", email)

            return result

        except Exception as e:
            log_error(
                error=e,
                message="Database error during user search",
                extra_context={"email": email}
            )
            raise
```

### 4. External API Integration Logging

```python
from src.mlogger import get_logger
from src.mlogger.utils import create_structured_log, log_error, log_performance
import time

logger = get_logger(__name__)

class ExternalAPIClient:

    async def call_payment_api(self, payment_data: dict, request_id: str):
        start_time = time.time()

        # Log outgoing API call
        create_structured_log(
            level="INFO",
            message="Calling external payment API",
            component="payment_client",
            operation="payment_request",
            request_id=request_id,
            extra_fields={
                "external_api": "payment_gateway",
                "amount": payment_data.get("amount")
            }
        )

        try:
            response = await self.http_client.post("/payment", json=payment_data)

            # Log response
            duration = (time.time() - start_time) * 1000
            log_performance(
                operation="external_payment_api",
                duration_ms=duration,
                threshold_ms=5000,  # External API threshold lebih tinggi
                extra_context={
                    "request_id": request_id,
                    "status_code": response.status_code
                }
            )

            if response.status_code == 200:
                logger.success("Payment API call successful: {}", request_id)
            else:
                logger.warning("Payment API returned non-200 status: {} - {}",
                             response.status_code, request_id)

            return response.json()

        except TimeoutError as e:
            logger.error("Payment API timeout: {}", request_id)
            raise

        except Exception as e:
            log_error(
                error=e,
                message="Payment API call failed",
                extra_context={
                    "request_id": request_id,
                    "external_api": "payment_gateway"
                }
            )
            raise
```

### 5. Background Tasks dan Scheduled Jobs

```python
from src.mlogger import get_logger
from src.mlogger.utils import create_structured_log, log_performance
import time

logger = get_logger(__name__)

class DataSyncTask:

    async def sync_user_data(self):
        task_id = self.generate_task_id()
        start_time = time.time()

        # Log task start
        create_structured_log(
            level="INFO",
            message="User data sync task started",
            component="sync_task",
            operation="user_data_sync_start",
            extra_fields={"task_id": task_id}
        )

        try:
            # Get data to sync
            pending_users = await self.get_pending_sync_users()
            logger.info("Found {} users to sync", len(pending_users))

            processed_count = 0
            error_count = 0

            for user in pending_users:
                try:
                    await self.sync_single_user(user.id)
                    processed_count += 1

                    # Log progress setiap 100 records
                    if processed_count % 100 == 0:
                        logger.info("Sync progress: {}/{} users processed",
                                   processed_count, len(pending_users))

                except Exception as e:
                    error_count += 1
                    logger.error("Failed to sync user {}: {}", user.id, str(e))

            # Log task completion
            duration = (time.time() - start_time) * 1000

            create_structured_log(
                level="SUCCESS",
                message="User data sync task completed",
                component="sync_task",
                operation="user_data_sync_complete",
                extra_fields={
                    "task_id": task_id,
                    "processed_count": processed_count,
                    "error_count": error_count,
                    "duration_ms": duration
                }
            )

        except Exception as e:
            log_error(
                error=e,
                message="User data sync task failed",
                extra_context={"task_id": task_id}
            )
            raise
```

### 6. Middleware Logging

```python
from src.mlogger import get_logger
from src.mlogger.utils import create_structured_log, log_performance
import time

logger = get_logger(__name__)

class RequestLoggingMiddleware:

    async def __call__(self, request, call_next):
        start_time = time.time()
        request_id = self.generate_request_id()

        # Bind request_id ke request untuk digunakan di handler
        request.state.request_id = request_id

        # Log incoming request
        create_structured_log(
            level="INFO",
            message="HTTP request received",
            component="middleware",
            operation="request_start",
            request_id=request_id,
            extra_fields={
                "method": request.method,
                "path": request.url.path,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "ip_address": request.client.host if request.client else "unknown"
            }
        )

        try:
            # Process request
            response = await call_next(request)

            # Log response
            duration = (time.time() - start_time) * 1000

            log_performance(
                operation="http_request",
                duration_ms=duration,
                threshold_ms=1000,  # Warn if request > 1s
                extra_context={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "method": request.method,
                    "path": request.url.path
                }
            )

            # Log based on status code
            if response.status_code < 400:
                logger.info("Request completed successfully: {} {} - {} ({}ms)",
                           request.method, request.url.path,
                           response.status_code, round(duration, 2))
            elif response.status_code < 500:
                logger.warning("Request completed with client error: {} {} - {} ({}ms)",
                              request.method, request.url.path,
                              response.status_code, round(duration, 2))
            else:
                logger.error("Request completed with server error: {} {} - {} ({}ms)",
                            request.method, request.url.path,
                            response.status_code, round(duration, 2))

            return response

        except Exception as e:
            duration = (time.time() - start_time) * 1000

            log_error(
                error=e,
                message="Request processing failed",
                extra_context={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration
                }
            )
            raise
```

### 7. Authentication & Security Logging

```python
from src.mlogger import get_logger
from src.mlogger.utils import create_structured_log

logger = get_logger(__name__)

class AuthService:

    async def authenticate_user(self, email: str, password: str, request_info: dict):
        # Log login attempt
        create_structured_log(
            level="INFO",
            message="User login attempt",
            component="auth",
            operation="login_attempt",
            extra_fields={
                "email": email,
                "ip_address": request_info.get("ip_address"),
                "user_agent": request_info.get("user_agent")
            }
        )

        try:
            user = await self.user_service.get_by_email(email)

            if not user:
                # Log failed login - user not found
                create_structured_log(
                    level="WARNING",
                    message="Login failed - user not found",
                    component="auth",
                    operation="login_failed",
                    extra_fields={
                        "email": email,
                        "reason": "user_not_found",
                        "ip_address": request_info.get("ip_address")
                    }
                )
                raise AuthenticationError("Invalid credentials")

            if not self.verify_password(password, user.password_hash):
                # Log failed login - wrong password
                create_structured_log(
                    level="WARNING",
                    message="Login failed - invalid password",
                    component="auth",
                    operation="login_failed",
                    user_id=user.id,
                    extra_fields={
                        "email": email,
                        "reason": "invalid_password",
                        "ip_address": request_info.get("ip_address")
                    }
                )
                raise AuthenticationError("Invalid credentials")

            # Log successful login
            create_structured_log(
                level="SUCCESS",
                message="User login successful",
                component="auth",
                operation="login_success",
                user_id=user.id,
                extra_fields={
                    "email": email,
                    "ip_address": request_info.get("ip_address")
                }
            )

            return user

        except AuthenticationError:
            raise
        except Exception as e:
            log_error(
                error=e,
                message="Authentication system error",
                extra_context={
                    "email": email,
                    "ip_address": request_info.get("ip_address")
                }
            )
            raise
```

## 🔧 Level Logging Decision Tree

```
┌─ Normal flow/operation?
│   ├─ Important milestone → SUCCESS
│   ├─ Regular progress → INFO
│   └─ Detailed debugging → DEBUG
│
├─ Something unusual but handled?
│   ├─ Potential issue → WARNING
│   ├─ Expected business error → WARNING/INFO
│   └─ Rate limiting → WARNING
│
├─ Error occurred?
│   ├─ Recoverable error → ERROR
│   ├─ Business logic error → WARNING/ERROR
│   └─ System/Critical failure → CRITICAL
│
└─ Development/troubleshooting?
    ├─ Function entry/exit → TRACE
    ├─ Variable values → DEBUG
    └─ Algorithm steps → DEBUG
```

## 📊 Performance Thresholds Guidelines

| Operasi | Normal (ms) | Warning (ms) | Critical (ms) |
|---------|-------------|--------------|---------------|
| Database Query | < 100 | > 500 | > 2000 |
| API Response | < 200 | > 1000 | > 5000 |
| External API Call | < 1000 | > 5000 | > 15000 |
| File Processing | < 500 | > 2000 | > 10000 |
| Authentication | < 50 | > 200 | > 1000 |

## 🎯 Best Practices Summary

### ✅ DO

- Gunakan `get_logger(__name__)` untuk logger biasa
- Gunakan `create_structured_log()` untuk business events
- Gunakan `log_error()` untuk exception handling
- Gunakan `log_performance()` untuk monitoring operasi
- Include request_id dalam context untuk tracing
- Log both start dan completion untuk operasi penting
- Gunakan appropriate log levels

### ❌ DON'T

- Jangan log sensitive data (password, token) tanpa sanitization
- Jangan gunakan level CRITICAL untuk error biasa
- Jangan log terlalu verbose di production
- Jangan include full stack trace untuk business errors
- Jangan lupa include context yang berguna untuk debugging

### 🔍 Troubleshooting Tips

1. **Request tracing**: Selalu include request_id
2. **Performance issues**: Gunakan log_performance dengan threshold
3. **Error investigation**: Gunakan log_error dengan full context
4. **Business flow**: Gunakan structured logging untuk key events
5. **Background tasks**: Log progress dan completion status

---

Dengan mengikuti panduan ini, logging akan menjadi konsisten dan mudah untuk monitoring, debugging, dan troubleshooting aplikasi! 🚀
