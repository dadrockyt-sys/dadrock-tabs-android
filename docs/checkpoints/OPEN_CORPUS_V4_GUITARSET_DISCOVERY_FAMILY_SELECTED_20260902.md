# Open-Corpus V4 GuitarSet Discovery Family — Selected

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Scientific boundary

The preregistered V4 discovery family has now been scored exactly once on discovery players `02/04` only. This checkpoint freezes the result **before any player `05` V4 reference use**.

No thresholds, family members, qualification conditions, or deterministic selection rules may be changed based on this result.

## Frozen family

Preregistration:
- `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_DISCOVERY_FAMILY_PREREGISTRATION_20260902.md`;
- creation commit `b47a7e7a19ac865366295dfed7c5b3d7b7b00334`.

Configs:
- `H72-D025`: octave-down only, baseline MIDI >=72, duration <=0.25 s;
- `H72-D030`: octave-down only, baseline MIDI >=72, duration <=0.30 s;
- `H72-D035`: octave-down only, baseline MIDI >=72, duration <=0.35 s.

Frozen evaluator:
- `validation/open_corpus/evaluate_guitarset_v4_discovery_family.py`;
- blob `254b495c55149725dae5795b83278787b4930869`.

## Run identity

Exact discovery-family workflow:
- workflow creation commit `a69788be8498b72224e8d15d99c193016280bb70`;
- run `33584036171`;
- job `100104285213`;
- conclusion: **SUCCESS**.

Pre-reference guards passed:
- original candidate artifact identity reverified;
- candidate manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83` reverified;
- all 177 candidate JSON hashes reverified;
- candidate regeneration false;
- Basic Pitch not importable;
- exactly 117 discovery JAMS extracted (`02`=59, `04`=58);
- player `05` references absent;
- prospective `00/01/03` references absent;
- no WAV files present.

## Exact result

Status: **`V4_DISCOVERY_FAMILY_SELECTED`**.

All three frozen configs qualified:
- `H72-D025`;
- `H72-D030`;
- `H72-D035`.

The frozen deterministic selection rule selected **`H72-D035`**.

Discovery baseline:
- primary macro F1: **79.23291495571898%**;
- primary combined micro F1: **75.48820336017702%**.

### `H72-D025`

Changed pitches: **107**.

All frozen qualification conditions passed:
- event-count identity: true;
- primary macro gain strictly positive: true;
- primary combined micro gain strictly positive: true;
- player-02 primary micro non-regression: true;
- player-04 primary micro non-regression: true;
- strict50 combined micro non-regression: true;
- no discovery track primary TP loss: true.

Exact gains:
- primary combined micro: **+0.0411660277356134 pp**;
- primary macro: **+0.05617398217495406 pp**;
- player `02` primary micro: **+0.010499238805181221 pp**;
- player `04` primary micro: **+0.07064284993438719 pp**;
- strict50 combined micro: **+0.0411660277356134 pp**.

Track outcomes: 0 negative-primary-TP tracks; 6 positive-primary-TP tracks.

### `H72-D030`

Changed pitches: **137**.

All frozen qualification conditions passed.

Exact gains:
- primary combined micro: **+0.05145753466950964 pp**;
- primary macro: **+0.0689285119977967 pp**;
- player `02` primary micro: **+0.010499238805181221 pp**;
- player `04` primary micro: **+0.09082652134422631 pp**;
- strict50 combined micro: **+0.056603288136471974 pp**.

Track outcomes: 0 negative-primary-TP tracks; 8 positive-primary-TP tracks.

### `H72-D035` — SELECTED

Changed pitches: **157**.

All frozen qualification conditions passed.

Exact gains:
- primary combined micro: **+0.05660328813645776 pp**;
- primary macro: **+0.07533076559106178 pp**;
- player `02` primary micro: **+0.010499238805181221 pp**;
- player `04` primary micro: **+0.10091835704913876 pp**;
- strict50 combined micro: **+0.061749041603405885 pp**.

Track outcomes: 0 negative-primary-TP tracks; 8 positive-primary-TP tracks.

The selected config is therefore the family member with the largest frozen primary combined micro gain, as required by the preregistered deterministic selection rule.

## Frozen report identities

- score report SHA256 `ea8a15ad7d9bb436a3c7108e1cfe67231ac5d2dadf42580abdcc2832ed3339bf`;
- artifact name `guitarset-v4-discovery-family-score`;
- artifact ID `9829448816`;
- artifact ZIP SHA256 `a34320aa04467fd9ca73736e63bb93a603c02b9954c04ebf771fd1eb2bf83cf6`.

## Consequence

Only **`H72-D035`** may proceed to player-`05` confirmation. The other two family members are no longer candidates for confirmation.

Before any player-`05` V4 reference is read, a separate one-shot confirmation contract must freeze:
- the exact `H72-D035` rule;
- the confirmation scorer;
- the confirmation qualification gate;
- fail-closed behavior;
- all pre-reference artifact/provenance guards.

The player-`05` confirmation must not tune or compare thresholds. If the frozen confirmation gate fails, this V4 hypothesis closes without weakening the gate.

## Counters at this boundary

- exact V4 discovery-family score calls: **1**;
- selected config: **`H72-D035`**;
- player `05` V4 reference read: **false**;
- player `05` V4 confirmation score calls: **0**;
- GuitarSet prospective evaluation processed: **false**;
- GuitarSet prospective evaluation score calls: **0**;
- V168 prospective reference-facing score calls: **0**;
- GPU/CUDA/Modal: **none**;
- `main` / Production: **untouched**.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
