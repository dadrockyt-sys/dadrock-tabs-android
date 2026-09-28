# Next chat: start here

S1 synthetic-only sampling experiment is complete.

Run 36370848921 / job 108766686822: workflow SUCCESS, S1 scientific gate FAILED because all criteria were required and absolute test recall was 0.4651 < 0.55.

Onset-aware vs uniform five-frame:
- F1: 0.6283 vs 0.3226
- recall: 0.4651 vs 0.1938
- repeated-note recall: 0.5000 vs 0.1429
- precision: 0.9677 vs 0.9615
- negative-only FP rate: 0.0 events/s

Nine of ten S1 criteria passed. Do not call it a pass.

At exact positive reference frames the onset-aware model had onset admission 0.5814 but correct-state admission only 0.2093, making state admission the leading observed remaining bottleneck.

No P1/P2/P3, no threshold search, no retry.

Exact next task: offline review only; freeze one state-admission hypothesis before asking for any new optimizer authorization.
