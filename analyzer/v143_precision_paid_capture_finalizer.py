from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

EXPECTED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_POLICY = "envelope-balanced-secondary-v2"
EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"


class PaidCaptureFinalizationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PaidCaptureFinalizationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finalized_lock(
    *,
    product: Mapping[str, Any],
    compare: Mapping[str, Any],
    validation: Mapping[str, Any],
    lock: Mapping[str, Any],
    run_id: int,
    trigger_sha: str,
    product_sha256: str,
    compare_sha256: str,
    validation_sha256: str,
) -> dict[str, Any]:
    trace = product.get("preFreezeTrace") or {}
    candidate = product.get("candidate") or {}
    policy = product.get("precisionPolicy") or {}
    replay = product.get("precisionReplayEvidence") or {}
    compare_source = compare.get("source") or {}
    comparison = compare.get("comparison") or {}
    voicing = compare.get("voicingValidation") or {}

    _require(lock.get("captureState") == "reserved_before_modal", "capture lock was not reserved before Modal")
    _require(int(lock.get("runId") or -1) == int(run_id), "capture lock runId mismatch")
    _require(str(lock.get("triggerSha") or "") == str(trigger_sha), "capture lock triggerSha mismatch")
    _require(lock.get("automaticRetryAllowed") is False, "capture lock permits automatic retry")
    _require(lock.get("singlePaidCaptureConsumed") is False, "paid capture was already marked consumed")
    _require(str(lock.get("approvedAudioSha256") or "") == EXPECTED_AUDIO_SHA256, "reserved audio identity mismatch")
    _require(str(lock.get("protectedPipelineBlob") or "") == EXPECTED_PROTECTED_BLOB, "reserved protected-pipeline blob mismatch")

    _require(trace.get("passed") is True, "cannot finalize a failed candidate trace")
    for field in (
        "attackPolicyReplayReady",
        "sourceViewEvidenceReady",
        "precisionStrengthRecomputeReady",
        "zeroValuePreservationReady",
        "protectedPipelineUnchanged",
    ):
        _require(trace.get(field) is True, f"candidate trace missing green {field}")
    _require(trace.get("productionModified") is False, "candidate trace indicates production modification")

    _require(candidate.get("sourceSha256") == EXPECTED_AUDIO_SHA256, "candidate source audio identity mismatch")
    _require(candidate.get("professionalReferenceUsed") is False, "candidate indicates professional reference use")
    _require(candidate.get("productionModified") is False, "candidate indicates production modification")
    _require(policy.get("name") == EXPECTED_POLICY, "precision policy mismatch")
    _require(policy.get("professionalReferenceUsed") is False, "precision policy indicates professional reference use")

    for field in (
        "referenceFree",
        "fixedRetainedAttackPitchReplayReady",
        "attackPolicyReplayReady",
        "sourceViewEvidenceReady",
        "precisionStrengthRecomputeReady",
        "zeroValuePreservationReady",
    ):
        _require(replay.get(field) is True, f"replay missing green {field}")
    _require(replay.get("professionalReferenceUsed") is False, "replay indicates professional reference use")
    _require(replay.get("productionModified") is False, "replay indicates production modification")

    _require(validation.get("passed") is True, "replay artifact validation failed")
    for field in (
        "baselineAttackReplayMatches",
        "fixedRetainedAttackPitchReplayReady",
        "attackPolicyReplayReady",
        "sourceViewEvidenceMatches",
        "precisionStrengthRecomputeMatches",
        "zeroValuePreservationMatches",
    ):
        _require(validation.get(field) is True, f"replay artifact validation missing green {field}")
    _require(validation.get("referenceFree") is True, "validation is not reference-free")
    _require(validation.get("professionalReferenceUsed") is False, "validation indicates professional reference use")
    _require(validation.get("productionModified") is False, "validation indicates production modification")
    _require(validation.get("eventsSha256") == trace.get("eventsSha256"), "validation events hash mismatch")
    _require(validation.get("replayEvidenceSha256") == trace.get("replayEvidenceSha256"), "validation replay hash mismatch")

    _require(compare.get("referenceFree") is True, "replay comparison is not reference-free")
    _require(compare.get("productionModified") is False, "replay comparison indicates production modification")
    _require(compare_source.get("professionalReferenceUsed") is False, "replay comparison indicates professional reference use")
    _require(compare_source.get("newInferenceUsed") is False, "replay comparison indicates new inference use")
    _require(compare_source.get("primaryRecomputeMatches") is True, "primary recomputation mismatch")
    _require(compare_source.get("storedV2ReplayMatches") is True, "stored v2 replay mismatch")
    _require("primaryRecomputeMismatchAttackCount" in comparison, "primary recompute mismatch counter is missing")
    _require("v2ReplayMismatchAttackCount" in comparison, "stored v2 replay mismatch counter is missing")
    _require(int(comparison["primaryRecomputeMismatchAttackCount"]) == 0, "primary recompute mismatch count is non-zero")
    _require(int(comparison["v2ReplayMismatchAttackCount"]) == 0, "stored v2 replay mismatch count is non-zero")

    for field in (
        "passed",
        "stringFretReplayMatches",
        "primaryPreservationMatches",
        "gridTimingReplayMatches",
        "physicalOnsetReplayMatches",
    ):
        _require(voicing.get(field) is True, f"deterministic voicing/timing validation missing green {field}")
    _require(voicing.get("referenceFree") is True, "voicing/timing validation is not reference-free")
    _require(voicing.get("newInferenceUsed") is False, "voicing/timing validation indicates new inference")
    _require(voicing.get("professionalReferenceUsed") is False, "voicing/timing validation indicates professional reference use")
    _require(voicing.get("productionModified") is False, "voicing/timing validation indicates production modification")

    finalized = copy.deepcopy(dict(lock))
    finalized.update(
        {
            "captureState": "completed",
            "singlePaidCaptureConsumed": True,
            "automaticRetryAllowed": False,
            "approvedAudioSha256": EXPECTED_AUDIO_SHA256,
            "protectedPipelineBlob": EXPECTED_PROTECTED_BLOB,
            "policy": EXPECTED_POLICY,
            "eventsSha256": str(trace["eventsSha256"]),
            "replayEvidenceSha256": str(trace["replayEvidenceSha256"]),
            "replayInputAttackCount": int(validation["inputAttackCount"]),
            "replayEligibleAttackCount": int(validation["eligibleAttackCount"]),
            "replayAttackCount": int(validation["retainedAttackCount"]),
            "replayEligiblePitchHypothesisCount": int(validation["eligiblePitchHypothesisCount"]),
            "replayOriginalPitchHypothesisCount": int(validation["originalPitchHypothesisCount"]),
            "attackPolicyReplayReady": True,
            "sourceViewEvidenceReady": True,
            "precisionStrengthRecomputeReady": True,
            "zeroValuePreservationReady": True,
            "baselineAttackReplayMatches": True,
            "sourceViewEvidenceMatches": True,
            "precisionStrengthRecomputeMatches": True,
            "zeroValuePreservationMatches": True,
            "storedV2ReplayMatches": True,
            "primaryRecomputeMatches": True,
            "v2ReplayMismatchAttackCount": 0,
            "primaryRecomputeMismatchAttackCount": 0,
            "deterministicVoicingReplayMatches": True,
            "stringFretReplayMatches": True,
            "primaryPreservationMatches": True,
            "gridTimingReplayMatches": True,
            "physicalOnsetReplayMatches": True,
            "candidateProductSha256": str(product_sha256),
            "replayPolicyCompareSha256": str(compare_sha256),
            "replayArtifactValidationSha256": str(validation_sha256),
            "professionalReferenceUsed": False,
            "newInferenceUsed": False,
            "productionModified": False,
        }
    )
    return finalized


