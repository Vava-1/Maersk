"""
Enterprise Security Module for AfriSwarm.
Implements RBAC, cryptographic audit signing, PII redaction, and data sovereignty.
"""
import hashlib
import hmac
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from functools import wraps

from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

from ..config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption key management
_fernet_key = settings.SECRET_KEY[:32].encode() if len(settings.SECRET_KEY.encode()) >= 32 else settings.SECRET_KEY.encode().ljust(32, b'0')
_fernet = Fernet(base64.urlsafe_b64encode(_fernet_key[:32]))

import base64  # Added for Fernet key encoding


# ───────────────────────────────────────────────
# Authentication
# ───────────────────────────────────────────────
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


# ───────────────────────────────────────────────
# Audit Trail Cryptographic Signing
# ───────────────────────────────────────────────
def sign_audit_entry(entry: Dict[str, Any]) -> str:
    """Create cryptographic signature for immutable audit logs."""
    entry_string = str(sorted(entry.items()))
    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        entry_string.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature


def verify_audit_signature(entry: Dict[str, Any], signature: str) -> bool:
    """Verify the integrity of an audit log entry."""
    expected = sign_audit_entry(entry)
    return hmac.compare_digest(expected, signature)


# ───────────────────────────────────────────────
# PII Redaction
# ───────────────────────────────────────────────
PII_PATTERNS = {
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "phone": re.compile(r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
    "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
    "passport": re.compile(r'\b[A-Z]{1,2}\d{6,9}\b'),
}


def redact_pii(text: str) -> str:
    """Redact personally identifiable information from text."""
    if not settings.PII_REDACTION_ENABLED:
        return text
    redacted = text
    for pii_type, pattern in PII_PATTERNS.items():
        redacted = pattern.sub(f"[REDACTED_{pii_type.upper()}]", redacted)
    return redacted


# ───────────────────────────────────────────────
# RBAC (Role-Based Access Control)
# ───────────────────────────────────────────────
ROLE_PERMISSIONS = {
    "admin": ["*"],  # All permissions
    "operator": [
        "agents.read", "agents.chat",
        "tasks.read", "tasks.create",
        "shipments.read", "shipments.create",
        "routes.read",
        "risks.read",
        "compliance.read",
        "analytics.read",
        "dashboard.read",
        "guardian.read",
        "escalation.respond",
    ],
    "analyst": [
        "agents.read",
        "tasks.read",
        "shipments.read",
        "routes.read",
        "risks.read",
        "compliance.read",
        "analytics.read", "analytics.export",
        "dashboard.read",
        "knowledge.read",
    ],
    "viewer": [
        "dashboard.read",
        "analytics.read",
        "risks.read",
        "shipments.read",
    ],
    "guardian": [
        "guardian.*",
        "agents.read", "agents.heal",
        "system.read", "system.configure",
        "security.read", "security.respond",
    ],
}


def check_permission(user_role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    permissions = ROLE_PERMISSIONS.get(user_role, [])
    if "*" in permissions:
        return True
    if permission in permissions:
        return True
    # Check wildcard permissions
    for p in permissions:
        if p.endswith(".*") and permission.startswith(p[:-2]):
            return True
    return False


def require_permission(permission: str):
    """Decorator to require a specific permission."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user info from kwargs or args
            user = kwargs.get("user") or kwargs.get("current_user")
            if user is None:
                for arg in args:
                    if hasattr(arg, "role"):
                        user = arg
                        break
            if user is None:
                raise PermissionError("Authentication required")
            if not check_permission(user.role, permission):
                raise PermissionError(f"Permission denied: {permission}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ───────────────────────────────────────────────
# Data Encryption
# ───────────────────────────────────────────────
def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data before storage."""
    return _fernet.encrypt(data.encode()).decode()


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data from storage."""
    return _fernet.decrypt(encrypted_data.encode()).decode()


# ───────────────────────────────────────────────
# Rate Limiting Helpers
# ───────────────────────────────────────────────
class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}

    def is_allowed(self, key: str) -> bool:
        now = datetime.utcnow().timestamp()
        window_start = now - self.window_seconds

        if key not in self.requests:
            self.requests[key] = []

        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if t > window_start]

        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True
        return False


# Global rate limiters
auth_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)
api_rate_limiter = RateLimiter(max_requests=1000, window_seconds=60)
