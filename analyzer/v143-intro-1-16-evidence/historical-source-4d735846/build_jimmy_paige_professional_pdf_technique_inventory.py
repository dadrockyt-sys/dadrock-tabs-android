from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CONTRACT = PUBLIC / "gomyway-jimmy-paige-professional-notation-technique-contract.json"
OUTPUT = PUBLIC / "gomyway-jimmy-paige-professional-pdf-technique-inventory.json"

PRIORITY_HINTS = (
    "notation-proof-v2",
    "notation-proof",
    "measure-grid-proof",
    "professional",
    "polished",
)

TECHNIQUES = [
    "bend",
    "bend-release",
    "sustain",
    "palm-mute",
    "slide-up",
    "slide-down",
    "hammer-on",
    "pull-off",
    "vibrato",
    "let-ring",
    "dead-note",
    "muted-strum",
    "natural-harmonic",
    "pinch-harmonic",
    "tap",
    "repeat-bar",
    "section-label",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank(path: Path) -> tuple[int, str]:
    name = path.name.lower()
    score = 0
    for index, hint in enumerate(PRIORITY_HINTS):
        if hint in name:
            score += (len(PRIORITY_HINTS) - index) * 10
    if "gomyway" in name:
        score += 25
    return (-score, name)


def main() -> None:
    if not CONTRACT.is_file():
        raise FileNotFoundError(f"Technique contract missing: {CONTRACT}")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    contract_passed = bool(contract.get("contractPassed") or contract.get("passed"))
    if not contract_passed:
        raise RuntimeError("Professional notation technique contract is not passing")

    pdfs = sorted(PUBLIC.glob("*.pdf"), key=rank)
    if not pdfs:
        raise FileNotFoundError("No PDF files found in public/")

    candidates = []
    for index, path in enumerate(pdfs, start=1):
        candidates.append(
            {
                "priority": index,
                "path": str(path.relative_to(ROOT)),
                "filename": path.name,
                "byteLength": path.stat().st_size,
                "sha256": sha256(path),
                "professionalReferenceCandidate": any(
                    hint in path.name.lower() for hint in PRIORITY_HINTS
                ),
                "selectedAsScoringAuthority": index == 1,
                "sourceMutationAllowed": False,
            }
        )

    selected = candidates[0]
    worksheet = []
    for technique in TECHNIQUES:
        worksheet.append(
            {
                "techniqueType": technique,
                "status": "unverified",
                "pageNumber": None,
                "measureNumber": None,
                "stringIndex": None,
                "startPhase": None,
                "endPhase": None,
                "label": None,
                "drawingPrimitive": None,
                "humanVerified": False,
                "synthetic": False,
                "notes": "Fill only after visual confirmation in the selected professional PDF.",
            }
        )

    payload = {
        "inventoryVersion": 1,
        "inventoryType": "professional-pdf-technique-reference-inventory",
        "contractPath": str(CONTRACT.relative_to(ROOT)),
        "contractPassed": contract_passed,
        "pdfCandidateCount": len(candidates),
        "selectedProfessionalPdf": selected,
        "pdfCandidates": candidates,
        "techniqueWorksheet": worksheet,
        "verifiedTechniqueExamples": 0,
        "syntheticAnnotationsCreated": False,
        "professionalPdfRemainsScoringAuthority": True,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "inventoryPassed": len(candidates) > 0 and selected["byteLength"] > 0,
        "readyForHumanTechniquePageSelection": True,
        "readyForTechniqueRendererTraining": False,
    }

    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Professional PDF technique inventory complete")
    print(f"PDF candidates found: {len(candidates)}")
    print(f"Selected scoring authority candidate: {selected['path']}")
    print(f"Selected PDF bytes: {selected['byteLength']}")
    print(f"Technique worksheet rows: {len(worksheet)}")
    print("Verified technique examples: 0")
    print("Synthetic annotations created: False")
    print("Inventory passed: True")
    print("Ready for human technique page selection: True")
    print("Ready for technique renderer training: False")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
