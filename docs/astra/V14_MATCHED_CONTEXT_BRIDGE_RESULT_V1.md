# V14 matched-context bridge result V1

Date: 2026-09-29 UTC  
Status: **COMPLETE — FAILED FROZEN MATERIAL-RECOVERY GATE**

## Provenance

- workflow run: **36590057639**
- job: **109480499261**
- launch identity: `v14-matched-context-v1-20260929-02`
- launch commit: `e6b3085493b90cecd3ce56d498609ce1afaf54b7`
- artifact: **11043457682**
- artifact digest: `sha256:bc69dfbc4de527e2cef9c85b7f0cc29bca27aea16f16f799222d7ef6de9f02fb`
- workflow blob: `78a41f71f2c0ea66f37882bc8ef7ca82fc7bc6a8`
- runner blob: `68fd78964acc474337988182fc7c619adff691b2`
- contract blob: `5984ccd902713e2e1147b7f683e77c8166d46c90`

The earlier run **36546933952** is not a scientific V14 result. It used the wrong batch root and a non-parity runtime, failed the control reproduction guard, and was subsequently repaired before this fresh explicitly authorized execution.

## Control reproduction

The corrected run exactly reproduced the successful historical 2-second comparator:

- precision **0.8269230769**
- recall **0.6666666667**
- F1 **0.7381974249**
- negative-only FP/s **0**
- state admission **0.2945736434**
- onset admission **0.6201550388**
- joint admission **0.2868217054**

All control reproduction checks passed.

## V14 bridge on the common comparator population

- precision **0.4968944099**
- recall **0.6201550388**
- F1 **0.5517241379**
- negative-only FP/s **0**
- state admission **0.2868217054**
- onset admission **0.5736434109**
- joint admission **0.2713178295**

Versus reproduced control:
- precision **-0.3300286670**
- recall **-0.0465116279**
- F1 **-0.1864732870**

## Recovery versus V9 failure

Frozen V9 common result:
- precision **0.3244274809**
- recall **0.6589147287**
- F1 **0.4347826087**

V14 therefore recovered:
- **38.54%** of the original V9 F1 deficit
- **34.32%** of the original V9 precision deficit

This is meaningful improvement over V9, but below the prospectively frozen 50% material-recovery requirement.

## Frozen gate result

Required:
- F1 >= **0.5864900168**
- precision >= **0.5756752789**
- recall decline vs successful comparator <= **0.05**
- negative FP/s <= **0.10**

Observed:
- F1 **0.5517241379** -> **FAIL**
- precision **0.4968944099** -> **FAIL**
- recall decline **0.0465116279** -> **PASS**
- negative FP/s **0** -> **PASS**
- exact 500 updates/model -> **PASS**
- exactly 2 models -> **PASS**
- finite metrics -> **PASS**
- no threshold search -> **PASS**
- no scientific retry -> **PASS**

**Overall V14 result: FAIL.**

## Bridge-own test

For completeness, the bridge-trained model on the bridge-domain test produced:
- precision **0.4466666667**
- recall **0.4751773050**
- F1 **0.4604810997**
- negative-only FP/s **0**

This does not alter the primary decision because the frozen common comparator population is the primary gate.

## Dataset/training identity

Control render:
- 294 examples
- 588 s
- 87 frames/clip
- 735 attack groups
- 903 attacked note labels
- 0 state truncations

Bridge render:
- 294 examples
- 588 s
- 87 frames/clip
- 819 attack groups
- 987 attacked note labels
- **384 deterministic state truncations**

Training:
- 500 updates/control
- 500 updates/bridge
- 64,000 sampled frames/arm
- 16,000 sampled attack frames/arm
- control attacked-note labels sampled: **19,702**
- bridge attacked-note labels sampled: **19,294**

Stratum pool sizes:

Control:
- positive onset 525
- active non-onset 8,220
- negative-structure inactive 4,635
- other inactive 4,890

Bridge:
- positive onset 585
- active non-onset 7,440
- negative-structure inactive 4,559
- other inactive 5,686

## Interpretation

The 2-second matched-context bridge substantially improved the V9 common-population failure, which supports the recovery review's conclusion that clip/context construction was an important part of the regression.

However, it did **not** restore enough performance to satisfy the frozen recovery gate. Even after returning to 2-second context, precision remained far below the successful comparator.

This means the failure cannot be explained solely by the 4-second tail/context geometry. The bridge still changes several joint properties, including attack density, state truncation behavior, family-conditional event structure, and sampler-pool geometry. The **384 deterministic state truncations** are especially important evidence that the bridge's denser short-gap timing conflicts strongly with historical state-duration semantics.

That is a structural generator-design issue, not a reason to keep tuning one sampler statistic at a time.

## Stop rule applied

Per the frozen recovery strategy:

- do **not** open V15 or V16 automatically;
- do **not** continue serial synthetic micro-optimization;
- do **not** change thresholds/losses/steps to chase a pass;
- do **not** run V2B;
- do **not** access P1/P2/P3 automatically.

The next authorized work is documentation/review only: prepare one decision brief choosing among:
1. larger synthetic-generator redesign;
2. separately authorized independent real-development evidence;
3. pause this model line.

No new empirical project is open.
