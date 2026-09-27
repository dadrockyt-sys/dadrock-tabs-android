# Astra — current handoff

Updated: 2026-09-27 UTC  
Branch: `astra-work`  
Status: **REVIEWED HANDOFF: P1 TRAINING-ONLY GATE MET; P2 TRANSFER FAILED; CAUSE NOT YET ISOLATED; OFFLINE DIAGNOSTIC PACKAGE NEXT; P3 SEALED**
Next-chat guide: `docs/astra/NEXT_CHAT.md`

## GPT-5.6 handoff review — 2026-09-27 — READ THIS FIRST

This review supersedes the older next-step prescriptions below; the historical receipts remain unchanged. Reviewed branch head: `13d3be19fcabd82bd9afd02be168d5dda589fd7d`. User requested inspection and a saved direction, not another real-data run.

### Verdict and established evidence

Keep the small-budget engineering approach. Do not restart V1–V5 or spend more epochs on the four P1 crops. Decoder V2 achieved the recorded training-only gate (16 TP, 0 FP, 0 FN; offset fraction 0.9375; only two repeated reference attacks). This is a useful plumbing/learnability result, not evidence of a usable transcription product.

The P2 screen failed with no decoded events. The latest activation diagnostic run 36325297420 / job 108636792679 is independently confirmed SUCCESS through GitHub job steps, including cleanup. Its committed receipt reports 0/15 P2 onset probes and 9/15 state probes passing. This review inspected the receipt, model source, diagnostic source and workflow; it did not independently recompute the raw artifact metrics.

### Corrections to the previous interpretation

1. **Observed onset-admission failure is not a causal diagnosis of the onset head.** The shared encoder, training coverage, features, timing/labels and head can all contribute. The classifier in `p1_p2_activation_diagnostic_v1.py` labels any zero-onset/nonzero-state case `onset_head_generalization_failure`; that label is descriptive, not an intervention proving that retraining only the head will work.
2. **Chords also have substantial state failure:** only 1/4 P2 chord state probes pass, compared with 0/2 PalmMute, 7/8 scales and 1/1 single notes. Do not characterize everything except PalmMute as onset-only.
3. **There is no changing head bias between performers.** With identical frozen weights, for string s, `z2-z1 = w_s · (h2-h1)`; the bias cancels. Global cosine/Euclidean similarity can conceal changes along a sensitive weight direction. Close embeddings alone cannot justify a head-only repair; far embeddings alone cannot establish which repair will help.
4. **Category pairing is not event alignment.** P1/P2 crops are selected independently and have different event counts. Match by verified source sequence identity, string/fret and local context where possible; report unmatched events. Never zip events by array position or silently choose favorable matches.
5. **The current model has no explicit inter-frame context.** `TinyEventFitModel.forward` is a per-frame 192->128 ReLU MLP with linear heads. CQT frames contain windowed audio, but the model cannot explicitly compare adjacent frames. Missing temporal attack information is a hypothesis worth assessing; it is not yet a demonstrated cause or permission to change architecture.
6. Mixed feature RMS directions do not prove normalization irrelevant. They only fail to support a single simple global-gain explanation. Likewise 15 probes are insufficient for broad performer/content claims.

### Exact next task: one decision-ready OFFLINE package

GPT-5.6 should prepare one combined diagnostic design, implementation, synthetic tests and request-only workflow, before asking for any fresh real-data authorization. Ordinary reversible offline implementation is already permitted by AGENTS.md. Do not ask Stephen to authorize writing the design or synthetic tests.

The package should resolve these questions in one bounded pass rather than create an open-ended sequence of diagnostics:

- **Reproduction first.** Assert exact capture allowlists, 200-frame shapes, source/crop/target identities, model SHA, finite arrays and zero unresolved selected labels against frozen manifests. Current diagnostic loading verifies a feature against its newly generated metadata and four categories, but does not itself compare all source/crop/target identities to the frozen reference. Strengthen this in the new diagnostic without editing old receipts.
- **Resolve raw-versus-scored counts.** The latest diagnostic reports 23 raw P1 decoded events, whereas the decoder-V2 engineering receipt reports 16 scored predictions. Run the identical boundary-exclusion/scoring path and retain event-ID exclusion accounting. Do not assume those seven events are all harmless boundaries without checking. Preserve the 15 raw versus 14 scored P2 distinction explicitly.
- **Check preprocessing reproducibility.** Equal aggregate F1 does not establish numerically equivalent features/logits. If original arrays are available within allowed evidence, compare finite values, shapes and numeric differences under predeclared tolerances; otherwise label numerical equivalence unverified. Do not explain byte-hash differences as harmless solely because package versions match.
- **Probe attacks AND controls.** Include source-defined attack windows, active non-attack/sustain frames and silence, plus per-string positive counts and exclusions. Keep exact center-frame and fixed +/-2-frame results separate. No best-window selection presented as exact onset accuracy and no shifted-label/threshold search.
- **Measure task-relevant margins.** Retain encoder statistics as descriptive context. Record frozen onset logits, `w·h`, constant bias, and pairwise projected differences where valid. For state errors report true fret versus silence AND strongest incorrect fret, with actual softmax/admission outcomes. Examine chords and PalmMute explicitly.
- **Assess temporal-information hypothesis without fitting.** Use fixed, source-aligned neighboring-frame feature changes as descriptive evidence alongside attack/sustain controls; do not tune a new detector on these results. Missing separation is informative, but no observational statistic alone proves a causal repair.
- **Keep outcome branches honest.** Output reproduction failure / insufficient correspondence / descriptive evidence favoring a bounded probe / inconclusive. Do not invent a post-result cutoff for “close embeddings.” If causal isolation is needed, design a controlled intervention next rather than call descriptive geometry a proof.

Proposed ceiling for this diagnostic package: the same eight already-exposed P1/P2 captures, 200 frames each, one frozen model, 0 optimizer steps, unchanged 0.50/0.50 thresholds, one CPU job no longer than the existing 90-minute ceiling, zero automatic retries, no paid compute, P3 sealed. This is a design ceiling, **not execution authorization**. Reuse permitted saved evidence before proposing another source download; do not assume old single-run media grants authorize reuse in a new experiment.

Synthetic tests should target real remaining risks: wrong capture/target rejection, unequal event counts and unmatched correspondence, boundary-accounting consistency, bias-cancellation/projection identity, and attack-versus-sustain controls. Make the exact runnable scope and expected decisions reviewable, then obtain the authorization required by the existing corpus freeze.

### Subsequent fitting and success criteria

If the diagnostic supports a fit, choose ONE predeclared, capped hypothesis test. A frozen-encoder head-only probe is a cheap test of feature usability, not an automatic product fix; it cannot change state errors if only the onset head is trained. A temporal-context candidate is an alternative hypothesis, not an extra automatic candidate. Define budgets, comparator, split, metrics and stop conditions before launch; no sweep, automatic retry, threshold rescue or 2,000-epoch restart.

**Split before fitting.** P2's examined examples are development data. If training on both P1 and P2, neither performer is a performer holdout. A content-disjoint split within P1/P2 can test new content but cannot establish unseen-performer generalization. Group all views/crops of each underlying performance together; hold composition/exercise identities together across performers when claiming unseen-content performance. No random frame split. Newly selected evaluation data require their own authorized scope. Never relabel these four pairs as untouched validation.

Report per-content event precision/recall/F1, state errors, repeated-attack numerator/denominator, offsets, real silence/non-attack false positives, exclusions and runtime. Synthetic silence alone is not real-audio specificity evidence. Predeclare advancement criteria without relaxing historical gates retroactively. If a capped candidate fails, record and stop that candidate; do not extend its budget.

P3 remains sealed for a separately frozen, explicitly authorized final gate after development decisions are finished. Neither isolated direct-input guitar results nor P3 alone should be assumed to establish bass, rhythm/lead selection, mixed-song transcription, playable fingering or customer readiness. Those product requirements need representative, separately designed evaluation later.

### Cost, evidence and handoff discipline

Avoid repeated multi-gigabyte preparation for small numerical questions where permitted derived evidence can suffice. The latest diagnostic artifact expires **2026-10-04T14:52:03Z** according to its receipt. Check the V3 model artifact's availability/expiry too; future workflows depend on it. Plan authorized durable retention of model/derived evidence and manifest hashes before expiration, consistent with data rules; never retrain just to recreate an expired model or commit customer/corpus audio to Git.

Do not multiply workflows and approvals for ordinary offline fixes. Preserve historical launch files and frozen receipts; prepare one coherent next request. If ambiguous after the combined diagnostic, write down which bounded intervention would distinguish hypotheses and its cost rather than automatically ordering another observational run.

**Next response from GPT-5.6 should implement the offline package above and report its tests, remaining uncertainty, and exact proposed execution scope.** No new real-media access, fitting, launch artifact, deployment or production change is authorized by this review. Update this checkpoint after the milestone and verify the remote branch. The historical log below is evidence, not the active task queue.

