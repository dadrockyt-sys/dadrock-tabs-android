# Songsterr Fresh V6 — Purpose-Built Artifact-Proof Trust-Boundary Audit

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: synthetic/reference-blind governance only. No real corpus media, Basic Pitch, V6 correctness, protected-song execution, duration research, Modal, Vercel heavy-GPU, or L4 GPU.

## Authority

Canonical state required an audit of `scripts/songsterr-fresh/purpose_built_capture_preregistration_artifact_proof_v1.py` before adding more governance layers. The question was whether the production path itself obtains artifact metadata/content from the cited GitHub Actions run or instead trusts caller-supplied artifact JSON.

## Finding

**PASS — no concrete production trust gap found. No code change is justified.**

The production CLI path in `main()` does all of the following itself:

1. obtains run metadata from GitHub through `server.fetch_run_metadata(repository, run_id, token)`;
2. calls `fetch_run_artifacts(repository, run_id, token)`, whose URL is scoped to `https://api.github.com/repos/<repo>/actions/runs/<run_id>/artifacts`;
3. computes the only accepted artifact name as `purpose-built-preregistration-attestation-<run_id>`;
4. `_select_artifact(...)` requires exactly one artifact with that exact name;
5. downloads the ZIP through GitHub's artifact endpoint using the integer artifact ID returned by that exact run-scoped listing;
6. parses artifact bytes in memory rather than extracting paths to disk;
7. requires exact root entries `attestation.json` and `run-mode.txt` to each occur exactly once before reading them;
8. rejects a missing/invalid/non-object payload or invalid run-mode content;
9. requires artifact metadata `expired` to be exactly `false`;
10. checks the artifact's `workflow_run.id` against the expected run when GitHub includes that subobject;
11. requires the downloaded attestation payload to bind the expected repository, head SHA, run ID, run attempt, workflow ref, capture-plan path, capture-plan SHA, `attestationValid:true`, empty errors, and `mode: real_preregistration`;
12. separately requires `run-mode.txt` to equal `real_preregistration`;
13. composes with the existing server-integrity proof, including the hardened workflow/generator blob checks;
14. fail-closes `mayAdvanceToReferenceBlindStructuralAudit` unless all merged errors are empty and the server-integrity proof is valid.

The public `validate_artifact_proof(...)` helper accepts artifact/run objects as arguments because it is the pure validation layer used by synthetic tests. That is **not** a production bypass: the CLI does not accept artifact JSON/payload parameters from the caller and instead obtains metadata and bytes from GitHub before invoking the helper.

## High-value check review

- exact artifact name: enforced;
- exact cited-run association: enforced structurally by the run-scoped GitHub artifacts endpoint, plus exact run-derived artifact name, with an additional `workflow_run.id` cross-check when present;
- non-expired artifact: enforced;
- single unambiguous `attestation.json`: enforced at the exact root path used by the parser;
- single unambiguous `run-mode.txt`: enforced at the exact root path used by the parser;
- `real_preregistration` mode: enforced independently in JSON and text file;
- exact capture-plan path/SHA: enforced;
- run ID/attempt: enforced;
- head SHA: enforced;
- repository: enforced;
- workflow ref: enforced;
- server-integrity/hardened blob checks: inherited and required.

No ZIP extraction occurs, so path-traversal entries cannot overwrite local files. Extra unrelated ZIP members do not become trusted inputs because only the two exact root members are read and all authoritative identity fields are independently checked.

## Tests / prior CI

The synthetic test file `test_purpose_built_capture_preregistration_artifact_proof_v1.py` already covers:

- valid exact artifact/plan binding;
- rejection of a successful run reused for a different plan SHA;
- rejection of synthetic mode masquerading as real preregistration;
- rejection of wrong-name or expired artifacts;
- exact named ZIP payload requirements.

The canonical state records eight-stage synthetic CI run `34793985984`, job `103823432519`, as successful. No new code was introduced by this audit, so another CI run would add no new executable coverage.

## Decision

Do **not** add another wrapper or governance layer merely for duplication. The current production artifact-proof path is already anchored to GitHub-fetched run metadata, GitHub-fetched run-scoped artifact metadata, and GitHub-downloaded artifact bytes. Continue fail-closed.

This audit does not authorize any real preregistration, capture, media access, Basic Pitch, V6 correctness, model validation, customer eligibility, or delivery advancement.

Standing policy remains:
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed
