from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
STAGE3_DIR = ROOT / "validation" / "v145_rhythm_decoder"
if str(STAGE3_DIR) not in sys.path:
    sys.path.insert(0, str(STAGE3_DIR))

import offline_stage3_adapter as adapter  # noqa: E402


OPEN = adapter.RENDERER_OPEN_MIDI


def event(
    index: int,
    *,
    measure: int = 1,
    step: int = 0,
    string_index: int = 5,
    fret: int = 0,
    midi: int | None = None,
    techniques: list[str] | None = None,
    **extra,
) -> dict:
    return {
        "eventIndex": index,
        "measure": measure,
        "step": step,
        "stringIndex": string_index,
        "fret": fret,
        "midi": OPEN[string_index] + fret if midi is None else midi,
        "durationSteps": 1,
        "techniques": [] if techniques is None else list(techniques),
        "metadataSource": "synthetic",
        **extra,
    }


def decoded(
    source_index: int,
    *,
    midi: int,
    onset_steps: float,
    string: int,
    fret: int,
):
    step_seconds = adapter._source_step_seconds()
    return adapter.stage2.stage1.DecodedNote(
        source_index=source_index,
        midi=midi,
        raw_onset=0.0,
        onset=onset_steps * step_seconds,
        duration=step_seconds,
        confidence=1.0,
        timing_cost=0.0,
        string=string,
        fret=fret,
    )


def result(*notes, undecoded=()):
    return SimpleNamespace(
        grid=None,
        decoded_notes=tuple(notes),
        undecoded_source_indices=tuple(undecoded),
        cluster_count=1 if notes else 0,
        decoded_cluster_count=1 if notes else 0,
    )


def full_synthetic_payload() -> dict:
    events: list[dict] = []
    used: set[tuple[int, int, int]] = set()

    # Guarantee all 113 measures before filling the remaining cells.
    for measure in range(1, adapter.EXPECTED_MEASURE_COUNT + 1):
        string_index = (measure - 1) % 6
        cell = (measure, 0, string_index)
        used.add(cell)
        events.append(
            event(
                len(events),
                measure=measure,
                step=0,
                string_index=string_index,
            )
        )

    for measure in range(1, adapter.EXPECTED_MEASURE_COUNT + 1):
        for step in range(16):
            for string_index in range(6):
                if len(events) >= adapter.EXPECTED_SOURCE_EVENT_COUNT:
                    break
                cell = (measure, step, string_index)
                if cell in used:
                    continue
                used.add(cell)
                events.append(
                    event(
                        len(events),
                        measure=measure,
                        step=step,
                        string_index=string_index,
                    )
                )
            if len(events) >= adapter.EXPECTED_SOURCE_EVENT_COUNT:
                break
        if len(events) >= adapter.EXPECTED_SOURCE_EVENT_COUNT:
            break

    assert len(events) == adapter.EXPECTED_SOURCE_EVENT_COUNT
    return {
        "tempo": adapter.EXPECTED_TEMPO_BPM,
        "timeSignature": adapter.EXPECTED_TIME_SIGNATURE,
        "events": events,
    }


