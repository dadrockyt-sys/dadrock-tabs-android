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
- Ordinary metadata research/coding/GitHub/CPU/checkpoint work may proceed.
- Explicit user authorization is required before Modal, Vercel heavy-GPU, L4 GPU, purpose-built holdout spending/procurement, performer/vendor contact or hiring, or recording/data acquisition.

## V6 — METHOD + EXTERNAL SCORING FRAMEWORK FROZEN

Final method preregistration:
`docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`
commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.

Frozen implementation:
`scripts/songsterr-fresh/onset_birth_corroboration_v6.py`
commit `3a6cbb144fec5613ab6350deb6539297d713df28`
blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.

External scoring framework:
`docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`
commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen correctness design:
- Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note length `127.7 ms`, bends false, melodia true;
- preserve every decoded event and selected integer MIDI exactly once;
- canonical isolated-guitar DI audio only;
- one-to-one matching within immutable performance: onset <= `0.050 s`, pitch <= `50 cents`;
- primary metric V6-positive precision with one-sided 95% Wilson lower bound;
- mandatory >=`1,000` pooled V6-positive estimates;
- pooled Wilson lower bound >=`0.9900`;
- player/category strata with >=100 positives require point precision >=`0.9500`;
- frozen categories: `chords`, `scales`, `singlenotes`, `techniques`, `music`;
- identity/runtime guards, event-preservation gate, deferred correctness reveal, exactly one official correctness run.

Do not change method/runtime/settings/matching/tolerances/gates/strata from holdout observations.

## GUITAR-TECHS — CLOSED OUTCOME C BEFORE CORRECTNESS

Result:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`
commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.

Official audit run `34754519541`, job `103716527380`: success.
Artifact `10317695640`; ZIP SHA-256 `d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`; merged JSON SHA-256 `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`.

Facts:
- 9 verified packages;
- 104 DI/MIDI pairs;
- 18,934 reference events;
- 0 unpaired DI/MIDI;
- all 104 alignment statuses `OK`;
- lag range `-8..+10` hops, median `-5`;
- 5 same-key overlaps, 7 unmatched note-ons, 0 unmatched note-offs.

Frozen result: `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; `datasetStructurallySuitable:false` because the preregistered audit required zero MIDI anomalies.

Basic Pitch/V6/correctness were never run. Do not score, repair/drop events, create an A/B binding, or rerun Guitar-TECHS for V6 correctness.

## REPLACEMENT HOLDOUT GATES

Before any candidate media access, all must be defensible:
1. explicit usable/permissive performance-audio rights for current product validation;
2. real guitar;
3. immutable independent performed note-level onset + pitch truth, not reconstructed from evaluated audio;
4. plausible >=1,000 V6-positive evidence volume without duplicate/effect inflation;
5. defensible untouched status.

Then freeze a corpus-specific reference-blind inventory/alignment preregistration before media access. Structural/alignment audit comes before correctness. Reject unsuitable data without correctness. If suitable, bind immutable identities to the already-frozen framework, run contract/synthetic-only harness CI, then exactly one ordinary-GitHub-CPU official correctness run.

## CURRENT RESEARCH CHECKPOINTS

