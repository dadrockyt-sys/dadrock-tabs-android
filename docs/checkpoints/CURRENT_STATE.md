# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-06 — **FINAL ONE-SHOT TERMINAL FAILURE RECORDED; LIVE BUDGET CONSUMED; HOLD.**  
Branch: `v143-contextual-prune-lobo`

## FINAL STATUS

The user-authorized current-V143 `gomyway` Rhythm run was executed exactly once after two pre-start infrastructure failures. The one live/model-bearing start was accepted, then the first same-token status poll returned HTTP 502. Per the hard no-retry authorization, **no second model start was sent and none is authorized now.**

Final counters:
- Current-V143 `gomyway` Rhythm live/model-bearing starts: **1 consumed / 0 available**.
- Professional full-1–113 score passes: **0 consumed / 1 unused**.
- PDF E2E: **0 performed**.
- Lead/Bass model runs: **0 / not authorized**.
- Replacement/retry Rhythm model run: **NOT authorized**.

Current branch state must remain **HOLD** unless the user explicitly grants a new live/model-bearing run authorization.

## FINAL LIVE RUN — ATTEMPT 3

- Arm commit / workflow `GITHUB_SHA`: `c0655037bc8d5053b4868e4ef8b20c83683416b6`
- Workflow: `V143 Final Rhythm One Shot`
- Workflow run: `34012949265`
- Workflow run number: `3`
- Job: `101431778382`
- Job conclusion: `failure`
- Existing immutable Preview reused: `dpl_3LdGRdXb7ZkmNUojrXun72my84M4`
- Preview URL: `https://dadrock-tabs-android-iwhmrcol7-stephen-mcnally-s-projects.vercel.app`
- Preview source commit: `6212f6c64a2bcebaebfae7f4f7bc22d2a0483894`
- Preview target/state: `preview` / `READY`
- No new deployment was created by attempt 3.
- No production deployment/promotion/change occurred.
- No Deployment Protection disablement, bypass-secret creation, or temporary share-link creation occurred.

Protected Preview path:
- Exact Preview identity verification: PASS.
- Model-free `vercel curl --deployment` route preflight: HTTP **400** with expected invalid-transcription response; `protectedPreviewRouteReached=true`.
- This proved the protected route was reachable through the repo-established authenticated Vercel CLI path before the model start.

Single authorized start:
- `operation: "start"` request count: **1**.
- Start HTTP status: **202**.
- Start transport exit code: **0**.
- Start request time: **4.536004 s**.
- Signed async token accepted: **true** (`startAccepted=true`).
- At this point the live budget became **1 consumed / 0 available**.

Same-token terminal polling:
- Poll count: **1**.
- Poll #1 HTTP status: **502**.
- Async elapsed time at terminal failure: **13 s**.
- Terminal state: `failed`.
- Runner stopped immediately with the explicit no-retry path.
- No second `operation:"start"` was sent.

Vercel runtime request evidence for the same deployment/time window:
- 05:02:15 POST `/api/analyze-audio-tab` → 400 (model-free preflight).
- 05:02:16 POST `/api/analyze-audio-tab` → 202 (single accepted live start).
- 05:02:27 POST `/api/analyze-audio-tab` → 502 (first same-token terminal poll).
- 05:02:29 POST `/api/analyze-audio-tab` → 200 (same-job ACK cleanup).

Same-job cleanup:
- ACK HTTP status: **200**.
- ACK curl exit code: **0**.
- ACK request time: **0.277502 s**.
- `acknowledged=true`.
- `transientResultCleared=true`.
- The EXIT cleanup path used the same signed job only; it did not invoke a replacement model run.

Durable artifact:
- Artifact name: `v143-final-rhythm-one-shot`
- Artifact ID: `9983034564`
- Workflow-reported artifact zip SHA-256: `9efac7899d95008ab36faa95e7384f77256bdc9efbb93454fb31eadb1f958028`
- Preserved bounded `summary.json` records:
  - `modelBearingStartRequestCount: 1`
  - `liveBudgetConsumed: true`
  - `startAccepted: true`
  - `startStatus: 202`
  - `pollCount: 1`
  - `terminalStatus: 502`
  - `terminalState: failed`
  - `completed: false`
  - `ackStatus: 200`
  - `acknowledged: true`
  - `transientResultCleared: true`
  - `professionalScoreCalls: 0`
  - `pdfE2EPerformed: false`
  - `referenceOpenedBeforeFreeze: false`
  - `productionEnvironmentChanged: false`
  - `productionPromotionPerformed: false`
  - `deploymentProtectionDisabled: false`
  - `deploymentProtectionBypassSecretCreated: false`
  - `temporaryShareLinkCreated: false`
  - `rawAudioRetained: false`
  - `rawStemsRetained: false`
  - `modelBytesRetained: false`

