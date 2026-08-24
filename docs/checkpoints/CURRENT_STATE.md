# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 16:54 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; do not modify/merge `main` or live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1` (reverified unchanged at 16:54).
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. Runtime/shadows may never read/train/tune/select from it.
- Retired scored render identities must never be rerun/rescored:
  - `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
  - `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- Any future score requires a genuinely new approved-audio/frozen-evidence corrected candidate identity → immutable freeze/PDF → lock → exactly one professional score.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**
- **No more Modal/L4 unless the user explicitly reopens paid usage.** Current work is CPU-only/reference-free.

## Immutable historical score state
### Score 1 — retired
- 725 selected attacks → 985 rendered notes, 113 measures, PDF fidelity 1.0.
- run `32731885778`: coverage `1.0`; pitch F1 `0.23718280683583634`; pitch+timing F1 `0.033143448990160536`; critical mismatches `1723`.

### Harmonic contradiction correction + Score 2 — retired
- 144 fundamental promotions; 96 contradictory strongest upper harmonics suppressed (+12=78, +19=11, +24=6, +28=1).
- Corrected retired render identity `07b12...`; 889 events; PDF-event fidelity 1.0.
- run `32752374788`: generated 889; reference 946; pitch F1 `0.24305177111716622`; pitch+timing F1 `0.03051771117166212`; string/fret+timing F1 `0.01852861035422343`; chord F1 `0.012048192771084336`; critical mismatches `1635`.
- Conclusion: harmonic contradiction was real but not the dominant broad failure.

## Frozen/reference-free evidence
- `debug/v143-contextual-prune/frozen-approved-audio-preholdout-evidence.json`
- 725 retained attacks, 113 measures, `tempoBpm=129.19921875`, approved source SHA exact.
- Historical preholdout run `32702772593` artifact `rhythm-professional-preholdout-real-audio` recovered without new inference.
- Candidate generation run `32699399835`, job `97347696711`, trigger commit `1861f7a2a4aec814dd8b8504e5cca7c1f8ce6ae1`; candidate product commit `289a04e0fe30b5668ddaf39427404d8472ca1f51`.
- Historical carrier source blob `99866aa8af14dc243d226c6fb28d68af14d003ac`; historical precision source blob `feeaafea511bf727099d1532a323f9106af75b7a`.

## Timing diagnosis — simple global fixes rejected
- Global physical accent/phase evidence is sectional/mixed; reject a global half-bar origin shift.
- Metadata BPM `129.19921875`; global timestamp fit `129.2881694947` (+0.06885%). Reject global BPM replacement.
- Local timing residuals are nonmonotonic and sectionally variable. Any future timing correction needs a locally varying, reference-free physical grid; no simple mutation is justified yet.

## Pivotal pitch diagnosis
The upstream carrier was **not pitch-starved**.
- Same 725 retained attacks entered precision with `7,535` observed pitch hypotheses (mean `10.393`, max 26).
- Only 2/725 attacks were single-hypothesis before precision.
- Legacy precision retained only `987` hypotheses (mean 1.361), leaving 487/725 attacks single-hypothesis.
- `6,548` observed pitches were suppressed.
- Therefore the dominant diversity collapse is inside the legacy precision secondary gate, not Basic Pitch candidate proposal.

### Exact legacy gate semantics
- Primary selection may promote a physically present lower fundamental using harmonic-family evidence.
- Every non-primary secondary is compared against the **strongest raw candidate**, independently for score, attack, and body.
- Normal secondary floor = `0.80`.
- Exact upper-harmonic intervals `{12,19,24,28,31,36}` use floor `0.92`.
- Legacy retention requires `score AND attack AND body` all to clear the applicable floor.
- There is no MIDI64 special-case in the source.

### Exact optional-candidate accounting — new
Files:
- `analyzer/v143_precision_optional_candidate_accounting.py`
- `debug/v143-contextual-prune/precision-optional-candidate-accounting.json`

Reconciled arithmetic:
- 7,535 original hypotheses − 725 primaries = 6,810 non-primary hypotheses.
- On 144 promoted-fundamental attacks, the strongest raw pitch is a distinct secondary and is a forced survivor because all of its relative ratios are 1.0.
- Removing those 144 forced occupants leaves **6,666 genuinely optional secondary candidates**.
- Only **118/6,666 = 1.7702%** survived the legacy gate.
- **6,548/6,666 = 98.2298% of optional candidates were suppressed.**
- This exactly reconciles the historical `suppressedPitchCount=6548`.

### Retained-survivor brittleness diagnostic — new
Files:
- `analyzer/v143_precision_survivorship_gate_brittleness_diagnostic.py`
- `debug/v143-contextual-prune/precision-survivorship-gate-brittleness-diagnostic.json`