- `SONGSTERR_FRESH_V6_REPLACEMENT_HOLDOUT_METADATA_SEARCH.md` — `64d9516d0efbba380769bd6cc52f93572393180a`
- `SONGSTERR_FRESH_V6_REPLACEMENT_HOLDOUT_SEARCH_UPDATE_2026-09-13.md` — `e8d8080c6944038a48150c9c42711a16cf92da6b`
- `SONGSTERR_FRESH_AGPTSET_RIGHTS_REVIEW_2026-09-13.md` — `5f4b9c6042eba77225eb5f146fdd5c73c3bee5b3`
- `SONGSTERR_FRESH_AGPTSET_REFERENCE_PROVENANCE_REVIEW_2026-09-13.md` — `8cb52041dec0782d5791b8bf5108596c407fc6b2`
- `SONGSTERR_FRESH_MULTIMODAL_ELECTRIC_GUITAR_METADATA_REVIEW_2026-09-13.md` — `1f64818fa63327ca17c23586cc79017c74b83446`
- `SONGSTERR_FRESH_GIHME_METADATA_RELEASE_REVIEW_2026-09-13.md` — `1c440f0e9a4e8281c49cf90877e786b5c2c9d9cd`
- `SONGSTERR_FRESH_MMIP_METADATA_RIGHTS_REVIEW_2026-09-13.md` — `dd44674afa5b1d394cf760a192bbb1a2cae67b83`
- `SONGSTERR_FRESH_EGDB_METADATA_RIGHTS_REFERENCE_REVIEW_2026-09-13.md` — `a15aef9df3f90d7076cc71d5ae470c9fb1fc7db0`
- `SONGSTERR_FRESH_GUITARDUETS_METADATA_REFERENCE_REVIEW_2026-09-13.md` — `2b6c2d50e5cea17e96a3e8666f611292fc362aa7`
- `SONGSTERR_FRESH_EGIPT_METADATA_REFERENCE_RIGHTS_REVIEW_2026-09-13.md` — `40312c628c55dc5d7e635f718ce99921b984430e`
- `SONGSTERR_FRESH_V6_GENERAL_CORPUS_METADATA_SWEEP_2026-09-13.md` — `c962d14c94aac08858226166c712ad93ea651993`
- `SONGSTERR_FRESH_V6_RECENT_REPOSITORY_SWEEP_2026-09-13.md` — `f5961fe28bda99721721f7fdcb5c0481c5ab80fb`
- `SONGSTERR_FRESH_V6_MULTITRACK_BENCHMARK_SWEEP_2026-09-13.md` — `fb3469695768ce572c2c8fce2d7bdc6c5711a9fb`
- `SONGSTERR_FRESH_V6_RIGHTS_MIRROR_FRONTIER_RECHECK_2026-09-13.md` — `23d55751561b7102e6e726a6adc8a419511e67dd`
- `SONGSTERR_FRESH_V6_PURPOSE_BUILT_EXTERNAL_HOLDOUT_OPTION_2026-09-13.md` — latest `dde8aa9cc97d8cbd9efbd06cc4d8c8b00d45fda4`
- `SONGSTERR_FRESH_V6_2026_LITERATURE_FRONTIER_SWEEP_2026-09-13.md` — `ac6ac23f25c8f6f6c225464abc92b0988d064dd8`
- `SONGSTERR_FRESH_V6_INSTITUTIONAL_TECHNIQUE_FRONTIER_2026-09-13.md` — `95eec317ead304b9e03a2139b72e15a9a4efeff8`
- `SONGSTERR_FRESH_V6_REFERENCE_HARDWARE_LANDSCAPE_2026-09-13.md` — `84b61b31dc0f4a23c7c182580632ab417879bb69`
- `SONGSTERR_FRESH_GEOFF_BREMNER_REFERENCE_PROVENANCE_REVIEW_2026-09-13.md` — `4e5e884da729ba7f6227f2d644544232ed312853`

## CANDIDATE STATUS

### AG-PT-set — REJECTED: AUDIO-DERIVED REFERENCE + RIGHTS UNRESOLVED

Reference review `8cb52041dec0782d5791b8bf5108596c407fc6b2` established that the precise onset labels are constructed from the recordings: `aubioonset` seeds candidate labels; musician annotators inspect waveform + high-resolution Mel spectrogram in Audacity, add/remove labels and visually align them to onsets; known note sequence/pitch plus a pitch detector help identify annotation mistakes. This may be excellent MIR annotation, but it fails the frozen requirement for a separately captured independent performed note stream. Zenodo data-file rights also remain unestablished for product validation.

Do not acquire/audit/score AG-PT-set for V6 under the current release. Rights clearance alone cannot cure reference provenance. Reconsider only if an authoritative separately captured contemporaneous performed note-level onset+pitch stream exists.

