# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 America/Toronto — GFN V2 frozen MIXED; synthetic six-channel debleed V1 preregistration frozen before result execution
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless the user explicitly reopens them.
- Guitar-TECHS rescue/correctness, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, protected-song execution and other explicitly closed/revealed lines remain closed.
- Never silently alter/drop decoded event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; DSP/model research stays under `scripts/songsterr-fresh/`.
- Fail closed: `basicPitchAuthorized:false`, `v6Authorized:false`, `correctnessAuthorized:false`, `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`; duration authority remains paused, Policy C `UNENROLLED`, protected-song execution embargoed.
- Ordinary metadata research/coding/GitHub/CPU/checkpoint work may proceed.
- Budget remains effectively limited to existing Vercel/model costs. No new hardware, bench equipment, audio interfaces, sensors, donor instruments, performers, studios, vendors, rights packages, or paid acquisition may be assumed.
- Do not weaken validation standards to fit budget. Synthetic/non-holdout evidence must never be represented as untouched external correctness validation.

## V6 — FROZEN

Method preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`, commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
Implementation: `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
External scoring framework: `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`, commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials remain unchanged: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; preserve each decoded event and selected integer MIDI exactly once; isolated-guitar DI evaluation path; one-to-one within-performance matching onset <= `0.050 s`, pitch <= `50 cents`; >=`1,000` pooled V6-positive estimates; pooled one-sided 95% Wilson LB >=`0.9900`; strata with >=100 positives require point precision >=`0.9500`; frozen categories `chords`, `scales`, `singlenotes`, `techniques`, `music`; deferred correctness reveal and exactly one official correctness run.

Do not alter V6 method/runtime/settings/matching/tolerances/gates/strata from holdout observations.

## GUITAR-TECHS — CLOSED OUTCOME C BEFORE CORRECTNESS

Immutable result checkpoint: `docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`, commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.
Official audit run `34754519541`, job `103716527380`, artifact ID `10317695640`, run head `f3c9d4a88740146918c34a3538c565f21079f3bf`.

