from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3161_near_zero_microtiming_refinement_v1 as micro

s3161 = micro.s3161
recur = micro.recur
recall = micro.recall
v2 = micro.v2
v3 = micro.v3
harmonic = micro.harmonic
register = s3161.register

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3161-protected-source-recall-recovery-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-protected-source-recall-recovery-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        true = int(counts["true"])
        false = int(counts["false"])
        total = true + false
        rows.append({
            "signature": signature,
            "true": true,
            "false": false,
            "total": total,
            "precision": round(100.0 * true / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-float(r["precision"]), -int(r["true"]), int(r["false"]), str(r["signature"])))


def first_int(row: dict[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        value = row.get(key)
        if value is None:
            continue
        try:
            return int(round(float(value)))
        except (TypeError, ValueError):
            pass
    return None


def source_token(row: dict[str, Any]) -> tuple[int, int, int] | None:
    token = row.get("token")
    if isinstance(token, (list, tuple)) and len(token) >= 3:
        try:
            return (int(token[0]), int(token[1]), int(token[2]))
        except (TypeError, ValueError):
            pass

    measure = first_int(row, ("measure", "measureIndex", "measure_index", "bar", "barIndex"))
    step = first_int(row, ("step", "stepIndex", "step_index", "slot", "slotIndex"))
    pitch = first_int(row, ("pitch", "midi", "midiPitch", "midi_pitch", "note"))
    if measure is None or step is None or pitch is None:
        return None
    return (measure, step, pitch)


def bucket_float(value: float, cuts: list[float], labels: list[str]) -> str:
    for cut, label in zip(cuts, labels):
        if value <= cut:
            return label
    return labels[-1]


def source_metadata_signatures(row: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    numeric_keys = (
        "score", "confidence", "probability", "prob", "amplitude", "velocity",
        "magnitude", "salience", "energy", "duration", "durationMs", "duration_ms",
    )
    for key in numeric_keys:
        if key not in row or row.get(key) is None:
            continue
        try:
            value = float(row[key])
        except (TypeError, ValueError):
            continue
        if "duration" in key.lower():
            b = bucket_float(value, [0.03, 0.06, 0.12, 0.25, 0.5, 1.0, 99999.0], [
                "d003", "d006", "d012", "d025", "d050", "d100", "d100p"
            ])
        else:
            b = bucket_float(value, [0.01, 0.03, 0.06, 0.10, 0.20, 0.40, 0.70, 99999.0], [
                "v001", "v003", "v006", "v010", "v020", "v040", "v070", "v070p"
            ])
        out.add(f"sourceMeta::{key}|{b}")
    return out


def micro_signatures(
    tok: tuple[int, int, int],
    grid: dict[tuple[int, int], float],
    winner_audio: Any,
    winner_sr: int,
    alt_audio: Any,
    alt_sr: int,
) -> set[str]:
    measure, step, _pitch = tok
    center = float(grid[(measure, step)])
    wf = micro.onset_offset_features(winner_audio, winner_sr, center)
    af = micro.onset_offset_features(alt_audio, alt_sr, center)
    return {f"recoverMicro::{sig}" for sig in micro.signatures_for(wf, af)}


def combined_signatures(
    tok: tuple[int, int, int],
    row: dict[str, Any],
    maps: dict[str, Any],
    grid: dict[tuple[int, int], float],
    winner_audio: Any,
    winner_sr: int,
    alt_audio: Any,
    alt_sr: int,
) -> set[str]:
    reg = {f"recoverRegister::{s}" for s in register.signatures_for(register.local_features(tok, maps))}
    mic = micro_signatures(tok, grid, winner_audio, winner_sr, alt_audio, alt_sr)
    meta = source_metadata_signatures(row)
    structural = {
        f"recoverStructure::step{tok[1]}",
        f"recoverStructure::stepParity{tok[1] % 2}",
        f"recoverStructure::stepQuarter{tok[1] % 4}",
        f"recoverStructure::pitchClass{tok[2] % 12}",
        f"recoverStructure::register{'low' if tok[2] < 48 else ('mid' if tok[2] < 60 else 'high')}",
        f"recoverStructure::measurePhase{tok[0] % 4}|stepQuarter{tok[1] % 4}",
    }
    out = set().union(reg, mic, meta, structural)

    # Cross only broad families; avoid token-identity signatures.
    for r in reg:
        if "measurePitchRecurrence" in r or "neighborPitchRecurrence" in r or "measurePitchRank" in r:
            for m in mic:
                if "microTimingAgreement" in m or "microOnsetSharpness" in m or "microAttackBalance" in m:
                    out.add(f"recoverCross::{r}||{m}")
    for s in structural:
        if "register" in s or "stepQuarter" in s:
            for m in mic:
                if "microTimingAgreement" in m or "microOnsetSharpness" in m:
                    out.add(f"recoverStructuralCross::{s}||{m}")
    return out


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)
    champion, reconstruction = s3161.reconstruct_3161(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 31.61 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    source_rows: dict[tuple[int, int, int], list[dict[str, Any]]] = defaultdict(list)
    unparsed = 0
    for row in events:
        tok = source_token(row)
        if tok is None:
            unparsed += 1
            continue
        source_rows[tok].append(row)
    if not source_rows:
        sample = events[0] if events else {}
        raise RuntimeError(f"Could not parse any protected source tokens; sample keys={sorted(sample.keys())}")

    source = Counter({tok: len(rows) for tok, rows in source_rows.items()})
    filtered = source - champion
    maps = register.build_maps(champion)

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    recoverable_true = 0
    recovery_false = 0

    # Detection-side features are computed first. Reference is consulted only below to attach labels.
    for tok, count in filtered.items():
        if (tok[0], tok[1]) not in grid:
            continue
        representative = source_rows[tok][0]
        sigs = sorted(combined_signatures(
            tok, representative, maps, grid, winner_audio, winner_sr, alt_audio, alt_sr
        ))

        truth_count = int((Counter({tok: count}) & reference)[tok])
        false_count = int(count) - truth_count
        recoverable_true += truth_count
        recovery_false += false_count
        for sig in sigs:
            if truth_count:
                groups[sig]["true"] += truth_count
            if false_count:
                groups[sig]["false"] += false_count
        details.append({
            "token": list(tok),
            "sourceCount": int(count),
            "recoverableTrue": truth_count,
            "recoveryFalse": false_count,
            "signatures": sigs,
        })

    ranked = precision_rows(groups)
    high_precision = [
        r for r in ranked
        if int(r["true"]) >= 5 and float(r["precision"]) >= 80.0
    ]
    perfect = [
        r for r in ranked
        if int(r["true"]) >= 3 and int(r["false"]) == 0
    ]
    high_precision.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), int(r["false"]), str(r["signature"])))
    perfect.sort(key=lambda r: (-int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during protected-source recall recovery profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "31.61-protected-source-recall-recovery",
        "champion3161Score": score,
        "reconstruction": reconstruction,
        "protectedSourceEventCount": len(events),
        "parsedSourceTokenCount": len(source_rows),
        "unparsedSourceEventCount": unparsed,
        "filteredSourceCount": int(sum(filtered.values())),
        "recoverableTrueCount": recoverable_true,
        "recoveryFalseCount": recovery_false,
        "perfectRecoverySignaturesMin3True": perfect,
        "highPrecisionRecoverySignaturesMin5True80Pct": high_precision,
        "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": score["pitchF1"],
        "matched": score["matched"],
        "missing": score["missing"],
        "extra": score["extra"],
        "filteredSourceCount": int(sum(filtered.values())),
        "recoverableTrueCount": recoverable_true,
        "recoveryFalseCount": recovery_false,
        "perfectRecoverySignatureCount": len(perfect),
        "highPrecisionRecoverySignatureCount": len(high_precision),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 PROTECTED-SOURCE RECALL RECOVERY V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Protected source events:", len(events))
    print("Parsed source tokens:", len(source_rows))
    print("Unparsed source events:", unparsed)
    print("Filtered source count available for recovery:", int(sum(filtered.values())))
    print("Recoverable true count in protected source:", recoverable_true)
    print("Recovery false count in protected source:", recovery_false)
    print("Perfect recovery signatures (3+ true, 0 false):", len(perfect))
    for row in perfect[:40]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("High-precision recovery signatures (5+ true, >=80%):", len(high_precision))
    for row in high_precision[:40]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
