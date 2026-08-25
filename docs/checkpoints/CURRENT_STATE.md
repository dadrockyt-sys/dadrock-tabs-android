# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; produce genuinely professional guitar tablature, not merely a polished-looking PDF.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved audio SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. No runtime/shadow tuning or selection from it.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 without fresh explicit user authorization. None is currently authorized.**
- Timing frozen unless new source-only evidence proves otherwise; tempo exactly `129.19921875`.

## Preserved capture / baseline
- Authorized historical run `32805316807`; pinned capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`.
- Baseline: eligible `984`; retained attacks `725`; selected pitches `970`; rendered events `967`; voicing drops `3`; measures `1-113`.
- Candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Durable manifest `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json`; CPU materializer `analyzer/materialize_v143_precision_fixture.py`.

## Independent guitar evidence
- Exact approved source `public/gomywayfullaitest.m4a` verified SHA; no Modal needed.
- Robust electric TabCNN checkpoint SHA256 `1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c`; exact-audio evidence `debug/v143-contextual-prune/electric-tabcnn-v3-consensus-evidence.json`.
- Use only as independent positive consensus, never blind replacement.

## Attack V3 — strongest attack shadow
- Baseline `725` + exception-band `123` + electric-consensus subfloor `43` = **`891` retained**.
- Durable validation `debug/v143-contextual-prune/attack-shadow-v3-replay-validation.json`, commit `8c1a36f2254197adabc1ed1e1ef65ba62853d073`, SHA256 `039a42d06abdc60a111cd85f0db9ac07b81caf1c1d91fd65e260ffb6119b1892`.
- Exact: selected/rendered `1214/1209`; drops `5`; measures `113/113`; no invented/unplayable/invalid pitch.
- `freezeReady=false`: 166 rescued attacks lack recomputed downstream technique/sustain.

## Primary V4 — strongest primary correction
- 34 lower-primary corrections accepted only where exact electric model pairwise favors new lower primary over old upper primary; no new scalar threshold.
- Durable validation `debug/v143-contextual-prune/contextual-harmonic-primary-shadow-v4-validation.json`, commit `a742a3df5b468ee54b6fadf72c0f111b8c824424`, SHA256 `7eea032a2bdc12fcb0d5e0c4693bdc7a6ea06db447d1a28c0044192e724cad99`.
- Baseline after V4 remains selected/rendered `970/967`, drops `3`.

## Combined Content V5 — CURRENT STRONGEST MUSICAL CONTENT SHADOW
- Attack V3 + validated Primary V4; all 34 V4 corrections touch baseline attacks only.
- Durable validation `debug/v143-contextual-prune/combined-content-shadow-v5-validation.json`, commit `b0dce933d8686d0dbd1c1a7da78460053a71739f`, SHA256 `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- Exact: retained attacks `891`; selected/rendered `1214/1209`; drops `5`; measures `113/113`; no invented pitch, invalid/unplayable primary, unobserved attack/pitch, relocation, new inference, or new threshold.
- `referenceFree=true`, `professionalReferenceUsed=false`, `modalInvoked=false`, `productionModified=false`.
- V5 remains **not freeze-ready** because technique/sustain has not been recomputed for rescued attacks.

## V5 voicing feasibility
- Five drops fully explained: 3 physically assignable but over resolver 28-semitone span (m19/s6 `[52,86]`, m40/s14 `[40,78]`, m63/s14 `[47,78]`); 2 unavoidable low-E same-string collisions (m113/s13 `[41,43]`, m113/s14 `[43,44]`).
- Do not relax the resolver merely to force them through.