## Historical direction and execution log (superseded as task queue)

## Direction

Do not restart full V1–V5-style training. V1–V5 remain FAIL; V4 is still the best historical legacy development macro F1 at 0.243523 and V5 remains 0.064131. The V5 onset-admission collapse was already diagnosed. P3 remains sealed.

The economical path is now concrete: preserve explicit source attacks, prove one tiny event-aware candidate can fit four of its own P1 training examples under a hard budget, and only then consider a separate same-budget cross-performer screen.

## Offline preparation completed

- `astra_backend/evaluation/prepared_event_adapter_v1.py` preserves source attack IDs and frozen lag identity; handles carry-in without false onsets; excludes boundary events from event/offset scoring; whole-event masks registered exclusions; and reports unsupported frets, overlaps, negative aligned time, sub-frame attacks and frame-grid collisions instead of silently repairing them.
- `astra_backend/tiny_fit_pilot_v1.py` freezes one candidate only: 192->128 ReLU shared encoder, six-string state head, explicit onset head, random seed 20260921, Adam lr 0.01.
- Onset supervision is explicit source-event supervision, not state changes. The decoder can emit same-string/same-fret reattacks and does not invent a fret-change attack without onset admission.
- Hard code caps: four P1 examples, one view each, 200 frames/example, 200 optimizer steps total, 2700 seconds training/evaluation, 3600 seconds whole job, one candidate, zero automatic retries.
- Exact frozen capture keys:
  1. `P1|chords|Drop3_7|directinput`
  2. `P1|scales|Ab|directinput`
  3. `P1|singlenotes|allsinglenotes|directinput`
  4. `P1|techniques|PalmMute|directinput`
- Future real source handling lists each pinned ZIP then extracts exactly one selected MIDI plus one direct-input audio member. Unrelated media is not extracted.
- `docs/astra/TINY_FIT_PILOT_DESIGN_V1.json` is the exact design blob verified by the synthetic gate. Do not edit it without re-running verification.

## Exact-runtime synthetic gate — PASS

GitHub Actions run **36275788105**, job **108498148554**, head `2975017d9632f75a9e24e4eb5d8e3b2ae0546468`: **SUCCESS**.

Verified runtime: Python 3.10.15, NumPy 1.21.6, Torch 1.11.0+cpu, CPU.

The gate passed:
- event-contract regression tests;
- fabricated prepared-event adapter tests;
- tiny-fit component/cap tests;
- stable source attack IDs;
- carry-in with no false onset;
- whole-event mask semantics;
- same-fret reattack decoding;
- explicit onset supervision;
- finite synthetic backward pass and decreasing synthetic loss;
- optimizer-cap and wall-cap extension rejection;
- selected-ZIP extraction isolation.

Execution boundary: **20 synthetic optimizer-step operations only; 0 real optimizer steps; no P1, P2 or P3 media accessed; no paid compute.**

Frozen receipt: `docs/astra/TINY_FIT_PILOT_SYNTHETIC_VERIFICATION_V1.json`.  
GitHub artifact ID: `10917501716`.

## Dormant real pilot

`.github/workflows/astra-tiny-fit-pilot-real.yml` is prepared but intentionally has **no workflow_dispatch**. It can trigger only when a future `docs/astra/TINY_FIT_PILOT_REAL_LAUNCH_V1.json` is committed.

Before media access it requires:
1. the frozen synthetic receipt;
2. a separately created real authorization document explicitly granting this exact P1-only 200-step scope;
3. a source-pinned launch document matching all frozen Git blobs.

It has a 60-minute GitHub CPU job timeout, no P2/P3 source path, no automatic retry, and no route to full training.

## Current authorization / launch boundary

The user explicitly continued with the exact frozen P1 scope in chat on 2026-09-26.

Created once:
- `docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_V1.json`
- `docs/astra/TINY_FIT_PILOT_REAL_LAUNCH_V1.json`

Launch commit: `9aa5c9e89a41e08c2cc25681bf77fe481020a608`.  
Canonical capped P1 workflow run: **36276196059**, job **108499312084**.

This authorization applies only to that single bounded run: four specified P1 training examples, one view each, 200 frames/example, at most 200 optimizer steps total, one candidate, zero retries, zero paid compute. **Do not create a second launch artifact, rerun the workflow, extend optimizer steps, open P2/P3, retune thresholds, or restart full training without new explicit authorization.**

## Advancement rule if the real pilot is later authorized

Training-example explicit-event F1 >= 0.95; matched offsets within 50 ms >= 0.90; repeated-attack coverage must be present and recall >= 0.90; all metrics finite; zero unresolved selected-crop labels.

Passing is only an engineering learnability screen. It does not prove generalization and does not authorize full training, P2/P3, production use or customer delivery. Failure stops the candidate; no extra epochs, retries, threshold rescue or second architecture are automatic.

## Verification notes

The earlier workflow-definition failures at runs created before the UTF-8 workflow repair are configuration-only and are not pilot evidence. The repaired synthetic run above is the canonical verification.

Normal `Astra backend tests` also passed on the design-trigger commit. Historical V1–V5 results and Event-v2 evidence remain unchanged.

## Preserved history

The pre-pilot history remains at `docs/checkpoints/archive/CURRENT_STATE_2026_09_26_PRE_PILOT.md` (original Git blob `1ae91540ac02133a4a1c63989350ad615f065954`). Consult specific sections only when needed.

## Explicit next steps for the next chat

1. Inspect canonical run **36276196059** / job **108499312084**. Do not launch or rerun anything.
2. If it is still in progress, record the current step only; the existing run is the sole authorized real P1 execution.
3. When it completes, inspect the bounded result and artifact. Preserve run ID, job ID, head SHA, runtime versions, prepared-example/source hashes, optimizer-step count, elapsed time, metrics, unresolved-label counts, stop reason, and artifact identity in a frozen result receipt and this checkpoint.
4. If it fails or stops before/during optimizer work, preserve evidence and diagnose the existing run only. No automatic retry, no added steps/epochs, no threshold rescue, no second candidate, no P2/P3, and no V6/full-training restart.
5. If it passes every frozen training-only threshold, preserve evidence and stop. Passing permits only the future **design** of a separate same-budget cross-performer screen; it does not itself authorize that screen or any full training.

Frozen advancement conditions remain:
- minimum per-example explicit-event F1 >= 0.95;
- matched-offset-within-50-ms fraction >= 0.90;
- repeated same-string/same-fret attack coverage present;
- repeated-attack recall >= 0.90 when present;
- all metrics finite;
- unresolved selected-crop label count = 0.

Current state at this checkpoint: **one capped P1 pilot authorized and launched; canonical run 36276196059 in progress; no second launch/rerun authorized; P2/P3 closed; full training not restarted.**

## Capped P1 pilot attempt 1 — PREPARATION FAILURE, NOT A MODEL RESULT

Canonical run **36276196059**, job **108499312084**, launch head `9aa5c9e89a41e08c2cc25681bf77fe481020a608`, attempt 1 completed **failure**.

The authorization/hash gate and exact frozen runtime installation passed. The run failed in **Prepare exactly four selected P1 training examples** before the training step. Therefore:
- real optimizer steps executed: **0**;
- model fitting/evaluation did not run;
- no advancement metrics exist;
- P2 and P3 were not accessed;
- no bounded-result artifact was uploaded;
- cleanup completed successfully.

P1 media access was limited to the first pinned archive, `P1_chords.zip`. Its hash checks passed, and exactly the selected `Drop3_7` MIDI and direct-input WAV were extracted before the preparation guard stopped:
- MIDI: `P1_chords/midi/midi_Drop3_7.mid`, 2729 bytes, SHA-256 `a5856f6a6c1306fa6f0070ba8cf14dd8d61c60f1e3cc852695e5e05031c2274a`;
- audio: `P1_chords/audio/directinput/directinput_Drop3_7.wav`, 29532984 bytes, SHA-256 `c3dccbba8365eb1a701c2bf47dca6aae8be894aff768323cea19ad00a3d1d34e`.

Failure:
`RuntimeError: metadata selection no longer matches frozen pilot capture keys`

Root cause: `select_pilot_capture_keys()` sorted bare performance names. With the real correction map, bare `"A"` sorts before `"Ab"`, while the frozen scale capture is `P1|scales|Ab|directinput`. The frozen identity was derived from full capture-key lexical ordering, where the separator makes `...|Ab|...` sort before `...|A|...`. The synthetic unit fixture omitted the competing `A` key, so this inconsistency escaped verification.

Offline repair: order performances by their lexicographically first **full capture key** and add a regression fixture containing both `A` and `Ab`. This does not change the four frozen capture identities, architecture, objective, thresholds, training budget, or P2/P3 boundary.

**The failed authorization was single-launch. A second real P1 run is not authorized.** After exact-runtime synthetic re-verification of the repair, create a new source-pinned authorization request and require new explicit user authorization before another real media/optimizer run.

## Offline repair verification — PASS

