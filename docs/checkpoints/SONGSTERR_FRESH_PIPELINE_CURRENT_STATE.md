# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-16 America/Toronto — the EGSet12 real-evaluation PRE remains consumed by a provenance-blocked first attempt, GAPS has separately failed a full-history untouched-lineage audit, and two successive metadata-only successor-corpus searches have not identified a new corpus that simultaneously provides real guitar audio, deterministic note-onset + MIDI-pitch truth, stable source/rights identity and strict untouched-lineage status. Real correctness remains **unknown**. No successor PRE or model run is currently authorized.

Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- **Do not resume archived V143/Gomyway unless the user explicitly asks.**
- GOAT/reference scoring remains closed unless explicitly reopened.
- Guitar-TECHS, GuitarSet/V3 validation, IDMT/V4, V5/FLGD, duration research, protected-song work and other closed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched.
- `songsterr_pipeline/**` remains read-only for this research line.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Never rewrite, soften or reinterpret frozen historical FAIL/C/PASS results.

## GLOBAL AUTHORIZATION — NO SUCCESSOR EXECUTION AUTHORIZED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Authorization chronology:

1. `I authorize a model run when your ready` was pre-PRE willingness/intent only.
2. `Record pre with my authorization` authorized recording EGSet12 PRE `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a` only.
3. A later `Please continue 💚` was valid post-freeze authorization for that exact EGSet12 PRE/corpus/action.
4. That authorization was consumed by authoritative run `35176277018`, job `105058572244`, attempt 1.
5. The run stopped at provenance before media/model/reference/scoring and must not be retried or rescued under that PRE.
6. Later `Please continue 💚` instructions after the consumed run authorize continuation of the already-permitted metadata/provenance research boundary, not execution on an alternate corpus. Any successor correctness run still requires a new exact PRE and fresh post-freeze authorization.

## FROZEN CANDIDATE

Final candidate remains exactly:

`S AND E AND O AND K`

Authority:

- positive-core PRE `b7cfc43b6bd7e80d9a05694b37d332f1ef540696`;
- composer `scripts/songsterr-fresh/v7_fail_closed_positive_core_v1.py`;
- composer commit `5683830ebd0573b902bf205fe972a540fbaf37a9`, blob `6174a95c14a58ddd4dca47f021e591ebee8ee736`;
- mechanical result `99b37c2875a1c2551418fc8422ae4c302bf17eae`;
- run `35121000102`, job `104878449999`, artifact `10457970208`;
- immutable label `PASS_MECHANICAL_FAIL_CLOSED_POSITIVE_CORE / NO_REAL_CORRECTNESS`.

State mapping:

- `POSITIVE_CORE_CANDIDATE` -> `corroborated`;
- `PROTECTION_REJECTED` -> `rejected`;
- `UNRESOLVED_SUPPORT_OR_CONTEXT` -> `insufficient` / abstention.

Forbidden: raw `0.01`, rank/top-K, weighted score, maximum-only rule, candidate subset, candidate-confidence rescue, reattack fallback, threshold sweep, post-hoc rescue or candidate rewrite.

## FROZEN SUPPORT / MODEL PREPARATION LINEAGE

KKT authority:

- PRE `4ea9c075ea02231206a7602457e028b65c2e7a9e`;
- module commit `7020dc21d1cbcc89597f24511bd40bd37b4c9f60`;
- blob `2daa9f7f6983a3ec894fc08a86e9bced7b1f96c4`;
- result `cfe72ac6fb2459166a25cdd0789a59d257c846d1`;
- run `35119500201`, job `104873352558`, artifact `10456247666`.

Prepared Basic Pitch identity from prior successful Songsterr-fresh proposal lineage:

- Python `3.10.21`;
- NumPy `1.26.4`;
- `tflite-runtime==2.14.0`;
- `basic-pitch==0.4.0`;
- transcriber blob `e9137496363f14cbe6194e32304c8b17b0b6569c`;
- `basic_pitch.inference.predict()` once per input;
- MIDI `40..88`;
- onset threshold `0.5`;
- frame threshold `0.3`;
- minimum note length `127.7 ms`;
- `multiple_pitch_bends=False`;
- `melodia_trick=True`.

Frozen audio preparation:

