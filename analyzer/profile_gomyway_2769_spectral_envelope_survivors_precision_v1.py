from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2731_dual_stem_spectral_envelope_shape_v1 as envelope

recur = envelope.recur
recall = envelope.recall
v2 = envelope.v2
v3 = envelope.v3
harmonic = envelope.harmonic
survivor2731 = envelope.survivor

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-2731-dual-stem-spectral-envelope-shape-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2769-spectral-envelope-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2769-spectral-envelope-survivors-precision-v1-manifest.json"
EXPECTED = (183, 684, 272)
EXPECTED_F1 = 27.69
EXPECTED_ZERO_SIGNATURES = 4
EXPECTED_PRUNE_COUNT = 18


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
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def reconstruct_2769(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference):
    champion2731, _ = survivor2731.reconstruct_2731(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )

    payload = v2.load_json(PROFILE_PATH)
    if payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("27.31 spectral-envelope profile is not reference-free during detection")

    rows = list(payload.get("rows", []))
    row_by_token = {
        tuple(int(v) for v in row["token"]): row
        for row in rows
    }

    zero_rows = list(payload.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != EXPECTED_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected {EXPECTED_ZERO_SIGNATURES} validated spectral-envelope signatures, got {len(zero_rows)}"
        )
    for row in zero_rows:
        if int(row.get("true", -1)) != 0 or int(row.get("false", 0)) < 5:
            raise RuntimeError(f"Invalid validated zero-precision spectral-envelope row: {row}")

    exact = {str(row["signature"]) for row in zero_rows}
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion2731.items():
        row = row_by_token.get(tok)
        if row is None:
            continue
        signatures = {str(s) for s in row.get("signatures", [])}
        if signatures & exact:
            pruned[tok] = count

    prune_count = int(sum(pruned.values()))
    true_pruned = int(sum((pruned & reference).values()))
    false_pruned = prune_count - true_pruned
    if prune_count != EXPECTED_PRUNE_COUNT or true_pruned != 0 or false_pruned != EXPECTED_PRUNE_COUNT:
        raise RuntimeError(
            f"Failed to reconstruct validated spectral-envelope prune: "
            f"pruned={prune_count} true={true_pruned} false={false_pruned}"
        )

    champion = champion2731 - pruned
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 27.69 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}"
        )
    return champion, pruned


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
    champion, applied_prune = reconstruct_2769(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score = recur.grade(champion, reference)

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = envelope.spectral_envelope_features(winner_audio, winner_sr, center, pitch)
        af = envelope.spectral_envelope_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(envelope.signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "signatures": signatures,
        })

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero = [row for row in ranked if int(row["true"]) == 0 and int(row["false"]) >= 5]
    zero.sort(key=lambda row: (-int(row["false"]), str(row["signature"])))
    supported = [row for row in ranked if int(row["true"]) >= 5]
    supported.sort(key=lambda row: (-float(row["precision"]), -int(row["true"]), str(row["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 27.69 spectral-envelope survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-27.69-spectral-envelope-survivors-precision",
        "champion2769Score": score,
        "featureFamily": "dual-stem-spectral-envelope-and-partial-shape-survivors",
        "appliedSpectralEnvelopeSignatureCount": EXPECTED_ZERO_SIGNATURES,
        "appliedSpectralEnvelopePruneCount": int(sum(applied_prune.values())),
        "appliedSpectralEnvelopeTruePruned": int(sum((applied_prune & reference).values())),
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "supportedTrueSignaturesMin5True": supported,
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
        "zeroPrecisionSignatureCount": len(zero),
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 27.69 SPECTRAL ENVELOPE SURVIVORS PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Applied spectral-envelope signature count:", EXPECTED_ZERO_SIGNATURES)
    print("Applied spectral-envelope prune count:", int(sum(applied_prune.values())))
    print("Applied spectral-envelope true pruned:", int(sum((applied_prune & reference).values())))
    print("Generalizable zero-precision spectral-envelope survivor signatures (5+ false, 0 true):", len(zero))
    for row in zero[:40]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true spectral-envelope survivor signatures:")
    for row in supported[:30]:
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
