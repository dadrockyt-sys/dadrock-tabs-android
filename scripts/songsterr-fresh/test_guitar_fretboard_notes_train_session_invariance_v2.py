import importlib.util
import json
import pathlib
import tempfile
import unittest

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "probe", HERE / "guitar_fretboard_notes_train_session_invariance_v2.py"
)
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


def synthetic_feature_rows(session_offsets=None):
    session_offsets = session_offsets or {"ele": 2.0, "eqm": 0.0, "eqm2": 5.0}
    rows = []
    open_midis = {1: 64, 2: 59, 3: 55, 4: 50, 5: 45, 6: 40}
    for source in probe.ALLOWED_SOURCES:
        offset = float(session_offsets[source])
        for string_number in range(1, 7):
            for fret in range(13):
                midi = open_midis[string_number] + fret
                vec = np.zeros(16, dtype=np.float64)
                vec[(string_number - 1) % 12] = 3.0 + 0.03 * fret
                vec[6] = 0.1 * fret
                vec[7] = 0.2 * string_number
                vec[12:] = np.array([0.1, 0.2, 0.3, 0.4]) + 0.005 * fret
                vec = vec + offset
                rows.append({
                    "source": source,
                    "string_number": string_number,
                    "fret": fret,
                    "midi_number": midi,
                    "features": vec.tolist(),
                })
    return rows


def tone(f0, harmonic_shape, sr=44100, seconds=2.0):
    t = np.arange(int(sr * seconds), dtype=np.float64) / sr
    x = np.zeros_like(t)
    for h, amp in enumerate(harmonic_shape, start=1):
        x += amp * np.sin(2 * np.pi * f0 * h * t)
    return x * np.exp(-0.9 * t)


class ProbeTests(unittest.TestCase):
    def test_access_constants_are_train_only(self):
        self.assertEqual(probe.ALLOWED_SOURCES, ("ele", "eqm", "eqm2"))
        self.assertEqual(probe.RESERVED_SOURCES, ("deb", "ele_natural"))
        self.assertIn("train-00000-of-00001.parquet", probe.TRAIN_URL)
        self.assertNotIn("deb", probe.TRAIN_URL)
        self.assertNotIn("ele_natural", probe.TRAIN_URL)
        self.assertEqual(
            probe.DATASET_REVISION,
            "a33a26243e88e7ccd4893bee30eac3219ec8bef8",
        )

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

    def test_sha_gate_fails_closed(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"not-the-pinned-train-parquet")
            f.flush()
            with self.assertRaises(ValueError):
                probe.validate_train_parquet_sha(f.name)

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

    def test_silence_and_wrong_sample_rate_fail_closed(self):
        with self.assertRaises(ValueError):
            probe.extract_features(np.zeros(44100), 44100, 110.0)
        with self.assertRaises(ValueError):
            probe.extract_features(np.ones(44100), 48000, 110.0)

    def test_source_robust_normalization_is_deterministic_and_order_independent(self):
        rows = synthetic_feature_rows()
        a_rows, a_summary = probe.normalize_feature_rows(rows)
        b_rows, b_summary = probe.normalize_feature_rows(list(reversed(rows)))
        self.assertEqual(probe.canonical_json_bytes(a_rows), probe.canonical_json_bytes(b_rows))
        self.assertEqual(probe.canonical_json_bytes(a_summary), probe.canonical_json_bytes(b_summary))
        self.assertEqual(len(a_rows), 234)
        for source in probe.ALLOWED_SOURCES:
            self.assertTrue(a_summary[source]["allFinite"])

    def test_normalization_fallbacks_are_frozen(self):
        matrix = np.zeros((78, 16), dtype=np.float64)
        matrix[:, 0] = np.arange(78, dtype=np.float64)
        matrix[:, 1] = 5.0
        median, scale, methods = probe._source_normalization_stats(matrix)
        self.assertTrue(np.all(np.isfinite(median)))
        self.assertTrue(np.all(np.isfinite(scale)))
        self.assertEqual(methods[0], "mad")
        self.assertEqual(methods[1], "unit")
        self.assertEqual(scale[1], 1.0)

    def test_same_midi_restriction_and_matching(self):
        rows, _ = probe.normalize_feature_rows(synthetic_feature_rows())
        out = probe.evaluate_direction(rows, "eqm", "eqm2")
        self.assertEqual(out["eligibleQueryCount"], 68)
        self.assertEqual(out["correctCount"], 68)
        self.assertEqual(out["exactPositionAccuracy"], 1.0)
        for value in out["perMidi"].values():
            self.assertGreaterEqual(value["candidateCount"], 2)

    def test_tie_break_is_string_then_fret(self):
        rows = synthetic_feature_rows({"ele": 0.0, "eqm": 0.0, "eqm2": 0.0})
        for row in rows:
            row["features"] = np.zeros(16).tolist()
        normalized, _ = probe.normalize_feature_rows(rows)
        out = probe.evaluate_direction(normalized, "eqm", "eqm2")
        midi45 = out["perMidi"]["45"]
        self.assertEqual(midi45["candidateCount"], 2)
        self.assertEqual(midi45["queries"], 2)
        self.assertEqual(midi45["correct"], 1)

    def test_primary_and_ele_diagnostics_are_separate(self):
        normalized, _ = probe.normalize_feature_rows(synthetic_feature_rows())
        out = probe.evaluate_all(normalized)
        self.assertEqual(
            [(d["prototypeSource"], d["querySource"]) for d in out["primary"]["directions"]],
            list(probe.PRIMARY_DIRECTIONS),
        )
        self.assertEqual(
            [(d["prototypeSource"], d["querySource"]) for d in out["diagnosticEleDirections"]],
            list(probe.DIAGNOSTIC_DIRECTIONS),
        )
        self.assertEqual(out["primary"]["pooled"]["eligibleQueryCount"], 136)

    def test_interpretation_rule_is_frozen(self):
        self.assertEqual(probe.classify_session_invariance(0.60, 0.10), "SESSION_INVARIANCE_IMPROVED")
        self.assertEqual(probe.classify_session_invariance(0.60, 0.20), "MIXED")
        self.assertEqual(probe.classify_session_invariance(0.50, 0.10), "MIXED")
        self.assertEqual(probe.classify_session_invariance(0.50, 0.20), "NO_IMPROVEMENT")
        self.assertEqual(
            probe.classify_session_invariance(probe.V1_POOLED_ACCURACY, probe.V1_DIRECTIONAL_GAP),
            "NO_IMPROVEMENT",
        )

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
        self.assertEqual(
            probe.canonical_json_bytes(value),
            probe.canonical_json_bytes(json.loads(json.dumps(value))),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
