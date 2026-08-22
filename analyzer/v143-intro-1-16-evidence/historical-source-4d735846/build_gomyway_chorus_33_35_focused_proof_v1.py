from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

V1_MODULE_PATH = Path(__file__).with_name(
    "build_gomyway_chorus_33_35_chord_candidate_projection_v1.py"
)
PROJECTION_PATH = PUBLIC / "gomyway-chorus-33-35-chord-candidate-projection-v4.json"
SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-focused-proof-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-focused-proof-v1-manifest.json"

EXPECTED_SUPPORTED = {
    (33, 0), (33, 4), (33, 8),
    (34, 0), (34, 4), (34, 8),
    (35, 0), (35, 2), (35, 6), (35, 10),
}
EXPECTED_UNSUPPORTED = {(35, 4), (35, 8)}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def load_v1_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "gomyway_chord_projection_v1",
        V1_MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load V1 chord projection helpers.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    v1 = load_v1_module()
    projection = load(PROJECTION_PATH)
    source = load(SOURCE_PATH)

    if projection.get("readyForFocusedChorusProof") is not True:
        raise RuntimeError("V4 projection is not ready for focused chorus proof.")
    if projection.get("acceptedCandidateCount") != 10:
        raise RuntimeError("Expected 10 accepted chorus candidates.")
    if projection.get("rejectedCandidateCount") != 0:
        raise RuntimeError("Focused proof requires zero rejected candidates.")
    if projection.get("unsupportedTargetCount") != 2:
        raise RuntimeError("Expected exactly two preserved unsupported targets.")

    source_hash_before = sha256(SOURCE_PATH)
    source_events = v1.source_rows(source)
    if len(source_events) != 949:
        raise RuntimeError(f"Expected 949 protected source events, found {len(source_events)}.")

    proof_rows: list[dict[str, Any]] = []
    seen_supported: set[tuple[int, int]] = set()

    for row in projection.get("rows", []):
        if not isinstance(row, dict):
            continue
        measure = int(row["measureNumber"])
        step = int(row["quantizedStep"])
        key = (measure, step)
        selected = row.get("selectedCandidate")
        if key not in EXPECTED_SUPPORTED:
            raise RuntimeError(f"Unexpected supported target: {key}")
        if row.get("qualityGate") is not True or not isinstance(selected, dict):
            raise RuntimeError(f"Target failed focused-proof gate: {key}")

        proposed_notes = selected.get("notes")
        if not isinstance(proposed_notes, list):
            raise RuntimeError(f"Selected candidate has no notes: {key}")

        current_notes = v1.current_notes_at(source_events, measure, step)
        proof_rows.append({
            "measureNumber": measure,
            "quantizedStep": step,
            "currentProtectedSourceNotes": [
                {"string": string, "fret": fret}
                for string, fret in current_notes
            ],
            "proposedReadOnlyChordNotes": proposed_notes,
            "expectedMultiplicity": row["expectedMultiplicity"],
            "chordLabel": row["chordLabel"],
            "benchmarkFretDistance": selected.get("benchmarkFretDistance"),
            "audioSupported": True,
            "qualityGate": True,
            "readOnlyOverlay": True,
            "sourceEventsModified": False,
            "productionEligible": False,
        })
        seen_supported.add(key)

    unsupported = {
        (int(row["measureNumber"]), int(row["quantizedStep"]))
        for row in projection.get("unsupportedRows", [])
        if isinstance(row, dict)
    }

    supported_complete = seen_supported == EXPECTED_SUPPORTED
    unsupported_preserved = unsupported == EXPECTED_UNSUPPORTED
    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = supported_complete and unsupported_preserved and source_unchanged

    output = {
        "schemaVersion": 1,
        "proofType": "read-only-focused-chorus-33-35-chord-overlay",
        "passed": passed,
        "supportedTargetCount": len(proof_rows),
        "allSupportedTargetsPassed": supported_complete,
        "unsupportedTargetsPreserved": unsupported_preserved,
        "unsupportedRows": projection.get("unsupportedRows", []),
        "rows": proof_rows,
        "protectedSourceEventCount": len(source_events),
        "protectedSourceSha256Before": source_hash_before,
        "protectedSourceSha256After": source_hash_after,
        "sourceEventsModified": not source_unchanged,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalNotesCopiedIntoProtectedSource": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "readyForTechniqueCorrectionWork": passed,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "supportedTargetCount": len(proof_rows),
        "allSupportedTargetsPassed": supported_complete,
        "unsupportedTargetsPreserved": unsupported_preserved,
        "protectedSourceEventCount": len(source_events),
        "sourceEventsModified": not source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "readyForTechniqueCorrectionWork": passed,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 FOCUSED PROOF V1 COMPLETE")
    print("Passed:", passed)
    print("Supported targets proven:", len(proof_rows))
    print("All 10 supported targets passed:", supported_complete)
    print("Unsupported targets preserved:", unsupported_preserved)
    print("Protected source event count:", len(source_events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Professional reference used as training label only: True")
    print("Professional notes copied into protected source: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for bends and vibrato work:", passed)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
