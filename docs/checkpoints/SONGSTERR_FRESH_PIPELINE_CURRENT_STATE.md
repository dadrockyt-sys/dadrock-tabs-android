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
- Explicit user authorization is required before Modal, Vercel heavy-GPU, L4 GPU, purpose-built spending/procurement, performer/vendor contact or hiring, or recording/data acquisition.

## V6 — FROZEN

Method preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`, commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
Implementation: `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
External scoring framework: `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`, commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials:
- Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true;
- preserve every decoded event and selected integer MIDI exactly once;
- isolated-guitar DI evaluation path;
- one-to-one within-performance match: onset <= `0.050 s`, pitch <= `50 cents`;
- V6-positive precision, one-sided 95% Wilson lower bound;
- >=`1,000` pooled V6-positive estimates;
- pooled Wilson LB >=`0.9900`;
- player/category strata with >=100 positives require point precision >=`0.9500`;
- frozen categories `chords`, `scales`, `singlenotes`, `techniques`, `music`;
- deferred correctness reveal and exactly one official correctness run.

Do not alter method/runtime/settings/matching/tolerances/gates/strata from holdout observations.

## GUITAR-TECHS — CLOSED OUTCOME C BEFORE CORRECTNESS

Result checkpoint `docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`, commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.
Official audit run `34754519541`, job `103716527380`, artifact `10317695640`.
104 DI/MIDI pairs, 18,934 reference events, all alignments `OK`, but 5 same-key overlaps + 7 unmatched note-ons violate the preregistered zero-anomaly structural gate.
Frozen result: `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; `datasetStructurallySuitable:false`.
Basic Pitch/V6/correctness were never run. Do not score, repair/drop events, bind or rerun.

## REPLACEMENT HOLDOUT GATES

Before candidate media access all must be defensible:
1. explicit usable/permissive performance-audio rights for product validation;
2. real guitar;
3. immutable independent performed note-level onset + pitch truth, not reconstructed from evaluated audio;
4. plausible >=1,000 V6-positive capacity without duplicate/effect inflation;
5. defensible untouched status.

Then freeze corpus-specific reference-blind inventory/alignment preregistration before media access; structural audit first; reject unsuitable data without correctness; if suitable bind identities, run contract/synthetic-only harness CI, then exactly one ordinary-GitHub-CPU correctness run.

## ACTIVE / RECENT CHECKPOINTS

- replacement metadata search `64d9516d0efbba380769bd6cc52f93572393180a`
- replacement update `e8d8080c6944038a48150c9c42711a16cf92da6b`
- AG-PT rights `5f4b9c6042eba77225eb5f146fdd5c73c3bee5b3`
- AG-PT reference provenance `8cb52041dec0782d5791b8bf5108596c407fc6b2`
- Multimodal Electric Guitar review `1f64818fa63327ca17c23586cc79017c74b83446`
- GIHME `1c440f0e9a4e8281c49cf90877e786b5c2c9d9cd`
- MMIP `dd44674afa5b1d394cf760a192bbb1a2cae67b83`
- EGDB `a15aef9df3f90d7076cc71d5ae470c9fb1fc7db0`
- GuitarDuets `2b6c2d50e5cea17e96a3e8666f611292fc362aa7`
- EG-IPT `40312c628c55dc5d7e635f718ce99921b984430e`
- general corpus sweep `c962d14c94aac08858226166c712ad93ea651993`
- recent repository sweep `f5961fe28bda99721721f7fdcb5c0481c5ab80fb`
- multitrack sweep `fb3469695768ce572c2c8fce2d7bdc6c5711a9fb`
- rights/mirror frontier `23d55751561b7102e6e726a6adc8a419511e67dd`
- GAPS 2026 release reassessment `957b41b38c62baeab6e01b9d68487d97f44b5199`
- purpose-built option latest `dde8aa9cc97d8cbd9efbd06cc4d8c8b00d45fda4`
- 2026 literature frontier `ac6ac23f25c8f6f6c225464abc92b0988d064dd8`
- institutional/technique frontier `95eec317ead304b9e03a2139b72e15a9a4efeff8`
- reference hardware landscape `84b61b31dc0f4a23c7c182580632ab417879bb69`
- Geoff Bremner provenance `4e5e884da729ba7f6227f2d644544232ed312853`
- commercial guitar data frontier `764061d755d06d1a54b749a99016ce3207baf30e`
- purpose-built manifest chronology hardening `f7df06a0746bf78cf126c05d5c281375e8f2258d`
- chronology regression expansion `2e3199fa28b22debea95eb6a0c2cafcc6c1e7665`
- purpose-built synthetic CI harness `b9db9c5e50f181f53a812d0bc27a2ac4425a7701`
- corrected chronology regression expectation `7da490bc07314c5a831d819212184d97b3e3512d`
- purpose-built semantic guard `d08824ceba7dc8498a581d2387512bf612b22ea8`
- semantic guard synthetic tests `f7a3ea335aebd6a78c2cd5c2af7c775660728e16`
- combined base + semantic CI gate `20b4263dc37ab8556e6cd4f6b2f03e812c64cdf7`
- hardened purpose-built capture-plan binding `98619b94f0f0c2361fdf84583dcf398f9eaee1bc`
- capture-plan binding regression suite `73e19a312af066701130ff759718a739f4fb2936`
- synthetic frozen capture-plan fixture `31178d7eeb3908eb5b40782944ba3c0d383141c7`
- synthetic preregistration-evidence fixture `617706bc6a70c2b95d4ee6bd751cdc23bd76cfda`
- preregistration Git-proof validator `bba24857c78e6541961988e29712b68cdfcb7ce0`
- preregistration Git-proof regression suite `513113bdff971365038ed720d65ddd0c94fcabff`
- four-stage purpose-built CI gate `68dbea3dd97a53fb46e0d92aeab210f77f0b6231`
- Git preregistration timestamp normalization `10e3c4a3d5f5d9cad8f0683b6027342d002521e0`
- hosted preregistration attestation generator `fde97b60ee991d625b558af1ae1c6b6d6f7a40c0`
- hosted attestation regression suite `dcb693ee184a73ada76c2ee20777eaad9d8779fa`
- read-only hosted attestation workflow `933b20b1bd70761717645ab3c7c6b15b1721a7eb`
- GitHub server preregistration proof `120473870a3103cc08073320cda6830b5bf9bd85`
- GitHub server-proof regression suite `dbebaa49d4e76fc95f9d11845c21ad7a85ee2630`
- six-stage comprehensive purpose-built CI gate `c5b960d89554c8474cecc95505021873af2b5411`
- hosted preregistration server-attestation checkpoint `c4bdaba60f84032d64bb3e5a31c8d7ad998fd7df`

## CURRENT CANDIDATE STATUS

### AG-PT-set — REJECTED: AUDIO-DERIVED REFERENCE

Its precise onset reference is constructed from recorded audio: `aubioonset` candidate labels followed by musician inspection/correction/alignment using Audacity waveform + high-resolution Mel spectrogram; known note sequence/pitch and a pitch detector assist error correction. Excellent MIR annotation can still fail the frozen independence gate. Zenodo data-file rights are also unresolved for this use. Do not acquire/audit/score. Rights clearance alone cannot cure reference provenance.

### GAPS — REJECTED: AUDIO-DERIVED REFERENCE

Official 2026 Hugging Face v1.1 now includes audio and advertises an MIT dataset-card license, superseding the earlier narrow claim that no permissive-looking official distribution exists. However, the published GAPS construction method aligns GuitarPro scores to third-party YouTube performances using DTW and then fine-aligns note/chord timing to activations from an existing transcription model before manual verification/re-alignment/filtering. The emitted performance MIDI onset timing is therefore materially reconstructed from the evaluated audio, not an independent performed reference stream. Dedicated reassessment `957b41b38c62baeab6e01b9d68487d97f44b5199`. Third-party recording rights are also not established to the frozen product-validation standard by the repository-level MIT tag alone. Reject; do not acquire/audit/score. Licensing clarification cannot cure the reference-provenance failure.

### EGSet12 — NOT UNTOUCHED

21 matching pre-search commits among 7,662 reachable commits. Reject; do not rewrite history.

### IDMT-SMT-Audio-Effects / GUITAR-FX-DIST — RIGHTS BLOCKED

CC BY-NC-ND 4.0. Reject.

### EG-Solo / G&N / TENT — RECORDING RIGHTS BLOCKED

Third-party/professional YouTube/popular-song or commercial textbook-CD sources. Reject.

### EG-IPT — REFERENCE + RIGHTS FAIL

52,320 real electric-guitar files / >28 h / DI, but no released independent performed note stream and no explicit permissive media rights. Reject before media access.

### Multimodal Electric Guitar Data — RIGHTS CLEANER, REFERENCE INSUFFICIENT

Zenodo `6470235/6470236`, ~32.5 GB, 36 real guitarists, CC BY 4.0; actions/EMG/MoCap/audio, not immutable performed note-level onset+pitch truth. Not audit-ready.

### MMIP — RIGHTS + REFERENCE FAIL

CC BY-NC-SA; guitar MIDI produced post-recording via Ableton audio-to-MIDI. Reject.

### GIHME — RELEASE NEVER MATERIALIZED

~10 h described in paper, but public release remains placeholder without complete corpus/checksums/license. Reject/not audit-ready.

### EGFxSet — NARROW BACKUP

~690 unique clean real electric-guitar performances, CC BY 4.0, but no established high-resolution independent performed onset reference. Effect variants cannot inflate evidence.

### EGDB / EGDB-PG — RIGHTS + AUDIO-DERIVED ONSET FAIL

Real DI, but rights unestablished and onset reference materially derived from recorded DI/expected score timing. Reject.

### GuitarDuets — REAL SUBSET LACKS NOTE TRUTH

Note-level MIDI exists for synthesized duets, not an immutable performed reference for real duets. Reject.

### Geoff Bremner Multimodal Music Corpus — PRIVATE-LICENSE LEAD ONLY

Public sample has original single-rightsholder material, real stems, one arrangement-level MIDI, Guitar Pro, PDFs and Ableton project, plus separately offered commercial licensing. Public text does not establish that guitar MIDI was captured simultaneously from guitar performances, that MIDI onset times are performed attacks, exact guitar-stem/MIDI mapping, full-corpus volume or clock semantics. Dedicated review `4e5e884da729ba7f6227f2d644544232ed312853`.

Keep metadata-only. Do not contact/acquire yet. If MIDI is authored/quantized score, Guitar Pro/DAW export, post-hoc transcription or audio-derived, reject even if licensing is available.

### GRAUX / Water commercial guitar packs — REJECTED BEFORE PURCHASE

Commercial frontier checkpoint `764061d755d06d1a54b749a99016ce3207baf30e`.

GRAUX offers live-recorded guitar WAV/stems plus MIDI and a clear named rightsholder, but its product material explicitly describes companion MIDI as **bass notes and chords**, not an independently captured per-note performed stream. Public license is a music-production incorporation license, non-transferable and restrictive on raw redistribution/sublicensing; it does not clearly grant validation-corpus use. Do not purchase/download/contact for V6 under the current metadata phase.

### Other rejected/not-audit-ready leads

- GPT/Su 2014: inaccessible/unverifiable release/terms.
- robot/isolated chord datasets: chord labels only.
- NSynth / Slakh2100: synthetic sampler/VST audio.
- URMP: no guitar.
- GuitarJam: clean CC0 DI, no note truth.
- `guitar-fretboard-notes`: 390 notes, no independent onset, inadequate capacity.
- Semantic Timbre: EGFxSet effect derivative.
- `guitar-chord-mix`: derivative mixture of exposed/ineligible sources.
- MedleyDB / MUSDB18 / MoisesDB: rights/reference semantics fail.
- UT Austin/Kaggle guitar dataset: NC-SA + frame/fret labels, not independent note truth.
- MagCIL `guitar_style_dataset`: 549 technique recordings + MuseScore exercises; no independent performed note truth; software MIT license does not establish media rights.
- University of Manchester/NOVARS: 61.93 GB / 21 guitarists, but published capture is audio/video/Myo, not independent note MIDI/onsets; performance data not released for this purpose.
- targeted Mendeley/Figshare collections: too small/narrow and/or lack independent onset truth.
- Selekt guitar stems: rights-oriented real stems, but no independent note reference.

## 2026 / PUBLIC FRONTIER

TART reuses GuitarSet/EGDB/noisy derivatives. Playability-Aware/Noise2Fret uses GuitarSet + GOAT; **GOAT remains archived and is not reopened**. EG-VAE does not expose a qualifying reference corpus. Alternate-tuning work reviewed is synthetic/VST. Generic repositories, current literature, institutional technique data and commercial loop libraries have not surfaced a qualifying replacement.

This is an evidence-bounded near-exhaustion result, not proof that none exists.

## PURPOSE-BUILT UNTOUCHED HOLDOUT — DESIGN ONLY

Design checkpoint latest `dde8aa9cc97d8cbd9efbd06cc4d8c8b00d45fda4`; hardware landscape `84b61b31dc0f4a23c7c182580632ab417879bb69`.

Strongest surfaced architecture:
- real guitar;
- conventional clean magnetic DI = evaluated signal;
- separate physical fret-position sensing for pitch identity + independent trigger/dynamics sensing;
- feasibility example only: Industrial Radio Fretsense / Solange 6.

Fretsense still does not provide infallible onset truth: piezo trigger/filter/decay settings matter. Any future capture must use a preregistered non-holdout calibration phase, then frozen/hashed hardware/firmware/settings/geometry; raw MIDI must pass a zero-anomaly reference-blind structural audit. Current product availability/lead time is unproven. Do not contact/order.

Jamstik/Fishman-style hexaphonic pitch-to-MIDI is weaker because reference events come from real-time pitch detection and can miss/add notes; Fishman currently documents pitch-detection latency around 7–14 ms. Digital smart/controller guitars fail the conventional real-guitar DI requirement. Piezo-audio smart systems do not supply independent note truth.

Purpose-built material must be original/public-domain/rightscleared, explicitly licensed for product validation, collected with zero model access/no model-informed retakes, raw reference preservation and frozen QA. Provisional >=20,000 raw-reference notes / multi-player collection remains planning only; frozen >=1,000 V6-positive gate remains authoritative.

No purchase, deposit, contact, hiring, recording or data acquisition without explicit user authorization.

### Purpose-built capture declaration + preregistration contract — SIX-STAGE SYNTHETIC CI PASS

Mandatory governance chain for any future purpose-built capture:
1. base reference-blind manifest validator `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v1.py`;
2. semantic guard `scripts/songsterr-fresh/purpose_built_capture_manifest_semantic_guard_v1.py`;
3. content-only capture-plan binding `scripts/songsterr-fresh/purpose_built_capture_preregistration_binding_v1.py`;
4. local Git-history preregistration proof `scripts/songsterr-fresh/purpose_built_capture_preregistration_git_proof_v1.py`;
5. deliberate read-only GitHub-hosted preregistration attestation using `.github/workflows/songsterr-purpose-built-preregistration-attestation.yml` and `purpose_built_capture_preregistration_attestation_v1.py`;
6. GitHub-server proof `scripts/songsterr-fresh/purpose_built_capture_preregistration_server_proof_v1.py`.

Chronology hardening commit `f7df06a0746bf78cf126c05d5c281375e8f2258d` requires timezone-aware UTC capture timestamps, contiguous attempt numbers beginning at 1 within each slot, and strictly increasing capture times consistent with attempt-number order. Regression commit `2e3199fa28b22debea95eb6a0c2cafcc6c1e7665` covers non-UTC offsets, naive timestamps, accepted `+00:00`, numbering gaps, reversed chronology and equal timestamps. CI run `34791117386` failed only because a regression expected a different error-string rendering; correction commit `7da490bc07314c5a831d819212184d97b3e3512d` then passed run `34791164882`, job `103815530838`.

Semantic guard commit `d08824ceba7dc8498a581d2387512bf612b22ea8` closes retry identity mutation (`playerId`/`exerciseId`/`category`) and identical evaluated/reference hardware path-ID loopholes; tests commit `f7a3ea335aebd6a78c2cd5c2af7c775660728e16`. Combined run `34791310019`, job `103815933282`, passed base + semantic markers.

Capture-plan hardening commit `98619b94f0f0c2361fdf84583dcf398f9eaee1bc` requires exact planned-slot coverage, exactly one admitted transport-valid take per slot, an exact frozen failure-reason vocabulary, and frozen criteria for each selected failure class. Allowed objective design classes are `ABSENT_REFERENCE_CHANNEL`, `CLIPPING_LIMIT_EXCEEDED`, `DEVICE_DISCONNECT`, `MALFORMED_MIDI_STREAM`, `MISSING_OR_CORRUPT_FILE`, `TRANSPORT_FAILURE`, and `WRONG_SAMPLE_RATE_OR_FORMAT`; subjective/model-informed retake reasons are invalid. Regression update `73e19a312af066701130ff759718a739f4fb2936` passed run `34792351488`, job `103818805869`.

The first plan-binding draft was superseded because including a future Git preregistration commit inside the plan whose hash helps define that commit is circular. The corrected plan is content-only. Synthetic plan fixture commit `31178d7eeb3908eb5b40782944ba3c0d383141c7` has canonical JSON SHA256 `695e2c8ff1e383ed8d7d5fee8c4549a507b2b8f14058353ae6d6f00155532d35`; separate evidence commit `617706bc6a70c2b95d4ee6bd751cdc23bd76cfda` binds the plan path + SHA.

Git-proof commit `bba24857c78e6541961988e29712b68cdfcb7ce0` verifies the prereg commit exists and is ancestral, the exact plan/evidence exist there, and capture timestamps postdate the commit. Initial four-stage run `34792462528`, job `103819128558`, failed only because Git's valid `-04:00` committer timestamp was fed to the capture manifest's intentionally UTC-only parser. Commit `10e3c4a3d5f5d9cad8f0683b6027342d002521e0` normalizes any timezone-aware Git timestamp to UTC without weakening the capture timestamp rule. Run `34792551012`, job `103819374190`, then passed all four local layers.

Git commit times are self-authored metadata, so the four-stage local proof is no longer sufficient by itself for a future real capture. Hosted attestation generator `fde97b60ee991d625b558af1ae1c6b6d6f7a40c0`, tests `dcb693ee184a73ada76c2ee20777eaad9d8779fa`, and read-only workflow `933b20b1bd70761717645ab3c7c6b15b1721a7eb` add a GitHub-hosted timestamp boundary. A `push` run is synthetic CI only; **only `workflow_dispatch` is eligible for a future real preregistration**.

Synthetic hosted run `34792723781`, job `103819867260`, completed `success`, emitted `PURPOSE_BUILT_PREREGISTRATION_ATTESTATION_V1_SYNTHETIC_TESTS_OK` + `PURPOSE_BUILT_PREREGISTRATION_ATTESTATION_V1_OK`, and uploaded artifact `10328593887` (Actions-reported artifact ZIP SHA256 `bdc09570e3ef74b5fe3ca9a0f05b927b284a4c930480924bd70432215eba8a26`). Its event was `push`, so it is explicitly **not** a real capture preregistration.

Server proof commit `120473870a3103cc08073320cda6830b5bf9bd85` with tests `dbebaa49d4e76fc95f9d11845c21ad7a85ee2630` requires a cited Actions run to match repository/run ID/workflow/head branch, be `workflow_dispatch`, finish successfully, descend from the frozen prereg commit, retain the exact plan/evidence at its head, and have GitHub `created_at`/`run_started_at`/`updated_at` all valid. Every capture timestamp must be strictly later than the latest server timestamp, so the hosted run must have completed before recording. Detailed checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_PREREGISTRATION_SERVER_ATTESTATION_2026-09-13.md`, commit `c4bdaba60f84032d64bb3e5a31c8d7ad998fd7df`.

