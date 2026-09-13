# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-13 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless the user explicitly reopens them.
- GuitarSet/V3, IDMT/V4, V5/FLGD, duration research and protected-song execution remain closed/revealed.
- Never silently alter/drop decoded event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; DSP/model research stays under `scripts/songsterr-fresh/`.
- Fail closed: `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, Policy C `UNENROLLED`, protected-song embargoed.
- Ordinary research/coding/GitHub/CPU/checkpoint work may proceed. Explicit user authorization is required before Modal, Vercel heavy-GPU, L4 GPU, spending/procurement, performer/vendor hiring/contact for a purpose-built holdout, or recording/data acquisition for that route.

## V6 — METHOD + EXTERNAL SCORING FRAMEWORK FROZEN

Final method preregistration:
`docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`
commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.

Frozen implementation:
`scripts/songsterr-fresh/onset_birth_corroboration_v6.py`
commit `3a6cbb144fec5613ab6350deb6539297d713df28`
blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.

External scoring framework preregistration:
`docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`
commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen correctness design includes:
- Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note length `127.7 ms`, bends false, melodia true;
- preserve every decoded event and selected integer MIDI exactly once;
- DI-only canonical isolated-guitar audio path;
- one-to-one matching within immutable performance, onset <= `0.050 s`, pitch <= `50 cents`;
- pooled V6-positive precision with one-sided 95% Wilson lower bound;
- mandatory >=`1,000` pooled V6-positive estimates;
- pooled Wilson lower bound >=`0.9900`;
- player/category strata with >=100 positives require point precision >=`0.9500`;
- frozen categories: `chords`, `scales`, `singlenotes`, `techniques`, `music`;
- identity/runtime guards, event-preservation gate, deferred correctness reveal and single official run rule.

Do not change method/runtime/settings/matching/tolerances/gates/strata from holdout observations.

## GUITAR-TECHS V6 HOLDOUT — CLOSED OUTCOME C BEFORE CORRECTNESS

Immutable result:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`
commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.

Official audit run `34754519541`, job `103716527380`: success.
Artifact ID `10317695640`; ZIP SHA-256 `d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`; merged JSON SHA-256 `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`.

Population facts:
- 9 verified packages;
- 104 paired DI/MIDI performances;
- 18,934 paired reference events;
- 0 unpaired DI / 0 unpaired MIDI;
- all 104 alignment statuses `OK`;
- lag range `-8..+10` hops, median `-5` hops;
- 5 same-key overlaps, 7 unmatched note-ons, 0 unmatched note-offs.

