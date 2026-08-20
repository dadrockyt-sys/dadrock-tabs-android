#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ANALYZER = ROOT / "analyzer"
if str(ANALYZER) not in sys.path:
    sys.path.insert(0, str(ANALYZER))

import v143_correlation_safe_fixed_count_reranker_freeze as freeze

CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"
CANDIDATE_PATH = CAL / "fresh-17-96-correlation-safe-fixed-count-reranker-frozen-events.json"
MANIFEST_PATH = CAL / "fresh-17-96-correlation-safe-fixed-count-reranker-freeze-manifest.json"
REFERENCE_PATH = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = ROOT / "debug" / "v143-grading" / "current-reference-grade.json"

TARGET_MEASURES = set(range(17, 97))
CURRENT_REFERENCE_COUNT = 431
CURRENT_BAND_REFERENCE_COUNTS = {
    (17, 32): 115,
    (33, 48): 93,
    (49, 64): 107,
    (65, 80): 51,
    (81, 96): 65,
}
OLD_STALE_BAND_REFERENCE_COUNTS = {
    (17, 32): 115,
    (33, 48): 93,
    (49, 64): 110,
    (65, 80): 50,
    (81, 96): 65,
}


def load_json(path: Path) -> Any:
    if not path.exists() or path.stat().st_size <= 0:
        raise RuntimeError(f"Missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_reference_blind_safe(path: Path) -> tuple[set[tuple[int, int]], bool]:
    """Read only measure headers/events through 96; stop before any 97 event payload."""
    ref: set[tuple[int, int]] = set()
    current_measure: int | None = None
    hit_reserve_boundary = False

    measure_re = re.compile(r'"measureNumber"\s*:\s*(\d+)')
    step_re = re.compile(r'"quantizedStep"\s*:\s*(\d+)')

    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            mm = measure_re.search(line)
            if mm:
                current_measure = int(mm.group(1))
                if current_measure >= 97:
                    hit_reserve_boundary = True
                    break

            sm = step_re.search(line)
            if sm and current_measure is not None and 17 <= current_measure <= 96:
                ref.add((current_measure, int(sm.group(1))))

    return ref, hit_reserve_boundary


def extract_candidate(payload: Any) -> set[tuple[int, int]]:
    events = payload.get("events") if isinstance(payload, dict) else None
    if not isinstance(events, list):
        raise RuntimeError("Frozen candidate payload has no events list")
    found: set[tuple[int, int]] = set()
    for event in events:
        if not isinstance(event, dict):
            continue
        measure = int(event["measure"])
        step = int(event["step"])
        if measure in TARGET_MEASURES and 0 <= step < 16:
            found.add((measure, step))
    return found


def metrics(pred: set[tuple[int, int]], ref: set[tuple[int, int]]) -> dict[str, Any]:
    tp = len(pred & ref)
    fp = len(pred - ref)
    fn = len(ref - pred)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "predicted": len(pred),
        "reference": len(ref),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
    }


def subset(values: set[tuple[int, int]], lo: int, hi: int) -> set[tuple[int, int]]:
    return {key for key in values if lo <= key[0] <= hi}


