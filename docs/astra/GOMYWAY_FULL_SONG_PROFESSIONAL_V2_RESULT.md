# Go My Way Full-Song Three-Role Professional Benchmark V2 — Result

Date: 2026-10-03  
Branch: `astra-work`

## Purpose

Score the current untouched separator -> Basic Pitch path against the existing frozen professional Go My Way references for **rhythm, lead, and bass** across the full 113-measure song structure.

This is existing development material, not a sealed holdout.

## Authoritative scorer-ready references

Confirmed frozen V154 scorer-ready identities:

- Rhythm
  - `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json`
  - SHA-256: `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`
  - 113-measure reference contract
  - 603 events / **946 scored note rows**

- Lead
  - `research/v154-professional-references/scorer-ready/lead-scorer-ready.json`
  - SHA-256: `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`
  - 113-measure reference contract
  - 487 source events / **447 scored note rows**
  - frozen exclusions: measures **28, 39**

- Bass
  - `research/v154-professional-references/scorer-ready/bass-scorer-ready.json`
  - SHA-256: `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`
  - 113-measure reference contract
  - 569 source events / **547 scored note rows**
  - frozen exclusion: measure **88**

The rhythm equivalence audit confirms that the two final V154 rhythm scorer-ready representations are exact normalized multiset equivalents at **946 rows**. The older 971-row intro+17..113 development normalization is therefore not the canonical V154 scorer-ready rhythm bundle.

## Source audio

`public/gomywayfullaitest.m4a`

Repository Git blob:
`5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`

The successful workflow verifies that exact repository object before inference.

## Inference

Reference-blind:
- untouched BS-Roformer-SW 6-stem FP16 ONNX
- frozen Basic Pitch 0.4.0 defaults
- raw guitar stem
- raw bass stem
- whole-mix controls

No:
- threshold search
- audio cleanup
- consolidation
- role reassignment
- reference-conditioned inference
- `main` modification

## GitHub Actions evidence

Successful run:
`37096244645`

Head:
`15474cd6cdff2f9792950d72a02508915484e5cc`

Artifact:
- id: `11264986579`
- digest: `sha256:a8997135b0251aa8f4ed8f98b5c91650209f50840b9b6964b73b0e0f85b7e48f`

Runtime: **877.64 s**

## Fresh direct-time professional-reference score

Primary metric in this run:
- exact MIDI
- one-to-one onset match
- fixed **50 ms** tolerance
- reference rows projected to absolute audio time
- frozen uncertainty exclusions honored

### Rhythm — raw guitar stem

- predictions: **1023**
- targets: **946**
- TP: **56**
- FP: **967**
- FN: **890**
- precision: **5.47%**
- recall: **5.92%**
- F1: **5.69%**
- mean matched onset error: **24.64 ms**

Whole-mix rhythm F1: **3.04%**

Separator delta: approximately **+2.65 percentage points**.

### Lead — raw guitar stem

- predictions after frozen exclusions: **1005**
- targets: **447**
- TP: **45**
- FP: **960**
- FN: **402**
- precision: **4.48%**
- recall: **10.07%**
- F1: **6.20%**
- mean matched onset error: **27.39 ms**

Whole-mix lead F1: **1.00%**

Separator delta: approximately **+5.20 percentage points**.

### Combined rhythm + lead — raw guitar stem

- predictions: **1005**
- targets: **1393**
- TP: **96**
- FP: **909**
- FN: **1297**
- precision: **9.55%**
- recall: **6.89%**
- F1: **8.01%**
- mean matched onset error: **26.10 ms**

Whole-mix combined-guitar F1: **2.89%**.

This is the clearest current evidence that separation helps expose guitar note activity, even though absolute note transcription remains far from professional-tab accuracy.

### Bass — raw bass stem

- predictions: **686**
- targets: **547**
- TP: **50**
- FP: **636**
- FN: **497**
- precision: **7.29%**
- recall: **9.14%**
- F1: **8.11%**
- mean matched onset error: **22.04 ms**

Whole-mix bass F1: **9.05%**.

For this pipeline/transcriber, the raw bass separator output is slightly worse than the whole-mix control on exact MIDI/onset.

## Role-confusion diagnostics

- bass stem vs rhythm F1: **2.56%**
- bass stem vs lead F1: **0.18%**
- guitar stem vs bass F1: **1.66%**

The low cross-role scores indicate that the separated streams are not simply interchangeable, even though their desired-role transcription quality remains low.

## Canonical V154 scorer distinction

The repository also contains the frozen canonical V154 scorer:

`validation/v154_cpu_multitrack/score_frontend_reference.py`

Git blob:
`9644e65719fbd361a9b39778ae9950c5e983e855`

Its primary contract is **measure/step-space** exact MIDI matching within ±0.5 grid steps. That scorer is correct for a generated candidate that independently produces its own measure/step grid.

The current BS-Roformer + Basic Pitch benchmark produces raw absolute-time events only. Converting those timestamps into measure/step coordinates using the **professional-reference timing map** and then marking the candidate as `referenceRead=false` would be reference leakage.

Therefore this V2 result deliberately stays in absolute audio time. Do not silently rescore it through the V154 step scorer unless a reference-independent structure/grid stage first produces the candidate's measure/step coordinates.

For historical context only, an older independent V154 candidate already scored under the exact canonical step scorer at:
- combined guitar primary F1: **4.92%**
- bass primary F1: **11.17%**

Those numbers are not directly comparable to the V2 50 ms absolute-time scores because the candidate architecture and scoring coordinate contract differ.

## Interpretation

The professional 1–113 bundle confirms that the present bottleneck is not merely lack of reference coverage.

On this song:
1. separation substantially improves guitar evidence over the whole mix;
2. exact professional-tab MIDI/onset agreement is still only single-digit F1;
3. bass separation does not improve the frozen Basic Pitch result;
4. rhythm-vs-lead role separation is still absent because both are decoded from the same generic guitar stem;
5. a trustworthy end-to-end system still needs a reference-independent musical structure grid plus substantially stronger note recognition before string/fret/technique scoring becomes meaningful.

No production or automatic-correction action is authorized from this development benchmark.
