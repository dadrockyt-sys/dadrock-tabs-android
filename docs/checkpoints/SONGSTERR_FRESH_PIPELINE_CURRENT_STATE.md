# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 America/Toronto
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
Artifact remains live/unexpired as of 2026-09-14; GitHub-reported archive digest `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`, run head `f3c9d4a88740146918c34a3538c565f21079f3bf`.
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

## REPLACEMENT CORPUS STATUS

- **AG-PT-set — REJECTED: AUDIO-DERIVED REFERENCE.** Precise onset reference is constructed from recorded audio (`aubioonset` candidates + musician correction/alignment using waveform/spectrogram; pitch/known-note aids). Rights were also unresolved. Rights clearance cannot cure provenance.
- **GAPS — REJECTED: AUDIO-DERIVED REFERENCE.** Official 2026 HF v1.1 now exposes audio with an MIT dataset-card tag, but the published construction aligns GuitarPro scores to third-party YouTube performances with DTW and transcription-model activations followed by manual verification/re-alignment/filtering. Performance timing is materially reconstructed from evaluated audio. Third-party recording rights also remain unproven to the frozen product-validation standard. Dedicated reassessment `957b41b38c62baeab6e01b9d68487d97f44b5199`.
- **François Leduc Guitar Dataset (FLGD) — REJECTED: AUDIO/MODEL-DERIVED PERFORMANCE TIMING.** Real solo-guitar audio is paired with high-resolution MIDI, but the ICASSP 2024 method aligns commercial GuitarPro scores to transcription-model activations on the evaluated audio and fine-aligns note timing to activation peaks. The performed onset stream is therefore reconstructed from evaluated audio/model activations, failing frozen gate 3. The newer HF card says MIT, while the original Zenodo release was research-restricted and required separate non-research score permission; rights ambiguity is secondary because provenance already fails. Dedicated review checkpoint `docs/checkpoints/SONGSTERR_FRESH_FRANCOIS_LEDUC_DATASET_METADATA_REFERENCE_REVIEW_2026-09-14.md`, commit `fa99798f4c2b08842f534533ea51d84ae9b2a967`.
- **EGSet12 — NOT UNTOUCHED.** 21 matching pre-search commits among 7,662 reachable commits. Reject; do not rewrite history.
- **IDMT-SMT-Audio-Effects / GUITAR-FX-DIST — RIGHTS BLOCKED.** CC BY-NC-ND 4.0.
- **EG-Solo / G&N / TENT — RECORDING RIGHTS BLOCKED.** Third-party/professional YouTube/popular-song or commercial textbook-CD sources.
- **EG-IPT — REFERENCE + RIGHTS FAIL.** 52,320 real electric-guitar files / >28 h / DI, but no released independent performed note stream and no explicit permissive media rights.
- **Multimodal Electric Guitar Data — RIGHTS CLEANER, REFERENCE INSUFFICIENT.** Zenodo `6470235/6470236`, ~32.5 GB, 36 real guitarists, CC BY 4.0; actions/EMG/MoCap/audio, not immutable performed note-level onset+pitch truth.
- **MMIP — RIGHTS + REFERENCE FAIL.** CC BY-NC-SA; guitar MIDI produced post-recording via Ableton audio-to-MIDI.
- **GIHME — PUBLIC CORPUS STILL NOT MATERIALIZED.** Fresh 2026-09-14 primary-source recheck confirms Zenodo `6798338` still exposes only conference paper `79.pdf` (680.6 kB, MD5 `3165bf69606999426fc803c7d3f548c3`) despite describing ~10 h of annotated hexaphonic-guitar improvisations. No authoritative audio/annotation corpus archive, package manifest or immutable corpus identities are publicly exposed. Dedicated recheck `docs/checkpoints/SONGSTERR_FRESH_GIHME_PUBLIC_RELEASE_RECHECK_2026-09-14.md`, commit `6dcdeeba53e2a6b0433f77c3a36a0a9d6c446eb8`.
- **MUSMET — RIGHTS + REFERENCE FAIL.** 2025 Horizon-Europe release has real electric-guitar ensemble audio synchronized with EEG, but the authoritative release describes audio+EEG rather than an independent performed guitar note-event stream, and its Rights field exposes consortium copyright without an explicit permissive performance-audio license. Dedicated review `dea3b9682cad4661eedad96a5e7ee3599dd89af9`.
- **Klangio GST-MM-2025 — REFERENCE GRANULARITY + AUDIO-DERIVED ONSET + RIGHTS FAIL.** 90 minutes of real acoustic-guitar microphone/pickup recordings with ESP32 motion data, but released supervision is strum-direction/chord labeling rather than independent performed per-note onset+pitch truth; annotation explicitly combines spectral-flux onset detection from recorded audio with motion/recording-plan information. Public Apache-2.0 statement covers software, not clearly the performance-audio dataset. Dedicated review `b77bf09259aaf122b60f778921abca110633f4a8`.
- **EGFxSet — NARROW BACKUP ONLY.** ~690 unique clean real electric-guitar performances, CC BY 4.0, but no established high-resolution independent performed onset reference. Effects cannot inflate evidence.
- **EGDB / EGDB-PG — RIGHTS + AUDIO-DERIVED ONSET FAIL.** Real DI, but rights unestablished and onset reference materially derived from recorded DI/expected score timing.
- **GuitarDuets — REAL SUBSET LACKS NOTE TRUTH.** Note-level MIDI applies to synthesized duets, not an immutable performed reference for real duets.
- **DoMP — REJECTED: AUTHORITATIVE PUBLIC RELEASE LACKS EVALUATED AUDIO.** The Audio Mostly 2024 paper describes live electric-guitar performances captured with a Fishman TriplePlay MIDI tracker and says MIDI+audio exist; Zenodo record `10818617` is CC BY 4.0. But the authoritative deposit exposes only `DoMP.zip` (2.7 MB, MD5 `c5f0e2b10eae47435f409930a4fa94ae`), and its archive preview shows `.mid` files with no WAV/FLAC/MP3/AIFF/M4A entries. There is therefore no released real-guitar audio population to pair with the MIDI for V6 scoring. Dedicated review `docs/checkpoints/SONGSTERR_FRESH_DOMP_METADATA_RELEASE_REVIEW_2026-09-14.md`, commit `4ed022234695996d2b491863918ee1f6909ae1a7`.
- **Geoff Bremner Multimodal Music Corpus — PRIVATE-LICENSE LEAD ONLY.** Public sample has original single-rightsholder material, real stems, arrangement MIDI/Guitar Pro/PDF/Ableton and commercial licensing, but public metadata does not establish simultaneously captured performed guitar MIDI, onset semantics, exact guitar-stem mapping, full-corpus volume or clock semantics. Dedicated review `4e5e884da729ba7f6227f2d644544232ed312853`. Keep metadata-only; no contact/acquisition.
- **GRAUX / Water commercial packs — REJECTED BEFORE PURCHASE.** Live guitar WAV/stems exist, but companion MIDI is described as bass notes/chords, not independent performed per-note truth; public license is music-production oriented. Dedicated review `764061d755d06d1a54b749a99016ce3207baf30e`.
- **2025–2026 recent primary-source delta sweep — NO NEW ADMISSIBLE CANDIDATE.** Fresh literature/release search found only already-governed Guitar-TECHS, Klangio GST-MM-2025, GAPS, GuitarDuets, archived GOAT, and synthesized-only leads; no new corpus cleared all five pre-media gates. Checkpoint `docs/checkpoints/SONGSTERR_FRESH_V6_RECENT_CORPUS_DELTA_SWEEP_2026-09-14.md`, commit `393e2769d007ed88f1dca61a8403cd54ee4e8001`.
- Other non-qualifying leads remain: GPT/Su 2014, robot/isolated chord sets, NSynth, Slakh2100, URMP, GuitarJam, `guitar-fretboard-notes`, Semantic Timbre, `guitar-chord-mix`, MedleyDB, MUSDB18, MoisesDB, UT Austin/Kaggle, MagCIL guitar_style_dataset, Manchester/NOVARS, Mendeley/Figshare leads, Selekt stems.

