# Guitar-FL Stage B concrete capture hardware selection V1

Date: 2026-10-06
Branch: `astra-work`
Status: **PROCUREMENT SHORTLIST FROZEN / NO PURCHASE EXECUTED**

## Design objective

Satisfy the frozen Stage-B V1 requirement that evaluated DI, physical fret-state reference, and six independent excitation channels share **one authoritative hardware acquisition clock**.

The most robust implementation is to represent all authoritative planes as simultaneously sampled analog channels into one multichannel ADC/audio interface.

Required simultaneous channels:

- Plane A clean DI: **1**
- Plane B per-string fret-contact state: **6**
- Plane C per-string excitation sensors: **6**
- total: **13 analog input channels**

A 16-input interface therefore leaves three spare channels while avoiding any separate-clock synchronization path.

## Primary interface class

### Tascam US-16x08 class — preferred V1 capture interface

Why it fits:
- 16 simultaneous analog inputs;
- 24-bit conversion;
- supports 48 kHz, matching the frozen Plane-A and Plane-C rate;
- inputs 1–8 provide mic preamps;
- inputs 9–10 support instrument/line operation;
- remaining analog inputs provide sufficient capacity for the 13 authoritative streams.

Frozen use:
- session format: **48 kHz / 24-bit**
- all A/B/C channels recorded in one multichannel stream / one interface clock
- no ADAT or secondary clock required

This class is preferred over an 8-input interface because an 8-input device cannot simultaneously acquire DI + six fret-state channels + six excitation channels without adding a second clocked converter.

## Authoritative channel map

Proposed immutable channel map:

1. clean magnetic DI
2. string 6 excitation
3. string 5 excitation
4. string 4 excitation
5. string 3 excitation
6. string 2 excitation
7. string 1 excitation
8. reserved excitation/reference diagnostic
9. string 6 fret-state encoded voltage
10. string 5 fret-state encoded voltage
11. string 4 fret-state encoded voltage
12. string 3 fret-state encoded voltage
13. string 2 fret-state encoded voltage
14. string 1 fret-state encoded voltage
15. hardware calibration/reference voltage
16. reserved

Channels 8, 15 and 16 may be repurposed only before the capture-plan identity is frozen.

## Plane-B electrical implementation class

The fret-contact matrix remains custom instrumentation.

Each string must produce one independently sampled state voltage whose valid ranges deterministically encode:
- open/unfretted;
- fret 1..N;
- invalid/open-circuit fault state.

Requirements:
- passive/contact sensing must not derive state from Plane-A audio;
- each string channel sampled by the same 48 kHz ADC clock;
- the decoder may downsample logically, but the frozen hardware minimum remains >=1 kHz;
- voltage bands, hysteresis, debounce, fault bands and calibration coefficients must be frozen on non-holdout calibration material;
- no evaluated-DI or model output may be used in calibration.

Using six analog fret-state channels removes the need for a separately clocked microcontroller data stream in V1.

## Plane-C excitation sensor class

Use six physically independent per-string piezo/force/acceleration sensors, each conditioned into its own analog input.

Requirements:
- one sensor channel per string;
- raw 48 kHz waveform retained;
- no summed bridge channel as authoritative reference;
- sensor gains fixed before holdout capture;
- event-birth decoder frozen on calibration performances only.

Low-cost piezo discs/contact pickups are acceptable for **bench calibration prototypes**, but not automatically accepted as the final holdout sensors until cross-string leakage and saturation QA pass.

## DI path

Plane-A DI must remain:
- clean;
- mono;
- magnetic pickup output;
- no amp/cab/effects;
- no denoise/normalization/separation;
- one dedicated interface input;
- input gain fixed by calibration identity.

## Procurement tiers

### Tier 1 — minimum viable calibration rig

- one 16-input 24-bit interface in the US-16x08 class;
- six piezo/contact sensors plus six identical high-impedance conditioning channels;
- custom six-string fret-contact matrix;
- shielded cabling;
- calibration/reference voltage source;
- one sacrificial/calibration guitar or removable non-destructive sensor fixture.

Purpose: prove transport, clock, cross-talk, fret-state separability, event-birth separability and decoder stability.

### Tier 2 — holdout-ready rig

Only after Tier-1 calibration passes:
- mechanically stable six-string contact matrix;
- matched per-string excitation sensors;
- fixed conditioning electronics;
- documented wiring harness;
- immutable firmware/configuration where applicable;
- spare identical sensors/interface cabling for hardware replacement under frozen identity rules.

## Rejected interface classes for V1

- ordinary 2/4/8-input interfaces: insufficient simultaneous authoritative inputs;
- USB mixers without guaranteed discrete multichannel recording: not accepted;
- multiple independent USB interfaces: violate the single-clock V1 requirement unless a new preregistered hardware clock architecture is introduced;
- MIDI guitar/pitch-to-MIDI products as Plane-B truth: they estimate pitch and do not constitute direct physical fret-state identity.

## Purchase boundary

This file freezes a **hardware class and channel architecture**, not a purchase transaction.

Before spending:
1. verify the exact selected unit can expose at least 13 simultaneous discrete analog inputs to the recording host at 48 kHz / 24-bit;
2. verify OS/driver support on the intended capture computer;
3. freeze exact model/firmware/driver identity;
4. perform no holdout recording until the calibration package passes.

No purchase has been executed by this decision.
