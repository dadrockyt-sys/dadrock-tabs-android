# Pixabay Bass T1 Smoke Evaluator Contract V1

Date: 2026-10-02
Status: **CONTRACT FROZEN / EXECUTION DISABLED**

## Goal
This smoke diagnostic answers only whether the frozen T1 path behaves plausibly on a small, diverse set of rights-reviewed bass fixtures.

It is not the independent paired real-development study and cannot establish product accuracy.

## Inputs
Exactly the 12 IDs in `PIXABAY_BASS_T1_SMOKE_MANIFEST_V1.json`.

Before execution every input must:
- match its expected SHA-256;
- have its Pixabay asset URL/contributor record frozen;
- remain byte-identical to the uploaded file;
- be outside Git.

## T1
Use only the prospective bass T1 configuration already documented:
- Basic Pitch 0.4.0;
- onset threshold 0.50;
- frame threshold 0.30;
- minimum note length 127.7 ms;
- returned range E1-G4 / MIDI 28-67;
- no threshold sweep;
- no frequency-range changes;
- no retries for scientific reasons.

## Output capture
For each file record:
- exact input SHA-256;
- Basic Pitch package version;
- exact model SHA-256;
- exact config JSON SHA-256;
- wall time;
- peak RSS;
- predicted event count;
- minimum/maximum predicted MIDI;
- event list: onset, offset, MIDI pitch, confidence if available;
- warnings/errors;
- no manual edits.

## Metadata-only sanity checks
These do not require musical ground truth:
1. process completes without exception;
2. all predicted pitches remain inside frozen MIDI 28-67;
3. no NaN/negative event times;
4. every event has offset > onset;
5. events are deterministically ordered;
6. identical rerun is not allowed merely to improve a result;
7. exact model/config provenance is attached.

## Diagnostic interpretation
Because these files do not have independent note-event annotations, do **not** report precision/recall/F1 as if truth existed.

Permitted descriptive diagnostics:
- zero-event file count;
- events per second;
- minimum/maximum MIDI by file;
- repeated/retrigger density on long sustained-note fixtures B22/B23;
- octave-spread warnings for nominal single-note fixtures;
- qualitative "needs annotation" flags only where the filename implies one note or a small count.

## Prospective stop rules
Stop and review if any of the following occurs:
- any file cannot be hashed to the frozen manifest value;
- package/model/config identity differs from the frozen contract;
- any crash or unreadable input;
- any predicted event outside MIDI 28-67;
- malformed event timing;
- environment exceeds the prospectively filled wall-time or memory ceiling;
- any urge to alter thresholds/settings based on outputs.

## What a successful smoke run means
Only:
- T1 can ingest the selected bass fixtures reproducibly;
- the bass-range configuration is operational;
- basic runtime/memory and event-shape behavior can be measured.

It does **not** establish:
- note accuracy;
- bass transcription quality;
- separation quality;
- tablature quality;
- full-song performance;
- commercial readiness.

## Execution gate
No execution until:
1. all 12 provenance rows are frozen;
2. immutable T1 environment/model/config hashes are frozen;
3. runtime and peak-RSS ceiling fields are filled;
4. one explicit bounded authorization is recorded.

Until then this contract is documentation only.
