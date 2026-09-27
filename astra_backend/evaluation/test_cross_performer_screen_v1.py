import json
import tempfile
import unittest
from pathlib import Path
import zipfile

from evaluation.cross_performer_screen_v1 import (
    AGG_F1_MIN,
    AGG_PRECISION_MIN,
    AGG_RECALL_MIN,
    EACH_EXAMPLE_F1_MIN,
    P2_CAPTURE_KEYS,
    _performance_key_from_path,
    extract_selected_source,
)


class CrossPerformerScreenV1Tests(unittest.TestCase):
    def test_frozen_population_is_exact_four_homologous_p2_directinput(self):
        self.assertEqual(len(P2_CAPTURE_KEYS), 4)
        self.assertEqual(
            set(P2_CAPTURE_KEYS),
            {
                "P2|chords|Drop3_7|directinput",
                "P2|scales|Ab|directinput",
                "P2|singlenotes|allsinglenotes|directinput",
                "P2|techniques|PalmMute|directinput",
            },
        )

    def test_thresholds_match_existing_development_event_gates(self):
        self.assertEqual(AGG_PRECISION_MIN, 0.75)
        self.assertEqual(AGG_RECALL_MIN, 0.60)
        self.assertEqual(AGG_F1_MIN, 0.67)
        self.assertEqual(EACH_EXAMPLE_F1_MIN, 0.55)

    def test_performance_key_parser(self):
        self.assertEqual(_performance_key_from_path(Path("midi/midi_Ab.mid")), "Ab")
        self.assertEqual(
            _performance_key_from_path(Path("directinput/directinput_Drop3_7.wav")),
            "Drop3_7",
        )

    def test_extractor_only_emits_selected_midi_and_directinput(self):
        with tempfile.TemporaryDirectory() as td:
            archive = Path(td) / "P2_scales.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("P2_scales/midi/midi_Ab.mid", b"midi")
                z.writestr("P2_scales/audio/directinput/directinput_Ab.wav", b"wav")
                z.writestr("P2_scales/audio/micamp/micamp_Ab.wav", b"mic")
                z.writestr("P2_scales/midi/midi_A.mid", b"other-midi")
                z.writestr("P2_scales/audio/directinput/directinput_A.wav", b"other")
            out = Path(td) / "out"
            receipt = extract_selected_source(
                archive,
                capture_key="P2|scales|Ab|directinput",
                output_dir=out,
            )
            self.assertFalse(receipt["unrelatedMediaExtracted"])
            self.assertEqual(len(receipt["selectedMembers"]), 2)
            names = {Path(x["path"]).name for x in receipt["selectedMembers"]}
            self.assertEqual(names, {"midi_Ab.mid", "directinput_Ab.wav"})
            self.assertFalse((out / "micamp" / "micamp_Ab.wav").exists())

    def test_p1_and_p3_capture_keys_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            archive = Path(td) / "x.zip"
            with zipfile.ZipFile(archive, "w"):
                pass
            for key in (
                "P1|scales|Ab|directinput",
                "P3|music|x|directinput",
            ):
                with self.assertRaises(ValueError):
                    extract_selected_source(archive, capture_key=key, output_dir=Path(td)/"o")


if __name__ == "__main__":
    unittest.main()
