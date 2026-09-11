# Songsterr Fresh — Policy C Pinned Compute Authority V1

Status: IMPLEMENTED SCAFFOLD / UNENROLLED
Branch: `songsterr-fresh-pipeline-v1`
Authority ID: `songsterr-fresh-authority-v1`

## PURPOSE

Policy B proved that the current hosted Demucs → Basic Pitch floating-point path has no independently justified cross-platform numerical admission bound, and finite repeated hosted consensus is not a universal portability proof. Policy C changes the execution authority instead of weakening those findings.

Policy C defines one explicitly enrolled, fixed self-hosted compute surface as the only authority-eligible model execution surface. GitHub-hosted model runs remain measurement/history evidence only. There is no hosted fallback and no selection among multiple hosted outputs.

This authority is a reproducibility scope, not a security attestation. It does not attempt to prove that a machine is uncompromised. It deliberately excludes machine IDs, serial numbers, MAC addresses, IP addresses, usernames, and other host secrets from the branch-tracked fingerprint.

## AUTHORITY CONTRACT

Branch-tracked manifest: `scripts/songsterr-fresh/pinned_compute_authority_v1.json`

Required runner labels:
- `self-hosted`
- `linux`
- `x64`
- `songsterr-fresh-authority-v1`

The manifest begins `UNENROLLED`. No model output is authority-eligible while it is un-enrolled.

The authority fingerprint covers reproducibility-relevant state including:
- CPU architecture/model/family/stepping/microcode and normalized CPU-feature hash
- logical CPU count
- kernel/system/libc identity
- exact Python version, implementation, and interpreter executable SHA-256
- Node and FFmpeg first-line versions plus executable SHA-256
- pinned Python package versions
- full installed Python-distribution lock hash, including normalized versions plus installed `RECORD`, `direct_url.json`, and `INSTALLER` metadata hashes, so transitive/package-content drift invalidates authority
- NumPy build/configuration hash
- PyTorch build/configuration hash
- deterministic thread/hash environment

The model path remains fixed:
- frozen authorized audio fixture/blob
- exact decoded separation WAV identity
- frozen structure identity
- Demucs `htdemucs_6s`, CPU, shifts 0, overlap 0.25, segment 7
- exact Demucs model asset SHA-256
- Basic Pitch 0.4.0 fixed decoding settings
- duration-free evidence boundary

## ENROLLMENT

1. Provision one dedicated fixed Linux x64 machine and register it as a GitHub self-hosted runner with the required authority label. It must not be an autoscaling or ephemeral pool that can silently move between CPU surfaces.
2. Preinstall the branch-pinned toolchain and package versions. The authority workflow intentionally performs no `apt` or `pip` installation before a canary.
3. Manually dispatch `Songsterr Fresh Policy C Pinned Compute Authority` with `mode=probe`.
4. The probe must pass the branch-pinned package-set check and produce `authority-probe.json`. A probe alone never enrolls authority and never validates model evidence.
5. Review the probe and deliberately commit its exact `fingerprint` and `fingerprintSha256` into `pinned_compute_authority_v1.json`, changing `enrollmentStatus` to `ENROLLED`. Enrollment is a branch-reviewed policy change, not an automatic workflow side effect.
6. Any later fingerprint drift fails closed. Re-enrollment requires another deliberate manifest change and fresh reproducibility canaries.

## AUTHORITY CANARY

After enrollment, manually dispatch the same workflow with `mode=canary`.

Before any Demucs or Basic Pitch execution, `verify_pinned_compute_authority.py --verify-current` must exactly match the enrolled fingerprint. If not, the model process does not run.

A canary then:
- verifies the exact fixture and decoded separation WAV
- rebuilds and verifies frozen reference-blind structure
- runs fixed Demucs separation and verifies the exact model asset
- invokes Basic Pitch once with same-inference activation and decision-surface diagnostics
- builds duration-free model evidence
- writes a `songsterr-fresh-pinned-compute-authority-canary-v1` summary containing exact output identities

One canary can never promote model validation.

## REPRODUCIBILITY PROOF

`scripts/songsterr-fresh/aggregate_pinned_compute_authority_canaries.py` requires at least three separate workflow run IDs. All must have:
- the same source commit
- the same enrolled authority fingerprint
- the same fixed input identity
- exact guitar-stem SHA-256
- exact note-inference identity
- exact activation-bundle identity
- exact decision-surface identity
- exact canonical evidence identity and event count

Any mismatch fails closed.

If all three are exact, the result may state `pinnedAuthorityReproducibilityDemonstrated:true`. It still states `modelValidationComplete:false`; reproducibility proof alone does not automatically establish semantic/model quality, duration authority, customer eligibility, or delivery permission.

## DRIFT / INVALIDATION

The enrolled authority is invalidated by any fingerprint mismatch, including hardware, microcode, kernel/libc, interpreter, toolchain, package, numerical-library configuration, or deterministic-environment drift. There is no tolerance around the fingerprint and no fallback to another runner.

Normal maintenance therefore follows: change → untrusted/drifted → deliberate re-enrollment → three new exact authority canaries → separate validation review.

## EXISTING POLICY B EVIDENCE REMAINS VALID

Policy C does not erase the hosted variation evidence. It preserves the conclusion that hosted cross-platform output is not universally portable under the old Policy B requirements. Hosted canaries and automatic decoder-trace follow-ups remain useful measurement/history evidence, but they are not the Policy C authority.

## CURRENT PROMOTION STATE

- authority enrollment: `UNENROLLED`
- pinned-authority reproducibility demonstrated: false
- `modelValidationComplete`: false
- customer-eligible events: 0
- duration research: paused
- V2 remains authoritative; V3 remains candidate-only
- archived V143/Gomyway implementation/reference/pro-scorer path remains out of scope
