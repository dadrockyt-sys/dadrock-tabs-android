# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-17 America/Toronto — successor metadata search 16 recorded; RWC J007/J009/J010 public identities locked; older Benetos/Dixon hand-edited J007/J009 ground truth elevated as the highest-value file hunt.
Branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

Status: **METADATA/PROVENANCE SEARCH CONTINUES — NO ELIGIBLE UNTOUCHED SUCCESSOR CORPUS SELECTED; NO SUCCESSOR PRE OR RUN AUTHORIZED; REAL CORRECTNESS UNKNOWN**

## HARD SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- **Do not resume archived V143/Gomyway unless the user explicitly asks.**
- `songsterr_pipeline/**` remains read-only for this research line.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Never rewrite, soften or reinterpret frozen historical FAIL/C/PASS results.
- Closed/exposed corpus families remain closed unless explicitly reopened; do not recycle them as “untouched.”

## GLOBAL AUTHORIZATION

Current successor execution authority is **none**.

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

The prior EGSet12 PRE authorization was consumed by authoritative run `35176277018` / job `105058572244`. Current continue/search instructions authorize metadata/provenance research only. Any alternate-corpus correctness execution requires a new exact PRE and fresh post-freeze authorization.

## FROZEN CANDIDATE — UNCHANGED

Final candidate remains exactly `S AND E AND O AND K`.

Authority:
- positive-core PRE `b7cfc43b6bd7e80d9a05694b37d332f1ef540696`;
- composer commit `5683830ebd0573b902bf205fe972a540fbaf37a9`, blob `6174a95c14a58ddd4dca47f021e591ebee8ee736`;
- result `99b37c2875a1c2551418fc8422ae4c302bf17eae`;
- run `35121000102`, job `104878449999`, artifact `10457970208`;
- label `PASS_MECHANICAL_FAIL_CLOSED_POSITIVE_CORE / NO_REAL_CORRECTNESS`.

State mapping remains fail-closed: all `S,E,O,K` true -> `corroborated`; resolved required predicate rejection -> `rejected`; unresolved/missing/malformed/nonfinite required predicate -> `insufficient` / abstention.

Forbidden: raw `0.01`, rank/top-K, weighted score, maximum-only rule, candidate subset chosen from results, candidate-confidence rescue, reattack fallback, threshold sweep, post-hoc rescue, predicate substitution/candidate rewrite, majority vote, per-MIDI exceptions.

KKT authority remains PRE `4ea9c075ea02231206a7602457e028b65c2e7a9e`, module commit `7020dc21d1cbcc89597f24511bd40bd37b4c9f60`, blob `2daa9f7f6983a3ec894fc08a86e9bced7b1f96c4`, result `cfe72ac6fb2459166a25cdd0789a59d257c846d1`, run `35119500201`, job `104873352558`, artifact `10456247666`.

Prepared historical Basic Pitch identity remains Python `3.10.21`, NumPy `1.26.4`, SciPy `1.15.3`, `tflite-runtime==2.14.0`, `basic-pitch==0.4.0`, transcriber blob `e9137496363f14cbe6194e32304c8b17b0b6569c`, MIDI 40..88, onset 0.5, frame 0.3, minimum note length 127.7 ms, `multiple_pitch_bends=False`, `melodia_trick=True`. Frozen V2 audio loader blob remains `f9bef389f848c8f003ffa844b1eb2eea5754002d`; V6 DSP blob remains `2b18ef0ee710a6ad5ecb27253b977495db7d6534` at 44.1 kHz / FFT 8192.

## EGSET12 — CONSUMED / NO RERUN

- PRE commit `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a`.
- Result commit `1d3192adce476110c1bfa12658590e2e179d0a04`.
- Run `35176277018`, job `105058572244`, artifact `10478985810`.
- Status **`BLOCKED_UNTOUCHED_LINEAGE_PROVENANCE / REAL_EVALUATION_NOT_EXECUTED`**.
- Prior exposure includes `9c0ad09436f74b6168043a2e779b25fb3922199b`; no correctness evidence exists and the consumed PRE must not be rerun/rescued.

## GAPS — PROVENANCE FAILED / NO RERUN

