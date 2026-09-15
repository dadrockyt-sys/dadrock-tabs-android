# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 America/Toronto — GFN V2 frozen MIXED; synthetic six-channel debleed V1 complete; next step is review of existing purpose-built calibration/reference authority for the next $0 software contract
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

Method preregistration commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
Implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
External scoring framework commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials remain unchanged: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; preserve each decoded event and selected integer MIDI exactly once; isolated-guitar DI evaluation path; one-to-one within-performance matching onset <= `0.050 s`, pitch <= `50 cents`; >=`1,000` pooled V6-positive estimates; pooled one-sided 95% Wilson LB >=`0.9900`; strata with >=100 positives require point precision >=`0.9500`; frozen categories `chords`, `scales`, `singlenotes`, `techniques`, `music`; deferred correctness reveal and exactly one official correctness run.

Do not alter V6 method/runtime/settings/matching/tolerances/gates/strata from holdout observations.

## GUITAR-TECHS — CLOSED OUTCOME C BEFORE CORRECTNESS

Immutable result checkpoint commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.
Official audit run `34754519541`, job `103716527380`, artifact ID `10317695640`, run head `f3c9d4a88740146918c34a3538c565f21079f3bf`.
Frozen decision `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; `datasetStructurallySuitable:false`. Basic Pitch/V6/correctness were never run. Do not rescue, repair, score, bind, or rerun.

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

Dataset `collegefishiesd/guitar-fretboard-notes`, pinned revision `a33a26243e88e7ccd4893bee30eac3219ec8bef8`, declared `CC-BY-SA-4.0`.
Already-exposed train sources: `ele`, `eqm`, `eqm2`, 78 rows each, 234 total.
Reserved untouched sources: `deb` (`test`) and `ele_natural` (`validation`), 78 rows each.
Canonical train parquet SHA-256 `86ac522303251f2a5d77376261c23bf1af09b3c69183ad365b105cd230354add`.

### Train-only V1 — COMPLETE / NON_HOLDOUT

Preregistration commit `ff62869274bd509802f5c4b3e565422eb23741f3`.
Implementation/test/workflow head `7ab93ec73848b9f0fee366cbf19f1dc13b39930f`.
Run `34914789254`, job `104209961023`, SUCCESS.
Result checkpoint commit `535e6861bb9895f5c38161ec7877a6534cf6fa4e`.
V1 result: forward `60.29%`, reverse `47.06%`, pooled `53.68%`, chance `39.71%`, lift `+13.97 pp`, directional gap `13.24 pp`.

### Train-only V2 session-invariance — COMPLETE / FROZEN MIXED RESULT

Preregistration commit `e528ebd1279ec883da0b786d73dd25e03aa47890`.
Implementation blob `6340ef9cfc6c8fc59d6caf83eca6a1db020a2c1b`.
Test blob `348ff567d7a5c0f88657d306be8c50a32f2682b2`.
Workflow blob `510946af72f07aedf33e475c8f8ca06ae79d30ae`.
Workflow head `fb9e391477e77e0e9d3dee42243d0e812a33d581`.
Run `34915518842`, job `104212166273`, SUCCESS; 18/18 tests passed first.
Artifact ID `10375219509`; ZIP SHA-256 `2ed0080474a57810b7fcd4f1babccd0c33e9db97340aed94fae653f5f6b333cc`.
Result JSON SHA-256 `0a1f39e33a791371e2f7aa6f1ccc7a25d476052be08b8eb80645129bf01869f7`.
Result checkpoint commit `4569a2f7970cde7975107146ba9ffb785066864b`.
V2 result: forward `52.94%`, reverse `48.53%`, pooled `50.74%`, chance `39.71%`, lift `+11.03 pp`, directional gap `4.41 pp`.
Frozen comparison: pooled accuracy `-2.94 pp`, directional gap `-8.82 pp`; classification `MIXED`. No tuning/rerun from V2. Reserved sources remain untouched.

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

## SYNTHETIC SIX-CHANNEL CROSSTALK / DEBLEED V1 — COMPLETE

Preregistration commit `54802e0eda32f8cb65da39ea2bce70c443d16eab`, frozen before result execution.
Implementation blob `a41dbe3131167f09e748a15843143ecfe1e57d8c`, commit `a3d26f1bd399c915466f39ed86529810dabd613d`.
Test blob `55f61041e97c42738865b47d6b614ba829f7455c`, commit `a9626d0e409fca43110516ad9fdc695f1badc64c`.
Workflow blob `404c53970806eda15a3757192ae5712ae68c6deb`, workflow head `39f5b2cef2141f7df5377d4ce24ecabebe617011`.
Run `34915944228`, job `104213442029`, SUCCESS; 16/16 contract tests passed before official harness execution.
Artifact ID `10376620438`; ZIP SHA-256 `53064b9521177251f7e5bb17f672927d8cf7be173fd4a67effa5dd81f7f39b6b`.
Result JSON SHA-256 `ece7a4525be33329b4f26d05b145f478179d22b1d0472865fd77bc44c05a5a0c`.
Result checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_SYNTHETIC_SIX_CHANNEL_CROSSTALK_DEBLEED_RESULT_V1_2026-09-14.md`
commit `f233da0000188977334331c4614b6e541ae2490b`.

