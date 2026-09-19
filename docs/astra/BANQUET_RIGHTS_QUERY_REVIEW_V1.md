# Astra Milestone 7C — Banquet rights and query boundary

Date: 2026-09-19 UTC. Parent: `115b668fc625d8468a5c7b408f277b6de3b87602`.
Result: **review complete; admission conditions not met**. Banquet remains blocked.

## Checkpoint rights retrieval

The authoritative record is [Zenodo 13694558](https://zenodo.org/records/13694558), recommended file `ev-pre-aug.ckpt`. Prior 7B evidence recorded published MD5 `4dfb91d6d27c2dfd4992a15070915541` and rounded size 645.5 MB. These are inherited publisher observations, not bytes verified in this turn. No SHA-256 or exact record revision was newly established.

This turn attempted the record page, `/api/records/13694558`, and `/records/13694558/export/json`. Web retrieval failed or reported inaccessible URLs; TinyFish page/API retrieval timed out; a bounded direct API request timed out after 20 seconds with zero bytes. No license payload was obtained. This is **unavailable evidence**, not evidence that the publisher prohibits commercial use or omitted a license. Do not repeat the historical inference that software MIT necessarily licenses this checkpoint.

Missing evidence remains the authoritative record revision and license/permission applicable to this exact file, with development and commercial inference scope. No permission has been inferred, and neither admission nor execution code has been relaxed.

## Canonical query source inspection

All Banquet source below is pinned to `79ed5bb75e5c3a40cd319d9d990cee913fc65c26` in `kwatcharasupat/query-bandit`.

| Source | Git blob | Finding |
| --- | --- | --- |
| [train.py](https://github.com/kwatcharasupat/query-bandit/blob/79ed5bb75e5c3a40cd319d9d990cee913fc65c26/train.py) | `9b4d19e75817187a70231ca0a7552d5633c0a7d8` | BYOQ loads separate query audio, tiles/truncates it to ten seconds, and passes it as `batch.query.audio`. `stem_name` labels the result; it does not generate conditioning. |
| [bandit.py](https://github.com/kwatcharasupat/query-bandit/blob/79ed5bb75e5c3a40cd319d9d990cee913fc65c26/core/models/e2e/bandit/bandit.py) | `4b2575d64a6db6a7dd160176e313f019e3c1cd1f` | `PasstFiLMConditionedBandit.adapt_query` invokes the audio query encoder and passes its output to FiLM. Both normal and optimized separation call this audio-dependent method. |
| [passt.py](https://github.com/kwatcharasupat/query-bandit/blob/79ed5bb75e5c3a40cd319d9d990cee913fc65c26/core/models/e2e/querier/passt.py) | `a213f7854800d25349ceb584073ae7d748d9877c` | The actual conditioned model constructs `Passt`, not `PasstWrapper`. It averages audio channels, resamples 44.1 kHz to 32 kHz, and produces a 768-dimensional PaSST embedding. |

**New technical finding:** there is an identifiable potential cache boundary between the query encoder output and FiLM. This is an inference about a possible future adapter, not an upstream cached-embedding API or a tested implementation. No input accepting a label or precomputed vector was found in these canonical entry points. The alternate unconditioned `Bandit` class is not evidence that `ev-pre-aug.ckpt` can become a label-only model.

**Additional dependency:** `Passt` constructs `hear21passt.base.get_basic_model(mode="embed_only", arch="openmic")`. A future execution review must identify that model's exact weights, terms, and initialization/download behavior as well as Banquet's. Do not instantiate the class merely to inspect it. No PaSST model was imported, fetched or run here.

A cached embedding would still need an independently documented source recording, explicit product-use rights, exact encoder/checkpoint identity, preprocessing settings, vector digest and later authorized equivalence/quality testing. No such recording or embedding is currently frozen. Synthesizing a vector or reusing legacy stems would not establish meaningful instrument conditioning. No archived data, query library or audio notebook was opened.

The optimized multi-query method also reassigns the mixture representation inside its loop. If that path is ever adopted, verify independence/order invariance of successive queries; do not assume it safely reuses the original representation. This is a static observation only, not a measured defect claim.

## Decision

Checkpoint development/commercial rights remain unresolved because authoritative retrieval failed. Query provenance remains unresolved, and the identified cache boundary alone cannot clear it. Keep `developmentExecutionReady:false` and `customerDeliveryEligible:false`. Bass/generic guitar are candidate capabilities only; lead and rhythm retain `LEAD_RHYTHM_DISTINCTION_UNAVAILABLE`.

No code change is warranted under 7C step 6 because its evidence conditions did not resolve. Existing gates already encode the blocked outcome. Regression verification is recorded in `MILESTONE_7C_VERIFICATION.json`; no new tests mirror these documentation-only findings.

## Independent search continuation: SAM-Audio

Reviewed upstream `facebookresearch/sam-audio` revision `bb4c6999d2677c7402360e426afc01ddfad6dce0`:

- [README](https://github.com/facebookresearch/sam-audio/blob/bb4c6999d2677c7402360e426afc01ddfad6dce0/README.md), blob `c614478e32009372b27a41f1ffe70e822e72d80d`: supports text-conditioned target/residual separation without a separate query recording. It names `facebook/sam-audio-small`, requires Python >=3.11, recommends CUDA, and identifies PE-AV as a dependency. Checkpoint access requires publisher approval/authentication.
- [SAM License](https://github.com/facebookresearch/sam-audio/blob/bb4c6999d2677c7402360e426afc01ddfad6dce0/LICENSE), blob `00030caa37d1d1714b2eb0d7f55c50c5805ed4ce`, dated November 19, 2025: expressly includes trained weights in its covered materials. Section 1(a) grants use and modification rights without a noncommercial-only limitation. This is a promising artifact-scope distinction; it is not a completed review of the entire deployment or its dependencies. Redistribution, use restrictions and other agreement conditions still apply.
- Attempts to read the small model's Hugging Face raw README/LICENSE through web retrieval were inaccessible. No access request or license acceptance was submitted, and no artifact was downloaded. Exact model revision, file digests, sizes and dependency terms are not frozen.

**Research lead only:** text prompts fit the product input better, but neither bass/guitar accuracy nor lead/rhythm identity follows from prompt support. CPU feasibility, total model memory, latency, and affordability are unknown. Do not call this selected, execution-ready, or commercially cleared. Do not migrate the existing Python 3.10 lock.

Next: Milestone 7D, bounded metadata/documentation review of SAM-Audio small and required dependencies. First establish whether the full model set could plausibly fit the 4096-MB/1200-second CPU target before investing in installation work. If evidence rules that out, record rejection/deferment and continue searching; do not silently relax the budget or provision a GPU.
