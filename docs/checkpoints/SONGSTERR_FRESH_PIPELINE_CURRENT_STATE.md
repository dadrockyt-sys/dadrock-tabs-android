# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 America/Toronto — GFN V2 frozen MIXED; synthetic debleed V1 complete; hardware-marker clock-map V1 complete
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless the user explicitly reopens them.
- Guitar-TECHS rescue/correctness, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, protected-song execution and other explicitly closed/revealed lines remain closed.
- Never silently alter/drop decoded event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; DSP/model research stays under `scripts/songsterr-fresh/`.
- Fail closed: `basicPitchAuthorized:false`, `v6Authorized:false`, `correctnessAuthorized:false`, `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`; duration authority remains paused, Policy C `UNENROLLED`, protected-song execution embargoed.
- Budget remains effectively limited to existing Vercel/model costs. No new hardware, bench equipment, audio interfaces, sensors, donor instruments, performers, studios, vendors, rights packages, or paid acquisition may be assumed.
- Synthetic/non-holdout evidence must never be represented as untouched external correctness validation.

## V6 — FROZEN

Method preregistration commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
Implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
External scoring framework commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials remain unchanged: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; preserve each decoded event and selected integer MIDI exactly once; isolated-guitar DI; one-to-one matching onset <= `0.050 s`, pitch <= `50 cents`; >=`1,000` pooled V6-positive estimates; pooled one-sided 95% Wilson LB >=`0.9900`; strata with >=100 positives require point precision >=`0.9500`; frozen categories `chords`, `scales`, `singlenotes`, `techniques`, `music`; deferred correctness reveal; exactly one official correctness run.

Do not alter V6 method/runtime/settings/matching/tolerances/gates/strata from holdout observations.

## GUITAR-TECHS — CLOSED OUTCOME C

Immutable result checkpoint commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.
Official audit run `34754519541`, job `103716527380`, artifact ID `10317695640`, run head `f3c9d4a88740146918c34a3538c565f21079f3bf`.
Frozen decision `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; `datasetStructurallySuitable:false`. Basic Pitch/V6/correctness were never run. Do not rescue, repair, score, bind, or rerun.

## REPLACEMENT HOLDOUT GATES

Before candidate media access all five must be defensible: usable/permissive validation rights; real guitar; immutable independent note-level onset+pitch truth not reconstructed from evaluated audio; plausible >=1,000 V6-positive capacity without duplicate/effect inflation; defensible untouched status.

If all five clear, freeze corpus-specific reference-blind inventory/alignment preregistration before media access; structural audit first; reject unsuitable data without correctness. Only after structural PASS may immutable population identities be bound, synthetic/contract harness CI run, and exactly one ordinary-GitHub-CPU correctness run occur. No tuning/rerun after correctness exposure.

No currently reviewed public candidate clears all five gates.

## GUITAR FRETBOARD NOTES — NON_HOLDOUT TRAIN-ONLY RESEARCH

Dataset `collegefishiesd/guitar-fretboard-notes`, pinned revision `a33a26243e88e7ccd4893bee30eac3219ec8bef8`, declared `CC-BY-SA-4.0`.
Allowed exposed train sources: `ele`, `eqm`, `eqm2`, 78 rows each, 234 total.
Reserved untouched sources: `deb` (`test`) and `ele_natural` (`validation`), 78 rows each.
Canonical train parquet SHA-256 `86ac522303251f2a5d77376261c23bf1af09b3c69183ad365b105cd230354add`.
Do not access reserved sources without a later separately frozen authorization.

### V1 — COMPLETE

Preregistration `ff62869274bd509802f5c4b3e565422eb23741f3`; integration head `7ab93ec73848b9f0fee366cbf19f1dc13b39930f`; run `34914789254`, job `104209961023`, SUCCESS; result checkpoint `535e6861bb9895f5c38161ec7877a6534cf6fa4e`.
Result: forward `60.29%`, reverse `47.06%`, pooled `53.68%`, chance `39.71%`, lift `+13.97 pp`, directional gap `13.24 pp`.

### V2 SESSION-INVARIANCE — COMPLETE / FROZEN MIXED

Preregistration `e528ebd1279ec883da0b786d73dd25e03aa47890`; implementation blob `6340ef9cfc6c8fc59d6caf83eca6a1db020a2c1b`; test blob `348ff567d7a5c0f88657d306be8c50a32f2682b2`; workflow blob `510946af72f07aedf33e475c8f8ca06ae79d30ae`; head `fb9e391477e77e0e9d3dee42243d0e812a33d581`; run `34915518842`, job `104212166273`, SUCCESS; 18/18 tests passed first.
Artifact `10375219509`, ZIP SHA `2ed0080474a57810b7fcd4f1babccd0c33e9db97340aed94fae653f5f6b333cc`; result JSON SHA `0a1f39e33a791371e2f7aa6f1ccc7a25d476052be08b8eb80645129bf01869f7`; result checkpoint `4569a2f7970cde7975107146ba9ffb785066864b`.
Result: forward `52.94%`, reverse `48.53%`, pooled `50.74%`, chance `39.71%`, lift `+11.03 pp`, directional gap `4.41 pp`; vs V1 pooled `-2.94 pp`, gap `-8.82 pp`; frozen classification `MIXED`. No tuning/rerun from V2. Reserved sources remained untouched.

## PURPOSE-BUILT HOLDOUT — SOFTWARE ACTIVE / PHYSICAL ROUTE BUDGET-PAUSED

Prospective authority:
- expanded design `e37d2b4662db949157d2cf4797370f05648b6940`;
- physical-reference semantics `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- capture QA/gate matrix `2b191b39f2f1c19564f1353381779acbc96fbeda`;
- hardware/calibration necessity + bench gate `a0279b8c48c51176678229abfa92576b1d1c0c95`;
- custom/hybrid topology `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf`.

