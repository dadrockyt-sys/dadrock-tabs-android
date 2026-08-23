#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy

from v143_approved_shadow_physical_review import (
    APPROVED_AUDIO_SHA256,
    EXPECTED_PROTECTED_PIPELINE_BLOB,
    review_approved_correction_shadow,
)


def _timing_invariants() -> dict[str, bool]:
    return {
        "tempoChanged": False,
        "barPhaseChanged": False,
        "attackTimingChanged": False,
        "candidateSelectionChanged": False,
        "pitchChanged": False,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


def _valid_action() -> dict[str, object]:
    return {
        "approvedAudioIdentityPassed": True,
        "approvedAudioSha256": APPROVED_AUDIO_SHA256,
        "protectedPipelineUnchanged": True,
        "protectedPipelineBlob": EXPECTED_PROTECTED_PIPELINE_BLOB,
        "referenceTokenScanPassed": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "liveEndpointDeployedOrModified": False,
        "shadowAttempted": True,
        "shadowExitCode": 0,
        "reportExists": True,
    }


def _valid_report() -> dict[str, object]:
    return {
        "sourceSha256": APPROVED_AUDIO_SHA256,
        "invariants": {
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
        },
        "correction": {
            "baseEventCount": 3,
            "correctedEventCount": 4,
            "rescuedEventCount": 1,
            "suppressedPitchCount": 1,
            "baseEventsPreserved": True,
            "rescuesAreObservedSlots": True,
            "candidateRelocatesEvents": False,
        },
        "rescuedEvents": [{"measure": 101, "step": 4}],
        "coverage": {
            "targetMeasureCount": 113,
            "populatedMeasureCountBefore": 112,
            "populatedMeasureCountAfter": 113,
            "missingMeasuresBefore": [101],
            "missingMeasuresAfter": [],
        },
        "pitchSupport": {
            "changedEventCount": 1,
            "suppressedPitchCount": 1,
        },
        "pitchChanges": [
            {
                "measure": 12,
                "step": 8,
                "beforeMidis": [40, 52],
                "afterMidis": [40],
                "suppressedCount": 1,
            }
        ],
        "timingConsistency": {"invariants": _timing_invariants()},
        "timingHypothesis": {
            "invariants": _timing_invariants(),
            "barPhaseEvidence": {
                "phaseSelectedOrChanged": False,
                "currentWinnerMatches": True,
                "confidence": 0.8,
            },
        },
    }


def main() -> None:
    action = _valid_action()
    report = _valid_report()
    accepted = review_approved_correction_shadow(action, report)
    assert accepted.passed is True, accepted.issues
    assert accepted.issues == ()
    assert accepted.metrics["rescuedEventCount"] == 1
    assert accepted.metrics["missingMeasureCountAfter"] == 0

    invented_pitch = deepcopy(report)
    invented_pitch["pitchChanges"][0]["afterMidis"] = [40, 55]
    invented = review_approved_correction_shadow(action, invented_pitch)
    assert invented.passed is False
    assert any("introduced a pitch" in issue for issue in invented.issues)

    lost_coverage = deepcopy(report)
    lost_coverage["coverage"]["missingMeasuresAfter"] = [102]
    lost = review_approved_correction_shadow(action, lost_coverage)
    assert lost.passed is False
    assert any("newly missing measure" in issue for issue in lost.issues)

    moved_timing = deepcopy(report)
    moved_timing["timingHypothesis"]["barPhaseEvidence"]["phaseSelectedOrChanged"] = True
    moved = review_approved_correction_shadow(action, moved_timing)
    assert moved.passed is False
    assert any("selected or changed bar phase" in issue for issue in moved.issues)

    print("V143 approved shadow physical review proof passed")
    print(accepted.to_dict())


if __name__ == "__main__":
    main()
