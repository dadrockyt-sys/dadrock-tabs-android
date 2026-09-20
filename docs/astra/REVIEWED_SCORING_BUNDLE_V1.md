# Reviewed development scoring bundle

The CLI connects immutable predictions, private reviewed labels and an independently
reviewed piecewise timing map to exact-MIDI onset scoring. It does not run inference,
search timing offsets, infer missing labels or approve musical evidence.

```bash
python astra_backend/evaluation/score_reviewed_bundle.py \
  --spec /private/scoring-spec.json \
  --predictions docs/astra/evaluations/GOMYWAY_FIRST30_BASIC_PITCH_V1.json \
  --labels /private/reviewed-labels.json \
  --alignment /private/reviewed-alignment.json \
  --output /private/new-scoring-report.json
```

The output path must not already exist. Validation failure writes no report.

The spec requires version 1, scope (`whole-mix-to-rhythm` or
`whole-mix-to-combined-reference`), audioSha256 (the exact decoded excerpt),
predictionSha256, labelsSha256, alignmentSha256, sourceSha256ByRole, windowSeconds,
onsetToleranceSeconds and pitchPolicy `reviewed-sounding-midi-at-attack`.
All hashes bind exact file bytes, not their interpretation. The report includes
input hashes and the spec hash; spec hash documents settings but does not prove
when they were chosen. Freeze it prospectively before scoring, not after trying variants.

Labels require matching audioSha256, sourceSha256ByRole and pitchPolicy;
reviewStatus `complete`, unresolvedItems `[]`, coverageReviewed `true`, exact
windowSeconds and roles. Each event has a unique id, role, reviewStatus `complete`,
beat (cumulative quarter-note units), and kind: attack, rest, tie-continuation or
bend-continuation. Only an attack has MIDI; non-attacks cannot carry a MIDI target.
The reviewer must resolve sounding pitch at attack and distinguish a new attack
from a continuing bend/tie. Unresolved notation blocks approval. Rests and blank
measures must be explicitly reviewed; a coverage flag is a reviewer declaration,
not automatic completeness detection.

Alignment requires matching audioSha256, reviewStatus `complete`,
independentOfPredictions `true`, evidenceId and ordered segments. Every segment
has beatStart/beatEnd and timeStart/timeEnd. Beats and times increase; adjacent
segments meet exactly and cover the scoring window. Times interpolate linearly
within segments. The reviewer must bind the evidenceId to independently observed
landmarks; setting a boolean cannot create that evidence.

For combined bass/lead/rhythm references, exact simultaneous equal-pitch targets
are merged into one acoustic target. Near-simultaneous events are not merged.
This avoids demanding two note detections for one shared acoustic pitch, but does
not measure role attribution. Counts of merged targets are reported.

Reports contain aggregate TP/FP/FN, onset-error statistics and provenance only;
private target IDs and normalized labels are omitted. Customer delivery remains
false and roleAccuracy null. Whole-mix events unmatched to a rhythm-only reference
are not automatically false musical notes. Duration, techniques, fretboard position
and rendering accuracy are not scored by this runner.

## Current Gomyway readiness

All source images/PDFs and the frozen prediction exist. The old rhythm fixture
failed visual audit. Fresh private labels and a verified first-measure timing
anchor are not yet available; therefore no reviewed bundle is approved and no
replacement real score has been generated. See GOMYWAY_SCORING_BUNDLE_STATUS_V1.json.
