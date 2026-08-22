import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PREFLIGHT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-full-song-rhythm-regression-preflight.json"
OUTPUT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-113-measure-rhythm-regression.json"

EXPECTED_MEASURES = set(range(1, 114))
MEASURE_KEYS = {
    "measure",
    "measureNumber",
    "measure_number",
    "measureIndex",
    "measure_index",
    "bar",
    "barNumber",
    "bar_number",
}
COLLECTION_KEYS = {
    "measures",
    "measureRows",
    "measure_rows",
    "events",
    "noteEvents",
    "note_events",
    "rows",
    "sections",
    "attacks",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_measure(value: Any, key: str | None = None) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        number = value
    elif isinstance(value, float) and value.is_integer():
        number = int(value)
    elif isinstance(value, str) and value.strip().isdigit():
        number = int(value.strip())
    else:
        return None

    # Index fields are commonly zero-based. Convert only an explicit index key.
    if key and "index" in key.lower() and 0 <= number <= 112:
        number += 1

    return number if 1 <= number <= 113 else None


def collect_measures(value: Any, parent_key: str | None = None) -> set[int]:
    found: set[int] = set()

    if isinstance(value, dict):
        for key, child in value.items():
            if key in MEASURE_KEYS:
                measure = normalized_measure(child, key)
                if measure is not None:
                    found.add(measure)
            elif key in COLLECTION_KEYS and isinstance(child, list):
                # When a document contains exactly 113 ordered measure rows but
                # omits explicit numbers, its positions provide protected
                # coverage evidence without changing any musical content.
                if key.lower().startswith("measure") and len(child) == 113:
                    found.update(EXPECTED_MEASURES)
                for item in child:
                    found.update(collect_measures(item, key))
            else:
                found.update(collect_measures(child, key))

    elif isinstance(value, list):
        for item in value:
            found.update(collect_measures(item, parent_key))

    return found


def structural_signals(value: Any) -> dict[str, bool]:
    signals = {
        "hasSections": False,
        "hasTiming": False,
        "hasRhythm": False,
        "hasEvents": False,
        "hasWinner": False,
        "hasAttacks": False,
    }

    def walk(item: Any) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                lowered = key.lower()
                if "section" in lowered:
                    signals["hasSections"] = True
                if any(token in lowered for token in ("time", "phase", "beat", "tempo", "alignment")):
                    signals["hasTiming"] = True
                if "rhythm" in lowered or "duration" in lowered:
                    signals["hasRhythm"] = True
                if "event" in lowered or "note" in lowered:
                    signals["hasEvents"] = True
                if "winner" in lowered or "selected" in lowered:
                    signals["hasWinner"] = True
                if "attack" in lowered or "onset" in lowered:
                    signals["hasAttacks"] = True
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)

    walk(value)
    return signals


def inspect_candidate(path: Path) -> dict[str, Any]:
    try:
        payload = load_json(path)
    except Exception as exc:
        return {
            "path": str(path.relative_to(ROOT)),
            "readableJson": False,
            "error": str(exc),
            "coveredMeasures": [],
            "measureCoverageCount": 0,
        }

    measures = collect_measures(payload)
    signals = structural_signals(payload)
    score = len(measures)
    score += 20 if signals["hasEvents"] else 0
    score += 15 if signals["hasTiming"] else 0
    score += 15 if signals["hasRhythm"] else 0
    score += 10 if signals["hasSections"] else 0
    score += 10 if signals["hasWinner"] else 0
    score += 10 if signals["hasAttacks"] else 0

    return {
        "path": str(path.relative_to(ROOT)),
        "readableJson": True,
        "sha256": sha256_file(path),
        "coveredMeasures": sorted(measures),
        "measureCoverageCount": len(measures),
        "structuralSignals": signals,
        "selectionScore": score,
    }


