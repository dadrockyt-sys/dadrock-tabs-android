# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute rules

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, redeem tokens, send customer emails, weaken thresholds, or call Bass/Lead professional structured output early.

Required Rhythm path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Preview/full must use the same authenticated/frozen stream. Browser/PDF may not invent placement. Professional human reference is scorer-only and may never be read/trained/tuned/selected by runtime. Any post-score musical improvement must remain general/reference-free and requires a fresh audio run before rescoring.

**Save this checkpoint frequently.**

## Completion gate

Rhythm is complete only with professional score >=0.99, zero critical mismatches, and PDF-event fidelity exactly 1.0. Then create `Final Rhythm Pipeline`. Bass remains paused until then; Lead remains after Bass.

## Real-audio structural baseline

Approved fixture: `public/gomywayfullaitest.m4a`.
Prior structural proof: 358 valid Rhythm events, measures 1..113 / 112 unique measures, all 16 grid steps, 25 technique events, sustain 358/358, tempo 129.19921875, 4/4, E Standard, prior full+preview PDFs.
This remains structural proof only.

## Professional holdout

Do not open/recover the professional human reference until a fresh real-audio reference-free freeze/PDF proof is locked.
`validation/rhythm_holdout/reference/reference-inventory.json` remains `completeReferenceAvailable:false`, `finalScoringAuthorized:false`.

## Product PDF source of truth

`app/ai-tab/page.js` is authoritative.
Preview → `/api/generate-tab-preview`; full/purchased → `/api/generate-tab-pdf`.
Authenticated Rhythm path:
`page.js → PDF API → createJimmyPaigeProfessionalPdf → createAiTabPdf → createV143RhythmPdf`.

## CPU gate 1 — GREEN

Minimal-dependency bootstrap source:
`f84e4b1504fb648799341fbf68255664fb95dc0b` — `Use minimal PDF dependency for Rhythm static gate`.

Actions run ID: `32622951910`.
Run identity: `debug/v143-contextual-prune/rhythm-static-bootstrap.json` schema 4, installStatus 0, preflightStatus 0, reportSchemaVersion 7, reportPassed true.

Authoritative schema-v7 result:
- eventCount 400
- uniqueMeasureCount 100
- frozen/pdf SHA identical: `6475a7d68071a8810890982e1c06c0d39f99e85d646680706233ceed5a58b37e`
- PDF-event fidelity 1.0
- full PDF 1,689,220 bytes / 4 pages
- preview PDF 1,678,893 bytes / 4 pages
- product contract schema 7 green
- real-audio workflow contract green
- runtime anti-leakage green
- polished branding/logo green
- no failed checks
- professional reference unopened
- Production unchanged

The green bootstrap report was copied exactly to canonical:
`debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json`
at commit `1f995f876e52f091c404002e340b062e373cbe05`.

CPU static gate is now established green.

## CPU gate 2 — self-test V2 IN FLIGHT

Created fresh isolated workflow:
`.github/workflows/rhythm-professional-holdout-self-test-v2.yml`
commit `1c64d91fff0fb13f4982c212267c22f2951061f7`.

It is CPU-only and triggers only from its own workflow file. It:
- checks out exact triggering SHA;
- has branch concurrency and no actor guard;
- installs only isolated `pdf-lib@1.17.1`;
- verifies runtime isolation and compiles scorer-only tools;
- creates synthetic complete/partial references only after runtime-isolation proof;
- proves positive final wrapper at >=0.99, fidelity 1.0, zero critical mismatch;
- proves partial reference, leakage and PDF mismatch hard failures;
- reruns full static product→professional-PDF glue with `GITHUB_ACTIONS=false`;
- writes only `debug/v143-contextual-prune/rhythm-professional-holdout-self-test.json` schema 6;
- never overwrites canonical static evidence;
- never opens the real professional holdout;
- does not trigger GPU or touch Production.

## Next after schema-v6 self-test green

1. Strengthen/verify the real-audio pre-holdout compact proof if needed without changing musical thresholds.
2. Intentionally trigger exactly one fresh approved-audio GPU run.
3. Require source hash, full runtime safety, positive frozen events, polished preview/full PDFs, exact event/hash identity, fidelity 1.0, reference sealed, Production unchanged.
4. Lock that fresh freeze/PDF evidence.
5. Only then recover/use the complete professional human-written reference strictly scorer-side.
6. If score <0.99 or critical mismatches >0, change only general/reference-free musical logic, rerun audio from scratch, then rescore.
7. Once real gate passes, test DadRock `/ai-tab` user end-to-end and create `Final Rhythm Pipeline`.
