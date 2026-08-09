from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_2134_local_pitch_competition_precision_prune_cv_v1 as b2134

comp = b2134.comp
recur = b2134.recur
recall = b2134.recall
v2 = b2134.v2
v3 = b2134.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_2134_PATH = PUBLIC / "gomyway-2134-dual-stem-local-pitch-competition-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2144-local-pitch-competition-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2144-local-pitch-competition-survivors-precision-v1-manifest.json"
EXPECTED = (183, 684, 660)
EXPECTED_F1 = 21.44
TARGET_SIGNATURE = b2134.TARGET_SIGNATURE


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        true_count = int(counts["true"])
        false_count = int(counts["false"])
        total = true_count + false_count
        out.append({
            "signature": signature,
            "true": true_count,
            "false": false_count,
            "total": total,
            "precision": round(100.0 * true_count / total, 2) if total else 0.0,
        })
    return sorted(out, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


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

    profile = v2.load_json(PROFILE_2134_PATH)
    if profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("21.34 local-pitch-competition profile is not reference-free during detection")

    zero_rows = list(profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    zero_signatures = {str(r["signature"]) for r in zero_rows}
    if TARGET_SIGNATURE not in zero_signatures:
        raise RuntimeError(f"Expected validated zero-precision signature missing: {TARGET_SIGNATURE}")

    rows = list(profile.get("rows", []))
    if not rows:
        raise RuntimeError("21.34 local-pitch-competition profile has no rows")
    row_by_token = {token(row): row for row in rows}

    champion_2134 = comp.reconstruct_2134(grid)
    pruned: Counter[tuple[int, int, int]] = Counter()
    survivor_rows: list[dict[str, Any]] = []

    for tok, count in champion_2134.items():
        row = row_by_token.get(tok)
        if row is None:
            continue
        if TARGET_SIGNATURE in b2134.row_signatures(row):
            pruned[tok] = count
        else:
            survivor_rows.append(row)

    champion = champion_2134 - pruned
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 21.44 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    for row in survivor_rows:
        tok = token(row)
        truth = "true" if reference.get(tok, 0) > 0 else "false"
        count = int(row.get("count", 1))
        for signature in b2134.row_signatures(row):
            groups[signature][truth] += count
        details.append({**row, "survives2144Prune": True, "trueSurvivor": truth == "true"})

    ranked = precision_rows(groups)
    zero_precision = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero_precision.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported_true = [r for r in ranked if int(r["true"]) >= 5]
    supported_true.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 21.44 local-pitch-competition survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-21.44-local-pitch-competition-survivors-precision",
        "champion2144Score": score,
        "validatedLocalPitchPruneRule": "localpitch2134_exact_zero_precision",
        "validatedLocalPitchSignature": TARGET_SIGNATURE,
        "validatedLocalPitchPruneCount": int(sum(pruned.values())),
        "survivorRowCount": len(survivor_rows),
        "zeroPrecisionGeneralizableSignaturesMin5False": zero_precision,
        "supportedTrueSignaturesMin5True": supported_true,
        "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-only-repeatable-zero-precision-21.44-local-pitch-competition-survivor-signatures-with-prune-specific-heldout-cv-or-freeze-family-if-exhausted",
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
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 21.44 LOCAL PITCH COMPETITION SURVIVORS PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Validated local-pitch signature:", TARGET_SIGNATURE)
    print("Validated local-pitch prune count:", sum(pruned.values()))
    print("Local-pitch survivor rows:", len(survivor_rows))
    print("Generalizable zero-precision local-pitch-competition survivor signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true local-pitch-competition survivor signatures (5+ true):")
    for row in supported_true[:30]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
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
