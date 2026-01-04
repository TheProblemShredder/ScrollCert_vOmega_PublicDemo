# ScrollCert vΩ — Verification-First Research Demo

This repo demonstrates a verification-first workflow:

- Preregistration (metric/threshold/direction)
- Negative control
- Ablation discipline (delta gate)
- Φ decision (PASS/FAIL) with gate details
- Blinded evaluation mode (ARM labels until reveal)
- AEQ–CID IDs + content-hash evidence spine
- Append-only ledger (outputs/ledger.ndjson)

## Quickstart

Run (standard):
  ./run.py

Run (blinded):
  ./run.py --blind --salt "demo_salt_001"

Outputs (generated under outputs/):
- phi_card.md
- evidence_capsule.BASELINE.json
- evidence_capsule.ABLATED.json
- ledger.ndjson
- blind_map.json / reveal.json (when --blind)
