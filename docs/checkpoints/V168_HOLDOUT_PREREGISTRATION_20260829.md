# V168 — Cross-song holdout evaluation preregistration

Date: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`
Status: **HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED**
Classification: prospective evaluation protocol; no V168 reference-facing score has occurred.

## Why V168 exists
V167 is closed/terminal single-song calibration on **Lenny Kravitz — Are You Gonna Go My Way**. Its promoted iteration remains I005. The terminal recurrence rule `recur-gap1-earliest` scored higher on that calibration song but did not clear the prospectively frozen I006 promotion gate and was not promoted.

V168 changes the scientific question. It must not continue optimizing the Lenny song. Its purpose is to test whether a fully frozen recovery policy learned during V167 improves transcription on genuinely independent songs.

## Repository asset inventory at preregistration
The repository currently contains only one frozen professional reference set suitable for the V154/V167 scoring contract:
- Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Rhythm, Lead, and Bass are components of that same song/reference set.
- `research/v154-professional-references/scorer-ready/frontend-reference-payload.json` is therefore calibration data, not a cross-song holdout.

Repository searches performed before this preregistration found no independent second-song asset under terms including holdout reference, professional reference, ground truth, golden reference, reference MIDI, benchmark reference, expected transcription, `reference.json`, or `reference-payload.json` beyond the existing Lenny lane.

**Conclusion: no valid cross-song holdout is presently available. V168 must remain blocked and perform zero scoring until independent assets are frozen.**

## Frozen policies to compare later
V168 is a two-policy comparison only. No additional variant may be added after any holdout reference is admitted or scored.

### Policy A — promoted V167 baseline
`v168-baseline-i005-policy`
- Freeze the general recovery policy represented by V167 I005 / `gss-active-only`.
- Fixed structural settings inherited from V167:
  - active Basic Pitch context required;
  - `fundamentalPresent` required;
  - template rank >= 0.975;
  - activity support >= 0.05;
  - onset support >= 0.50;
  - candidate/max-active template score ratio >= 1.00;
  - reject nearest different active intervals {12, 19, 24};
  - top 1 addition per site;
  - Guitar polyphony cap 6;
  - inactive branch disabled.
- These thresholds/settings are frozen training/calibration choices and may not be changed on holdout.

### Policy B — fixed terminal V167 challenger
`v168-gap1-earliest-policy`
- Apply the exact Policy A recovery stream, then apply the terminal reference-blind recurrence rule:
  - group recovery additions by MIDI;
  - form connected components where consecutive addition grid steps differ by <=1;
  - retain the earliest addition in each component;
  - singleton additions remain unchanged.
- No onset/activity/score tie-break is used for this policy.
- This rule is frozen from the terminal V167 finding and may not be altered on holdout.

The song-specific V167 JSON candidates are **not** themselves cross-song candidates. For each admitted holdout song, Policy A and Policy B must be regenerated from that song's reference-blind frontend/evidence using the fixed policies above.

## Holdout admission gate
V168 scoring may not be armed until all of the following are true:
1. At least **two genuinely independent songs** have been admitted as holdout assets.
2. Each holdout song is different from `Are You Gonna Go My Way`; different artists are preferred when practical.
3. Each song has a frozen source-audio identity and a professional scorer-ready reference identity covering combined Guitar. Bass reference may exist but is not used to choose the V168 Guitar policy.
4. Reference identities/hashes and uncertainty annotations are frozen before Policy A/B outputs are scored.
5. Professional reference note/event content is unavailable to candidate generation. Candidate generation may use only source audio, fixed frontend outputs/evidence, and the frozen policy definitions.
6. For every admitted song, both Policy A and Policy B complete outputs and SHA256 identities are frozen before any professional reference for that song is opened by the scorer.
7. The complete holdout-song manifest and both policy outputs for every song are frozen before the first V168 reference-facing score call.
8. If fewer than two valid independent songs are available, status remains `HOLDOUT_ASSET_MISSING` and score calls remain **0**.

## Evaluation endpoint
Primary endpoint per song:
- combined-Guitar timing-aware pitch F1 using the frozen V154 scorer contract (primary timing tolerance as implemented by the frozen scorer).

Secondary diagnostics per song:
- primary precision;
- primary recall;
- matched events;
- generated events;
- false positives;
- false negatives;
- gross timing-aware pitch F1;
- same-measure pitch-content F1.

Bass is not a V168 policy-selection endpoint because the V167 recovery change is Guitar-only. If a holdout Bass reference exists, Bass may be reported as an invariant/sanity diagnostic only and must not influence policy selection.

## Aggregate decision rule — frozen prospectively
No single holdout song can cause promotion by itself.

Across all admitted holdout songs:
- compute **macro-average primary Guitar F1** for Policy A and Policy B, weighting each song equally;
- compute macro-average primary precision and recall for diagnostics.

Policy B passes the V168 generalization gate only if ALL are true:
1. macro-average primary Guitar F1 is at least **+0.10 percentage points** above Policy A;
2. macro-average primary precision is **not below** Policy A;
3. Policy B does not lose more than **0.25 percentage points primary F1 on any individual holdout song**;
4. there are at least two admitted/scored independent songs;
5. no holdout-driven retuning, song exclusion, variant addition, or policy mutation occurred after reference access.

If these conditions are not all met, Policy A remains the generalization baseline. A failed V168 result does not authorize returning to V167 and retuning on the Lenny song.

## Tie / inconclusive handling
- If Policy A and B are tied within numerical tolerance, retain Policy A.
- If the holdout set is incomplete, corrupted, materially ambiguous, or fewer than two songs survive predeclared quality checks, declare V168 **INCONCLUSIVE / HOLDOUT_INSUFFICIENT** rather than changing the rules.
- Do not add another policy to break a tie after seeing holdout scores.

## Reference-use and anti-leakage boundary
- Professional reference content cannot be read by candidate generation or policy code.
- No per-event reference assignments may be used to keep/drop/retime/re-pitch an event.
- No direct reference-event copying.
- No post-score candidate correction or retuning.
- No song may be removed because its score is unfavorable. Exclusion is allowed only for a prospectively documented asset-integrity failure that is determined without using comparative score direction.
- Public repository may store hashes, manifests, scorer logic, aggregate metrics, and non-copyright-sensitive receipts; private/user-provided reference bytes remain subject to the existing storage boundary.

## Implementation boundary before scoring
Before any V168 scorer workflow exists, freeze:
1. a V168 policy implementation module containing exactly Policy A and Policy B;
2. the holdout admission/manifest schema;
3. the scorer identity (initially expected to reuse frozen V154 scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855` if the admitted references satisfy that contract);
4. a generation workflow that cannot access professional reference paths;
5. complete per-song Policy A/B candidate hashes;
6. one global holdout manifest proving all candidate identities were frozen before reference scoring.

Only after those objects are frozen may a separate one-shot scorer workflow be armed.

## Score-call accounting
Current V168 score-call count: **0**.

When the admission gate is eventually satisfied, the scorer budget is exactly:
- 2 policy Guitar scores per admitted song;
- optional Bass invariant score only if prospectively included in the finalized holdout manifest, never for policy selection;
- no calibration-song score calls inside V168;
- no reproduction-control score calls unless explicitly preregistered before holdout reference access.

## Promotion / production boundary
A V168 pass establishes evidence that Policy B generalizes better than Policy A under this holdout protocol. It does **not** by itself modify `main`, Production, or the Android/web app.

Any production integration remains a separate explicit user-authorized phase with its own checkpoint, code review, and safety verification.

## Compute boundary
- CPU-only work is authorized under the current branch methodology.
- GPU/CUDA/Modal requires fresh explicit user authorization immediately before use.
- No such authorization is implied by this preregistration.

## Current next action
**Do not score.** Await or deliberately acquire/freeze at least two independent professional-reference songs, then record their identities in a V168 holdout manifest without changing this evaluation rule.
