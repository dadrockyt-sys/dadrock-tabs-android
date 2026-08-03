from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "public" / "gomyway-final-unique-source-resolution-audit.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"

CHUNKS = [
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-final-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-final-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-final-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-final-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-final-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-final-approved.json",
]


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def approved(measure: dict[str, Any]) -> bool:
    status = str(measure.get("humanReview", {}).get("status", "")).lower()
    events = measure.get("events", [])
    return status in {
        "approved", "human-approved", "validated", "source-approved",
        "source-reviewed", "exact-repeat-confirmed",
    } or (bool(events) and all(bool(event.get("humanValidated")) for event in events))


def main() -> None:
    audit = load(AUDIT)
    if not audit.get("readyForTraining") or int(audit.get("humanApprovedCount", 0)) != 97:
        raise RuntimeError("Final source-resolution audit is not ready for training")

    measures: dict[int, dict[str, Any]] = {}
    source_chunks: list[str] = []
    for path in CHUNKS:
        packet = load(path)
        source_chunks.append(str(path.relative_to(ROOT)))
        for measure in packet.get("measures", []):
            number = int(measure["measureNumber"])
            if number in measures:
                raise RuntimeError(f"Duplicate measure {number}")
            measures[number] = measure

    expected = set(range(17, 114))
    if set(measures) != expected:
        raise RuntimeError(f"Coverage mismatch: {sorted(expected - set(measures))}")
    unapproved = [number for number in sorted(measures) if not approved(measures[number])]
    if unapproved:
        raise RuntimeError(f"Unapproved measures remain: {unapproved}")

    ordered = [measures[number] for number in range(17, 114)]
    payload = {
        "schemaVersion": 1,
        "title": "Gomyway professional rhythm reference",
        "instrument": "rhythm-guitar",
        "stringCount": 6,
        "measureStart": 17,
        "measureEnd": 113,
        "gridSubdivision": "sixteenth-note",
        "stepsPerQuarter": 4,
        "tempoBpm": 129,
        "humanApprovedMeasureCount": 97,
        "readyForTraining": True,
        "professionalReferenceUsedForScoringOnly": True,
        "protectedBaselinesChanged": False,
        "sourceChunks": source_chunks,
        "measures": ordered,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["contentSha256"] = hashlib.sha256(canonical).hexdigest()
    temp = OUTPUT.with_suffix(".json.tmp")
    temp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temp.replace(OUTPUT)

    print("Final professional rhythm reference built")
    print("Measures covered: 97 / 97")
    print("Human-approved measures: 97 / 97")
    print("Ready for training: True")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("SHA256:", payload["contentSha256"])
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
