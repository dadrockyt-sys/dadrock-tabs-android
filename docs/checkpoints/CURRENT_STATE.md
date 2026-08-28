# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V160 generation is now terminal/PASS and consumed forever. The sole reference-blind CPU run completed successfully, independent timebase QC PASS and independent structural QC PASS both hold, and the fresh candidate is authoritative + eligible for exactly one separately preregistered professional-reference score. The generation workflow self-deleted and self-sealed at bot commit `4e4b4c57dafeca61bc4a829929f8c4909133cbff`. No professional-reference read or score has occurred yet for V160. Next: preregister/seal exactly one CPU professional-reference scoring run against this frozen V160 candidate; only after that scoring seal exists may the frozen scorer/reference be opened by the scoring workflow. GPU/Modal/CUDA remain 0; main/Production remains untouched.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only. Generation/transcription/postmortem/successor generation implementation must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Never retune/correct/select a replacement for a consumed scored candidate.
- **V159 is closed forever:** no re-arm, replay, regeneration, structural-QC rerun, repair-in-place, or score.
- **V160 generation is now closed forever:** no re-arm, replay, regeneration, re-QC, candidate replacement, threshold sweep, variant selection, or human correction.
- V160 may receive **at most one** professional-reference score, only through a separately preregistered/sealed scoring run.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Immutable shared identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Historical audio commit `74b0f815ff3f66f325220975c410621503de440f`.
- Audio SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; bytes `3478611`.
- Normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855` — scoring only.
- Frozen professional reference `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; Git blob `2fbed60b543c0488934d8642c488aa06bf31bbf5` — scoring only.
- Front-end score gates remain Guitar timing-aware pitch F1 >= `0.80` and Bass >= `0.80` before role/string/fret/technique/PDF work.

## Closed historical versions
- V154: one score forever; Guitar `0.04915390813859791`, Bass `0.1116751269035533`; failed.
- V155: invalid duplicate generation; score count 0 forever.
- V156: aborted before candidate; score count 0 forever.
- V157: one score forever; Guitar `0.07692307692307694`, Bass `0.05757575757575757`; failed.
- V158: one score forever; Guitar `0.007756948933419521`, Bass `0.001976284584980237`; failed/consumed.
- V159: one generation run forever; score count 0 forever; terminal `STRUCTURAL_QC_RUNTIME_FAIL`; candidate non-authoritative/ineligible for scoring; never re-arm.

## V159 frozen terminal evidence
- Run ID `33195994387`, run #1 attempt #1, job `98933144549`, CPU-only.
- Fresh `htdemucs_6s`; timebase 448 detected beats, selected phase 1; independent timebase QC PASS.
- Candidate SHA256 `a2057b0f160f8f689ea7593acb277e8a6c56325ef3183cfef58e7196907fb36c`; Guitar 2276, Bass 460.
- Structural QC crashed before receipt write due NumPy `bool_` JSON serialization.
- Terminal freeze commit `e0ab58ef5766f6c1515453c05b80e86429140acb`; candidateAuthoritative=false; scoringEligible=false; neverRearmV159=true.
- Frozen diagnoses remain at commits `1cb558d2865f96739ab5c9ef513d15c4d09f5ba4` and `4094f636ee6ab13f6eca8d43b19823f845b143b0`.

## V160 sealed design + implementation identities
- Preregistration: `debug/v160-cpu-autonomous/preregistration.json`; commit `0ab352eb781e31eb21d7329d6f08d894af02471a`; blob `cc238bcbf62c5defec410def962124d5012bd506`.
- Numeric implementation contract: `debug/v160-cpu-autonomous/implementation-contract.json`; commit `242fb649f0c01887d4de7961bb32c3d47de7ad7d`; blob `3d5ef47a998b638683c83ae08c92e45d5422f389`.
- `validation/v160_cpu_autonomous/build_timebase_v160.py`; blob `b5aa459381da6a5d5379ed8bdb1a07ba26467b63`.
- `validation/v160_cpu_autonomous/timebase_qc_v160.py`; blob `a2dba655709572d5c50dd8d4ec8656fa96eb03a3`.
- `validation/v160_cpu_autonomous/transcribe_v160.py`; blob `864f0da266816e999cd6c2750dbceb27e870b67a`.
- `validation/v160_cpu_autonomous/structural_qc_v160.py`; blob `679047e1e26b7ab4dff765dd05745317ce3f43e2`.
- `validation/v160_cpu_autonomous/test_json_native_v160.py`; blob `f2cc178c4b6a6a771a0c8f8b1527d9742f13126e`.
- `debug/v160-cpu-autonomous/negative-runtime-guard.py`; blob `e6cd45c7d8bd23a92100847f3a219c84524cbbc2`.
- Static preflight workflow `.github/workflows/v160-static-preflight.yml`; blob `1e2e16a68f72c2f7265a584256fc2402049cf940`.
- Static preflight consumed/PASS: run `33197726025`, run #1 attempt #1, job `98939034732`, head `6e6cff4c73e1a951d4154f1ddbce8550576d8cbb`; never rerun.

