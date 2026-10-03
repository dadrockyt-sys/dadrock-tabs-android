# Trust / Flag Study Source Inventory — Current Shortfall

Date: 2026-10-02  
Branch: `astra-work`

## Inventory inspected

Private repository:
`dadrockyt-sys/dadrock-tabs-private-fixtures`

Branch:
`main`

Head commit:
`13e86335bc87740932f49cf2dd5251ba49b8d519`

The repository currently contains:
- the S0 fixture ZIP;
- `s0_sources/README.md`;
- `s0_sources/manifest.json`;
- **14 source audio assets**.

The committed S0 manifest supplies SHA-256 identities for all 14 source audio assets.

## Eligibility result

Eligible new source assets for the Trust / Flag Holdout Protocol V1:

**0**

All 14 accessible source assets are the same S0 development sources already used by the current separator/recognizer/transcription experiments.

Therefore none may be used in:
- the new 48-case calibration phase;
- the sealed 48-case holdout phase.

## Protocol shortfall

Required minimum new study:
- calibration: 48 cases;
- holdout: 48 cases;
- total: 96 cases;
- calibration and holdout source sets must be mutually disjoint;
- all study sources must also be disjoint from S0/prior development.

Current private inventory:
- new eligible source assets: **0**.

A real candidate manifest therefore cannot currently pass admission.

## Decision

**STOP at manifest-admission boundary.**

Do not:
- reuse S0 assets under new mixtures;
- fabricate SHA-256 identities;
- clone/copy/transform S0 sources and treat them as new sources;
- reduce the required strata;
- define a trust threshold;
- render new study audio;
- run BS-Roformer or Basic Pitch for this study.

The next legitimate requirement is acquisition/import of genuinely new, source-disjoint fixture material with independently recorded source identity/provenance.

Once new assets exist, inventory them first, hash them, assign only model-free study strata, and run the holdout manifest admission validator before any waveform study execution.
