#!/usr/bin/env python3
import hashlib
import json
from typing import Any, Dict

def canonical_json(obj: Any) -> str:
    """
    Deterministic JSON encoding: stable ordering, stable separators.
    This is the foundation for reproducible IDs/hashes.
    """
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def sha12(s: str) -> str:
    """Short content hash (12 hex) for human-readable ledger lines."""
    return sha256_hex(s)[:12]

def obj_sha12(obj: Any) -> str:
    return sha12(canonical_json(obj))