Reverified evidence: 104 DI/MIDI pairs, 18,934 reference events, all 104 alignment statuses `OK`; 5 same-key overlaps + 7 unmatched note-ons; frozen decision `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; `datasetStructurallySuitable:false`. Basic Pitch/V6/correctness were never run on Guitar-TECHS. Do not score, repair/drop events, bind or rerun.

## REPLACEMENT HOLDOUT GATES

Before candidate media access all five must be defensible:
1. explicit usable/permissive performance-audio rights for product validation;
2. real guitar;
3. immutable independent performed note-level onset + pitch truth, not reconstructed from evaluated audio;
4. plausible >=1,000 V6-positive capacity without duplicate/effect inflation;
5. defensible untouched status.

If all five clear, freeze corpus-specific reference-blind inventory/alignment preregistration before media access; structural audit first; reject unsuitable data without correctness. Only after structural PASS may immutable population identities be bound, controlled synthetic/contract-only harness CI run, and exactly one ordinary-GitHub-CPU external correctness run occur. No tuning/rerun after correctness exposure.

No currently reviewed public candidate clears all five gates.

## ZERO-COST EXTERNAL-CORPUS RESEARCH — GUITAR FRETBOARD NOTES

Dataset: `collegefishiesd/guitar-fretboard-notes`.
Pinned revision: `a33a26243e88e7ccd4893bee30eac3219ec8bef8`.
Declared license: `CC-BY-SA-4.0`.

This corpus is NON_HOLDOUT feasibility research only. It contains isolated real-guitar notes labeled by exact physical string/fret and is not an admissible Songsterr Fresh correctness holdout.

Already-exposed train sources: `ele`, `eqm`, `eqm2`, 78 rows each, 234 total.
Reserved untouched sources: `deb` (`test`) and `ele_natural` (`validation`), 78 rows each.
Do not access either reserved source without a later separately frozen authorization.
Canonical train parquet SHA-256: `86ac522303251f2a5d77376261c23bf1af09b3c69183ad365b105cd230354add`.

### Train-only V1 — COMPLETE / NON_HOLDOUT

Preregistration commit `ff62869274bd509802f5c4b3e565422eb23741f3`.
Implementation/test/workflow head `7ab93ec73848b9f0fee366cbf19f1dc13b39930f`.
GitHub CPU run `34914789254`, job `104209961023`, SUCCESS.
Result checkpoint commit `535e6861bb9895f5c38161ec7877a6534cf6fa4e`.

V1 result: `eqm`->`eqm2` 41/68=`60.29%`; reverse 32/68=`47.06%`; pooled 73/136=`53.68%`; chance `39.71%`; lift `+13.97 pp`; directional gap `13.24 pp`.

### Train-only V2 session-invariance — COMPLETE / FROZEN MIXED RESULT

Preregistration commit `e528ebd1279ec883da0b786d73dd25e03aa47890`.
Implementation blob `6340ef9cfc6c8fc59d6caf83eca6a1db020a2c1b`.
Test blob `348ff567d7a5c0f88657d306be8c50a32f2682b2`.
Workflow blob `510946af72f07aedf33e475c8f8ca06ae79d30ae`.
Workflow head `fb9e391477e77e0e9d3dee42243d0e812a33d581`.
GitHub run `34915518842`, job `104212166273`, SUCCESS; 18/18 synthetic contract tests passed before real-audio execution.
Artifact ID `10375219509`; ZIP SHA-256 `2ed0080474a57810b7fcd4f1babccd0c33e9db97340aed94fae653f5f6b333cc`.
Canonical result JSON SHA-256 `0a1f39e33a791371e2f7aa6f1ccc7a25d476052be08b8eb80645129bf01869f7`.
Result checkpoint commit `4569a2f7970cde7975107146ba9ffb785066864b`.

V2 result: `eqm`->`eqm2` 36/68=`52.94%`; reverse 33/68=`48.53%`; pooled 69/136=`50.74%`; chance `39.71%`; lift `+11.03 pp`; directional gap `4.41 pp`.
Frozen comparison: pooled accuracy worsened by `2.94 pp`, directional gap improved by `8.82 pp`; frozen classification `MIXED`.
No tuning/rerun is authorized from the observed V2 result. Reserved `deb` and `ele_natural` remained untouched.

All downstream authorization remains closed:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

## PURPOSE-BUILT HOLDOUT — SOFTWARE ACTIVE, PHYSICAL ROUTE BUDGET-PAUSED

The purpose-built independent-sensor route remains the prospective technical authority, but under the current budget it may advance only through zero-additional-cost software/documentation/synthetic CI. Real hardware procurement, physical calibration, and real holdout capture remain paused.

Design authority:
- expanded design `e37d2b4662db949157d2cf4797370f05648b6940`;
- physical-reference semantics `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- capture QA/gate matrix `2b191b39f2f1c19564f1353381779acbc96fbeda`.

Capture-manifest V2.1: run `34908936464`, job `104191861049`, SUCCESS; evidence checkpoint commit `9d3b17b392bd486753cb657318c048a7ae2460a7`.
Reference-blind structural audit V1: run `34912172056`, job `104201857367`, SUCCESS; evidence checkpoint commit `df7eb9edacb170ab24e2c200b1c0a8028625f87a`.
Stage-0 contact replay V1: run `34913326360`, job `104205441130`, SUCCESS; evidence checkpoint commit `8ecc0601f84c4f7916ce1a8c08ac021fc425be25`.
These establish software-contract behavior only, not real physical sensing performance.

Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding:
- `HARDWARE_PROCUREMENT_PAUSED:true`
- `PAID_VENDOR_CONTACT_PAUSED:true`
- `PAID_PERFORMER_OR_STUDIO_WORK_PAUSED:true`
- `REAL_CALIBRATION_CAPTURE_PAUSED:true`
- `REAL_HOLDOUT_CAPTURE_PAUSED:true`
- `SOFTWARE_DOCUMENTATION_SYNTHETIC_CI_ALLOWED:true`