Public/institutional/commercial search is near exhausted but this is not proof that no qualifying corpus exists.

## PURPOSE-BUILT UNTOUCHED HOLDOUT — DESIGN ONLY

Design checkpoint latest `dde8aa9cc97d8cbd9efbd06cc4d8c8b00d45fda4`; hardware landscape `84b61b31dc0f4a23c7c182580632ab417879bb69`.

Strongest surfaced architecture remains:
- real guitar;
- conventional clean magnetic DI = evaluated signal;
- separate physical fret-position sensing for pitch identity + independent trigger/dynamics sensing;
- feasibility example only: Industrial Radio Fretsense / Solange 6.

Fretsense-style reference still requires preregistered non-holdout calibration and frozen/hashed hardware/firmware/settings/geometry; raw MIDI must pass a zero-anomaly reference-blind structural audit. Jamstik/Fishman-style pitch-to-MIDI is weaker because the reference itself depends on pitch detection. No purchase, contact, hiring, recording or data acquisition without explicit user authorization.

Purpose-built material must be original/public-domain/rightscleared, explicitly licensed for product validation, collected with zero model access/no model-informed retakes, raw reference preservation and frozen objective QA. Provisional >=20,000 raw-reference notes / multi-player collection remains planning only; frozen >=1,000 V6-positive gate remains authoritative.

