# Open-Corpus V3 GuitarSet Development — NO DEVELOPMENT SIGNAL

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Final V3 development classification

**`NO_DEVELOPMENT_SIGNAL`** under the prospectively frozen V3 development qualification and selection contract.

This closes the current eight-configuration V3 selective-octave trigger family. None of the frozen configurations qualified. The sealed GuitarSet prospective-evaluation players `00/01/03` therefore remain sealed and **must not be run for this V3 family**.

This is a development result only. It does not modify V168, the frozen V168 Policy A/B logic, or the GOAT holdout plan.

## Frozen candidate source

Original candidate workflow head: `f494e5b2f586ec335b16dcabce687e63bb1f88fb`  
Original Actions run: `33581322528`  
Candidate job: `100096037798` — **SUCCESS**.

Authoritative frozen candidate identities:
- candidate artifact ID: `9828683652`;
- artifact name: `guitarset-v3-development-frozen-candidates`;
- artifact ZIP SHA256: `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`;
- candidate freeze manifest SHA256: `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- candidate file count: **177**;
- Basic Pitch baseline events: **29,245**;
- ordinary V2 proposal events: **10,693**;
- trigger-eligible events: **10,642**.

Development tracks were exactly the preregistered admissible set:
- player `02`: 59;
- player `04`: 58;
- player `05`: 60;
- total: **177**.

The three predeclared anomaly tracks were excluded. Prospective evaluation players `00/01/03` were absent from candidate generation.

Candidate generation was CPU/TFLite only. No reference was read and the candidate artifact is immutable for this study. **Do not regenerate it.**

## Mechanical recovery history

The original scorer job `100097954531` failed before references because `candidate-manifest-sha256.txt` contained the absolute temporary Job-A path. That failure was checkpointed at commit `63de07c41db5322b5e0330339552f14dfc677c78`.

The first scorer-only recovery, run `33582237435`, job `100098746109`, successfully rebound the original artifact and reverified every candidate hash, then failed on the first `import jams` because `jams==0.3.4` had resolved to NumPy 2.2.6 and JAMS 0.3.4 uses `np.float_`. The failure occurred before the first `jams.load` completed. That runtime failure was checkpointed at commit `b8933a36b6cea21e00c8c247f906b7c7e5ed5c58`.

The only runtime recovery change was prospectively frozen as `numpy==1.26.4` with unchanged `jams==0.3.4`. No scorer, trigger, candidate, threshold, split, matching, exclusion, or selection rule changed.

## Successful scorer-only runtime recovery

Recovery workflow creation commit: `fea2d10cdeeae39424abd6dd5cd94792d01614ce`  
Actions run: `33582451429`  
Job: `100099402236` (`Score frozen V3 candidates with NumPy 1.26.4`) — **SUCCESS**.

The successful job reverified before references:
- original candidate run/head;
- artifact ID/name/digest;
- candidate manifest SHA256;
- all **177** candidate-file SHA256 receipts;
- frozen scorer blob `19ef54155735a6ac1e65441250b47d1572ac0380`;
- frozen trigger blob `14ddd15fc29bfe947a4e3ce12050b10f43d2435f`;
- frozen candidate-generator blob `61068cee19132c40f3d0b15231d64ea3d428e1ca`;
- Basic Pitch unavailable in the scorer runtime;
- candidateRegenerated=false.

It then verified the frozen GuitarSet annotation archive and extracted exactly the same 177 development JAMS files, with no evaluation-player files and no excluded anomaly files.

Reference runtime:
- Python 3.10.21;
- NumPy 1.26.4;
- JAMS 0.3.4.

## Frozen development score report

Score report:
- file: `guitarset-v3-development-score.json`;
- SHA256: `80f68643e11644d085674ddbb1771d7bd6502bcc328c94d3cc356aea1a7af057`;
- `score-sha256.txt` SHA256: `99af9770e34cb8359d46d401f89f0394907896d50ab957be36db806fe849f4e8`.

Artifact:
- ID `9828894162`;
- name `guitarset-v3-development-score-runtime-recovery-report`;
- ZIP SHA256 `569252da6d45a38e6661a5f26feb1cbbda2c0971c54e979c30470037b2d1087b`.

Development reference event count: **28,115**.  
Event-count identity: **PASS**.

### Baseline

- primary 100 ms macro F1: **80.3621313923964%**;
- primary 100 ms micro F1: **76.62482566248256%**;
- primary micro precision: **75.14446914002394%**;
- primary micro recall: **78.16468077538681%**;
- primary TP/pred/ref: **21976 / 29245 / 28115**;
- strict 50 ms macro F1: **78.16769905338124%**;
- strict 50 ms micro F1: **74.51882845188284%**.

Baseline primary player micro F1:
- player `02`: **77.22190141214762%**;
- player `04`: **73.82177818145121%**;
- player `05`: **79.01368085221435%**.

### Frozen V3 configurations

| Config | Changed pitches | Primary macro F1 | Macro delta pp | Primary micro F1 | Micro delta pp | Strict50 micro delta pp | Player 02 delta pp | Player 04 delta pp | Player 05 delta pp | Qualified |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `C075-M005` | 5869 | 73.27485575264657% | -7.0872756397498335 | 67.06764295676429% | -9.557182705718276 | -9.330543933054386 | -12.788072864717293 | -8.083560399636681 | -7.808359919969718 | no |
| `C075-M010` | 4012 | 76.36052702588408% | -4.001604366512325 | 70.93096234309624% | -5.693863319386324 | -5.603207810320782 | -8.052916163578146 | -4.258754667474022 | -4.801816903693279 | no |
| `C075-M015` | 2685 | 78.22869254872845% | -2.1334388436679603 | 73.44839609483962% | -3.1764295676429413 | -3.1450488145048894 | -5.008136910074015 | -1.715612069835501 | -2.855134375168973 | no |
| `C075-M020` | 1732 | 79.24934653550362% | -1.1127848568927874 | 74.9442119944212% | -1.680613668061369 | -1.6596931659693155 | -2.9502861042574438 | -0.7266121707538815 | -1.3951224787757468 | no |
| `C100-M005` | 4881 | 74.94303135397419% | -5.419100038422215 | 69.19456066945607% | -7.430264993026498 | -7.259414225941427 | -10.362748700719195 | -5.822989201735794 | -6.132049964851575 | no |
| `C100-M010` | 3546 | 77.0982300171661% | -3.2639013752303043 | 71.86192468619247% | -4.762900976290098 | -4.700139470013937 | -6.793007506955746 | -3.4110404682611772 | -4.120478018709775 | no |
| `C100-M015` | 2457 | 78.53753426060162% | -1.824597131794789 | 73.83891213389123% | -2.785913528591337 | -2.7684797768479683 | -4.32568638773688 | -1.4633161772126329 | -2.617206510571549 | no |
| `C100-M020` | 1620 | 79.36093022561383% | -1.0012011667825789 | 75.09414225941423% | -1.5306834030683376 | -1.509762900976284 | -2.5933119848810975 | -0.6761529922292766 | -1.3518628670307749 | no |

Every configuration preserved event count, but **every non-identity qualification condition failed for every configuration**:
- primary macro gain was below +0.25pp;
- primary combined micro F1 regressed;
- at least one development player lost more than 0.10pp primary micro F1;
- strict50 combined micro F1 regressed.

`qualifiedConfigIds = []`.  
`selectedConfig = null`.

The most conservative configuration, `C100-M020`, changed the fewest pitches (1620 / 29245 = **5.539408445888186%**) and was the least harmful of the frozen family, yet still lost **1.0012011667825789pp macro F1**, **1.5306834030683376pp primary micro F1**, and **1.509762900976284pp strict50 micro F1**. This confirms that the frozen consensus/margin trigger family does not isolate a beneficial intervention subset on GuitarSet development.

## Scientific interpretation boundary

The current V3 trigger family is **closed / terminal**. Do not weaken its qualification gate, pick the least-bad configuration, or run it on the sealed evaluation players.

A future V4-style development generation may use this consumed development set for iterative hypothesis formation, but it must be explicitly separated from V3 and preregistered before any new development scoring. The prospective evaluation players `00/01/03` remain untouched so they can still serve as a future one-shot evaluation only after a genuinely frozen new design qualifies on development.

Do not reinterpret `NO_DEVELOPMENT_SIGNAL` as evidence that V2 itself is useless. The earlier controlled P1/P2 experiment showed that V2 is strong once a true octave ambiguity is known. This result says the V3 temporal-consensus + median-advantage gates are still not sufficient to identify those safe intervention cases from Basic Pitch proposals.

## Counters / isolation

- GuitarSet development score calls: **1**;
- GuitarSet prospective evaluation processed: **false**;
- GuitarSet prospective evaluation score calls: **0**;
- V168 prospective reference-facing score calls: **0**;
- V168 policies modified: **false**;
- GOAT holdout selection modified: **false**;
- GPU/CUDA/Modal: **none**;
- `main` / Production: **untouched**.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

## Next safe action

1. Keep GuitarSet players `00/01/03` sealed; do not run V3 prospective evaluation.
2. Preserve this V3 result as terminal for the eight frozen trigger configurations.
3. If continuing the public-corpus research lane, open a new V4 development-only hypothesis-generation phase using only `02/04/05` evidence. Freeze its exploratory question and data-use boundary before any new per-event reference analysis.
4. A new V4 candidate/evaluation design may reach the sealed players only after its feature logic, selection rule, scorer and prospective PASS/FAIL contract are frozen and the development gate is passed.
5. GOAT approval remains the independent primary path for V168.
