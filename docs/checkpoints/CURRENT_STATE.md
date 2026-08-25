# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; produce a genuinely professional guitar-tab PDF, not merely a polished-looking PDF.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1` — reverified exact after latest commits.
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
- Workflow `32805316807`, pinned capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`; one successful Modal command consumed, automatic retry disabled.
- Counts: eligible attacks `984`; retained `725`; pruned `259`; replay pitch hypotheses `10585`; selected pitches `970`; rendered pitches `967`; voicing drops `3`; measures `1-113`.
- Candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`; replay validation `182247f2beda257a49cfb454b1e7fc920594ffe5ecce39f7b9517ed15b21b95a`; compare `c77f923db45099f79df563e2c2d2487e46dceaef6f9469db8bd790f78f8cfcda`; lock `49898a441aed8519d96a71bc46c3e85d5d6c64c4be6da5398e9749ab1d6287be`; events `20fef66fdfd48b4e26ae3ec34fe215a4538375e6e6541a4c3f94b97e6fd8d547`; replay evidence `2c42c590bd9ddb47e304b385b67319cd15873b2dd75953d17e90b9b16bb140a2`.
- Permanent manifest `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json`, commit `87b4b698010fa11c62e76e061a2bbe91825de5ba`.
- CPU materializer `analyzer/materialize_v143_precision_fixture.py`, commit `72f43d8c82629b9ff388fa0013fe6e06b024a660`.

## Attack precision state
- `v143_contextual_prune_precision_shadow_v2.py`: non-harmonic secondaries use 2-of-3 score/attack/body at existing `0.80`; harmonic upper intervals `{12,19,24,28,31,36}` remain 3-of-3 at `0.92`.
- Attack shadow V2 remains strongest supported attack correction: adds `148`, removes `0` -> `873` shadow attacks; remaining pruned `111` = `105` physically positive sub-0.60 nonlocal + `6` nonpositive.
- Do not broaden the remaining 105 without an independent source-only discriminator; low transient/body ratio can be sustain bleed.
- Attack V2 remains a precision shadow only because replay schema 2 lacks the complete downstream CQT/stem universe needed to recompute technique/sustain for newly rescued attacks.

## Professional PDF renderer
- `lib/createV143RhythmPdf.js` is already a structured six-line graphical renderer with systems, measures, beat grid, sections, chord stacks, techniques, sustain and deterministic string/fret validation.
- Historical PDF fidelity is `1.0`; **musical content accuracy — especially fundamental/pitch and source-accurate fretboard placement — is the dominant blocker.**

## Harmonic-primary research
### V1 — local confirmation
- `analyzer/v143_contextual_harmonic_primary_shadow_v1.py`, commit `ece9b156b4e9d9cd14294ba767a71b025a12dd21`.
- Validator `9d8344c339aeb19f50eb1b16c323643578d00e78`; durable validation `5bdaccd327beaa55366d26e27276d94c1d4bf27a`.
- Repairs strongest-raw upper harmonics only when an observed lower candidate passes existing `FUNDAMENTAL_MIN_RAW_RATIO=0.55` and a same-measure retained attack within existing ±2-step radius already uses that lower MIDI.
- CPU replay: `12/725` primaries corrected; invented pitches `0`; invalid primaries `0`; all changed primaries playable.

### V2 — two-view physical harmonic support — NEW STRONGEST PRIMARY SHADOW
- Module: `analyzer/v143_contextual_harmonic_primary_shadow_v2.py`, commit `36c5f595d9664b5f0844ccc19ef0b237a758300e`.
- Independent replay validator: `analyzer/v143_contextual_harmonic_primary_shadow_v2_replay_validator.py`, commit `ce2bbb1f5d9eb1a10b218ffebc3fb290ed833e4b`.
- Durable compact validation: `debug/v143-contextual-prune/contextual-harmonic-primary-shadow-v2-validation.json`, commit `5f0d0fe4ab12b2e36f7c2da8c91b839018596be0`.
- Full local validation SHA256: `439760c749775ec0209119fba36530329c83c781640ca0121bdab6a887ccfdf8`.
- Policy `local-or-two-view-harmonic-support-primary-v2` preserves V1. If local confirmation is absent, a lower observed candidate may replace a strongest-raw upper harmonic only when:
  1. upper-lower interval is already in the existing harmonic family `{12,19,24,28,31,36}`;
  2. lower candidate is physically positive/observed;
  3. the **existing 0.55 strength guard passes independently in view A and view B**; and
  4. the lower candidate has **strictly more positive upper-harmonic-family members than the current primary in both independent views**.
