# GPT-5.6 handoff — post-V14 product-direction review
Date: 2026-10-02
Branch: astra-work
Reviewed commit: 0109cebffff99940725440aa8ff03319b993677c
Status: Documentation-only decision brief; no new empirical project opened.

## Recommendation

Choose **independent real-development evidence**, with separately scoped acquisition/evaluation authorization. Keep the present synthetic model line frozen. Do not launch V15, redesign the generator first, or promise that another model will solve this.

The first question should be: **Can a fixed transcription baseline recover useful notes from a real, original isolated instrument recording, and how much does its output degrade when fed a separated version of that same performance?** Then independently test the note-to-tab stage using verified notes. This provides a stage-by-stage error budget tied to Stephen's actual goal.

Start with a bounded bass-first feasibility study, then single-guitar lead and rhythm. Bass-first is a scope decision (often fewer simultaneous target notes), not a claim that bass is solved or always easy. Guitar/bass remain the destination. Automatic lead/rhythm separation and near-perfect full-song tabs are not established capabilities.

## Scope and evidence

Read both CURRENT_STATE handoffs, AGENTS.md, post-V13 strategy review, V14 result MD/JSON, V14 runner, S6 model, existing playable-shape decoder, historical Basic Pitch runner, separator review and Stage-B failure analysis. Read upstream Basic Pitch, Demucs and GuitarSet documentation on 2026-10-02. Repository evidence below is pinned to the reviewed commit.

This was a source/document review, not an audio listening test or reproduction. No audio/corpus/model files were opened, weights downloaded, inference/training/rendering executed, workflows dispatched, or production changes made. Numerical findings are from committed records, not independently regenerated artifacts. Shell cloning was unavailable; the connected GitHub interface supplied source and is used for writeback. This is not a complete backend audit.

## Why the idea is difficult

A finished stereo song does not contain neatly labelled instrument tracks. Separation estimates them and may remove target notes or retain other instruments. A clean-sounding stem need not preserve every quiet attack. Distortion, harmonics, overlapping guitars and effects can confuse pitch and onset estimation. Finally, correct pitches do not uniquely determine the original guitar fingering: several strings can play the same pitch.

Treat these as separate deliverables:
1. target-source selection/separation;
2. pitch, onset, offset and continuous technique evidence;
3. phrase/rhythm interpretation;
4. playable string/fret assignment;
5. notation and user correction.

An attractive playable tab can still contain wrong notes. Exact original fingering and a musically equivalent playable arrangement require different scoring and user-facing claims.

## Assessment of GPT-5.6's work

Useful work worth keeping:
- Frozen results, explicit unsuccessful outcomes, reproducible control and provenance.
- Separation of synthetic diagnostics from real-transfer claims.
- Preservation of held-out data and termination of serial micro-studies.
- Existing playable-position/shape enumeration: reuse it rather than starting tab rendering over.

The strategic problem is optimizing recovery of a narrow synthetic comparator while the product's full audio-to-tab chain remains unvalidated. The recent work provides evidence about this model/generator package, not about commercial recordings or customer correction effort.

There were also avoidable engineering/interpretation problems:
- V14's first run trained both arms before rejecting the historical control because of seed/runtime mismatch. Future experiments should validate configuration first and evaluate the control before spending the remaining candidate budget, where the prospective protocol permits that order.
- Long append-only handoffs contain multiple superseded "current" authorities. This review adds a current pointer and preserves history.
- Do not confuse constraint compliance, a green workflow, admission diagnostics or descriptor coverage with musical accuracy.

## What the numbers actually show

From docs/astra/V14_MATCHED_CONTEXT_BRIDGE_RESULT_V1.json:

| Same common synthetic test | Control | V14 bridge |
| --- | ---: | ---: |
| Pitch/onset precision | 0.826923 | 0.496894 |
| Pitch/onset recall | 0.666667 | 0.620155 |
| Pitch/onset F1 | 0.738197 | 0.551724 |
| Correct matched events | 86 | 80 |
| False positive events | 18 | 81 |
| Missed events | 43 | 49 |
| Pitch/onset/offset F1 | 0.609756 | 0.416107 |
| Chord-family pitch/onset F1 | 0.384615 | 0.285714 |
| Negative-only FP/second | 0 | 0 |

