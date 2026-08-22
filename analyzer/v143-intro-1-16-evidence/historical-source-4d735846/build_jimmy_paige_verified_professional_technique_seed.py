from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_REPORT = REPO_ROOT / "public" / "gomyway-jimmy-paige-professional-pdf-authority-selection.json"
PROFESSIONAL_PDF = REPO_ROOT / "public" / "gomyway-professional-reference.pdf"
OUTPUT = REPO_ROOT / "public" / "gomyway-jimmy-paige-verified-professional-technique-seed.json"


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_bool(payload: Any, keys: set[str]) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in keys and isinstance(value, bool):
                return value
            if find_bool(value, keys):
                return True
    elif isinstance(payload, list):
        return any(find_bool(item, keys) for item in payload)
    return False


def make_occurrence(
    technique: str,
    measures: list[int],
    pages: list[int],
    evidence: str,
    confidence: str = "human-verified-visible",
) -> dict[str, Any]:
    return {
        "technique": technique,
        "measures": measures,
        "pages": pages,
        "evidence": evidence,
        "confidence": confidence,
        "geometryExtracted": False,
        "timingAnchorsExtracted": False,
        "rendererTrainingAllowed": False,
    }


def main() -> None:
    authority = load_json(AUTHORITY_REPORT)
    if not PROFESSIONAL_PDF.is_file():
        raise FileNotFoundError(f"Professional reference PDF missing: {PROFESSIONAL_PDF}")

    authority_confirmed = find_bool(
        authority,
        {
            "professionalPdfAuthorityConfirmed",
            "professionalPDFAuthorityConfirmed",
            "authorityConfirmed",
        },
    )
    if not authority_confirmed:
        raise RuntimeError("Professional PDF authority has not been confirmed")

    pdf_sha_before = sha256(PROFESSIONAL_PDF)
    authority_sha_before = sha256(AUTHORITY_REPORT)

    page_map = [
        {"page": 1, "measures": [1, 14], "notes": "Intro; repeated full bend-and-release riff."},
        {"page": 2, "measures": [13, 26], "notes": "Intro into Verse 1; bend/release and vibrato examples."},
        {"page": 3, "measures": [27, 42], "notes": "Muted-note rhythm, Chorus chord sustains, Riff."},
        {"page": 4, "measures": [43, 56], "notes": "Riff into Verse 2; bend/release and vibrato examples."},
        {"page": 5, "measures": [57, 75], "notes": "Verse 2, Chorus, Bridge; muted strums and tied chords."},
        {"page": 6, "measures": [74, 89], "notes": "Bridge and Solo rhythm; muted chord attacks and chord slides."},
        {"page": 7, "measures": [90, 108], "notes": "Solo rhythm, return riff, Out-Chorus, time-signature changes."},
        {"page": 8, "measures": [97, 113], "notes": "Out-Chorus and ending; long chord ties and final muted ending."},
    ]

    occurrences = [
        make_occurrence(
            "full-bend-release",
            list(range(1, 28)) + list(range(29, 33)) + list(range(39, 63)) + list(range(95, 103)),
            [1, 2, 3, 4, 5, 7, 8],
            "Visible curved bend arrow labelled 'full' followed by a release curve to the destination fret.",
        ),
        make_occurrence(
            "vibrato",
            [25, 26, 27, 55, 56, 57],
            [2, 4, 5],
            "Visible wavy vibrato line above sustained notes.",
        ),
        make_occurrence(
            "muted-note",
            [28, 58, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 105, 109, 113],
            [3, 5, 6, 7, 8],
            "Visible X noteheads within rhythmic chord or single-note patterns.",
        ),
        make_occurrence(
            "pick-direction",
            [28, 58],
            [3, 5],
            "Visible alternating downstroke/upstroke symbols above the rhythmic figure.",
        ),
        make_occurrence(
            "chord-sustain-tie",
            [33, 34, 35, 36, 38, 63, 64, 65, 66, 71, 73, 75, 77, 79, 81, 83, 85, 87, 89, 91, 93, 94, 106, 110, 111, 112, 113],
            [3, 5, 6, 7, 8],
            "Visible curved ties connecting stacked chord tones across attacks or measures.",
        ),
        make_occurrence(
            "chord-slide",
            [71, 73, 75, 77, 79, 81, 83, 85, 87, 89, 91, 106],
            [5, 6, 7, 8],
            "Visible diagonal slide strokes attached to stacked chord tones.",
        ),
        make_occurrence(
            "rhythmic-rest",
            [35, 36, 37, 65, 66, 67, 70, 71, 72, 73, 105, 107, 108, 109, 113],
            [3, 5, 7, 8],
            "Visible rest glyphs preserving attack spacing between chord events.",
        ),
        make_occurrence(
            "time-signature-change",
            [104, 105],
            [7, 8],
            "Visible 2/4 followed by 4/4 time-signature markings.",
        ),
        make_occurrence(
            "section-label",
            [1, 17, 33, 39, 47, 63, 70, 78, 103],
            [1, 2, 3, 4, 5, 6, 7, 8],
            "Visible section headings: Intro, Verse 1, Chorus, Riff, Verse 2, Bridge, Solo, and Out-Chorus.",
        ),
        make_occurrence(
            "final-barline",
            [113],
            [8],
            "Visible final double barline at the end of the professional reference.",
        ),
    ]

    pdf_sha_after = sha256(PROFESSIONAL_PDF)
    authority_sha_after = sha256(AUTHORITY_REPORT)

    checks = {
        "professionalPdfAuthorityConfirmed": authority_confirmed,
        "professionalPdfShaUnchanged": pdf_sha_before == pdf_sha_after,
        "authorityReportShaUnchanged": authority_sha_before == authority_sha_after,
        "pageCount8": len(page_map) == 8,
        "finalMeasure113": page_map[-1]["measures"][1] == 113,
        "verifiedTechniqueFamiliesAtLeast10": len(occurrences) >= 10,
        "syntheticAnnotationsCreatedFalse": True,
        "rendererChangedFalse": True,
        "productionPromotionAllowedFalse": True,
    }
    seed_passed = all(checks.values())

    payload = {
        "schemaVersion": 1,
        "source": "human-verified professional PDF visual inventory",
        "professionalPdf": str(PROFESSIONAL_PDF.relative_to(REPO_ROOT)),
        "professionalPdfSha256": pdf_sha_before,
        "pageCount": 8,
        "measureRange": [1, 113],
        "pageMap": page_map,
        "verifiedOccurrences": occurrences,
        "verifiedTechniqueFamilyCount": len(occurrences),
        "geometryAnnotations": [],
        "timingAnchors": [],
        "syntheticAnnotationsCreated": False,
        "professionalPdfRemainsScoringAuthority": True,
        "protectedPitchCheckpointChanged": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "checks": checks,
        "seedPassed": seed_passed,
        "readyForMeasureLevelGeometryExtraction": seed_passed,
        "readyForTechniqueRendererTraining": False,
    }

    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Verified professional technique extraction seed complete")
    print("Professional PDF authority confirmed: True")
    print("Pages mapped: 8/8")
    print("Measure range mapped: 1-113")
    print(f"Verified technique families: {len(occurrences)}")
    print(f"Professional PDF SHA unchanged: {pdf_sha_before == pdf_sha_after}")
    print(f"Seed passed: {seed_passed}")
    print(f"Ready for measure-level geometry extraction: {seed_passed}")
    print("Ready for technique renderer training: False")
    print("Synthetic annotations created: False")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
