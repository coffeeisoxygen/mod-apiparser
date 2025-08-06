# # Simple usage
# service = get_token_service()

# # Create tokens
# access_token = service.create_access_token(
#     subject="user123",
#     extra_claims={"role": "admin", "permissions": ["read", "write"]}
# )

# refresh_token = service.create_refresh_token("user123")

# # Verify token
# try:
#     claims = service.verify_token(access_token)
#     print(f"User: {claims['sub']}, Role: {claims.get('role')}")
# except TokenExpiredError:
#     print("Token expired, refresh needed")
# except TokenInvalidError:
#     print("Invalid token")

# # Refresh tokens
# new_access, new_refresh = service.refresh_access_token(refresh_token)

# # Blacklist token (logout)
# service.blacklist_token(access_token)

# RSA256 with key files
# rsa_service = AdvancedTokenService(
#     algorithm="RS256",
#     key_file_path=Path("keys/jwt_key"),
#     access_token_expire_minutes=30,
#     refresh_token_expire_days=30,
# )

# # Custom issuer/audience
# custom_service = AdvancedTokenService(
#     issuer="my-api",
#     audience="my-frontend",
#     algorithm="HS512",
# )
