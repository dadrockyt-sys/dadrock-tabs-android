from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
SEARCH_DIR = ROOT / "validation" / "v144_rhythm_calibration"
MODAL_DIR = ROOT / "modal"
for entry in (HOLDOUT_DIR, SEARCH_DIR, MODAL_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from canonical import canonical_events, sha256_json  # noqa: E402
from search_atomic_singleton_onset_replacements import (  # noqa: E402
    ACCEPTED_EVENT_SHA256,
    SOURCE_EVENT_COUNT,
    SOURCE_EVENT_SHA256,
    changed_event_count,
    reconstruct_accepted_baseline,
)
from v144_rhythm_singleton_onset_replacement_policy import (  # noqa: E402
    apply_singleton_onset_replacement_rule,
)

NEW_BASELINE_NAME = "singleton-onset-replace-be9e9aa7a734e3cd"
NEW_EVENT_SHA256 = "4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881"
NEW_EVENT_COUNT = 1144
NEW_MEASURE_COUNT = 113
CONTEXT_SIGNATURE = "stepParity::0"
SOURCE_STRING_INDEX = 0
SOURCE_PITCH_CLASS = 4
TARGET_STRING_INDEX = 3
SEMITONE_SHIFT = -12
CHANGED_EVENT_COUNT = 110


class SelectedSingletonBaselineReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v5_path = ROOT / "debug" / "v143-contextual-prune" / "v5-professional-pdf" / "v5-render-stream.json"
        cls.manifest_path = ROOT / "debug" / "v144-rhythm-calibration" / "selected" / "v144-singleton-onset-replacement-selected-baseline.json"

    def test_reference_free_chain_reconstructs_exact_selected_event_identity(self) -> None:
        v5_payload = json.loads(self.v5_path.read_text(encoding="utf-8"))
        v5_events = canonical_events(v5_payload.get("events") or [])
        self.assertEqual(len(v5_events), SOURCE_EVENT_COUNT)
        self.assertEqual(sha256_json(v5_events), SOURCE_EVENT_SHA256)

        prior = reconstruct_accepted_baseline(v5_events)
        self.assertEqual(len(prior), NEW_EVENT_COUNT)
        self.assertEqual(sha256_json(prior), ACCEPTED_EVENT_SHA256)

        selected = canonical_events(
            apply_singleton_onset_replacement_rule(
                prior,
                CONTEXT_SIGNATURE,
                SOURCE_STRING_INDEX,
                SOURCE_PITCH_CLASS,
                TARGET_STRING_INDEX,
                SEMITONE_SHIFT,
                maximum_abs_semitone_shift=12,
            )
        )
        self.assertEqual(len(selected), NEW_EVENT_COUNT)
        self.assertEqual(sha256_json(selected), NEW_EVENT_SHA256)
        self.assertEqual(len({int(row["measure"]) for row in selected}), NEW_MEASURE_COUNT)
        self.assertEqual(
            changed_event_count(
                prior,
                selected,
                expected_context_signature=CONTEXT_SIGNATURE,
                expected_source_string_index=SOURCE_STRING_INDEX,
                expected_source_pitch_class=SOURCE_PITCH_CLASS,
                expected_target_string_index=TARGET_STRING_INDEX,
                expected_semitone_shift=SEMITONE_SHIFT,
            ),
            CHANGED_EVENT_COUNT,
        )

    def test_manifest_locks_reconstruction_and_calibration_only_scope(self) -> None:
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["classification"], "v144-rhythm-selected-calibration-baseline")
        self.assertEqual(manifest["status"], "accepted-calibration-baseline-not-production")
        self.assertEqual(manifest["name"], NEW_BASELINE_NAME)
        self.assertEqual(manifest["previousBaseline"]["eventSha256"], ACCEPTED_EVENT_SHA256)
        self.assertEqual(manifest["sourceSearch"]["reportGitBlob"], "92de07b1cac11cba87e923c18eebf9cce7b0cea7")
        self.assertFalse(manifest["sourceSearch"]["replayAllowed"])

        transform = manifest["transform"]
        self.assertEqual(transform["contextSignature"], CONTEXT_SIGNATURE)
        self.assertEqual(transform["sourceStringIndex"], SOURCE_STRING_INDEX)
        self.assertEqual(transform["sourcePitchClass"], SOURCE_PITCH_CLASS)
        self.assertEqual(transform["targetStringIndex"], TARGET_STRING_INDEX)
        self.assertEqual(transform["semitoneShift"], SEMITONE_SHIFT)
        self.assertEqual(transform["changedEventCount"], CHANGED_EVENT_COUNT)
        self.assertEqual(transform["changedOnsetCount"], CHANGED_EVENT_COUNT)
        self.assertTrue(transform["eventCountPreserving"])
        self.assertTrue(transform["eventOrderPreserving"])
        self.assertTrue(transform["timingPreserving"])
        self.assertTrue(transform["measurePreserving"])
        self.assertTrue(transform["exactlyOneGeneratedNoteOnsetRequired"])
        self.assertTrue(transform["pitchChangeRequired"])
        self.assertTrue(transform["stringChangeRequired"])
        self.assertTrue(transform["explicitTargetString"])
        self.assertFalse(transform["adjacentStringOnly"])
        self.assertTrue(transform["tuningDerivedFret"])
        self.assertFalse(transform["professionalReferenceRuntimeInput"])

        selected = manifest["selectedCandidate"]
        self.assertEqual(selected["eventCount"], NEW_EVENT_COUNT)
        self.assertEqual(selected["generatedMeasureCount"], NEW_MEASURE_COUNT)
        self.assertEqual(selected["eventSha256"], NEW_EVENT_SHA256)
        self.assertEqual(selected["pdfEventSha256"], NEW_EVENT_SHA256)
        self.assertEqual(selected["pdfEventFidelity"], 1.0)
        self.assertTrue(selected["baselineGeneratedMeasureSetPreserved"])

        self.assertTrue(manifest["fitGate"]["passed"])
        self.assertTrue(manifest["validationGate"]["passed"])
        self.assertTrue(manifest["canaryGate"]["passed"])
        self.assertTrue(manifest["fullGoldCalibration"]["passed"])
        self.assertEqual(manifest["fullGoldCalibration"]["measureCoverageRecall"], 1.0)
        self.assertEqual(manifest["fullGoldCalibration"]["gatedMetrics"]["pdfEventFidelity"], 1.0)
        self.assertEqual(manifest["fullGoldCalibration"]["metricRegressions"], {})

        scope = manifest["promotionScope"]
        self.assertTrue(scope["calibrationBaseline"])
        self.assertFalse(scope["productionPromotionAllowed"])
        self.assertFalse(scope["rhythmComplete"])
        self.assertFalse(scope["near100CalibrationTargetReached"])
        self.assertFalse(scope["mayClaimUnseenGeneralization"])

        safety = manifest["safety"]
        self.assertFalse(safety["v5Modified"])
        self.assertFalse(safety["mainModified"])
        self.assertFalse(safety["productionModified"])
        self.assertFalse(safety["runtimeReferenceInputUsed"])
        self.assertFalse(safety["modalGpuInvoked"])
        self.assertFalse(safety["historicalSearchWorkflowReplayAllowed"])
        self.assertFalse(safety["consumedFamilyRunnerUpSelectionAllowed"])
        self.assertFalse(safety["sourceFamilyReplayAllowed"])


if __name__ == "__main__":
    unittest.main()
