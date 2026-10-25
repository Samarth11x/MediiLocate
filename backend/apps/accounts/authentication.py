"""
Authentication classes for MediLocate accounts.
Enforces standard Django REST Framework SessionAuthentication with CSRF validation.
"""

from rest_framework.authentication import SessionAuthentication


class EnforcedSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication that strictly enforces CSRF token validation
    on all state-changing HTTP methods for session-authenticated users.
    """
    pass


# Deprecated alias preserved for import backwards compatibility,
# but now strictly enforces CSRF verification to prevent CSRF vulnerabilities.
class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    DEPRECATED: Formerly bypassed CSRF. Now strictly delegates to standard
    SessionAuthentication with CSRF enforcement as required by security release gate.
    """
    pass

