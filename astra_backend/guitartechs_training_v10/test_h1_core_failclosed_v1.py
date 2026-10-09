"""No-media AST tests for the *committed* H1 core train/evaluate functions."""
from __future__ import annotations
import ast
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import tempfile
import time
import types
import unittest
import numpy as np
import torch

SOURCE=Path(__file__).with_name("h1_pilot_core_v1.py")
METRICS=("precision","recall","f1","completeness","frameAccuracy","abstentionRate")
AUDITS=("predictedEvents","referenceEvents","truePositiveEvents",
        "stateArgmaxActivePositions","activeRunsBeforeGapMerge","activeRunsAfterPrune",
        "strongStartCandidates","confirmedStartCandidates",
        "acceptedStrongStarts","acceptedConfirmedStarts")


def source_function(name, env):
    tree=ast.parse(SOURCE.read_text(encoding="utf-8"))
    fn=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name==name)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),str(SOURCE),"exec"),env)
    return env[name]


class EvaluationFailures(unittest.TestCase):
    def exercise(self, audit_patch=None, capture_patch=None, macro_patch=None):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            f=root/"f.npy"; r=root/"r.npy"
            np.save(f,np.zeros((192,12),np.float32),allow_pickle=False)
            np.save(r,np.full((6,12),-1,np.int64),allow_pickle=False)
            audit={key:0 for key in AUDITS}
            metric={key:0.0 for key in METRICS}
            summary={**metric,"captureCount":1,"performanceCount":1}
            if audit_patch:audit.update(audit_patch)
            if capture_patch:metric.update(capture_patch)
            if macro_patch:summary.update(macro_patch)
            env={
                "np":np,"math":math,
                "infer_raw":lambda m,x:(np.zeros((12,6,21)),np.zeros((12,6))),
                "summarize_capture":lambda a,b,ref:(np.full((12,6),-1),audit),
                "metric_base":types.SimpleNamespace(capture_metrics=lambda a,b:metric),
                "aggregate":lambda caps:summary,
            }
            run=source_function("evaluate",env)
            return run(types.SimpleNamespace(eval=lambda:None),[
                {"_features":str(f),"_labels":str(r),
                 "performer":"P2","category":"chords","performanceKey":"synthetic"}],1,1)

    def test_synthetic_valid(self):
        self.assertEqual(self.exercise()["totals"]["activeRunsAfterPrune"],0)

    def test_nonfinite_capture_metrics(self):
        for wrong in (float("nan"),float("inf")):
            with self.subTest(wrong=wrong),self.assertRaisesRegex(RuntimeError,"NONFINITE_OR_MISSING_CAPTURE"):
                self.exercise(capture_patch={"f1":wrong})

    def test_all_event_fields_are_required_including_nonnegative_ints(self):
        for wrong in (-1,True,None):
            with self.subTest(wrong=wrong),self.assertRaisesRegex(RuntimeError,"INVALID_EVENT_COUNTER_SCHEMA"):
                self.exercise(audit_patch={"acceptedConfirmedStarts":wrong})
        with self.assertRaisesRegex(RuntimeError,"INVALID_EVENT_COUNTER_SCHEMA"):
            self.exercise(audit_patch={"activeRunsBeforeGapMerge":None})

    def test_impossible_matching_and_bad_macro(self):
        with self.assertRaisesRegex(RuntimeError,"IMPOSSIBLE_EVENT_COUNTS"):
            self.exercise(audit_patch={"truePositiveEvents":1})
        with self.assertRaisesRegex(RuntimeError,"count drift"):
            self.exercise(macro_patch={"performanceCount":2})
        with self.assertRaisesRegex(RuntimeError,"NONFINITE_OR_MISSING_MACRO"):
            self.exercise(macro_patch={"f1":float("nan")})


class TrainingStepFailures(unittest.TestCase):
    @staticmethod
    def rows():
        return [{"key":"k","performer":"P1","category":"chords",
                 "performanceKey":f"piece{i}"} for i in range(40)]

    def setup_core(self):
        counters={"before":0,"after":0,"updates":0}
        class Tiny(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.w=torch.nn.Parameter(torch.tensor(1.))
            def forward(self,features):
                return {"value":self.w*1.0}
        class CountSGD(torch.optim.SGD):
            def step(self,*args,**kwargs):
                counters["updates"]+=1
                return super().step(*args,**kwargs)
        def factory():
            model=Tiny()
            return model,CountSGD(model.parameters(),lr=.1)
        v9=types.SimpleNamespace(
            _setup_determinism=lambda:None,
            _new_model_and_optimizer=lambda root:factory(),
            _training_content_weights=lambda rows:{"chords":1.},
            _content_name=lambda x:x,
            build_epoch_plan=lambda rows,epoch:list(range(40)),
            batch_epoch_plan=lambda plan,batch_size:[
                [{"captureKey":"k","startFrame":0}],
                [{"captureKey":"k","startFrame":1}]],
            base=types.SimpleNamespace(
                state_sha256=lambda model:"synthetic",
                _sequence_tensors=lambda rows,item:(
                    torch.zeros((1,1)),torch.zeros((1,6,200),dtype=torch.long)))
        )
        def loss(a,b,y,w,normalized):
            sup=(a["value"]+b["value"])*.5
            zero=sup*0
            return sup,zero,zero,{"stateCE":sup}
        env={
            "v9":v9,"math":math,"json":json,"hashlib":hashlib,
            "np":np,"torch":torch,"time":time,"defaultdict":defaultdict,
            "EPOCHS":20,"losses":loss,
            "probe":lambda model,sup,kl:{},
            "paired_tensor_views":lambda x,seed:(x,x),
        }
        return source_function("train_arm",env),v9,counters

    def test_budget_callback_blocks_optimizer_before_step(self):
        train,_,count=self.setup_core()
        def block():
            count["before"]+=1
            raise RuntimeError("synthetic_budget_block")
        with self.assertRaisesRegex(RuntimeError,"synthetic_budget_block"):
            train(self.rows(),"fold","per_position_normalized","unused","sha",before_step=block)
        self.assertEqual((count["before"],count["updates"]),(1,0))

    def test_callback_failure_after_update_is_explicit(self):
        train,_,count=self.setup_core()
        def after(*args):
            count["after"]+=1
            raise RuntimeError("synthetic_receipt_write_error")
        with self.assertRaisesRegex(RuntimeError,"synthetic_receipt_write_error"):
            train(self.rows(),"fold","per_position_normalized","unused","sha",
                  on_step=after)
        self.assertEqual((count["updates"],count["after"]),(1,1))

    def test_group_drift_fails_before_optimizer(self):
        train,v9,count=self.setup_core()
        v9.build_epoch_plan=lambda rows,epoch:[]
        with self.assertRaisesRegex(RuntimeError,"training plan group drift"):
            train(self.rows(),"fold","per_position_normalized","unused","sha")
        self.assertEqual(count["updates"],0)


if __name__=="__main__":unittest.main()
