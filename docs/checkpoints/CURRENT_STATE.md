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
- guard helper commit `588b314c3103ffbea8a0a933351562551750f670`; product integration `534be3fec36cf5ec4a87089b1298becb4933693d`; proof extension `30d7da578667f7d128824d7d343be782bf064533`.

## One-shot new approved-audio candidate — FULL L4 RUN TIMED OUT
Workflow `.github/workflows/v143-harmonic-guard-candidate-once.yml`; trigger marker commit `a9e9ddd61c1d41b2530ab15e352bf8f410b592fc` at `2026-08-24T15:08:46Z` (~10:08 local).
- no success candidate/proof was committed; original marker remains; **do not retrigger it**.
- zero-Modal preflight replay passed every original pre-Modal gate.
- read-only Modal auth/list diagnostic proved app reached Modal, created `15:09:13Z`, stopped `15:39:28Z`, matching the function `timeout=1800` almost exactly.
- second read-only stopped-app-ID diagnostic found that the stopped ephemeral app had already aged out of `modal app list`; no ID/log recovery remained available. It invoked no remote function/GPU.

## Exact historical stage timing now recovered from run 32697939613
Successful exact pass job `97343555320` gives direct stage evidence from the same frozen separator graph:
- Modal image uses `audio-separator[gpu]==0.44.5`; do **not** describe the image as CPU-only Torch.
- seeded Demucs intentionally sets `CUDA_VISIBLE_DEVICES=''`, one CPU thread, oneDNN disabled and deterministic seed 143. Direct Demucs therefore reports no hardware acceleration and took ~7m42s.
- BS-RoFormer unsets the CUDA mask, reports CUDA + ONNX CUDA provider, and took ~47s on GPU.
- cascade Demucs restores the deterministic CPU mask and took ~7m17s.
- downstream repaired-timing precision shadow then completed and the whole pass finished successfully in ~18m26s.
- exact successful stage hashes: normalized WAV `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`; direct guitar `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`; cascade guitar `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41`.
- current seeded separator source confirms this resource split is intentional: direct/cascade Demucs CPU-only single-thread; RoFormer GPU-auto-proven-deterministic.
Conclusion: reserving an L4 for the entire product candidate spends ~15 minutes of the L4 reservation on deliberately CPU-only Demucs before the heavier product post-processing. The new product path can exceed the 30-minute whole-function timeout even though the frozen separator graph itself is valid.

## Offline promoted-harmonic projection — GREEN
`debug/v143-contextual-prune/harmonic-guard-offline-projection-proof.json`, bot commit `ed16166cf8aab235f1cc8c123e0d379c42b0af1c`.
- reproduces retired 985-event SHA exactly: `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`.
- suppresses exactly 96 harmonic duplicates; simulated 725 attacks / 889 render events.
- simulated new projected SHA `50aa17f6855a816ce73f8b427062e8c24c5ce0a5751c7b6425e79c6cea89ecca`.
- `simulationAcceptedAsCandidate=false`: proof only, not a replacement approved-audio candidate.

## Cost-bounded staged recovery — PREPARED, NOT YET TRIGGERED
New one-shot recovery module: `analyzer/v143_harmonic_guard_staged_recovery_modal.py`, commit `346ffd37d2ac5eb52fd1bf66111b9940699c722a`.
Design preserves the frozen algorithm but separates resource reservations:
1. fresh direct deterministic Demucs on Modal CPU only; exact normalized/direct SHA gates;
2. BS-RoFormer only on L4, hard timeout 600s;
3. fresh cascade deterministic Demucs on Modal CPU only; exact cascade SHA gate;
4. unchanged post-separator candidate/guard/semantic/sustain assembly on Modal CPU only.
Thus the only L4 stage is the ~47-second historical RoFormer workload; no full-pipeline L4 reservation.

Fail-closed recovery checker: `analyzer/check_v143_harmonic_guard_staged_recovery.py`, commit `8661ca7b9ffafb392bb1ab21fa362578f27ee8ac`.
CPU-only preflight workflow: `.github/workflows/v143-harmonic-guard-staged-recovery-preflight.yml`, commit `59412eb646101bc859aac254dcfdeb01697d599d`.
- preflight compiles + AST/static validates resource isolation, exact fixture/protected/stem bindings, frozen pipeline call sequence, orchestration order and anti-leakage.
- it does not invoke Modal or GPU.
- preflight proof commit is pending at this checkpoint. **Do not trigger staged recovery until `harmonic-guard-staged-recovery-preflight.json` exists with `passed=true`.**

## Downstream prepared
- CPU binding post-proof `.github/workflows/v143-harmonic-guard-candidate-postproof.yml` commit `5d7e96c38c8328457bd82aeeb691245a66ffed00`.
- fail-closed preholdout `.github/workflows/v143-harmonic-guard-final-preholdout.yml` commit `12958a2f5f245697148a7fba190dd7bb8e98987c`; marker not created.
- preholdout requires real candidate + initial proof + binding proof, new frozen identity, exact PDF renderer projection and `pdfEventFidelity == 1.0`; scorer remains sealed.

## Cost control
- One failed ~30-minute full-L4 candidate attempt occurred; do not repeat it.
- recovery is designed so only RoFormer receives L4; deterministic Demucs and product assembly use CPU.
- no professional scorer/reference has been reopened.
- old candidate/freeze/scorer untouched.

## Next exact actions
1. Require staged recovery CPU preflight `passed=true` and save its source/protected/resource-plan hashes here.
2. Only then create a dedicated staged-recovery marker exactly once and run the fresh approved audio through CPU → short L4 RoFormer → CPU → CPU assembly.
3. Require exact proven normalized/direct/cascade hashes, schema v4, guard suppression >0, 113 measures, and projected render SHA new vs retired; compare against offline expected `50aa17...` but fail closed rather than forcing it.
4. Commit real candidate + initial proof; allow automatic CPU binding proof.
5. Once binding is green, trigger preholdout once. Require PDF fidelity 1.0 and frozen SHA == bound new render SHA.
6. Only then permit exactly one professional score; completion only if score >=0.99 and critical mismatches=0.
