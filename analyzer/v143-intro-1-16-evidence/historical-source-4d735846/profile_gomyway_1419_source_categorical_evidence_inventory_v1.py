from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1419_champion_cached_repeatable_residual_joint_gate_v1 as bench

v2 = bench.v2
recall = bench.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-source-categorical-evidence-inventory-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-source-categorical-evidence-inventory-v1-manifest.json"

FIELDS = [
    "source",
    "sourceStar",
    "techniques",
    "introBlinding",
    "introRecovery",
    "section",
    "timeSignature",
    "tempoBpm",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return repr(value)


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    field_counts: dict[str, Counter[str]] = {field: Counter() for field in FIELDS}
    field_presence: Counter[str] = Counter()
    top_keys: Counter[str] = Counter()
    source_key_presence: dict[str, Counter[str]] = defaultdict(Counter)

    for event in events:
        source = str(event.get("source", "<missing>"))
        for key in event.keys():
            top_keys[str(key)] += 1
            source_key_presence[source][str(key)] += 1

        for field in FIELDS:
            if field in event:
                field_presence[field] += 1
                field_counts[field][normalized(event.get(field))] += 1

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during categorical evidence inventory")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-source-categorical-evidence-inventory",
        "protectedEventCount": len(events),
        "fieldPresence": dict(field_presence),
        "fieldCounts": {
            field: dict(counter.most_common(30)) for field, counter in field_counts.items()
        },
        "topEventKeys": dict(top_keys.most_common(40)),
        "sourceKeyPresence": {
            source: dict(counter.most_common(40))
            for source, counter in source_key_presence.items()
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

    print("GOMYWAY 14.19 SOURCE CATEGORICAL EVIDENCE INVENTORY V1")
    print("Passed: True")
    print("Protected event count:", len(events))
    print("Field presence:", output["fieldPresence"])
    for field in FIELDS:
        print(f"{field} counts:", output["fieldCounts"][field])
    print("Top event keys:", output["topEventKeys"])
    print("Source key presence:", output["sourceKeyPresence"])
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