The common test has 42 clips; its negative-only denominator is only **6 seconds**. Zero false positives there does not mean few false positives inside music: the bridge produced 81 false positives in the common evaluation. Report both quantities, with denominators.

The successful comparator itself misses one-third of reference pitch/onset events and has weak chord results. Its F1 of 0.738 is not "73.8% correct tablature," and it is not an adequate near-perfect product target. V14's own-domain pitch/onset F1 is 0.460481, so its weakness is not restricted to transfer back to the comparator.

V9 common F1 was 0.434783. V10/V11/V12/V13 improved F1 by approximately 0.00326/0.01592/0.02440/0.00490 respectively, as recorded in the post-V13 review; V12 also violated the negative-FP ceiling. V14 recovered 38.54% of the V9 F1 deficit and 34.32% of the precision deficit, below both frozen 50% recovery requirements. Preserve FAIL.

### The 384 truncations: important, but not a proven cause

The V14 runner's _truncate_same_string shortens an earlier state when the next state starts on that string. The bridge records **384 state truncations** versus control **0**, across each arm's complete 294-example dataset (588 seconds). It has 819 attack groups/987 attacked labels versus 735/903 in control.

These truncations demonstrate interaction between the timing schedule and duration rules. They are **not automatically 384 incorrect labels**: a newly fretted note can physically terminate the preceding string state. Nor do these counts establish the cause of the precision regression. A future generator design would need consistent score, acoustic envelope, release and label semantics, including intentional damping and non-attacked transitions.

Qualify the previous handoff's "context duration mattered" statement: V14 is a package intervention changing multiple properties, so the observed recovery supports sensitivity to that package; it does not isolate clip duration causally. Do not rewrite the frozen result.

### Limits of the current representation

S6Model is a feed-forward Linear(960,128)+ReLU encoder with string-state and per-string onset heads; V14 supplies five CQT frames. This is a local classifier, without learned phrase-length sequence reasoning. The CQT itself has frequency-dependent temporal support, so "five frames" is not a precise bound on the underlying waveform receptive field.

This inspection does not prove a larger model would fix the failures. It does show why the model is not by itself a solution for phrase fingering, rhythm notation or separating lead from rhythm. Do not jump from this limitation to unbounded architecture searches.

## Concrete integration findings

### Bass must have its own validated configuration

astra_backend/evaluation/run_basic_pitch_development.py is explicitly a historical **whole-mix development-only** baseline, with no role assignment. It sets minimum_frequency=82.406889..., approximately guitar E2. That excludes the low register of standard bass (E1 is about 41.2 Hz). Its minimum_note_length=127.7 ms also needs scrutiny before any fast-note evaluation.

This is not evidence that every active bass path shares the defect, and it does not explain V14's synthetic result. It is evidence that this runner cannot be reused unchanged as a bass baseline. Verify model-supported range, frontend range, tuning, output filtering and event-duration policy together; lowering an output filter cannot extend a model's trained output range. Freeze a new version for any future study and retain the historical baseline.

### Playable shapes already exist, but are not verified performance recovery

astra_backend/playableShapeDecoder.mjs enumerates positions, rejects impossible shape constraints and scores candidates with role heuristics and optional neighboring center-fret context. That is valuable infrastructure. It does not establish global optimal fingering or identify the actual recorded string.

Evaluate it separately using verified notes. Future phrase-level decoding should consider held notes, same-string occupancy across time, hand movement and technique continuity. Preserve acoustic pitches; do not delete/invent notes solely to make a convenient shape. Distinguish "no feasible assignment" from "uncertain original fingering."

### Separation remains a separate capability question

The existing independent separator review describes Banquet as promising for bass/guitar but records checkpoint/query-audio/runtime blockers and no established lead/rhythm distinction. This review does not resolve or waive those boundaries. A general guitar stem is not a lead stem.

