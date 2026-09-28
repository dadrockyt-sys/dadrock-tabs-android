# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S11 COMPLETE — ROBUSTNESS GATE FAILED; DIVERSITY EFFECT DIRECTIONALLY CONSISTENT BUT MAGNITUDE/JOINT EFFECT SEED-SENSITIVE; SYNTHETIC TUNING CLOSED; P1/P2/P3 SEALED**

## Standing authorization policy

User standing instruction: **"You do not need my authorization for these inexpensive runs going forward please continue"**.

Effective policy:
- routine GitHub work: pre-authorized;
- bounded inexpensive GitHub Actions model runs in the current synthetic workflow: pre-authorized;
- Codespaces and potentially billable Vercel work still require an explicit boundary decision;
- P1/P2/P3 real-data access still requires explicit authorization;
- production/deployment/main mutation remains outside the standing run authorization.

## Canonical S11 execution

- run **36380767479**
- job **108795887577**
- launch head `38d04c96afbc76e17cc12f6244a8a3cc59f89a66`
- workflow **SUCCESS**
- artifact **10952457629**
- artifact digest `sha256:3116ffec405cd5c86d068a2ee6c662a6fe03f337f08224501687b932258f1377`
- exactly 6 models
- optimizer **3,000 total = 500 x 6**
- no threshold search/retry
- no P1/P2/P3/Codespaces/Vercel

Frozen result:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S11_RESULT_V1.json`

## S11 result

30-voicing intervention had positive paired gains in all 3 seeds for:
- chord F1;
- chord recall;
- overall onset F1;
- overall onset recall.

Mean paired gains:
- chord F1 **+0.0649**
- chord recall **+0.1019**
- onset F1 **+0.0190**
- onset recall **+0.0543**
- state admission **+0.0258**
- joint admission **+0.0026**
- precision **-0.0458**

S11 robustness gate **FAILED**.

Failed frozen criteria:
- mean chord F1 gain >= +0.10;
- mean chord recall gain >= +0.12;
- mean onset F1 gain >= +0.04;
- mean onset recall gain >= +0.06;
- mean joint admission gain >= +0.03;
- no seed precision loss > 0.05.

Worst precision delta was **-0.1185**.

## Interpretation

Chord-voicing diversity is directionally consistent across the three seeds, but the effect magnitude and integrated state/joint behavior are not robust enough under the frozen S11 criteria.

Per the preregistered mixed/seed-sensitive branch:
- do not promote S9 as seed-robust;
- stop synthetic architecture/data tuning;
- document instability honestly.

Analysis:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S11_ROBUSTNESS_ANALYSIS_V1.md`

## Next boundary

A proposal for a tightly scoped P1/P2 transfer evaluation is prepared at:
- `docs/astra/P1_P2_TRANSFER_EVALUATION_PROPOSAL_V1.md`

**P1/P2 access is not authorized by the standing inexpensive synthetic-run policy.**
P3 remains sealed.

No more synthetic model tuning should run automatically from S11.
