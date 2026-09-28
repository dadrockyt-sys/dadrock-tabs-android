# Astra S6 failure analysis V1

Date: 2026-09-28
Scope: offline review only. No model execution, rendering, optimizer work, threshold search, P1/P2/P3, Codespaces, or Vercel.

## Frozen S6 result

S6 replaced the linear state head with a one-hidden-layer nonlinear state head while keeping the shared encoder and onset head identically initialized.

Control linear head:
- state admission 0.3178
- joint admission 0.3101
- onset recall 0.5659
- onset F1 0.7053
- repeated recall 0.5714
- median true-state probability 0.0942
- median silence probability 0.6330
- median true-minus-silence margin -0.4466

Nonlinear state head:
- state admission 0.3798
- joint admission 0.3256
- onset recall 0.6047
- onset F1 0.7123
- repeated recall 0.5238
- median true-state probability 0.2180
- median silence probability 0.4812
- median true-minus-silence margin -0.1195

The nonlinear head clearly moved state confidence and state admission in the intended direction, but the frozen S6 gate failed.

## What the result supports

The state branch benefits from nonlinear state-specific capacity.

Evidence:
- exact state admission +0.0620;
- median true-state probability more than doubled;
- median silence probability fell materially;
- median true-minus-silence margin moved much closer to zero.

This is a stronger representation signal than S5's weight-only change, which produced zero state-admission gain.

## Why the replacement head is not yet a clean solution

Joint admission improved only +0.0155.

Event F1 improved only +0.0070, below the +0.03 frozen criterion.

Repeated-note recall fell from 0.5714 to 0.5238.

The intervention also changed the entire state-head initialization and removed the direct linear state projection. Although the shared encoder/onset head were controlled, the two state pathways did not start with equal state logits.

That makes one especially clean next experiment available: retain the control linear state path exactly and add nonlinear capacity only as a residual correction initialized to zero.

## Chosen next hypothesis

Test a **zero-initialized nonlinear residual state correction**.

Control:
- state_logits = Linear(128,126)

Intervention:
- base_logits = the exact same Linear(128,126)
- residual = Linear(128,128) -> ReLU -> Linear(128,126)
- final state_logits = base_logits + residual
- initialize the residual output layer weights and bias to exactly zero.

This gives:
- identical shared encoder tensors;
- identical onset-head tensors;
- identical base linear state-head tensors;
- exactly identical pre-update state logits;
- exactly identical pre-update onset logits;
- extra state capacity that starts as a no-op and can learn only if useful.

Everything else stays at the S6/S5 weight-9 configuration.

This isolates learned nonlinear residual capacity more cleanly than replacing the state head outright.
