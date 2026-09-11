# Songsterr Fresh — OVHcloud Low-Cost Policy C Authority Runbook

Status: candidate provisioning runbook only; no authority host is enrolled by this document.

## Hard policy state

- Canonical branch: `songsterr-fresh-pipeline-v1`.
- Do not touch `main` / Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, or pro scorer.
- Keep `modelValidationComplete:false`.
- Keep customer-eligible events at `0`.
- Keep duration V2/V3 research paused.
- Codespaces remains workbench/measurement only and must not be enrolled as Policy C authority.

## Why VPS-1 is the first candidate

Completed Codespaces workbench measurement v2 on 4 cores / 8 GB showed:

- total wall time: 283 s
- Demucs wall time: 236 s
- Basic Pitch wall time: 11 s
- Demucs peak RSS: 2,492,104 KiB (~2.38 GiB)
- Basic Pitch peak RSS: 396,552 KiB (~387 MiB)
- frozen structure identity remained `fnv1a32:2f493225`

Therefore 4 GB RAM is the smallest practical authority-host target justified by observed capacity evidence. 2 GB is below the measured Demucs peak and is not acceptable. 8 GB is optional headroom rather than a demonstrated requirement.

Provider pricing checked 2026-09-10 from OVHcloud Canada:

- plan: VPS-1
- price shown: from CAD $6.20/month
- vCPU: 2 vCores
- memory: 4 GB RAM
- storage: 40 GB SSD NVMe
- public bandwidth: 500 Mbps
- traffic: unlimited
- daily backup: previous 24 hours included
- installation fees: free on OVHcloud developer VPS page
- Canadian VPS page identifies Beauharnois, Quebec as a Canadian VPS location

Always verify the checkout total before purchase because provider pricing/availability can change.

## Purchase configuration

Choose only:

- VPS-1
- Canada location; prefer Beauharnois if that is the listed Canadian VPS location at checkout
- Ubuntu 22.04 LTS x64 / amd64
- monthly billing unless a cheaper commitment is explicitly desired later
- no control panel image
- no Docker preinstall image
- no paid extra IPs
- no paid backup add-on beyond the included daily backup
- no paid monitoring/security add-ons required for Policy C

Use an SSH public key at provisioning time if OVHcloud offers that option. Never commit private SSH keys or registration tokens.

## First boot checks — before Policy C bootstrap

Connect by SSH as the provisioned administrator/root account and verify:

```bash
uname -m
cat /etc/os-release
nproc
free -h
df -h /
```

Required outcome:

- architecture: `x86_64`
- Ubuntu 22.04 LTS
- 2 logical vCPUs expected for VPS-1
- approximately 4 GB RAM
- enough free disk for repository, models, venv, and temporary Demucs output

If the host is ARM, below 4 GB RAM, or materially different from the purchased plan, stop. Do not adapt Policy C around it.

## Base packages

Ubuntu 22.04 should provide Python 3.10. Install/verify only the prerequisites needed by the existing authority bootstrap:

```bash
sudo apt-get update
sudo apt-get install -y python3.10 python3.10-venv git curl ffmpeg ca-certificates
python3.10 --version
ffmpeg -version | head -1
git --version
curl --version | head -1
```

Install Node.js 22 using the current official NodeSource/Node installation method used by the project runbook, then verify:

```bash
node --version
```

Do not install the Demucs/Basic Pitch Python stack globally.

## Clone only the fresh branch

```bash
git clone --branch songsterr-fresh-pipeline-v1 --single-branch https://github.com/dadrockyt-sys/dadrock-tabs-android.git
cd dadrock-tabs-android
```

Verify:

```bash
git branch --show-current
git rev-parse HEAD
```

The branch must be `songsterr-fresh-pipeline-v1`.

## Build the dedicated authority environment

Run the existing one-time bootstrap exactly as maintained in the repository:

```bash
sudo bash scripts/songsterr-fresh/bootstrap_pinned_compute_authority.sh
```

Expected dedicated environment:

`/opt/songsterr-fresh-authority/venv`

Do not rebuild or mutate this venv after enrollment without treating it as a re-enrollment event.

## Capacity rule for the 4 GB VPS

The first authority probe does not run Demucs/Basic Pitch. After deliberate fingerprint enrollment, the first canary will be the real capacity test on VPS-1.

If the first canary:

- completes normally: continue with the remaining exact canaries
- is killed by OOM or cannot complete because of sustained memory pressure: VPS-1 is inadequate; do not weaken checks, change model settings, add ad-hoc package changes, or promote partial outputs
- becomes impractically slow: record timing and review VPS-2 (4 vCores / 8 GB) only if needed

Do not add swap merely to force a passing authority result without a separate review. The point of this first candidate is to test whether the measured ~2.38 GiB Demucs peak fits cleanly in a fixed 4 GB surface.

## GitHub self-hosted runner

From GitHub repository Settings → Actions → Runners, create one Linux x64 self-hosted runner for this host.

Use the GitHub-provided current download/registration commands. Never commit or paste the temporary registration token into repository files.

Required custom label:

`songsterr-fresh-authority-v1`

Runner registration must include `--disableupdate` so automatic runner application updates cannot silently change the enrolled authority surface.

Install/start it as a service with the GitHub runner `svc.sh` commands and verify service status.

Only one runner carrying the authority custom label should be active at a time.

## Probe — still UNENROLLED

Manually dispatch:

`Songsterr Fresh Policy C Pinned Compute Authority`

with:

`mode=probe`

The workflow must run only on:

- `self-hosted`
- `linux`
- `x64`
- `songsterr-fresh-authority-v1`

Review `authority-probe.json`.

A probe does not enroll authority and does not authorize model output.

## Deliberate enrollment

Only after reviewing the safe probe:

1. copy its exact `fingerprint` and `fingerprintSha256` into `scripts/songsterr-fresh/pinned_compute_authority_v1.json`
2. change `enrollmentStatus` from `UNENROLLED` to `ENROLLED`
3. commit that explicit enrollment on `songsterr-fresh-pipeline-v1`
4. do not change model validation, customer eligibility, or duration state

## Exact canary sequence

From one unchanged source commit:

1. dispatch `mode=canary`
2. confirm the enrolled fingerprint verifies before model execution
3. repeat for at least three separate workflow run IDs
4. require exact identities for guitar stem, note inference, activation bundle, decision surface, and canonical evidence
5. aggregate with `aggregate_pinned_compute_authority_canaries.py`

Any fingerprint drift, source drift, package drift, tool drift, or output drift fails closed.

## What success means

Three exact canaries plus successful aggregation demonstrate reproducibility on the enrolled Policy C surface only.

They do NOT automatically:

- set `modelValidationComplete:true`
- create customer-eligible events
- resume duration research
- prove Basic Pitch is ground truth
- justify any threshold tolerance
- authorize hosted/Codespaces outputs

A separate model-evidence validation review is still required.

## Provider maintenance / migration

OVHcloud is a VPS provider and may perform infrastructure maintenance. Policy C does not assume the underlying virtual CPU identity is immutable forever.

Every authority canary verifies the enrolled fingerprint before model execution. If CPU identity, microcode, kernel, libc, executable hashes, Python distribution lock, or other enrolled fingerprint material changes, the workflow must fail closed. Review the change and deliberately re-enroll before further authority use.