Repair commit: `12632441e4fc90ce41d0315ec3b9174f2a569607`.

Exact-runtime synthetic verification run **36277137786**, job **108501969202**: **SUCCESS**. Normal backend tests run **36277137773** also passed.

The repaired selector regression explicitly includes both P1 scale performances `A` and `Ab`, and `test_metadata_only_selection_is_frozen` passes while retaining the original frozen capture key `P1|scales|Ab|directinput`.

Repair verification boundary: **0 real optimizer steps; no P1/P2/P3 media accessed; no paid compute.** Candidate architecture, objective, thresholds, 200-step cap, four frozen capture keys and P2/P3 boundaries are unchanged.

Frozen repaired receipt: `docs/astra/TINY_FIT_PILOT_SYNTHETIC_VERIFICATION_V2.json`.
Final V2 request blob: `9a2ad838e8e6e4de1d53ceee45fc35e0bc1b6bfe`.  
Dormant V2 workflow blob: `2e8a16371c11ca5ef7bf9aba3d2b4fbb9ec11324`.  
Synthetic artifact ID: `10917224706`.

## Retry gate — REQUEST ONLY

A new reviewable request is frozen at:
`docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_REQUEST_V2.json`.

A separate dormant retry workflow is prepared at:
`.github/workflows/astra-tiny-fit-pilot-real-v2.yml`.

The V2 workflow triggers only on a future commit of `docs/astra/TINY_FIT_PILOT_REAL_LAUNCH_V2.json`. That launch file does **not** exist. `TINY_FIT_PILOT_REAL_AUTHORIZATION_V2.json` also does **not** exist.

**Do not rerun attempt 1 and do not create V2 authorization/launch artifacts unless the user explicitly authorizes the exact V2 request.**

If explicitly authorized, verify every V2-pinned blob, create `TINY_FIT_PILOT_REAL_AUTHORIZATION_V2.json` matching the request exactly, then create exactly one source-pinned `TINY_FIT_PILOT_REAL_LAUNCH_V2.json`. One retry only; zero automatic retries.

Attempt 1 remains non-model evidence: 0 optimizer steps. P2/P3 remain closed and full training remains stopped.

## V2 capped P1 retry — AUTHORIZED AND LAUNCHED ONCE

User explicitly authorized the frozen V2 request in chat on 2026-09-26.

Created:
- `docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_V2.json`
- `docs/astra/TINY_FIT_PILOT_REAL_LAUNCH_V2.json`

Authorization commit: `5942493a9fc373e5fe20f9c7aeee21d58e7caedc`.  
Launch commit: `891bbcc00391163fc4820235886d3ca1be76c113`.  
Canonical V2 workflow run: **36277631151**, job **108503320536**.

Scope remains exactly frozen: four specified P1 training performances, one view each, 200 frames/example, at most 200 optimizer steps total, 2700-second train/eval cap, 3600-second job cap, one candidate, zero automatic retries, zero paid compute. P2/P3 remain closed; full training remains stopped.

**Do not create another V2 launch, rerun this workflow, extend optimizer steps, retune thresholds, open P2/P3, or restart full training without new explicit authorization.**

Next action: inspect only run **36277631151**. Preserve its result/failure evidence when complete. If it fails, diagnose that existing run only. If it passes, preserve evidence and stop; no cross-performer screen is authorized yet.

## V2 capped P1 retry — PREPARATION FAILURE, NOT A MODEL RESULT

Canonical run **36277631151**, job **108503320536**, launch head `891bbcc00391163fc4820235886d3ca1be76c113`: **FAILURE during preparation**.

The V2 selector repair passed: authorization/source pins and runtime setup succeeded, and the first frozen capture `P1|chords|Drop3_7|directinput` was selected. The run then stopped because its chosen 200-frame event crop was not launch-ready:

`RuntimeError: prepared pilot example has unresolved labels`

Execution boundary:
- real optimizer steps: **0**;
- training/evaluation: **not executed**;
- P1 media access: first pinned chords archive only;
- P2/P3 access: **none**;
- automatic retry: **none**;
- result artifact: **none**;
- cleanup: **success**.

The exact unresolved subtype is **not recoverable from this run** because the V2 harness wrote the temporary metadata locally but raised before printing the unresolved diagnostics; cleanup then removed the temporary files. Do not invent whether it was overlap, sub-frame attack, frame-grid collision, unsupported fret or another registered unresolved condition.

Frozen failure receipt: `docs/astra/TINY_FIT_PILOT_REAL_FAILURE_V2.json`.

## Offline crop-repair direction

The next offline design is `docs/astra/TINY_FIT_PILOT_DESIGN_V2.json`.

It keeps the same four P1 captures, model architecture, objective, thresholds and 200-step budget. The only preparation change is source-driven and training-only: enumerate deterministic repeated-attack candidates first, then individual source-attack candidates, and select the earliest crop whose prepared labels are `launchReady` with zero unresolved selected-crop labels. Rejected candidates are not repaired; their unresolved-code summaries are retained. If no clean crop exists, fail closed before optimizer work.

The real harness now emits `TINY_FIT_PREPARE_REJECT=` structured diagnostics before a crop-preparation stop.

**No further real P1 run is authorized.** First require exact-runtime synthetic verification of this offline repair. Only after a frozen successful verification may a new request-only authorization artifact be prepared.

## Launch-ready crop repair — exact-runtime verification PASS

Repair commit: `192d61755924f296604fb1706666228e70dff378`.

Synthetic verification run **36279935269**, job **108509713391**: **SUCCESS**. Backend tests run **36279935295**: **SUCCESS**.

Verified in Python 3.10.15 / NumPy 1.21.6 / Torch 1.11.0+cpu:
- launch-ready crop selection skips unresolved candidates;
- an all-unresolved candidate set fails closed;
- unresolved crop rejection diagnostics are retained;
- existing event/carry/mask/reattack tests still pass;
- synthetic backward/loss-decrease and hard budget-extension guards still pass.

Verification boundary: **0 real optimizer steps; no P1/P2/P3 media accessed; no paid compute.**

Frozen receipt: `docs/astra/TINY_FIT_PILOT_SYNTHETIC_VERIFICATION_V3.json`.  
Artifact ID: `10917829509`.

## V3 retry gate — REQUEST ONLY

Request: `docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_REQUEST_V3.json`.
Final V3 request blob: `00f74000650b97dc48f978cd05e4ee673aaf085c`.  
Dormant V3 workflow blob: `ccf8f50c28c49fce097f66e53bafb5bc7c7cc45c`.  
Dormant workflow: `.github/workflows/astra-tiny-fit-pilot-real-v3.yml`.

The request is not authorization. `TINY_FIT_PILOT_REAL_AUTHORIZATION_V3.json` and `TINY_FIT_PILOT_REAL_LAUNCH_V3.json` do not exist.

The V3 workflow can trigger only on a future V3 launch document and remains capped at the same four P1 captures, 200 frames/example, at most 200 optimizer steps, one candidate, zero retries, zero paid compute. P2/P3 remain closed; full training remains stopped.

**Require new explicit user authorization of the exact V3 request before any further P1 media access or real optimizer step.**

## V3 pre-launch guard repair

A final pre-launch verification found an impossible self-reference in the dormant V3 workflow: it required `TINY_FIT_PILOT_REAL_AUTHORIZATION_V3.json` to contain the Git blob SHA of itself before that blob could exist.

This was caught **before** creating a V3 authorization artifact, launch artifact, accessing any further P1 media, or executing any real optimizer step.

Repair: the future launch artifact must pin the authorization blob; the authorization artifact must pin every pre-existing frozen source but does not self-pin. This changes no capture, crop rule, model, objective, threshold, optimizer budget, P2/P3 boundary, or retry policy.

The user's chat authorization immediately preceding this discovery was **not consumed** because the exact frozen request was found invalid before authorization materialization. The repaired request must be explicitly authorized again before a V3 authorization or launch artifact is created.

## Repaired V3 capped P1 retry — AUTHORIZED AND LAUNCHED ONCE

User explicitly authorized the repaired V3 request in chat on 2026-09-26.

Created:
- `docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_V3.json`
- `docs/astra/TINY_FIT_PILOT_REAL_LAUNCH_V3.json`

Authorization commit: `cb9916e409bd0fbb9790f592c02ba484619ab548`.  
Launch commit: `70e0cdb2440357dbcb61005b8a5ca1b49ff32329`.  
Canonical V3 workflow run: **36280547470**, job **108511412597**.

Scope remains exactly frozen: four specified P1 training performances, one view each, 200 frames/example, at most 200 optimizer steps total, 2700-second train/eval cap, 3600-second job cap, one candidate, zero automatic retries, zero paid compute. P2/P3 remain closed; full training remains stopped.

**Do not create another V3 launch, rerun this workflow, extend optimizer steps, retune thresholds, open P2/P3, or restart full training without new explicit authorization.**

