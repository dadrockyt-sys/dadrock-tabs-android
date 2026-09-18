# Astra Work — active project instructions

Read `docs/checkpoints/CURRENT_STATE.md` first. Active development branch: `astra-work`.

- Product: Jimmy PAIge for DadRock Tabs; audio upload -> selected bass/rhythm/lead -> accurate playable preview -> optional purchased full PDF.
- Active backend: `astra_backend/`. Do not change `main`, deploy, or resume archived workflows as a side effect of development.
- V143/Gomyway and Songsterr Fresh research are archived. Their checkpoints/results remain historical evidence, not the active task queue. Never reinterpret a frozen failure as a pass or reuse exposed data as an untouched holdout.
- Preserve archived source in `songsterr_pipeline/`; Astra's copied source is independently editable. User authorized the new foundation and milestone saving.
- Ordinary reversible backend implementation and CPU synthetic tests may proceed within the active milestone. Any paid inference, real-corpus access governed by earlier freezes, production promotion or external action must respect existing authorization; this setup does not grant it.
- After every major step: update CURRENT_STATE with changes, tests, actual results, gaps and exact next task; commit code/tests/docs together to astra-work; verify the remote ref. Do not claim saved work from a local commit alone.
- Before a long operation, record an in-progress checkpoint when practical. Record failures honestly. Never store credentials, customer audio or secrets in Git.
- If interrupted: inspect branch, HEAD and working tree; preserve unfinished changes; resume the checkpoint's next task. Do not restart archived queues.