Frozen synthetic identities:
- source SHA-256 `8bceb544b681a5b8a507bb7c70aa0f2f379ceec42f2b7b5bf08643e089f2196c`;
- perturbation SHA-256 `9f6e18edb69aeb8d0d68dcc8c2040f4725339f94ef3f73d1c86aa6cda777da51`;
- 13 matrix cases, 52 matrix/perturbation runs, all finite.

Main finding: with an exact known invertible synthetic matrix and `sigma=0`, direct inversion recovered the six untouched source channels to float64 numerical precision even at condition number `39.0`. With perturbation, error rose strongly with conditioning. At the hardest frozen case (paired bleed `0.95`, condition `39.0`, `sigma=0.01`), untreated pooled NRMSE was `0.9500526301`, direct solve `0.1414678382`, and fixed ridge `0.1387224500`. The fixed ridge rule showed clean-case bias but slightly better robustness in that hardest noisy case.

Interpretation remains prospective software-only: if real six-channel hardware becomes available, matrix conditioning and calibration error must be measured explicitly. This result does not show that real crosstalk is linear/stable/known, does not create authoritative per-string channels from mono/stereo audio, and does not authorize any real capture or correctness work.

## ACTIVE NEXT ACTION — REVIEW EXISTING CALIBRATION / REFERENCE AUTHORITY

Before starting another experiment, re-read the existing purpose-built design, physical-reference semantics, capture QA/gate matrix, hardware/calibration necessity document, and custom/hybrid topology on this branch. Identify the next zero-additional-cost software/documentation/synthetic contract that is already implied by those authorities.

Do not create a new validation route merely because the synthetic debleed harness succeeded. Prefer a narrow contract that prepares eventual real calibration or reference integrity while preserving all current budget and correctness gates. Freeze any new method before executing its result.

## STILL FORBIDDEN

Guitar-TECHS correctness/repair/rescue; archived V143/Gomyway; GOAT/reference scoring; GuitarSet/V3; IDMT/V4; V5/FLGD; duration research; protected-song execution; restricted corpus use outside rights; rescue via evaluated-audio-derived truth; counting synthetic/effect/duplicate derivatives as independent real evidence; changing frozen V6/scoring rules from holdout observations; real-holdout optimizer/threshold sweeps or fine-tuning; treating vendor MIDI as infallible truth; Production/customer promotion without untouched external validation plus separate policy review; new validation-route hardware/performance/vendor/studio spending under the current budget; and any access to reserved Guitar Fretboard Notes `deb` or `ele_natural` before a later separately frozen authorization.

## FRESH-CHAT HANDOFF / IMMEDIATE NEXT ACTION

Continue only on `songsterr-fresh-pipeline-v1`; re-fetch the live branch head and this file before mutation.

Immediate task: review existing purpose-built calibration/reference authority and select the next already-implied $0 software-only contract. Keep all correctness/holdout/customer authorization false. Do not access reserved GFN sources. Do not reopen V143/Gomyway or any other closed line unless explicitly asked.
