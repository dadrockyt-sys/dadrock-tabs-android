# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; do not modify/merge `main` or change live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional human reference is scorer-only. Runtime/shadows may never read/train/tune/select from it.
- Retired scored freeze event SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8f8edc629f3ce01975c4f1af8c51dfdb` is INVALID text; canonical retired scored SHA is `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb` and must never be rerun/rescored.
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

## One-shot new approved-audio candidate — TRIGGER ISSUED, NO SUCCESS OUTPUT
Workflow `.github/workflows/v143-harmonic-guard-candidate-once.yml` commit `346d0f38381906e9c821b7f6020c932f3e2b4c1c`.

Trigger marker commit: `a9e9ddd61c1d41b2530ab15e352bf8f410b592fc` at `2026-08-24T15:08:46Z` (~10:08 local). Trigger commit author is `dadrockyt-sys`, so the workflow job actor guard does not suppress it. Workflow existed at that exact trigger revision.

Current evidence:
- new candidate path still 404;
- new initial proof still absent;
- original one-shot marker still exists;
- no success bot commit `Record one-shot harmonic-guard approved-audio candidate` exists.
Therefore candidate success is not proven. **Do not create another candidate marker or invoke another approved-audio inference until the original Modal-stage evidence is isolated.**

## Zero-cost pre-Modal replay — PROVEN GREEN
`debug/v143-contextual-prune/harmonic-guard-candidate-preflight-diagnostic.json` is now committed and `passed=true`.
- all original pre-Modal checks pass: marker, old candidate blob `20e7a583...`, protected blob exact, approved fixture SHA exact, guard proof exact/opportunity count 96, all candidate Python compilation, guard checker, anti-leakage.
- no Modal import/invocation/GPU, professional reference, runtime labels, or Production.
Conclusion: the one-shot did not fail because of a deterministic pre-Modal gate defect. Remaining failure location is Modal install/auth/inference or post-inference validation/commit.

## Offline retired-candidate projection — PROVEN GREEN
`debug/v143-contextual-prune/harmonic-guard-offline-projection-proof.json` committed by Actions at branch head `ed16166cf8aab235f1cc8c123e0d379c42b0af1c` (`2026-08-24T15:29:52Z`).
- reproduces retired scored projection exactly: 985 events, SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`.
- identifies/promotes 144 primaries and suppresses exactly 96 strongest harmonic duplicates: +12=78, +19=11, +24=6, +28=1.
- simulated result: 725 attacks, 889 raw/render events.
- simulated projected render SHA: `50aa17f6855a816ce73f8b427062e8c24c5ce0a5751c7b6425e79c6cea89ecca`, which is new vs retired.
- protected runtime blob exact; no Modal/GPU/reference/runtime-label/Production use.
- `simulationAcceptedAsCandidate=false`: this proves the guard and downstream render projection are coherent, but it is NOT a substitute for a new approved-audio inference.

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
- Exactly one candidate trigger has been issued; do not issue a second yet.
- CPU preflight and offline projection are green and zero-Modal.
- No professional scorer/reference has been opened.
- Old candidate/freeze/scorer remain untouched.

## Next exact actions
1. Perform a **read-only Modal diagnostic** using existing GitHub secrets: `modal token info` plus history/log inspection for app `dadrock-v143-repaired-timing-precision-candidate-product`; it must not call `modal run`, remote functions, or GPU.
2. Use that evidence to determine whether the original one-shot reached Modal and whether it failed during build/inference versus after inference.
3. If a completed original Modal invocation can be recovered without rerunning, preserve its evidence/candidate if possible.
4. Only if evidence proves no usable candidate can be recovered may a separately guarded recovery inference be considered; never blindly retrigger the original marker.
5. Once a real new candidate + initial proof + binding proof are green, save exact blob/raw/render identities here and create the dedicated preholdout marker once.
6. Only after preholdout `passed=true` + PDF fidelity 1.0 + new frozen identity may exactly one professional score be permitted.
