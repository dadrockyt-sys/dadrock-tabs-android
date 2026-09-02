# Open-Corpus P3 Reference-Blind Octave Bridge — FAIL

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Scientific status

**`REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL`** under the prospectively frozen P3 bridge contract.

This is a clean scientific negative result, not a runtime/integrity failure. The two-job reference-isolation workflow completed successfully. The result demonstrates that the frozen V2 harmonic selector, although perfect in the earlier controlled reference-centered +/-12 task, is **not safe as an always-on octave corrector for every Basic Pitch event in polyphonic musical excerpts**.

Do not rerun this exact P3 experiment, change its thresholds after seeing the outcome, or use P3 per-event reference errors to tune a replacement. P3 is now consumed evaluation evidence.

## Frozen preregistration / identities

Scientific preregistration:
- `docs/checkpoints/OPEN_CORPUS_P3_REFERENCE_BLIND_OCTAVE_PREREGISTRATION_20260902.md`
- creation commit `75b4ee9613da84d4a097f486d67fec79e18eb40c`.

Final pre-inference readiness checkpoint:
- `docs/checkpoints/OPEN_CORPUS_P3_REFERENCE_BLIND_BRIDGE_READY_20260902.md`
- creation commit `08a8a82cb7457baeeb0b600ff7edeb73d154093b`.

