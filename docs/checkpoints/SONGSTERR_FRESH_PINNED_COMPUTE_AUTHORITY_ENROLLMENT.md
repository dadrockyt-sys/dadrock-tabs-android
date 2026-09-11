# Songsterr Fresh — Policy C Authority Enrollment Runbook

Status: READY FOR HOST PROVISIONING / AUTHORITY STILL UNENROLLED
Branch: `songsterr-fresh-pipeline-v1`
Authority ID / custom runner label: `songsterr-fresh-authority-v1`

This runbook turns one persistent Linux x64 machine into the sole Policy C model-output authority. It is intentionally fail-closed. A cloud VM is acceptable as a reproducibility surface only because every authority canary re-verifies the enrolled hardware/software fingerprint before any Demucs or Basic Pitch execution. If the provider migrates the VM onto a materially different CPU/kernel/toolchain surface, the fingerprint changes and authority stops.

Policy C is a reproducibility boundary, not a security attestation. It does not assert that the underlying cloud host is physically immutable or uncompromised.

## 1. PROVISION ONE PERSISTENT HOST

Recommended initial target:
- DigitalOcean persistent Droplet (not an ephemeral/autoscaling pool)
- Ubuntu 22.04 LTS x64
- CPU-only execution
- at least 4 vCPU and 8 GB RAM; 8 vCPU / 16 GB RAM is preferred for the Demucs CPU canary
- enough local disk for the OS, Python environment, model cache, source/stems, and GitHub runner workspace

Do not create multiple authority-labeled runners. Policy C is intentionally one enrolled compute surface at a time.

If the Droplet is rebuilt, resized onto a different CPU surface, its kernel/libc/toolchain changes, the authority venv changes, or the GitHub runner software is deliberately updated, treat that as possible authority drift and re-enroll before trusting model output.

## 2. INSTALL HOST PREREQUISITES

On Ubuntu 22.04, install the host prerequisites before enrollment. Keep normal OS administration outside model runs; model runs themselves must not install packages.

Required commands/software:
- `git`
- `curl`
- `ffmpeg`
- Python 3.10 with `venv`
- Node.js 22.x

After Node 22 is installed, verify:

```bash
python3.10 --version
node --version
ffmpeg -version | head -n1
git --version
curl --version | head -n1
```

Python must report 3.10.x and Node must report v22.x.

## 3. BUILD THE DEDICATED AUTHORITY VENV ONCE

Check out the fresh branch on the host or copy the bootstrap script from the branch, then run it with sufficient permission to create `/opt/songsterr-fresh-authority`:

```bash
sudo bash scripts/songsterr-fresh/bootstrap_pinned_compute_authority.sh
```

The script creates:

```text
/opt/songsterr-fresh-authority/venv
```

and installs the branch-pinned model stack. It refuses to overwrite an existing authority venv. Rebuilding the venv after enrollment is a re-enrollment event.

The Policy C workflow prepends only that venv to the normal system tool paths and requires `python3` to resolve to `/opt/songsterr-fresh-authority/venv/bin/python3`.

## 4. REGISTER THE GITHUB SELF-HOSTED RUNNER

In GitHub, open:

```text
Repository → Settings → Actions → Runners → New self-hosted runner
```

Choose Linux x64 and follow GitHub's current download/install commands for the runner application. Do not copy the registration token into this repository, a script, issue, checkpoint, artifact, or chat transcript. Use it only on the authority host while it is valid.

During first-time `config.sh`, register against this repository and assign the custom label:

```bash
./config.sh \
  --url https://github.com/dadrockyt-sys/dadrock-tabs-android \
  --token <TIME_LIMITED_REGISTRATION_TOKEN> \
  --labels songsterr-fresh-authority-v1 \
  --disableupdate
```

GitHub automatically supplies the normal self-hosted OS/architecture labels; the workflow additionally requires the custom `songsterr-fresh-authority-v1` label.

