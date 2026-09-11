# Songsterr Fresh — Policy C-S Codespaces Session Authority

Status: implemented and contract-tested; no real Codespaces session has been enrolled or qualified yet.

## Purpose

Policy C-S is a zero-cost-first authority mode for a personal GitHub Pro Codespaces account. It is an alternate execution-authority mode; it does not weaken or overwrite persistent Policy C.

Persistent Policy C remains `UNENROLLED`. Codespaces must never be written into `pinned_compute_authority_v1.json` as the persistent fixed-self-hosted authority.

Policy C-S instead treats exactly one active Codespaces Linux boot as one ephemeral authority epoch. The epoch expires fail-closed when that boot/fingerprint/source binding changes.

## Cost boundary

GitHub documentation checked 2026-09-10 states that personal GitHub Pro includes:

- 180 Codespaces core-hours per month
- 20 GB-month Codespaces storage

On the user-available 4-core Codespace, 180 core-hours corresponds to about 45 active wall-clock hours before paid compute usage. The measured full Songsterr Fresh workbench path took 283 seconds, so three qualification canaries should consume roughly 15 minutes plus setup/overhead, far below the monthly included compute allowance when quota remains.

Payment details are configured, so usage beyond included allowance can become billable. Use GitHub Budgets and alerts for Codespaces and enable **Stop usage when budget limit is reached** at a personally acceptable amount. Included-usage alerts at 90% and 100% are also recommended.

Stopped Codespaces stop compute usage, but Codespaces storage is metered while a Codespace exists. After required evidence is preserved, deleting an idle Codespace is the strongest no-cost storage strategy. Verify current GitHub billing UI/usage before relying on a zero-dollar outcome.

Official GitHub references:

- https://docs.github.com/en/billing/reference/product-usage-included
- https://docs.github.com/en/billing/concepts/product-billing/github-codespaces
- https://docs.github.com/en/billing/concepts/budgets-and-alerts
- https://docs.github.com/en/codespaces/troubleshooting/troubleshooting-included-usage

## Hard project boundaries

- Canonical branch: `songsterr-fresh-pipeline-v1`.
- Do not touch `main` / Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, or pro scorer.
- Keep `modelValidationComplete:false`.
- Keep customer-eligible events at `0`.
- Keep duration V2/V3 research paused.
- Basic Pitch is not ground truth.
- Policy C-S surface qualification alone does not advance delivery.

## Session identity

A real Policy C-S probe reuses the existing hardened Policy C compute/toolchain probe and requires its prerequisites to pass. The C-S session fingerprint then additionally binds:

1. exact `songsterr-fresh-pipeline-v1` Git commit,
2. clean Git worktree,
3. exact Policy C compute/toolchain fingerprint,
4. SHA-256 of Linux `/proc/sys/kernel/random/boot_id`,
5. Linux x64 Codespaces runtime,
6. at least 4 logical CPUs,
7. at least 4 GiB reported RAM.

The raw Linux boot ID is never written to evidence; only its SHA-256 is stored. No machine-id, network identity, or user identity is collected.

The source commit binding intentionally means code changes require a new authority epoch. A stop/restart/rebuild or any hardware/software/package/toolchain drift also requires a new epoch.

## Enrollment

Setup does not enroll anything. Enrollment is deliberately separate.

From a clean, up-to-date Codespace:

```bash
bash scripts/songsterr-fresh/codespaces_session_authority.sh probe
```

Review:

```text
/workspaces/.songsterr-fresh-session-authority/session-probe.json
```

The probe alone is non-authoritative and non-promotional.

Then explicitly create one session epoch:

```bash
bash scripts/songsterr-fresh/codespaces_session_authority.sh enroll
```

The underlying verifier requires the literal acknowledgement `SESSION_BOUND_AUTHORITY_EXPIRES_ON_RESTART`. The wrapper supplies it only because the user explicitly invoked the `enroll` command.

Enrollment alone does **not** qualify the surface.

## Three-canary qualification

Run:

```bash
bash scripts/songsterr-fresh/codespaces_session_authority.sh qualify
```

This executes three distinct local canaries with IDs 1, 2, and 3. Each canary:

1. verifies the exact enrolled session immediately before model execution,
2. runs the already-proven Codespaces workbench full path,
3. verifies the exact same session immediately after model execution,
4. validates authorized source identity and frozen reference-blind structure,
5. validates the exact Demucs asset,
6. validates note/activation/evidence same-inference binding,
7. validates decision-surface non-promotional guards,
8. requires duration-free evidence,
9. records exact fixed-input and model/evidence output identities.

Aggregation requires all three canaries to have:

- distinct local execution IDs,
- the same authority epoch,
- the same session fingerprint,
- the same Linux boot binding,
- the same source commit,
- the same decoded separation WAV identity,
- the same fixed structure/model identities,
- exact guitar-stem identity,
- exact note-inference identity,
- exact activation-bundle identity,
- exact decision-surface identity,
- exact canonical-evidence identity,
- exact event count.

Any drift fails closed.

A green aggregate sets only:

```text
sessionAuthoritySurfaceQualified=true
```

It does **not** set `modelValidationComplete`, does not authorize customer delivery, and does not resume duration work.

## Lifetime and re-enrollment

Qualification is valid only while the current exact session fingerprint continues to verify.

Stopping, restarting, rebuilding, changing source commit, changing packages/toolchain, or changing hardware/OS fingerprint causes verification failure. A fresh enrollment creates a new authority epoch and must start qualification from zero.

A new epoch does not inherit prior model-validation status or customer-delivery eligibility. This prevents a new stable-but-different Codespaces surface from silently becoming equivalent to the prior authority surface.

Manual expiry is available with:

```bash
bash scripts/songsterr-fresh/codespaces_session_authority.sh expire
```

## Current implementation

- `scripts/songsterr-fresh/codespaces_session_authority.py`
- `scripts/songsterr-fresh/codespaces_session_authority.sh`
- `scripts/songsterr-fresh/run_codespaces_session_authority_canary.sh`
- `scripts/songsterr-fresh/build_codespaces_session_authority_canary.py`
- `scripts/songsterr-fresh/aggregate_codespaces_session_authority_canaries.py`
- `scripts/songsterr-fresh/qualify_codespaces_session_authority.sh`

Contract/self-test workflow run `34560456258` passed before real model qualification. The one-shot CI helper is not part of the permanent design.

## After a green session qualification

Do not stop the Codespace immediately if the next model-evidence review will use this authority epoch. Keep the exact session active, perform the separate model-evidence validation review, and preserve only the needed evidence. Stopping the Codespace deliberately ends the epoch.

Even after exact three-canary qualification, the standing project state remains:

```text
modelValidationComplete=false
customerEligibleEvents=0
duration research paused
```
