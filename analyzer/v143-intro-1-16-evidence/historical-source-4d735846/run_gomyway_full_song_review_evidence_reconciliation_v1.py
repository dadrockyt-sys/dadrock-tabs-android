from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-full-song-review-evidence-reconciliation-v1.json"

EXPECTED_START = 1
EXPECTED_END = 113
MAX_FILE_BYTES = 50_000_000

MEASURE_KEYS = ("measureNumber", "measure", "barNumber", "bar")
START_KEYS = ("startMeasure", "measureStart", "firstMeasure")
END_KEYS = ("endMeasure", "measureEnd", "lastMeasure")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def int_value(value: Any) -> int | None:
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


def explicit_measure(record: dict[str, Any]) -> int | None:
    for key in MEASURE_KEYS:
        if key in record:
            number = int_value(record.get(key))
            if number is not None:
                return number
    return None


def measure_range(record: dict[str, Any]) -> tuple[int, int] | None:
    start = None
    end = None
    for key in START_KEYS:
        start = int_value(record.get(key))
        if start is not None:
            break
    for key in END_KEYS:
        end = int_value(record.get(key))
        if end is not None:
            break
    if start is not None and end is not None and start <= end:
        return start, end

    value = record.get("measureRange")
    if isinstance(value, list) and len(value) >= 2:
        start = int_value(value[0])
        end = int_value(value[1])
        if start is not None and end is not None and start <= end:
            return start, end
    return None


def walk(node: Any, path: str = "$") -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(node, dict):
        yield path, node
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")


def approval_state(record: dict[str, Any]) -> tuple[bool, bool, str]:
    human = record.get("humanReview")
    if not isinstance(human, dict):
        human = {}

    status = str(
        human.get("status")
        or record.get("reviewStatus")
        or record.get("status")
        or ""
    ).strip().lower()

    approved = bool(
        human.get("humanApproved")
        or human.get("humanValidated")
        or record.get("humanApproved")
        or record.get("humanValidated")
        or status in {"approved", "validated", "passed", "complete"}
    )
    resolved = bool(
        human.get("sourceResolved")
        or record.get("sourceResolved")
        or approved
    )
    return approved, resolved, status


def passed_state(record: dict[str, Any]) -> bool:
    if record.get("passed") is True:
        return True
    for key, value in record.items():
        if not isinstance(key, str):
            continue
        lowered = key.lower()
        if value is True and (
            lowered.endswith("supported")
            or lowered.endswith("complete")
            or lowered.endswith("preserved")
            or lowered.endswith("validated")
        ):
            return True
    return False


def is_relevant_file(path: Path) -> bool:
    name = path.name.lower()
    return name.startswith("gomyway") and any(
        token in name
        for token in (
            "professional-rhythm-reference",
            "benchmark",
            "conclusion",
            "validation",
            "adjudication",
            "consensus",
            "review",
            "retention",
        )
    )


