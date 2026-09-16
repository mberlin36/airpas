"""
API Root Config
"""

# Application database configuration:
from .database import DATABASE_URL

__all__ = [
    # Application database configuration:
    "DATABASE_URL",
]