## PURPOSE-BUILT GOVERNANCE — EIGHT-STAGE SYNTHETIC CI PASS

Any future purpose-built real capture must pass **all eight** governance layers; none authorizes correctness:

1. `purpose_built_capture_manifest_contract_v1.py` — base reference-blind manifest contract.
2. `purpose_built_capture_manifest_semantic_guard_v1.py` — freezes retry player/exercise/category identity and requires distinct declared evaluated/reference hardware path IDs.
3. `purpose_built_capture_preregistration_binding_v1.py` — binds exact content-only capture plan, slots, failure vocabulary and criteria.
4. `purpose_built_capture_preregistration_git_proof_v1.py` — proves plan/evidence existed in ancestral Git history before capture timestamps.
5. `purpose_built_capture_preregistration_attestation_v1.py` + dedicated Actions workflow — read-only GitHub-hosted attestation; only deliberate `workflow_dispatch` can count for real preregistration.
6. `purpose_built_capture_preregistration_server_proof_v1.py` — verifies GitHub run identity/status/event/head/ancestry, historical plan/evidence continuity and server timestamps before every capture.
7. `purpose_built_capture_preregistration_server_integrity_guard_v1.py` — pins the attestation run head to the exact hardened workflow blob `b8b5bd78abad1aa0cfa0cf3be9d4c8ab31ed178f` and exact hardened attestation-generator blob `9172762fd86077701c20b77655f82e9307f00c5d`; merely descending from the hardening commit is not enough.
8. `purpose_built_capture_preregistration_artifact_proof_v1.py` — requires the exact run artifact `purpose-built-preregistration-attestation-<run_id>` to be present/unexpired, parse as the real preregistration attestation, and bind the exact manifest capture-plan path + SHA, run ID/attempt, head SHA, repository, workflow ref and `real_preregistration` mode. This prevents reusing a successful run that actually attested a different plan.

Important history:
- chronology hardening `f7df06a0746bf78cf126c05d5c281375e8f2258d`; chronology regressions `2e3199fa28b22debea95eb6a0c2cafcc6c1e7665`; corrected expectation `7da490bc07314c5a831d819212184d97b3e3512d`;
- semantic guard `d08824ceba7dc8498a581d2387512bf612b22ea8`; semantic tests `f7a3ea335aebd6a78c2cd5c2af7c775660728e16`;
- capture-plan hardening `98619b94f0f0c2361fdf84583dcf398f9eaee1bc`; binding regressions `73e19a312af066701130ff759718a739f4fb2936`;
- synthetic plan fixture `31178d7eeb3908eb5b40782944ba3c0d383141c7`, canonical JSON SHA256 `695e2c8ff1e383ed8d7d5fee8c4549a507b2b8f14058353ae6d6f00155532d35`; evidence fixture `617706bc6a70c2b95d4ee6bd751cdc23bd76cfda`;
- Git proof `bba24857c78e6541961988e29712b68cdfcb7ce0`; Git timestamp normalization `10e3c4a3d5f5d9cad8f0683b6027342d002521e0`;
- hosted attestation generator `fde97b60ee991d625b558af1ae1c6b6d6f7a40c0`; tests `dcb693ee184a73ada76c2ee20777eaad9d8779fa`; workflow `933b20b1bd70761717645ab3c7c6b15b1721a7eb`; hardened real-mode minimum commit `e3d90f275dc92e1d705bf7db78f0b4d6622a324a`;
- server proof `120473870a3103cc08073320cda6830b5bf9bd85`; tests `dbebaa49d4e76fc95f9d11845c21ad7a85ee2630`; server-attestation checkpoint `c4bdaba60f84032d64bb3e5a31c8d7ad998fd7df`;
- hardened real-mode server-proof regression head `090312826608f56b617199e9e88e0e5e7ae2a0e6`, CI run `34793151891` success;
- server integrity guard `20718d125ab3ed6a2c6ef4ee92d63e647fae8e88`; tests `bb339750c2c0a19e33eba9e510e18120c9d83b17`; seven-stage CI gate `ae59b264dd823ebc13bb6c671fc11507b96fdd07`, run `34793892204`, job `103823162095`, success;
- hosted artifact proof `fbeb1c22b03851061fc47be5b0f63c6b0f0cdb92`; tests `065dba46dcac975fa8876a4e4947162c0cee8dcf`; eight-stage CI gate `df69b6b55e197d228736aa7910cd9ca30677f9f5`, run `34793985984`, job `103823432519`, success. All eight synthetic test steps passed.
- hosted artifact-proof production trust-boundary audit checkpoint `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_ARTIFACT_PROOF_TRUST_BOUNDARY_AUDIT_2026-09-13.md`, commit `2456945a1c270842594010b7c3ffde423f68adb7`: **PASS, no concrete gap and no code change justified**. Production fetches exact cited-run metadata/artifact listing and downloads exact artifact bytes from GitHub before validation; caller-supplied artifact objects exist only in the pure helper/test boundary.

