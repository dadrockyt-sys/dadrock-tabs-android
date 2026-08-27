# V154 CPU multitrack scorer — reference contract

This directory contains scoring logic only. It must not contain scraped or redistributed third-party tablature.

## Intended song

- Artist: Lenny Kravitz
- Title: Are You Gonna Go My Way
- Parts: `rhythm`, `lead`, `bass`

## Why three professional parts help

The scorer evaluates four distinct questions:

1. **Combined guitar recognition** — compare generated Rhythm+Lead notes against the professional Rhythm+Lead union while ignoring role labels.
2. **Guitar role separation** — among correctly recognized guitar notes, measure whether each was assigned to Rhythm vs Lead correctly.
3. **Per-part transcription** — score Rhythm, Lead, and Bass separately.
4. **Fretboard assignment** — when the authorized reference includes string/fret positions, score timing-aware string/fret correctness independently of pitch recognition.

This separates acoustic recognition errors from musical-role errors and fretboard-placement errors.

## Required JSON shape

```json
{
  "schema": "dadrock.tabs.multitrack-reference.v1",
  "song": {
    "artist": "Lenny Kravitz",
    "title": "Are You Gonna Go My Way"
  },
  "referenceAuthorization": {
    "userProvidedOrAuthorized": true,
    "privateScoringOnly": true,
    "sourceDescription": "user-provided/licensed professional transcription"
  },
  "parts": {
    "rhythm": [],
    "lead": [],
    "bass": []
  }
}
```

Each note object must contain:

```json
{
  "measure": 1,
  "step": 0.0,
  "midi": 64,
  "stringIndex": 0,
  "fret": 0
}
```

`stringIndex` and `fret` are optional. If they are absent, pitch/timing scoring still works and position scoring is omitted.

## Metric policy

The primary note metric is **timing-aware MIDI F1 with ±0.5 of the 16-step measure grid**. A broader ±2-step match is reported as a gross diagnostic.

Per-measure MIDI multiset/pitch-content scoring is retained only as a diagnostic and must **not** be used for event-level calibration or candidate selection. This avoids the nonlocal-credit failure identified in V153 event 347.

## Leakage boundary

- Candidate generation must not read the professional reference.
- The reference is opened only at the scoring boundary.
- Scoring never writes corrections back into the candidate.
- Gold/reference results must not be used to tune or search variants of an already-scored candidate.
- No automatic Production promotion.
