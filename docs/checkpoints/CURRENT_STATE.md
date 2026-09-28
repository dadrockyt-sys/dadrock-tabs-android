# Astra — current handoff

Updated: 2026-09-28 UTC (2026-09-27 America/Toronto)
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S5 COMPLETE — STATE WEIGHT 9 REJECTED; FROZEN GATE FAILED; OFFLINE REVIEW NEXT; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only code/tests/docs/metadata work is pre-authorized.

Explicit approval is required for model execution, Codespaces, and potentially billable Vercel operations.

## Canonical S5 execution

- run **36375196849**
- job **108779493106**
- launch head `1b0c481ba8fba60df34b52e193a7a54b797fbf86`
- workflow conclusion **SUCCESS**
- artifact **10949759498**
- artifact digest `sha256:5b68a700603d62d1b77930c34ba22fb930cdac1fd8551c435c7259a216f417ce`
- focused tests **4 / 4 passed**
- 294 clips / 588 s
- optimizer **500 + 500 = 1,000**
- no threshold search/retuning
- no automatic retry
- no P1/P2/P3, Codespaces, or Vercel

Frozen result:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S5_RESULT_V1.json`

## Scientific result — S5 FAIL

Weight 6 control:
- precision **0.9059**
- recall **0.5969**
- F1 **0.7196**
- onset+offset F1 **0.4821**
- repeated recall **0.5952**
- onset admission **0.5659**
- state admission **0.3333**
- joint admission **0.3178**

Weight 9 intervention:
- precision **0.8901**
- recall **0.6279**
- F1 **0.7364**
- onset+offset F1 **0.5470**
- repeated recall **0.6190**
- onset admission **0.6124**
- state admission **0.3333**
- joint admission **0.3333**

Key changes:
- state admission **+0.0000**
- joint admission **+0.0155**
- recall **+0.0310**
- F1 **+0.0167**
- onset admission **+0.0465**
- onset+offset F1 **+0.0649**

Only **7 / 14** frozen criteria passed. `s5GatePassed=false`.

Do not round F1 0.7364 into the 0.74 absolute requirement.

## Interpretation

Weight 9 produced modest event-level improvements but did not move exact state admission at all. It therefore does not support further automatic active-state weighting as the primary path.

Per the frozen S5 decision branch, the next offline review should consider one bounded **state-representation architectural** hypothesis rather than another weight increase.

## Exact next step

Offline review/design only.

No further model execution, P1/P2 transfer, P3, Codespaces, Vercel, threshold rescue, or extra optimizer steps without explicit authorization where required.