Earlier synthetic hosted attestation run `34792723781` / job `103819867260` was a `push` event and is **not** a real capture preregistration. It remains synthetic evidence only.

For a future real population, successful eight-stage governance can only establish `mayAdvanceToReferenceBlindStructuralAudit:true`. It does **not** establish source truth, structural suitability, Basic Pitch authorization, V6 authorization, correctness authorization, model validation, customer eligibility or delivery advancement.

## NEXT ALLOWED ACTION — FRESH CHAT ORDER

1. **Start by verifying the branch head and reading this checkpoint in full.** Work only on `songsterr-fresh-pipeline-v1`; if the branch advanced, merge/continue from the newer state rather than overwriting it.
2. **Artifact-proof trust boundary is closed unless new evidence demonstrates a concrete loophole.** Do not add governance layers merely for duplication. Keep existing eight-stage CI synthetic-only.
3. **Continue metadata-only replacement-corpus research only when there is genuinely new evidence** (new primary release, authoritative rights change, or independent performed onset+pitch reference). Do not re-screen closed candidates from mirrors or derivative releases unless a hard gate materially changes.
4. **If a new existing corpus clears all five pre-media gates**, stop before media access and first freeze a corpus-specific reference-blind inventory/alignment preregistration. Structural audit comes before Basic Pitch/V6/correctness.
5. **If purpose-built capture remains the only viable route**, keep hardware/protocol/calibration design on paper. Do not contact vendors/performers, spend money, procure hardware, hire, or record until the user explicitly authorizes it. After authorization, freeze exact real plan + evidence, verify hardened blobs, deliberately run the real hosted preregistration, preserve its exact artifact, pass server/integrity/artifact proof, and only then record.
6. **After any future structural audit passes**, bind immutable population identities, run no-real-correctness harness CI, then perform exactly one ordinary-GitHub-CPU correctness run under the frozen V6/scoring framework. Never tune from that result.
7. Ask the user before Modal, Vercel heavy-GPU, L4 GPU, or any purpose-built spending/contact/acquisition. No question is needed for ordinary metadata research, coding, synthetic tests, GitHub CPU CI, or checkpoint maintenance.

## STILL FORBIDDEN

- Guitar-TECHS correctness/repair/rescue;
- AG-PT-set or GAPS acquisition/audit/scoring under current audio-derived references;
- EGSet12 history rewriting/scoring;
- NC/ND or otherwise restricted corpus use outside rights;
- rescue via evaluated-audio-derived/reconstructed truth;
- counting synthetic/effect/duplicate/derivative files as independent real evidence;
- reopening GOAT/reference scoring due to literature mentions;
- V5 FLGD rerun/tuning or revealed-holdout/protected-song tuning of V6;
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

Continue only on `songsterr-fresh-pipeline-v1`; **first verify the live branch head, then read this file before doing anything else**. The hosted artifact-proof production trust-boundary audit is complete and passed without code changes; do not reopen it absent a concrete newly discovered loophole.

V6 method/scoring remain frozen and no replacement-holdout correctness has been exposed. Guitar-TECHS is closed outcome C before correctness. AG-PT-set, GAPS and François Leduc are rejected because precise performance timing is materially reconstructed from evaluated audio/model activations; licensing changes cannot cure reference provenance. GIHME has been freshly rechecked and still has no public corpus package behind its ten-hour dataset description. DoMP has now been checked as a potentially stronger live-performance/MIDI-tracker lead, but its authoritative Zenodo release contains only the small MIDI archive and no released evaluated audio. Public/institutional/commercial corpus searches remain near exhausted; the 2026-09-14 recent primary-source delta sweep found no new corpus clearing all five pre-media gates. Purpose-built independent-sensor capture is the strongest remaining design route, but remains design-only and requires explicit user authorization before contact/spending/recording.

Purpose-built governance currently requires eight layers: base manifest, semantic guard, content-only plan binding, local Git-history proof, deliberate GitHub-hosted `workflow_dispatch` attestation, GitHub server proof, exact hardened workflow/generator blob integrity, and exact hosted attestation-artifact binding to the plan. Latest eight-stage synthetic run `34793985984` / job `103823432519` is green. Production artifact proof has now been audited and confirmed to obtain artifact metadata/content from the cited GitHub run rather than trusting caller-supplied artifact JSON.

Do not treat synthetic CI, GitHub timestamps, or hosted artifacts as real-corpus suitability or model validation. No real media, Basic Pitch, V6, or correctness may be touched until the separate gates say so. Do not reopen archived V143/Gomyway or GOAT/reference scoring unless explicitly asked.