## SYNTHETIC SIX-CHANNEL CROSSTALK / DEBLEED V1 — PREREGISTRATION FROZEN / IMPLEMENTATION NEXT

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_SYNTHETIC_SIX_CHANNEL_CROSSTALK_DEBLEED_PREREGISTRATION_V1_2026-09-14.md`
commit `54802e0eda32f8cb65da39ea2bce70c443d16eab`.

Frozen before any official harness result execution.

Core frozen contract:
- fully local, network-free, model-free, synthetic-only NumPy CPU harness;
- exactly six immutable source channels, 8,192 samples each, generated from fixed integer-bin sinusoid tables and RMS-normalized;
- separate deterministic six-channel perturbation bank generated analytically and RMS-normalized;
- family A `distance_decay`: row-normalized inverse-distance off-diagonal weights with bleed levels `(0.00,0.02,0.05,0.10,0.20,0.35,0.50)`;
- family B `paired_conditioning`: symmetric pairs `(0,1)`, `(2,3)`, `(4,5)` with levels `(0.10,0.30,0.50,0.70,0.85,0.95)`;
- perturbation RMS scales `(0.0,0.0001,0.001,0.01)`;
- mixing `Y = M @ S + sigma*P`;
- untreated baseline `Y`;
- direct recovery `solve(M,Y)`;
- fixed ridge recovery `solve(M.T@M + 1e-4*I, M.T@Y)`;
- condition number `cond(M,2)`;
- per-channel, pooled, and max-channel NRMSE; direct/ridge improvement dB over untreated baseline;
- source/perturbation/matrix SHA-256 identities;
- no production PASS threshold.

Next mandatory order:
1. implement the frozen harness without changing the method;
2. add synthetic contract tests first, including source immutability, exact matrix families/levels, equations, deterministic hashes/results, zero-bleed direct recovery near machine precision, and authorization closure;
3. commit implementation/tests/workflow;
4. ordinary GitHub CPU CI must run compile + tests before the official harness-result step;
5. freeze a dedicated result checkpoint and update this file.

Interpretation boundary: this harness can only characterize deterministic linear debleeding when six already-separated channels and a known synthetic mixing matrix exist. It cannot create authoritative six-string truth from mono/stereo audio and cannot establish real sensor calibration, real holdout correctness, or customer readiness.

## STILL FORBIDDEN

Guitar-TECHS correctness/repair/rescue; archived V143/Gomyway; GOAT/reference scoring; GuitarSet/V3; IDMT/V4; V5/FLGD; duration research; protected-song execution; restricted corpus use outside rights; rescue via evaluated-audio-derived truth; counting synthetic/effect/duplicate derivatives as independent real evidence; changing frozen V6/scoring rules from holdout observations; real-holdout optimizer/threshold sweeps or fine-tuning; treating vendor MIDI as infallible truth; Production/customer promotion without untouched external validation plus separate policy review; new validation-route hardware/performance/vendor/studio spending under the current budget; and any access to reserved Guitar Fretboard Notes `deb` or `ele_natural` before a later separately frozen authorization.

## FRESH-CHAT HANDOFF / IMMEDIATE NEXT ACTION

Continue only on `songsterr-fresh-pipeline-v1`; re-fetch the live branch head and this file before mutation.

Immediate task: implement the already-frozen synthetic six-channel crosstalk/debleed V1 preregistration at commit `54802e0eda32f8cb65da39ea2bce70c443d16eab`, add contract tests first, then ordinary GitHub CPU CI. Keep all correctness/holdout/customer authorization false. Do not access reserved GFN sources. Do not reopen V143/Gomyway or any other closed line unless explicitly asked.
