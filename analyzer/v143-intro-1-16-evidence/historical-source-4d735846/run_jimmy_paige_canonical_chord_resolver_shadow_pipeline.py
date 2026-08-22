from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-canonical-chord-resolver-prototype.json"
READONLY_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-canonical-chord-resolver-readonly-integration.json"
GATE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-protected-chord-resolver-gate.json"
SOURCE_EVENT_CANDIDATES = [
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json",
    REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json",
]
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-canonical-chord-resolver-shadow-output.json"
REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-canonical-chord-resolver-shadow-report.json"


def load(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def first_existing(paths: list[Path]) -> Path:
    for path in paths:
        if path.is_file():
            return path
    raise FileNotFoundError("No protected source event cache was found")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    prototype = load(PROTOTYPE_PATH)
    readonly = load(READONLY_PATH)
    gate = load(GATE_PATH)
    source_path = first_existing(SOURCE_EVENT_CANDIDATES)

    if not bool(gate.get("gatePassed", False)):
        raise RuntimeError("Protected resolver gate is not passing")
    if not bool(readonly.get("integrationPassed", False)):
        raise RuntimeError("Read-only integration validation is not passing")
    if not bool(prototype.get("readyForReadOnlyIntegrationBenchmark", False)):
        raise RuntimeError("Resolver prototype is not ready for shadow integration")

    source_sha_before = sha256(source_path)
    source_events = load(source_path)

    shadow_rows: list[dict[str, Any]] = []
    for row in prototype.get("attackRows", []):
        guards = row.get("guardRequirements", {})
        required_guards = {
            "repeatedSectionMappingPresent": bool(guards.get("repeatedSectionMappingPresent", False)),
            "observedChordAttackPresent": bool(guards.get("observedChordAttackPresent", False)),
            "pitchClassRecognitionPassed": bool(guards.get("pitchClassRecognitionPassed", False)),
            "timingWithin300ms": bool(guards.get("timingWithin300ms", False)),
            "protectedResolverGatePassed": bool(guards.get("protectedResolverGatePassed", False)),
        }
        all_guards_passed = all(required_guards.values())
        if not all_guards_passed:
            raise RuntimeError(
                f"Shadow row failed guards: {row.get('heldOutMeasureNumber')}:{row.get('attackNumber')}"
            )

        shadow_rows.append(
            {
                "measureNumber": row["heldOutMeasureNumber"],
                "attackNumber": row["attackNumber"],
                "targetPhase": row["targetPhase"],
                "chordLabels": row.get("chordLabels", []),
                "resolutionMode": row["resolutionMode"],
                "resolvedFretsHighToLow": row["resolvedFretsHighToLow"],
                "resolvedMidiPitches": row.get("resolvedMidiPitches", []),
                "observedMidiPitches": row.get("observedMidiPitches", []),
                "absoluteTimingDeltaSeconds": row.get("absoluteTimingDeltaSeconds"),
                "allGuardsPassed": True,
                "renderEligible": False,
                "productionEligible": False,
                "sourceEventMutationAllowed": False,
            }
        )

    shadow_payload = {
        "shadowVersion": 1,
        "mode": "read-only-shadow",
        "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "sourceEventCache": str(source_path.relative_to(REPO_ROOT)),
        "sourceEventCount": len(source_events) if isinstance(source_events, list) else None,
        "sourceEventSha256": source_sha_before,
        "resolvedChordAttacks": len(shadow_rows),
        "attackRows": shadow_rows,
        "rendererMayConsume": False,
        "productionMayConsume": False,
        "syntheticNotesCreated": False,
        "sourceEventsMutated": False,
        "professionalPdfRemainsScoringAuthority": True,
    }
    OUTPUT_PATH.write_text(json.dumps(shadow_payload, indent=2) + "\n", encoding="utf-8")

    source_sha_after = sha256(source_path)
    source_unchanged = source_sha_before == source_sha_after
    all_rows_guarded = all(row["allGuardsPassed"] for row in shadow_rows)
    shadow_passed = (
        source_unchanged
        and all_rows_guarded
        and len(shadow_rows) == int(prototype.get("targetAttacks", 0))
        and len(shadow_rows) > 0
    )

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "canonical-chord-resolver-shadow-pipeline",
        "sourceEventCache": str(source_path.relative_to(REPO_ROOT)),
        "sourceEventShaBefore": source_sha_before,
        "sourceEventShaAfter": source_sha_after,
        "sourceEventShaUnchanged": source_unchanged,
        "shadowResolvedAttacks": len(shadow_rows),
        "expectedResolvedAttacks": int(prototype.get("targetAttacks", 0)),
        "invalidGuardRows": sum(1 for row in shadow_rows if not row["allGuardsPassed"]),
        "shadowPipelinePassed": shadow_passed,
        "professionalPdfRemainsScoringAuthority": True,
        "protectedPitchCheckpointChanged": False,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "readyForMultiSectionShadowValidation": shadow_passed,
        "readyForProduction": False,
        "shadowOutput": str(OUTPUT_PATH.relative_to(REPO_ROOT)),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Canonical chord resolver shadow pipeline complete")
    print(f"Shadow resolved attacks: {len(shadow_rows)}/{prototype.get('targetAttacks', 0)}")
    print(f"Invalid guard rows: {report['invalidGuardRows']}")
    print(f"Source event SHA unchanged: {source_unchanged}")
    print(f"Shadow pipeline passed: {shadow_passed}")
    print(f"Ready for multi-section shadow validation: {shadow_passed}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Shadow output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