Frozen V2 evaluator:
- `validation/open_corpus/evaluate_harmonic_candidate_ranking_v2_v169.py`
- Git blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`.

Frozen harmonic helper:
- `validation/open_corpus/analyze_guitar_techs_harmonic_octave_v169.py`
- Git blob `c39305df4f875bf6aec0d5e9d5b6448a5f7404df`.

Audio-only candidate generator:
- `validation/open_corpus/generate_p3_reference_blind_octave_candidates_v169.py`
- creation commit `419829793908ebdc9cbeca767532eb165e6d478c`
- Git blob `e3fe6f88b585405751dad139d82769dd00743d69`.

Reference-only scorer:
- `validation/open_corpus/score_p3_octave_bridge_v169.py`
- creation commit `721fa5ca0262e23a9071c7a837ab16b33e83ed48`
- Git blob `70ed9ceb69584ce96945688ae45cd9c8ffa3022a`.

Basic Pitch model SHA256:
- `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`.

P3 archive:
- Guitar-TECHS Zenodo record `14963133`
- `P3_music.zip`
- official MD5 `071ba80aecf00f4a31fbd167b3f22198`
- observed SHA256 `033489e22600751fb5a1633e7d856b901c6782e0486fa02135e830780d9dbfe2`.

## Two-job workflow / isolation receipts

Workflow:
- `.github/workflows/open-corpus-p3-reference-blind-octave-bridge.yml`
- creation commit `bdda7e10312d6104c8ce9e418a58dd43b9dcf3e8`.

GitHub Actions:
- run `33578675945`
- candidate job `100088107787`: **SUCCESS**
- scorer job `100088672148`: **SUCCESS**.

Candidate job verified:
- exact frozen code identities;
- Basic Pitch 0.4.0 / TFLite 2.14.0 exact model identity;
- CPU only / CUDA unused;
- exact P3 archive MD5 + SHA256;
- exactly 24 DI/micAmp WAVs extracted;
- source ZIP deleted before candidate Python;
- no MIDI/reference file present in candidate workspace;
- candidate output surface contained JSON only;
- candidate `referenceRead=false` and V168 reference-facing score calls remained 0.

Scorer job verified:
- exact frozen scorer identity;
- Basic Pitch was not importable in scorer environment;
- frozen candidate artifact/hash verified before reference download;
- exact P3 archive independently re-downloaded and verified;
- exactly 12 MIDI references extracted;
- no WAV/MP3 audio present in scorer workspace;
- candidate regeneration = false;
- scorer audio read = false;
- V168 reference-facing score calls remained 0.

## Frozen candidate stream

Across 24 capture-work units:
- Basic Pitch baseline events: **4693**
- corrected events: **4693**
- event-count identity: **true**
- V2 changed pitch on **1121 / 4693 = 23.88663967611336%** of events
- boundary-unscored events: **0**.

Candidate freeze manifest SHA256:
- `88f1171baed46758916d48d640ca9f07476948d8292d310d7469f3f0d5849cc0`.

Frozen candidate artifact:
- artifact ID `9827623576`
- artifact ZIP digest `437031e6ed7f021694358f75e2f29033a1c53cdf249d35792291f5a624cdba7a`.

## Primary 100 ms scoring result

Combined 24-unit macro F1:
- baseline: **60.576880733206515%**
- corrected: **51.95250763325269%**
- delta: **-8.624373099953829pp**.

Combined micro:
- baseline F1 **60.8219816043777%**, precision **55.65736202855316%**, recall **67.04312114989733%**, TP/pred/ref **2612/4693/3896**;
- corrected F1 **52.5323087670276%**, precision **48.071595994033665%**, recall **57.90554414784395%**, TP/pred/ref **2256/4693/3896**;
- delta micro F1 **-8.289672837350096pp**.

Direct input:
- baseline macro F1 **59.82782636219705%**;
- corrected macro F1 **50.889836936691765%**;
- baseline micro F1 **59.718437783832876%**, TP/pred/ref **1315/2456/1948**;
- corrected micro F1 **51.36239782016349%**, TP/pred/ref **1131/2456/1948**;
- delta micro F1 **-8.356039963669389pp**.

Mic/amp:
- baseline macro F1 **61.32593510421597%**;
- corrected macro F1 **53.01517832981361%**;
- baseline micro F1 **61.98327359617682%**, TP/pred/ref **1297/2237/1948**;
- corrected micro F1 **53.76344086021506%**, TP/pred/ref **1125/2237/1948**;
- delta micro F1 **-8.21983273596176pp**.

## Strict 50 ms result

Combined macro F1:
- baseline **57.47009703962679%**
- corrected **49.22080531991671%**
- delta **-8.249291719710087pp**.

Combined micro F1:
- baseline **57.957853067877515%**
- corrected **49.97089300267784%**
- delta **-7.986960065199675pp**.

Direct-input micro delta: **-7.947320617620349pp**.  
Mic/amp micro delta: **-8.028673835125446pp**.

## Frozen classification conditions

FAIL conditions that triggered:
- combined 100 ms macro loss >0.25pp: **true**;
- direct-input 100 ms micro loss >0.10pp: **true**;
- mic/amp 100 ms micro loss >0.10pp: **true**;
- combined strict-50ms micro loss >0.10pp: **true**.

Integrity condition:
- event-count identity failure: **false**.

Therefore the prospectively frozen status is unambiguously **`REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL`**.

## Score artifact identity

Score report:
- `p3-reference-blind-octave-score.json`
- SHA256 `540cfe330e975584a0857ace2511ba021ab918b82dd1392a48452ffbebb92170`.

Score artifact:
- artifact ID `9827647977`
- ZIP digest `4fc7438f6e10e5f0f9cc00e2e0306dd98bed95094a0ab8c4b719dd8474c3669b`.

## Scientific interpretation

The controlled V2 result and this P3 result are compatible:

1. V2 is highly effective when asked a **specific octave-disambiguation question around the true pitch neighborhood**.
2. Basic Pitch already supplies many correct pitches on real music.
3. Applying V2 to every Basic Pitch event changed nearly one quarter of predictions and substantially reduced both precision and recall.
4. Therefore the promising research object is no longer an always-on re-ranker. It is a **conservative reference-blind trigger/gate** that identifies the small subset of events where an octave correction should even be considered.

This interpretation is based on the aggregate frozen result. Do **not** mine P3 per-event reference errors to fit that gate.

P3 is now an evaluation-consumed corpus for this lane. Any V3 gate may be developed with already-designated development evidence such as P1/P2 single-note material and physics/synthetic guards, but its next prospective evaluation should use fresh independent public evidence selected and frozen before outcome inspection.

## V168 isolation

- V168 prospective reference-facing score calls: **0**
- V168 Policy A/B modified: **false**
- GOAT holdout selection modified: **false**
- GOAT restricted bytes read: **false**
- GPU/CUDA/Modal: **none**
- `main` / Production: **untouched**.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
