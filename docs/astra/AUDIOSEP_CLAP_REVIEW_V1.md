# Astra 7E — CLAP provenance, loading footprint and sample coverage

Date: 2026-09-19 UTC. Parent: `bbeaa9964b130cd7bb26025c2711728a830a778d`.

## Results

1. The exact CLAP artifact used by AudioSep is now linked to the upstream publisher by matching published SHA-256 and byte size, with an explicit CC0 declaration on the model-hosting repository. The earlier unknown CLAP publisher-license link has been resolved at this evidence level.
2. AudioSep's standard full-CLAP loader remains **resource-unverified**, not admitted. Inspection establishes full audio/text construction and checkpoint-copy peaks; exact tensor payload and measured memory remain unknown.
3. Astra now has an independent, tested sample chunk planner. It covers short inputs and tails without adopting the upstream loop defect. This is implemented backend functionality, not model inference or quality evidence.

## Exact CLAP artifact and declared terms

- [Official LAION-AI/CLAP README](https://github.com/LAION-AI/CLAP/blob/1fd4c37df5ffbfcfbad5415c170bc66cf94c9994/README.md), Git blob `5a76d231361a9f66380331a3dff6f8c6b242fab1`, explicitly links `lukewys/laion_clap` and names `music_speech_audioset_epoch_15_esc_89.98.pt` for the larger HTSAT-base model. It identifies training on music, speech, AudioSet and LAION-Audio-630k; no training data was accessed here.
- [Upstream artifact-adding commit](https://huggingface.co/lukewys/laion_clap/commit/4226474e38defca6fc9272a7848bb7b0355ccd7a) publishes **2,352,471,003 bytes** and SHA-256 **`51c68f12f9d7ea25fdaaccf741ec7f81e93ee594455410f3bca4f47f88d8e006`**. Both match AudioSep's official Space artifact identity frozen in 7D. No downloaded bytes were hashed; this is publisher-metadata correspondence.
- [Model-repository license commit](https://huggingface.co/lukewys/laion_clap/commit/d57333f4fd55123da1ee2e89c3e46fa7cebad415) adds `license: cc0-1.0`; the currently accessible artifact page also declares CC0. [Official code LICENSE](https://github.com/LAION-AI/CLAP/blob/1fd4c37df5ffbfcfbad5415c170bc66cf94c9994/LICENSE), blob `0e259d42c996742e9e3cba14c677129b2c1b6311`, supplies the CC0 text, including commercial-purpose scope and its limits.
- This supports development and commercial reuse under the publisher's declared rights for this CLAP artifact. It does not turn third-party rights, software dependencies, customer recordings or full engine deployment into blanket permission. Retain the upstream CC0 provenance alongside the AudioSep Space MIT declaration; do not relabel CLAP as originally MIT.

The observed model-repository head was `b3708341862f581175dba5c356a4ebf74a9b6651`. Attempts to retrieve its pinned README and artifact-detail URLs were inaccessible via the web tool. The immutable upload and initial-license commit pages above were accessible and provided the evidence. The model-repository declaration and official publisher link resolve the earlier missing link; do not repeat the same rights search as if no evidence exists.

## Loading and memory inspection

AudioSep source remains pinned to `944583f18b84589dc965de3ad77525c945334252`.

| Path | Git blob | Finding |
| --- | --- | --- |
| `utils.py` | `1ca65d6104c437e44302ee839a29d0d78e5f8a6c` | Builds ResUNet, then Lightning `load_from_checkpoint(..., strict=False, map_location=cpu)` with the already built query encoder |
| `models/CLAP/open_clip/factory.py` | `844f9ca0e12a0ff43ba3e042a3e43530ebe91b8c` | Constructs full CLAP, deserializes the checkpoint on CPU, then copies its state into the constructed model; fp16 route asserts non-CPU |
| `models/CLAP/open_clip/model.py` | `5677da7ec2cebaa44c9328ece4873359f459426a` | Constructs HTSAT audio branch and pretrained RoBERTa text branch plus projections; text encoding uses RoBERTa and text projection |

Source paths resolve under [the pinned AudioSep tree](https://github.com/Audio-AGI/AudioSep/tree/944583f18b84589dc965de3ad77525c945334252). Additional wrapper/pipeline identities are in the 7D report.

The wrapper's fp32 CPU construction loads the full CLAP despite text-only use. It also constructs `roberta-base` weights/tokenizer through Transformers before applying the CLAP checkpoint. That secondary initialization must be pinned or eliminated in a future exact loader; it cannot silently access the network. AudioSep then constructs the separator and loads its checkpoint non-strictly; future integration must account for missing/unexpected keys rather than treating a returned model as verified.

Let C be resident full-CLAP tensors, S resident separator tensors, D the deserialized checkpoint payload, and H interpreter/dependency/temporary overhead. CLAP startup includes approximately C + D_clap + H; separator startup includes C + S + D_separator + H. Steady inference adds activations, input/output buffers and temporaries to C + S + H. These are live-allocation models, not measured bounds: serialization size does not establish D or resident parameter bytes, and checkpoint metadata may contain non-parameter state.

The two files total 3,617,315,079 disk bytes, leaving only about 0.48 decimal GB under a 4096-decimal-MB budget if one incorrectly equated files with resident weights. That arithmetic illustrates why disk totals cannot establish fit; it is **not** an assertion that memory equals disk size. No exact resident-weight count, peak-memory measurement or 1200-second CPU timing is available. Keep the resource blocker.

**Practical direction:** a text-only CLAP adapter could retain the fine-tuned text branch, text projection, tokenizer behavior and output normalization while omitting the unused audio branch. It must avoid constructing the full model first, preserve checkpoint keys and prove embedding equivalence later under authorized execution. Dropping the audio branch after the existing constructor would not solve its startup peak. A frozen prompt embedding could reduce steady runtime further, but none has been generated or validated. Plain RoBERTa output is not a substitute for the fine-tuned CLAP embedding. No adapter/model was executed here.

## Implemented chunk planner

`astra_backend/sampleChunkPlan.mjs` exports `createSampleChunkPlan` through `index.mjs`. It accepts total/core/left-context/right-context integer sample counts and returns an immutable lazy repeatable iterable. Descriptors specify global input/output/context intervals and an input-local crop interval. All intervals are half-open.

- Every nonempty input receives at least one chunk, including clips shorter than the context window.
- Output intervals form a contiguous, non-overlapping partition; input context may overlap and is clipped at edges.
- Empty input yields no chunks. Unknown options, invalid counts, nonpositive cores and unsafe combined window sizes are rejected before iteration.
- Planning never allocates an audio buffer or a complete chunk list, imports a model, reads a file or grants execution authority.

Six tests verify sample-ID reconstruction on real-scale 32-kHz boundaries, 2,280 combinations of small lengths/asymmetric contexts, empty input, validation, lazy safe-integer edge cases, repeatability and mutation isolation. Tests import through the public backend entry point. **Full suite: 160 passed, zero failed/skipped/cancelled.**

The planner assumes a consumer can produce one aligned output sample per input sample before cropping. It does not verify model stride/padding, runtime output lengths, seam quality, cancellation, timeout or numerical output validity. No production route uses it yet. The independent implementation addresses coverage geometry; it does not patch or execute AudioSep.

## Next work

Implement a CPU-synthetic chunk-processing adapter around this plan with injected reader/processor/writer callbacks, explicit length/finiteness validation, sequential bounded processing and failure/cancellation tests. Never substitute zeros for a failed or missing chunk. Separately freeze a text-only CLAP loading design and remaining tokenizer/config/software identities from public source/metadata. Preserve the now-established CLAP publisher rights evidence and focus on the remaining resource/integration problem. Keep all model/real-audio execution blocked until its separate prerequisites are satisfied.
