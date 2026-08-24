# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; do not modify/merge `main` or change live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional human reference is scorer-only. Runtime/shadows may never read/train/tune/select from it.
- Retired scored freeze event SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb` must never be rerun/rescored.
- Any accepted correction requires a completely new approved-audio candidate → immutable freeze/PDF → lock → one professional score.
- Completion remains score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is not complete.**

## Last scored candidate / holdout result
- Repaired timing + precision: 449 repaired beats, 0 interval outliers, 113 measures / 1796 slots, all measures populated, explicit primary complete.
- Exact 2-pass proof run `32697939613` passed. Old candidate/freeze must not be rerun/rescored.
- One-shot professional run `32731885778`: coverage recall `1.0`, pitch-content F1 `0.23718280683583634`, pitch+timing F1 `0.033143448990160536`, critical mismatches `1723`.
- Scorer/reference is closed again. Allowed diagnosis only: coverage solved; timing/grid identity and pitch identity fundamentally wrong.
- Retired scored render identity `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`: 725 selected/unique attacks → 985 rendered notes, 236 multi-note onsets, max chord size 6, 113 measures, PDF fidelity 1.0.

## Physical onset provenance — corrected and proven
- sustain promotion no longer overwrites physical `onsetTime`; grid `timeSeconds/start` remains separate.
- observed schema-v2 proof passed with unchanged event/grid/pitch identity and protected runtime.
- render/freeze projection omits physical timing seconds, so this fix alone cannot change scored identity.

## Precision polyphonic expansion — audio-only defect PROVEN
- 725 attacks → 985 notes = 260 secondary notes.
- 144 fundamental promotions; all 144 still rendered the strongest raw pitch.
- 96/144 promoted attacks rendered that strongest pitch at a harmonic-family interval above the promoted primary: +12=78, +19=11, +24=6, +28=1.
- synthetic `[40,52]` proves the contradiction: 52 strongest raw, 40 promoted as fundamental, then 52 still emitted independently.
- protected runtime exact; no professional reference/runtime labels/Production/Modal GPU used by the audit.

## Minimal promoted-harmonic guard — PROVEN GREEN
- helper `analyzer/v143_precision_promoted_harmonic_guard.py`, commit `588b314c3103ffbea8a0a933351562551750f670`.
- removes only the exact strongest upper harmonic when precision promoted a lower primary away from it; attacks/grid/primary/non-harmonic secondaries remain unchanged.
- observed `precision-promoted-harmonic-guard-proof.json`: `passed=true`, opportunity count 96, attack identity unchanged, scoring pitch identity changed, protected exact, anti-leakage passed, no reference/GPU/Production.
- product integration commit `534be3fec36cf5ec4a87089b1298becb4933693d`; schema v4 + `promotedHarmonicGuardDiagnostics`.
- product-proof extended commit `30d7da578667f7d128824d7d343be782bf064533`.

## One-shot new approved-audio candidate — TRIGGER ISSUED, RUN DID NOT COMMIT OUTPUT
Workflow `.github/workflows/v143-harmonic-guard-candidate-once.yml` commit `346d0f38381906e9c821b7f6020c932f3e2b4c1c`.

Safety design:
- dedicated marker only; bot commits excluded from triggering a second inference.
- pre-Modal gate requires old candidate blob exact `20e7a583...`, protected exact, approved fixture SHA exact, green guard proof/opportunity count 96, checker pass, anti-leakage pass.
- exactly one Modal L4 invocation writes only new candidate path; old candidate is never overwritten.
- after inference it requires schema v4, guard suppression >0, 113 measures, safety invariants, and projected render SHA != retired `a81190...` before committing candidate/proof and deleting marker.

Trigger marker commit: `a9e9ddd61c1d41b2530ab15e352bf8f410b592fc` at `2026-08-24T15:08:46Z` (~10:08 local). Trigger commit author is `dadrockyt-sys`, so `github.actor != 'github-actions[bot]'` does not suppress the job. Workflow existed at that exact trigger revision.

By ~11:24 local, more than the workflow's 55-minute timeout later:
- new candidate path still returned 404;
- new initial proof still absent;
- original one-shot marker still exists;
- no success bot commit `Record one-shot harmonic-guard approved-audio candidate` exists.
Therefore success is not proven and the run is treated as failed/timed out before its success commit. **Do not retrigger or touch the original marker until failure stage is isolated.**

Connected GitHub tooling cannot list this private push-triggered run directly: commit-run wrapper is PR-only, combined status exposed no run, and direct private Actions listing URL is unavailable. No GitHub failure email was found in connected Gmail.

## Zero-cost pre-Modal failure isolation — TRIGGERED
Added `analyzer/check_v143_harmonic_guard_candidate_preflight.py` commit `1a43dfae76ae85fcb7aadad722893319b9c974dd`.
- reproduces the original one-shot's full pre-Modal gate without importing/invoking Modal;
- verifies original marker, old candidate blob, protected blob, approved audio SHA, guard proof/opportunity count, candidate-source compilation, guard checker, and anti-leakage;
- always writes structured JSON and records `modalInvoked=false`, `modalGpuUsed=false`, no reference/runtime labels/Production.

Added CPU-only workflow `.github/workflows/v143-harmonic-guard-candidate-preflight-diagnostic.yml` commit `0fa9f922c32667459f6ef2ffea16c0be26a6c593`.
Dedicated diagnostic marker triggered once in commit `0f86e6e2c0d9ed97775e996155432ebde3bf5305`.
- this diagnostic cannot call Modal or scorer;
- it leaves the original one-shot candidate marker untouched;
- on completion it writes `harmonic-guard-candidate-preflight-diagnostic.json` + log and deletes only its own diagnostic marker.
At this checkpoint the diagnostic JSON has not appeared yet (first re-check 404).

## CPU post-proof prepared
`.github/workflows/v143-harmonic-guard-candidate-postproof.yml` commit `5d7e96c38c8328457bd82aeeb691245a66ffed00`.
- auto-runs only if a new candidate/proof is eventually committed;
- recomputes final blob/raw/render hashes, requires identity != retired `a81190...`, and binds determinism inheritance from exact 2-pass run `32697939613` plus pure deterministic guard;
- no second GPU inference, reference, or Production use.

## New fail-closed preholdout prepared, NOT triggered
`.github/workflows/v143-harmonic-guard-final-preholdout.yml` commit `12958a2f5f245697148a7fba190dd7bb8e98987c`.
- dedicated preholdout marker has NOT been created.
- requires candidate + initial proof + final binding proof all green.
- rejects retired `c621...`, `e693...`, and scored `a81190...` before freeze.
- freezes exact candidate, renders full/preview PDFs, requires frozen SHA == bound projected SHA, renderer exact, `pdfEventFidelity == 1.0`, and new non-retired identity.
- scorer/reference stays sealed; cannot claim Rhythm complete or promote Production.

## Cost control
- Do not create a second candidate marker or manually dispatch candidate while the first failure stage is unknown.
- Preflight diagnostic is CPU-only and zero-Modal.
- No professional scorer/reference has been opened.
- Old candidate/freeze/scorer remain untouched.

## Next exact actions
1. Read CPU preflight diagnostic as soon as it commits.
2. If preflight fails: correct only the proven pre-Modal defect, then decide whether the original one-shot is known not to have reached Modal before any retrigger.
3. If preflight passes: failure occurred at/after Modal; do not blindly rerun. Instrument a fail-safe path that preserves raw candidate/failure evidence before considering one additional inference.
4. If the original candidate unexpectedly appears, immediately validate initial proof + binding proof and save exact identities here; never issue another inference.
5. Only after a green new candidate binding proof may the dedicated preholdout marker be created once.
6. Only after preholdout `passed=true` + PDF fidelity 1.0 + new frozen identity may exactly one professional score be permitted.
