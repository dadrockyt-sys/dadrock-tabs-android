# Songsterr Fresh — Low-Cost Policy C Authority Options

Updated: 2026-09-10 America/Toronto

This document is a cost/capacity decision record for the fresh workstream only. It does not enroll an authority, validate the model, change duration authority, or authorize archived V143/Gomyway implementation/reference/pro-scorer work.

## Measured requirement

The completed GitHub Codespaces workbench measurement v2 at source commit `3faf16b740846ebd3106d81cb1cf1dcefe1001d5` established the following capacity observations on the user-available 4-core / 8 GB Codespace:

- full measurement wall time: 283 s (4 min 43 s)
- frozen structure: 31 s
- Demucs: 236 s
- Basic Pitch: 11 s
- Demucs peak RSS: 2,492,104 KiB (~2.38 GiB)
- Basic Pitch peak RSS: 396,552 KiB (~387 MiB)
- frozen structure remained accepted and matched `fnv1a32:2f493225`

Therefore:

- 2 GB RAM is below the observed Demucs peak and is not an acceptable authority target.
- 4 GB RAM is the minimum practical target currently justified by measurement.
- 8 GB RAM is optional headroom, not a demonstrated requirement.
- Fewer/slower vCPUs may increase runtime but do not by themselves invalidate Policy C; the surface must instead be explicitly enrolled and then reproduce exactly under the existing fail-closed contract.

## Current provider comparison

Pricing below was checked against provider-owned pages on 2026-09-10 and can change. Taxes and optional add-ons are not included unless stated by the provider.

### OVHcloud Canada VPS-1 — current preferred budget candidate

Official OVHcloud Canada VPS page currently lists:

- 2 vCores
- 4 GB RAM
- 40 GB NVMe SSD
- Ubuntu 22.04 available at no OS surcharge
- Canadian VPS location available
- from CAD $6.20/month

Sources:
- https://www.ovhcloud.com/en-ca/vps/vps-canada/
- https://www.ovhcloud.com/en-ca/vps/os/

Why it is the current first candidate:

- clears the measured ~2.38 GiB Demucs peak with practical headroom
- materially cheaper than the DigitalOcean 4 GB option
- persistent VPS rather than an ephemeral/autoscaling pool
- Ubuntu 22.04 is directly supported, matching the existing Policy C runbook
- OVH documentation demonstrates Ubuntu 22.04 x86_64 VM environments

Policy C caveat: it is still virtualized hardware. Host CPU/kernel/microcode or other fingerprint fields may change after provider maintenance or migration. Existing Policy C behavior is intentionally fail-closed: any material fingerprint drift requires a new probe, deliberate re-enrollment, and three fresh canaries.

### IONOS Canada VPS M+ — promotional alternative

Official IONOS Canada page currently lists:

- 4 vCores
- 4 GB RAM
- 120 GB NVMe
- CAD $5/month for the first 3 months
- CAD $14/month shown regular price
- 1-year term for the promotion
- CAD $15 setup fee shown on the offer page

Source:
- https://www.ionos.ca/servers/vps

This is not as attractive as the headline $5 suggests once the setup fee, term, and post-promotion price are considered. It remains a fallback if OVH provisioning is unavailable.

IONOS Cloud Basic Cube S is a separate pay-as-you-go option currently listed at 2 vCPU / 4 GB / 120 GB for CAD $14.40 per 30 days:
- https://cloud.ionos.ca/prices

### DigitalOcean Basic 4 GiB — known-compatible but over budget

DigitalOcean currently lists its Basic shared-CPU 4 GiB / 2 vCPU / 80 GiB plan at USD $24/month. This meets the measured memory need but remains over the user's stated budget.

Source:
- https://www.digitalocean.com/pricing/droplets

## Decision

Do not purchase or provision a larger 8 GB authority host solely for memory. The next paid-host candidate should be a persistent Linux x64 VPS with at least 4 GB RAM, with OVHcloud Canada VPS-1 currently the preferred cost target based on provider-listed pricing and the completed capacity measurement.

Before enrollment on any provider:

1. Provision Ubuntu 22.04 x64 on exactly one persistent VPS.
2. Install Python 3.10 + venv, Node 22, FFmpeg, Git, and cURL.
3. Run the existing Policy C bootstrap to create `/opt/songsterr-fresh-authority/venv`.
4. Register exactly one GitHub self-hosted runner with label `songsterr-fresh-authority-v1` and `--disableupdate`.
5. Run `mode=probe` only.
6. Review the complete safe fingerprint before changing `UNENROLLED` to `ENROLLED`.
7. After deliberate enrollment, run at least three separate exact canaries from one unchanged source commit and aggregate fail-closed.

Until those steps occur, `modelValidationComplete` remains false, customer-eligible events remain 0, and duration research remains paused.
