# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **Active phase: V144 Rhythm calibration/retraining toward the professional human-written reference target for the `/ai-tab` product. V5 remains permanently frozen and may not be modified or rescored. Do not start Bass/Lead until Rhythm V144 quality is proven or the user explicitly redirects.**

## Product focus — `/ai-tab`
- User-facing product flow: `dadrocktabs.com/ai-tab` → user uploads audio → selects Rhythm, Bass, or Lead → receives a professional-quality PDF preview → optional purchase unlocks the full professionally rendered PDF.
- Page construction is centered at `app/ai-tab/page.js`.
- The scorer is an engineering quality/evaluation gate for the transcription engine. The scorer itself is not the end product.
- The desired end result is a musically accurate, professionally readable tablature PDF preview and, after purchase/unlock, the full professionally rendered PDF.

## Hard boundaries — NOW PERMANENT FOR V5
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` remains required at Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved source SHA256 remains `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Frozen V5 is irreversible.
- **The single final professional holdout has now been opened and consumed.**
- **No tuning, candidate modification, threshold adjustment, candidate selection, replacement, or professional-holdout retry is permitted from this result.**
- No Modal/L4 without fresh explicit user authorization; none was used in this continuation.
- Tempo remains frozen exactly `129.19921875`.
- Completion gate was professional score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`.
- **V5 did NOT pass the final completion gate. Rhythm is NOT complete.**
- Existing `freezeReady=false` safety sentinels must remain false.

## Frozen V5 identities — UNCHANGED
- V5 exact: `891` attacks / `1214` selected / `1209` rendered / `5` voicing drops / `113` measures.
- Events: `967` baseline + `242` rescued; `933` preserved metadata + `276` conservative neutral; `21` technique events.
- Combined V5 validation SHA256 `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- Raw render-stream SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; 1,748,095 bytes.
- Canonical scorer event SHA256 `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Renderer-normalized PDF event SHA256 is exactly the same canonical hash.
- Source-only validation run `32872086764` = SUCCESS.
- Reference-free scorer preflight run `32918988699` = SUCCESS.
- Candidate/PDF identities remained unchanged through final scoring.

## Professional reference — VERIFIED / HOLDOUT CONSUMED FOR V5
- Professional image source verified SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`.
- Structured source verified SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`.
- Built reference verified SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Reference completeness passed: `113` measures, `603` playable onsets, `946` playable notes, `104` populated measures.
- `referenceOpenedOnlyAfterFreezeValidation=true`.
- Professional source/reference was opened only inside the one-shot final workflow after all V5 pre-reference gates passed.
- Transient source/reference payloads were removed by the workflow; only the non-reference final diagnostic is persisted.

## Final one-shot professional holdout — COMPLETE / FAILED GATE
- Trigger commit: `ec5528b5e06b14b4a203702d218cfd9eddbcc2b1`.
- Final workflow run: `32919666736`.
- All workflow steps completed **SUCCESS**, including immutable V5 revalidation, professional source verification, reference completeness, single scoring invocation, and permanent result-sentinel persistence.
- Result bot commit: `4af2bf9046a5f038106a855eb03fbaefaebf299e` (`Record immutable V5 final professional holdout result`).
- Persisted result: `debug/v143-contextual-prune/v5-professional-pdf/final-professional-holdout-result.json`, Git blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- `executionCompleted=true`, `executionPhase=complete`.
- `professionalHoldoutOpened=true` — **one-shot is permanently consumed**.
- `professionalReferenceSourceVerified=true`.
- `referenceCompletenessPassed=true`.
- `candidateModified=false`.
- `modalInvoked=false`; `productionModified=false`; `freezeReadyChanged=false`.
- Scorer return code `2` = completed score that did not satisfy the hard gate.

## Final scored outcome
- `near100ProfessionalGatePassed=false`.
- `finalCompletionGatePassed=false`.
- `scorerRhythmComplete=false`.
- `rhythmComplete=false`.
- **Critical mismatch count: `1875`** (required `0`).
  - gross unmatched generated notes: `1069`
  - gross unmatched reference notes: `806`
- PDF-event fidelity: **`1.0`** — this gate passed.
- Missing reference measures: `[]`; measure coverage recall: **`1.0`**.
- Gated musical metrics from the immutable final result:
  - pitch content F1: `0.2830626450116009`
  - pitch/timing tolerant F1: `0.044547563805104405`
  - string/fret/timing tolerant F1: `0.03062645011600928`
  - chord pitch-set tolerant F1: `0.022757697456492636`
  - exact voicing tolerant F1: `0.022757697456492636`
- These values are recorded **diagnostically only**. They must not be used to tune or select a replacement V5 candidate.

## Trigger / retry safety
- Final result sentinel now exists at `debug/v143-contextual-prune/v5-professional-pdf/final-professional-holdout-result.json`.
- The final workflow’s first guard refuses any future run before reference access when this sentinel exists.
- Do **not** rerun the final workflow, recreate/change the trigger file to induce another attempt, or rerun the failed API launcher.
- Earlier API launcher run `32919421673` failed before target workflow creation and did not consume the holdout; it is superseded by the completed one-shot final run above.

## Current V5 integrity
- Protected runtime untouched.
- `main`/Production untouched.
- Frozen V5 content/timing/metadata/thresholds/selection unchanged.
- No Modal/L4 used.
- PDF identity/fidelity proven exact.
- Professional reference provenance/completeness proven exact for the consumed V5 protocol.
- Final musical gate failed; V5 is therefore **not promotable as Rhythm-complete**.

## Continuation verification — 2026-08-25 22:40 America/Montreal
- Resumed from this checkpoint on explicit user request to continue on `v143-contextual-prune-lobo` and save this file often.
- Branch existed and was verified before further work; pre-continuation head was `12898eb6590067d06ded7620eb86964bd9124c10` (`docs: checkpoint immutable V5 final holdout result`).
- Permanent final-result sentinel re-read successfully at Git blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Sentinel still reports `professionalHoldoutOpened=true`, `finalCompletionGatePassed=false`, `rhythmComplete=false`, `tuningAllowedAfterHoldout=false`, `candidateSelectionAllowedAfterHoldout=false`, and `thresholdAdjustmentAllowedAfterHoldout=false`.
- Protected analyzer re-read successfully and remains exactly Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- No V5 candidate, scorer, threshold, workflow trigger, Production/main content, Modal/L4 job, or `freezeReady` sentinel was changed during this verification.
- Because the prior checkpoint explicitly required new project-phase direction after the immutable failed gate, no automatic Bass/Lead transition or new Rhythm experiment was started at that point.

## V144 Rhythm phase — EXPLICITLY AUTHORIZED 2026-08-25
- The user has now explicitly directed the next phase: retrain/calibrate **V144 Rhythm** toward the professional human-written transcription that represents the desired final quality level.
- Professional human-written visual target is located on `main` at `public/Professionalexample.jpg`.
- Verified repository identity from the `main` tree: Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, size `979757` bytes.
- The same path is not present on `v143-contextual-prune-lobo`; V144 work must not modify `main`. If local bytes are required, establish a verified branch-local calibration asset/reference without changing Production/main.
- V144 target: **near-100% agreement with the professional transcription**, while preserving professional PDF layout/readability and exact PDF-event fidelity as an independent gate.
- Protocol terminology: once V144 is iteratively changed while viewing/scoring against this professional page/reference, it is the V144 **gold calibration/reference benchmark**, not a statistically unseen holdout. Retain a separate unseen professional example for a true final generalization holdout if that validation is desired.
- This new V144 phase does not reopen, replace, or modify V5. V5’s consumed one-shot result and sentinels remain immutable historical evidence.
- No Modal/L4/GPU execution is authorized by this phase direction alone; fresh explicit user authorization is still required before any such run.

## Next exact actions
1. Keep V5 permanently immutable; never alter or rescore its candidate, thresholds, result sentinel, protected analyzer, or final holdout record.
2. Establish V144 Rhythm as a separate calibration/pipeline protocol; never overwrite the protected V143/V5 analyzer.
3. Establish verified branch-local provenance/access for the professional target from `main/public/Professionalexample.jpg` without modifying `main`.
4. Reuse the existing structured professional-reference/scorer machinery where safe, but isolate V144 artifacts/results from V5’s consumed one-shot protocol.
5. Drive V144 toward near-100% musical agreement with the gold professional reference while preserving PDF-event fidelity `1.0` and professional rendering quality.
6. Use existing repository evidence/archives before any new Modal/L4 work. Do not invoke Modal/L4/GPU without fresh explicit authorization.
7. Save this checkpoint after each meaningful V144 increment.
8. Do not start Bass/Lead until V144 Rhythm quality is proven or the user explicitly redirects.

## Crash-resilient continuation queue — 2026-08-25
This section is the immediate resume point if the GPT interface crashes. Complete items in order and update this file after each meaningful step.

1. **Inventory V143/V5 reference/scorer assets without changing them.** Locate exact repository paths for the structured professional-reference builder, professional scorer, V5 final workflow, renderer-normalization/PDF-fidelity checks, and any archived calibration evidence that can be safely reused by V144.
2. **Record the reusable-vs-frozen boundary.** For every located asset, classify it as read-only V5 evidence, safely reusable generic machinery, or V144-only code/artifact. Do not modify anything classified as V5 evidence.
3. **Establish a V144-only professional target asset.** Copy/derive the verified `main/public/Professionalexample.jpg` into a clearly named V144 calibration area on this branch, preserving provenance and recording source blob/hash. Never change `main`.
4. **Create the V144 protocol skeleton.** Add new V144-specific pipeline/scorer/config/result paths rather than replacing `analyzer/v143_reference_free_rhythm_pipeline.py` or any V5 sentinel/workflow.
5. **Reconstruct the gold structured reference using existing machinery.** Keep V144 outputs outside the V5 final-holdout paths. Verify measure/onset/note completeness before using the reference for iterative calibration.
6. **Establish a reproducible V143→V144 baseline comparison.** Use existing repository evidence first. Record musical mismatch categories separately from PDF-event fidelity so rendering success cannot mask transcription errors.
7. **Prioritize highest-impact musical error classes.** Attack pitch-content/chord-set errors first, then onset/timing alignment, then exact string/fret voicing and technique notation. Make one interpretable V144 change at a time and persist diagnostics.
8. **Keep compute authorization boundary explicit.** Repository inspection, branch-local code/config/reference setup, and non-GPU analysis are allowed; do not invoke Modal/L4/GPU until the user explicitly authorizes it.
9. **Checkpoint frequently.** After inventory, provenance establishment, protocol skeleton, baseline reconstruction, and each material calibration increment, append exact files/SHAs/results plus the next resume action here.
10. **Completion condition remains Rhythm-first.** Do not begin Bass/Lead unless V144 Rhythm quality is proven against the gold calibration target and rendering fidelity remains exact, or the user explicitly redirects.

### Immediate next resume action
Search the branch for the professional-reference/scorer/workflow assets named or implied by the V5 record, document their exact paths and classification in this checkpoint, then create only the minimum V144-isolated scaffolding needed for calibration. No V5 mutation and no GPU invocation.

## Resume log — 2026-08-26 00:05 America/Montreal
- Branch re-verified: `v143-contextual-prune-lobo`.
- Resumed at the crash-resilient continuation queue exactly as requested.
- Current phase: inventorying V5 professional-reference, scorer, workflow, renderer-normalization/PDF-fidelity, and archived calibration machinery before any V144 source addition.
- Guardrail remains active: no frozen V5 candidate, scorer result, threshold, protected analyzer, final-holdout sentinel/workflow trigger, `main`/Production content, or `freezeReady` state has been modified.
- No Modal/L4/GPU invocation has occurred.
- Next resume action: finish exact-path classification, save that classification here, then add only V144-isolated scaffolding.

## V144 exact-path inventory and reusable boundary — 2026-08-26
### Frozen/read-only V5 evidence — never edit or rerun as a V144 tuning surface
- `analyzer/v143_reference_free_rhythm_pipeline.py` — protected coordinator, Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- `debug/v143-contextual-prune/v5-professional-pdf/final-professional-holdout-result.json` — consumed one-shot V5 result, Git blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- `debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json` — frozen raw V5 render stream, SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- `debug/v143-contextual-prune/v5-professional-pdf/v5-rhythm-shadow.pdf` — frozen V5 PDF, SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`.
- `.github/workflows/v143-v5-final-professional-holdout.yml` — consumed V5 one-shot protocol; do not dispatch/retry or edit it for calibration.
- `.github/workflows/v143-dispatch-v5-final-professional-holdout-once.yml` and V5 trigger/sentinel paths — historical only; never reuse as V144 launch machinery.

