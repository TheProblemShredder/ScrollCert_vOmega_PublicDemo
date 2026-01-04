#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict, List

from src.hash_utils import canonical_json, sha12

BASE = Path(__file__).resolve().parents[1]

def _blind_token(salt: str, claim_id: str, true_label: str) -> str:
    return sha12(canonical_json({"salt": salt, "claim_id": claim_id, "true": true_label}))

def make_blind_map(claim_id: str, true_labels: List[str], salt: str) -> Dict[str, str]:
    """
    Deterministic blinding:
    true label -> blind label
    """
    # For demo, make stable blind IDs like ARM_<sha12>
    out = {}
    for t in true_labels:
        out[t] = f"ARM_{_blind_token(salt, claim_id, t).upper()}"
    return out

def write_blind_files(claim_id: str, blind_map: Dict[str, str]) -> Dict[str, Path]:
    """
    Writes:
      outputs/blind_map.json   (true->blind)  (keep private if desired)
      outputs/reveal.json      (blind->true)  (for reveal step)
    """
    out_dir = BASE / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    p_map = out_dir / "blind_map.json"
    p_rev = out_dir / "reveal.json"

    p_map.write_text(json.dumps({
        "claim_id": claim_id,
        "true_to_blind": blind_map
    }, indent=2), encoding="utf-8")

    p_rev.write_text(json.dumps({
        "claim_id": claim_id,
        "blind_to_true": {v: k for k, v in blind_map.items()}
    }, indent=2), encoding="utf-8")

    return {"blind_map": p_map, "reveal": p_rev}
