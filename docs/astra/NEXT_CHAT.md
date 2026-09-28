# Next chat: start here

S3 is complete and failed its frozen gate.

pos_weight 16 versus 8:
- exact onset admission 0.6744 vs 0.5891
- event recall 0.5814 vs 0.5814
- event F1 0.6977 vs 0.7075
- repeated-note recall 0.5238 vs 0.5714
- state/joint admission 0.2868 vs 0.3333

So higher onset weighting moved onset admission but did not improve event recall and slightly harmed state/joint admission.

Repeated-reference preceding-frame onset probabilities stayed below the 0.50 threshold, so rising-edge plateau gating is not supported as the dominant repeated-attack bottleneck.

Standing policy:
- routine GitHub-only non-model workflows are pre-authorized;
- model execution, Codespaces, and potentially billable Vercel work require explicit authorization.

Next: offline review only. Do not run another model until a new one-variable design is frozen and explicitly authorized.