Capture-manifest V2.1: run `34908936464`, job `104191861049`, SUCCESS; evidence checkpoint `9d3b17b392bd486753cb657318c048a7ae2460a7`.
Reference-blind structural audit V1: run `34912172056`, job `104201857367`, SUCCESS; evidence checkpoint `df7eb9edacb170ab24e2c200b1c0a8028625f87a`.
Stage-0 contact replay V1: run `34913326360`, job `104205441130`, SUCCESS; evidence checkpoint `8ecc0601f84c4f7916ce1a8c08ac021fc425be25`.
These prove software-contract behavior only, not real physical sensing performance.

Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding: hardware procurement, paid vendor/performer/studio work, real calibration capture, and real holdout capture are paused; software/documentation/synthetic CI is allowed.

## SYNTHETIC SIX-CHANNEL CROSSTALK / DEBLEED V1 — COMPLETE

Preregistration `54802e0eda32f8cb65da39ea2bce70c443d16eab`; implementation blob `a41dbe3131167f09e748a15843143ecfe1e57d8c`, commit `a3d26f1bd399c915466f39ed86529810dabd613d`; tests blob `55f61041e97c42738865b47d6b614ba829f7455c`, commit `a9626d0e409fca43110516ad9fdc695f1badc64c`; workflow blob `404c53970806eda15a3757192ae5712ae68c6deb`, head `39f5b2cef2141f7df5377d4ce24ecabebe617011`; run `34915944228`, job `104213442029`, SUCCESS; 16/16 tests passed first.
Artifact `10376620438`, ZIP SHA `53064b9521177251f7e5bb17f672927d8cf7be173fd4a67effa5dd81f7f39b6b`; result JSON SHA `ece7a4525be33329b4f26d05b145f478179d22b1d0472865fd77bc44c05a5a0c`; result checkpoint `f233da0000188977334331c4614b6e541ae2490b`.

