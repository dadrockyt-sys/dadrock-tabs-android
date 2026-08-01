import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

GAP_ANALYSIS_PATH = PUBLIC / "gomyway-jimmy-paige-targeted-rhythm-gap-analysis.json"
OUTPUT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-section-comparison-preflight.json"

REFERENCE_CANDIDATES = [
    PUBLIC / "gomyway-professional-rhythm-reference-v2.json",
    PUBLIC / "gomyway-professional-rhythm-reference.json",
]

SIGNAL_TOKENS = {
    "pitch": ("pitch", "midi", "fret", "string", "voicing"),
    "timing": ("time", "phase", "beat", "tempo", "offset", "alignment"),
    "attack": ("attack", "onset", "strum"),
    "duration": ("duration", "sustain", "release", "tie"),
    "technique": ("bend", "vibrato", "mute", "slide", "pick", "technique"),
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
                if lowered in {
                    "measure",
                    "measurenumber",
                    "measure_number",
                    "bar",
                    "barnumber",
                    "bar_number",
                }:
                    if isinstance(child, int) and 1 <= child <= 113:
                        found.add(child)
                    elif isinstance(child, str) and child.isdigit():
                        number = int(child)
                        if 1 <= number <= 113:
                            found.add(number)
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)

    walk(value)
    return found


def main() -> None:
    if not GAP_ANALYSIS_PATH.exists():
        raise FileNotFoundError(
            f"Missing gap analysis: {GAP_ANALYSIS_PATH.relative_to(ROOT)}"
        )

    gap_analysis = load_json(GAP_ANALYSIS_PATH)
    if gap_analysis.get("targetedRhythmGapAnalysisReady") is not True:
        raise RuntimeError("Targeted rhythm gap analysis has not passed")
    if gap_analysis.get("readyForProtectedSectionComparison") is not True:
        raise RuntimeError("Protected section comparison gate is not open")

    reference_path = next((path for path in REFERENCE_CANDIDATES if path.exists()), None)
    if reference_path is None:
        raise FileNotFoundError(
            "No professional rhythm reference JSON found. Expected one of: "
            + ", ".join(str(path.relative_to(ROOT)) for path in REFERENCE_CANDIDATES)
        )

    reference = load_json(reference_path)
    reference_signals = signal_map(reference)
    reference_measures = measure_numbers(reference)

    candidate_paths = sorted(
        path
        for path in PUBLIC.glob("gomyway-*.json")
        if path not in {GAP_ANALYSIS_PATH, OUTPUT_PATH, reference_path}
        and any(
            token in path.name.lower()
            for token in ("winner", "event", "rhythm", "timing", "section", "professional")
        )
    )

    candidate_reports = []
    for path in candidate_paths:
        try:
            payload = load_json(path)
        except Exception as exc:
            candidate_reports.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "readable": False,
                    "error": str(exc),
                }
            )
            continue

        candidate_reports.append(
            {
                "path": str(path.relative_to(ROOT)),
                "readable": True,
                "sha256": sha256_file(path),
                "signals": signal_map(payload),
                "measureCoverageCount": len(measure_numbers(payload)),
            }
        )

    readable_candidates = [row for row in candidate_reports if row.get("readable")]
    candidate_signal_coverage = {
        signal: any(row.get("signals", {}).get(signal) for row in readable_candidates)
        for signal in SIGNAL_TOKENS
    }

    section_plan = gap_analysis.get("sectionPlan") or []
    section_plan_valid = (
        len(section_plan) == 9
        and section_plan[0].get("startMeasure") == 1
        and section_plan[-1].get("endMeasure") == 113
    )

    reference_ready = all(reference_signals.values())
    candidate_evidence_ready = all(candidate_signal_coverage.values())
    preflight_passed = (
        section_plan_valid
        and reference_ready
        and candidate_evidence_ready
        and len(readable_candidates) > 0
    )

    output = {
        "preflightName": "Jimmy Page protected section comparison preflight",
        "preflightVersion": 1,
        "professionalReference": str(reference_path.relative_to(ROOT)),
        "professionalReferenceSha256": sha256_file(reference_path),
        "professionalReferenceSignals": reference_signals,
        "professionalReferenceExplicitMeasureCount": len(reference_measures),
        "sectionPlanCount": len(section_plan),
        "sectionPlanValid": section_plan_valid,
        "candidateArtifactsInspected": len(candidate_reports),
        "readableCandidateArtifacts": len(readable_candidates),
        "candidateSignalCoverage": candidate_signal_coverage,
        "candidateReports": candidate_reports,
        "protectedSectionComparisonPreflightPassed": preflight_passed,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForProtectedSectionComparison": preflight_passed,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Protected section comparison preflight complete")
    print(f"Professional reference: {reference_path.relative_to(ROOT)}")
    for name, present in reference_signals.items():
        print(f"Professional reference {name} signal present: {present}")
    print(f"Section plan valid: {section_plan_valid}")
    print(f"Candidate artifacts inspected: {len(candidate_reports)}")
    print(f"Readable candidate artifacts: {len(readable_candidates)}")
    for name, present in candidate_signal_coverage.items():
        print(f"Candidate {name} evidence present: {present}")
    print(f"Protected section comparison preflight passed: {preflight_passed}")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Ready for protected section comparison: {preflight_passed}")
    print("Ready for production: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not preflight_passed:
        raise RuntimeError("Protected section comparison preflight did not pass")


if __name__ == "__main__":
    main()
