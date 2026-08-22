from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

import benchmark_gomyway_1419_champion_cached_repeatable_residual_joint_gate_v1 as bench

v2 = bench.v2
recall = bench.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-source-strength-evidence-inventory-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-source-strength-evidence-inventory-v1-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def floating(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def quantiles(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0}
    ordered = sorted(values)

    def pct(p: float) -> float:
        if len(ordered) == 1:
            return ordered[0]
        pos = (len(ordered) - 1) * p
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            return ordered[lo]
        frac = pos - lo
        return ordered[lo] * (1.0 - frac) + ordered[hi] * frac

    return {
        "count": len(ordered),
        "min": round(ordered[0], 6),
        "p10": round(pct(0.10), 6),
        "p25": round(pct(0.25), 6),
        "median": round(statistics.median(ordered), 6),
        "p75": round(pct(0.75), 6),
        "p90": round(pct(0.90), 6),
        "max": round(ordered[-1], 6),
        "mean": round(statistics.mean(ordered), 6),
    }


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    strength_values: list[float] = []
    confidence_values: list[float] = []
    pairs: list[tuple[float, float]] = []
    source_counts: Counter[str] = Counter()

    for event in events:
        strength = floating(event.get("strength"))
        confidence = floating(event.get("confidence"))
        if strength is not None:
            strength_values.append(strength)
        if confidence is not None:
            confidence_values.append(confidence)
        if strength is not None and confidence is not None:
            pairs.append((strength, confidence))
        source = event.get("source")
        if source is not None:
            source_counts[str(source)] += 1

    pearson = None
    if len(pairs) >= 2:
        xs = [x for x, _ in pairs]
        ys = [y for _, y in pairs]
        mx = statistics.mean(xs)
        my = statistics.mean(ys)
        num = sum((x - mx) * (y - my) for x, y in pairs)
        den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
        den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
        if den_x > 0.0 and den_y > 0.0:
            pearson = round(num / (den_x * den_y), 6)

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during strength evidence inventory")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-source-strength-evidence-inventory",
        "protectedEventCount": len(events),
        "strengthSummary": quantiles(strength_values),
        "confidenceSummary": quantiles(confidence_values),
        "strengthConfidencePairCount": len(pairs),
        "strengthConfidencePearson": pearson,
        "sourceCounts": dict(source_counts.most_common()),
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "not-used-in-inventory",
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
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 SOURCE STRENGTH EVIDENCE INVENTORY V1")
    print("Passed: True")
    print("Protected event count:", len(events))
    print("Strength summary:", output["strengthSummary"])
    print("Confidence summary:", output["confidenceSummary"])
    print("Strength/confidence pair count:", len(pairs))
    print("Strength/confidence Pearson:", pearson)
    print("Source counts:", output["sourceCounts"])
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
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
