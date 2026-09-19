# Jimmy PAIge Astra — Bounded Benchmark Plan V1

Status: prospective plan; no dataset selected and no real-audio evaluation authorized by this document
Date: 2026-09-19 UTC

## Decision this benchmark must support

Determine which affordable audio engine, if any, supplies sufficiently accurate and complete events for Astra to create a useful bass, lead or rhythm tab. The benchmark must locate the dominant failure stage before development effort is committed.

This plan does not assume a new neural model must be trained. Candidate engines may include existing lawful open-source components, current paid infrastructure already in budget, or a hybrid. Each candidate is compared under the same frozen interface and development fixtures.

## Budget and execution boundary

- New cash spend: CAD $0 unless the user later changes the budget.
- Prefer CPU/offline synthetic work and already-paid capacity.
- No automatic paid GPU/model dispatch.
- Record wall time, compute surface and estimated marginal cost for every candidate run.
- Stop a candidate when it cannot fit the available service timeout/memory envelope or would require unapproved recurring spend.

## Three populations

### Contract fixtures

Generated/non-copyrighted symbolic events and synthetic audio where useful. Reusable for implementation tests. Purpose: schema, invariants, error attribution and regression—not real-world quality.

### Development set

Lawfully usable, identity-pinned audio with authoritative or carefully qualified labels. Reusable for diagnosis and engineering. Results may influence the system, so this set can never become the final untouched evaluation.

### Locked final evaluation

Selected and identity-frozen before its annotations or quality results are opened. It must cover the intended product population and provide defensible rights and reference semantics. Any prior exposure moves an item to development or excludes it.

No final evaluation is selected yet. Historical GuitarSet, FLGD, IDMT, Gomyway/V143 and exposed Fresh corpora retain their recorded status and cannot be relabeled untouched.

## Coverage matrix

Every development/final plan reports coverage rather than averaging away missing product modes.

| Dimension | Required strata |
| --- | --- |
| Requested role | bass, lead guitar, rhythm guitar |
| Source | isolated role, full mix |
| Texture | single notes, simultaneous notes/chords |
| Activity | sparse, medium, dense |
| Guitar context | one guitar, overlapping lead/rhythm where available |
| Tone | clean and effected/overdriven where rights/reference permit |
| Structure | straight, triplet/swing, pickup, meter changes where available |

If a stratum lacks lawful authoritative material, report it as unvalidated. Do not infer coverage from another stratum.

## Unit of evaluation

Use track-level metrics first, then pooled counts. Report medians and worst relevant strata so long files cannot dominate the decision.

For note-event matching, freeze onset and pitch matching rules before the locked evaluation. Match events one-to-one. Report raw true positives, false positives and false negatives alongside rates.

## Stage metrics

### Requested-part extraction

- requested-role presence classification
- target energy retained and interference/leakage where isolated references exist
- downstream note-event change caused by separation
- lead/rhythm assignment accuracy where authoritative role labels exist

Audio separation scores alone cannot pass the product; downstream transcription must improve or remain correct.

### Pitch and event detection

- note precision, recall and F1
- onset precision, recall and F1
- false positives and false negatives per minute
- chord/set exact match and per-note chord precision/recall
- note-count ratio, with split/duplicate/merged-event counts

### Duration and rhythm

- offset/duration match under a prospectively frozen rule
- beat/downbeat and meter accuracy where reference exists
- onset position error in beats/subdivisions
- tied-note/rest/measure reconstruction errors

### Playability and notation

- percentage assigned to playable string/fret positions
- exact MIDI reconstruction
- unique strings in simultaneous shapes
- unresolved versus heuristic physical placements
- phrase position movement and impossible-transition counts
- renderer compatibility and PDF generation success

Playability metrics validate construction from supplied events; they do not validate that the supplied events are correct.

### Product review

For a small development-only sample, use a frozen review form scored without seeing engine identity:

- recognizable requested part
- missing musical content
- wrong extra content
- rhythm readability
- fingering plausibility
- usefulness of the four-system preview
- correction effort estimate

Human review is diagnostic until raters, protocol and acceptance rules are frozen.

## Provisional development gates

These gates decide whether a component is worth further engineering; they are not final customer-admission thresholds.

1. Contract: schema valid; complete lineage; no silent defaults; deterministic stages reproduce exactly.
2. Coverage: every claimed role has at least one authorized development fixture in isolated and mixture conditions.
3. Integrity: no customer-rendered event loses its source identity; every drop/abstention is counted.
4. Comparative value: a candidate must improve a named full-chain metric or reduce cost/latency without materially degrading another required role/stratum.
5. Operational fit: completes inside the intended 1200-second analyzer ceiling with the 600-second ownership margin and available memory/cost.
6. Failure honesty: absent/uncertain roles abstain instead of producing confident generic tabs.

Final admission thresholds will be frozen only after the development population, reference semantics and achievable error distribution are known, and before opening the locked final result. They must include both precision and recall/completeness.

## Stop conditions

Stop and record the result when:

- source identity, permission or annotation meaning is unresolved;
- the requested role cannot be represented by the reference;
- evaluation annotations or audio are exposed before the final freeze;
- a candidate needs post-result threshold tuning on the locked set;
- the method improves presentation while upstream note F1/completeness is unchanged or worse;
- a candidate exceeds authorized cost, memory or latency;
- a test failure cannot be assigned to separation, inference, structure, fingering or rendering;
- the available evidence cannot support the intended lead/rhythm/bass claim.

## Candidate comparison record

Each candidate record must include:

- code/model/version and immutable artifact identity
- input population identities and role strata
- exact configuration and random seeds where applicable
- runtime, memory, hardware and marginal cost
- stage-by-stage raw counts/metrics
- abstentions and failed files
- known data exposure and development use
- result: continue, revise under a new development version, or stop

Do not rank candidates with a single weighted score until weights are prospectively justified. Preserve the metric vector and product-stratum table.

## Milestone 3 entry criteria

Milestone 3 may build the offline adapter and synthetic end-to-end fixtures after:

- request/result schemas parse successfully;
- existing Astra backend tests remain green;
- fixtures exercise complete, partial, abstained and failed outcomes;
- fixtures cover all three roles, chords, missing duration, unresolved structure, role absence and renderer incompatibility;
- no real audio or archived scorer is required.
