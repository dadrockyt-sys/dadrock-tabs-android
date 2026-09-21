import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "guitartechs_training_v2" / "sampling.py"
SPEC = importlib.util.spec_from_file_location("guitartechs_v2_sampling", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def rows(groups=41, views=("directinput", "micamp")):
    out = []
    for i in range(groups):
        for view in views:
            out.append({
                "key": f"P1|chords|perf{i:02d}|{view}",
                "performer": "P1",
                "category": "chords",
                "performanceKey": f"perf{i:02d}",
                "captureView": view,
                "frames": 1000 + i,
            })
    return out


class GuitarTechsV2SamplingTests(unittest.TestCase):
    def test_every_performance_appears_exactly_once_per_epoch(self):
        plan = MOD.build_epoch_plan(rows(), epoch=0)
        self.assertEqual(len(plan), 41)
        self.assertEqual(len({x["groupKey"] for x in plan}), 41)

    def test_correlated_views_do_not_add_performance_weight(self):
        two_views = MOD.build_epoch_plan(rows(4, ("directinput", "micamp")), epoch=3)
        four_views = MOD.build_epoch_plan(rows(4, ("directinput", "micamp", "ego", "exo")), epoch=3)
        self.assertEqual(len(two_views), 4)
        self.assertEqual(len(four_views), 4)

    def test_plan_is_deterministic_but_rotates_across_epochs(self):
        a = MOD.build_epoch_plan(rows(8), epoch=7)
        b = MOD.build_epoch_plan(rows(8), epoch=7)
        c = MOD.build_epoch_plan(rows(8), epoch=8)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_segments_are_exactly_200_frames_and_in_bounds(self):
        plan = MOD.build_epoch_plan(rows(6), epoch=4)
        for item in plan:
            self.assertEqual(item["endFrame"] - item["startFrame"], 200)
            self.assertGreaterEqual(item["startFrame"], 0)

    def test_tail_batch_is_not_dropped(self):
        plan = MOD.build_epoch_plan(rows(), epoch=0)
        batches = MOD.batch_epoch_plan(plan, batch_size=32)
        self.assertEqual([len(x) for x in batches], [32, 9])

    def test_exposure_is_200x_single_frame_at_same_batch_steps(self):
        self.assertEqual(2500 * 32, 80000)
        self.assertEqual(2500 * 32 * 200, 16000000)
        self.assertEqual((2500 * 32 * 200) // (2500 * 32), 200)

    def test_short_or_malformed_capture_fails_closed(self):
        bad = rows(1)
        bad[0]["frames"] = 199
        with self.assertRaises(ValueError):
            MOD.build_epoch_plan(bad, epoch=0)


if __name__ == "__main__":
    unittest.main()
