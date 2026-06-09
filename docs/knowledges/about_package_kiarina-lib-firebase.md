---
title: About kiarina-lib-firebase package
description: >-
  kiarina-lib-firebase is a library for Firebase authentication
  with REST API integration and automatic token management using pydantic-settings-manager.
---

kiarina-lib-firebase provides a simple and secure way to manage Firebase authentication using REST APIs.
This library enables custom token exchange and automatic ID token lifecycle management with configuration management using pydantic-settings-manager.

Key features include:
- Custom token exchange for refresh/ID tokens via Firebase REST API
- Automatic ID token lifecycle management with `TokenManager`
- Token refresh 5 minutes before expiration
- Thread-safe token refresh with `asyncio.Lock`
- Secure API key management with SecretStr
- Multi-configuration support for different projects/environments
- Async-only API for modern Python applications
- Environment variable configuration

Main utilities:
- `exchange_custom_token()`: Exchange custom token for refresh token and ID token
- `TokenManager`: Service class for automatic ID token lifecycle management
- `TokenResponse`: Schema for Firebase token exchange responses

Exception classes:
- `FirebaseAuthError`: Base exception for Firebase Auth errors
- `InvalidCustomTokenError`: Custom token is invalid or expired
- `InvalidRefreshTokenError`: Refresh token is invalid or expired
- `FirebaseAPIError`: Firebase API returned an error response
