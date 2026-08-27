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

import v145_rhythm_decoder as stage1  # noqa: E402
import v145_rhythm_sequence_decoder as stage2  # noqa: E402


def grid(quantum: float = 0.25, phase: float = 0.0) -> stage2.InferredTimingGrid:
    return stage2.InferredTimingGrid(
        quantum=quantum,
        phase=phase,
        support=1.0,
        median_normalized_residual=0.0,
        mean_normalized_residual=0.0,
        evidence_count=8,
        candidate_count=1,
    )


def evidence(source_index: int, midi: int, onset: float) -> stage1.EvidenceEvent:
    return stage1.EvidenceEvent(
        source_index=source_index,
        midi=midi,
        onset=onset,
        duration=0.0,
        confidence=1.0,
    )


class V145RhythmSequenceDecoderTests(unittest.TestCase):
    def test_infers_quarter_second_grid_from_jittered_generated_onsets(self) -> None:
        events = [
            {"midi": 52, "onset": 0.011},
            {"midi": 54, "onset": 0.249},
            {"midi": 55, "onset": 0.503},
            {"midi": 57, "onset": 0.748},
            {"midi": 59, "onset": 1.002},
            {"midi": 60, "onset": 1.249},
        ]

        inferred = stage2.infer_timing_grid(events)

        self.assertIsNotNone(inferred)
        assert inferred is not None
        self.assertGreaterEqual(inferred.quantum, 0.24)
        self.assertLessEqual(inferred.quantum, 0.26)
        self.assertGreaterEqual(inferred.support, 0.80)
        self.assertLessEqual(inferred.median_normalized_residual, 0.12)

    def test_rejects_irregular_unsupported_generated_onsets(self) -> None:
        onsets = [
            0.000,
            0.071,
            0.193,
            0.362,
            0.589,
            0.881,
            1.238,
            1.659,
            2.143,
            2.692,
            3.307,
            3.991,
            4.742,
            5.561,
            6.449,
            7.406,
        ]
        events = [{"midi": 52 + (index % 8), "onset": onset} for index, onset in enumerate(onsets)]

        self.assertIsNone(stage2.infer_timing_grid(events))

    def test_requires_minimum_evidence_count(self) -> None:
        events = [
            {"midi": 52, "onset": 0.0},
            {"midi": 54, "onset": 0.25},
            {"midi": 55, "onset": 0.5},
        ]
        self.assertIsNone(stage2.infer_timing_grid(events))

    def test_clusters_near_simultaneous_attacks_from_first_raw_onset(self) -> None:
        rows = (
            evidence(0, 52, 0.100),
            evidence(1, 59, 0.135),
            evidence(2, 64, 0.190),
            evidence(3, 65, 0.400),
        )

        clusters = stage2.cluster_evidence(rows, 0.25)

        self.assertEqual(len(clusters), 3)
        self.assertEqual([event.source_index for event in clusters[0].events], [0, 1])
        self.assertEqual([event.source_index for event in clusters[1].events], [2])
        self.assertEqual([event.source_index for event in clusters[2].events], [3])

    def test_cluster_options_require_one_common_onset_and_unique_strings(self) -> None:
        cluster = stage2.EvidenceCluster(
            cluster_index=0,
            events=(evidence(0, 52, 0.24), evidence(1, 59, 0.26), evidence(2, 64, 0.25)),
        )

        options = stage2.cluster_options(cluster, grid())

        self.assertTrue(options)
        for option in options:
            self.assertTrue(all(row.candidate_onset == option.onset for row in option.timing_candidates))
            self.assertEqual(sorted(row.midi for row in option.timing_candidates), [52, 59, 64])
            strings = [position.string for position in option.guitar_state.positions]
            self.assertEqual(len(strings), len(set(strings)))
            self.assertEqual(sorted(position.midi for position in option.guitar_state.positions), [52, 59, 64])

    def test_global_sequence_uses_each_source_event_at_most_once(self) -> None:
        events = [
            {"midi": 52, "onset": 0.010},
            {"midi": 59, "onset": 0.018},
            {"midi": 54, "onset": 0.252},
            {"midi": 55, "onset": 0.498},
            {"midi": 57, "onset": 0.751},
            {"midi": 59, "onset": 1.001},
            {"midi": 60, "onset": 1.249},
        ]
        original = copy.deepcopy(events)

        result = stage2.decode_global_rhythm_sequence(events)

        self.assertEqual(events, original)
        self.assertIsNotNone(result.grid)
        source_indices = [note.source_index for note in result.decoded_notes]
        self.assertEqual(len(source_indices), len(set(source_indices)))
        self.assertTrue(set(source_indices).isdisjoint(result.undecoded_source_indices))
        for note in result.decoded_notes:
            self.assertEqual(note.midi, int(round(events[note.source_index]["midi"])))

    def test_global_sequence_requires_strictly_increasing_cluster_onsets(self) -> None:
        clusters = (
            stage2.EvidenceCluster(0, (evidence(0, 52, 0.24),)),
            stage2.EvidenceCluster(1, (evidence(1, 54, 0.26),)),
            stage2.EvidenceCluster(2, (evidence(2, 55, 0.51),)),
        )

        selected, _ = stage2.select_global_sequence(clusters, grid())

        selected_onsets = [option.onset for option in selected]
        self.assertEqual(selected_onsets, sorted(selected_onsets))
        self.assertEqual(len(selected_onsets), len(set(selected_onsets)))

    def test_global_continuity_can_override_locally_cheapest_fingering(self) -> None:
        clusters = (
            stage2.EvidenceCluster(
                0,
                (evidence(0, 72, 0.000), evidence(1, 72, 0.010)),
            ),
            stage2.EvidenceCluster(
                1,
                (evidence(2, 65, 0.250),),
            ),
        )

        selected, undecoded = stage2.select_global_sequence(clusters, grid())
        standalone = stage1.choose_guitar_state([65])

        self.assertEqual(undecoded, tuple())
        self.assertEqual(len(selected), 2)
        self.assertIsNotNone(standalone)
        assert standalone is not None
        global_second = selected[1].guitar_state.positions[0]
        local_second = standalone.positions[0]
        self.assertEqual(global_second.midi, 65)
        self.assertEqual(local_second.midi, 65)
        self.assertNotEqual(global_second.fret, local_second.fret)
        self.assertLess(
            stage1.state_transition_cost(selected[0].guitar_state, selected[1].guitar_state),
            stage1.state_transition_cost(selected[0].guitar_state, standalone),
        )

    def test_more_than_six_note_cluster_fails_closed(self) -> None:
        cluster = stage2.EvidenceCluster(
            0,
            tuple(evidence(index, 52 + index, 0.01 * index) for index in range(7)),
        )
        self.assertEqual(stage2.cluster_options(cluster, grid()), tuple())

    def test_unplayable_cluster_fails_closed(self) -> None:
        cluster = stage2.EvidenceCluster(0, (evidence(0, 100, 0.0),))
        self.assertEqual(stage2.cluster_options(cluster, grid()), tuple())

    def test_unsupported_grid_decode_returns_no_fabricated_notes(self) -> None:
        events = [
            {"midi": 52, "onset": 0.000},
            {"midi": 54, "onset": 0.071},
            {"midi": 55, "onset": 0.193},
        ]

        result = stage2.decode_global_rhythm_sequence(events)

        self.assertIsNone(result.grid)
        self.assertEqual(result.decoded_notes, tuple())
        self.assertEqual(result.undecoded_source_indices, (0, 1, 2))

    def test_public_runtime_api_has_no_label_or_gold_inputs(self) -> None:
        prohibited = {"gold", "reference", "fit", "validation", "canary"}
        public_functions = [
            stage2.infer_timing_grid_from_evidence,
            stage2.infer_timing_grid,
            stage2.cluster_evidence,
            stage2.cluster_options,
            stage2.select_global_sequence,
            stage2.decode_global_rhythm_sequence,
        ]
        for function in public_functions:
            names = {name.lower() for name in inspect.signature(function).parameters}
            self.assertTrue(names.isdisjoint(prohibited), (function.__name__, names))

    def test_stage2_has_no_modal_dependency(self) -> None:
        source = Path(stage2.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import modal", source)
        self.assertNotIn("from modal", source)

    def test_stage2_is_deterministic(self) -> None:
        events = [
            {"midi": 52, "onset": 0.011},
            {"midi": 59, "onset": 0.015},
            {"midi": 54, "onset": 0.249},
            {"midi": 55, "onset": 0.503},
            {"midi": 57, "onset": 0.748},
            {"midi": 59, "onset": 1.002},
            {"midi": 60, "onset": 1.249},
        ]
        first = stage2.decode_global_rhythm_sequence(events)
        second = stage2.decode_global_rhythm_sequence(events)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
