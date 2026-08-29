# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163/V164/V165 are terminal and permanently closed. V166 is independently preregistered from reference-free static architecture; its numeric contract, finalized implementation, authoritative CPU static preflight, pre-run identity, and song-blind CPU generation environment are all separately sealed PASS. V166 has still executed no song audio, normalization, Demucs separation, timebase, pitch inference, candidate generation, professional-reference/scorer read, V165 candidate/score runtime read, or GPU work. All preparatory writes are now complete. Next boundary: audit/arm exactly one CPU-only V166 generation run and make zero branch writes while active. `main`/Production remain untouched.**

## Standing safety
- CPU-only reference-free work authorized at assistant discretion.
- Fresh explicit authorization required immediately before Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159–V165 generation versions closed forever; V163/V165 score opportunities closed forever.
- Never rerun/rearm/repair/retune/regenerate/re-QC/rescore a closed version.
- No professional-reference event/measure mining, score-informed retune, threshold sweep, variant selection, or human correction.
- V166 does **not** claim score blindness because V165 aggregate score was observed before V166 preregistration; V166 design/numerics are quarantined from V165 score/reference evidence.
- PR #22 remains open/unmerged as visibility only.

## V165 terminal anchors
- Sole generation run `33223256331`, attempt `1`, job `99021632117`; terminal commit `97c2efe6acf988a4535de1fff449194b7b2f7c2b`; structural QC PASS.
- Candidate blob `e70a444cb7778a6f56988cf8cc69dccb9c1d89ce`; SHA256 `b1ad02001724750ea82d693591a7c0b1f214820de37a590871a6d78eef63e5cb`; Guitar `1043`, Bass `405`.
- Sole actual score run `33225802868`, run `1`, attempt `1`, job `99029213716`; terminal score commit `37a96aff29b88dd5c7f4272c2ed503cbbad2fc7f`; `SCORE_GATE_FAIL`.
- Score terminal blob `3e9a5b3d6e3a5d11b2f719bdf8e808b7f2076164`; `neverRescoreV165=true`.
- Delayed-registration run #2 `33225842248` / job `99029324185` was guard-rejected before scorer; zero second score executions. Inert score workflow removed at `4d9f2dddcc1b0e5b5a87d0a7667090f1143f4799` `[skip ci]`.

## V166 preregistration / contract
- Prereg commit `e29bfd3cea779f447b13b78a6d299c81fd220a23`; blob `ca45241b4ab4689c8ceb3a7107e158367814cc1d`; PASS.
- Contract commit `5313af5ca30a0cf4201ac6b24534f2821af9d444`; blob `9ab505ee8c7de732b6e9a8928854ae99d3ebb0c7`; PASS; sealed before V166 code.
- Sole hypothesis: Guitar template evidence uses exact paired offsets `[-1,0,1,2,3,4]` instead of predecessor `[-1,0,1]`, with the same frozen `template_scores`; per-frame clipping unchanged.
- All Basic Pitch settings, onset/local-evidence logic, Guitar admission/register/segmentation/recovery thresholds, Bass logic, timebase/subdivision/grid logic, and caps remain frozen.

## V166 finalized code identities
- Event logic `6561194742093d76bab452ef0bbb0b889724dc4e`.
- Timebase builder `6a5fddf7a8a7d3cc29256a67c21a75fd0d894eab`.
- Timebase QC `5d59eda867f7252dff86faa0ec3a30bdb1c8c289`.
- Transcriber `f04ca86525b2ce71680a90b84ed476943e9e6426`.
- Structural QC `f69203ebd37c479ee06652f842f3e927e16beb9d`.
- Paired-window fixture `59fd7379bf0fe6538e44f33732b91a04e0200046`.
- Runtime-compatibility fixture `cf1eec33be04a9c4c2c0bb27425f93c2520f0a0e`.
- JSON-native fixture `bead3542375d4364db080cbe0ffce2de499ca325`.
- Negative runtime guard `fad6ea1a3d6750e86affc2214a417652c2261446`.
- Static workflow `e148c696dd77963f62129f74adccc852e84587d5`.

## V166 inherited-runtime compatibility
- Inherited V164 timebase/QC/transcriber runtime validators require legacy `frozenV162SourcePins`; V166 supplies the exact transitive frozen predecessor identities **in memory only**.
- Structural QC supplies only inherited `structuralQc` schema in an in-memory contract view.
- Sealed contract remains blob `9ab505ee...`; no musical/numeric values changed.

## V166 authoritative CPU static preflight — PASS
- Run #1 `33226280778`, job `99030569221`: PASS but superseded after runtime-compatibility hardening; no song/model execution.
- **Authoritative run #2 `33226477755`, run `2`, attempt `1`, job `99031116386`, head `cfe9a0227f87d2163ac6149ec615eecf8c2852bc`: SUCCESS.**
- Python `3.11.16`; NumPy `2.0.2`.
- Compile PASS; paired-window fixture PASS; inherited runtime-interface compatibility PASS; JSON-native PASS; negative runtime guard PASS.
- Static safety: songAudioRead=false; Demucs=false; pitchInference=false; professionalReference=false; scorer=false; V165CandidateRead=false; V165ScoreRead=false; gpu=false.

