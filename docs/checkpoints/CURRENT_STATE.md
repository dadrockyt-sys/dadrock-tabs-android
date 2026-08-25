# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; produce a genuinely professional guitar-tab PDF, not merely a polished-looking PDF.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. No runtime/shadow tuning or selection from it.
- Retired render identities must never be rerun/rescored:
  - `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
  - `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 without fresh explicit user authorization. None is currently authorized.**
- Keep timing frozen unless new source-only evidence proves otherwise. Tempo remains exactly `129.19921875`.

## Historical professional-score state — reference now closed
- Score 1 retired: 725 attacks -> 985 notes, 113 measures, PDF fidelity 1.0; pitch F1 `0.23718280683583634`; pitch+timing F1 `0.033143448990160536`; critical mismatches `1723`.
- Score 2 retired after harmonic contradiction guard: 889 events, PDF fidelity 1.0; pitch F1 `0.24305177111716622`; pitch+timing F1 `0.03051771117166212`; critical mismatches `1635`.
- Do not score/tune against either retired identity again.

## Successful paid capture — permanently reusable CPU fixture
- Authorized workflow run `32805316807` completed successfully at commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`.
- Exactly one successful Modal command consumed; automatic retry disabled/final lock completed.
- Counts: eligible attacks `984`; retained `725`; pruned `259`; original observed pitch hypotheses `7535`; eligible replay pitch hypotheses `10585`; stored selected pitches `970`; rendered pitches `967`; voicing drops `3`; fail-safe attacks `0`; measures `1-113`.
- Legacy selected pitches `891`; precision-v2 selected `970`; v2 adds `79`, removes `0`, across `75` attacks.
- Strict replay mismatches zero; deterministic voicing/string/fret/grid/onset replay green.
- Candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Replay validation SHA256 `182247f2beda257a49cfb454b1e7fc920594ffe5ecce39f7b9517ed15b21b95a`.
- Replay compare SHA256 `c77f923db45099f79df563e2c2d2487e46dceaef6f9469db8bd790f78f8cfcda`.
- Capture lock SHA256 `49898a441aed8519d96a71bc46c3e85d5d6c64c4be6da5398e9749ab1d6287be`.
- Events SHA256 `20fef66fdfd48b4e26ae3ec34fe215a4538375e6e6541a4c3f94b97e6fd8d547`.
- Replay evidence SHA256 `2c42c590bd9ddb47e304b385b67319cd15873b2dd75953d17e90b9b16bb140a2`.
- Artifact `v143-precision-v2-one-shot-32805316807`, ID `9548666053`, ZIP SHA256 `5104522aab3e6193c6b06fe3abb807994065f858a945a81070c611fc63707d4f`, is secondary only.
- Permanent manifest: `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json`, commit `87b4b698010fa11c62e76e061a2bbe91825de5ba`.
- CPU materializer: `analyzer/materialize_v143_precision_fixture.py`, commit `72f43d8c82629b9ff388fa0013fe6e06b024a660`.
- Future precision/attack/pitch/voicing/timing research must use this saved fixture CPU-only first.

## Precision-v2
Module `analyzer/v143_contextual_prune_precision_shadow_v2.py`, policy `envelope-balanced-secondary-v2`.
- Non-harmonic secondaries: 2-of-3 score/attack/body at existing `0.80`.
- Harmonic intervals `{12,19,24,28,31,36}`: strict 3-of-3 at `0.92`.
- Primary/no-invention/harmonic protections preserved.
- Replay schema 2 persists all 984 eligible attacks with A/B evidence, candidate MIDI universe, attack/early/sustain/body/continuity/score, grid/onset/error, precision strength/support counts and retained identities.

## Attack shadows
### V1
- `analyzer/v143_contextual_prune_attack_shadow_v1.py`, commit `674dd4de5331e079f80e6f2fc798b9c80de9d289`.
- Validator commit `d917e1193bf57d3b31bebce2427fae9523ac7057`; durable validation commit `bf25366d68561fc7c995e2b115e5e1314f8e7ff4`.
- Adds 26, removes 0 -> 751. 25 sub-0.60 local transient peaks + 1 exception-band. 36 observed pitches; no voicing/unplayable/invention/collision failures.

### V2 — strongest supported attack correction so far
- `analyzer/v143_contextual_prune_attack_shadow_v2.py`, commit `1f4477291b138ec04d843369bdc35f3dcb590167`.
- Validator commit `ab4642a463227385a28136767688b68ab7b42d0f`; validation commit `43beb3cbba6d576171614cd47ad03aac78a8baaf`.
- Existing 0.60-0.70 exception band no longer requires composite-strength local maximum; below 0.60 only V1 local transient peaks survive. No new numeric threshold.
- Adds 148, removes 0 -> 873 shadow attacks. Remaining pruned `111` = `105` physically positive subfloor nonlocal + `6` nonpositive.
- New attacks select 214 observed pitches; voicing renders 212; only drops m19/s6 `[52,86]->[52]`, m113/s14 `[43,44]->[43]`; no invented pitches/unplayable primaries/grid collisions.
- Do not broaden the remaining 105 positive subfloor attacks without an independent source-only discriminator because low transient/body ratio may be sustain bleed.

## Upstream correction/downstream boundary
- Order: protected contextual prune -> source-only correction -> precision-v2 -> promoted-harmonic guard -> replay capture -> deterministic voicing -> semantic/sustain.
- Correction counts: base `952`; corrected `984`; rescued `32`; observed slots `1795`; strict slots `1649`. Pinned product stores counts, not identities of the 32 rescues vs 952 base events. Do not invent the split.
- Replay schema 2 supports CPU attack/pitch policy and deterministic voicing/string/fret/grid/onset experiments.
- It does not persist the full downstream CQT/stem energy universe needed to recompute all bend/legato/sustain annotations for hypothetical newly retained attacks. Attack V1/V2 remain shadows, not freeze-ready candidates.

## Professional-PDF renderer audit — new 2026-08-24 finding
- API path for analysisVersion `1.4.3` already reaches `lib/createV143RhythmPdf.js` through `lib/createAiTabPdf.js`; this is not the old ASCII renderer.
- `createV143RhythmPdf.js` already provides a dedicated graphical 6-line tab renderer: landscape Letter systems, 4 measures/system, measure/beat labels, structural markers/repeats/simile, chord stacks, confidence classes, P.M./trill/dead-note/slide/hammer/pull/bend/sustain annotations, sections/subheadings and legend/footer.
- `lib/v143RenderContract.js` strictly validates 1/16 grid identity, string 0-5, fret 0-24, MIDI/string/fret consistency, measure coverage, onset/confidence and sustain-shadow schema.
- Historical PDF fidelity is already `1.0`; therefore **layout is not the dominant blocker to a professional result. Musical event correctness is.**
- Renderer cosmetics can be improved later (e.g. more conventional rhythmic stems/beams), but should not distract from pitch/attack correctness first.

## Pitch/fundamental diagnosis — highest-impact current investigation
- Successful product producer is `analyzer/v143_repaired_timing_precision_candidate_product_modal.py`.
- Harmonic guard implementation is `analyzer/v143_precision_promoted_harmonic_guard.py`.
- Primary/fundamental promotion actually occurs earlier in `v143_contextual_prune_precision_shadow[_v2].py`; the later harmonic guard **does not change the primary**. It only removes the strongest upper pitch when the precision stage has already reinterpreted that pitch as an overtone of a promoted lower primary.
- Current harmonic-family selector uses candidate score plus capped upper-harmonic contributions at intervals `{12,19,24,28,31,36}`, then requires the selected lower primary's raw score to be at least `0.55` of the strongest raw score.
- CPU inspection of the exact saved replay (no scorer/reference): current retained primaries are highly concentrated, with MIDI `64` as primary for `202/725` attacks; `194/202` of those are simply the strongest raw pitch rather than a promoted lower fundamental. Other common primaries include MIDI 52=`107`, 62=`76`, 59=`61`, 57=`39`, 67=`36`.
- The rendered product is also strongly open-position biased because the current deterministic voicing resolver independently chooses the lowest-fret legal position at every attack; this is a separate fingering/presentation problem from MIDI correctness.
- For MIDI-64 primary attacks, observed lower harmonic-family candidates are common. Example aggregate: MIDI 52 coexists in `117` such attacks; MIDI 40 in `67`. Median lower52/high64 score ratio is only ~`0.317`, so the existing capped harmonic-family rule often cannot reinterpret a weak physical fundamental even when multiple upper harmonics support it.
- CPU shadow experiments with uncapped harmonic summation can reduce the MIDI-64 concentration, but **no alternative has been selected/frozen** because there is no independent source-only acceptance criterion yet. Do not choose a new weighting merely because it changes this song's distribution.
- Key research need: build a genuinely general guitar-specific fundamental estimator from the already-persisted two-view physical evidence (direct fundamental presence + multi-harmonic support + A/B consistency), then validate only no-invention/physical/structural invariants before any future holdout score.

## Fingering/voicing quality — independent safe improvement path
- `analyzer/v143_rhythm_guitar_note_mapper.py::resolve_joint_chord_voicing` is stateless. Its lexicographic objective minimizes within-chord fret span/max/sum and therefore tends to choose open/lowest-fret positions independently at each attack.
- This can produce technically legal but non-human tab fingering and contributes to the large open-string count. A professional tab should optimize position continuity across adjacent attacks while preserving the exact selected MIDI set and attack grid.
- A phrase/sequence-aware deterministic voicing optimizer is a promising CPU-only improvement because it can be validated without any reference: exact attack identity unchanged; exact MIDI set unchanged; standard-tuning legality; unique/non-crossing strings; deterministic output; and lower cumulative hand/string movement than the current stateless mapping.
- This should be developed as a shadow/validator first, then integrated only after invariants are green.

## Timing state
- Relative sixteenth spacing remains strongly source-supported; at residual <=0.20 step, 697/697 pairs exactly match labeled grid gaps.
- Tempo exactly `129.19921875`.
- Beat repair has no leading phase-index error. Absolute bar phase remains weak/section-dependent; no global timing mutation justified.

## Current mutation/cost state
- No Modal/L4 after successful run `32805316807`.
- No professional scorer/reference invoked.
- No Production or `main` modification.
- Protected runtime unchanged.
- No freeze-ready candidate yet.

## Next exact actions
1. Reverify branch/protected blob after checkpoint write.
2. Stay CPU-only on the pinned capture.
3. Build/validate a **sequence-aware professional voicing shadow** that preserves every attack/MIDI and improves ergonomic continuity; no inference required.
4. In parallel, continue source-only primary/fundamental research using two-view harmonic evidence; do not select arbitrary song-specific weights.
5. Keep Attack V2 as strongest supported attack shadow; do not broaden the remaining 105 positive subfloor attacks without new independent evidence.
6. Once content correctness is materially stronger, enhance `createV143RhythmPdf.js` toward conventional rhythmic tablature while preserving render-contract fidelity.
7. Do not freeze/professional-score while newly rescued attacks lack recomputable downstream technique/sustain evidence.
8. No Modal/L4 without fresh explicit authorization for a clearly identified missing evidence dimension.
9. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.
