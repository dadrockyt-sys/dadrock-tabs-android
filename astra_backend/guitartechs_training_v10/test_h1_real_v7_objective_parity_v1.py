"""No-media, tiny-network regression against frozen V7/V9 objective functions.

Imports the actual frozen V7 loss, V9 view+KL helpers and H1 core. This
fixture is NOT the full TemporalTabCNNV9 model or an epoch-20 SHA proof.
"""
from __future__ import annotations
import hashlib
import json
import unittest
import torch
from torch import nn

from guitartechs_training_v7.model import NUM_PITCHES
from guitartechs_training_v7.objective_decoder import v7_sequence_loss
from guitartechs_training_v9.paired_view import paired_tensor_views, symmetric_kl_consistency
from guitartechs_training_v10 import h1_pilot_core_v1 as h1


class TinyMultihead(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv=nn.Linear(192, 12)
        self.acoustic=nn.Linear(12, 12)
        self.temporal=nn.Linear(12, 12)
        self.routing=nn.Linear(12, 12)
        self.dropout=nn.Dropout(0.15)
        self.state_head=nn.Linear(12, 6*21)
        self.activity_head=nn.Linear(12, 6)
        self.pitch_head=nn.Linear(12, NUM_PITCHES)
        self.event_head=nn.Linear(12, 6)

    def forward(self,x):
        z=x.mean((2,4))   # 1,200,192 synthetic tensor, not real audio
        z=self.dropout(torch.tanh(self.conv(z)))
        z=torch.tanh(self.acoustic(z))
        z=torch.tanh(self.temporal(z))
        z=torch.tanh(self.routing(z))
        return {
            "tablature":self.state_head(z),
            "activity":self.activity_head(z),
            "pitch":self.pitch_head(z),
            "event":self.event_head(z),
        }


def _fixture():
    rng=torch.Generator().manual_seed(72736)
    out=[]
    for i in range(4):
        x=torch.rand((1,200,1,192,9),generator=rng)
        labels=torch.full((1,6,200),-1,dtype=torch.long)
        labels[:,0,20+i:26+i]=3
        labels[:,1,80+i:91+i]=4
        labels[:,2,150:155]=-100
        out.append((x,labels))
    return out


def _fold(instrumented):
    torch.manual_seed(20260921)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)
    model=TinyMultihead()
    optimizer=torch.optim.Adadelta(model.parameters(),lr=1.0)
    batch=_fixture()
    traces=[]
    for step in range(2):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        for micro,(x,y) in enumerate(batch[step*2:step*2+2]):
            item={"captureKey":f"synthetic-{micro}","startFrame":0,"endFrame":200}
            view_seed=int(hashlib.sha256(json.dumps({"epoch":step,"item":item},sort_keys=True).encode()).hexdigest()[:16],16)
            a,b=paired_tensor_views(x,view_seed)
            oa,ob=model(a),model(b)
            if instrumented:
                supervised,raw,kl,_=h1.losses(oa,ob,y,1.125,False)
                if step==0 and micro==0:
                    rng_before=torch.get_rng_state().clone()
                    _=h1.probe(model,supervised,kl)
                    if not torch.equal(rng_before,torch.get_rng_state()):
                        raise AssertionError("H1 probe modified global RNG")
                total=supervised+kl
            else:
                sa,_=v7_sequence_loss(oa,y,content_weight=1.125)
                sb,_=v7_sequence_loss(ob,y,content_weight=1.125)
                batchmean=symmetric_kl_consistency(
                    oa["tablature"].reshape(1,200,6,21),
                    ob["tablature"].reshape(1,200,6,21))
                total=0.5*(sa+sb)+0.10*batchmean
            if not torch.isfinite(total):
                raise AssertionError("nonfinite tiny-network control loss")
            (total/2).backward()
        optimizer.step()
        traces.append(torch.get_rng_state().clone())
    return ( {k:v.detach().clone() for k,v in model.state_dict().items()},
             optimizer.state_dict(), traces )


class FrozenLossExpressionParity(unittest.TestCase):
    def test_original_control_exact_optimizer_parameters_rng(self):
        original=_fold(False)
        instrumented=_fold(True)
        for key in original[0]:
            self.assertTrue(torch.equal(original[0][key], instrumented[0][key]),key)
        a,b=original[1],instrumented[1]
        self.assertEqual(a["param_groups"],b["param_groups"])
        for key,values in a["state"].items():
            for name,old in values.items():
                new=b["state"][key][name]
                if isinstance(old,torch.Tensor):
                    self.assertTrue(torch.equal(old,new),f"{key}/{name}")
                else:
                    self.assertEqual(old,new)
        for rng_a,rng_b in zip(original[2],instrumented[2]):
            self.assertTrue(torch.equal(rng_a,rng_b))

    def test_normalized_kl_exact_factor_at_loss_boundary(self):
        torch.manual_seed(123)
        model=TinyMultihead().train()
        x,y=_fixture()[0]
        a,b=paired_tensor_views(x,897)
        oa,ob=model(a),model(b)
        sup,raw,original,_=h1.losses(oa,ob,y,1.125,False)
        nsup,nraw,normalized,_=h1.losses(oa,ob,y,1.125,True)
        self.assertTrue(torch.equal(sup,nsup))
        self.assertTrue(torch.equal(raw,nraw))
        self.assertTrue(torch.allclose(original,normalized*1200,rtol=1e-5,atol=1e-5))


if __name__=="__main__":
    unittest.main()