### Safely reusable generic validation machinery — consume as read-only interfaces first
- `validation/rhythm_holdout/score_rhythm_holdout.py` — generic post-freeze professional scoring core, Git blob `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`.
- `validation/rhythm_holdout/freeze_rhythm_analysis.py` — generic reference-free freeze utility, Git blob `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`.
- `validation/rhythm_holdout/verify_pdf_event_fidelity.py` — exact PDF-event identity validator, Git blob `5e1564216873046237fb545078a04a6b18f72b27`.
- `validation/rhythm_holdout/verify_reference_completeness.py` — structured professional-reference completeness validator, Git blob `2504581dd72b6c375fbc0b68d4d396fce58deb87`.
- `lib/v143RenderContract.js` — existing renderer normalization/validation contract, Git blob `ccbb93c48982798cc474309fd981f6ca02d5c8d4`; V144 may validate compatibility against it but must not silently change V5 rendering semantics.
- `analyzer/v143_production_engine.py` — current candidate ranker loader/interface, Git blob `9201f8bb5671183051322b1ee739717336be762c`; read-only V144 baseline dependency.
- `analyzer/v143_rhythm_runtime.py` — current carrier-feature/rank/select runtime, Git blob `3f530da2c50c6b8c967a607a860c54135ee504af`; read-only V144 baseline dependency.

