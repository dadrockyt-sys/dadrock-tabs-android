# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 005 is frozen current best: Guitar `gss-active-only` **42.7940586109996% F1**, Bass **80.45325779036827% F1**. The corrected post-I005 aggregate/reference-blind diagnosis is terminal/frozen and supports a small active-topology pruning family. The topology generator and grader are now staged in code but no topology candidate/manifest exists yet and no topology score call has occurred. The next boundary is reference-blind generation/freeze only. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Active-topology family — IMPLEMENTATION STAGED / CANDIDATES NOT GENERATED
- Generator `validation/v167_single_song_calibration/build_active_topology_guitar_variants_v167.py`: commit `7e37530f7b280978c6da4d78b7b7cfc398f914d1`, blob `b7ac8a77e74df27a0b2af5bceb25bb97c81d4c7d`.
- Grader `validation/v167_single_song_calibration/score_active_topology_guitar_variants_v167.py`: commit `4f34bfb2e03d7cb6d0ff84c5b89789ded15fc536`, blob `4458d45cfa2ea018cf40a3a24344e1b7dd9d104a`.
- Generator has no scorer/professional-reference input. It keeps all 1050 original I003 Guitar coordinates and filters only the exact 48 frozen I005 `gss-active-only` additions by their already-frozen topology evidence. Bass is copied normalized-exact from I005.
- Preregistered topology categories from the frozen diagnosis: `single`=23, `chord`=18, `near_unison`=5, `remote`=2.
- Preregistered variants:
  - `topo-repro-i005`: keep all 48; no-score reproduction control; expected Guitar 1098.
  - `topo-single-or-chord`: keep 41 = single+chord; expected Guitar 1091.
  - `topo-single-only`: keep 23; expected Guitar 1073.
  - `topo-chord-only`: keep 18; expected Guitar 1068.
- No onset/activity/rank/ratio dimensions are allowed in this family.
- Grader policy is staged to verify the complete committed manifest/candidate hashes before importing scorer or opening reference; reproduction control is normalized-verified without scoring; Bass normalized equality is verified without scoring; exactly the three new Guitar rules are scored.
- Planned score calls: Guitar **3**, Bass **0**, reproduction control **0**.
- Selection is frozen in advance: max Guitar F1, then precision, fewer kept I005 additions, lexicographic id.
- Separate I006 promotion eligibility is frozen in advance: winning new rule must gain at least **+0.10pp F1 vs I005** and have **precision >= I005**. The scorer workflow may never create I006 automatically.

## Post-I005 aggregate diagnosis — FROZEN / TERMINAL
- Corrected analyzer blob `82ec287869102ab6af949afa174a2543768dbc55`; rearm run `33265328718`, job `99134275015`; terminal `dbfa511f90b2f8ccd58411211fdde540fa5ca0c9`.
- Analysis `debug/v167-single-song-calibration/post-i005-active-only-aggregate-analysis.json`: blob `043eaa2367f1efbb6309e13d2fcd52952b809e81`, SHA256 `fe7e826724a11e115a25f932d4b58ed88e3aedae67fb54142cc532cc40ab8450`.
- Receipt blob `eb7e888bf1bb772a90496126df434a621728972e`, status `POST_I005_ACTIVE_ONLY_AGGREGATE_ANALYSIS_FROZEN`.
- Policy: professional reference=false; scorer=false; new score calls=0; per-event reference matches=false; new rule selected=false; GPU/CUDA/Modal=false; main/Production=false.

### Frozen structural findings
- Exact I005 additions: **48 / 48 unique selected sites**.
- Ratio candidate/max-active = **1.0 for all 48**; max-active tie count=1 for all 48; pre-grid active-max candidate count=1 for all 48. Ratio/tie/competition are dead dimensions.
- Active MIDI multiplicity: 1 pitch=23; 2=15; 3=5; 4=5.
- Topology: no different active=23; chord interval=18; near-unison 1–2 semitones=5; remote-above-octave=2.
- Onset support mean 0.909745, median 1.0; >=0.65 retains 42/48. Historical paired whole-rule evidence rejects simple onset tightening: for `allow_active + exclude_harmonic_octave`, onset 0.65 vs 0.50 had 0 improvements / 2 losses / 1 tie, mean -0.144912pp F1; closest q100 rule lost -0.217717pp F1.
- Activity support mean 0.772771; template rank mean 0.997024 and p25+ =1.0. These are not included in the new family.

## Iteration 005 — FROZEN CURRENT BEST
### Guitar
- Candidate blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- F1 **42.7940586109996%**; precision **48.54280510018215%**; recall **38.26274228284279%**.
- 533 matched / 1098 generated / 1393 reference; FP565/FN860.
- I005 = all 1050 original rich I003 Guitar dictionaries + exactly 48 frozen state-split additions.

### Bass — closed
- F1 **80.45325779036827%**; precision **83.203125%**; recall **77.87934186471663%**.
- 426 matched / 512 generated / 547 reference; FP86/FN121.
- Bass must remain exactly I005/I004/I003.

## Immutable identities
- I003 blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Post-I005 diagnosis blob `043eaa2367f1efbb6309e13d2fcd52952b809e81`, SHA256 `fe7e826724a11e115a25f932d4b58ed88e3aedae67fb54142cc532cc40ab8450`.
- Frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.

## Standing V167 methodology
- Calibration only; never present scores as holdout/generalization performance.
- Complete deterministic whole variants must be committed/frozen with hashes before any new reference/scorer read.
- No per-event reference choices, direct reference-event copying, or post-score mutation/retuning.
- I003/I004/I005 and terminal reports are immutable. Bass is closed.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — reference-blind topology candidate freeze
1. Create one self-removing CPU-only generation workflow from this exact checkpoint parent.
2. Verify I003, I005, frozen diagnosis, generator blob `b7ac8a77e74df27a0b2af5bceb25bb97c81d4c7d`, grader blob `4458d45cfa2ea018cf40a3a24344e1b7dd9d104a`, and checkpoint identity.
3. Assert generator has no scorer/reference CLI/path; compile generator/grader.
4. Run generator only. Require topology source counts 23/18/5/2 and variant kept-addition counts 48/41/23/18; reproduction normalized exactly I005; Bass exact I005.
5. Freeze candidate directory, manifest, and generation receipt in a terminal self-removing commit. **Do not read/import scorer or professional reference in this workflow.**
6. Checkpoint frozen candidate/manifest hashes. Only after that may a separate scoring workflow be armed.
7. CPU only; no GPU/CUDA/Modal; never modify main/Production.
