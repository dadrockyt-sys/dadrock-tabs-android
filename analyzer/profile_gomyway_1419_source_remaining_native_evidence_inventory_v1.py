from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import benchmark_gomyway_1419_champion_cached_repeatable_residual_joint_gate_v1 as bench

v2 = bench.v2
recall = bench.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-source-remaining-native-evidence-inventory-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-source-remaining-native-evidence-inventory-v1-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return repr(value)


def shape(value: Any) -> str:
    if value is None:
        return "none"
    if isinstance(value, dict):
        return "dict:" + ",".join(sorted(str(k) for k in value.keys()))
    if isinstance(value, list):
        return f"list:{len(value)}"
    if isinstance(value, tuple):
        return f"tuple:{len(value)}"
    return type(value).__name__


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    source_counts: Counter[str] = Counter()
    source_starts_presence = 0
    source_starts_shapes: Counter[str] = Counter()
    source_starts_values: Counter[str] = Counter()
    source_starts_lengths: Counter[int] = Counter()

    techniques_presence = 0
    techniques_shapes: Counter[str] = Counter()
    techniques_values: Counter[str] = Counter()
    techniques_lengths: Counter[int] = Counter()

    intro_recovery_presence = 0
    intro_recovery_shapes: Counter[str] = Counter()
    intro_recovery_values: Counter[str] = Counter()

    intro_blinding_presence = 0
    intro_blinding_shapes: Counter[str] = Counter()
    intro_blinding_values: Counter[str] = Counter()

    for event in events:
        source_counts[str(event.get("source", "<missing>"))] += 1

        if "sourceStarts" in event:
            source_starts_presence += 1
            value = event.get("sourceStarts")
            source_starts_shapes[shape(value)] += 1
            source_starts_values[norm(value)] += 1
            if isinstance(value, (list, tuple, dict, str)):
                source_starts_lengths[len(value)] += 1

        if "techniques" in event:
            techniques_presence += 1
            value = event.get("techniques")
            techniques_shapes[shape(value)] += 1
            techniques_values[norm(value)] += 1
            if isinstance(value, (list, tuple, dict, str)):
                techniques_lengths[len(value)] += 1

        if "introRecovery" in event:
            intro_recovery_presence += 1
            value = event.get("introRecovery")
            intro_recovery_shapes[shape(value)] += 1
            intro_recovery_values[norm(value)] += 1

        if "introBlinding" in event:
            intro_blinding_presence += 1
            value = event.get("introBlinding")
            intro_blinding_shapes[shape(value)] += 1
            intro_blinding_values[norm(value)] += 1

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during remaining native evidence inventory")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-source-remaining-native-evidence-inventory",
        "protectedEventCount": len(events),
        "sourceCounts": dict(source_counts.most_common()),
        "sourceStarts": {
            "presence": source_starts_presence,
            "shapes": dict(source_starts_shapes.most_common()),
            "lengths": dict(source_starts_lengths.most_common()),
            "topValues": dict(source_starts_values.most_common(20)),
        },
        "techniques": {
            "presence": techniques_presence,
            "shapes": dict(techniques_shapes.most_common()),
            "lengths": dict(techniques_lengths.most_common()),
            "topValues": dict(techniques_values.most_common(30)),
        },
        "introRecovery": {
            "presence": intro_recovery_presence,
            "shapes": dict(intro_recovery_shapes.most_common()),
            "topValues": dict(intro_recovery_values.most_common(20)),
        },
        "introBlinding": {
            "presence": intro_blinding_presence,
            "shapes": dict(intro_blinding_shapes.most_common()),
            "topValues": dict(intro_blinding_values.most_common(20)),
        },
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "not-used-in-inventory",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 SOURCE REMAINING NATIVE EVIDENCE INVENTORY V1")
    print("Passed: True")
    print("Protected event count:", len(events))
    print("Source counts:", output["sourceCounts"])
    print("sourceStarts presence:", source_starts_presence)
    print("sourceStarts shapes:", output["sourceStarts"]["shapes"])
    print("sourceStarts lengths:", output["sourceStarts"]["lengths"])
    print("sourceStarts top values:", output["sourceStarts"]["topValues"])
    print("techniques presence:", techniques_presence)
    print("techniques shapes:", output["techniques"]["shapes"])
    print("techniques lengths:", output["techniques"]["lengths"])
    print("techniques top values:", output["techniques"]["topValues"])
    print("introRecovery presence:", intro_recovery_presence)
    print("introRecovery shapes:", output["introRecovery"]["shapes"])
    print("introRecovery top values:", output["introRecovery"]["topValues"])
    print("introBlinding presence:", intro_blinding_presence)
    print("introBlinding shapes:", output["introBlinding"]["shapes"])
    print("introBlinding top values:", output["introBlinding"]["topValues"])
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
