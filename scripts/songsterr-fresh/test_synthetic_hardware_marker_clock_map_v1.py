import importlib.util
import pathlib
import unittest

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "clockmap", HERE / "synthetic_hardware_marker_clock_map_v1.py"
)
clockmap = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(clockmap)


class ClockMapTests(unittest.TestCase):
    def test_frozen_schedules_and_case_ids(self):
        self.assertEqual(clockmap.SAMPLE_RATE, 48000)
        self.assertEqual(clockmap.MARKER_TICKS, tuple(range(0, 10_000_001, 500_000)))
        self.assertEqual(clockmap.EVALUATION_TICKS, tuple(range(0, 10_000_001, 250_000)))
        self.assertEqual([c["caseId"] for c in clockmap.CASE_DEFINITIONS], [
            "exact_affine", "positive_100ppm", "negative_100ppm",
            "deterministic_marker_jitter_1ms", "quadratic_warp_10ms",
            "quadratic_warp_180ms_stress"
        ])
        self.assertEqual(clockmap.FROZEN_STRUCTURAL_BOUND_SECONDS, 0.025)

    def test_source_has_no_rng_network_or_audio_alignment_dependencies(self):
        text = (HERE / "synthetic_hardware_marker_clock_map_v1.py").read_text()
        for forbidden in (
            "np.random", "numpy.random", "urllib", "requests", "socket",
            "crosscor", "spectrogram", "basic_pitch", "dtw"
        ):
            self.assertNotIn(forbidden, text.lower())

    def test_half_away_nonnegative(self):
        self.assertEqual(clockmap.half_away_nonnegative(0.49), 0)
        self.assertEqual(clockmap.half_away_nonnegative(0.5), 1)
        self.assertEqual(clockmap.half_away_nonnegative(1.5), 2)
        with self.assertRaises(ValueError):
            clockmap.half_away_nonnegative(-0.1)

    def test_nominal_marker_schema(self):
        markers = clockmap.generate_case_markers("exact_affine")
        x, samples, sr = clockmap.validate_markers(markers, 48000)
        self.assertEqual(len(x), 21)
        self.assertEqual(len(samples), 21)
        self.assertEqual(sr, 48000)

    def test_fewer_than_four_markers_rejected(self):
        markers = clockmap.generate_case_markers("exact_affine")[:3]
        with self.assertRaises(ValueError):
            clockmap.validate_markers(markers, 48000)

    def test_skipped_or_duplicate_marker_ids_rejected(self):
        markers = clockmap.generate_case_markers("exact_affine")
        bad = [dict(m) for m in markers]
        bad[3]["markerId"] = 4
        with self.assertRaises(ValueError):
            clockmap.validate_markers(bad, 48000)

    def test_bool_integer_fields_rejected(self):
        markers = clockmap.generate_case_markers("exact_affine")
        bad = [dict(m) for m in markers]
        bad[0]["loggerTick"] = False
        with self.assertRaises(ValueError):
            clockmap.validate_markers(bad, 48000)
        with self.assertRaises(ValueError):
            clockmap.validate_markers(markers, True)

    def test_nonmonotonic_ticks_rejected(self):
        markers = clockmap.generate_case_markers("exact_affine")
        bad = [dict(m) for m in markers]
        bad[5]["loggerTick"] = bad[4]["loggerTick"]
        with self.assertRaises(ValueError):
            clockmap.validate_markers(bad, 48000)

    def test_nonmonotonic_audio_samples_rejected(self):
        markers = clockmap.generate_case_markers("exact_affine")
        bad = [dict(m) for m in markers]
        bad[5]["audioSampleIndex"] = bad[4]["audioSampleIndex"]
        with self.assertRaises(ValueError):
            clockmap.validate_markers(bad, 48000)

    def test_exact_affine_coefficients(self):
        markers = clockmap.generate_case_markers("exact_affine")
        transform = clockmap.fit_clock_map(markers, 48000)
        self.assertAlmostEqual(transform["interceptSeconds"], 0.25, places=14)
        self.assertAlmostEqual(transform["secondsPerLoggerTick"], 1e-6, places=18)
        self.assertEqual(transform["markerCount"], 21)

    def test_all_markers_are_used_no_rejection(self):
        markers = clockmap.generate_case_markers("deterministic_marker_jitter_1ms")
        transform = clockmap.fit_clock_map(markers, 48000)
        self.assertEqual(transform["markerCount"], len(markers))
        self.assertEqual(len(transform["markerResidualSeconds"]), len(markers))

    def test_mapping_equation_exact(self):
        transform = {"interceptSeconds": 0.125, "secondsPerLoggerTick": 1.25e-6}
        ticks = [0, 100, 200]
        mapped = clockmap.map_logger_ticks(transform, ticks)
        expected = np.array([0.125, 0.125125, 0.12525])
        self.assertTrue(np.array_equal(mapped, expected))

    def test_query_ticks_must_be_integer_nonnegative_nondecreasing(self):
        transform = {"interceptSeconds": 0.0, "secondsPerLoggerTick": 1e-6}
        for bad in ([0, -1], [1, 0], [0, 1.5], [False, 1]):
            with self.assertRaises(ValueError):
                clockmap.map_logger_ticks(transform, bad)

    def test_residual_formula(self):
        markers = clockmap.generate_case_markers("deterministic_marker_jitter_1ms")
        t = clockmap.fit_clock_map(markers, 48000)
        x = np.array([m["loggerTick"] for m in markers], dtype=float)
        y = np.array([m["audioSampleIndex"] for m in markers], dtype=float) / 48000.0
        residual = t["interceptSeconds"] + t["secondsPerLoggerTick"] * x - y
        self.assertTrue(np.array_equal(np.asarray(t["markerResidualSeconds"]), residual))
        self.assertEqual(t["maxAbsoluteMarkerResidualSeconds"], float(np.max(np.abs(residual))))
        self.assertEqual(t["rmsMarkerResidualSeconds"], float(np.sqrt(np.mean(residual * residual))))

    def test_marker_input_hash_is_deterministic(self):
        markers = clockmap.generate_case_markers("positive_100ppm")
        a = clockmap.fit_clock_map(markers, 48000)
        b = clockmap.fit_clock_map([dict(m) for m in markers], 48000)
        self.assertEqual(a["markerInputSha256"], b["markerInputSha256"])

    def test_exact_affine_truth_error_near_float_precision(self):
        out = clockmap.evaluate_case("exact_affine")
        self.assertLessEqual(out["maxAbsoluteTruthMappingErrorSeconds"], 1e-14)
        self.assertTrue(out["syntheticTruthWithinFrozen025SecondStructuralBound"])

    def test_harness_is_canonical_and_byte_deterministic(self):
        a = clockmap.run_harness()
        b = clockmap.run_harness()
        self.assertEqual(clockmap.canonical_json_bytes(a), clockmap.canonical_json_bytes(b))
        self.assertEqual(a["caseCount"], 6)
        self.assertTrue(a["allFinite"])

    def test_authorization_boundary_closed(self):
        out = clockmap.run_harness()
        for key, expected in clockmap.AUTHORIZATION_BOUNDARY.items():
            self.assertEqual(out[key], expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
