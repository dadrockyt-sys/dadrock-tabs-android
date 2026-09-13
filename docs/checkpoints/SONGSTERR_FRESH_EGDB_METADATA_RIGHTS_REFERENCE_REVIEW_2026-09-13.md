# Songsterr Fresh V6 — EGDB / EGDB-PG Metadata, Rights, and Reference Review

Status: **REJECTED / NOT AUDIT-READY BEFORE MEDIA ACCESS**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Purpose

Evaluate EGDB and its later EGDB-PG amplifier-rendered family as a possible untouched replacement external holdout for the already-frozen V6 admission method, using metadata/paper/license evidence only. No EGDB/EGDB-PG media was downloaded, Basic Pitch was not invoked, V6 was not invoked, and correctness was not computed.

## Scientific metadata

The original EGDB work describes a real electric-guitar collection built from a Stratocaster-type guitar fitted with a hexaphonic pickup. The authors recorded clean direct-input (DI) audio while a professional guitarist performed 240 tablatures in a studio against click tracks. The paper reports 118 minutes of unique performed DI audio, then six timbral copies produced by re-rendering the DI through different amplifiers.

This is real performed guitar rather than synthesized guitar audio, and the DI path would be scientifically relevant to V6 if all other gates cleared.

## Reference construction is not independent performed truth

The paper's annotation section prevents use as the frozen V6 external truth source.

The performed note onsets were not captured independently as hardware MIDI or another contemporaneous symbolic performance stream. Instead:

1. expected note onset times were derived from the reference tabs and BPM;
2. an onset-detection algorithm was run on each recorded DI string signal to estimate actual audio onset times;
3. each detected onset was assigned the pitch of the closest expected tab onset;
4. the first author manually checked all 240 recordings and corrected a small number of onset labels.

The paper explicitly says offsets were also not directly observed; they were constructed from actual onset plus expected symbolic duration.

Therefore the onset timing used as transcription ground truth is derived from the same recorded DI audio family that would be evaluated, even though it was subsequently manually inspected. That is materially different from an independent performed MIDI/note-capture reference. Under the current frozen V6 holdout discipline, audio-derived onset detection cannot be promoted into external correctness truth merely because it is bundled with a dataset.

## Rights gate also fails to clear

The original EGDB project page publicly links dataset access but does not surface an explicit dataset license. Public dataset indexes likewise report the EGDB license as unknown.

The newer EGDB-PG Zenodo release (record family including `19789500`) hosts amplifier-rendered EGDB material, but the Zenodo record's Rights / License field is blank. `Open` repository access is not itself a permissive data-file license.

The associated papers being openly readable or CC-licensed does not license the separate audio dataset.

## Disposition

**Do not download, audit, bind, or score EGDB or EGDB-PG for V6 admission under current evidence.**

Two independent gates fail:
- no authoritative permissive dataset-audio license has been established;
- performed onset truth is constructed using onset detection on the recorded DI audio rather than captured independently from the evaluated signal.

A later author permission could potentially resolve rights, but it would not by itself resolve the reference-provenance problem. Reconsideration would require an authoritative independently captured performed note-onset+pitch reference that is not manufactured from the evaluated audio, followed by untouched-history screening before any media access.

## Frozen-policy boundary

This review changes no V6 constants, Basic Pitch settings, canonical audio path, matcher, tolerances, Wilson statistic, admission gates, strata rules, or deferred-reveal/single-run rule.

Fail-closed state remains:
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed
- Production unchanged.
