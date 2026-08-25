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
- Current retained primary distribution from exact saved replay: MIDI 64=`202/725`, 52=`107`, 62=`76`, 59=`61`, 57=`39`, 67=`36`. Of MIDI64 primaries, `194/202` remain strongest raw rather than a promoted lower fundamental.
- Lower observed candidates are common under MIDI64 primaries: MIDI52 coexists in `117`; MIDI40 in `67`. Weak physical fundamentals can lose to strong overtones under existing independent per-attack ranking.
- Do **not** select uncapped harmonic weighting merely because it changes this song's distribution; no independent acceptance criterion exists.

## Contextual harmonic-primary shadow V1 — CPU-only, reference-free
- Module `analyzer/v143_contextual_harmonic_primary_shadow_v1.py`, commit `ece9b156b4e9d9cd14294ba767a71b025a12dd21`.
- Validator `analyzer/v143_contextual_harmonic_primary_shadow_v1_replay_validator.py`, commit `9d8344c339aeb19f50eb1b16c323643578d00e78`.
- Validation `debug/v143-contextual-prune/contextual-harmonic-primary-shadow-v1-validation.json`, commit `5bdaccd327beaa55366d26e27276d94c1d4bf27a`.
- Only repairs a strongest-raw upper-harmonic primary when a lower candidate is observed/positive at the same attack, the upper-lower interval is already in the harmonic family, existing `FUNDAMENTAL_MIN_RAW_RATIO=0.55` passes, and a retained attack in the same measure within existing ±2-step local radius already uses that lower MIDI as primary.
- No new numeric threshold/song/key/chord/reference rule; no cascading corrections.
- CPU replay: `12/725` primaries corrected; attacks `725->725`; invented pitches `0`; invalid primaries `0`; validation green. Transitions `64->52` x9, `64->40` x1, `52->40` x1, `62->50` x1; octave x11/two-octave x1; MIDI64 primaries `202->192`.
- All 12 changed pitch sets remain jointly playable in standard tuning under current resolver. **Shadow only**, not producer-integrated/frozen/scored.

## Fingering/voicing research — important limit discovered
- Current resolver is stateless and heavily favors lowest-fret legal placements.
- Exact rendered product groups into 725 attacks: 516 single-note, 181 two-note, 24 three-note, 3 four-note, 1 five-note. Enumerating all legal noncrossing standard-tuning voicings is cheap (max 20 states/attack; median 6).
- A CPU dynamic-programming prototype using physical fret/string geometry reduced cumulative hand-motion dramatically versus baseline, but predictably shifted many attacks higher on the neck because **MIDI alone cannot determine the performer's intended string/fret choice**. A continuity optimizer can make fingering smoother but cannot prove source-accurate fingering.
- Therefore do not integrate a sequence voicing optimizer as an accuracy fix without independent string/hand-position evidence. This is now secondary to obtaining a guitar-specific tablature evidence source.

## Specialized guitar-AMT research — strongest new strategic lead
- Public MIT-licensed 2026 project `ErenReyhanlioglu/Guitar-Transcription` directly predicts guitar tablature/string-fret state, hand position, string activity, pitch class and multipitch from HCQT + Mel features.
- Public pretrained weights exist in `ErenReyhanlioglu/Guitar-Transcription-Weights`; six fold `model_best.pt` checkpoints are ~26.8 MB each. The weights repository license is also MIT.
- Reported six-fold GuitarSet results: tablature F1 ~`0.784`, TDR ~`0.946`, tab-derived multipitch F1 ~`0.845`, auxiliary multipitch F1 ~`0.864`.
- Model config: 22050 Hz, hop 512, HCQT `6x144` harmonics `[0.5,1,2,3,4,5]`, Mel 256, 19-frame context, standard tuning `[40,45,50,55,59,64]`, frets 0-19 + silence, MIDI 40-88.
- Acoustic GuitarSet domain gap must be tested; treat this as independent source-only tab/pitch/string evidence, not a blind timing replacement.
- Strategic architecture: preserve V143 beat/grid timing -> guitar-AMT frame/string/fret evidence -> snap/fuse only source-supported attacks/pitches onto frozen grid -> preserve no-invention/render contracts -> semantic/sustain/render.

### Bounded guitar-AMT probe harness now committed
- `analyzer/v143_specialized_guitar_amt_probe.py`, commit `97c76dd32e236663850f3ad7996b86f9a527ea2c`.
- Durable feature-contract self-test: `debug/v143-contextual-prune/specialized-guitar-amt-probe-self-test.json`, commit `27d71618538bd5b7d0e860b2f0513f916f0315a0`.
- Self-test reproduces HCQT shape `6x144x44` and Mel shape `1x256x44` for a synthetic one-second signal; green.
- Harness records source-audio SHA, checkpoint SHA, upstream provenance/license/blobs, and refuses a non-approved source SHA unless `--allow-nonapproved-domain-probe` is explicitly supplied.
- It loads upstream code/checkpoint from caller-supplied paths; no third-party weights/code are vendored into DadRock.
- It reproduces the upstream amt-tools feature contract with librosa: VQT harmonic stack, -80..0 dB -> 0..1 scaling, Mel 256, 19-frame windows, 500-frame chunk inference.
- With `--v143-product`, it samples the model on the existing 984 frozen V143 eligible grid attacks and exports model tab/string/fret notes, candidate multipitch probabilities, string activity and hand-position probabilities. This is designed for source-only fusion diagnostics without changing timing/attacks.
- Current environment could inspect public checkpoint metadata but cannot retrieve the ~26.8 MB binary through the available GitHub text connector; no checkpoint inference has been run yet. This is a tooling-access limit, not a model rejection.

## Audio availability check
- ChatGPT library file `DS Music - Are You Gonna Go My Way (Remastered 2025) - Lenny Kravitz.m4a`: 3,464,988 bytes, duration ~210.675 s, SHA256 `c187bead44529d38544b8452f57328aaf17ce606f08217b78e3157c648392481`.
- It does **not** match approved fixture SHA `215bd5a6...`; it cannot be substituted for freeze/score/candidate claims. It may only be a clearly isolated domain-compatibility probe.
- Preserved paid artifact ZIP contains JSON evidence, not audio/stems; exact approved-fixture inference with a new model is unavailable from it alone.

## Timing/current mutation state
- Relative sixteenth spacing remains strongly source-supported; tempo `129.19921875`; no global timing mutation justified.
- No Modal/L4 after run `32805316807`; no professional scorer/reference; no Production/main change; protected runtime unchanged; no freeze-ready candidate.

## Next exact actions
1. Reverify protected runtime blob after checkpoint.
2. Stay CPU-only/no Modal.
3. Continue trying a zero-cost/local route to obtain one MIT guitar-AMT checkpoint binary; if unavailable, keep harness ready rather than weakening boundaries.
4. If checkpoint becomes locally accessible, first run only the library M4A as an explicitly non-approved domain probe and inspect structural guitar/string/fret plausibility; never score it as the approved fixture.
5. Keep contextual harmonic-primary V1 and Attack V2 as conservative source-only shadows; no arbitrary weight expansion.
6. Do not integrate sequence voicing optimization without independent string/hand-position evidence; the guitar-AMT branch can supply that missing evidence.
7. Once exact approved audio is available to the harness, test guitar-AMT evidence against frozen timing/source invariants before producer integration.
8. Improve conventional PDF rhythm notation only after musical content is materially stronger.
9. Do not freeze/professional-score while required downstream evidence is absent.
10. No Modal/L4 without fresh explicit authorization.
11. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.