Upstream Demucs documents an experimental guitar/piano six-source model, not a reliable lead-versus-rhythm service. Basic Pitch documents single-instrument use as its best setting. Neither is a verified replacement pipeline here, and historical blocked checkpoints remain blocked. Candidate selection must follow the existing exact-artifact review process without reopening archived experiments.

## Required comparison of the three paths

| Path | Information value | Overfitting risk | Cost profile | What it resolves |
| --- | --- | --- | --- | --- |
| Larger synthetic-generator redesign | Medium for generator consistency; uncertain for real songs | High risk of improving internal proxies without transfer | Potentially substantial engineering and repeated training | Timing/duration/renderer semantics, not automatically real-source transcription |
| Independent real-development evidence — RECOMMENDED | High: measures where errors enter the actual chain | Manageable with independent annotations, grouped splits and bounded comparison | Annotation/acquisition dominates initially; inference can be bounded | Clean-source ceiling, separation penalty, bass-range failure, tab-decoder error |
| Pause this model line | No additional empirical information; prevents further sunk cost | No additional model-selection exposure | Lowest immediate cost | Resource decision, not technical feasibility |

Exactly one direction is recommended: the middle path. The current synthetic line stays frozen while that direction is prepared; this is not a second parallel research project.

## Proposed bounded study — design for review, not permission to execute

Draft a bass-first feasibility packet using **12 new 15–30-second performances**, across at least three independent performers/sessions, with original isolated bass tracks and corresponding mixes. This is a proposed budget of 3–6 minutes of unique music, not a statistically sufficient product benchmark. Prefer rights-cleared multitracks or voluntary recordings by collaborators; do not require Stephen to record them himself.

Include sustained low notes, repeated picked/fingered notes, rests, octave-confusable notes and a clearly defined tuning/range. Reserve guitar chords, bends/slides, distorted rhythm and multiple simultaneous guitars for a subsequent explicitly scoped stage, not silent exclusions from a universal product claim.

Before access:
- Identify actual sources, original stems, permissions, exact files, storage location, acquisition cost and overlap checks. Do not invent an allowlist or treat P1/P2/V2B/P3 as the new pool.
- Split by performer/session (and composition where applicable), not random adjacent chunks. For example eight development and four locked confirmation excerpts, with confirmation performers/sessions excluded from selection. With only a few groups, explicitly retain the weak-generalization caveat.
- Human-adjudicate complete note onsets, pitch and offsets from the recorded performance; retain uncertainty masks. A composition MIDI file is not automatically ground truth for how a musician actually played it.
- Exact original fingering needs reliable string/fret evidence. Without it, score pitch-equivalent playability, not fabricated exact-string accuracy.
- Existing spectral-flux/YIN V2B landmarks are useful exposed development diagnostics, not exhaustive human-verified truth. Do not copy their labels as the answer key for a new model.
- Select at most two fixed transcription candidates and one eligible separator before observing results. Inspect existing evaluation records first to avoid repeating a known mismatch. No fine-tuning, model sweep, threshold sweep or best-seed selection in this first study.
- Freeze versions, hashes, role-specific range, event decoder, onset/offset matching, alignment, compute/storage ceilings, and failure handling in one reviewable packet. Do not invent dollar estimates without runtime evidence.

### Three paired measurements

| Arm | Input and processing | Question |
| --- | --- | --- |
| A | Original isolated instrument recording -> fixed transcriber | Can note extraction work before separation artifacts? |
| B | Corresponding mix -> fixed separator -> same transcriber | How much does separation change downstream transcription? |
| C | Verified note events -> existing tab decoder | How much error/ambiguity belongs to string/fret assignment? |

Keep the clean recorded effect chain as representative as possible. A dry DI-only recording is useful diagnostically but is not equivalent to an effected instrument stem from a mix. Record alignment/sample-rate/channel transformations. Correct only documented latency using a preregistered rule; do not maximize test scores by searching shifts against annotations.

