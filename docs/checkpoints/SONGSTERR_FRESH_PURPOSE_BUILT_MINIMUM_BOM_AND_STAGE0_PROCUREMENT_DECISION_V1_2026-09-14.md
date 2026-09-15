# Songsterr Fresh — Purpose-Built Minimum BOM + Stage-0 Procurement Decision V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **FROZEN STAGED NON-HOLDOUT BENCH PROCUREMENT DECISION / NO HOLDOUT CAPTURE AUTHORITY**

Parent topology: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_CUSTOM_REFERENCE_PROTOTYPE_TOPOLOGY_V1_2026-09-14.md`, commit `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf`.

## 1. Decision

`STAGE0_PHYSICAL_CONTACT_BENCH_NOW_OBJECTIVELY_NECESSARY: true`

`STAGE1_REAL_INSTRUMENT_MODIFICATION_NOW_NECESSARY: false`

`STAGE2_SIX_CHANNEL_EXCITATION_HARDWARE_NOW_NECESSARY: false`

`STAGE2_EIGHT_CHANNEL_AUDIO_INTERFACE_NOW_NECESSARY: false`

`REAL_HOLDOUT_RECORDING_AUTHORIZED: false`

The remaining decisive uncertainty is physical: can a low-cost physical string/fret/contact plane identify independent string/fret state under single notes, same-fret chords, different-fret chords and multi-contact conditions without evaluated-audio/model inference? Documentation and synthetic code cannot answer that. A small NON_HOLDOUT physical contact bench is therefore the first objectively necessary procurement/engineering stage.

Expensive excitation/audio hardware is explicitly deferred until this physical-state feasibility gate passes.

## 2. Stage-0 objective

Build a small insulated contact coupon/fixture that can exercise representative six-string/fret electrical states without modifying a real guitar or collecting any holdout performance.

It must answer:
- whether multiplexed conductive string/fret scanning can remain unambiguous under polyphony;
- whether electrical string isolation is required;
- whether one continuous fret/contact conductor creates unacceptable cross-string coupling;
- whether segmented/isolated per-string contact sensing is required;
- whether raw contact observations can be timestamped and regenerated deterministically;
- whether ambiguous states can be detected explicitly rather than guessed.

Stage 0 is engineering calibration only. No musical/model correctness meaning attaches to a PASS.

## 3. Preferred reusable logger candidate

### Teensy 4.1 — document-compatible preferred Stage-0 logger

Current official PJRC specifications include:
- 600-MHz ARM Cortex-M7;
- 55 total digital I/O pins;
- 18 analog inputs;
- onboard microSD/SDIO;
- multiple SPI/I2C/serial interfaces.

That is more than enough for the small Stage-0 contact coupon and remains reusable for a later full six-string logger rather than becoming throwaway hardware.

Current DigiKey Canada listing reviewed 2026-09-14:
- SparkFun Teensy 4.1 without Ethernet, part 20360;
- listed active/in stock;
- single-unit price `CAD $49.24` at time of screen.

Sources:
- https://www.pjrc.com/store/teensy41.html
- https://www.digikey.ca/en/products/detail/sparkfun-electronics/20360/16688096

This is a preferred candidate, not a claim that no other MCU can work.

## 4. Optional multiplexing parts

A full-scale segmented sensing approach may eventually require analog/digital multiplexing. Stage 0 should buy only a few inexpensive parts for topology experiments rather than enough for a final 132-position system.

Document-compatible examples:
- TI `CD74HC4051E`, 8:1 analog multiplexer/demultiplexer, through-hole PDIP, active product;
- current DigiKey Canada single-unit screen price approximately `CAD $1.62`;
- TI `CD74HC4067`, 16:1 analog multiplexer/demultiplexer, active product, compatible with 3.3-V-class logic/signal ranges subject to the datasheet.

Sources:
- https://www.digikey.ca/en/products/detail/texas-instruments/CD74HC4051E/475938
- https://www.ti.com/product/CD74HC4067

Exact mux topology is intentionally not frozen before the contact experiment reveals whether multiplexed continuous-fret scanning is viable.

## 5. Stage-0 mechanical/electrical coupon

Minimum generic materials:
- insulating base;
- six electrically distinguishable steel-string/wire conductors;
- several representative conductive fret/contact bars or segmented contact pads;
- breadboard/prototype board;
- current-limiting resistors / resistor assortment;
- jumper wire;
- connectors/clips;
- optional mux parts above;
- nonconductive spacers/fixtures needed to reproduce isolated and common-contact configurations.

The coupon must support at least these configurations:
1. isolated strings + one shared continuous fret conductor;
2. multiple strings touching the same fret simultaneously;
3. multiple strings touching different frets simultaneously;
4. deliberately electrically common strings to characterize the ordinary-metal-bridge failure mode;
5. electrically isolated per-string fret/contact segments as the fallback reference architecture.

Only low-voltage bench logic/sensing is permitted. The exact resistor/drive values must remain within MCU/component datasheet limits and are engineering values, not holdout-derived thresholds.

## 6. Stage-0 logger output

Every raw scan record should preserve at minimum:
- monotonic logger tick;
- scan/cycle sequence number;
- raw per-string/per-contact observation before debounce;
- configured topology ID;
- explicit electrical/sensor status;
- firmware/configuration identity.

Any decoded string/fret state must be reproducible from preserved raw bytes plus the frozen decoder/configuration. Ambiguity is a first-class output, not an invitation to guess.

No evaluated audio is required or allowed for Stage-0 truth decisions.

## 7. Stage-0 PASS/FAIL decision

### PASS to Stage 1

Stage 0 may advance only if one physical topology demonstrates all of the following under repeated synthetic/mechanical contact patterns:
- all six string identities remain independently observable;
- representative open/fret/contact states are deterministically distinguishable;
- same-fret and different-fret polyphonic contact patterns are distinguishable;
- no hidden electrical coupling causes one contact to masquerade as another without being detectably ambiguous;
- raw logs/ticks are stable enough for deterministic replay;
- ambiguous/invalid states are explicitly observable.

### FAIL / topology change

If a continuous-fret / multiplexed topology cannot resolve chords because of cross-string electrical coupling, do not tune a decoder to guess around it. Freeze that topology as `BENCH_FAIL` for authoritative truth and move to electrically isolated per-string segmented/capacitive/contact sensing.

No evaluated DI/model output may be consulted to choose which topology “looks right.”

## 8. Local programming/capture host

A Teensy-class logger must be programmed and its raw logs retrieved by a local host. If an existing suitable Linux/macOS/Windows host is unavailable, a small dedicated Linux SBC becomes a support component rather than part of reference truth.

Raspberry Pi 5 is a document-compatible host class:
- official spec: 2.4-GHz quad-core 64-bit Cortex-A76;
- USB 3.0 and USB 2.0 ports;
- microSD storage;
- Wi-Fi/Ethernet;
- PJRC provides open-source `teensy_loader_cli`, documented for Linux and explicitly supporting `TEENSY41`.

Current Canadian examples screened:
- Raspberry Pi 5 2GB board at PiShop Canada: `CAD $90.95`;
- PiShop 2GB budget kit including case, microSD and 27-W supply: `CAD $134.95`.

Sources:
- https://www.raspberrypi.com/products/raspberry-pi-5/
- https://www.pjrc.com/teensy/loader_cli.html
- https://www.pishop.ca/product/raspberry-pi-5-2gb/
- https://www.pishop.ca/product/raspberry-pi-5-budget-kit-2gb/

The host is needed only if no suitable existing machine is available. It is not itself an authoritative sensor and cannot be used to reinterpret reference truth.

## 9. Stage-2 audio interface — deferred budget lead

Once the physical pitch-state plane passes, the frozen prototype requires eight simultaneous analog channels:
- 1 clean magnetic DI;
- 6 per-string excitation channels;
- 1 conditioned hardware sync marker.

### Behringer UMC1820 — preferred budget document lead, not yet purchase-authorized

Current manufacturer documentation states:
- eight combination XLR/TRS analog inputs with preamps;
- 24-bit / 96-kHz conversion;
- simultaneous multichannel USB operation.

Long & McQuade Canada currently lists it at `CAD $274` and states the eight analog input channels are sent separately to the computer.

That is sufficient on paper for this bench channel budget; 192-kHz premium interfaces are not required by the frozen 25-ms structural timing bound merely for higher headline sample rate.

Sources:
- https://www.behringer.com/en/products/0805-AAN
- https://www.long-mcquade.com/191896/Pro-Audio-Recording/Audio-Interfaces/Behringer/U-PHORIA-UMC1820-Audiophile-18x20-24-Bit-96-kHz-USB-Audio-MIDI-Interface-with-Midas-Preamps.htm

Linux community reports describe UMC1820 as USB class-compliant and working with ALSA/Linux. This is useful for a future Raspberry-Pi/Linux bench path but remains a bench verification item rather than an official manufacturer guarantee for the exact Pi configuration.

Do **not** buy the interface at Stage 0 unless it is independently useful for another purpose; it cannot answer the fret-state feasibility question.

## 10. Stage-2 excitation hardware — deferred

Graph Tech Ghost-style six individual piezo saddles remain a plausible per-string excitation source. Current Graph Tech documentation describes six separate piezo/string electrical signals and current six-saddle sets around `USD $137.45` for some Strat/Tele/Parker-style configurations, with higher prices for other bridges.

But the frozen use would require direct/raw per-string capture before any pitch-to-MIDI conversion. The exact six-channel buffer/breakout path, bridge compatibility and electrical string-isolation properties are still unproven.

Sources:
- https://help-center.graphtech.com/en-US/ghost-hexpander-review-764628
- https://graphtech.com/collections/ghost-pickup-systems-guitar-saddle

Therefore Ghost/piezo procurement remains deferred until Stage 0 passes and an actual instrument topology is selected.

## 11. Staged spending boundary

### Objectively justified now — Stage 0 only

If equivalent parts are not already available:
- one reusable real-time logger board (Teensy 4.1 class);
- basic breadboard/wire/resistor/contact-fixture materials;
- a few inexpensive mux parts only if needed for the chosen coupon experiment;
- a small Linux host only if there is no existing machine capable of programming/log retrieval.

The electronics core of Stage 0 is intentionally kept in the tens-of-dollars range before shipping/tax when an existing host is available.

### Not objectively justified yet

Do not yet purchase solely for this validation route:
- Behringer UMC1820 or another eight-channel interface;
- Graph Tech Ghost/hexaphonic piezo system;
- a donor guitar or modified fretboard/neck;
- premium MIDI-guitar products;
- performers, studio time or rights packages.

Those become necessary only after the preceding stage produces the evidence needed to justify them.

## 12. Next technical action before/while Stage-0 parts are obtained

Freeze and implement a **Stage-0 raw contact logger/schema + replay validator** using synthetic electrical-state fixtures only. The software must:
- have no audio/model input path;
- preserve raw scan/tick identity;
- deterministically decode only physical contact states;
- surface ambiguity explicitly;
- support byte-stable test fixtures;
- be runnable in GitHub CPU CI without real hardware.

That software work can proceed immediately and will reduce bench discretion once hardware exists.

## 13. Authority boundary

No real holdout exists. Stage-0 bench data is permanently NON_HOLDOUT engineering/calibration material.

Keep:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Archived V143/Gomyway remains untouched and closed.
