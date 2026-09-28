# Next chat: start here

Standing authorization policy from Stephen:

- Routine GitHub operations and GitHub Actions runs are pre-authorized when they do **not** execute a model and do not involve Codespaces or potential Vercel cost.
- Explicit authorization is still required before:
  1. any model execution (training, optimizer, inference/evaluation, pretrained/local model runs);
  2. Codespaces usage when cost may be incurred;
  3. Vercel operations that may incur cost.

This supersedes older instructions to ask before every GitHub run.

Current experiment state:
- S2 is frozen as a scientific fail.
- S3 design is frozen in `docs/astra/SYNTHETIC_DATA_DIVERSITY_S3_DESIGN_V1.md`.
- S3 changes only onset BCE pos_weight 8 -> 16 with all other settings fixed.

Because S3 executes models, **explicit S3 authorization is still required before launch**.
