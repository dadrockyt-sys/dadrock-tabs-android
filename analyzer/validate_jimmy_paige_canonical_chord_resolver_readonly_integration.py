from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-canonical-chord-resolver-prototype.json"
GATE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-protected-chord-resolver-gate.json"
EVENT_CACHE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-canonical-chord-resolver-readonly-integration.json"


def load(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    before_event_hash = digest(EVENT_CACHE_PATH)
    events = load(EVENT_CACHE_PATH)
    prototype = load(PROTOTYPE_PATH)
    gate = load(GATE_PATH)

    if not bool(gate.get("gatePassed", False)):
        raise RuntimeError("Protected resolver gate is not passing")
    if not bool(prototype.get("readyForReadOnlyIntegrationBenchmark", False)):
        raise RuntimeError("Resolver prototype is not ready for read-only integration")

    rows = prototype.get("attackRows", [])
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("Resolver prototype contains no attack rows")

    integration_rows: list[dict[str, Any]] = []
    exact_count = 0
    transferred_count = 0
    invalid_rows: list[dict[str, Any]] = []

    for row in rows:
        mode = str(row.get("resolutionMode", ""))
        guards = row.get("guardRequirements", {})
        valid = bool(
            guards.get("repeatedSectionMappingPresent", False)
            and guards.get("observedChordAttackPresent", False)
            and guards.get("pitchClassRecognitionPassed", False)
            and guards.get("timingWithin300ms", False)
            and guards.get("protectedResolverGatePassed", False)
            and row.get("sourceEventMutationAllowed") is False
            and row.get("syntheticAttackCreationAllowed") is False
        )

        if mode == "observed-exact":
            exact_count += 1
        elif mode == "guarded-template-transfer":
            transferred_count += 1
        else:
            valid = False

        integration_row = {
            "heldOutMeasureNumber": row.get("heldOutMeasureNumber"),
            "attackNumber": row.get("attackNumber"),
            "resolutionMode": mode,
            "resolvedFretsHighToLow": row.get("resolvedFretsHighToLow", []),
            "resolvedMidiPitches": row.get("resolvedMidiPitches", []),
            "observedMidiPitches": row.get("observedMidiPitches", []),
            "absoluteTimingDeltaSeconds": row.get("absoluteTimingDeltaSeconds"),
            "guardRequirements": guards,
            "validReadOnlyResolution": valid,
        }
        integration_rows.append(integration_row)
        if not valid:
            invalid_rows.append(integration_row)

    after_event_hash = digest(EVENT_CACHE_PATH)
    source_events_unchanged = before_event_hash == after_event_hash
    all_rows_valid = not invalid_rows
    resolved_count = len(integration_rows)
    target_count = int(prototype.get("targetAttacks", resolved_count))

    checks = {
        "protectedGatePassed": bool(gate.get("gatePassed", False)),
        "prototypeResolvedAllTargets": resolved_count == target_count,
        "allResolutionGuardsPassed": all_rows_valid,
        "sourceEventsUnchanged": source_events_unchanged,
        "syntheticAttacksCreated": False,
        "rendererChanged": False,
        "professionalPdfRemainsScoringAuthority": True,
    }
    integration_passed = all(
        value if name not in {"syntheticAttacksCreated", "rendererChanged"} else not value
        for name, value in checks.items()
    )

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "canonical-chord-resolver-readonly-integration",
        "status": "complete",
        "sourcePrototype": str(PROTOTYPE_PATH.relative_to(REPO_ROOT)),
        "sourceGate": str(GATE_PATH.relative_to(REPO_ROOT)),
        "sourceEvents": str(EVENT_CACHE_PATH.relative_to(REPO_ROOT)),
        "sourceEventSha256Before": before_event_hash,
        "sourceEventSha256After": after_event_hash,
        "sourceEventCount": len(events) if isinstance(events, list) else None,
        "exactObservedAttacks": exact_count,
        "guardedTemplateTransferredAttacks": transferred_count,
        "resolvedAttacks": resolved_count,
        "targetAttacks": target_count,
        "invalidResolutionRows": invalid_rows,
        "checks": checks,
        "integrationPassed": integration_passed,
        "attackRows": integration_rows,
        "productionPromotionAllowed": False,
        "protectedPitchCheckpointChanged": False,
        "readyForShadowPipelineIntegration": integration_passed,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Canonical chord resolver read-only integration validation complete")
    print(f"Exact observed attacks: {exact_count}")
    print(f"Guarded template-transferred attacks: {transferred_count}")
    print(f"Resolved attacks: {resolved_count}/{target_count}")
    print(f"Invalid resolution rows: {len(invalid_rows)}")
    print(f"Source event SHA unchanged: {source_events_unchanged}")
    print(f"Integration passed: {integration_passed}")
    print(f"Ready for shadow pipeline integration: {integration_passed}")
    print("Ready for production: False")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
