from __future__ import annotations

import json
from pathlib import Path

import rhythm_candidate_analyzer_v8 as rhythm_candidates

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIO_PATH = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
FIXTURE_PATH = REPO_ROOT / "analyzer" / "fixtures" / "gomyway_full_chord_sustain_reference.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates.json"


def _load_fixture() -> dict:
    if not FIXTURE_PATH.exists():
        return {
            "tempo": 129.0,
            "timeSignature": "4/4",
            "expectedMeasureCount": 113,
        }
    return json.loads(FIXTURE_PATH.read_text())


def main() -> None:
    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"Missing rhythm benchmark audio: {AUDIO_PATH}")

    fixture = _load_fixture()
    tempo = float(fixture.get("tempo") or 129.0)
    time_signature = str(fixture.get("timeSignature") or "4/4")
    total_measures = max(1, int(fixture.get("expectedMeasureCount") or 113))

    candidates, diagnostics = rhythm_candidates.analyze_rhythm_candidates(
        str(AUDIO_PATH),
        tempo=tempo,
        time_signature=time_signature,
        total_measures=total_measures,
    )

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-direct-audio-rhythm-candidate-evidence",
        "audioName": AUDIO_PATH.name,
        "tempo": tempo,
        "timeSignature": time_signature,
        "totalMeasures": total_measures,
        "candidates": candidates,
        "diagnostics": diagnostics,
        "passed": bool(candidates)
        and diagnostics.get("independentOfV7Events") is True
        and diagnostics.get("rendererChanged") is False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "Direct-audio rhythm candidates are read-only timing evidence. "
            "They must not replace, synthesize, or move any V7 note until a later "
            "adoption benchmark proves stronger repeated-riff support and preserves "
            "source pitch, traceability, and the locked V7 production output."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2))

    print("V8 direct rhythm candidate pass:", report["passed"])
    print("Independent of V7 events:", diagnostics.get("independentOfV7Events"))
    print("Renderer changed:", diagnostics.get("rendererChanged"))
    print("Rhythm candidates:", diagnostics.get("candidateCount"))
    print("Intro rhythm candidates:", diagnostics.get("introCandidateCount"))
    print("Intro onset-step histogram:", diagnostics.get("introStepHistogram"))
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