Next action: inspect only run **36280547470**. If it fails before/during optimizer work, preserve and diagnose that single run only. If it completes training, preserve exact metrics/evidence and stop; no cross-performer screen or broader training is authorized.

## V3 capped P1 result — WORKFLOW GREEN, ENGINEERING GATE NOT MET

Canonical run **36280547470**, job **108511412597**, launch head `70e0cdb2440357dbcb61005b8a5ca1b49ff32329`: **GitHub Actions SUCCESS**.

All four P1 examples prepared successfully with zero unresolved selected-crop labels. The one authorized candidate completed exactly **200 optimizer steps** and stopped at `requested_steps_reached`.

Fit evidence:
- total loss: **5.8937435 -> 0.0399992**
- state loss: **3.0180442 -> 0.0124796**
- onset loss: **0.7189248 -> 0.0068799**

Engineering screen:
- recall on every example: **1.0**
- repeated-attack recall: **1.0**
- matched offsets within 50 ms: **0.9375** (passes 0.90)
- unresolved selected-crop labels: **0**
- minimum per-example event F1: **0.50** (fails required 0.95)
- `engineeringAdvancementThresholdsMet=false`

Per-example F1:
- Drop3_7 chord: **0.705882**
- Ab scale: **0.941176**
- allsinglenotes: **0.50**
- PalmMute: **0.666667**

Totals: **16 references, 25 predictions, 16 true positives, 9 false positives, 0 false negatives**. This is a precision/extra-attack failure, not a recall failure.

### Boundary scoring mismatch

The preparation contract retains carry-out attacks as positive onset targets but excludes carry-out events from `scorableEvents`. The evaluator decodes all model events and scores them only against `scorableEvents`.

These four crops contain **7 carry-out positive target attacks**. `onsetAdmissionRecall=1.0` on every example. Therefore boundary scoring explains **7 of the 9 observed false positives** under the current evaluator; **2 non-boundary extra attacks remain**.

This does not convert the pilot into a pass: even boundary-adjusted diagnostic accounting still leaves the minimum example below the frozen 0.95 F1 gate. No thresholds were retuned and no rerun occurred.

Frozen result: `docs/astra/TINY_FIT_PILOT_REAL_RESULT_V3.json`.  
Actions artifact: **10918434248**, digest `sha256:4b62ad7336a216cbee0bf8a52c3c9c56d51eca7f963702c95bba7be320a7c573`.  
Result JSON SHA-256: `1bda3d5b7c790641742a99c07685c8d477938cd7426ad48f58d84928a3328647`.  
Model SHA-256: `fba076f8b6e5fe177ba7b15e5d6780269194f530b2648037ac0763a4937eb67f`.

**Stop here.** Do not rerun V3, add optimizer steps, retune thresholds, open P2/P3, start a cross-performer screen, or restart full training. Cheapest next work: repair the evaluator boundary contract offline and design a zero-optimizer diagnostic that records decoded prediction events. Any new P1 media access or optimizer work requires fresh explicit authorization.

## V3 zero-optimizer boundary diagnostic — AUTHORIZED, PRE-LAUNCH

User instruction: **"Run the diagnostic."**

Authorized scope only:
- reprepare the same four frozen P1 crops;
- load the exact frozen V3 200-step model artifact;
- execute inference/scoring only, **0 optimizer steps**;
- reproduce the raw V3 score exactly;
- rescore with whole-event carry-in/carry-out boundary exclusions through the existing Event-v2 exclusion contract;
- record each remaining unmatched prediction with decoder probabilities and target/reference context.

No threshold retuning, model mutation, P2/P3, cross-performer screen, automatic retry, or full training is authorized.

Design: `docs/astra/TINY_FIT_V3_DIAGNOSTIC_DESIGN_V1.json`.  
Authorization: `docs/astra/TINY_FIT_V3_DIAGNOSTIC_AUTHORIZATION_V1.json`.  
Dormant workflow: `.github/workflows/astra-tiny-fit-v3-diagnostic.yml`.

The diagnostic workflow remains inert until exactly one `docs/astra/TINY_FIT_V3_DIAGNOSTIC_LAUNCH_V1.json` is committed after tests/source pins are verified.

## V3 zero-optimizer boundary diagnostic — LAUNCHED ONCE

User authorized this diagnostic by instructing **"Run the diagnostic."**

Launch commit: `f581e98c0999ca9e4ef4ece2cea103df462b3800`.  
Canonical diagnostic run: **36281561748**.

Authorized execution remains:
- same four frozen P1 examples;
- exact frozen V3 model artifact from run 36280547470;
- **0 optimizer steps**;
- no threshold retuning or model mutation;
- no P2/P3;
- no automatic retry;
- no full training or cross-performer screen.

**Do not create another diagnostic launch or rerun this workflow.** Inspect run **36281561748** only. On completion, freeze the diagnostic JSON and exact remaining false-positive event evidence.

## V3 zero-optimizer diagnostic V1 — EVALUATOR INSTRUMENTATION FAILURE

Run **36281561748**, job **108514239716** failed inside the diagnostic evaluator after:
- authorization/source-pin verification: PASS;
- exact frozen V3 artifact download/hash verification: PASS;
- same four P1 examples re-prepared: PASS;
- optimizer steps executed: **0**.

Failure:
`ValueError: events require unique nonempty IDs`

Root cause is a Python module-identity mismatch, not duplicate IDs: `tiny_fit_pilot_v1.py` creates events using `evaluation.event_contract_v2.Event`, while the diagnostic imported the same source file as top-level `event_contract_v2.Event`. Those are different Python class objects, so `validate_events()` rejected valid decoder events at its `isinstance` check.

Offline repair: use the canonical `evaluation.event_contract_v2` namespace in the diagnostic and add a regression that sends actual `decode_event_list()` events through `detailed_score()`.

Frozen failure receipt: `docs/astra/TINY_FIT_V3_DIAGNOSTIC_FAILURE_V1.json`.

**Do not rerun diagnostic V1.** The original diagnostic authorization specified zero automatic retries. After backend tests pass, prepare a new request-only V2 diagnostic gate; a second diagnostic run requires new explicit authorization.

## Repaired zero-optimizer diagnostic V2 — REQUEST ONLY

Namespace-repair commit: `cdf874c3d3a6c2429441c9f23605bafe407e4026`.  
Verification run **36281862601**: **SUCCESS** for complete backend and focused evaluation suites.

The repair changes only Python import identity: the diagnostic now uses canonical `evaluation.event_contract_v2.Event`, matching `tiny_fit_pilot_v1.py`. A regression sends actual `decode_event_list()` events through the diagnostic scorer and passes.

Request: `docs/astra/TINY_FIT_V3_DIAGNOSTIC_AUTHORIZATION_REQUEST_V2.json`.  
Dormant retry workflow: `.github/workflows/astra-tiny-fit-v3-diagnostic-v2.yml`.

No V2 diagnostic authorization or launch exists. The retry remains **0 optimizer steps**, same four P1 crops, exact frozen V3 model, unchanged thresholds, no P2/P3.

**Require new explicit user authorization before creating `TINY_FIT_V3_DIAGNOSTIC_AUTHORIZATION_V2.json` or `TINY_FIT_V3_DIAGNOSTIC_LAUNCH_V2.json`.**

## Repaired zero-optimizer diagnostic V2 — AUTHORIZED AND LAUNCHED ONCE

User explicitly authorized the repaired diagnostic V2 in chat on 2026-09-26.

Created:
- `docs/astra/TINY_FIT_V3_DIAGNOSTIC_AUTHORIZATION_V2.json`
- `docs/astra/TINY_FIT_V3_DIAGNOSTIC_LAUNCH_V2.json`

Authorization commit: `b8b85ea8e1948e8693efc15f441c4a973c9f4d50`.  
Launch commit: `a1b84b8a572678eae6d6c77af1fc0aaa4e19d0bc`.  
Canonical diagnostic V2 run: **36282028911**.

Scope remains:
- exact frozen V3 model and result artifact;
- same four P1 crops;
- **0 optimizer steps**;
- unchanged thresholds/model weights;
- no P2/P3;
- zero automatic retries;
- no cross-performer screen or full training.

**Do not create another V2 diagnostic launch or rerun this workflow without new explicit authorization.** Inspect only run **36282028911**. If it completes, freeze the exact boundary-corrected metrics and remaining unmatched prediction events. If it fails, preserve and diagnose that run only.

## Repaired zero-optimizer diagnostic V2 — GREEN

Canonical run **36282028911**, job **108515568798**: **SUCCESS**.

Execution boundary:
- exact frozen V3 model loaded and hash-verified;
- same four P1 crops re-prepared;
- optimizer steps: **0**;
- thresholds/model weights/crop selection: **unchanged**;
- P2/P3: **not opened**.

Raw V3 accounting reproduced exactly: **16 references, 25 predictions, 16 TP, 9 FP, 0 FN**.

