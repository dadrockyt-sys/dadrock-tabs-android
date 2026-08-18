# V143 deterministic separator repeatability checkpoint

Status: GREEN on real GOMYWAY audio before professional-reference scoring.

Seeded two-pass full-separation diagnostic:

- deterministic seed: 143
- Demucs shifts preserved: 1
- pass 1 noteCount: 358
- pass 1 bendCount: 13
- pass 1 legatoCount: 12
- pass 2 noteCount: 358
- pass 2 bendCount: 13
- pass 2 legatoCount: 12
- carrierAExact: true
- carrierBExact: true
- frozenNoteFingerprintExact: true
- structuralNoteFingerprintExact: true
- bendFingerprintExact: true
- legatoFingerprintExact: true
- customerOutputExact: true
- allExact: true
- referenceFree: true
- professionalReferenceUsed: false
- runtimeLabelsRequired: false
- productionSeparatorModified: false

Promotion rule:

The frozen separator graph remains unchanged: direct Demucs6s Guitar plus BS-RoFormer Instrumental -> Demucs6s Guitar, with Demucs shifts=1, overlap=.10, segment=6. Determinism is introduced only by seeding Python, NumPy and Torch RNG state at the audio-separator subprocess boundary before inference. Seed 143 is the production candidate.

This checkpoint is the rollback anchor for deterministic production-separator promotion and later technique/render work.
