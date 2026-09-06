# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-06 — **NEW USER-AUTHORIZED REPAIR + ONE REPLACEMENT RHYTHM RUN + ONE PROFESSIONAL SCORE.**  
Branch: `v143-contextual-prune-lobo`

## NEW AUTHORIZATION — CURRENT TURN

User explicitly said: **“Fix the error and please run again with scorer.”**

This grants exactly:
- **1 additional current-V143 `gomyway` Rhythm model-bearing start** after a model-free diagnosis/repair;
- **1 professional full-1–113 scoring pass** against the completed frozen replacement result;
- deterministic preview/full PDF validation from that same completed structured result.

Budget now:
- Historical live starts already consumed: **1** (workflow `34012949265`).
- Newly authorized replacement live starts: **1 available / 0 consumed**.
- Professional full-1–113 score: **1 available / 0 consumed**.
- Replacement PDF E2E: **0 performed**.
- No second replacement/retry is authorized if this newly authorized live start fails.
- No Lead/Bass model run, production deployment/promotion, Deployment Protection weakening, optimizer/training/threshold sweep, scheduler/model/parameter mutation.

## LAST TERMINAL RUN — DO NOT RERUN

- Workflow run: `34012949265`; job `101431778382`; arm commit `c0655037bc8d5053b4868e4ef8b20c83683416b6`.
- Preview: `dpl_3LdGRdXb7ZkmNUojrXun72my84M4`, source `6212f6c64a2bcebaebfae7f4f7bc22d2a0483894`, target `preview`, READY.
- Protected route preflight: expected HTTP 400 and route reached.
- Exactly one model-bearing `operation:"start"`: HTTP 202, `startAccepted=true`.
- First same-token poll: HTTP 502 after ~13 s; runner stopped with no replacement.
- Same-job ACK: HTTP 200, acknowledged, transient result/control cleared.
- Professional score calls: 0. PDF E2E: 0.
- Artifact: `9983034564`, zip SHA-256 `9efac7899d95008ab36faa95e7384f77256bdc9efbb93454fb31eadb1f958028`.
- Raw 502 response was intentionally scrubbed, so exact worker failure must be recovered using non-model diagnostics/source history rather than guessed.

## MODEL-FREE DIAGNOSIS IN PROGRESS

The accepted start proves Vercel packaging/protected transport/start issuance are working. The failure boundary is downstream in the async bridge/orchestrator/Modal worker path.

Current pinned bridge behavior:
- `run_rhythm_async_job` calls fixed Modal worker `dadrock-v143-ai-tab-live / rhythm_v143_request`.
- Any worker exception is intentionally converted to a generic failed envelope, so the Vercel poll becomes 502 without leaking secrets.
- Status polling reads only the same queued result/control/FunctionCall.

Next actions before consuming the new authorization:
1. Use only model-free diagnostics/history/source inspection to identify and repair the fast worker failure.
2. Prefer an existing non-model dependency/smoke function or deployment validation over a live audio/model request.
3. Pin repaired bridge/worker/helper blobs and verify Preview/source boundary.
4. Save a **PRE-REPLACEMENT-RUN** checkpoint with new live counter still 0 consumed.
5. Execute exactly one replacement Rhythm start; once sent, mark new live authorization consumed.
6. Poll only its same signed job/token/FunctionCall; if it fails, STOP — no second replacement.
7. If completed, freeze the exact structured result, render preview/full PDFs from the same events, then run exactly one professional scorer pass against the pinned 1–113 reference.
8. ACK/clear the same job and save FINAL checkpoint.

## PINNED SOURCE / REFERENCE

- Audio: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Audio blob: `4dd709e3fa177b4daeed71ca97f0199757729d4b` (also verified on `main`).
- Analyze route blob used by prior Preview: `a3d02876d2c4efeb6f5258586046bc95cfc132b6`.
- `next.config.js` packaging repair blob: `d057c0731bc7f8b261c3598a45a7aea6dc5c9583`.
- Async bridge prior blob: `169b4bb136eba742c3422a73ee5dd0174ca06c49`.
- Async protocol blob: `1bd55017e16a4e1d8b14c7429492f811a43a28d8`.
- Modal live worker prior blob: `111bf14a8f91045d3478901f8e36b88a2e7f181a`.
- Deterministic separator/scheduler blob: `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Full professional reference: `research/v154-professional-references/rhythm-professional-reference.json`.
- Reference blob: `248741bade9665a34648c59a2994bd27d73fc406`.
- Reference SHA-256: `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Coverage: measures 1–113; 113 measures; 603 professional events/onsets; 946 notes.
- Professional scorer: `validation/rhythm_holdout/score_rhythm_holdout.py`, prior blob `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`.
- Final holdout orchestrator: `validation/rhythm_holdout/run_final_holdout_gate.py`, prior blob `c6a84434eefa768a924395b76d1d25b4e5a51307`.

Current state: **AUTHORIZED REPAIR MODE. Historical live 1 consumed. New replacement live = 1 available / 0 consumed. Professional score = 1 available / 0 consumed. PDF E2E = 0 performed.**
