# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V161 is terminal and consumed forever after exactly one generation and exactly one professional-reference score. Score terminal bot commit `d1dd2f07bc5e07130a858981821d3b67bc2de78b`; score run `33209465651`, run #1 attempt #1, job `98978832375`; score workflow self-deleted. Outcome `SCORE_GATE_FAIL`. Combined Guitar primary F1 `0.06993006993006994`; Bass primary F1 `0.20883534136546184`; gates remain `0.80/0.80`. Candidate blob/hash remained frozen and unchanged. Next: preregister V162 from aggregate frozen evidence only; no V161 rerun/rescore/repair/retune.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring authorized at assistant discretion.
- Fresh explicit authorization required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159, V160, and V161 are closed forever.
- V161: no regeneration, re-QC, repair, candidate replacement, threshold sweep, variant selection, rescore, or post-score retune.
- Professional reference/scorer may not guide successor implementation at event level. V162 may use only frozen aggregate score evidence plus reference-blind runtime/implementation evidence copied into its preregistration.
- No V161 candidate event-level mining/reuse for V162 tuning.
- No human correction. Do not commit professional-tab screenshot bytes.
- Target remains automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF.

## V160 frozen score baseline
- Guitar: primary F1 `0.09975470155355683`; gross ±2-step F1 `0.2131370945761788`; measure+pitch F1 `0.3881166530389752`; generated `2276`; matched primary/gross/measure `183/391/712`.
- Bass: primary F1 `0.18073485600794442`; gross `0.31777557100297915`; measure+pitch `0.5124131082423039`; generated `460`; matched `91/160/258`.
- Reference aggregate counts frozen from scorer output: Guitar `1393`, Bass `547`.

## V161 generation terminal — PASS / CONSUMED
- Arm/head `418a25f82e4aa3742e995e4a3ce341bc48a24151`; workflow blob `38cd491453c618f595d42bb6d42e87e478f35f0e`.
- Run `33208183041`, #1 attempt #1, job `98974530460`, success.
- Bot terminal commit `1b58ffcb8c2ee8fc7dd6152bf02c071d75035ade`; generation workflow deleted.
- Terminal freeze blob `5ff59c993698b00df3503c6e22e036f181140aa4`: `STRUCTURAL_QC_PASS`, authoritative/scoring-eligible, neverRearmV161=true.
- Structural-QC blob `2146cf9f7b9e92ce704ef2118e711bd42ae2e093`; SHA256 `ba17ac241d438e15d13f0d45a93194e97151868805541dc252ea41caa1ae34ba`; PASS; errors `[]`.
- Candidate blob `52178705ef3830f6849b71037cd283877aa7655f`; SHA256 `75c4edd6560ee832bf7df4799c4e9389a7424e7056ac5f3cd5a9e07fc254996a`; final counts Guitar `895`, Bass `449`.
- Candidate remained same blob after scoring.

## V161 reference-blind runtime diagnostics — FROZEN
- Guitar: Basic Pitch raw 1404 → consolidated 985 → admitted 978 → final 895; onset-refined 827; register repairs 382; admission rejects 7; standalone harmonic recovery 0/disabled.
- Bass: detected onsets 465 → retained/merged 464 → admitted/final 449; onset-refined 464; activity rejects 1; transition proposals 0.
- These runtime diagnostics are reference-blind and may inform V162 only at aggregate/architectural level; no V161 event rows may be mined.

## V161 score preregistration — SEALED / CONSUMED
- `debug/v161-cpu-autonomous/score-preregistration.json`; seal commit `22fdd5df418f0d196f5472026c6c0ffd24f893e6`; blob `8f50b65d023bd5469935ed3ca70c115bf0b86dda`.
- Frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- One-score maximum, gates `0.80/0.80`, candidate consumed regardless outcome.

