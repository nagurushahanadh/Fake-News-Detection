from __future__ import annotations

import hashlib


def hash_password(password: str) -> str:
    """Very basic password hashing (for demo only)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash
