#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str

def _cmp(value: float, threshold: float, direction: str) -> (bool, str):
    if direction == "greater_than":
        return value > threshold, f"{value:.6g} > {threshold:.6g}"
    if direction == "greater_or_equal":
        return value >= threshold, f"{value:.6g} >= {threshold:.6g}"
    if direction == "less_than":
        return value < threshold, f"{value:.6g} < {threshold:.6g}"
    if direction == "less_or_equal":
        return value <= threshold, f"{value:.6g} <= {threshold:.6g}"
    return False, f"Unknown direction '{direction}'"

def apply_gates(prereg: Dict[str, Any], metrics: Dict[str, Any], ablation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    gates: List[GateResult] = []

    # Gate 1: prereg falsification gate
    fals = prereg.get("falsification", {})
    metric_name = fals.get("metric", "score")
    threshold = float(fals.get("threshold", 0.0))
    direction = fals.get("direction", "greater_than")

    value = float(metrics.get(metric_name, 0.0))
    ok, cmp_txt = _cmp(value, threshold, direction)
    gates.append(GateResult(
        name="falsification_gate",
        passed=ok,
        detail=f"{metric_name}={value:.6g} ; require {cmp_txt}"
    ))

    # Gate 2: delta gate (optional, but we enable it for ablation discipline)
    if ablation is not None:
        dg = ablation.get("delta_gate", {})
        d_metric = dg.get("metric", "delta")
        d_threshold = float(dg.get("threshold", 0.0))
        d_direction = dg.get("direction", "greater_or_equal")

        d_val = float(metrics.get(d_metric, 0.0))
        d_ok, d_cmp = _cmp(d_val, d_threshold, d_direction)
        gates.append(GateResult(
            name="delta_gate",
            passed=d_ok,
            detail=f"{d_metric}={d_val:.6g} ; require {d_cmp}"
        ))

    all_passed = all(g.passed for g in gates)
    return {
        "phi": "PASS" if all_passed else "FAIL",
        "gates": [{"name": g.name, "passed": g.passed, "detail": g.detail} for g in gates]
    }
