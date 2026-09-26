# Next chat: start here

Repository: `dadrockyt-sys/dadrock-tabs-android`, branch `astra-work`.
Canonical status: `docs/checkpoints/CURRENT_STATE.md`.

## Current direction

Stop full retraining until the event labels/scoring preserve repeated attacks and a tiny training-only fitting test works. V1–V5 remain FAIL. Keep P3 sealed and main/Production unchanged.

The user requested economical preparation for the next GPT chat, not another unbounded run. Offline implementation is authorized. Real optimizer work needs the existing explicit authorization gate after a concrete pilot is prepared.

## Already done — do not redo

- Reviewed all five versions. V4 best legacy macro F1 0.243523; V5 0.064131.
- V5 diagnosis proved hard onset admission collapse. State-only ablation recovers 0.218843; still below V4. Do not repeat this diagnosis.
- Reproduced lost repeated-note boundaries; added explicit event adapter, frame targets and scorer.
- Added corrected PR/ROC histogram helper and measured-status abstention helper.
- 26 focused offline tests passed on Python 3.12.14; Python 3.10 GitHub verification also passed (run 36273580660). This is synthetic evidence, not real guitar quality or frozen-ML-runtime training verification.
- Prepared the bounded pilot proposal; it is NOT launch-ready.
- Archived the long historical checkpoint intact. Read it only for specific old evidence, not as an active queue.

## Read only these first

1. `AGENTS.md` and current checkpoint.
2. `docs/astra/EVENT_CONTRACT_V2.md`.
3. `docs/astra/TINY_FIT_PILOT_PROPOSAL_V1.json`.
4. The three new Python files in `astra_backend/evaluation/` named in the contract.

## Exact next work

Implement the prepared-event/crop/mask adapter on fabricated source fixtures. Then implement one tiny-fit model/loss/event-list decoder and enforce the pilot caps synthetically. Prepare a source-pinned, reviewable real-data authorization request only when ready.

Do not start by inventing V6 architecture changes, researching more papers, rerunning V5 or requesting another full 2,000 combined epochs. Do not rename this pilot a validation success. Do not weaken frozen thresholds or use P3 for design.

Proposed limits: four P1 training performances, one view each, 200 frames each; 200 optimizer steps total; 45 minutes training/evaluation within a 60-minute CPU job; zero paid compute; no automatic retries/extension. Exact selection and implementation remain to freeze.

Potential evidence preservation issue: V5 Actions model artifacts expire October 2–3 UTC. See `V5_ARTIFACT_INVENTORY_2026_09_26.json`. This inventory is metadata, not a backup. Preserve verified model artifacts through the established durable artifact path before expiry if reuse is selected; do not rerun training merely to recover expired files. No logit cache was emitted by the reviewed diagnosis code.

## Verify and save

```sh
python -m unittest discover -s astra_backend/evaluation -p 'test_event_contract_v2.py' -v
```

After a meaningful change, save code/tests/status together on `astra-work`, verify the remote commit, and keep CURRENT_STATE short. Preserve unrelated local changes. Report remaining blockers plainly. No full suite or model rerun merely to refresh old evidence.
