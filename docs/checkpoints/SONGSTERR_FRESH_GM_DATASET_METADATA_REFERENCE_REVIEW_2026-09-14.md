# Songsterr Fresh V6 — GM Dataset Metadata / Reference Review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/reference review only; no dataset media acquisition, Basic Pitch, V6 correctness, protected-song execution, Modal, Vercel heavy-GPU, or L4 work.

## Authority

V6 remains frozen by:
- `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md` — commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`
- implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`
- `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md` — commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`

The five replacement-holdout pre-media gates remain: usable performance-audio rights; real guitar; immutable independent performed note-level onset+pitch truth; plausible >=1,000 V6-positive capacity without derivative inflation; defensible untouched status.

## Candidate

`GM Dataset`, introduced in Simone Chieppa et al., *Automatic Guitar Transcription With Deep Neural Networks*, IEEE Access 13 (2025), DOI `10.1109/ACCESS.2025.3583646`.

Primary public manuscript reviewed: University of Coimbra MIR mirror of the IEEE Access article (`mir.dei.uc.pt/pdf/Journals/MERGE/Access_2025_Chieppa.pdf`).

## Primary-source facts

The paper states that GM Dataset was created specifically as a new testing corpus and contains real guitar recordings spanning rock, jazz/blues, pop, reggae and classical material. It mixes acoustic guitar and clean electric guitar recordings; some were recorded with a mobile phone and others with a semi-professional sound card / DAW.

Crucially, the performed-event reference was not captured independently from the player. The authors selected existing songs, obtained MIDI files and tablatures from Ultimate Guitar, corrected/adapted some scores in Guitar Pro, recorded performances while following those transcriptions, then imported the exported transcription MIDI into a DAW and aligned it to the recording. The single transcription was subsequently split into six per-string MIDI files in Guitar Pro.

The paper reports 18 recordings totaling about 25 minutes 29 seconds:
- 4 rock — 7:12
- 5 jazz/blues — 6:40
- 5 pop — 6:58
- 2 reggae — 1:57
- 2 classical — 2:42

The article itself is distributed under CC BY-NC-ND 4.0, but that publication license is not an explicit permissive performance-audio/data license for product validation. The described corpus also uses transcriptions of commercial songs sourced from Ultimate Guitar and names copyrighted repertoire examples. No separate authoritative public corpus package/license establishing product-validation rights was located in this review.

## Frozen-gate evaluation

1. **Performance-audio rights: FAIL / unresolved.** The article license is not a corpus performance-audio grant, and the described material includes copyrighted repertoire/transcriptions.
2. **Real guitar: PARTIAL PASS.** Real acoustic and clean electric guitar performances are described, but the frozen V6 evaluated path is isolated-guitar DI; the corpus mixes phone/audio-interface capture and acoustic/electric material rather than one clearly qualifying DI population.
3. **Independent performed note-level onset+pitch truth: FAIL.** The reference originates from pre-existing tablature/MIDI score material and is DAW-aligned to the newly recorded performance. It is therefore score-following/aligned annotation, not an independently captured performed-event stream.
4. **Population capacity: FAIL.** Eighteen recordings / ~25.5 minutes is not a defensible route to the frozen >=1,000 V6-positive admission capacity without first exposing correctness, and there is no basis for inflating the population through derived representations.
5. **Untouched status: not reached as an admission question.** Even if otherwise untouched by this V6 project, hard gates 1, 3 and 4 already fail.

## Decision

**REJECT BEFORE MEDIA ACCESS.** GM Dataset is not an admissible V6 replacement holdout under the frozen rules. Do not acquire or score it for V6 correctness. Do not reinterpret its score-following DAW-aligned MIDI as independent performed truth.

This is a metadata/reference determination only. It does not modify any frozen V6 constant, Basic Pitch setting, audio path, matcher, tolerance, uncertainty rule, admission gate, stratum rule, or deferred-reveal/single-run rule.

## Guitar-TECHS status recheck for this continuation

Official run `34754519541`, job `103716527380`, remains `completed/success`; artifact `guitar-techs-v6-alignment-inventory` ID `10317695640` remains live/unexpired with GitHub digest `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`. Frozen audit decision remains `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; no Guitar-TECHS correctness or duplicate run is permitted.

## Fail-closed state

Remain:
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- Policy C `UNENROLLED`
- protected-song execution embargoed