The raw 502 status-response body was intentionally scrubbed after bounded evidence and ACK. Therefore the exact bridge error string is not durably recoverable from the preserved artifact. Do not infer a specific internal Modal failure without new non-model diagnostic evidence. The durable conclusion is: **the accepted async job reached terminal HTTP 502 on the first same-token poll.**

## PRE-START ATTEMPT HISTORY

### Attempt 1 — packaging failure; no model start
- Arm commit: `610ac358cdff8b60970c408b366666425c2d660a`
- Workflow run: `34012505486`
- Job: `101430616920`
- Preview: `dpl_7fe8G9PswNHpvVr7ovMkiVByMpqU`
- Failure: `NOW_SANDBOX_WORKER_MAX_UNCOMPRESSED_FUNCTION_SIZE`; `/api/analyze-audio-tab` 425.26 MB > 250 MB.
- Artifact ID: `9982913980`
- Summary proved starts=0, scores=0, PDF=0.
- Never rerun this workflow/job.

Packaging repair:
- Commit: `cd32eccdb2f3b587e6bbae5b4e3e19406d120e3e`
- `next.config.js` blob: `d057c0731bc7f8b261c3598a45a7aea6dc5c9583`
- `/api/analyze-audio-tab` now uses the existing `public/**/*` trace exclusion with explicit DadRock logo include.
- Exact repaired Preview later built READY, confirming the 425 MB blocker was fixed.

### Attempt 2 — protection transport failure; no model start
- Arm commit: `6212f6c64a2bcebaebfae7f4f7bc22d2a0483894`
- Workflow run: `34012747879`
- Job: `101431245172`
- Preview: `dpl_3LdGRdXb7ZkmNUojrXun72my84M4` — READY.
- Raw GitHub OIDC curl preflight did not reach the route; no Vercel function runtime invocation recorded.
- Artifact ID: `9982986412`
- Summary proved starts=0, scores=0, PDF=0.
- Never rerun this workflow/job.

Transport repair:
- Historical repo helper commit `e24eb3b3ef05f25faa2ddefd1bee66327549b98e` established the correct protected-Preview transport: `vercel curl --deployment`.
- Final helper: `.github/scripts/v143-one-shot-final-rhythm-existing-preview.sh`
- Helper blob: `e2847e4d05ae1fea781ef07e891fece1bfbecbf0`
- Attempt 3 proved this transport works: preflight reached route and returned the expected 400 before the single live start.

## PINNED CURRENT-V143 SOURCE BOUNDARY USED

- Audio: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Audio Git blob: `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- Analyze route blob: `a3d02876d2c4efeb6f5258586046bc95cfc132b6`
- `/ai-tab` page blob: `c218639afcdbb7540ff7cc34583afc6d83587fa0`
- `next.config.js` blob: `d057c0731bc7f8b261c3598a45a7aea6dc5c9583`
- Async bridge blob: `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- Async protocol blob: `1bd55017e16a4e1d8b14c7429492f811a43a28d8`
- Modal live worker blob: `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- Deterministic separator/scheduler blob: `fc9b4c45c208d80be7abab64a8959f2a3babcee8`
- Fixed Modal worker: app `dadrock-v143-ai-tab-live`, function `rhythm_v143_request`.

## PROFESSIONAL REFERENCE / SCORE / PDF — NOT CONSUMED

Pinned full professional reference remains:
- `research/v154-professional-references/rhythm-professional-reference.json`
- Git blob: `248741bade9665a34648c59a2994bd27d73fc406`
- SHA-256: `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- Coverage: measures 1–113, 113 stored measures, 603 professional events/onsets, 946 notes.

Because the live job did not complete:
- no freeze snapshot was produced;
- no preview/full PDF E2E was rendered from a completed live result;
- the professional scorer-only reference was never copied/opened;
- `professionalScoreCalls = 0`;
- the reserved score pass remains unused but cannot be meaningfully run without a completed frozen live result.

## HARD HOLD

Do **not**:
- rerun workflow `34012949265` or job `101431778382`;
- send another Rhythm `operation:"start"`;
- use Lead/Bass to substitute for the failed Rhythm run;
- run the professional scorer against any historical or partial candidate as a replacement for this failed live run;
- fabricate PDF or professional-score results;
- mutate optimizer/training/thresholds/model parameters to justify a retry;
- deploy/promote production as part of this failed gate.

Permitted while on HOLD without a new live-run authorization:
- inspect existing source code, historical logs/artifacts, and non-model diagnostics;
- reason about the terminal 502 using already-preserved evidence;
- make model-free code/infrastructure repairs if needed, but **do not arm or issue another model-bearing start**.

Current state: **TERMINAL HOLD. Live = 1 consumed / 0 available. Professional score = 0 consumed / 1 unused. PDF E2E = 0 performed. Same-job transient result cleared. No model retry authorized.**
