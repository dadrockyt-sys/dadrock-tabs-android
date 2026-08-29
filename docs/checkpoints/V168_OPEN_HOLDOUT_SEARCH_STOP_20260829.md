# V168 — Open professional holdout search stop

Date: 2026-08-29 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **OPEN SEARCH EXHAUSTED TO CURRENT PRACTICAL FRONTIER / EXTERNAL ACCESS OR NEW PROVENANCE REQUIRED / NO ASSETS ADMITTED / SCORING NOT ARMED**

## Purpose
Freeze a score-blind stopping point for the current public/open dataset search. This prevents repeated re-screening of the same unsuitable corpora and prevents weakening the already-frozen V168 professional-reference gate merely because a convenient open holdout has not been found.

## Safety boundary
- No V168 reference-facing score call occurred. Count remains **0**.
- No candidate generation was implemented or run.
- No generic/new-song scorer adapter was implemented or armed.
- No professional-reference note-event content was opened to select favorable tracks.
- No external source/reference asset was admitted.
- CPU-only authorization remained in force.
- `main` and Production were not modified.

## Search conclusion
Under the current frozen intake contract, the public/open search has reached diminishing returns. The recurring failure modes are:
1. isolated notes/chords/technique samples rather than independent song/piece streams;
2. model-, tracker-, pickup-, or alignment-derived references rather than independently established professional references;
3. strong human references paired with third-party/commercial audio lacking a frozen exact-source research-use basis;
4. open audio/reference packages whose professional annotation provenance is not documented strongly enough for `professional_scorer_ready`;
5. synthetic material, which is not professional holdout ground truth under the frozen contract.

The absence of an easy open candidate is **not** grounds to weaken `professional_scorer_ready`, `derivedFromModelOrCandidateOutput=false`, exact source/reference binding, reference blindness, or the >=2-song requirement.

## Primary path — GOAT remains strongest lead
GOAT remains the only currently screened lead that combines:
- real original electric-guitar recordings;
- song/piece-like tablature content;
- strong manual audio/tab verification described by the authors;
- a publisher-controlled **request-access path specifically for research purposes**.

It remains **NOT ADMITTED** because actual access has not been granted to this project and exact access/use terms plus source/reference bytes have not been frozen.

Public GOAT repository instructions explicitly direct researchers to request dataset access on Zenodo. The ISMIR paper states the dataset is distributed on Zenodo **by request to better control its use for research purposes only**.

### Prospective data-integrity warning — NOT an exclusion decision
A currently open public GitHub issue in `JackJamesLoth/GOAT-Dataset` reports possible duration/EOF mismatches for `item_67`, `item_96`, and `item_110`:
- `item_96` and `item_110`: reporter says DI/amp audio is roughly half the MIDI/GP duration;
- `item_67`: reporter says final note offsets extend slightly beyond audio EOF.

At this checkpoint there is no author reply on that issue. These are **third-party issue reports, not authoritative confirmed defects**.

If GOAT access is later granted, these reported items must be checked prospectively as a data-integrity preflight **before** any candidate/reference scoring. Any exclusion rule must be frozen from source/reference integrity criteria without comparative Policy A/B scores; do not drop adverse-result songs after scoring.

## Secondary path — G&N remains provenance-strong but rights-blocked
Dedicated checkpoint: `docs/checkpoints/V168_GN_DATASET_SCREENING_20260829.md`.

The G&N references have unusually strong professional/human provenance: an experienced electric-guitar player annotated all note events/techniques and a second electric-guitar player checked every label. However, the source audio comes from a commercial instructional publication, and no lawful stable research-use acquisition path for the exact source audio plus annotations has been frozen.

Therefore G&N remains **PROMISING / BLOCKED / NOT ADMITTED**. Purchasing or possessing publisher audio is not automatically a frozen V168 use grant.

## Additional public/open candidates — terminal fast triage

### Kaggle Guitar Transcription Dataset — EXCLUDED
Public Kaggle data card describes:
- 355 fretboard-segmentation image frames;
- 1,995 tablature image frames;
- per-frame finger press/fret/string labels;
- WAV files mapped to frame timestamps;
- creators played guitar and annotated the data;
- CC BY-NC-SA 4.0.

This is useful visual/fretboard supervision, but its ground truth is **frame-level finger/fret state**, not an independently established professional timing-aware note-event reference stream for complete guitar pieces. No professional annotator provenance was identified. It does not satisfy the current V168 reference semantics.

