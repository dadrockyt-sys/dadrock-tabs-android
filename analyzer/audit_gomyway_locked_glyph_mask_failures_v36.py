import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-locked-glyph-mask-rebuild-v35.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-glyph-mask-failure-audit-v36.json"
REQUIRED_FRETS = ["0", "2", "3"]
MIN_RATIO = 0.015
MAX_RATIO = 0.48


def main() -> None:
    if not SOURCE_PATH.exists():
        raise RuntimeError(f"Missing prerequisite: {SOURCE_PATH.relative_to(ROOT)}")

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if not bool(source.get("allMasksBuilt", False)):
        raise RuntimeError("V35 did not build all masks")

    failures: list[dict[str, Any]] = []
    ratios_by_fret: dict[str, list[float]] = defaultdict(list)
    selected_counts: Counter[int] = Counter()
    selected_counts_by_fret: dict[str, Counter[int]] = defaultdict(Counter)
    entries_observed = 0

    print("Locked glyph mask failure audit v36 starting", flush=True)

    for fret in REQUIRED_FRETS:
        entries = source.get("cleanMasks", {}).get(fret, [])
        for entry in entries:
            entries_observed += 1
            metadata = entry.get("maskMetadata", {})
            ratio = float(metadata.get("foregroundRatio", 0.0))
            foreground_pixels = int(metadata.get("foregroundPixels", 0))
            component_count = int(metadata.get("selectedComponentCount", 0))
            ratios_by_fret[fret].append(ratio)
            selected_counts[component_count] += 1
            selected_counts_by_fret[fret][component_count] += 1

            reason = None
            if ratio < MIN_RATIO:
                reason = "foreground-too-sparse"
            elif ratio > MAX_RATIO:
                reason = "foreground-too-dense"

            if reason is not None:
                failures.append({
                    "templateId": entry.get("templateId"),
                    "fret": fret,
                    "measure": entry.get("measure"),
                    "stringHighEToLowE": entry.get("stringHighEToLowE"),
                    "foregroundRatio": ratio,
                    "foregroundPixels": foreground_pixels,
                    "selectedComponentCount": component_count,
                    "sourceCrop": entry.get("sourceCrop"),
                    "sourceBoundingBox": entry.get("sourceBoundingBox"),
                    "cleanMaskImage": entry.get("cleanMaskImage"),
                    "reason": reason,
                })

    summary_by_fret: dict[str, dict[str, Any]] = {}
    for fret in REQUIRED_FRETS:
        ratios = ratios_by_fret[fret]
        if not ratios:
            summary_by_fret[fret] = {
                "count": 0,
                "minimumForegroundRatio": None,
                "medianForegroundRatio": None,
                "maximumForegroundRatio": None,
                "failureCount": 0,
                "selectedComponentCounts": {},
            }
            continue
        summary_by_fret[fret] = {
            "count": len(ratios),
            "minimumForegroundRatio": round(min(ratios), 6),
            "medianForegroundRatio": round(median(ratios), 6),
            "maximumForegroundRatio": round(max(ratios), 6),
            "failureCount": sum(1 for item in failures if item["fret"] == fret),
            "selectedComponentCounts": dict(selected_counts_by_fret[fret]),
        }

    sparse_failures = [item for item in failures if item["reason"] == "foreground-too-sparse"]
    dense_failures = [item for item in failures if item["reason"] == "foreground-too-dense"]
    all_failures_isolated = len(failures) > 0 and len(failures) <= 12

    output = {
        "diagnosticName": "Gomyway locked glyph mask failure audit v36",
        "referenceType": "locked-professional-glyph-mask-statistics-audit",
        "sourceMaskRebuild": str(SOURCE_PATH.relative_to(ROOT)),
        "requiredFretClasses": REQUIRED_FRETS,
        "plausibleForegroundRange": [MIN_RATIO, MAX_RATIO],
        "maskEntriesObserved": entries_observed,
        "summaryByFret": summary_by_fret,
        "selectedComponentCountDistribution": dict(selected_counts),
        "implausibleMaskCount": len(failures),
        "sparseFailureCount": len(sparse_failures),
        "denseFailureCount": len(dense_failures),
        "implausibleMasks": failures,
        "allFailuresIsolatedForTargetedRebuild": all_failures_isolated,
        "humanVisualValidationComplete": False,
        "glyphMasksHumanApproved": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "targeted-rebuild-of-v36-implausible-masks-v37"
            if all_failures_isolated
            else "recalibrate-mask-threshold-and-component-selection-v37"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked glyph mask failure audit v36 complete")
    print(f"Mask entries observed: {entries_observed}")
    for fret in REQUIRED_FRETS:
        summary = summary_by_fret[fret]
        print(
            f"Fret {fret}: count={summary['count']}, "
            f"min={summary['minimumForegroundRatio']}, "
            f"median={summary['medianForegroundRatio']}, "
            f"max={summary['maximumForegroundRatio']}, "
            f"failures={summary['failureCount']}",
            flush=True,
        )
    print(f"Implausible mask count: {len(failures)}")
    print(f"Sparse failure count: {len(sparse_failures)}")
    print(f"Dense failure count: {len(dense_failures)}")
    print(f"Selected component count distribution: {dict(selected_counts)}")
    for item in failures:
        print(
            f"FAIL {item['templateId']}: fret={item['fret']}, "
            f"m={item['measure']}, s={item['stringHighEToLowE']}, "
            f"ratio={item['foregroundRatio']:.6f}, "
            f"pixels={item['foregroundPixels']}, "
            f"components={item['selectedComponentCount']}, "
            f"reason={item['reason']}",
            flush=True,
        )
    print(f"All failures isolated for targeted rebuild: {all_failures_isolated}")
    print("Human visual validation complete: False")
    print("Glyph masks human approved: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
