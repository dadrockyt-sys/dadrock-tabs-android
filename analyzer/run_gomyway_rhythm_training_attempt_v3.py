from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import run_gomyway_rhythm_training_attempt_v2 as v2

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "analyzer" / "training_profiles" / "rhythm-guitar-reference.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def halton(index: int, base: int) -> float:
    result = 0.0
    factor = 1.0
    while index > 0:
        factor /= base
        result += factor * (index % base)
        index //= base
    return result


def adaptive_parameters(attempt: int, best: dict[str, Any] | None) -> dict[str, Any]:
    best_params = (best or {}).get("parameters", {})
    center_tempo = float(best_params.get("tempoBpm", 129.0))
    center_origin = float(best_params.get("audioOriginSeconds", 0.0))
    radius = max(0.01, 0.30 / (1.0 + attempt / 96.0))
    tempo = center_tempo + (halton(attempt, 2) - 0.5) * 2.0 * max(0.08, radius * 4.0)
    origin = center_origin + (halton(attempt, 3) - 0.5) * 2.0 * radius
    octave_modes = [0, -12, 12]
    confidence_levels = [0.0, 0.04, 0.08, 0.12, 0.16, 0.20, 0.24]
    strategies = ["rhythm-heavy", "lowest-fret"]
    return {
        "tempoBpm": round(max(126.0, min(132.0, tempo)), 6),
        "audioOriginSeconds": round(max(-0.45, min(0.45, origin)), 6),
        "octaveShift": octave_modes[(attempt - 1) % len(octave_modes)],
        "stringStrategy": strategies[((attempt - 1) // len(octave_modes)) % len(strategies)],
        "minimumConfidence": confidence_levels[((attempt - 1) // 2) % len(confidence_levels)],
        "searchRadiusSeconds": round(radius, 6),
        "adaptiveSeedComposite": float((best or {}).get("compositePercent", 0.0)),
    }


def main() -> None:
    profile = load(PROFILE_PATH)
    attempt = v2.attempt_number(profile)
    best_path = ROOT / profile["bestCheckpointPath"]
    best = load(best_path) if best_path.exists() else None
    params = adaptive_parameters(attempt, best)
    reference = load(ROOT / profile["professionalReferencePath"])
    source = load(ROOT / profile["candidateSourceEventsPath"])
    refs = v2.reference_events(reference)
    candidates = v2.generate(source.get("events", []), reference, params)
    scored = v2.score(refs, candidates, int(profile.get("timingToleranceSteps", 1)))
    result = {
        "attempt": attempt,
        "status": "scored-adaptive-regeneration-v3",
        "parameters": params,
        **scored,
        "candidateEvents": candidates,
        "protections": profile["protectedRules"],
        "sixteenthNoteGridUsed": True,
        "professionalReferenceUsedForScoringOnly": True,
        "professionalReferenceCopiedIntoCandidate": False,
        "rendererEventsPromoted": False,
        "humanReviewRequiredBeforeRendererPromotion": True,
    }
    write(ROOT / profile["attemptResultPath"], result)
    print("ADAPTIVE GENERATION 3 ATTEMPT", attempt, "SCORED", flush=True)
    print("Parameters:", params, flush=True)
    print("Candidate events:", len(candidates), flush=True)
    print("Category scores:", result["categoryScoresPercent"], flush=True)
    print("Matched:", result["matchedReferenceEventCount"], "Unresolved:", result["unresolvedReferenceEventCount"], flush=True)


if __name__ == "__main__":
    main()