Boundary-corrected accounting:
- references: **16**
- predictions: **17**
- true positives: **16**
- false positives: **1**
- false negatives: **0**
- minimum per-example F1: **0.9230769231**
- matched offsets within 50 ms: **0.9375**
- frozen 0.95 per-example F1 gate: **still not met**

Per-example boundary-corrected F1:
- PalmMute: **1.0**
- allsinglenotes: **1.0**
- Drop3_7: **0.9230769231**
- Ab scale: **1.0**

The boundary correction excludes **8 of the 9** raw false positives, confirming the V3 evaluator was substantially contaminated by carry-in/carry-out scoring.

### One genuine remaining false positive

Only one unmatched prediction remains, on `P1|chords|Drop3_7|directinput`:

- prediction ID: `diag:2:s1:2`
- string index: **1 (A string)**
- fret: **0**
- predicted onset: **0.2321995465 s**
- nearest true same-string/same-fret onset: **0.2058412698 s**
- onset delta: **+0.0263582766 s**
- the true reference remains active until **0.2370912698 s**
- target state at predicted onset: **fret 0 active**
- target onset at predicted onset: **0**
- onset probability: **0.5066716671**
- frozen onset threshold: **0.5**
- margin over threshold: only **0.0066716671**
- active probability: **0.7487640977**
- silence probability: **0.2512359321**

Classification: **same-string/same-fret duplicate reattack inside a still-active true note**. This is not a wrong-note error and not a recall error. The decoder split a held note because a borderline onset score barely crossed 0.5.

Frozen result: `docs/astra/TINY_FIT_V3_DIAGNOSTIC_RESULT_V2.json`.  
Diagnostic artifact: **10918344868**, digest `sha256:7010e18f691153be935541898fdaf916f15ea7a592f25b3d3885340f577cd4ad`.  
Diagnostic JSON SHA-256: `c960a86f9f2847656598afb1ed790161bccca5bfe7700dfffc28027ac340842d`.

**Stop here.** Do not retrain, retune thresholds, rerun the diagnostic, open P2/P3, or start a cross-performer screen without new explicit authorization.

Cheapest next question: design an offline decoder-contract test for a short refractory/event-identity rule that suppresses this within-note duplicate reattack while preserving true same-fret repeated attacks. This should be tested first on synthetic and frozen-logit evidence with **0 optimizer steps**.

## V3 zero-optimizer diagnostic V2 — GREEN

Canonical run **36282028911**, job **108515568798**: **SUCCESS**.

Execution boundary:
- optimizer steps: **0**;
- thresholds changed: **no**;
- model weights changed: **no**;
- same four P1 crops reproduced: **yes**;
- P2/P3: **not opened**.

Raw V3 totals reproduced exactly: **16 references, 25 predictions, 16 TP, 9 FP, 0 FN**.

With whole-event carry-in/carry-out exclusions passed through the existing Event-v2 scoring contract:
- corrected totals: **16 references, 17 predictions, 16 TP, 1 FP, 0 FN**;
- matched offsets within 50 ms: **0.9375**;
- corrected minimum per-example F1: **0.923077**.

Corrected F1:
- PalmMute: **1.0**
- allsinglenotes: **1.0**
- Ab scale: **1.0**
- Drop3_7: **0.923077**

The boundary mismatch therefore explains **8 of the original 9 false positives**.

### Only remaining false positive

Capture: `P1|chords|Drop3_7|directinput`  
String: A (string index 1)  
Fret: 0  
Predicted onset: **0.23220 s**  
Nearest real same-string/fret onset: **0.20584 s**  
Delta: **+26.36 ms**

At the false onset frame:
- onset probability: **0.506672**
- frozen onset threshold: **0.50**
- margin above threshold: **+0.006672**
- active-state probability: **0.748764**
- target state: active fret 0
- target onset: **0**

This is a **near-threshold duplicate onset while the correct note state remains active**, not a wrong-note/state prediction.

Frozen diagnostic result: `docs/astra/TINY_FIT_V3_DIAGNOSTIC_RESULT_V2.json`.  
Artifact: **10918344868**, digest `sha256:7010e18f691153be935541898fdaf916f15ea7a592f25b3d3885340f577cd4ad`.

The corrected result still does **not** meet the frozen 0.95 per-example F1 gate because Drop3_7 remains at 0.923077. No threshold retuning is permitted retroactively.

**Next cheapest step:** offline analysis of duplicate-onset suppression / onset-separation semantics around this single event. Do not retrain, retune thresholds, open P2/P3, or start a cross-performer screen yet.

## Offline decoder V2 candidate — same-fret onset rising-edge gate

Frozen diagnostic V2 isolated one remaining false positive: A string, fret 0, in Drop3_7. The real source onset maps to target frame **9**; the false predicted reattack starts at frame **10**, exactly one 23.22 ms frame later. The false frame has target onset 0 and onset probability **0.506672**, only **0.006672** above the frozen 0.50 threshold.

Frozen V3 metadata contains two genuine scorable same-string/same-fret reattacks:
- Ab scale high-e fret 4: target frames 9 -> 30 (**21 frames / 487.6 ms grid spacing**);
- Drop3_7 A-string open: target frames 9 -> 185 (**176 frames / 4.0867 s grid spacing**).

Candidate `astra_backend/evaluation/event_decoder_v2.py` leaves both frozen thresholds at 0.50 but changes same-fret reattack semantics: while the same fret remains active, a reattack requires a **fresh below->above onset-threshold crossing**. Consecutive suprathreshold onset frames therefore remain one attack. Different-fret admitted onsets and state-change-without-onset behavior remain unchanged.

Synthetic regressions cover:
- consecutive same-fret onset plateau => one attack;
- separated fresh same-fret threshold crossing => two attacks;
- different-fret onset during an onset plateau => preserved;
- fret change without onset => still no invented attack.

Analysis receipt: `docs/astra/V3_REATTACK_DECODER_ANALYSIS_V1.json`.

This is offline evidence only. **No P1 media has been newly accessed for this decoder candidate, no optimizer step has run, and no threshold has been retuned.** After tests pass, the next permissible action is only to freeze a request for one zero-optimizer P1 re-decode with decoder V2; that real-data check requires new explicit authorization.

## Decoder V2 zero-optimizer P1 re-decode — REQUEST ONLY

Decoder V2 candidate commit `a7ce312ffb51037d5f9d978c676f721b69d1fd6f` passed complete backend and focused evaluation suites in run **36283349847**.

A dormant real-P1 check is staged to answer one narrow question: does the rising-edge same-fret decoder remove the single residual Drop3_7 false onset while preserving all true attacks, repeated-attack recall, offset quality, and silence behavior?

The check uses:
- exact frozen V3 model and hashes;
- exact same four P1 crops;
- boundary-corrected Event-v2 scoring;
- state threshold **0.50** and onset threshold **0.50** unchanged;
- **0 optimizer steps**;
- decoder V1 corrected metrics must reproduce diagnostic V2 before decoder V2 is interpreted.

Request: `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_AUTHORIZATION_REQUEST_V1.json`.  
Design: `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_DESIGN_V1.json`.  
Dormant workflow: `.github/workflows/astra-tiny-fit-v3-decoder-v2-check.yml`.

No authorization or launch file exists. **Fresh explicit authorization is required before any new P1 media access.** A pass would remain training-example evidence only and would not authorize P2/P3, cross-performer screening, or full training.

## Decoder V2 zero-optimizer P1 check — AUTHORIZED AND LAUNCHED ONCE

User explicitly authorized the frozen decoder V2 request in chat on 2026-09-26.

Created:
- `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_AUTHORIZATION_V1.json`
- `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_LAUNCH_V1.json`

Authorization commit: `d3c9382782d9128b3f14bd92043e468b402e81a4`.  
Launch commit: `e45bc98ca9e7fbc38865987792ddff6aacabd137`.  
Canonical decoder V2 check run: **36283779556**, job **108520534718**.

Authorized scope remains:
- exact frozen V3 model and hashes;
- same four frozen P1 examples;
- decoder V2 rising-edge same-fret semantics;
- state threshold 0.50 and onset threshold 0.50 unchanged;
- **0 optimizer steps**;
- no threshold retuning;
- no model mutation;
- no P2/P3;
- zero automatic retries;
- no cross-performer screen or full training.

**Do not create another decoder V2 launch or rerun this workflow.** Inspect run **36283779556** only. On completion, freeze the exact V1 reproduction, decoder V2 metrics, remaining FP/FN evidence, repeated-attack recall, offset fraction, and engineering training-only gate. A pass does not establish generalization.

## Decoder V2 zero-optimizer P1 check V1 — FEATURE-BYTE IDENTITY FAILURE

Run **36283779556**, job **108520534718** passed authorization/source pins, frozen V3 artifact hashes, and preparation of all four exact P1 crops. It executed **0 optimizer steps** and failed before decoder V2 could be interpreted.

Failure:
`RuntimeError: prepared examples differ from frozen V3 target set`

