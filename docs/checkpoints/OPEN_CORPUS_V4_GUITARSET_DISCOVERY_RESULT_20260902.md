# Open-Corpus V4 GuitarSet Discovery — Frozen Result

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Boundary

This checkpoint freezes the completed V4 development-only discovery result **before** any V4 trigger family is formulated and before any player `05` reference is used.

The preregistered discovery definition remains authoritative:
- discovery players `02/04` only;
- confirmation player `05` reserved and unread for V4 per-event labels;
- prospective evaluation players `00/01/03` remain sealed;
- immutable V3 candidate artifact reused; no audio decoding, Basic Pitch inference, or candidate regeneration;
- one-event counterfactual labels use the unchanged exact-pitch one-to-one matcher at primary 100 ms and secondary 50 ms.

## Run identity

Real discovery workflow:
- workflow creation commit `48d32716fce48556f88c7318366ade373af0faea`;
- run `33582980473`;
- job `100101041812`;
- conclusion: **SUCCESS**.

Frozen analyzer:
- `validation/open_corpus/analyze_guitarset_v4_discovery.py`;
- blob `f25706803b5ae0f46be59c95cd3e1485cefd3aba`.

Immutable candidate inputs reverified in-run:
- original candidate run `33581322528`;
- artifact ID `9828683652`;
- artifact ZIP SHA256 `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`;
- candidate manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- all 177 candidate JSON hashes reverified before references;
- candidateRegenerated=false.

Discovery references:
- exactly 117 JAMS: player `02` = 59, player `04` = 58;
- player `05` JAMS absent from the discovery workspace;
- players `00/01/03` absent;
- no WAV files present.

## Frozen discovery outputs

Discovery artifact:
- artifact name `guitarset-v4-discovery-report`;
- artifact ID `9829078706`;
- artifact ZIP SHA256 `2f7353b3bd82cd3d0dc5db08bcc0490656defb956e55c1a7da3cd6a0f5b4eff1`.

Frozen file hashes:
- `v4-discovery-report.json` SHA256 `5250a27c0249b019e2f080a2ef754290d31ce8d3ff0a66779c51b0b7cfbfb509`;
- `v4-discovery-labeled-rows.jsonl` SHA256 `a8d0852333a4f277b180dc1585b09b304d441171ef0b252c7c80b588d1411b9b`.

Status in report: `V4_DISCOVERY_REPORT_FROZEN`.

## Primary discovery result

Population:
- 117 discovery tracks;
- 7,518 trigger-eligible ordinary-V2 octave proposals;
- 19,400 total reference note events across the 117 tracks.

Primary 100 ms one-event counterfactual classes:
- beneficial: **119 / 7,518 = 1.5828677839851024%**;
- neutral: **2,669 / 7,518 = 35.50146315509444%**;
- harmful: **4,730 / 7,518 = 62.91566906092046%**.

By V2 direction:
- octave-up (`high`): 2,113 events; beneficial 9 (**0.4259346900141978%**), neutral 569 (**26.92853762423095%**), harmful 1,535 (**72.64552768575486%**);
- octave-down (`low`): 5,405 events; beneficial 110 (**2.0351526364477337%**), neutral 2,100 (**38.85291396854764%**), harmful 3,195 (**59.11193339500463%**).

By discovery player:
- player `02`: 4,221 events; beneficial 60 (**1.4214641080312722%**), neutral 1,317 (**31.201137171286426%**), harmful 2,844 (**67.37739872068231%**);
- player `04`: 3,297 events; beneficial 59 (**1.789505611161662%**), neutral 1,352 (**41.006976038823176%**), harmful 1,886 (**57.203518350015166%**).

Strict50 secondary classes:
- beneficial 105;
- neutral 2,835;
- harmful 4,578.

## Immediate scientific interpretation boundary

The V3 failure is explained at a stronger event-level resolution: indiscriminate ordinary-V2 octave swapping is overwhelmingly harmful in this open corpus. Octave-up proposals are especially unsafe, and octave-down proposals remain mostly harmful.

This checkpoint **does not select a V4 trigger**. The frozen labeled discovery rows may now be inspected only for hypothesis formation using the already-preregistered reference-blind feature set. Player identity may be used for replication checks only and must never become a trigger feature.

Any V4 candidate family must be:
1. small and interpretable;
2. formulated only from the frozen `02/04` discovery rows and allowed reference-blind observables;
3. separately preregistered with an exact confirmation qualification gate and deterministic selection rule **before** any player `05` per-event reference use;
4. rejected if confirmation does not pass without weakening the preregistered gate.

## Counters at this boundary

- V4 discovery completed: yes;
- V4 discovery labeled events: 7,518;
- player `05` V4 per-event reference read: **false**;
- player `05` V4 per-event labels computed: **false**;
- V4 trigger selected: **false**;
- GuitarSet prospective evaluation processed: **false**;
- GuitarSet prospective evaluation score calls: **0**;
- V168 prospective reference-facing score calls: **0**;
- GPU/CUDA/Modal: **none**;
- `main` / Production: **untouched**.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
