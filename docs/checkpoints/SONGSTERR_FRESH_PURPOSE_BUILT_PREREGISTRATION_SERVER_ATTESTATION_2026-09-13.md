# Songsterr Fresh — Purpose-Built Preregistration Server Attestation

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: synthetic/reference-blind governance tooling only

## PURPOSE

The local Git-history preregistration proof is necessary but not sufficient as independent timing evidence because Git author/committer timestamps are self-authored metadata. This checkpoint adds a GitHub-hosted Actions attestation and server-metadata proof so a future real purpose-built capture must have an externally platform-timestamped preregistration run completed before any declared capture timestamp.

This does **not** establish physical source truth, structural suitability, model validity, correctness, or customer eligibility. It does not authorize procurement/contact/recording, Basic Pitch, V6, protected-song execution, or any real holdout access.

## HOSTED ATTESTATION GENERATOR

Generator:
`script/songsterr-fresh` is not used; the actual research path is:
`scripts/songsterr-fresh/purpose_built_capture_preregistration_attestation_v1.py`

Commit: `fde97b60ee991d625b558af1ae1c6b6d6f7a40c0`

Synthetic tests:
`scripts/songsterr-fresh/test_purpose_built_capture_preregistration_attestation_v1.py`

Commit: `dcb693ee184a73ada76c2ee20777eaad9d8779fa`

The generator validates the content-only capture plan + preregistration evidence and emits a fail-closed attestation payload binding:
- repository;
- exact Actions run ID + attempt;
- exact run head SHA;
- workflow ref;
- repository-relative capture-plan path;
- canonical JSON SHA256 of the plan;
- planned slot count;
- frozen objective acquisition-failure vocabulary/criteria status;
- frozen false model/correctness policy boundary.

It does not contain or inspect real audio/reference bytes.

## READ-ONLY ATTESTATION WORKFLOW

Workflow:
`.github/workflows/songsterr-purpose-built-preregistration-attestation.yml`

Commit: `933b20b1bd70761717645ab3c7c6b15b1721a7eb`

Permissions: `contents: read` only.

The workflow has two intentionally distinct modes:
- `push` => synthetic CI only;
- `workflow_dispatch` => the only event eligible for a future real preregistration.

A real future capture must therefore deliberately dispatch this workflow with the frozen plan/evidence paths **before recording begins**. Ordinary push-mode test runs must never satisfy real preregistration.

Synthetic hosted run:
- run `34792723781`
- job `103819867260`
- event `push` (therefore synthetic-only, not real preregistration)
- head SHA `933b20b1bd70761717645ab3c7c6b15b1721a7eb`
- result `success`
- artifact `10328593887`
- artifact ZIP SHA256 reported by Actions: `bdc09570e3ef74b5fe3ca9a0f05b927b284a4c930480924bd70432215eba8a26`
- generated plan SHA256: `695e2c8ff1e383ed8d7d5fee8c4549a507b2b8f14058353ae6d6f00155532d35`
- markers:
  - `PURPOSE_BUILT_PREREGISTRATION_ATTESTATION_V1_SYNTHETIC_TESTS_OK`
  - `PURPOSE_BUILT_PREREGISTRATION_ATTESTATION_V1_OK`

This run is evidence that the hosted tooling functions, not authorization for capture.

## GITHUB SERVER PROOF

Verifier:
`scripts/songsterr-fresh/purpose_built_capture_preregistration_server_proof_v1.py`

Commit: `120473870a3103cc08073320cda6830b5bf9bd85`

Synthetic tests:
`scripts/songsterr-fresh/test_purpose_built_capture_preregistration_server_proof_v1.py`

Commit: `dbebaa49d4e76fc95f9d11845c21ad7a85ee2630`

For real use the CLI fetches GitHub Actions run metadata from the GitHub API with a token. The verifier requires all of the following:
1. the preceding local Git preregistration proof is valid;
2. cited run ID matches the fetched run;
3. repository matches `dadrockyt-sys/dadrock-tabs-android`;
4. event is exactly `workflow_dispatch`;
5. status is `completed` and conclusion is `success`;
6. workflow path is exactly `.github/workflows/songsterr-purpose-built-preregistration-attestation.yml`;
7. head branch is exactly `songsterr-fresh-pipeline-v1`;
8. run head SHA exists in local history;
9. preregistration commit is an ancestor of the run head;
10. run head is an ancestor of current HEAD;
11. plan at run head has the exact frozen SHA;
12. preregistration evidence at run head binds the same plan path/SHA;
13. attestation workflow exists at run head;
14. GitHub `created_at`, `run_started_at`, and `updated_at` are timezone-aware/valid;
15. every capture timestamp is strictly later than the latest of those server timestamps (effectively requiring the hosted attestation run to have completed before capture).

Push runs are explicitly rejected as real preregistration. Failed/incomplete runs, wrong repositories, wrong workflow paths, wrong run IDs, pre-preregistration run heads, and captures occurring before completion are covered by synthetic regressions.

## COMPREHENSIVE SYNTHETIC GATE

The branch contract workflow was expanded at commit `c5b960d89554c8474cecc95505021873af2b5411` to run six stages with full Git history:
1. base capture-manifest contract;
2. semantic guard;
3. content-only capture-plan binding;
4. local Git-history preregistration proof;
5. hosted-attestation payload tests;
6. GitHub-server proof tests.

Official synthetic run:
- run `34792825257`
- job `103820159787`
- conclusion `success`

All six markers were emitted:
- `PURPOSE_BUILT_CAPTURE_MANIFEST_CONTRACT_V1_SYNTHETIC_TESTS_OK`
- `PURPOSE_BUILT_CAPTURE_MANIFEST_SEMANTIC_GUARD_V1_SYNTHETIC_TESTS_OK`
- `PURPOSE_BUILT_CAPTURE_PREREGISTRATION_BINDING_V1_SYNTHETIC_TESTS_OK`
- `PURPOSE_BUILT_CAPTURE_PREREGISTRATION_GIT_PROOF_V1_SYNTHETIC_TESTS_OK`
- `PURPOSE_BUILT_PREREGISTRATION_ATTESTATION_V1_SYNTHETIC_TESTS_OK`
- `PURPOSE_BUILT_PREREGISTRATION_SERVER_PROOF_V1_SYNTHETIC_TESTS_OK`

## AUTHORITY BOUNDARY

For a future purpose-built population, a successful local Git proof is no longer sufficient by itself to advance to raw-byte structural audit. A real `workflow_dispatch` hosted preregistration run must also be completed before capture and pass the server proof.

Only after the full declaration/preregistration chain passes may the population advance to a **reference-blind raw-byte structural/alignment audit**. Even then:
- `authoritativeStructuralSuitabilityEstablished:false` until that audit itself passes;
- `basicPitchAuthorized:false`;
- `v6Authorized:false`;
- `correctnessAuthorized:false`;
- `modelValidationComplete:false`;
- `customerEligibleEvents:0`;
- `mayAdvanceDelivery:false`.

No real corpus media, Basic Pitch, V6, correctness, procurement/contact/recording, or archived V143/Gomyway/GOAT work occurred in this checkpoint.
