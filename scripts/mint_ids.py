#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Ensure project root is on sys.path so "src.*" imports work
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from src.aeq_cid import mint_fat  # noqa: E402

def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def main():
    prereg = load_json(BASE / "preregister" / "claim.json")
    abln  = load_json(BASE / "preregister" / "ablation.json")
    neg   = load_json(BASE / "controls" / "negative_control.json")

    out = {}
    out["preregister"] = mint_fat(prereg, "prereg", meta={"claim_id": prereg.get("claim_id","?")})
    out["ablation"]    = mint_fat(abln,  "ablation", meta={"ablation_id": abln.get("ablation_id","?")})
    out["neg_control"] = mint_fat(neg,   "control", meta={"control_id": neg.get("control_id","?")})

    out_path = BASE / "outputs" / "aeq_cids.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Wrote:", out_path)
    for k, v in out.items():
        print(f"{k}: {v.get('cid_fat', v['cid'])}")

if __name__ == "__main__":
    main()
