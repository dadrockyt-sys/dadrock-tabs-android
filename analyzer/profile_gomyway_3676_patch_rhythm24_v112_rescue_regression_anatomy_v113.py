from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V112_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v111-lowband-phase-interaction-augmentation-v112.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v112-rescue-regression-anatomy-v113.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v112-rescue-regression-anatomy-v113-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
LOWBAND_FEATURES = ["mean::lowBurst", "mean::lowRise", "mean::lowDecay30", "mean::lowPostSlope"]
PHASE_LABELS = ["p2sin", "p2cos", "p4sin", "p4cos"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_float(v: Any) -> float | None:
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except Exception:
        return None


def cohen_d(a: list[float], b: list[float]) -> float | None:
    if len(a) < 2 or len(b) < 2:
        return None
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    va = float(np.var(aa, ddof=1))
    vb = float(np.var(bb, ddof=1))
    denom = len(aa) + len(bb) - 2
    if denom <= 0:
        return None
    pooled = math.sqrt(max(0.0, ((len(aa) - 1) * va + (len(bb) - 1) * vb) / denom))
    if pooled <= 1e-12:
        return None
    return float((np.mean(aa) - np.mean(bb)) / pooled)


def categorical_counts(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for label, pred in (("gain", lambda r: bool(r.get("gainVsV96"))), ("loss", lambda r: bool(r.get("lossVsV96")))):
        c = Counter(str(r.get(key)) for r in rows if pred(r))
        out[label] = dict(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))
    return out


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text())
    slots = list(payload.get("candidateSlots") or [])
    if not slots or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")
    if not V112_PATH.exists():
        raise RuntimeError(f"Missing saved V112 output: {V112_PATH}")

    v112 = json.loads(V112_PATH.read_text())
    rows = list(v112.get("rowsDetail") or [])
    gains = [r for r in rows if bool(r.get("gainVsV96"))]
    losses = [r for r in rows if bool(r.get("lossVsV96"))]
    if len(gains) != 6 or len(losses) != 7:
        print(f"WARNING: expected V112 changed-row counts 6 gains / 7 losses, got {len(gains)} / {len(losses)}")

    names = sorted((slots[0].get("features") or {}).keys())
    idx = {name: i for i, name in enumerate(names)}
    missing = [name for name in LOWBAND_FEATURES if name not in idx]
    if missing:
        raise RuntimeError(f"Missing V113 low-band source features: {missing}")

    xb = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in slots],
        dtype=np.float64,
    )
    pf = np.asarray(v17.phase_features(slots), dtype=np.float64)
    measures = np.asarray([int(r["measure"]) for r in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    changed = [r for r in rows if bool(r.get("gainVsV96")) or bool(r.get("lossVsV96"))]
    detail = []
    numeric_by_group: dict[str, dict[str, list[float]]] = {
        "gain": defaultdict(list),
        "loss": defaultdict(list),
    }

    for r in changed:
        group = "gain" if bool(r.get("gainVsV96")) else "loss"
        phase = float(r["phase"])
        fold = int(r["fold"])
        ids = np.asarray(
            [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures],
            dtype=np.int16,
        )
        test = ids == fold
        if int(np.sum(test)) == 0:
            raise RuntimeError(f"Empty reconstructed test fold phase={phase} fold={fold}")

        metrics: dict[str, float] = {}
        for f in LOWBAND_FEATURES:
            col = xb[test, idx[f]]
            metrics[f"testMean::{f}"] = float(np.mean(col))
            metrics[f"testStd::{f}"] = float(np.std(col))
        for j, p in enumerate(PHASE_LABELS):
            col = pf[test, j]
            metrics[f"testMean::{p}"] = float(np.mean(col))
            metrics[f"testStd::{p}"] = float(np.std(col))
        for f in LOWBAND_FEATURES:
            low = xb[test, idx[f]]
            for j, p in enumerate(PHASE_LABELS):
                prod = low * pf[test, j]
                metrics[f"testMean::{f}*{p}"] = float(np.mean(prod))
                metrics[f"testStd::{f}*{p}"] = float(np.std(prod))

        for k, v in metrics.items():
            numeric_by_group[group][k].append(float(v))

        detail.append({
            "group": group,
            "source": r.get("source"),
            "phase": phase,
            "fold": fold,
            "decision": r.get("decision"),
            "pairRadius": r.get("pairRadius"),
            "lambda": r.get("lambda"),
            "excluded": bool(r.get("excluded")),
            "v28Passed": bool(r.get("v28Passed")),
            "v96Passed": bool(r.get("v96Passed")),
            "v112Passed": bool(r.get("v112Passed")),
            "testRows": int(np.sum(test)),
            "metrics": metrics,
        })

    effects = []
    metric_keys = sorted(set(numeric_by_group["gain"]) | set(numeric_by_group["loss"]))
    for key in metric_keys:
        ga = numeric_by_group["gain"].get(key, [])
        lo_vals = numeric_by_group["loss"].get(key, [])
        if not ga or not lo_vals:
            continue
        d = cohen_d(ga, lo_vals)
        effects.append({
            "metric": key,
            "gainMean": float(np.mean(ga)),
            "lossMean": float(np.mean(lo_vals)),
            "differenceGainMinusLoss": float(np.mean(ga) - np.mean(lo_vals)),
            "cohenD": d,
            "absCohenD": abs(d) if d is not None else None,
            "gainN": len(ga),
            "lossN": len(lo_vals),
        })
    effects.sort(key=lambda x: (-(x["absCohenD"] if x["absCohenD"] is not None else -1.0), x["metric"]))

    phase_bins = {"gain": Counter(), "loss": Counter()}
    for r in changed:
        group = "gain" if bool(r.get("gainVsV96")) else "loss"
        b = int(math.floor((float(r["phase"]) % 1.0) * 16.0))
        b = min(max(b, 0), 15)
        phase_bins[group][f"{b}/16-{b+1}/16"] += 1

    summary = {
        "v96ScorePercent": (v112.get("summary") or {}).get("v96ScorePercent"),
        "v112ScorePercent": (v112.get("summary") or {}).get("v112ScorePercent"),
        "changedRows": len(changed),
        "gainsVsV96": len(gains),
        "lossesVsV96": len(losses),
        "netVsV96": len(gains) - len(losses),
        "categorical": {
            "source": categorical_counts(changed, "source"),
            "decision": categorical_counts(changed, "decision"),
            "pairRadius": categorical_counts(changed, "pairRadius"),
            "lambda": categorical_counts(changed, "lambda"),
            "v28Passed": categorical_counts(changed, "v28Passed"),
            "phaseBin1over16": {
                "gain": dict(phase_bins["gain"]),
                "loss": dict(phase_bins["loss"]),
            },
        },
        "topNumericEffectsGainVsLoss": effects[:24],
    }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V113")

    out = {
        "schemaVersion": 113,
        "profileType": "v112-rescue-vs-regression-anatomy-diagnostic",
        "summary": summary,
        "changedRowsDetail": detail,
        "usesSavedV112OutcomesOnlyForDiagnosis": True,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "heldoutOutcomeChangesUsedForDiagnosisOnly": True,
        "diagnosticOutcomesTaintedForFutureSelection": True,
        "newProductionTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k != "changedRowsDetail"}, indent=2) + "\n")

    print("GOMYWAY V113 V112 RESCUE-vs-REGRESSION ANATOMY DIAGNOSTIC COMPLETE")
    print(f"V96 scoreboard: {summary['v96ScorePercent']}%")
    print(f"V112 scoreboard: {summary['v112ScorePercent']}%")
    print(f"Changed rows: {len(changed)} = gains {len(gains)} / losses {len(losses)} / net {len(gains)-len(losses):+d}")
    print("\n=== CATEGORICAL ANATOMY ===")
    for key, val in summary["categorical"].items():
        print(f"{key}: {val}")
    print("\n=== TOP NUMERIC EFFECTS: V112 GAINS vs LOSSES ===")
    for e in effects[:16]:
        print(e)
    print("\nUses saved V112 outcomes only for diagnosis: True")
    print("Previously exposed V56/V57 only: True")
    print("V97 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("Held-out outcome changes used for diagnosis only: True")
    print("New production tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
