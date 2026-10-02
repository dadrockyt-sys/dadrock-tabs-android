# GitHub Actions S0 Separator Runner V1

Date: 2026-10-02
Branch: `astra-work`

The Codespace-only process is now packaged as a GitHub Actions job.

## Why a trigger file

The project remains intentionally off `main`. GitHub manual `workflow_dispatch` is tied to workflows present on the default branch, so this workflow instead runs only when this file changes on `astra-work`:

`docs/astra/S0_SEPARATOR_RUN_TRIGGER.txt`

No other `astra-work` commit runs the expensive separator job.

## One-time secret

The main repository needs an **Actions repository secret** named:

`S0_FIXTURE_TOKEN`

This is separate from a Codespaces secret of the same name.

The token should be fine-grained, read-only for:
`dadrockyt-sys/dadrock-tabs-private-fixtures`

Do not put the token in Git, workflow YAML, issues, chat, or logs.

## What each run does

1. checks out `astra-work`;
2. checks out the private fixture repository using `S0_FIXTURE_TOKEN`;
3. verifies the expected 16 fixture files;
4. installs FFmpeg + Python runtime dependencies;
5. downloads the exact FP16 BS-Roformer ONNX model;
6. verifies SHA-256 `d3d2bac77a7023282cb5f35a5807179e34076b60589867b572275f1a8ec36444`;
7. compiles the evaluation code;
8. regenerates all 12 deterministic S0 mixtures;
9. runs the frozen BS-Roformer + frozen cleanup comparison;
10. writes a GitHub run summary;
11. uploads **only** `s0_bs_roformer_result.json` as an artifact;
12. deletes private fixture audio, generated mixtures, private checkout, and model from the runner.

No private MP3/WAV audio is uploaded as a workflow artifact.

## How to run

After the Actions secret exists, edit:

`docs/astra/S0_SEPARATOR_RUN_TRIGGER.txt`

Change `run_marker` to a new unique value (for example a timestamp) and commit that single change to `astra-work`.

Then open GitHub **Actions -> Astra S0 Separator Evaluation**.

## Cost behavior

The job uses a GitHub-hosted runner rather than an active Codespace. Codespaces can remain stopped.

This does not make execution free: GitHub Actions usage is governed by the repository/account's Actions allowance and billing. The workflow is intentionally manual-by-trigger and does not run on normal commits.
