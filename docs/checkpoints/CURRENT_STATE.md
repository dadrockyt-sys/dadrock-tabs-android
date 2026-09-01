# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-01 UTC  
Branch: `v143-contextual-prune-lobo`

## Active phase
**V168 remains `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 is CLOSED / TERMINAL. The GOAT restricted-dataset access request has now been submitted successfully through Zenodo and is awaiting the dataset owner's decision. As of 2026-09-01, no owner/Zenodo reply has been received. Submission is not approval: no GOAT bytes or owner grant/conditions are present yet, no holdout asset has been admitted, and V168 reference-facing score calls remain exactly 0. `main`/Production remain untouched. CPU only; fresh explicit authorization is required immediately before GPU/CUDA/Modal.**

## Percentage reporting — STANDING USER INSTRUCTION
The user prefers a percentage score in future progress/test updates because it helps motivation and makes progress easier to follow.

### Project Progress Score — fixed five-gate rubric
Each gate is worth 20 percentage points:
1. **Preregistration + frozen Policy A/B complete** — 20%.
2. **Admission/provenance validators frozen + self-tested** — 20%.
3. **External candidate screening completed to a defensible stop boundary** — 20%.
4. **>=2 admissible independent professional holdout songs acquired; rights/provenance frozen; exact source/reference SHA256-bound; both validators passed** — 20%.
5. **Reference-blind Policy A/B candidates frozen for all admitted songs + prospective holdout scoring completed under the frozen evaluation rule** — 20%.

### Current score
**Project Progress Score: 60%** — gates 1–3 complete; gates 4–5 incomplete.  
**Test Score: NOT RUN** — no legitimate V168 holdout evaluation has occurred.

### Score-integrity rules
- Percentage display is motivational/reporting only and never replaces frozen scientific pass/fail gates.
- Never invent/inflate a model score or round upward to imply success.
- Keep **Project Progress Score** separate from **Test Score**.
- If no legitimate evaluation ran, report `Test Score: NOT RUN`.
- Meaningful research progress may be reported even if the fixed Project Progress Score remains unchanged.
- Include percentage score in future checkpoint updates and user-facing progress/test summaries unless the user asks otherwise.

Score-reporting rule creation commit: `6145665b2705e904f657e59ed5631404f03d36d7`.

## Latest milestone — GOAT ACCESS REQUEST SUBMITTED
Dedicated submission checkpoint:
- `docs/checkpoints/V168_GOAT_ACCESS_REQUEST_SUBMITTED_20260829.md`
- creation commit `2d9a2d62a712af34c2c60dfd6cf587bd9e314d96`
- status **REQUEST SUBMITTED / AWAITING OWNER DECISION / ACCESS NOT YET GRANTED / NO ASSETS ADMITTED / SCORING NOT ARMED**.

The user supplied a screenshot of an auto-generated Zenodo email whose subject/body state that the access request was submitted successfully. This is sufficient to record successful submission, but **not** approval or file access.

No private request-management link, token, password, credential, or other secret value is stored in the repository.

Prepared-request checkpoint:
- `docs/checkpoints/V168_GOAT_ACCESS_REQUEST_READY_20260829.md`
- creation commit `e6895981e3571550297efb954ec1436314042a9b`.

### GOAT authoritative access posture
- Dataset record: `https://zenodo.org/records/15690894`
- DOI `10.5281/zenodo.15690894`.
- Version v1; files restricted/request-access.
- Public record asks for a short description of intended use.
- Public record states research purposes only / not intended for commercial product use.
- Public repository `JackJamesLoth/GOAT-Dataset` directs researchers to request access through Zenodo.
- ISMIR paper says distribution is by request to control research-only use.
- No owner approval/grant has yet been claimed in this project.

### GOAT scientific/provenance notes — FROZEN
- ~5.9 h unique high-quality electric-guitar DI recordings.
- Guitar Pro tablatures / DadaGP, quantized MIDI, and separately fine-aligned MIDI are described.
- Audio/tab pairs were manually checked/aligned so every note matched.
- The separately fine-aligned MIDI was produced through an external alignment procedure and must **not** be silently relabeled `derivedFromModelOrCandidateOutput=false`.
- Before any admission, freeze exact owner grant/terms, record/version, file bytes + SHA256, source/reference pair binding, chosen reference layer, timing conversion if any, reference isolation, and deterministic score-blind song selection.

