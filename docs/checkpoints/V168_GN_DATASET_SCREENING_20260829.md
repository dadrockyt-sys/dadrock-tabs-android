# V168 — G&N electric-guitar dataset screening

Date: 2026-08-29 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **PROMISING REFERENCE PROVENANCE / BLOCKED ON SOURCE+REFERENCE ACQUISITION AND USE BASIS / NOT ADMITTED / SCORING NOT ARMED**

## Safety boundary
Metadata/provenance screening only. No G&N source-audio bytes or professional-reference note-event bytes were acquired or opened. No candidate generation was implemented. No scorer/reference-facing evaluation occurred. V168 reference-facing score calls remain **0**. CPU only. `main`/Production untouched.

## Candidate identity
The G&N dataset is described in:

Ting-Wei Su, Yuan-Ping Chen, Li Su, Yi-Hsuan Yang (2019), **TENT: Technique-Embedded Note Tracking for Real-World Guitar Solo Recordings**, Transactions of the International Society for Music Information Retrieval, DOI `10.5334/tismir.23`.

The source recording material comes from the companion audio to:

Danny Gill & Nick Nolan (1997), **Rock Lead Basics: Master Class Series**, Musicians Institute Press / Hal Leonard, ISBN `9780793573783`.

## Professional-reference provenance — STRONG
The TENT paper states that G&N contains:
- 42 unaccompanied monophonic electric-guitar solo tracks;
- 20–40 seconds each, 19:31 total;
- 1,113 note events;
- clean-tone and distortion electric-guitar recordings.

Most importantly for the frozen V168 reference gate, the paper states:
- timestamps of **all note events** and involved playing techniques were **carefully annotated by an experienced electric-guitar player** (the paper's second author);
- the annotator used the guitar tablatures supplied by the book;
- the labels were then **checked by another electric-guitar player** (the first author) to make sure every label was correct.

This is substantially stronger professional/human annotation provenance than most public guitar AMT datasets screened so far and is not described as model-derived ground truth.

## Source-audio acquisition/use basis — MATERIAL BLOCKER
The exact audio is not an original open research recording corpus. It is companion material from the commercial *Rock Lead Basics* instructional publication.

Current commercial listings still identify the title as a Musicians Institute/Hal Leonard product and describe access to more than 75 full demonstration tracks through publisher-controlled online audio/access-code mechanisms.

The TENT article's CC BY 4.0 publication license applies to the article, not automatically to the textbook/CD audio or to any separately created dataset annotations.

No authoritative public research-use license or redistribution/use grant for the exact commercial source recordings was found in this screening.

Therefore a purchased book/CD or access code must **not** be treated as permission to ingest the audio into V168 merely by assumption. Before admission, the project would need a clear lawful research-use basis for the exact source bytes consistent with the frozen manifest's `rightsOrUseBasis` field.

## Public SoloLa repository inspection
TENT points to `srviest/SoloLa` for reproducibility.

Metadata-only inspection of the public repository shows:
- code, trained model artifacts, output files, and `answers/*.answer` files;
- **no source `.wav` files** in the inspected recursive tree;
- **no repository `LICENSE` file** in the inspected recursive tree;
- README describes the SoloLa system and requirements but does not publish a G&N dataset license or an authorized source-audio acquisition route.

The presence of `answers/*.answer` files is not enough to admit a professional reference: without a frozen explicit dataset/license statement, exact track-to-source binding, and source-audio identity, they cannot prospectively be relabeled as an admissible professional reference merely from filenames.

No answer/note-event file content was opened in this screening.

## Frozen-gate assessment
### Positive
- 42 real electric-guitar solo tracks;
- independent track-level evaluation units;
- strong, explicit experienced-player annotation provenance;
- independent second-player label checking;
- ground truth is not described as model-derived;
- note timestamps and pitches were used for note-tracking evaluation in the publication.

### Blocking
- exact source audio originates from a commercial instructional publication;
- no frozen public research-use grant for those source bytes was found;
- the public reproducibility repository does not provide the source audio;
- no repository license was found;
- exact reference annotation distribution/use terms and source/reference SHA256 bindings are not available/frozen;
- no actual assets have passed either V168 validator.

## Decision
**G&N is `PROMISING / BLOCKED / NOT ADMITTED`.**

Its reference provenance is strong enough to keep it as a serious fallback lead, but it cannot enter V168 unless the exact source audio and corresponding author-created annotations can be lawfully acquired under a frozen research-use basis and then hash-bound prospectively.

Do not purchase/rip/copy publisher audio and call that an admission path without reviewing the actual permitted use. Do not treat the CC BY article license as a dataset license.

## Next boundary
1. Keep GOAT as the primary acquisition lead because its dataset record explicitly offers a research-access request path, even though access has not yet been granted.
2. Keep G&N as a secondary provenance-strong lead only if a legitimate rights/use path for both exact source audio and annotations can be established.
3. Continue searching for an openly obtainable dataset with G&N-level human/professional annotation provenance plus an explicit research-use source-audio license; do not weaken any frozen gate.
4. No candidate generation, reference conversion, or generic scorer adapter until a complete >=2-song manifest passes both frozen validators.
5. V168 remains `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; reference-facing score calls remain **0**.
