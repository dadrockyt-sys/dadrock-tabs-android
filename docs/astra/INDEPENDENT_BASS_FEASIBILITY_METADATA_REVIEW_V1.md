# Independent Bass Feasibility Metadata Review V1

Date: 2026-10-02
Status: preparation only; empirical execution disabled.

## T1 Basic Pitch
Authoritative upstream review establishes:
- current release: basic-pitch 0.4.0;
- Apache-2.0 source license;
- model note range begins at MIDI 21 / A0 (27.5 Hz);
- official defaults: onset 0.50, frame 0.30, minimum note length 127.7 ms;
- input is resampled to 22050 Hz;
- Basic Pitch works best on one instrument at a time.

Therefore standard 4-string bass E1 is inside the model representation. This does not establish bass accuracy.

Frozen V1 settings:
- package: basic-pitch==0.4.0
- Linux TensorFlowLite path
- bundled ICASSP-2022 TFLite model
- historical repository-asserted model SHA-256: 3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676
- onset threshold 0.50
- frame threshold 0.30
- minimum note length 127.7 ms
- returned range MIDI 28-67 / E1-G4 (41.2034446141-391.995435982 Hz)
- multiple pitch bends false
- melodia trick true
- MIDI tempo 120

The old 82.406889 Hz historical filter remains historical and must not be reused for this bass study.

Remaining T1 blockers: immutable dependency lock/environment, model-hash re-verification in that environment, wall-time benchmark and peak-RSS benchmark.

## S1 separator
Provisional technical candidate: Open-Unmix UMX-HQ.
- repository: sigsep/open-unmix-pytorch
- release v1.3.0, release commit 814f144
- source code license MIT
- 44.1 kHz stereo four-stem model with a bass target
- published bass weight: bass-8d85a5bd.pth
- published size: 35.6 MB
- published MD5: 8cc37d31903fe48306468ee968f4b1b6
- Zenodo DOI: 10.5281/zenodo.3370489

It is not execution-eligible yet. The reviewed weight metadata does not state a permissive weight license, and UMX-HQ was trained on MUSDB18-HQ, whose source material includes non-commercial/academic restrictions. Do not infer weight-use rights from the MIT code license. No weights were downloaded.

Current decision: no execution-eligible S1 separator selected.

## Real-audio source rights
Do not use MedleyDB or MUSDB18/HQ as the default V1 source pool: their official documentation imposes non-commercial/academic-use restrictions.

Do not treat Cambridge-MT multitracks as automatically eligible. Its FAQ says research use was not specifically agreed with contributors and requires contacting contributors; AI-engine training requires individual licensing arrangements.

Preferred route: new collaborator recordings or directly permissioned contributor recordings, with explicit permission for private software development/evaluation and a paired isolated bass + matching mix.

## Twelve acquisition slots
Freeze three performer/session groups with four 15-30 second performances each:
- C01 P01 low-register sustained notes + rests — development
- C01 P02 repeated fingerstyle notes — development
- C01 P03 octave movement — development
- C01 P04 ordinary musical phrase — development
- C02 P01 low-register sustained notes + rests — development
- C02 P02 repeated picked notes — development
- C02 P03 octave movement — development
- C02 P04 ordinary musical phrase — development
- C03 P01 low-register sustained notes + rests — confirmation
- C03 P02 repeated notes — confirmation
- C03 P03 octave movement — confirmation
- C03 P04 ordinary musical phrase — confirmation

These are acquisition slots, not fabricated completed sources. Real identities, permissions, files and hashes are still required.

## Budget
Paid-spend ceiling remains CAD $0.
Runtime, memory and temporary-storage ceilings remain unresolved and must not be invented.

## Next task
1. Fill the 12 slots with real permissioned source identities.
2. Resolve UMX-HQ model-weight use rights or reject it and review one alternate separator.
3. Freeze exact package/checkpoint SHA-256 values without touching study audio.
4. Benchmark T1/S1 on a permitted non-study synthetic smoke asset.
5. Freeze runtime/memory/storage ceilings.
6. Only then request one bounded empirical execution authorization.

No audio, corpus, checkpoint, model, inference, separation, training, decoder run, or workflow dispatch was performed by this review.