def main() -> None:
    manifest = load_json(MANIFEST_PATH)
    candidate_payload = load_json(CANDIDATE_PATH)

    if manifest.get("predictionsFrozenBeforeGrading") is not True:
        raise RuntimeError("Freeze manifest does not assert predictionsFrozenBeforeGrading=true")
    if manifest.get("targetProfessionalReferenceOpened") is not False:
        raise RuntimeError("Freeze manifest says target professional reference was opened before freeze")
    if manifest.get("measures97To113Opened") is not False:
        raise RuntimeError("Freeze manifest says reserve measures 97-113 were opened before freeze")

    expected_candidate_sha = (
        manifest.get("fingerprints", {})
        .get("frozenPredictions", {})
        .get("sha256")
    )
    actual_candidate_sha = sha256(CANDIDATE_PATH)
    if expected_candidate_sha != actual_candidate_sha:
        raise RuntimeError(
            "Frozen candidate fingerprint mismatch: "
            f"manifest={expected_candidate_sha} actual={actual_candidate_sha}"
        )

    candidate = extract_candidate(candidate_payload)
    if len(candidate) != 765:
        raise RuntimeError(f"Frozen candidate count mismatch: {len(candidate)} != 765")

    reference, hit_reserve_boundary = parse_reference_blind_safe(REFERENCE_PATH)
    if not hit_reserve_boundary:
        raise RuntimeError("Did not encounter measure-97 boundary; refusing grade")
    if len(reference) != CURRENT_REFERENCE_COUNT:
        raise RuntimeError(
            f"Current committed reference count changed: {len(reference)} != {CURRENT_REFERENCE_COUNT}"
        )

    actual_band_counts = {
        f"{lo}-{hi}": len(subset(reference, lo, hi))
        for lo, hi in CURRENT_BAND_REFERENCE_COUNTS
    }
    expected_band_counts = {
        f"{lo}-{hi}": expected
        for (lo, hi), expected in CURRENT_BAND_REFERENCE_COUNTS.items()
    }
    if actual_band_counts != expected_band_counts:
        raise RuntimeError(
            f"Current committed reference band counts changed: {actual_band_counts} != {expected_band_counts}"
        )

    # Recompute the promoted base-0.27 predictions from the same frozen, reference-free
    # caches and model used when the fixed-count candidate was frozen. This avoids
    # comparing the candidate to stale TP/FP/FN constants from an older reference version.
    base_model = load_json(freeze.BASE_MODEL_PATH)
    if float(base_model.get("threshold", -1.0)) != 0.27:
        raise RuntimeError(f"Expected promoted base threshold 0.27, got {base_model.get('threshold')}")

    rows_by_measure, grid = freeze._merge_fresh_caches()
    base_scores, base_evidence = freeze._score_measures(
        rows_by_measure,
        grid,
        TARGET_MEASURES,
        base_model,
    )
    base = freeze._active_from_scores(
        base_scores,
        base_evidence,
        TARGET_MEASURES,
        float(base_model["threshold"]),
    )
    if len(base) != 765:
        raise RuntimeError(f"Replayed base-0.27 count mismatch: {len(base)} != 765")

    base_combined = metrics(base, reference)
    candidate_combined = metrics(candidate, reference)

    bands: dict[str, Any] = {}
    for lo, hi in CURRENT_BAND_REFERENCE_COUNTS:
        name = f"{lo}-{hi}"
        band_ref = subset(reference, lo, hi)
        bands[name] = {
            "referenceCount": len(band_ref),
            "oldStaleReferenceCount": OLD_STALE_BAND_REFERENCE_COUNTS[(lo, hi)],
            "referenceCountDeltaVsOld": len(band_ref) - OLD_STALE_BAND_REFERENCE_COUNTS[(lo, hi)],
            "base027": metrics(subset(base, lo, hi), band_ref),
            "fixedCountReranker": metrics(subset(candidate, lo, hi), band_ref),
        }

    result = {
        "schemaVersion": 1,
        "grade": "v143-current-committed-reference",
        "measureRange": "17-96",
        "referencePath": str(REFERENCE_PATH.relative_to(ROOT)),
        "referenceCount": len(reference),
        "reserveBoundaryEncountered": hit_reserve_boundary,
        "reservePayloadOpened": False,
        "referenceBandCounts": actual_band_counts,
        "oldStaleReferenceBandCounts": {
            f"{lo}-{hi}": value
            for (lo, hi), value in OLD_STALE_BAND_REFERENCE_COUNTS.items()
        },
        "referenceDriftVsOldBenchmark": {
            f"{lo}-{hi}": actual_band_counts[f"{lo}-{hi}"] - value
            for (lo, hi), value in OLD_STALE_BAND_REFERENCE_COUNTS.items()
        },
        "frozenCandidate": {
            "path": str(CANDIDATE_PATH.relative_to(ROOT)),
            "sha256": actual_candidate_sha,
            "count": len(candidate),
        },
        "base027": base_combined,
        "fixedCountReranker": candidate_combined,
        "deltaVsBase": {
            "tp": candidate_combined["tp"] - base_combined["tp"],
            "fp": candidate_combined["fp"] - base_combined["fp"],
            "fn": candidate_combined["fn"] - base_combined["fn"],
            "precision": round(candidate_combined["precision"] - base_combined["precision"], 6),
            "recall": round(candidate_combined["recall"] - base_combined["recall"], 6),
            "f1": round(candidate_combined["f1"] - base_combined["f1"], 6),
        },
        "bands": bands,
        "invariants": {
            "predictionsFrozenBeforeGrading": True,
            "candidateFingerprintMatchedFreezeManifest": True,
            "candidateCountPreserved": len(candidate) == len(base) == 765,
            "professionalReferenceUsedForBaseReplay": False,
            "measures97To113Opened": False,
            "productionModified": False,
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("=== V143 CURRENT-REFERENCE GRADE ===")
    print(f"REFERENCE={len(reference)} BASE={len(base)} CANDIDATE={len(candidate)}")
    print("REFERENCE_BANDS", actual_band_counts)
    print("BASE", base_combined)
    print("CANDIDATE", candidate_combined)
    print("DELTA", result["deltaVsBase"])
    print(f"WROTE={OUTPUT_PATH}")


if __name__ == "__main__":
    main()
