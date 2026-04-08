"""
Singleton session service instance.

Provides a global session_service that handles both Redis-backed and in-memory sessions.
Uses the factory function from session_service.py to automatically select the best backend.

Usage:
    from backend.services.session_singleton import session_service
    session_id, session = session_service.get_or_create_session()
"""
from backend.services.session_service import get_session_service

# Get the appropriate session service (Redis if available, else Memory)
session_service = get_session_service()

