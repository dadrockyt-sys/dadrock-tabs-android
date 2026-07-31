from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
JOIN_PATH = REPO_ROOT / "public" / "gomyway-v8-notation-em-riff-identity-join.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-v8-em-riff-identity-candidate-summary.json"

STRING_NAMES = {
    0: "high-e",
    1: "B",
    2: "G",
    3: "D",
    4: "A",
    5: "low-E",
}


def _candidate_label(candidate: dict[str, Any] | None) -> str:
    if not candidate:
        return "none"
    string_index = candidate.get("stringIndex")
    fret = candidate.get("fret")
    support = candidate.get("support")
    string_name = STRING_NAMES.get(string_index, f"string-{string_index}")
    return f"{string_name} fret {fret} (support {support})"


def main() -> None:
    if not JOIN_PATH.exists():
        raise FileNotFoundError(
            "Missing V8 Em riff identity join. Run "
            "python analyzer/run_v8_notation_em_riff_identity_join_benchmark.py first."
        )

    join = json.loads(JOIN_PATH.read_text())
    if join.get("passed") is not True:
        raise ValueError("V8 Em riff identity join has not passed.")

    summary_patterns: dict[str, list[dict[str, Any]]] = {}
    print("V8 Em riff identity candidate summary")

    for pattern_id in ("em-riff-a", "em-riff-b"):
        print(f"{pattern_id}:")
        summary_slots: list[dict[str, Any]] = []
        for slot in (join.get("patternEvidence") or {}).get(pattern_id) or []:
            step = slot.get("quantizedStep")
            leading = slot.get("leadingIdentity")
            alternatives = (slot.get("identityCandidates") or [])[1:4]
            print(f"  step {step}: {_candidate_label(leading)}")
            if alternatives:
                print(
                    "    alternatives:",
                    "; ".join(_candidate_label(item) for item in alternatives),
                )
            summary_slots.append(
                {
                    "quantizedStep": step,
                    "leadingIdentity": leading,
                    "alternatives": alternatives,
                    "manualProfessionalVerificationRequired": True,
                }
            )
        summary_patterns[pattern_id] = summary_slots

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-em-riff-identity-candidate-summary",
        "passed": True,
        "readyForExactScoring": False,
        "patterns": summary_patterns,
        "safeguards": {
            "sourceJoinReadOnly": True,
            "doesNotModifyV8Notation": True,
            "doesNotPromoteCandidates": True,
            "professionalManualVerificationRequired": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
            "noSyntheticNotes": True,
        },
        "nextStep": (
            "Compare the nine printed leading identities against the visible professional score. "
            "Do not promote any identity until it is manually confirmed."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Ready for exact scoring: False")
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
