# V168 — GOAT research access request ready

Date: 2026-08-29 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **REQUEST TEXT PREPARED / ACCESS NOT YET CLAIMED OR GRANTED / NO ASSETS ADMITTED / SCORING NOT ARMED**

## Project Progress Score
**60%** under the standing five-gate rubric in `docs/checkpoints/CURRENT_STATE.md`.

Gate 4 remains incomplete because GOAT access has not actually been granted and no exact external source/reference bytes have been acquired/hash-frozen.

**Test Score: NOT RUN.** V168 reference-facing score calls remain **0**.

## Authoritative access conditions confirmed
Authoritative GOAT Zenodo dataset record:
- `https://zenodo.org/records/15690894`
- DOI `10.5281/zenodo.15690894`
- Dataset, Version v1, Restricted.
- Record description asks interested users to contact/request access and include a short description of intended use.
- Record explicitly states the dataset is **for research purposes only** and **not intended for use in any commercial product**.
- Zenodo Rights section currently exposes no populated license value on the inspected public record page.

Authoritative project repository:
- `https://github.com/JackJamesLoth/GOAT-Dataset`
- README directs users who want the dataset to request access on the Zenodo page.

Zenodo request mechanism:
- Restricted records may allow requests from authenticated users and/or guests depending on owner settings.
- Request form may ask for identity/contact information and optionally/conditionally a message to the record owner.
- Any granted access terms must be preserved as provenance; do not infer broader rights than the grant states.

## Ready-to-submit request message

> Hello,
>
> I would like to request research access to the GOAT dataset for a non-commercial evaluation of an automatic guitar-transcription system.
>
> The immediate purpose is a controlled cross-song research holdout test comparing two already-frozen transcription policies. The GOAT reference annotations would be kept isolated from candidate generation and used only after candidate outputs are frozen, so the evaluation remains reference-blind.
>
> The restricted GOAT files would not be redistributed, published, or incorporated into a commercial product. This research evaluation is being kept separate from Production, and no dataset-derived reference content would be shipped.
>
> I will preserve and follow any additional access/use conditions you specify and cite the GOAT dataset/paper in resulting research documentation.
>
> Thank you for considering the request.

## Submission boundary
This repository cannot claim that the request has been submitted or approved until that actually occurs through Zenodo.

When submitting:
1. Use the official GOAT Zenodo record `15690894`.
2. Submit the prepared research-use description above (minor identity/signature wording may be added by the requester).
3. Preserve evidence of the exact request and any owner conditions/grant response.
4. Do **not** record passwords, login credentials, secret access links, tokens, or private download URLs in the public repository.
5. If access is granted via expiring secret link, store only a non-secret provenance label publicly; keep the secret URL outside the repository.
6. If the owner grants access with extra conditions, those conditions become controlling for V168 and must be frozen before asset admission.

## What must be preserved if access is granted
Before opening V168 scoring:
- grant date/time and non-secret grant identity;
- exact GOAT record/version identity;
- exact owner-specified use restrictions;
- exact downloaded file names/byte sizes and SHA256 identities;
- source-audio/reference pair bindings;
- exact professional reference layer chosen prospectively;
- whether any selected reference layer is model/alignment-derived;
- deterministic score-blind song/integrity selection rule;
- integrity result for any source/reference duration mismatch;
- proof that professional reference bytes remain inaccessible to candidate generation.

## Known integrity preflight item
Public GitHub issue #1 in `JackJamesLoth/GOAT-Dataset` currently reports possible duration/EOF mismatches for `item_67`, `item_96`, and `item_110`. There was no author reply at the most recent checkpoint.

These reports are **unverified third-party reports**, not confirmed defects. If access is granted, check them prospectively during metadata/integrity intake and freeze any exclusion/repair policy before comparative Policy A/B scoring.

## Hard boundaries unchanged
- Access request preparation does not admit GOAT.
- Access request preparation does not increase the fixed Project Progress Score above 60%.
- No candidate generation.
- No scorer/new-song adapter.
- No reference-facing scoring.
- No holdout-driven tuning or song exclusion.
- CPU only under current authorization.
- Never modify/merge/promote `main` or Production without explicit user direction.
