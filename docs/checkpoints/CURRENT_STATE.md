# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-27 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 broad-Other CPU benchmark COMPLETE / SUCCESS / SEALED. Frozen generated combined-Guitar + Bass output exists. Reference-facing scoring has NOT run.**

## History preservation
- Full checkpoint before this compact continuation: commit `3705b8aba3f166000867f7c68e5dfc104bc71fd9`; checkpoint blob `5a19f89583af89e777380d5ddb453c4957afe5f5`.
- Immediately preceding compact checkpoint before benchmark arming: blob `f64ee7e35536449026b3c208475c3e5083d33458`.
- Earlier pre-compaction history: `docs/checkpoints/archive/CURRENT_STATE-pre-phase-c-auth-intake-20260827.md`; blob `f71ba11394e6f2f46843055e748e8717ff484158`.
- Old consumed V147–V153 one-use runs remain sealed and non-reusable.

## Standing authorization / safety
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only. Generation/transcription must not read them.
- Freeze generated outputs before reference access. No silent variant search; no post-score retuning of the same scored output.
- Do not commit user-uploaded professional-tab screenshots or note-by-note copyrighted reference data to this public repository.
- Target: fully automatic audio -> professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## V153 sealed conclusion
- V153 event-347 attribution proved the aggregate pitch-content deficit was a coarse measure-level `(measure, MIDI)` histogram effect, not local event timing/chord evidence.
- Per-measure pitch-content is diagnostic only for V154 and must not drive event-level selection.
- V154 is an architecture reset, not another one-event Gold-guided micro-correction path.

## V154 pre-reset engineering history
- A1 `33087772583`: TFLite/NumPy ABI engineering failure before transcription; sealed.
- A2 `33088418439`: Basic Pitch CPU inference succeeded; JSON persistence failed on nested NumPy scalar metadata; sealed.
- A3 `33088829644`: raw Basic Pitch CPU inference succeeded with **572 notes**, but repository persistence push failed non-fast-forward; Demucs/reference scoring did not run; score calls `0`; sealed and must not be rerun as-is.
- A3 established deterministic normalization: **44.1 kHz, stereo, PCM s16le**, using imageio-ffmpeg. Runtime evidence: Python 3.10, NumPy 1.26.4, PyTorch 2.8.0+cpu, CUDA unavailable.

## Frozen professional reference identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Rhythm: existing `main:public/Professionalexample.jpg`; Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`; receipt `debug/v154-cpu-autonomous/reference-receipts/rhythm-existing-professionalexample-20260827.json`.
- Bass: 17 user screenshots, visible measures 1–113; set SHA256 `abd1748066966ceb93fe40bf8c8df3168f6c871ba006e44d28f8840184e3cde3`; measure-88 `Timing mishap here` remains an uncertainty flag.
- Lead: 22 user screenshots, visible measures 1–113; set SHA256 `de2f20c330e52aca6125e29ca2cf5c4b719406fc267a98d43d98f3ab1453ff3c`; opening tempo quarter=129, 4/4; visible measures 39–40 uncertainty annotation remains flagged.
- Three-part manifest: `debug/v154-cpu-autonomous/reference-receipts/reference-set-manifest-20260827.json`; commit `4eae3fa541c1cbede282db20c113a22f7b906fbb`.
- Raw Bass/Lead screenshot bytes are not available in this active ChatGPT conversation/Library. Do not guess or reconstruct their note content from receipts or memory.

## V154 frozen broad-Other protocol
- Preregistration: `debug/v154-cpu-autonomous/broad-other-preregistration.json`; creation commit `69102364d79c315044c994ff0acaf52dbc827dd5`; Git blob `eb81efbb1ed25b023b5bce6e1159ae7785875b4a`.
- Historical audio: commit `74b0f815ff3f66f325220975c410621503de440f`, `public/gomywayfullaitest.m4a`, `3478611` bytes, SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Grid: tempo `129.19921875`, 4 steps/beat, 16 steps/measure, 113 measures.
- Separator: CPU `demucs==4.1.0`, model `htdemucs`, shifts `1`, jobs `1`; `Other` = combined Rhythm+Lead acoustic source; `Bass` independent.
- Transcriber: Basic Pitch `0.4.0`, onset `0.5`, frame `0.3`, minimum note length `127.7 ms`, melodia enabled, no threshold sweep; combined Guitar MIDI `40–88`, Bass MIDI `28–67`.
- Runtime: Python 3.10, NumPy 1.26.4, PyTorch 2.8.0+cpu, imageio-ffmpeg 0.6.0; CUDA absent/unavailable.
- Transcriber: `validation/v154_cpu_multitrack/transcribe_broad_other.py`; creation commit `c4a707d34b1a44dc34a8245f922773d43f0538cf`; blob `2f09ca1b8bc012749468f0079497ded71d318782`.