Comprehensive CI commit `c5b960d89554c8474cecc95505021873af2b5411` runs six synthetic stages with full Git history. Run `34792825257`, job `103820159787`, completed `success` and emitted all six markers:
- `PURPOSE_BUILT_CAPTURE_MANIFEST_CONTRACT_V1_SYNTHETIC_TESTS_OK`
- `PURPOSE_BUILT_CAPTURE_MANIFEST_SEMANTIC_GUARD_V1_SYNTHETIC_TESTS_OK`
- `PURPOSE_BUILT_CAPTURE_PREREGISTRATION_BINDING_V1_SYNTHETIC_TESTS_OK`
- `PURPOSE_BUILT_CAPTURE_PREREGISTRATION_GIT_PROOF_V1_SYNTHETIC_TESTS_OK`
- `PURPOSE_BUILT_PREREGISTRATION_ATTESTATION_V1_SYNTHETIC_TESTS_OK`
- `PURPOSE_BUILT_PREREGISTRATION_SERVER_PROOF_V1_SYNTHETIC_TESTS_OK`

For a future purpose-built population, all declaration/preregistration layers must pass before any raw-byte reference-blind structural audit. A real hosted preregistration must be deliberately dispatched and completed **before capture**. Even after successful server proof, only `mayAdvanceToReferenceBlindStructuralAudit:true` is possible; `authoritativeStructuralSuitabilityEstablished:false`, `basicPitchAuthorized:false`, `v6Authorized:false`, and `correctnessAuthorized:false` remain frozen until their separate gates. The synthetic PASS proves governance/tool behavior only, not real-corpus suitability, reference truth, model validity, correctness, or delivery eligibility. No real holdout audio/reference bytes were accessed and no correctness was computed.