- V2 loader/validator blob `f9bef389f848c8f003ffa844b1eb2eea5754002d`;
- deterministic WAV decode / finite float64 conversion / stereo mean reduction;
- `scipy.signal.resample_poly` to `44100 Hz`;
- V6 DSP blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`, `SAMPLE_RATE=44100`, `FFT_SIZE=8192`.

These identities remain historical/prepared; no successor corpus has been run through them.

## EGSET12 PRE — CONSUMED / NO RERUN

- PRE file `docs/checkpoints/SONGSTERR_FRESH_EGSET12_REAL_EVALUATION_PRE.md`;
- PRE commit `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a`;
- parent `08a87028f5ea683b670e96f4b71625ebfdbbb7fb`;
- corpus EGSet12 v1 / Zenodo `11406378`;
- frozen first score exact MIDI + one-to-one onset match within `<=0.050 s`;
- no prospective performance pass threshold.

Authoritative result:

- result file `docs/checkpoints/SONGSTERR_FRESH_EGSET12_REAL_EVALUATION_RESULT.md`;
- result commit `1d3192adce476110c1bfa12658590e2e179d0a04`;
- workflow/head `b6cc09f1d1576f5e14586ed640e87691c38d714b`;
- run `35176277018`;
- job `105058572244`;
- attempt `1`;
- artifact ID `10478985810`;
- artifact digest `sha256:da71074013e67c09b7ae85bcafcb914ff2858bf9abb6941a27c769e403c8a53c`;
- status **`BLOCKED_UNTOUCHED_LINEAGE_PROVENANCE / REAL_EVALUATION_NOT_EXECUTED`**.

Exact provenance hit includes prior EGSet12 metadata review at commit `9c0ad09436f74b6168043a2e779b25fb3922199b`, file `docs/checkpoints/SONGSTERR_FRESH_V6_EGSET12_PREMEDIA_REJECTION.md`.

The authoritative attempt stopped before runtime setup, corpus download, Basic Pitch, qualification, annotation parsing and scoring. It produced no EGSet12 correctness evidence.

## GAPS SUCCESSOR AUDIT — FAILED UNTOUCHED PROVENANCE

Audit workflow/head:
- `80eeaa05c0a063bb193a315b0c2e1aa81041e093`;
- run `35177384414`;
- job `105061966125`;
- artifact `10479606030`;
- artifact digest `sha256:b9d54aa6e967db6929c3765e2928022eebc36abb07a090e9e742b6a0e6eb426d`.

Frozen result:
- file `docs/checkpoints/SONGSTERR_FRESH_GAPS_PROVENANCE_AUDIT_RESULT.md`;
- commit `e4eb3530e4a13e060135e92adddadfbe812a7f03`;
- status **`FAIL_PRIOR_LINEAGE_EXPOSURE / NO_CORPUS_MEDIA_OPENED`**.

Material prior-lineage hits include:
- `9a20dcde71f954d4a1704dfca2985e91366f8cc6` — `SONGSTERR_FRESH_V6_PREMEDIA_BATCH_URMP_GAPS_EGDB.md`;
- `e110d90c5f8761a4c1fd27af06fc018bc2dec24a` — `SONGSTERR_FRESH_V6_REPLACEMENT_HOLDOUT_GAPS_METADATA_REVIEW_2026-09-14.md`.

Do not rerun GAPS provenance with narrower terms to force a clean result.

## SUCCESSOR-CORPUS METADATA SEARCH

Initial search checkpoint:
- file `docs/checkpoints/SONGSTERR_FRESH_SUCCESSOR_CORPUS_METADATA_SEARCH_2026-09-16.md`;
- commit `9e92faee8b650449d67042732f05f00739f0778a`;
- status **NO ELIGIBLE UNTOUCHED REAL-GUITAR NOTE-BIRTH CORPUS SELECTED**.

That search rejected or excluded GAPS, GuitarDuets, the Jackson Lightfoot/Dhiren Wijesinghe transcription dataset, EG-IPT, EGDB variants, GuitarSet, IDMT-SMT-Guitar, FLGD, Guitar-TECHS, EGFxSet and GOAT under the current scope/relevance/provenance requirements.

Continued search checkpoint:
- file `docs/checkpoints/SONGSTERR_FRESH_SUCCESSOR_CORPUS_METADATA_SEARCH_CONTINUED_2026-09-16.md`;
- commit `35e9f786935dddd6e9960b7b98c96497e129112d`;
- status **NO ELIGIBLE UNTOUCHED REAL-GUITAR NOTE-BIRTH CORPUS SELECTED**.

New findings frozen there:

1. **GuitarJam (`Julian-br/GuitarJam`)** — real CC0 monophonic electric-guitar DI audio, but public metadata exposes no aligned MIDI/note-event pitch reference. Reject for this correctness boundary.
2. **AG-PT-set / Zenodo `10159492`** — correction: it *does* provide precise onset labels and ground-truth `pitch_midi`, so its reference semantics are scientifically suitable. However, repository history proves prior AG-PT exposure at `e114eab039e588484d4f91fba153dd56e4a4cbaf`, `225aaf022fc1fe64077d96e635bd57e99626e10e`, and `2c7becc8787202be05770bb9d9153f146880e1aa`. Reject as untouched.
3. **EG-Solo** — already exposed in historical AG-PT/EG-Solo triage and blocked there on exact-source rights/use basis. Reject as untouched.
4. **G&N/TENT electric-guitar solo lead** — already surfaced in historical triage; source-use basis unresolved. Not untouched.
5. **`magcil/guitar_style_dataset` / Zenodo `10075352`** — real electric-guitar technique recordings and exercise scores, but public metadata does not establish synchronized note-birth onset+pitch truth bound to each performed recording. Reject for this boundary.

No successor media, annotation payload, model output or correctness result was opened in either search checkpoint.

## HISTORICAL NO-RERUN / CLOSED LEDGER

Do not rerun or reconstruct:

- EGSet12 attempt `35176277018`, job `105058572244`;
- GAPS provenance audit `35177384414`, job `105061966125`, merely to force a different result;
- temporal/support `35053450282`, job `104658560061`, result `86549fcf3f15898aa551064b522ce42ca32b1b86`;
- candidate-breadth `35057264267`;
- gate-free `35057812575`;
- fixed-feature `35058404820`;
- protection/raw-fit `35059307767`;
- support-conditioned landscape `35060032406`;
- KKT `35119500201`;
- positive-core `35121000102`;
- V7 first real attempt `35051186125`.

Prior EGFxSet/V2/V7 observations remain exposed historical evidence, not untouched populations.

## CURRENT TECHNICAL CONCLUSION

The candidate remains mechanically frozen but still lacks an untouched external real-corpus correctness measurement. EGSet12 and GAPS failed strict provenance before media; AG-PT would satisfy pitch+onset reference semantics but is also historically exposed; newly found clean-looking audio corpora such as GuitarJam lack the required aligned note reference.

Therefore **real correctness remains unknown**. The scientifically valid result is still “no eligible untouched successor selected,” not relaxation of provenance, substitution of weaker labels, reopening a closed corpus by implication, or post-hoc reuse of an exposed dataset.

## NEXT ENGINEERING / RESEARCH BOUNDARY

Without explicit scope change, continue **metadata/provenance-only discovery** for a genuinely new external guitar corpus.

For any newly promising corpus:

1. freeze the pre-selection branch base;
2. search full repository history for corpus name, DOI/record ID, source repository and distinctive identifiers before media access;
3. reject immediately if prior lineage exposure is found;
4. verify from metadata that exact performed audio has deterministic onset + integer-MIDI pitch truth and a defensible research-use basis;
5. only then write a new prospective real-evaluation/scoring PRE for exact `S AND E AND O AND K`;
6. update this checkpoint to that PRE commit;
7. stop for fresh post-freeze authorization before any media/model/correctness execution.

Do not silently substitute another corpus under the consumed EGSet12 PRE.

## FRESH CHAT RESUME POINT

1. Reconcile live branch and read this checkpoint first.
2. Latest successor-search checkpoint is `docs/checkpoints/SONGSTERR_FRESH_SUCCESSOR_CORPUS_METADATA_SEARCH_CONTINUED_2026-09-16.md`, commit `35e9f786935dddd6e9960b7b98c96497e129112d`.
3. No successor corpus is selected; no successor PRE exists; no successor run is authorized.
4. EGSet12 run `35176277018` and GAPS audit `35177384414` remain frozen no-rescue evidence.
5. Candidate authority remains `99b37c2875a1c2551418fc8422ae4c302bf17eae`; KKT authority remains `cfe72ac6fb2459166a25cdd0789a59d257c846d1`.
6. Historical raw `0.01`, rank/top-K, weighted score, candidate subset and reattack fallback remain forbidden.
7. Continue metadata/provenance-only discovery unless the user explicitly changes scope.
8. Archived V143/Gomyway remains untouched.

## DO NOT DO

- Do not resume V143/Gomyway.
- Do not switch Production or `main`.
- Do not rerun EGSet12 or weaken its provenance rule.
- Do not rerun GAPS audit with narrower search terms to force a clean result.
- Do not silently substitute another corpus under PRE `2a2ed0...`.
- Do not reopen GOAT, Guitar-TECHS, GuitarSet, IDMT, FLGD, EGFxSet, EGDB, EGSet12, GAPS, AG-PT, EG-Solo or G&N as “untouched.”
- Do not tune from synthetic or real post-result values.
- Do not transfer historical raw `0.01` into the positive-core composition.
- Do not introduce rank/top-K, majority vote, weighted score, maximum-only rescue, per-MIDI exceptions, candidate subset search or reattack fallback.
- Do not alter frozen V6/V3/V7/KKT/positive-core logic in place.
- Do not open successor corpus correctness/model output before a new PRE plus fresh post-freeze authorization.

Archived V143/Gomyway remains untouched.