Main finding: exact known-matrix inversion removes synthetic bleed to float64 precision without perturbation; perturbation amplification grows with condition number. Hardest frozen case (paired bleed `0.95`, condition `39.0`, `sigma=0.01`): untreated pooled NRMSE `0.9500526301`, direct `0.1414678382`, fixed ridge `0.1387224500`. Synthetic software evidence only.

## HARDWARE-MARKER CLOCK MAP V1 — COMPLETE

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_SYNTHETIC_HARDWARE_MARKER_CLOCK_MAP_PREREGISTRATION_V1_2026-09-14.md`
commit `ee861c0ed0c133b824115ffd3f90820d56aad7c8`.

Implementation commit `1c7e304aab00216f0128f20b6704184f73609943`, blob `9b1992e366a162d92b0c92ce402d11ca815ec5d9`.
Test commit `a3e6c2c3d0ae17373c1f9a68ee959b7087c57ad4`, blob `39b975f651a8ff2d4a50507d00219e6cd2a345fe`.
Workflow integration head `9637ef5025f614702534d0ec667c1e114fd8157e`, workflow blob `6df889ce29247b03c9844fd5a81681f9798349f2`.
Official run `34916421318`, job `104214912711`, SUCCESS; 18/18 contract tests passed first.
Artifact `10377035271`, size 4,668 bytes, ZIP SHA `3b0f59501fabad7301eb43f6343d0e6c445320eccd02cde178561e6ac8539689`.
Canonical result JSON SHA `2566b0aad10040189ea1427a9098e864575b36adafd9d529bec2afdd14259e59`.
Result checkpoint `79293a7632915fc67f5b7ee0ac2242466ec83ea7`.

Frozen result summary:
- `exact_affine`: max truth error `0`, within synthetic 25 ms diagnostic;
- `positive_100ppm`: max truth error `0.0000010822510834 s`, within;
- `negative_100ppm`: max truth error `0.0000010822510825 s`, within;
- `deterministic_marker_jitter_1ms`: max truth error `0.0000432900432898 s`, within;
- `quadratic_warp_10ms`: max truth error `0.0015833333333344 s`, within;
- `quadratic_warp_180ms_stress`: max truth error `0.0285000000000011 s`, outside the inherited `0.025 s` synthetic diagnostic bound.

Interpretation is strictly synthetic software feasibility: the fixed all-marker affine OLS transform behaves deterministically, reconstructs affine relationships correctly, and visibly fails the synthetic 25 ms diagnostic when clock behavior is sufficiently nonlinear. No real-hardware drift/jitter/dropout threshold was created; no physical calibration/bench/holdout/correctness/customer authority was gained.

## STILL FORBIDDEN

Guitar-TECHS correctness/repair/rescue; archived V143/Gomyway; GOAT/reference scoring; GuitarSet/V3; IDMT/V4; V5/FLGD; duration research; protected-song execution; restricted corpus use outside rights; rescue via evaluated-audio-derived truth; counting synthetic/effect/duplicate derivatives as independent real evidence; changing frozen V6/scoring rules from holdout observations; real-holdout optimizer/threshold sweeps or fine-tuning; treating vendor MIDI as infallible truth; Production/customer promotion without untouched external validation plus separate policy review; new validation-route hardware/performance/vendor/studio spending under the current budget; and any access to reserved GFN `deb` or `ele_natural` before a separately frozen authorization.

## FRESH-CHAT HANDOFF / IMMEDIATE NEXT ACTION

Continue only on `songsterr-fresh-pipeline-v1`; re-fetch live head + this file before mutation.

Immediate task: review the remaining purpose-built pre-capture blockers and select the next already-implied zero-additional-cost software-only contract. Highest-value candidates are calibration-artifact identity/provenance binding and deterministic reference-decoder/configuration identity plumbing. Do not invent physical thresholds from synthetic data, do not begin real calibration/holdout capture, and keep all correctness/holdout/customer authorization false.

Do not access reserved GFN sources or reopen V143/Gomyway/other closed lines unless explicitly asked.
