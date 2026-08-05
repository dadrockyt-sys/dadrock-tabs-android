from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-v8-notation-projection-source-audit-v1.json"
READY_PATH = PUBLIC_DIR / "gomyway-full-song-review-evidence-merge-v1.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path.relative_to(REPO_ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected JSON object: {path.relative_to(REPO_ROOT)}")
    return value


def inspect_payload(path: Path, payload: dict[str, Any]) -> dict[str, Any] | None:
    metadata = payload.get("notationMetadata")
    if not isinstance(metadata, dict):
        return None
    markers = metadata.get("allMarkers")
    if not isinstance(markers, list):
        return None

    marker_types = sorted(
        {
            str(marker.get("type"))
            for marker in markers
            if isinstance(marker, dict) and marker.get("type") is not None
        }
    )
    event_linked = sum(
        1
        for marker in markers
        if isinstance(marker, dict)
        and ("eventIndex" in marker or bool(marker.get("eventIndices")))
    )
    starts = [
        float(marker.get("start"))
        for marker in markers
        if isinstance(marker, dict) and isinstance(marker.get("start"), (int, float))
    ]
    ends = [
        float(marker.get("end"))
        for marker in markers
        if isinstance(marker, dict) and isinstance(marker.get("end"), (int, float))
    ]

    name = path.name.lower()
    score = 0
    if "v8" in name:
        score += 6
    if "full-song" in name:
        score += 4
    if "notation" in name:
        score += 4
    if "metadata" in name or "projection" in name:
        score += 3
    if payload.get("passed") is True:
        score += 2
    if payload.get("protectedBaselinesChanged") is False:
        score += 1
    if len(markers) > 0:
        score += 2

    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "score": score,
        "projectionType": payload.get("projectionType"),
        "passed": payload.get("passed"),
        "protectedBaselinesChanged": payload.get("protectedBaselinesChanged"),
        "songDuration": payload.get("songDuration"),
        "markerCount": len(markers),
        "eventLinkedMarkerCount": event_linked,
        "markerTypes": marker_types,
        "firstMarkerStart": min(starts) if starts else None,
        "lastMarkerEnd": max(ends) if ends else None,
    }


def main() -> None:
    ready = load_json(READY_PATH)
    full_song_ready = bool(ready.get("readyForProtectedPdfComparison"))

    candidates: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []
    for path in sorted(PUBLIC_DIR.glob("gomyway*.json")):
        if path == OUTPUT_PATH:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            parse_errors.append({
                "path": str(path.relative_to(REPO_ROOT)),
                "error": f"{type(exc).__name__}: {exc}",
            })
            continue
        if not isinstance(payload, dict):
            continue
        record = inspect_payload(path, payload)
        if record is not None:
            candidates.append(record)

    candidates.sort(
        key=lambda item: (
            int(item.get("score") or 0),
            int(item.get("markerCount") or 0),
            item.get("path", ""),
        ),
        reverse=True,
    )

    selected = candidates[0] if candidates else None
    selected_is_v8 = bool(selected and "v8" in selected["path"].lower())
    selected_green = bool(
        selected
        and selected.get("passed") is True
        and selected.get("protectedBaselinesChanged") is False
        and int(selected.get("markerCount") or 0) > 0
    )
    ready_for_v8_binding = bool(full_song_ready and selected_is_v8 and selected_green)

    report = {
        "schemaVersion": 1,
        "auditType": "v8-notation-projection-source",
        "fullSongReadyForComparison": full_song_ready,
        "candidateCount": len(candidates),
        "selectedProjection": selected,
        "selectedProjectionIsV8": selected_is_v8,
        "selectedProjectionGreen": selected_green,
        "readyForV8LayoutBinding": ready_for_v8_binding,
        "candidates": candidates[:40],
        "parseErrors": parse_errors,
        "interpretation": (
            "A true V8 notation PDF must be built from a green V8 notation-metadata projection, "
            "then passed through the protected read-only layout binding and proof renderer. A V7 "
            "projection may validate the renderer but cannot validate the reviewed V8 rhythm content."
        ),
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("V8 notation-projection source audit V1 complete")
    print("Full-song ready for comparison:", full_song_ready)
    print("Projection candidates:", len(candidates))
    print("Selected projection:", selected["path"] if selected else None)
    print("Selected projection is V8:", selected_is_v8)
    print("Selected projection green:", selected_green)
    print("Ready for V8 layout binding:", ready_for_v8_binding)
    print()
    print("Top projection candidates:")
    for item in candidates[:10]:
        print(
            " ",
            item["path"],
            f"score={item['score']}",
            f"markers={item['markerCount']}",
            f"passed={item['passed']}",
        )
    print()
    print("Automatic promotion allowed: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