## NEXT ALLOWED ACTION

1. Metadata-only research where genuinely new information may still exist: private/rightsholder corpora, future institutional independent-sensor releases, or purpose-built protocol/hardware design.
2. Do not pursue AG-PT-set under current audio-derived reference.
3. Keep Geoff Bremner metadata-only unless authoritative documentation resolves performed MIDI provenance; do not contact/acquire yet.
4. Keep Multimodal Electric Guitar Data and EGFxSet as reference-insufficient backups.
5. Purpose-built protocol/preregistration and synthetic contract tooling may continue on paper/ordinary GitHub CPU; no procurement/contact/capture without explicit user authorization.
6. Any selected existing corpus must pass all gates before media access and receive corpus-specific reference-blind preregistration first.
7. Any future purpose-built capture must freeze the exact content-only plan + separate Git evidence, then complete a successful `workflow_dispatch` hosted preregistration before recording, and finally pass the server proof before raw-byte structural audit.
8. If a structural audit eventually passes, bind identities, run no-real-correctness harness CI, then exactly one ordinary-GitHub-CPU correctness run.
9. Ask the user before Modal/Vercel heavy-GPU/L4 or any purpose-built spending/contact/acquisition.

## STILL FORBIDDEN

- Guitar-TECHS correctness/repair/rescue;
- AG-PT-set V6 acquisition/audit/scoring under current audio-derived reference;
- GAPS V6 acquisition/audit/scoring under current audio-derived reference;
- EGSet12 history rewriting/scoring;
- NC/ND or otherwise restricted corpus use outside rights;
- rescue via evaluated-audio-derived/reconstructed truth;
- counting synthetic/effect/duplicate/derivative files as independent real evidence;
- reopening GOAT/reference scoring due to literature mentions;
- V5 FLGD rerun/tuning or use of revealed holdout/protected-song correctness to tune V6;
- changing frozen V6/scoring rules from holdout observations;
- protected-song execution;
- duration research;
- archived V143/Gomyway or GOAT/reference scoring;
- real-corpus optimizer/threshold sweeps or fine-tuning on proposed admission holdouts;
- treating vendor MIDI as infallible truth;
- purpose-built calibration on admitted holdout/model outcomes;
- purpose-built procurement/contact/hiring/recording/acquisition without explicit authorization;
- Production/customer promotion without untouched external validation + separate policy review;
- Modal/Vercel heavy-GPU/L4 without explicit user authorization.

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1`; read this file first. V6 method/scoring remain frozen and no replacement-holdout correctness has been exposed. Guitar-TECHS is closed outcome C before correctness. AG-PT-set and GAPS are rejected because their precise performance timing is materially reconstructed from evaluated audio; licensing changes cannot cure reference provenance. Public/institutional/commercial corpus searches remain near exhausted. Purpose-built independent-sensor capture is the strongest remaining design route, but remains design-only and requires explicit user authorization before contact/spending/recording. Purpose-built governance now requires six layers: base manifest contract, semantic guard, content-only capture-plan binding, local Git-history proof, deliberate GitHub-hosted `workflow_dispatch` preregistration, and GitHub-server proof that the hosted run completed before every capture timestamp. Comprehensive synthetic run `34792825257` / job `103820159787` is green. Do not treat synthetic/hosted CI as real-corpus suitability or model validation. Do not reopen archived V143/Gomyway or GOAT/reference scoring unless explicitly asked.
