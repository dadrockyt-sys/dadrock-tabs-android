# V168-related diagnostic — SplitMySong isolated-guitar input

Date: 2026-09-01 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **DIAGNOSTIC INPUT FROZEN / CPU COMPARISON NOT YET SCORED**

## Scope
This is a legacy single-song diagnostic using **Lenny Kravitz — Are You Gonna Go My Way**. It is outside the frozen V168 prospective holdout evaluation. It must not be counted as a V168 holdout, V168 Test Score, or V168 prospective reference-facing score call.

V168 remains `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; Project Progress Score remains **60%** and Test Score remains **NOT RUN**.

## User-supplied diagnostic audio
File name: `Guitar - Are You Gonna Go My Way - Lenny Kravitz ｜ Only Guitar (Isolated).m4a`

Observed properties:
- SHA256: `6601b8d01cbbbe6b6e70d9ec0ca3c15d17873c78e62ae4acdc258c96f168e3c9`
- AAC-LC
- 44.1 kHz stereo
- ~128 kbps
- duration ~217.06 s
- metadata title: `Are You Gonna Go My Way - Lenny Kravitz | Only Guitar (Isolated)`
- metadata states: `Audio isolated with www.SplitMySong.com`
- embedded source URL: `https://www.youtube.com/watch?v=sQBvgJdSlJc`

This is an **external model-generated separation**, not a professional symbolic/audio reference. It is therefore diagnostic-only and is not admissible under the V168 professional-reference provenance gate.

## Diagnostic question
Does feeding this externally isolated guitar audio into the existing DadRock AI Tab CPU transcription path improve the legacy AYGGMW combined-Guitar score relative to the frozen promoted V167 I005 baseline?

Frozen comparison baseline:
- V167 I005 `gss-active-only`
- Guitar F1: **42.7940586109996%**
- Precision: **48.54280510018215%**
- Recall: **38.26274228284279%**
- TP/predicted/reference: **533 / 1098 / 1393**
- FP/FN: **565 / 860**
- prediction SHA256: `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`

## Alignment freeze — reference-blind
A source-audio onset-envelope cross-correlation check against the available same-song mix found:
- start lag: **0.000 s**
- no time-stretch required
- the isolated file appears to differ primarily by ~5.5 s of trailing silence/padding

Frozen diagnostic alignment rule:
- start at t=0 with **no shift**
- **no time-stretch**
- do not use professional note-event reference content to optimize alignment
- ignore/crop only trailing audio outside the original song timebase if needed; no reference-driven event alignment is permitted

## Exact historical detector path recovered
The V167 observer uses Basic Pitch with:
- `onset_threshold=0.50`
- `frame_threshold=0.30`
- `minimum_note_length=90.0` ms
- guitar-frequency bounds inherited from the frozen CPU transcriber
- `multiple_pitch_bends=False`
- `melodia_trick=True`

V167 promoted Policy/I005 then applies the frozen `gss-active-only` contextual filter:
- Basic Pitch active context required
- `fundamentalPresent=true`
- harmonic template rank >= 0.975
- activity support >= 0.05
- onset support >= 0.50
- candidate/max-active score ratio >= 1.00
- reject nearest different active intervals {12,19,24}
- top1/site
- Guitar cap6
- inactive branch off

No thresholds or selectors may be changed after seeing this diagnostic score.

## Runtime status / blocker
Local CPU runtime has `librosa`, `numpy`, `scipy`, `soundfile`, `torch`, and Demucs installed, but:
- `basic_pitch` is not installed;
- local runtime network/DNS prevents installing Basic Pitch from PyPI/GitHub;
- the Demucs `htdemucs_6s` weight is not cached locally, and local network/DNS prevents fetching it.

Do **not** substitute another pitch detector. Preferred next route is an existing GitHub Actions CPU runner with Python 3.11 and the exact Basic Pitch dependency, if the repository already contains a suitable historical workflow.

No GPU/CUDA/Modal has been used or authorized for this diagnostic.

## Integrity boundary
- This diagnostic may use the legacy AYGGMW reference only **after** the candidate stream is generated and frozen.
- It does not alter V168 Policy A/B, admission validators, holdout requirements, or prospective evaluation rule.
- V168 prospective reference-facing score calls remain exactly **0**.
- Project Progress Score remains **60%**.
- Test Score remains **NOT RUN**.
