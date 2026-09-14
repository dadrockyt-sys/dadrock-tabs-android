# Songsterr Fresh V6 — Recent Corpus Delta Sweep (2026-09-14)

Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/reference-provenance search only. No media acquisition, no Basic Pitch, no V6 correctness, no archived GOAT/reference scoring, no V5/FLGD reopening.

## Preconditions reverified

- Guitar-TECHS Actions run `34754519541`, job `103716527380` is `completed/success`.
- Frozen Guitar-TECHS audit outcome remains `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; do not score or rerun.
- V6 method/scoring remain frozen under the existing preregistrations.

## Search purpose

Perform a delta search for genuinely new or materially changed public guitar corpora, emphasizing 2025–2026 releases and primary/authoritative dataset pages. A candidate is only actionable if it can plausibly clear all five pre-media gates: usable performance-audio rights, real guitar, independent performed note-level onset+pitch truth, >=1,000-positive capacity, and untouched status.

## Findings

### No newly admissible corpus surfaced

The recent primary-source search returned the same small cluster already governed by the canonical state:

- **Guitar-TECHS** remains the strongest synchronized real-guitar/MIDI corpus, but its immutable structural audit already ended at decision C before correctness.
- **Klangio GST-MM-2025** remains a strumming/chord dataset whose semi-automatic labels combine spectral-flux onset detection from the evaluated recording with motion/recording-plan information; it is already rejected for V6 note-level reference independence/granularity and unresolved dataset-audio rights.
- **GAPS v1.1** now distributes audio and carries an MIT dataset-card tag, but its high-resolution performance MIDI is produced by score-to-audio alignment using transcription-model/audio activations and therefore remains audio-derived under the frozen V6 independence rule.
- **GuitarDuets** still provides note-level MIDI for synthesized duet material rather than an independent performed note stream for the real recordings.
- **GOAT** continues to surface prominently in 2025 search results, but GOAT/reference scoring is explicitly archived/out of scope and was not reopened, inspected for correctness, acquired, or scored.
- **SynthTab/Slakh-like results** are synthesized rather than untouched real-guitar holdouts and therefore do not qualify.

### Important negative-result interpretation

This sweep strengthens the practical conclusion that the public 2025–2026 literature is not currently exposing a new corpus that clears the frozen pre-media gates. It is **not** a proof of nonexistence. The canonical rule remains: only re-screen a closed lead when a primary release, rights statement, or reference-provenance fact materially changes a hard gate.

## Sources checked

Authoritative/public pages used in the delta search included:

- Guitar-TECHS project/IEEE and Zenodo release pages.
- ISMIR 2025 / Klangio guitar-strumming repository metadata.
- GAPS official project, Zenodo, and Hugging Face dataset-card pages.
- GuitarDuets Zenodo metadata.
- ISMIR 2025 GOAT publication metadata only; archived GOAT/reference-scoring scope was not reopened.
- SynthTab project metadata to rule out synthesized-only evidence.

## Binding outcome

`recentPublicCorpusDeltaHasNewAdmissibleCandidate:false`

No corpus-specific structural preregistration is justified from this sweep. Do not acquire candidate media and do not expose correctness. Continue metadata-only replacement-corpus research only upon genuinely new evidence, or keep purpose-built independent-sensor capture at design-only status until the user explicitly authorizes any contact/spending/procurement/recording.

## Fail-closed state

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- Policy C `UNENROLLED`
- protected-song execution embargoed
- no Modal, Vercel heavy-GPU, or L4 GPU used
