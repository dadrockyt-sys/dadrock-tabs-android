# V8 Longer-Duration Synthetic Curriculum Result V1

Date: 2026-09-29  
Status: **V8A COMPLETED — NO ARM ADVANCES; NO TRAINING**

## Accepted execution

Accepted model-free workflow:
- run **36523314347**
- job **109260764079**
- head `8e110132c778b7158a431a99e81bf2fe182e27d5`
- artifact **11012914117**
- artifact digest `sha256:56ff7a8c938a4818ab4d4cb4bf17a59a959b57482c0b40a38a301ba9e674e640`
- conclusion: **success**

Two earlier workflow attempts failed before producing scientific output because they unnecessarily imported the full audio frontend. The accepted V8A runner is standalone timing-only. A pre-accepted accounting bug that collapsed simultaneous chord onsets was also corrected before the accepted result.

## V8A results

| Arm | Duration | Onsets/s | IOI p50 | IOI p90 | Repeat <=250 ms | Boundary fallbacks | Timing distance | Advances |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| L0 | 2 s | 1.6538 | 0.3400 s | 0.4000 s | 26.67% | 0 | 1.1331 | baseline |
| L1 | 4 s | 1.6346 | 0.3400 s | **0.8516 s** | **38.89%** | **13 / 273 (4.76%)** | **0.4926** | No |
| L2 | 6 s | 1.6410 | 0.3400 s | **0.9101 s** | 36.52% | **40 / 273 (14.65%)** | 0.5150 | No |

Frozen V2B targets:
- onset density **1.4906/s**
- IOI p50 **0.2560 s**
- IOI p90 **0.8824 s**
- repeated attacks <=250 ms **47.02%**

## L1

L1 substantially improves the timing distribution:
- timing-distance improvement vs L0: **56.52%**
- IOI p90 moves from 0.4000 s to **0.8516 s**
- repeated-attack fraction moves from 26.67% to **38.89%**
- aggregate rate remains within the frozen ±15% requirement.

However, **13/273 positive clips require deterministic boundary fallback (4.76%)**, exceeding the frozen **2%** ceiling.

Therefore L1 does not advance.

## L2

L2 also improves timing distance by **54.55%** and places IOI p90 close to V2B at **0.9101 s**.

But:
- repeated-attack error improvement falls just below the frozen **0.10** requirement;
- **40/273 clips (14.65%)** require boundary fallback.

Therefore L2 does not advance.

## Decision

**No V8 arm advances.**

Accordingly:
- no V8 waveform corpus is rendered;
- V8B paired training does not run;
- V8C synthetic sanity does not run;
- V8D V2B inference does not run;
- optimizer steps: **0**
- model inference: **0**

## Supported interpretation

Longer clips clearly make the V2B-like long IOI tail representable. The 4-second curriculum in particular moves the timing distribution much closer to V2B.

But the frozen motif-placement scheme still relies on too many boundary corrections, so it fails the prospective integrity gate before training.

This is evidence that **duration was part of the structural constraint**, but it is not evidence that longer-duration training improves transfer.

A next experiment would need to redesign motif placement so the desired timing distribution is generated natively without post-placement boundary fallback, or move to a separately authorized fresh real-domain training study.

V1.1 remains sealed. P1/P2/P3 remain closed. A2 remains closed. Main/Production are unchanged.
