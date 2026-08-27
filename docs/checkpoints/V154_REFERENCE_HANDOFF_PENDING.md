
## V154 reference handoff — CURRENT STATE / NEXT STEPS — 2026-08-27 UTC
- **Active state:** V154 CPU multitrack reset is paused while the user fetches professional Rhythm / Lead / Bass references for **Lenny Kravitz — Are You Gonna Go My Way**. Do not run reference-facing V154 scoring until those user-provided/authorized references are normalized and frozen.
- New scorer saved: `validation/v154_cpu_multitrack/score_multitrack_reference.py`; Git blob `f58b6cf7349a6f6e5f49b241a585ba5bf3648966`; creation commit `bf7ff4c5e1d5f2aaa14816216354a78ad24712fb`.
- Reference contract: `validation/v154_cpu_multitrack/REFERENCE_FORMAT.md`; creation commit `b599d191a82ded6690e2ca203d78a13d8a1abb48`. Empty non-copyright template: `validation/v154_cpu_multitrack/reference-template.json`; creation commit `d44b684522e51a359061c15b55faa2d507540280`.
- Preferred CPU architecture is now **broad Other stem -> combined Rhythm+Lead note/onset transcription -> musical Rhythm/Lead role separation -> fret/string assignment -> techniques -> PDF**. Bass remains a separate stem/transcription/scoring path.
- Primary metrics: timing-aware pitch F1 within ±0.5 grid step for combined Guitar, Rhythm, Lead, and Bass; conditional Rhythm/Lead role-assignment accuracy; timing-aware string/fret accuracy after note+role recognition. Gross ±2-step timing is diagnostic. Per-measure pitch-content is **diagnostic only** and forbidden for event-level candidate selection after V153 Phase D/E proved it can award nonlocal credit.
- Copyright/reference boundary: **do not scrape, download, commit, or redistribute Songsterr or other third-party tablature into this public repository**. User-provided or otherwise authorized professional references may be normalized for private/ephemeral scoring. Public-repo records should keep scorer logic, schemas, hashes/manifests, and results—not third-party note-by-note tab content unless the user has publication rights.
- Leakage boundary: transcription/candidate generation may not read professional references. Freeze outputs first; references open only at scoring. No post-score retuning of the scored output and no silent candidate search.

### V154 A3 status at handoff
- Run `33088829644`, job `98575791648`: **ENGINEERING FAILURE AFTER SUCCESSFUL RAW CPU INFERENCE**.
- Exact historical audio verification and CPU normalization succeeded. Basic Pitch 0.4.0 completed CPU inference on the raw normalized mix with **572 note events**. `CUDA_VISIBLE_DEVICES` was empty and the environment used `torch 2.8.0+cpu`.
- Raw output was written and committed locally as `e515ac43`, but the push was rejected non-fast-forward because the branch changed concurrently. This is a persistence/concurrency failure, **not** a transcription-model failure.
- Demucs/Other separation did not run; separated-guitar transcription did not run; Gold/reference was never opened; score calls `0`; no human correction, threshold sweep, Modal, L4, CUDA execution, GPU, main/Production modification, or promotion occurred.
- A3 artifact `v154-cpu-pretrained-reset-a3-33088829644`, artifact ID `9653448751`, ZIP SHA256 `4f5164093744796de5a3a124b1c9cea62f65e71d0418e924218f83e490d61a84`, preserves the raw Basic Pitch JSON plus audio/runtime evidence. Do not rerun consumed A3 as-is.

### Exact next steps after the references arrive
1. **Ingest only user-provided/authorized Rhythm, Lead, and Bass references.** Inspect their format and normalize to the V154 reference contract without publishing third-party note data.
2. **Freeze reference identities before scoring:** source type, note counts, timing-grid mapping, position-data availability, and cryptographic hashes/manifests. Keep reference data inaccessible to generation code.
3. **Preregister the broad-Other CPU benchmark before opening the references.** Use Other for the combined Rhythm+Lead acoustic source and Bass separately. No threshold sweep or Gold-guided branch selection.
4. **Preserve/recover the successful A3 raw Basic Pitch evidence where useful**, but supersede the old guitar-specific separation branch with the broad-Other architecture. Any CPU rerun needed solely for persistence/runtime repair must be declared as engineering repair, not model search.
5. **Run combined-guitar recognition first:** CPU-transcribe Other and score against the union of professional Rhythm+Lead while ignoring role labels. This is the primary test of whether the acoustic frontend hears the guitar notes.
6. **Score Bass independently** from the CPU bass stem against professional Bass.
7. **Only after recognition is frozen, separate Rhythm vs Lead musically** using chord/polyphony structure, melodic continuity, repetition, note density/duration, technique trajectories, fretboard continuity, and long-range role consistency; then score conditional role accuracy.
8. **Assign strings/frets after stable notes and roles**, then score timing-aware position accuracy. Technique inference follows stable note/position inference.
9. **Generate the professional PDF only after transcription layers meet preregistered quality gates.** PDF fidelity/layout remains downstream and must not hide acoustic errors.
10. **No human correction is part of the target architecture.** No Modal/L4/CUDA/GPU execution without fresh explicit user authorization. Never modify/merge/promote `main` or Production automatically.

### Resume point
- While references are being fetched: **STOP reference-facing experimentation and preserve state**.
- On resume: normalize/freeze the references, then preregister the broad-Other CPU benchmark and success gates **before** scoring against them.
