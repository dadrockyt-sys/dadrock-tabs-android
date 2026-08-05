from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-out-chorus-reference-coverage-audit-v1.json"
)
ADJUDICATION_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-out-chorus-listening-adjudication-v1.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-out-chorus-retention-benchmark-v1.json"
)

EXPECTED_KEYS = {
    (103, 2),
    (103, 3),
    (104, 9),
    (105, 15),
    (109, 15),
}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing required input: {path.relative_to(REPO_ROOT)}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    audit = load(AUDIT_PATH)
    adjudication = load(ADJUDICATION_PATH)

    unresolved_events = audit.get("unresolvedEvents") or []
    unresolved_keys = {
        (int(item["measureNumber"]), int(item["candidateStep"]))
        for item in unresolved_events
    }

    adjudicated_items = adjudication.get("items") or []
    adjudicated_keys = {
        (int(item["measureNumber"]), int(item["candidateStep"]))
        for item in adjudicated_items
    }

    validated_keys = {
        (int(item["measureNumber"]), int(item["candidateStep"]))
        for item in adjudicated_items
        if item.get("humanValidated") is True
        and item.get("judgment") == "real-rhythm-articulation"
    }

    covered_count = int(audit.get("coveredCandidateCount") or 0)
    unresolved_count = int(audit.get("unresolvedCandidateCount") or 0)
    deduplicated_count = int(audit.get("deduplicatedCandidateCount") or 0)
    retained_count = covered_count + len(validated_keys)
    retained_fraction = (
        retained_count / deduplicated_count
        if deduplicated_count
        else 0.0
    )

    exact_key_match = (
        unresolved_keys == EXPECTED_KEYS
        and adjudicated_keys == EXPECTED_KEYS
    )
    all_unresolved_validated = validated_keys == EXPECTED_KEYS
    complete_retention = retained_count == deduplicated_count

    passed = (
        exact_key_match
        and all_unresolved_validated
        and unresolved_count == len(EXPECTED_KEYS)
        and complete_retention
    )

    report = {
        "schemaVersion": 1,
        "benchmarkType": "out-chorus-human-validated-retention",
        "section": "Out-Chorus",
        "measureRange": [103, 110],
        "auditSource": str(AUDIT_PATH.relative_to(REPO_ROOT)),
        "adjudicationSource": str(
            ADJUDICATION_PATH.relative_to(REPO_ROOT)
        ),
        "deduplicatedCandidateCount": deduplicated_count,
        "professionallyCoveredCandidateCount": covered_count,
        "previouslyUnresolvedCandidateCount": unresolved_count,
        "humanValidatedRhythmCandidateCount": len(validated_keys),
        "retainedCandidateCount": retained_count,
        "retainedCandidateFraction": round(retained_fraction, 6),
        "expectedUnresolvedKeys": [list(key) for key in sorted(EXPECTED_KEYS)],
        "auditUnresolvedKeys": [list(key) for key in sorted(unresolved_keys)],
        "adjudicatedKeys": [list(key) for key in sorted(adjudicated_keys)],
        "validatedKeys": [list(key) for key in sorted(validated_keys)],
        "exactKeyMatch": exact_key_match,
        "allUnresolvedCandidatesHumanValidated": all_unresolved_validated,
        "completeOutChorusRetentionSupported": complete_retention,
        "passed": passed,
        "interpretation": (
            "Eight deduplicated candidates are already covered by the professional "
            "reference. Manual synchronized listening validates the remaining five as "
            "real rhythm-guitar articulations. Retaining all thirteen candidates is "
            "therefore supported for this Out-Chorus review set."
        ),
        "automaticEventMutationAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Out-Chorus retention benchmark V1 complete")
    print("Passed:", passed)
    print("Deduplicated candidates:", deduplicated_count)
    print("Professionally covered candidates:", covered_count)
    print("Human-validated rhythm candidates:", len(validated_keys))
    print("Retained candidates:", retained_count)
    print("Retained fraction:", round(retained_fraction, 6))
    print("Exact unresolved-key match:", exact_key_match)
    print("All unresolved candidates human validated:", all_unresolved_validated)
    print("Complete Out-Chorus retention supported:", complete_retention)
    print("Automatic event mutation allowed: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
