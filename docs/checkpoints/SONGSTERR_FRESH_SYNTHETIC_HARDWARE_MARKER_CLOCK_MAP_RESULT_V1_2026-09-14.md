# Songsterr Fresh — Synthetic Hardware-Marker Clock Map Result V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: COMPLETE / SYNTHETIC SOFTWARE EVIDENCE ONLY

## Frozen authority

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_SYNTHETIC_HARDWARE_MARKER_CLOCK_MAP_PREREGISTRATION_V1_2026-09-14.md`
commit `ee861c0ed0c133b824115ffd3f90820d56aad7c8`.

Implementation commit: `1c7e304aab00216f0128f20b6704184f73609943`.
Implementation blob: `9b1992e366a162d92b0c92ce402d11ca815ec5d9`.
Test commit: `a3e6c2c3d0ae17373c1f9a68ee959b7087c57ad4`.
Test blob: `39b975f651a8ff2d4a50507d00219e6cd2a345fe`.
Workflow integration head: `9637ef5025f614702534d0ec667c1e114fd8157e`.
Workflow blob: `6df889ce29247b03c9844fd5a81681f9798349f2`.

## Official GitHub CPU execution

Workflow: `Songsterr Fresh Synthetic Hardware Marker Clock Map V1`.
Run: `34916421318`.
Job: `104214912711` (`synthetic-clock-map`).
Head SHA: `9637ef5025f614702534d0ec667c1e114fd8157e`.
Conclusion: SUCCESS.

Execution order was preserved:
1. frozen NumPy `2.1.3` installed;
2. harness/tests compiled;
3. synthetic contract tests ran first;
4. official frozen harness ran only after tests passed;
5. canonical result was uploaded.

Contract tests: 18/18 PASS on the first official run.

Artifact:
- ID `10377035271`;
- name `songsterr-fresh-synthetic-hardware-marker-clock-map-v1`;
- size 4,668 bytes;
- ZIP SHA-256 `3b0f59501fabad7301eb43f6343d0e6c445320eccd02cde178561e6ac8539689`.

Canonical result JSON SHA-256:
`2566b0aad10040189ea1427a9098e864575b36adafd9d529bec2afdd14259e59`.

## Frozen result summary

Contract: `songsterr-fresh-synthetic-hardware-marker-clock-map-v1`.
Algorithm contract: `hardware-marker-affine-ols-v1`.
Sample rate: 48,000 Hz.
Case count: 6.
Inherited structural timing bound used only as a synthetic diagnostic: `0.025 s`.

| Case | Max marker residual | RMS marker residual | Max truth mapping error | RMS truth mapping error | Synthetic truth <= 25 ms? |
|---|---:|---:|---:|---:|---|
| `exact_affine` | 0 | 0 | 0 | 0 | YES |
| `positive_100ppm` | 0.000008982684 s | 0.000005713083 s | 0.000001082251 s | 0.000000640268 s | YES |
| `negative_100ppm` | 0.000008982684 s | 0.000005713083 s | 0.000001082251 s | 0.000000640268 s | YES |
| `deterministic_marker_jitter_1ms` | 0.001039393939 s | 0.000680866855 s | 0.000043290043 s | 0.000026452129 s | YES |
| `quadratic_warp_10ms` | 0.001583333333 s | 0.000817002684 s | 0.001583333333 s | 0.000783034074 s | YES |
| `quadratic_warp_180ms_stress` | 0.028500000000 s | 0.014707847130 s | 0.028500000000 s | 0.014094613333 s | NO |

The exact affine case was recovered exactly under the frozen float64 runtime. The +/-100 ppm affine cases were recovered to microsecond-scale truth error, limited by synthetic 48 kHz marker sample quantization. The deterministic <=1 ms marker-jitter case remained far inside the inherited 25 ms synthetic diagnostic bound. The 10 ms quadratic warp also remained inside it. The deliberately extreme 180 ms nonlinear stress warp exceeded the inherited bound at 28.5 ms maximum truth mapping error, demonstrating that the frozen single affine transform fails visibly when the underlying synthetic clock relation is sufficiently nonlinear.

## Interpretation boundary

This result establishes only deterministic software behavior of the frozen paired-hardware-marker affine clock transform under the six preregistered synthetic inputs.

It supports the intended software contract:
- exact affine relationships are reconstructed correctly;
- fixed sample quantization and marker jitter produce finite measurable residuals;
- a fixed affine map cannot perfectly represent sufficiently nonlinear clock behavior;
- the already-existing 25 ms structural timing bound can be exercised against synthetic truth without changing it.

It does **not** establish or estimate:
- real logger oscillator drift/jitter;
- real marker-generation/detection accuracy;
- real audio-interface clock behavior;
- real sync dropout limits;
- real acquisition-QA thresholds;
- physical hardware calibration or bench PASS;
- future holdout structural suitability;
- external correctness;
- V6 readiness;
- customer eligibility or delivery authority.

No empirical hardware drift/jitter/dropout threshold was created from these synthetic results. Any such threshold remains blocked until future NON_HOLDOUT physical calibration exists and is frozen prospectively before real holdout capture.

## Authorization boundary after result

Unchanged:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Archived V143/Gomyway remains closed. Reserved Guitar Fretboard Notes sources `deb` and `ele_natural` remain untouched.
