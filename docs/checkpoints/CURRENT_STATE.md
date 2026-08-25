# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; produce genuinely professional guitar tablature, not merely a polished-looking PDF.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved audio SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. No runtime/shadow tuning or selection from it.
- Retired render identities never rerun/rescore: `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`, `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 without fresh explicit user authorization. None is currently authorized.**
- Timing frozen unless new source-only evidence proves otherwise; tempo exactly `129.19921875`.

## Preserved paid capture — CPU replay source of truth
- Authorized run `32805316807`; pinned capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`; one Modal command consumed historically, automatic retry disabled.
- Baseline: eligible `984`; retained `725`; pruned `259`; replay pitch hypotheses `10585`; selected `970`; rendered `967`; voicing drops `3`; measures `1-113`.
- Candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`; replay validation `182247f2beda257a49cfb454b1e7fc920594ffe5ecce39f7b9517ed15b21b95a`; compare `c77f923db45099f79df563e2c2d2487e46dceaef6f9469db8bd790f78f8cfcda`; lock `49898a441aed8519d96a71bc46c3e85d5d6c64c4be6da5398e9749ab1d6287be`.
- Durable manifest `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json`; CPU materializer `analyzer/materialize_v143_precision_fixture.py`.

## Exact approved source / independent guitar evidence
- Exact source is in repo at `public/gomywayfullaitest.m4a`; CPU fetch run `32815950324`, artifact `9551396214`, approved SHA verified. No Modal.
- Robust electric-guitar TabCNN: DAFx 2024 `robust-guitar-tabs/code`, CC0-1.0; Zenodo `11406378`; checkpoint SHA256 `1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c`.
- Acquisition run `32815631220`, artifact `9551275181`, no Modal/L4.
- Exact model contract: 22050 Hz, hop 512, CQT 192 bins / 24 bins-octave / C1, -80..0 dB -> 0..1, 9-frame context, six strings.
- Evidence `debug/v143-contextual-prune/electric-tabcnn-v3-consensus-evidence.json`, commit `f783f9c551e0efb8b9807e7bfe2a964826e18fee`.
- Group overlap: baseline `348/725`; exception-band `60/123`; V2 subfloor-local `5/25`; remaining positive subfloor-nonlocal `38/105`; nonpositive `0/6`.
- Use this model only as independent positive consensus, never blind replacement.

## Attack shadow V3 — strongest validated attack shadow
- V3 = baseline `725` + existing exception-band `123` + electric-consensus subfloor `43` = **`891` retained**.
- Relative to V2: remove 20 unsupported local-subfloor rescues, add 38 supported nonlocal rescues, net +18.
- Validator `analyzer/v143_contextual_prune_attack_shadow_v3_replay_validator.py`, commit `d00e2699f07f60b6a5b76d81fc7197f9e5f23e8c`.
- Passing CPU replay `32818611451`, job `97711880585`; exact validation SHA256 `039a42d06abdc60a111cd85f0db9ac07b81caf1c1d91fd65e260ffb6119b1892`.
- Durable output `debug/v143-contextual-prune/attack-shadow-v3-replay-validation.json`, commit `8c1a36f2254197adabc1ed1e1ef65ba62853d073`.
- Exact V3: retained `891`; pruned `93` (`87` positive + `6` nonpositive); selected/rendered `1214/1209`; drops `5`; rescued component `244/242`, drops `2`; measures `113/113`; no invented/unplayable/invalid pitch.
- `freezeReady=false`: rescued attacks lack recomputed downstream technique/sustain evidence.

## Harmonic Primary V4 — strongest validated primary correction
- V3 physical harmonic shadow proposed `43` lower-primary corrections.
- V4 accepts only when exact electric model max legal probability for proposed lower primary is strictly greater than old upper primary at same frame; pairwise only, no new threshold.
- Exact: accepts `34`, rejects `9`; median new-old probability `+0.104154`; primary MIDI64 baseline `202 -> 187`.
- Validator `analyzer/v143_contextual_harmonic_primary_shadow_v4_replay_validator.py`, commit `6a1dd9285dacc863ccb9f0a6a7e508b719ea2c38`.
- Durable validation `debug/v143-contextual-prune/contextual-harmonic-primary-shadow-v4-validation.json`, commit `a742a3df5b468ee54b6fadf72c0f111b8c824424`; SHA256 `7eea032a2bdc12fcb0d5e0c4693bdc7a6ea06db447d1a28c0044192e724cad99`.
- Baseline after V4 remains attacks `725`, selected/rendered `970/967`, drops `3`; no invented/invalid/unplayable primary.

## Combined Content Shadow V5 — CURRENT STRONGEST CONTENT SHADOW
- Validator `analyzer/v143_contextual_prune_combined_content_shadow_v5_replay_validator.py`, commit `3e15b4689cbaf72fd086b7142033b980c9ac401a`.
- Policy: Attack V3 + exact validated Primary V4; all 34 V4 corrections touch pre-existing baseline attacks only; rescued corrections `0`.
- Passing run `32819028013`, job `97713095027`; exact combined validation SHA256 `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- Durable output `debug/v143-contextual-prune/combined-content-shadow-v5-validation.json`, commit `b0dce933d8686d0dbd1c1a7da78460053a71739f`; artifact `9552426114`.
- Exact combined: retained `891`; pruned `93`; selected/rendered `1214/1209`; drops `5`; measures `113/113`; combined primary MIDI64 `234`.
- No invented pitch, invalid/unplayable primary, unobserved attack/pitch, relocation, new inference, or new threshold.
- `referenceFree=true`, `professionalReferenceUsed=false`, `modalInvoked=false`, `productionModified=false`.
- V5 remains **not freeze-ready** because technique/sustain has not been recomputed for the 166 rescued attacks.

