# Independent Bass Feasibility Execution Packet V1

Date: 2026-10-02
Branch: `astra-work`
Status: **PREPARED / EXECUTION DISABLED**
Purpose: bounded, independent evidence about where errors enter the real bass-audio -> notes -> playable-tab chain.

This packet implements the post-V14 handoff. It does **not** authorize source acquisition, audio access, model/checkpoint download, separation, transcription, rendering, inference, training, workflow dispatch, P1/P2/V2B/P3 access, or Production changes.

## 1. Study question

For a small set of new, rights-cleared bass performances:

1. Can one fixed note transcriber recover useful note events from the **original isolated bass recording**?
2. How much does the same transcriber degrade when the corresponding **mix is separated first**?
3. Given **human-verified note events**, how much error or ambiguity remains in the existing playable string/fret assignment stage?

These are three different questions. Results must not be collapsed into one "tab accuracy" number.

## 2. Scope

### Fixed study size

- 12 unique performances.
- 15-30 seconds each.
- Total unique musical duration: **180-360 seconds**.
- At least **3 independent performer-session groups**.
- Bass only for V1.
- Standard 4-string bass is the default target unless the source manifest prospectively declares another tuning for a specific performance.
- No guitar, lead/rhythm attribution, full-song claim, customer-delivery claim, or commercial-readiness claim is in scope.

### Required content coverage

Across the 12 performances, the source manifest must include examples of:
- sustained low-register notes;
- repeated notes;
- rests / target-absent regions;
- octave-confusable material;
- at least two articulation styles where available (for example fingerstyle and pick);
- ordinary musical transitions rather than isolated test tones only.

The manifest must record what is actually present. Do not manufacture coverage claims when a source does not contain a requested condition.

## 3. Real-source and rights plan

No source has been approved or opened by this packet.

Before execution, create a source manifest with **exactly 12 entries**. Each entry must contain:
- source ID;
- performer/session group ID;
- composition/performance ID;
- exact isolated-bass file identity;
- exact corresponding-mix file identity;
- SHA-256 for both files after lawful acquisition;
- duration, sample rate, channels and format;
- tuning and lowest expected pitch where known;
- provenance / source owner;
- explicit permission basis for development/evaluation use;
- permission basis for storing the file outside Git;
- whether exact string/fret ground truth exists and how it was obtained;
- acquisition cost, if any;
- overlap check against historical P1/P2/V2B/P3 and archived song-specific evidence.

Preferred source type: newly recorded or collaborator-provided material with explicit development/evaluation permission and paired isolated bass + mix.

Do **not**:
- reuse P1/P2/V2B/P3;
- treat archived customer/song evidence as the new pool;
- use a composition MIDI file as performance ground truth without human adjudication;
- place audio, credentials, or private source material in Git.

If fewer than 12 compliant entries exist, stop before execution.

## 4. Grouped split

Prospectively assign:
- **8 development performances**
- **4 locked confirmation performances**

Rules:
- split by performer-session group, never by adjacent random chunks;
- confirmation must contain at least one entire performer-session group absent from development;
- where compositions repeat, keep the same composition on one side when practical;
- do not change the split after seeing any transcription or separation result;
- keep confirmation annotations hidden from model/candidate selection decisions until development measurements are frozen.

With this small number of groups, all generalization claims remain weak and must be labelled as such.

## 5. Candidate inventory

### T1 — Basic Pitch, fixed baseline candidate

Repository integration path:
- `astra_backend/evaluation/run_basic_pitch_development.py`

Historical package facts:
- TFLite model SHA-256 asserted by the runner:
  `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`
- historical thresholds: onset 0.50, frame 0.30;
- historical minimum note length: 127.7 ms;
- historical minimum frequency: 82.406889 Hz.

**Bass blocker:** that historical minimum frequency is approximately guitar E2 and excludes the low register of standard bass. The historical runner therefore cannot be reused unchanged.

