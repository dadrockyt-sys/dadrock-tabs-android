import importlib.util
import pathlib
import unittest

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("harness", HERE / "synthetic_six_channel_debleed_v1.py")
harness = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(harness)

EXPECTED_SOURCE_SHA = "8bceb544b681a5b8a507bb7c70aa0f2f379ceec42f2b7b5bf08643e089f2196c"
EXPECTED_PERTURBATION_SHA = "9f6e18edb69aeb8d0d68dcc8c2040f4725339f94ef3f73d1c86aa6cda777da51"


class HarnessTests(unittest.TestCase):
    def test_frozen_dimensions_and_levels(self):
        self.assertEqual(harness.CHANNEL_COUNT, 6)
        self.assertEqual(harness.SAMPLE_COUNT, 8192)
        self.assertEqual(harness.DISTANCE_DECAY_LEVELS, (0.00, 0.02, 0.05, 0.10, 0.20, 0.35, 0.50))
        self.assertEqual(harness.PAIRED_CONDITIONING_LEVELS, (0.10, 0.30, 0.50, 0.70, 0.85, 0.95))
        self.assertEqual(harness.PERTURBATION_LEVELS, (0.0, 0.0001, 0.001, 0.01))
        self.assertEqual(harness.RIDGE_LAMBDA, 1e-4)

    def test_harness_source_has_no_rng_or_network_dependencies(self):
        text = (HERE / "synthetic_six_channel_debleed_v1.py").read_text()
        for forbidden in ("np.random", "numpy.random", "urllib", "requests", "socket", "http://", "https://"):
            self.assertNotIn(forbidden, text)

    def test_source_bank_is_deterministic_finite_rms_one_and_hashed(self):
        a = harness.generate_source_bank()
        b = harness.generate_source_bank()
        self.assertEqual(a.shape, (6, 8192))
        self.assertTrue(np.array_equal(a, b))
        self.assertTrue(np.all(np.isfinite(a)))
        self.assertTrue(np.allclose(np.sqrt(np.mean(a * a, axis=1)), 1.0, atol=1e-14, rtol=0))
        self.assertEqual(harness.array_sha256(a), EXPECTED_SOURCE_SHA)

    def test_perturbation_bank_is_deterministic_finite_rms_one_and_hashed(self):
        a = harness.generate_perturbation_bank()
        b = harness.generate_perturbation_bank()
        self.assertEqual(a.shape, (6, 8192))
        self.assertTrue(np.array_equal(a, b))
        self.assertTrue(np.all(np.isfinite(a)))
        self.assertTrue(np.allclose(np.sqrt(np.mean(a * a, axis=1)), 1.0, atol=1e-14, rtol=0))
        self.assertEqual(harness.array_sha256(a), EXPECTED_PERTURBATION_SHA)

    def test_distance_decay_weights_are_frozen(self):
        w = harness.distance_decay_weights()
        self.assertEqual(w.shape, (6, 6))
        self.assertTrue(np.allclose(np.diag(w), 0.0, atol=0, rtol=0))
        self.assertTrue(np.allclose(np.sum(w, axis=1), 1.0, atol=1e-15, rtol=0))
        self.assertAlmostEqual(w[0, 1] / w[0, 2], 2.0, places=14)

    def test_distance_decay_matrices_have_unit_diagonal_and_frozen_row_bleed(self):
        for level in harness.DISTANCE_DECAY_LEVELS:
            m = harness.build_distance_decay_matrix(level)
            self.assertTrue(np.allclose(np.diag(m), 1.0, atol=0, rtol=0))
            off = m - np.eye(6)
            self.assertTrue(np.allclose(np.sum(off, axis=1), level, atol=1e-15, rtol=0))
        with self.assertRaises(ValueError):
            harness.build_distance_decay_matrix(0.11)

    def test_paired_conditioning_topology_is_frozen(self):
        level = 0.7
        m = harness.build_paired_conditioning_matrix(level)
        expected = np.eye(6)
        for a, b in ((0, 1), (2, 3), (4, 5)):
            expected[a, b] = level
            expected[b, a] = level
        self.assertTrue(np.array_equal(m, expected))
        with self.assertRaises(ValueError):
            harness.build_paired_conditioning_matrix(0.6)

    def test_condition_number_reporting_matches_numpy(self):
        m = harness.build_paired_conditioning_matrix(0.85)
        source = harness.generate_source_bank()
        perturbation = harness.generate_perturbation_bank()
        out = harness.evaluate_matrix_case("paired_conditioning", 0.85, m, source, perturbation)
        self.assertAlmostEqual(out["conditionNumber2"], float(np.linalg.cond(m, 2)), places=14)

    def test_direct_solver_is_exact_frozen_equation(self):
        m = harness.build_distance_decay_matrix(0.35)
        source = harness.generate_source_bank()
        y = m @ source
        expected = np.linalg.solve(m, y)
        actual = harness.recover_direct(m, y)
        self.assertTrue(np.array_equal(actual, expected))

    def test_ridge_solver_is_exact_frozen_equation(self):
        m = harness.build_paired_conditioning_matrix(0.7)
        source = harness.generate_source_bank()
        y = m @ source
        expected = np.linalg.solve(m.T @ m + 1e-4 * np.eye(6), m.T @ y)
        actual = harness.recover_ridge(m, y)
        self.assertTrue(np.array_equal(actual, expected))

    def test_nrmse_formula(self):
        source = harness.generate_source_bank()
        metrics = harness.nrmse_metrics(2.0 * source, source)
        self.assertTrue(np.allclose(metrics["perChannelNrmse"], 1.0, atol=1e-14, rtol=0))
        self.assertAlmostEqual(metrics["pooledNrmse"], 1.0, places=14)
        self.assertAlmostEqual(metrics["maxChannelNrmse"], 1.0, places=14)

    def test_zero_bleed_zero_perturbation_direct_recovery_is_machine_precision(self):
        source = harness.generate_source_bank()
        perturbation = harness.generate_perturbation_bank()
        m = harness.build_distance_decay_matrix(0.0)
        out = harness.evaluate_matrix_case("distance_decay", 0.0, m, source, perturbation)
        zero = out["runs"][0]
        self.assertEqual(zero["perturbationRmsScale"], 0.0)
        self.assertLessEqual(zero["direct"]["pooledNrmse"], 1e-14)

    def test_source_and_perturbation_are_not_mutated(self):
        source = harness.generate_source_bank()
        perturbation = harness.generate_perturbation_bank()
        source_before = source.copy()
        perturbation_before = perturbation.copy()
        m = harness.build_distance_decay_matrix(0.5)
        harness.evaluate_matrix_case("distance_decay", 0.5, m, source, perturbation)
        self.assertTrue(np.array_equal(source, source_before))
        self.assertTrue(np.array_equal(perturbation, perturbation_before))

    def test_run_harness_counts_and_hashes(self):
        out = harness.run_harness()
        self.assertEqual(out["matrixCaseCount"], 13)
        self.assertEqual(out["runCaseCount"], 52)
        self.assertEqual(len(out["cases"]), 13)
        self.assertEqual(out["sourceSha256"], EXPECTED_SOURCE_SHA)
        self.assertEqual(out["perturbationSha256"], EXPECTED_PERTURBATION_SHA)
        self.assertTrue(out["allFinite"])

    def test_canonical_json_is_byte_deterministic(self):
        a = harness.run_harness()
        b = harness.run_harness()
        self.assertEqual(harness.canonical_json_bytes(a), harness.canonical_json_bytes(b))

    def test_authorization_boundary_remains_closed(self):
        self.assertEqual(harness.AUTHORIZATION_BOUNDARY, {
            "basicPitchAuthorized": False,
            "v6Authorized": False,
            "correctnessAuthorized": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
        })
        out = harness.run_harness()
        for key, expected in harness.AUTHORIZATION_BOUNDARY.items():
            self.assertEqual(out[key], expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
