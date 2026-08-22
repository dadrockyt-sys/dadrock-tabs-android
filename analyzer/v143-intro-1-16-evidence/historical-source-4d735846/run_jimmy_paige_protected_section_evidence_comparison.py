import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

PREFLIGHT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-section-comparison-preflight.json"
GAP_ANALYSIS_PATH = PUBLIC / "gomyway-jimmy-paige-targeted-rhythm-gap-analysis.json"
OUTPUT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-section-evidence-comparison.json"

SIGNAL_TOKENS = {
    "pitch": ("pitch", "midi", "fret", "string", "voicing"),
    "timing": ("time", "phase", "beat", "tempo", "offset", "alignment"),
    "attack": ("attack", "onset", "strum"),
    "duration": ("duration", "sustain", "release", "tie"),
    "technique": ("bend", "vibrato", "mute", "slide", "pick", "technique"),
}

MEASURE_KEYS = {
    "measure",
    "measurenumber",
    "measure_number",
    "bar",
    "barnumber",
    "bar_number",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key).lower())
            keys.update(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(walk_keys(child))
    return keys


def signal_map(value: Any) -> dict[str, bool]:
    keys = walk_keys(value)
    return {
        name: any(any(token in key for token in tokens) for key in keys)
        for name, tokens in SIGNAL_TOKENS.items()
    }


def measure_numbers(value: Any) -> set[int]:
    found: set[int] = set()

    def walk(item: Any) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                lowered = str(key).lower()
                if lowered in MEASURE_KEYS:
                    number: int | None = None
                    if isinstance(child, int) and not isinstance(child, bool):
                        number = child
                    elif isinstance(child, str) and child.strip().isdigit():
                        number = int(child.strip())
                    if number is not None and 1 <= number <= 113:
                        found.add(number)
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)

    walk(value)
    return found


def section_overlap(measures: set[int], start: int, end: int) -> set[int]:
    return {number for number in measures if start <= number <= end}


def main() -> None:
    if not PREFLIGHT_PATH.exists() or not GAP_ANALYSIS_PATH.exists():
        raise FileNotFoundError("Required section-comparison artifacts are missing")

    preflight = load_json(PREFLIGHT_PATH)
    gap_analysis = load_json(GAP_ANALYSIS_PATH)

    if preflight.get("protectedSectionComparisonPreflightPassed") is not True:
        raise RuntimeError("Protected section comparison preflight has not passed")
    if gap_analysis.get("targetedRhythmGapAnalysisReady") is not True:
        raise RuntimeError("Targeted rhythm gap analysis has not passed")

    reference_relative = preflight.get("professionalReference")
    if not isinstance(reference_relative, str):
        raise RuntimeError("Preflight does not identify a professional reference")
    reference_path = ROOT / reference_relative
    if not reference_path.exists():
        raise FileNotFoundError(f"Missing professional reference: {reference_relative}")

    reference = load_json(reference_path)
    reference_signals = signal_map(reference)
    reference_measures = measure_numbers(reference)

    candidate_rows: list[dict[str, Any]] = []
    for report in preflight.get("candidateReports") or []:
        if not isinstance(report, dict) or report.get("readable") is not True:
            continue
        relative = report.get("path")
        if not isinstance(relative, str):
            continue
        path = ROOT / relative
        if not path.exists():
            continue
        try:
            payload = load_json(path)
        except Exception:
            continue
        candidate_rows.append(
            {
                "path": relative,
                "sha256": sha256_file(path),
                "signals": signal_map(payload),
                "measures": measure_numbers(payload),
            }
        )

    section_results = []
    all_sections_ready = True

    for section in gap_analysis.get("sectionPlan") or []:
        start = int(section["startMeasure"])
        end = int(section["endMeasure"])
        expected_measures = set(range(start, end + 1))

        reference_overlap = section_overlap(reference_measures, start, end)
        reference_scope = (
            "explicit-section-measures"
            if reference_overlap
            else "global-professional-reference"
        )

        supporting_candidates = []
        union_measures: set[int] = set()
        signal_coverage = {name: False for name in SIGNAL_TOKENS}

        for row in candidate_rows:
            overlap = section_overlap(row["measures"], start, end)
            if not overlap:
                continue
            union_measures.update(overlap)
            for name, present in row["signals"].items():
                signal_coverage[name] = signal_coverage[name] or present
            supporting_candidates.append(
                {
                    "path": row["path"],
                    "coveredMeasures": sorted(overlap),
                    "signals": row["signals"],
                }
            )

        # Some full-song artifacts intentionally omit explicit measure numbers.
        # They may support global signal discovery, but they cannot prove section
        # placement. Section readiness therefore requires explicit overlap.
        measure_coverage_passed = union_measures == expected_measures
        candidate_signals_passed = all(signal_coverage.values())
        reference_signals_passed = all(reference_signals.values())
        section_ready = (
            measure_coverage_passed
            and candidate_signals_passed
            and reference_signals_passed
            and len(supporting_candidates) > 0
        )
        all_sections_ready = all_sections_ready and section_ready

        section_results.append(
            {
                "section": section["section"],
                "startMeasure": start,
                "endMeasure": end,
                "priority": section.get("priority"),
                "expectedMeasureCount": len(expected_measures),
                "coveredMeasureCount": len(union_measures),
                "missingMeasures": sorted(expected_measures - union_measures),
                "measureCoveragePassed": measure_coverage_passed,
                "referenceScope": reference_scope,
                "referenceSignals": reference_signals,
                "candidateSignalCoverage": signal_coverage,
                "candidateSignalsPassed": candidate_signals_passed,
                "supportingCandidateCount": len(supporting_candidates),
                "supportingCandidates": supporting_candidates,
                "sectionComparisonEvidenceReady": section_ready,
                "musicalValueAgreementConfirmed": False,
            }
        )

    output = {
        "comparisonName": "Jimmy Page protected nine-section evidence comparison",
        "comparisonVersion": 1,
        "professionalReference": reference_relative,
        "professionalReferenceSha256": sha256_file(reference_path),
        "sectionCount": len(section_results),
        "sectionsEvidenceReady": sum(
            1 for row in section_results if row["sectionComparisonEvidenceReady"]
        ),
        "allSectionsEvidenceReady": all_sections_ready,
        "sectionResults": section_results,
        "interpretation": {
            "confirmed": [
                "section-specific candidate measure coverage",
                "section-specific availability of pitch, timing, attack, duration, and technique evidence",
                "professional reference availability for all five evidence families",
            ],
            "notYetConfirmed": [
                "note-for-note pitch equality",
                "attack-by-attack timing equality",
                "duration and technique value equality",
            ],
        },
        "protectedSectionEvidenceComparisonPassed": all_sections_ready,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForProtectedSectionValueExtraction": all_sections_ready,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Protected nine-section evidence comparison complete")
    print(f"Sections inspected: {len(section_results)}")
    for row in section_results:
        print(
            f"{row['section']}: measures {row['startMeasure']}-{row['endMeasure']} "
            f"coverage={row['coveredMeasureCount']}/{row['expectedMeasureCount']} "
            f"signals={row['candidateSignalsPassed']} "
            f"ready={row['sectionComparisonEvidenceReady']}"
        )
    print(f"Sections evidence-ready: {output['sectionsEvidenceReady']}/{len(section_results)}")
    print(f"Protected section evidence comparison passed: {all_sections_ready}")
    print("Musical value agreement confirmed: False")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Ready for protected section value extraction: {all_sections_ready}")
    print("Ready for production: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not all_sections_ready:
        raise RuntimeError("Protected section evidence comparison did not pass")


if __name__ == "__main__":
    main()
