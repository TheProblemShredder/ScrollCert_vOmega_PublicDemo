#!/usr/bin/env python3
"""
AEQ–CID (Demo) — Self-describing, reproducible IDs for artifacts.

This is a minimal, pragmatic implementation:
- Canonical JSON -> SHA256 -> sha12 (thin)
- Optional "fat" ID includes: kind, version, sha12, crc32, small meta map
- All deterministic.

Format (demo):
  thin: aeq:v2:<kind>:<sha12>:<crc8>
  fat : aeq:v2:<kind>:<sha12>:<crc8>:<meta_compact>

Where meta_compact is a compact k=v list (no spaces).
"""

import zlib
from typing import Any, Dict, Optional

from src.hash_utils import canonical_json, sha256_hex, sha12

def _crc8_hex(s: str) -> str:
    # CRC32 then take last byte => 2 hex chars (cheap tamper check)
    c = zlib.crc32(s.encode("utf-8")) & 0xFFFFFFFF
    return f"{c & 0xFF:02x}"

def mint_thin(obj: Any, kind: str, version: str = "v2") -> Dict[str, str]:
    canon = canonical_json(obj)
    h12 = sha12(canon)
    crc8 = _crc8_hex(f"{kind}|{version}|{h12}")
    cid = f"aeq:{version}:{kind}:{h12}:{crc8}"
    return {"cid": cid, "sha12": h12, "crc8": crc8}

def mint_fat(obj: Any, kind: str, meta: Optional[Dict[str, Any]] = None, version: str = "v2") -> Dict[str, str]:
    base = mint_thin(obj, kind=kind, version=version)
    meta = meta or {}
    # Compact meta encoding: keys sorted, values stripped to safe scalar-ish strings
    parts = []
    for k in sorted(meta.keys()):
        v = meta[k]
        if isinstance(v, float):
            vs = f"{v:.6g}"
        else:
            vs = str(v)
        vs = vs.replace(" ", "").replace(":", "_").replace("|", "_").replace(",", "_")
        parts.append(f"{k}={vs}")
    meta_compact = ",".join(parts) if parts else "meta=none"
    fat = f"{base['cid']}:{meta_compact}"
    return {**base, "cid_fat": fat, "meta_compact": meta_compact}

def verify_cid_thin(cid: str) -> bool:
    # Verify the crc8 matches the embedded components
    try:
        prefix, version, kind, h12, crc8 = cid.split(":", 4)
        if prefix != "aeq":
            return False
        expect = _crc8_hex(f"{kind}|{version}|{h12}")
        return expect == crc8
    except Exception:
        return False
