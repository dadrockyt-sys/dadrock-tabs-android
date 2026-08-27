from __future__ import annotations

from pathlib import Path
import copy
import inspect
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

import v145_rhythm_decoder as decoder  # noqa: E402


class V145RhythmDecoderTests(unittest.TestCase):
    def test_normalize_aliases_defaults_invalids_and_input_immutability(self) -> None:
        events = [
            {"midi": 60, "onset": 0.25, "duration": 0.4, "confidence": 0.8},
            {"midiPitch": 62.2, "time": 0.5, "durationSeconds": 0.2, "probability": 1.2},
            {"pitch": 64, "startTime": 0.75},
            {"midi": 65, "onset": -0.1},
            {"midi": "66", "onset": 1.0},
            {"midi": 67},
        ]
        original = copy.deepcopy(events)

        normalized = decoder.normalize_rhythm_events(events)

        self.assertEqual(events, original)
        self.assertEqual(len(normalized), 3)
        self.assertEqual([row.midi for row in normalized], [60, 62, 64])
        self.assertEqual(normalized[0].duration, 0.4)
        self.assertEqual(normalized[1].confidence, 1.0)
        self.assertEqual(normalized[2].duration, 0.0)
        self.assertEqual(normalized[2].confidence, 1.0)

    def test_timing_lattice_keeps_nearest_and_neighbors(self) -> None:
        evidence = decoder.normalize_rhythm_events([{"midi": 60, "onset": 0.26}])
        candidates = decoder.timing_candidates_for_event(evidence[0], 0.25, max_shift_steps=1)

        self.assertEqual(candidates[0].candidate_onset, 0.25)
        self.assertAlmostEqual(candidates[0].timing_cost, 0.04)
        self.assertEqual({row.candidate_onset for row in candidates}, {0.0, 0.25, 0.5})
        self.assertTrue(all(row.midi == 60 for row in candidates))
        self.assertTrue(all(row.raw_onset == 0.26 for row in candidates))

        lattice = decoder.build_timing_lattice(evidence, 0.25, max_shift_steps=1)
        self.assertEqual(set(lattice), {0.0, 0.25, 0.5})

    def test_timing_validation_fails_closed(self) -> None:
        evidence = decoder.normalize_rhythm_events([{"midi": 60, "onset": 0.2}])
        with self.assertRaises(ValueError):
            decoder.timing_candidates_for_event(evidence[0], 0.0)
        with self.assertRaises(ValueError):
            decoder.timing_candidates_for_event(evidence[0], float("nan"))
        with self.assertRaises(ValueError):
            decoder.timing_candidates_for_event(evidence[0], 0.25, max_shift_steps=-1)

    def test_guitar_positions_preserve_exact_midi(self) -> None:
        positions = decoder.enumerate_guitar_positions(64)

        self.assertIn(decoder.GuitarPosition(midi=64, string=1, fret=0), positions)
        self.assertIn(decoder.GuitarPosition(midi=64, string=2, fret=5), positions)
        tuning_by_string = {6: 40, 5: 45, 4: 50, 3: 55, 2: 59, 1: 64}
        for position in positions:
            self.assertEqual(tuning_by_string[position.string] + position.fret, 64)
            self.assertGreaterEqual(position.fret, 0)
            self.assertLessEqual(position.fret, 24)

    def test_simultaneous_state_uses_unique_strings_and_preserves_inventory(self) -> None:
        midis = [52, 59, 64]
        states = decoder.enumerate_guitar_states(midis, max_fret_span=7)

        self.assertTrue(states)
        for state in states:
            self.assertEqual(sorted(position.midi for position in state.positions), sorted(midis))
            strings = [position.string for position in state.positions]
            self.assertEqual(len(strings), len(set(strings)))
            self.assertLessEqual(state.fret_span, 7)

    def test_continuity_can_prefer_nearby_fingering_without_pitch_change(self) -> None:
        previous = decoder.GuitarState(
            positions=(decoder.GuitarPosition(midi=64, string=2, fret=5),),
            fret_span=0,
            anchor_fret=5.0,
            local_cost=0.05,
        )

        without_previous = decoder.choose_guitar_state([65])
        with_previous = decoder.choose_guitar_state([65], previous=previous)

        self.assertIsNotNone(without_previous)
        self.assertIsNotNone(with_previous)
        assert without_previous is not None
        assert with_previous is not None
        self.assertEqual(without_previous.positions[0].midi, 65)
        self.assertEqual(with_previous.positions[0].midi, 65)
        self.assertLess(
            decoder.state_transition_cost(previous, with_previous),
            decoder.state_transition_cost(previous, without_previous),
        )

    def test_decode_nearest_path_groups_timing_then_assigns_guitar_state(self) -> None:
        events = [
            {"midi": 52, "onset": 0.24, "confidence": 0.9},
            {"midi": 59, "onset": 0.26, "confidence": 0.8},
            {"midi": 64, "onset": 0.25, "confidence": 0.7},
            {"midi": 65, "onset": 0.51, "confidence": 0.9},
        ]
        original = copy.deepcopy(events)

        result = decoder.decode_nearest_timing_path(events, 0.25)

        self.assertEqual(events, original)
        self.assertEqual(result.evidence_count, 4)
        self.assertEqual(result.decoded_evidence_count, 4)
        self.assertEqual(result.undecoded_onsets, tuple())
        first_onset = [note for note in result.decoded_notes if note.onset == 0.25]
        self.assertEqual(sorted(note.midi for note in first_onset), [52, 59, 64])
        self.assertEqual(len({note.string for note in first_onset}), 3)
        for note in result.decoded_notes:
            tuning_by_string = {6: 40, 5: 45, 4: 50, 3: 55, 2: 59, 1: 64}
            self.assertEqual(tuning_by_string[note.string] + note.fret, note.midi)

    def test_unplayable_evidence_is_left_undecoded(self) -> None:
        result = decoder.decode_nearest_timing_path([{"midi": 100, "onset": 0.24}], 0.25)

        self.assertEqual(result.evidence_count, 1)
        self.assertEqual(result.decoded_evidence_count, 0)
        self.assertEqual(result.decoded_notes, tuple())
        self.assertEqual(result.undecoded_onsets, (0.25,))

    def test_more_than_six_simultaneous_pitches_fails_closed(self) -> None:
        self.assertEqual(decoder.enumerate_guitar_states([52, 53, 54, 55, 56, 57, 58]), tuple())

    def test_public_runtime_api_has_no_label_or_gold_inputs(self) -> None:
        prohibited = {"gold", "reference", "fit", "validation", "canary"}
        public_functions = [
            decoder.normalize_rhythm_events,
            decoder.timing_candidates_for_event,
            decoder.build_timing_lattice,
            decoder.choose_nearest_timing_candidates,
            decoder.enumerate_guitar_positions,
            decoder.enumerate_guitar_states,
            decoder.state_transition_cost,
            decoder.choose_guitar_state,
            decoder.decode_nearest_timing_path,
            decoder.decoded_pitch_inventory,
        ]
        for function in public_functions:
            parameter_names = {name.lower() for name in inspect.signature(function).parameters}
            self.assertTrue(parameter_names.isdisjoint(prohibited), (function.__name__, parameter_names))

    def test_core_has_no_modal_dependency(self) -> None:
        source = Path(decoder.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import modal", source)
        self.assertNotIn("from modal", source)

    def test_decoder_is_deterministic(self) -> None:
        events = [
            {"midi": 52, "onset": 0.24},
            {"midi": 59, "onset": 0.26},
            {"midi": 64, "onset": 0.25},
            {"midi": 65, "onset": 0.51},
        ]
        first = decoder.decode_nearest_timing_path(events, 0.25)
        second = decoder.decode_nearest_timing_path(events, 0.25)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
