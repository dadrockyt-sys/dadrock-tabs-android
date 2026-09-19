# Astra 7D — SAM-Audio resource review and bounded alternative search

Date: 2026-09-19 UTC. Parent: `8d0a38e55ab7e239cd6118845641b7285a49c49c`.

## Decision

**Defer the standard SAM-Audio small loader under the current 4096-MB CPU memory / 1200-second analyzer / zero-new-spend target.** Its published checkpoint is 5.1 GB and the loader constructs additional components. This is a resource-feasibility decision from metadata and source, not measured out-of-memory failure, a claim that all possible optimized versions are impossible, or permission to change the budget.

No model, installation, audio, gated-access acceptance, paid service or production action occurred. Existing admission gates remain unchanged. Regression suite: 154 passed, zero failed.

## Source identity

SAM-Audio repository revision: `bb4c6999d2677c7402360e426afc01ddfad6dce0`.

| Reviewed path | Git blob |
| --- | --- |
| `sam_audio/model/base.py` | `3aa3a57054065966f894c86c44672e13e63f7936` |
| `sam_audio/model/model.py` | `2ac5ddc7d317c1d5f472d3b24209e4a6ccc8eb51` |
| `sam_audio/model/config.py` | `e2369086397bd6656da598c2a49fd1d5418a8ddd` |
| `sam_audio/model/text_encoder.py` | `09152d96321f088cfa4132890176492e69d06bf7` |
| `sam_audio/model/vision_encoder.py` | `37973ff2096f3211b0edc645250e7ad2152b6770` |
| `sam_audio/model/codec.py` | `36067bee6ee9e985452f92693c81dee678d49353` |
| `pyproject.toml` | `b06a9f5d6bfbea059543ade953fda31c0be1ebac` |