Known public GitHub issue #1 reports possible duration/EOF mismatches for `item_67`, `item_96`, and `item_110`. Treat these as **unverified third-party reports**, not confirmed defects. If access is granted, check them prospectively during integrity intake and freeze any exclusion/repair rule before comparative scoring.

Submitting the request is meaningful progress, but it does **not** satisfy gate 4; Project Progress Score therefore remains **60%**.

## Public/open holdout search — FROZEN STOP
Dedicated checkpoint:
- `docs/checkpoints/V168_OPEN_HOLDOUT_SEARCH_STOP_20260829.md`
- creation commit `2b4d60cd022655076817b1e5bdad5bf5d0298606`
- status **OPEN SEARCH EXHAUSTED TO CURRENT PRACTICAL FRONTIER / EXTERNAL ACCESS OR NEW PROVENANCE REQUIRED**.

Do not continue broad public-dataset searching by default. Resume only if genuinely new evidence/corpora appear, GOAT access status changes, G&N rights/provenance changes, or the user supplies another exact licensed professional holdout source/reference pair.

## Candidate status summary
### GOAT — PRIMARY LEAD / REQUEST PENDING / NOT ADMITTED
Strongest current path. Await owner decision. No files/reference events may be assumed available before grant.

### G&N — PROVENANCE-STRONG FALLBACK / BLOCKED
Dedicated checkpoint: `docs/checkpoints/V168_GN_DATASET_SCREENING_20260829.md`, commit `b71cf2c079b695d9b6c18faacc4a85853d7c0d16`.
- 42 unaccompanied monophonic electric-guitar solo tracks, 20–40 s each.
- Experienced electric-guitar player manually annotated note/timing/technique labels from book tablature; second electric-guitar player checked every label.
- Strong professional/human reference provenance.
- Blocked because exact source audio is commercial *Rock Lead Basics* companion material and no frozen lawful research-use acquisition path for exact source audio + annotations exists.

### IDMT-SMT-Guitar — BLOCKED
Dedicated checkpoint: `docs/checkpoints/V168_IDMT_SMT_GUITAR_SCREENING_20260829.md`, commit `5c197a9cef7700df717cfbb041a0673aab5429f0`.
Evaluation-purpose CC BY-NC-ND 4.0 basis exists, but exact professional annotation/validation provenance for the later five song-like subset-3 pieces is not strong enough for the current gate.

### AG-PT — EXCLUDED
`docs/checkpoints/V168_AGPT_EGSOLO_TRIAGE_20260829.md`, commit `e114eab039e588484d4f91fba153dd56e4a4cbaf`. Human/musician annotations, but isolated monophonic technique-note units rather than song/piece holdout streams.

### EG-Solo — BLOCKED
Promising manual tablature-assisted annotation, but source performances are third-party professional YouTube demonstrations and no frozen exact-source research-use grant was found.

### EGDB real-world — BLOCKED
Musician manual annotation reported for five YouTube guitar recordings; exact professional symbolic references/use basis and source rights remain unresolved.

### EGSet12 — BLOCKED
Authors' loader requires `jams_corrected/<track>.jams`; corrected JAMS are not publicly published/explained sufficiently. Do not substitute public Zenodo JAMS by assumption.

### Terminal exclusions / not admitted
- François Leduc — high-resolution MIDI uses transcription-model activations for alignment; violates strict no-model-derived-reference gate.
- GAPS — high-resolution reference alignment algorithm/model-assisted before human verification/correction.
- GuitarSet — annotation construction relies substantially on automated monophonic pitch tracking; known annotation issues.
- Guitar-TECHS — synchronized MIDI/pickup capture, not independently established professional note-event transcription reference.
- Kaggle Guitar Transcription Dataset — frame-level finger/fret labels, not professional timing-aware song reference.
- EGFxSet — isolated tones.
- GUITAR-FX-DIST — isolated notes/chords/effects material.
- EG-IPT — isolated monophonic single-note technique material.

