# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Montreal
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

## Closed historical professional score
- Retired score 1: 725 attacks -> 985 notes, 113 measures, PDF fidelity 1.0; pitch F1 `0.23718280683583634`; pitch+timing F1 `0.033143448990160536`; critical mismatches `1723`.
- Retired score 2: 889 events, PDF fidelity 1.0; pitch F1 `0.24305177111716622`; pitch+timing F1 `0.03051771117166212`; critical mismatches `1635`.
- Do not tune against these identities.

## Successful paid capture — permanently reusable CPU fixture
- Workflow `32805316807`, pinned capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`; exactly one successful Modal command consumed and automatic retry disabled.
- Counts: eligible attacks `984`; retained `725`; pruned `259`; original pitch hypotheses `7535`; replay hypotheses `10585`; stored selected pitches `970`; rendered `967`; voicing drops `3`; measures `1-113`.
- Strict replay/voicing/grid/onset checks all green.
- Candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`; replay validation `182247f2beda257a49cfb454b1e7fc920594ffe5ecce39f7b9517ed15b21b95a`; compare `c77f923db45099f79df563e2c2d2487e46dceaef6f9469db8bd790f78f8cfcda`; lock `49898a441aed8519d96a71bc46c3e85d5d6c64c4be6da5398e9749ab1d6287be`; events `20fef66fdfd48b4e26ae3ec34fe215a4538375e6e6541a4c3f94b97e6fd8d547`; replay evidence `2c42c590bd9ddb47e304b385b67319cd15873b2dd75953d17e90b9b16bb140a2`.
- Permanent manifest `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json` commit `87b4b698010fa11c62e76e061a2bbe91825de5ba`.
- CPU materializer `analyzer/materialize_v143_precision_fixture.py` commit `72f43d8c82629b9ff388fa0013fe6e06b024a660`.
- Future precision/attack/pitch/voicing/timing work uses this fixture CPU-only first.

## Precision-v2 and attack shadows
- `analyzer/v143_contextual_prune_precision_shadow_v2.py`, policy `envelope-balanced-secondary-v2`: non-harmonic secondaries use 2-of-3 score/attack/body at existing `0.80`; harmonic upper intervals `{12,19,24,28,31,36}` stay 3-of-3 at `0.92`.
- Replay schema 2 stores every eligible attack with two-view evidence, candidate MIDI universe, envelope/score values, grid/onset/error and support counts.
- Attack V1 commit `674dd4de5331e079f80e6f2fc798b9c80de9d289`: adds 26 attacks, no removals/failures.
- Attack V2 commit `1f4477291b138ec04d843369bdc35f3dcb590167`, validator `ab4642a463227385a28136767688b68ab7b42d0f`, validation `43beb3cbba6d576171614cd47ad03aac78a8baaf`: adds 148, removes 0 -> 873 shadow attacks; remaining pruned `111` = `105` positive subfloor nonlocal + `6` nonpositive. New attacks select 214 observed pitches; voicing renders 212; only two expected voicing drops.
- Attack V2 is the strongest supported attack correction. Do not broaden remaining 105 positive subfloor events without independent source-only evidence because low transient/body ratio may be sustain bleed.

## Upstream/downstream replay boundary
- Order: protected contextual prune -> source-only correction -> precision-v2 -> promoted-harmonic guard -> replay capture -> deterministic voicing -> semantic/sustain.
- Correction counts: base `952`; corrected `984`; rescued `32`; observed slots `1795`; strict slots `1649`; rescue identities are not persisted. Do not invent the 32-vs-952 split.
- Schema 2 supports CPU attack/pitch policy and deterministic voicing/string/fret/grid/onset experiments, but not the full downstream CQT/stem universe required to recompute every bend/legato/sustain annotation for hypothetical newly retained attacks. Attack V1/V2 remain shadows, not freeze-ready candidates.

## Professional PDF renderer audit
- V143 API already reaches `lib/createV143RhythmPdf.js` through `lib/createAiTabPdf.js`; this is a bespoke graphical 6-line renderer, not the old ASCII renderer.
- It already includes landscape systems, four measures/system, measure/beat labels, repeat/simile markers, chord stacks, confidence classes, P.M./trill/dead-note/slide/hammer/pull/bend/sustain annotations, section labels and legend/footer.
- `lib/v143RenderContract.js` strictly validates 1/16 grid identity, string/fret/MIDI consistency, measure coverage and sustain schema.
- Historical PDF fidelity is already `1.0`: **musical event correctness, especially pitch/fundamental selection, is the dominant blocker.** More conventional rhythm stems/beams can be added later after content accuracy improves.

