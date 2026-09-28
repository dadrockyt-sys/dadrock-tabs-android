import math
import unittest

from .post_a1_result_validator_v1 import ValidationError, validate_result

SEEDS = [20260927, 20260928, 20260929]
IDS = {"control": "c", "intervention": "i", "challenge": "q"}


def metrics(x):
    return {
        "stateAdmission": x,
        "jointAdmission": x,
        "onsetPrecision": x,
        "onsetRecall": x,
        "onsetF1": x,
        "negativeFpEvents": 0,
        "negativeSeconds": 6.0,
        "negativeFpPerSecond": 0.0,
    }


def fixture():
    rows = []
    for seed in SEEDS:
        domains = {}
        for domain in ("ordinary", "challenge"):
            candidate = metrics(0.5)
            comparator = metrics(0.4)
            domains[domain] = {
                "candidate": candidate,
                "comparator": comparator,
                "delta": {
                    key: 0.1
                    for key in (
                        "stateAdmission",
                        "jointAdmission",
                        "onsetPrecision",
                        "onsetRecall",
                        "onsetF1",
                    )
                },
            }
        rows.append({"seed": seed, "optimizerSteps": 500, **domains})
    return {
        "schema": "future-result-v1",
        "identities": IDS,
        "rows": rows,
        "execution": {"modelCount": 3, "optimizerStepsTotal": 1500},
    }


def check(obj):
    return validate_result(
        obj,
        expected_schema="future-result-v1",
        expected_seeds=SEEDS,
        expected_steps_per_model=500,
        expected_model_count=3,
        expected_total_steps=1500,
        expected_identities=IDS,
    )


class TestValidator(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(check(fixture()))

    def test_duplicate_seed_rejected(self):
        x = fixture()
        x["rows"][1]["seed"] = x["rows"][0]["seed"]
        with self.assertRaises(ValidationError):
            check(x)

    def test_missing_metric_rejected(self):
        x = fixture()
        del x["rows"][0]["ordinary"]["candidate"]["onsetF1"]
        with self.assertRaises(ValidationError):
            check(x)

    def test_boolean_rejected_as_number(self):
        x = fixture()
        x["rows"][0]["ordinary"]["candidate"]["onsetF1"] = True
        with self.assertRaises(ValidationError):
            check(x)

    def test_nan_rejected(self):
        x = fixture()
        x["rows"][0]["ordinary"]["candidate"]["onsetF1"] = math.nan
        with self.assertRaises(ValidationError):
            check(x)

    def test_impossible_fraction_rejected(self):
        x = fixture()
        x["rows"][0]["ordinary"]["candidate"]["stateAdmission"] = 1.1
        with self.assertRaises(ValidationError):
            check(x)

    def test_inconsistent_delta_rejected(self):
        x = fixture()
        x["rows"][0]["ordinary"]["delta"]["jointAdmission"] = 0.2
        with self.assertRaises(ValidationError):
            check(x)

    def test_inconsistent_fp_rate_rejected(self):
        x = fixture()
        x["rows"][0]["ordinary"]["candidate"].update(
            negativeFpEvents=1, negativeFpPerSecond=0.0
        )
        with self.assertRaises(ValidationError):
            check(x)

    def test_identity_mismatch_rejected(self):
        x = fixture()
        x["identities"] = {"control": "wrong"}
        with self.assertRaises(ValidationError):
            check(x)

    def test_step_total_rejected(self):
        x = fixture()
        x["execution"]["optimizerStepsTotal"] = 1499
        with self.assertRaises(ValidationError):
            check(x)


if __name__ == "__main__":
    unittest.main()
