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

Frozen essentials: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; preserve every decoded event and selected integer MIDI exactly once; isolated-guitar DI evaluation path; one-to-one within-performance match onset <= `0.050 s`, pitch <= `50 cents`; V6-positive precision with one-sided 95% Wilson LB; >=`1,000` pooled V6-positive estimates; pooled Wilson LB >=`0.9900`; player/category strata with >=100 positives require point precision >=`0.9500`; frozen categories `chords`, `scales`, `singlenotes`, `techniques`, `music`; deferred correctness reveal and exactly one official correctness run.

Do not alter method/runtime/settings/matching/tolerances/gates/strata from holdout observations.

## GUITAR-TECHS — CLOSED OUTCOME C BEFORE CORRECTNESS

Result checkpoint `docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`, commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.
Official audit run `34754519541`, job `103716527380`, exact artifact `guitar-techs-v6-alignment-inventory`, artifact ID `10317695640`.
Reverified 2026-09-14: job remains completed/successful; artifact remains live/unexpired; GitHub-reported archive digest `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`; run head `f3c9d4a88740146918c34a3538c565f21079f3bf`. Artifact ZIP was downloaded again and independently SHA-256 checked to the same digest; merged JSON SHA-256 remains `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`.
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

If all five clear, freeze corpus-specific reference-blind inventory/alignment preregistration before media access; structural audit first; reject unsuitable data without correctness. Only after a structural pass may immutable population identities be bound, controlled synthetic/contract-only harness CI run, and exactly one ordinary-GitHub-CPU external correctness run occur. No tuning/rerun after correctness exposure.

## REPLACEMENT CORPUS STATUS