Before execution, T1 needs a new frozen bass configuration with:
- exact Basic Pitch package version;
- exact model artifact identity;
- verified model-supported frequency range;
- explicit minimum/maximum frequency;
- event decoder settings;
- minimum note length;
- onset/frame thresholds;
- no threshold sweep after results are observed.

Changing an output frequency filter must not be described as extending the trained model's supported range.

### T2 — none in V1

No second transcriber is selected. This is deliberate. V1 is a stage-localization study, not a model leaderboard.

A second transcriber may be added only by revising and re-freezing this packet **before** any audio/model result is observed. Maximum candidates remain two.

### S1 — separator slot is not yet execution-eligible

Existing independent review:
- `docs/astra/INDEPENDENT_SEPARATOR_REVIEW_V1.md`

Banquet/query-bandit is technically relevant to bass/generic guitar, but remains blocked in the existing review by unresolved checkpoint rights, query-audio integration, exact checkpoint SHA-256 and runtime budget.

Historical Demucs work remains historical evidence. Do not silently reopen archived separator experiments.

**Execution blocker:** one exact separator must be selected before authorization, with:
- repository/revision;
- exact checkpoint/model identity and SHA-256;
- code + checkpoint rights basis for this development evaluation;
- target stem definition;
- input/output sample-rate/channel behavior;
- fixed inference settings;
- measured runtime and peak memory on the intended execution environment;
- no source-specific query audio unless its rights/provenance are independently approved.

No separator candidate = no Arm B execution.

## 6. Independent annotation rubric

Each reference note event must contain:
- `event_id`;
- MIDI pitch;
- onset seconds;
- offset seconds;
- `attack_group_id`;
- uncertainty flag;
- optional articulation/technique tag;
- optional observed string/fret, only when independently supported.

Annotation procedure:
1. Annotator works from the original isolated bass track, not transcriber output.
2. Mark complete note events, including repeated attacks of the same pitch.
3. Mark uncertain onset, offset or pitch explicitly rather than forcing certainty.
4. Mark target-absent intervals of at least 0.50 s.
5. Group simultaneous acoustic attacks under one `attack_group_id`.
6. A second pass adjudicates disagreements or uncertain events.
7. Transcriber outputs remain hidden until the reference for that performance is frozen.

Events with unresolved pitch are excluded from pitch scoring but retained in an uncertainty ledger. Events with reliable pitch/onset but uncertain offset remain eligible for pitch/onset scoring and excluded from offset scoring.

Exact original string/fret accuracy is scored only where a reliable independent observation exists. Otherwise Arm C reports pitch-preserving playability and ambiguity, not fabricated "ground truth fingering."

## 7. Three fixed arms

### Arm A — clean-source ceiling

`original isolated bass -> T1 -> event metrics`

Question: can the fixed transcriber recover the performance before separation artifacts?

### Arm B — separation penalty

`corresponding mix -> S1 -> separated bass -> same T1 -> same event metrics`

Question: what paired degradation is introduced by the separation + downstream chain?

### Arm C — note-to-tab stage

`verified note events -> existing playable shape decoder -> assignment metrics`

Primary reuse target:
- `astra_backend/playableShapeDecoder.mjs`

Arm C must preserve source pitches. It may abstain or report no feasible assignment; it must not delete or invent notes to improve playability.

## 8. Exact metric definitions

### Pitch/onset matching

A prediction matches a reference when:
- MIDI pitch is exactly equal; and
- onset absolute error <= **50 ms**.

Use one-to-one matching. If more than one valid pairing exists, choose the assignment minimizing absolute onset error, with deterministic tie-breaking by reference then prediction index.

Report precision, recall and F1 per performance and as:
- macro average across performances;
- capture-balanced average across performer-session groups;
- pooled event counts as descriptive only.

### Pitch/onset/offset matching

Requires the pitch/onset match above plus:

`abs(predicted_offset - reference_offset) <= max(50 ms, 20% of reference duration)`

