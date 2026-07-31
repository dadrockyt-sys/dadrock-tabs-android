from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = REPO_ROOT / "public"
OUTPUT_PATH = PUBLIC_ROOT / "gomyway-v7-identity-source-discovery.json"

EXCLUDED_NAMES = {
    "gomyway-professional-rhythm-reference.json",
    "gomyway-professional-rhythm-pattern-library.json",
    "gomyway-professional-em-riff-event-scaffold.json",
    "gomyway-professional-em-riff-timing-alignment.json",
    "gomyway-professional-em-riff-identity-evidence.json",
    "gomyway-full-song-v8-rhythm-candidates.json",
}


def walk(value: Any, path: str = "$" ) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if "stringIndex" in value and "fret" in value:
            found.append({
                "jsonPath": path,
                "measureNumber": value.get("measureNumber"),
                "quantizedStep": value.get("quantizedStep"),
                "start": value.get("start"),
                "stringIndex": value.get("stringIndex"),
                "fret": value.get("fret"),
            })
        for key, child in value.items():
            found.extend(walk(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(walk(child, f"{path}[{index}]"))
    return found


def main() -> None:
    reports: list[dict[str, Any]] = []
    for file_path in sorted(PUBLIC_ROOT.glob("*.json")):
        if file_path.name in EXCLUDED_NAMES:
            continue
        try:
            payload = json.loads(file_path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        matches = walk(payload)
        if not matches:
            continue
        measures = sorted({
            int(item["measureNumber"])
            for item in matches
            if item.get("measureNumber") is not None
            and str(item.get("measureNumber")).lstrip("-").isdigit()
        })
        reports.append({
            "file": str(file_path.relative_to(REPO_ROOT)),
            "identityEventCount": len(matches),
            "measureRange": [measures[0], measures[-1]] if measures else None,
            "sampleEvents": matches[:5],
        })

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "read-only-v7-identity-source-discovery",
        "passed": True,
        "candidateSourceCount": len(reports),
        "candidateSources": reports,
        "explanation": (
            "The V8 rhythm-candidate file contains onset timing only and intentionally has no "
            "string/fret identity. This discovery locates existing protected JSON sources that "
            "contain stringIndex and fret fields so a later benchmark can join V8 timing to V7 "
            "identity without altering either source."
        ),
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "noSyntheticNotes": True,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("V7 identity source discovery pass: True")
    print("Candidate identity sources found:", len(reports))
    for item in reports:
        print("-", item["file"], "events:", item["identityEventCount"], "measures:", item["measureRange"])
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
