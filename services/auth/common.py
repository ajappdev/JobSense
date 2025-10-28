"""Load authentication-related environment variables.

This module uses python-dotenv to load a local .env file during development
and exposes named constants for the auth service to consume.

Security:
- SECRET_KEY should be set in production. It may be None in development if not
  provided, but the application should fail fast if SECRET_KEY is missing in
  a production environment.
- Do not commit secrets to source control.
"""

from dotenv import load_dotenv
import os
from typing import Optional

# Load variables from a local .env file (if present). Calling this at import
# time is convenient for small services; consider explicit initialization for
# larger apps.
load_dotenv()


def _get_env(name: str) -> Optional[str]:
    """Return an environment variable value or None if not set."""
    return os.getenv(name)


# Environment-backed configuration values (may be None when not set).
# Annotated with Optional[str] for clarity and static analysis.
SECRET_KEY: Optional[str] = _get_env("SECRET_KEY")
GOOGLE_CLIENT_ID: Optional[str] = _get_env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET: Optional[str] = _get_env("GOOGLE_CLIENT_SECRET")
APPLE_CLIENT_ID: Optional[str] = _get_env("APPLE_CLIENT_ID")
LINKEDIN_CLIENT_ID: Optional[str] = _get_env("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET: Optional[str] = _get_env("LINKEDIN_CLIENT_SECRET")


# Public API for imports (keeps namespace explicit).
__all__ = [
    "SECRET_KEY",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "APPLE_CLIENT_ID",
    "LINKEDIN_CLIENT_ID",
    "LINKEDIN_CLIENT_SECRET",
]