## V160 pre-run seals
- Immutable nested pre-run identity receipt: `debug/v160-cpu-autonomous/pre-run-identity-receipt.json`; seal commit `97333e9533b5ab4d40d2f29c31cfab771fa1e3e9`; blob `699dda80f25e0222dc7ef2f857fa65327f2d49db`; PASS.
- Reviewer audit discovered that the sealed transcriber/structural-QC implementation expected equivalent legacy flat pre-run fields. The immutable receipt was not edited.
- Runtime-compatible control-plane projection: `debug/v160-cpu-autonomous/pre-run-runtime-envelope.json`; seal commit `c27f19c2bcb07b7b45342cecede56cee8ebbf6be`; blob `a1cd82c8c5b5dc150d051b3f013ff4eb208b36a8`; PASS.
- Projection changed no generation numerics, timebase logic, pitch logic, structural-QC logic, or implementation code.
- Both pre-run seals were verified by the generation workflow before audio processing.

## V160 sole one-shot generation — TERMINAL PASS / CONSUMED
- Workflow name `V160 one-shot reference-blind CPU generation`.
- Workflow path was `.github/workflows/v160-generate.yml`; audited Git blob `35c644cb4d29341d2f7d0404b896703c7fca2da4`.
- Sole arm commit `a66d4b23ba625ee1583aa9d6f11eb0115efb2de2`; parent `f439f8abf1b270ce4cb85393bde580386ed4be84`.
- Run ID `33205440520`; run number `1`; attempt `1`; job ID `98965166224`; head SHA `a66d4b23ba625ee1583aa9d6f11eb0115efb2de2`.
- Run conclusion `success`; guard PASS; CPU pipeline PASS; terminal freeze/self-seal PASS.
- Run started `2026-08-28T19:47:53Z`; completed `2026-08-28T19:53:51Z`.
- Terminal bot commit `4e4b4c57dafeca61bc4a829929f8c4909133cbff`; message `research: freeze sole V160 reference-blind CPU candidate [skip ci]`; parent is the sole arm commit.
- Generation workflow self-deleted successfully and is absent again after terminal freeze.
- **Never re-arm or rerun V160 generation.**

## V160 CPU/environment evidence
- `debug/v160-cpu-autonomous/environment-receipt.json`; Git blob `749c2c7e58f81c6c5bded06aad74f80a16743bdc`; artifact SHA256 `591348b4c7ee96137879162acaedbae51ecad75bb893d65e702e85ed04efab70`.
- Python `3.10.21`; Torch `2.8.0+cpu`; `torch.version.cuda=null`; `cudaAvailable=false`.
- NumPy 1.26.4; SciPy 1.13.1; SoundFile 0.12.1; Basic Pitch 0.4.0; Demucs 4.1.0; imageio-ffmpeg 0.6.0; librosa 0.11.0.
- Fresh deterministic CPU `htdemucs_6s`; shifts=1; jobs=1; repeatCount=1; seed=0; Torch/math threads=1; deterministic algorithms true.
- Stem SHA256: Guitar `b8685062c59f5c62253029f8294afdaf25f3f8adf8868ae97b47db09ab8838f9`; Bass `f109347354dd9ae4a293189834b1f6d58199a4eebe5d51dfeeedc6707c4a5316`; Drums `7ef184f2fc3b6f7fc12ea5c342bc537f6b69f1680ce36e9d4f7189be85d93e39`.
- Reference read=false; reference-facing score calls=0; V159 runtime artifact read=false; CUDA/GPU=false; Modal=false; main/Production=false.

## V160 timebase + independent QC — PASS
- `debug/v160-cpu-autonomous/timebase.json`; Git blob recorded by terminal commit; artifact SHA256 `79e76bd0cea771cb92d163031f4c7645b8f0046ca651acc7e4b63a563bcb7ec8`.
- `debug/v160-cpu-autonomous/timebase-qc.json`; Git blob `f122b624bb6bdfd629947ec3a5963c7b4373b3c2`; artifact SHA256 `45cc89876921b99886cb126bd381e272968f8fc0c6affe672184f0ac81da8aa4`.
- Independent timebase QC validation PASS; every recorded check true.
- Detected beats `448`; beat-count duration BPM `127.12771798813968`; mean-IBI BPM `128.6810400651738`; median-IBI BPM `129.19921874999932`; tempo-consistency ratio approximately `1.0`.
- Timebase QC safety proves pitch inference had not yet been invoked and professional-reference paths opened=0.

## V160 fresh candidate + generation receipt
- Candidate `debug/v160-cpu-autonomous/generated.json`; Git blob `892be048486c843ae5d3268e35f84cd95b4245af`; SHA256 `db6b8428fac758d5c0fd750b797152dbd9c3f7295c3b6c6872ee631ee8c8ff76`.
- Candidate event counts: combined Guitar `2276`; Bass `460`; pre-grid excluded counts 0/0.
- Generation receipt `debug/v160-cpu-autonomous/generation-receipt.json`; Git blob `f88c8e9d6b1d84539e1837cd59da0c50262825ec`; SHA256 `3728aefc31d9987db2c1915792b3650094c46e60f1bcf446a3e4ce56de3a18ca`.
- Generation receipt status is intentionally `PENDING_INDEPENDENT_STRUCTURAL_QC`; authority is determined only by the separately written structural-QC and terminal-freeze receipts.
- Generation safety: referenceRead=false; professional paths=0; score calls=0; no prior candidate/score/diagnostic runtime reads; no threshold sweep; no variant selection; no human correction; no GPU/Modal; no Production modification.

