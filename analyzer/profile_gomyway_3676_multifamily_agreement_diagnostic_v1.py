from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_pitch_register_interval_recovery_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PITCH_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-recovery-v1.json"
STABILITY_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-signature-stability-v1.json"
PATTERN_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-pattern-recovery-v1.json"
PHRASE_PATH = PUBLIC / "gomyway-3676-repeated-phrase-template-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-multifamily-agreement-diagnostic-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-multifamily-agreement-diagnostic-v1-manifest.json"

EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token_tuple(value: Any) -> tuple[int, int, int]:
    if isinstance(value, str):
        parts = value.replace("(", "").replace(")", "").replace("[", "").replace("]", "").split(",")
        if len(parts) >= 3:
            return int(parts[0]), int(parts[1]), int(parts[2])
        raise ValueError(value)
    if isinstance(value, (list, tuple)) and len(value) >= 3:
        return int(value[0]), int(value[1]), int(value[2])
    raise ValueError(value)


def precision(true: int, false: int) -> float:
    total = true + false
    return 100.0 * true / total if total else 0.0


def pitch_f1(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def contiguous_fold(measure: int, lo: int, hi: int) -> int:
    span = max(1, hi - lo + 1)
    return min(FOLD_COUNT - 1, int(FOLD_COUNT * (measure - lo) / span))


def shifted_window_fold(measure: int, lo: int, hi: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / FOLD_COUNT
    shift = width / 2.0
    pos = ((measure - lo) + shift) % span
    return min(FOLD_COUNT - 1, int(pos / width))


def selected_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    true = sum(str(r.get("label")) == "true" for r in rows)
    false = len(rows) - true
    matched = EXPECTED[0] + true
    missing = EXPECTED[1] - true
    extra = EXPECTED[2] + false
    return {
        "selected": len(rows),
        "recoverTrue": true,
        "recoverFalse": false,
        "precision": round(precision(true, false), 2),
        "pitchF1": pitch_f1(matched, missing, extra),
        "matchedMissingExtra": [matched, missing, extra],
    }


def partition_stats(
    rows: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
    fold_fn: Callable[[int], int],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for fold in range(FOLD_COUNT):
        chosen = [r for r in rows if fold_fn(int(r["measure"])) == fold and predicate(r)]
        stats = selected_stats(chosen)
        out.append({"fold": fold, **stats})
    return out


def scheme_summary(parts: list[dict[str, Any]], base_precision: float) -> dict[str, Any]:
    supported = [p for p in parts if int(p["selected"]) > 0]
    improving = [p for p in supported if float(p["pitchF1"]) > EXPECTED_F1 and int(p["recoverTrue"]) > 0]
    precision_lift = [p for p in supported if float(p["precision"]) >= base_precision + 5.0]
    return {
        "supportedFolds": len(supported),
        "improvingFolds": len(improving),
        "precisionLiftFolds": len(precision_lift),
        "minSupportedPrecision": round(min((float(p["precision"]) for p in supported), default=0.0), 2),
        "meanSupportedPrecision": round(sum(float(p["precision"]) for p in supported) / len(supported), 2) if supported else 0.0,
    }


def main() -> None:
    before = sha256(prof.recall.CANDIDATE_PATH)

    pitch_payload = json.loads(PITCH_PATH.read_text(encoding="utf-8"))
    stability_payload = json.loads(STABILITY_PATH.read_text(encoding="utf-8"))
    pattern_payload = json.loads(PATTERN_PATH.read_text(encoding="utf-8"))
    phrase_payload = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))

    if tuple(pitch_payload.get("championMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Pitch profiler is not anchored to frozen 36.76 champion")
    if tuple(stability_payload.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Stability profiler is not anchored to frozen 36.76 champion")
    if tuple(phrase_payload.get("championMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Phrase profiler is not anchored to frozen 36.76 champion")

    pitch_rows = list(pitch_payload.get("candidateRows") or [])
    pattern_rows = list(pattern_payload.get("candidateRows") or [])
    phrase_rows = list(phrase_payload.get("candidateRows") or [])
    stable_rows = list(stability_payload.get("stableSignatures") or [])
    if not pitch_rows or not pattern_rows:
        raise RuntimeError("Required residual candidate rows are missing")

    stable_pitch_signatures = {
        str(r.get("signature"))
        for r in stable_rows
        if str(r.get("family")) == "prCross" and bool(r.get("stableDiagnostic"))
    }
    if not stable_pitch_signatures:
        raise RuntimeError("No stable diagnostic prCross signatures found")

    pattern_map = {token_tuple(r.get("token")): r for r in pattern_rows}
    phrase_map = {token_tuple(r.get("token")): r for r in phrase_rows}

    rows: list[dict[str, Any]] = []
    for p in pitch_rows:
        tok = token_tuple(p.get("token"))
        raw = pattern_map.get(tok, {})
        phrase = phrase_map.get(tok)
        sigs = {str(s) for s in (p.get("signatures") or [])}

        persistence = int(raw.get("sweepPersistence", 0) or 0)
        stems = int(raw.get("stemCountAtWide", 0) or 0)
        strictest = int(raw.get("strictestSweepIndex", 99) if raw else 99)
        grid_error = float(raw.get("minGridError", 9.0) if raw else 9.0)
        duration = float(raw.get("maxDuration", 0.0) if raw else 0.0)
        amplitude = float(raw.get("maxAmplitude", 0.0) if raw else 0.0)

        phrase_exact = int(phrase.get("exactSupport", 0) if phrase else 0)
        phrase_pc = int(phrase.get("pcSupport", 0) if phrase else 0)
        phrase_strong = int(phrase.get("strongSupport", 0) if phrase else 0)
        phrase_similarity = float(phrase.get("bestSimilarity", 0.0) if phrase else 0.0)

        pitch_core = bool(sigs & stable_pitch_signatures)
        acoustic_stems = stems >= 2
        acoustic_persistent = persistence >= 3
        acoustic_strict = strictest <= 1
        acoustic_timing = grid_error <= 0.035
        acoustic_duration = duration >= 0.08
        acoustic_multi = sum((acoustic_stems, acoustic_persistent, acoustic_strict, acoustic_timing, acoustic_duration)) >= 2
        acoustic_strong = acoustic_stems and acoustic_persistent

        phrase_any = phrase is not None
        phrase_exact_support = phrase_exact >= 1
        phrase_pc_support = phrase_pc >= 1
        phrase_strong_support = phrase_strong >= 1 or phrase_similarity >= 0.60

        rows.append({
            "token": list(tok),
            "measure": int(p["measure"]),
            "step": int(p.get("step", tok[1])),
            "pitch": int(p.get("pitch", tok[2])),
            "label": str(p.get("label")),
            "pitchCore": pitch_core,
            "acoustic": {
                "stemBoth": acoustic_stems,
                "persistent3p": acoustic_persistent,
                "strictSweep": acoustic_strict,
                "tightGrid": acoustic_timing,
                "duration80ms": acoustic_duration,
                "multiEvidence": acoustic_multi,
                "strong": acoustic_strong,
                "sweepPersistence": persistence,
                "stemCountAtWide": stems,
                "strictestSweepIndex": strictest,
                "minGridError": grid_error,
                "maxDuration": duration,
                "maxAmplitude": amplitude,
            },
            "phrase": {
                "present": phrase_any,
                "exact": phrase_exact_support,
                "pc": phrase_pc_support,
                "strong": phrase_strong_support,
                "exactSupport": phrase_exact,
                "pcSupport": phrase_pc,
                "strongSupport": phrase_strong,
                "bestSimilarity": phrase_similarity,
            },
        })

    residual_true = sum(r["label"] == "true" for r in rows)
    residual_false = len(rows) - residual_true
    base_precision = precision(residual_true, residual_false)
    measures = sorted({int(r["measure"]) for r in rows})
    lo, hi = min(measures), max(measures)

    rules: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
        ("pitchCore", lambda r: bool(r["pitchCore"])),
        ("pitchCore+stemBoth", lambda r: bool(r["pitchCore"] and r["acoustic"]["stemBoth"])),
        ("pitchCore+persistent3p", lambda r: bool(r["pitchCore"] and r["acoustic"]["persistent3p"])),
        ("pitchCore+strictSweep", lambda r: bool(r["pitchCore"] and r["acoustic"]["strictSweep"])),
        ("pitchCore+tightGrid", lambda r: bool(r["pitchCore"] and r["acoustic"]["tightGrid"])),
        ("pitchCore+acousticMulti", lambda r: bool(r["pitchCore"] and r["acoustic"]["multiEvidence"])),
        ("pitchCore+acousticStrong", lambda r: bool(r["pitchCore"] and r["acoustic"]["strong"])),
        ("pitchCore+phraseAny", lambda r: bool(r["pitchCore"] and r["phrase"]["present"])),
        ("pitchCore+phraseExact", lambda r: bool(r["pitchCore"] and r["phrase"]["exact"])),
        ("pitchCore+phraseStrong", lambda r: bool(r["pitchCore"] and r["phrase"]["strong"])),
        ("pitchCore+acousticMulti+phraseAny", lambda r: bool(r["pitchCore"] and r["acoustic"]["multiEvidence"] and r["phrase"]["present"])),
        ("pitchCore+acousticMulti+phraseStrong", lambda r: bool(r["pitchCore"] and r["acoustic"]["multiEvidence"] and r["phrase"]["strong"])),
        ("pitchCore+acousticStrong+phraseAny", lambda r: bool(r["pitchCore"] and r["acoustic"]["strong"] and r["phrase"]["present"])),
        ("pitchCore+acousticStrong+phraseStrong", lambda r: bool(r["pitchCore"] and r["acoustic"]["strong"] and r["phrase"]["strong"])),
    ]

    normal_fn = lambda m: m % FOLD_COUNT
    section_fn = lambda m: contiguous_fold(m, lo, hi)
    shifted_fn = lambda m: shifted_window_fold(m, lo, hi)

    results: list[dict[str, Any]] = []
    for name, predicate in rules:
        chosen = [r for r in rows if predicate(r)]
        full = selected_stats(chosen)
        normal_parts = partition_stats(rows, predicate, normal_fn)
        section_parts = partition_stats(rows, predicate, section_fn)
        shifted_parts = partition_stats(rows, predicate, shifted_fn)
        normal = scheme_summary(normal_parts, base_precision)
        section = scheme_summary(section_parts, base_precision)
        shifted = scheme_summary(shifted_parts, base_precision)

        diagnostic_stable = (
            int(full["selected"]) >= 4
            and int(full["recoverTrue"]) >= 2
            and float(full["precision"]) >= max(35.0, base_precision + 5.0)
            and int(normal["supportedFolds"]) >= 3
            and int(section["supportedFolds"]) >= 3
            and int(shifted["supportedFolds"]) >= 3
            and sum([
                int(normal["precisionLiftFolds"]) >= 3,
                int(section["precisionLiftFolds"]) >= 3,
                int(shifted["precisionLiftFolds"]) >= 3,
            ]) >= 2
        )

        results.append({
            "rule": name,
            "fullData": full,
            "normal": normal,
            "section": section,
            "shiftedWindow": shifted,
            "normalFolds": normal_parts,
            "sectionFolds": section_parts,
            "shiftedWindowFolds": shifted_parts,
            "stableDiagnostic": diagnostic_stable,
        })

    results.sort(key=lambda r: (
        not bool(r["stableDiagnostic"]),
        -float(r["fullData"]["pitchF1"]),
        -float(r["fullData"]["precision"]),
        -int(r["fullData"]["recoverTrue"]),
        int(r["fullData"]["recoverFalse"]),
    ))

    after = sha256(prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during multi-family agreement diagnostic")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-multifamily-agreement-diagnostic",
        "frozenChampionPitchF1": EXPECTED_F1,
        "frozenChampionMatchedMissingExtra": list(EXPECTED),
        "residualRows": len(rows),
        "residualTrue": residual_true,
        "residualFalse": residual_false,
        "residualBasePrecision": round(base_precision, 2),
        "stablePitchCoreSignatureCount": len(stable_pitch_signatures),
        "stablePitchCoreSignatures": sorted(stable_pitch_signatures),
        "rules": results,
        "stableDiagnosticRules": [r for r in results if bool(r["stableDiagnostic"])],
        "candidateRows": rows,
        "note": "Diagnostic only. Stable pitch-core signatures were discovered on full data; no rule is promotion-eligible. Any promising agreement rule must be relearned inside nested training folds before held-out evaluation.",
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "stableDiagnosticRuleCount": len(output["stableDiagnosticRules"]),
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 MULTI-FAMILY AGREEMENT DIAGNOSTIC V1 COMPLETE")
    print("Passed: True")
    print("Frozen champion:", EXPECTED_F1, EXPECTED)
    print("Residual base precision:", round(base_precision, 2))
    print("Stable pitch-core signatures:", len(stable_pitch_signatures))
    print("Agreement rules evaluated:", len(results))
    for row in results:
        print("RULE", row["rule"], "full=", row["fullData"], "stableDiagnostic=", row["stableDiagnostic"])
        print("  normal=", row["normal"])
        print("  section=", row["section"])
        print("  shifted=", row["shiftedWindow"])
    print("Stable diagnostic rules:", len(output["stableDiagnosticRules"]))
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
