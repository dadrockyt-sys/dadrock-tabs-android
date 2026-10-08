# Guitar-TECHS H1 paired 20-epoch pilot — preflight green, real launch blocked

**2026-10-08 · `astra-work` · current state: DO NOT CLAIM TRAINING LAUNCHED**

## Outcome

The user explicitly replied **“I authorize”** to the proposed prospective one-factor real-P1/P2 loss-normalization comparison after the independently verified [synthetic shared-network gradient study](./GUITARTECHS_POST_V9_SHARED_NETWORK_SYNTHETIC_GRADIENT_RESULT_V1.md). This was narrowly scoped into a reviewable **20-epoch pilot**, not a full V10 run. The protocol, code and dedicated Actions workflows were committed, and the **no-media preflight succeeded**.

**Attempted GitHub write of the single-use real-training launch JSON returned: `This tool call was blocked by OpenAI's safety checks`.** This is a hard execution blocker. **No real-data pilot has been dispatched**; the absent launch file was explicitly rechecked via GitHub `fetch_file` (404). Do not work around or retry the safety block through a different endpoint, smaller payload, browser, credentials or external service. An authorized user may review the protocol and decide how to proceed using an approved execution surface. New assistant sessions must **not** infer a training run from the green preflight.

## Verified status, sources and limits

- User approval receipt committed: `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_AUTHORIZATION_V1.json`.
- Frozen protocol committed **before any real training**: `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_PROTOCOL_V1.md`.
- Prospective trainer source is separate from V9: `astra_backend/guitartechs_training_v10/h1_pilot_core_v1.py` (Git blob `d21ae6cea23ade887f2ad8d8ac6331a20670f761`) and `astra_backend/guitartechs_training_v10/run_h1_20epoch_paired_pilot_v1.py` (blob `a17367d754aaf995b2089ac51fce5231334138df`). No modification of original V9 source or frozen metrics.
- No-media preflight launch commit `6f3c1ba827d4ab4ac0c4711365a152468293a18a`; GitHub Actions [run 37852114708](https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37852114708), job `113567305044`: **completed success** in one attempt, all source-hash, dependency, original loss and normalized loss algebra, synthetic gradients and no-weight-mutation steps passed. No P1/P2 data was downloaded in that workflow.
- Real-data workflow file exists at `.github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml` (blob `20d99b6171d9cb0c148f935883f1d783a52f3636`), but **was NOT launched**. It can only be triggered by an authorized, **currently absent** `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_TRAINING_LAUNCH_V1.json`; this creation was blocked. Thus no real-data run ID, no optimizer results, no model metrics, and no new artifacts exist for this pilot.
- Scientific design: train `original_batchmean` and `per_position_normalized` separately, both folds P1→P2 and P2→P1, 20 epochs/40 optimizer steps per arm/fold, **max total 160 optimizer steps**; original seed `20260921`, same V9 architecture and view augmentation, Adadelta and fixed V8 decoder. Single non-paid CPU-only Ubuntu runner capped **300 minutes**, one run with no retry. Experimental arm changes only `0.10*KL_batchmean` to `0.10*KL_batchmean/(200*6)`. Original V9 epoch-20 state hashes `933c5fa...` and `56b275d...` must independently reproduce before comparison. Full original 256-capture P1/P2 population only; no P3, protected song, Stage-B holdout, Production or `main`.
- Positive directional evidence was prospectively set as normalized arm obtaining strictly positive full-fold F1 **and** V4 admitted events in both P1/P2 folds, while original remains zero and exact original ep20 state hashes match. No advancement/pass claim without additional full scientific gate. No checkpoint/seed/threshold rescue or full 1000 epoch continuation.

## Explicit next handoff

**Stop at BLOCKED_LAUNCH and report the tool safety block to the user.** Maintain preflight success distinct from real-training status; no optimizer step on the approved real-data study has been confirmed. Keep the user's authorization receipt, frozen protocol and source intact. Do not self-dispatch via another connector or UI to evade the safety check. The user can separately direct an approved environment/agent to review and operate the workflow; do not present this as completed execution or imply safety clearance.

All frozen V9 scientific FAIL (macro F1 0) and V8 clean comparator (macro F1 `0.24680584415601026`) remain unchanged. Preserve rights, Go My Way quantized and spectral bass evidence separately; P3/protected songs/Stage-B, paid compute, Production and `main` stay closed.
