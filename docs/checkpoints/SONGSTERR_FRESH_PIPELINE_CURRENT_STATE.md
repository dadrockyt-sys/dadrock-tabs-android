# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-11 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT, reference/pro scoring, training/fine-tuning, broad threshold/optimizer sweeps and duration work remain closed unless explicitly reopened.
- Never silently alter/drop MIDI or event identity.
- Preserve `/ai-tab` UX flow.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP execution stays under `scripts/songsterr-fresh/`.

Current authority remains fail-closed:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research paused
- persistent Policy C `UNENROLLED`.

## HISTORICAL CLOSED WORK

V1/V2 are frozen research diagnostics rejected as admission authority.

Historical V2 protected-song result: 1,140 preserved events; 187 corroborated / 951 not / 2 insufficient. It cannot tune V4.

V3 is closed after GuitarSet v1.1.0 external validation failed preregistered gates:
- 357/357 tracks
- 62,438 decoded events
- 11,252 V3-positive
- 10,019 correct positives
- precision `0.8904194809811589`
- one-sided 95% Wilson lower bound `0.8854816094599652`
- required lower bound `0.9900` → FAIL.

GuitarSet is historical only and MUST NOT be reused as V4 pass/fail validation.

## V4 FROZEN METHOD

V4 preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V4.md`
- initial commit `a5cec402cf3bcd6c28ac3339d4d00de4d8cdf8b2`
- synthetic-only amendment `30b2769772d0a2a2edeaa8e92bff66ce3518fede`.

Frozen implementation:
- `scripts/songsterr-fresh/independent_pitch_corroboration_v4.py`
- commit `6e9e11e60d0d6958c30edf6bb5d686d545936a19`
- contract `songsterr-fresh-temporal-consensus-pitch-corroboration-research-v4`.

Frozen V4 rule:
- mono isolated guitar, 44,100 Hz;
- existing onset + integer selected MIDI only;
- full MIDI 40..88 spectral competition;
- three 8192-sample post-onset windows at offsets 1024 / 7168 / 13312;
- spectral strict global winner + YIN semitone-cell winner required in all three windows;
- no margins, voting, confidence, duration, next onset, activation, decision surface, reference, performer/style identity or event deletion.

Controlled V4 CI is green. No protected-song V4 execution has occurred.

## IDMT EXTERNAL VALIDATION — STAGE A COMPLETE

Dataset identity:
- IDMT-SMT-Guitar Dataset v1.0.0
- DOI `10.5281/zenodo.7544110`
- archive `IDMT-SMT-GUITAR_V2.zip`
- MD5 `06796e08731bccffaed6ae59361486e4`
- SHA-256 `02816258252538603c051054219cb4bba1c0ae8c9d0a3ca5418dfc951eae997a`.

Stage A report SHA-256:
`fd9086891a9a699619810f4bccd6f0f2533c194afc6cc1b09cf80484626d704f`.

Immutable Stage A result:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_STAGE_A_RESULT.md`
- commit `b5516dd0b2d84014f4e28d45bb04bce1ba0617ca`.

Observed inventory:
- 4,292 ZIP members
- 1,173 WAV
- 667 XML
- 569 exact WAV/XML leaf-stem pairs
- pre-filter pair counts dataset1=312 / dataset2=252 / dataset3=5
- 512 unpaired WAV / 9 unpaired XML / 45 ambiguous stem groups
- WAV formats: mono 16-bit 911, mono 24-bit 261, stereo 16-bit 1; observed sample rate 44,100 Hz
- XML event fields include `onsetSec`, `offsetSec`, `pitch`, string/fret and expression metadata.

Stage A performed no model inference or correctness scoring.

## IDMT EXTERNAL VALIDATION — STAGE B MANIFEST COMPLETE

Manifest-preparation preregistration:
`docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_MANIFEST_PREREGISTRATION.md`

Manifest tool:
`scripts/songsterr-fresh/prepare_idmt_v4_stage_b_manifest.py`

Controlled manifest CI green:
- run `34656525179`
- job `103450044793`
- source `3a9b47fc67f9d0b9a7643a46d6cd460b974360d9`.