## Pitch/fundamental diagnosis
- Producer: `analyzer/v143_repaired_timing_precision_candidate_product_modal.py`.
- Existing lower-fundamental promotion occurs in `v143_contextual_prune_precision_shadow[_v2].py`; `v143_precision_promoted_harmonic_guard.py` only removes a contradictory strongest upper harmonic after a promotion and never changes primary MIDI itself.
- Current retained primary distribution from the exact saved replay is heavily concentrated: MIDI 64=`202/725`, 52=`107`, 62=`76`, 59=`61`, 57=`39`, 67=`36`. Of the MIDI-64 primaries, `194/202` remain the strongest raw pitch rather than a promoted lower fundamental.
- Lower observed candidates are common under MIDI-64 primaries (MIDI52 coexists in `117`; MIDI40 in `67`). Weak physical fundamentals can therefore lose to strong overtones under the existing independent per-attack harmonic-family ranking.
- Do **not** select an uncapped harmonic weighting just because it changes this song's distribution; that has no independent acceptance criterion.

## New contextual harmonic-primary shadow V1 — CPU-only, reference-free
- Module: `analyzer/v143_contextual_harmonic_primary_shadow_v1.py`, commit `ece9b156b4e9d9cd14294ba767a71b025a12dd21`.
- Replay validator: `analyzer/v143_contextual_harmonic_primary_shadow_v1_replay_validator.py`, commit `9d8344c339aeb19f50eb1b16c323643578d00e78`.
- Durable validation: `debug/v143-contextual-prune/contextual-harmonic-primary-shadow-v1-validation.json`, commit `5bdaccd327beaa55366d26e27276d94c1d4bf27a`.
- Purpose: repair isolated strongest-raw upper-harmonic primary flips only when a lower candidate is already physically observed/positive at that attack, the current primary is in the existing harmonic interval family above it, the **existing `FUNDAMENTAL_MIN_RAW_RATIO=0.55`** guard passes, and a retained attack in the same measure within the **existing ±2-step local radius** already uses that exact lower MIDI as primary.
- No new numeric threshold, song/key/chord/reference label, attack or unobserved pitch is introduced. Input neighbor primaries are immutable during the pass, so corrections cannot cascade.
- Exact CPU replay result: `12/725` primaries corrected; attacks unchanged `725->725`; invented pitches `0`; invalid primaries `0`; validation green.
- Transitions: `64->52` x9, `64->40` x1, `52->40` x1, `62->50` x1. Harmonic intervals: octave x11, two octaves x1. MIDI64 primary count falls `202->192` for this conservative shadow.
- This is a **shadow only**. It has not been inserted into the paid producer, frozen, or professionally scored.

## Fingering/voicing quality
- `v143_rhythm_guitar_note_mapper.py::resolve_joint_chord_voicing` is stateless and independently minimizes chord fret span/max/sum each attack, tending toward open/lowest-fret legal positions rather than phrase-continuous human fingering.
- A sequence-aware deterministic voicing optimizer remains a safe CPU-only improvement path if it preserves exact attack/MIDI content, standard-tuning legality, unique/non-crossing strings and deterministic output while reducing physical position jumps. Build/validate as shadow before integration.

## Timing/current mutation state
- Relative sixteenth spacing remains strongly source-supported; tempo `129.19921875`; no global timing mutation justified.
- No Modal/L4 after run `32805316807`; no professional scorer/reference; no Production/main change; protected runtime unchanged; no freeze-ready candidate.

## Next exact actions
1. Reverify protected runtime blob after this checkpoint.
2. Stay CPU-only on pinned fixture.
3. Validate contextual harmonic-primary V1 more deeply for playable voicing and structural consistency; do not expand its criteria without independent source evidence.
4. Build/validate sequence-aware professional voicing shadow without changing attacks or MIDI content.
5. Continue general two-view harmonic/fundamental research; no arbitrary song-specific weights.
6. Keep Attack V2 as strongest attack correction; do not broaden remaining 105 positive subfloor attacks without new evidence.
7. Improve conventional PDF rhythm notation only after musical content is materially stronger.
8. Do not freeze/professional-score while newly rescued attacks lack recomputable downstream technique/sustain evidence.
9. No Modal/L4 without fresh explicit authorization for a clearly identified missing evidence dimension.
10. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.