## V166 pre-run identity — SEALED PASS
- File `debug/v166-cpu-autonomous/pre-run-identity-receipt.json`.
- Commit `67c000de77542f1a7025c78732d31b1e3a0c6454`; blob `097d309d27f34ef0c02548b31a2440e3054aac00`.
- Schema `dadrock.tabs.v166.pre-run-identity-receipt.v1`; status `SEALED_AFTER_AUTHORITATIVE_STATIC_PREFLIGHT_BEFORE_SONG_PROCESSING`; PASS.
- Pins exact finalized V166 code/fixture/guard/static identities and authoritative static run.
- At seal: environment/timebase/timebase-QC/candidate/generation receipt/structural-QC/terminal/generation workflow absent; all runtime/reference/V165/GPU counters zero.

## V166 CPU environment — SEALED PASS
- Read-only song-blind workflow `.github/workflows/v166-environment-seal.yml` arm commit `a5fe0cca4e4aa40f19ec197997758174713b1b5c`; workflow blob `fe4cfcb8b30a1a70d6bbc8d9a97b93a62a258be6`.
- Environment run `33226566787`, run `1`, attempt `1`, job `99031367719`, head `a5fe0cca4e4aa40f19ec197997758174713b1b5c`; SUCCESS.
- Identity/absence gate PASS before dependency installation; exact pre-run blob `097d309...` and all finalized V166 pins matched.
- Verified Python `3.10.21`; torch `2.8.0+cpu`; `torch.version.cuda=null`; `torch.cuda.is_available()=false`.
- Exact dependencies: numpy `1.26.4`; scipy `1.13.1`; soundfile `0.12.1`; basic-pitch `0.4.0`; demucs `4.1.0`; imageio-ffmpeg `0.6.0`; librosa `0.11.0`.
- Determinism: seed `0`; Torch deterministic algorithms true; Torch threads/inter-op `1`; math-library threads `1`; `CUDA_VISIBLE_DEVICES` empty.
- Planned but not executed at seal: Demucs `htdemucs_6s`, CPU, shifts `1`, jobs `1`, repeat `1`.
- Environment receipt committed at `314d0481f84f3fc9c9a9e36edc750bf1e639a233`; blob `cec6af69f7fb0e35e25784c9cdcec5c8b5f907c1`; schema `dadrock.tabs.v166.cpu-environment-receipt.v1`; PASS.
- Receipt safety: referenceRead=false; professionalReferencePathsOpened=0; scorer=false; V165CandidateRead=false; V165ScoreRead=false; songAudioRead=false; normalization=false; Demucs=false; pitchInference=false; CUDA/GPU=false; Modal=false; main/Production=false.

## Current counters
- V165 generation `1` consumed; V165 actual score `1` consumed.
- V166 static runs `2`; authoritative #2 PASS.
- V166 pre-run identity `1` PASS; CPU environment verification `1` PASS; environment receipt `1` PASS.
- V166 song audio reads `0`; normalization `0`; Demucs `0`; timebase builds/QC `0`; pitch inference `0`; candidate generations `0`; structural-QC runtime `0`.
- V166 professional-reference/scorer reads `0`; V165 candidate/score runtime reads `0`; GPU/CUDA/Modal `0`; main/Production modifications `0`.

## Hard boundary — NEXT
1. Never reopen V163/V164/V165.
2. Both V166 pre-song seals are satisfied: pre-run blob `097d309...` and environment blob `cec6af69...`.
3. **All preparatory branch writes are complete after this checkpoint.** Audit/create `.github/workflows/v166-generate.yml` as the sole trigger for exactly one CPU generation run.
4. Generation must be run `1`, attempt `1`, CPU-only, rerun/duplicate/second-arm forbidden. Make zero assistant/manual branch writes while active.
5. The one-shot run must fresh-materialize fixed source, fresh-normalize, fresh-separate using the verified CPU environment, build a fresh V166 timebase, run independent V166 timebase QC, and **must not invoke pitch before timebase-QC PASS**.
6. Only after timebase-QC PASS may fresh pitch/transcription run, followed by independent V166 structural QC. Only structural-QC PASS may make the candidate authoritative.
7. Generation must not read professional reference/scorer, V165 candidate/score, prior generated candidates/scores, or use threshold sweep/variant selection/human correction.
8. Generation terminalization must freeze exact artifacts/run identity, self-delete workflow, and consume V166 generation forever regardless of PASS/FAIL.
9. No GPU/Modal/CUDA without fresh explicit authorization. Never modify/merge `main`/Production without explicit direction.