## Professional PDF renderer — substantial upgrade complete
- `lib/createV143RhythmPdf.js` upgraded at commit `08ee3bcc1cec3428641741a8281206aa4218cb8d` without changing analyzer/pitch/timing evidence.
- New engraving: clean sheet-style header, 3 measures/system, TAB mark/barlines/measure numbers, rehearsal marks, rhythm stems + beat-local beaming, graphical slides/hammer/pull/bends/vibrato/sustain, technique lanes, compact continuation headers, professional footer/page numbering, and removal of full debug timing grid.
- Synthetic fixture `scripts/v143-professional-pdf-fixture.mjs`; successful visual run `32820654412`, bot commit `a5655d56df411cd3011c42807dc9119019b9858d`. Visual inspection: no clipping/broken glyphs; major commercial-quality improvement. Synthetic PM/let-ring ranges can still be visually consolidated if those techniques become present in final content.

## Real preserved 113-measure PDF render — PASSED
- Real candidate schema inspection run `32821063375`, job `97719080566`, bot commit `dc2c2ad...`: pinned product exposes a direct structured `events` array of **967** baseline render events with string/fret/measure/step/sustain/technique fields; no note reconstruction or guessing required.
- Real render script `scripts/v143-render-real-candidate-pdf.mjs` commit `4b3b958d181ea37fa26bb1e4a083b061e8700ae5`; summary-field fix `e4e7b62e8d600d08d8a8c3ca3a690cab4ddc8c55`.
- Workflow `.github/workflows/v143-render-real-candidate-pdf.yml` commit `abdebb07d1d1600efc8cdeb5cb1a89dfc09e53fb`.
- **Passing real render run `32821330353`, job `97719895086`.** Protected runtime guard passed; materializer reported Modal/L4 false and professional reference false.
- Exact render: source/projected events `967/967`; unique measures `113`; unique onsets `725`; max notes/populated measure `18`; max chord size `5`; multi-note onsets `209`; section count `8`; tempo `129.19921875`; E Standard; 4/4.
- PDF: **6 Letter pages**, 1,738,077 bytes, SHA256 `3b47dfa93b8ad05b7de94c6d51f65acc9fa2d9a05701e1daecb3cdf78c0c768f`.
- Durable render commit `2470225d9cb726e35a07459e29783997a3447699`: `debug/v143-contextual-prune/real-candidate-professional-pdf/` contains PDF, first/middle/last inspection PNGs, report, pdfinfo, and hashes. Artifact `9553226034`.
- Visual inspection of first/middle/last pages: no clipping, dense chords and two-digit frets readable, clean headers/rehearsal marks/barlines, good commercial-tab appearance. Last page has extra lower whitespace but is acceptable. Internal title `V143 Approved Rhythm Reference` is inspection-only and **not final customer-facing metadata**.
- Critical limitation: this successful real PDF renders the **baseline 967-event stream**, not strongest V5 `1209` rendered-note content. It proves the engraving renderer can carry a real 113-measure song professionally; it is not the final musical PDF.

## Current integrity
- Branch head before this checkpoint update: `2470225d9cb726e35a07459e29783997a3447699`.
- Protected runtime guard passed in successful real render run `32821330353`.
- No Production/main change; no professional scorer/reference; no new Modal/L4 usage.

## Next exact actions
1. Build a CPU-only **V5 render-stream materializer** from the immutable pinned product + durable Attack V3 + Primary V4 evidence, preserving existing baseline event metadata where identity matches and emitting only validated deterministic V5 string/fret content.
2. Render the V5 1209-note / 891-onset shadow through the proven professional PDF renderer; inspect first/middle/last pages and enforce exact content counts.
3. Clearly mark any V5 inspection PDF as a **reference-free shadow / not freeze-ready** because rescued attacks still lack recomputed technique/sustain; do not invent techniques or durations for them.
4. Then resolve downstream technique/sustain for all 166 rescued attacks before any freeze/professional scoring/final-customer PDF claim.
5. Preserve timing/tempo and Attack V3 / Primary V4 criteria unless source-only evidence proves a defect.
6. No Modal/L4 without fresh explicit authorization.
7. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, PDF fidelity=1.0.