Frozen decision: `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; `datasetStructurallySuitable:false` because preregistered structural suitability required zero MIDI anomalies.

Basic Pitch was not invoked; V6 was not invoked; correctness was not computed. Do not score, repair/drop events, create an A/B binding, or rerun Guitar-TECHS for V6 correctness.

## CURRENT ACTIVE WORK — REPLACEMENT UNTOUCHED HOLDOUT SEARCH

A replacement may advance toward media access only when all are defensible before correctness:
1. explicit usable/permissive performance-audio rights for this product-validation use;
2. real guitar;
3. immutable independent performed note-level onset + pitch truth, not reconstructed from evaluated audio;
4. plausible >=1,000 V6-positive evidence volume without duplicate/effect inflation;
5. defensible untouched status.

Before any selected corpus media access, freeze a corpus-specific reference-blind inventory/alignment preregistration. Structural/alignment audit comes before correctness. If unsuitable, reject without model correctness. If suitable, bind immutable identities into the already-frozen scoring framework, run contract/synthetic-only harness CI, then exactly one ordinary-GitHub-CPU correctness execution.

### Active research checkpoints

- `docs/checkpoints/SONGSTERR_FRESH_V6_REPLACEMENT_HOLDOUT_METADATA_SEARCH.md` — `64d9516d0efbba380769bd6cc52f93572393180a`.
- `docs/checkpoints/SONGSTERR_FRESH_V6_REPLACEMENT_HOLDOUT_SEARCH_UPDATE_2026-09-13.md` — `e8d8080c6944038a48150c9c42711a16cf92da6b`.
- `docs/checkpoints/SONGSTERR_FRESH_AGPTSET_RIGHTS_REVIEW_2026-09-13.md` — `5f4b9c6042eba77225eb5f146fdd5c73c3bee5b3`.
- `docs/checkpoints/SONGSTERR_FRESH_AGPTSET_REFERENCE_PROVENANCE_REVIEW_2026-09-13.md` — `8cb52041dec0782d5791b8bf5108596c407fc6b2`.
- `docs/checkpoints/SONGSTERR_FRESH_MULTIMODAL_ELECTRIC_GUITAR_METADATA_REVIEW_2026-09-13.md` — `1f64818fa63327ca17c23586cc79017c74b83446`.
- `docs/checkpoints/SONGSTERR_FRESH_GIHME_METADATA_RELEASE_REVIEW_2026-09-13.md` — `1c440f0e9a4e8281c49cf90877e786b5c2c9d9cd`.
- `docs/checkpoints/SONGSTERR_FRESH_MMIP_METADATA_RIGHTS_REVIEW_2026-09-13.md` — `dd44674afa5b1d394cf760a192bbb1a2cae67b83`.
- `docs/checkpoints/SONGSTERR_FRESH_EGDB_METADATA_RIGHTS_REFERENCE_REVIEW_2026-09-13.md` — `a15aef9df3f90d7076cc71d5ae470c9fb1fc7db0`.
- `docs/checkpoints/SONGSTERR_FRESH_GUITARDUETS_METADATA_REFERENCE_REVIEW_2026-09-13.md` — `2b6c2d50e5cea17e96a3e8666f611292fc362aa7`.
- `docs/checkpoints/SONGSTERR_FRESH_EGIPT_METADATA_REFERENCE_RIGHTS_REVIEW_2026-09-13.md` — `40312c628c55dc5d7e635f718ce99921b984430e`.
- `docs/checkpoints/SONGSTERR_FRESH_V6_GENERAL_CORPUS_METADATA_SWEEP_2026-09-13.md` — `c962d14c94aac08858226166c712ad93ea651993`.
- `docs/checkpoints/SONGSTERR_FRESH_V6_RECENT_REPOSITORY_SWEEP_2026-09-13.md` — `f5961fe28bda99721721f7fdcb5c0481c5ab80fb`.
- `docs/checkpoints/SONGSTERR_FRESH_V6_MULTITRACK_BENCHMARK_SWEEP_2026-09-13.md` — `fb3469695768ce572c2c8fce2d7bdc6c5711a9fb`.
- `docs/checkpoints/SONGSTERR_FRESH_V6_RIGHTS_MIRROR_FRONTIER_RECHECK_2026-09-13.md` — `23d55751561b7102e6e726a6adc8a419511e67dd`.
- `docs/checkpoints/SONGSTERR_FRESH_V6_PURPOSE_BUILT_EXTERNAL_HOLDOUT_OPTION_2026-09-13.md` — latest `dde8aa9cc97d8cbd9efbd06cc4d8c8b00d45fda4`.
- `docs/checkpoints/SONGSTERR_FRESH_V6_2026_LITERATURE_FRONTIER_SWEEP_2026-09-13.md` — `ac6ac23f25c8f6f6c225464abc92b0988d064dd8`.
- `docs/checkpoints/SONGSTERR_FRESH_V6_INSTITUTIONAL_TECHNIQUE_FRONTIER_2026-09-13.md` — `95eec317ead304b9e03a2139b72e15a9a4efeff8`.

## CANDIDATE / FRONTIER STATUS

### AG-PT-set — REJECTED: AUDIO-DERIVED REFERENCE + RIGHTS UNRESOLVED

Latest immutable reference review:
`docs/checkpoints/SONGSTERR_FRESH_AGPTSET_REFERENCE_PROVENANCE_REVIEW_2026-09-13.md`
commit `8cb52041dec0782d5791b8bf5108596c407fc6b2`.

AG-PT-set remains scientifically substantial (~15 h 55 m total; ~10 h 04 m labeled; 32,592 labeled note events), but its Audio Mostly 2024 methodology establishes that the released onset reference is **constructed from the recorded audio**:
- candidate labels were seeded with `aubioonset`;
- five musician annotators inspected the waveform + high-resolution Mel spectrogram in Audacity;
- they added missed onsets, removed false positives and visually aligned labels to audio onsets at millisecond zoom;
- known note number/pitch/sequence plus a pitch detector were used to identify/correct annotation mistakes.

That can produce excellent MIR annotations, but it violates the frozen V6 requirement for a separately captured independent performed note-level onset+pitch stream. The primary Zenodo archive also still lacks an explicit permissive dataset-file license for this product-validation use.

Disposition: reject before media access. Even future rights clearance alone cannot make AG-PT-set eligible. Reconsider only if an authoritative separately captured contemporaneous performed note-level onset+pitch stream exists; a better audio-derived/manual annotation does not cure provenance.

### GAPS — RIGHTS BLOCKED
~14 h, 300 performances, >200 performers, high-resolution MIDI. Official project terms restrict to non-commercial research and impose distribution/permission limits. A Hugging Face mirror tagged `MIT` does not override authoritative corpus terms. Do not use absent written permission clearing product-validation use.

### EGSet12 — NOT UNTOUCHED
Full-history audit found 21 distinct matching pre-search commits among 7,662 reachable commits. Reject; do not rewrite history to restore untouched status.

### IDMT-SMT-Audio-Effects / GUITAR-FX-DIST — RIGHTS BLOCKED
Current Fraunhofer terms remain CC BY-NC-ND 4.0. Reject.

### EG-Solo / G&N / TENT — RECORDING RIGHTS BLOCKED
EG-Solo annotations rely on third-party/professional YouTube/popular-song audio; G&N/TENT derive from commercial textbook-CD recordings. Reject.

### EG-IPT — REFERENCE + RIGHTS FAIL
52,320 real electric-guitar files / >28 h / DI path, but no released immutable independent performed per-note onset+pitch stream has been established and explicit permissive dataset-media rights are also not established. Reject before media access.

### Multimodal Electric Guitar Data — RIGHTS CLEANER, REFERENCE INSUFFICIENT
Zenodo `6470235/6470236`, ~32.5 GB, 36 real guitarists, CC BY 4.0. Public materials establish actions/EMG/MoCap/audio, not immutable performed note-level onset+pitch truth. Do not download for V6 admission unless such a reference is authoritatively released.

### MMIP — RIGHTS + REFERENCE PROVENANCE FAIL
CC BY-NC-SA 4.0; guitar MIDI produced after recording via Ableton audio-to-MIDI. Reject.

### GIHME — RELEASE NEVER MATERIALIZED
Paper describes ~10 h hexaphonic guitar improvisations, but official repository remains placeholder without completed corpus, stable annotation package/checksums/license. Do not reconstruct from demos/videos/detectors.

### EGFxSet — narrow backup only
Real electric-guitar hardware recordings / CC BY 4.0, about 690 unique clean performances, but no established high-resolution performed onset reference. Effect variants cannot inflate independent evidence.

### EGDB / EGDB-PG — RIGHTS + AUDIO-DERIVED ONSET REFERENCE FAIL
Real clean DI from 240 performed tablatures, but authoritative dataset-audio rights are not established; onset reference is materially derived using onset detection on recorded DI, expected tab/BPM timing and correction. Reject before media access.

### GuitarDuets — REAL SUBSET LACKS NOTE TRUTH
~3 h real + synthesized duets; note-level MIDI is supplied for synthesized duets, not an immutable performed note reference for the real subset. Reject.

### Other public/repository candidates — rejected before media access
- GPT/Su 2014: historical release inaccessible/unverifiable and current data terms/bytes cannot be frozen.
- Physically Augmented Guitar Chord Dataset / Isolated Guitar Chords: chord labels only, not per-note performed truth.
- NSynth / Slakh2100: sampler/VST rendered, not real performed guitar.
- URMP: no guitar population.
- GuitarJam: clean CC0 DI but no note truth.
- `guitar-fretboard-notes`: 390 nominal notes only, no independent performed onset timestamps and below plausible >=1,000-positive capacity.
- Semantic Timbre Dataset: effect expansion of the same ~690 EGFxSet performances, not new evidence.
- `guitar-chord-mix`: derivative mixture of exposed/ineligible corpora plus synthetic/noise material.
- MedleyDB / MUSDB18 / MoisesDB: rights and/or guitar note-reference semantics fail.
- UT Austin/Kaggle guitar transcription set: CC BY-NC-SA; frame/fret labels rather than independent performed note-level onset+pitch truth.
- MagCIL `guitar_style_dataset`: 549 real technique recordings plus MuseScore exercises, but technique/exercise labels are not independent performed note truth; repository MIT license explicitly applies to software and does not establish permissive media rights.
- University of Manchester/NOVARS AI Guitar Assistant: 61.93 GB multimodal data from 21 guitarists, but published capture design is audio/video/Myo biometrics rather than a contemporaneous independent note-level MIDI/onset stream; performance data also remain outside the published analysis/release.
- Mendeley/Figshare fret-note/instrument-class collections reviewed are too small/narrow and/or lack independent performed onset truth; Portuguese field-recording instrument corpus is CC BY-NC-SA and class-level only.

### Geoff Bremner Multimodal Music Corpus — PRIVATE-LICENSE LEAD ONLY
Cleaner single-rights-holder story and advertised commercial licensing, but public material has not established guitar-specific contemporaneous performed-MIDI/onset provenance, full-corpus evidence volume, stable full-corpus identities, or exact rights for this experiment. Do not acquire media yet.

## 2026 LITERATURE / INSTITUTIONAL FRONTIER

Newest reviewed work still reuses known/closed sources or synthetic derivatives:
- TART (2026-09-10) evaluates GuitarSet, EGDB and noisy derivatives; no new independent holdout.
- Playability-Aware / Noise2Fret (2026-08-31) uses GuitarSet plus GOAT. **GOAT/reference scoring remains archived and is not reopened by this observation.**
- EG-VAE (2026-08-06) does not establish a new real-guitar corpus with independent performed note-level onset+pitch truth.
- current alternate-tuning work reviewed uses synthetic/VST-rendered material.
- targeted institutional / Mendeley / Figshare searches have not surfaced a qualifying independently note-referenced real-guitar corpus.

Generic public repositories, current transcription literature and targeted institutional technique datasets are now close to exhausted under the frozen gates. This is an evidence-bounded result, not proof that no qualifying corpus exists.

## PURPOSE-BUILT UNTOUCHED HOLDOUT — DESIGN OPTION ONLY

Latest immutable design checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_V6_PURPOSE_BUILT_EXTERNAL_HOLDOUT_OPTION_2026-09-13.md`
commit `dde8aa9cc97d8cbd9efbd06cc4d8c8b00d45fda4`.

