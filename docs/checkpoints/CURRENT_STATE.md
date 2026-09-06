# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-06 — **AUTHORIZED REPLACEMENT START CONSUMED; MODAL FUNCTION CRASH-LOOP OBSERVED; NO RETRY.**
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

Confirmed root cause of the prior fast 502: production Modal HTTP bridge deployment drift. Repaired source catches both built-in `TimeoutError` and `modal.exception.TimeoutError`; stale deployed bridge did not.

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
- immutable source-boundary checks passed before E2E
- `Run exactly one current-V143 Rhythm E2E` entered `in_progress`

The replacement budget is permanently treated as consumed. GitHub did not expose the live sub-command log while the E2E step was in progress, but the model-bearing section was entered and the operator then observed Modal reporting the function as **crash-looping**. This is a decisive failure/unsafe-continuation signal for this authorized start. There is **no authorized replacement start**.

## MODAL CRASH-LOOP FAILURE SIGNAL — USER OBSERVED

- During run `34046854397` / job `101523324268`, the operator reported that Modal shows the invoked function **crash-looping**.
- This means the repaired HTTP pending-poll bridge fixed the prior false-fast-502 boundary, but the same authorized FunctionCall is now exhibiting a distinct worker/runtime failure mode.
- Do **not** interpret the longer GitHub `in_progress` state as a healthy model run.
- Do **not** trigger/re-arm/rerun a model-bearing workflow.
- Continue only passive observation of this same workflow/job until terminal evidence is available.
- The helper polls only the same signed token and has an EXIT trap that attempts ACK/clear for that same job; no replacement start path exists in the helper.
- Do not open/run the professional scorer or PDF E2E unless this exact same job returns a valid completed structured result and freezes successfully.

Current counters:
- replacement live: **0 available / 1 consumed**
- professional full-1–113 score: **1 available / 0 consumed**
- replacement PDF E2E: **0 confirmed performed**

## NEXT ACTION — DIAGNOSE WITHOUT MODEL RETRY

1. Observe only run `34046854397` / job `101523324268` to its terminal state and collect its terminal logs/artifact.
2. Confirm whether the one start was HTTP 202 accepted, the same job/token was polled, and whether ACK/clear succeeded.
3. Recover the exact crash-loop cause from terminal GitHub evidence and/or model-free Modal/runtime source/deployment diagnostics.
4. **NO second model start.** Any fix must be diagnosed and prepared without consuming another model run unless the user later grants new explicit authorization.
5. Professional score remains unused unless the exact authorized job somehow completed and produced a valid frozen result.
6. Save the terminal failure evidence and root cause here before any future action.