- No new numeric confidence threshold, song/key/chord/reference rule, attack, unobserved pitch or timing relocation.
- Input primary map is immutable during the pass; corrections cannot cascade.
- Exact CPU replay: `62/725` primaries corrected; reason split `50` two-view-only + `10` local+two-view + `2` local-only.
- Harmonic intervals: octave `52`, 19-semitone `4`, two-octave `4`, 28-semitone `1`, 31-semitone `1`.
- Major transitions: `64->52` x24, `52->40` x6, `71->59` x5, `64->40` x3, `62->50` x3, `67->55` x3, `69->57` x3, `76->64` x3.
- MIDI64 primary count drops `202 -> 179`.
- Selected pitches `970 -> 968`; deterministic rendered pitches `967 -> 966`; shadow voicing drops `2`.
- Attack identity unchanged; invented pitches `0`; invalid primaries `0`; unplayable primaries `0`; validation green.
- **V2 is now the strongest supported primary/fundamental shadow. It is not producer-integrated/frozen/professionally scored.**

## Fretboard/string placement limit
- Current resolver is deterministic but stateless and favors low-fret legal voicings.
- Sequence continuity can smooth fingering but MIDI alone cannot prove performer string/fret choice; do not integrate a continuity optimizer as an accuracy fix without independent string/hand-position evidence.

## Specialized guitar-AMT lead
- MIT 2026 `ErenReyhanlioglu/Guitar-Transcription` directly predicts tablature/string-fret state, hand position, string activity, pitch class and multipitch from HCQT+Mel; reported GuitarSet tablature F1 ~`0.783`, TDR ~`0.946`.
- Probe harness committed: `analyzer/v143_specialized_guitar_amt_probe.py`, commit `97c76dd32e236663850f3ad7996b86f9a527ea2c`; self-test commit `27d71618538bd5b7d0e860b2f0513f916f0315a0`.
- Harness is research-only, hashes source/checkpoint, refuses non-approved audio unless explicit domain-probe flag is supplied, and can sample model string/fret/multipitch evidence on the frozen V143 grid.
- Public checkpoint binary (~26.8 MB) is still inaccessible through the available text-only GitHub connector; no checkpoint inference has been run.

## Audio availability
- Library M4A `DS Music - Are You Gonna Go My Way (Remastered 2025) - Lenny Kravitz.m4a`: SHA256 `c187bead44529d38544b8452f57328aaf17ce606f08217b78e3157c648392481`, not approved fixture SHA `215bd5a6...`.
- It may be used only as an explicitly non-approved model/domain research probe, never for freeze/score/candidate claims.

## Current mutation/cost state
- No Modal/L4 after successful run `32805316807`.
- No professional scorer/reference reopened.
- No `main`/Production changes.
- Protected runtime remains exact blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- No freeze-ready candidate yet.

## Next exact actions
1. Stay CPU-only/no Modal.
2. Deep-check harmonic-primary V2 for repeated-structure consistency and false-octave safeguards using only saved source evidence; do not tune against retired scores.
3. Search for the exact approved audio in available persistent files; if found, run specialized guitar-AMT only after a checkpoint becomes locally accessible.
4. Keep trying a zero-cost route to obtain one MIT guitar-AMT checkpoint; if unavailable, do not weaken the source/fixture boundaries.
5. Keep Attack V2 as strongest attack shadow; do not broaden remaining subfloor attacks without new evidence.
6. Do not integrate sequence voicing without independent string/hand-position evidence.
7. Only after musical content is materially stronger, improve conventional printed rhythm notation/stems/beams if needed.
8. Do not freeze/professional-score while required downstream evidence is absent.
9. No Modal/L4 without fresh explicit authorization.
10. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.
