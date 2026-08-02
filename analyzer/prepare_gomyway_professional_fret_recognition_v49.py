"""Prepare read-only professional fret-glyph recognition jobs for measures 17-113.

This stage validates the complete v48 scaffold and the locked human-reviewed
fret template library, then creates one recognition job per canonical row. It
does not invent fret values, modify measures 1-16, use candidate audio, or
promote any result to production.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SCAFFOLD = PUBLIC / "gomyway-approved-string-geometry-extraction-scaffold-v48.json"
TEMPLATES = PUBLIC / "gomyway-locked-glyph-template-library-v33.json"
OUTPUT = PUBLIC / "gomyway-professional-fret-recognition-jobs-v49.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def flatten_templates(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        fret = value.get("fret")
        template_id = value.get("templateId") or value.get("id")
        image = value.get("image") or value.get("mask") or value.get("templateImage")
        if template_id is not None or (fret is not None and image is not None):
            found.append(value)
        for child in value.values():
            found.extend(flatten_templates(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(flatten_templates(child))
    return found


def normalize_fret(value: Any) -> str | None:
    try:
        fret = str(int(value))
    except (TypeError, ValueError):
        return None
    return fret if fret in {"0", "2", "3"} else None


def main() -> None:
    scaffold = load_json(SCAFFOLD)
    templates = load_json(TEMPLATES)

    if scaffold.get("complete17To113CoveragePassed") is not True:
        raise RuntimeError("V48 does not have complete measures 17-113 coverage")
    if scaffold.get("lockedMeasures1To16Modified") is not False:
        raise RuntimeError("V48 locked-measure safeguard is not intact")
    if scaffold.get("candidateAudioUsed") is not False:
        raise RuntimeError("V48 unexpectedly used candidate audio")

    rows = scaffold.get("rows")
    if not isinstance(rows, list) or len(rows) != 45:
        raise RuntimeError(f"Expected 45 v48 canonical rows, found {len(rows or [])}")

    raw_templates = flatten_templates(templates)
    by_fret: dict[str, list[dict[str, Any]]] = {"0": [], "2": [], "3": []}
    for template in raw_templates:
        fret = normalize_fret(template.get("fret"))
        if fret is None:
            template_id = str(template.get("templateId") or template.get("id") or "")
            for candidate in ("0", "2", "3"):
                if f"fret-{candidate}-" in template_id:
                    fret = candidate
                    break
        if fret is not None:
            by_fret[fret].append(template)

    counts = {fret: len(items) for fret, items in by_fret.items()}
    missing_classes = [fret for fret, count in counts.items() if count == 0]
    if missing_classes:
        raise RuntimeError(f"Missing locked template classes: {missing_classes}")

    jobs: list[dict[str, Any]] = []
    covered: set[int] = set()
    for index, row in enumerate(rows, start=1):
        measures = row.get("measures", [])
        if not isinstance(measures, list):
            measures = []
        normalized_measures = sorted(
            {
                int(measure)
                for measure in measures
                if isinstance(measure, int) and 17 <= measure <= 113
            }
        )
        covered.update(normalized_measures)
        jobs.append(
            {
                "jobIndex": index,
                "pageNumber": int(row.get("pageNumber", 0)),
                "rowIndex": int(row.get("rowIndex", 0)),
                "measures": normalized_measures,
                "crop": row.get("crop"),
                "pixelBounds": row.get("pixelBounds", {}),
                "stringRowsPixels": row.get("stringRowsPixels", []),
                "allowedLockedFretClasses": ["0", "2", "3"],
                "templateCountsByFret": counts,
                "recognitionPerformed": False,
                "recognizedGlyphs": [],
                "humanVerificationRequired": True,
            }
        )

    expected = set(range(17, 114))
    missing_measures = sorted(expected - covered)
    complete = len(jobs) == 45 and not missing_measures

    output = {
        "diagnosticName": "Gomyway professional fret recognition job preparation v49",
        "scaffoldSource": str(SCAFFOLD.relative_to(ROOT)),
        "templateSource": str(TEMPLATES.relative_to(ROOT)),
        "canonicalRowsExpected": 45,
        "canonicalRowsPrepared": len(jobs),
        "uniqueMeasures17To113Covered": len(covered),
        "complete17To113CoveragePassed": complete,
        "missingMeasures": missing_measures,
        "requiredFretClasses": ["0", "2", "3"],
        "templateCountsByFret": counts,
        "allRequiredTemplateClassesAvailable": not missing_classes,
        "recognitionJobs": jobs,
        "professionalFretGlyphRecognitionPerformed": False,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "run-locked-template-matching-over-v49-recognition-jobs-v50",
    }

    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Professional fret recognition job preparation v49 complete")
    print(f"Canonical rows prepared: {output['canonicalRowsPrepared']}")
    print(f"Unique measures 17-113 covered: {output['uniqueMeasures17To113Covered']}")
    print(f"Complete 17-113 coverage passed: {complete}")
    print(f"Missing measures: {missing_measures}")
    print(f"Template counts by fret: {counts}")
    print("All required template classes available: True")
    print("Professional fret glyph recognition performed: False")
    print("Semantic note events 17-113 extracted: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")

    if not complete:
        raise RuntimeError("V49 failed complete recognition-job coverage")


if __name__ == "__main__":
    main()
