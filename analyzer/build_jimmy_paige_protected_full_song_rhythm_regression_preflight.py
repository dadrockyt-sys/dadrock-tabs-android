import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

APPROVAL_PATH = PUBLIC / "gomyway-jimmy-paige-protected-renderer-integration-approval.json"
PROFESSIONAL_PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
OUTPUT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-full-song-rhythm-regression-preflight.json"

EXPECTED_MEASURES = 113


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "path": str(path.relative_to(ROOT)),
            "readableJson": False,
            "topLevelKeys": [],
        }

    return {
        "path": str(path.relative_to(ROOT)),
        "readableJson": True,
        "topLevelKeys": sorted(payload.keys()) if isinstance(payload, dict) else [],
        "sha256": sha256_file(path),
    }


def main() -> None:
    approval = load_json(APPROVAL_PATH)
    if not PROFESSIONAL_PDF_PATH.exists():
        raise FileNotFoundError(
            f"Missing required artifact: {PROFESSIONAL_PDF_PATH.relative_to(ROOT)}"
        )

    approval_passed = (
        approval.get("humanApproved") is True
        and approval.get("visualContractsApproved") == 9
        and approval.get("automatedChecksPassed") is True
        and approval.get("sourceEventsMutated") is False
        and approval.get("rendererChanged") is False
        and approval.get("productionRendererCalled") is False
        and approval.get("productionOutputCreated") is False
        and approval.get("productionPromotionAllowed") is False
        and approval.get("professionalPdfRemainsScoringAuthority") is True
        and approval.get("readyForProtectedFullSongRhythmRegression") is True
    )

    candidate_patterns = (
        "gomyway-full-song-v8*.json",
        "gomyway-jimmy-paige-full-song*.json",
        "gomyway-professional-rhythm*.json",
        "gomyway-v8-*.json",
    )

    discovered = {}
    seen = set()
    for pattern in candidate_patterns:
        for path in sorted(PUBLIC.glob(pattern)):
            if path.name in seen:
                continue
            seen.add(path.name)
            discovered[path.name] = inspect_json(path)

    required_candidate_groups = {
        "sectionMap": [
            name for name in discovered
            if "section" in name.lower()
        ],
        "timingOrRhythm": [
            name for name in discovered
            if any(token in name.lower() for token in ("rhythm", "timing", "alignment"))
        ],
        "fullSongEventsOrWinner": [
            name for name in discovered
            if any(token in name.lower() for token in ("full-song", "winner", "events"))
        ],
    }

    source_inventory_ready = all(required_candidate_groups.values())
    preflight_passed = approval_passed and source_inventory_ready

    output = {
        "preflightName": "Jimmy Page protected 113-measure rhythm regression preflight",
        "preflightVersion": 1,
        "expectedMeasureCount": EXPECTED_MEASURES,
        "rendererIntegrationHumanApprovalPassed": approval_passed,
        "professionalPdfPresent": True,
        "professionalPdfSha256": sha256_file(PROFESSIONAL_PDF_PATH),
        "approvalArtifactSha256": sha256_file(APPROVAL_PATH),
        "discoveredCandidateArtifacts": discovered,
        "requiredCandidateGroups": required_candidate_groups,
        "sourceInventoryReady": source_inventory_ready,
        "protectedFullSongRhythmRegressionPreflightPassed": preflight_passed,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForProtected113MeasureRegression": preflight_passed,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Protected full-song rhythm regression preflight complete")
    print(f"Expected measures: {EXPECTED_MEASURES}")
    print(f"Renderer integration human approval passed: {approval_passed}")
    print(f"Candidate artifacts discovered: {len(discovered)}")
    print(f"Section map candidates: {len(required_candidate_groups['sectionMap'])}")
    print(f"Timing or rhythm candidates: {len(required_candidate_groups['timingOrRhythm'])}")
    print(f"Full-song events or winner candidates: {len(required_candidate_groups['fullSongEventsOrWinner'])}")
    print(f"Source inventory ready: {source_inventory_ready}")
    print(f"Protected preflight passed: {preflight_passed}")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Ready for protected 113-measure regression: {preflight_passed}")
    print("Ready for production: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not approval_passed:
        raise RuntimeError("Protected renderer integration human approval gate did not pass")


if __name__ == "__main__":
    main()
