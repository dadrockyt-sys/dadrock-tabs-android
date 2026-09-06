# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-06 — **AUTHORIZED REPLACEMENT RUN TERMINAL FAILURE; START CONSUMED; NO RETRY.**
Branch: `v143-contextual-prune-lobo`

## HARD AUTHORIZATION BOUNDARY

User authorized exactly:
- 1 additional current-V143 `gomyway` Rhythm model-bearing start after repair;
- 1 professional full-1–113 scoring pass only against a completed frozen replacement result;
- deterministic preview/full PDF validation only from that same completed result.

Current counters:
- replacement live: **0 available / 1 consumed**
- professional full-1–113 score: **1 available / 0 consumed**
- replacement PDF E2E: **0 performed**

Do not:
- issue/rearm/rerun any second Rhythm start without new explicit user authorization;
- issue Lead/Bass model-bearing work;
- run the professional scorer without a valid completed frozen replacement result;
- deploy/promote Vercel production, weaken Deployment Protection, run optimizer/training/threshold sweeps, or mutate scheduler/model/parameters.

## REPAIRED BRIDGE + GREEN MODEL-FREE PREFLIGHT

The old ~7-second 502 was confirmed as stale Modal HTTP bridge deployment behavior around zero-timeout pending polls. The repaired bridge was deployed and model-free verified before the replacement run.

Pinned repaired boundary:
- bridge `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`
- worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`
- bridge deploy run `34041343616`, job `101508549305`, success
- deploy evidence artifact `9991761743`, SHA-256 `02dff61207bac1b42331cd0359e92ab3bcecd252e00c15cbb0011d714f6aa49e`

Green protected Preview preflight:
- run `34042266658`, job `101511044644`, success
- Preview `dpl_5j26ZS2xq3utrHxW7waCd5NEPaQk`
- URL `https://dadrock-tabs-android-r9uhb2dg9-stephen-mcnally-s-projects.vercel.app`
- source `631544a8668033392300f2739c87232553dbadc0`
- `/ai-tab` HTTP 200, 38016 bytes
- invalid-type analyze probe HTTP 400 with expected route error
- evidence artifact `9992037110`, SHA-256 `bf83017022ca3cc15ff7e13841615b3223ac64da05b9e8aed1c62ef7e40e186d`
- model/audio/reference counters all zero

## ONE-SHOT RUNNER

- workflow `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- helper `.github/scripts/v143-one-shot-final-rhythm-existing-preview.sh`
- helper blob `e2847e4d05ae1fea781ef07e891fece1bfbecbf0`
- retarget commit `9f4d8b59a15288cab02c7930093f80db57e52df0`
- workflow blob `d803af28820cff23750e503cf2fdea5aa8299d83`
- arm marker commit `acdf236e5e2649d3beb515fb2fc8a0abf345cc51`

Runner contract remained intact: one Rhythm start only, same-token polling only, no replacement path, freeze before reference access, deterministic PDFs from the freeze, one professional score only after valid completion, then same-job ACK/clear.

Pinned audio/reference:
- audio `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- professional reference `research/v154-professional-references/rhythm-professional-reference.json`
- reference SHA-256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- reference coverage: measures 1–113; 113 measures; 603 professional events/onsets; 946 notes

## TERMINAL AUTHORIZED REPLACEMENT RESULT

GitHub Actions:
- workflow `V143 Final Rhythm One Shot`
- run `34046854397`
- job `101523324268`
- conclusion **failure**
- only failing step: `Run exactly one current-V143 Rhythm E2E`
- scrub step success
- bounded artifact upload success

Exact terminal transport evidence:
- protected Preview identity/source boundary passed
- protected analyze route preflight HTTP 400, route reached
- exactly **1** model-bearing start request
- start HTTP **202**, `startAccepted=true`
- start accepted at about `2026-09-06T16:54:33Z`
- polls **1 through 130** returned HTTP **202** against the same signed job/token
- poll 130: elapsed about **902 s**
- poll **131** returned terminal HTTP **502** at elapsed about **908 s** (`2026-09-06T17:09:35Z`)
- helper printed `STOP: authorized job returned terminal failure; no retry.` and exited code 6
- same-job EXIT-trap ACK succeeded: HTTP **200**, `acknowledged=true`
- `transientResultCleared=true`
- `completed=false`, `terminalState=failed`, `terminalStatus=502`

