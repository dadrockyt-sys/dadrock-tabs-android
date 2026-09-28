# Next chat: start here

Repository: `dadrockyt-sys/dadrock-tabs-android`, branch `astra-work`.
Updated: 2026-09-27.

## Current verified position

MR-MT3 repaired-runtime Stage-A run **36356352219**, job **108724744341** was workflow GREEN but **scientifically FAILED** the frozen gate.

Frozen result:
- `docs/astra/MR_MT3_FRONT_END_FEASIBILITY_RESULT_V1.json`
- artifact **10944877326**
- projected TP/FP/FN **0 / 0 / 31**
- projected F1 **0.0**

Important nuance:
- MR-MT3 emitted **1,777** note events across the eight captures
- **1,772** were rejected as non-guitar programs
- **5** as percussion
- **0** for pitch range
- **0** survived the frozen accepted-program contract 24-31

Do not post-hoc remap program IDs from these outcomes.

The generic frozen-pretrained-front-end branch is stopped:
- Basic Pitch: strong recall, poor precision
- MR-MT3: abundant notes but incompatible instrument-program semantics under the frozen guitar projection

## Exact next task

Offline design only for a **commercial-safe synthetic/data-diversity strategy**.

The next design should directly address representation overfitting and guitar-specific supervision while keeping storage/training bounded and licenses commercially usable.

No optimizer work, no third generic AMT front end, no threshold/program tuning on these eight captures, and no P3.
