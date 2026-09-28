# Astra source-domain simulator training failure analysis V1

Date: 2026-09-28  
Status: **POST-HOC DESCRIPTIVE REVIEW ONLY — NO PARAMETER TUNING / NO NEW MODEL**

## Frozen result

Source-domain training V1 completed one bounded synthetic-only execution:
- run **36476678125**
- job **109112023738**
- launch head `a47bd80c71e275c9523744c348c7c559a557dcbf`
- workflow conclusion **SUCCESS**
- scientific gate **FAIL**
- artifact **10993997488**
- artifact digest `sha256:06015a175a2e84b5094b4ffe9dbd58196be14c39b8e25025fbdf3efb65007c3a`
- artifact `result.json` SHA-256 `3e769072bf5bd906318bfd78ae2f7b126e81f6f0d39dd183dbf4b1f9a33fdacf`

Frozen repository result:
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_RESULT_V1.json`

No P1/P2/P3 data were accessed.

## What happened

The intervention improved source-domain challenge **precision** in all three paired seeds:
- mean precision delta **+0.1083**.

Challenge F1 was positive in all three seeds:
- seed deltas **+0.0129, +0.00066, +0.0450**;
- mean **+0.0195**.

But challenge **recall fell in every seed**:
- deltas **-0.0543, -0.0465, -0.0465**;
- mean **-0.0491**.

The intervention therefore missed both the preregistered mean-benefit floors and the all-seed positive-recall criterion.

Ordinary synthetic competence also regressed:
- onset F1 mean **-0.0303**;
- onset recall mean **-0.0568**;
- joint admission mean **-0.0388**;
- one seed ordinary F1 loss **-0.0530**;
- one seed joint-admission loss **-0.0543**.

The ordinary legato family lost more than 0.15 F1 in two seeds:
- **0.3091** loss in seed 20260927;
- **0.3333** loss in seed 20260929.

## Prediction-count tradeoff

The challenge improvements came from fewer false positives at the cost of true positives.

Seed 20260927:
- control challenge TP/FP/FN: **80 / 46 / 49**;
- intervention: **73 / 26 / 56**.

Seed 20260928:
- control: **82 / 32 / 47**;
- intervention: **76 / 20 / 53**.

Seed 20260929:
- control: **84 / 56 / 45**;
- intervention: **78 / 26 / 51**.

The same direction appears on the ordinary clean test: intervention precision rose modestly in every seed while recall fell in every seed.

This is consistent with a more conservative onset decision pattern under the fixed decoder/0.50 threshold. It does not establish why the learned logits shifted.

## Frozen feature-coverage description

Using only the already-frozen control/intervention/challenge arrays, median prepared-CQT positive flux at labeled attack frames was compared by family.

| Family | Intervention train / control train median flux | Challenge test / control test median flux |
|---|---:|---:|
| chords | 0.833 | 0.560 |
| isolated | 0.823 | 0.376 |
| legato | 0.859 | 0.390 |
| mixed | 0.739 | 0.590 |
| palmmute | 0.846 | 0.566 |
| repeated | 0.818 | 0.472 |
| scales | 0.852 | 0.461 |

Thus the randomized training package typically softened median onset flux by about **14–26%**, while the single fixed challenge profile softened it by about **41–62%** depending on family.

This is descriptive post-hoc evidence only. It does not authorize changing the challenge or enlarging the training ranges.

## What this suggests — and what it does not

The frozen challenge combines several difficult-but-predeclared source conditions simultaneously. Its individual parameter values lie within or near the frozen source-domain ranges, but their fixed co-occurrence produces a stronger prepared-feature onset shift than the typical randomized training examples.

That makes **joint coverage of source conditions** a plausible issue. It is not proven to be the only cause:
- legato ordinary regression is substantial even though legato's mean feature-shift magnitude is not uniquely the largest;
- the frozen loss/sampler may also encourage conservative behavior under broader source variation;
- the current MLP architecture may still lack useful invariances.

Do not infer that simply making attacks softer, widening parameter ranges, lowering the threshold, or increasing onset loss would solve the problem.

## Scientific decision

Reject the exact V1 source-domain training package under its frozen gate.

Do not:
- rerun V1;
- choose the strongest seed;
- lower the 0.50 threshold;
- relax the challenge;
- widen simulator ranges after seeing this result;
- increase onset loss/sampler weights post hoc;
- change architecture in the same follow-up;
- reopen P1/P2;
- open P3.

## Next justified work

The next step should be **model-free joint-coverage analysis/design only**, using the existing deterministic simulator specification and frozen synthetic arrays.

The purpose is to answer whether the challenge represents a rare/extreme *combination* of otherwise admitted source conditions, and whether the intervention package gives balanced coverage across the source-domain axes and musical families.

A future coverage review may inspect:
- deterministic simulator parameter draws across the 210 training rows;
- marginal and joint occupancy of attack-rise, coloration, nonlinearity, noise and dynamics axes;
- family-conditioned coverage;
- prepared-CQT onset-flux and feature-shift distributions;
- whether the fixed challenge lies inside the prospective parameter envelope but at an extreme joint corner.

It must **not** choose new training ranges or a new challenge from the failed model result.

No further model run should be proposed until that model-free coverage review is frozen.

## Resume instruction

Perform a model-free source-domain joint-coverage review only. Use no P1/P2/P3 data, run no model, perform zero optimizer steps, and do not change thresholds, simulator ranges, challenge parameters, architecture, loss or sampler.
