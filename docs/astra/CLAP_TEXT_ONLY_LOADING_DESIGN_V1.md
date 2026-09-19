# Astra 7F — text-only CLAP loading design

Date: 2026-09-19 UTC. Parent: `bdf2636bec5650b9312865693b416629dd166314`.
Status: source-backed design; no model loader, download, embeddings or inference executed.

## Intended integration

Retain AudioSep's fine-tuned text embedding exactly while avoiding HTSAT audio-model construction and the redundant pretrained RoBERTa weight load. This could reduce startup and resident memory. It does not yet establish a fit within 4096 MB or 1200 seconds, and it does not authorize model execution.

The existing AudioSep checkpoint and CLAP publisher/CC0 link stay frozen as recorded in `AUDIOSEP_CLAP_REVIEW_V1.md`. No new model substitution is proposed.

## Canonical source contract

Repository: `Audio-AGI/AudioSep`, revision `944583f18b84589dc965de3ad77525c945334252`.

| Path | Git blob | Relevant behavior |
| --- | --- | --- |
| `models/clap_encoder.py` | `6cd6421f89e76af6fdb33cfdc85f632d81044baf` | Slow `RobertaTokenizer`, padding to 512, text singleton duplication, detached fp32 output |
| `models/CLAP/open_clip/model.py` | `5677da7ec2cebaa44c9328ece4873359f459426a` | RoBERTa pooler output -> text projection -> L2 normalization |
| `models/CLAP/open_clip/model_configs/HTSAT-base.json` | `6cef625a89daf4431f1c9f72e10bc9640eef2ba8` | Audio and generic text config; not the actual RoBERTa vocabulary/hidden-size authority |
| `models/CLAP/open_clip/factory.py` | `844f9ca0e12a0ff43ba3e042a3e43530ebe91b8c` | Full construction before state load; optional checkpoint `state_dict` and module prefix handling |

