"""Synthetic arithmetic+probe parity fixture; does not use V9 architecture or real data."""
from __future__ import annotations
import hashlib
import json
import unittest

import torch
from torch import nn
from torch.nn import functional as F
from guitartechs_training_v9.paired_view import paired_tensor_views, symmetric_kl_consistency

# Same 200 frames x six strings x 21 logits, augmentation/view-seed and Adadelta
# arithmetic as the original-V9 control. Supervised loss is a *stand-in*;
# exact V7 objective and actual V9 weights still require independent parity.
T = 200
S = 6
C = 21
SEED = 20260921


class TinySharedNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Linear(192, 12)
        self.acoustic = nn.Linear(12, 12)
        self.temporal = nn.Linear(12, 12)
        self.routing = nn.Linear(12, 12)
        self.state_head = nn.Linear(12, S*C)
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        x = x.mean(dim=(2, 4))  # synthetic B,T,192
        x = torch.relu(self.conv(x))
        x = self.dropout(torch.relu(self.acoustic(x)))
        x = torch.relu(self.temporal(x))
        x = torch.relu(self.routing(x))
        return self.state_head(x).reshape(1, T, S, C)


def _fixture():
    generator = torch.Generator().manual_seed(19405)
    frames = [torch.rand((1,T,1,192,9), generator=generator) for _ in range(4)]
    labels = [torch.randint(0,C,(1,T,S), generator=generator) for _ in range(4)]
    return list(zip(frames, labels))


def _probe(network, supervised, weighted):
    parameters = tuple(network.parameters())
    gs = torch.autograd.grad(supervised,parameters,retain_graph=True,allow_unused=True)
    gk = torch.autograd.grad(weighted,parameters,retain_graph=True,allow_unused=True)
    return [(a.detach().clone() if a is not None else None,
             b.detach().clone() if b is not None else None) for a,b in zip(gs,gk)]


def _digest(network):
    h=hashlib.sha256()
    for name,value in sorted(network.state_dict().items()):
        h.update(name.encode());h.update(value.detach().contiguous().numpy().tobytes())
    return h.hexdigest()


def _run(instrumented,normalized=False):
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)
    net = TinySharedNet()
    optimizer = torch.optim.Adadelta(net.parameters(), lr=1.0)
    samples = _fixture()
    record = []
    for step in range(2):
        optimizer.zero_grad(set_to_none=True)
        for microbatch,item in enumerate(samples[step*2:(step+1)*2]):
            x,target=item
            view_seed=int(hashlib.sha256(json.dumps({'epoch':step,'item':{'captureKey':microbatch,'startFrame':0}},sort_keys=True).encode()).hexdigest()[:16],16)
            a,b=paired_tensor_views(x,view_seed)
            oa,ob=net(a),net(b)
            sa=F.cross_entropy(oa.flatten(0,2),target.flatten())
            sb=F.cross_entropy(ob.flatten(0,2),target.flatten())
            sup=(sa+sb)*.5
            raw=symmetric_kl_consistency(oa,ob)
            weighted=0.10*raw/(1200 if normalized else 1)
            if instrumented and step==0 and microbatch==0:
                pre=torch.get_rng_state().clone()
                _probe(net,sup,weighted)
                if not torch.equal(pre,torch.get_rng_state()):
                    raise AssertionError('probe mutated torch RNG')
            ((sup+weighted)/2).backward()
        optimizer.step()
        record.append((_digest(net), torch.get_rng_state().clone()))
    state={k:v.detach().clone() for k,v in net.state_dict().items()}
    optim={id: {key: (value.detach().clone() if isinstance(value,torch.Tensor) else value)
                for key,value in values.items()} for id,values in optimizer.state_dict()['state'].items()}
    return state,optim,record


class SyntheticParity(unittest.TestCase):
    def test_original_instrumented_parameter_optimizer_rng_parity(self):
        baseline=_run(False)
        instrumented=_run(True)
        for a,b in zip(baseline[2],instrumented[2]):
            self.assertEqual(a[0],b[0])
            self.assertTrue(torch.equal(a[1],b[1]))
        for key in baseline[0]:
            self.assertTrue(torch.equal(baseline[0][key],instrumented[0][key]),key)
        for index in baseline[1]:
            for key in baseline[1][index]:
                a,b=baseline[1][index][key],instrumented[1][index][key]
                if isinstance(a,torch.Tensor): self.assertTrue(torch.equal(a,b),str((index,key)))
                else: self.assertEqual(a,b)

    def test_normalized_arm_is_distinct(self):
        self.assertNotEqual(_run(False)[2][-1][0],_run(True,normalized=True)[2][-1][0])


if __name__=='__main__':
    unittest.main()
