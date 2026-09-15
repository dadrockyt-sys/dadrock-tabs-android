# Songsterr Fresh — Reference Evidence Derivation Replay Population V1 Result

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: SYNTHETIC POPULATION PASS / FINAL FUNCTIONAL SOFTWARE-LINEAGE GATE COMPLETE

## Authority

Gap review:
- checkpoint commit `0a50220a089f22733d7066e5772da7e73d71f557`.

Frozen preregistration:
- file `docs/checkpoints/SONGSTERR_FRESH_REFERENCE_EVIDENCE_DERIVATION_REPLAY_POPULATION_V1_PREREGISTRATION_2026-09-14.md`;
- commit `3aa4518bf1bc7b183f1e7025dbc1a4d182245db2`.

Checkpoint recording frozen method before implementation:
- commit `8f70849696b1e1a66157e68d29a541a60390a241`.

## Accepted implementation / tests / workflow

Implementation:
- file `scripts/songsterr-fresh/reference_evidence_derivation_replay_population_v1.py`;
- commit `fa3883a6089d93501c9e2a59e607b1a668eea259`;
- blob/content SHA `62c0a7ae08bd136fca9f72ad303203d214ea5782`.

Synthetic tests:
- file `scripts/songsterr-fresh/test_reference_evidence_derivation_replay_population_v1.py`;
- commit `8afd45fcb117bfa7914479c7cb68b9e25794d06b`;
- blob/content SHA `8f45d892cbcea707f1a14341cc143ca7335390b7`.

Workflow:
- file `.github/workflows/songsterr-fresh-reference-evidence-derivation-replay-population-v1.yml`;
- integration head `3f98ae44490b616e04dd003b46b76b5afcbfe433`;
- blob/content SHA `7e514084f9cf0919968e798a47216134be46cc48`.

## Official GitHub CPU run

- workflow run `34920805043`;
- job `104228294085` (`synthetic-derivation-replay-population-v1`);
- head SHA `3f98ae44490b616e04dd003b46b76b5afcbfe433`;
- conclusion `success`;
- GitHub-hosted Ubuntu 24.04 CPU;
- Python `3.12.14`;
- compile PASS;
- frozen synthetic tests ran before the official harness;
- **38/38 tests PASS** in `1.841 s`;
- executable two-attempt chain generation PASS;
- official frozen replay validator PASS;
- result summary PASS;
- artifact upload PASS.

Artifact:
- name `songsterr-fresh-reference-evidence-derivation-replay-population-v1`;
- artifact ID `10377539320`;
- uploaded ZIP size `1,670` bytes;
- uploaded ZIP SHA-256 `6970bc7c29d275a8cac221d3270a3ce5aacc0c62b219c021d929d81fc54975e5`;
- canonical result JSON SHA-256 `7fb41331f9b382987b579df228edfb504276317e3efb3428011f35c561151109`.

## Frozen official synthetic result

Top-level:
- `contract`: `songsterr-fresh-purpose-built-reference-evidence-derivation-replay-population-v1`;
- `contractValid:true`;
- `populationDerivationReplayEstablished:true`;
- `errors:[]`;
- `pythonRuntimeVersion:3.12.14`;
- `admittedBindingCount:2`;
- `submittedReplayCount:2`;
- `verifiedReplayCount:2`.

Verified upstream identities:
- Capture Manifest V2.3 result SHA `7b0cdc9ac655c95773dca1cd4c6b4b71215b3c3438db650a37bfca13fe4b941b`;
- Capture Manifest V2.3 admitted-population SHA `6f649fae8391178524acc817443945849b9105c5030fa6e1195dc664a23b4d53`;
- Structural Population Completeness result SHA `ee5209672b9d246e63caa6c797822376cb95b504bdd55c8eb42e10e7b2717970`;
- Structural Population Completeness identity SHA `7e4b7d08b7747d78d8a922821ac4ff3e79631c861b6f9e620c51f545a831fd6b`;
- Provenance V1 result SHA `ec45533583c90ba235508ed5e9d728f3b1d85d910f86f9f1c567908c013563a4`;
- canonical calibration-package binding SHA `46aaa082c4f1aada2006fdc55e75a14588fbc9f0fb1cd8ec6119bf60309ccead`.

Executable decoder identity:
- decoder ID `synthetic-executable-reference-decoder-v1`;
- software version `1.0.0-executable-synthetic`;
- decoder code SHA `5a695bab11b9b3dbe883298de9cd3444e491c4d9199220c550b6295bb37ff8dc`;
- decoder configuration SHA `3202544052895862da14adb3834f7f1b56b2ea3abd08864d5b51769c43791ce1`;
- supplied code/config bytes matched those package-bound identities before execution.