Paths resolve under [the pinned source tree](https://github.com/Audio-AGI/AudioSep/tree/944583f18b84589dc965de3ad77525c945334252).

### Keys retained and operations

Proposed text module retains these original names, with no broad key renaming:

| Key group | Purpose / source-derived shape |
| --- | --- |
| `text_branch.embeddings.*` | RoBERTa token/position/type embeddings and LayerNorm |
| `text_branch.encoder.layer.0.*` through `.11.*` | Twelve RoBERTa transformer layers |
| `text_branch.pooler.dense.weight`, `.bias` | Required pooler used by the original `pooler_output` path; not mean pooling |
| `text_projection.0.weight`, `.bias` | Linear 768 -> 512: expected weight [512,768], bias [512] |
| `text_projection.2.weight`, `.bias` | Linear 512 -> 512: expected weight [512,512], bias [512] |

The default projection activation in the inspected constructor is ReLU. After projection, `get_text_embedding` applies `F.normalize(..., dim=-1)`; the adapter must preserve its L2/epsilon semantics under the future pinned Torch version. `text_transform` is instantiated by CLAP but is not used on this inference path. Neither audio projection/branch/transform nor contrastive logit scales contribute to this text output.

Actual checkpoint tensor keys, dtypes, shapes and persistent-buffer inventory have **not** been inspected. The table defines expectations from source, not verified artifact contents. A missing pooler or projection must fail, never be randomly initialized or replaced by pretrained base-model weights.

### Tokenization and architecture

- Preserve `RobertaTokenizer`, not an unverified fast-tokenizer substitution; preserve byte-level BPE vocabulary/merges, special tokens, whitespace behavior and masks.
- Original wrapper calls padding `max_length`, truncation true, max length 512, tensor output; it duplicates a singleton text to a two-row batch before selecting row zero. Preserve this initially, including eval/no-grad and output fp32; optimize only after an authorized equivalence comparison.
- Do not use the generic HTSAT config's `vocab_size:49408`, `width:512`, or `context_length:77` as RoBERTa architecture/tokenizer values. The runtime constructs `RobertaModel.from_pretrained('roberta-base')` instead.
- Public [RoBERTa config revision](https://huggingface.co/FacebookAI/roberta-base/commit/47a52b98637fc8df2bf37a7b785cea13ad81ba94) and its [config page](https://huggingface.co/FacebookAI/roberta-base/blob/main/config.json) identify hidden size 768, 12 layers/heads, intermediate size 3072, vocabulary 50265, position count 514, type vocabulary 1 and LayerNorm epsilon 1e-5. Use a `RobertaModel` with pooling, not `RobertaForMaskedLM`, despite the config's architectures label.
- Public [tokenizer config revision](https://huggingface.co/FacebookAI/roberta-base/commit/e2da8e2f811d1448a5b465c236feacd80ffbac7b) records maximum length 512. Vocabulary/merge files, complete tokenizer defaults, package versions and local file hashes still need freezing. These config observations do not prove the historical alias resolved to identical bytes at AudioSep training time.

### Strict extraction/loading proposal

1. Verify authorized original artifact bytes against the already-published digest before any deserialization. No such verification/download is performed in 7F.
2. Use a narrowly reviewed safe deserialization path; unknown serialized globals must fail rather than falling back to unrestricted pickle execution. Exact checkpoint container contents and compatible loader version remain unknown.
3. Accept only the reviewed container form and a uniform optional `module.` prefix. Reject mixed prefixes, duplicate normalized keys, unexpected text namespaces and collisions. Do not reproduce a loose starts-with-module check.
4. Enumerate expected text-module parameters/buffers from an exact pinned configuration. Compare every retained key, shape, dtype and finite tensor value. Handle version-specific buffers only through an explicit documented allowlist. No `strict=False` blanket acceptance.
5. Classify omitted keys explicitly as reviewed non-text namespaces (audio branch/projection/transform, unused text_transform, logit scales). Unknown leftover namespaces fail. Exact key inventory remains a prerequisite, not an invented fact.
6. Construct RoBERTa from local configuration and the two projection layers, never full CLAP or `from_pretrained` base weights. Apply every required fine-tuned tensor strictly. No implicit network access or random fallbacks.
7. Release original checkpoint storage before separator construction. A later authorized preprocessing step could produce a minimal text-only artifact with its own digest, original-parent digest, extraction implementation identity and attribution. Filtering after a full `torch.load` alone does not eliminate checkpoint deserialization peak.
8. Validate numerical equivalence to the pinned original wrapper with varied text, whitespace, truncation, singleton/multirow batches and exact preprocessing. Freeze tolerances before measurement. This future test requires separate model-execution authorization; no embeddings were produced here.

## Implemented integration boundary

`sampleChunkProcessor.mjs` now wraps the planner with injected sequential read/process/write callbacks. It validates finite samples and exact lengths, copies/crops buffers, requires exact write receipts and throws errors containing confirmed prefix counts plus uncertain write ranges. Ten tests cover transformed reconstruction, async ordering, malformed outputs, stage failures, cancellation during writes, buffer ownership and detached-buffer count attacks. The full backend suite passes 170 tests.

This is a reusable integration boundary, not a model or file adapter. It assumes sample-aligned processing; stride/padding, seam quality and model memory remain unknown. Cancellation is cooperative and waits for pending callbacks. Sink receipts are trusted by contract; external writes are not transactional, and an uncertain range is not safe for blind retry.

## Next implementation

Connect complete/failed/cancelled chunk outcomes to Astra's existing offline analysis-stage contract using synthetic callbacks, ensuring partial/uncertain output cannot reach customer rendering. Then freeze local tokenizer/config identities and the exact text-key inventory contract from metadata, without weights or inference. Keep resource and numerical-equivalence prerequisites visible rather than reopening the resolved CLAP publisher-rights search.

## Milestone 7G refinement

`CLAP_TOKENIZER_FILES_V1.json` freezes four proposed local bundle files at the
immutable RoBERTa revision e2da8e2f811d1448a5b465c236feacd80ffbac7b: config,
tokenizer config, vocabulary and merges. Public non-weight bytes were fetched and
SHA-256 hashed; computed Git blob identities match the repository tree metadata.
No tokenizer was instantiated. Historical training-time alias resolution, complete
special-token/default behavior and dependency compatibility remain unverified.

`CLAP_TEXT_KEY_INVENTORY_V1.json` enumerates 203 expected parameter names/shapes
from the pinned CLAP path plus RoBERTa configuration and the linked Transformers
4.30.2 source reference. That source has a persistent position_ids buffer and a
nonpersistent token_type_ids buffer. This reference is not a chosen runtime lock or
proof of the checkpoint inventory. Reconcile the actual runtime and checkpoint
buffers explicitly; do not silently discard them or use strict=False. No model was
imported and no checkpoint tensor was inspected.

The offline chunk adapter now records outcomes in extraction.chunkProgress while
leaving events/structure/tablature unrun. Sample completion alone supplies no role
or quality evidence. Next work should define the missing validated extraction and
synthetic downstream handoff, alongside a strict metadata inventory validator.
