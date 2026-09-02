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

Fixed V168 five-gate rubric remains unchanged.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

Parallel open-corpus development does not increase the V168 Project Progress Score and is not a V168 holdout test.

## V168 frozen evaluation

Preregistration:
- `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`
- creation commit `64d724e816808aa60d766923bb1a9ce241e89e89`.

Policy A: `v168-baseline-i005-policy` = frozen V167 I005 `gss-active-only`.

Policy B: `v168-gap1-earliest-policy` = exact Policy A stream followed by same-MIDI gap<=1 connected-component collapse to earliest event.

Policy B may promote only if ALL prospectively frozen conditions hold:
- macro Guitar F1 >= A +0.10pp;
- macro precision >= A;
- no individual holdout song loses >0.25pp F1;
- >=2 independent songs;
- no holdout-driven retuning/exclusion/variant mutation.

Frozen admission/provenance:
- `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`, blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`;
- `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`, blob `9edb8a65cc809d7fe42a288d6a00cfc602f37dcc`;
- `docs/checkpoints/V168_HOLDOUT_ASSET_INTAKE_REQUIREMENTS_20260829.md`, blob `3064b8e9000fbab1b031ed32389cb82aab846876`.

Frozen V154 scorer blob remains `9644e65719fbd361a9b39778ae9950c5e983e855`; it is Lenny-specific and no GOAT/new-song scorer adapter is armed.

## GOAT pre-access readiness — frozen

Requested dataset:
- Zenodo record `15690894`;
- DOI `10.5281/zenodo.15690894`;
- v1, restricted, research-only / not intended for commercial-product use.

Access checkpoints:
- `docs/checkpoints/V168_GOAT_ACCESS_REQUEST_READY_20260829.md`;
- `docs/checkpoints/V168_GOAT_ACCESS_REQUEST_SUBMITTED_20260829.md`.

Pre-access integrity/selection preregistration:
- `docs/checkpoints/V168_GOAT_INTEGRITY_SELECTION_PREREGISTRATION_20260901.md`;
- creation commit `be69f777524ee24a1bb92e958f38e459689db4ae`.

Machine-readable GOAT selection contract:
- `validation/v168_holdout/goat_selection_contract_v168.json`;
- Git blob `ae3b33d89faa6cd31bb596b8553de75cb3320b9e`;
- SHA256 `8c84eefa442d4c547180e1543cace9031ca2d801c1d04956893b3fb24e71096b`.

Selection-receipt validator:
- `validation/v168_holdout/validate_goat_selection_receipt_v168.py`;
- blob `2f33b8c3df1caee63abe3493b64c16d6d4889b00`.

Static selector run `33569762190`, job `100060930936`: **SUCCESS**; no audio/reference/candidate/scorer read and V168 score calls 0.

Frozen GOAT selection rules include: unique base-DI performance per holdout unit; reamps not independent; target 3 works/minimum 2; official released v1 test split if unambiguous, otherwise deterministic SHA256 ranking; item_67/96/110 are not hard-coded exclusions; source/reference SHA256 binding required; no repair/time-stretch/note dropping to rescue failures.

## V167 terminal handoff — immutable

Promoted I005 `gss-active-only`:
- Guitar F1 **42.7940586109996%**, precision **48.54280510018215%**, recall **38.26274228284279%**, TP/pred/ref **533/1098/1393**;
- Bass F1 **80.45325779036827%**;
- promoted rich SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.

Highest unpromoted `recur-gap1-earliest` Guitar F1 **42.88012872083669%**, +**0.08607010983709418pp**, below frozen +0.10pp threshold. No I006 exists.

## SplitMySong AYGGMW diagnostic — terminal fail-closed

Dedicated checkpoint:
- `docs/checkpoints/V168_SPLITMYSONG_HISTORICAL_SUPPORT_FAIL_CLOSED_20260901.md`;
- creation commit `bfd8b2e1064c2025c2edc142589fbbafa0ef464b`.

Exactly one private observation occurred:
- status `FAIL_CLOSED_NO_CANDIDATE`;
- required unique steps 1471, covered 1421, missing 50;
- candidate=false, referenceRead=false, scorerRead=false;
- observation SHA256 `f6cd2d2d7f29ebce3bc550d1907149f7c0d6d2b81cab08eadfdbd6b5b8107b95`;
- gate SHA256 `77df30d58d3229c344ad498d78dd32db0f44b9df40f7f81011b1edd6e7e0da06`.

Do not rerun, score, weaken the gate, or interpolate/extrapolate missing support.

## Parallel open-corpus breakthrough lane — ACTIVE / V168 ISOLATED

Preregistration created before real public-corpus result:
- `docs/checkpoints/OPEN_CORPUS_BREAKTHROUGH_PREREGISTRATION_20260901.md`;
- creation commit `f0b966df4881311456b5c455161431d8a771114e`.

Boundary:
- this is V169-style development only;
- do not use restricted GOAT or public GOAT example references for tuning;
- do not use Lenny professional reference for new tuning;
- do not modify V168 Policy A/B or GOAT selection from these results;
- use permissively licensed public corpora and do not commit third-party audio.

Primary corpus: Guitar-TECHS. First question: can harmonic-series evidence retain the true lower guitar pitch when literal f0 is weaker than 2f0, reducing octave/upper-harmonic confusion compared with binary `fundamentalPresent`?

### P1 single-note inventory

Workflow run `33574919010`, job `100076655414`: **SUCCESS**.

`P1_singlenotes.zip`:
- official MD5 PASS `ca0c4674dde3805574685a313f7c39eb`;
- SHA256 `130592ae5555476ea8e4070c0f3421794ef8b5e252dfa780745d07eedd0eb4a4`;
- contains synchronized per-string MIDI plus direct-input and mic/amp WAV captures.

### P1 harmonic-octave first result — PROMISING / NEEDS REPLICATION

Dedicated result checkpoint:
- `docs/checkpoints/OPEN_CORPUS_GUITAR_TECHS_P1_HARMONIC_RESULT_20260902.md`;
- creation commit `5ef3a3dff39e46e31527e2ef7824a655338a2539`.

Analysis script:
- `validation/open_corpus/analyze_guitar_techs_harmonic_octave_v169.py`;
- creation commit `3f67a134f646cc35f12e9c49e545e8b0c1df5fd1`.

Successful workflow:
- head `517d3e6a8c52bde0e3aae21f0c0804fd931f9ae1`;
- run `33575395022`;
- job `100078129343`;
- conclusion **SUCCESS**;
- CPU / Python 3.10.21.

P1 had **142** ground-truth single notes across six strings.

Direct-input result:
- f0 weaker than 2f0: **67/142 = 47.183098591549296%**;
- f0 < half 2f0: **44/142 = 30.985915492957748%**;
- frozen harmonic score preferred true lower pitch over +12-semitone interpretation: **100% overall, 100% among weak f0, 100% among very-weak f0**;
- median true-minus-octave margin `0.43499407504790505`.

Mic/amp result:
- f0 weaker than 2f0: **40/142 = 28.169014084507044%**;
- f0 < half 2f0: **21/142 = 14.788732394366198%**;
- frozen harmonic score preferred true lower pitch: **100% overall and in both weak-f0 subsets**;
- median true-minus-octave margin `0.6157824198109649`.

Aggregate report SHA256:
`e804caaeff90a45adee2270c7971b63d2cc9c57cd7c9a0a9c2bdd8f137f98d7a`.

Interpret cautiously: this is a strong P1 signal, not yet a general transcription breakthrough. The metric is evaluated around known true pitches and structurally uses odd-harmonic evidence that the octave interpretation cannot explain. It needs an independent-player replication and later a reference-blind candidate-selection test with both true and false lower-octave hypotheses.

## NEXT SAFE ACTION

**Run Guitar-TECHS P2 single notes as a confirmatory independent-player replication using the exact P1 harmonic formula unchanged.**

Before seeing P2 aggregate results, do not alter harmonic weights, frequency-band widths, weak-fundamental definitions, or success metrics based on P1.

If P2 strongly replicates, checkpoint it as a candidate breakthrough and then freeze a V169-style reference-blind feature before testing on a separate corpus/split.

GOAT approval remains an independent external event. If it arrives at any time, follow the already-frozen GOAT intake/admission sequence before any V168 candidate/scorer arm.

## Standing safety / methodology

- V168 prospective evaluation is not calibration continuation.
- Open-corpus development cannot mutate V168.
- No commercial-tab scraping or unauthorized copyrighted transcription corpus ingestion.
- No per-event professional-reference choices for V168 candidates.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save this checkpoint before/after new scientific boundaries and immediately on GOAT approval/denial.
