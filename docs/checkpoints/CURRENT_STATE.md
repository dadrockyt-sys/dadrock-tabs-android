# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-06 11:54 America/Toronto — **AUTHORIZED REPLACEMENT ONE-SHOT IS LIVE; REPLACEMENT BUDGET LOCKED/CONSERVATIVELY CONSUMED.**
Branch: `v143-contextual-prune-lobo`

## ACTIVE AUTHORIZATION / HARD LIMITS

User authorized exactly:
- 1 additional current-V143 `gomyway` Rhythm model-bearing start after repair;
- 1 professional full-1–113 score against the completed frozen replacement result;
- deterministic preview/full PDF validation from that same completed result.

Hard limits remain:
- **NO second replacement/retry** after the authorized model-bearing start path is entered/fails without new explicit authorization.
- **NO second professional score** without new explicit authorization.
- No Lead/Bass model-bearing run.
- No Vercel production deploy/promotion/change.
- No Deployment Protection weakening.
- No optimizer/training/threshold sweep.
- No scheduler/model/parameter mutation.

## REPAIR + GREEN PREFLIGHT

Confirmed root cause: production Modal HTTP bridge deployment drift. Repaired source already caught both built-in `TimeoutError` and `modal.exception.TimeoutError`; stale deployed bridge did not.

Repaired production bridge boundary:
- bridge blob `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`
- worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`
- bridge deploy workflow run `34041343616`, job `101508549305`, success
- bridge deploy evidence artifact `9991761743`, SHA-256 `02dff61207bac1b42331cd0359e92ab3bcecd252e00c15cbb0011d714f6aa49e`

Green protected Preview preflight:
- run `34042266658`, job `101511044644`, success
- Preview deployment `dpl_5j26ZS2xq3utrHxW7waCd5NEPaQk`
- Preview URL `https://dadrock-tabs-android-r9uhb2dg9-stephen-mcnally-s-projects.vercel.app`
- Preview source `631544a8668033392300f2739c87232553dbadc0`
- `/ai-tab` HTTP 200, 38016 bytes
- analyze invalid-type probe HTTP 400 with expected route error
- preflight evidence artifact `9992037110`, SHA-256 `bf83017022ca3cc15ff7e13841615b3223ac64da05b9e8aed1c62ef7e40e186d`
- preflight model/audio/reference counters all zero

## EXACT ONE-SHOT RUNNER

- Workflow `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- Helper `.github/scripts/v143-one-shot-final-rhythm-existing-preview.sh`
- helper blob `e2847e4d05ae1fea781ef07e891fece1bfbecbf0`
- runner retarget commit `9f4d8b59a15288cab02c7930093f80db57e52df0`
- runner workflow blob `d803af28820cff23750e503cf2fdea5aa8299d83`
- only Preview URL/deployment/source were retargeted; route/page/config/bridge/protocol/worker/scheduler/helper/audio/reference pins were unchanged

Verified runner contract:
1. model-free source + protected-route preflight;
2. exactly one `operation:"start"` for `gomyway-midterm-source.m4a`, song `Are You Gonna Go My Way`, artist `Lenny Kravitz`, transcription type `rhythm`;
3. poll only the same signed job/token/FunctionCall; STOP/no replacement on failure;
4. freeze the exact completed result before reference access;
5. render deterministic preview/full PDFs from that freeze and verify PDF event fidelity;
6. open the pinned professional reference only after freeze/PDF validation;
7. exactly one professional full-1–113 scoring pass;
8. ACK/clear the same job; EXIT trap also only ACKs that same job;
9. raw token/result/reference material is scrubbed; bounded evidence and PDFs are retained.

Pinned audio/reference:
- audio `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- reference `research/v154-professional-references/rhythm-professional-reference.json`
- reference SHA-256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- reference coverage measures 1–113; 113 measures; 603 professional events/onsets; 946 notes

## LIVE AUTHORIZED REPLACEMENT RUN

Arm marker commit:
- `acdf236e5e2649d3beb515fb2fc8a0abf345cc51` (`test: arm repaired V143 Rhythm one-shot`)

GitHub Actions:
- workflow `V143 Final Rhythm One Shot`
- run `34046854397`
- job `101523324268`
- current observed state: `Run exactly one current-V143 Rhythm E2E` is **in progress**
- checkout, immutable source-boundary checks, Node setup, and pinned Vercel CLI installation all completed successfully before the E2E step

GitHub does not expose this job's live sub-command log until completion, so the exact HTTP-202/start-token evidence is not yet visible externally. Because the model-bearing E2E step has begun and may already have sent `operation:"start"`, the replacement budget is now **conservatively locked and treated as consumed**. It must never be reused even if the workflow later reports a pre-start ambiguity.

Current counters:
- replacement live: **0 available / 1 locked-consumed**
- professional full-1–113 score: **1 available / 0 consumed** until terminal evidence proves the one authorized score was called
- replacement PDF E2E: **0 confirmed performed** until terminal evidence proves it completed

## NEXT ACTION — SAME RUN ONLY

- Observe only run `34046854397` / job `101523324268` to terminal state.
- **DO NOT trigger, rerun, re-arm, or replace it.**
- When terminal logs/artifact become available, determine exact start acceptance/job identity, completion/failure, frozen-result hashes, PDF fidelity/hashes, whether the single professional score was called, score metrics, and same-job ACK/clear status.
- If the live run failed after start: STOP; no second start.
- If completed: accept only the frozen result/PDFs/score generated by this same one-shot; do not regenerate or rescore.
- Save a FINAL checkpoint with workflow/job/artifact/evidence identifiers and final counters.
