# V154 CPU multitrack scorer checkpoint

Date: 2026-08-27 UTC
Branch: `v143-contextual-prune-lobo`

## Architecture decision

The next DadRock transcription architecture will treat source separation and guitar-role separation as different problems:

1. CPU source separation produces a broad **Other** stem rather than trying to acoustically separate Rhythm vs Lead guitar.
2. CPU note/onset transcription detects the union of guitar activity from Other.
3. Musical voice separation assigns recognized guitar notes to **Rhythm** vs **Lead** afterward.
4. Bass remains independently evaluated.
5. Fret/string assignment is evaluated after note recognition and role assignment.

This supports a fully automatic path without human correction while avoiding unnecessary Modal/L4/CUDA/GPU use.

## Scorer saved

- `validation/v154_cpu_multitrack/score_multitrack_reference.py`
- Initial scorer creation commit: `bf7ff4c5e1d5f2aaa14816216354a78ad24712fb`
- Reference contract: `validation/v154_cpu_multitrack/REFERENCE_FORMAT.md`
- Empty non-copyright reference template: `validation/v154_cpu_multitrack/reference-template.json`

The repository intentionally contains **no scraped third-party tablature data**. Professional Rhythm/Lead/Bass references may be supplied later by the user or another authorized source for private scoring.

## Metric policy

Primary metrics:

- Rhythm timing-aware pitch F1, ±0.5 step
- Lead timing-aware pitch F1, ±0.5 step
- Bass timing-aware pitch F1, ±0.5 step
- Combined Rhythm+Lead guitar-union timing-aware pitch F1, ignoring role labels
- Guitar role-assignment accuracy conditional on a correct timing-aware guitar-note match
- Timing-aware string/fret score when authorized reference position data exists

Diagnostics:

- Gross timing-aware pitch F1 at ±2 steps
- Per-measure pitch-content multiset F1

The per-measure pitch-content metric is **diagnostic only** and is forbidden for event-level candidate selection, because V153 Phase D/E proved it can award nonlocal credit to a pitch elsewhere in the same measure.

## Reference leakage boundary

- Candidate generation may not read the professional reference.
- Reference is read only at scoring time.
- Scoring does not modify candidates.
- No scored-candidate retuning or silent variant search.
- No automatic Production promotion.

## Copyright boundary

Do not scrape, download, embed, or redistribute Songsterr or other third-party professional tablature into the repository. If the user supplies a lawfully accessible/licensed reference, normalize it only for private scoring under the reference contract.

## Execution authorization

CPU-only analysis/scoring remains at assistant discretion. Fresh explicit user authorization is required before any Modal, NVIDIA L4, CUDA, or GPU execution.