- Workflow/head `80eeaa05c0a063bb193a315b0c2e1aa81041e093`.
- Run `35177384414`, job `105061966125`, artifact `10479606030`.
- Result commit `e4eb3530e4a13e060135e92adddadfbe812a7f03`.
- Status **`FAIL_PRIOR_LINEAGE_EXPOSURE / NO_CORPUS_MEDIA_OPENED`**.
- Material prior-lineage hits include `9a20dcde71f954d4a1704dfca2985e91366f8cc6` and `e110d90c5f8761a4c1fd27af06fc018bc2dec24a`.

## SUCCESSOR SEARCH LEDGER

1. `SONGSTERR_FRESH_SUCCESSOR_CORPUS_METADATA_SEARCH_2026-09-16.md` — `9e92faee8b650449d67042732f05f00739f0778a`.
2. `...CONTINUED_2026-09-16.md` — `35e9f786935dddd6e9960b7b98c96497e129112d`.
3. `...CONTINUED_2_2026-09-16.md` — `54e3008a79eeec42093b007595f6b23e28d66cde`.
4. `...CONTINUED_3_2026-09-16.md` — `eb82c2e519da2215b10dbc000ed33def70f76920`.
5. `...CONTINUED_4_2026-09-16.md` — `9ad31c9aec5359d9d1163e6c99c1efbb5427c02c`.
6. `...CONTINUED_5_2026-09-17.md` — `55dd29a3ccc3b1528a5eef6a7485e60cfe01ebd1`.
7. `...CONTINUED_6_2026-09-17.md` — `2a639cdea2e6a4402932dd83dbc46854c236e8ad`.
8. `...CONTINUED_7_2026-09-17.md` — `7e2083ebf158e064688378d18cea5b37b0e5d6b7`.
9. `...CONTINUED_8_2026-09-17.md` — `1013fe6e4c6209b716bcb3b5d0e2073b24ebcd57`.
10. `...CONTINUED_9_2026-09-17.md` — `fba68582e7ebd7f64dfd2316006d64029682b997`.
11. `...CONTINUED_10_2026-09-17.md` — `076d6fe2ece97b9d09aed3ef0d5070fb7efeb37a`.
12. `...CONTINUED_11_2026-09-17.md` — `8428b57412b089bb1d3f36bbcb290a342abb32c4`.
13. `...CONTINUED_12_2026-09-17.md` — `1a05c498d353682e9d7e15d302047bdfc5a06677`.
14. `...CONTINUED_13_2026-09-17.md` — `aca75bc58510de5f8b643cdc9747a26287998b6b`.
15. `...CONTINUED_14_2026-09-17.md` — `ef803893d2482d2719eaa1a22cde98cfa17155f9`.
16. `...CONTINUED_15_2026-09-17.md` — `24b207a5bae006c21fa306b5a6096840e84149c4`.

## CURRENT EVALUATION-CANDIDATE STATUSES

### RWC 2.0 Jazz guitar solos — strongest public scrapeable lead

RWC 2.0 provides public audio and aligned MIDI under CC BY-NC 4.0.

Stable identities:
- Jazz audio Zenodo `10.5281/zenodo.18656623`, v2, `RWC-J.zip`, MD5 `c5d7d989e1afb8257ec50a3696d90c37`.
- Annotation repository `rwc-music/rwc-annotations`, CC BY-NC 4.0; repository head observed in Search 16 `0a1a6c31dbe73a7f5d44f7caef8cd0999402a4c2`.
- `RWC_J007.mid`: blob `fcc51bc1e0eaa6ef1c22be45a15b04e81b31353c`, 12814 bytes.
- `RWC_J009.mid`: blob `c983338f9d95d1bf91b3e8e2389708fa9d50bafd`, 10707 bytes.
- `RWC_J010.mid`: blob `9ea85986d63af889ce2ebcd35fd084b831f410b9`, 7268 bytes.
- Guitar-only Jazz tracks `RWC_J006`–`RWC_J010` are identified in public metadata.
- Pitch content originates in professional human transcription; later AIST MIDI was manually aligned, and the 2026 release was re-aligned with SyncToolbox plus human listening verification.

Track-level public QC changes the candidate subset prospectively:
- `J006`: **exclude** — maintainer issue #258 explicitly says warping improved but onsets are not matching.
- `J008`: **hold unresolved** — listed for `check` in the public issue.
- `J007`, `J009`, `J010`: strongest remaining public guitar-only candidates; not listed in the inspected problem table, but that absence is not affirmative perfect-onset proof.

