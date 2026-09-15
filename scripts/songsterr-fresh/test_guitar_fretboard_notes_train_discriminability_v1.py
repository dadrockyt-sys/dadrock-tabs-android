import importlib.util
import json
import pathlib
import unittest

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("probe", HERE / "guitar_fretboard_notes_train_discriminability_v1.py")
probe = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(probe)


def metadata_rows():
    open_midis = {1: 64, 2: 59, 3: 55, 4: 50, 5: 45, 6: 40}
    rows = []
    for source in probe.ALLOWED_SOURCES:
        for string_number in range(1, 7):
            for fret in range(13):
                rows.append({
                    "source": source,
                    "string_number": string_number,
                    "fret": fret,
                    "midi_number": open_midis[string_number] + fret,
                })
    return rows


def tone(f0, harmonic_shape, sr=44100, seconds=2.0):
    t = np.arange(int(sr * seconds), dtype=np.float64) / sr
    x = np.zeros_like(t)
    for h, amp in enumerate(harmonic_shape, start=1):
        x += amp * np.sin(2 * np.pi * f0 * h * t)
    return x * np.exp(-0.9 * t)


class ProbeTests(unittest.TestCase):
    def test_metadata_nominal(self):
        out = probe.validate_metadata_rows(metadata_rows())
        self.assertEqual(out["rowCount"], 234)
        self.assertEqual(out["observedSources"], ["ele", "eqm", "eqm2"])

    def test_reserved_source_fails_closed(self):
        rows = metadata_rows()
        rows[0]["source"] = "deb"
        with self.assertRaises(ValueError):
            probe.validate_metadata_rows(rows)

    def test_wrong_count_fails_closed(self):
        with self.assertRaises(ValueError):
            probe.validate_metadata_rows(metadata_rows()[:-1])

    def test_duplicate_identity_fails_closed(self):
        rows = metadata_rows()
        rows[-1] = dict(rows[-2])
        with self.assertRaises(ValueError):
            probe.validate_metadata_rows(rows)

    def test_boolean_integer_metadata_rejected(self):
        rows = metadata_rows()
        rows[0]["fret"] = False
        with self.assertRaises(ValueError):
            probe.validate_metadata_rows(rows)

    def test_feature_vector_is_16_finite_values(self):
        x = tone(110.0, [1.0, 0.5, 0.3, 0.2, 0.1, 0.05])
        f = probe.extract_features(x, 44100, 110.0)
        self.assertEqual(f.shape, (16,))
        self.assertTrue(np.all(np.isfinite(f)))
        self.assertAlmostEqual(float(f[0]), 0.0, places=12)
        self.assertAlmostEqual(float(np.sum(f[12:])), 1.0, places=9)

    def test_feature_extraction_is_deterministic(self):
        x = tone(146.8324, [1.0, 0.2, 0.7, 0.1, 0.4])
        a = probe.extract_features(x, 44100, 146.8324)
        b = probe.extract_features(x.copy(), 44100, 146.8324)
        self.assertTrue(np.array_equal(a, b))

    def test_silence_fails_closed(self):
        with self.assertRaises(ValueError):
            probe.extract_features(np.zeros(44100), 44100, 110.0)

    def test_wrong_sample_rate_fails_closed(self):
        with self.assertRaises(ValueError):
            probe.extract_features(np.ones(44100), 48000, 110.0)

    def test_cross_session_matching_recovers_position_signal(self):
        rows = []
        for source, delta in (("eqm", 0.0), ("eqm2", 0.02)):
            idx = 0
            for s in range(1, 7):
                for fret in range(13):
                    midi = 1000 + idx
                    base = np.zeros(16, dtype=float)
                    base[(s - 1) % 12] = 2.0 + 0.01 * fret
                    if (s, fret) == (6, 5):
                        midi = 45
                        base = np.array([0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .4, .3, .2, .1], dtype=float)
                    elif (s, fret) == (5, 0):
                        midi = 45
                        base = np.array([0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .1, .2, .3, .4], dtype=float)
                    rows.append({
                        "source": source,
                        "string_number": s,
                        "fret": fret,
                        "midi_number": midi,
                        "features": (base + delta).tolist(),
                    })
                    idx += 1
        for s in range(1, 7):
            for fret in range(13):
                rows.append({"source": "ele", "string_number": s, "fret": fret, "midi_number": 2000 + s * 20 + fret, "features": np.zeros(16).tolist()})
        out = probe.evaluate_primary(rows)
        self.assertEqual(out["pooled"]["eligibleQueryCount"], 4)
        self.assertEqual(out["pooled"]["correctCount"], 4)
        self.assertEqual(out["pooled"]["exactPositionAccuracy"], 1.0)
        self.assertEqual(out["pooled"]["chanceBaseline"], 0.5)

    def test_candidate_tie_break_is_string_then_fret(self):
        rows = []
        for source in ("eqm", "eqm2"):
            for s in range(1, 7):
                for fret in range(13):
                    midi = 1000 + s * 20 + fret
                    if (s, fret) in ((5, 0), (6, 5)):
                        midi = 45
                    rows.append({"source": source, "string_number": s, "fret": fret, "midi_number": midi, "features": np.zeros(16).tolist()})
        out = probe.evaluate_direction(rows, "eqm", "eqm2")
        self.assertEqual(out["eligibleQueryCount"], 2)
        self.assertEqual(out["correctCount"], 1)

    def test_authorization_boundary_is_closed(self):
        self.assertEqual(probe.AUTHORIZATION_BOUNDARY, {
            "basicPitchAuthorized": False,
            "v6Authorized": False,
            "correctnessAuthorized": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
        })

    def test_canonical_json_is_byte_identical(self):
        value = {"z": 1, "a": [3, 2, 1], "nested": {"b": False, "a": 1}}
        self.assertEqual(probe.canonical_json_bytes(value), probe.canonical_json_bytes(json.loads(json.dumps(value))))


if __name__ == "__main__":
    unittest.main(verbosity=2)
