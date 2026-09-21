# Guitar-TECHS V2 CPU Budget V1

Synthetic benchmark run: `35630098935`

All measurements use the exact frozen Python 3.10.15 / PyTorch 1.11.0+cpu / NumPy 1.21.6 runtime and pinned TabCNN source, with random synthetic 200-frame sequences only.

| Sequence microbatch | Effective-step median | Peak RSS |
| ---: | ---: | ---: |
| 1 | 7.60 s | 704,840 KiB |
| 2 | 7.91 s | 930,976 KiB |
| 4 | 8.05 s | 1,436,432 KiB |
| 8 | 17.70 s | 2,235,116 KiB |

Microbatch 1 is both fastest and lowest-memory, using gradient accumulation to preserve an effective batch of 32 sequences.

Frozen V2 budget:
- 200 frames/sequence
- 32 effective sequences/batch
- sequence microbatch 1
- 1,000 performance-balanced epochs/fold
- 50 validation checkpoints (every 20 epochs)
- no dropped performance tail
- max 2,000 optimizer steps/fold
- P1 exposure: 8.2M supervised frames (102.5× V1)
- P2 exposure: 8.0M supervised frames (100× V1)
- public CPU runner timeout cap: 345 minutes/fold

Training-only synthetic estimate is ~2.70 h for P1 and ~2.64 h for P2 using per-sequence scaling from the benchmark, leaving bounded room for feature preparation and validation inside the runner cap.

Receipt: `docs/astra/GUITARTECHS_V2_CPU_BUDGET_V1.json`  
SHA-256: **`8705df7cde4456dc17b5973d84404981387a322ea195a3f995a72ae6b236b430`**

No real media or P3 material was used.