Real Stage B manifest-preparation result generated outside repo:
- output SHA-256 `dfea0060296ea2289e82041545e8da0f80dd81c5dee6668e8bc7ab08293bbdeb`
- included-manifest SHA-256 `0c7946f6ac5af341bcca155a24189c4cd85b9366c0cab3282469ad43236ca344`
- 568 included pairs / 1 mechanically excluded pair
- included dataset counts: dataset1=312 / dataset2=252 / dataset3=4
- 4,661 reference note events
- pitch range MIDI 40..92, all integer-valued
- onset range 0.19..68.0664 s
- offset range 1.4448..73.9406 s
- no Basic Pitch/V4/matching/correctness result was produced by manifest preparation.

## FINAL STAGE B SCORING CONTRACT — FROZEN BEFORE RESULTS

Primary preregistration:
`docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_PREREGISTRATION.md`
commit `63c4a2ce74b7a9da213a176f76cfac781cec0769`.

Numerical-boundary amendment, still before any real correctness result:
`docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_NUMERICAL_AMENDMENT.md`
commit `4ee6f2c557c51fbeeaa626bdc12f790311117f36`.

Matching is frozen:
- per-file one-to-one maximum-cardinality bipartite matching
- onset absolute difference <= 0.050 s
- pitch absolute difference <= 50 cents
- offsets ignored
- inclusive binary64 boundary implemented as `delta < limit OR math.isclose(delta, limit, rel_tol=0, abs_tol=1e-12)` solely to preserve the preregistered inclusive boundary.

Primary metric:
- V4-positive precision
- one-sided 95% Wilson lower bound, `z=1.6448536269514722`.

Mandatory gates:
1. all 568 files complete; zero post-hoc exclusions;
2. at least 1,000 V4-positive events;
3. pooled one-sided 95% Wilson lower bound >= 0.9900;
4. dataset1: >=100 positives and point precision >=0.9500;
5. dataset2: >=100 positives and point precision >=0.9500;
6. dataset3 remains pooled but is diagnostic only because only four files were preregistered;
7. any sample-width stratum with >=100 positives must have precision >=0.9500;
8. all identity and policy guards remain intact.

These gates are frozen before IDMT results and may not be relaxed afterward.

## OFFICIAL VALIDATION HARNESS — FROZEN / GREEN

Core harness:
`scripts/songsterr-fresh/external_idmt_v4_validation.py`
implementation commit `6b48911b3694d9057b3da279fe7a8ba820395c76`.

Official numerical adapter / entrypoint:
`scripts/songsterr-fresh/run_external_idmt_v4_validation.py`
commit `b4a224c399263bd8ecb906727f6d7331af4db5fe`.

The adapter changes only inclusive floating-point boundary comparison and adds its own/amendment hashes to implementation provenance.

Controlled official-entrypoint CI:
- workflow `.github/workflows/songsterr-fresh-idmt-v4-external-validation-ci.yml`
- green run `34657193712`
- job `103452045087`
- validated source `2d07d73aa3d6d5a6088eb26c53bf1905d22f7b78`
- compile, amended matching/Wilson/gate self-test, frozen input/gate constants, execution/non-promotion guards and no-real-IDMT guard all SUCCESS.

No real IDMT correctness result has been observed as of this checkpoint commit.

## NEXT ALLOWED ACTION — ONE OFFICIAL IDMT V4 RUN

The next and only scoring action allowed under this preregistration is one official full-corpus run on the exact 568-file manifest using the current branch source containing this checkpoint.

Before execution:
- Codespace must `git pull --ff-only` to the current branch head;
- worktree must be clean;
- preserve existing Stage A archive/report and Stage B manifest outside repo;
- use the pinned Songsterr Fresh workbench runtime: Python 3.10.x, Basic Pitch 0.4.0, NumPy 1.26.4, SoundFile 0.13.1, librosa 0.11.0;
- create a fresh work/output directory; never overwrite an existing official attempt.

During execution:
- do not edit, pull, commit, restart/rebuild the Codespace or launch a second run;
- harness prints progress for each of 568 files;
- any source/runtime/input/file failure exits fail-closed.

After execution:
- inspect only the immutable result against the frozen gates;
- no tuning, threshold changes, exclusions or reruns after any correctness result is observed;
- passing still requires a separate policy review;
- protected song remains embargoed until that later review.

## STILL FORBIDDEN

- protected-song V4 execution before separate post-IDMT policy review
- duration research
- GuitarSet rerun/tuning
- archived V143/Gomyway / GOAT / reference scoring
- threshold sweeps
- training/fine-tuning
- customer promotion from CI, hashes, reproducibility or an unreviewed IDMT result.
