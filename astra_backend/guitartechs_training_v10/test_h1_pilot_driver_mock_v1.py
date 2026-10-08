"""Mock the *actual main function AST*; no torch/model/real features/network needed."""
import argparse
import ast
import contextlib
import io
import json
from pathlib import Path
import platform
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from guitartechs_training_v10 import h1_pilot_readiness_v1 as guards

HERE = Path(__file__).resolve().parent
FOLDS = (
    ("p1-train-p2-validate", "P1", "P2", 41, 120, 40, "a" * 64),
    ("p2-train-p1-validate", "P2", "P1", 40, 136, 41, "b" * 64),
)


def fake_rows():
    rows = []
    for performer, captures, groups in (("P1", 136, 41), ("P2", 120, 40)):
        for i in range(captures):
            rows.append({"key": f"{performer}|chords|g{i%groups}|view{i}",
                         "performer": performer, "category": "chords",
                         "performanceKey": f"g{i%groups}", "frames": 200,
                         "_features": "dummy.features.npy", "_labels": "dummy.labels.npy"})
    return rows


class MockDriver(unittest.TestCase):
    def run_case(self, failing_control=None, unexpected_steps=0):
        rows = fake_rows()
        training_calls = []
        outputs = {}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.jsonl"
            manifest.write_text("synthetic mock manifest\n")
            output = root / "pilot.json"
            def train_arm(subset, fold, arm, source_root, control_sha, before_step, on_step):
                training_calls.append((fold, arm))
                for i in range(40 + unexpected_steps):
                    before_step()
                    on_step(fold, arm, i//2+1, i+1)
                bad_hash = failing_control == "hash" and fold == FOLDS[1][0] and arm == "original_batchmean"
                return {"fold": fold, "arm": arm}, {
                    "arm": arm, "steps": 40 + unexpected_steps,
                    "initialStateSha256": "initial_" + fold,
                    "epoch20Sha256": "mismatch" if bad_hash else control_sha,
                    "matchesFrozenOriginalEpoch20": not bad_hash,
                }
            def evaluate(model, validation, captures, performances):
                is_control = model["arm"] == "original_batchmean"
                bad_admission = is_control and failing_control == "admission"
                return {"metrics": {"f1": 0.0 if is_control else 0.4},
                        "totals": {"predictedEvents": 0 if is_control else 1,
                                   "activeRunsAfterPrune": 1 if bad_admission else (0 if is_control else 1)}}
            stub_np = types.SimpleNamespace(
                __version__="mock-numpy",load=lambda name, **kw: types.SimpleNamespace(
                    shape=(192,200) if ".features." in name else (6,200)))
            stub_core = types.SimpleNamespace(
                FOLDS=FOLDS,EPOCHS=20,SEED=20260921,KL_WEIGHT=.10,
                np=stub_np,train_arm=train_arm,evaluate=evaluate)
            stub_v9 = types.SimpleNamespace(_setup_determinism=lambda: None,
                base=types.SimpleNamespace(load_manifest=lambda *_:rows))
            stub_torch = types.SimpleNamespace(__version__="mock-torch",get_num_threads=lambda:1)
            stub_guards = types.SimpleNamespace(
                ScalarProgress=guards.ScalarProgress,require_zero_control=guards.require_zero_control,
                sha256_file=guards.sha256_file,verify_population=lambda *_: {"captureCount":256})
            source = (HERE / "run_h1_20epoch_paired_pilot_v1.py").read_text()
            syntax = ast.parse(source)
            main = next(node for node in syntax.body if isinstance(node,ast.FunctionDef) and node.name == "main")
            env = {
                "argparse": argparse,"json": json,"Path": Path, "platform": platform,
                "sys":sys,"torch":stub_torch,"v9":stub_v9,"core":stub_core,
                "safety":stub_guards,"HERE":HERE,
                "CANDIDATE":"synthetic_h1_mock","SCHEMA":"synthetic_mock",
            }
            exec(compile(ast.Module(body=[main], type_ignores=[]), "driver-main-ast", "exec"),env)
            args = ["mock-driver","--source-root",str(root),"--manifest",str(manifest),
                    "--data-dir",str(root),"--out",str(output)]
            try:
                with patch.object(sys,"argv",args),contextlib.redirect_stdout(io.StringIO()):
                    env["main"]()
            except Exception as exc:
                outputs["error"] = exc
            progress = output.with_suffix(".progress.json")
            outputs["calls"] = list(training_calls)
            outputs["journal"] = json.loads(progress.read_text()) if progress.exists() else None
            outputs["result"] = json.loads(output.read_text()) if output.exists() else None
        return outputs

    def test_two_controls_precede_treatments(self):
        state = self.run_case()
        self.assertNotIn("error",state)
        self.assertEqual([arm for _,arm in state["calls"]],
                         ["original_batchmean"]*2+["per_position_normalized"]*2)
        self.assertEqual(state["journal"]["optimizerStepsConfirmed"],160)
        self.assertEqual(state["journal"]["status"],"completed")
        self.assertEqual(len(state["journal"]["armResults"]),4)
        self.assertEqual(state["result"]["optimizerSteps"],160)

    def test_control_admission_blocks_treatment_and_writes_failure(self):
        state = self.run_case(failing_control="admission")
        self.assertIsInstance(state["error"],RuntimeError)
        self.assertIn("ORIGINAL_CONTROL_NONZERO_ADMISSION",str(state["error"]))
        self.assertEqual(state["calls"],[ (FOLDS[0][0],"original_batchmean") ])
        self.assertEqual(state["journal"]["optimizerStepsConfirmed"],40)
        self.assertEqual(state["journal"]["status"],"failed")
        self.assertIsNone(state["result"])

    def test_original_hash_mismatch_blocks_treatment(self):
        state = self.run_case(failing_control="hash")
        self.assertIn("ORIGINAL_EPOCH20_SHA_REPRODUCTION_FAILED",str(state["error"]))
        self.assertEqual(len(state["calls"]),2)
        self.assertEqual(state["journal"]["optimizerStepsConfirmed"],80)
        self.assertIsNone(state["result"])

    def test_cap_stops_extra_mock_steps(self):
        state = self.run_case(unexpected_steps=1)
        self.assertIn("H1_GLOBAL_STEP_CAP_EXHAUSTED",str(state["error"]))
        self.assertEqual(state["journal"]["optimizerStepsConfirmed"],160)
        self.assertIsNone(state["result"])


if __name__ == "__main__":
    unittest.main()
