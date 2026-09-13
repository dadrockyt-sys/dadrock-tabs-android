# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-13 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, duration research and protected-song execution remain closed unless explicitly reopened by the user.
- Never silently alter/drop event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` stays deterministic/model-free/process-free/network-free; model/DSP research stays under `scripts/songsterr-fresh/`.
- Authority remains fail-closed: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, Policy C `UNENROLLED`, protected song embargoed.

## USER COMPUTE AUTHORIZATION RULE

Ordinary research/coding/GitHub/CPU/test/checkpoint work may proceed at assistant discretion. Explicit user authorization is required before any Modal, Vercel heavy-GPU, or L4 GPU run.

## CLOSED / REVEALED LINES

V1/V2 rejected diagnostics. GuitarSet/V3 and IDMT/V4 closed/revealed. V5/FLGD closed/rejected and may not be rerun or tuned. Archived V143/Gomyway and GOAT/reference scoring remain closed.

## V6 — METHOD + SCORING FRAMEWORK FROZEN / NO REAL CORRECTNESS YET

Final V6 method preregistration:
`docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`
commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.

Frozen implementation:
`scripts/songsterr-fresh/onset_birth_corroboration_v6.py`
commit `3a6cbb144fec5613ab6350deb6539297d713df28`
blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.

External scoring framework preregistration:
`docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`
commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Do not change V6 constants, Basic Pitch settings, DI-only canonical audio path, event-preservation rule, matcher, 50 ms/50-cent tolerances, Wilson statistic, admission gates, strata rules, or deferred-reveal/single-run rule from holdout observations.

## GUITAR-TECHS V6 AUDIT — COMPLETE / REJECTED BEFORE CORRECTNESS

Official audit run `34754519541`, job `103716527380`: **SUCCESS**.
All nine exact package audits, merged-result generation, fail-closed verification and artifact upload completed successfully.

Immutable result checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`
commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.

Artifact:
- ID `10317695640`
- archive digest / downloaded ZIP SHA-256 `d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`
- merged JSON SHA-256 `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`

Audit facts:
- 9 verified packages
- 104 paired DI/MIDI performances
- 18,934 paired reference events
- 0 unpaired DI / 0 unpaired MIDI
- all 104 alignment statuses `OK`
- pairing identity manifest `24ff1b4eef07f28eb678f38fbec80f8cc26668329812868a89992e20eb73efa7`
- alignment lag manifest `95b244d78014e20ea0f468ecf88aacf90e8442f4aef675b246845202d98fcc84`
- proposed-population manifest `bd239d63ba39a370f7c9e09df544b3b207596acf523b09e2be57bbc49cf0b765`
- lag range -8..+10 hops, median -5 hops; all-within-one-hop false
- MIDI anomalies: 5 same-key overlaps, 7 unmatched note-ons, 0 unmatched note-offs

The preregistered structural gate requires zero MIDI anomalies. Official decision:

`C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`

`datasetStructurallySuitable:false`.

Basic Pitch was not invoked, V6 was not invoked, correctness was not computed. Guitar-TECHS is closed as the V6 external holdout: do not score, repair/drop events to rescue, or create an A/B binding.

## CURRENT ACTIVE WORK — REPLACEMENT UNTOUCHED HOLDOUT SEARCH

Metadata/license/structure research checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_V6_REPLACEMENT_HOLDOUT_METADATA_SEARCH.md`
latest substantive update commit `64d9516d0efbba380769bd6cc52f93572393180a`.

No V6 correctness has been run on any replacement candidate.

### GAPS — REJECTED ON EXPLICIT RIGHTS TERMS

GAPS is scientifically attractive (~14 h, 300 performances, >200 performers, high-resolution note-level MIDI), and the current Hugging Face repository advertises MIT metadata. However the official GAPS companion site explicitly states that the dataset contains copyright material, is limited to non-commercial research, is permission-bound to the signing researcher/organisation, and may not be sold/leased/published/distributed to third parties without written permission.

The older Zenodo release also provided YouTube URLs rather than audio, reinforcing that underlying recording rights are distinct from repository metadata.

Disposition: **do not use/download/audit GAPS for this V6 admission path unless explicit written permission is later obtained from the GAPS administrator.**

### EGSet12 — REJECTED AS NOT UNTOUCHED

EGSet12 was a strong open-license lead on public metadata: Zenodo record `11406378` contains original real solo electric-guitar WAV/JAMS/GP performances and public metadata reports CC BY 4.0/open access.

A controlled branch-history contamination audit has now terminally resolved the untouched gate:

Immutable result checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_EGSET12_CONTAMINATION_AUDIT_RESULT.md`
commit `a4fc980a51a151332625acd7e8a69154589d6a2a`.

