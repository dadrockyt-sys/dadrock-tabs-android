# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; produce a genuinely professional guitar-tab PDF, not merely a polished-looking PDF.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. Do not tune runtime/shadows from it.
- Retired render identities never rerun/rescore: `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`, `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 without fresh explicit user authorization. None is currently authorized.**
- Timing frozen unless new source-only evidence proves otherwise; tempo exactly `129.19921875`.

## Closed historical score state
- Retired score 1: 725 attacks -> 985 notes; PDF fidelity 1.0; pitch F1 `0.23718280683583634`; pitch+timing F1 `0.033143448990160536`; critical mismatches `1723`.
- Retired score 2: 889 events; PDF fidelity 1.0; pitch F1 `0.24305177111716622`; pitch+timing F1 `0.03051771117166212`; critical mismatches `1635`.
- Reference now closed; no further tuning from those scores.

## Permanently reusable paid capture
- Successful workflow `32805316807`, pinned commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`; one Modal command consumed, automatic retry disabled.
- Counts: eligible attacks `984`; retained `725`; pruned `259`; replay hypotheses `10585`; selected pitches `970`; rendered `967`; voicing drops `3`; measures `1-113`.
- Candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`; replay validation `182247f2beda257a49cfb454b1e7fc920594ffe5ecce39f7b9517ed15b21b95a`; compare `c77f923db45099f79df563e2c2d2487e46dceaef6f9469db8bd790f78f8cfcda`; lock `49898a441aed8519d96a71bc46c3e85d5d6c64c4be6da5398e9749ab1d6287be`; events `20fef66fdfd48b4e26ae3ec34fe215a4538375e6e6541a4c3f94b97e6fd8d547`; replay evidence `2c42c590bd9ddb47e304b385b67319cd15873b2dd75953d17e90b9b16bb140a2`.
- Permanent manifest `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json`, commit `87b4b698010fa11c62e76e061a2bbe91825de5ba`.
- CPU materializer `analyzer/materialize_v143_precision_fixture.py`, commit `72f43d8c82629b9ff388fa0013fe6e06b024a660`.

## Attack precision
- Precision-v2 pitch policy: non-harmonic secondaries use 2-of-3 score/attack/body at existing `0.80`; harmonic upper secondaries `{12,19,24,28,31,36}` stay 3-of-3 at `0.92`.
- Attack shadow V2 remains strongest supported attack correction: adds `148`, removes `0` -> `873` shadow attacks; remaining pruned `111` = `105` physically positive sub-0.60 nonlocal + `6` nonpositive.
- Do not broaden remaining 105 without independent source-only evidence because low transient/body ratio can be sustain bleed.
- Attack V2 is not freeze-ready: replay schema lacks full downstream CQT/stem evidence for technique/sustain on newly rescued attacks.

## PDF renderer
- `lib/createV143RhythmPdf.js` already renders structured six-line tab with measures, beat grid, sections, chord stacks, techniques and sustain; render contract verifies string/fret/MIDI and measure coverage.
- Historical PDF fidelity is already `1.0`. **Musical content correctness, especially fundamental/pitch and source-accurate string/fret assignment, is the blocker.**

## Fundamental / harmonic-primary shadows
### V1 — local source confirmation
- Module commit `ece9b156b4e9d9cd14294ba767a71b025a12dd21`; validator `9d8344c339aeb19f50eb1b16c323643578d00e78`; validation `5bdaccd327beaa55366d26e27276d94c1d4bf27a`.
- Same-measure ±2-step lower-primary confirmation using existing harmonic family + existing `FUNDAMENTAL_MIN_RAW_RATIO=0.55`.
- `12/725` primaries corrected; no invented/invalid/unplayable primary.

### V2 — broader two-view support, now superseded
- Module `analyzer/v143_contextual_harmonic_primary_shadow_v2.py`, commit `36c5f595d9664b5f0844ccc19ef0b237a758300e`; validator `ce2bbb1f5d9eb1a10b218ffebc3fb290ed833e4b`; validation `5f0d0fe4ab12b2e36f7c2da8c91b839018596be0`.
- V2 corrected `62/725`, but deeper CPU review found `19` V2-only corrections where the lower candidate's sole harmonic-family evidence was the current upper primary itself — a simple dyad can satisfy that and is not an independent overtone proof.
- **Do not promote V2. It is superseded by V3.**

### V3 — extra-harmonic guarded two-view support — CURRENT STRONGEST PRIMARY SHADOW
- Module `analyzer/v143_contextual_harmonic_primary_shadow_v3.py`, commit `f8de0947507689388cc3f6b8b01c16145b8b5afc`.
- Independent replay validator `analyzer/v143_contextual_harmonic_primary_shadow_v3_replay_validator.py`, commit `0c5e610dd37cec142a67e4e3110ad9fd3cdc2bba`.
- Durable validation `debug/v143-contextual-prune/contextual-harmonic-primary-shadow-v3-validation.json`, commit `969ba449be844990f06ebfe275a6d5b4d64a1bda`.
- Full local validation SHA256 `d5063ae3eb13c61922b3e3d429df6630326ff1346d69eb2036299d06ca870de8`.
- V3 preserves V1. For the two-view fallback a lower observed harmonic-family candidate must:
  1. use an existing harmonic interval from `{12,19,24,28,31,36}`;
  2. pass the existing `0.55` physical-strength guard independently in view A and view B;
  3. have at least one **additional positive harmonic-family member beyond the current upper primary in each independent view**; and
  4. have strictly richer harmonic support than the current primary in both views.
- This rejects simple lower/current dyads as insufficient evidence without adding a new numeric confidence threshold.
- Exact CPU replay: `43/725` primaries corrected; reason split `31` two-view-extra-harmonic + `7` local+two-view + `5` local-only.
- Harmonic intervals: octave `37`, 19-semitone `3`, two-octave `3`.
- Main transitions: `64->52` x17, `52->40` x6, `64->40` x3, `71->59` x3, `67->55` x3, `69->57` x3, `62->50` x2.
- MIDI64 primaries `202 -> 183`.
- Selected pitches `970 -> 969`; deterministic rendered pitches `967 -> 966`; voicing drops remain `3`.
- Attack identity unchanged; invented pitches `0`; invalid primaries `0`; unplayable primaries `0`; validation green.
- Structural diagnostic only (not selection): all `43/43` corrected new primaries already recur elsewhere in the retained source-derived transcription, and `33/43` recur at the same 16th-step position in another measure.
- V3 rejects `19` V2-only simple-dyad corrections.
- **V3 is the strongest supported primary/fundamental shadow. It is not producer-integrated/frozen/professionally scored.**

## String/fret assignment limit
- Current deterministic resolver is stateless and tends toward lowest-fret legal positions.
- Sequence continuity can make fingering smoother but MIDI alone cannot establish the performer's actual string/fret choice. Do not integrate sequence voicing as an accuracy fix without independent string/hand-position evidence.

## Specialized guitar-AMT branch
- MIT 2026 `ErenReyhanlioglu/Guitar-Transcription` directly predicts tablature/string-fret, hand position, string activity, pitch class and multipitch from HCQT+Mel; reported GuitarSet tablature F1 ~`0.783`, TDR ~`0.946`.
- Research-only probe harness `analyzer/v143_specialized_guitar_amt_probe.py`, commit `97c76dd32e236663850f3ad7996b86f9a527ea2c`; feature-contract self-test commit `27d71618538bd5b7d0e860b2f0513f916f0315a0`.
- Public checkpoint binary (~26.8 MB) remains inaccessible through the available text-only GitHub connector; no model checkpoint inference yet.

## Audio availability
- Persistent Library contains only one audio file: `DS Music - Are You Gonna Go My Way (Remastered 2025) - Lenny Kravitz.m4a`, SHA256 `c187bead44529d38544b8452f57328aaf17ce606f08217b78e3157c648392481`.
- It does **not** match approved fixture SHA `215bd5a6...`; exact approved audio is not currently present in the Library.
- Nonmatching M4A may be used only for explicitly isolated domain research, never freeze/score/candidate claims.

## Current mutation/cost state
- No Modal/L4 after successful run `32805316807`.
- No professional scorer/reference reopened.
- No `main` or Production changes.
- Protected runtime last reverified exact blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- No freeze-ready candidate yet.

## Next exact actions
1. Reverify protected runtime blob after this checkpoint.
2. Stay CPU-only/no Modal.
3. Deep-check V3 against repeated-structure and chord/dyad ambiguity using saved evidence only; do not tune from retired scores.
4. Investigate whether selected secondary-pitch inflation can be reduced using similarly independent two-view physical structure without hurting true chords.
5. Keep Attack V2 unchanged unless a genuinely independent onset discriminator appears.
6. Continue zero-cost checkpoint-access research for the specialized guitar-AMT branch; do not weaken fixture boundaries.
7. Do not integrate sequence voicing without independent string/hand-position evidence.
8. Improve printed rhythm stems/beams only after musical event content is materially stronger.
9. Do not freeze/professional-score while required downstream evidence is absent.
10. No Modal/L4 without fresh explicit authorization.
11. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.