Decision: **EXCLUDED / NOT ADMITTED**.

### EGFxSet — EXCLUDED
Authoritative Zenodo record `10.5281/zenodo.7044411` contains recordings of all individual clean tones of a 22-fret Stratocaster across pickup configurations, with the clean notes then processed through guitar effects. The associated publication describes a professional guitarist playing all 138 possible notes.

Despite excellent real-hardware/professional-performance provenance, its unit is isolated single tones repeated across pickups/effects, not independent song/piece streams.

Decision: **EXCLUDED / WRONG EVALUATION UNIT**.

### GUITAR-FX-DIST — EXCLUDED
Zenodo releases contain processed versions of IDMT-SMT-Audio-Effects material. The underlying unprocessed corpus consists of short isolated monophonic notes and 2/3/4-note intervals/chords, then massively processed through distortion/overdrive/fuzz configurations.

This is an effects/audio-modeling corpus, not a >=2-song professional timing-aware note-event holdout.

Decision: **EXCLUDED / WRONG EVALUATION UNIT**.

### EG-IPT — EXCLUDED
Authoritative Zenodo description identifies 52,320 **monophonic isolated single-note performances** covering 19 electric-guitar techniques, performed by a professional guitarist. Strong performer provenance, wrong evaluation unit for V168 cross-song holdout.

Decision: **EXCLUDED / WRONG EVALUATION UNIT**.

## Previously frozen screened candidates
- **EGSet12:** BLOCKED — authors' evaluation code requires unpublished/unresolved `jams_corrected` provenance; do not substitute public JAMS by assumption.
- **IDMT-SMT-Guitar subset 3:** BLOCKED — later-added five song-like pieces lack sufficiently documented professional annotation/validation provenance under current gate.
- **EG-Solo:** BLOCKED — promising human tablature-assisted reference, but third-party YouTube popular-rock source recordings lack a frozen exact-source research-use basis.
- **EGDB real-world set:** BLOCKED — strong musician manual-reference statement, but public symbolic reference identity/use basis not frozen and source is third-party YouTube material.
- **GuitarSet:** NOT ADMITTED — labels substantially depend on automated monophonic pitch tracking from hex-string recordings and known annotation issues.
- **Guitar-TECHS:** NOT ADMITTED — synchronized instrument/MIDI-pickup labels are not independently established professional transcription references.
- **François Leduc:** EXCLUDED — released high-resolution MIDI alignment is transcription-model-assisted.
- **GAPS:** EXCLUDED — high-resolution alignment is algorithm/model-assisted before human correction under the current strict no-model-derived-reference gate.
- **AG-PT:** EXCLUDED — isolated monophonic technique-note material, not song/piece holdout.

## Important non-evidence
Third-party repositories or projects may document that they obtained private permission for a dataset. Such a grant applies to that recipient and **does not transfer to this project**. Do not treat somebody else's private author permission, local license posture, or use decision as DadRock's rights/use basis.

Likewise, public availability, a YouTube URL, a commercial purchase, a paper license, or a GitHub repository without explicit dataset terms does not by itself establish the exact-source `rightsOrUseBasis` required by the frozen V168 intake contract.

## Frozen stop decision
**Do not continue broad public dataset searching by default.** Resume open-candidate search only when one of the following occurs:
1. genuinely new dataset/provenance evidence appears that plausibly clears all frozen gates;
2. GOAT access is actually granted;
3. a lawful explicit G&N source+annotation research-use path is obtained;
4. another exact source/reference pair is user-supplied or licensed with professional scorer-ready provenance.

Until then:
- V168 remains `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`;
- reference-facing score calls remain **0**;
- no candidate-generation implementation should be staged;
- no generic V168 scorer adapter should be staged;
- no gate should be weakened;
- CPU only;
- `main`/Production untouched.

## Next actionable boundary
The next useful work is **external asset access/provenance**, not more model/scorer code:
1. obtain legitimate GOAT research access and preserve the exact grant/terms;
2. after access, freeze exact dataset version/bytes and run a score-blind integrity/provenance intake, including checking the unverified public issue reports before choosing/fixing the deterministic song set;
3. alternatively, obtain explicit lawful research-use rights and exact source/reference distribution for G&N or another professional set;
4. only after >=2 songs pass both frozen V168 validators may candidate generation be implemented.
