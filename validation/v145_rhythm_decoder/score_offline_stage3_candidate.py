from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
V144_DIR = ROOT / "validation" / "v144_rhythm_calibration"
for entry in (HOLDOUT_DIR, V144_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from canonical import canonical_events, sha256_json  # noqa: E402
import score_rhythm_holdout as scorer  # noqa: E402
from score_selected_conjunction_candidate import score_full_candidate  # noqa: E402


SCHEMA_VERSION = 14504
CLASSIFICATION = "v145-rhythm-stage3-offline-calibration-score"
EVALUATION_ROLE = "calibration-benchmark-not-unseen-holdout"
EXPECTED_CANDIDATE_SCHEMA = 14503
EXPECTED_CANDIDATE_CLASSIFICATION = "v145-rhythm-stage3-offline-generated-only-candidate"
EXPECTED_CANDIDATE_EVENT_COUNT = 1209
EXPECTED_GENERATED_MEASURE_COUNT = 113
EXPECTED_GENERATED_MEASURE_SET = frozenset(range(1, EXPECTED_GENERATED_MEASURE_COUNT + 1))

ACCEPTED_MANIFEST_CLASSIFICATION = "v144-rhythm-selected-calibration-baseline"
ACCEPTED_MANIFEST_STATUS = "accepted-calibration-baseline-not-production"
ACCEPTED_NAME = "singleton-onset-replace-be9e9aa7a734e3cd"
ACCEPTED_EVENT_COUNT = 1144
ACCEPTED_EVENT_SHA256 = "4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881"
ACCEPTED_MEASURE_COUNT = 113
ACCEPTED_CRITICAL_MISMATCH_COUNT = 1712
ACCEPTED_METRICS = {
    "pitchContentF1": 0.35406698564593303,
    "pitchTimingTolerantF1": 0.06698564593301436,
    "stringFretTimingTolerantF1": 0.05454545454545454,
    "chordPitchSetTolerantF1": 0.0580511402902557,
    "exactVoicingTolerantF1": 0.0580511402902557,
    "measureCoverageRecall": 1.0,
    "pdfEventFidelity": 1.0,
}
EXPECTED_GOLD_SHA256 = "18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac"


ReadJson = Callable[[Path], Any]
ReadBytes = Callable[[Path], bytes]
PreReferenceFn = Callable[[Path], tuple[Mapping[str, Any], list[dict[str, Any]], Mapping[str, Any]]]
ValidateReferenceFn = Callable[[Any], Mapping[str, Any]]
ScoreFn = Callable[[Sequence[Mapping[str, Any]], Mapping[str, Any]], dict[str, Any]]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _candidate_only_validation(payload: Any) -> tuple[Mapping[str, Any], list[dict[str, Any]], str]:
    candidate = _require_mapping(payload, "Stage3 candidate")
    if candidate.get("schemaVersion") != EXPECTED_CANDIDATE_SCHEMA:
        raise ValueError("Stage3 candidate schema changed")
    if candidate.get("classification") != EXPECTED_CANDIDATE_CLASSIFICATION:
        raise ValueError("Stage3 candidate classification changed")
    if candidate.get("evaluationRole") != "generated-only-pre-reference-candidate":
        raise ValueError("Stage3 candidate evaluation role changed")
    if candidate.get("instrument") != "rhythm":
        raise ValueError("Stage3 candidate instrument changed")

    metadata = _require_mapping(candidate.get("candidate"), "Stage3 candidate metadata")
    if int(metadata.get("eventCount") or 0) != EXPECTED_CANDIDATE_EVENT_COUNT:
        raise ValueError("Stage3 candidate metadata event count changed")
    if int(metadata.get("generatedMeasureCount") or 0) != EXPECTED_GENERATED_MEASURE_COUNT:
        raise ValueError("Stage3 candidate metadata measure count changed")
    expected_sha = str(metadata.get("eventSha256") or "")
    if len(expected_sha) != 64:
        raise ValueError("Stage3 candidate metadata event SHA is invalid")

    safety = _require_mapping(candidate.get("safety"), "Stage3 candidate safety")
    expected_safety = {
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "goldInputUsed": False,
        "acceptedBaselineChanged": False,
    }
    for key, expected in expected_safety.items():
        if safety.get(key) is not expected:
            raise ValueError(f"Stage3 candidate safety flag changed: {key}")

    raw_events = candidate.get("renderEvents")
    if not isinstance(raw_events, Sequence) or isinstance(raw_events, (str, bytes)):
        raise ValueError("Stage3 candidate renderEvents must be an array")
    events = canonical_events(raw_events)
    if len(events) != EXPECTED_CANDIDATE_EVENT_COUNT:
        raise ValueError("Stage3 candidate canonical event count changed")
    actual_sha = sha256_json(events)
    if actual_sha != expected_sha:
        raise ValueError("Stage3 candidate metadata/event SHA mismatch")
    return candidate, events, actual_sha


def _validate_candidate_freeze_identity(
    candidate: Mapping[str, Any],
    candidate_events: Sequence[Mapping[str, Any]],
    candidate_sha: str,
    freeze_manifest: Mapping[str, Any],
    frozen_events: Sequence[Mapping[str, Any]],
) -> None:
    if len(candidate_events) != EXPECTED_CANDIDATE_EVENT_COUNT:
        raise ValueError("Stage3 candidate event count changed")
    if len(frozen_events) != EXPECTED_CANDIDATE_EVENT_COUNT:
        raise ValueError("Stage3 frozen event count changed")

    frozen_canonical = canonical_events(frozen_events)
    frozen_sha = sha256_json(frozen_canonical)
    if frozen_sha != candidate_sha:
        raise ValueError("Stage3 frozen/candidate event SHA mismatch")
    if list(frozen_canonical) != list(candidate_events):
        raise ValueError("Stage3 frozen/candidate canonical events differ")

    if freeze_manifest.get("eventSha256") != candidate_sha:
        raise ValueError("Stage3 freeze manifest candidate SHA mismatch")
    if freeze_manifest.get("pdfEventSha256") != candidate_sha:
        raise ValueError("Stage3 PDF event SHA mismatch")
    if float(freeze_manifest.get("pdfEventFidelity") or 0.0) != 1.0:
        raise ValueError("Stage3 PDF event fidelity must equal 1.0")

    measures = {int(row["measure"]) for row in candidate_events}
    if measures != set(EXPECTED_GENERATED_MEASURE_SET):
        raise ValueError("Stage3 candidate must cover exactly measures 1..113")
    indices = [int(row["eventIndex"]) for row in candidate_events]
    if indices != list(range(EXPECTED_CANDIDATE_EVENT_COUNT)):
        raise ValueError("Stage3 candidate eventIndex sequence changed")

    metadata = _require_mapping(candidate.get("candidate"), "Stage3 candidate metadata")
    if int(metadata.get("eventCount") or 0) != len(candidate_events):
        raise ValueError("Stage3 candidate metadata count differs from frozen candidate")
    if metadata.get("eventSha256") != candidate_sha:
        raise ValueError("Stage3 candidate metadata SHA differs from frozen candidate")


def _validate_accepted_manifest(manifest_value: Any) -> Mapping[str, Any]:
    manifest = _require_mapping(manifest_value, "accepted family #10 manifest")
    if manifest.get("classification") != ACCEPTED_MANIFEST_CLASSIFICATION:
        raise ValueError("accepted family #10 manifest classification changed")
    if manifest.get("status") != ACCEPTED_MANIFEST_STATUS:
        raise ValueError("accepted family #10 manifest status changed")
    if manifest.get("name") != ACCEPTED_NAME:
        raise ValueError("accepted family #10 name changed")

    selected = _require_mapping(manifest.get("selectedCandidate"), "accepted selectedCandidate")
    if int(selected.get("eventCount") or 0) != ACCEPTED_EVENT_COUNT:
        raise ValueError("accepted family #10 event count changed")
    if selected.get("eventSha256") != ACCEPTED_EVENT_SHA256:
        raise ValueError("accepted family #10 event SHA changed")
    if selected.get("pdfEventSha256") != ACCEPTED_EVENT_SHA256:
        raise ValueError("accepted family #10 PDF event SHA changed")
    if float(selected.get("pdfEventFidelity") or 0.0) != 1.0:
        raise ValueError("accepted family #10 PDF fidelity changed")
    if int(selected.get("generatedMeasureCount") or 0) != ACCEPTED_MEASURE_COUNT:
        raise ValueError("accepted family #10 generated measure count changed")

    full = _require_mapping(manifest.get("fullGoldCalibration"), "accepted fullGoldCalibration")
    if int(full.get("criticalMismatchCount") or 0) != ACCEPTED_CRITICAL_MISMATCH_COUNT:
        raise ValueError("accepted family #10 critical mismatch count changed")
    gated = _require_mapping(full.get("gatedMetrics"), "accepted gated metrics")
    for name, expected in ACCEPTED_METRICS.items():
        if name == "pdfEventFidelity":
            actual = float(selected.get("pdfEventFidelity") or 0.0)
        else:
            actual = float(gated.get(name))
        if actual != expected:
            raise ValueError(f"accepted family #10 metric changed: {name}")
    return manifest


def evaluate_stage3_candidate(
    freeze_dir: Path,
    candidate_json: Path,
    reference_json: Path,
    accepted_manifest_json: Path,
    *,
    read_json: ReadJson = _read_json,
    read_bytes: ReadBytes = _read_bytes,
    pre_reference_fn: PreReferenceFn = scorer.validate_pre_reference,
    validate_reference_fn: ValidateReferenceFn = scorer.validate_reference,
    score_fn: ScoreFn = score_full_candidate,
    expected_gold_sha256: str = EXPECTED_GOLD_SHA256,
) -> dict[str, Any]:
    # 1) Candidate-only validation. No calibration material may be opened here.
    candidate_payload, candidate_events, candidate_sha = _candidate_only_validation(read_json(candidate_json))
    candidate_before = deepcopy(candidate_payload)

    # 2) Frozen pre-reference gate. It validates reference-free freeze/PDF identity before gold access.
    freeze_manifest, frozen_events, _snapshot = pre_reference_fn(freeze_dir)

    # 3) Candidate/freeze/PDF identity gate. Calibration material is still unopened.
    _validate_candidate_freeze_identity(
        candidate_payload,
        candidate_events,
        candidate_sha,
        freeze_manifest,
        frozen_events,
    )

    # 4–5) Only now may the accepted calibration baseline manifest be read.
    accepted_manifest = _validate_accepted_manifest(read_json(accepted_manifest_json))
    del accepted_manifest  # identity has been fully validated; constants below remain frozen.

    # 6) Gold bytes are opened only after every prior gate passes; hash before parse/validation.
    reference_raw = read_bytes(reference_json)
    reference_sha = hashlib.sha256(reference_raw).hexdigest()
    if reference_sha != expected_gold_sha256:
        raise ValueError("V144 calibration gold SHA256 changed")
    reference = validate_reference_fn(json.loads(reference_raw.decode("utf-8")))

    # 7) Score the already-frozen candidate exactly once.
    frozen_canonical = canonical_events(frozen_events)
    candidate_score = score_fn(frozen_canonical, reference)

    # Scoring is observational only; no candidate mutation is permitted.
    if candidate_payload != candidate_before:
        raise ValueError("Stage3 candidate mutated during evaluation")
    if sha256_json(canonical_events(candidate_payload.get("renderEvents") or [])) != candidate_sha:
        raise ValueError("Stage3 candidate event identity changed during evaluation")

    score_metrics = _require_mapping(candidate_score.get("gatedMetrics"), "candidate gated metrics")
    gated_metrics = {
        name: float(score_metrics[name])
        for name in (
            "pitchContentF1",
            "pitchTimingTolerantF1",
            "stringFretTimingTolerantF1",
            "chordPitchSetTolerantF1",
            "exactVoicingTolerantF1",
            "measureCoverageRecall",
        )
    }
    gated_metrics["pdfEventFidelity"] = 1.0
    critical = int(candidate_score["criticalMismatchCount"])

    deltas = {
        name: float(gated_metrics[name]) - float(ACCEPTED_METRICS[name])
        for name in ACCEPTED_METRICS
    }

    return {
        "schemaVersion": SCHEMA_VERSION,
        "classification": CLASSIFICATION,
        "evaluationRole": EVALUATION_ROLE,
        "instrument": "rhythm",
        "mayClaimUnseenGeneralization": False,
        "candidate": {
            "eventCount": EXPECTED_CANDIDATE_EVENT_COUNT,
            "eventSha256": candidate_sha,
            "generatedMeasureCount": EXPECTED_GENERATED_MEASURE_COUNT,
            "pdfEventFidelity": 1.0,
            "gatedMetrics": gated_metrics,
            "criticalMismatchCount": critical,
            "score": candidate_score,
        },
        "acceptedComparison": {
            "name": ACCEPTED_NAME,
            "eventCount": ACCEPTED_EVENT_COUNT,
            "eventSha256": ACCEPTED_EVENT_SHA256,
            "generatedMeasureCount": ACCEPTED_MEASURE_COUNT,
            "gatedMetrics": dict(ACCEPTED_METRICS),
            "criticalMismatchCount": ACCEPTED_CRITICAL_MISMATCH_COUNT,
            "candidateMinusAcceptedGatedMetricDeltas": deltas,
            "criticalMismatchDelta": critical - ACCEPTED_CRITICAL_MISMATCH_COUNT,
        },
        "reference": {
            "role": "gold-calibration-reference-not-unseen-holdout",
            "sha256": reference_sha,
            "openedOnlyAfterPreReferenceGate": True,
        },
        "safety": {
            "referenceOpenedOnlyAfterPreReferenceGate": True,
            "candidateMutatedDuringEvaluation": False,
            "acceptedBaselineChanged": False,
            "promotionAllowed": False,
            "modalGpuUsed": False,
            "liveAudioBenchmarkRun": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score one already-frozen V145 Stage3 Rhythm candidate against the V144 calibration gold."
    )
    parser.add_argument("freeze_dir", type=Path)
    parser.add_argument("candidate_json", type=Path)
    parser.add_argument("reference_json", type=Path)
    parser.add_argument("accepted_manifest_json", type=Path)
    parser.add_argument("output_score_report", type=Path)
    args = parser.parse_args()

    report = evaluate_stage3_candidate(
        args.freeze_dir,
        args.candidate_json,
        args.reference_json,
        args.accepted_manifest_json,
    )
    args.output_score_report.parent.mkdir(parents=True, exist_ok=True)
    args.output_score_report.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