### GAPS — RIGHTS BLOCKED

Scientifically attractive (~14 h, 300 performances, >200 performers, high-resolution MIDI) but official terms restrict non-commercial research and redistribution/permission. A permissive-looking Hugging Face mirror tag does not supersede official corpus terms. Do not use absent written permission clearing this product-validation use.

### EGSet12 — NOT UNTOUCHED

Full-history audit found 21 matching pre-search commits among 7,662 reachable commits. Reject; do not rewrite history to restore untouched status.

### IDMT-SMT-Audio-Effects / GUITAR-FX-DIST — RIGHTS BLOCKED

Current Fraunhofer terms remain CC BY-NC-ND 4.0. Reject.

### EG-Solo / G&N / TENT — RECORDING RIGHTS BLOCKED

EG-Solo relies on third-party/professional YouTube/popular-song audio; G&N/TENT on commercial textbook-CD recordings. Reject.

### EG-IPT — REFERENCE + RIGHTS FAIL

52,320 real electric-guitar files / >28 h / DI path, but no released immutable independent performed note onset+pitch stream and no explicit permissive dataset-media rights. Reject before media access.

### Multimodal Electric Guitar Data — RIGHTS CLEANER, REFERENCE INSUFFICIENT

Zenodo `6470235/6470236`, ~32.5 GB, 36 real guitarists, CC BY 4.0. Public materials establish actions/EMG/MoCap/audio, not immutable performed note-level onset+pitch truth. Do not download for V6 admission absent a qualifying released reference.

### MMIP — RIGHTS + REFERENCE PROVENANCE FAIL

CC BY-NC-SA 4.0; guitar MIDI is produced post-recording via Ableton audio-to-MIDI. Reject.

### GIHME — RELEASE NEVER MATERIALIZED

Paper describes ~10 h hexaphonic guitar improvisations; official repository remains a placeholder without completed corpus, stable annotations/checksums/license. Do not reconstruct from demos/videos/detectors.

### EGFxSet — NARROW BACKUP ONLY

Real electric-guitar hardware recordings / CC BY 4.0, about 690 unique clean performances, no established high-resolution performed onset reference. Effect variants cannot inflate independent evidence.

### EGDB / EGDB-PG — RIGHTS + AUDIO-DERIVED ONSET REFERENCE FAIL

Real clean DI from 240 performed tablatures, but rights are unestablished and onset reference is materially derived from recorded DI plus expected tab/BPM timing and correction. Reject before media access.

### GuitarDuets — REAL SUBSET LACKS NOTE TRUTH

~3 h real + synthesized duets; note-level MIDI exists for synthesized duets, not an immutable performed reference for real performances. Reject.

### Geoff Bremner Multimodal Music Corpus — PRIVATE-LICENSE LEAD / NOT AUDIT-READY

Dedicated review `4e5e884da729ba7f6227f2d644544232ed312853`.

The public sample has an unusually clean chain-of-title story: original music, single creator/rightsholder, real stems, MIDI, Guitar Pro, notation, Ableton project, and separately offered commercial licensing. But the public repository exposes one arrangement-level `Pharisaism.mid`, one Guitar Pro file, separate guitar notation PDFs, an Ableton project and multiple guitar stems, while the dataset card does **not** say that guitar MIDI was captured simultaneously from those performances or that MIDI timing represents performed attacks. Public metadata does not establish instrument mapping, performed-vs-authored MIDI provenance, clock alignment, full-corpus volume or guitar population.

Keep only as a metadata lead. Do not acquire media or contact the rights holder under the current metadata-only phase. It may advance only if authoritative pre-media documentation establishes independently captured guitar-specific performed MIDI/onset semantics, sufficient population/volume, stable identities and exact product-validation rights. If the MIDI is authored/quantized score data, Guitar Pro/DAW export, post-hoc transcription or audio-derived, reject even if commercial licensing is available.

### Other rejected/not-audit-ready public leads