## Stage-one scorer / validation
- Scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`; creation commit `a5cab589b3efca8ec454311c49120543c04277fb`; blob `13936b70555bb1b3a9e4f83767376fd5d8b1bc51`.
- Combined Guitar is scored against private Rhythm+Lead union before role splitting; Bass scored independently.
- Primary metric: same-MIDI one-to-one onset matching within ±0.5 grid step; ±2 gross timing diagnostic; per-measure pitch-content diagnostic only.
- Explicit uncertain reference events may use `excludeFromScoring=true`; no silent repair.
- Synthetic/reference-free tests: `validation/v154_cpu_multitrack/test_frontend_contract.py`; commit `69457239e304970a4b0c933dcaf708351d6b220b`.
- Authoritative one-use test run `33096282137`, job `98601930286`: **SUCCESS**. Workflow sealed at commit `5dd4182ed0eaaa5d6e8da5da19c26fc2b5b1a7d7`.
- Redundant synthetic run `33096281645` is non-scientific duplicate validation and remains sealed; its workflow was removed at commit `477be95555d13e24621349b1b9edfaf834dc2a8d`.

## V154 architecture decision gates — FROZEN
- Combined Rhythm+Lead timing-aware note/pitch F1 target: **>= 0.80**.
- Bass timing-aware note/pitch F1 target: **>= 0.80**.
- Onset-aware note F1 target: **>= 0.75**.
- Later conditional Rhythm/Lead role accuracy target: **>= 0.85**.
- Later conditional string/fret correctness target: **>= 0.85**.
- Missing a gate diagnoses the responsible architecture stage; it is not permission to tune the consumed output against reference truth.

## Broad-Other CPU benchmark — COMPLETE / SUCCESS / SEALED
- Authoritative one-use run: **`33096559281`**, job **`98602884120`**, head SHA `986e2a69a6cb877a203d2f8b04115914dc8fd2e6`.
- Every benchmark step passed: frozen protocol verification; exact historical audio identity; CPU-only runtime/CUDA assertions; deterministic normalization; CPU Demucs separation; frozen Basic Pitch transcription; generation manifest; immutable artifact upload.
- One-use workflow `.github/workflows/v154-broad-other-cpu-once.yml` was sealed/deleted after the run at commit `e969790e760dba4cf544521f2640cc130dc05d44`. **Do not rerun this consumed workflow.**
- Immutable artifact ID `9656706944`, name `v154-broad-other-cpu-33096559281`, size `99782` bytes, digest `sha256:f0944432c37b369ac38cd25d058265a76f36b23e2f0bcf9808880d9e141dc518`; downloaded ZIP SHA256 independently verified identical. Artifact expires `2026-09-26T17:07:48Z`.
- Normalized WAV: `37298398` bytes, SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Combined Guitar (`Other`) stem: `37298220` bytes, SHA256 `c288232d1fff42f0fcf57e3e46dfd274428cb2d4e1c916f7fe663d28d42b1440`.
- Bass stem: `37298220` bytes, SHA256 `918670e9293b5aa633593fbe491ff520a045774ead7cbdba0a851301d4e86b0f`.
- Basic Pitch model SHA256 `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`.
- Frozen generated output: `generated.json`, `1145129` bytes, SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`.
- Frozen generated counts: **1089 combined-Guitar note events**, **635 Bass note events**.
- Durable public identity manifest: `debug/v154-cpu-autonomous/broad-other-run-33096559281-result.json`; creation commit `07ca01dc67c8e4fd68af8fd20d7acf62b61c3bde`.
- These counts are **not accuracy scores**. They are generated-output identity only and must not be interpreted as quality evidence before professional reference scoring.
- Reference/Gold inputs were absent from generation. Reference-facing score calls: **0**. Human correction: **NO**. Threshold sweep: **NO**. Modal/L4/CUDA/GPU: **NO**. `main`/Production modification: **NO**.

## Current execution status
- Reference-facing score calls this continuation: **0**.
- Professional reference note data opened this continuation: **NO**.
- Stage-one synthetic tests: **PASS / SEALED**.
- Broad-Other CPU benchmark: **PASS / OUTPUT FROZEN / WORKFLOW SEALED**.
- Modal/L4/CUDA/GPU used: **NO**.
- `main` / Production modified: **NO**.

## Exact next steps
1. Run reference-free structural QC on the already-frozen `generated.json` only (grid bounds, duration/onset sanity, MIDI-range enforcement, duplicate/overlap diagnostics, measure coverage). This may diagnose engineering defects but must not retune the frozen output.
2. Persist only QC/identity metadata; do not expose or reconstruct professional reference note content.
3. Do **not** reference-score generated outputs until the privately normalized Rhythm/Lead/Bass payload is accessible and its normalized identity is frozen. Current chat has no raw Bass/Lead screenshot bytes.
4. Once private normalized references are accessible, score the frozen combined Guitar first and Bass second **exactly once** with `score_frontend_reference.py`; no post-score retuning of this consumed generated output.
5. Only after acoustic recognition is frozen/scored should Rhythm/Lead role separation, fret/string assignment, techniques, and PDF work continue.
6. Continue saving this checkpoint after each meaningful QC/result freeze.
