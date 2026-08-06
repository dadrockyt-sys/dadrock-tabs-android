from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
FOCUSED_PROOF_PATH = PUBLIC / "gomyway-chorus-33-35-focused-proof-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-bend-vibrato-inventory-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-bend-vibrato-inventory-v1-manifest.json"

TECHNIQUE_KEYS = {
    "bend",
    "bends",
    "bendAmount",
    "bendSemitones",
    "bendType",
    "preBend",
    "release",
    "vibrato",
    "vibratoDepth",
    "vibratoRate",
    "technique",
    "techniques",
    "articulation",
    "articulations",
}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def measure_of(row: dict[str, Any]) -> int | None:
    return integer(row.get("measureNumber", row.get("measure")))


def step_of(row: dict[str, Any]) -> int | None:
    return integer(row.get("quantizedStep", row.get("step")))


def canonical_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_techniques(value: Any, prefix: str = "") -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            if key in TECHNIQUE_KEYS:
                found.append({"path": child_prefix, "value": child})
            found.extend(collect_techniques(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(collect_techniques(child, f"{prefix}[{index}]"))
    return found


def classify(found: list[dict[str, Any]]) -> tuple[bool, bool]:
    text = json.dumps(found, sort_keys=True).lower()
    has_bend = "bend" in text or '"release"' in text
    has_vibrato = "vibrato" in text
    return has_bend, has_vibrato


def main() -> None:
    source_hash_before = canonical_hash(SOURCE_PATH)
    source = load(SOURCE_PATH)
    proof = load(FOCUSED_PROOF_PATH)

    if proof.get("passed") is not True:
        raise RuntimeError("Focused chorus proof is not green.")
    if proof.get("readyForBendsAndVibratoWork") is not True:
        raise RuntimeError("Focused chorus proof is not ready for bends/vibrato work.")

    events = source_rows(source)
    if len(events) != 949:
        raise RuntimeError(f"Expected 949 protected source events, found {len(events)}.")

    rows: list[dict[str, Any]] = []
    bend_rows = 0
    vibrato_rows = 0

    for index, event in enumerate(events):
        measure = measure_of(event)
        if measure not in {33, 34, 35}:
            continue

        found = collect_techniques(event)
        has_bend, has_vibrato = classify(found)
        if has_bend:
            bend_rows += 1
        if has_vibrato:
            vibrato_rows += 1

        rows.append({
            "sourceEventIndex": index,
            "measureNumber": measure,
            "quantizedStep": step_of(event),
            "hasExistingBendMetadata": has_bend,
            "hasExistingVibratoMetadata": has_vibrato,
            "techniqueMetadata": found,
            "readOnly": True,
        })

    source_hash_after = canonical_hash(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after

    # This stage inventories existing metadata only. It deliberately does not
    # claim audio support, infer missing techniques, or promote any correction.
    output = {
        "schemaVersion": 1,
        "inventoryType": "read-only-chorus-bend-vibrato-metadata-inventory",
        "passed": source_unchanged and len(events) == 949,
        "chorusEventCount": len(rows),
        "eventsWithExistingBendMetadata": bend_rows,
        "eventsWithExistingVibratoMetadata": vibrato_rows,
        "rows": rows,
        "readyForAudioTechniqueEvidence": source_unchanged,
        "audioTechniqueSupportClaimed": False,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalNotesCopiedIntoProtectedSource": False,
        "sourceEventCount": len(events),
        "sourceHashBefore": source_hash_before,
        "sourceHashAfter": source_hash_after,
        "sourceHashUnchanged": source_unchanged,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": output["passed"],
        "chorusEventCount": len(rows),
        "eventsWithExistingBendMetadata": bend_rows,
        "eventsWithExistingVibratoMetadata": vibrato_rows,
        "readyForAudioTechniqueEvidence": output["readyForAudioTechniqueEvidence"],
        "sourceEventCount": len(events),
        "sourceHashUnchanged": source_unchanged,
        "sourceEventsModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 BEND/VIBRATO INVENTORY V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Chorus source events inventoried:", len(rows))
    print("Events with existing bend metadata:", bend_rows)
    print("Events with existing vibrato metadata:", vibrato_rows)
    print("Audio technique support claimed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Professional reference used as training label only: True")
    print("Professional notes copied into protected source: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for audio technique evidence:", output["readyForAudioTechniqueEvidence"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
