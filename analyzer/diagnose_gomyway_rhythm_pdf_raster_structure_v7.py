import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-raster-structure-diagnostic-v6.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-raster-structure-diagnostic-v7.json"
EXPECTED_MEASURES = 113


def stave_height(stave: dict[str, Any]) -> int:
    rows = stave["stringRowsPixels"]
    return int(rows[-1] - rows[0])


def row_overlap_ratio(a: dict[str, Any], b: dict[str, Any]) -> float:
    ar = a["stringRowsPixels"]
    br = b["stringRowsPixels"]
    a0, a1 = ar[0], ar[-1]
    b0, b1 = br[0], br[-1]
    overlap = max(0, min(a1, b1) - max(a0, b0))
    span = max(1, min(a1 - a0, b1 - b0))
    return overlap / span


def dedupe_staves(staves: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(
        staves,
        key=lambda stave: (
            stave["stringRowsPixels"][0],
            -stave["measureBoxes"],
        ),
    )
    selected: list[dict[str, Any]] = []
    for stave in ordered:
        duplicate_index = None
        for index, prior in enumerate(selected):
            if row_overlap_ratio(stave, prior) >= 0.18:
                duplicate_index = index
                break
        if duplicate_index is None:
            selected.append(stave)
            continue

        prior = selected[duplicate_index]
        # Prefer the candidate with fewer suspicious internal columns, then more boxes.
        prior_columns = len(prior["barlineColumnsPixels"])
        current_columns = len(stave["barlineColumnsPixels"])
        prior_key = (prior_columns <= 8, prior["measureBoxes"], -prior_columns)
        current_key = (current_columns <= 8, stave["measureBoxes"], -current_columns)
        if current_key > prior_key:
            selected[duplicate_index] = stave
    return sorted(selected, key=lambda stave: stave["stringRowsPixels"][0])


def cluster_with_support(values: list[int], tolerance: int = 18) -> list[dict[str, Any]]:
    if not values:
        return []
    groups: list[list[int]] = [[min(values)]]
    for value in sorted(values)[1:]:
        center = round(median(groups[-1]))
        if abs(value - center) <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [
        {
            "x": round(median(group)),
            "support": len(group),
            "members": group,
        }
        for group in groups
    ]


def page_consensus(staves: list[dict[str, Any]]) -> dict[str, Any]:
    all_columns = [
        int(x)
        for stave in staves
        for x in stave["barlineColumnsPixels"]
    ]
    clusters = cluster_with_support(all_columns)
    if not clusters:
        return {
            "pageLeftRail": None,
            "pageRightRail": None,
            "repeatedInternalColumns": [],
            "consensusColumns": [],
        }

    left = min(cluster["x"] for cluster in clusters)
    right = max(cluster["x"] for cluster in clusters)
    minimum_support = max(2, round(len(staves) * 0.40))
    repeated_internal = [
        cluster
        for cluster in clusters
        if left + 60 < cluster["x"] < right - 60
        and cluster["support"] >= minimum_support
    ]
    consensus_columns = [left] + [c["x"] for c in repeated_internal] + [right]
    consensus_columns = sorted(set(consensus_columns))
    return {
        "pageLeftRail": left,
        "pageRightRail": right,
        "minimumInternalSupport": minimum_support,
        "repeatedInternalColumns": repeated_internal,
        "consensusColumns": consensus_columns,
    }


def main() -> None:
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    pages_out: list[dict[str, Any]] = []
    total_v6_staves = 0
    total_canonical_staves = 0
    total_consensus_boxes = 0

    print("Rhythm PDF overlap-aware structure diagnostic v7 starting", flush=True)

    for page in data["pages"]:
        selected = page["selectedConfiguration"]
        v6_valid = [
            stave
            for stave in selected["staves"]
            if stave.get("plausibleSystem")
        ]
        canonical = dedupe_staves(v6_valid)
        consensus = page_consensus(canonical)
        consensus_boxes = max(0, len(consensus["consensusColumns"]) - 1)

        total_v6_staves += len(v6_valid)
        total_canonical_staves += len(canonical)
        total_consensus_boxes += consensus_boxes * len(canonical)

        pages_out.append(
            {
                "pageNumber": page["pageNumber"],
                "v6ValidStaves": len(v6_valid),
                "canonicalNonOverlappingStaves": len(canonical),
                "canonicalStaves": canonical,
                "pageConsensus": consensus,
                "consensusBoxesPerCanonicalStave": consensus_boxes,
                "rawConsensusBoxTotalForPage": consensus_boxes * len(canonical),
                "warning": (
                    "Raw page totals are diagnostic only because adjacent PDF pages "
                    "contain overlapping source measures."
                ),
            }
        )

        print(
            f'Page {page["pageNumber"]}: '
            f'{len(v6_valid)} v6 staves -> {len(canonical)} canonical; '
            f'{consensus_boxes} consensus boxes/stave',
            flush=True,
        )

    output = {
        "diagnosticName": "Gomyway rhythm PDF overlap-aware structure diagnostic v7",
        "inputDiagnostic": str(INPUT_PATH.relative_to(ROOT)),
        "pdfPageCount": data["pdfPageCount"],
        "metadataSourcePageCount": data["metadataSourcePageCount"],
        "pdfPageCountUsedAsAuthority": True,
        "totalV6ValidStaves": total_v6_staves,
        "totalCanonicalNonOverlappingStaves": total_canonical_staves,
        "rawConsensusBoxTotalAcrossPages": total_consensus_boxes,
        "rawConsensusTotalMayNotBeComparedDirectlyTo113": True,
        "reason": (
            "The PDF pages are overlapping screen captures; measures visible at the "
            "bottom of one page reappear at the top of the next. Global measure-number "
            "anchoring is required before deduplicated 1-113 extraction."
        ),
        "nextRequiredStage": "measure-number-anchor-extraction",
        "expectedUniqueMeasureNumbers": EXPECTED_MEASURES,
        "verifiedMeasures1To16Protected": True,
        "rhythmGuitarOnlyTarget": True,
        "professionalReferenceRemainsAuthority": True,
        "candidateOutputMayNotBecomeReference": True,
        "productionPromotionAllowed": False,
        "pages": pages_out,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rhythm PDF overlap-aware structure diagnostic v7 complete", flush=True)
    print(f"V6 valid staves: {total_v6_staves}", flush=True)
    print(f"Canonical non-overlapping staves: {total_canonical_staves}", flush=True)
    print(f"Raw consensus boxes across pages: {total_consensus_boxes}", flush=True)
    print("Raw total comparable directly to 113: False", flush=True)
    print("Next required stage: measure-number-anchor-extraction", flush=True)
    print("Verified measures 1-16 protected: True", flush=True)
    print("Production promotion allowed: False", flush=True)
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
