from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ABS_PATH = PUBLIC / "gomyway-3676-patch-ridge-recurrent-feature-gate-nested-cv-v1.json"
RANK_PATH = PUBLIC / "gomyway-3676-patch-ridge-relative-rank-calibration-nested-cv-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-ridge-calibration-strategy-comparison-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-ridge-calibration-strategy-comparison-v1-manifest.json"

EXPECTED = (272, 595, 341)


def scheme_rows(payload: dict, scheme: str) -> list[dict]:
    key_map = {
        "normal": "normalCv",
        "section": "sectionCv",
        "shiftedWindow": "shiftedWindowCv",
    }
    return list(payload.get(key_map[scheme]) or [])


def held(row: dict) -> tuple[int, int, float, float, float]:
    cand = row.get("heldoutCandidate") or {}
    base = row.get("heldoutBase") or {}
    true = int(cand.get("true", 0))
    false = int(cand.get("false", 0))
    precision = float(cand.get("precision", 0.0))
    base_precision = float(base.get("precision", 0.0))
    lift = float(row.get("heldoutPrecisionLift", precision - base_precision))
    return true, false, precision, base_precision, lift


def selected_pct(row: dict) -> float:
    cand = row.get("heldoutCandidate") or {}
    selected = int(cand.get("selected", 0))
    test_rows = int(row.get("testRows", 0))
    return round(100.0 * selected / test_rows, 3) if test_rows else 0.0


def main() -> None:
    if not ABS_PATH.exists():
        raise RuntimeError(f"Missing absolute-threshold result: {ABS_PATH.name}")
    if not RANK_PATH.exists():
        raise RuntimeError(f"Missing relative-rank result: {RANK_PATH.name}")

    absolute = json.loads(ABS_PATH.read_text(encoding="utf-8"))
    rank = json.loads(RANK_PATH.read_text(encoding="utf-8"))

    if tuple(absolute.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Absolute-threshold result is not anchored to frozen 36.76 champion")
    if tuple(rank.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Relative-rank result is not anchored to frozen 36.76 champion")

    comparisons: list[dict] = []
    aggregate = defaultdict(lambda: {"absoluteWins": 0, "rankWins": 0, "ties": 0, "absolutePass": 0, "rankPass": 0})

    for scheme in ["normal", "section", "shiftedWindow"]:
        a_rows = scheme_rows(absolute, scheme)
        r_rows = scheme_rows(rank, scheme)
        if len(a_rows) != len(r_rows):
            raise RuntimeError(f"Fold count mismatch for {scheme}: {len(a_rows)} vs {len(r_rows)}")

        for a, r in zip(a_rows, r_rows):
            if int(a.get("fold", -1)) != int(r.get("fold", -1)):
                raise RuntimeError(f"Fold identity mismatch in {scheme}")
            fold = int(a.get("fold", -1))
            at, af, ap, ab, al = held(a)
            rt, rf, rp, rb, rl = held(r)
            if rl > al + 1e-9:
                winner = "relativeRank"
                aggregate[scheme]["rankWins"] += 1
            elif al > rl + 1e-9:
                winner = "absoluteThreshold"
                aggregate[scheme]["absoluteWins"] += 1
            else:
                winner = "tie"
                aggregate[scheme]["ties"] += 1
            aggregate[scheme]["absolutePass"] += int(bool(a.get("passed")))
            aggregate[scheme]["rankPass"] += int(bool(r.get("passed")))

            row = {
                "scheme": scheme,
                "fold": fold,
                "winnerByLift": winner,
                "absolute": {
                    "true": at,
                    "false": af,
                    "precision": ap,
                    "basePrecision": ab,
                    "lift": al,
                    "selectedPct": selected_pct(a),
                    "passed": bool(a.get("passed")),
                    "lambda": a.get("lambda"),
                    "tailQuantile": a.get("tailQuantile"),
                },
                "relativeRank": {
                    "true": rt,
                    "false": rf,
                    "precision": rp,
                    "basePrecision": rb,
                    "lift": rl,
                    "selectedPct": selected_pct(r),
                    "passed": bool(r.get("passed")),
                    "lambda": r.get("lambda"),
                    "tailQuantile": r.get("tailQuantile"),
                },
                "liftDeltaRankMinusAbsolute": round(rl - al, 2),
                "selectedPctDeltaRankMinusAbsolute": round(selected_pct(r) - selected_pct(a), 3),
            }
            comparisons.append(row)
            print("COMPARE", row, flush=True)

    summary = {k: dict(v) for k, v in aggregate.items()}
    print("SUMMARY", summary, flush=True)

    # This profiler is diagnosis only. It deliberately does not invent a hybrid rule.
    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-ridge-calibration-strategy-comparison-read-only",
        "baselineMatchedMissingExtra": list(EXPECTED),
        "comparisons": comparisons,
        "summary": summary,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "note": "Read-only comparison of two already-completed nested-CV calibration strategies. No new detector is trained and no hybrid rule is selected from held-out labels.",
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH RIDGE CALIBRATION STRATEGY COMPARISON V1 COMPLETE")
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
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