All crop selections and target hashes reproduced exactly, but all four CQT feature byte hashes differed from the frozen V3 hashes. The successful diagnostic V2 and this failed check used the same Ubuntu runner image and pinned Python/NumPy/SciPy/librosa/Torch versions, so feature SHA byte equality is not a reliable semantic invariant for the hosted preprocessing path.

Repair: feature SHA remains recorded provenance, but the gate now requires exact non-feature source/crop/target identity and then requires decoder V1's boundary-corrected totals and minimum F1 to reproduce frozen diagnostic V2 exactly before decoder V2 may be interpreted.

Frozen failure: `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_FAILURE_V1.json`.

No retry is authorized. After tests pass, freeze a new request-only repaired decoder V2 check.

## Repaired decoder V2 zero-optimizer P1 check retry V2 — REQUEST ONLY

Check V1 run **36283779556** stopped before decoder V2 interpretation because all four re-prepared CQT feature byte hashes differed from frozen V3, despite exact crop/target reproduction and the same runner image/pinned software. It executed **0 optimizer steps**.

Repair:
- feature SHA is retained as provenance, not semantic equality;
- exact non-feature source/crop/target identity is still required;
- decoder V1 boundary-corrected totals must reproduce diagnostic V2 exactly;
- decoder V1 boundary-corrected minimum F1 must reproduce diagnostic V2 exactly;
- only after those semantic guards pass may decoder V2 be interpreted.

Repair code run **36284377888**: SUCCESS.  
Regression/test run **36284381574**: SUCCESS.

Frozen V1 failure: `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_FAILURE_V1.json`.  
Retry V2 request: `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_AUTHORIZATION_REQUEST_V2.json`.  
Dormant retry workflow: `.github/workflows/astra-tiny-fit-v3-decoder-v2-check-v2.yml`.

No V2 authorization or launch exists. **Fresh explicit authorization is required before any new P1 media access or inference.** Scope remains exact frozen V3 model, same four P1 crops, decoder V2, unchanged 0.50/0.50 thresholds, 0 optimizer steps, no P2/P3, no automatic retry.

## Repaired decoder V2 zero-optimizer P1 check retry V2 — AUTHORIZED AND LAUNCHED ONCE

User explicitly authorized the repaired retry request in chat on 2026-09-26.

Authorization commit: `99b7dc85c7737d7ba4c59e8680a7f9e80aea22e6`.  
Launch commit: `5c9e9eb00cc777ee1ef81ca88d31e3b6f0982237`.  
Canonical retry V2 run: **36284602349**.

Authorized scope remains:
- exact frozen V3 model and artifact hashes;
- same four frozen P1 examples;
- decoder V2 rising-edge same-fret semantics;
- decoder V1 boundary-corrected semantic metrics must reproduce before decoder V2 is interpreted;
- state/onset thresholds remain 0.50 / 0.50;
- **0 optimizer steps**;
- no model mutation;
- no P2/P3;
- zero automatic retries;
- no cross-performer screen or full training.

**Do not create another retry V2 launch or rerun this workflow.** Inspect run **36284602349** only.

## Decoder V2 zero-optimizer P1 check retry V2 — GREEN, TRAINING-ONLY GATE MET

Canonical run **36284602349**, job **108522850285**: **SUCCESS**.

The repaired semantic guard passed before decoder V2 interpretation:
- decoder V1 boundary-corrected totals reproduced exactly: **16 references, 17 predictions, 16 TP, 1 FP, 0 FN**;
- decoder V1 corrected minimum per-example F1 reproduced exactly: **0.9230769231**.

Decoder V2 then produced:
- **16 references, 16 predictions, 16 TP, 0 FP, 0 FN**;
- PalmMute F1: **1.0**;
- allsinglenotes F1: **1.0**;
- Drop3_7 F1: **1.0**;
- Ab scale F1: **1.0**;
- minimum per-example F1: **1.0**;
- matched offsets within 50 ms: **0.9375**;
- repeated reference attacks: **2**;
- repeated-attack recall: **1.0**;
- synthetic silence false positives: **0**;
- unresolved labels: **0**;
- `engineeringTrainingOnlyGateMet=true`.

Decoder V2 uses the same frozen 0.50 state/onset thresholds and the same frozen V3 model weights. It executed **0 optimizer steps**. The only decoder semantic change is same-fret reattack admission requiring a fresh below->above onset-threshold crossing while the same fret remains active.

Frozen result: `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_RESULT_V2.json`.  
Result commit: `2a0de5c7a4ffe86325f9320f47e45fb811244380`.  
Actions artifact: **10919563631**, digest `sha256:099b87369a12cf6117e69199edfac292aee0af14b09746dddd1f118390676446`.  
Result JSON SHA-256: `1d974927660bd41fcb2e2367c172580720a2b72b2b4a6051cb4c786f7ded2c2d`.

### Meaning and hard boundary

This **establishes engineering learnability on the four selected P1 training examples** with decoder V2. It does **not** establish cross-performer generalization, customer readiness, or justify full training by itself.

**Stop here.** No P2/P3 access, cross-performer screen, full training, customer delivery, or additional optimizer work is authorized. The next scientifically meaningful step is a separately designed cross-performer/generalization screen with fresh explicit authorization.

## Minimal P2 cross-performer screen — REQUEST ONLY

After the decoder V2 P1 engineering gate passed, the next step has been reduced to the smallest source-disjoint generalization screen that can falsify the current success before any additional optimizer spend.

Frozen design:
- P2 only; P1 media is not reopened;
- exact homologous `directinput` captures:
  - `P2|chords|Drop3_7|directinput`
  - `P2|scales|Ab|directinput`
  - `P2|singlenotes|allsinglenotes|directinput`
  - `P2|techniques|PalmMute|directinput`
- 200 frames/example;
- independent deterministic source-only launch-ready crop selection;
- exact frozen V3 model + decoder V2;
- state/onset thresholds remain **0.50 / 0.50**;
- **0 optimizer steps**;
- no threshold retuning, no model mutation;
- P3 remains sealed;
- missing/unresolved selected capture fails closed; no substitution.

The screen reuses the existing performer-disjoint development event thresholds that are computable on this four-example screen:
- aggregate precision >= **0.75**
- aggregate recall >= **0.60**
- aggregate F1 >= **0.67**
- each selected content example F1 >= **0.55**
- repeated-attack recall >= **0.60** when repeated references are present
- unresolved labels = **0**
- synthetic-silence false positives = **0**

Screen code and guards passed backend/focused evaluation tests in run **36286081940**.

Design: `docs/astra/P2_CROSS_PERFORMER_SCREEN_DESIGN_V1.json`.  
Request: `docs/astra/P2_CROSS_PERFORMER_SCREEN_AUTHORIZATION_REQUEST_V1.json`.  
Dormant workflow: `.github/workflows/astra-p2-cross-performer-screen-v1.yml`.

A green screen would support only a broader P1/P2 development-evaluation design. It would **not** establish final generalization, authorize P3, full training, production mutation, or customer delivery.

**No P2 authorization or launch exists. Fresh explicit authorization is required before P2 media access.**

## Minimal P2 cross-performer zero-optimizer screen — AUTHORIZED AND LAUNCHED ONCE

User explicitly authorized the frozen P2 screen request in chat on 2026-09-26.

Authorization commit: `7571663d9b9cee36c0e569fe8a1a7193b18cbf9b`.  
Launch commit: `09bd6a3ede14991c1682941ad7fe46333c8da39b`.  
Canonical P2 screen run: **36286306972**, job **108527632565**.

Authorized scope:
- P2 only; exact four homologous `directinput` captures;
- exact frozen V3 model + decoder V2;
- independent deterministic source-only crop selection;
- state/onset thresholds remain 0.50 / 0.50;
- **0 optimizer steps**;
- no threshold retuning;
- no model mutation;
- no P1 media access;
- P3 remains sealed;
- zero automatic retries;
- no broader P1/P2 development run, full training, production mutation, or customer delivery.

**Do not create another P2 screen launch or rerun this workflow.** Inspect run **36286306972** only. On completion, preserve aggregate precision/recall/F1, each-example F1, repeated-attack recall, offset fraction, unresolved labels, and the green/red screen decision. A green result supports only designing a broader P1/P2 development evaluation; it does not authorize P3 or full training.

## Minimal P2 cross-performer screen — AUTHORIZED AND LAUNCHED ONCE

User explicitly authorized the frozen request by saying **"I authorize"**.

Frozen request:
- `docs/astra/P2_CROSS_PERFORMER_SCREEN_AUTHORIZATION_REQUEST_V1.json`
- request blob: `e813af9d17e714c5cbc1cc89fc4788ae4860c069`

Authorization:
- `docs/astra/P2_CROSS_PERFORMER_SCREEN_AUTHORIZATION_V1.json`
- authorization blob: `9a873326fb9ee95f95afec80db8852b76a4f3852`
- authorization commit: `7571663d9b9cee36c0e569fe8a1a7193b18cbf9b`

