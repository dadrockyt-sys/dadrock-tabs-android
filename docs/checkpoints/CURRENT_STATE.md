# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 is COMPLETE / FROZEN / SCORED EXACTLY ONCE / BOTH FRONT-END GATES FAILED and is permanently consumed. V154 architecture + timebase diagnostics are COMPLETE / FROZEN. V155 is PROTOCOL-INVALID / ABORTED BEFORE SCORING: its supposedly one-use generation workflow triggered twice, both runs created different candidate bytes from the same nominal configuration, and one non-authoritative output was committed. V155 must never read the professional reference or be scored. Clean successor V156 is PREREGISTERED BEFORE GENERATION at commit `2b4b6a593e1191f62f40f5feabb92bf4d046ce4e`; no V156 candidate exists and V156 score calls are 0. Next: amend V156 preregistration before generation to freeze deterministic Demucs RNG handling, then implement/test one canonical generator + independent QC contract before creating the one-and-only generation workflow.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; candidate generation/transcription must not read them.
- **V154 scored candidate is consumed forever:** no modification, threshold sweep, correction, variant selection, tuned replacement, or rescoring of a modified V154 candidate.
- **V155 is protocol-invalid/aborted and must never be reference-scored.** Do not select between or promote outputs from its duplicate generation attempts.
- **V156 currently has no candidate and no reference access.** Any V156 generation must obey the sealed one-run/one-candidate protocol.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Target remains fully automatic audio -> professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Song / immutable shared identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Audio: `public/gomywayfullaitest.m4a`; SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Source m104 = 2/4 (8 sixteenth steps); others 4/4.
- Meter map: `research/v154-professional-references/source-meter-to-fixed-grid-mapping.json`; SHA256 `1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648`.
- Frozen scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.

## Professional references — AUTHORITATIVE / FROZEN
- **Rhythm:** `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json`; 946 rows; SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`; equivalence PASS.
- **Lead:** `research/v154-professional-references/scorer-ready/lead-scorer-ready.json`; 447 pitched rows; SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`.
- Lead timing: `research/v154-professional-references/lead-source-local-attack-timing.json`; SHA256 `a1c30e9a14048fac6da6801d1ace1db203daf8807511f26c76a268e3cbf426c3`.
- **Bass:** `research/v154-professional-references/scorer-ready/bass-scorer-ready.json`; 547 pitched rows; SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`.
- Bass timing: `research/v154-professional-references/bass-source-local-attack-timing.json`; SHA256 `7d2f4eed21413c6169ec8fcea75274b64c6dc8bb5f3c8de9cbc536b94afab244`.
- Lead rendered pages 84–105 were recovered and byte-authenticated; screenshot bytes remain uncommitted.
- Combined immutable reference: `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; Guitar 1393 / Bass 547; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; freeze run `33138868905`, job `98744968281`, commit `46e42ab`.

