# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Non-negotiable boundary

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required Rhythm path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Professional human reference is scorer-only. Runtime may never read/train/tune/select from it. Any correction after a holdout failure must remain general/reference-free. After accepting any correction, create a **brand-new approved-audio run/freeze/PDF identity before another professional score**.

Rhythm completion requires:
- professional score >= `0.99`
- critical mismatches = `0`
- PDF-event fidelity = `1.0`

**Rhythm is NOT complete.**

## Protected runtime boundary

Protected file:
`analyzer/v143_reference_free_rhythm_pipeline.py`

Required exact blob:
`7f72f8ed9b14af8bc93e95544195204d99c6bec1`

Restore commit:
`4ff233346b8dc7b80d8f4316fe1317338b5be718`

All shadow gates must continue proving this blob unchanged and Production unmodified.

## Approved fixture / old scored freeze

Approved audio:
`public/gomywayfullaitest.m4a`

SHA256:
`215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

Old scored freeze:
- 358 attacks
- 1,017 rendered notes
- 277 polyphonic attacks
- 112 populated measures of 1–113
- missing measure 101
- event SHA256 `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e`
- PDF-event fidelity `1.0`

Do **not** rescore this old freeze after tuning.

## Scorer-only reference / holdout

Local temporary reference:
`/mnt/data/scorer_workspace/validation/rhythm_holdout/reference/professional-rhythm-complete.json`

SHA256:
`4d3e7ee6b5485c747bc917077b0648747da7f7d7325c8ccce5058fc41090d8cd`

State: measures 1–113 contiguous; 577 playable onset objects; 925 playable note entries; 104 measures with playable attacks; completeness verifier PASSED. **Never commit this reference.**

Old frozen professional holdout FAILED:
- pitch content F1 `0.2626158599382081`
- pitch/timing tolerant F1 `0.07209062821833163`
- string/fret/timing tolerant F1 `0.030895983522142123`
- chord pitch-set tolerant F1 `0.0`
- exact voicing tolerant F1 `0.0`
- measure coverage recall `0.9911504424778761`
- PDF-event fidelity `1.0`
- critical mismatches `1653`

General failure classes only: attack under-selection/measure loss; polyphony/harmonic inflation; broad pitch-position-timing mismatch. No song-specific runtime rule may come from the scorer/reference.

## Attack + pitch correction shadow

Files:
- `analyzer/v143_contextual_prune_shadow_correction.py`
- `analyzer/check_v143_contextual_prune_shadow_correction.py`
- `analyzer/v143_contextual_prune_shadow_correction_modal.py`
- `.github/workflows/v143-contextual-prune-shadow-correction-cpu.yml`
- `.github/workflows/v143-contextual-prune-shadow-correction-approved-audio.yml`

### Conservative uncertainty fix — CPU PASSED

General bug fixed: an uncertain multi-pitch base event could previously be collapsed to one relative winner even when the strongest candidate itself failed independent two-view attack/body support.

Now:
- strongest candidate failing physical floors => preserve entire original observed pitch set
- secondary suppression occurs only after the strongest pitch has positive independent two-view support
- attack/timing/string/fret/Production behavior remains unchanged

Code commit `2544c1c6da446bb6eaeaf96b6745757fce0a54a4`.
Checker commit `b682d5ed6574866ec2ac175d6c72be13f9fc8fbd`.

Current source-stamped CPU report:
`debug/v143-contextual-prune/shadow-correction-cpu.json`

PASSED:
- schema 2
- checked-out commit `d1a50efc2ffb640068f4c8bf72b4c0bb1f42b7ee`
- correction source blob `3bcad86b67116cc6d50295f2937a7bf3602b41dd`
- checker blob `bfe37235938b33d2f36f4f9d6ef39ebabeeb57e7`
- Modal runner blob `1ee6b81c5cc61dfea7d6ed927948896770db3ac0`
- synthetic `baseEventCount=2`, proving the new unsupported two-pitch preservation case ran
- corrected 4 / rescued 2 / suppressed pitches 1
- reference token scan passed
- protected pipeline exact
- Production unchanged

### Workflow race/freshness/anti-leakage hardening

Long-running Modal workflows could lose their final diagnostic commit if normal code/checkpoint commits advanced the branch. Current diagnostic workflows now source-stamp their inputs and rebase on latest branch before pushing.

Correction CPU workflow:
- source stamping `d1a50efc2ffb640068f4c8bf72b4c0bb1f42b7ee`
- rebase-before-push `b7b0e7bb04923c54f37c2376b83776d5123be20c`

Approved correction workflow:
- race-safe/source-stamped `9d5315abc3e6535403059bb399e33437ee23c46b`
- hardened anti-leakage/protected-runtime `f088337bef0811187b87e93265186f80336d8c2d`
- schema 3 action records source identities, protected blob and token-scan state
- refuses execution if approved SHA/protected pipeline/reference-token gates fail
- fetches/rebases before diagnostic push
- no live/Production mutation

Approved correction action/report remain pending. Do not accept musically until present and green.

## Independent approved-shadow physical review gate

Prepared a reusable, scorer-free consistency reviewer so an arriving approved correction report can be checked without opening the professional reference:
- `analyzer/v143_approved_shadow_physical_review.py` — commit `68c13fb87b08b1eb949d4732650238d900e7fdfc`
- `analyzer/check_v143_approved_shadow_physical_review.py` — commit `2de96bca2f1298dff5221a761fb2c2602140088a`
- `.github/workflows/v143-approved-shadow-physical-review.yml` — commit `39263eedc06f7caffb42c4ca0917721c04586fb5`

The review deliberately does **not** decide musical correctness. It validates only reference-free consistency before review:
- exact approved fixture / protected runtime / anti-leakage state
- shadow actually ran successfully and produced a report
- base events preserved; corrected count = base + rescued
- every listed rescue is unique/valid and count-consistent
- populated-measure coverage cannot decrease and no newly missing measure may appear
- pitch changes may only suppress pitches already present in observed candidate sets; they may never invent pitch
- pitch suppression counts must reconcile exactly
- timing diagnostics/hypotheses may not change tempo, phase, attacks, selection or pitch

Synthetic CPU gate is pending. It includes tamper cases that must reject invented pitches, newly lost coverage, and phase mutation.

## Semantic primary-note guard

Existing CPU report `debug/v143-contextual-prune/rhythm-semantic-primary-note-guard.json` is green. It preserves event/timing/pitch/string/fret identity while removing secondary bend/legato ownership errors. Protected pipeline exact; Production unchanged. Not integrated into routing yet.

## Sustain shadow

Existing CPU report `debug/v143-contextual-prune/rhythm-sustain-consensus-shadow.json` is green. Two guitar-view harmonic persistence; writes only `rhythmSustainShadow`; no attack/pitch invention; no tie/let-ring inference; Production unchanged.

## Approved-audio semantics + sustain

Runner:
`analyzer/v143_rhythm_semantics_sustain_approved_shadow_modal.py`
commit `cd0fec62bdd3b4da9ce7645db4d3582d528a2164`

Workflow:
`.github/workflows/v143-rhythm-semantics-sustain-approved-shadow.yml`
- original `c4077eff19e1e720719fc0147c1625df49c5c32a`
- race-safe/source-stamped `a7af569758c50c68a2dea6d59bc0804ec66562db`
- hardened anti-leakage/protected-runtime `6443b78a2a593734726499186ba4eeb58da2317f`

Current action schema 3 records runner/guard/sustain source identities, exact protected blob and reference-token scan. It refuses execution if approved SHA, protected-runtime or anti-leakage gates fail; rebases before diagnostic push; and retains event-identity/semantic/sustain/no-Production invariants.

Expected action/report are pending. Do not integrate semantics/sustain until green.

## Timing diagnostics

Existing timing consistency shadow is green: `debug/v143-contextual-prune/rhythm-timing-consistency-shadow.json`.

Four-way phase + grid ambiguity shadow is also CPU green:
- module `2774a0421bc7f6781b5263d355f852c6dcf0f411`
- proof `70dab327ffdedf216c18de8fb5eb5c7ffb131fcc`
- workflow `57754a31de69a061563a96c7623f2dfcc74cb59f`
- Actions diagnostic `1fcf86c55e90ddf1c33846e43c982461d0de7af3`

It exposes all four 4/4 phase hypotheses and nearest-vs-runner-up grid ambiguity without selecting/changing phase, timing, attacks or pitches. Approved correction Modal runner includes these diagnostics only (`d3639460ca54d7b8a5710978469cbe44bf1ac35e`).

## Existing production semantic path

`analyzer/v143_modal_live_endpoint.py` already applies bends then legato post-selection. Old output was not technique-disabled. Any semantic changes must remain general/reference-free.

## Immediate next steps

1. Read the new physical-review CPU diagnostic; require green before using the reviewer.
2. Read hardened race-safe approved attack/pitch action/report when committed and run the independent physical review against it.
3. Read hardened race-safe approved semantics/sustain action/report when committed.
4. Inspect four-way phase confidence/grid ambiguity and correction deltas only as label-free evidence.
5. If approved invariants/evidence pass, independently accept only general corrections.
6. Then create a **brand-new** approved-audio analysis/freeze/PDF identity.
7. Only then open scorer-only reference for a new holdout.
8. Require >=0.99, zero critical mismatches and PDF-event fidelity 1.0 before Rhythm completion.