- **Guitar-TECHS — CLOSED C.** Structural zero-anomaly gate failed before correctness.
- **AG-PT-set — REJECTED.** Precise onset reference is audio-derived (`aubioonset` + waveform/spectrogram correction/alignment); rights unresolved.
- **GAPS — REJECTED; v1.1 DELTA REVIEWED.** The newer Hugging Face v1.1 release now includes audio and declares `license: mit`, but the paper still constructs performed timing from evaluated audio using DTW plus closest transcription-model activations, manual downbeat intervention, re-alignment, and model-agreement filtering. The recordings originate from 205 YouTube performers and the reviewed public materials do not establish a track-by-track product-validation rights chain. The release delta therefore does not cure the decisive independent-reference failure. Checkpoint `docs/checkpoints/SONGSTERR_FRESH_GAPS_V1_1_RELEASE_DELTA_REVIEW_2026-09-14.md`, commit `7a6ebe309cfe17067990433ed88e58f5ef68ba48`.
- **François Leduc Guitar Dataset (FLGD) — REJECTED.** Performance timing aligned/fine-aligned using transcription-model activations from evaluated audio. Checkpoint `docs/checkpoints/SONGSTERR_FRESH_FRANCOIS_LEDUC_DATASET_METADATA_REFERENCE_REVIEW_2026-09-14.md`, commit `fa99798f4c2b08842f534533ea51d84ae9b2a967`.
- **EGSet12 — NOT UNTOUCHED.** Reject; do not rewrite history.
- **IDMT-SMT-Audio-Effects / GUITAR-FX-DIST — RIGHTS BLOCKED.** CC BY-NC-ND 4.0.
- **EG-Solo / G&N / TENT — RECORDING RIGHTS BLOCKED.** Third-party/professional copyrighted sources.
- **EG-IPT — REFERENCE + RIGHTS FAIL.** Large real-guitar DI corpus, but no released independent performed note stream and no explicit permissive media rights.
- **Multimodal Electric Guitar Data — REFERENCE INSUFFICIENT.** Real guitar / CC BY 4.0, but actions/EMG/MoCap/audio do not establish immutable performed note-level onset+pitch truth.
- **MMIP — RIGHTS + REFERENCE FAIL.** CC BY-NC-SA; guitar MIDI produced post-recording via Ableton audio-to-MIDI.
- **M-M Guitar / Perez-Carrillo — REJECTED.** Onsets derived from recorded audio; pitch from score; too small and public availability/rights unresolved. Checkpoint `c338d05c6c321a2aebe7ca72d1f8b803bcfb36e1`.
- **GIHME — PUBLIC CORPUS NOT MATERIALIZED.** Zenodo `6798338` still exposes only conference paper `79.pdf`, not the advertised audio/annotation package. Checkpoint `6dcdeeba53e2a6b0433f77c3a36a0a9d6c446eb8`.
- **MUSMET — RIGHTS + REFERENCE FAIL.** Real electric-guitar ensemble audio + EEG, but no independent note-event reference; no explicit permissive performance-audio license. Checkpoint `dea3b9682cad4661eedad96a5e7ee3599dd89af9`.
- **Klangio GST-MM-2025 — REJECTED.** Strum/chord supervision, spectral-flux audio-derived onset component, and performance-audio rights not clearly established. Checkpoint `b77bf09259aaf122b60f778921abca110633f4a8`.
- **EGFxSet — NARROW BACKUP ONLY.** ~690 unique clean performances, CC BY 4.0, but no established high-resolution independent performed onset reference; effects cannot inflate evidence.
- **EGDB / EGDB-PG — REJECTED AS V6 REPLACEMENT HOLDOUT.** Current EGDB-PG v2 is an amplifier-rendered derivative of the already-governed EGDB performance population, not a new independent real-performance corpus. The 256 presets cannot inflate population evidence; no new independent performed onset+pitch reference is established, untouched status fails, and the current Zenodo v2 Rights section exposes no explicit license value. Dedicated checkpoint `docs/checkpoints/SONGSTERR_FRESH_EGDB_PG_V2_DERIVATIVE_HOLDOUT_REVIEW_2026-09-14.md`, commit `4462eabf17d5adcf0d05234d6e85eb5f6e2fcf68`.
- **GuitarDuets — REAL SUBSET LACKS NOTE TRUTH.** Note-level MIDI applies to synthesized material, not immutable performed truth for real duets.
- **DoMP — REJECTED.** Paper describes live electric guitar + Fishman TriplePlay MIDI, but authoritative Zenodo `10818617` release exposes only the MIDI archive and no evaluated audio. Checkpoint `4ed022234695996d2b491863918ee1f6909ae1a7`.
- **Geoff Bremner Multimodal Music Corpus — PRIVATE-LICENSE LEAD ONLY.** Public material does not establish simultaneously captured performed guitar MIDI/onset semantics/full-corpus population; no contact/acquisition.
- **GRAUX / Water commercial packs — REJECTED BEFORE PURCHASE.** Companion MIDI is not independent performed per-note guitar truth; licensing is production-oriented.
- **PolyMap — METADATA-ONLY / NOT ADMISSIBLE ON CURRENT PUBLIC EVIDENCE.** 64-channel real-guitar capture prototype, but no released qualifying corpus/reference/rights/population identities. Checkpoint `bd5379d5384e565abb89f81b1bd8288be41a13e0`.
- **TART 2026 — NO NEW HOLDOUT.** Uses already-governed GuitarSet/EGDB and noisy derivatives. Checkpoint `4a6d8e9b9860d2693e72fc0b4bb0af0404692959`.
- **Five guitar dataset — REJECTED BEFORE MEDIA ACCESS.** Zenodo `4988354` contains 30 underlying real-guitar performances recorded simultaneously through DI/mobile/computer setups (90 WAV views), but no independent performed note-level onset+pitch reference. Checkpoint `docs/checkpoints/SONGSTERR_FRESH_FIVE_GUITAR_DATASET_METADATA_REVIEW_2026-09-14.md`, commit `b4911312dd3a38d8578b0b97ef47b48b26b85e61`.
- **SJSU Patil 2025 thesis corpus — REJECTED AS CURRENT V6 HOLDOUT / METADATA-ONLY LEAD.** Institutional abstract reports 75,579 songs / 5,134+ hours, but no authoritative public corpus package with explicit permissive performance-audio rights, no established independent performed onset+pitch reference provenance, no frozen qualifying real-guitar/isolation population, and no defensible untouched external split were established. Dedicated checkpoint `docs/checkpoints/SONGSTERR_FRESH_SJSU_PATIL_2025_CORPUS_METADATA_REVIEW_2026-09-14.md`, commit `0e0c96a745edf484020aa8742ce1e3cd0212ecdd`.
- **FretboardFlow — REJECTED BEFORE MEDIA ACCESS.** Public ISMIR/GitHub evidence confirms real expert-performed hexaphonic guitar recordings, but the project README explicitly states the MIDI is quantized to four chords per bar and is not millisecond-accurate; the ISMIR description uses the GuitarSet/KAMIR automated hexaphonic-transcription pipeline. Current public repo also lacks a declared license and says audio will be uploaded. This fails the frozen independent high-resolution onset-reference gate before media access. Dedicated checkpoint `docs/checkpoints/SONGSTERR_FRESH_FRETBOARDFLOW_METADATA_REFERENCE_REVIEW_2026-09-14.md`, commit `f64f0dc851219142687b53d46cbc80ba86b94d84`.
- **2025–2026 recent primary-source delta sweep — NO ADMISSIBLE CANDIDATE FOUND.** Checkpoint `393e2769d007ed88f1dca61a8403cd54ee4e8001`.
- Other non-qualifying leads remain closed unless genuinely new primary evidence materially changes a hard gate: GPT/Su 2014, robot/isolated chord sets, NSynth, Slakh2100, URMP, GuitarJam, `guitar-fretboard-notes`, Semantic Timbre, `guitar-chord-mix`, MedleyDB, MUSDB18, MoisesDB, UT Austin/Kaggle, MagCIL guitar_style_dataset, Manchester/NOVARS, Mendeley/Figshare leads, Selekt stems.

Public/institutional/commercial search is near exhausted but this is not proof that no qualifying corpus exists.

