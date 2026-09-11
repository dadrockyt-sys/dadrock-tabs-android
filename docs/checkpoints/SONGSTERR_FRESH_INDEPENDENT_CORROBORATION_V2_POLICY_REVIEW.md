# Songsterr Fresh — Independent Corroboration V2 Policy Review

Recorded: 2026-09-11 America/Toronto

Status: **REJECTED AS ADMISSION AUTHORITY / RETAINED AS RESEARCH DIAGNOSTIC**

## Decision

Independent Corroboration V2 must not be promoted into a customer-admission authority.

The frozen V2 evaluator passed its preregistered controlled/contract suite, a new Policy C-S Codespaces epoch was enrolled and qualified with exactly three canaries, and the authorized-song research execution completed once under that still-valid epoch. Those facts establish controlled behavior and same-session reproducibility, but they do not establish an independently justified correctness criterion for customer admission.

V2 therefore remains a research diagnostic only.

## Evidence considered

### Controlled boundary

The frozen controlled suite passed 15/15 deterministic fixtures with the preregistered distribution:
- 6 corroborated;
- 7 not corroborated;
- 2 insufficient.

The contract tests also proved strict tie behavior, duration-bearing evidence rejection, fixed-window fail-closed behavior, event-identity preservation, and non-promotion guards.

These fixtures test whether the implementation follows the frozen signal-processing contract. They do not establish real-world transcription correctness across unknown customer audio.

### Policy C-S execution boundary

The V2 authorized-song run used Policy C-S epoch:
- `87926671-e6e9-4cda-87ea-8f248a6dae93`

The epoch was bound to frozen source commit:
- `a76ab8cebb47a2dd1cf78243f00e436470e32df3`

The epoch passed exactly three qualification canaries and remained verified through the authorized-song research execution.

This establishes same-session reproducibility for the bound model path. Reproducibility does not imply semantic correctness.

### Authorized-song frozen research result

Across exactly 1,140 preserved upstream events:
- 187 `independently-corroborated-candidate`;
- 951 `not-independently-corroborated`;
- 2 `insufficient-evidence`.

The result retained the research-only policy boundary:
- `admissionDecisionMade=false`;
- `modelValidationComplete=false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery=false`;
- duration authority unchanged.

The aggregate 187/951/2 distribution is not a ground-truth accuracy measurement. It cannot be converted into a success rate, precision estimate, confidence prior, threshold, or customer-admission rule.

## Why promotion is rejected

V2 has no independently justified external correctness contract.

Specifically:
- the controlled fixtures are synthetic contract tests, not an independently annotated real-audio validation population;
- Policy C-S establishes execution/session reproducibility, not pitch-label truth;
- the authorized song is the protected evaluation fixture and cannot be used to tune or calibrate the method after observation;
- V2 preregistered no public validation corpus, dataset version, annotation interpretation, sampling protocol, or acceptance metric;
- there is therefore no predeclared out-of-sample estimate showing that a V2-positive event has sufficient correctness for customer admission;
- exact hashes, stable event count, deterministic execution, and aggregate positive count do not supply that missing semantic guarantee.

This is an **evidence-adequacy failure for promotion**, not an implementation failure and not a Policy C-S failure.

## Retrospective stress diagnostics

The previously known MIDI-55 (~46.2024095 s) and MIDI-64 (~79.6261406 s) authorized-song cases are now permitted to be inspected as retrospective diagnostics because the frozen V2 run has completed.

Their outcome is not required to decide this policy review. Even if one or both look favorable under V2, two protected-song examples cannot establish an independently justified customer-admission contract. If they look unfavorable, V2 must still not be patched in place from those observations.

No V2 threshold, competitor set, harmonic rule, YIN rule, window size, channel-combination policy, or controlled-fixture expectation may be changed under this preregistration based on those cases.

## Consequences

- Independent Corroboration V2 remains frozen and retained for provenance/research diagnostics.
- The 187 V2-positive events remain research labels only.
- No V2 result may delete, rewrite, or silently change upstream event identity.
- `modelValidationComplete:false` remains unchanged.
- customer-eligible events remain `0`.
- `mayAdvanceDelivery:false` remains unchanged.
- duration authority remains unchanged and duration research stays paused.
- Persistent Policy C remains `UNENROLLED`.
- The completed V2 Policy C-S epoch is historical only and may not be reused for new authority work after source drift.
- No GOAT/V143/reference/professional scorer path is reopened.

## Successor-research boundary

Any successor admission method must be a new preregistration/version. It must not be tuned to the authorized-song V1/V2 results or to the historical MIDI-55/MIDI-64 cases.

A credible successor must add genuinely independent validation evidence before any protected-song evaluation. If a public or otherwise independently annotated corpus is proposed, a new preregistration must freeze before results are viewed:
- exact dataset/version and right-to-use basis;
- exact file/subset selection;
- annotation interpretation and event-matching rules;
- sampling protocol;
- metrics;
- acceptance policy and thresholds;
- treatment of ambiguity/polyphony;
- separation between development and final evaluation data.

Until such a successor is preregistered, implemented, validated, and separately reviewed, the upstream model-evidence blocker remains unresolved and customer delivery stays fail-closed.