def main() -> None:
    evidence: dict[int, list[dict[str, Any]]] = defaultdict(list)
    artifact_reports: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []

    for file_path in sorted(PUBLIC_DIR.glob("gomyway*.json")):
        if file_path == OUTPUT_PATH or not is_relevant_file(file_path):
            continue
        if file_path.stat().st_size > MAX_FILE_BYTES:
            continue

        try:
            payload = load_json(file_path)
        except Exception as exc:
            parse_errors.append({
                "file": str(file_path.relative_to(REPO_ROOT)),
                "error": f"{type(exc).__name__}: {exc}",
            })
            continue

        file_passed = isinstance(payload, dict) and passed_state(payload)
        covered_measures: set[int] = set()
        explicit_approved: set[int] = set()
        explicit_resolved: set[int] = set()

        for json_path, record in walk(payload):
            approved, resolved, status = approval_state(record)
            number = explicit_measure(record)
            if number is not None and EXPECTED_START <= number <= EXPECTED_END:
                covered_measures.add(number)
                if approved:
                    explicit_approved.add(number)
                if resolved:
                    explicit_resolved.add(number)
                if approved or resolved:
                    evidence[number].append({
                        "file": str(file_path.relative_to(REPO_ROOT)),
                        "jsonPath": json_path,
                        "type": "explicit-measure-review",
                        "approved": approved,
                        "sourceResolved": resolved,
                        "status": status,
                    })

            span = measure_range(record)
            if span is not None and (file_passed or passed_state(record)):
                start, end = span
                start = max(start, EXPECTED_START)
                end = min(end, EXPECTED_END)
                if start <= end:
                    for measure in range(start, end + 1):
                        evidence[measure].append({
                            "file": str(file_path.relative_to(REPO_ROOT)),
                            "jsonPath": json_path,
                            "type": "passed-range-artifact",
                            "approved": True,
                            "sourceResolved": True,
                            "status": "artifact-passed",
                        })

        artifact_reports.append({
            "file": str(file_path.relative_to(REPO_ROOT)),
            "topLevelPassed": file_passed,
            "coveredMeasureCount": len(covered_measures),
            "explicitApprovedMeasures": sorted(explicit_approved),
            "explicitResolvedMeasures": sorted(explicit_resolved),
        })

    expected = set(range(EXPECTED_START, EXPECTED_END + 1))
    approved_measures = {
        measure
        for measure, rows in evidence.items()
        if any(row["approved"] for row in rows)
    }
    resolved_measures = {
        measure
        for measure, rows in evidence.items()
        if any(row["sourceResolved"] for row in rows)
    }

    missing_review_evidence = sorted(expected - approved_measures)
    missing_resolution_evidence = sorted(expected - resolved_measures)

    measure_reports = []
    for measure in range(EXPECTED_START, EXPECTED_END + 1):
        rows = evidence.get(measure, [])
        measure_reports.append({
            "measureNumber": measure,
            "reviewEvidenceFound": measure in approved_measures,
            "sourceResolutionEvidenceFound": measure in resolved_measures,
            "evidenceCount": len(rows),
            "evidence": rows,
        })

    report = {
        "schemaVersion": 1,
        "auditType": "full-song-review-evidence-reconciliation",
        "measureRange": [EXPECTED_START, EXPECTED_END],
        "filesExamined": len(artifact_reports),
        "measuresWithReviewEvidence": len(approved_measures),
        "measuresWithResolutionEvidence": len(resolved_measures),
        "missingReviewEvidenceMeasures": missing_review_evidence,
        "missingResolutionEvidenceMeasures": missing_resolution_evidence,
        "allMeasuresHaveReviewEvidence": not missing_review_evidence,
        "allMeasuresHaveResolutionEvidence": not missing_resolution_evidence,
        "readyToRepairCompletionAudit": (
            not missing_review_evidence and not missing_resolution_evidence
        ),
        "artifactReports": artifact_reports,
        "measureReports": measure_reports,
        "parseErrors": parse_errors,
        "interpretation": (
            "The V1 completion audit treated the monolithic professional-reference metadata as the "
            "only review authority. Earlier section work is stored across approved reference chunks, "
            "benchmarks, conclusions, adjudications, and validation artifacts. This reconciliation "
            "collects those distributed sources before any completion decision is made."
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

    print("Full-song review-evidence reconciliation V1 complete")
    print("Files examined:", report["filesExamined"])
    print("Measures with review evidence:", report["measuresWithReviewEvidence"])
    print("Measures with resolution evidence:", report["measuresWithResolutionEvidence"])
    print("Missing review evidence measures:", report["missingReviewEvidenceMeasures"])
    print("Missing resolution evidence measures:", report["missingResolutionEvidenceMeasures"])
    print("All measures have review evidence:", report["allMeasuresHaveReviewEvidence"])
    print("All measures have resolution evidence:", report["allMeasuresHaveResolutionEvidence"])
    print("Ready to repair completion audit:", report["readyToRepairCompletionAudit"])
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
