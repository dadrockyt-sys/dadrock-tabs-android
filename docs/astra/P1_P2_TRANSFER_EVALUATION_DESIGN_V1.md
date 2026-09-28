# Astra P1/P2 transfer evaluation design V1

Date: 2026-09-28
Status: **IMPLEMENTATION FROZEN — P1/P2 ACCESS NOT AUTHORIZED**

## Purpose

Prospectively compare the frozen historical V3 baseline and one frozen synthetic S9/S11 candidate on the exact same P1/P2 prepared crops under evaluator V2.

P2 is the primary transfer population. P1 is compatibility context only because the V3 baseline was trained on the four P1 examples.

## Baseline

Frozen V3 checkpoint:
- run 36280547470
- artifact 10918434248
- model SHA256 `fba076f8b6e5fe177ba7b15e5d6780269194f530b2648037ac0763a4937eb67f`
- decoder V2
- thresholds 0.50 / 0.50
- zero retraining.

If the artifact expires, **do not retrain merely to recreate it**. Stop and resolve provenance/durability explicitly.

## Candidate

Single predeclared synthetic candidate:
- S9/S11 five-frame architecture;
- nonlinear 128-unit replacement state head;
- 30 unique training chord voicings;
- state active weight 9;
- onset pos_weight 8;
- onset loss multiplier 4;
- original 32/32/32/32 onset-aware sampler;
- Adam lr 0.003;
- exactly 500 steps;
- run seed **20260927**, chosen before P1/P2 access because it is the first frozen S11 seed;
- thresholds 0.50 / 0.50;
- no seed selection after real-data results.

## Population

Exactly eight direct-input crops:
- four P1 homologous captures;
- four P2 homologous captures;
- chords Drop3_7, scales Ab, allsinglenotes, PalmMute;
- 200 x 192 prepared features;
- zero unresolved labels;
- no substitution.

## Prospective evaluator

Use `evaluation_protocol_v2.py`.

Because prepared crop-local references omit source events crossing crop boundaries, apply a symmetric **50 ms interior edge guard** to both references and predictions:
- event onset in first 50 ms -> onset-ineligible;
- event offset in final 50 ms -> offset-ineligible.

This prevents ambiguous crop-boundary predictions from becoming asymmetric false positives while keeping interior scoring prospective and fixed.

No threshold search or post-result retuning.

## Frozen P2 transfer-evidence gate

All must pass:
1. candidate pooled P2 pitch-onset F1 >= **0.35**;
2. candidate pooled P2 recall >= **0.35**;
3. candidate pooled P2 precision >= **0.40**;
4. candidate P2 F1 gain over frozen V3 baseline >= **+0.25**;
5. candidate produces >=1 true positive in at least **3 of 4** P2 examples.

This is a development transfer gate only. It does not authorize P3, production, or customer delivery.

## Execution ceiling if authorized

- P1/P2 media access: exact eight allowlisted captures only;
- P3: sealed;
- candidate synthetic training: exactly 1 model x 500 steps;
- baseline training: 0 steps;
- transfer evaluation: 0 optimizer steps;
- threshold search: 0;
- automatic retries: 0;
- CPU-only GitHub Actions;
- <=120 job minutes;
- no Codespaces/Vercel.

## Authorization boundary

A future authorization must explicitly allow P1 and P2 media/source access for this exact evaluation and keep P3 sealed.
