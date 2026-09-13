# Songsterr Fresh V6 — EGSet12 Branch-History Contamination Audit Result

Status: **IMMUTABLE RESULT — EGSet12 REJECTED AS UNTOUCHED V6 HOLDOUT**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Purpose

This checkpoint records the branch-history-only contamination audit for EGSet12. It does not inspect or score EGSet12 audio/reference pairs and does not invoke Basic Pitch, V6, matching, or correctness.

The purpose was solely to determine whether EGSet12 could still qualify as an untouched external holdout for the already-frozen V6 admission protocol.

## Controlled audit identity

Workflow:
`.github/workflows/songsterr-fresh-egset12-contamination-audit.yml`

Workflow creation commit:
`f4d347a04b14340ac441ff35375413e4d479a38a`

Run:
`34760898067`

Job:
`103733427004`

Execution:
GitHub-hosted Ubuntu 24.04 CPU only. No Modal, Vercel heavy-GPU, L4, corpus download, model inference or correctness.

Branch head audited:
`f4d347a04b14340ac441ff35375413e4d479a38a`

Reachable commit count:
`7662`

Identifiers searched across reachable history:
- `EGSet12`
- `egset12`
- `11406378`
- `robust-guitar-tabs`

To avoid self-contamination from this newly created search lane, the audit excluded only:
- `docs/checkpoints/SONGSTERR_FRESH_V6_REPLACEMENT_HOLDOUT_METADATA_SEARCH.md`
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
- `.github/workflows/songsterr-fresh-egset12-contamination-audit.yml`

Search methods were Git history pickaxe/regex (`git log -S` and `git log -G`) over all commits reachable from branch HEAD.

## Result

The controlled audit **failed the untouched-history gate by design** because pre-search EGSet12 exposure exists in reachable branch history.

- match lines emitted: `42`
- unique matching commits: `21`
- audit-text SHA-256: `21e8da1cc4385b702df4ee9c141c5b952d83acc39bc6bedbf8a391ecf46fc294`

Artifact:
- name: `egset12-contamination-history-audit`
- artifact ID: `10318981287`
- artifact ZIP SHA-256: `858da60e05998cacbee0a78cb566533403859c9fa632789240b190f50bf31301`
- size: `1608` bytes

Representative pre-search matching commits include:
- `13998014a523c6daa5f0a7f611bd6cac7a9eb470` — `Add bounded electric-guitar TabCNN research fetch`
- `f783f9c551e0efb8b9807e7bfe2a964826e18fee` — `Persist exact approved electric TabCNN consensus evidence`
- `9bbf01b81e8a2b6baedec5c64af35c13d5530f13` — `Checkpoint exact-source electric consensus progress`
- `bb7d5d2050bce1c6a5f3995df2c741468a43b014` — `Persist electric-consensus subfloor attack evidence`
- `06c6237d4c6f3a5d2110afa0f57bbd79f9ae9952` — `checkpoint: freeze V168 external candidate screening`
- `f0b966df4881311456b5c455161431d8a771114e` — `preregister parallel open-corpus breakthrough lane`
- `4b6333f40c9c419bc7db6933c9b2497671a9fca7` — `checkpoint independent P2 harmonic confirmation`
- `583ed2edc95251569b7cf248c3ff797a3690651d` — `checkpoint replicated P2 harmonic signal`
- `69ea19fe47b9805e264010c15288bdc44e6d99b2` — `checkpoint V1 synthetic fail-fast boundary`

The audit also found the Zenodo record identifier `11406378` and `robust-guitar-tabs` in older branch commits.

## Decision

EGSet12 is **not an untouched corpus on this branch** and is therefore rejected as the V6 external admission holdout.

This decision does not depend on whether every historical use exposed final correctness. The frozen V6 external-validation design requires a defensible untouched holdout; repeated prior branch exposure to the exact corpus/project identifiers and earlier electric-guitar evidence lanes is sufficient to fail that requirement conservatively.

Do not:
- download or score EGSet12 for V6 admission;
- attempt to erase/rewrite branch history to restore untouched status;
- create a corpus-specific V6 binding for EGSet12;
- use EGSet12 observations to change V6/scoring constants.

EGSet12 may remain historical/reference material only outside the untouched V6 admission-holdout role.

## Policy boundary

This audit exposed no new real-corpus V6 correctness. Therefore all authority remains fail-closed:
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed
- Production unchanged.

## Next action

Continue metadata/license/structure search for a **different untouched, permissively licensed real-guitar corpus** with performed note-level timing and enough likely independent event volume to support the frozen `>=1000` V6-positive gate.

No candidate audio/reference audit may begin until its untouched status, rights/provenance and corpus-specific reference-blind audit preregistration are defensible.