## V160 independent structural QC — PASS
- `debug/v160-cpu-autonomous/structural-qc.json`; Git blob `5372885dfc9e07dfa8394294deafdf32c8f5a356`; SHA256 `2bb154499a849596f9e6e098df232d69a72379aa8508544dfa748797e23c3f34`.
- Validation `PASS`; errors `[]`.
- All checks true: candidate/generation/timebase schemas, candidate/generation safety, code pins, candidate hash, sealed JSON hash chain, timebase hash chain, timebase-QC hash chain, environment receipt + exact embedding, one generation workflow run, frozen grid, Guitar structure, Bass structure, stream counts, transcriber pin, write-once boundary, pre-run reference blindness, timebase reference blindness.
- The V159 `numpy.bool_` receipt failure class is repaired: structural receipt serialized successfully with native bool checks.

## V160 terminal freeze — STRUCTURAL_QC_PASS
- `debug/v160-cpu-autonomous/terminal-freeze.json`; Git blob `9690c523290955dcf0ef15074bb6746105ec0810`; schema `dadrock.tabs.v160.terminal-freeze.v1`.
- Outcome `STRUCTURAL_QC_PASS`; lastCompletedStage `STRUCTURAL_QC_PASS`.
- `candidateAuthoritative=true`.
- `eligibleForProfessionalReferenceScoring=true`.
- `neverRearmV160=true`.
- Terminal freeze pins workflow blob `35c644cb4d29341d2f7d0404b896703c7fca2da4`, immutable pre-run blob `699dda80f25e0222dc7ef2f857fa65327f2d49db`, and runtime-envelope blob `a1cd82c8c5b5dc150d051b3f013ff4eb208b36a8`.
- Terminal safety: referenceRead=false; professional paths opened=0; score calls=0; no prior candidate/score/V159 runtime read; no CUDA/GPU/Modal; main/Production=false.

## Score boundary — CURRENT
- V160 professional-reference score count is **0**.
- The candidate is now frozen and cannot be tuned, replaced, filtered, corrected, regenerated, re-QC'd, or selected among variants based on reference information.
- Exactly one professional-reference scoring execution is allowed after a separate score preregistration/seal.
- The score must use the frozen candidate SHA256 `db6b8428fac758d5c0fd750b797152dbd9c3f7295c3b6c6872ee631ee8c8ff76`, frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`, and frozen reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5` / SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Score gates remain Guitar timing-aware pitch F1 >= `0.80` and Bass >= `0.80`.
- Regardless of score, this candidate is consumed after that single score and cannot be modified/re-scored.

## Current hard boundary
- V159 terminal forever.
- V160 generation terminal/PASS and consumed forever; never re-arm generation.
- No professional reference/scorer content may be opened until the one-shot V160 scoring plan is separately preregistered and sealed.
- Do not modify the frozen V160 candidate or any generation/QC artifact.
- V160 score maximum = 1; current score count = 0.
- No GPU/Modal/CUDA without fresh explicit user authorization.
- Never touch `main`/Production without explicit user direction.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before every write.
2. Create a **V160 scoring preregistration/identity seal before opening the scorer or professional reference**. It must pin: terminal commit `4e4b4c57dafeca61bc4a829929f8c4909133cbff`; generation run `33205440520` #1 attempt #1 job `98965166224`; candidate SHA256 `db6b8428fac758d5c0fd750b797152dbd9c3f7295c3b6c6872ee631ee8c8ff76`; structural-QC PASS receipt SHA256 `2bb154499a849596f9e6e098df232d69a72379aa8508544dfa748797e23c3f34`; terminal-freeze blob `9690c523290955dcf0ef15074bb6746105ec0810`; frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`; frozen reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5` + SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; gates Guitar/Bass >=0.80; one score only; no rerun.
3. Preregistration must explicitly state candidate frozen before reference read; no tuning/repair/selection after scoring; score workflow creation is sole trigger; expected score run #1 attempt #1; workflow self-deletes/self-seals after one score.
4. Only after the scoring preregistration is sealed may reviewer work open the frozen scorer/reference for the scoring-only purpose and construct/audit the exact CPU score workflow.
5. Arm exactly one CPU score workflow by its sole creation commit. While active, no assistant/manual branch writes; read-only observation only.
6. After the scoring workflow self-seals, update this checkpoint with exact score/run/job/head/receipt identities and consume V160 forever regardless of pass/fail.
7. If both Guitar and Bass meet >=0.80, proceed to preregister the next role/string/fret/technique/PDF phase. If either misses, V160 remains closed and successor design may use only the allowed frozen score evidence under a new preregistration; never retune V160.
8. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
