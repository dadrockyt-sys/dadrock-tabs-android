# Go My Way Full-Song Three-Role Professional Score V1

Date: 2026-10-03
Branch: `astra-work`

## Key recovery

A deeper Git-history provenance scan recovered the full machine-readable bass and lead reference system that had been stored under older V154 research paths:

- `research/v154-professional-references/bass-professional-reference-machine-readable.json`
- `research/v154-professional-references/bass-source-local-attack-timing.json`
- `research/v154-professional-references/lead-professional-reference-machine-readable.json`
- `research/v154-professional-references/lead-source-local-attack-timing.json`
- `research/v154-professional-references/source-meter-to-fixed-grid-mapping.json`

This confirmed the user's recollection: complete 1-113 professional source coverage exists for rhythm, bass, and lead.

Provenance recovery run:
`37094671478` - **success**

Artifact:
- id: `11262639696`
- digest: `sha256:3f64e1c493788502696d6516b11849290ea2a273531008ea9e1737893f288013`

## Frozen scorer coverage

- rhythm: **971** pitched scorer targets
- bass: **547** pitched scorer targets
- lead: **447** pitched scorer targets
- total: **1,965**

Bass timing audit:
- 569 source events
- 547 pitched scorer rows
- measure 88 unresolved timing remains excluded through null timing

Lead timing audit:
- 487 source events
- 447 pitched scorer rows
- preserved source exclusions/uncertainty, including the measure-39 source-error passage

The scorer respects the source 2/4 bar at measure 104 instead of stretching it to 4/4.

## Scoring-only contract

The three-role score downloaded the frozen prediction artifact from run `37094392537`.

It did **not**:
- run the separator
- run Basic Pitch
- modify predictions
- search alignment
- tune thresholds

Primary metric:
one-to-one exact MIDI + onset within 50 ms.

Diagnostic metrics:
- pitch-class + onset
- onset-only

## Results

### Rhythm - generic raw guitar stem

Targets: **971**

Exact MIDI/onset:
- TP 36
- precision **3.51%**
- recall **3.71%**
- F1 **3.61%**

Pitch-class/onset F1:
**7.82%**

Onset-only F1:
**25.35%**

Whole-mix exact F1:
**2.07%**

Separator delta:
**+1.53 points**

### Lead - same generic raw guitar stem

Targets: **447**

Exact MIDI/onset:
- TP 44
- precision **4.29%**
- recall **9.84%**
- F1 **5.98%**

Pitch-class/onset F1:
**8.83%**

Onset-only F1:
**22.28%**

Whole-mix exact F1:
**0.99%**

Separator delta:
**+4.99 points**

### Bass - raw bass stem

Targets: **547**

Exact MIDI/onset:
- TP 51
- precision **7.34%**
- recall **9.32%**
- F1 **8.21%**

Pitch-class/onset F1:
**9.02%**

Onset-only F1:
**31.72%**

Whole-mix exact F1:
**9.29%**

Separator delta:
**-1.08 points**

## Overall

Three-role macro exact-MIDI/onset F1:
**5.93%**

The raw separator materially helps both guitar-role scores, especially lead, but the raw bass stem scores slightly worse than the whole mix under the same transcriber.

The generic guitar stem is shared by rhythm and lead; these role scores therefore measure musical evidence agreement, not successful rhythm-vs-lead source separation.

## GitHub Actions evidence

Successful scoring run:
`37095137423`

Head:
`3b555b10be0b25df207a9178b145d5b9f05efe3b`

Artifact:
- id: `11264400463`
- digest: `sha256:63c86d9ca40af348dd98796c1a08e7946cc473aed7a75793e16abd7cb64a2f75`

Two earlier scoring-only attempts failed before scoring because the runner inherited unnecessary inference-module dependencies. The final scorer was made inference-runtime-free rather than expanding those dependencies.
