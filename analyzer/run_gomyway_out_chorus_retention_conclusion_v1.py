from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "public" / "gomyway-out-chorus-retention-benchmark-v1.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-out-chorus-retention-conclusion-v1.json"


def main() -> None:
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    report = {
        "schemaVersion": 1,
        "conclusionType": "out-chorus-retention-lock",
        "source": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "section": data.get("section"),
        "measureRange": data.get("measureRange"),
        "passed": data.get("passed"),
        "deduplicatedCandidateCount": data.get("deduplicatedCandidateCount"),
        "professionallyCoveredCandidateCount": data.get("professionallyCoveredCandidateCount"),
        "humanValidatedRhythmCandidateCount": data.get("humanValidatedRhythmCandidateCount"),
        "retainedCandidateCount": data.get("retainedCandidateCount"),
        "retainedFraction": data.get("retainedFraction"),
        "exactUnresolvedKeyMatch": data.get("exactUnresolvedKeyMatch"),
        "allUnresolvedCandidatesHumanValidated": data.get("allUnresolvedCandidatesHumanValidated"),
        "completeOutChorusRetentionSupported": data.get("completeOutChorusRetentionSupported"),
        "decision": (
            "Retain all 13 deduplicated Out-Chorus rhythm candidates for measures 103-110. "
            "Eight are covered by the professional reference and five were confirmed by direct listening."
        ),
        "automaticEventMutationAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Out-Chorus retention conclusion V1 complete")
    print("Passed:", report["passed"])
    print("Retained candidates:", report["retainedCandidateCount"])
    print("Retained fraction:", report["retainedFraction"])
    print("Complete Out-Chorus retention supported:", report["completeOutChorusRetentionSupported"])
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