## Frozen V168 machinery — UNCHANGED
- Base admission validator: `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`, blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`.
- Provenance companion: `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`, blob `9edb8a65cc809d7fe42a288d6a00cfc602f37dcc`.
- Intake requirements: `docs/checkpoints/V168_HOLDOUT_ASSET_INTAKE_REQUIREMENTS_20260829.md`, blob `3064b8e9000fbab1b031ed32389cb82aab846876`.
- Preregistration: `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`, commit `64d724e816808aa60d766923bb1a9ce241e89e89`, blob `3a72db20d4ebebf8e4a25f5c37125e1a40934047`.
- Provenance self-test receipt: `debug/v168-holdout/provenance-gate-selftest-receipt.json`, blob `5540b4895e94eeb7636cbf1c0b80b1786e7bf861`.
- Frozen V154 scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Core `score_stream()` is song-generic, but current V154 CLI/loaders hardcode **Lenny Kravitz — Are You Gonna Go My Way**. Do not build/arm a generic V168 adapter before asset admission.

## Frozen V168 policies — UNCHANGED
**Policy A — `v168-baseline-i005-policy`**  
V167 I005 / `gss-active-only` with frozen calibration settings: active Basic Pitch context, `fundamentalPresent`, rank>=0.975, activity>=0.05, onset>=0.50, candidate/max-active score ratio>=1.00, reject nearest different active intervals {12,19,24}, top1/site, Guitar cap6, inactive branch off.

**Policy B — `v168-gap1-earliest-policy`**  
Exact Policy A stream, then same-MIDI connected components with consecutive grid gaps <=1 collapse to earliest event; singletons unchanged.

No holdout-driven selector/threshold mutation.

## Holdout admission gate — HARD BLOCK
No V168 scorer workflow may be armed until:
1. >=2 genuinely independent songs pass BOTH frozen validators;
2. each is different from `Are You Gonna Go My Way`; different artists preferred where practical;
3. each has frozen exact source audio + professional scorer-ready combined-Guitar reference identity + source/reference pair binding;
4. `professionalReference.derivedFromModelOrCandidateOutput=false` is defensible;
5. candidate generation cannot access professional-reference content/bytes;
6. Policy A/B candidates are generated reference-blind and fully hash-frozen for every admitted song;
7. a global candidate-freeze manifest is committed before first reference-facing score call.

If fewer than 2 valid songs exist, remain `HOLDOUT_ASSET_MISSING`; score calls remain **0**.

## V168 prospective evaluation rule — UNCHANGED
Primary metric: combined-Guitar timing-aware pitch F1 under frozen V154 `score_stream()` semantics, equal-weight macro average across admitted holdout songs.

Policy B passes only if ALL:
- macro F1 >= Policy A + **0.10pp**;
- macro precision >= Policy A;
- no individual song loses > **0.25pp F1** vs Policy A;
- >=2 independent songs scored;
- no holdout-driven retuning, adverse-result song exclusion, variant addition, or post-score mutation.

Tie/inconclusive -> retain Policy A / `HOLDOUT_INSUFFICIENT`.

## V167 terminal handoff — IMMUTABLE
- Promoted I005 `gss-active-only`: Guitar F1 **42.7940586109996%**, P48.54280510018215%, R38.26274228284279%; 533/1098/1393; FP565/FN860; SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Bass F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%; 426/512/547; FP86/FN121.
- Highest scored but unpromoted `recur-gap1-earliest`: Guitar F1 **42.88012872083669%**, +0.08607010983709418pp vs I005; SHA256 `a72ce501c6d4cdbcbbdc67370ef2b35b88ad2358921d1de90f86d7f5af4c4dbe`.
- It did NOT clear frozen +0.10pp promotion threshold. No I006 exists.
- V167 closure commit `cef3d57baf346e1f01faad19bb0998d602e86386`.

## Standing safety / methodology
- V168 is prospective holdout evaluation, not calibration continuation.
- Professional-reference content cannot be read to choose favorable tracks or by candidate-generation/policy code.
- Freeze all candidates before any professional-reference scoring.
- No per-event reference choices, direct reference-event copying, post-score mutation, retuning, adverse-result song exclusion, or gate weakening.
- Third-party/private permission obtained by another project does not transfer to DadRock.
- Public availability, YouTube URL, commercial purchase, article license, or unlicensed GitHub repository is not by itself an adequate exact-source rights/use basis.
- CPU only; fresh explicit authorization immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## 2026-09-01 related finding — BTS separation input quality / tone bleed
This is a related engineering observation only. It does **not** alter V168's frozen evaluator, policies, admission gates, score, or CPU/GPU authorization state.

Backing Track Studio inspection on branch `backing-track-studio` found:
- separator: `audio-separator[cpu]==0.30.2` using Demucs six-source `htdemucs_6s.yaml`;
- upload UI currently accepts MP3, WAV, M4A and AAC;
- every uploaded source is decoded before separation with FFmpeg to **44.1 kHz, stereo, 16-bit PCM WAV** (`pcm_s16le`);
- separated stems are WAV;
- the reconstructed customer backing track is encoded only **after separation** as 192 kbps MP3;
- current Demucs run parameters are `shifts=1`, `overlap=0.10`, `segment_size=6`, CPU-only.

Quality interpretation / working recommendation:
- Preferred canonical source for separation is **lossless stereo PCM WAV**. FLAC is technically equivalent lossless input if/when the BTS upload UI is extended to accept it.
- Prefer a genuine lossless original/master at 44.1 kHz or 48 kHz. Do not upsample a lower-rate/lossy source merely to create a larger WAV.
- 24-bit lossless source is useful when it is genuinely available, but the present BTS normalization intentionally converts to 16-bit PCM before Demucs. A genuine 16-bit CD-quality WAV remains a strong source.
- MP3/AAC/M4A/typical MP4 audio is normally lossy. Decoding it to WAV before Demucs does **not** restore information already discarded by the codec.
- MP4 is a container, not an intrinsic audio quality level; its audio can be lossy AAC or, less commonly, another codec. Therefore `.mp4` alone is not a quality recommendation.
- Lossless input can reduce codec artifacts and preserve transient/stereo/spectral cues, but it cannot eliminate source-separation bleed caused by overlapping harmonics, distortion, reverb, doubled guitars, dense mixes, or model limitations.
- The BTS 192 kbps MP3 encode happens after source separation, so it cannot be the cause of guitar information leaking into the wrong stem during inference, although it can slightly reduce final playback fidelity.
- The current separator settings are speed-leaning. Upstream Demucs defaults to overlap `0.25`; its shift-trick documentation says additional shift predictions can improve SDR but scale inference time roughly with the number of shifts. A controlled quality test of overlap/segment/shifts is therefore a higher-value next BTS experiment than changing container extensions alone.
- Upstream Demucs itself describes `htdemucs_6s` as an experimental six-source model, so audible guitar bleed may remain even with pristine lossless input.

Do not change the V168 research branch separator/scorer/evaluator because of this BTS observation. If BTS quality work resumes, keep it isolated to `backing-track-studio` and compare the same lossless reference excerpts under controlled separator settings before adopting any slower production configuration.

## 2026-09-01 diagnostic — SplitMySong isolated guitar
Dedicated diagnostic checkpoint:
- `docs/checkpoints/V168_SPLITMYSONG_GUITAR_DIAGNOSTIC_20260901.md`
- creation commit `b9b5d6440540dcbaa8f3c2db1119a69d4a248d92`
- status **DIAGNOSTIC INPUT FROZEN / CPU COMPARISON NOT YET SCORED**.

The user supplied an externally separated AYGGMW guitar stem produced by SplitMySong. Exact diagnostic audio SHA256: `6601b8d01cbbbe6b6e70d9ec0ca3c15d17873c78e62ae4acdc258c96f168e3c9`.

Scientific boundary:
- external model-generated separation only; **not** a professional reference and **not** an admissible V168 holdout asset;
- diagnostic question is whether this cleaner isolated-guitar input improves the legacy AYGGMW transcription result when passed through the exact frozen V167 I005 CPU path;
- frozen comparison baseline is Guitar F1 **42.7940586109996%**, P **48.54280510018215%**, R **38.26274228284279%**, TP/pred/ref **533/1098/1393**;
- reference-blind audio alignment check froze start offset at **0.000 s**, no time-stretch; isolated stem contains approximately 5.5 s of trailing padding;
- exact historical Basic Pitch observer settings recovered: onset `0.50`, frame `0.30`, minimum note length `90 ms`, guitar frequency range, no multiple pitch bends, Melodia trick on;
- exact V167 I005 contextual thresholds/selectors remain frozen and must not be changed after seeing the diagnostic result;
- local CPU sandbox lacks Basic Pitch and the Demucs six-source model weights, and local DNS prevents dependency/model download. Do not substitute another detector;
- historical successful runtime is now proven as GitHub Actions Ubuntu 24.04 CPU / Python `3.10.21` / `basic-pitch==0.4.0` with `tflite-runtime==2.14.0`; TensorFlow and ONNX Runtime were absent;
- no GPU/CUDA/Modal has been used or authorized.

This diagnostic does not alter V168: **Project Progress Score remains 60%; Test Score remains NOT RUN; V168 prospective reference-facing score calls remain exactly 0.**

## NEXT boundary — GOAT OWNER DECISION / EXTERNAL ACCESS REQUIRED
1. **Project Progress Score: 60%. Test Score: NOT RUN.**
2. **Do not score V168 prospective holdouts.** The frozen SplitMySong AYGGMW diagnostic may be scored separately after its candidate stream is generated and hash-frozen, because it is explicitly outside V168 prospective evaluation.
3. **Do not implement V168 candidate generation or a generic/new-song scorer adapter.**
4. GOAT request is submitted; as of 2026-09-01 no reply has been received. Await explicit owner/Zenodo decision. Do not claim approval until grant evidence exists.
5. Preserve non-secret grant wording/date/conditions/restrictions if approval arrives; never commit secret links/tokens/credentials.
6. Once access is actually granted, perform score-blind GOAT metadata/integrity intake first: exact record/version, file bytes/SHA256, source/reference binding, reference-layer derivation, use terms, and the reported duration/EOF anomalies.
7. Freeze deterministic integrity/song-selection rules before reading professional note-event content for scoring or generating comparative results.
8. No asset admission until a complete >=2-song manifest passes BOTH frozen validators.
9. Only after admission may reference-blind Policy A/B candidate generation be armed; freeze all candidates globally before first score call.
10. Save `CURRENT_STATE.md` before any future admission, candidate-code arm, scorer arm, or reference-facing score call.
11. Keep Project Progress Score/Test Score in future user-facing updates.
12. CPU only; no GPU/CUDA/Modal; never modify main/Production.

## 2026-09-01 resume checkpoint — historical Basic Pitch runtime trace
- Re-fetched `docs/checkpoints/CURRENT_STATE.md` from `v143-contextual-prune-lobo` before making changes and preserved all frozen V168/V167 boundaries.
- Confirmed the safe continuation remains the isolated SplitMySong AYGGMW guitar diagnostic on CPU only; V168 itself remains unarmed at **Project Progress Score 60% / Test Score NOT RUN**.
- Corrected a stale repository-search clue: `scripts/doctor-basic-pitch.ps1` is **not present** at the current branch head, so no Basic Pitch package version is being asserted from that stale path.
- Inspected the current `.github/workflows` directory; there is no workflow filename containing `basic`, so the historical runtime was traced through the self-deleting V162→V165 workflow lineage and GitHub Actions history rather than filename matching.
- No detector substitution, Basic Pitch retuning, V167 I005 threshold change, V168 validator/scorer change, benchmark mutation, GPU/CUDA/Modal use, `main` change, or Production change has been made in this resume step.

## 2026-09-01 provenance correction — Basic Pitch runtime trace
- Corrected the earlier old-ref interpretation: `b8c698eff3854cf2c40b375c5ef81070a5e0fe69` is the **tree SHA** of branch-head commit `76215896844d9361db110fa2d81a1c7416c16631`, not a commit SHA.
- V162 itself cannot prove an executed Basic Pitch runtime: its sole generation run `33213057382` terminated at `PRE_RUN_GUARD_FAIL` with no environment receipt, candidate, generation receipt, or pitch inference artifact.
- V164 did freeze a CPU environment receipt proving Python `3.10.21`, `basic-pitch==0.4.0`, Torch `2.8.0+cpu`, CUDA unavailable, but its generation terminated at `TRANSCRIBER_FAIL` after timebase QC and produced no candidate.
- V165 is the first successful candidate-generation runtime in this lineage. Frozen environment receipt `debug/v165-cpu-autonomous/environment-receipt.json` records Python `3.10.21`, `basic-pitch==0.4.0`, Torch `2.8.0+cpu`, CUDA unavailable, and the exact dependency set. Generation run `33223256331`, job `99021632117`, completed `STRUCTURAL_QC_PASS` and committed authoritative candidate `debug/v165-cpu-autonomous/generated.json` with SHA256 `b1ad02001724750ea82d693591a7c0b1f214820de37a590871a6d78eef63e5cb`.
- The successful V165 Actions log proves the Basic Pitch installation pulled `tflite-runtime==2.14.0`; it explicitly warned that CoreMLTools, ONNX Runtime, and TensorFlow were not installed. Therefore the executed Basic Pitch backend was the TFLite runtime path, not TensorFlow or ONNX.
- The authoritative V165 candidate records `basicPitchVersion=0.4.0`, raw Basic Pitch Guitar event count `1404`, and `basicPitchModelSha256=3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`.
- This supersedes the earlier provisional expectation of a Python 3.11 environment. Exact historical reproduction target for the SplitMySong diagnostic is **Ubuntu 24.04 CPU / Python 3.10.21 / Basic Pitch 0.4.0 / tflite-runtime 2.14.0**, with the Basic Pitch model file required to hash to `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676` before inference.
- No diagnostic candidate has been regenerated yet. Before any candidate-generation arm, re-fetch this checkpoint, verify the SplitMySong audio bytes still hash to `6601b8d01cbbbe6b6e70d9ec0ca3c15d17873c78e62ae4acdc258c96f168e3c9`, and freeze the exact reference-blind diagnostic workflow/code identity.
- No GPU/CUDA/Modal workload was triggered or authorized. V168 remains frozen at **Project Progress Score 60% / Test Score NOT RUN**.

## 2026-09-01 continuation checkpoint — SplitMySong input + successful V165 run identity
- Recomputed SHA256 directly on the materialized SplitMySong guitar file `Guitar - Are You Gonna Go My Way - Lenny Kravitz ｜ Only Guitar (Isolated).m4a`: **`6601b8d01cbbbe6b6e70d9ec0ca3c15d17873c78e62ae4acdc258c96f168e3c9`**, exactly matching the frozen diagnostic identity above.
- Corrected a stale compacted-context transcription that had shown a different `6601...` suffix. The file bytes and authoritative checkpoint agree on `6601b8d01c...`; the stale value must not be used.
- Resolved successful GitHub Actions generation run **`33223256331`**, job **`99021632117`**, workflow **`.github/workflows/v165-generate.yml`**, historical head commit **`c04832da85afdd9a585141dd763dc3c1212ace6e`**.
- Historical workflow inspection confirms CPU-only `ubuntu-latest`, `actions/setup-python@v5` with Python `3.10`, `basic-pitch==0.4.0`, and the V165 transcriber entrypoint `validation/v165_cpu_autonomous/transcribe_v165.py`; the successful frozen receipt remains authoritative for the exact resolved patch/runtime versions and TFLite model hash.
- `validation/v165_cpu_autonomous/transcribe_v165.py` is a shim into the V164/V163/V162 lineage. V164 freezes the Basic Pitch prediction settings and model symbol; the exact V167 I005 contextual-filter identity still must be recovered/frozen before diagnostic generation is armed.
- No reference-facing scorer has been run, no diagnostic candidate has been generated, and no legacy reference triplets were exposed to generation code in this continuation step.
- No GPU/CUDA/Modal use, V168 policy/scorer/validator change, `main` change, or Production change. **Project Progress Score remains 60%; Test Score remains NOT RUN.**

## 2026-09-01 continuation checkpoint — V167 I005 identity comparison resolved
- Compared the two post-I005 aggregate analyzers. `analyze_post_i005_active_only_v167.py` was introduced at commit `fdbb26b4ca50f235dbaf459941004194bcf3a7c1`; four minutes later `analyze_post_i005_active_only_v167_rearm.py` was introduced at commit `70ace4cd7d7594ee89c8ab341bdbdde9059eec3d` specifically to correct the first analyzer's eligibility-boundary error.
- The first analyzer incorrectly equated a reference-blind **pre-grid** structural eligibility count with the state-split builder's **post timing/dedupe/polyphony** `eligible` count. The rearm analyzer is therefore the authoritative one for post-I005 aggregate diagnosis; the first analyzer must not be used to reconstruct the frozen winner.
- The stronger source of truth for exact generation identity is `validation/v167_single_song_calibration/promote_state_split_guitar_winner_v167.py`, which freezes and verifies the builder identities, winner config, frozen report/manifest identities, candidate SHA, summary, and metrics before promotion.
- Exact frozen builder identities are recovered at current branch head and match the promotion guardrails: base builder `build_upstream_recovery_variants_v167.py` blob **`24413d321f64bbfcce48812ceb85b4593dcfa80c`** and state-split builder `build_state_split_guitar_variants_v167.py` blob **`6b480d43744a5c67c02510d55162581d896afee4`**.
- Exact `gss-active-only` generation config is recovered: `templateRankMin=0.975`, `activitySupportMin=0.05`, `onsetSupportMin=0.50`, `fundamentalPresentRequired=true`, active Basic Pitch context required, active candidate/max-active template-score ratio `>=1.00`, reject nearest different active intervals `{12,19,24}`, top-1 addition per site, existing I003 events preferred, step/MIDI dedupe on, Guitar polyphony cap `6`, inactive branch disabled.
- The builder uses the frozen corrected timing path from the base builder, including `GLOBAL_PHASE_CORRECTION=-12` grid steps and deterministic candidate ordering. The state-split winner summary is exactly 48 active additions / 48 eligible / 48 sites with adds, yielding 1098 Guitar events.
- Frozen state-split winner candidate SHA256 is **`aa042135c542f2025522bb0d8ab9491c8457bf95025db5953b714d452afc0d5e`**; promoted rich I005 SHA256 remains **`86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`**.
- This resolves the previously open **exact V167 I005 contextual-filter identity** blocker for the SplitMySong diagnostic. The next safe engineering step is to freeze a dedicated reference-blind diagnostic generation workflow/code path that pins the already-recovered V165 Basic Pitch runtime/model identity and these exact V167 builder/config identities, verifies the SplitMySong input hash before inference, and emits/hash-freezes the candidate before any legacy AYGGMW scorer/reference access.
- No SplitMySong candidate has been generated or scored in this comparison step. No reference content was exposed to generation code. No GPU/CUDA/Modal use, V168 mutation, `main` change, or Production change occurred. **Project Progress Score remains 60%; Test Score remains NOT RUN.**

## 2026-09-01 continuation checkpoint — SplitMySong input preflight frozen
- The user-supplied isolated-guitar audio was verified privately without committing audio bytes. Exact source identity: SHA256 **`6601b8d01cbbbe6b6e70d9ec0ca3c15d17873c78e62ae4acdc258c96f168e3c9`**, 3,610,958 bytes, AAC, 44.1 kHz stereo, duration 217.060136 s.
- Deterministic reference-blind normalization is frozen as FFmpeg audio stream 0 -> 22.05 kHz mono PCM S16LE. Two local executions reproduced the same normalized bytes: SHA256 **`fdb0578d71f77c150e7fe66766a03953be55e7028fef4c24dc777416f2e7ff4f`**, 9,572,600 bytes, duration 217.060136 s.
- Frozen preregistration: `debug/v168-splitmysong-diagnostic/preregistration.json`, creation commit `32c64d8a1c47c840759b011a421cf8274675dab5`, blob **`547e505d7bdd8926bcb4168aaeb0edf76bab564f`**.
- Frozen implementation contract: `debug/v168-splitmysong-diagnostic/implementation-contract.json`, creation commit `412942e5602108001f54ff4cfdc955eef010da42`, blob **`5d6494bf19cabc6274a5cd3a3288608ef16c9bff`**.
- Reference-blind preflight: `validation/v168_splitmysong_diagnostic/preflight_splitmysong_v168.py`, creation commit `45c3e2dca07bc56940c4e71fd31fdf59c4787467`, blob **`bec0f7e98aa57f104adbabd4eed1423530bcd373`**, SHA256 **`de2d9d9809ec757fd536c7dba4a460f6f83e57f44e37c4f1d91130ca3bb0b5dd`**.
- Local input-preflight receipt: `debug/v168-splitmysong-diagnostic/input-preflight-receipt.json`, corrected byte-identity commit `db72524011fe9db12f03dfaa9fbde95290f2ddff`, blob **`bfe5a27a42d3d9470057d754f106a75e9df0a12c`**, SHA256 **`a0f7824e4becb6f5aaf4d988fb7efc03178999d32d3d7a729b3cac2aeff1bac0`**, status `INPUT_FROZEN / PASS`.
- The preflight has separate `input` and `arm` phases. `input` verifies only private audio identity and deterministic normalization. `arm` additionally refuses to pass unless Python 3.10.21, the exact V165 dependency set including Basic Pitch 0.4.0 / TFLite Runtime 2.14.0 / Torch 2.8.0+cpu, the Basic Pitch model SHA256, and all frozen V162/V164/V165/V167 code blobs match.
- The `arm` phase performs no pitch inference and accepts no scorer/reference path. Passing it would only authorize the already-preregistered one-shot CPU generation step; it cannot score or expose legacy AYGGMW reference content.
- No audio or normalized WAV was committed. No candidate was generated, no pitch inference or scorer ran, no professional or legacy AYGGMW reference was read, and reference-facing score calls remain 0.
- Exact runtime inference remains unarmed because the private local sandbox cannot reproduce the pinned Python 3.10.21 / Basic Pitch TFLite environment and the public repository must not be used to transfer the copyrighted audio.
- No GPU/CUDA/Modal use, V168 policy/scorer/validator mutation, `main` change, or Production change occurred. **Project Progress Score remains 60%; Test Score remains NOT RUN.**
- Next safe step: obtain an access-controlled CPU execution path that can receive the already-verified private audio without public exposure, pass the strict `arm` preflight, generate exactly one candidate reference-blind, hash-freeze it, and only then permit the separate legacy AYGGMW diagnostic scorer to read its existing reference.

## 2026-09-01 continuation checkpoint — SplitMySong CPU environment verified
- A reproducible CPU execution environment now exists for the diagnostic. The environment is code-only; no user audio is stored in the repository or GitHub Actions.
- Exact pinned dependency file: `validation/v168_splitmysong_diagnostic/requirements-cpu.txt`, blob **`fa90d51a2b88b14f6043e6e3fab22d22aae02c7a`**. It pins Basic Pitch 0.4.0, TFLite Runtime 2.14.0, Torch 2.8.0+cpu, NumPy 1.26.4, SciPy 1.13.1, SoundFile 0.12.1, Librosa 0.11.0, ImageIO-FFmpeg 0.6.0, and Demucs 4.1.0.
- Exact CPU container: `validation/v168_splitmysong_diagnostic/Dockerfile.cpu`, blob **`742eb14ae2caba91d57c26d549edf101a0f0a887`**. Base image is Python 3.10.21 slim Bookworm; FFmpeg/Git/libsndfile are installed; CUDA visibility is disabled and deterministic single-thread math environment variables remain frozen.
- Exact environment verifier: `validation/v168_splitmysong_diagnostic/verify_environment_v168.py`, blob **`af7bc08a29ef25b13c1f8186bea99061f2f65555`**. It requires Python 3.10.21, exact package versions, Torch 2.8.0+cpu with CUDA unavailable, Basic Pitch model SHA256 **`3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`**, and the frozen V162/V164/V165/V167 repository blobs.
- GitHub Actions smoke workflow `v168-splitmysong-environment-smoke.yml` built and verified the container successfully in run **33516983504** at commit **`f323ef311207fe3590f1061f55f158af6e30a1e3`**. Both the Docker build and the second in-container verifier execution passed.
- A personal Codespaces configuration now exists at `.devcontainer/v168-splitmysong/devcontainer.json`, blob **`1fcc212dc929631c8842812cc1e2a13affd9c571`**. This gives an access-controlled browser-hosted filesystem for the private audio while reusing the same verified CPU image.
- Private arm launcher: `validation/v168_splitmysong_diagnostic/run_private_arm_preflight.sh`, blob **`316c77eaf1c447f3defb193d08baaf8a52edc3d9`**. It writes environment, normalized-audio, and arm receipts only into a user-private output directory and does not invoke pitch inference or scoring.
- Environment status is now **CPU_ENVIRONMENT_READY**. Candidate generation remains unarmed until the verified private audio is placed inside an access-controlled execution environment and the strict `arm` preflight passes there.
- No audio was committed or uploaded as an Actions artifact. No candidate was generated, no pitch inference/scorer/reference ran, no GPU/CUDA/Modal use occurred, and V168 holdout/scoring state is unchanged. **Project Progress Score remains 60%; Test Score remains NOT RUN.**
- Next safe step: create/open the personal Codespace from `v143-contextual-prune-lobo` using the `v168-splitmysong` devcontainer, place the already-hash-frozen isolated guitar file only inside that Codespace, run the private arm preflight, and freeze its PASS receipt before implementing or running the one-shot candidate generator.