Findings:
- 987 retained hypotheses = 725 primaries + 262 secondaries.
- 144/262 secondaries are the forced strongest-raw survivors on promoted attacks; only 118 are nontrivial gate survivors.
- Among those 118: limiting dimension is attack 57 times, body 47, total score only 14.
- 61/118 (51.69%) survive within 0.05 of the hard floor; 94/118 (79.66%) within 0.10.
- This supports classification `hard-intersection-survivorship-brittleness-clue`: the three-way conjunction is dominated by independent attack/body envelope requirements even though total score already combines physical evidence.

### MIDI64 symptom retained
- primary MIDI64=202; non64=523.
- MIDI64 single-hypothesis 179/202 = 88.61%; non64 308/523 = 58.89%.
- Only 15/202 MIDI64-primary attacks retain a nontrivial secondary vs 93/523 non64 attacks.
- Treat as a symptom of the gate interaction, not evidence of a hard-coded E4 rule.
- Correct primary-open partition remains 264 open / 461 fretted; older 423/303 values are invalid and must not be reused.

## Historical raw-row recovery result
- Exact candidate run `32699399835` has zero uploaded artifacts.
- Exact job logs contain only aggregate diagnostics; no per-event `candidateMidis`, `rawPhysicalAttacks`, or suppressed rows.
- Candidate adapter persisted only post-precision-supported hypotheses.
- Preholdout raw/freeze/PDF artifacts likewise do not contain the 6,548 suppressed per-event rows.
- The producer used a `TemporaryDirectory`; historical stems/carrier rows were ephemeral, not a persistent Modal volume.
- Repo searches for `candidateMidis`, `rawPhysicalAttacks`, and the temporary stem filenames found no persisted snapshot.
- Therefore exact replay of a relaxed policy on the historical 7,535 rows is impossible without one new carrier capture.

## Precision v2 prepared — NOT RUN
New research-only module:
- `analyzer/v143_contextual_prune_precision_shadow_v2.py` commit `efcc90b6d8b004395159e35fd1a87f079952a3e1`.
- Policy name `envelope-balanced-secondary-v2`.
- Attack selection, local-prominence logic, fail-safe behavior, fundamental promotion, no-invention invariants, and harmonic protection remain unchanged.
- For **non-harmonic** observed secondaries only: replace legacy 3-of-3 conjunction with **2-of-3 physical consensus** across score/attack/body at the existing 0.80 floor.
- For exact upper-harmonic intervals `{12,19,24,28,31,36}`: retain the full legacy 3-of-3 0.92 gate.
- No new numeric threshold, pitch, attack, key/chord/song rule, runtime label, or professional information was introduced.

Policy guard:
- `analyzer/check_v143_precision_shadow_v2_policy.py` commit `e923c597bef9fdd88ef59392a8f61bf7f8ce8b1c`.
- `.github/workflows/v143-precision-shadow-v2-cpu-guard.yml` added and later updated at commit `249fae8403387a4a6fe0c9250453a6959dc3a4d3` to compile/test the v2 path, historical accounting, candidate integration, protected-runtime blob, and anti-leakage tokens.
- Workflow is CPU-only and contains no Modal invocation.

## Candidate path prepared to prevent another evidence-loss cycle — NOT RUN
`analyzer/v143_repaired_timing_precision_candidate_product_modal.py` updated at commit `83c050f5a8246dfbd80b118390039cab7d29909b` (blob `859040d832d3f77be4e5b361bdc86cbf186fb354`).
- Future isolated candidate generation now calls precision v2, then the existing promoted-harmonic guard.
- It persists `precisionReplayEvidence` for every retained attack: every observed original candidate MIDI plus compact score/attack/body/early/sustain/continuity physical evidence, selected flag, and primary flag.
- This means **one future carrier capture can support repeated CPU-only precision policy experiments without rerunning separator/Basic Pitch inference**.
- Candidate metadata explicitly records the v2 policy and that no new threshold/reference information is used.
- The producer file was locally syntax-compiled before commit.
- Protected runtime was reverified unchanged after integration.
- **No candidate was generated, no Modal/L4 was invoked, no scorer was invoked, no events were mutated, and Production/main remain untouched.**

## Next exact actions
1. Retrieve/verify the CPU guard result if available; fix any static/invariant failure without inference.
2. Finish a source-only preflight around `precisionReplayEvidence` so a future capture is rejected unless it persists a complete replayable candidate universe.
3. Do not run the candidate yet under the current cost boundary.
4. Once the no-cost preflight is green, the remaining hard blocker is one explicit user-authorized carrier/candidate capture. That capture must persist replay evidence; after it, all policy sensitivity work should return to CPU-only.
5. Use the captured replay evidence to quantify legacy vs v2 retention and inspect physical-support distributions without professional mismatches.
6. Only if source-only evidence supports the corrected candidate: immutable freeze/PDF → fidelity 1.0 → lock → exactly one professional score.
7. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.
