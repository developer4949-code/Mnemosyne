"""
core/security.py

Security utilities.

Centralises password hashing, JWT token generation, and other cryptographic
functions. No endpoint should implement hashing directly.

(This module is a placeholder for Milestone 3, where authentication is fully implemented.)
"""

from passlib.context import CryptContext

# bcrypt is the industry standard for password hashing.
# We configure it here so the entire app uses the same parameters.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if a plaintext password matches the hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash from a plaintext password."""
    return pwd_context.hash(password)