The 2026 paper also explicitly states that some note-level missing/incorrect/additional-note discrepancies can remain and that systematic quantitative note-level evaluation is future work. The current timing can include algorithmic audio–MIDI warping rather than independent per-note manual onset placement.

Current status:
**`RWC_J007/J009/J010 = STRONGEST_PUBLIC_SCRAPEABLE_CANDIDATES / RIGHTS_AND_FILE_IDENTITY_CLEAR / HUMAN_TRANSCRIBED_PITCH_TRUTH / CURRENT_PER_NOTE_ONSET_AUTHORITY_NOT_YET_STRONG_ENOUGH_FOR_PRE / FULL_HISTORY_PROVENANCE_NOT_YET_PROVEN`**.

No RWC MIDI/audio payload was opened.

### Older Benetos/Dixon RWC manual ground truth — highest-value file hunt

Primary transcription literature documents a stronger historical reference artifact. The test set identifies RWC Jazz No. 6, 7, 8 and 9 as guitar. The authors state that the supplied MIDI had note errors/omissions and unrealistic durations, so aligned ground-truth MIDI was created for the **first 23 seconds** of each recording using **Sonic Visualiser for spectrogram visualization and MIDI editing**. Evaluation used this ground truth at a 10 ms time scale.

For this project, J007 and J009 are especially valuable because they overlap the strongest current public guitar-only candidates while providing substantially stronger documented manual ground-truth semantics than the modern automatically re-warped MIDI.

The actual hand-edited 23-second GT MIDI files have **not** been located in a stable public release or mirror yet, and rights for those derived GT artifacts are not established merely by publication of the papers.

Status:
**`TECHNICALLY_STRONG_MANUAL_23S_GUITAR_GT / EXACT_PUBLIC_GT_FILE_NOT_LOCATED / RIGHTS_FOR_DERIVED_GT_NOT_YET_ESTABLISHED / NOT_PRE_READY`**.

### Arty

Primary MIT thesis metadata documents dry/direct electric guitar with note events containing integer MIDI pitch plus absolute onset/offset, where timing was hand-annotated from the audio in Sonic Visualizer and combined with MusicXML pitch/technique metadata. Reference independence and note-event semantics appear technically acceptable.

Status:
**`TECHNICALLY_PROMISING_REFERENCE / UNRESOLVED_STABLE_PUBLIC_RELEASE_AND_DATASET_RIGHTS / NOT_PRE_READY`**.

No Arty payload was opened.

### GM Dataset

Actual-audio synchronization/timing/content correction is documented and no AMT label generator is documented, but no authoritative stable public package/version/file manifest or dataset-specific rights basis has been found.

Status:
**`UNRESOLVED_STABLE_PUBLIC_RELEASE_AND_DATASET_RIGHTS / REFERENCE_ALIGNMENT_POTENTIALLY_ACCEPTABLE_FROM_METADATA / NOT_PRE_READY`**.

## SCRAPEABLE AUXILIARY DATA

### RWC Instrument Sound 2.0

Public 2026 Zenodo release `10.5281/zenodo.17170844`, v1, CC BY-NC 4.0; `RWC-I.zip` MD5 `fb5789335fe68abdc09929618e9f0403`. Includes classical, steel-string acoustic, and electric guitar families. Public documentation says individual sounds are generally recorded in ascending pitch order and stringed-instrument ranges are recorded per string.

Potentially valuable for isolated-note diagnostics. However, the repeated per-string structure means event-to-MIDI mapping must not be guessed from a single global chromatic sequence.

Status:
**`AUXILIARY_HIGH_VALUE_PUBLIC_REAL_GUITAR_NOTES / EXACT_PER_EVENT_PITCH_ORDER_MAPPING_NOT_YET_PROVEN`**.

### MINST

Repository `ejhumphrey/minst-dataset`, inspected at commit `5847ac421522a393df77ca2a43acdc326f7d64e8`.

