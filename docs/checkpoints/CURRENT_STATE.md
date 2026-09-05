# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet prospective `00/01/03` sealed.
- Current quality verdict: **NO QUALITY VERDICT — PERFORMANCE/IDENTITY DIAGNOSTICS ONLY**.

## Production — unchanged

- `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**;
- deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY;
- bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- routing proven `usingV143RhythmAnalyzer=true`; Deployment Protection preserved;
- Production worker/bridge/Vercel unchanged by diagnostics.

## Exact CPU anchor — GREEN

Approved fixture `public/gomywayfullaitest.m4a` SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.

- normalized SHA `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`;
- Guitar SHA `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`;
- PCM-int16 SHA `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`;
- shift `0,22050,6026`;
- fresh run `33914759546`, job `101159244192`, call `fc-01M1Q0MFR88FXWAQ1R47TSX77Z`;
- exact parity GREEN; client wall **666.404s**; oneDNN off; Torch intra/inter-op = 1;
- artifact `9953064061`; cleanup GREEN.

## GPU — TERMINAL / CLOSED

Current-controls L4 run `33916705535`, job `101165425904`, call `fc-01M1Q1ZA6GFSF1NZTPFF2GQA9P`:

- separation **42.404s**, client wall **51.663s**, **12.899x** faster;
- source/normalized/dimensions/private shift exact;
- Guitar SHA `5820375b67d6d3ad38386c267f8e21b721a06446ba9d8b4de14260d832d2f5a4`;
- PCM SHA `376c33be95e277f811f1edc2bea14a4d6287f4ad7ae4e8eca2c5c84134b9341b`;
- `runtimeInvariantsPassed=true`, **`exactCpuParityPassed=false`**;
- artifact `9953451993`; cleanup GREEN.

**GPU PROMOTION CLOSED. Do not rerun GPU or weaken exact parity.**

## Native split-parallel CPU — TERMINAL / CLOSED

Diagnostic-only implementation used exact dependency-native Demucs chunk-level `num_workers=4` concurrency while keeping Torch intra/inter-op, OMP and MKL at 1.

- wrapper `analyzer/v143_demucs_split_parallel_cli.py`;
- probe `analyzer/v143_demucs_split_parallel_probe.py`;
- collector `.github/scripts/v143_demucs_split_parallel_collect.py`;
- workflow `.github/workflows/v143-demucs-split-parallel.yml`;
- run **`33917237702`**, job **`101167122276`**, call **`fc-01M1Q2AZTBAM6NC7WVQQVAF1YR`**;
- Modal `cpu=4.0`, no GPU, memory 16GB;
- Torch intra/inter-op = 1; OMP=1; MKL=1; oneDNN disabled; private shift RNG exact;
- source SHA exact; normalized SHA exact; shift trace exact `0,22050,6026`;
- separation **149.928s**; client wall **158.720s**;
- speedup vs exact CPU anchor **4.199x**; material-speed gate PASS;
- runtime invariants PASS;
- Guitar SHA **`52a781bcab05335636c5bfb99168b8c01a9d627c34f1a59acf00f01512a41630`**;
- PCM SHA **`1f5665f8deceda3b13a9e8a4ac4b561a548530a7bf671f605998139cfc133c2e`**;
- **exact CPU parity FAIL**;
- artifact **`9953701945`** uploaded; isolated-app cleanup GREEN; `productionAppTouched=false`.

### Interpretation

The dependency-native split executor is materially faster, but concurrent CPU model execution changes the exact numerical output even though ordered overlap-add/reduction, chunk geometry, frozen model/settings, shift trace, single-threaded kernels and oneDNN-off controls were preserved.

Therefore **split-parallel promotion is CLOSED**. Do not rerun it, weaken exact parity, or promote the faster hash.

## Authorization / next action

User authorized non-reference-facing V143 performance work and repository-owned Gomyway audio. No authorization for reference-facing scoring, GOAT, sealed GuitarSet, SplitMySong reopening, or weakened fail-closed criteria.

1. Inspect current V143 request flow and storage for an **exact source-hash stage cache** architecture that can reuse previously computed exact deterministic separator outputs without changing their bytes.
2. Prefer caching normalized input identity and exact deterministic separator-stage artifacts/derived aggregate outputs keyed by source SHA + frozen execution-policy/version hashes; fail closed on any key mismatch.
3. Do not retain raw user audio beyond existing policy; determine whether exact deterministic stem cache is acceptable under current retention/privacy boundaries before implementing it. If stem retention is not acceptable, inspect downstream feature/cache boundaries that preserve exact behavior without stem persistence.
4. No new Demucs/GPU/split-parallel compute should start until cache architecture is understood.
5. Production/bridge/Vercel/UI remain unchanged until a reference-free exact structural gate passes.
6. Reference-facing accuracy remains unarmed.

## In-progress cache architecture inspection — 2026-09-04

- Resumed on `v143-contextual-prune-lobo` from this checkpoint.
- Re-read the frozen boundaries; authorized work remains cache architecture inspection/design only.
- Inspected `app/api/analyze-audio-tab/route.js`. The app-side API route forwards analysis requests to the remote live V143 analyzer bridge, so a reusable-byte cache should be placed at the analyzer/bridge stage where stable normalized audio identity and deterministic separator outputs are available, not in any reference-facing path.
- Branch-local analyzer/bridge source is being traced before any cache implementation.
- Earlier inspection checkpoint referenced commit `e13054da0c7f639528f6f5be1394ce811563da01`; the actual branch head immediately before this fresh-chat save is **`9254deb4f4767e56018702bd7ad157f47740f913`** (`docs: checkpoint continuity save`).
- Recursive branch-tree inspection found no repository path containing `http_bridge`; this strengthens the current boundary finding that the live Modal V143 bridge implementation is external to the checked-in app tree or generated/deployed from a source not named as the live bridge in this branch.
- No Demucs/GPU/split-parallel runs, reference-facing scoring, analyzer semantic changes, production bridge changes, Vercel changes, or UI changes were made in this pass.

## Fresh-chat handoff — exact next steps

Start the next chat by reading this file on branch `v143-contextual-prune-lobo`. Continue without re-opening closed GPU/split-parallel work.

1. **Enumerate branch-local analyzer entrypoints.** Inspect all `analyzer/` Python files plus `.github/workflows/` and `.github/scripts/` references that create, deploy, call, or name the V143 Modal application. Build a short source-of-truth map: app/API route → HTTP bridge → worker/analyzer → separator → downstream feature stages.
2. **Locate the live bridge construction source without guessing.** Search for the known production bridge/app naming, Modal decorators/classes/functions, `usingV143RhythmAnalyzer`, request payload fields, and worker invocation names. If the live bridge implementation is genuinely absent from the repository, record that as a deployment-source boundary instead of fabricating an insertion point.
3. **Identify the nearest exact cache boundary.** Prefer a pre-separation lookup keyed by canonical normalized-source identity plus a frozen execution-policy/version fingerprint, returning exact previously produced separator bytes only on a full key match. Cache miss or any metadata mismatch must fall through to the existing exact CPU path unchanged.
4. **Define the cache key/fingerprint before implementation.** At minimum account for normalized source SHA, separator/model identity, model weights/version, Demucs parameters, shifts/seed behavior, sample rate/channels, Torch/runtime determinism controls, and any code/policy version that can change output bytes. The design must make stale or ambiguous entries impossible to accept silently.
5. **Resolve retention/privacy boundary before storing stems.** Do not persist raw uploaded user audio beyond existing policy. Determine from current code/config whether deterministic separated stems may be retained. If stem persistence is not clearly allowed, move the candidate cache boundary downstream to derived non-audio artifacts/features that can still eliminate repeated work while preserving exact semantics.
6. **Prototype only in isolated diagnostic code after the structural design is clear.** Do not alter the production Modal bridge, production worker, Vercel deployment, UI, or `main` for the first cache experiment. The prototype must prove: cache miss = current exact CPU bytes; cache hit = byte-identical outputs; key mismatch = fail closed/miss; no reference-facing scoring.
7. **Use repository-owned `public/gomywayfullaitest.m4a` only after the reference-free structural gate exists.** First test should establish exact cache miss→populate→hit parity against the GREEN CPU anchor hashes already recorded above. Do not run GPU or split-parallel variants.
8. **Measure only performance/identity.** Capture wall time for miss vs hit, cache-hit identity hashes, key metadata, and cleanup/retention behavior. No accuracy/quality claims or reference comparisons are authorized.
9. **Promotion gate.** Consider any production-facing cache change only if exact bytes are unchanged, privacy/retention is acceptable, key invalidation is fail-closed, production routing semantics stay unchanged, and the speed benefit is material. Otherwise close the cache candidate and document why.
10. **Checkpoint frequently.** Save meaningful source-map findings, boundary decisions, prototype commits/runs, hashes, and next steps back to this `docs/checkpoints/CURRENT_STATE.md` on `v143-contextual-prune-lobo` so another fresh chat can resume safely.

### Hard stops preserved for the next chat

- No reference-facing scoring or quality verdict.
- No GOAT restricted bytes.
- No sealed GuitarSet `00/01/03` access.
- No SplitMySong reopening.
- No GPU or split-parallel reruns.
- No weakening exact parity or fail-closed criteria.
- No production bridge/worker/Vercel/UI change before a reference-free exact structural gate passes.
- Do not merge this diagnostic/cache work to `main` merely to test architecture; keep it isolated on `v143-contextual-prune-lobo` until the promotion gate is satisfied.

## Continuation checkpoint — source mapping resumed (2026-09-04)

- Fresh-chat resume verified branch tip **`bc79891e4f302871fcd2f79006a49c17130c2e07`** before this save.
- Its Git tree is **`2b0ce1e80a83f035c39930bd325241982bbc5865`**; this is a tree SHA, not a commit SHA.
- Re-read the full frozen-boundary and cache-architecture handoff above.
- Source mapping remains the active task: enumerate branch-local V143 analyzer/workflow/deployment entrypoints and locate the exact privacy-safe cache boundary before implementation.
- The previously established request-flow clue remains: `app/api/analyze-audio-tab/route.js` forwards to the remote live V143 bridge; the checked-in implementation corresponding to the live `http_bridge` deployment name has not yet been identified.
- **No runtime behavior, production bridge/worker, Vercel/UI, Demucs/GPU/split-parallel compute, reference-facing scoring, or retention policy was changed in this continuation before this checkpoint save.**

## Exact stage-cache structural gate — GREEN (2026-09-04)

- Branch-local isolated primitive: `analyzer/v143_exact_stage_cache.py`.
- Synthetic gate: `analyzer/v143_exact_stage_cache_probe.py`.
- CI gate: `.github/workflows/v143-exact-stage-cache-structural.yml`.
- Primitive commit lineage:
  - `54e8af3f429c5129418e2f8e5ff8fa860b43349c` — `feat: add isolated V143 exact stage cache primitive`;
  - `8c9bee773d81c66bd700d83f450b53c16c4d7ff4` — `feat: wire exact V143 cache miss-hit fallback semantics`;
  - `351d430b601c83578d385aa162dc971b04d1b310` — `test: cover V143 cache miss-hit fallback wiring`.
- Structural CI run **`33936373413`**, job **`101224995003`**, head `351d430b601c83578d385aa162dc971b04d1b310`, conclusion **SUCCESS**.
- Evidence artifact **`9960303358`**, `v143-exact-stage-cache-structural`, SHA256 digest `e6ff4e789edf959d59b2299f9fe916ea6ea21ff83a395bd738f86bb1441468f2`.
- The gate is synthetic only: no audio used, no Demucs/model import/invocation, no reference-facing scoring.
- Proven semantics: empty miss; deterministic content-addressed key; exact compute on miss; best-effort populate; hit returns exact stored bytes and skips compute; full fingerprint mismatch changes key and misses; corruption is rejected and falls back to exact compute; invalid compute bytes are not hidden; cleanup succeeds.
- Fingerprint is fail-closed and includes normalized-source SHA, separator model, separator weights SHA, Demucs parameters, shift policy, sample rate/channels, Torch/OMP/MKL runtime controls including oneDNN state, and code-policy version.
- The cache helper deliberately has **no production default root** and explicitly does not authorize retention. This preserves the unresolved privacy/retention boundary.

### Source-of-truth wiring boundary

- `app/api/analyze-audio-tab/route.js` remains only the request forwarder and V143 anti-leakage response gate; it is too shallow to host the exact separator-stage cache because it does not own canonical normalized identity or separator bytes.
- Exact search for the known live bridge name `dadrock-v143-http-bridge` returns **zero checked-in code matches**. The checked-in repository therefore still does not provide a source-proven production bridge insertion point.
- Do **not** fabricate a production insertion point, wire the cache into the Next route, or persist user stems merely because the structural gate is GREEN.
- Production/main/bridge/worker/Vercel/UI remain unchanged by this cache work.

### Next authorized gate

1. Preserve the structural gate as GREEN and keep all cache code isolated on `v143-contextual-prune-lobo`.
2. Before any production-facing cache wiring, obtain/source-map the actual live V143 bridge/worker implementation and resolve whether separated-stem retention is explicitly permitted. Until both are known, production wiring remains BLOCKED BY SOURCE/RETENTION BOUNDARY.
3. The repository-owned `public/gomywayfullaitest.m4a` may now be used for a **reference-free exact identity/performance cache diagnostic** because the synthetic structural gate is GREEN, but only through an isolated diagnostic path with ephemeral cleanup and the existing exact CPU implementation unchanged.
4. That first real-audio diagnostic must prove miss output equals the frozen GREEN exact CPU hashes, then hit output equals the same exact hashes while skipping separation; any key mismatch/corruption must fail closed to the exact CPU path.
5. No reference comparisons, quality scoring, GPU, split-parallel, sealed assets, production bridge/worker/Vercel/UI, or `main` merge are authorized by this structural success.
