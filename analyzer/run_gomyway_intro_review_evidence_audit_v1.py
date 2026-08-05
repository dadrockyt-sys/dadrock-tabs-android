from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
ANALYZER_DIR = REPO_ROOT / "analyzer"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-intro-review-evidence-audit-v1.json"

INTRO_START = 1
INTRO_END = 16
MAX_FILE_BYTES = 40_000_000

REVIEW_TERMS = (
    "approved",
    "humanvalidated",
    "humanapproved",
    "reviewed",
    "locked",
    "passed",
    "protected",
)
RESOLUTION_TERMS = (
    "sourceresolved",
    "resolved",
    "locked",
    "protected",
    "passed",
)
INTRO_TERMS = (
    "intro",
    "orientation",
    "offset",
    "12-slot",
    "12 slot",
    "rhythm template",
)
MEASURE_KEYS = (
    "measureNumber",
    "measure",
    "barNumber",
    "bar",
)


def normalized(value: Any) -> str:
    return str(value).strip().lower().replace("_", "").replace("-", "").replace(" ", "")


def integer_value(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            number = float(value)
        except ValueError:
            return None
        if number.is_integer():
            return int(number)
    return None


def measure_from_record(record: dict[str, Any]) -> int | None:
    for key in MEASURE_KEYS:
        if key in record:
            value = integer_value(record.get(key))
            if value is not None:
                return value
    return None


def walk(node: Any, path: str = "$") -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(node, dict):
        yield path, node
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")


def record_signals(record: dict[str, Any]) -> tuple[bool, bool, list[str]]:
    flattened: list[str] = []
    for key, value in record.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            flattened.append(f"{normalized(key)}={normalized(value)}")
    text = " ".join(flattened)
    review = any(term in text for term in REVIEW_TERMS)
    resolution = any(term in text for term in RESOLUTION_TERMS)
    matched_intro_terms = [term for term in INTRO_TERMS if normalized(term) in text]
    return review, resolution, matched_intro_terms


def compact_record(record: dict[str, Any], json_path: str) -> dict[str, Any]:
    keep = {
        "measureNumber",
        "measure",
        "barNumber",
        "bar",
        "section",
        "sectionLabel",
        "status",
        "reviewStatus",
        "humanApproved",
        "humanValidated",
        "sourceResolved",
        "passed",
        "locked",
        "protected",
        "orientationOffset",
        "offset",
        "templateLength",
        "slotCount",
        "notes",
    }
    result = {
        key: value
        for key, value in record.items()
        if key in keep and isinstance(value, (str, int, float, bool, type(None), list, dict))
    }
    result["jsonPath"] = json_path
    return result


def json_files() -> list[Path]:
    candidates = list(PUBLIC_DIR.glob("gomyway*.json"))
    candidates.extend(ANALYZER_DIR.glob("*gomyway*intro*.json"))
    return sorted({path for path in candidates if path != OUTPUT_PATH})


def main() -> None:
    reviewed_measures: set[int] = set()
    resolved_measures: set[int] = set()
    files_with_intro_evidence: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []
    keyword_only_files: list[dict[str, Any]] = []

    for path in json_files():
        if path.stat().st_size > MAX_FILE_BYTES:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            parse_errors.append({
                "file": str(path.relative_to(REPO_ROOT)),
                "error": f"{type(exc).__name__}: {exc}",
            })
            continue

        file_records: list[dict[str, Any]] = []
        file_reviewed: set[int] = set()
        file_resolved: set[int] = set()
        intro_term_counts: Counter[str] = Counter()

        for json_path, record in walk(payload):
            review, resolution, intro_terms = record_signals(record)
            for term in intro_terms:
                intro_term_counts[term] += 1

            measure = measure_from_record(record)
            if measure is None or not INTRO_START <= measure <= INTRO_END:
                continue

            if review:
                reviewed_measures.add(measure)
                file_reviewed.add(measure)
            if resolution:
                resolved_measures.add(measure)
                file_resolved.add(measure)

            if review or resolution or intro_terms:
                file_records.append(compact_record(record, json_path))

        if file_records or file_reviewed or file_resolved:
            files_with_intro_evidence.append({
                "file": str(path.relative_to(REPO_ROOT)),
                "reviewedMeasures": sorted(file_reviewed),
                "resolvedMeasures": sorted(file_resolved),
                "introTermCounts": dict(sorted(intro_term_counts.items())),
                "sampleRecords": file_records[:24],
            })
        elif intro_term_counts:
            keyword_only_files.append({
                "file": str(path.relative_to(REPO_ROOT)),
                "introTermCounts": dict(sorted(intro_term_counts.items())),
            })

    expected = set(range(INTRO_START, INTRO_END + 1))
    missing_review = sorted(expected - reviewed_measures)
    missing_resolution = sorted(expected - resolved_measures)

    report = {
        "schemaVersion": 1,
        "auditType": "intro-review-evidence",
        "measureRange": [INTRO_START, INTRO_END],
        "reviewedMeasures": sorted(reviewed_measures),
        "resolvedMeasures": sorted(resolved_measures),
        "missingReviewEvidenceMeasures": missing_review,
        "missingResolutionEvidenceMeasures": missing_resolution,
        "filesWithIntroEvidence": files_with_intro_evidence,
        "keywordOnlyFiles": keyword_only_files,
        "parseErrors": parse_errors,
        "allIntroMeasuresHaveReviewEvidence": not missing_review,
        "allIntroMeasuresHaveResolutionEvidence": not missing_resolution,
        "readyToMergeIntoFullSongReconciliation": not missing_review and not missing_resolution,
        "interpretation": (
            "The full-song reconciliation found evidence for measures 17-113 and isolated measures "
            "1-16 as the only remaining gap. This audit searches specifically for the locked intro "
            "orientation, rhythm-template, approval, and source-resolution evidence before changing "
            "the completion logic. A missing result means the intro evidence needs a dedicated "
            "read-only conclusion artifact; it does not mean the intro transcription itself failed."
        ),
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Intro review-evidence audit V1 complete")
    print("Measure range:", report["measureRange"])
    print("Reviewed intro measures:", report["reviewedMeasures"])
    print("Resolved intro measures:", report["resolvedMeasures"])
    print("Missing review evidence measures:", report["missingReviewEvidenceMeasures"])
    print("Missing resolution evidence measures:", report["missingResolutionEvidenceMeasures"])
    print("Files with intro evidence:", len(files_with_intro_evidence))
    print("Ready to merge into full-song reconciliation:", report["readyToMergeIntoFullSongReconciliation"])
    print()

    for item in files_with_intro_evidence:
        print(
            item["file"],
            "reviewed=", item["reviewedMeasures"],
            "resolved=", item["resolvedMeasures"],
            "introTerms=", item["introTermCounts"],
        )

    print()
    print("Automatic promotion allowed: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