Events with uncertain reference offsets are excluded from this metric's denominator and reported separately.

### Octave errors

An octave error is an unmatched prediction within 50 ms of a reference onset whose pitch differs from that reference by a non-zero integer multiple of 12 semitones. Report count and rate.

### Repeated-note recall

A reference event is in the repeated-note subset when the immediately preceding reference attack on the same MIDI pitch occurred <= **500 ms** earlier. Report pitch/onset recall on this subset.

### False positives during music

Count unmatched predicted note onsets inside annotated performance-active regions. Report FP/second.

### Target-absent false positives

For manually annotated target-absent intervals >=0.50 s, count unmatched predicted onsets and report FP/second with total absent-duration denominator.

### Low-register coverage

Report reference and matched counts by MIDI octave/register and explicitly for notes below historical Basic Pitch minimum 82.406889 Hz. This is diagnostic; it must not be used to post-hoc alter T1 settings.

### Arm B paired penalty

For every performance and aggregate:
- `F1_B - F1_A`;
- precision difference;
- recall difference;
- offset-F1 difference;
- FP/second difference.

Do not compare unrelated clips as if paired.

### Arm C decoder metrics

On each eligible reference attack group report:
- pitch preservation: input MIDI multiset equals output-assigned MIDI multiset;
- resolved assignment coverage;
- no-feasible-assignment rate;
- candidate-count distribution;
- invalid-shape rate;
- exact string/fret accuracy only on independently observed string/fret references;
- ambiguity rate: more than one valid playable candidate before heuristic selection.

Phrase-level movement/continuity is **not** established by the present local decoder and must be reported as a limitation.

### Correction effort

For a timed human correction pass report:
- correction minutes per minute of source audio;
- number of pitch edits;
- onset edits;
- offset edits;
- note insertions/deletions;
- fingering edits.

A manual-from-scratch comparison is interpretable only if counterbalanced across equivalent material. Otherwise correction-time comparisons are exploratory and cannot establish product benefit.

## 9. Prospective engineering gates

These are narrow feasibility gates, not claims of "near-perfect" tablature or commercial readiness. Do not lower them after seeing outputs.

### Arm A acceptable

On the 4 locked confirmation performances:
- macro pitch/onset F1 >= **0.85**;
- macro pitch/onset/offset F1 >= **0.75**;
- target-absent FP rate <= **0.20/s**;
- no entire low-register category with zero recall when that category has >=3 eligible reference events.

If Arm A fails any gate, stop interpretation at **transcription/input-domain bottleneck**. Do not optimize S1.

### Arm B acceptable relative to A

Only evaluated if Arm A passes:
- confirmation macro pitch/onset F1 drop `A-B` <= **0.10**;
- confirmation macro precision drop <= **0.10**;
- target-absent FP-rate increase <= **0.10/s**;
- no newly introduced systematic octave-error pattern affecting >=20% of eligible confirmation events in any register with >=5 events.

If A passes and B fails, freeze **separation/downstream interaction bottleneck**.

### Arm C acceptable

Using verified notes:
- pitch preservation = **100%** for resolved assignments;
- invalid-shape / no-feasible-assignment rate <= **5%** of eligible monophonic attack groups;
- resolved assignment coverage >= **95%** for eligible monophonic attack groups.

If exact string/fret truth is unavailable, do not create an exact-fingering pass gate.

If A/B/C pass but correction effort is still high or no valid counterbalanced manual baseline exists, product benefit remains **unproven**.

## 10. Execution budget

### Fixed scientific operation count

With one transcriber and one separator:
- 12 Arm-A transcriptions;
- 12 separator runs;
- 12 Arm-B transcriptions;
- 12 Arm-C decoder evaluations;
- 0 training runs;
- 0 fine-tuning;
- 0 threshold sweeps;
- 0 seed sweeps;
- 0 automatic scientific retries.

