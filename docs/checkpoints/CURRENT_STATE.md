# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; produce a genuinely professional guitar-tab PDF, not merely a polished-looking PDF.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. No runtime/shadow tuning or selection from it.
- Retired render identities never rerun/rescore: `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`, `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 without fresh explicit user authorization. None is currently authorized.**
- Timing frozen unless new source-only evidence proves otherwise; tempo exactly `129.19921875`.

## Preserved paid capture — CPU replay source of truth
- Successful authorized run `32805316807`; pinned capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`; one Modal command consumed, automatic retry disabled.
- Counts: eligible attacks `984`; retained `725`; pruned `259`; replay pitch hypotheses `10585`; selected pitches `970`; rendered `967`; voicing drops `3`; measures `1-113`.
- Candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`; replay validation `182247f2beda257a49cfb454b1e7fc920594ffe5ecce39f7b9517ed15b21b95a`; compare `c77f923db45099f79df563e2c2d2487e46dceaef6f9469db8bd790f78f8cfcda`; lock `49898a441aed8519d96a71bc46c3e85d5d6c64c4be6da5398e9749ab1d6287be`.
- Durable manifest `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json`; CPU materializer `analyzer/materialize_v143_precision_fixture.py`.

## Attack state
- Legacy precision: ratio >=0.70 retain; 0.60-0.70 required composite local max; <0.60 prune; positive requires attack>0 and body>-0.25.
- Attack shadow V2 remains strongest fully source-replayable V143-only attack correction: adds `148`, removes `0`, -> `873`; remaining `111` = `105` positive subfloor nonlocal + `6` nonpositive.
- V2 files: `analyzer/v143_contextual_prune_attack_shadow_v2.py` commit `1f4477291b138ec04d843369bdc35f3dcb590167`; validator `ab4642a463227385a28136767688b68ab7b42d0f`; validation `43beb3cbba6d576171614cd47ad03aac78a8baaf`.
- Newly rescued attacks still lack the original producer's full downstream two-stem bend/legato/sustain evidence, so attack shadows are not freeze-ready.

## Exact approved audio is now locally recoverable without Modal
- Repository contains exact approved audio at `public/gomywayfullaitest.m4a`.
- Research-only CPU workflow `.github/workflows/v143-research-approved-audio-fetch.yml` verifies SHA before upload.
- Run `32815950324` succeeded; artifact `9551396214`; local research copy was verified byte-exact SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- This removes the previous blocker that specialized source models could only be tested on a non-approved re-encoding.

## Specialized guitar evidence
### Acoustic GuitarSet HCQT+Mel model
- MIT project `ErenReyhanlioglu/Guitar-Transcription`; fold1 checkpoint SHA256 `2572b3fe58429668ec9aeaee56bf40af265726a6c3652151b176b21da2bde953`, Git blob `82094eecad83603b331b1bfbce0f0310f8942df8`.
- Exact-approved grid-only CPU probe completed on all `984` V143 attacks.
- Baseline retained: active `425/725`, discrete model-tab/candidate overlap `144/725` (`19.9%`), median max candidate multipitch probability `0.2911`.
- V3 primary direction: new lower probability higher `19/43`, old upper higher `24/43`; therefore this acoustic-domain model does **not** independently support V3 and is not used as a primary consensus gate.

### Robust electric-guitar TabCNN — strongest independent source model
- DAFx 2024 `robust-guitar-tabs/code`; repository license `CC0-1.0`; checkpoint published with Zenodo record `11406378` (TabCNN + GuitarProFX).
- Checkpoint MD5 `ce168b2cd426f81a2a78499214e40605`; SHA256 `1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c`.
- Research workflow run `32815631220` successfully acquired the public checkpoint; artifact `9551275181`; no Modal/L4.
- Exact model contract reproduced: 22050 Hz, hop 512, CQT 192 bins / 24 bins-octave / C1, -80..0 dB -> 0..1, 9-frame context, six strings, frets 0-19 + silence.
- Exact-approved full-grid CPU probe:
  - baseline retained `725`: model active `577` (`79.6%`), discrete model-tab/candidate overlap `348` (`48.0%`), median max candidate probability `0.391995`;
  - V2 exception-band `123`: active `96`, overlap `60` (`48.8%`), median `0.386752` — essentially baseline-like independent support;
  - V2 subfloor local peaks `25`: active `15`, overlap `5` (`20.0%`), median `0.093627`;
  - remaining positive subfloor nonlocal `105`: active `73`, overlap `38` (`36.2%`), median `0.300974`;
  - remaining nonpositive `6`: active `2`, candidate overlap `0`.
- Exact electric evidence persisted at `debug/v143-contextual-prune/electric-tabcnn-v3-consensus-evidence.json`, commit `f783f9c551e0efb8b9807e7bfe2a964826e18fee`.
- This independent model is useful as a **positive consensus source**, not a blind replacement: even on exact audio it misses many current V143 notes.

## Harmonic primary progression
### V3 — V143 physical evidence only
- `analyzer/v143_contextual_harmonic_primary_shadow_v3.py`; validator `analyzer/v143_contextual_harmonic_primary_shadow_v3_replay_validator.py`.
- V3 corrected `43/725` primaries using same-measure local support OR stricter two-view extra-harmonic support; attacks unchanged; invented/unplayable 0.
- V3 was deliberately not frozen because an independent source model had not yet confirmed the direction.

### V4 — CURRENT STRONGEST PRIMARY SHADOW
- Exact-approved robust electric TabCNN provides the missing independent criterion.
- Decision: accept a V3 lower-primary correction only when the external electric model's **max legal string/fret probability for the proposed lower primary is strictly greater than that for the old upper primary** at the same exact grid frame. This is pairwise only; **no new numeric threshold**.
- Exact result: V3 proposed `43`; electric consensus accepts `34`, rejects `9`.
- Across all 43 V3 proposals, electric model favors new lower `34`, old upper `9`; median new-minus-old probability `+0.104154`; its discrete top tablature chooses new `16` times vs old `2`.
- V4 accepted intervals: octave `29`, 19 semitones `3`, two octaves `2`.
- Primary MIDI64 count `202 -> 187`.
- Exact replay after V4: attacks `725 -> 725`; selected pitches `970 -> 970`; rendered pitches `967 -> 967`; voicing drops remain `3`; invented pitch `0`; invalid primary `0`; unplayable primary `0`.
- Validator: `analyzer/v143_contextual_harmonic_primary_shadow_v4_replay_validator.py`, commit `6a1dd9285dacc863ccb9f0a6a7e508b719ea2c38`.
- Durable validation: `debug/v143-contextual-prune/contextual-harmonic-primary-shadow-v4-validation.json`, commit `a742a3df5b468ee54b6fadf72c0f111b8c824424`; local full validation SHA256 `7eea032a2bdc12fcb0d5e0c4693bdc7a6ea06db447d1a28c0044192e724cad99`.
- V4 is still a **shadow**: not inserted into producer, not frozen, not professionally scored.

## Electric evidence for attack research — not yet promoted
- Below the old 0.60 transient floor, the robust electric model produces a discrete predicted tablature pitch that intersects the existing V143 candidate MIDI universe on `43` attacks total: `5/25` V2 local-peak rescues + `38/105` previously unrescued positive subfloor attacks; `0/6` nonpositive.
- This gives a promising no-new-threshold future attack policy: below 0.60, require independent electric model/tab candidate overlap instead of relying on local transient prominence alone.
- Do not promote yet. First build an exact CPU replay/voicing validator and quantify the resulting attack/pitch set. Downstream technique/sustain remains a separate freeze boundary.

## PDF/string-fret state
- `lib/createV143RhythmPdf.js` is already a structured graphical six-line renderer; historical PDF fidelity reached `1.0`. Musical content correctness remains the main blocker.
- Current stateless voicing resolver cannot infer performer-intended positions from MIDI alone. The electric TabCNN can now provide independent string/fret evidence; use it conservatively as consensus before any sequence voicing mutation.

## Research infrastructure / cleanup
- Draft PR #20 `v143-research-checkpoint-fetch` exists only to trigger bounded CPU research workflows. **Never merge it.**
- Temporary research fetch workflows live only on `v143-contextual-prune-lobo`; remove them after needed public artifacts/provenance are durably captured.
- No Modal/L4 used in this entire specialized-model phase.

## Current integrity
- Branch head before this checkpoint: `a742a3df5b468ee54b6fadf72c0f111b8c824424`.
- Protected runtime reverified exact blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1` immediately before checkpoint.
- No Production/main change; no professional scorer/reference; no freeze-ready candidate yet.

## Next exact actions
1. Reverify branch head + protected blob after this checkpoint commit.
2. Build **Attack V3 electric-consensus replay shadow**: baseline retained + full existing 0.60-0.70 exception band + below-0.60 attacks only when exact-approved electric TabCNN's discrete predicted MIDI intersects the already-observed V143 candidate MIDI set. Recompute V2 pitch sets and deterministic voicing CPU-only; no thresholds/new pitches.
3. Keep V4 as current strongest primary correction and apply it to existing retained attacks in any combined content shadow.
4. Investigate electric-model string/fret consensus only where it agrees with V143-observed pitch; do not blindly replace current voicing.
5. Resolve downstream technique/sustain evidence for any newly rescued attacks before freeze/professional scoring.
6. Improve conventional notation appearance only after musical content is materially stronger.
7. No Modal/L4 without fresh explicit authorization.
8. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, PDF fidelity=1.0.
