# Songsterr Fresh — Purpose-Built Reference Hardware Document/API Screen V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **INITIAL DOCUMENT/API SCREEN / NO HOLDOUT CAPTURE AUTHORITY**
Parent gate: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_REFERENCE_HARDWARE_BENCH_QUALIFICATION_PREREGISTRATION_V1_2026-09-14.md`

## Decision

`NO_COMPLETE_OFF_THE_SHELF_AUTHORITATIVE_REFERENCE_QUALIFIER_FOUND_IN_INITIAL_SCREEN`

`HYBRID_OR_CUSTOM_REFERENCE_ARCHITECTURE_LIKELY_REQUIRED: true`

`IMMEDIATE_COMMERCIAL_MIDI_GUITAR_PURCHASE_JUSTIFIED: false`

The initial current-product/document screen found no complete commercial system that satisfies the frozen authoritative-reference semantics by itself. The common commercial approach is a divided/hexaphonic pickup followed by pitch-recognition processing. That can preserve string separation and may be useful as an independent excitation/vibration plane, but it does not establish physical fret/contact identity independently of acoustic/electrical pitch inference.

## Frozen acceptance basis

A complete qualifier must independently provide:
1. physical string + nominal fret/contact state;
2. independent event-birth/rearticulation evidence;
3. raw/exportable provenance;
4. hardware clock/sync evidence;
5. configuration/calibration identity;
6. deterministic offline regeneration;
7. sensor/stream health evidence.

Pitch-to-MIDI output alone is insufficient.

## Candidate screen

### Jamstik current MIDI guitars — `DOCUMENT_REJECTED` as authoritative pitch-state truth

Current Jamstik documentation states that its MIDI guitars use a six-channel hexaphonic pickup plus onboard signal processing to detect pitch per string and translate performance into MIDI. Current support documentation also exposes sensitivity settings that change how likely a note is registered. That is valuable as a musical MIDI controller but violates the authoritative pitch-state requirement because nominal note identity is still derived from detected string vibration/pitch rather than a physical fret/contact state.

Document sources reviewed:
- Jamstik, “Jamstik MIDI Guitar FAQ | Compatibility, Latency, MPE & Setup” — https://jamstik.com/pages/faq
- Jamstik, “How Jamstik MIDI Guitars Work” — https://jamstik.com/pages/how-it-works
- Jamstik Help Center, “Jamstik MIDI Guitar Device Settings” — https://support.jamstik.com/hc/en-us/articles/11591028822285-Jamstik-MIDI-Guitar-Device-Settings

Result: do not purchase a current Jamstik as the authoritative physical pitch-state plane.

### Fishman TriplePlay — `DOCUMENT_REJECTED` as authoritative pitch-state truth

Fishman describes TriplePlay as using a hexaphonic pickup and real-time guitar pitch detection. Per-string separation is useful, but the product's note identity is produced by pitch detection and does not expose an independent physical fret/contact truth under the frozen semantics.

Document sources reviewed:
- Fishman, “TriplePlay Connect MIDI Guitar Controller” — https://fishman.com/dp/tripleplay-connect/
- Fishman, “TriplePlay Support” — https://fishman.com/tripleplay-support/

Result: do not purchase TriplePlay as the authoritative physical pitch-state plane.

### BOSS/Roland GK-5 / Serial GK — `DOCUMENT_REJECTED` as authoritative pitch-state truth; possible component lead only

Roland's GK-5 manual states that the divided pickup detects guitar-string vibration. Serial GK transports divided pickup signals. This preserves per-string signal separation but still does not provide physical fret/contact state. The proprietary serial path also requires additional proof of raw-access and synchronization suitability before it could be accepted even as a component of the excitation plane.

Document sources reviewed:
- BOSS GK-5 Owner's Manual — https://static.roland.com/assets/media/pdf/GK-5_eng01_W.pdf
- BOSS VG-800 Reference Manual / Serial GK overview — https://static.roland.com/assets/media/pdf/VG-800_reference_eng01_W.pdf

Result: not an authoritative pitch-state plane. Do not buy it for that purpose. It remains only a possible per-string vibration/excitation component if later raw-access evidence justifies a bench sample.

### Graph Tech Ghost / Hexpander — `BENCH_REQUIRED_COMPONENT_ONLY` for excitation; not a complete qualifier

Graph Tech documents separate piezo saddles producing six discrete electrical string signals and routing the hexaphonic signal through a 13-pin output. Their own explanation notes that an external converter analyzes signal frequency to turn those signals into MIDI. Therefore Ghost does not itself solve physical fret/contact identity.

Its important difference is that the six separate piezo channels may be useful as a raw, physically independent per-string vibration/excitation plane if they can be captured directly before pitch-to-MIDI conversion. That still requires proof of direct raw-channel access, capture topology, timing and failure-state observability.

Document sources reviewed:
- Graph Tech, “Ghost Hexpander Review” — https://help-center.graphtech.com/en-US/ghost-hexpander-review-764628
- Graph Tech Ghost Hexpander product pages — https://graphtech.com/products/ghost-hexpander-basic-preamp-w-traktion

Result: not a complete reference system. Keep only as a possible excitation-plane component for later architecture design; no purchase yet.

### FretTraX — physical pitch-state precedent, but `DOCUMENT_REJECTED_FOR_CURRENT_PROCUREMENT`

FretTraX is the strongest commercial precedent found for the required pitch-state concept. Its developer described the system as fret scanning and specifically stated that left-hand string-to-fret touches trigger MIDI. That is materially closer to frozen physical pitch-state semantics than pitch-recognition products.

However:
- InnProcess states that the technology was sold to another musical-instrument company and no further guitar/bass retrofits are available;
- the developer stated that the implementation did not provide right-hand/pluck detection, so even the historical system would require a separate excitation plane.

Document sources reviewed:
- FretTraX — https://frettrax.com/
- FretTraX “Off and Running!!” discussion — https://frettrax.com/hello-world/

Result: useful architecture precedent, not a current procurement path.

### Open/research physical fret-sensing approaches — `CUSTOM_BUILD_LEAD`

Public technical work demonstrates that physical fret/string/contact sensing is feasible without pitch recognition:
- conductive-string/fret scanning has been prototyped by scanning individual strings against conductive frets;
- ElektroCaster describes touch-sensing frets plus a separate per-string signal path and open hardware approach;
- “Let's Frets!” demonstrated per-string/per-fret capacitive sensing using six sensing regions per fret;
- FretTraX historically demonstrated low-latency string-to-fret touch scanning.

These are not turnkey authoritative holdout products. They support the engineering feasibility of a custom or hybrid pitch-state plane whose raw contact states and clock can be fully controlled and preserved.

Sources reviewed:
- PJRC, “ElektroCaster” — https://www.pjrc.com/elektrocaster/
- CHI 2021, “Let's Frets! Assisting Guitar Students During Practice via Capacitive Sensing”
- Nerd Club guitar tutor physical string/fret scanning explanation — https://nerdclub-uk.blogspot.com/2015/03/guitar-tutor-project-explained.html

## Architecture consequence

The best current direction is not one commercial MIDI guitar. It is a **hybrid/custom reference apparatus** with logically separate planes:

1. **Pitch-state plane:** custom physical string/fret/contact sensing with raw state access and deterministic string/fret mapping.
2. **Excitation plane:** separate per-string physical vibration/force/acceleration/piezo evidence capable of same-pitch reattack detection; a raw hexaphonic piezo bridge is one plausible component class.
3. **Evaluated DI plane:** ordinary clean magnetic DI remains separate and is never an input to reference truth.
4. **Clock plane:** common hardware clock where possible, otherwise microcontroller/reference ticks plus immutable hardware sync pulses captured in the evaluated/reference acquisition system.

## Procurement decision after screen

No screened commercial MIDI product justifies purchase as the authoritative reference system.

The next justified engineering work is to freeze a **custom/hybrid prototype topology V1 and minimum bill-of-material requirements**. Procurement becomes necessary only for components in that frozen topology whose required properties cannot be established without a bench sample.

This screen does not claim exhaustive proof that no future/current product can qualify; it records the initial current document/API result under the frozen qualification gate.

## Authority boundary

No real holdout exists. No correctness/model output was used. No product purchase or vendor/performer contact has occurred.

Keep:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Archived V143/Gomyway remains untouched and closed.