Maximum transcriber invocations: **24**.
Maximum separator invocations: **12**.
Maximum decoder evaluations: **12**.

A technical retry after an infrastructure failure is **not** pre-authorized. Freeze the failure and request review.

### Runtime / memory

Current exact runtime and peak-memory budget is **UNRESOLVED** because S1 is not selected and the bass-valid T1 configuration has not been benchmarked on the intended environment.

Before execution authorization, add:
- environment identity;
- measured T1 seconds/audio-second and peak RSS from a non-study smoke input;
- measured S1 seconds/audio-second and peak RSS from a non-study smoke input;
- hard wall-time ceiling for the complete run.

Do not infer the budget from historical unrelated workloads.

### Storage

- Git audio storage: **0 bytes**.
- Unique study audio duration: <= **360 seconds**.
- Binary model/checkpoint storage: unresolved until S1/T1 artifacts are frozen.
- Temporary/local audio byte ceiling: unresolved until exact source formats are known.
- Permanent committed output should be metadata/results only (JSON/MD), with no private audio.

Execution remains disabled until a byte ceiling is filled prospectively.

### Paid cost

Current paid-spend ceiling: **CAD $0**.

If lawful source acquisition, compute, or model access requires payment, revise the packet with exact quoted/known ceilings and obtain explicit approval before spending.

## 11. Admission checks before any source/model access

Fail closed unless all are true:
- exactly 12 source-manifest rows;
- 8 development + 4 confirmation;
- minimum 3 performer-session groups;
- confirmation contains a group absent from development;
- no P1/P2/V2B/P3 identity;
- rights fields complete for each source;
- file SHA-256 fields frozen;
- T1 package/model/config frozen and bass-range review complete;
- S1 selected, rights-reviewed, hashed and runtime-benchmarked;
- annotation schema version frozen;
- metric code/config hash frozen;
- operation-count budget unchanged;
- runtime, memory and storage ceilings filled;
- paid-spend ceiling compatible with approval;
- one explicit bounded user authorization recorded after this packet is complete.

Any missing field stops before opening source audio or loading a model.

## 12. Disabled execution entry point

Prepared path:
- `astra_backend/evaluation/independent_bass_feasibility_v1.py`

Current behavior is intentionally fail-closed. It validates the packet status and exits without opening audio or loading models.

There is no live workflow, launch marker, authorization file or execution token in this preparation.

## 13. Current blockers

1. Exact 12-source rights-cleared manifest is missing.
2. Bass-valid T1 frequency/model-support configuration is not frozen.
3. S1 exact eligible separator is not selected.
4. Runtime / peak-memory evidence for T1 and S1 is missing.
5. Temporary byte ceiling is missing because source/checkpoint formats are not yet fixed.
6. Independent annotations do not exist.
7. No empirical execution authorization has been requested or granted.

These are intentional blockers, not placeholders to bypass.

## 14. Exact next task

Metadata/documentation only:

1. identify 12 candidate source performances and document rights/provenance without opening audio;
2. resolve/freeze the bass-valid Basic Pitch configuration from authoritative package/model evidence;
3. select exactly one eligible separator or freeze "no eligible separator" as the blocker;
4. benchmark candidate runtime only on a non-study synthetic/public smoke asset if permitted by the existing boundary, without touching the 12 study sources;
5. fill runtime/memory/storage ceilings;
6. freeze source manifest + candidate hashes + annotation template + evaluator contract;
7. then request **one bounded authorization** for exactly the admitted 12-performance execution.

Until all seven are satisfied: no source opening, checkpoint download, separation, transcription, workflow dispatch or real-data computation.

## 15. Interpretation boundary

A pass permits only the next scoped decision: whether bass deserves a larger independent development study and which stage to work on.

A pass does **not** establish:
- near-perfect full-song tabs;
- guitar accuracy;
- lead/rhythm separation;
- exact original fingering;
- customer delivery readiness;
- commercial readiness.

A failure remains useful if it identifies the first failing stage.
