from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-full-song-rhythm-completion-audit-v1.json"

REFERENCE_CANDIDATES = (
    PUBLIC_DIR / "gomyway-professional-rhythm-reference.json",
    PUBLIC_DIR / "gomyway-professional-rhythm-reference-full-machine.json",
    PUBLIC_DIR / "gomyway-professional-rhythm-reference-chunk-97-113-source-resolved.json",
)

TIMING_CANDIDATES = (
    PUBLIC_DIR / "gomyway-professional-timing-map-v2.json",
    PUBLIC_DIR / "gomyway-professional-timing-map-v1.json",
)

REQUIRED_ARTIFACTS = {
    "outChorusRetention": PUBLIC_DIR / "gomyway-out-chorus-retention-conclusion-v1.json",
    "finalEndingValidation": PUBLIC_DIR / "gomyway-final-ending-validation-benchmark-v1.json",
}

EXPECTED_START = 1
EXPECTED_END = 113


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def first_existing(paths: tuple[Path, ...]) -> Path:
    for path in paths:
        if path.exists():
            return path
    tried = ", ".join(str(path.relative_to(REPO_ROOT)) for path in paths)
    raise FileNotFoundError(f"No required source found. Tried: {tried}")


def measure_number(item: dict[str, Any]) -> int | None:
    for key in ("measureNumber", "measure", "barNumber", "bar"):
        value = item.get(key)
        if isinstance(value, bool):
            continue
        try:
            return int(float(value))
        except (TypeError, ValueError):
            continue
    return None


def section_name(item: dict[str, Any]) -> str:
    value = item.get("section") or item.get("sectionLabel") or "Unknown"
    return str(value).strip() or "Unknown"


def review_state(item: dict[str, Any]) -> tuple[str, bool, bool]:
    human = item.get("humanReview") or {}
    status = str(human.get("status") or item.get("reviewStatus") or "unknown")
    human_approved = bool(
        human.get("humanApproved")
        or item.get("humanApproved")
        or item.get("humanValidated")
        or status == "approved"
    )
    source_resolved = bool(
        human.get("sourceResolved")
        or item.get("sourceResolved")
        or human_approved
    )
    return status, human_approved, source_resolved


def extract_measures(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("measures", "measureReports"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def artifact_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": str(path.relative_to(REPO_ROOT)),
            "exists": False,
            "passed": False,
        }
    payload = load_json(path)
    passed = bool(
        payload.get("passed")
        or payload.get("completeOutChorusRetentionSupported")
        or payload.get("completeFinalEndingValidationSupported")
    )
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "exists": True,
        "passed": passed,
    }


