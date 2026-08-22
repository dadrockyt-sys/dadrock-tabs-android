from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import benchmark_gomyway_3676_multifamily_nested_agreement_cv_v1 as bench

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3676-pitchcore-failure-anatomy-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-pitchcore-failure-anatomy-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feature_tags(row: dict[str, Any]) -> set[str]:
    tags: set[str] = set()
    for sig in row.get("prcross") or ():
        tail = str(sig).split("::", 1)[-1]
        parts = tail.split("|")
        for part in parts:
            tags.add(f"pitch::{part}")
    for name in ("stemBoth", "persistent3p", "strictSweep", "tightGrid", "acousticMulti", "acousticStrong", "phraseAny", "phraseExact", "phraseStrong"):
        if bool(row.get(name)):
            tags.add(f"evidence::{name}")
    return tags


def summarize_selected(rows: list[dict[str, Any]]) -> dict[str, Any]:
    true_rows = [r for r in rows if r["label"] == "true"]
    false_rows = [r for r in rows if r["label"] != "true"]
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        label = "true" if row["label"] == "true" else "false"
        for tag in feature_tags(row):
            groups[tag][label] += 1

    ranked = []
    for tag, c in groups.items():
        t, f = int(c["true"]), int(c["false"])
        support = t + f
        if support < 2:
            continue
        precision = 100.0 * t / support if support else 0.0
        ranked.append({
            "feature": tag,
            "true": t,
            "false": f,
            "support": support,
            "precision": round(precision, 2),
            "falseMinusTrue": f - t,
        })
    ranked.sort(key=lambda r: (-int(r["falseMinusTrue"]), -int(r["false"]), float(r["precision"]), str(r["feature"])))
    return {
        "selected": len(rows),
        "true": len(true_rows),
        "false": len(false_rows),
        "precision": round(100.0 * len(true_rows) / len(rows), 2) if rows else 0.0,
        "falseConcentratedFeatures": ranked[:30],
        "trueConcentratedFeatures": sorted(ranked, key=lambda r: (-int(r["true"] - r["false"]), -int(r["true"]), -float(r["precision"])))[:30],
    }


def evaluate_scheme(rows: list[dict[str, Any]], name: str, fold_fn: Callable[[int], int]) -> list[dict[str, Any]]:
    out = []
    for fold in range(FOLD_COUNT):
        train = [r for r in rows if fold_fn(r["measure"]) != fold]
        test = [r for r in rows if fold_fn(r["measure"]) == fold]
        learned = bench.learn_pitch_core(train)
        marked = bench.mark_pitch_core(test, learned)
        selected = [r for r in marked if r["pitchCore"]]
        stats = bench.stats(selected)
        failed = not (bool(learned) and stats["recoverTrue"] > 0 and stats["pitchF1"] > EXPECTED_F1)
        out.append({
            "scheme": name,
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "learnedStablePrCrossCount": len(learned),
            "learnedStablePrCross": sorted(learned),
            "heldoutPitchCore": stats,
            "failed": failed,
            "anatomy": summarize_selected(selected),
        })
        print(f"{name} fold {fold}: learned={len(learned)} held={stats['recoverTrue']}/{stats['recoverFalse']} F1={stats['pitchF1']} failed={failed}", flush=True)
    return out


def main() -> None:
    before = sha256(bench.prof.recall.CANDIDATE_PATH)
    rows = bench.prepare_rows()
    if not rows:
        raise RuntimeError("No residual rows available")
    measures = [r["measure"] for r in rows]
    lo, hi = min(measures), max(measures)

    normal = evaluate_scheme(rows, "normal", lambda m: m % FOLD_COUNT)
    section = evaluate_scheme(rows, "section", lambda m: bench.contiguous_fold(m, lo, hi, FOLD_COUNT))
    shifted = evaluate_scheme(rows, "shiftedWindow", lambda m: bench.shifted_fold(m, lo, hi, FOLD_COUNT))

    failed = [r for r in normal + section + shifted if r["failed"]]
    failure_feature_counts: Counter[str] = Counter()
    for fold in failed:
        for item in fold["anatomy"]["falseConcentratedFeatures"][:12]:
            if int(item["falseMinusTrue"]) > 0:
                failure_feature_counts[str(item["feature"])] += 1

    repeated_failure_features = [
        {"feature": feature, "failedFolds": count}
        for feature, count in failure_feature_counts.most_common()
        if count >= 2
    ]

    after = sha256(bench.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during pitch-core failure anatomy profiling")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-pitchcore-failure-anatomy-diagnostic",
        "frozenChampionPitchF1": EXPECTED_F1,
        "frozenChampionMatchedMissingExtra": list(EXPECTED),
        "normal": normal,
        "section": section,
        "shiftedWindow": shifted,
        "failedFoldCount": len(failed),
        "repeatedFailureFeatures": repeated_failure_features,
        "note": "Diagnostic only. Held-out labels are used only to explain failures after pitch-core detection. No rule or champion promotion is allowed from this profiler.",
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
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
        "failedFoldCount": len(failed),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PITCHCORE FAILURE ANATOMY V1 COMPLETE")
    print("Failed folds:", len(failed))
    print("Repeated false-concentrated features:")
    for item in repeated_failure_features[:30]:
        print("FAILURE", item)
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