## V5 voicing feasibility — passed
- Resolver contract: standard tuning open MIDI high-to-low `(64,59,55,50,45,40)`, max fret `24`, hard MIDI span `<=28`, unique/order-valid strings.
- Audit `analyzer/v143_contextual_prune_voicing_feasibility_audit.py`; passing run `32819559047`, job `97714646838`; SHA256 `b86e18609793095887324dbafad8d7940f275bb3cd60a0d0feb67de9e3c2c85a`.
- Durable `debug/v143-contextual-prune/voicing-feasibility-audit.json`, commit `bbe3ff799096303dc196654cf1a7637707fdc8d8`.
- Five V5 drops fully explained without changing pitch identity:
  - m19/s6 `[52,86] -> [52]`: physically assignable, span `34` > 28.
  - m40/s14 `[40,78] -> [40]`: physically assignable, span `38` > 28.
  - m63/s14 `[47,78] -> [78]`: physically assignable, span `31` > 28.
  - m113/s13 `[41,43] -> [41]`: unavoidable low-E same-string collision.
  - m113/s14 `[43,44] -> [43]`: unavoidable low-E same-string collision.
- Do not relax the resolver cap merely to force these through.

## Professional PDF renderer — ACTIVE WORK
- User explicitly asked to make the result a professional-level guitar-tab PDF.
- `lib/createV143RhythmPdf.js` was substantially upgraded on commit `08ee3bcc1cec3428641741a8281206aa4218cb8d` **without touching analyzer/pitch/timing evidence**.
- New layout direction:
  - clean sheet-music style DadRock header instead of large generator marketing header;
  - 3 measures/system for materially better 16th-note and two-digit fret spacing;
  - vertical TAB mark + real barlines + compact measure numbers;
  - rehearsal-mark boxes from reference-free section boundaries;
  - rhythm stems and beat-local eighth/16th beaming tied to actual `durationSteps`;
  - palm-mute and let-ring dashed technique ranges;
  - graphical bend arrows/release arrows and bend amount labels rather than long packed tokens;
  - actual slide lines and cleaner hammer/pull connectors;
  - vibrato zig-zag graphics, sustain lines, natural/pinch harmonic/dead-note handling;
  - compact continuation headers, deterministic PDF metadata, professional footer/page numbering;
  - full timing debug grid removed from the visual surface; only tiny beat ticks remain.
- Renderer import changed from Next-only alias to relative `./v143RenderContract.js`, preserving Next compatibility while allowing direct CPU fixture rendering.
- Synthetic professional engraving fixture added at `scripts/v143-professional-pdf-fixture.mjs`, commit `2c59c88e5d4c10617b2d739404cf65195c10f11f`; it exercises chords, 16ths, PM, let-ring, bends, bend-release, hammer/pull, slides, vibrato, harmonics, dead notes, tap and trill.
- Visual test workflow `.github/workflows/v143-professional-pdf-fixture.yml` added on commit `b321eab4468f35e63e01feb8d7ab6bdd527419d1`.
- First visual run `32820456852` did **not** execute the renderer because repository `yarn.lock` is stale under `--frozen-lockfile`; protected runtime identity guard passed. This is an infrastructure-only failure, not a renderer result.
- Workflow switched to repository `package-lock.json` + `npm ci` on commit `1fb58ec9fab9079ace9ea7c89e3d461c2ed7f563`; rerun `32820532320` is currently in progress.
- No Modal/L4, professional reference, Production change, or analyzer mutation occurred in this PDF work.

## Current integrity
- Branch head at this checkpoint: `1fb58ec9fab9079ace9ea7c89e3d461c2ed7f563`.
- Protected runtime was reverified exact blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1` by visual-test run `32820456852` before its dependency-install failure.
- No Production/main change; no professional scorer/reference; no freeze-ready transcription candidate yet.

## Next exact actions
1. Finish rerun `32820532320`; persist fixture PDF + page-1 PNG, visually inspect the rendered page, and iterate typography/spacing/technique graphics until it looks like commercial-quality guitar tablature.
2. Add a build compatibility check after the direct renderer fixture passes.
3. Recover per-string/per-fret electric TabCNN evidence for the three physically assignable wide-span drops m19/s6, m40/s14, m63/s14; use pairwise/argmax evidence only, no new threshold or pitch invention.
4. Resolve downstream technique/sustain evidence for all `166` rescued attacks before freeze/professional scoring.
5. Keep timing/tempo, Attack V3 criteria, and Primary V4 criteria frozen unless new source-only evidence proves a defect.
6. Do not force m113 same-string collisions into simultaneous voicings.
7. Remove temporary CPU workflows after durable evidence is secured.
8. No Modal/L4 without fresh explicit authorization.
9. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, PDF fidelity=1.0.
