import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
GATE_PATH = PUBLIC / "gomyway-jimmy-paige-protected-renderer-integration-gate.json"
PREVIEW_REPORT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-renderer-integration-preview.json"
PREVIEW_SVG_PATH = PUBLIC / "gomyway-jimmy-paige-protected-renderer-integration-preview.svg"
OUTPUT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-renderer-integration-approval.json"

EXPECTED_FAMILIES = [
    "full-bend-release",
    "vibrato",
    "muted-note",
    "pick-direction",
    "chord-sustain-tie",
    "chord-slide",
    "time-signature-change",
    "section-label",
    "final-barline",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    gate = load_json(GATE_PATH)
    preview = load_json(PREVIEW_REPORT_PATH)

    if not PREVIEW_SVG_PATH.exists() or PREVIEW_SVG_PATH.stat().st_size == 0:
        raise RuntimeError("Protected integration preview SVG is missing or empty")

    checks = {
        "protectedIntegrationGatePassed": gate.get(
            "protectedRendererIntegrationGatePassed"
        ) is True,
        "readyForHumanIntegrationInspection": preview.get(
            "readyForHumanIntegrationInspection"
        ) is True,
        "examplesComparedNine": preview.get("examplesCompared") == 9,
        "familyCoverageNineOfNine": preview.get(
            "representativeTechniqueFamilies"
        ) == 9,
        "allVisualContractsMatched": preview.get(
            "allVisualContractsMatched"
        ) is True,
        "sourceEventsUnchanged": preview.get("sourceEventsMutated") is False,
        "rendererStillUnchanged": preview.get("rendererChanged") is False,
        "productionRendererNotCalled": preview.get(
            "productionRendererCalled"
        ) is False,
        "productionOutputNotCreated": preview.get(
            "productionOutputCreated"
        ) is False,
        "productionPromotionStillBlocked": preview.get(
            "productionPromotionAllowed"
        ) is False,
        "professionalPdfStillAuthority": preview.get(
            "professionalPdfRemainsScoringAuthority"
        ) is True,
    }

    automated_checks_passed = all(checks.values())
    if not automated_checks_passed:
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"Cannot record human approval; failed checks: {failed}")

    approval = {
        "approvalName": "Jimmy Page protected renderer integration human approval",
        "approvalVersion": 1,
        "approvedAtUtc": datetime.now(timezone.utc).isoformat(),
        "approvalMethod": "human visual side-by-side inspection",
        "humanApproved": True,
        "visualResult": "approved",
        "approvedTechniqueFamilies": EXPECTED_FAMILIES,
        "automatedChecks": checks,
        "automatedChecksPassed": True,
        "artifactHashes": {
            str(GATE_PATH.relative_to(ROOT)): sha256_file(GATE_PATH),
            str(PREVIEW_REPORT_PATH.relative_to(ROOT)): sha256_file(
                PREVIEW_REPORT_PATH
            ),
            str(PREVIEW_SVG_PATH.relative_to(ROOT)): sha256_file(PREVIEW_SVG_PATH),
        },
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForProtectedFullSongRhythmRegression": True,
        "readyForProductionRendererIntegration": False,
    }

    OUTPUT_PATH.write_text(json.dumps(approval, indent=2) + "\n", encoding="utf-8")

    print("Protected renderer integration human approval recorded")
    print("Human approved: True")
    print("Visual contracts approved: 9/9")
    print("Automated checks passed: True")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print("Ready for protected full-song rhythm regression: True")
    print("Ready for production renderer integration: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