A purpose-built corpus is now a materially stronger fallback because even AG-PT-set's precise labels fail independence. It is **not selected and no acquisition is authorized**.

Preferred architecture if ever chosen:
- real guitar;
- evaluated signal = conventional clean magnetic DI;
- reference = simultaneous independent physical fret-position + trigger/dynamics sensor path;
- current feasibility example only: Industrial Radio Fretsense/Solange 6.

Important caveat: physical fret sensing strengthens pitch identity, but onset timing remains sensor/algorithm derived through piezo-trigger logic with configurable trigger/filter/decay behavior. It is not presumed perfect truth. A future capture preregistration would require a separate non-holdout calibration phase, then frozen/hashed hardware, firmware, trigger/filter/decay settings and geometry before admitted takes. Raw MIDI must pass a fail-closed structural audit with zero orphan note-ons, zero orphan note-offs and zero same-key overlaps under frozen semantics. Piezo channels may be diagnostics only if preregistered; never alternate scoring audio or a rescue path.

Jamstik-style six-channel hexaphonic MIDI + separate audio is a weaker fallback because vendor documentation acknowledges extra/missed MIDI notes and channel-preservation pitfalls.

The purpose-built design requires original/public-domain/rightscleared material, explicit product-validation rights, zero model access during collection, no model-informed retakes, raw reference preservation, frozen capture-QA rules and the same five scoring categories. A provisional >=20,000 raw-reference-note / multi-player collection preference is planning only and does **not** change the frozen >=1,000 V6-positive gate.

