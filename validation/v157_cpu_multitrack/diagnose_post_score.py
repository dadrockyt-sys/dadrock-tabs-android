#!/usr/bin/env python3
"""Post-score architecture diagnosis for frozen/consumed V157.

This script may read the frozen V157 candidate and frozen professional reference
because V157 scoring is complete. It deliberately does NOT import/call the official
scorer, does not write a candidate, and does not propose a corrected V157 variant.
All alignment scans are diagnostic architecture evidence only and must never be
promoted as song-specific generation constants.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any, Iterable

EPS = 1e-9


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rows(payload: dict[str, Any], stream: str) -> list[dict[str, Any]]:
    if stream == "combinedGuitar":
        return [dict(x) for x in payload["streams"][stream]]
    return [dict(x) for x in payload["streams"]["bass"]]


def ref_rows(payload: dict[str, Any], stream: str) -> list[dict[str, Any]]:
    parts = payload["parts"]
    raw = parts["rhythm"] + parts["lead"] if stream == "combinedGuitar" else parts["bass"]
    return [dict(x) for x in raw if not bool(x.get("excludeFromScoring", False))]


def absolute(note: dict[str, Any]) -> float:
    return (int(note["measure"]) - 1) * 16.0 + float(note["step"])


def prf(matched: int, generated: int, reference: int) -> dict[str, Any]:
    precision = matched / generated if generated else 1.0
    recall = matched / reference if reference else 1.0
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {"matched": matched, "generated": generated, "reference": reference,
            "precision": precision, "recall": recall, "f1": f1}


def optimal_abs_matches(generated: list[dict[str, Any]], reference: list[dict[str, Any]], shift: float, tol: float) -> int:
    """Maximum-cardinality same-MIDI matches in absolute-grid time; generated shifted only."""
    gg: dict[int, list[float]] = defaultdict(list)
    rr: dict[int, list[float]] = defaultdict(list)
    for n in generated:
        gg[int(n["midi"])].append(absolute(n) + shift)
    for n in reference:
        rr[int(n["midi"])].append(absolute(n))
    total = 0
    for midi in set(gg) & set(rr):
        g = sorted(gg[midi]); r = sorted(rr[midi])
        n, m = len(g), len(r)
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n - 1, -1, -1):
            for j in range(m - 1, -1, -1):
                best = max(dp[i + 1][j], dp[i][j + 1])
                if abs(g[i] - r[j]) <= tol + EPS:
                    best = max(best, 1 + dp[i + 1][j + 1])
                dp[i][j] = best
        total += dp[0][0]
    return total


def shift_scan(generated: list[dict[str, Any]], reference: list[dict[str, Any]], lo=-16.0, hi=16.0, step=0.25, tol=0.5) -> dict[str, Any]:
    values = []
    k = 0
    x = lo
    while x <= hi + EPS:
        matched = optimal_abs_matches(generated, reference, round(x, 6), tol)
        values.append({"shiftSteps": round(x, 6), "matched": matched, **prf(matched, len(generated), len(reference))})
        k += 1; x = lo + k * step
    best_match = max(v["matched"] for v in values)
    best = [v for v in values if v["matched"] == best_match]
    # deterministic diagnostic tie-break: closest to zero, then lower shift.
    chosen = min(best, key=lambda v: (abs(v["shiftSteps"]), v["shiftSteps"]))
    return {"chosen": chosen, "allBestShifts": [v["shiftSteps"] for v in best], "scanRange": [lo, hi], "increment": step, "tolerance": tol}


def quartile_shift_scan(generated: list[dict[str, Any]], reference: list[dict[str, Any]]) -> list[dict[str, Any]]:
    max_abs = max([absolute(x) for x in generated + reference], default=0.0)
    out = []
    for q in range(4):
        a = max_abs * q / 4.0; b = max_abs * (q + 1) / 4.0
        g = [x for x in generated if a <= absolute(x) < b or (q == 3 and absolute(x) <= b)]
        r = [x for x in reference if a <= absolute(x) < b or (q == 3 and absolute(x) <= b)]
        scan = shift_scan(g, r, lo=-16, hi=16, step=0.5, tol=0.5) if g and r else None
        out.append({"quartile": q + 1, "absoluteRange": [a, b], "generated": len(g), "reference": len(r), "shiftScan": scan})
    return out


def measure_pitch_content(generated: list[dict[str, Any]], reference: list[dict[str, Any]]) -> dict[str, Any]:
    gc = Counter((int(x["measure"]), int(x["midi"])) for x in generated)
    rc = Counter((int(x["measure"]), int(x["midi"])) for x in reference)
    matched = sum((gc & rc).values())
    return prf(matched, len(generated), len(reference))


def strict_measure_matches(generated: list[dict[str, Any]], reference: list[dict[str, Any]], tol=0.5) -> dict[str, Any]:
    gg: dict[tuple[int, int], list[float]] = defaultdict(list)
    rr: dict[tuple[int, int], list[float]] = defaultdict(list)
    for x in generated: gg[(int(x["measure"]), int(x["midi"]))].append(float(x["step"]))
    for x in reference: rr[(int(x["measure"]), int(x["midi"]))].append(float(x["step"]))
    matched = 0
    for key in set(gg) & set(rr):
        g = sorted(gg[key]); r = sorted(rr[key]); n, m = len(g), len(r)
        dp = [[0]*(m+1) for _ in range(n+1)]
        for i in range(n-1,-1,-1):
            for j in range(m-1,-1,-1):
                best=max(dp[i+1][j],dp[i][j+1])
                if abs(g[i]-r[j]) <= tol+EPS: best=max(best,1+dp[i+1][j+1])
                dp[i][j]=best
        matched += dp[0][0]
    return prf(matched, len(generated), len(reference))


def source_breakdown(guitar: list[dict[str, Any]], reference: list[dict[str, Any]]) -> dict[str, Any]:
    out = {}
    for source in sorted(set(str(x.get("source")) for x in guitar)):
        subset = [x for x in guitar if str(x.get("source")) == source]
        out[source] = {
            "count": len(subset),
            "strictMeasureTiming": strict_measure_matches(subset, reference),
            "measurePitchContent": measure_pitch_content(subset, reference),
            "globalShiftDiagnostic": shift_scan(subset, reference),
        }
    return out


def pitch_hist(rows_: Iterable[dict[str, Any]]) -> dict[str, int]:
    c = Counter(int(x["midi"]) for x in rows_)
    return {str(k): c[k] for k in sorted(c)}


def measure_counts(rows_: Iterable[dict[str, Any]]) -> Counter[int]:
    return Counter(int(x["measure"]) for x in rows_)


def bass_sparsity(generated: list[dict[str, Any]], reference: list[dict[str, Any]], metadata: dict[str, Any]) -> dict[str, Any]:
    gm = measure_counts(generated); rm = measure_counts(reference)
    all_measures = sorted(set(gm) | set(rm))
    ratios = []
    missing_measures = []
    for m in all_measures:
        if rm[m] > 0:
            ratios.append(gm[m] / rm[m])
            if gm[m] == 0: missing_measures.append(m)
    raw_onsets = int(metadata.get("detectedOnsetCount", 0))
    pre = int(metadata.get("eventCountBeforeGridDedupe", len(generated)))
    return {
        "generatedCount": len(generated),
        "referenceCount": len(reference),
        "generatedToReferenceRatio": len(generated)/len(reference) if reference else None,
        "detectedOnsetCount": raw_onsets,
        "detectedOnsetsToReferenceRatio": raw_onsets/len(reference) if reference else None,
        "eventsBeforeGridDedupe": pre,
        "eventsToDetectedOnsetsRatio": pre/raw_onsets if raw_onsets else None,
        "generatedFirstMeasure": min(gm) if gm else None,
        "generatedLastMeasure": max(gm) if gm else None,
        "referenceFirstMeasure": min(rm) if rm else None,
        "referenceLastMeasure": max(rm) if rm else None,
        "referenceMeasuresWithNoGeneratedBass": missing_measures,
        "medianPerMeasureGeneratedReferenceRatio": median(ratios) if ratios else None,
        "generatedPitchHistogram": pitch_hist(generated),
        "referencePitchHistogram": pitch_hist(reference),
        "strictMeasureTiming": strict_measure_matches(generated, reference),
        "measurePitchContent": measure_pitch_content(generated, reference),
        "globalShiftDiagnostic": shift_scan(generated, reference),
        "quartileShiftDiagnostic": quartile_shift_scan(generated, reference),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generated", type=Path, required=True)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise RuntimeError("V157 diagnostic output is write-once")
    generated_payload = load(args.generated)
    reference_payload = load(args.reference)
    guitar = rows(generated_payload, "combinedGuitar")
    bass = rows(generated_payload, "bass")
    rg = ref_rows(reference_payload, "combinedGuitar")
    rb = ref_rows(reference_payload, "bass")

    report = {
        "schema": "dadrock.tabs.v157.post-score-architecture-diagnostic.v1",
        "classification": "post-score-diagnostic-only-no-candidate-correction",
        "safety": {
            "officialScorerImported": False,
            "officialScorerCalled": False,
            "additionalReferenceFacingScoreCalls": 0,
            "candidateModified": False,
            "candidateVariantWritten": False,
            "thresholdSweepForCandidate": False,
            "futureHardcodedReferenceCorrectionAllowed": False,
        },
        "combinedGuitar": {
            "count": len(guitar), "referenceCount": len(rg),
            "strictMeasureTiming": strict_measure_matches(guitar, rg),
            "measurePitchContent": measure_pitch_content(guitar, rg),
            "globalShiftDiagnostic": shift_scan(guitar, rg),
            "quartileShiftDiagnostic": quartile_shift_scan(guitar, rg),
            "sourceBreakdown": source_breakdown(guitar, rg),
        },
        "bass": bass_sparsity(bass, rb, generated_payload.get("streamMetadata", {}).get("bass", {})),
        "interpretationRules": [
            "Shift scans are post-score architecture evidence only; never promote selected shifts to future song-specific constants.",
            "Source-specific reference metrics may motivate generic architecture changes but may not be used to filter or rewrite V157.",
            "V157 score count stays permanently 1; this diagnostic must not import or call the official scorer.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
