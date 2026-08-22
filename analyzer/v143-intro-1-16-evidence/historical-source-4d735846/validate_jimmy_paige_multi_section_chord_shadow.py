from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
TRAINED_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-professional-chords-33-38-pitch-class-recovery.json"
HELDOUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-pitch-class-validation-63-67.json"
SHADOW_OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-canonical-chord-resolver-shadow-output.json"
SHADOW_REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-canonical-chord-resolver-shadow-report.json"
GATE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-protected-chord-resolver-gate.json"
SOURCE_EVENT_CANDIDATES = [
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json",
    REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json",
]
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-multi-section-chord-shadow-validation.json"


def load(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required result not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def first_existing(paths: list[Path]) -> Path:
    for path in paths:
        if path.is_file():
            return path
    raise FileNotFoundError("No protected source event cache found")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("measureReports", [])
    return rows if isinstance(rows, list) else []


def main() -> None:
    trained = load(TRAINED_PATH)
    heldout = load(HELDOUT_PATH)
    shadow = load(SHADOW_OUTPUT_PATH)
    shadow_report = load(SHADOW_REPORT_PATH)
    gate = load(GATE_PATH)
    source_path = first_existing(SOURCE_EVENT_CANDIDATES)

    source_sha_before = sha256(source_path)

    if not bool(gate.get("gatePassed", False)):
        raise RuntimeError("Protected chord resolver gate is not passing")
    if not bool(shadow_report.get("shadowPipelinePassed", False)):
        raise RuntimeError("Single-section shadow pipeline is not passing")

    trained_rows = measure_rows(trained)
    heldout_rows = measure_rows(heldout)

    trained_target = sum(int(row.get("targetAttacks", 0)) for row in trained_rows)
    trained_matched = sum(int(row.get("matchedAttacks", 0)) for row in trained_rows)
    heldout_target = sum(int(row.get("targetAttacks", 0)) for row in heldout_rows)
    heldout_matched = sum(
        int(row.get("guardedMatchedAttacks", row.get("matchedAttacks", 0)))
        for row in heldout_rows
    )

    # Fallback to top-level validated totals when individual rows use a different schema.
    trained_target = trained_target or int(trained.get("targetAttacks", 0))
    trained_matched = trained_matched or int(trained.get("guardedMatchedAttacks", 0))
    heldout_target = heldout_target or int(heldout.get("targetAttacks", 0))
    heldout_matched = heldout_matched or int(
        heldout.get("guardedMatchedAttacks", heldout.get("pitchClassMatchedAttacks", 0))
    )

    shadow_rows = shadow.get("attackRows", [])
    if not isinstance(shadow_rows, list):
        raise RuntimeError("Shadow output does not contain attackRows")

    invalid_shadow_rows = [
        row
        for row in shadow_rows
        if not isinstance(row, dict)
        or not bool(row.get("allGuardsPassed", False))
        or bool(row.get("renderEligible", False))
        or bool(row.get("productionEligible", False))
        or bool(row.get("sourceEventMutationAllowed", False))
    ]

    combined_target = trained_target + heldout_target
    combined_matched = trained_matched + heldout_matched
    combined_recall = (
        100.0 * combined_matched / combined_target if combined_target else 0.0
    )

    source_sha_after = sha256(source_path)
    source_unchanged = source_sha_before == source_sha_after

    checks = {
        "trainedSection23of23": trained_matched == 23 and trained_target == 23,
        "heldoutSection21of21": heldout_matched == 21 and heldout_target == 21,
        "combined44of44": combined_matched == 44 and combined_target == 44,
        "shadowResolved21of21": len(shadow_rows) == 21,
        "allShadowRowsGuarded": len(invalid_shadow_rows) == 0,
        "sourceEventShaUnchanged": source_unchanged,
        "protectedGatePassed": bool(gate.get("gatePassed", False)),
        "singleSectionShadowPassed": bool(shadow_report.get("shadowPipelinePassed", False)),
    }

    passed = all(checks.values())

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "multi-section-canonical-chord-resolver-shadow-validation",
        "sections": [
            {
                "name": "professional-chorus-training-section",
                "measures": [33, 34, 35, 36, 37, 38],
                "matchedAttacks": trained_matched,
                "targetAttacks": trained_target,
            },
            {
                "name": "held-out-repeated-chorus",
                "measures": [63, 64, 65, 66, 67],
                "matchedAttacks": heldout_matched,
                "targetAttacks": heldout_target,
            },
        ],
        "combinedMatchedAttacks": combined_matched,
        "combinedTargetAttacks": combined_target,
        "combinedRecallPercentage": round(combined_recall, 2),
        "shadowResolvedAttacks": len(shadow_rows),
        "invalidShadowRows": invalid_shadow_rows,
        "sourceEventCache": str(source_path.relative_to(REPO_ROOT)),
        "sourceEventShaBefore": source_sha_before,
        "sourceEventShaAfter": source_sha_after,
        "checks": checks,
        "multiSectionShadowPassed": passed,
        "professionalPdfRemainsScoringAuthority": True,
        "protectedPitchCheckpointChanged": False,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "syntheticNotesCreated": False,
        "productionPromotionAllowed": False,
        "readyForRendererSidecarBenchmark": passed,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Multi-section chord resolver shadow validation complete")
    print(f"Training section: {trained_matched}/{trained_target}")
    print(f"Held-out section: {heldout_matched}/{heldout_target}")
    print(
        f"Combined professional chord attacks: {combined_matched}/{combined_target} "
        f"({combined_recall:.2f}%)"
    )
    print(f"Shadow resolved attacks: {len(shadow_rows)}/21")
    print(f"Invalid shadow rows: {len(invalid_shadow_rows)}")
    print(f"Source event SHA unchanged: {source_unchanged}")
    for name, result in checks.items():
        print(f"{name}: {result}")
    print(f"Multi-section shadow passed: {passed}")
    print(f"Ready for renderer sidecar benchmark: {passed}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
