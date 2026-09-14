# Songsterr Fresh V6 — Five guitar dataset metadata review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/rights/reference review only; no candidate media acquired or scored.

## Frozen authority

V6 method remains frozen by `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md` at commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`, implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`. External scoring remains frozen by `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md` at commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Guitar-TECHS official reference-blind audit run `34754519541`, job `103716527380`, remains completed/successful. Exact artifact `guitar-techs-v6-alignment-inventory`, artifact ID `10317695640`, remains unexpired as checked 2026-09-14; GitHub-reported archive digest remains `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`. Frozen audit decision remains `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; no Guitar-TECHS correctness is permitted.

## Candidate

**Five guitar dataset**, Eduard Vergés Franch, Zenodo DOI `10.5281/zenodo.4988354`, published 2021-06-18.

Primary public record reviewed:
- Zenodo record `4988354` describes 30 guitar performances of six songs, using five guitars, recorded simultaneously through three setups: DI, mobile microphone and computer microphone; 90 WAV recordings total.
- The authoritative Zenodo file listing exposes WAV recordings and per-file MD5s. The public description/file listing does not expose a MIDI package, performed-note event stream, fret/string sensor stream, or other independent note-level onset+pitch truth.
- Example Freesound publications from the same dataset are explicitly marked Creative Commons 0, demonstrating permissive rights for at least those individual audio items. This does not cure the missing independent reference stream.

## Frozen pre-media gate assessment

1. **Performance-audio rights:** potentially favorable for individual Freesound copies because example items are CC0; corpus-wide Zenodo rights would still need exact authoritative confirmation if the candidate passed the reference gate.
2. **Real guitar:** PASS. The dataset is explicitly real guitar captured through DI/microphones.
3. **Independent performed note-level onset + pitch truth:** **FAIL.** No authoritative released note-event reference stream is identified. The public deposit is an audio dataset; tempo/song identity is not a performed note-level onset+pitch reference.
4. **Plausible >=1,000 V6-positive capacity:** not reached. The reference gate already fails; additionally only 30 underlying performances exist, with three simultaneous recording views that cannot be counted as independent performances.
5. **Untouched status:** not investigated further because a hard pre-media gate already fails.

## Decision

**REJECT BEFORE MEDIA ACCESS — NO INDEPENDENT PERFORMED NOTE-LEVEL REFERENCE.**

Do not download/audit/score this dataset for V6. Do not treat its three simultaneous recording setups as independent evidence. A later authoritative release containing an independent simultaneously captured performed note-level onset+pitch reference would constitute genuinely new evidence and may justify reopening metadata review; absent that, this candidate is closed.

No Basic Pitch, V6 correctness, Modal, Vercel heavy-GPU or L4 GPU work was performed. `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`, duration remains unchanged/paused, Policy C remains `UNENROLLED`, and protected-song execution remains embargoed.

## Sources reviewed

- Zenodo, Five guitar dataset, record `4988354`, DOI `10.5281/zenodo.4988354`.
- Freesound, EduardVerges Five Guitar dataset examples (e.g. Runaway Train / Where Did You Sleep Last Night), showing CC0 licensing for the surfaced audio items.
