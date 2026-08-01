from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-chords-measures-33-38-v1.json"
SHADOW_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-canonical-chord-resolver-shadow-output.json"
MULTI_SECTION_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-multi-section-chord-shadow-validation.json"
SOURCE_EVENT_CANDIDATES = [
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json",
    REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json",
]
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-renderer-sidecar.json"
REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-renderer-sidecar-report.json"

STRING_NAMES = ["e", "B", "G", "D", "A", "E"]


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


def render_cells(frets: list[int | None]) -> list[dict[str, Any]]:
    if len(frets) != 6:
        raise RuntimeError(f"Expected six-string voicing, got {len(frets)} slots")
    return [
        {
            "stringIndex": index,
            "stringName": STRING_NAMES[index],
            "fret": fret,
            "display": "-" if fret is None else str(fret),
        }
        for index, fret in enumerate(frets)
    ]


def main() -> None:
    reference = load(REFERENCE_PATH)
    shadow = load(SHADOW_PATH)
    multi = load(MULTI_SECTION_PATH)
    source_path = first_existing(SOURCE_EVENT_CANDIDATES)

    if not bool(multi.get("multiSectionShadowPassed", False)):
        raise RuntimeError("Multi-section shadow validation is not passing")

    source_sha_before = sha256(source_path)
    reference_sha_before = sha256(REFERENCE_PATH)
    shadow_sha_before = sha256(SHADOW_PATH)

    rows: list[dict[str, Any]] = []

    for measure in reference.get("measures", []):
        measure_number = int(measure["measureNumber"])
        for attack_number, attack in enumerate(measure.get("attacks", []), start=1):
            frets = attack["voicingFretsHighToLow"]
            rows.append(
                {
                    "sectionRole": "training-professional-reference",
                    "measureNumber": measure_number,
                    "attackNumber": attack_number,
                    "targetPhase": attack["phase"],
                    "chordLabels": measure.get("chordLabels", []),
                    "resolutionMode": "professional-reference",
                    "renderCells": render_cells(frets),
                    "rendererMayConsume": False,
                    "productionMayConsume": False,
                }
            )

    for attack in shadow.get("attackRows", []):
        frets = attack["resolvedFretsHighToLow"]
        rows.append(
            {
                "sectionRole": "heldout-shadow-resolved",
                "measureNumber": int(attack["measureNumber"]),
                "attackNumber": int(attack["attackNumber"]),
                "targetPhase": attack["targetPhase"],
                "chordLabels": attack.get("chordLabels", []),
                "resolutionMode": attack["resolutionMode"],
                "renderCells": render_cells(frets),
                "rendererMayConsume": False,
                "productionMayConsume": False,
            }
        )

    invalid_rows: list[dict[str, Any]] = []
    for row in rows:
        cells = row.get("renderCells", [])
        string_indexes = [cell.get("stringIndex") for cell in cells]
        if len(cells) != 6 or string_indexes != [0, 1, 2, 3, 4, 5]:
            invalid_rows.append(row)
            continue
        for cell in cells:
            fret = cell.get("fret")
            if fret is not None and (not isinstance(fret, int) or fret < 0 or fret > 24):
                invalid_rows.append(row)
                break

    training_rows = [row for row in rows if row["sectionRole"] == "training-professional-reference"]
    heldout_rows = [row for row in rows if row["sectionRole"] == "heldout-shadow-resolved"]

    sidecar = {
        "sidecarVersion": 1,
        "sidecarType": "protected-chord-renderer-input",
        "mode": "benchmark-only",
        "trainingSectionAttackRows": len(training_rows),
        "heldoutSectionAttackRows": len(heldout_rows),
        "combinedAttackRows": len(rows),
        "rows": rows,
        "rendererMayConsume": False,
        "productionMayConsume": False,
        "sourceEventsMutated": False,
        "syntheticAttacksCreated": False,
        "professionalPdfRemainsScoringAuthority": True,
    }
    OUTPUT_PATH.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")

    source_sha_after = sha256(source_path)
    reference_sha_after = sha256(REFERENCE_PATH)
    shadow_sha_after = sha256(SHADOW_PATH)

    checks = {
        "trainingSection23of23": len(training_rows) == 23,
        "heldoutSection21of21": len(heldout_rows) == 21,
        "combined44of44": len(rows) == 44,
        "allRowsHaveSixStrings": len(invalid_rows) == 0,
        "sourceEventShaUnchanged": source_sha_before == source_sha_after,
        "professionalReferenceShaUnchanged": reference_sha_before == reference_sha_after,
        "shadowOutputShaUnchanged": shadow_sha_before == shadow_sha_after,
        "multiSectionShadowPassed": True,
    }
    benchmark_passed = all(checks.values())

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "protected-chord-renderer-sidecar",
        "checks": checks,
        "trainingSectionAttackRows": len(training_rows),
        "heldoutSectionAttackRows": len(heldout_rows),
        "combinedAttackRows": len(rows),
        "invalidRows": invalid_rows,
        "rendererSidecarBenchmarkPassed": benchmark_passed,
        "readyForNonRenderingLayoutPreview": benchmark_passed,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "protectedPitchCheckpointChanged": False,
        "professionalPdfRemainsScoringAuthority": True,
        "sidecarOutput": str(OUTPUT_PATH.relative_to(REPO_ROOT)),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Protected chord renderer sidecar benchmark complete")
    print(f"Training section render rows: {len(training_rows)}/23")
    print(f"Held-out section render rows: {len(heldout_rows)}/21")
    print(f"Combined render rows: {len(rows)}/44")
    print(f"Invalid render rows: {len(invalid_rows)}")
    for name, passed in checks.items():
        print(f"{name}: {passed}")
    print(f"Renderer sidecar benchmark passed: {benchmark_passed}")
    print(f"Ready for non-rendering layout preview: {benchmark_passed}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Sidecar: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
