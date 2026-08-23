from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_PROTECTED_PIPELINE_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"
EXPECTED_TARGET_MEASURE_COUNT = 113


@dataclass(frozen=True)
class PhysicalReviewResult:
    passed: bool
    issues: tuple[str, ...]
    metrics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": 1,
            "mode": "v143-approved-shadow-physical-review",
            "passed": bool(self.passed),
            "issues": list(self.issues),
            "metrics": dict(self.metrics),
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _integer(value: Any, default: int = -1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def review_approved_correction_shadow(
    action: Mapping[str, Any],
    report: Mapping[str, Any],
) -> PhysicalReviewResult:
    """Validate only reference-free safety/consistency of an approved-audio shadow.

    This deliberately does not decide whether a correction is musically correct and
    does not inspect any professional reference or score. It verifies that the
    approved fixture, protected runtime boundary, event-preservation rules, coverage
    monotonicity, pitch-suppression direction, and timing non-mutation claims are
    internally consistent before a human/reference-free evidence review proceeds.
    """

    issues: list[str] = []

    if action.get("approvedAudioIdentityPassed") is not True:
        issues.append("approved audio identity did not pass")
    if str(action.get("approvedAudioSha256") or "") != APPROVED_AUDIO_SHA256:
        issues.append("approved audio SHA does not match the locked fixture")
    if action.get("protectedPipelineUnchanged") is not True:
        issues.append("protected Rhythm pipeline was not proven unchanged")
    if str(action.get("protectedPipelineBlob") or "") != EXPECTED_PROTECTED_PIPELINE_BLOB:
        issues.append("protected Rhythm pipeline blob is not the locked blob")
    if action.get("referenceTokenScanPassed") is not True:
        issues.append("scorer/reference token scan did not pass")
    if action.get("professionalReferenceUsed") is not False:
        issues.append("action claims professional reference use")
    if action.get("runtimeLabelsRequired") is not False:
        issues.append("action claims runtime labels are required")
    if action.get("productionModified") is not False:
        issues.append("action claims Production was modified")
    if action.get("liveEndpointDeployedOrModified") is not False:
        issues.append("action claims live endpoint deployment/modification")
    if action.get("shadowAttempted") is not True:
        issues.append("approved-audio shadow was not attempted")
    if _integer(action.get("shadowExitCode"), 1) != 0:
        issues.append("approved-audio shadow exit code was non-zero")
    if action.get("reportExists") is not True:
        issues.append("approved-audio shadow report was not produced")

    if str(report.get("sourceSha256") or "") != APPROVED_AUDIO_SHA256:
        issues.append("report source SHA does not match the approved fixture")

    invariants = _as_mapping(report.get("invariants"))
    required_invariants = {
        "sourceIsApprovedFixture": True,
        "referenceFree": True,
        "runtimeLabelsRequired": False,
        "baseEventsPreserved": True,
        "rescuedEventsPhysicallyObserved": True,
        "candidateRelocatesEvents": False,
        "timingDiagnosticChangesGrid": False,
        "timingHypothesisChangesGrid": False,
        "liveRhythmOutputChanged": False,
        "leadChanged": False,
        "bassChanged": False,
        "productionModified": False,
    }
    for key, expected in required_invariants.items():
        if invariants.get(key) is not expected:
            issues.append(f"report invariant failed: {key}")

    correction = _as_mapping(report.get("correction"))
    base_count = _integer(correction.get("baseEventCount"))
    corrected_count = _integer(correction.get("correctedEventCount"))
    rescued_count = _integer(correction.get("rescuedEventCount"))
    suppressed_count = _integer(correction.get("suppressedPitchCount"))
    if min(base_count, corrected_count, rescued_count, suppressed_count) < 0:
        issues.append("correction counts are missing or negative")
    if corrected_count != base_count + rescued_count:
        issues.append("corrected event count is not base plus rescued events")
    if correction.get("baseEventsPreserved") is not True:
        issues.append("correction diagnostics do not preserve base events")
    if correction.get("rescuesAreObservedSlots") is not True:
        issues.append("correction diagnostics do not prove observed rescue slots")
    if correction.get("candidateRelocatesEvents") is not False:
        issues.append("correction diagnostics claim event relocation")

    rescued_events = _as_sequence(report.get("rescuedEvents"))
    if rescued_count >= 0 and len(rescued_events) != rescued_count:
        issues.append("rescued event list length does not match rescued count")
    rescue_keys: set[tuple[int, int]] = set()
    for raw in rescued_events:
        item = _as_mapping(raw)
        measure = _integer(item.get("measure"))
        step = _integer(item.get("step"))
        key = (measure, step)
        if measure <= 0 or step < 0:
            issues.append("rescued event has invalid measure/step")
            continue
        if key in rescue_keys:
            issues.append("rescued event list contains a duplicate slot")
        rescue_keys.add(key)

    coverage = _as_mapping(report.get("coverage"))
    target_measure_count = _integer(coverage.get("targetMeasureCount"))
    populated_before = _integer(coverage.get("populatedMeasureCountBefore"))
    populated_after = _integer(coverage.get("populatedMeasureCountAfter"))
    if target_measure_count != EXPECTED_TARGET_MEASURE_COUNT:
        issues.append("approved fixture target measure count is not 113")
    if populated_before < 0 or populated_after < 0:
        issues.append("coverage populated-measure counts are missing")
    if populated_after < populated_before:
        issues.append("correction reduced populated-measure coverage")

    missing_before = {_integer(value) for value in _as_sequence(coverage.get("missingMeasuresBefore"))}
    missing_after = {_integer(value) for value in _as_sequence(coverage.get("missingMeasuresAfter"))}
    if -1 in missing_before or -1 in missing_after:
        issues.append("coverage missing-measure list contains an invalid value")
    if not missing_after.issubset(missing_before):
        issues.append("correction introduced a newly missing measure")

    pitch_support = _as_mapping(report.get("pitchSupport"))
    pitch_changes = _as_sequence(report.get("pitchChanges"))
    changed_event_count = _integer(pitch_support.get("changedEventCount"))
    pitch_suppressed_count = _integer(pitch_support.get("suppressedPitchCount"))
    if changed_event_count != len(pitch_changes):
        issues.append("pitch change list length does not match changedEventCount")
    if pitch_suppressed_count != suppressed_count:
        issues.append("pitchSupport suppression count does not match correction diagnostics")

    summed_suppression = 0
    for raw in pitch_changes:
        item = _as_mapping(raw)
        before = tuple(sorted({_integer(value) for value in _as_sequence(item.get("beforeMidis"))}))
        after = tuple(sorted({_integer(value) for value in _as_sequence(item.get("afterMidis"))}))
        if not before or not after or -1 in before or -1 in after:
            issues.append("pitch change contains an invalid/empty pitch set")
            continue
        if not set(after).issubset(set(before)):
            issues.append("pitch correction introduced a pitch not present in the observed candidate set")
        expected_suppression = len(before) - len(after)
        reported_suppression = _integer(item.get("suppressedCount"))
        if reported_suppression != expected_suppression:
            issues.append("pitch change suppressedCount is inconsistent with before/after sets")
        if expected_suppression <= 0:
            issues.append("pitch change does not actually suppress a candidate pitch")
        summed_suppression += max(0, expected_suppression)
    if summed_suppression != max(0, suppressed_count):
        issues.append("summed pitch suppression does not match correction suppression count")

    timing = _as_mapping(report.get("timingConsistency"))
    timing_invariants = _as_mapping(timing.get("invariants"))
    timing_required = {
        "tempoChanged": False,
        "barPhaseChanged": False,
        "attackTimingChanged": False,
        "candidateSelectionChanged": False,
        "pitchChanged": False,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }
    for key, expected in timing_required.items():
        if timing_invariants.get(key) is not expected:
            issues.append(f"timing consistency invariant failed: {key}")

    hypothesis = _as_mapping(report.get("timingHypothesis"))
    hypothesis_invariants = _as_mapping(hypothesis.get("invariants"))
    for key, expected in timing_required.items():
        if hypothesis_invariants.get(key) is not expected:
            issues.append(f"timing hypothesis invariant failed: {key}")
    phase = _as_mapping(hypothesis.get("barPhaseEvidence"))
    if phase.get("phaseSelectedOrChanged") is not False:
        issues.append("timing hypothesis selected or changed bar phase")

    metrics = {
        "baseEventCount": base_count,
        "correctedEventCount": corrected_count,
        "rescuedEventCount": rescued_count,
        "suppressedPitchCount": suppressed_count,
        "targetMeasureCount": target_measure_count,
        "populatedMeasureCountBefore": populated_before,
        "populatedMeasureCountAfter": populated_after,
        "missingMeasureCountBefore": len(missing_before),
        "missingMeasureCountAfter": len(missing_after),
        "pitchChangedEventCount": changed_event_count,
        "phaseWinnerMatchesCurrent": phase.get("currentWinnerMatches"),
        "phaseConfidence": phase.get("confidence"),
    }
    return PhysicalReviewResult(
        passed=not issues,
        issues=tuple(issues),
        metrics=metrics,
    )


__all__ = [
    "APPROVED_AUDIO_SHA256",
    "EXPECTED_PROTECTED_PIPELINE_BLOB",
    "EXPECTED_TARGET_MEASURE_COUNT",
    "PhysicalReviewResult",
    "review_approved_correction_shadow",
]