Launch:
- `docs/astra/P2_CROSS_PERFORMER_SCREEN_LAUNCH_V1.json`
- launch blob: `3b46c2592d6d47f3c353e3efd8b81e5947104e06`
- launch commit: `09bd6a3ede14991c1682941ad7fe46333c8da39b`

Canonical workflow:
- run: **36286306972**
- job: **108527632565**
- workflow: `Astra P2 cross-performer zero-optimizer screen v1`
- launch head: `09bd6a3ede14991c1682941ad7fe46333c8da39b`
- monitor: `https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/36286306972`

Last observed step state:
- authorization/source-pin verification: **PASS**
- frozen V3 artifact download: **PASS**
- frozen V3 artifact hash verification: **PASS**
- exact runtime install: **PASS**
- prepare exactly four homologous P2 directinput examples: **IN PROGRESS**
- model evaluation: pending
- evidence upload: pending
- cleanup: pending

Authorized scope is exactly:
- P2 only;
- captures:
  - `P2|chords|Drop3_7|directinput`
  - `P2|scales|Ab|directinput`
  - `P2|singlenotes|allsinglenotes|directinput`
  - `P2|techniques|PalmMute|directinput`
- 200 frames/example;
- exact frozen V3 model;
- decoder V2 rising-edge same-fret semantics;
- state/onset thresholds **0.50 / 0.50**, unchanged;
- **0 optimizer steps**;
- no threshold retuning;
- no model mutation;
- no automatic retry;
- no broader P1/P2 development run;
- no full training;
- **P3 remains sealed**;
- no customer delivery / production mutation.

Frozen screen gates:
- aggregate precision >= **0.75**
- aggregate recall >= **0.60**
- aggregate F1 >= **0.67**
- each selected example F1 >= **0.55**
- repeated-attack recall >= **0.60** when repeated references exist
- unresolved labels = **0**
- synthetic-silence false positives = **0**
- all metrics finite
- post-result threshold retuning forbidden

### EXACT NEXT STEPS — RESUME HERE

1. **Inspect only canonical run 36286306972 / job 108527632565.**
   Do not create another launch file and do not rerun the workflow.

2. If P2 preparation fails:
   - preserve the exact preparation diagnostics / rejection codes;
   - freeze a failure receipt;
   - update this checkpoint;
   - stop.
   No substitution capture, automatic retry, P3 access, optimizer work, or threshold change is authorized.

3. If evaluation completes:
   collect and freeze, at minimum:
   - all four prepared capture identities / crop selections / target hashes;
   - unresolved-label counts;
   - aggregate reference / prediction / TP / FP / FN counts;
   - aggregate precision, recall, F1;
   - per-example precision, recall, F1 for chord / scale / single-note / PalmMute;
   - matched-offset-within-50ms fraction;
   - repeated-reference count and repeated-attack recall;
   - synthetic-silence false-positive count;
   - `crossPerformerScreenGreen`;
   - confirmation optimizer steps = 0;
   - confirmation thresholds/model weights unchanged;
   - confirmation P3 was not opened;
   - artifact ID/digest and cleanup status.

4. If the screen is **RED**:
   - freeze the result;
   - classify the performer-shift failure by content/error type;
   - stop before any broader training.
   The next work should be diagnosis only and would require a newly frozen design before any new media/optimizer authorization.

5. If the screen is **GREEN**:
   - freeze the result;
   - stop.
   Green means only that these four source-disjoint P2 examples pass the pre-existing development event gates.
   It does **not** establish final generalization and does **not** authorize P3, full training, production mutation, or customer delivery.
   The next permissible planning step is a **broader P1/P2 development-evaluation design/request only**, with P3 still sealed and no optimizer work unless separately authorized.

6. **Never open P3 from this run.**
   `P3_music.zip` remains the sealed single-use final generalization gate and must not influence thresholds, decoder choices, model changes, or development decisions before a separate explicit authorization and freeze.

This section is the canonical handoff for the next chat.

## Minimal P2 cross-performer screen — COMPLETE, RED

Canonical run **36286306972**, job **108527632565** completed successfully at the workflow level.

Execution guards all held:
- authorization/source pins: PASS
- frozen V3 artifact hashes: PASS
- exact four P2 captures prepared: PASS
- optimizer steps: **0**
- thresholds changed: **no**
- model weights changed: **no**
- P1 media reopened: **no**
- P3 opened: **no**
- cleanup: PASS
- automatic retry: **no**

Frozen evidence:
- result: `docs/astra/P2_CROSS_PERFORMER_SCREEN_RESULT_V1.json`
- result commit: `f10b7d5401472498278cc5bb3331ec25d11aced9`
- artifact ID: **10920718166**
- artifact digest: `sha256:1c3325d4e961e94e1541e3f8b48cd65a870a74a7d568d3e829ad1dfdb1fcb1ad`
- result JSON SHA-256: `06ed422bbb055a831c472d75c2c333dfd98946773c93bdd79a470f959b8eb914`

### Screen result

Aggregate:
- references: **14**
- predictions: **0**
- true positives: **0**
- false positives: **0**
- false negatives: **14**
- recall: **0.0**
- F1: **0.0**
- precision: undefined because prediction count = 0
- repeated reference attacks: **2**
- repeated-attack recall: **0.0**
- unresolved labels: **0**
- synthetic-silence false positives: **0**
- `crossPerformerScreenGreen=false`

Per example:
- `P2|chords|Drop3_7|directinput`: 4 references, 0 predictions, F1 **0.0**
- `P2|scales|Ab|directinput`: 7 references, 0 predictions, F1 **0.0**, repeated recall **0.0**
- `P2|singlenotes|allsinglenotes|directinput`: 1 reference, 0 predictions, F1 **0.0**
- `P2|techniques|PalmMute|directinput`: 2 references, 0 predictions, F1 **0.0**, repeated recall **0.0**

Classification: **complete cross-performer recall collapse**. The P1-trained frozen model + decoder V2 produced no decoded event on any selected P2 example.

This is not a label-preparation failure: all four selected P2 crops were launch-ready with zero unresolved labels. It is also not the previous duplicate-onset precision issue: there were no predictions at all.

### EXACT NEXT STEPS — RESUME HERE

1. **Do not broaden training, retune thresholds, open P3, or run another P2 screen.**
   The current evidence blocks broader training.

2. The next experiment must be **diagnostic only and zero-optimizer**.
   Its purpose is to determine why P2 produces no decoded events.

3. Freeze a new diagnostic design/request before any new P2 media access. It should record, for each of the same four P2 crops:
   - onset probability distribution by string/frame;
   - maximum onset probability and frames nearest each reference onset;
   - state active probability for the true string/fret at each reference onset;
   - silence probability and active-minus-silence margin;
   - counts of frames passing onset-only, state-only, and joint decoder admission;
   - decoded events at the frozen 0.50/0.50 thresholds;
   - no threshold search or retuning.

4. To distinguish model-output collapse from input-domain shift, the diagnostic should also compare frozen P1 vs P2:
   - CQT feature mean/std and per-feature distribution summaries;
   - RMS-normalized audio/feature scale summaries available from the prepared crops;
   - model onset-logit and state-margin summaries.
   Use matched homologous captures where possible.

5. Interpret the diagnostic without changing thresholds:
   - **onset low, state healthy** => onset head/generalization failure;
   - **state low/silence dominant, onset healthy** => state-head/domain failure;
   - **both low** => representation/domain-shift or severe memorization;
   - **both individually pass but joint admission is zero** => decoder/admission interaction.
   These are diagnostic categories only, not automatic fixes.

6. After that diagnostic:
   - if the failure is clearly preprocessing/domain normalization, design the smallest offline normalization/representation test first;
   - if it is model memorization/generalization failure, design a new small P1+P2 development training experiment with strict capped compute;
   - do not return to 2,000-epoch runs without new evidence.

7. **P3 remains sealed.**
   `P3_music.zip` must not be opened or used for tuning, architecture selection, threshold selection, decoder changes, or development diagnosis.

No new P2 media access, optimizer work, or threshold change is authorized by this result. A fresh explicit authorization is required for the proposed activation/domain-shift diagnostic.

## P1-P2 activation/domain-shift diagnostic — AUTHORIZED AND LAUNCHED ONCE

User explicitly instructed **"Run the diagnostic"** on 2026-09-27. This authorization applies only to the zero-optimizer diagnostic described below.

Artifacts:
- design: `docs/astra/P1_P2_ACTIVATION_DIAGNOSTIC_DESIGN_V1.json`
- authorization: `docs/astra/P1_P2_ACTIVATION_DIAGNOSTIC_AUTHORIZATION_V1.json`
- launch: `docs/astra/P1_P2_ACTIVATION_DIAGNOSTIC_LAUNCH_V1.json`
- workflow: `.github/workflows/astra-p1-p2-activation-diagnostic-v1.yml`