`--disableupdate` is deliberate: silent runner application updates would otherwise alter the execution surface. GitHub still requires disabled-update runners to be updated within its supported update window, so a planned runner update must be treated as maintenance followed by a new authority probe/re-enrollment as needed.

Install and start the runner as a system service from the runner directory:

```bash
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

For Ubuntu/Debian systems using `needrestart`, follow GitHub's documented exclusion for the Actions runner service so package maintenance does not restart the runner in the middle of a workflow job.

## 5. RUN THE UNENROLLED PROBE

From GitHub Actions, manually dispatch:

```text
Songsterr Fresh Policy C Pinned Compute Authority
mode = probe
```

The workflow will route only to a runner with all of:
- `self-hosted`
- `linux`
- `x64`
- `songsterr-fresh-authority-v1`

The probe must pass:
- dedicated authority venv check
- Python 3.10 check
- Node 22 check
- exact named package-version check
- full installed Python-distribution lock generation
- NumPy/PyTorch build-configuration hashing
- CPU/kernel/libc/interpreter/toolchain fingerprint generation

The output artifact is `authority-probe.json`. A successful probe still does **not** enroll the machine and does **not** validate model evidence.

## 6. DELIBERATELY ENROLL THE EXACT FINGERPRINT

Review the probe artifact. Then update only these fields in:

```text
scripts/songsterr-fresh/pinned_compute_authority_v1.json
```

Change:

```json
"enrollmentStatus": "UNENROLLED"
```

to:

```json
"enrollmentStatus": "ENROLLED"
```

and set:
- `enrolledFingerprint` to the probe's exact `fingerprint` object
- `enrolledFingerprintSha256` to the probe's exact `fingerprintSha256`

Do not hand-edit individual fingerprint fields to make a machine fit. Enrollment binds to what the verified probe actually observed.

Commit the enrollment as a reviewed branch change.

## 7. RUN THREE SEPARATE AUTHORITY CANARIES FROM ONE SOURCE COMMIT

After enrollment, do not change the source commit between canaries. Manually dispatch `mode=canary` at least three separate times.

Every canary verifies the authority fingerprint **before** model execution and then requires the fixed:
- source fixture/blob
- decoded separation WAV identity
- frozen reference-blind structure identity
- Demucs 4.1.0 `htdemucs_6s` CPU path
- Demucs model asset SHA-256
- Basic Pitch 0.4.0 settings
- duration-free evidence boundary

Each run writes `authority-canary.json` with exact identities for:
- guitar stem
- note inference
- activation bundle
- decision surface
- canonical model evidence

## 8. AGGREGATE THE THREE CANARIES

Use:

```text
scripts/songsterr-fresh/aggregate_pinned_compute_authority_canaries.py
```

with at least three separate canary summaries. The aggregation succeeds only when all runs have:
- distinct workflow run IDs
- one source commit
- one enrolled authority fingerprint
- one fixed input identity
- exact stem identity
- exact note-inference identity
- exact activation-bundle identity
- exact decision-surface identity
- exact canonical-evidence identity and event count

Any difference fails closed.

Even a successful aggregation only establishes:

```text
pinnedAuthorityReproducibilityDemonstrated = true
```

It still does not automatically set `modelValidationComplete:true`, does not add duration authority, and does not make customer events eligible. Model-evidence validation remains a separate review step.

## 9. MAINTENANCE / DRIFT RULE

After enrollment, any of the following must be treated as an authority-change event unless the verifier proves the exact enrolled fingerprint is unchanged:
- Droplet rebuild/restore/resize/migration
- CPU model, flags, microcode, or logical CPU-count change
- kernel or libc change
- Python interpreter change
- Node or FFmpeg executable change
- any named Python package version change
- any installed Python distribution/version/RECORD/direct-url/installer metadata change
- NumPy or PyTorch build-configuration change
- deterministic environment change
- GitHub runner application update when the execution environment may have changed

The safe sequence is always:

```text
change → authority untrusted → probe → deliberate enrollment/re-enrollment → 3 exact canaries → separate validation review
```

There is no fallback to GitHub-hosted model output or to another un-enrolled machine.
