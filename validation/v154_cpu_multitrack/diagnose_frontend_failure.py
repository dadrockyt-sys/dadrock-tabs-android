#!/usr/bin/env python3
"""Post-score diagnostic-only analysis of the consumed V154 front end.

This script reads the frozen candidate, frozen reference, and frozen score only.
It does NOT import/call the official scorer and does NOT write any candidate.
Its output is descriptive architecture diagnosis for choosing a future experiment.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json"
REF = ROOT / "research/v154-professional-references/scorer-ready/frontend-reference-payload.json"
SCORE = ROOT / "debug/v154-cpu-autonomous/v154-frontend-reference-score/score.json"
OUT = ROOT / "debug/v154-cpu-autonomous/v154-frontend-reference-score/architecture-diagnostic.json"

EXPECTED = {
    GEN: "1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37",
    REF: "b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7",
    SCORE: "c206f6bc951c6bd9b6cc19e6758c4aef6654f349cc1f5712df1f052e46fa798b",
}

SECTIONS = [
    ("intro_riff", 1, 16),
    ("verse1", 17, 32),
    ("chorus1", 33, 38),
    ("riff_return1", 39, 46),
    ("verse2", 47, 62),
    ("chorus2", 63, 69),
    ("bridge", 70, 77),
    ("solo", 78, 94),
    ("outro", 95, 113),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pinned(path: Path) -> Any:
    actual = sha256(path)
    if actual != EXPECTED[path]:
        raise RuntimeError(f"identity drift {path}: {actual}")
    return json.loads(path.read_text(encoding="utf-8"))


def rows(raw: Iterable[dict[str, Any]]) -> list[dict[str, float | int]]:
    out = []
    for n in raw:
        if bool(n.get("excludeFromScoring", False)):
            continue
        out.append({"measure": int(n["measure"]), "step": float(n["step"]), "midi": int(n["midi"])})
    return out


def prf(matched: int, generated: int, reference: int) -> dict[str, float | int]:
    p = 1.0 if generated == 0 else matched / generated
    r = 1.0 if reference == 0 else matched / reference
    f = 0.0 if p + r == 0 else 2 * p * r / (p + r)
    return {"matched": matched, "generated": generated, "reference": reference, "precision": p, "recall": r, "f1": f}


def counter_metric(g: list[dict[str, Any]], r: list[dict[str, Any]], key) -> dict[str, Any]:
    gc = Counter(key(n) for n in g)
    rc = Counter(key(n) for n in r)
    return prf(sum((gc & rc).values()), sum(gc.values()), sum(rc.values()))


def match_sorted(gs: list[float], rs: list[float], tol: float) -> int:
    i = j = matched = 0
    while i < len(gs) and j < len(rs):
        if gs[i] < rs[j] - tol:
            i += 1
        elif rs[j] < gs[i] - tol:
            j += 1
        else:
            matched += 1
            i += 1
            j += 1
    return matched


def same_measure_midi_matches(g: list[dict[str, Any]], r: list[dict[str, Any]], tol: float) -> int:
    gg: dict[tuple[int, int], list[float]] = defaultdict(list)
    rr: dict[tuple[int, int], list[float]] = defaultdict(list)
    for n in g:
        gg[(int(n["measure"]), int(n["midi"]))].append(float(n["step"]))
    for n in r:
        rr[(int(n["measure"]), int(n["midi"]))].append(float(n["step"]))
    return sum(match_sorted(sorted(gg[k]), sorted(rr[k]), tol) for k in set(gg) & set(rr))


def absolute_midi_matches(g: list[dict[str, Any]], r: list[dict[str, Any]], tol: float, shift: float) -> int:
    gg: dict[int, list[float]] = defaultdict(list)
    rr: dict[int, list[float]] = defaultdict(list)
    for n in g:
        gg[int(n["midi"])].append((int(n["measure"]) - 1) * 16.0 + float(n["step"]) + shift)
    for n in r:
        rr[int(n["midi"])].append((int(n["measure"]) - 1) * 16.0 + float(n["step"]))
    return sum(match_sorted(sorted(gg[k]), sorted(rr[k]), tol) for k in set(gg) & set(rr))


def quantile(vals: list[float], q: float) -> float | None:
    if not vals:
        return None
    s = sorted(vals)
    idx = int(round((len(s) - 1) * q))
    return s[idx]


def fractional_step_stats(g: list[dict[str, Any]]) -> dict[str, Any]:
    d = [abs(float(n["step"]) - round(float(n["step"]))) for n in g]
    return {"medianDistanceToIntegerStep": median(d) if d else None, "p90": quantile(d, 0.90), "maximum": max(d) if d else None}


def nearest_same_measure_midi_delta(g: list[dict[str, Any]], r: list[dict[str, Any]]) -> dict[str, Any]:
    rr: dict[tuple[int, int], list[float]] = defaultdict(list)
    for n in r:
        rr[(int(n["measure"]), int(n["midi"]))].append(float(n["step"]))
    signed = []
    for n in g:
        candidates = rr.get((int(n["measure"]), int(n["midi"])))
        if not candidates:
            continue
        gs = float(n["step"])
        rs = min(candidates, key=lambda x: abs(gs - x))
        signed.append(gs - rs)
    bins = Counter(round(x * 4) / 4 for x in signed)
    absd = [abs(x) for x in signed]
    return {
        "generatedNotesWithSameMeasureMidiReference": len(signed),
        "medianAbsoluteDeltaSteps": median(absd) if absd else None,
        "p90AbsoluteDeltaSteps": quantile(absd, 0.90),
        "topSignedQuarterStepDeltaBins": [{"delta": k, "count": v} for k, v in bins.most_common(12)],
    }


def shift_scan(g: list[dict[str, Any]], r: list[dict[str, Any]]) -> dict[str, Any]:
    scans = []
    for i in range(-64, 65):  # -16..+16 in quarter-step increments
        shift = i / 4
        m = absolute_midi_matches(g, r, 0.5, shift)
        scans.append((m, shift))
    scans.sort(key=lambda x: (-x[0], abs(x[1]), x[1]))
    best_m, best_shift = scans[0]
    zero_m = absolute_midi_matches(g, r, 0.5, 0.0)
    return {
        "toleranceSteps": 0.5,
        "scanRangeSteps": [-16, 16],
        "scanIncrementSteps": 0.25,
        "zeroShift": {**prf(zero_m, len(g), len(r)), "shiftSteps": 0.0},
        "bestShift": {**prf(best_m, len(g), len(r)), "shiftSteps": best_shift},
        "topShifts": [{"shiftSteps": s, "matched": m} for m, s in scans[:10]],
    }


def measure_shift_scan(g: list[dict[str, Any]], r: list[dict[str, Any]]) -> dict[str, Any]:
    vals = []
    for shift in range(-4, 5):
        metric = counter_metric(g, r, lambda n, shift=shift: (int(n["measure"]) + shift, int(n["midi"])))
        vals.append((float(metric["f1"]), shift, metric))
    vals.sort(key=lambda x: (-x[0], abs(x[1]), x[1]))
    return {"best": {"measureShift": vals[0][1], **vals[0][2]}, "all": [{"measureShift": s, **m} for _, s, m in vals]}


def section_metrics(g: list[dict[str, Any]], r: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for name, lo, hi in SECTIONS:
        gg = [n for n in g if lo <= int(n["measure"]) <= hi]
        rr = [n for n in r if lo <= int(n["measure"]) <= hi]
        primary = same_measure_midi_matches(gg, rr, 0.5)
        gross = same_measure_midi_matches(gg, rr, 2.0)
        out.append({
            "section": name,
            "measures": [lo, hi],
            "pitchContentByMeasure": counter_metric(gg, rr, lambda n: (int(n["measure"]), int(n["midi"]))),
            "pitchClassContentByMeasure": counter_metric(gg, rr, lambda n: (int(n["measure"]), int(n["midi"]) % 12)),
            "timingSameMidiTolerance0_5": prf(primary, len(gg), len(rr)),
            "timingSameMidiTolerance2_0": prf(gross, len(gg), len(rr)),
        })
    return out


def diagnose_stream(g: list[dict[str, Any]], r: list[dict[str, Any]]) -> dict[str, Any]:
    exact_content = counter_metric(g, r, lambda n: (int(n["measure"]), int(n["midi"])))
    pc_content = counter_metric(g, r, lambda n: (int(n["measure"]), int(n["midi"]) % 12))
    primary = same_measure_midi_matches(g, r, 0.5)
    gross = same_measure_midi_matches(g, r, 2.0)
    return {
        "counts": {"generated": len(g), "reference": len(r)},
        "pitchContentByMeasure": exact_content,
        "pitchClassContentByMeasure": pc_content,
        "timingSameMidiTolerance0_5": prf(primary, len(g), len(r)),
        "timingSameMidiTolerance2_0": prf(gross, len(g), len(r)),
        "generatedFractionalStepStats": fractional_step_stats(g),
        "nearestSameMeasureMidiTimingDelta": nearest_same_measure_midi_delta(g, r),
        "globalAbsoluteShiftScan": shift_scan(g, r),
        "measureIndexShiftScanPitchContent": measure_shift_scan(g, r),
        "sections": section_metrics(g, r),
    }


def infer(label: str, d: dict[str, Any]) -> list[str]:
    findings = []
    exact = float(d["pitchContentByMeasure"]["f1"])
    pc = float(d["pitchClassContentByMeasure"]["f1"])
    primary = float(d["timingSameMidiTolerance0_5"]["f1"])
    gross = float(d["timingSameMidiTolerance2_0"]["f1"])
    zero = float(d["globalAbsoluteShiftScan"]["zeroShift"]["f1"])
    best = float(d["globalAbsoluteShiftScan"]["bestShift"]["f1"])
    shift = float(d["globalAbsoluteShiftScan"]["bestShift"]["shiftSteps"])
    mshift = int(d["measureIndexShiftScanPitchContent"]["best"]["measureShift"])
    if exact - primary > 0.20:
        findings.append(f"{label}: timing/grid placement is a major failure mode; measure-level exact-pitch content F1 exceeds ±0.5-step timing F1 by {exact-primary:.3f}.")
    if gross - primary > 0.10:
        findings.append(f"{label}: many same-pitch events are displaced beyond the primary half-step timing window; widening to ±2 steps gains {gross-primary:.3f} F1 but remains far below target.")
    if best > zero + 0.05:
        findings.append(f"{label}: a global absolute-time shift of {shift:+.2f} steps materially improves diagnostic same-MIDI alignment (F1 {zero:.3f}->{best:.3f}), indicating grid-origin/phase error.")
    else:
        findings.append(f"{label}: no single global phase shift fixes the architecture (best diagnostic shift {shift:+.2f} steps, F1 {best:.3f}); errors are not just one constant offset.")
    if mshift != 0:
        findings.append(f"{label}: best pitch-content measure-index diagnostic shift is {mshift:+d}, suggesting possible coarse bar-index alignment error to investigate.")
    if pc > exact + 0.08:
        findings.append(f"{label}: pitch-class F1 exceeds exact-MIDI F1 by {pc-exact:.3f}, consistent with octave/register errors contributing materially.")
    else:
        findings.append(f"{label}: pitch-class relaxation gives limited gain ({exact:.3f}->{pc:.3f}); failures are not dominated by octave/register mistakes alone.")
    worst = sorted(d["sections"], key=lambda x: float(x["timingSameMidiTolerance0_5"]["f1"]))[:3]
    findings.append(f"{label}: weakest timing sections are " + ", ".join(f"{x['section']}={float(x['timingSameMidiTolerance0_5']['f1']):.3f}" for x in worst) + ".")
    return findings


def main() -> int:
    if OUT.exists():
        raise RuntimeError("diagnostic output already exists; write-once")
    gen = load_pinned(GEN)
    ref = load_pinned(REF)
    _score = load_pinned(SCORE)

    guitar_g = rows(gen["streams"]["combinedGuitar"])
    bass_g = rows(gen["streams"]["bass"])
    guitar_r = rows(ref["parts"]["rhythm"] + ref["parts"]["lead"])
    bass_r = rows(ref["parts"]["bass"])

    guitar = diagnose_stream(guitar_g, guitar_r)
    bass = diagnose_stream(bass_g, bass_r)
    findings = infer("combinedGuitar", guitar) + infer("bass", bass)
    report = {
        "schema": "dadrock.tabs.v154.post-score-architecture-diagnostic.v1",
        "validation": "PASS",
        "frozenInputs": {str(p.relative_to(ROOT)): EXPECTED[p] for p in EXPECTED},
        "policy": {
            "diagnosticOnly": True,
            "officialScorerImportedOrCalled": False,
            "additionalOfficialReferenceFacingScoreCalls": 0,
            "generatedCandidateModified": False,
            "generatedCandidateCorrectionWritten": False,
            "candidateRetuningOrThresholdSweep": False,
            "cpuOnly": True,
            "modalL4CudaGpuUsed": False,
            "mainOrProductionModified": False,
        },
        "combinedGuitar": guitar,
        "bass": bass,
        "findings": findings,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"validation": "PASS", "findings": findings, "output": str(OUT.relative_to(ROOT)), "sha256": sha256(OUT)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