### Archived research/calibration evidence — reusable for methodology, not production mutation
- `analyzer/benchmark_gomyway_3161_microtiming_contextual_cv_v1.py` — deterministic contextual-signature/CV experiment, Git blob `df3c351c1293ea2188906b8810b4dbd327f75ef0`.
- `analyzer/V143_CONTEXTUAL_PRUNE_17_113_RESEARCH_CLOSURE_CHECKPOINT.md` — proves historical/reference-free 17–113 contextual chain closure and explicitly forbids treating that research result as direct production promotion.
- The historical contextual method conditions detection-side microtiming evidence on structural/register context and requires zero matched-note loss plus cross-validation/stability before accepting a prune. V144 can reuse this *methodological shape* while keeping all outputs/version gates new.

### V144 calibration target and baseline facts
- `main/public/Professionalexample.jpg` remains the verified visual gold target; main-tree Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, size `979757` bytes. `main` remains untouched.
- Exact professional source identity already verified in the consumed V5 protocol: image SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`, structured source SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`, built reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Gold reference completeness: 113 measures / 603 playable onsets / 946 playable notes / 104 populated measures.
- V5 establishes that rendering is not the limiting problem: PDF-event fidelity `1.0` and measure coverage `1.0` already pass.
- Musical baseline that V144 must materially beat: pitch-content F1 `0.2830626450116009`; pitch/timing tolerant F1 `0.044547563805104405`; string/fret/timing tolerant F1 `0.03062645011600928`; chord pitch-set tolerant F1 and exact-voicing tolerant F1 both `0.022757697456492636`; 1875 critical mismatches.
- Therefore V144 priority is upstream musical transcription accuracy, not a renderer rewrite: first reduce false/missing pitch content, then timing alignment, then string/fret voicing and technique notation while holding PDF fidelity at `1.0`.

### V144 isolation decision
- V144 will add new calibration/protocol/config/test/result paths only. It will not replace or edit `analyzer/v143_reference_free_rhythm_pipeline.py`, V5 debug/sentinel paths, or V5 workflows.
- The professional reference is now a **V144 gold calibration benchmark**, not a new unseen holdout. V144 results must never be described as unbiased generalization performance on that same reference.
- A deterministic no-prune/baseline path must remain available. Any contextual/split policy must lose to or fall back to baseline unless it achieves configured minimum musical gain without unacceptable canary drift or matched-note loss.
- No Modal/L4/GPU is authorized or invoked at this stage.

### Immediate next resume action after this inventory checkpoint
1. Establish a V144-only provenance manifest for the professional target without modifying `main`.
2. Add minimum V144 split-policy/selector/config/tests plus a CPU-only GitHub Actions gate.
3. Use synthetic/frozen non-reference fixtures first to prove deterministic fallback, split isolation, and no V5 mutation.
4. Only after the CPU gate is green, reconstruct the gold structured reference into a V144-only temporary/calibration path and begin measured V144 musical calibration.
5. Keep Bass/Lead disabled and keep `/ai-tab` frontend contract unchanged until Rhythm quality gate is genuinely reached.
