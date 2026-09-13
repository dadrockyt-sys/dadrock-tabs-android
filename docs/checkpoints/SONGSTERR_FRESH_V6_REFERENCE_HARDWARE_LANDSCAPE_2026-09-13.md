# Songsterr Fresh V6 — Independent Reference Hardware Landscape

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **DESIGN/FEASIBILITY RESEARCH ONLY — NO PROCUREMENT, CONTACT, RECORDING OR DATA ACQUISITION AUTHORIZED**

## Purpose

Stress-test whether the purpose-built untouched-holdout fallback has a more defensible independent-reference architecture than ordinary pitch-to-MIDI guitar, now that AG-PT-set has been rejected because its precise reference onsets were constructed from evaluated audio.

The target architecture must preserve:
- real performed guitar;
- conventional isolated guitar DI as the evaluated audio;
- a contemporaneous note reference whose pitch/onset evidence comes from physically separate sensing rather than the evaluated DI waveform;
- raw event preservation and reference-blind structural auditability.

This review does not select or recommend a purchase.

## Industrial Radio Fretsense / Solange 6 — strongest surfaced architecture, with caveats

Primary current product/support pages reviewed:
- https://industrialradio.com.au/products/fretsense/
- https://industrialradio.com.au/products/solange-6-midi-guitar/
- https://industrialradio.com.au/products/fsi-1-fretsense-interface/
- https://industrialradio.com.au/support/downloads/
- https://industrialradio.com.au/support/software-editors/

### Why it remains technically distinctive

Industrial Radio states that Fretsense:
- detects held fret/note position through conductivity between metal strings and wired frets rather than deriving pitch solely from an audio waveform;
- combines fret sensing with bridge pitch-bend sensors and piezo bridge-saddle trigger sensing;
- exposes conventional magnetic guitar audio separately from MIDI/reference signals;
- routes magnetic audio, MIDI and individual piezo signals through the FSI-1 interface;
- is implemented in the Solange 6 as a real six-string electric guitar with EMG magnetic pickups and a backup 1/4-inch audio output.

This creates a stronger experimental separation than Fishman/Jamstik-style pitch-to-MIDI: pitch identity is principally obtained from fret/string contact while trigger information is obtained from separate bridge sensing, leaving the conventional magnetic output available as the V6 evaluation DI.

### Important limitations

Fretsense is not an infallible ground-truth device:
- note triggering remains sensor/algorithm derived from piezo saddle signals and/or optional RadioPick triggering;
- available editor/manual material shows configurable trigger gain/filter/decay behavior in the Fretsense family;
- pitch-bend, slides, open strings, legato and retriggers can create complex raw MIDI semantics that must be handled only through preregistered structural rules;
- exact guitar firmware/settings must be confirmed rather than inferred from a related bass-editor manual.

Therefore a future V6 capture could use Fretsense only as a **separately sensed contemporaneous reference candidate**, followed by a zero-anomaly reference-blind audit. It must never be presumed correct because of vendor claims.

### Current availability uncertainty

Industrial Radio's site is live and currently crawled, lists Solange 6/FSI-1/Fretsense as products, exposes current download/support pages, and states that all Fretsense instruments ship with an FSI-1. However, the Solange 6 product page's shipping table and product-update text show a last update in September 2019, and the page states a 12-month build time. This is insufficient evidence of current order fulfillment/lead time in 2026.

**Disposition:** strongest technical feasibility architecture found, but procurement availability and exact current firmware semantics would need verification only if the user later explicitly selects the purpose-built route. Do not contact/order now.

## Jamstik / hexaphonic pitch-to-MIDI — weaker reference architecture

Already reviewed Jamstik documentation establishes separate traditional guitar audio plus six-channel hexaphonic MIDI. But pitch identity is still inferred from string audio, vendor documentation acknowledges extra/missed MIDI events depending on sensitivity, and downstream DAW/MPE paths can lose per-string channel identity.

**Disposition:** lower-confidence fallback only; not preferable to independently fret-sensed pitch identity.

## AeroBand smart/digital guitars — not a real-guitar DI holdout

Current AeroBand products expose MIDI and fretboard sensors, but use a digital/sensorized instrument design (including silicone/sensor fretboard elements and digital sound generation). Even where real strings are present, this does not establish a conventional magnetic real-electric-guitar DI signal independent from the controller electronics.

**Disposition:** unsuitable for the frozen real performed-guitar external holdout. Do not substitute controller-generated audio/MIDI for real-guitar DI validation.

## Historical switch-matrix/fret-sensing instruments — architecturally interesting, operationally unsuitable

Historical instruments such as SynthAxe and Casio DG-series demonstrate the valuable concept of decoupling fret/pitch identity from trigger sensing. They are not a practical current V6 holdout path because they are controller instruments rather than a current conventional guitar with a clean magnetic DI evaluation path, and availability/support/reproducibility are unsuitable.

Other old/obscure fret-sensing systems (e.g. historical ROR/FretTrax discussions) lack a current authoritative product/reference specification adequate for freezing a reproducible validation experiment.

**Disposition:** conceptual prior art only.

## HyVibe / audio-sensor smart guitars — not independent note truth

HyVibe's current system uses a piezo saddle sensor feeding signal-processing algorithms and body exciters. It is a smart acoustic-guitar audio-processing architecture, not a separately sensed note identity/onset reference stream independent of the evaluated audio.

**Disposition:** not a V6 reference source.

## Hardware decision frontier

No surfaced architecture is perfect. The current ordering for **design feasibility only** is:

1. **Fretsense-style physical fret identity + separate trigger sensors + separate conventional magnetic DI** — strongest independence story, still needs calibration freeze and structural rejection rules.
2. **hexaphonic pitch-to-MIDI + separate conventional audio** — weaker because reference pitch/onset is still audio-tracked and known to emit misses/extras.
3. **digital controller/switch-matrix smart guitars** — strong symbolic certainty but fail the real conventional-guitar DI requirement.
4. **software/pickup audio-to-MIDI from evaluated/related audio** — unacceptable as independent truth under the frozen V6 gate.

This hierarchy does not authorize acquisition and does not change any V6 scoring rule.

## Minimum future verification before any hardware selection

If the user later explicitly selects the purpose-built route, verify before purchase/contact/capture:
- current manufacturer availability and exact model/revision;
- exact pitch/fret sensing semantics including open strings, slides, hammer-ons/pull-offs, bends and repeated attacks at one fret;
- exact trigger source and thresholds/filter/decay parameters;
- raw MIDI channel/event behavior without DAW transformations;
- independent conventional magnetic output path;
- firmware/editor version and ability to export/freeze settings;
- common clock/timestamp strategy for audio + MIDI capture;
- reproducible backup/export of all instrument settings;
- a preregistered non-holdout calibration protocol;
- structural acceptance/rejection rules frozen before admitted takes.

## Authority unchanged

No product was purchased, contacted, ordered or tested. No performer was contacted. No data was recorded/acquired. No Basic Pitch/V6 correctness occurred. Archived V143/Gomyway and GOAT/reference scoring remain closed. The purpose-built route remains design-only pending explicit user authorization.
