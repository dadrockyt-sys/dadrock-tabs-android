# Songsterr Fresh — Successor Corpus Metadata Search Continued 4

Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/provenance research only

Status: **NO ELIGIBLE UNTOUCHED REAL-GUITAR NOTE-BIRTH CORPUS SELECTED**

## Purpose

Continue the metadata/provenance-only search after the first four successor-corpus checkpoints. No candidate media, annotation payload, model output, or correctness result was opened. No Basic Pitch or Songsterr-fresh qualifier was run.

## New candidates / checks

### 1. GIHME / Guitar Improvisations with Hexaphonic Multieffect

Public metadata continues to support that GIHME contains approximately ten hours of real hexaphonic-guitar improvisations with annotations including notes, playing techniques, tuning, and effects. Repository-history searches for `Gihme` and the full corpus name returned no prior Songsterr-fresh commit hits.

However, the authoritative public records surfaced in this continuation expose the conference paper and descriptive metadata rather than a stable downloadable corpus package with immutable audio/annotation file identities and a directly inspectable annotation schema. The public Zenodo record `6798338` is a conference-paper record, not a corpus release.

Disposition: **STRONGEST OPEN LEAD, BUT STILL NOT PRE-READY.** Do not infer deterministic note-birth onset/MIDI semantics or corpus file identity merely from the word `notes` in the paper abstract.

### 2. GM Dataset — Chieppa / Brutti / Paiva (2025)

The 2025 IEEE Access paper `Automatic Guitar Transcription With Deep Neural Networks` identifies a small `GM Dataset` recorded specifically to test generalization beyond GuitarSet. Publicly surfaced article text states that the dataset contains real guitar recordings across rock, jazz/blues, pop, reggae, and classical material and that labels are represented as per-string MIDI/tab information after manual preparation/alignment.

Repository-history search for `Chieppa` returned no prior Songsterr-fresh commit hit. This is consistent with Search 4's initial clean result.

No authoritative public dataset repository, immutable release/version identifier, file manifest, or dataset license was found in this continuation.

Disposition: **INITIAL-LINEAGE-CLEAN BUT NOT PRE-READY.** The absence of a stable public release prevents prospective corpus identity freezing and independent reproducibility.

### 3. Five guitar dataset — Zenodo `4988354`

Public Zenodo metadata describes 30 real performances of six guitar songs, captured simultaneously via DI, mobile microphone, and computer microphone, producing 90 recordings.

The public record establishes audio recordings but does not establish synchronized note-onset + MIDI-pitch ground truth tied to the performances.

Disposition: **REJECT FOR THIS BOUNDARY — real guitar audio but no verified deterministic note-birth reference.**

### 4. HF1

MIR dataset indexes list HF1 as containing onset, offset, and pitch annotations. Verification shows HF1 is a **Hardanger fiddle** corpus whose notes were human-annotated by the fiddle players.

Disposition: **REJECT — not guitar.**

### 5. Recent 2025–2026 search pass

Searches targeting `new guitar transcription dataset`, `real guitar + MIDI`, `hexaphonic guitar + MIDI annotations`, `Fishman TriplePlay`, and recent Zenodo/academic releases predominantly returned already-known families: GuitarSet, Guitar-TECHS, GAPS, GOAT, EGDB/EGDB-PG/EGDB-NDSP, FLGD, MMIP, and the GM Dataset.

Under the current hard scope and untouched-lineage criterion, those already-known/exposed/closed families do not become eligible through a newer mirror, packaging update, or amplifier-rendered derivative.

## Current conclusion

No new corpus found in this continuation simultaneously satisfies:

1. real guitar performance audio;
2. deterministic onset + integer-MIDI-pitch truth for the exact performance;
3. reference independence from Basic Pitch or another AMT system;
4. stable public source/version/file identities;
5. usable research rights/access;
6. strict untouched Songsterr-fresh lineage status; and
7. current branch scope.

Therefore **no successor PRE is justified yet**.

GIHME remains the strongest unresolved lead because its public metadata describes real hexaphonic-guitar performances with note annotations and current lineage searches are clean. The unresolved blockers are corpus availability, immutable release identity, annotation schema, and note-birth timing/pitch semantics.

GM remains a secondary unresolved lead but lacks a stable authoritative public release and rights/version identity.

## Next search boundary

Continue metadata/provenance-only discovery, with priority on:

- institutional repositories associated with GIHME / UMONS / PRISM that may expose the corpus separately from the paper;
- supplementary repositories attached to 2025–2026 guitar-transcription papers;
- HCI/performance-capture datasets using hardware MIDI guitar controllers or per-string pickups where MIDI is captured contemporaneously rather than inferred from audio;
- lesser-known research-data repositories with immutable DOI/version/file manifests.

For any candidate that appears viable, perform repository-history provenance search **before** opening corpus media or annotation payloads. Only after clean provenance plus stable source/version/reference semantics are established may a new PRE be written.

## Safety / authority record

- successor corpus media opened: `0`
- successor annotation payloads opened: `0`
- successor model runs: `0`
- successor correctness scores: `0`
- candidate logic changes: `0`
- threshold changes: `0`
- V143/Gomyway activity: `0`

No successor execution is authorized.