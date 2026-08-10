from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3676_pitch_register_interval_recovery_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-signature-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-signature-stability-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def family(sig: str) -> str:
    return sig.split("::", 1)[0]


def counts(rows: list[dict[str, Any]], sig: str) -> tuple[int, int]:
    true = false = 0
    for row in rows:
        if sig not in {str(s) for s in (row.get("signatures") or [])}:
            continue
        if str(row.get("label")) == "true":
            true += 1
        else:
            false += 1
    return true, false


def precision(true: int, false: int) -> float:
    total = true + false
    return 100.0 * true / total if total else 0.0


def contiguous_fold(measure: int, lo: int, hi: int) -> int:
    span = max(1, hi - lo + 1)
    return min(FOLD_COUNT - 1, int(FOLD_COUNT * (measure - lo) / span))


def shifted_window_fold(measure: int, lo: int, hi: int) -> int:
    """True shifted contiguous windows, not a modulo-fold relabeling."""
    span = max(1, hi - lo + 1)
    width = span / FOLD_COUNT
    shift = width / 2.0
    pos = ((measure - lo) + shift) % span
    return min(FOLD_COUNT - 1, int(pos / width))


def partition_stats(
    rows: list[dict[str, Any]],
    sig: str,
    fold_fn,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for fold in range(FOLD_COUNT):
        held = [r for r in rows if fold_fn(int(r["measure"])) == fold]
        t, f = counts(held, sig)
        out.append({
            "fold": fold,
            "true": t,
            "false": f,
            "support": t + f,
            "precision": round(precision(t, f), 2),
        })
    return out


def summarize_scheme(parts: list[dict[str, Any]]) -> dict[str, Any]:
    supported = [p for p in parts if int(p["support"]) > 0]
    positive = [p for p in supported if int(p["true"]) > int(p["false"])]
    useful = [p for p in supported if float(p["precision"]) >= 35.0 and int(p["true"]) > 0]
    return {
        "supportedFolds": len(supported),
        "positiveFolds": len(positive),
        "usefulFolds": len(useful),
        "minSupportedPrecision": round(min((float(p["precision"]) for p in supported), default=0.0), 2),
        "meanSupportedPrecision": round(sum(float(p["precision"]) for p in supported) / len(supported), 2) if supported else 0.0,
    }


def main() -> None:
    before = sha256(prof.recall.CANDIDATE_PATH)
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    rows = list(profile.get("candidateRows") or [])
    if not rows:
        raise RuntimeError("Pitch/register/interval profiler candidate rows are missing")
    if tuple(profile.get("championMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Profiler is not anchored to frozen 36.76 champion")

    measures = sorted({int(r["measure"]) for r in rows})
    lo, hi = min(measures), max(measures)

    signature_set: set[str] = set()
    for row in rows:
        signature_set.update(str(s) for s in (row.get("signatures") or []))

    residual_true = sum(str(r.get("label")) == "true" for r in rows)
    residual_false = len(rows) - residual_true
    base_precision = precision(residual_true, residual_false)

    normal_fn = lambda m: m % FOLD_COUNT
    section_fn = lambda m: contiguous_fold(m, lo, hi)
    shifted_fn = lambda m: shifted_window_fold(m, lo, hi)

    ranked: list[dict[str, Any]] = []
    for sig in sorted(signature_set):
        t, f = counts(rows, sig)
        total = t + f
        if total < 4 or t < 2:
            continue

        normal_parts = partition_stats(rows, sig, normal_fn)
        section_parts = partition_stats(rows, sig, section_fn)
        shifted_parts = partition_stats(rows, sig, shifted_fn)
        normal_summary = summarize_scheme(normal_parts)
        section_summary = summarize_scheme(section_parts)
        shifted_summary = summarize_scheme(shifted_parts)

        # Diagnostic only. This is deliberately stricter than full-data ranking.
        # A later nested benchmark must relearn any rule inside each training fold.
        agreement = sum([
            int(normal_summary["usefulFolds"]) >= 3,
            int(section_summary["usefulFolds"]) >= 3,
            int(shifted_summary["usefulFolds"]) >= 3,
        ])
        stable = (
            t >= 4
            and precision(t, f) >= max(35.0, base_precision + 5.0)
            and int(normal_summary["supportedFolds"]) >= 3
            and int(section_summary["supportedFolds"]) >= 3
            and int(shifted_summary["supportedFolds"]) >= 3
            and agreement >= 2
        )

        ranked.append({
            "signature": sig,
            "family": family(sig),
            "true": t,
            "false": f,
            "support": total,
            "precision": round(precision(t, f), 2),
            "liftVsResidualPctPoints": round(precision(t, f) - base_precision, 2),
            "agreementSchemes": agreement,
            "stableDiagnostic": stable,
            "normal": normal_summary,
            "section": section_summary,
            "shiftedWindow": shifted_summary,
            "normalFolds": normal_parts,
            "sectionFolds": section_parts,
            "shiftedWindowFolds": shifted_parts,
        })

    ranked.sort(
        key=lambda r: (
            not bool(r["stableDiagnostic"]),
            -int(r["agreementSchemes"]),
            -float(r["precision"]),
            -int(r["true"]),
            int(r["false"]),
        )
    )
    stable = [r for r in ranked if bool(r["stableDiagnostic"])]

    family_totals: dict[str, Counter[str]] = defaultdict(Counter)
    for row in ranked:
        fam = str(row["family"])
        family_totals[fam]["signatures"] += 1
        if bool(row["stableDiagnostic"]):
            family_totals[fam]["stable"] += 1
            family_totals[fam]["true"] += int(row["true"])
            family_totals[fam]["false"] += int(row["false"])

    family_summary = []
    for fam, c in family_totals.items():
        family_summary.append({
            "family": fam,
            "evaluatedSignatures": int(c["signatures"]),
            "stableSignatures": int(c["stable"]),
            "stableTrueSupport": int(c["true"]),
            "stableFalseSupport": int(c["false"]),
            "stableAggregatePrecision": round(precision(int(c["true"]), int(c["false"])), 2),
        })
    family_summary.sort(key=lambda r: (-int(r["stableSignatures"]), -float(r["stableAggregatePrecision"]), str(r["family"])))

    after = sha256(prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during signature stability profiling")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-pitch-register-interval-signature-stability-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "residualRows": len(rows),
        "residualTrue": residual_true,
        "residualFalse": residual_false,
        "residualBasePrecision": round(base_precision, 2),
        "evaluatedSignatureCount": len(ranked),
        "stableDiagnosticSignatureCount": len(stable),
        "familySummary": family_summary,
        "stableSignatures": stable,
        "rankedSignatures": ranked,
        "note": "Diagnostic only. Stable signatures are not promotion-eligible until nested training-fold validation passes.",
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
        "stableDiagnosticSignatureCount": len(stable),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PITCH REGISTER INTERVAL SIGNATURE STABILITY V1 COMPLETE")
    print("Passed: True")
    print("Frozen champion:", EXPECTED_F1, EXPECTED)
    print("Residual base precision:", round(base_precision, 2))
    print("Evaluated signatures:", len(ranked))
    print("Stable diagnostic signatures:", len(stable))
    print("Family summary:")
    for item in family_summary:
        print("FAMILY", item)
    print("Top stable signatures:")
    for item in stable[:25]:
        print("STABLE", {
            "signature": item["signature"],
            "family": item["family"],
            "true": item["true"],
            "false": item["false"],
            "precision": item["precision"],
            "agreementSchemes": item["agreementSchemes"],
            "normal": item["normal"],
            "section": item["section"],
            "shiftedWindow": item["shiftedWindow"],
        })
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
