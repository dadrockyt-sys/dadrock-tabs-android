# Jimmy PAIge — Astra backend

Active branch: `astra-work`. Canonical progress: `../docs/checkpoints/CURRENT_STATE.md`.

This is an independently editable, self-contained copy of the Fresh deterministic core and its CPU synthetic tests, pinned from commit `7be69898cf3eb7ae32cbe8963714895ad99c5853`. It does not import the archived directory, V143 code, neural models, network clients or production routes. Original module labels and contract versions intentionally remain unchanged so adoption does not silently alter payload semantics.

## Included

Musical structure mapping; simultaneous playable shapes; rhythm spelling including rests/ties; phrase-level fretboard paths; product payload adaptation; note-evidence diagnostics and conservative delivery gates. The offline `analysisContractAdapter.mjs` implements the Astra V1 request/result state machine without audio inference or network access. Source identities for the adopted Fresh snapshot: `../docs/astra/BACKEND_ADOPTION_MANIFEST.json`.

## Not yet included

Astra audio separation, role-aware audio transcription, automatic musical-structure inference, a trained model, validated real-audio accuracy, HTTP job orchestration or production integration. Preserving supplied notes and passing synthetic tests is not a correctness claim about those notes.

## Verify

From this directory run `npm test` (Node built-in test runner, no third-party installation). Existing evidence/quality gates remain intact. Astra fixtures cover all roles and the complete/partial/abstained/failed result states. Test failures must be fixed or recorded; never reinterpret them as real-audio validation.

## Reuse boundary

The V143 contribution is documented operational and delivery experience, not its song-specific pruning or unknown metric formulas. Both old branches remain archived. New work changes this directory under the active Astra milestone, with tests and a checkpoint commit after every major step.
