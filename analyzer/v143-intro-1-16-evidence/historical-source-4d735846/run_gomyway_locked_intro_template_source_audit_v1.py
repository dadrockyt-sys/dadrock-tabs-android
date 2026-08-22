from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-locked-intro-template-source-audit-v1.json"

TARGET_SLOT_COUNT = 12
TARGET_OFFSET = 12


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def scalar_matches_offset(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return int(value) == TARGET_OFFSET
    if isinstance(value, str):
        try:
            return int(float(value.strip())) == TARGET_OFFSET
        except ValueError:
            return False
    return False


def looks_like_slot(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return 0 <= float(value) <= 32
    if isinstance(value, str):
        lowered = value.lower()
        return any(token in lowered for token in ("attack", "rest", "tie", "sustain", "slot", "onset"))
    if isinstance(value, dict):
        keys = {str(key).lower() for key in value.keys()}
        return bool(keys & {
            "step",
            "slot",
            "quantizedstep",
            "attack",
            "onset",
            "rest",
            "tie",
            "sustain",
            "durationsteps",
        })
    return False


def slot_array_score(rows: list[Any], key_name: str) -> int:
    score = 0
    lowered = key_name.lower()
    if len(rows) == TARGET_SLOT_COUNT:
        score += 10
    if all(looks_like_slot(row) for row in rows):
        score += 4
    if any(token in lowered for token in ("intro", "rhythm", "template", "canonical", "slot", "pattern")):
        score += 6
    if any(token in lowered for token in ("locked", "protected", "consensus")):
        score += 3
    return score


def summarize(value: Any) -> Any:
    if isinstance(value, list):
        return value[:20]
    if isinstance(value, dict):
        return {key: value[key] for key in list(value.keys())[:20]}
    return value


def walk(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield child_path, key, child
            yield from walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, str(index), child
            yield from walk(child, child_path)


def analyze_file(path: Path) -> dict[str, Any] | None:
    payload = load_json(path)
    if payload is None:
        return None

    slot_candidates: list[dict[str, Any]] = []
    offset_matches: list[dict[str, Any]] = []
    intro_mentions: list[str] = []

    for json_path, key, value in walk(payload):
        lowered_path = json_path.lower()
        if "intro" in lowered_path:
            intro_mentions.append(json_path)

        if scalar_matches_offset(value) and any(
            token in lowered_path
            for token in ("offset", "orientation", "phase", "shift", "alignment")
        ):
            offset_matches.append({"jsonPath": json_path, "value": value})

        if isinstance(value, list) and len(value) == TARGET_SLOT_COUNT:
            score = slot_array_score(value, key)
            slot_candidates.append(
                {
                    "jsonPath": json_path,
                    "score": score,
                    "length": len(value),
                    "preview": summarize(value),
                }
            )

    slot_candidates.sort(key=lambda item: item["score"], reverse=True)
    if not slot_candidates and not offset_matches:
        return None

    best_slot_score = slot_candidates[0]["score"] if slot_candidates else 0
    return {
        "file": str(path.relative_to(REPO_ROOT)),
        "bestSlotScore": best_slot_score,
        "slotCandidates": slot_candidates[:20],
        "offsetMatches": offset_matches[:20],
        "introMentions": intro_mentions[:20],
        "likelyLockedIntroSource": bool(best_slot_score >= 14 and offset_matches),
    }


def main() -> None:
    records: list[dict[str, Any]] = []
    files_examined = 0

    for path in sorted(PUBLIC_DIR.rglob("*.json")):
        if path == OUTPUT_PATH:
            continue
        files_examined += 1
        record = analyze_file(path)
        if record is not None:
            records.append(record)

    records.sort(
        key=lambda item: (
            item["likelyLockedIntroSource"],
            item["bestSlotScore"],
            len(item["offsetMatches"]),
        ),
        reverse=True,
    )

    selected = records[0] if records else None
    selected_ready = bool(
        selected
        and selected["bestSlotScore"] >= 14
        and len(selected["offsetMatches"]) > 0
    )

    report = {
        "schemaVersion": 1,
        "auditType": "locked-intro-template-source",
        "targetSlotCount": TARGET_SLOT_COUNT,
        "targetOrientationOffset": TARGET_OFFSET,
        "filesExamined": files_examined,
        "candidateFiles": len(records),
        "selectedCandidate": selected,
        "candidates": records[:50],
        "readyForIntroAttackReconstruction": selected_ready,
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Locked intro-template source audit V1 complete")
    print("Files examined:", files_examined)
    print("Candidate files:", len(records))
    print("Selected candidate:", selected["file"] if selected else None)
    print("Best 12-slot score:", selected["bestSlotScore"] if selected else 0)
    print("Offset-12 matches:", len(selected["offsetMatches"]) if selected else 0)
    print("Ready for intro attack reconstruction:", selected_ready)

    if selected:
        print()
        print("Selected 12-slot candidates:")
        for item in selected["slotCandidates"][:5]:
            print(" ", item["jsonPath"], "score=", item["score"], "length=", item["length"])
        print("Selected offset matches:")
        for item in selected["offsetMatches"][:5]:
            print(" ", item["jsonPath"], "value=", item["value"])

    print()
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