def main() -> None:
    reference_path = first_existing(REFERENCE_CANDIDATES)
    timing_path = first_existing(TIMING_CANDIDATES)
    reference = load_json(reference_path)
    timing = load_json(timing_path)

    reference_measures = extract_measures(reference)
    timing_measures = extract_measures(timing)

    reference_by_measure: dict[int, dict[str, Any]] = {}
    for item in reference_measures:
        number = measure_number(item)
        if number is not None and EXPECTED_START <= number <= EXPECTED_END:
            reference_by_measure[number] = item

    timing_measure_numbers = {
        number
        for item in timing_measures
        if (number := measure_number(item)) is not None
        and EXPECTED_START <= number <= EXPECTED_END
    }

    expected = set(range(EXPECTED_START, EXPECTED_END + 1))
    reference_numbers = set(reference_by_measure)

    missing_reference = sorted(expected - reference_numbers)
    missing_timing = sorted(expected - timing_measure_numbers)

    section_measures: dict[str, list[int]] = defaultdict(list)
    status_counts: Counter[str] = Counter()
    unapproved_measures: list[int] = []
    unresolved_measures: list[int] = []
    measure_reports: list[dict[str, Any]] = []

    for number in sorted(reference_numbers):
        item = reference_by_measure[number]
        section = section_name(item)
        status, human_approved, source_resolved = review_state(item)
        section_measures[section].append(number)
        status_counts[status] += 1

        if not human_approved:
            unapproved_measures.append(number)
        if not source_resolved:
            unresolved_measures.append(number)

        measure_reports.append({
            "measureNumber": number,
            "section": section,
            "reviewStatus": status,
            "humanApproved": human_approved,
            "sourceResolved": source_resolved,
            "eventCount": len(item.get("events") or []),
            "measureFlags": item.get("measureFlags") or {},
        })

    section_reports = []
    for section, measures in sorted(
        section_measures.items(),
        key=lambda pair: min(pair[1]),
    ):
        section_unapproved = [m for m in measures if m in unapproved_measures]
        section_unresolved = [m for m in measures if m in unresolved_measures]
        section_reports.append({
            "section": section,
            "startMeasure": min(measures),
            "endMeasure": max(measures),
            "measureCount": len(measures),
            "unapprovedMeasures": section_unapproved,
            "unresolvedMeasures": section_unresolved,
            "complete": not section_unapproved and not section_unresolved,
        })

    artifacts = {
        name: artifact_summary(path)
        for name, path in REQUIRED_ARTIFACTS.items()
    }

    all_measures_present = not missing_reference and not missing_timing
    all_measures_reviewed = not unapproved_measures
    all_sources_resolved = not unresolved_measures
    all_required_artifacts_passed = all(
        item["exists"] and item["passed"] for item in artifacts.values()
    )

    passed = all(
        (
            all_measures_present,
            all_measures_reviewed,
            all_sources_resolved,
            all_required_artifacts_passed,
        )
    )

    report = {
        "schemaVersion": 1,
        "auditType": "full-song-rhythm-completion",
        "measureRange": [EXPECTED_START, EXPECTED_END],
        "referenceSource": str(reference_path.relative_to(REPO_ROOT)),
        "timingSource": str(timing_path.relative_to(REPO_ROOT)),
        "passed": passed,
        "referenceMeasureCount": len(reference_numbers),
        "timingMeasureCount": len(timing_measure_numbers),
        "missingReferenceMeasures": missing_reference,
        "missingTimingMeasures": missing_timing,
        "reviewStatusCounts": dict(sorted(status_counts.items())),
        "unapprovedMeasures": unapproved_measures,
        "unresolvedMeasures": unresolved_measures,
        "sectionCount": len(section_reports),
        "sectionReports": section_reports,
        "requiredArtifacts": artifacts,
        "allMeasuresPresent": all_measures_present,
        "allMeasuresReviewed": all_measures_reviewed,
        "allSourcesResolved": all_sources_resolved,
        "allRequiredArtifactsPassed": all_required_artifacts_passed,
        "readyForProtectedPdfComparison": passed,
        "measureReports": measure_reports,
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Full-song rhythm completion audit V1 complete")
    print("Passed:", report["passed"])
    print("Measure range:", report["measureRange"])
    print("Reference measures:", report["referenceMeasureCount"])
    print("Timing measures:", report["timingMeasureCount"])
    print("Missing reference measures:", report["missingReferenceMeasures"])
    print("Missing timing measures:", report["missingTimingMeasures"])
    print("Unapproved measures:", report["unapprovedMeasures"])
    print("Unresolved measures:", report["unresolvedMeasures"])
    print("Sections:", report["sectionCount"])
    print()

    for item in section_reports:
        print(
            f"{item['section']} "
            f"measures={item['startMeasure']}-{item['endMeasure']} "
            f"count={item['measureCount']} "
            f"complete={item['complete']} "
            f"unapproved={item['unapprovedMeasures']} "
            f"unresolved={item['unresolvedMeasures']}"
        )

    print()
    for name, item in artifacts.items():
        print(
            f"artifact {name}: "
            f"exists={item['exists']} passed={item['passed']} "
            f"path={item['path']}"
        )

    print()
    print("All measures present:", report["allMeasuresPresent"])
    print("All measures reviewed:", report["allMeasuresReviewed"])
    print("All sources resolved:", report["allSourcesResolved"])
    print("All required artifacts passed:", report["allRequiredArtifactsPassed"])
    print("Ready for protected PDF comparison:", report["readyForProtectedPdfComparison"])
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
