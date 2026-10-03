# YAMNet Recognizer Candidate V1

Date: 2026-10-02
Status: ZERO-SHOT FEASIBILITY PREPARED

YAMNet is the first independent recognizer candidate because the official TensorFlow implementation uses the Apache-2.0 license and its AudioSet class map contains direct guitar and bass classes relevant to this project.

V1 performs no training and freezes no cleanup threshold.

Evaluation set:
- 6 known guitar fixtures;
- 6 known bass fixtures;
- 2 known controls: drums and speech.

The first test asks:
- does guitar evidence rank above bass evidence on known guitar material?
- does bass evidence rank above guitar evidence on known bass material?
- how much guitar or bass evidence appears on the two controls?

No decision threshold for the "other" class is frozen in advance. The output is evidence only and must be reviewed before the recognizer can affect cleanup.
