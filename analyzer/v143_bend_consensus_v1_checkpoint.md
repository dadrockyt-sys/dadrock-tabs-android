# V143 Rhythm bend consensus v1 — frozen checkpoint

Status: GREEN on real GOMYWAY audio before any professional-reference scoring.

Real-audio smoke summary:

- success: true
- noteCount: 358
- bendEventCount: 8
- bendReleaseCount: 2
- bendAmountCounts: 1 semitone = 3, 2 semitones = 2, 3 semitones = 3
- bendViewAgreementCounts: 2 views = 8
- singleViewBendsRemaining: 0
- strictDualViewConsensus: true
- professionalReferenceUsed: false
- runtimeLabelsRequired: false

Freeze rules:

1. Frozen V143 attack timing, score/rank/selection, pitch evidence and string/fret mapping are untouched.
2. Bend evidence is appended only downstream of frozen V143 event assembly.
3. Production has two independently separated rhythm-guitar carriers; every retained audio-derived bend must agree across both views.
4. Single-view bends are rejected and their bend metadata/techniques are removed without deleting the underlying V143 note.
5. Bend amount and release state remain evidence-derived from uploaded audio only.
6. Professional human reference remains excluded from runtime and from this tuning stage.

This checkpoint is the rollback anchor for all later technique work.
