from __future__ import annotations

import unittest

from v143_rhythm_preexport_validator import validate_v143_preexport_events


def _hypotheses() -> list[dict]:
    return [
        {
            "midi": 40,
            "precisionRetained": True,
            "feasibilityRecovered": False,
        },
        {
            "midi": 47,
            "precisionRetained": False,
            "feasibilityRecovered": True,
        },
    ]


def _legal_recovered_dyad() -> list[dict]:
    hypotheses = _hypotheses()
    return [
        {
            "eventIndex": 0,
            "measure": 1,
            "step": 0,
            "stringIndex": 4,
            "stringName": "A",
            "fret": 2,
            "midi": 47,
            "dominantMidi": 40,
            "pitchHypotheses": hypotheses,
            "noteMapping": {
                "sourceAttackMidi": 40,
                "primaryTechniqueNote": False,
                "chordNoteIndex": 0,
                "chordNoteCount": 2,
                "precisionPitchRetained": False,
                "feasibilityRecoveredSecondary": True,
            },
        },
        {
            "eventIndex": 1,
            "measure": 1,
            "step": 0,
            "stringIndex": 5,
            "stringName": "E",
            "fret": 0,
            "midi": 40,
            "dominantMidi": 40,
            "pitchHypotheses": hypotheses,
            "noteMapping": {
                "sourceAttackMidi": 40,
                "primaryTechniqueNote": True,
                "chordNoteIndex": 1,
                "chordNoteCount": 2,
                "precisionPitchRetained": True,
                "feasibilityRecoveredSecondary": False,
            },
        },
    ]


class RhythmPreExportValidatorTest(unittest.TestCase):
    def test_accepts_legal_recovered_polyphonic_attack(self) -> None:
        diagnostics = validate_v143_preexport_events(
            _legal_recovered_dyad()
        )

        self.assertEqual(diagnostics.event_count, 2)
        self.assertEqual(diagnostics.attack_count, 1)
        self.assertEqual(diagnostics.multi_note_attack_count, 1)
        self.assertEqual(diagnostics.maximum_chord_size, 2)
        self.assertEqual(diagnostics.recovered_secondary_count, 1)

    def test_rejects_duplicate_simultaneous_string(self) -> None:
        events = _legal_recovered_dyad()
        events[1] = dict(events[1])
        events[1]["stringIndex"] = 4
        events[1]["fret"] = -5

        with self.assertRaises(ValueError):
            validate_v143_preexport_events(events)

    def test_rejects_illegal_standard_tuning_mapping(self) -> None:
        events = _legal_recovered_dyad()
        events[0] = dict(events[0])
        events[0]["midi"] = 48

        with self.assertRaises(ValueError):
            validate_v143_preexport_events(events)

    def test_rejects_recovered_note_without_observed_provenance(self) -> None:
        events = _legal_recovered_dyad()
        events[0] = dict(events[0])
        events[0]["pitchHypotheses"] = [
            {
                "midi": 40,
                "precisionRetained": True,
                "feasibilityRecovered": False,
            }
        ]

        with self.assertRaises(ValueError):
            validate_v143_preexport_events(events)

    def test_rejects_missing_or_changed_primary(self) -> None:
        events = _legal_recovered_dyad()
        events[1] = dict(events[1])
        events[1]["noteMapping"] = dict(events[1]["noteMapping"])
        events[1]["noteMapping"]["primaryTechniqueNote"] = False

        with self.assertRaises(ValueError):
            validate_v143_preexport_events(events)

    def test_rejects_unstable_event_order(self) -> None:
        events = list(reversed(_legal_recovered_dyad()))
        events[0] = dict(events[0])
        events[1] = dict(events[1])
        events[0]["eventIndex"] = 0
        events[1]["eventIndex"] = 1

        with self.assertRaises(ValueError):
            validate_v143_preexport_events(events)


if __name__ == "__main__":
    unittest.main()
