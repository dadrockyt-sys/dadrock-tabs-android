
## V154 explicit next steps — FROZEN EXECUTION ORDER — 2026-08-27 UTC
- This section is the authoritative resume order for the current V154 CPU-only architecture reset after the three professional references were received and identity-frozen.
- Goal remains **fully automatic audio -> professional-quality guitar/bass tablature PDF with no human correction**.
- Cost/execution preference remains **CPU-only whenever possible**. Fresh explicit user authorization is required immediately before any Modal / NVIDIA L4 / CUDA / GPU execution. CPU work and CPU scoring are at assistant discretion.
- Branch remains `v143-contextual-prune-lobo`. Never modify, merge, promote, or otherwise touch `main` or Production unless the user explicitly changes that policy.
- Do not return to one-event V153-style Gold-guided micro-corrections as the main path. V154 is an architecture benchmark/reset.
- Professional Rhythm, Lead, and Bass references are **scoring-only**. Generation/transcription code must not read them. Freeze generated outputs first; open normalized references only at the scoring boundary. No silent variant search and no post-score retuning of the same scored output.

### Exact resume sequence
1. **Privately normalize the frozen Rhythm, Lead, and Bass references** into the V154 scoring contract. Preserve measure numbering, rests/blank measures, note onsets, pitches, string/fret positions when visible, bends/slides/techniques where representable, and all uncertainty annotations. Do not commit user-uploaded screenshot bytes or note-by-note copyrighted reference content to the public repo.
2. **Freeze normalized reference identities** with cryptographic hashes, note/event counts, timing-grid mapping, position-data availability, uncertainty-mask locations, and source-manifest linkage. The normalized reference data itself remains private/ephemeral.
3. **Preregister the broad-Other CPU benchmark before reference-facing scoring.** Freeze: source audio identity; separator model/version/settings; `Other` and Bass stem definitions; CPU note-transcriber model/version/settings; sample-rate/audio normalization; timing grid; note matching tolerance; metric definitions; failure handling; and hard success gates. No threshold sweep chosen from Gold results.
4. **Repair/supersede the consumed V154 A3 persistence path without treating repair as model search.** Preserve the successful A3 evidence that Basic Pitch 0.4.0 completed CPU inference on the raw mix with 572 note events. Do not rerun consumed A3 as-is. Any necessary rerun must be a declared engineering/persistence repair or a new preregistered architecture benchmark.
5. **Run CPU source separation on the historical song audio.** Treat broad `Other` as the combined Rhythm+Lead acoustic source. Keep Bass as its own stem. Do not ask the separator to distinguish Rhythm versus Lead.
6. **Run the frozen CPU note/onset transcriber on `Other` and Bass without reference access.** Produce a combined-guitar event stream and a Bass event stream. Do not use professional tabs to choose notes, thresholds, octave corrections, or timing.
7. **Freeze generated transcription identities before scoring:** event JSON hashes, model/runtime versions, audio/stem hashes, note counts, timing metadata, and deterministic replay evidence where feasible.
8. **Primary acoustic-front-end test: score combined Guitar first** against the union of professional Rhythm+Lead, ignoring role labels. Primary metric is timing-aware pitch F1 at ±0.5 grid step; gross ±2-step timing is diagnostic. Per-measure pitch-content/histogram scoring is diagnostic only and must not drive event-level conclusions.
9. **Score Bass independently** with the same timing-aware note/onset framework. Report precision, recall, F1, timing error distribution, missed-note/extra-note counts, and performance by song section where possible.
10. **Make the first architecture decision from recognition results, not PDF appearance.** If combined-Guitar/Bass acoustic recognition is materially weak, improve/replace the CPU separation/transcription front end before working on fret assignment or notation polish. Do not hide recognition errors downstream.
11. **Only after combined Guitar recognition is frozen, perform Rhythm-versus-Lead role separation reference-free.** Use musical evidence such as polyphony/chord density, melodic continuity, repetition, note duration/density, register only as one weak feature, technique trajectories, fretboard continuity, and long-range role consistency. Do not split roles by fixed MIDI ranges.
12. **Freeze the role assignment, then score conditional Rhythm/Lead role accuracy** against the professional references. Distinguish acoustic note-recognition failures from role-assignment failures.
13. **Only after notes and roles are stable, infer guitar string/fret positions.** Prefer a sequence/playability-aware fretboard decoder over local pitch-to-fret heuristics. Then score timing-aware string/fret correctness conditional on correctly recognized pitch+role.
14. **Technique inference follows stable notes/positions:** bends, slides, vibrato, palm muting, hammer-ons/pull-offs, dead notes, etc. Score techniques separately so technique errors do not obscure core note recognition.
15. **Professional PDF generation is last.** Render Rhythm, Lead, and Bass tracks only after upstream gates are met. Evaluate notation/layout/PDF fidelity separately from acoustic correctness.
16. **Decision gate:** continue toward fully automatic production only if the architecture shows a credible path on this real song without human correction. If a modern CPU-only front end cannot approach the preregistered recognition gates, reconsider model class/separation strategy before spending more time on heuristic patches.

### Planned initial success gates to preregister before scoring
- Combined Rhythm+Lead timing-aware note/pitch F1: target **>= 0.80**.
- Bass timing-aware note/pitch F1: target **>= 0.80**.
- Onset-aware note F1: target **>= 0.75**.
- Rhythm/Lead role accuracy conditional on correctly recognized guitar notes: target **>= 0.85**.
- String/fret correctness conditional on correct pitch+role: target **>= 0.85**.
- These are architecture decision gates, not permission to tune against Gold. If a gate is missed, diagnose the responsible stage and preregister a genuinely new architecture/model change before another reference-facing score.

### Immediate next action on resume
- **Do not score yet.** First complete private reference normalization/freeze and write the broad-Other CPU benchmark preregistration. Then execute separation/transcription reference-free, freeze outputs, and only then open the references for the first combined-Guitar and Bass score.