- GPT/Su 2014: historical release inaccessible/unverifiable; current terms/bytes cannot be frozen.
- robot guitar chord corpus / isolated guitar chords: chord labels only.
- NSynth / Slakh2100: sampler/VST rendered, not real performed guitar.
- URMP: no guitar population.
- GuitarJam: clean CC0 DI but no note truth.
- `guitar-fretboard-notes`: 390 notes only; no independent onset timestamps; inadequate capacity.
- Semantic Timbre Dataset: effect expansion of EGFxSet source performances.
- `guitar-chord-mix`: derivative mixture of exposed/ineligible corpora plus synthetic/noise.
- MedleyDB / MUSDB18 / MoisesDB: rights and/or guitar note-reference semantics fail.
- UT Austin/Kaggle guitar transcription set: CC BY-NC-SA; frame/fret labels, not independent performed note truth.
- MagCIL `guitar_style_dataset`: 549 real technique recordings plus MuseScore exercises; technique/exercise labels are not independent performed note truth; repository MIT license explicitly applies to software, not enough to clear performance media.
- University of Manchester/NOVARS AI Guitar Assistant: 61.93 GB / 21 guitarists, but published capture is audio/video/Myo biometrics rather than independent note-level MIDI/onset; performance data not yet released/analyzed as such.
- targeted Mendeley/Figshare fret-note/instrument-class sets: too small/narrow and/or lack independent performed onset truth; Portuguese field-recording corpus is CC BY-NC-SA and class-level only.

## 2026 LITERATURE / INSTITUTIONAL FRONTIER

- TART (2026-09-10): GuitarSet, EGDB and noisy derivatives; no new independent holdout.
- Playability-Aware / Noise2Fret (2026-08-31): GuitarSet + GOAT. **GOAT/reference scoring remains archived and is not reopened.**
- EG-VAE (2026-08-06): no qualifying independently note-referenced real-guitar corpus established.
- alternate-tuning work reviewed uses synthetic/VST-rendered material.
- generic repositories and targeted institutional searches have not surfaced a qualifying replacement.

The public frontier is close to exhausted under the frozen gates. This is an evidence-bounded result, not proof no qualifying corpus exists.

## PURPOSE-BUILT UNTOUCHED HOLDOUT — DESIGN OPTION ONLY

Design checkpoint latest `dde8aa9cc97d8cbd9efbd06cc4d8c8b00d45fda4`.
Hardware landscape `84b61b31dc0f4a23c7c182580632ab417879bb69`.

A purpose-built corpus is now a materially stronger fallback because even precise public labels often fail independence. It is **not selected and no acquisition is authorized**.

Current design preference:
1. real guitar with conventional clean magnetic DI as evaluated signal;
2. simultaneous separately sensed reference using physical fret-position + independent trigger/dynamics sensors;
3. current feasibility example only: Industrial Radio Fretsense / Solange 6.

Fretsense is the strongest surfaced current architecture because fret/string conductivity supplies pitch identity, bridge/piezo sensors provide trigger/dynamics evidence, and conventional magnetic audio remains separate. But onset is still sensor/algorithm derived; trigger/filter/decay settings matter and raw MIDI is not presumed infallible. A future protocol would need non-holdout calibration, then frozen/hashed hardware, firmware, trigger/filter/decay settings and geometry before admitted takes. Raw MIDI must survive the same fail-closed zero-anomaly audit. Piezo channels are diagnostics only if preregistered, never scoring/rescue audio.

Current product availability/lead time is unproven; live manufacturer pages coexist with stale Solange pricing/shipping update text. Do not contact/order now.

Jamstik-style hexaphonic MIDI + separate audio is weaker because vendor docs acknowledge extra/missed MIDI and channel-preservation pitfalls. AeroBand/digital smart guitars and historical SynthAxe/Casio-style controllers fail the conventional real-guitar DI requirement. HyVibe/piezo-audio systems do not supply independent note truth.

