# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-01 UTC  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke them.

## Active project state

**V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**

- GOAT restricted-dataset access request was submitted through Zenodo and is still awaiting the owner's decision.
- Submission is not approval. No GOAT restricted bytes, owner grant, grant conditions, or admitted GOAT assets have been received.
- V168 prospective reference-facing score calls = **0**.
- `main` / Production untouched.
- CPU only. Fresh explicit authorization is required immediately before any GPU/CUDA/Modal use.

## Percentage reporting

Fixed five-gate rubric:
1. preregistration + Policy A/B frozen — 20%;
2. admission/provenance validators frozen + self-tested — 20%;
3. external candidate screening completed to defensible stop — 20%;
4. >=2 admissible independent professional holdout songs acquired, rights/provenance frozen, exact source/reference SHA256-bound, both validators passed — 20%;
5. reference-blind Policy A/B candidates frozen for all admitted songs + prospective scoring completed — 20%.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

SplitMySong diagnostics do not count as V168 holdout testing.

## Frozen V168 evaluation

Holdout preregistration:
- `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`
- creation commit `64d724e816808aa60d766923bb1a9ce241e89e89`
- blob `3a72db20d4ebebf8e4a25f5c37125e1a40934047`.

Frozen admission/provenance machinery:
- `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`, blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`;
- `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`, blob `9edb8a65cc809d7fe42a288d6a00cfc602f37dcc`;
- `docs/checkpoints/V168_HOLDOUT_ASSET_INTAKE_REQUIREMENTS_20260829.md`, blob `3064b8e9000fbab1b031ed32389cb82aab846876`.

Frozen scorer identity remains V154 blob `9644e65719fbd361a9b39778ae9950c5e983e855`; it is Lenny-specific and no GOAT/new-song scorer adapter is armed.

### Policy A — `v168-baseline-i005-policy`
Frozen V167 I005 `gss-active-only`: active Basic Pitch context required; `fundamentalPresent`; template rank >=0.975; activity >=0.05; onset >=0.50; candidate/max-active template-score ratio >=1.00; reject nearest different active intervals {12,19,24}; max 1 addition/site; Guitar cap 6; inactive branch disabled.

### Policy B — `v168-gap1-earliest-policy`
Exact Policy A stream, then collapse same-MIDI connected components with consecutive grid gaps <=1 to earliest event; singletons unchanged.

Policy B prospective pass requires ALL:
- macro Guitar F1 >= Policy A +0.10 percentage points;
- macro precision >= Policy A;
- no individual song loses >0.25pp F1;
- >=2 independent songs scored;
- no holdout-driven retuning/exclusion/variant mutation.

## GOAT access path

Access checkpoints:
- `docs/checkpoints/V168_GOAT_ACCESS_REQUEST_READY_20260829.md`
- `docs/checkpoints/V168_GOAT_ACCESS_REQUEST_SUBMITTED_20260829.md`

Authoritative requested record: Zenodo `15690894`, DOI `10.5281/zenodo.15690894`, v1, restricted, research-only / not intended for commercial-product use.

### Pre-access GOAT integrity/selection preregistration

Created before any restricted GOAT bytes were seen:
- `docs/checkpoints/V168_GOAT_INTEGRITY_SELECTION_PREREGISTRATION_20260901.md`
- creation commit `be69f777524ee24a1bb92e958f38e459689db4ae`.

Public evidence frozen in that preregistration:
- GOAT README blob `888ae24a02c79d17e291d755d524f35546e15ea7` describes 5.9h unique DI recordings plus 29.5h augmented audio;
- `render_amp.ipynb` blob `c94e935b51cc6f68cd63b5cd1a9107013e7f4ef9` shows randomized re-amping, internal `f_measure_fine >= 0.75`, an example `Dani`/`Lithium`/`Reptilia` test split, and warns final published structure may differ;
- public issue `JackJamesLoth/GOAT-Dataset#1` was open with no comments at inspection time and reports possible `item_67`, `item_96`, `item_110` duration/EOF anomalies. These are unverified reports and the items are not automatically excluded.

Frozen GOAT-specific rules include:
- one unique base performance / base DI recording per holdout unit; re-amps/amp variants cannot count as independent songs;
- exact source/reference SHA256 pair binding before admission;
- every scored reference onset must be within `[0, sourceDuration + 0.050s]`; otherwise fail `REFERENCE_ONSET_OUTSIDE_SOURCE_EOF`;
- note offsets beyond EOF alone do not fail an item when scored onsets remain valid;
- no truncation, note dropping, time-stretch, manual shift, or repair to rescue a failing item;
- target holdout size = 3 independent works when >=3 pass; minimum remains 2;
- Tier 1 uses an official/unambiguous released GOAT-v1 test split if one exists;
- public notebook `Dani`/`Lithium`/`Reptilia` names are not authoritative unless granted v1 independently marks them as released test data;
- Tier 2 fallback uses deterministic SHA256 ranking over integrity-pass base-DI work representatives;
- selection cannot use Policy A/B scores, pitch distribution, note density, difficulty, style, model errors, or other outcome-facing statistics;
- fewer than 2 eligible works => `INCONCLUSIVE / HOLDOUT_INSUFFICIENT`, not rule weakening.

### Machine-readable GOAT selection contract — frozen/static-tested

Dedicated static-readiness checkpoint:
- `docs/checkpoints/V168_GOAT_SELECTION_STATIC_READY_20260901.md`
- creation commit `9863af8844fa1f71d966414be6a24a633ae693b9`.