- README describes automatic high-recall onset initialization followed by visual human verification/correction; GUI supports add/remove/move onset markers at 10 ms resolution.
- README reports 5,618 RWC guitar notes.
- `data/onsets/rwc/` contains committed onset CSVs as immutable Git blobs.
- Guitar source categories include flamenco, nylon-string and steel-string guitar.
- Current RWC split code carries onset into the observation but does **not** carry `note_number`/pitch; the generated advertised final annotations table is not committed at its documented path.

Status:
**`AUXILIARY_HIGH_VALUE_PUBLIC_HUMAN_VERIFIABLE/CORRECTABLE_RWC_ONSETS / PITCH_NOT_CARRIED_IN_CURRENT_RWC_SPLIT_PIPELINE / NOT_EVALUATION_TRUTH_YET`**.

Do not open onset CSV contents under the current no-payload boundary.

### Virtuoso Strings

Public metadata reports 746 tracks and 68,728 onset annotations generated with a semi-automatic process plus human quality control. The surfaced material does not establish a qualifying guitar population or integer-MIDI pitch identity paired to the onset events.

Status:
**`AUXILIARY_ONSET_DATA / NO_QUALIFYING_GUITAR_PLUS_INTEGER_MIDI_REFERENCE_ESTABLISHED`**.

### GuitarSet Hugging Face mirror — tooling/schema only

A current public mirror exposes note rows shaped like `{onset_s, offset_s, midi, string}` through the dataset viewer, which is potentially useful for parser/schema fixtures without local audio download. GuitarSet remains a closed/exposed historical family in this project and must not be reused as untouched correctness evidence.

Status:
**`SCRAPEABLE_SCHEMA_FIXTURE_ONLY / CLOSED_EXPOSED_FOR_CORRECTNESS`**.

### MedleyDB

Public guitar stems and human-verified continuous/framewise f0 are useful for diagnostics; activation boundaries are not authoritative discrete note births.

Status:
**`AUXILIARY_USEFUL_PUBLIC_GUITAR_F0_STEMS / NOT_EVAL_TRUTH_DUE_NO_DISCRETE_NOTE_BIRTH_INTEGER_MIDI`**.

### TapToTab

Manual pitch labels for isolated guitar recordings but no authoritative actual performed onset timestamps.

Status:
**`AUXILIARY_PITCH_USEFUL / REJECT_NO_AUTHORITATIVE_ACTUAL_NOTE_BIRTH_TIMESTAMPS_FOR_EVALUATION`**.

## REJECTED / CLOSED IMPORTANT LEADS

- GIHME — Aubio/YIN-derived reference before manual verification; no stable public corpus release.
- MMIP — guitar MIDI from NeuralNote/Basic Pitch audio-to-MIDI.
- DoMP — Fishman TriplePlay MIDI tracking.
- DoPP — no verified exact performed note-birth + integer-MIDI truth.
- HF `collegefishiesd/guitar-fretboard-notes` — pitch/string/fret labels but no authoritative actual onset timestamps.
- Oslo multimodal guitar — synchronized signals but no exact onset+MIDI reference.
- Manchester AI guitar assistant — no stable public exact note-event corpus.
- Fretiq — string labels; pitch is audio-estimated.
- MAAL — segment/loop annotations, not note events.
- Let’s Frets!, NIME physical sensing, Guaus capacitive, Pesatori/Norgia laser — promising direct-sensing mechanisms but no qualifying public synchronized corpus.
- 2019 optical motion-capture guitar — note pitch/onsets derived from audio.
- MUSERC — non-guitar.
- Physically augmented robot guitar chord dataset — chord labels, not exact per-note events.
- Closed/exposed GuitarSet, GAPS, IDMT, FLGD/Leduc, Guitar-TECHS, EG-IPT, AG-PT, EGDB, GOAT, EGSet12 and related historical lines remain closed and were not reopened.

## CURRENT TECHNICAL CONCLUSION

The frozen candidate still lacks an untouched external real-corpus correctness measurement. **Real correctness remains unknown.**

RWC J007/J009/J010 remain the strongest **fully public scrapeable** guitar candidates because source identity, rights, population and human-transcribed pitch truth are clear. However, the current RWC 2.0 MIDI is no longer treated as having proven exact per-note onset authority: its timing includes automated synchronization/warping followed by listening verification, and the authors acknowledge remaining note-level discrepancies.

The highest-value next artifact is therefore the older Benetos/Dixon **hand-edited 23-second RWC guitar ground truth**, especially J007 and J009. Its documented annotation semantics are stronger, but the actual GT files and their reusable rights have not yet been found.

