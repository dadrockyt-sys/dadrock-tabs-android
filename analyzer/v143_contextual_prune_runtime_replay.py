#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import v143_contextual_prune_runtime as runtime
from v143_reserve_contextual_prune_predict_partial_tail import (
    merge_reference_free_context_partial_tail,
)


ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"

DEV_CONTEXTUAL_PATH = CAL / "contextual-prune-17-96-frozen-events.json"
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


def main() -> None:
    freeze_manifest = load_json(FREEZE_MANIFEST_PATH)
    prediction_manifest = load_json(PREDICTION_MANIFEST_PATH)

    if freeze_manifest.get("predictionsFrozenBeforeReserveGrading") is not True:
        raise RuntimeError("Development freeze is not sealed")
    if freeze_manifest.get("productionModified") is not False:
        raise RuntimeError("Development freeze marks production modified")

    freeze_fingerprints = freeze_manifest.get("fingerprints", {})
    if sha256(runtime.CONTEXTUAL_MODEL_PATH) != freeze_fingerprints.get("frozenModelSha256"):
        raise RuntimeError("Frozen contextual model fingerprint changed")
    if sha256(DEV_CONTEXTUAL_PATH) != freeze_fingerprints.get("frozenDevelopmentEventsSha256"):
        raise RuntimeError("Frozen development contextual-event fingerprint changed")

    invariants = prediction_manifest.get("invariants", {})
    if invariants.get("reserveCacheReferenceFree") is not True:
        raise RuntimeError("Reserve prediction manifest lost reference-free cache invariant")
    if invariants.get("professionalReferenceUsedForPrediction") is not False:
        raise RuntimeError("Reserve prediction manifest claims professional-reference use")
    if invariants.get("candidateAddsEvents") is not False:
        raise RuntimeError("Reserve prediction manifest claims contextual additions")
    if invariants.get("candidateRelocatesEvents") is not False:
        raise RuntimeError("Reserve prediction manifest claims contextual relocation")

    # Exact reserve runtime replay is the promotion gate. It uses only the same
    # sealed reference-free 81-113 carrier used before the one-shot reserve grade.
    # The original 17-32 fresh cache was not committed to GitHub, so 17-96 is
    # verified here by its frozen fingerprints rather than reconstructed from an
    # incomplete checkout. This does not weaken the reserve runtime equivalence test.
    reserve_rows, reserve_grid = merge_reference_free_context_partial_tail()
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

    if len(frozen_reserve_base) != 180:
        raise RuntimeError(f"Frozen reserve base count changed: {len(frozen_reserve_base)}")
    if len(frozen_reserve_candidate) != 153:
        raise RuntimeError(
            f"Frozen reserve contextual count changed: {len(frozen_reserve_candidate)}"
        )
    if set(reserve_result.base_events) != frozen_reserve_base:
        missing = sorted(frozen_reserve_base - set(reserve_result.base_events))
        added = sorted(set(reserve_result.base_events) - frozen_reserve_base)
        raise RuntimeError(
            "Reserve base runtime replay mismatch: "
            f"missing={missing[:12]} added={added[:12]}"
        )
    if set(reserve_result.candidate_events) != frozen_reserve_candidate:
        missing = sorted(frozen_reserve_candidate - set(reserve_result.candidate_events))
        added = sorted(set(reserve_result.candidate_events) - frozen_reserve_candidate)
        raise RuntimeError(
            "Reserve contextual runtime replay mismatch: "
            f"missing={missing[:12]} added={added[:12]}"
        )

    fingerprints = prediction_manifest.get("fingerprints", {})
    base_sha = sha256(RESERVE_BASE_PATH)
    candidate_sha = sha256(RESERVE_CONTEXTUAL_PATH)
    if base_sha != fingerprints.get("frozenBaseReserveEventsSha256"):
        raise RuntimeError("Frozen reserve base fingerprint changed")
    if candidate_sha != fingerprints.get("frozenContextualReserveEventsSha256"):
        raise RuntimeError("Frozen reserve contextual fingerprint changed")

    dev_frozen = extract_events(load_json(DEV_CONTEXTUAL_PATH), set(range(17, 97)))
    if len(dev_frozen) != 651:
        raise RuntimeError(f"Frozen development contextual count changed: {len(dev_frozen)}")

    report = {
        "schemaVersion": 2,
        "gate": "v143-contextual-prune-reference-free-reserve-runtime-replay",
        "development": {
            "measures": "17-96",
            "frozenCandidateEventCount": len(dev_frozen),
            "frozenCandidateSha256": sha256(DEV_CONTEXTUAL_PATH),
            "frozenCandidateFingerprintMatched": True,
            "runtimeReplay": "not-reconstructed-in-github-actions",
            "reason": "fresh-verse1-reference-free-cache.json used by the historical 17-96 research replay was never committed; refusing to fabricate or substitute that input",
        },
        "reserve": {
            "measures": "97-113",
            "contextMeasures": "81-113",
            "baseEventCount": len(reserve_result.base_events),
            "candidateEventCount": len(reserve_result.candidate_events),
            "prunedEventCount": len(reserve_result.pruned_events),
            "exactBaseReplay": True,
            "exactCandidateReplay": True,
            "frozenBaseSha256": base_sha,
            "frozenCandidateSha256": candidate_sha,
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
            "developmentFrozenArtifactModified": False,
            "productionModified": False,
        },
        "gatePassed": True,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("=== V143 CONTEXTUAL PRUNE RUNTIME REPLAY ===")
    print("DEV_FROZEN_CONTEXTUAL", len(dev_frozen))
    print("DEV_FINGERPRINT_MATCHED", True)
    print("RESERVE_BASE", len(reserve_result.base_events))
    print("RESERVE_CONTEXTUAL", len(reserve_result.candidate_events))
    print("RESERVE_PRUNED", len(reserve_result.pruned_events))
    print("EXACT_RESERVE_BASE_REPLAY", True)
    print("EXACT_RESERVE_CONTEXTUAL_REPLAY", True)
    print("PROFESSIONAL_REFERENCE_OPENED", False)
    print("PRODUCTION_MODIFIED", False)
    print(f"WROTE={REPORT_PATH}")


if __name__ == "__main__":
    main()
