# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; do not modify/merge `main` or change live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional human reference is scorer-only. Runtime/shadows may never read/train/tune/select from it.
- Retired scored freeze/render event SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb` must never be rerun/rescored.
- Any accepted correction requires a completely new approved-audio candidate → immutable freeze/PDF → lock → one professional score.
- Completion remains score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is not complete.**

## Last scored candidate / holdout result
- Repaired timing + precision: 449 repaired beats, 0 interval outliers, 113 measures / 1796 slots, all measures populated, explicit primary complete.
- Exact 2-pass proof run `32697939613` passed. Old candidate/freeze must not be rerun/rescored.
- One-shot professional run `32731885778`: coverage recall `1.0`, pitch-content F1 `0.23718280683583634`, pitch+timing F1 `0.033143448990160536`, critical mismatches `1723`.
- Scorer/reference is closed again. Allowed diagnosis only: coverage solved; timing/grid identity and pitch identity fundamentally wrong.
- Retired scored identity: 725 selected/unique attacks → 985 rendered notes, 236 multi-note onsets, max chord size 6, 113 measures, PDF fidelity 1.0.

## Precision polyphonic expansion — audio-only defect PROVEN
- 144 fundamental promotions; all 144 still rendered the strongest raw pitch.
- 96/144 strongest pitches were harmonic-family intervals above promoted primary: +12=78, +19=11, +24=6, +28=1.
- minimal promoted-harmonic guard is proven green, attack identity unchanged, pitch identity changed, protected runtime exact, anti-leakage passed, no reference/GPU/Production in proof.
- guard helper commit `588b314c3103ffbea8a0a933351562551750f670`; product integration `534be3fec36cf5ec4a87089b1298becb4933693d`; proof workflow extension `30d7da578667f7d128824d7d343be782bf064533`.

## One-shot new approved-audio candidate — MODAL TIMEOUT ISOLATED
Workflow `.github/workflows/v143-harmonic-guard-candidate-once.yml`; trigger marker commit `a9e9ddd61c1d41b2530ab15e352bf8f410b592fc` at `2026-08-24T15:08:46Z` (~10:08 local).

No success candidate/proof was committed and the original marker remains. Do not retrigger it.

### Pre-Modal replay — GREEN
`debug/v143-contextual-prune/harmonic-guard-candidate-preflight-diagnostic.json` passed every original pre-Modal gate: marker, old candidate blob, protected blob, fixture SHA, guard proof/opportunity 96, compilation, guard checker, anti-leakage. No Modal/GPU/reference/runtime labels/Production.

### Offline projection — GREEN
`debug/v143-contextual-prune/harmonic-guard-offline-projection-proof.json`, bot commit `ed16166cf8aab235f1cc8c123e0d379c42b0af1c`.
- reproduces retired 985-event SHA exactly: `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`.
- suppresses exactly 96 harmonic duplicates; simulated 725 attacks / 889 render events.
- simulated new projected SHA `50aa17f6855a816ce73f8b427062e8c24c5ce0a5751c7b6425e79c6cea89ecca`.
- `simulationAcceptedAsCandidate=false`: proof only, not a replacement approved-audio candidate.

### Read-only Modal diagnostic — decisive evidence
`debug/v143-contextual-prune/harmonic-guard-modal-readonly-diagnostic.json` passed authentication/listing without invoking `modal run`, a remote function, or GPU.
- `modal token info`: success.
- `modal app list`: success and found exactly one matching app.
- matching app state: `stopped`.
- app created `2026-08-24 15:09:13+00:00`.
- app stopped `2026-08-24 15:39:28+00:00`.
- elapsed app lifetime: ~30m15s.
- candidate function is configured `timeout=1800` seconds (30 minutes).
This proves the original one-shot **did reach Modal** and the lifetime aligns essentially exactly with its 1800-second function timeout. The failure is therefore isolated to the Modal remote build/inference path timing out before the local entrypoint could write/commit the candidate. Credentials and pre-Modal gates are not the problem.

Name-based history/log commands failed after stop because Modal no longer resolved the stopped app by name. A second read-only diagnostic should resolve the stopped app ID from `modal app list --json`, then query history/logs by that ID to identify the last completed stage. It must not invoke `modal run`, remote functions, or GPU.

## CPU post-proof prepared
`.github/workflows/v143-harmonic-guard-candidate-postproof.yml` commit `5d7e96c38c8328457bd82aeeb691245a66ffed00`; no second GPU inference/reference/Production.

## Fail-closed preholdout prepared, NOT triggered
`.github/workflows/v143-harmonic-guard-final-preholdout.yml` commit `12958a2f5f245697148a7fba190dd7bb8e98987c`.
- marker not created.
- requires real new candidate + initial proof + final binding proof green.
- freezes exact candidate, renders PDFs, requires frozen SHA == bound render SHA, `pdfEventFidelity == 1.0`, and rejects all retired identities.
- scorer/reference stays sealed.

## Cost control
- Exactly one candidate trigger and one ~30-minute Modal app execution occurred. Do not issue a second inference blindly.
- Read-only diagnostics are permitted and use no GPU.
- No professional scorer/reference has been reopened.
- Old candidate/freeze/scorer remain untouched.

## Next exact actions
1. Resolve the stopped Modal app ID read-only and fetch its history/logs by ID to identify the final completed stage and timeout location.
2. Use those logs to design the cheapest recovery: avoid repeating completed expensive work if an intermediate can be safely preserved/reused while still producing a completely new approved-audio candidate.
3. Any recovery inference must be separately fail-closed and issued only after CPU proof that it cannot repeat the same 1800-second timeout path.
4. Once a real new candidate + proof + binding proof are green, save exact identities here and trigger preholdout once.
5. Only after preholdout passes with PDF fidelity 1.0 and new frozen identity may exactly one professional score run.