Purpose-built collection, if ever explicitly selected, must use original/public-domain/rightscleared material, explicit product-validation rights, zero model access during collection, no model-informed retakes, raw reference preservation, frozen capture-QA rules and the same five categories. Provisional >=20,000 raw-reference-note / multi-player planning is **not** a new admission gate; frozen >=1,000 V6-positive remains authoritative.

No purchase, deposit, vendor/performer contact, hiring, recording or data acquisition without explicit user authorization.

## NEXT ALLOWED ACTION

1. Continue metadata-only work only where it can add new information: rights-holder/private corpora, future institutional releases with independently sensed notes, or purpose-built protocol/hardware feasibility.
2. Do not pursue AG-PT-set as a V6 holdout under its current audio-derived reference.
3. Keep Geoff Bremner metadata-only unless public/authoritative documentation resolves performed MIDI provenance; do not contact/acquire yet.
4. Keep Multimodal Electric Guitar Data and EGFxSet as reference-insufficient backups.
5. Continue purpose-built protocol/hardware metadata research if useful, but no procurement/contact/capture without explicit user authorization.
6. Any selected existing corpus must pass rights/reference/volume/untouched gates before media access and receive a corpus-specific reference-blind preregistration first.
7. If structural audit later passes, bind identities into the frozen framework, run no-real-correctness harness CI, then exactly one ordinary-GitHub-CPU correctness run.
8. Ask the user before Modal, Vercel heavy-GPU, L4, or purpose-built spending/contact/acquisition.

## STILL FORBIDDEN

- Guitar-TECHS V6 correctness, anomaly repair/exclusion or rescue binding;
- AG-PT-set acquisition/audit/scoring under its current audio-derived reference, even if rights alone later clear;
- GAPS use absent written permission clearing official restrictions; mirror tags do not supersede source terms;
- EGSet12 scoring/binding/history rewriting;
- IDMT-SMT-Audio-Effects / GUITAR-FX-DIST under current NC/ND terms;
- EG-Solo or G&N/TENT under current recording-rights evidence;
- EG-IPT, EGDB/EGDB-PG, GuitarDuets, MMIP, GIHME or MagCIL rescue through evaluated-audio-derived/reconstructed truth;
- synthetic renders/effect variants/duplicates/derivative mixtures counted as independent real performances;
- reopening GOAT/reference scoring because current papers use GOAT;
- V5 FLGD rerun/post-result tuning or use of revealed FLGD/IDMT/GuitarSet/protected-song correctness to tune V6;
- changing frozen V6/scoring rules from holdout observations;
- protected-song execution;
- duration research;
- archived V143/Gomyway or GOAT/reference scoring;
- real-corpus optimizer/threshold sweeps or training/fine-tuning on a proposed admission holdout;
- treating Fretsense/Jamstik/vendor MIDI as infallible truth;
- calibrating purpose-built hardware on admitted holdout material using Basic Pitch/V6/model outcomes;
- purpose-built procurement/hiring/contact/recording/data acquisition without explicit user authorization;
- Production/customer promotion without untouched external validation + separate policy approval;
- Modal, Vercel heavy-GPU or L4 without explicit user authorization.

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1` and read this file first. V6 method/scoring remain frozen; no replacement-holdout correctness has been exposed. Guitar-TECHS is closed outcome C before correctness. AG-PT-set is now rejected before media access because its precise onsets are constructed from recorded audio; rights clearance alone cannot cure that. GAPS remains rights-blocked. Geoff Bremner remains only a private-license metadata lead because its public sample does not establish that guitar MIDI is contemporaneous performed truth. Public repositories, 2026 literature and institutional technique datasets are close to exhausted. Purpose-built capture is a design-only fallback: Fretsense-style physical fret/trigger sensing + separate magnetic DI is the strongest surfaced architecture, but sensor MIDI requires frozen calibration/settings and a zero-anomaly reference-blind audit and current availability is unproven. No purchase, hiring, contact, recording or acquisition is authorized. Do not reopen archived V143/Gomyway or GOAT/reference scoring unless the user explicitly asks.