Controlled audit:
- workflow `.github/workflows/songsterr-fresh-egset12-contamination-audit.yml`
- workflow commit `f4d347a04b14340ac441ff35375413e4d479a38a`
- run `34760898067`, job `103733427004`
- GitHub-hosted Ubuntu CPU only; no corpus download/model/correctness
- branch head audited `f4d347a04b14340ac441ff35375413e4d479a38a`
- reachable commit count `7662`
- identifiers: `EGSet12`, `egset12`, `11406378`, `robust-guitar-tabs`
- match lines `42`
- unique matching pre-search commits `21`
- audit text SHA-256 `21e8da1cc4385b702df4ee9c141c5b952d83acc39bc6bedbf8a391ecf46fc294`
- artifact ID `10318981287`
- artifact ZIP SHA-256 `858da60e05998cacbee0a78cb566533403859c9fa632789240b190f50bf31301`

Representative earlier matching branch commits include electric-guitar TabCNN research/evidence, exact-source electric-consensus checkpoints, V168 external candidate screening, and parallel open-corpus research. Therefore EGSet12 fails the conservative untouched-holdout requirement.

Disposition: **do not download/score EGSet12 for V6 admission, do not rewrite history to attempt to restore untouched status, and do not create a V6 binding for it.**

### Backup: EGFxSet

Real electric-guitar hardware recordings, stable Zenodo release, CC BY 4.0/open-access description, 8,970 five-second files. However only 690 unique clean performances exist, most material is derived effects variants, and public metadata does not establish high-resolution note-onset timing. It remains a narrow structural backup rather than an audit-ready holdout.

### Metadata lead: GIHME — DATASET STILL UNRESOLVED

Public metadata describes ~10 hours of richly annotated real hexaphonic-guitar improvisations with note/technique/tuning/effect annotations. The surfaced Zenodo record `6798338` is definitively the conference paper only (`79.pdf`, ~680.6 kB), not the underlying dataset. Dataset package location, license, exact annotation timing representation and immutable audio/reference identities remain unresolved.

Explicit exclusions: GuitarSet (V3 revealed), IDMT (V4 revealed), Guitar-TECHS (outcome C), GAPS (rights gate), EGSet12 (branch-history contamination), Slakh/SynthTab (synthetic), GuitarJam (no surfaced note-level truth).

## NEXT ALLOWED ACTION

1. Continue metadata/license/structure search for a **different untouched, permissively licensed real-guitar corpus** with performed note-level timing and enough independent event volume to plausibly satisfy the frozen >=1,000 V6-positive gate.
2. Resolve GIHME dataset location/license/annotation representation; do not treat the paper record as the dataset.
3. Keep EGFxSet as a narrow backup and determine whether a fixed/preregisterable note onset exists.
4. For any newly surfaced candidate, perform branch-specific contamination/history review before selection; default-branch search is insufficient.
5. Select one replacement only after rights/provenance/untouched status are defensible and evidence volume is plausibly sufficient without duplication/rescue rules.
6. Freeze a corpus-specific reference-blind inventory/alignment preregistration before downloading/auditing real audio/reference pairs.
7. Run only structural/alignment audit first. If unsuitable, reject without correctness. If suitable, bind immutable identities into the already-frozen V6 scoring framework, build controlled no-real-correctness harness CI, then launch exactly one ordinary-GitHub-CPU official correctness run after prerequisites are green.
8. Ask the user only if Modal, Vercel heavy-GPU or L4 execution becomes necessary.

## STILL FORBIDDEN

- any Guitar-TECHS V6 correctness
- post-hoc repair/exclusion of Guitar-TECHS anomalies to rescue the holdout
- any GAPS audit/correctness under the current explicit non-commercial/copyright-material terms absent written permission
- EGSet12 V6 admission scoring/binding or history rewriting to restore untouched status
- V5 FLGD rerun/post-result tuning
- using FLGD/IDMT/GuitarSet/protected-song correctness to tune V6
- changing frozen V6/scoring rules from any holdout observation
- protected-song execution
- duration research
- archived V143/Gomyway / GOAT/reference scoring
- real-corpus optimizer/threshold sweeps
- training/fine-tuning on a proposed admission holdout
- Production/customer promotion without untouched external validation + separate policy approval
- Modal, Vercel heavy-GPU or L4 execution without explicit user authorization

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1` and read this file first. Guitar-TECHS is closed with outcome C and no V6 correctness. GAPS is rejected on explicit non-commercial/copyright-material rights terms. EGSet12 is now also rejected: controlled run `34760898067` found 21 distinct pre-search matching commits in this branch's reachable history, so it is not untouched. V6 method/scoring framework remain frozen and no replacement-holdout V6 correctness has been exposed. Current work is again metadata/license/structure search for another genuinely untouched, permissively licensed real-guitar corpus. Do not audit real candidate audio/reference pairs until rights, untouched status and a corpus-specific reference-blind preregistration are frozen.