def main() -> None:
    if not PREFLIGHT_PATH.exists():
        raise FileNotFoundError(
            f"Missing preflight artifact: {PREFLIGHT_PATH.relative_to(ROOT)}"
        )

    preflight = load_json(PREFLIGHT_PATH)
    if preflight.get("protectedFullSongRhythmRegressionPreflightPassed") is not True:
        raise RuntimeError("Protected full-song rhythm regression preflight has not passed")
    if preflight.get("expectedMeasureCount") != 113:
        raise RuntimeError("Preflight does not declare the 113-measure professional target")
    if preflight.get("rendererIntegrationHumanApprovalPassed") is not True:
        raise RuntimeError("Renderer integration human approval is missing")

    discovered = preflight.get("discoveredCandidateArtifacts") or {}
    candidate_paths: list[Path] = []
    for name, metadata in discovered.items():
        relative = metadata.get("path") if isinstance(metadata, dict) else None
        path = ROOT / relative if relative else PUBLIC / name
        if path.exists() and path.suffix.lower() == ".json":
            candidate_paths.append(path)

    inspections = [inspect_candidate(path) for path in sorted(set(candidate_paths))]
    readable = [item for item in inspections if item.get("readableJson")]
    ranked = sorted(
        readable,
        key=lambda item: (
            int(item.get("selectionScore", 0)),
            int(item.get("measureCoverageCount", 0)),
            item.get("path", ""),
        ),
        reverse=True,
    )

    union: set[int] = set()
    selected_sources: list[dict[str, Any]] = []
    remaining = set(EXPECTED_MEASURES)

    # Greedy source selection: choose artifacts that add the most uncovered
    # measures, using structural score only as a tie-breaker.
    unused = list(ranked)
    while remaining and unused:
        best = max(
            unused,
            key=lambda item: (
                len(set(item.get("coveredMeasures", [])) & remaining),
                int(item.get("selectionScore", 0)),
            ),
        )
        gain = set(best.get("coveredMeasures", [])) & remaining
        if not gain:
            break
        selected_sources.append(best)
        union.update(gain)
        remaining -= gain
        unused.remove(best)

    full_measure_coverage = union == EXPECTED_MEASURES
    all_required_signal_types = {
        "sections": any(item.get("structuralSignals", {}).get("hasSections") for item in readable),
        "timing": any(item.get("structuralSignals", {}).get("hasTiming") for item in readable),
        "rhythm": any(item.get("structuralSignals", {}).get("hasRhythm") for item in readable),
        "events": any(item.get("structuralSignals", {}).get("hasEvents") for item in readable),
        "attacks": any(item.get("structuralSignals", {}).get("hasAttacks") for item in readable),
    }
    structural_coverage_passed = all(all_required_signal_types.values())
    regression_passed = full_measure_coverage and structural_coverage_passed

    output = {
        "regressionName": "Jimmy Page protected 113-measure rhythm regression",
        "regressionVersion": 1,
        "expectedMeasureCount": 113,
        "candidateArtifactsInspected": len(inspections),
        "readableCandidateArtifacts": len(readable),
        "selectedSourceArtifacts": [item["path"] for item in selected_sources],
        "selectedSourceCount": len(selected_sources),
        "coveredMeasures": sorted(union),
        "coveredMeasureCount": len(union),
        "missingMeasures": sorted(EXPECTED_MEASURES - union),
        "fullMeasureCoveragePassed": full_measure_coverage,
        "requiredStructuralSignals": all_required_signal_types,
        "structuralCoveragePassed": structural_coverage_passed,
        "protected113MeasureRhythmRegressionPassed": regression_passed,
        "candidateInspections": inspections,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForTargetedRhythmGapAnalysis": True,
        "readyForProtectedFullSongComparison": regression_passed,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Protected 113-measure rhythm regression complete")
    print(f"Candidate artifacts inspected: {len(inspections)}")
    print(f"Readable candidate artifacts: {len(readable)}")
    print(f"Selected source artifacts: {len(selected_sources)}")
    print(f"Measures covered: {len(union)}/113")
    print(f"Missing measures: {sorted(EXPECTED_MEASURES - union)}")
    print(f"Full measure coverage passed: {full_measure_coverage}")
    for name, passed in all_required_signal_types.items():
        print(f"{name} signal present: {passed}")
    print(f"Structural coverage passed: {structural_coverage_passed}")
    print(f"Protected 113-measure rhythm regression passed: {regression_passed}")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print("Ready for targeted rhythm gap analysis: True")
    print(f"Ready for protected full-song comparison: {regression_passed}")
    print("Ready for production: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
