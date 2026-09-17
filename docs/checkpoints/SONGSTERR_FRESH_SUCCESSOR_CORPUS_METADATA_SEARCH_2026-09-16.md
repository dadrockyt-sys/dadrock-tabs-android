# Songsterr Fresh — Successor Corpus Metadata Search

Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/provenance research only

Status: **NO ELIGIBLE UNTOUCHED REAL-GUITAR NOTE-BIRTH CORPUS SELECTED**

## 1. PURPOSE

After the authoritative EGSet12 untouched-lineage attempt was blocked before media, and after GAPS separately failed a full-history untouched-lineage audit, this checkpoint records a metadata-only search for another external real-guitar corpus suitable for a prospective first correctness measurement of the already-frozen `S AND E AND O AND K` candidate.

No candidate media, annotation payload, model output, or correctness result was opened in this search. No Basic Pitch or Songsterr-fresh qualifier was run.

## 2. REQUIRED SUCCESSOR PROPERTIES

A new untouched-lineage PRE should not be written unless public metadata and repository-history audit can support all of the following before media access:

1. real guitar performance audio rather than synthesized-only audio;
2. note-level reference information capable of deterministic pitch + onset note-birth scoring against the exact performed audio;
3. stable source/version identities that can be frozen prospectively;
4. rights/access terms compatible with research evaluation;
5. no prior Songsterr-fresh lineage exposure that defeats the intended untouched-lineage claim;
6. no dependence on an already-closed research line unless the user explicitly reopens it.

## 3. CANDIDATES REVIEWED FROM PUBLIC METADATA

### A. GAPS / Guitar-Aligned Performance Scores

Disposition: **REJECT — PRIOR LINEAGE EXPOSURE**.

A dedicated full-history audit is frozen separately in `SONGSTERR_FRESH_GAPS_PROVENANCE_AUDIT_RESULT.md` and proves prior Songsterr-fresh GAPS metadata/provenance review. No GAPS media or correctness was opened, but it is not untouched under the current strict definition.

### B. GuitarDuets — Zenodo `12802440`

Public metadata describes approximately three hours of real and synthesized classical-guitar duet recordings. Critically, the dataset description and paper state that note-level MIDI annotations are provided for the **synthesized** duets, while the real subset does not have corresponding ground-truth note-level annotations; the paper explicitly lists real-subset note annotation as future work.

Disposition: **REJECT FOR THIS BOUNDARY — real subset lacks the required deterministic note-birth reference.**

The synthetic subset is not a substitute because the present scientific question requires a real external guitar population.

### C. Jackson Lightfoot / Dhiren Wijesinghe Guitar Transcription Dataset

Public Kaggle metadata describes recorded guitar audio/video plus frame-level tablature/fretboard labels derived from video frames. The labels describe finger/string/fret state at sampled frame timestamps; public metadata does not establish a performed note-birth event reference with exact note onset semantics suitable for the frozen pitch+onset scorer.

Disposition: **REJECT FOR THIS BOUNDARY — reference semantics are fret/finger-frame labels, not validated note-birth ground truth.**

### D. EG-IPT / Electric Guitar Instrumental Playing Techniques

Public project metadata describes an electric-guitar playing-technique classification corpus and associated code. The surfaced metadata supports technique labels, not a synchronized note-birth transcription reference for complete performed notes.

Disposition: **REJECT FOR THIS BOUNDARY — task/annotation target does not supply the required note-birth correctness reference.**

### E. EGDB-PG / EGDB-NDSP

Public 2025/2026 Zenodo metadata describes large amplifier-rendered electric-guitar transcription corpora in the EGDB family. However, the Songsterr-fresh lineage already contains explicit EGDB metadata/licensing review in the September 15 replacement-holdout search.

Disposition: **DO NOT TREAT AS UNTOUCHED.**

The newer packaging/amp-rendered variant does not erase prior lineage exposure to the EGDB family for the purpose of the current strict untouched-lineage claim. No media was opened in this search.

### F. GuitarSet

Scientifically suitable note-level real-guitar data exists, but GuitarSet/V3 validation is already a closed and exposed line in this branch.

Disposition: **INELIGIBLE AS UNTOUCHED / CLOSED LINE.**

### G. IDMT-SMT-Guitar

Scientifically useful real-guitar note-event data exists, but IDMT/V4 is already a closed and exposed line in this branch.

Disposition: **INELIGIBLE AS UNTOUCHED / CLOSED LINE.**

### H. François Leduc Guitar Dataset (FLGD)

Public metadata describes real solo-guitar audio with aligned MIDI, but V5/FLGD is already a closed and exposed line in this branch.

Disposition: **INELIGIBLE AS UNTOUCHED / CLOSED LINE.**

### I. Guitar-TECHS

Public metadata describes real electric guitar, multiple signal perspectives, and synchronized per-string MIDI, but Guitar-TECHS is already a closed/exposed line under the current hard scope.

Disposition: **INELIGIBLE AS UNTOUCHED / CLOSED LINE.**

### J. EGFxSet

Already exposed historical evidence in Songsterr-fresh and therefore not untouched.

Disposition: **INELIGIBLE AS UNTOUCHED.**

### K. GOAT

Current canonical hard scope says `GOAT/reference scoring remains closed unless explicitly reopened.`

Disposition: **NOT CONSIDERED FOR EXECUTION OR PRE SELECTION IN THIS CONTINUATION.**

No GOAT media/reference content was opened.

## 4. SEARCH RESULT

The metadata-only search did **not** identify a corpus that simultaneously clears:

- real guitar performance;
- deterministic note-birth reference;
- stable prospective identity;
- usable evaluation access/rights;
- strict untouched-lineage status;
- current branch scope.

Therefore no new real-evaluation PRE is scientifically justified from the candidates reviewed here.

The correct fail-closed outcome is **no corpus selected**, not a relaxed provenance definition, synthetic substitution, weaker reference semantics, or reuse of a closed/exposed corpus.

## 5. NEXT PERMITTED WORK

Without an explicit scope change, continue metadata-only discovery for a genuinely new external guitar corpus. For any promising new candidate:

1. freeze the pre-selection branch base before writing candidate-specific evaluation material;
2. run a full-history provenance audit against that base using exact corpus/source identifiers;
3. if clean, verify rights/access and note-reference semantics from metadata only;
4. only then write a new prospective real-evaluation PRE;
5. update the canonical current-state checkpoint;
6. stop for fresh post-freeze authorization before media/model/correctness execution.

Do not reopen GOAT, Guitar-TECHS, GuitarSet, IDMT, FLGD, EGFxSet, EGSet12, GAPS, EGDB, or archived V143/Gomyway without an explicit user instruction that changes the present scope.

## 6. SAFETY / AUTHORITY RECORD

- successor corpus media opened: `0`
- successor annotation payloads opened: `0`
- successor model runs: `0`
- successor correctness scores: `0`
- candidate logic changes: `0`
- threshold changes: `0`
- V143/Gomyway activity: `0`

Global authority remains unchanged.