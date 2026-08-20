#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import v143_correlation_safe_fixed_count_reranker_freeze as freeze
import v143_contextual_prune_runtime as runtime
from v143_reserve_contextual_prune_predict_partial_tail import (
    merge_reference_free_context_partial_tail,
)


ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"

DEV_BASE_PATH = CAL / "fresh-17-96-base027-runtime-replay.json"
DEV_CONTEXTUAL_FROZEN_PATH = CAL / "contextual-prune-17-96-frozen-events.json"
# The development freeze script writes the canonical candidate under this name.
DEV_CONTEXTUAL_FALLBACK_PATH = CAL / "contextual-prune-17-96-frozen-events.json"
RESERVE_BASE_PATH = CAL / "reserve-97-113-base027-frozen-events.json"
RESERVE_CONTEXTUAL_PATH = CAL / "reserve-97-113-contextual-prune-frozen-events.json"
FREEZE_MANIFEST_PATH = CAL / "contextual-prune-freeze-manifest.json"
PREDICTION_MANIFEST_PATH = CAL / "reserve-97-113-contextual-prune-prediction-manifest.json"
REPORT_PATH = CAL / "contextual-prune-runtime-replay-report.json"


def load_json(path: Path) -> Any:
    if not path.exists() or path.stat().st_size <= 0:
        raise RuntimeError(f"Missing required replay artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_events(payload: Any, allowed: set[int]) -> set[tuple[int, int]]:
    found: set[tuple[int, int]] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if "measure" in value and ("quantizedStep" in value or "step" in value):
                try:
                    measure = int(value["measure"])
                    step = int(value.get("quantizedStep", value.get("step")))
                except (TypeError, ValueError):
                    measure = -1
                    step = -1
                if measure in allowed and 0 <= step < 16:
                    found.add((measure, step))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(payload)
    return found


def merge_reserve_context() -> tuple[dict[int, list[dict[str, Any]]], dict[tuple[int, int], float]]:
    return merge_reference_free_context_partial_tail()


def canonical_dev_candidate_path() -> Path:
    # Keep the lookup explicit and reference-free. The freeze currently uses this
    # canonical artifact name; the fallback variable makes failure messaging clear.
    candidates = [
        CAL / "contextual-prune-17-96-frozen-events.json",
        CAL / "contextual-prune-frozen-events.json",
    ]
    for path in candidates:
        if path.exists() and path.stat().st_size > 0:
            return path
    raise RuntimeError(
        "Missing contextual-prune development frozen events; checked: "
        + ", ".join(str(path) for path in candidates)
    )


def main() -> None:
    freeze_manifest = load_json(FREEZE_MANIFEST_PATH)
    prediction_manifest = load_json(PREDICTION_MANIFEST_PATH)

    if freeze_manifest.get("predictionsFrozenBeforeReserveGrading") is not True:
        raise RuntimeError("Development freeze is not sealed")
    if freeze_manifest.get("productionModified") is not False:
        raise RuntimeError("Development freeze marks production modified")
    if prediction_manifest.get("invariants", {}).get("reserveCacheReferenceFree") is not True:
        raise RuntimeError("Reserve prediction manifest lost reference-free cache invariant")
    if prediction_manifest.get("invariants", {}).get("professionalReferenceUsedForPrediction") is not False:
        raise RuntimeError("Reserve prediction manifest claims reference use")

    # Development 17-96: exact replay from the five reference-free caches.
    dev_rows, dev_grid = freeze._merge_fresh_caches()
    dev_result = runtime.run_contextual_prune(
        dev_rows,
        dev_grid,
        set(range(17, 97)),
        context_measures=set(range(17, 97)),
    )
    if len(dev_result.base_events) != 765:
        raise RuntimeError(f"Development runtime base count changed: {len(dev_result.base_events)}")
    if len(dev_result.candidate_events) != 651:
        raise RuntimeError(
            f"Development runtime contextual count changed: {len(dev_result.candidate_events)}"
        )

    dev_frozen_path = canonical_dev_candidate_path()
    dev_frozen = extract_events(load_json(dev_frozen_path), set(range(17, 97)))
    if dev_frozen != set(dev_result.candidate_events):
        missing = sorted(dev_frozen - set(dev_result.candidate_events))
        added = sorted(set(dev_result.candidate_events) - dev_frozen)
        raise RuntimeError(
            "Development contextual runtime replay mismatch: "
            f"frozen={len(dev_frozen)} runtime={len(dev_result.candidate_events)} "
            f"missing={missing[:12]} added={added[:12]}"
        )

    # Reserve 97-113: exact replay from sealed reference-free section-5 + reserve caches.
    reserve_rows, reserve_grid = merge_reserve_context()
    reserve_result = runtime.run_contextual_prune(
        reserve_rows,
        reserve_grid,
        set(range(97, 114)),
        context_measures=set(range(81, 114)),
    )
    frozen_reserve_base = extract_events(load_json(RESERVE_BASE_PATH), set(range(97, 114)))
    frozen_reserve_candidate = extract_events(
        load_json(RESERVE_CONTEXTUAL_PATH), set(range(97, 114))
    )
    if set(reserve_result.base_events) != frozen_reserve_base:
        raise RuntimeError("Reserve base runtime replay does not match frozen base predictions")
    if set(reserve_result.candidate_events) != frozen_reserve_candidate:
        missing = sorted(frozen_reserve_candidate - set(reserve_result.candidate_events))
        added = sorted(set(reserve_result.candidate_events) - frozen_reserve_candidate)
        raise RuntimeError(
            "Reserve contextual runtime replay mismatch: "
            f"missing={missing[:12]} added={added[:12]}"
        )

    fingerprints = prediction_manifest.get("fingerprints", {})
    if sha256(RESERVE_BASE_PATH) != fingerprints.get("frozenBaseReserveEventsSha256"):
        raise RuntimeError("Frozen reserve base fingerprint changed")
    if sha256(RESERVE_CONTEXTUAL_PATH) != fingerprints.get("frozenContextualReserveEventsSha256"):
        raise RuntimeError("Frozen reserve contextual fingerprint changed")

    report = {
        "schemaVersion": 1,
        "gate": "v143-contextual-prune-reference-free-runtime-replay",
        "development": {
            "measures": "17-96",
            "baseEventCount": len(dev_result.base_events),
            "candidateEventCount": len(dev_result.candidate_events),
            "frozenCandidatePath": str(dev_frozen_path.relative_to(ROOT)),
            "exactCandidateReplay": True,
        },
        "reserve": {
            "measures": "97-113",
            "contextMeasures": "81-113",
            "baseEventCount": len(reserve_result.base_events),
            "candidateEventCount": len(reserve_result.candidate_events),
            "exactBaseReplay": True,
            "exactCandidateReplay": True,
            "frozenBaseSha256": sha256(RESERVE_BASE_PATH),
            "frozenCandidateSha256": sha256(RESERVE_CONTEXTUAL_PATH),
        },
        "runtime": {
            "baseThreshold": reserve_result.base_threshold,
            "pruneFraction": reserve_result.prune_fraction,
            "candidateAddsEvents": False,
            "candidateRelocatesEvents": False,
            "professionalReferenceRequiredAtRuntime": False,
        },
        "invariants": {
            "professionalReferenceOpenedByReplay": False,
            "reserveLabelsUsedByReplay": False,
            "frozenPredictionsModified": False,
            "productionModified": False,
        },
        "gatePassed": True,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("=== V143 CONTEXTUAL PRUNE RUNTIME REPLAY ===")
    print("DEV_BASE", len(dev_result.base_events))
    print("DEV_CONTEXTUAL", len(dev_result.candidate_events))
    print("RESERVE_BASE", len(reserve_result.base_events))
    print("RESERVE_CONTEXTUAL", len(reserve_result.candidate_events))
    print("EXACT_DEV_REPLAY", True)
    print("EXACT_RESERVE_REPLAY", True)
    print("PROFESSIONAL_REFERENCE_OPENED", False)
    print("PRODUCTION_MODIFIED", False)
    print(f"WROTE={REPORT_PATH}")


if __name__ == "__main__":
    main()
