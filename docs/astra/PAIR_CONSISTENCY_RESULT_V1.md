# Pair Consistency Diagnostic Result V1

Date: 2026-10-02
Run ID: 37085818797
Status: **SUCCESSFUL PAIR-DIAGNOSTIC PASS**

Artifact:
- id: 11261055511
- digest: `sha256:d5ca77065ff570ca8400c7b1458d4f1633a315c0f425cbd56122b90ba53e8ed4`

## Pair classifications

- S0M01: complementary_pair
- S0M02: complementary_pair
- S0M03: missing_or_silent_member
- S0M04: complementary_pair
- S0M05: complementary_pair
- S0M06: complementary_pair
- S0M07: missing_or_silent_member
- S0M08: missing_or_silent_member
- S0M09: missing_or_silent_member
- S0M10: **duplicate_bass_candidate**
- S0M11: missing_or_silent_member
- S0M12: ambiguous_pair

## Key result

S0M10 is the only duplicate-class candidate in the frozen S0 set.

Its two string stems both favor bass:
- guitar stem: guitar 0.2053, bass 0.2171
- bass stem: guitar 0.1513, bass 0.2018

The two stems are also close in energy:
- guitar stem energy 0.0049346
- bass stem energy 0.0041151
- gap ~0.789 dB

and identify each other as strongest overlap competitors.

## Protection cases

The classifier avoids destructive conclusions in the important counterexamples:
- S0M03 -> missing_or_silent_member
- S0M11 -> missing_or_silent_member
- S0M12 -> ambiguous_pair

This is materially better than single-stem energy or winner-take-all YAMNet classification.

## Decision

The pair classifier is strong enough for one bounded S0-only action experiment.

Next experiment on duplicate-class candidates only:
1. raw baseline;
2. mute the false claimed stem while leaving the companion unchanged;
3. merge the false claimed stem into the companion class and zero the false stem.

Measure:
- present companion SI-SDR before/after;
- absent false-stem residual energy;
- reconstruction consistency.

Do not generalize beyond S0. Do not apply to ambiguous or missing/silent-member pairs.
