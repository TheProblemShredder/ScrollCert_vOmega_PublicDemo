#!/usr/bin/env python3
import argparse
import json
import time
import random
from pathlib import Path

from src.hash_utils import canonical_json, obj_sha12, sha12
from src.gates import apply_gates
from src.aeq_cid import mint_fat
from src.blind import make_blind_map, write_blind_files

BASE = Path(__file__).resolve().parents[1]

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_text(path: Path, s: str):
    path.write_text(s, encoding="utf-8")

def deterministic_score(claim_id: str, kind: str, ablated: bool) -> float:
    seed = int(sha12(f"{claim_id}|{kind}|abl={ablated}"), 16) % (2**32)
    rng = random.Random(seed)

    if kind == "negative_control":
        return 0.50 + 0.05 * rng.random()

    base = 0.55 + 0.20 * rng.random()
    if ablated:
        base -= (0.06 + 0.04 * rng.random())
    return max(0.0, min(1.0, base))

def run_one(prereg, negctl, ablation, ablated: bool):
    claim_id = prereg.get("claim_id", "unknown_claim")

    score_main = deterministic_score(claim_id, "main", ablated=ablated)
    score_neg  = deterministic_score(claim_id, "negative_control", ablated=ablated)

    metrics = {
        "score": score_main,
        "score_negative_control": score_neg,
        "delta": score_main - score_neg
    }

    decision = apply_gates(prereg, metrics, ablation=ablation)

    capsule = {
        "claim_id": claim_id,
        "ablated": ablated,
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "preregister": prereg,
        "controls": {"negative_control": negctl},
        "ablation": ablation,
        "metrics": metrics,
        "decision": decision,
    }

    capsule["hashes"] = {
        "capsule_sha12": obj_sha12(capsule),
        "preregister_sha12": obj_sha12(prereg),
        "metrics_sha12": obj_sha12(metrics),
        "ablation_sha12": obj_sha12(ablation),
    }

    capsule["aeq_cid"] = {
        "preregister": mint_fat(prereg, "prereg", meta={"claim_id": claim_id}),
        "ablation": mint_fat(ablation, "ablation", meta={"ablation_id": ablation.get("ablation_id","?")}),
        "metrics": mint_fat(metrics, "metrics", meta={"ablated": ablated}),
        "capsule": mint_fat(capsule["hashes"], "capsule_hashes", meta={"ablated": ablated}),
    }

    return capsule

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blind", action="store_true", help="Enable blinded arm labels and write reveal mapping.")
    ap.add_argument("--salt", type=str, default="demo_salt_v1", help="Salt used for deterministic arm IDs.")
    args = ap.parse_args()

    prereg = load_json(BASE / "preregister" / "claim.json")
    negctl = load_json(BASE / "controls" / "negative_control.json")
    ablation = load_json(BASE / "preregister" / "ablation.json")

    claim_id = prereg.get("claim_id", "unknown_claim")

    # Deterministic blinding map
    true_labels = ["BASELINE", "ABLATED"]
    blind_map = make_blind_map(claim_id, true_labels=true_labels, salt=args.salt)

    t0 = time.time()

    base_capsule = run_one(prereg, negctl, ablation, ablated=False)
    ablt_capsule = run_one(prereg, negctl, ablation, ablated=True)

    out_base = BASE / "outputs" / "evidence_capsule.BASELINE.json"
    out_ablt = BASE / "outputs" / "evidence_capsule.ABLATED.json"
    write_text(out_base, json.dumps(base_capsule, indent=2, ensure_ascii=False))
    write_text(out_ablt, json.dumps(ablt_capsule, indent=2, ensure_ascii=False))

    def fmt_gate(g): return f"- {'✅' if g['passed'] else '❌'} **{g['name']}** — {g['detail']}"

    # Labels shown publicly
    label_base = blind_map["BASELINE"] if args.blind else "BASELINE"
    label_ablt = blind_map["ABLATED"] if args.blind else "ABLATED"

    lines = []
    lines.append("# Φ Decision Card (Baseline vs Ablated)")
    lines.append(f"- claim_id: `{claim_id}`")
    if args.blind:
        lines.append(f"- mode: **BLINDED**")
        lines.append(f"- salt_sha12: `{sha12(args.salt)}`")
    lines.append("")

    lines.append("## AEQ–CID (Preregister + Ablation)")
    lines.append(f"- prereg: `{base_capsule['aeq_cid']['preregister']['cid']}`")
    lines.append(f"- prereg_fat: `{base_capsule['aeq_cid']['preregister']['cid_fat']}`")
    lines.append(f"- ablation: `{base_capsule['aeq_cid']['ablation']['cid']}`")
    lines.append(f"- ablation_fat: `{base_capsule['aeq_cid']['ablation']['cid_fat']}`")
    lines.append("")

    for label, cap in [(label_base, base_capsule), (label_ablt, ablt_capsule)]:
        lines.append(f"## {label}")
        lines.append(f"- phi: **{cap['decision']['phi']}**")
        lines.append(f"- capsule_sha12: `{cap['hashes']['capsule_sha12']}`")
        lines.append(f"- metrics_cid: `{cap['aeq_cid']['metrics']['cid']}`")
        lines.append("")
        lines.append("### Gates")
        for g in cap["decision"]["gates"]:
            lines.append(fmt_gate(g))
        lines.append("")
        lines.append("### Metrics")
        m = cap["metrics"]
        lines.append(f"- score: {m['score']:.6g}")
        lines.append(f"- score_negative_control: {m['score_negative_control']:.6g}")
        lines.append(f"- delta: {m['delta']:.6g}")
        lines.append("")

    if args.blind:
        paths = write_blind_files(claim_id, blind_map)
        lines.append("## Reveal (post-Φ)")
        lines.append(f"- reveal_file: `{paths['reveal'].name}`")
        lines.append(f"- {blind_map['BASELINE']} → BASELINE")
        lines.append(f"- {blind_map['ABLATED']} → ABLATED")
        lines.append("")

    out_md = BASE / "outputs" / "phi_card.md"
    write_text(out_md, "\n".join(lines) + "\n")

    ledger = BASE / "outputs" / "ledger.ndjson"
    for (lbl, cap) in [(label_base, base_capsule), (label_ablt, ablt_capsule)]:
        ledger_line = canonical_json({
            "ts": cap["ts_utc"],
            "claim_id": claim_id,
            "arm": lbl,
            "ablated": cap["ablated"],
            "phi": cap["decision"]["phi"],
            "capsule_sha12": cap["hashes"]["capsule_sha12"],
            "prereg_cid": cap["aeq_cid"]["preregister"]["cid"],
            "metrics_cid": cap["aeq_cid"]["metrics"]["cid"],
            "blinded": bool(args.blind),
        })
        with ledger.open("a", encoding="utf-8") as f:
            f.write(ledger_line + "\n")

    dt_ms = (time.time() - t0) * 1000.0
    print("Wrote:")
    print(" -", out_base)
    print(" -", out_ablt)
    print(" -", out_md)
    print("Appended ledger:", ledger)
    print(f"runtime_ms: {dt_ms:.2f}")

if __name__ == "__main__":
    main()