Bounded evidence artifact:
- artifact `9993601754`
- name `v143-final-rhythm-one-shot`
- size 1114 bytes
- ZIP SHA-256 `9c5661024e59ee70068e87eb286aa8e1095f85455c2203ed64870d7dded7f50e`
- retained `summary.json` confirms `modelBearingStartRequestCount=1`, `professionalScoreCalls=0`, `pdfE2EPerformed=false`, `rawAudioRetained=false`, `rawStemsRetained=false`, `modelBytesRetained=false`, `referenceOpenedBeforeFreeze=false`, and no production/protection change.

Therefore:
- the repaired async bridge **did fix the old false-fast-502 behavior**: this run remained correctly `processing` for ~15 minutes instead of failing at the first pending poll;
- the authorized replacement nevertheless failed in the Modal worker/runtime path;
- the operator simultaneously observed Modal reporting the invoked function **crash-looping**;
- there is no completed structured result to freeze, no replacement PDF, and no valid basis for professional scoring;
- **NO RETRY IS AUTHORIZED.**

## CURRENT ROOT-CAUSE DIAGNOSIS — MODEL-FREE ONLY

Confirmed source/runtime facts:
- `analyzer/v143_modal_live_endpoint.py` declares the live Rhythm function with `gpu="L4"`, `timeout=1200`, `memory=8192`.
- **Correction:** current Modal documentation defines an integer `memory=8192` as a memory **request/minimum**, not an 8 GB hard limit. A hard memory limit requires a `(request, limit)` tuple. Therefore the earlier theory that this code necessarily hit an 8 GB Modal hard ceiling is **not supported and must not be treated as root cause**.
- The dependency smoke is import-only and does not execute the full separator/model path, so it still does not validate runtime behavior of the multiprocessing separator.
- Current `analyzer/v143_seeded_separator.py` uses spawned Demucs child processes and overlaps stages:
  1. start direct Demucs child;
  2. run BS-RoFormer in the parent while direct Demucs remains alive;
  3. start cascade Demucs child;
  4. only then join the direct child;
  5. join cascade child.
- There can therefore be a window with two Demucs child processes alive, and this scheduler is materially different from the older serial path.
- Parent/older behavior before commit `6772a0ca1d700ea6861cd4401b51e093144c8d26` was serial: direct Demucs -> BS-RoFormer -> cascade Demucs.
- Commit `6772a0ca1d700ea6861cd4401b51e093144c8d26` (`fix: seed V143 separator child scheduler`) introduced the overlapping child-process scheduler.

Interpretation:
- **confirmed failure boundary:** true Modal worker/runtime failure after a long processing period, not the repaired bridge's prior pending-poll bug.
- **not yet confirmed:** OOM, memory-limit termination, multiprocessing incompatibility, child-process crash, timeout/retry behavior, or another worker exception.
- The operator-visible Modal crash loop makes container/process lifecycle failure highly relevant, but GitHub/Vercel bounded evidence intentionally hides the raw Modal exception.
- Current focus should be the exact multiprocessing/runtime lifecycle introduced by the seeded child scheduler and the full separator execution path, rather than assuming an 8 GB cap.
- This still does **not** demonstrate that the Songsterr-inspired transcription logic itself is musically unsuccessful, because no completed transcription result reached freeze/scoring.

## NEXT SAFE WORK

1. Continue **model-free** diagnosis only; do not run/rearm the model.
2. Recover exact Modal app/container logs for the failed invocation if an existing authenticated diagnostic path is available; Modal's current CLI supports filtering app logs by FunctionCall/container IDs.
3. Audit the scheduler transition around `6772a0c...`, child process exit/error handling, and any prior successful full separator runs.
4. Determine whether the crash loop is caused by multiprocessing/container lifecycle, resource exhaustion, function timeout/retry semantics, or another exact worker exception.
5. Only after a confirmed cause, prepare the smallest repair candidate separately; do not deploy/run a new model-bearing test without respecting the authorization boundary.
6. Save stronger root-cause evidence here before further action.

Current state: **TERMINAL REPLACEMENT FAILURE. One authorized live start consumed and ACK/cleared. Professional score unused. PDF E2E not performed. No retry authorized. Bridge fix proven. Exact Modal worker crash-loop cause still under model-free diagnosis.**
