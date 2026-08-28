# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 is COMPLETE / FROZEN / SCORED EXACTLY ONCE / BOTH FRONT-END GATES FAILED and is permanently consumed. V154 architecture + timebase diagnostics are COMPLETE / FROZEN. V155 was PREREGISTERED BEFORE GENERATION, but its one-use generation workflow was accidentally triggered twice (runs `33140245244` and `33140267460`) and the armed workflow was pinned to an older generator implementation that does not fully conform to the sealed preregistration/standalone-QC contract. Therefore V155 is PROTOCOL-INVALID / ABORTED BEFORE SCORING. No V155 professional-reference read or score is permitted. After the in-flight CPU runs settle, preserve their outputs only as non-authoritative protocol-failure evidence and move the clean experiment to a fresh version.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; candidate generation/transcription must not read them.
- **V154 scored candidate is consumed forever:** no modification, threshold sweep, correction, variant selection, tuned replacement, or rescoring of a modified V154 candidate.
- **V155 is protocol-invalid/aborted and must never be reference-scored.** Do not select between or promote outputs from its duplicate generation attempts.
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

## V155 — PREREGISTERED / PROTOCOL-INVALID / ABORTED BEFORE SCORING
- V155 was confirmed unused before naming.
- Preregistration: `debug/v155-cpu-autonomous/preregistration.json`; commit `e5f51474308db460d7317cfbc4204f616ee0b069`; Git blob `9d6979b0d447d137db43017dfd18c9afdcb2a4d2`; status `PREREGISTERED_BEFORE_GENERATION`.
- The preregistration seals `singleCandidate=true`, `singleGenerationRun=true`, no candidate variant selection, no threshold sweep, and reference access only after one candidate is frozen.
- Older generator: `validation/v155_cpu_multitrack/generate_v155.py`; Git blob `d1ade9d49e4cd1d599844bc054710c146d5d1d92`.
- Independent standalone QC draft: `validation/v155_cpu_multitrack/structural_qc.py`; Git blob `4a56a1b87c243dffc2ad873eef368be27e6565d0`.
- Newer implementation closer to the sealed architecture: `validation/v155_cpu_multitrack/transcribe_hybrid.py`; added by commit `b917fcfecf64f18189c0145841204fa1ebf20fca`; Git blob `3357582dd8311b28f4b85f2ebfbc7acb8c9e4fb8`.
- One-use workflow: `.github/workflows/v155-generate-reference-blind-once.yml`; staged commit `8daf1d5c828a5c039bef80b9b6fcad7565c48efb`, armed commit `0d44713bee44c47d1c0c932e98a13ab948a21756`.
- **Protocol violation:** workflow creation triggered generation run `33140245244` (run_number 1) and the later arm commit triggered generation run `33140267460` (run_number 2). Both were in-flight on CPU. This violates the sealed `singleGenerationRun=true` policy before any reference access.
- The workflow is also pinned to older generator blob `d1ade9...`, while the newer `transcribe_hybrid.py` implementation exists and is materially closer to the sealed architecture. Therefore even a technically successful old-generator output is not accepted as authoritative V155.
- Pre-run contract audit also found the older generator and standalone QC draft used incompatible candidate/receipt field names and schemas. The generation workflow uses the generator's internal QC/inline assertions instead of the independent standalone QC, so the intended independent QC contract is not satisfied by the armed workflow.
- **No V155 professional-reference read or V155 reference-facing score is allowed. V155 score calls must remain 0 forever.**
- If either in-flight run commits output, retain it only as non-authoritative protocol-failure evidence. Do not compare/select between duplicate outputs and do not score them.

### V155 reference-blind timebase audits — DIAGNOSTIC HISTORY ONLY
- First audit prereg: `debug/v155-cpu-autonomous/grid-origin-audit-preregistration.json`; Git blob `8760972bc904cc1a062f897d9dc4275f8e09aa11`; run `33139737996`, job `98747664507`; output `debug/v155-cpu-autonomous/grid-origin-audit.json`, SHA256 `9773e587032b5a531ca3d9fe25e83a69f9a08c9087a0ddd0a71ee9b23b2a55e1`.
- First audit failed structurally: global RMS activity rule incorrectly selected a late-section origin near 159 s. Never promote it.
- First audit nevertheless showed V154 onset timestamps are close to raw-audio onset peaks (~+11 ms Guitar, ~+14 ms Bass), ruling out ~1.54 s Demucs/Basic-Pitch latency as the shared timing cause.
- Second audit prereg: `debug/v155-cpu-autonomous/grid-origin-audit-v2-preregistration.json`; Git blob `b8d04ed211873c7a3966e19c14617b25fd65e52e`; canonical output `debug/v155-cpu-autonomous/grid-origin-audit-v2.json`; SHA256 `e361e97857c8fbfe4f7aa8cd484e62f40259c5e09b3c522eb630c316af77bbf2`; successful freeze run `33140076202`, job `98748730406`, branch freeze commit after rebase `038dbb32`.
- V2 audio-only result: tempo `129.19921875` BPM, 448 tracked beats, stable run from beat 0, origin `0.6849886621 s`, but 4/4 bar-phase confidence margin only ~`1.65%`. The origin is too weak to promote on confidence alone.
- V2 also demonstrates why piecewise beat-synchronous interpolation is preferable to one constant step duration: detected beat intervals vary, while forcing one BPM accumulates phase error.

## Fresh-version architecture direction preserved from V155 preregistration
When moving to the fresh successor version, preserve the architectural intent but seal a new preregistration before any run:
- CPU-only `htdemucs_6s`, shifts 1, jobs 1, dedicated Guitar and Bass stems, no fallback.
- Audio-derived dynamic beat times and piecewise-linear beat grid; no `t=0` assumption and no reference-derived offset/BPM constants.
- Bass: HPSS harmonic Bass + pYIN + onset/voicing/pitch-change segmentation; no Basic Pitch for Bass.
- Guitar: dedicated Guitar stem + one fixed Basic Pitch pass fused with independent harmonic CQT salience/onset evidence; no threshold sweep/reference-guided completion.
- Exactly one generation workflow trigger, one candidate, independent reference-blind structural QC, candidate freeze/checkpoint at score calls 0, then exactly one guarded reference score.

## Exact next steps — RESUME HERE
1. Let V155 runs `33140245244` and `33140267460` settle. Record run/job conclusions and any committed artifacts as **non-authoritative protocol-failure evidence only**. Do not inspect professional references or score V155.
2. Ensure `.github/workflows/v155-generate-reference-blind-once.yml` cannot trigger any additional V155 generation. If one run self-seals/deletes it, verify deletion; otherwise remove/disable it after in-flight runs finish, without promoting any candidate.
3. Reconcile the implementation contract in a **fresh version**: use one canonical transcriber, one candidate/receipt schema, and one independent structural-QC schema. Mechanically test those contracts before staging generation.
4. Seal the fresh-version preregistration before workflow creation. Include a trigger-safety rule: workflow creation itself is the single generation trigger; do not perform a second arm edit. Record exact generator/QC blobs in the preregistration or a pre-run immutable receipt.
5. Generate exactly one CPU candidate reference-blind; run independent structural QC; freeze candidate + receipt + QC with score calls still 0.
6. Only then build one guarded one-use score workflow and score the fresh candidate exactly once against the frozen reference/scorer.
7. Stay CPU-only unless fresh explicit user authorization is obtained immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
8. Do not resume role separation/string/fret/technique/PDF work until a front-end candidate passes acoustic gates.
