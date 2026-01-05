[![CI](https://github.com/TheProblemShredder/ScrollCert_vOmega_PublicDemo/actions/workflows/ci.yml/badge.svg)](https://github.com/TheProblemShredder/ScrollCert_vOmega_PublicDemo/actions/workflows/ci.yml)

# ScrollCert vΩ — Verification-First Research Demo

A minimal, reproducible demonstration of a **verification-first workflow** for research/engineering claims:
preregistration → controls → ablations → blinded evaluation → Φ decision → audit ledger.

## What this shows
- **Preregistration** of a claim with thresholds (before seeing results)
- **Negative control** expected to fail (sanity check)
- **Ablation discipline**: remove a component and verify signal drops (delta gate)
- **Blinded evaluation**: arms are hidden until reveal (reduces experimenter bias)
- **Deterministic IDs (AEQ–CID)** + content-hash evidence spine
- **Append-only audit ledger** (`outputs/ledger.ndjson`) for traceability

> This repo uses synthetic metrics to demonstrate the methodology.  
> The same scaffolding is designed to wrap real experiments/adapters.

## What to open first (30 seconds)
- `docs/protocol_vomega.md` — the verification-first protocol in plain English
- `src/gates.py` — the PASS/FAIL gate logic (falsification + delta)
- `outputs/phi_card.md` — example decision card (generated locally)

## Quickstart

Run (standard):
    ./run.py

Run (blinded):
    rm -f outputs/ledger.ndjson
    ./run.py --blind --salt "demo_salt_001"
    head -n 40 outputs/phi_card.md

## Outputs (generated under `outputs/`)
- `phi_card.md`
- `evidence_capsule.BASELINE.json`
- `evidence_capsule.ABLATED.json`
- `ledger.ndjson`
- `blind_map.json` / `reveal.json` (when `--blind`)
## How to talk about this in interviews (30 seconds)
“I built a verification-first scaffold that forces claims to pass preregistration, negative controls, ablations, and blinded evaluation before I trust results. It emits deterministic IDs and an append-only ledger for audit. This repo is a minimal public demo of that methodology — the same pattern wraps real experiments and prevents self-deception in research and ML/quant workflows.”

## Skills demonstrated
- Python tooling & reproducible experiment scaffolds
- Deterministic hashing / audit IDs (content-addressed style)
- CI automation (GitHub Actions)
- Research engineering discipline (controls/ablations/blinding)

## Proof (reproducible run)

**Goal:** reproduce a deterministic test run + verify the package installs correctly.

### Commands
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e . pytest
pytest -q

python3 -c "import importlib; importlib.import_module('src'); print('import_ok', 'src')"
```

### Example output
See: `docs/example_output.txt`