Attempt replay 1:
- attempt `slot-1-attempt-2`;
- structural binding SHA `ec392a58e2ad32a6d26b09eea4e33ffd95f3bef94b8356c5290beddb946dd41d`;
- raw pitch evidence SHA `95a4179b92d781da2159c49cf9e2e164534b5bd1df271b7abec1c2ecb2197fed`;
- raw birth evidence SHA `5b0be2f5a2e85f8d5d9c5598715d235a20ec51e357afafe59efcedf68aa2fcc4`;
- replayed pitch-latch SHA `62328b8a8345737e62c4f802cf9a91124d57a64d42d6d671241025de8c477f96`;
- replayed birth SHA `d2ae5e0c4d8080cb59a86c13651649e7b4dc587323ae3df36939db29c0885dac`;
- both replayed output identities exactly matched the V2.3-bound structural targets already structurally audited upstream.

Attempt replay 2:
- attempt `slot-2-attempt-1`;
- structural binding SHA `7cb3375e091199f20178e44fb9e325040b35abf2815662b34ee504346147f0ed`;
- raw pitch evidence SHA `01d06954ca03f06cfc0cd720d56488ec67c20aafd4bc7f6f8c5075de8877ac13`;
- raw birth evidence SHA `eb28c6bb85170813b5b7013afbc32f01a0f930ed0e1cd273c4f9227fc7345b8b`;
- replayed pitch-latch SHA `7cfd3e7c50fda9cc555c2aae9a131a13774db9ff8b642395a3737ab6a955dc24`;
- replayed birth SHA `612474fcf1c4ed5b6eb46e834e5cd13a38f6ce658fe81f32a5e67532276120e3`;
- both replayed output identities exactly matched the V2.3-bound structural targets already structurally audited upstream.

Population replay identity:
- identity version `reference-evidence-derivation-replay-population-v1`;
- `populationDerivationReplaySha256` = `3d560d13732be33bd84cd8e228e805ea454e2d86c56a89215c08739164be709c`.

This identity commits to the verified V2.3 result/population, structural-population completeness result/identity, Provenance V1 result/package, exact decoder code/configuration identities, and all admitted per-attempt raw-evidence/replayed-output identities.

## What the 38 tests establish

The accepted suite verifies the frozen preregistration categories, including:
- one- and two-admitted-attempt PASS paths;
- hash-before-parse boundaries for V2.3, completeness and Provenance results;
- upstream contract/pass/population/link/authorization failures;
- canonical Provenance package binding verification;
- V2.3 -> Provenance result/package/decoder configuration identity linkage;
- decoder UTF-8 and exact code/configuration SHA gates before execution;
- structural binding object/contract/canonical-hash/admitted-set/package/configuration requirements;
- raw pitch/birth evidence SHA gates before execution;
- missing/extra/duplicate/count-mismatched replay population failures;
- decoder nonzero exit, timeout and missing-output failures;
- exact output-byte SHA equality, including rejection of semantically equivalent but byte-different JSON output;
- replay population identity sensitivity to valid raw-evidence identity and completeness-result byte identity changes;
- replay input-order invariance and canonical result determinism;
- downstream authorization remaining false/zero on PASS.

The official fixture deliberately uses raw evidence bytes that are framed/different from the decoded structural output bytes and a newly built executable synthetic decoder package validated under the unchanged Provenance V1 contract. The completed identity-only Provenance fixture was not relabeled as executable proof.

## Interpretation boundary

This synthetic PASS closes the identified **raw evidence -> exact package-bound decoder execution -> exact decoded structural target bytes -> structurally audited complete population** software-lineage gap.

It proves the frozen software contracts can replay an immutable Provenance-bound executable decoder over the exact admitted synthetic raw evidence and reproduce the exact decoded stream identities previously bound/audited for every admitted synthetic attempt.

It does **not** prove:
- physical sensor accuracy;
- accuracy of any future real decoder;
- real calibration validity;
- real hardware qualification;
- real holdout capture authority;
- Basic Pitch/V6 correctness;
- model validation;
- customer eligibility or delivery authority.

## Authorization boundary

Unchanged after PASS:
- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched. Archived V143/Gomyway remains closed.

## Required next action

Perform the preregistered final no-gap software-lineage review. Do not create another software gate unless that review identifies a concrete, non-duplicative declaration/substitution/functional-lineage gap.

If no concrete software gap remains, freeze that no-gap conclusion and stop software gate creation. The next objectively necessary purpose-built route is physical procurement/calibration/capture, which remains budget-paused and unauthorized under checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58`.
