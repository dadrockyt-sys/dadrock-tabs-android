# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; musical accuracy first, PDF second.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Frozen V5 is irreversible. The professional reference may be opened only for the one final immutable holdout; **no tuning, candidate modification, threshold adjustment, candidate selection, or replacement may follow from its results.**
- No Modal/L4 without fresh explicit user authorization. None is authorized.
- Tempo frozen exactly `129.19921875`.
- Completion gate: professional score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- Keep existing `freezeReady=false` safety sentinels false until all completion gates pass.

## Frozen V5 identities
- V5 exact: `891` attacks / `1214` selected / `1209` rendered / `5` voicing drops / `113` measures.
- Events: `967` baseline + `242` rescued; `933` preserved metadata + `276` conservative neutral; `21` technique events.
- Combined V5 validation SHA256 `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- Raw render-stream SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; 1,748,095 bytes.
- Inspection hashes: first `33693e32ee4a578e48f7e96360d0c06191bf0fff16f68d76d97e1e384f1aa5f3`; middle `1e265e8486e75505262de9ea33dea444f60731e025db20dea063dd1f75448775`; last `487df510c3931403017576dac2fe3e587479b9d827a496ea9d792fa5a2764671`.
- Source-only validation run `32872086764` = SUCCESS; candidate immutable/reference-free/no Modal/no Production change.

## Reference-free scorer preflight — GREEN
- Generic scorer path: `validation/rhythm_holdout/score_rhythm_holdout.py`; canonicalizer `canonical.py`; freeze builder `freeze_rhythm_analysis.py`; PDF fidelity validator `verify_pdf_event_fidelity.py`; completeness validator `verify_reference_completeness.py`.
- Preflight workflow `.github/workflows/v143-v5-professional-scorer-preflight.yml`, run `32918988699` = **SUCCESS**, result commit `fdac99e0c9d724187ef64720aa8e7d489a66b1d9`.
- Persisted report `debug/v143-contextual-prune/v5-professional-pdf/scorer-preflight-report.json`: passed, no failures, no reference access, no candidate/Modal/Production change.
- **Canonical scorer event SHA256 `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.**
- PDF renderer-normalized event hash exactly matches; fidelity `1.0`; 1209 events; 113 measures.

## Professional reference exact pins
- Committed image: commit `e0f91e74c815b9ecdf0a72fae6d1523414b34577`, `public/Professionalexample.jpg`, Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, 979815 bytes, SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`.
- Structured identity: Songsterr song `243`, revision `7868948`, rhythm track `3`, image id `v0-3-2-TvYYK-mMQgzBsDxG`, track name `Craig Ross | 1953 Gibson Les Paul Goldtop | Rhythm Guitar`, tuning `[64,59,55,50,45,40]`.
- Structured-source SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`.
- Built reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Expected reference: 113 measures / 603 playable onsets / 946 playable notes / 104 populated measures.
- User screenshot confirms path/commit provenance only; never use visible notes for tuning/scoring.

## Final one-shot scorer — AUDITED
- Workflow `.github/workflows/v143-v5-final-professional-holdout.yml` originally prepared commit `066743f7b0348a042d07cc837ca1679808c30b5f`.
- Full scorer/source logic has fixed concurrency, permanent branch result sentinel, complete V5 pre-reference revalidation, exact source/revision/hash pins, exact completeness/reference hash checks, one scorer invocation at minimum 0.99, transient reference cleanup, and a persisted result even on post-open failure.
- Any post-open failure consumes the one-shot and persists failure; any pre-reference failure does not open/consume the holdout.
- API dispatcher attempt run `32919421673` failed HTTP 404 before target workflow creation because GitHub cannot API-dispatch this branch-only workflow. **No holdout access occurred. Do not rerun that launcher.**

## Branch-native dedicated trigger — VERIFIED / NOT YET FIRED
- Final workflow trigger stanza updated in commit `43760dbd705dd96929b09cdbf41c1645d8b285c3`.
- Added only a push trigger on branch `v143-contextual-prune-lobo` for exact path `debug/v143-contextual-prune/v5-professional-pdf/final-professional-holdout-trigger.txt`, while retaining `workflow_dispatch`.
- Git commit patch proves only `7` additions / `2` deletions: trigger comment/stanza plus final newline. **No scoring/source/hash/sentinel logic changed.**
- The trigger-workflow edit itself did not match the dedicated trigger path; action inventory for head `43760dbd...` shows only unrelated cleanup workflow, not the final holdout.
- Therefore final holdout remains unopened and untriggered at this checkpoint.

## Current integrity
- Protected runtime untouched; `main`/Production untouched; V5 unchanged; no Modal/L4.
- `professionalHoldoutOpened=false` in project state.
- Rhythm remains incomplete.

## Next exact actions
1. Create `debug/v143-contextual-prune/v5-professional-pdf/final-professional-holdout-trigger.txt` exactly once. This intentionally fires the audited branch-native final workflow.
2. Monitor only workflow status/step summaries. Do not inspect transient professional source/reference payloads or logs containing them.
3. After completion, fetch only persisted `debug/v143-contextual-prune/v5-professional-pdf/final-professional-holdout-result.json`.
4. Immediately checkpoint the immutable result.
5. Regardless of pass/fail, **do not tune, modify, reselect, or replace V5 afterward.**
6. Declare Rhythm complete only if persisted result proves score >=0.99, critical mismatches=0, PDF fidelity=1.0, and final completion gate true.