## V154 — CONSUMED / ONE SCORE PERMANENTLY CLOSED
### Candidate
- `debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json`; SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`.
- Run `33096559281`, job `98602884120`, head `986e2a69a6cb877a203d2f8b04115914dc8fd2e6`; Guitar 1089 / Bass 635.
- Historical artifact id `9656706944`; digest `sha256:f0944432c37b369ac38cd25d058265a76f36b23e2f0bcf9808880d9e141dc518`.

### Frozen score
- `debug/v154-cpu-autonomous/v154-frontend-reference-score/score.json`; SHA256 `c206f6bc951c6bd9b6cc19e6758c4aef6654f349cc1f5712df1f052e46fa798b`.
- Receipt: `debug/v154-cpu-autonomous/v154-frontend-reference-score/score-receipt.json`; validation PASS; `referenceFacingScoreCalls=1`; wrapper invocation count 1.
- Run `33139017517`, job `98745430956`; freeze commit `f687153`.
- Guitar primary timing-aware pitch F1 `0.04915390813859791` — FAIL vs 0.80.
- Bass primary timing-aware pitch F1 `0.1116751269035533` — FAIL vs 0.80.
- **V154 reference-facing score count is permanently 1.**

### Frozen diagnostics / caveats
- Architecture diagnostic: `debug/v154-cpu-autonomous/v154-frontend-reference-score/architecture-diagnostic.json`; SHA256 `bcc7aa275fb9c8dab3e0e9350043c5d85d48788bc13c672d97ad949d4d5595cd`; run `33139198143`, job `98746009145`, commit `b6a7637`.
- Caveat: its `measureIndexShiftScanPitchContent` is invalid/no-op because the same shift-bearing key was applied to generated and reference rows. Disregard that submetric. `globalAbsoluteShiftScan` remains valid because it shifts generated positions only.
- Timebase diagnostic: `debug/v154-cpu-autonomous/v154-frontend-reference-score/timebase-diagnostic.json`; SHA256 `ddaddaa4cfff1de1b5e7466813d9e08cfaeb9451b5a08406e820209543fe2f3c`; run `33139677372`, job `98747482513`, commit `e87f81e`.
- Timebase tie-break can favor proximity to prior `-13.25` on equal match counts; exact reference-derived shift/BPM values are diagnostic only and never future candidate parameters.
- Both diagnostics imported/called no official scorer, added 0 official score calls, wrote no corrected candidate, and were CPU-only.

## V154 root cause — FROZEN ARCHITECTURE DIAGNOSIS
- Historical transcriber blob `2f09ca1b8bc012749468f0079497ded71d318782` mapped `absolute_step_float = seconds / STEP_SECONDS`, hard-anchoring musical grid step 0 to audio/stem timestamp `0.000 s`.
- V154 had no audio-derived beat/downbeat/phase origin estimation and no explicit Demucs/Basic-Pitch latency compensation.
- Valid diagnostic global shift: both streams prefer about `-13.25` sixteenth steps, but this is **not** a permitted correction and does not solve recognition.
- Section trend is nonconstant: Guitar early `-11.50` -> late `-13.25`; Bass `-11.50` -> `-13.50`; shared slope indicates cumulative timebase drift as well as origin error.
- Large residual pitch/polyphony errors remain, so timing repair alone cannot pass gates.
- Never hardcode reference-derived `-13.25` or diagnostic ~129.01 BPM in a future generator.

## V155 — PROTOCOL-INVALID / ABORTED / NEVER SCORE
- Preregistration: `debug/v155-cpu-autonomous/preregistration.json`; commit `e5f51474308db460d7317cfbc4204f616ee0b069`; Git blob `9d6979b0d447d137db43017dfd18c9afdcb2a4d2`; sealed `singleCandidate=true`, `singleGenerationRun=true`, no variant selection/sweep, reference access only after one frozen candidate.
- Old generator: `validation/v155_cpu_multitrack/generate_v155.py`; Git blob `d1ade9d49e4cd1d599844bc054710c146d5d1d92`.
- Standalone QC draft: `validation/v155_cpu_multitrack/structural_qc.py`; Git blob `4a56a1b87c243dffc2ad873eef368be27e6565d0`.
- Better-aligned later implementation: `validation/v155_cpu_multitrack/transcribe_hybrid.py`; commit `b917fcfecf64f18189c0145841204fa1ebf20fca`; Git blob `3357582dd8311b28f4b85f2ebfbc7acb8c9e4fb8`.
- Workflow `.github/workflows/v155-generate-reference-blind-once.yml` was staged at `8daf1d5c828a5c039bef80b9b6fcad7565c48efb` and then unnecessarily armed at `0d44713bee44c47d1c0c932e98a13ab948a21756`, causing **two generation runs**.

### Duplicate-run outcomes — non-authoritative protocol-failure evidence only
- **Run 1:** `33140245244`, job `98749260662`, final conclusion FAILURE because freeze/rebase conflicted after candidate creation. Generation/internal structural QC itself PASS.
  - Guitar stem SHA256 `15f5ee8ce9039b36d9d7624b95f140809bde28a231d2e4efcb90e2045364dba2`.
  - Bass stem SHA256 `bb79d0b636bfe97bd33475160000170422d80fd06474b535632a1ad9f6f598b3`.
  - Drums stem SHA256 `6774c3ebfde07aa24b69506e4d2554c789949595bb9f3a3c2d59439b0f8da618`.
  - Candidate SHA256 `5ca0fd218a6efd5ea8765590b259f8d8510697c8487bf3ef65a3d9339054dc51`; Guitar 1364 / Bass 79.
  - Beat count 452; downbeat phase 2; originBeatIndex -2; robust median tempo ~129.19921875.
- **Run 2:** `33140267460`, job `98749332172`, SUCCESS and self-sealed/deleted the V155 workflow.
  - Guitar stem SHA256 `ba1de21eee68e34c29f951812bddf8c38e7bc47fa1034ae7ee2cbc42b723b696`.
  - Bass stem SHA256 `cc7b66be0a6168c546b407ae824819ed99d71ef73dcc195b7de9fec76f62b0c1`.
  - Drums stem SHA256 `456d3e01309cd05dc0d6ba93036f7abd35d7a5001e74f0072e9944064ad5e581`.
  - Candidate SHA256 `cb5275aab111153f098e4f2e8b94ccf88d5d0052e2f528133702e870dac137ea`; Guitar 1359 / Bass 81.
  - Beat count 452; downbeat phase 2; originBeatIndex -2; robust median tempo ~129.19921875.
  - Branch freeze commit after rebase: `58b8c7d00a9c7e868531eb0ecab0c48507c7aa77`.
  - Non-authoritative committed evidence paths: `debug/v155-cpu-autonomous/generated.json` and `debug/v155-cpu-autonomous/generation-receipt.json`.
- The differing stem hashes and candidate hashes/counts prove the staged `htdemucs_6s --shifts 1` execution was **not deterministic** under the two nominally identical runs. This is execution/protocol evidence only; do not compare/select based on musical quality.
- V155 workflow is now self-sealed/deleted by successful run 2, so no further trigger should occur.
- **V155 professional-reference reads = 0; V155 reference-facing score calls = 0 and permanently forbidden.**

### V155 reference-blind timebase audits — DIAGNOSTIC HISTORY ONLY
- First audit prereg: `debug/v155-cpu-autonomous/grid-origin-audit-preregistration.json`; Git blob `8760972bc904cc1a062f897d9dc4275f8e09aa11`; run `33139737996`, job `98747664507`; output `debug/v155-cpu-autonomous/grid-origin-audit.json`, SHA256 `9773e587032b5a531ca3d9fe25e83a69f9a08c9087a0ddd0a71ee9b23b2a55e1`.
- First audit failed structurally: global RMS activity rule incorrectly selected a late-section origin near 159 s. Never promote it.
- It nevertheless showed V154 onset timestamps close to raw-audio onset peaks (~+11 ms Guitar, ~+14 ms Bass), ruling out ~1.54 s Demucs/Basic-Pitch latency as the shared timing cause.
- Second audit prereg: `debug/v155-cpu-autonomous/grid-origin-audit-v2-preregistration.json`; Git blob `b8d04ed211873c7a3966e19c14617b25fd65e52e`; canonical output `debug/v155-cpu-autonomous/grid-origin-audit-v2.json`; SHA256 `e361e97857c8fbfe4f7aa8cd484e62f40259c5e09b3c522eb630c316af77bbf2`; run `33140076202`, job `98748730406`, freeze commit `038dbb32`.
- V2 audio-only result: tempo `129.19921875` BPM, 448 tracked beats, stable from beat 0, origin `0.6849886621 s`, but bar-phase margin only ~1.65%; do not promote origin on confidence alone.
- V2 supports piecewise beat-synchronous interpolation instead of fixed step duration.

## V156 — CLEAN SUCCESSOR / PREREGISTERED / NO CANDIDATE
- Confirmed unused before naming.
- Preregistration: `debug/v156-cpu-autonomous/preregistration.json`.
- Commit `2b4b6a593e1191f62f40f5feabb92bf4d046ce4e`; current Git blob `bbad04a6f2076cde2ec2a266ec321c151d9b5868` before deterministic-RNG amendment.
- Status `PREREGISTERED_BEFORE_GENERATION`.
- **V156 candidate: NONE. V156 reference read: NO. V156 score calls: 0.**
- Architecture intentionally inherits the sealed V155 design without reference/quality tuning:
  - CPU-only `htdemucs_6s`, shifts 1, jobs 1, dedicated Guitar/Bass/Drums.
  - Audio-derived dynamic beat times + 4/4 phase + piecewise-linear beat-grid mapping; no `t=0` assumption and no reference-derived timing constants.
  - Bass = HPSS harmonic + pYIN + onset/voicing/pitch-change segmentation; no Basic Pitch for Bass.
  - Guitar = dedicated Guitar stem + single fixed Basic Pitch pass fused with harmonic CQT evidence; no threshold sweep/reference-guided completion.
  - Exactly one candidate; one generation run; independent structural QC required before freeze.
- Canonical V156 contract is already preregistered:
  - candidate schema `dadrock.tabs.v156.cpu-hybrid-generated.v1`.
  - receipt schema `dadrock.tabs.v156.cpu-hybrid-generation-receipt.v1`.
  - independent QC schema `dadrock.tabs.v156.reference-blind-structural-qc.v1`.
  - required event key `absoluteGridStep` plus `measure/step/midi/startSeconds/rawGridStep/source`.
- Trigger safety: workflow creation itself is the single generation trigger; **second arm edit forbidden**; duplicate run => abort V156 and move to a new version.
- V156 explicitly pins `scipy==1.13.1` and `soundfile==0.12.1` in addition to other frozen deps; workflow must install these exact versions rather than accepting newer transitive versions.

## V156 required pre-generation amendment — EXECUTION DETERMINISM ONLY
- V155 duplicate-run evidence revealed `htdemucs_6s --shifts 1` yielded different stems on two nominally identical CPU executions. This finding occurred **before any V156 generation/reference access**, so V156 preregistration may be amended to freeze deterministic RNG handling without changing musical architecture.
- Amendment must preserve `htdemucs_6s`, shifts=1, jobs=1. It must not tune quality or use any reference information.
- Freeze a single RNG seed (recommended `0`) for Python `random`, NumPy, and Torch before Demucs separation.
- Prefer in-process `demucs.separate.main(...)` after seeding so the RNG state applies to the random-shift path; a fresh `python -m demucs` subprocess can lose the parent seed.
- Record seed, Torch determinism settings, thread settings, model checkpoint identity, and resulting stem hashes in the environment/generation receipt.
- If deterministic Torch algorithms are unsupported by Demucs, treat it as a pure pre-candidate setup failure and adjust only execution determinism mechanics, never recognition parameters.

## Exact next steps — RESUME HERE
1. Amend `debug/v156-cpu-autonomous/preregistration.json` **before any V156 generation** to freeze deterministic Demucs RNG/thread handling while preserving `htdemucs_6s`, shifts=1, jobs=1 and all recognition parameters.
2. Implement one canonical V156 transcriber by adapting the already-written V155 `transcribe_hybrid.py` architecture only; change version/contracts and eliminate schema ambiguity. Do not read V155 generated musical output.
3. Implement one independent V156 structural-QC script matching the preregistered V156 candidate/receipt schemas exactly.
4. Mechanically/static-audit generator + receipt + QC contract before any workflow creation. Pin exact generator/QC Git blobs in a pre-run receipt/checkpoint.
5. Save checkpoint. Then create `.github/workflows/v156-generate-reference-blind-once.yml` **once**; workflow creation is the only trigger. Do not perform a later arm edit. Assert workflow run number = 1, CPU-only execution, exact audio/prereg/generator/QC blobs, and zero reference access.
6. During V156 generation, make no unrelated branch writes until the workflow freezes/self-seals, minimizing rebase-conflict risk.
7. Workflow must deterministically normalize audio, seeded in-process `htdemucs_6s` separation, run canonical V156 transcriber, run independent structural QC, then freeze candidate + generation receipt + QC and delete itself. Reference-facing score calls remain 0.
8. After V156 freeze, checkpoint and verify exactly one generation workflow run, one candidate, independent QC PASS, stable hashes, and no reference access.
9. Only then create a guarded one-use V156 score workflow and score exactly once against frozen reference/scorer. Never retune a consumed V156 candidate.
10. Stay CPU-only unless fresh explicit user authorization is obtained immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
11. Do not resume role separation/string/fret/technique/PDF work until a front-end candidate passes acoustic gates.
