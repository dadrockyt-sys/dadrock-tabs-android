from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
INVENTORY_PATH = PUBLIC_DIR / "gomyway-jimmy-paige-professional-pdf-technique-inventory.json"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-jimmy-paige-professional-pdf-authority-selection.json"

MIN_PROFESSIONAL_BYTES = 100_000
REJECT_TOKENS = (
    "isolated",
    "benchmark",
    "preview",
    "proof",
    "shadow",
    "adapter",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_pdf(path: Path) -> dict:
    name = path.name.lower()
    rejected_tokens = [token for token in REJECT_TOKENS if token in name]
    size = path.stat().st_size
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "name": path.name,
        "bytes": size,
        "sha256": sha256(path),
        "rejectedTokens": rejected_tokens,
        "largeEnoughForProfessionalAuthority": size >= MIN_PROFESSIONAL_BYTES,
        "filenameLooksLikeBenchmarkArtifact": bool(rejected_tokens),
        "eligibleBySafetyRules": size >= MIN_PROFESSIONAL_BYTES and not rejected_tokens,
    }


def main() -> None:
    if not INVENTORY_PATH.is_file():
        raise FileNotFoundError(
            "Technique inventory missing. Run build_jimmy_paige_professional_pdf_technique_inventory.py first."
        )

    pdfs = sorted(PUBLIC_DIR.glob("*.pdf"))
    candidates = [inspect_pdf(path) for path in pdfs]

    explicit = os.environ.get("JIMMY_PROFESSIONAL_PDF", "").strip()
    selected = None
    selection_mode = "none"
    selection_error = None

    if explicit:
        explicit_path = Path(explicit)
        if not explicit_path.is_absolute():
            explicit_path = REPO_ROOT / explicit_path
        if not explicit_path.is_file():
            selection_error = f"Explicit professional PDF does not exist: {explicit_path}"
        else:
            selected = inspect_pdf(explicit_path)
            selection_mode = "explicit-environment-variable"
            if selected["filenameLooksLikeBenchmarkArtifact"]:
                selection_error = "Explicit PDF filename looks like a proof/preview/benchmark artifact"
            elif not selected["largeEnoughForProfessionalAuthority"]:
                selection_error = (
                    f"Explicit PDF is only {selected['bytes']} bytes; minimum safe authority size is "
                    f"{MIN_PROFESSIONAL_BYTES} bytes"
                )
    else:
        eligible = [candidate for candidate in candidates if candidate["eligibleBySafetyRules"]]
        if len(eligible) == 1:
            selected = eligible[0]
            selection_mode = "single-safe-candidate"
        elif len(eligible) > 1:
            selection_error = (
                "Multiple safe PDF candidates remain. Set JIMMY_PROFESSIONAL_PDF to the exact professional copy."
            )
        else:
            selection_error = (
                "No safe professional PDF candidate found. The previous automatic choice was a small proof PDF, "
                "not a trustworthy scoring authority."
            )

    authority_confirmed = selected is not None and selection_error is None

    payload = {
        "gateVersion": 1,
        "minimumProfessionalBytes": MIN_PROFESSIONAL_BYTES,
        "candidateCount": len(candidates),
        "candidates": candidates,
        "selectionMode": selection_mode,
        "selectedAuthority": selected,
        "selectionError": selection_error,
        "professionalPdfAuthorityConfirmed": authority_confirmed,
        "readyForManualTechniqueExtraction": authority_confirmed,
        "readyForTechniqueRendererTraining": False,
        "syntheticAnnotationsCreated": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "protectedPitchCheckpointChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Professional PDF authority selection gate complete")
    print(f"PDF candidates inspected: {len(candidates)}")
    print(f"Minimum professional PDF bytes: {MIN_PROFESSIONAL_BYTES}")
    if selected:
        print(f"Selected candidate: {selected['path']}")
        print(f"Selected candidate bytes: {selected['bytes']}")
    else:
        print("Selected candidate: None")
    print(f"Professional PDF authority confirmed: {authority_confirmed}")
    print(f"Ready for manual technique extraction: {authority_confirmed}")
    print("Ready for technique renderer training: False")
    print("Synthetic annotations created: False")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    if selection_error:
        print(f"Selection blocked: {selection_error}")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