def finalize_paths(
    *,
    product_path: Path,
    compare_path: Path,
    validation_path: Path,
    lock_path: Path,
    run_id: int,
    trigger_sha: str,
) -> dict[str, Any]:
    product = json.loads(product_path.read_text())
    compare = json.loads(compare_path.read_text())
    validation = json.loads(validation_path.read_text())
    lock = json.loads(lock_path.read_text())
    finalized = _finalized_lock(
        product=product,
        compare=compare,
        validation=validation,
        lock=lock,
        run_id=run_id,
        trigger_sha=trigger_sha,
        product_sha256=_sha256(product_path),
        compare_sha256=_sha256(compare_path),
        validation_sha256=_sha256(validation_path),
    )
    lock_path.write_text(json.dumps(finalized, indent=2, sort_keys=True) + "\n")
    return finalized


def _self_test() -> None:
    trace = {
        "passed": True,
        "eventsSha256": "events",
        "replayEvidenceSha256": "replay",
        "attackPolicyReplayReady": True,
        "sourceViewEvidenceReady": True,
        "precisionStrengthRecomputeReady": True,
        "zeroValuePreservationReady": True,
        "protectedPipelineUnchanged": True,
        "productionModified": False,
    }
    product = {
        "preFreezeTrace": trace,
        "candidate": {"sourceSha256": EXPECTED_AUDIO_SHA256, "professionalReferenceUsed": False, "productionModified": False},
        "precisionPolicy": {"name": EXPECTED_POLICY, "professionalReferenceUsed": False},
        "precisionReplayEvidence": {
            "referenceFree": True,
            "fixedRetainedAttackPitchReplayReady": True,
            "attackPolicyReplayReady": True,
            "sourceViewEvidenceReady": True,
            "precisionStrengthRecomputeReady": True,
            "zeroValuePreservationReady": True,
            "professionalReferenceUsed": False,
            "productionModified": False,
        },
    }
    validation = {
        "passed": True,
        "baselineAttackReplayMatches": True,
        "fixedRetainedAttackPitchReplayReady": True,
        "attackPolicyReplayReady": True,
        "sourceViewEvidenceMatches": True,
        "precisionStrengthRecomputeMatches": True,
        "zeroValuePreservationMatches": True,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "productionModified": False,
        "eventsSha256": "events",
        "replayEvidenceSha256": "replay",
        "inputAttackCount": 3,
        "eligibleAttackCount": 3,
        "retainedAttackCount": 2,
        "eligiblePitchHypothesisCount": 5,
        "originalPitchHypothesisCount": 4,
    }
    compare = {
        "referenceFree": True,
        "productionModified": False,
        "source": {
            "professionalReferenceUsed": False,
            "newInferenceUsed": False,
            "primaryRecomputeMatches": True,
            "storedV2ReplayMatches": True,
        },
        "comparison": {"primaryRecomputeMismatchAttackCount": 0, "v2ReplayMismatchAttackCount": 0},
        "voicingValidation": {
            "passed": True,
            "stringFretReplayMatches": True,
            "primaryPreservationMatches": True,
            "gridTimingReplayMatches": True,
            "physicalOnsetReplayMatches": True,
            "referenceFree": True,
            "newInferenceUsed": False,
            "professionalReferenceUsed": False,
            "productionModified": False,
        },
    }
    lock = {
        "captureState": "reserved_before_modal",
        "runId": 123,
        "triggerSha": "abc",
        "automaticRetryAllowed": False,
        "singlePaidCaptureConsumed": False,
        "approvedAudioSha256": EXPECTED_AUDIO_SHA256,
        "protectedPipelineBlob": EXPECTED_PROTECTED_BLOB,
    }
    finalized = _finalized_lock(
        product=product,
        compare=compare,
        validation=validation,
        lock=lock,
        run_id=123,
        trigger_sha="abc",
        product_sha256="product",
        compare_sha256="compare",
        validation_sha256="validation",
    )
    assert finalized["captureState"] == "completed"
    assert finalized["singlePaidCaptureConsumed"] is True
    assert finalized["sourceViewEvidenceMatches"] is True
    assert finalized["storedV2ReplayMatches"] is True
    assert finalized["stringFretReplayMatches"] is True
    assert finalized["gridTimingReplayMatches"] is True

    broken = copy.deepcopy(compare)
    broken["voicingValidation"]["physicalOnsetReplayMatches"] = False
    try:
        _finalized_lock(
            product=product,
            compare=broken,
            validation=validation,
            lock=lock,
            run_id=123,
            trigger_sha="abc",
            product_sha256="product",
            compare_sha256="compare",
            validation_sha256="validation",
        )
    except PaidCaptureFinalizationError:
        pass
    else:
        raise AssertionError("paid finalizer accepted corrupted timing replay")

    missing_counter = copy.deepcopy(compare)
    del missing_counter["comparison"]["v2ReplayMismatchAttackCount"]
    try:
        _finalized_lock(
            product=product,
            compare=missing_counter,
            validation=validation,
            lock=lock,
            run_id=123,
            trigger_sha="abc",
            product_sha256="product",
            compare_sha256="compare",
            validation_sha256="validation",
        )
    except PaidCaptureFinalizationError:
        pass
    else:
        raise AssertionError("paid finalizer accepted missing replay mismatch counter")

    print("PASS v143 paid precision capture strict final-lock contract")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product")
    parser.add_argument("--compare")
    parser.add_argument("--validation")
    parser.add_argument("--lock")
    parser.add_argument("--run-id", type=int)
    parser.add_argument("--trigger-sha")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return
    if not all((args.product, args.compare, args.validation, args.lock, args.run_id is not None, args.trigger_sha)):
        raise SystemExit("product/compare/validation/lock/run-id/trigger-sha are required")
    finalized = finalize_paths(
        product_path=Path(args.product),
        compare_path=Path(args.compare),
        validation_path=Path(args.validation),
        lock_path=Path(args.lock),
        run_id=int(args.run_id),
        trigger_sha=str(args.trigger_sha),
    )
    print(json.dumps({"captureState": finalized["captureState"], "strictFinalLock": True}, sort_keys=True))


if __name__ == "__main__":
    main()