Paths resolve under [the pinned source](https://github.com/facebookresearch/sam-audio/tree/bb4c6999d2677c7402360e426afc01ddfad6dce0). README/license identities remain in the 7C review.

## Published evidence versus inference

- [Public small-model listing](https://huggingface.co/facebook/sam-audio-small/tree/main) reports `checkpoint.pt` at **5.1 GB**, plus `config.json`. These are rounded publisher file sizes, not resident-memory measurements. The page indicates FloatStorage in its serialization metadata. The exact model revision, byte count and digest were not exposed in the accessible evidence.
- The [model card](https://huggingface.co/facebook/sam-audio-small) has a CPU fallback example, but that example names the **large** model. It supplies no small-model CPU memory/latency result. Its license tag is `sam-license`.
- [Paper v1](https://arxiv.org/html/2512.18099v1), table 8, lists small as 500M parameters. Do not use that headline alone as the memory requirement of the complete loader. Section 7.6 reports about 7.3 seconds per ten-second input for **large on an A100 GPU**; this is not CPU evidence. It also cautions that fewer solver steps affect instrument separation more than some other tasks. No Astra quality result is derived from these observations.
- Public config and checkpoint detail pages returned **401 Unauthorized**; the metadata API was inaccessible. No authenticated access or alternate route around the gate was attempted. The file tree itself was publicly readable. Exact small config overrides therefore remain unknown.

The 5.1-GB file exceeds both 4.096 decimal GB and 4 GiB (4.295 decimal GB). File size alone does not prove peak RAM, but the standard loader constructs the model and loads a full state dictionary into CPU memory before copying it into the model. Combined with additional components, no defensible fit within 4096 MB was established. Quantization, offload, meta-device loading or removal of unused components would constitute a different, unverified integration.

## What the loader actually requires

| Component | Initialization / text-only relevance | Remaining identity/resource issue |
| --- | --- | --- |
| DiT, audio codec, projections, anchor layers | Constructed for separation; codec encodes and decodes audio | Included checkpoint content not inspected; activation and load peaks unknown |
| T5 text encoder and tokenizer | Loaded separately with Transformers; used for text queries | Default name `t5-base`; exact small config and downstream revision unverified |
| Perception vision encoder | Constructed even when no video is supplied; text-only forward then uses zeros | Default `PE-Core-L14-336`; memory is not eliminated by omitting video |
| Span predictor | Constructed pretrained when config is non-null; default `pe-a-frame-large` | `predict_spans=False` skips use, not initialization; small config unknown |
| Text/visual rankers | Created from config when configured; forward reranking conditional | `reranking_candidates=1` alone does not suppress construction; defaults null, small config unknown |

The load-state implementation explicitly treats text encoder, rankers and span predictor as independently loaded rather than checkpoint-contained. The dependency file requires Python >=3.11 and includes unpinned Git dependencies (DACVAE, ImageBind, CLAP, perception-models). Do not transplant that graph into Astra's frozen Python 3.10 environment.

The source license explicitly covers trained weights (7C evidence), and the model card associates SAM License with this model. A complete dependency/artifact rights review was not performed because the standard resource path was deferred first. Do not label the model prohibited or commercially cleared.

One further source-pinning issue for any future adoption: `_from_pretrained` accepts `revision` but passes `cls.revision` to `snapshot_download`; `SAMAudio.revision` is `None`. A caller's revision argument therefore must not be assumed to enforce a frozen download. No download was invoked to test this.

## Bounded alternative: AudioSep

Official repository revision `944583f18b84589dc965de3ad77525c945334252` in `Audio-AGI/AudioSep`:

| Source | Git blob |
| --- | --- |
| `README.md` | `d395194e1b1e4f68c62a063ed063f43f40015cdd` |
| `LICENSE` | `8060e2bf1747e386fb9ef65837631e0a7adcaaab` |
| `pipeline.py` | `baa03582d52c8b27c1f35f9352b055068bfd8ae9` |
| `config/audiosep_base.yaml` | `cb54d16397e523cb67a602a631276aa0770e7ae0` |
| `models/clap_encoder.py` | `6cd6421f89e76af6fdb33cfdc85f632d81044baf` |
| `models/resunet.py` | `4639b23750e56340fa395c6a3462993224c4f304` |

[Official source](https://github.com/Audio-AGI/AudioSep/tree/944583f18b84589dc965de3ad77525c945334252) implements 32-kHz mono ResUNet30 separation from CLAP **text** conditioning, with an explicit CPU path. No separate reference recording is needed. This improves product-input compatibility; it does not establish bass/guitar accuracy or lead/rhythm truth.

The official README links its own Hugging Face Space checkpoint directory. The [artifact-adding commit](https://huggingface.co/spaces/Audio-AGI/AudioSep/commit/5638854dccfaea5c5fa4f634c00fe74fbb119244) publishes immutable LFS identities:

| File | Published bytes | Published SHA-256 (not locally verified) |
| --- | ---: | --- |
| `audiosep_base_4M_steps.ckpt` | 1,264,844,076 | `f8cda01bfd0ebd141eef45d41db7a3ada23a56568465840d3cff04b8010ce82c` |
| `music_speech_audioset_epoch_15_esc_89.98.pt` | 2,352,471,003 | `51c68f12f9d7ea25fdaaccf741ec7f81e93ee594455410f3bca4f47f88d8e006` |

Combined disk bytes: **3,617,315,079** (about 3.37 GiB). This is not a RAM bound. The default CLAP wrapper initializes the full audio/text model in fp32 and a `roberta-base` tokenizer. Startup copies, unused audio-side parameters, activations and dependency overhead remain to be assessed. The README's memory-saving chunk option limits windows, not necessarily initialization or resident weights.

[The Space README at the same artifact commit](https://huggingface.co/spaces/Audio-AGI/AudioSep/blob/5638854dccfaea5c5fa4f634c00fe74fbb119244/README.md) declares `license: mit`. This is useful publisher license evidence attached to the artifact-hosting repository, beyond the separate GitHub software license. It does not by itself complete the upstream **CLAP** checkpoint rights chain or establish the provenance of every included component. Keep the exact scope of this evidence, rather than discarding it or upgrading it into complete clearance.

## Concrete integration defect to avoid

In pinned `models/resunet.py`, `chunk_inference` initializes its output to zeros and only enters the processing loop when `current_idx + WINDOW < L`. WINDOW is five seconds (160,000 samples). Therefore **all nonempty inputs of at most five seconds return the zero-filled output without calling the separation base**. This follows directly from control flow; no audio/model execution was performed. Tail processing is nested inside that loop and also needs boundary/coverage review before adoption.

Additionally, the README imports `inference` from `pipeline`, while this source revision defines `separate_audio`, not `inference`. Do not copy the README invocation blindly.

## Next bounded work

AudioSep remains a **research lead, not an admitted engine**. Milestone 7E should first resolve CLAP artifact provenance/license and inspect the full initialization memory path without downloading weights. In parallel within the same work session (no delegated agents needed), ordinary CPU synthetic backend work may implement an independent chunk planner with exact coverage tests, addressing the concrete short-input/tail risk for any future separator. This planner must not import AudioSep, models, audio files or archives, and it must grant no execution authority. Record any resource/rights blocker honestly; do not keep adding candidate admission gates merely to increase test counts.
