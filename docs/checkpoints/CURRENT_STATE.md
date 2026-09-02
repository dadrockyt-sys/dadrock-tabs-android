# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoint files under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## Active scientific state

**V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**

- GOAT restricted-dataset access request is submitted and still awaits explicit owner approval/denial.
- Submission is not approval; no restricted GOAT v1 bytes/assets have been admitted.
- V168 prospective reference-facing score calls = **0**.
- `main` / Production untouched.
- CPU only. Fresh explicit user authorization is required immediately before GPU/CUDA/Modal use.

## Percentage reporting

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

Parallel open-corpus development does not change the fixed V168 progress/test scoring.

## Frozen V168 / GOAT state

V168 preregistration:
- `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`, creation commit `64d724e816808aa60d766923bb1a9ce241e89e89`.

Policy A = frozen V167 I005 `gss-active-only` (`v168-baseline-i005-policy`).  
Policy B = exact Policy A stream + same-MIDI gap<=1 component collapse to earliest (`v168-gap1-earliest-policy`).

Policy B can promote only if ALL frozen criteria hold: macro Guitar F1 >= A +0.10pp; macro precision >= A; no song loses >0.25pp; >=2 independent songs; no holdout-driven retuning/exclusion/variant mutation.

Frozen V168 admission/provenance machinery:
- `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`, blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`;
- `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`, blob `9edb8a65cc809d7fe42a288d6a00cfc602f37dcc`;
- `docs/checkpoints/V168_HOLDOUT_ASSET_INTAKE_REQUIREMENTS_20260829.md`, blob `3064b8e9000fbab1b031ed32389cb82aab846876`.

GOAT requested record: Zenodo `15690894`, DOI `10.5281/zenodo.15690894`, v1, restricted, research-only / not intended for commercial-product use.

GOAT pre-access selection/integrity contract:
- `docs/checkpoints/V168_GOAT_INTEGRITY_SELECTION_PREREGISTRATION_20260901.md`, commit `be69f777524ee24a1bb92e958f38e459689db4ae`;
- `validation/v168_holdout/goat_selection_contract_v168.json`, SHA256 `8c84eefa442d4c547180e1543cace9031ca2d801c1d04956893b3fb24e71096b`;
- `validation/v168_holdout/validate_goat_selection_receipt_v168.py`, blob `2f33b8c3df1caee63abe3493b64c16d6d4889b00`;
- static selector run `33569762190`, job `100060930936`: **SUCCESS** with no audio/reference/candidate/scorer read and 0 V168 score calls.

No GOAT/new-song scorer adapter or candidate generator is armed. Frozen V154 scorer blob remains `9644e65719fbd361a9b39778ae9950c5e983e855` and is Lenny-specific.

## V167 immutable handoff

Promoted I005 Guitar F1 **42.7940586109996%**, precision **48.54280510018215%**, recall **38.26274228284279%**, TP/pred/ref **533/1098/1393**; Bass F1 **80.45325779036827%**; promoted rich SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.

Highest unpromoted `recur-gap1-earliest` Guitar F1 **42.88012872083669%**, +**0.08607010983709418pp**, below frozen +0.10pp threshold. No I006 exists.

## SplitMySong diagnostic — terminal fail-closed

Dedicated checkpoint: `docs/checkpoints/V168_SPLITMYSONG_HISTORICAL_SUPPORT_FAIL_CLOSED_20260901.md`, commit `bfd8b2e1064c2025c2edc142589fbbafa0ef464b`.

Exactly one private observation occurred: `FAIL_CLOSED_NO_CANDIDATE`; required unique steps 1471, covered 1421, missing 50; candidate=false; referenceRead=false; scorerRead=false; observation SHA256 `f6cd2d2d7f29ebce3bc550d1907149f7c0d6d2b81cab08eadfdbd6b5b8107b95`; gate SHA256 `77df30d58d3229c344ad498d78dd32db0f44b9df40f7f81011b1edd6e7e0da06`.

Do not rerun, score, weaken gate, or interpolate missing support.

## Parallel open-corpus breakthrough lane — ACTIVE / V168 ISOLATED

Preregistration:
- `docs/checkpoints/OPEN_CORPUS_BREAKTHROUGH_PREREGISTRATION_20260901.md`;
- creation commit `f0b966df4881311456b5c455161431d8a771114e`.

Boundary: V169-style development only. Do not use restricted/public-example GOAT references or Lenny professional reference for tuning; do not mutate V168; use permissively licensed public corpora; do not commit third-party audio.

### Harmonic-fundamental hypothesis

Question: can multi-harmonic/odd-harmonic evidence support the true lower guitar pitch even when literal f0 is weak relative to 2f0, improving on a binary `fundamentalPresent` gate?

Frozen development script:
- `validation/open_corpus/analyze_guitar_techs_harmonic_octave_v169.py`;
- creation commit `3f67a134f646cc35f12e9c49e545e8b0c1df5fd1`.

### P1 result

Checkpoint: `docs/checkpoints/OPEN_CORPUS_GUITAR_TECHS_P1_HARMONIC_RESULT_20260902.md`, commit `5ef3a3dff39e46e31527e2ef7824a655338a2539`.

Guitar-TECHS P1 archive:
- MD5 PASS `ca0c4674dde3805574685a313f7c39eb`;
- SHA256 `130592ae5555476ea8e4070c0f3421794ef8b5e252dfa780745d07eedd0eb4a4`.

Run `33575395022`, job `100078129343`: **SUCCESS**, 142 notes.

P1 DI: f0<2f0 **67/142 (47.1831%)**; f0<0.5*2f0 **44/142 (30.9859%)**; harmonic lower-vs-+12 result **142/142**, weak subset **67/67**, very-weak subset **44/44**.

P1 mic/amp: f0<2f0 **40/142 (28.1690%)**; f0<0.5*2f0 **21/142 (14.7887%)**; harmonic result **142/142**, weak **40/40**, very-weak **21/21**.

Report SHA256 `e804caaeff90a45adee2270c7971b63d2cc9c57cd7c9a0a9c2bdd8f137f98d7a`.

### P2 independent-player confirmation — REPLICATED

Checkpoint:
- `docs/checkpoints/OPEN_CORPUS_GUITAR_TECHS_P2_HARMONIC_CONFIRMATION_20260902.md`;
- creation commit `4b6333f40c9c419bc7db6933c9b2497671a9fca7`.

P2 confirmation used the **exact P1 formula unchanged**. Workflow commit `3ad977f11d3eba3af6324d80a626ef315476a3b1`; run `33575653483`, job `100078933242`: **SUCCESS**.

P2 archive:
- official MD5 PASS `40fbf03d8b04bb2cf42df20f36dc2254`;
- SHA256 `d6b54e40d22113d6c0a663165cb2af63735897a35bb45fc6d0ed49c944b548d9`.

137 notes across six strings.

P2 DI:
- f0<2f0 **19/137 = 13.86861313868613%**;
- f0<0.5*2f0 **0/137**;
- exact P1 formula preferred true lower pitch **137/137 = 100%**; weak subset **19/19**;
- median true-minus-octave margin `0.909773723392629`.

P2 mic/amp:
- f0<2f0 **11/137 = 8.02919708029197%**;
- f0<0.5*2f0 **4/137 = 2.9197080291970803%**;
- exact P1 formula preferred true lower pitch **137/137 = 100%**; weak **11/11**; very weak **4/4**;
- median true-minus-octave margin `0.9396754431215367`.

P2 report SHA256 `840dea4d62b0adbf2ca24ea5ff49103a0c5bc4597afd012200a169c548cc3ce2`.

Combined P1+P2 across DI+mic/amp: **558/558** lower-vs-+12 capture-note evaluations preferred the ground-truth lower pitch. Combined weak-f0 subset: **137/137**. Combined very-weak subset with examples: **69/69**.

### Interpretation

This is now a **candidate breakthrough in feature design**, because the P1 signal replicated on an independent professional player/hardware set without changing the formula. It strongly suggests that a strict literal-fundamental gate can discard usable guitar evidence.

It is **not yet an end-to-end transcription breakthrough**: the current experiment begins from a known reference pitch. The next experiment must give the algorithm competing pitch hypotheses, including false lower-octave candidates, and make it choose using audio-only harmonic coherence.

## NEXT SAFE ACTION

Freeze and test a V169-style **reference-blind candidate harmonic-coherence score** on P1/P2 development data, explicitly testing candidates at true pitch and octave confusions (`midi-12`, `midi`, `midi+12`) without using the reference to choose the winner. The reference may be used only afterward to evaluate whether the audio-only winner is correct.

The score must reward multi-harmonic coherence/odd-harmonic evidence so a false pitch one octave low cannot win solely because its second harmonic coincides with the real fundamental.

After development/freeze, validate on a separate public corpus/capture set. Keep EGSet12 benchmark-only by default and do not tune on it yet.

GOAT approval remains independent; if it arrives, immediately follow the frozen GOAT intake/admission sequence before any V168 candidate/scorer arm.

## Standing methodology

- V168 prospective evaluation is not calibration continuation.
- Open-corpus development cannot mutate V168.
- No commercial-tab scraping or unauthorized copyrighted transcription corpus ingestion.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after new scientific boundaries and immediately on GOAT approval/denial.