No purchase, deposit, vendor/performer contact, hiring, recording or purpose-built data acquisition without explicit user selection/authorization.

## NEXT ALLOWED ACTION

1. Continue metadata-only search only where it can add new information: rights-holder/private corpora, future institutional releases with independent note sensing, or purpose-built protocol/hardware feasibility.
2. Do not pursue AG-PT-set as a V6 holdout under its current audio-derived reference; rights clarification alone is no longer sufficient.
3. Keep Geoff Bremner only as a private-license metadata lead pending reference semantics, volume, identities and exact rights.
4. Keep Multimodal Electric Guitar Data and EGFxSet as non-audit-ready backups under their existing reference limitations.
5. Continue purpose-built **protocol/hardware metadata** research if useful, but no procurement/contact/capture without explicit user authorization.
6. Any newly selected existing corpus must pass rights/reference/volume/untouched gates before media access and must get a corpus-specific reference-blind preregistration first.
7. If structural audit later passes, bind identities into the frozen framework, run no-real-correctness harness CI, then exactly one ordinary-GitHub-CPU correctness run.
8. Ask the user before Modal, Vercel heavy-GPU or L4 execution, or before any purpose-built spending/contact/acquisition.

## STILL FORBIDDEN

- any Guitar-TECHS V6 correctness, anomaly repair/exclusion or rescue binding;
- AG-PT-set V6 acquisition/audit/scoring under its current audio-derived onset reference, even if rights alone later clear;
- GAPS use absent written permission clearing official restrictions; mirror tags do not supersede source terms;
- EGSet12 scoring/binding/history rewriting;
- IDMT-SMT-Audio-Effects / GUITAR-FX-DIST use under current NC/ND terms;
- EG-Solo or G&N/TENT use under current recording-rights evidence;
- EG-IPT, EGDB/EGDB-PG, GuitarDuets, MMIP, GIHME or MagCIL rescue through evaluated-audio-derived/reconstructed truth;
- counting synthetic renders, effect variants, duplicates or derivative mixtures as independent real performances;
- reopening GOAT/reference scoring merely because current papers use GOAT;
- V5 FLGD rerun/post-result tuning or using revealed FLGD/IDMT/GuitarSet/protected-song correctness to tune V6;
- changing frozen V6/scoring rules from any holdout observation;
- protected-song execution;
- duration research;
- archived V143/Gomyway or GOAT/reference scoring;
- real-corpus optimizer/threshold sweeps or training/fine-tuning on a proposed admission holdout;
- treating Fretsense/Jamstik/vendor MIDI as infallible reference truth;
- calibrating purpose-built reference hardware on admitted holdout material using Basic Pitch/V6/model outcomes;
- purpose-built procurement/hiring/contact/recording/data acquisition without explicit user authorization;
- Production/customer promotion without untouched external validation and separate policy approval;
- Modal, Vercel heavy-GPU or L4 execution without explicit user authorization.

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1` and read this file first. V6 method/scoring remain frozen and no replacement-holdout V6 correctness has been exposed. Guitar-TECHS is closed outcome C before correctness. **AG-PT-set is now also rejected before media access, not merely rights-blocked:** its paper explicitly constructs precise onset labels from the recordings using `aubioonset` plus Audacity waveform/spectrogram inspection and human correction, so it fails the frozen independent-reference gate; rights clearance alone cannot cure that. GAPS remains officially restricted despite a permissive mirror tag; Geoff Bremner is only a private-license lead; Multimodal Electric Guitar Data and EGFxSet remain reference-insufficient backups. Public repositories, 2026 literature and institutional technique datasets are close to exhausted. A purpose-built untouched holdout is documented as a design-only fallback, with physical fret/trigger sensing + separate DI preferred, but sensor-derived onset MIDI still requires calibration frozen before holdout collection and a zero-anomaly reference-blind audit. No purchase, hiring, contact, recording or acquisition is authorized. Do not reopen archived V143/Gomyway or GOAT/reference scoring unless the user explicitly asks.