Measure pitch/onset precision, recall and F1; pitch/onset/offset F1; octave errors; repeated-note recall; false positives during music and target-absent intervals; phrase coverage and abstention; instrument-range exclusions; invalid shapes; and correction minutes per minute of music. Retain per-clip/group results and paired A–B differences. Do not present pooled note counts as independent trials or six seconds of clean negatives as a reliable false-positive guarantee.

For user usefulness, have an evaluator correct the draft with a timer, and compare with an equivalent manual-transcription task using a counterbalanced assignment if practical. Otherwise label correction-time comparisons exploratory. A selective system must report both accuracy and coverage; abstaining on most notes cannot pass by precision alone.

### Prospective decision rules to freeze before running

Do not reuse the synthetic 50%-recovery gate as a product goal. Select concrete thresholds for the narrow proposed use case before any outputs are seen; human usability and full event accuracy both matter. This review deliberately does not assert an evidence-free "95% ready" requirement.

- A poor: stop separator optimization; investigate transcription/input-domain suitability.
- A acceptable, B poor: separation is the next bottleneck.
- A/B acceptable, C poor: focus on phrase-level fingering/notation.
- A/B/C acceptable but correction effort remains high: product benefit is unproven.
- No allowed source/checkpoint or no workable budget: stop with a specific blocker; do not substitute protected historical data.
- Confirmation failure: retain failure; no automatic new model, threshold or alternate confirmation set.

A passed small bass feasibility study permits only the next scoped decision. It does not establish near-perfect full-song guitar/bass tabs, multiple-guitar attribution or commercial readiness.

## Exact next task for GPT-5.6

1. Read this brief and both new handoff pointers; retain all historical failed results.
2. Prepare **one concrete independent bass feasibility execution packet** using metadata/documentation only: candidate inventory, source/rights plan, independent annotation rubric, proposed split, exact metric definitions, runtime/storage/cost budget, success/stop rules and disabled execution entry point. Where evidence is missing, mark it missing; do not invent files, hashes, permission or runtime estimates.
3. Reuse existing evaluator/decoder components where their contracts fit; explicitly flag the historical Basic Pitch bass-range mismatch. Do not port the six-string S6 output directly to bass.
4. Save the reviewable packet on astra-work before asking for the real-source/model-run scope. Request that bounded scope once, explaining it is required by the existing AGENTS/checkpoint real-data and empirical-execution boundary. Routine documentation does not need repeated permission.
5. No new corpus access, training, inference, rendering, workflow launch, V15/V16, V2B/P1/P2 reopening, P3 access or production changes follow from this review request.

## Source map

Internal paths above refer to commit 0109cebffff99940725440aa8ff03319b993677c. Primary evidence:
- docs/astra/V14_MATCHED_CONTEXT_BRIDGE_RESULT_V1.json
- astra_backend/synthetic/v14_empirical_v1.py
- astra_backend/synthetic/s6_pilot_v1.py
- docs/astra/POST_V13_RECOVERY_STRATEGY_REVIEW_V1.md
- astra_backend/evaluation/run_basic_pitch_development.py
- astra_backend/playableShapeDecoder.mjs
- docs/astra/INDEPENDENT_SEPARATOR_REVIEW_V1.md
- both CURRENT_STATE.md files, including the prior measurement review documenting V2B label limitations.

Upstream documentation checked 2026-10-02 (capability context only):
- https://github.com/spotify/basic-pitch — single-instrument recommendation and frequency filtering; not proof of accuracy here.
- https://github.com/facebookresearch/demucs — experimental six-source guitar/piano support; not lead/rhythm validation.
- https://github.com/marl/GuitarSet — guitar transcription dataset documentation; not authorization to access a corpus or a substitute for bass/mix evidence.

Verification for this review: compared committed V14 aggregate metrics with event counts and inspected the relevant source paths. No runtime tests were needed or performed for this documentation-only change. Remote writeback must be verified before claiming this handoff is saved.
