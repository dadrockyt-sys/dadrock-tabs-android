import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ASSIGNMENT_PATH = PUBLIC / "gomyway-locked-event-glyph-reassignment-v23.json"
UNMATCHED_PATH = PUBLIC / "gomyway-unmatched-locked-glyph-slots-v25.json"
COVERAGE_PATH = PUBLIC / "gomyway-locked-template-coverage-audit-v31.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-template-technique-signatures-v32.json"


def all_slots(data: dict[str, Any]) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for row in data.get("rows", []):
        page = int(row.get("pageNumber", 0))
        row_index = int(row.get("rowIndex", 0))
        for measure_entry in row.get("measureEventSlots", []):
            measure = int(measure_entry.get("measure", 0))
            for slot in measure_entry.get("eventSlots", []):
                copied = dict(slot)
                copied["pageNumber"] = page
                copied["rowIndex"] = row_index
                copied["measure"] = int(copied.get("measure", measure))
                slots.append(copied)
    return slots


def fret_key(slot: dict[str, Any]) -> str:
    value = slot.get("fret")
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return str(value)


def normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): normalize_value(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    return value


def technique_signature(slot: dict[str, Any]) -> str:
    technique = slot.get("technique")
    normalized = normalize_value(technique if isinstance(technique, dict) else {"value": technique})
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"))


def active_technique_keys(slot: dict[str, Any]) -> list[str]:
    technique = slot.get("technique")
    if not isinstance(technique, dict):
        return ["value"] if technique not in (None, False, "", 0, [], {}) else []
    return sorted(
        str(key)
        for key, value in technique.items()
        if value not in (None, False, "", 0, [], {})
    )


def main() -> None:
    for path in (ASSIGNMENT_PATH, UNMATCHED_PATH, COVERAGE_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    assignment = json.loads(ASSIGNMENT_PATH.read_text(encoding="utf-8"))
    unmatched = json.loads(UNMATCHED_PATH.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))

    slots = all_slots(assignment)
    if len(slots) != 144:
        raise RuntimeError(f"Expected 144 locked slots, found {len(slots)}")
    if int(unmatched.get("unmatchedEventSlots", -1)) != 6:
        raise RuntimeError("V25 did not isolate six unresolved events")
    if int(assignment.get("componentCollisionSlots", -1)) != 0:
        raise RuntimeError("V23 contains component collisions")

    strict_slots = [
        slot for slot in slots
        if slot.get("assignedComponentIndex") is not None
        and bool(slot.get("strictCandidate", False))
    ]

    signatures: Counter[str] = Counter()
    signatures_by_fret: dict[str, Counter[str]] = defaultdict(Counter)
    active_keys: Counter[str] = Counter()
    active_keys_by_fret: dict[str, Counter[str]] = defaultdict(Counter)
    examples_by_signature: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for slot in strict_slots:
        fret = fret_key(slot)
        signature = technique_signature(slot)
        signatures[signature] += 1
        signatures_by_fret[fret][signature] += 1
        keys = active_technique_keys(slot)
        if not keys:
            active_keys["<none>"] += 1
            active_keys_by_fret[fret]["<none>"] += 1
        for key in keys:
            active_keys[key] += 1
            active_keys_by_fret[fret][key] += 1
        if len(examples_by_signature[signature]) < 8:
            examples_by_signature[signature].append({
                "pageNumber": slot.get("pageNumber"),
                "rowIndex": slot.get("rowIndex"),
                "measure": slot.get("measure"),
                "stringHighEToLowE": slot.get("normalizedStringHighEToLowE"),
                "fret": slot.get("fret"),
                "componentIndex": slot.get("assignedComponentIndex"),
                "distancePixels": slot.get("distancePixels"),
                "activeTechniqueKeys": keys,
            })

    required_frets = [str(value) for value in coverage.get("requiredFretClasses", [])]
    dominant_signature = signatures.most_common(1)[0][0] if signatures else None
    dominant_count = signatures[dominant_signature] if dominant_signature is not None else 0
    dominant_ratio = dominant_count / len(strict_slots) if strict_slots else 0.0

    dominant_coverage_by_fret = {
        fret: signatures_by_fret[fret][dominant_signature] if dominant_signature is not None else 0
        for fret in required_frets
    }
    every_fret_has_dominant_examples = all(
        dominant_coverage_by_fret.get(fret, 0) >= 3 for fret in required_frets
    )

    technique_metadata_is_global_or_default = (
        len(strict_slots) >= 100
        and dominant_signature is not None
        and dominant_ratio >= 0.70
        and every_fret_has_dominant_examples
    )

    signature_rows = []
    for signature, count in signatures.most_common():
        signature_rows.append({
            "signature": json.loads(signature),
            "count": count,
            "ratio": round(count / len(strict_slots), 6) if strict_slots else 0.0,
            "countsByFret": {
                fret: signatures_by_fret[fret][signature]
                for fret in required_frets
            },
            "examples": examples_by_signature[signature],
        })

    output = {
        "diagnosticName": "Gomyway locked template technique signature audit v32",
        "referenceType": "locked-professional-template-technique-metadata-audit",
        "sourceAssignment": str(ASSIGNMENT_PATH.relative_to(ROOT)),
        "sourceUnmatchedInspection": str(UNMATCHED_PATH.relative_to(ROOT)),
        "sourceCoverageAudit": str(COVERAGE_PATH.relative_to(ROOT)),
        "lockedEventSlotsObserved": len(slots),
        "strictCollisionFreeSlots": len(strict_slots),
        "requiredFretClasses": required_frets,
        "uniqueTechniqueSignatures": len(signatures),
        "dominantTechniqueSignature": json.loads(dominant_signature) if dominant_signature else None,
        "dominantTechniqueSignatureCount": dominant_count,
        "dominantTechniqueSignatureRatio": round(dominant_ratio, 6),
        "dominantSignatureCoverageByFret": dominant_coverage_by_fret,
        "everyFretHasAtLeastThreeDominantSignatureExamples": every_fret_has_dominant_examples,
        "activeTechniqueKeyCounts": dict(active_keys),
        "activeTechniqueKeyCountsByFret": {
            fret: dict(active_keys_by_fret[fret]) for fret in required_frets
        },
        "techniqueSignatures": signature_rows,
        "techniqueMetadataIsGlobalOrDefault": technique_metadata_is_global_or_default,
        "unresolvedEventSlotsExcludedFromTemplates": 6,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "build-technique-neutral-locked-glyph-template-library-v33"
            if technique_metadata_is_global_or_default
            else "review-technique-signature-specific-template-groups-v33"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked template technique signature audit v32 complete")
    print(f"Locked event slots observed: {len(slots)}")
    print(f"Strict collision-free slots: {len(strict_slots)}")
    print(f"Required fret classes: {required_frets}")
    print(f"Unique technique signatures: {len(signatures)}")
    print(f"Dominant technique signature count: {dominant_count}")
    print(f"Dominant technique signature ratio: {dominant_ratio:.6f}")
    print(f"Dominant signature coverage by fret: {dominant_coverage_by_fret}")
    print(f"Every fret has at least three dominant-signature examples: {every_fret_has_dominant_examples}")
    print(f"Active technique key counts: {dict(active_keys)}")
    print(f"Technique metadata is global/default: {technique_metadata_is_global_or_default}")
    print("Unresolved event slots excluded from templates: 6")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Glyph templates built: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
