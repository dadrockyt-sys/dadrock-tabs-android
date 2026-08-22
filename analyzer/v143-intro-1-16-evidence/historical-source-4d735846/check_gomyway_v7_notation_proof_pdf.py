#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_MANIFEST = Path("/tmp/gomyway-full-song-v7-notation-proof-manifest.json")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required manifest not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    args = parser.parse_args()

    manifest = load_json(Path(args.manifest))
    checks = manifest.get("checks") or {}
    pdf_path = Path(str(manifest.get("outputPdf") or ""))

    guard = {
        "proofPassed": manifest.get("passed") is True,
        "sourceRenderPlanPassed": manifest.get("sourceRenderPlanPassed") is True,
        "allSourceChecksGreen": all(bool(value) for value in checks.values()),
        "nineProofPagesPresent": int(manifest.get("pageCount") or 0) == 9,
        "all103CommandsRendered": int(manifest.get("commandCount") or 0) == 103,
        "allMarkerTypesPreserved": sorted(manifest.get("markerTypes") or [])
        == [
            "bend-release",
            "chord-label",
            "muted-attack",
            "palm-mute-span",
            "rest",
            "slide",
        ],
        "proofPdfExists": pdf_path.is_file(),
        "proofPdfNonEmpty": pdf_path.is_file() and pdf_path.stat().st_size > 1000,
        "productionEventsUnaffected": manifest.get("affectsProductionEvents") is False,
        "generatedTabUnaffected": manifest.get("affectsGeneratedTab") is False,
        "productionPdfUnaffected": manifest.get("affectsProductionPdf") is False,
        "protectedBaselinesUnchanged": manifest.get("protectedBaselinesChanged") is False,
    }

    print("JIMMY PAIGE V7 STANDALONE NOTATION PROOF PDF GUARD")
    print("=" * 72)
    for name, passed in guard.items():
        print("PASS" if passed else "FAIL", name)
    print("Proof PDF:", pdf_path)
    print("PDF bytes:", pdf_path.stat().st_size if pdf_path.is_file() else 0)
    print("Pages:", manifest.get("pageCount"))
    print("Drawing commands:", manifest.get("commandCount"))

    if all(guard.values()):
        print("\nV7 STANDALONE NOTATION PROOF PDF PRESERVED 💚")
        print("All 103 notation instructions render on nine isolated proof pages.")
        print("Production events, generated tab, and the real PDF renderer remain untouched.")
        return

    raise SystemExit("\nV7 notation proof PDF regression detected. Do not integrate.")


if __name__ == "__main__":
    main()
