# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 005 is frozen current best: Guitar `gss-active-only` **42.7940586109996% F1**, Bass **80.45325779036827% F1**. The corrected post-I005 aggregate/reference-blind diagnosis is now terminal/frozen with zero new reference/scorer access. It rules out simple onset tightening and shows the remaining 48 I005 additions have no useful max-score ratio/tie competition dimension. The structurally defensible next hypothesis is a small **active-topology pruning family** based only on frozen active-pitch context: isolated-active vs chord-interval vs near-unison/remote context. No next family is implemented or scored yet. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Post-I005 aggregate diagnosis — FROZEN / TERMINAL
- First analyzer attempt blob `86a32010f441fb518146f3717ae8d9ab3b94b8ea`; run `33265180179`, job `99133883024`: immutable/reference-blind guard passed, analyzer failed safely before output because it confused pre-grid structural eligibility with the builder's post timing/dedupe/polyphony `eligible` count.
- Corrected analyzer `validation/v167_single_song_calibration/analyze_post_i005_active_only_v167_rearm.py`: blob `82ec287869102ab6af949afa174a2543768dbc55`.
- Corrected rearm commit `b0474ab800a187d382a67e61d3e18d17ee9a278e`; run `33265328718`, job `99134275015`; terminal self-removing commit `dbfa511f90b2f8ccd58411211fdde540fa5ca0c9`.
- Analysis `debug/v167-single-song-calibration/post-i005-active-only-aggregate-analysis.json`: blob `043eaa2367f1efbb6309e13d2fcd52952b809e81`, SHA256 `fe7e826724a11e115a25f932d4b58ed88e3aedae67fb54142cc532cc40ab8450`.
- Receipt `debug/v167-single-song-calibration/post-i005-active-only-aggregate-analysis-receipt.json`: blob `eb7e888bf1bb772a90496126df434a621728972e`, status `POST_I005_ACTIVE_ONLY_AGGREGATE_ANALYSIS_FROZEN`.
- Policy: professional reference read=false; scorer read=false; new reference-facing score calls=0; per-event reference match assignments read=false; new rule selected by analysis=false; GPU/CUDA/Modal=false; `main`/Production=false.

### Frozen structural findings for the exact 48 I005 additions
- Exactly **48 additions / 48 unique selected sites**.
- Candidate/max-active template-score ratio is **exactly 1.0 for all 48**.
- Max-active tie count is **1 at all 48 sites**; pre-grid active-max candidate count at each selected site is also **1**. Therefore ratio tightening, tie-breaking, or active-candidate competition are dead dimensions for this set.
- Active MIDI multiplicity: **1 active pitch: 23 sites; 2: 15; 3: 5; 4: 5**.
- Nearest-different-active topology: **no different active pitch: 23; chord interval: 18; near-unison 1–2 semitones: 5; other above octave: 2**.
- Exact nearest interval histogram: none 23; 1:1; 2:4; 3:7; 4:4; 5:2; 7:1; 9:2; 10:2; 15:1; 22:1.
- Onset support: min **0.547974**, p10 **0.631731**, p25 **0.858249**, median **1.0**, mean **0.909745**. Survival: >=0.55 47; >=0.60 43; >=0.65 42; >=0.70 41; >=0.75 40.
- Activity support: min **0.409515**, p10 **0.496324**, p25 **0.644686**, median **0.772817**, mean **0.772771**.
- Template rank: min/p10 **0.9795918**, p25/median/p75/p90/max **1.0**, mean **0.997024**. Rank is nearly saturated and is not an attractive new search dimension.

### Frozen aggregate evidence against onset tightening
- Across all 9 prior `allow_active` paired rules with otherwise identical config, onset 0.65 vs 0.50: **0 improved F1, 6 reduced F1, 3 tied**, mean F1 delta **-0.089190pp**.
- For `allow_active + exclude_harmonic_octave`: **0 improved, 2 reduced, 1 tied**, mean F1 delta **-0.144912pp**.
- Closest prior rule to I004 structure, `q100 allow noharm`: 0.50 F1 **42.617717478052675%** vs 0.65 F1 **42.4%**; tightening removed 6 events but lost 4 matches / 2 FP and F1 **-0.217717pp**.
- Therefore do **not** preregister a simple onset-floor increase as the next family.

### Frozen topology interpretation
- I005 already selects a unique max-active Basic-Pitch-active candidate at every retained site. The remaining meaningful reference-blind distinction is the topology of *other* active pitches.
- A small next family is defensible because 41/48 sites fall into musically interpretable isolated-active or chord-interval context, while 7/48 are near-unison (5) or remote-above-octave (2).
- This is a whole-rule structural hypothesis only. No event is labeled true/false by reference, and no per-event outcome may be used to choose which 7 to remove.

## Iteration 005 — FROZEN CURRENT BEST
### Guitar — `gss-active-only`
- Candidate blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- F1 **42.7940586109996%**; precision **48.54280510018215%**; recall **38.26274228284279%**.
- 533 matched / 1098 generated / 1393 reference; FP565/FN860.
- I005 = all 1050 original rich I003 Guitar dictionaries + exactly 48 frozen state-split additions.
- Normalized stream exactly equals already-scored state-split winner SHA256 `aa042135c542f2025522bb0d8ab9491c8457bf95025db5953b714d452afc0d5e`.

### Bass — closed / identical I003-I005
- F1 **80.45325779036827%**; precision **83.203125%**; recall **77.87934186471663%**.
- 426 matched / 512 generated / 547 reference; FP86/FN121.
- Bass must remain rich/normalized exactly I005/I004/I003 in all future Guitar-only variants.

## Immutable identities
- I003 blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- I004 blob `8dd85049a65f00541f7874ff99511b081a0b5ff2`, SHA256 `728785c631750cbfcad48cc3243c238d6e7de6f337cce87e125a651ca2793acc`.
- I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Evidence pool blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- Frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.

## Standing V167 methodology
- Calibration only; never present V167 scores as holdout/generalization performance.
- Complete deterministic whole variants must be frozen/hashes fixed before any new reference/scorer read.
- No per-event reference choices, direct reference-event copying, or post-score mutation/retuning.
- I003, I004, I005 and all terminal reports are immutable.
- Bass is closed.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — preregister small active-topology Guitar pruning family
1. Keep I005 immutable and Bass exactly I005 for every variant.
2. Build variants only by deterministic whole-rule filtering of the 48 frozen I005 additions using their already-frozen reference-blind active topology; all 1050 original I003 Guitar events remain untouched.
3. Proposed small family, frozen before scoring:
   - no-score reproduction control = exact I005;
   - `topo-single-or-chord`: keep additions with no different active pitch OR nearest different active interval in {3,4,5,7,8,9,10}; expected 41 additions;
   - `topo-single-only`: keep only no-different-active additions; expected 23;
   - `topo-chord-only`: keep only chord-interval additions; expected 18.
4. Do not add onset/activity/rank/ratio threshold dimensions to this family. Those would confound the topology hypothesis and are not supported by the frozen diagnosis.
5. Freeze manifest + all candidate hashes before any reference/scorer read. Reproduction control gets 0 score calls; Bass gets 0 score calls. Score exactly the 3 new Guitar whole rules.
6. Frozen selection: max Guitar F1, then precision, fewer additions, lexicographic id. Do not create I006 automatically. Require at least **+0.10pp F1 vs I005 and precision >= I005** before a separate no-rescore I006 promotion is even eligible.
7. Save preregistration/checkpoint before arming any reference-facing scorer workflow.
8. CPU only; no GPU/CUDA/Modal; never modify `main` or Production.