## PURPOSE-BUILT UNTOUCHED HOLDOUT — DESIGN ONLY

Strongest surfaced architecture remains real guitar + conventional clean magnetic DI as evaluated signal + a separate physical fret-position reference for pitch identity + independent trigger/dynamics sensing. Fretsense/Solange-style hardware is feasibility evidence only; Jamstik/Fishman-style pitch-to-MIDI is weaker because the reference depends on pitch detection.

Purpose-built material must be original/public-domain/rights-cleared, explicitly licensed for product validation, collected with zero model access/no model-informed retakes, raw reference preservation, frozen objective QA, and preregistered non-holdout calibration. Provisional >=20,000 raw-reference notes / multi-player collection remains planning only; frozen >=1,000 V6-positive gate remains authoritative. No purchase, contact, hiring, recording or data acquisition without explicit user authorization.

## PURPOSE-BUILT GOVERNANCE — EIGHT-STAGE SYNTHETIC CI PASS

Existing governance layers remain binding: base manifest contract; semantic guard; content-only capture-plan binding; ancestral Git-history proof; deliberate GitHub-hosted `workflow_dispatch` attestation; GitHub server proof; exact hardened workflow/generator blob integrity; exact hosted attestation-artifact binding.

Latest eight-stage synthetic CI run `34793985984`, job `103823432519`, is green. Hosted artifact-proof production trust-boundary audit checkpoint `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_ARTIFACT_PROOF_TRUST_BOUNDARY_AUDIT_2026-09-13.md`, commit `2456945a1c270842594010b7c3ffde423f68adb7`, is PASS: production obtains exact cited-run metadata/artifact listing and downloads exact artifact bytes from GitHub before validation; caller-supplied artifact objects are confined to helper/test boundaries.

Successful purpose-built governance can establish only `mayAdvanceToReferenceBlindStructuralAudit:true`; it does not establish source truth, structural suitability, Basic Pitch/V6/correctness authorization, model validation, customer eligibility or delivery advancement.

## NEXT ALLOWED ACTION

1. Verify live branch head and this checkpoint before each continuation.
2. Do not reopen the artifact-proof trust boundary absent concrete new evidence of a loophole.
3. Continue metadata-only replacement-corpus research only for genuinely new primary evidence, authoritative rights changes, or a newly established independent performed onset+pitch reference.
4. If a candidate clears all five pre-media gates, stop before media access and freeze a candidate-specific reference-blind inventory/alignment preregistration.
5. If purpose-built remains the only route, keep design/calibration/protocol work on paper until explicit authorization for spending/contact/acquisition.
6. After a future structural audit passes, bind immutable identities, run no-real-correctness harness CI, then exactly one ordinary-GitHub-CPU correctness run under the frozen V6/scoring framework.
7. Ask before Modal, Vercel heavy-GPU, L4 GPU, or purpose-built spending/contact/acquisition. No question is needed for ordinary metadata research, coding, synthetic tests, GitHub CPU CI, or checkpoint maintenance.

## STILL FORBIDDEN

Guitar-TECHS correctness/repair/rescue; AG-PT-set/GAPS acquisition or scoring under current references; EGSet12 history rewriting/scoring; NC/ND or otherwise restricted corpus use outside rights; rescue via evaluated-audio-derived truth; counting synthetic/effect/duplicate/simultaneous-view derivatives as independent real evidence; reopening GOAT/reference scoring from literature mentions; V5/FLGD rerun/tuning; protected-song execution; duration research; changing frozen V6/scoring rules from holdout observations; real-corpus optimizer/threshold sweeps or fine-tuning; treating vendor MIDI as infallible truth; purpose-built calibration on admitted holdout/model outcomes; purpose-built procurement/contact/hiring/recording without explicit authorization; Production/customer promotion without untouched external validation + separate policy review; Modal/Vercel heavy-GPU/L4 without explicit authorization.

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1`. Guitar-TECHS is closed outcome C before correctness; its official successful audit artifact remains live/unexpired with GitHub digest `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`, and the previously independently verified archive digest and merged JSON SHA remain unchanged. V6 method/scoring remain frozen and no replacement-holdout correctness has been exposed. Latest material delta reviewed: GAPS v1.1 now includes audio and declares MIT at the repository level, but its high-resolution note timing remains derived from evaluated audio by DTW + transcription-model activations, manual downbeat intervention, re-alignment, and model-agreement filtering; underlying performances are from third-party YouTube performers without a reviewed track-by-track product-validation rights chain. Dedicated checkpoint `docs/checkpoints/SONGSTERR_FRESH_GAPS_V1_1_RELEASE_DELTA_REVIEW_2026-09-14.md`, commit `7a6ebe309cfe17067990433ed88e58f5ef68ba48`. Purpose-built independent-sensor capture remains the strongest design route but is design-only and requires explicit user authorization before contact/spending/recording. No real candidate media, Basic Pitch/V6 correctness, Modal, Vercel heavy-GPU or L4 work is authorized by this checkpoint.