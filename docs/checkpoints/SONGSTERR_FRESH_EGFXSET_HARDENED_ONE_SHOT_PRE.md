# Songsterr Fresh — EGFxSet Hardened One-Shot PRE

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: PROSPECTIVELY FROZEN / ONE RUN AUTHORIZED

## Authorization

The user's instruction `Please try the run again` authorizes exactly one non-authoritative execution of the hardened pipeline against the same frozen EGFxSet candidate.

This authorization does not change any global authorization flag and does not reopen archived V143/Gomyway or any closed/reserved line.

## Immutable inputs

Media:
- EGFxSet v1.0, DOI `10.5281/zenodo.7044411`
- archive `Clean.zip`
- archive MD5 `cdb1b401960f56becc8640387910e78a`
- member `Clean/Bridge/6-0.wav`
- member bytes `722976`
- member SHA-256 `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`
- independent label: standard tuning string 6 / fret 0 / MIDI 40

Model proposals are reused from repaired run `34936227380`, artifact `10383413992`:
- artifact name `songsterr-egfxset-repaired-one-shot`
- artifact digest `sha256:c380d39bdee5c3ec2827c1ae682e83b71eabe3bc738fa27016d3bb409afe566a`
- `basic-pitch.json` SHA-256 `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`
- note identity SHA-256 `2e30685479444a8120dc3490c9c41329a89e57aa16979de42053b89a4bbb0444`
- immutable proposals: MIDI 40 at `0.011609977324263039 s`; MIDI 68 at `0.3599092970521542 s`

Basic Pitch MUST NOT be invoked in this run. Candidate confidence MUST NOT own qualification.

## Frozen environment

- GitHub Actions Ubuntu runner
- Node 20
- Python 3.10.21
- NumPy 1.26.4
- SciPy 1.15.3
- CPU only

## Frozen execution

Exactly once:

1. checkout the branch;
2. fetch prior artifact `10383413992` and verify the exact `basic-pitch.json` SHA-256;
3. fetch the exact EGFxSet archive/member and verify MD5, member SHA-256 and byte count;
4. create a reference-blind carrier structure context using the actual WAV duration and fixed 120 BPM / 4/4 / straight values solely to satisfy the existing structure-conditioned adapter contract; this carrier context is NOT timing correctness evidence;
5. run `qualify_basic_pitch_note_births_v1.py` once;
6. run `build_qualified_isolated_polyphonic_note_evidence.mjs` once;
7. run `adapt_qualified_note_evidence_v1.mjs` once;
8. score the frozen hardened diagnostic rule once;
9. upload all diagnostic JSON artifacts.

No Basic Pitch inference, threshold tuning, status rewriting, candidate substitution, retry, hand deletion, or alternate media is permitted.

## Frozen hardened diagnostic score

`PASS_INPUTS` requires exact media and Basic Pitch artifact identities.

`PASS_QUALIFICATION` requires:
- exactly 2 qualification rows bound to the immutable note identity;
- MIDI 40 status `corroborated`;
- MIDI 68 status `rejected`;
- zero `insufficient` rows;
- `candidateConfidenceUsedForDecision:false`.

`PASS_PROMOTION` requires:
- raw proposals remain preserved as MIDI `[40,68]`;
- promoted events are exactly `[40]`;
- rejected evidence preserves MIDI 68;
- unresolved onset count is 0.

`PASS_POSITION` requires the promoted MIDI 40 to have exactly one standard-tuning playable position: string 6 / fret 0 / reconstructed MIDI 40.

Overall PASS requires all four gates and successful script execution.

This result is non-authoritative. It cannot change `basicPitchAuthorized`, `v6Authorized`, `correctnessAuthorized`, `modelValidationComplete`, `customerEligibleEvents`, or `mayAdvanceDelivery`.

The historical repaired all-events smoke remains `FAIL_NON_AUTHORIZING_SMOKE` and may not be retroactively rescored.