Contract:
- `validation/v168_holdout/goat_selection_contract_v168.json`
- creation commit `7e89671fe3dc14e91c52cc533d0e1ceb5605c16c`
- Git blob `ae3b33d89faa6cd31bb596b8553de75cb3320b9e`
- SHA256 `8c84eefa442d4c547180e1543cace9031ca2d801c1d04956893b3fb24e71096b`.

Metadata-only receipt validator:
- `validation/v168_holdout/validate_goat_selection_receipt_v168.py`
- creation commit `263f9cdc8350f887f77fcc6021894ba2e00e26f6`
- Git blob `2f33b8c3df1caee63abe3493b64c16d6d4889b00`.

Static workflow:
- `.github/workflows/v168-goat-selection-static.yml`
- creation commit/head `bb5050522aada64304599b16ace99836a8f3eab8`
- Git blob `1d6eb422dcd02e36218ba32b11491bf123e6c5a5`.

GitHub Actions run `33569762190`, job `100060930936` completed **SUCCESS** on Ubuntu 24.04 / Python 3.10.21.

CI verified:
- exact contract blob and SHA256;
- exact validator blob;
- Python compile PASS;
- static AST guard PASS with stdlib-only imports and no audio/reference/candidate/scorer/MIDI/Guitar-Pro CLI surface;
- synthetic metadata self-test `SELF_TEST_PASS`;
- Tier 1 deterministic fixture selection `item_20`, `item_67`, `item_21` while synthetic `item_96` failed by EOF integrity rather than item name;
- Tier 2 deterministic fixture selection `base-a1`, `base-z`, `base-c`;
- insufficient one-work fixture => `INCONCLUSIVE_HOLDOUT_INSUFFICIENT`;
- negative cases rejected: selection-order drift, comparative-score leak, failed EOF item promoted to PASS;
- audioRead=false, referenceNoteEventRead=false, candidateRead=false, scorerRead=false, referenceFacingScoreCalls=0.

The repository is now prepared through the GOAT metadata-selection validation boundary without restricted data.

## V167 terminal handoff — immutable

Promoted I005 `gss-active-only`:
- Guitar F1 **42.7940586109996%**, precision **48.54280510018215%**, recall **38.26274228284279%**, TP/pred/ref **533/1098/1393**;
- Bass F1 **80.45325779036827%**, precision **83.203125%**, recall **77.87934186471663%**, TP/pred/ref **426/512/547**;
- promoted rich SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.

Highest unpromoted `recur-gap1-earliest` Guitar F1 **42.88012872083669%**, improvement **+0.08607010983709418pp**, below frozen +0.10pp threshold; SHA256 `a72ce501c6d4cdbcbbdc67370ef2b35b88ad2358921d1de90f86d7f5af4c4dbe`.

V167 closure commit `cef3d57baf346e1f01faad19bb0998d602e86386`. No I006 exists.

## SplitMySong AYGGMW diagnostic — terminal fail-closed

Dedicated result checkpoint:
- `docs/checkpoints/V168_SPLITMYSONG_HISTORICAL_SUPPORT_FAIL_CLOSED_20260901.md`
- creation commit `bfd8b2e1064c2025c2edc142589fbbafa0ef464b`.

Exactly one private SplitMySong Basic Pitch observation was run under the frozen one-shot historical-support gate.

Result:
- status `FAIL_CLOSED_NO_CANDIDATE`;
- candidate generated = false;
- required unique option steps 1471;
- missing 50;
- covered 1421/1471;
- referenceRead=false;
- scorerRead=false;
- Basic Pitch observation SHA256 `f6cd2d2d7f29ebce3bc550d1907149f7c0d6d2b81cab08eadfdbd6b5b8107b95`;
- neighborhood gate SHA256 `77df30d58d3229c344ad498d78dd32db0f44b9df40f7f81011b1edd6e7e0da06`.

Do not rerun the SplitMySong observation, interpolate/extrapolate the 50 missing shared-support values, weaken the gate, or score that failed/no-candidate diagnostic. Preserve private output read-only.

Historical full-lattice diagnostic also remains fail-closed: 1617/1805 historical V166 support steps covered (89.58448753462604%), 188 uncovered. No historical exact support source was found for the missing rows; do not reinterpret that earlier gate as PASS.

## NEXT SAFE ACTION

Repository-only pre-access GOAT preparation is complete through deterministic selection-receipt validation.

Primary next event is external: **await explicit GOAT owner approval or denial**.

If approval arrives, before any restricted-v1 admission/candidate/scorer work:
1. checkpoint exact non-secret approval wording/date/owner conditions/restrictions;
2. freeze exact Zenodo record/version and complete restricted-v1 file inventory/SHA256 identities;
3. identify the complete unique base-DI inventory and source/reference pair bindings;
4. produce the metadata-only integrity/selection receipt under the frozen contract;
5. run `validate_goat_selection_receipt_v168.py` plus the two existing holdout validators;
6. checkpoint selected >=2 assets and exact identities **before candidate generation is armed**.

Until explicit access is granted, do not build a GOAT candidate generator or GOAT/new-song scorer adapter and do not claim gate 4 complete.

## Standing safety / methodology

- V168 prospective evaluation is not calibration continuation.
- Professional-reference note/event content cannot be exposed to candidate-generation/policy code.
- Freeze all selected assets and Policy A/B candidates before any reference-facing score.
- No per-event reference choices, reference-event copying, post-score mutation, retuning, adverse-result song exclusion, gate weakening, or anomaly repair based on score direction.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save this checkpoint before future holdout admission, candidate-generation arm, scorer arm, reference-facing score, and after any new private/external boundary evidence.