## V161 sole professional-reference score — FAIL / CONSUMED
- Score arm/head `819b556110552bd646ba1e3b276b2a562b21a398`.
- Score workflow blob `4de6a1bf1b01d649b3f452ede77e4f95bf0f6179`.
- Run `33209465651`, run #1 attempt #1, job `98978832375`, workflow conclusion success.
- Bot terminal commit `d1dd2f07bc5e07130a858981821d3b67bc2de78b`, parent exactly score arm.
- `.github/workflows/v161-score.yml` is absent after self-seal.
- Score report `debug/v161-cpu-autonomous/reference-score.json`; blob `08ebbd9f7ef38eeeb3defcce9aa445b21f120f57`; SHA256 `3bf1c7da8304f2507e764e16deae62f36f220881dfa1d5f1c808fdedd6c34867`.
- Score terminal `debug/v161-cpu-autonomous/score-terminal-freeze.json`; blob `5b0550497432a6c5cb9b1b947694327b616f6241`.
- Score execution count `1`; candidateConsumed=true; scoreOpportunityConsumed=true; neverRerunOrRescoreV161=true.
- Safety: candidateModified=false; regenerated=false; reQc=false; thresholdSweep=false; variantSelection=false; humanCorrection=false; postScoreRetune=false; professionalReferenceUsedForScoringOnly=true; GPU/CUDA/Modal=false; main/Production=false.

## V161 frozen score metrics
### Combined Guitar
- Primary timing-aware pitch: F1 `0.06993006993006994`; matched `80`; generated `895`; reference `1393`; precision `0.0893854748603352`; recall `0.057430007178750894`.
- Gross ±2-step: F1 `0.1861888111888112`; matched `213`; precision `0.23798882681564246`; recall `0.15290739411342427`.
- Measure+pitch diagnostic: F1 `0.40297202797202797`; matched `461`; precision `0.5150837988826815`; recall `0.33094041636755206`.

### Bass
- Primary: F1 `0.20883534136546184`; matched `104`; generated `449`; reference `547`; precision `0.23162583518930957`; recall `0.19012797074954296`.
- Gross ±2-step: F1 `0.34136546184738953`; matched `170`; precision `0.37861915367483295`; recall `0.31078610603290674`.
- Measure+pitch: F1 `0.5261044176706828`; matched `262`; precision `0.5835189309576837`; recall `0.4789762340036563`.

## Frozen V160→V161 aggregate interpretation for V162 preregistration
- Guitar event flooding was substantially reduced (`2276 → 895`). Measure+pitch precision improved strongly (`~0.313 → ~0.515`) and measure+pitch F1 improved slightly (`0.3881 → 0.4030`), but primary recall collapsed (`~0.131 → ~0.057`) and primary F1 fell. V162 should preserve the precision gain while restoring genuine repeated/rearticulated Guitar notes; fixed-gap same-pitch consolidation appears too destructive as an architecture.
- Guitar gross F1 (`0.1862`) remains far above primary (`0.0699`), and measure+pitch F1 (`0.4030`) remains far above gross. V162 must change musical subdivision/onset-to-grid placement architecture rather than only pitch thresholds.
- Bass improved across all three metrics (primary `0.1807→0.2088`, gross `0.3178→0.3414`, measure `0.5124→0.5261`) while event count remained similar (`460→449`). V161 Bass architecture is directionally useful, but its intended pYIN transition-recovery branch generated zero proposals; V162 should replace that inactive recovery mechanism with an architecture that can segment stable pitch tracks/rearticulations without reference guidance.
- V161 local onset refinement alone did not close the large primary-vs-gross/measure gaps. V162 should treat the global 16-step mapping/subdivision lattice as an active architectural target while retaining the reference-blind beat/measure evidence foundation.
- No event-level professional-reference conclusion is permitted.

## Current hard boundary
- V161 is consumed forever. Never rerun/rescore or modify its candidate/artifacts.
- No V162 implementation code may exist before a V162 preregistration and numeric implementation contract are sealed.
- V162 design may use only the aggregate score/runtime evidence explicitly frozen above plus reference-blind V161 source/QC identities.
- Direct professional-reference event/measure mining and score-guided same-song variant selection are forbidden.
- No GPU/Modal/CUDA without fresh explicit authorization; never touch main/Production.

## Exact next steps — RESUME HERE
1. Re-fetch branch/checkpoint before every write.
2. Create/seal `debug/v162-cpu-autonomous/preregistration.json` before any V162 implementation code.
3. V162 prereg should freeze successor hypotheses: onset-aware Guitar rearticulation segmentation instead of fixed 80ms merge; harmonic evidence as validation only; stronger continuity-aware octave/register logic; song-blind subdivision-lattice/event-to-grid refinement; Bass stable pitch-track/rearticulation segmentation replacing the zero-activation transition branch.
4. Seal exact song-blind synthetic fixtures and one-shot CPU boundaries.
5. Create/seal numeric `implementation-contract.json` before V162 code.
6. Only then implement/static-test V162; no same-song score loop.