Authorization commit: `b162124b9fd26b9ecdf10a7405490bb551f5d7ea`.  
Launch commit: `a5c2c2add245f29c1b7b690a8ed22865217828b7`.  
Authorization blob: `b4e501e2eb6490372bfb0813def63414cd2b844c`.

Canonical diagnostic:
- run: **36325297420**
- job: **108636792679**
- monitor: `https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/36325297420`

Authorized scope:
- exact four frozen P1 control examples;
- exact four homologous P2 examples;
- exact frozen V3 model + decoder V2;
- state/onset thresholds remain **0.50 / 0.50**;
- **0 optimizer steps**;
- no threshold search or retuning;
- no model mutation;
- zero automatic retries;
- **P3 remains sealed**;
- no full training, production mutation, or customer delivery.

Diagnostic measurements:
- CQT feature mean/std/quantiles/absolute mean/L2 RMS;
- onset probability/logit distributions;
- state-logit distributions;
- whole-crop onset-only, state-only and joint-admission counts;
- reference-onset probes within +/-2 frames;
- true-fret probability, silence probability and active-minus-silence margin;
- reference onset/state/joint pass counts;
- decoder-V2 event counts at frozen thresholds;
- paired P2-minus-P1 feature/output deltas by content.

### EXACT NEXT STEPS

1. Inspect **only** run **36325297420**, job **108636792679**. Do not create another launch or rerun.
2. If setup/preparation fails, preserve the exact failure and stop. No substitution captures and no automatic retry.
3. If diagnostic completes, freeze the result JSON/artifact and classify P2 using the preregistered categories:
   - `onset_head_generalization_failure`
   - `state_head_or_representation_failure`
   - `both_heads_or_representation_domain_collapse`
   - `onset_state_admission_misalignment`
   - `partial_generalization_failure`
   - `reference_admission_healthy`
4. Preserve P1-vs-P2 paired feature/output statistics and reference-probe counts. Do not infer causality beyond the measured evidence.
5. No threshold change, optimizer work, broader training, or P3 access follows automatically from any diagnostic category.
6. If a preprocessing/domain-shift mechanism is clearly supported, next action is design/request-only for the smallest offline normalization/representation test.
7. If model memorization/generalization failure is supported instead, next action is design/request-only for a tightly capped P1+P2 development fit experiment.
8. P3 remains sealed under all outcomes until a separate final-gate design, freeze, and explicit authorization.

This is the canonical handoff.

## P1-P2 activation/domain-shift diagnostic — COMPLETE, WORKFLOW GREEN

Canonical diagnostic run **36325297420**, job **108636792679** completed **SUCCESS**.

Authorization / launch:
- authorization commit: `b162124b9fd26b9ecdf10a7405490bb551f5d7ea`
- launch commit: `a5c2c2add245f29c1b7b690a8ed22865217828b7`
- authorization blob: `b4e501e2eb6490372bfb0813def63414cd2b844c`
- launch blob: `5d5045ecb521561116b8e43cfe0cf541a42ba1b9`

Execution boundary:
- exact frozen V3 model: PASS
- exact P1 controls prepared: PASS
- exact homologous P2 examples prepared: PASS
- optimizer steps: **0**
- thresholds changed: **no**
- threshold search: **no**
- model weights changed: **no**
- P3 opened: **no**
- cleanup: PASS
- automatic retry: **no**

Frozen evidence:
- result: `docs/astra/P1_P2_ACTIVATION_DIAGNOSTIC_RESULT_V1.json`
- result commit: `bb223a6b6246945c3a6d2465756f8c8e99fc4a02`
- artifact ID: **10934054467**
- artifact digest: `sha256:9c12aeb14fd6b7a3766c10b19c0fc9827400a8f1c5da18f11e02f66784a8f7b5`
- raw diagnostic JSON SHA-256: `7f8313d7a0b75e82606d6c09092b94a3dd6098d27f66bcea64aebb1163df3027`

### Exact diagnostic finding

P1 control:
- decoded events: **23**
- reference probes: **16**
- onset passes within +/-2 frames: **16 / 16**
- true-state passes within +/-2 frames: **16 / 16**
- joint onset+state admissions: **16 / 16**
- class: `reference_admission_healthy`

P2:
- decoded events: **0**
- raw reference probes: **15**
- onset passes within +/-2 frames: **0 / 15**
- true-state passes within +/-2 frames: **9 / 15**
- joint onset+state admissions: **0 / 15**
- class: `onset_head_generalization_failure`

The prior P2 scoring screen reported 14 scored references because its Event-v2 boundary exclusions remove one boundary-intersecting reference. This diagnostic probes the raw prepared `scorableEvents` before that scorer exclusion; crop selections and target hashes match.

Per content:
- chords: P2 onset **0/4**, state **1/4**, joint **0/4**
- scales: P2 onset **0/8**, state **7/8**, joint **0/8**
- singlenotes: P2 onset **0/1**, state **1/1**, joint **0/1**
- PalmMute: P2 onset **0/2**, state **0/2**, joint **0/2**

Primary classification: **onset-head generalization failure**.  
Secondary classification: **PalmMute also has a state/representation failure**.

Feature-scale evidence does **not** support a simple global gain/normalization explanation:
- chords feature L2 RMS: P1 **0.3163**, P2 **0.3291** (P2 higher)
- scales: P1 **0.2918**, P2 **0.2597** (P2 lower)
- singlenotes: P1 **0.1964**, P2 **0.2162** (P2 higher)
- PalmMute: P1 **0.1932**, P2 **0.1168** (P2 lower)

Therefore do **not** assume that rescaling CQT magnitude alone will solve the generalization failure.

Threshold rescue is also blocked:
- frozen onset threshold remains **0.50**
- zero P2 reference windows reach 0.50
- most P2 reference-window onset probabilities are orders of magnitude below 0.50
- the P2 scale crop has a whole-crop non-reference onset maximum above 0.50, so simply lowering the threshold risks unrelated admissions
- post-result threshold retuning is forbidden

### EXACT NEXT STEPS — RESUME HERE

1. **Do not retrain yet. Do not lower thresholds. Do not open P3.**
   The current evidence is sufficient to localize the main failure but not yet to choose the correct repair.

2. The next experiment should be a **zero-optimizer encoder-vs-onset-head decomposition diagnostic** on the same matched P1/P2 captures.
   Purpose: determine whether P2 divergence is already present in the shared 128-dimensional encoder representation or is introduced/amplified primarily by the onset-head linear boundary.

3. Before any new P1/P2 media access, freeze a new design/request-only gate. The diagnostic should record:
   - shared encoder activation norm / mean / std / quantiles at reference windows;
   - matched P1-vs-P2 encoder cosine and Euclidean distances by content and, where comparable, physical string/fret;
   - nearest P1 reference embedding for every P2 reference embedding;
   - per-string onset-head linear contribution `h·w + b` at every reference window;
   - onset-head bias and contribution deltas P2-vs-P1;
   - true-state logit versus silence-logit margin at each reference window;
   - decomposition of state failure for PalmMute;
   - decoded events at the unchanged 0.50 / 0.50 thresholds only;
   - **0 optimizer steps and no threshold search**.

4. Interpret that decomposition with these frozen decision branches:
   - **Encoder representations remain close but P2 onset logits collapse:** treat the onset head/objective as the primary problem. Next design should be a tiny **balanced P1+P2 onset-head-focused development fit**, initially freezing the shared encoder, with a strict small optimizer cap. Do not jump to full-model or 2,000-epoch training.
   - **Encoder representations diverge strongly P1-vs-P2:** treat representation/domain robustness as the primary problem. First test normalization/representation alternatives offline or zero-optimizer where possible before fitting.
   - **PalmMute remains representation/state collapsed while other content is onset-only:** treat PalmMute as a separate content-specific representation problem; an onset-head repair alone must not be claimed as full generalization.
   - **Mixed/ambiguous:** collect only the minimum additional zero-optimizer evidence needed; do not spend optimizer budget to guess.

5. If a small P1+P2 fit is eventually justified, it must be separately designed and authorized with:
   - P1+P2 development only;
   - P3 sealed;
   - balanced performer sampling;
   - explicit onset supervision retained;
   - decoder V2 retained unless new evidence invalidates it;
   - no post-result threshold tuning;
   - strict optimizer/wall-clock cap;
   - zero automatic retries;
   - a held-out performer/content evaluation that prevents memorizing the same four pairs.

6. **Do not return to long 2,000-epoch V1-V5-style runs.**
   We now have direct evidence that the P1 model learned its training examples but the onset head does not transfer to P2. More epochs on P1 are not supported by the evidence.

7. **P3 remains sealed under every current branch.**
   `P3_music.zip` must not be used for diagnosis, threshold selection, representation choice, architecture choice, or development training. It remains the single-use final generalization gate.

8. No new media access, threshold change, optimizer work, broader training, production mutation, or customer delivery is authorized by this diagnostic result. A fresh explicit authorization is required for the encoder-vs-onset-head decomposition diagnostic.

This section is the canonical next-chat handoff.

