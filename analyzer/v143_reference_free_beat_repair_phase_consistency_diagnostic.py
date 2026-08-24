from __future__ import annotations

import json
import sys
from pathlib import Path

import soundfile as sf

from v143_reference_free_beat_grid_repair import repair_reference_free_beat_grid_from_samples
from v143_reference_free_timing import estimate_reference_free_timing_from_samples

APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
BEATS_PER_MEASURE = 4


def diagnose(audio_path: Path) -> dict:
    samples, sample_rate = sf.read(str(audio_path), dtype="float32", always_2d=False)
    original = estimate_reference_free_timing_from_samples(samples, int(sample_rate))
    repair = repair_reference_free_beat_grid_from_samples(samples, int(sample_rate), original)

    leading = int(repair.leading_extended_beat_count)
    trailing = int(repair.trailing_extended_beat_count)
    expected_first_after_prepend = (
        int(original.first_beat_in_measure) - leading
    ) % BEATS_PER_MEASURE
    expected_downbeat_after_prepend = (
        int(original.downbeat_index_mod4) + leading
    ) % BEATS_PER_MEASURE

    actual_first = int(repair.timing.first_beat_in_measure)
    actual_downbeat = int(repair.timing.downbeat_index_mod4)
    phase_reindex_needed = (leading % BEATS_PER_MEASURE) != 0

    return {
        "schemaVersion": 1,
        "mode": "v143-reference-free-beat-repair-phase-consistency-diagnostic",
        "sourceAudioSha256": APPROVED_AUDIO_SHA256,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
        "modalUsed": False,
        "newInferenceUsed": False,
        "productionModified": False,
        "protectedRuntimeModified": False,
        "candidateRenderProduced": False,
        "eventMutationProposed": False,
        "originalTiming": {
            "beatCount": len(original.beat_times),
            "firstBeatTimeSeconds": float(original.beat_times[0]),
            "lastBeatTimeSeconds": float(original.beat_times[-1]),
            "tempoBpm": float(original.tempo_bpm),
            "firstBeatInMeasure": int(original.first_beat_in_measure),
            "downbeatIndexMod4": int(original.downbeat_index_mod4),
            "beatConfidence": float(original.beat_confidence),
            "barConfidence": float(original.bar_confidence),
        },
        "repair": {
            **repair.diagnostics(),
            "leadingExtendedBeatCount": leading,
            "trailingExtendedBeatCount": trailing,
        },
        "phaseConsistency": {
            "leadingExtensionModulo4": leading % BEATS_PER_MEASURE,
            "phaseReindexNeededIfLeadingBeatsPrepended": phase_reindex_needed,
            "expectedFirstBeatInMeasureAfterPrepend": expected_first_after_prepend,
            "actualRepairedFirstBeatInMeasure": actual_first,
            "expectedDownbeatIndexMod4AfterPrepend": expected_downbeat_after_prepend,
            "actualRepairedDownbeatIndexMod4": actual_downbeat,
            "firstBeatCoordinateConsistent": actual_first == expected_first_after_prepend,
            "downbeatCoordinateConsistent": actual_downbeat == expected_downbeat_after_prepend,
            "repairPhaseCoordinateConsistent": (
                actual_first == expected_first_after_prepend
                and actual_downbeat == expected_downbeat_after_prepend
            ),
        },
        "interpretationBoundary": (
            "A repair that prepends L beats changes the sequence index of every original beat by L. "
            "Therefore the first-beat position must shift by -L mod 4 and downbeat sequence phase by +L mod 4. "
            "This diagnostic only audits coordinate consistency; it does not choose a musical bar phase or mutate events."
        ),
        "invariants": {
            "referenceConsulted": False,
            "modalInvoked": False,
            "eventsMutated": False,
            "attackGridMutated": False,
            "pitchSelectionMutated": False,
        },
    }


def main(source: str, destination: str) -> None:
    report = diagnose(Path(source))
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "originalTiming": report["originalTiming"],
        "repair": {
            "originalBeatCount": report["repair"]["originalBeatCount"],
            "repairedBeatCount": report["repair"]["repairedBeatCount"],
            "leadingExtendedBeatCount": report["repair"]["leadingExtendedBeatCount"],
            "trailingExtendedBeatCount": report["repair"]["trailingExtendedBeatCount"],
            "lookaheadBridgeBeatCount": report["repair"]["lookaheadBridgeBeatCount"],
        },
        "phaseConsistency": report["phaseConsistency"],
    }, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: v143_reference_free_beat_repair_phase_consistency_diagnostic.py WAV OUTPUT")
    main(sys.argv[1], sys.argv[2])
