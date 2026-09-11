# Songsterr Fresh Codespaces Workbench

Status: implemented as a non-authority development/measurement environment.
Branch: `songsterr-fresh-pipeline-v1`

## Purpose

Use GitHub Codespaces as an on-demand, low-cost workbench for the fresh Demucs → Basic Pitch path before paying for a persistent Policy C authority host.

This does **not** replace Policy C authority. A Codespace may be stopped, restarted, rebuilt, or moved to a different underlying VM. Therefore no Codespaces fingerprint may be committed as the Policy C enrolled fingerprint under the current authority contract.

Hard guards remain unchanged:

- `modelValidationComplete=false`
- customer-eligible events = 0
- duration research remains paused
- V2 duration authority remains authoritative; V3 remains candidate-only
- no archived V143/Gomyway implementation/reference/pro scorer is resumed
- the authorized `gomyway` file is only the exact fixed audio fixture
- Codespaces output is measurement/development evidence only

## Cost strategy

Use the smallest Codespaces machine permitted by this configuration:

- 2 cores
- 8 GB RAM
- 32 GB storage

GitHub currently prices 2-core Codespaces compute at $0.18 per running hour, with storage at $0.07/GB-month after included quota. Personal accounts currently include monthly Codespaces quota (GitHub Free: 120 core-hours + 15 GB-month; GitHub Pro: 180 core-hours + 20 GB-month). Because a 2-core machine consumes two core-hours per wall-clock hour, that corresponds to up to about 60 wall-clock hours/month on Free or 90 on Pro if the personal-account quota applies to the codespace. Only running codespaces incur compute charges; a stopped codespace incurs storage only.

These prices/quotas are operational planning values and may change; check GitHub billing before creating long-running workbenches.

## Configuration

Select this dev-container configuration when creating the Codespace:

`.devcontainer/songsterr-fresh-workbench/devcontainer.json`

It intentionally coexists with the repository's pre-existing default dev-container configuration and does not overwrite it.

The workbench requests the cheapest 2-core/8-GB/32-GB host class and provides:

- Ubuntu 22.04 container base
- Python 3.10
- Node 22
- FFmpeg
- deterministic thread/hash environment matching the Policy C model path
- the same exact named Python package versions as the Policy C manifest
- persistent Codespaces caches under `/workspaces/.songsterr-fresh-workbench`

The bootstrap is:

`.devcontainer/songsterr-fresh-workbench/setup.sh`

It creates/reuses:

`/workspaces/.songsterr-fresh-workbench/venv`

and writes a safe workbench fingerprint probe to:

`/workspaces/.songsterr-fresh-workbench/workbench-probe.json`

The probe uses the existing fail-closed Policy C verifier only to validate prerequisites and fingerprint the workbench. It does not call `--verify-current`, does not enroll authority, and cannot advance model validation or delivery.

## Full 2-core / 8-GB measurement

After the Codespace finishes its automatic setup, run:

```bash
bash scripts/songsterr-fresh/run_codespaces_workbench_measurement.sh
```

This executes exactly one measurement-only full path:

1. validates the manifest and collects a fresh workbench fingerprint;
2. fetches and hash-verifies the authorized fixed audio fixture;
3. recreates and verifies the frozen reference-blind structure;
4. runs fixed Demucs `htdemucs_6s` on CPU with shifts 0, overlap 0.25, segment 7;
5. verifies the exact Demucs model asset;
6. runs one Basic Pitch inference and preserves activation/decision sidecars;
7. builds canonical duration-free evidence;
8. records wall-clock timings, max resident memory for Demucs/Basic Pitch, and output hashes.

Results are retained under:

`/workspaces/.songsterr-fresh-workbench/runs/<timestamp>-<commit>/`

The key file is:

`workbench-measurement-summary.json`

It hard-codes:

- `workbenchOnly=true`
- `authorityEligible=false`
- `probeAloneEnrollsAuthority=false`
- `modelValidationComplete=false`
- `mayAdvanceDelivery=false`
- `durationAuthorityChanged=false`
- `customerEligibleEvents=0`

This benchmark answers whether the cheapest Codespaces machine has enough memory and acceptable runtime before committing to any persistent infrastructure.

## Budget behavior

Stop the Codespace as soon as a measurement is complete. Closing the browser tab alone does not necessarily stop it; use the Codespaces Stop action. GitHub's default idle timeout is 30 minutes unless the account setting has been changed.

Keep model/package caches in the persistent `/workspaces/.songsterr-fresh-workbench` directory so repeated workbench sessions do not need to redownload everything unless the Codespace is deleted.

## Authority boundary

Under the current Policy C contract, the Codespace must never:

- be registered as `songsterr-fresh-authority-v1`;
- have its fingerprint committed as `enrolledFingerprint`;
- run the Policy C `canary` workflow as authority;
- promote a measurement result to customer eligibility;
- change duration authority.

If Codespaces later proves stable enough that we want it to become the release authority, that would require a new explicit authority-policy design and independent reproducibility proof. It is not implied by successful workbench measurements.