Arty remains technically strong in documented manual-onset semantics but weak in public availability/rights. MINST/RWC-I add useful scrapeable diagnostics but do not yet expose a proven onset-to-integer-MIDI mapping suitable for correctness evaluation.

Across all searches: successor media opened `0`; successor annotation payloads opened `0`; model runs `0`; correctness scores `0`; candidate/threshold changes `0`; V143/Gomyway activity `0`.

## NEXT RESEARCH BOUNDARY

Continue **metadata/provenance-only discovery**:

1. Search archives, author pages, QMUL/City repositories, supplementary material, old project/code pages and legitimate mirrors for the Benetos/Dixon hand-edited 23-second RWC guitar GT MIDI files, prioritizing J007 and J009.
2. Search RWC public alignment/QC metadata, issues, PRs and history for affirmative track-level evidence about J007/J009/J010 without opening MIDI/audio payloads.
3. Search for another public real-guitar corpus with stable rights and manually/directly/symbolically authored per-note onset + integer-MIDI truth independent of AMT.
4. Investigate whether RWC Instrument Sound exposes an authoritative per-file/per-string event-order/pitch manifest that can pair MINST corrected onsets with integer MIDI without audio pitch estimation.
5. Continue Arty/GM public-release watch.
6. Before any real candidate payload access, complete a true full-history provenance audit; default-branch and commit-message searches are not enough.
7. If a candidate clears source/version/file identity, rights, population, exact independent reference and clean provenance gates, freeze a new exact prospective PRE for unchanged `S AND E AND O AND K`, update this checkpoint to the exact PRE commit, then **STOP for fresh post-freeze user authorization** before opening/downloading media or annotations or running Basic Pitch/qualification/scoring.

## FRESH CHAT RESUME POINT

- Latest search checkpoint: `docs/checkpoints/SONGSTERR_FRESH_SUCCESSOR_CORPUS_METADATA_SEARCH_CONTINUED_15_2026-09-17.md`, commit `24b207a5bae006c21fa306b5a6096840e84149c4`.
- No successor selected; no successor PRE exists; no successor run is authorized.
- RWC J007/J009/J010 remain the strongest current **fully public scrapeable** candidates, but current RWC 2.0 per-note onset authority is not yet strong enough for PRE.
- Exact current public MIDI blobs: J007 `fcc51bc1e0eaa6ef1c22be45a15b04e81b31353c`; J009 `c983338f9d95d1bf91b3e8e2389708fa9d50bafd`; J010 `9ea85986d63af889ce2ebcd35fd084b831f410b9`.
- The Benetos/Dixon hand-edited 23-second J007/J009 GT is the highest-value file hunt; artifact existence is documented but files/rights remain unresolved.
- Arty has strong manual-onset semantics but no public immutable package/license.
- MINST/RWC-I are high-value auxiliary scrapeable data; exact pitch-event mapping remains unresolved.
- No successor payload has been opened.
- Full-history provenance remains unresolved; commit-message search is not treated as proof.
- Archived V143/Gomyway remains untouched.

## DO NOT DO

- Do not resume V143/Gomyway.
- Do not switch Production or `main`.
- Do not weaken EGSet12/GAPS provenance outcomes.
- Do not silently substitute another corpus under PRE `2a2ed0...`.
- Do not reopen closed/exposed corpus families as untouched.
- Do not use AMT/pitch-tracker output as authoritative independent correctness truth.
- Do not convert clip labels, pattern labels, chord labels, string classes, downbeats, framewise f0, or gesture streams into exact note-birth truth without authoritative event semantics.
- Do not choose an RWC track based on model/correctness results; all track exclusions/inclusions must remain prospective from source/QC metadata.
- Do not equate the modern RWC 2.0 automatically re-aligned MIDI with the older Benetos/Dixon manually edited 23-second GT unless file identity/provenance proves equivalence.
- Do not guess RWC Instrument Sound pitch order from counts or global range.
- Do not open RWC/Arty/MINST successor annotation or audio payloads before a new PRE plus fresh post-freeze authorization.
- Do not alter frozen V6/V3/V7/KKT/positive-core logic in place.

Archived V143/Gomyway remains untouched.