class Stage3OfflineAdapterTests(unittest.TestCase):
    def test_generated_evidence_reconstructs_absolute_16th_grid(self):
        rows = [event(0, measure=2, step=3, string_index=5, fret=2)]
        rows[0]["durationSteps"] = 4
        evidence = adapter.reconstruct_generated_evidence(rows)
        step_seconds = adapter._source_step_seconds()
        self.assertEqual(evidence[0]["midi"], 42)
        self.assertAlmostEqual(evidence[0]["onset"], 19 * step_seconds)
        self.assertAlmostEqual(evidence[0]["duration"], 4 * step_seconds)
        self.assertEqual(evidence[0]["confidence"], 1.0)

    def test_protection_includes_technique_link_source_and_target(self):
        rows = [
            event(0, techniques=["palm-mute"]),
            event(1, legatoTargetEventIndex=2),
            event(2),
            event(3),
        ]
        self.assertEqual(adapter.protected_source_indices(rows), frozenset({0, 1, 2}))

    def test_valid_unprotected_common_onset_group_applies_atomically(self):
        rows = [
            event(0, step=0, string_index=5, fret=0),
            event(1, step=0, string_index=4, fret=2),
        ]
        before = deepcopy(rows)
        decode = result(
            decoded(0, midi=40, onset_steps=1, string=6, fret=0),
            decoded(1, midi=47, onset_steps=1, string=5, fret=2),
        )
        candidate, stats = adapter.apply_decode_result(
            rows,
            decode,
            step_seconds=adapter._source_step_seconds(),
            required_measure_set=frozenset({1}),
        )
        self.assertEqual([row["step"] for row in candidate], [1, 1])
        self.assertEqual(stats["appliedGroupCount"], 1)
        self.assertEqual(stats["appliedEventCount"], 2)
        for source, changed in zip(before, candidate):
            changed_keys = {key for key in set(source) | set(changed) if source.get(key) != changed.get(key)}
            self.assertTrue(changed_keys.issubset({"measure", "step", "stringIndex", "fret"}))
            self.assertEqual(source["midi"], changed["midi"])
            self.assertEqual(source["eventIndex"], changed["eventIndex"])

    def test_protected_member_preserves_entire_decoded_group(self):
        rows = [
            event(0, step=0, string_index=5, techniques=["palm-mute"]),
            event(1, step=0, string_index=4),
        ]
        before = deepcopy(rows)
        decode = result(
            decoded(0, midi=40, onset_steps=1, string=6, fret=0),
            decoded(1, midi=45, onset_steps=1, string=5, fret=0),
        )
        candidate, stats = adapter.apply_decode_result(
            rows,
            decode,
            step_seconds=adapter._source_step_seconds(),
            required_measure_set=frozenset({1}),
        )
        self.assertEqual(candidate, before)
        self.assertEqual(stats["protectedGroupCount"], 1)
        self.assertEqual(stats["appliedGroupCount"], 0)

    def test_conversion_residual_over_frozen_limit_preserves_group(self):
        rows = [event(0, step=0, string_index=5)]
        decode = result(decoded(0, midi=40, onset_steps=1.02, string=6, fret=0))
        candidate, stats = adapter.apply_decode_result(
            rows,
            decode,
            step_seconds=adapter._source_step_seconds(),
            required_measure_set=frozenset({1}),
        )
        self.assertEqual(candidate, rows)
        self.assertEqual(stats["residualOrRangePreservedGroupCount"], 1)

    def test_external_renderer_cell_collision_preserves_group(self):
        rows = [
            event(0, step=0, string_index=5),
            event(1, step=1, string_index=5),
        ]
        decode = result(decoded(0, midi=40, onset_steps=1, string=6, fret=0), undecoded=(1,))
        candidate, stats = adapter.apply_decode_result(
            rows,
            decode,
            step_seconds=adapter._source_step_seconds(),
            required_measure_set=frozenset({1}),
        )
        self.assertEqual(candidate, rows)
        self.assertEqual(stats["collisionPreservedGroupCount"], 1)

    def test_midi_change_fails_closed(self):
        rows = [event(0, step=0, string_index=5)]
        decode = result(decoded(0, midi=41, onset_steps=1, string=6, fret=1))
        with self.assertRaisesRegex(ValueError, "changed MIDI"):
            adapter.apply_decode_result(
                rows,
                decode,
                step_seconds=adapter._source_step_seconds(),
                required_measure_set=frozenset({1}),
            )

    def test_measure_set_change_fails_closed(self):
        rows = [
            event(0, measure=1, step=0, string_index=5),
            event(1, measure=2, step=0, string_index=4),
        ]
        decode = result(decoded(1, midi=45, onset_steps=1, string=5, fret=0), undecoded=(0,))
        with self.assertRaisesRegex(ValueError, "measure coverage"):
            adapter.apply_decode_result(
                rows,
                decode,
                step_seconds=adapter._source_step_seconds(),
                required_measure_set=frozenset({1, 2}),
            )

    def test_physical_position_mismatch_fails_closed(self):
        rows = [event(0, step=0, string_index=5)]
        decode = result(decoded(0, midi=40, onset_steps=1, string=5, fret=0))
        with self.assertRaisesRegex(ValueError, "does not reproduce source MIDI"):
            adapter.apply_decode_result(
                rows,
                decode,
                step_seconds=adapter._source_step_seconds(),
                required_measure_set=frozenset({1}),
            )

    def test_full_builder_calls_stage2_exactly_once_and_keeps_no_decode_source_exact(self):
        payload = full_synthetic_payload()
        no_decode = SimpleNamespace(
            grid=None,
            decoded_notes=tuple(),
            undecoded_source_indices=tuple(range(adapter.EXPECTED_SOURCE_EVENT_COUNT)),
            cluster_count=0,
            decoded_cluster_count=0,
        )
        with patch.object(adapter.stage2, "decode_global_rhythm_sequence", return_value=no_decode) as mock_decode:
            candidate = adapter.build_stage3_candidate(payload)
        self.assertEqual(mock_decode.call_count, 1)
        self.assertEqual(candidate["renderEvents"], payload["events"])
        self.assertEqual(candidate["candidate"]["eventCount"], adapter.EXPECTED_SOURCE_EVENT_COUNT)
        self.assertEqual(candidate["candidate"]["generatedMeasureCount"], adapter.EXPECTED_MEASURE_COUNT)
        self.assertTrue(candidate["safety"]["referenceFree"])
        self.assertFalse(candidate["safety"]["goldInputUsed"])
        self.assertFalse(candidate["safety"]["acceptedBaselineChanged"])

    def test_full_builder_requires_actual_v5_root_tempo_key(self):
        payload = full_synthetic_payload()
        payload["tempoBpm"] = payload.pop("tempo")
        with self.assertRaisesRegex(ValueError, "source tempo changed"):
            adapter.build_stage3_candidate(payload)

    def test_source_index_identity_is_fixed(self):
        payload = full_synthetic_payload()
        payload["events"][10]["eventIndex"] = 11
        no_decode = SimpleNamespace(
            grid=None,
            decoded_notes=tuple(),
            undecoded_source_indices=tuple(range(adapter.EXPECTED_SOURCE_EVENT_COUNT)),
            cluster_count=0,
            decoded_cluster_count=0,
        )
        with patch.object(adapter.stage2, "decode_global_rhythm_sequence", return_value=no_decode):
            with self.assertRaisesRegex(ValueError, "eventIndex"):
                adapter.build_stage3_candidate(payload)


if __name__ == "__main__":
    unittest.main()
