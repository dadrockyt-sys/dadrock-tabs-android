# Next chat: start here

Repository: `dadrockyt-sys/dadrock-tabs-android`, branch `astra-work`.
Updated: 2026-09-27.

## Current verified position

Basic Pitch Stage A failed because recall was strong but precision was poor (27 TP / 52 FP / 4 FN).

Offline comparison is complete:
- `docs/astra/NEXT_PATH_COMPARISON_V1.json`

Selected next path:
- `docs/astra/MR_MT3_FRONT_END_FEASIBILITY_DESIGN_V1.json`
- `docs/astra/MR_MT3_FRONT_END_FEASIBILITY_AUTHORIZATION_REQUEST_V1.json`

MR-MT3 is selected over immediate SynthTab-style pretraining because it preserves a zero-optimizer, low-cost gate and has cleaner MIT licensing, while the released SynthTab corpus is ~2 TB and CC BY-NC 4.0.

## Exact next task

Offline implementation only:
1. Pin exact mt3-infer release, MR-MT3 backend provenance, checkpoint bytes/SHA-256 and licenses.
2. Implement MIDI projection to guitar programs 24-31 and pitches 40-83 only.
3. Reuse corrected pitch/onset scorer and crop boundaries.
4. Add synthetic multitrack/program/range/percussion/crop/ambiguity tests.
5. Run synthetic verification.

Do not access real P1/P2 media yet. No optimizer, no threshold search, no P3.
