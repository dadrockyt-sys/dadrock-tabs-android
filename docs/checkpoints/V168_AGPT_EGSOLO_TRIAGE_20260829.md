# V168 — AG-PT-set + EG-Solo candidate triage

Date: 2026-08-29 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **SCREENING ONLY / NO ASSETS ADMITTED / SCORING NOT ARMED**

## Safety boundary
This checkpoint freezes metadata/provenance triage only. No candidate generation was implemented. No scorer/reference-facing evaluation was run. No source-audio or professional-reference note-event bytes were opened for selection or scoring. V168 reference-facing score calls remain **0**. CPU-only boundary remains unchanged. `main`/Production remain untouched.

---

## AG-PT-set — EXCLUDED AS V168 SONG HOLDOUT

### Authoritative identity
Zenodo record: `https://zenodo.org/records/10159492`  
DOI: `10.5281/zenodo.10159492`  
Version: `v1`  
Archive: `aGPTset_z.zip`, 6.7 GB  
Published MD5: `1dff8103f9ad6e1a86cee2e5e39cbe87`

### Dataset facts
The authoritative Zenodo record describes:
- 15 h 55 m of **monophonic** recordings;
- 12 expressive acoustic-guitar playing techniques;
- 10 h 04 m labeled for 8 techniques;
- 32,592 labeled **individual notes**;
- performances by 6 players on 7 acoustic steel-string guitars;
- millisecond-level onset timestamps plus technique labels.

The associated 2024 AG-PT paper further describes the material as individual monophonic guitar sounds and states that the onset reference was annotated by musicians.

### V168 gate assessment
AG-PT has useful human/musician annotation provenance and real guitar audio, but its evaluation unit is isolated/monophonic technique-note material rather than independent songs or song-like complete Guitar streams. It therefore cannot satisfy the current V168 purpose of a >=2-song cross-song holdout comparison without redefining the frozen evaluation target.

### Decision
**EXCLUDED / NOT ADMITTED.**

Do not reinterpret isolated-note technique recordings as songs merely to satisfy the holdout count. No V168 asset was admitted and score calls remain **0**.

---

## EG-Solo — BLOCKED ON SOURCE-AUDIO USE BASIS

### Authoritative/public project facts
Official project/demo page: `https://bryanyu1997.github.io/EG-Solo_demo/`  
Public GitHub repository: `bryanyu1997/EG-Solo_demo`.

The project page states:
- 76 clips;
- about 40 minutes total;
- clips come from **professional electric-guitar solo demonstration videos available on YouTube**;
- the content is popular rock-song solo material with backing tracks;
- 6,833 annotated notes plus nine technique classes;
- note/technique annotations are stored as MIDI tracks;
- annotation labels are distributed separately via Google Drive.

A later 2024 annotation-quality paper reports that EG-Solo authors manually annotated onsets with the aid of guitar tablatures. This is promising human-reference provenance.

### Public repository inspection
The public `bryanyu1997/EG-Solo_demo` tree was inspected through GitHub metadata only.
- No repository `LICENSE` file is present in the inspected recursive tree.
- The repo contains demo-rendered WAV files under `transcription_demo/ground-truth`, `our-predicted`, and `solola` plus the project page source.
- These rendered demo files are not a substitute for a frozen license/use basis for the original YouTube source performances.
- The full source-audio dataset itself is not presented as a clean, independently licensed downloadable asset in the public project materials inspected.

### Material blocker
The exact source performances are third-party professional YouTube demonstrations of popular rock songs. The inspected project materials do not establish a rights/use grant that would let this project freeze and use those exact source-audio bytes as an internal V168 evaluation asset under the existing intake contract.

Even if the MIDI annotations are human/manual and potentially strong, the frozen V168 manifest requires a defensible `rightsOrUseBasis` for the exact source audio and a frozen source/reference pair binding. A YouTube location or public availability is not by itself such a use grant.

### Decision
**BLOCKED / NOT ADMITTED.**

Do not download or pair YouTube source audio by assumption. Do not treat demo-rendered `ground-truth` WAVs as the professional symbolic reference. Reopen only if a legitimate exact-source use basis and stable source identity are obtained prospectively.

---

## Resulting V168 state
- AG-PT: **EXCLUDED** — wrong evaluation unit (monophonic individual-note/technique material, not song holdout).
- EG-Solo: **BLOCKED** — strong human annotation signal, but source-audio rights/use basis and exact licensed source identity are unresolved.
- GOAT remains the strongest acquisition lead, contingent on legitimate restricted research access and frozen access terms.
- No external asset admitted.
- Candidate generation remains unimplemented.
- Scoring remains unarmed.
- V168 reference-facing score calls remain **0**.

## Next boundary
1. Do not score.
2. Keep legitimate GOAT research access as the primary acquisition path.
3. Continue metadata-only screening only for candidates that plausibly provide >=2 real, independent guitar pieces with professional/human note-event references **and** a defensible exact-source use basis.
4. A promising provenance-only fallback is the older G&N electric-guitar solo dataset used by TENT: its published paper says an experienced electric-guitar player carefully annotated note events/techniques and another electric-guitar player checked every label. Before any consideration, determine whether the commercial textbook-CD audio and annotations have a lawful, stable research-use acquisition path. Do not acquire or use them by assumption.
5. Do not weaken the frozen `professional_scorer_ready`, no-model-derived-reference, source/reference-pair, or >=2-song requirements.
6. No reference conversion, candidate generation, or generic scorer adapter until a complete manifest passes both frozen validators.
