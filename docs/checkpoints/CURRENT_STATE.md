# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163/V164/V165 are terminal and permanently closed. V165 consumed its sole authoritative generation and professional-reference score. V166 is independently preregistered from reference-free static architecture, its numeric contract is sealed, implementation is complete, authoritative CPU static preflight PASS includes inherited-runtime compatibility, and the V166 pre-run identity is now sealed PASS. No V166 song audio, normalization, Demucs, timebase, pitch inference, candidate generation, scorer/reference, V165 candidate/score runtime read, or GPU work has occurred. Next boundary: song-blind CPU environment seal. `main`/Production remain untouched.**

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
- Score report blob `ef1ba2a1a3a55db5c52a4bf3a0b80353b6b3755a`; SHA256 `0cce7f35d6d3de4bfcabcb1df3eea07893d35be9176b9e959980f47bc6c91576`; score terminal blob `3e9a5b3d6e3a5d11b2f719bdf8e808b7f2076164`; `neverRescoreV165=true`.
- Delayed-registration run #2 `33225842248` / job `99029324185` was guard-rejected before scorer; zero second score executions. Inert score workflow removed at `4d9f2dddcc1b0e5b5a87d0a7667090f1143f4799` `[skip ci]`.

## V166 preregistration / contract
- Prereg commit `e29bfd3cea779f447b13b78a6d299c81fd220a23`; blob `ca45241b4ab4689c8ceb3a7107e158367814cc1d`; PASS.
- Contract commit `5313af5ca30a0cf4201ac6b24534f2821af9d444`; blob `9ab505ee8c7de732b6e9a8928854ae99d3ebb0c7`; PASS; sealed before V166 code.
- Sole hypothesis: Guitar template evidence uses exact paired offsets `[-1,0,1,2,3,4]` instead of predecessor `[-1,0,1]`, with the same frozen `template_scores`; per-frame clipping unchanged.
- All Basic Pitch settings, onset/local-evidence logic, Guitar admission/register/segmentation/recovery thresholds, Bass logic, timebase/subdivision/grid logic, and caps remain frozen.

## V166 finalized code identities
- Event logic blob `6561194742093d76bab452ef0bbb0b889724dc4e`: exact V165 behavior, version-isolated.
- Timebase builder blob `6a5fddf7a8a7d3cc29256a67c21a75fd0d894eab`.
- Timebase QC blob `5d59eda867f7252dff86faa0ec3a30bdb1c8c289`.
- Transcriber blob `f04ca86525b2ce71680a90b84ed476943e9e6426`.
- Structural QC blob `f69203ebd37c479ee06652f842f3e927e16beb9d`.
- Paired-window fixture blob `59fd7379bf0fe6538e44f33732b91a04e0200046`.
- Runtime-compatibility fixture blob `cf1eec33be04a9c4c2c0bb27425f93c2520f0a0e`.
- JSON-native fixture blob `bead3542375d4364db080cbe0ffce2de499ca325`.
- Negative runtime guard blob `fad6ea1a3d6750e86affc2214a417652c2261446`.
- Static workflow blob `e148c696dd77963f62129f74adccc852e84587d5`.

## V166 inherited-runtime compatibility hardening
- Static audit found inherited V164 timebase/QC/transcriber runtime validators still require legacy `frozenV162SourcePins`, while sealed V166 contract intentionally uses transitive frozen V165 source pins.
- Builder/QC/transcriber now supply the exact frozen V162 predecessor identity dictionary **in memory only**; sealed contract blob remains exactly `9ab505ee...`.
- Structural QC separately supplies only inherited `structuralQc` schema in an in-memory contract view.
- No musical/numeric values were added/changed; compatibility values are exact identities inherited from frozen predecessor wrappers.

## V166 CPU static preflight
- Run #1 `33226280778`, attempt `1`, job `99030569221`, head `7cf6436c186ef72a5a1f27071ec6c342c3b78a8b`: PASS but superseded after runtime-interface hardening; no song/model execution.
- **Authoritative run #2** `33226477755`, attempt `1`, job `99031116386`, head `cfe9a0227f87d2163ac6149ec615eecf8c2852bc`: complete SUCCESS.
- Python `3.11.16`, NumPy `2.0.2`.
- Syntax compile PASS.
- Paired-window fixture PASS: exact offsets, boundary clipping, constant-time equivalence, transient dilution, runtime patch.
- Runtime-interface fixture PASS: sealed contract unchanged; timebase/timebase-QC/transcriber legacy pins supplied in memory; structural-QC schema in memory only.
- JSON-native fixture PASS.
- Negative runtime guard PASS with no failures.
- Static safety: songAudioRead=false; Demucs=false; pitchInference=false; professionalReference=false; scorer=false; V165CandidateRead=false; V165ScoreRead=false; gpu=false.
- Unrelated legacy cleanup workflow failures on feature-branch pushes are not V166 failures.

## V166 pre-run identity — SEALED PASS
- File `debug/v166-cpu-autonomous/pre-run-identity-receipt.json`.
- Commit `67c000de77542f1a7025c78732d31b1e3a0c6454`.
- Schema `dadrock.tabs.v166.pre-run-identity-receipt.v1`; status `SEALED_AFTER_AUTHORITATIVE_STATIC_PREFLIGHT_BEFORE_SONG_PROCESSING`; PASS.
- Pins exact prereg/contract, all finalized V166 code/fixtures/guard/static-workflow blobs, and authoritative static run `33226477755` / job `99031116386`.
- At seal: environment receipt, timebase, timebase-QC, candidate, generation receipt, structural-QC receipt, terminal freeze, and generation workflow all absent.
- At seal counters: reference/scorer `0`; V165 candidate/score reads `0`; song audio/normalization/Demucs/pitch `0`; GPU/CUDA/Modal `0`; main/Production modifications `0`.

## Current counters
- V165 generation `1` consumed; V165 actual score `1` consumed.
- V166 static runs `2`; authoritative run #2 PASS.
- V166 pre-run identity seals `1` PASS.
- V166 environment seals `0`; song audio reads `0`; normalization `0`; Demucs `0`; timebase builds/QC `0`; pitch inference `0`; candidates `0`.
- V166 professional-reference/scorer reads `0`; V165 candidate/score runtime reads `0`; GPU/CUDA/Modal `0`; main/Production modifications `0`.

## Hard boundary — NEXT
1. Never reopen V163/V164/V165.
2. V166 prereg/contract/code/static identities above are frozen. No further code/numeric edits unless a purely static defect is found before song processing; any code change requires a fresh authoritative static run and resealed pre-run identity before runtime.
3. Next create/run a **song-blind, read-only CPU environment seal**. It may install/verify dependencies and CPU determinism only; it must not read song audio, normalize, separate, build timebase, invoke pitch, read scorer/reference, or read V165 candidate/score runtime artifacts.
4. Environment receipt must pin the exact V166 pre-run receipt and verified CPU dependency versions/settings before any generation workflow exists.
5. Only after environment PASS may the one-shot V166 CPU generation workflow be audited/armed. Generation max `1` run / `1` attempt; no branch writes while active; fresh timebase + independent QC must PASS before pitch.
6. No GPU/Modal/CUDA without fresh explicit authorization. Never modify/merge `main`/Production without explicit direction.
