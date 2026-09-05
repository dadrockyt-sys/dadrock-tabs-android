# V143 Normal-Routing Promotion Evidence Decision

Date: 2026-09-05 America/Toronto  
Branch: `v143-contextual-prune-lobo`

## Decision

**`MODEL_BEARING_E2E_NOT_JUSTIFIED`**

The pre-production normal-routing promotion evidence boundary is **CLOSED / GREEN** without another model-bearing approved-fixture execution.

This is an evidence-composition decision, not a quality verdict and not a production deployment.

## Evidence already available

### Gate 1 — scheduler structure

Actions run `33942915753`, job `101243642285`: GREEN/CLOSED.

It proves the exact scheduler candidate blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8` preserves:

- literal multiprocessing `spawn`;
- direct Demucs child → parent RoFormer → cascade Demucs child ordering;
- deterministic child environments;
- parent RoFormer GPU visibility;
- fail-closed child termination/join and pipe cleanup;
- frozen output/public contract;
- no reference/scoring/restricted-corpus active path.

### Gate 2 — exact model/runtime execution

Authoritative Actions run `33943100948`, job `101244148835`, artifact `9962641557`: GREEN/CLOSED.

It executes the exact same scheduler candidate on the approved repository fixture and proves:

- exact frozen source, normalized audio, model, WAV and PCM identities;
- exact direct/cascade deterministic shift traces;
- deterministic CPU Demucs runtime invariants;
- exact public return contract;
- request-scoped cleanup;
- no reference-facing input, scoring, quality verdict, or persistent audio/stem retention.

No Gate-2 rerun is authorized; the later failed sibling run was diagnosed as a duplicate-run shared-app cleanup race, not a scheduler parity failure.

### Gate 3A — normal-routing source composition

Actions run `33945157629`, job `101249801382`, artifact `9963085825`, digest `sha256:9084a0d17ca44154e66a89f78546b6e210e3a302110e9e560c99b9f20a39ad09`: GREEN/CLOSED.

It proves exact source identities compose the normal request path:

`Vercel Rhythm selection → HTTP bridge → live Rhythm worker → Vercel-audio request adapter → Rhythm-only router → deterministic stem provider → authoritative paired stem bundle → deterministic wrapper → Gate-2-proven seeded scheduler`.

It also proves:

- Lead/Bass remain on the legacy analyzer path;
- private Blob handoff fields are preserved;
- Vercel fails closed unless the V143 anti-leakage runtime fields are complete;
- the request adapter owns request-scoped temporary storage and download→normalize→route ordering;
- direct/cascade carrier files remain independent;
- no restricted/reference-scoring imports occur in the pinned routing chain;
- the gate itself performs no audio/model/Modal/GPU/secret/reference/scoring work.

## Why another pre-deploy model-bearing E2E is not justified

A further approved-fixture normal-route model execution would repeat the expensive separator/model computation already established by Gate 2 while reaching that same scheduler through source composition already established by Gate 3A.

The only meaningful incremental properties such a run could add are operational deployment properties such as:

- actual deployed environment-variable selection;
- live HTTP/Modal network handoff;
- deployed image/package availability;
- private Blob credential/download behavior;
- post-deploy worker/bridge reachability.

Those properties belong to the **actual integration/deployment verification boundary**. Testing them before deploying the candidate would either require an artificial duplicate deployment environment or would exercise the unchanged production deployment rather than the candidate being promoted. Neither justifies repeating the model execution.

Therefore the correct next phase is a narrow production integration/deploy plan followed by deployment-specific smoke/routing verification. Model recomputation should occur only if the integration/deployment process changes a model-bearing source/runtime fingerprint or a deployment-specific failure creates a concrete need for it.

## Closed boundary

Pre-production promotion evidence status:

- Gate 1: **GREEN / CLOSED**
- Gate 2: **GREEN / CLOSED**
- Gate 3A: **GREEN / CLOSED**
- Additional pre-deploy model-bearing E2E: **NOT JUSTIFIED / DO NOT RUN**
- Normal-routing promotion evidence boundary: **GREEN / CLOSED**

## Safety state

- Reference-facing inputs: `0`
- Reference score calls: `0`
- Quality verdict made: `false`
- GOAT restricted bytes: `0`
- Sealed GuitarSet `00/01/03`: untouched
- SplitMySong: remains terminal `FAIL_CLOSED_NO_CANDIDATE`
- Production worker changed: `false`
- Production bridge changed: `false`
- Vercel changed: `false`
- `main` merge performed: `false`

## Next boundary

Prepare the **narrow production integration/deploy plan**. Before any write to `main` or production, enumerate the exact branch-vs-production changes, deployment order, rollback point, and no-model smoke/routing checks. Do not implicitly merge or deploy as part of planning.
