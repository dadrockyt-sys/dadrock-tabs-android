from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-notation.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-v8-notation-identity-schema.json"


def walk(value: Any, path: str = "$"):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]")


def safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(
            "Missing public/gomyway-full-song-v8-notation.json. "
            "Run the existing V8 notation benchmark that creates it first."
        )

    document = json.loads(SOURCE_PATH.read_text())
    identity_nodes: list[dict[str, Any]] = []
    key_histogram: Counter[str] = Counter()
    measure_values: list[int] = []

    for path, node in walk(document):
        if "stringIndex" not in node or "fret" not in node:
            continue
        string_index = safe_int(node.get("stringIndex"))
        fret = safe_int(node.get("fret"))
        if string_index is None or fret is None:
            continue

        key_histogram.update(node.keys())
        measure = None
        for key in ("measureNumber", "measure", "barNumber", "bar"):
            candidate = safe_int(node.get(key))
            if candidate is not None:
                measure = candidate
                measure_values.append(candidate)
                break

        identity_nodes.append(
            {
                "path": path,
                "stringIndex": string_index,
                "fret": fret,
                "measureNumber": measure,
                "availableKeys": sorted(node.keys()),
                "timingFields": {
                    key: node.get(key)
                    for key in (
                        "start", "startTime", "start_time", "time", "position",
                        "positionInMeasure", "quantizedStep", "step", "duration",
                        "durationSteps", "end", "endTime"
                    )
                    if key in node
                },
            }
        )

    sample_nodes = identity_nodes[:20]
    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-notation-identity-schema-inspection",
        "passed": bool(identity_nodes),
        "source": str(SOURCE_PATH.relative_to(REPO_ROOT)),
        "identityNodeCount": len(identity_nodes),
        "measureRange": (
            [min(measure_values), max(measure_values)] if measure_values else None
        ),
        "nodesWithDirectMeasureNumber": len(measure_values),
        "commonIdentityNodeKeys": key_histogram.most_common(30),
        "sampleIdentityNodes": sample_nodes,
        "readOnly": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "nextStep": (
            "Use the discovered timing and measure fields to join protected V8 rhythm "
            "onsets with protected notation string/fret identities without modifying either source."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("V8 notation identity schema pass:", report["passed"])
    print("Identity nodes found:", len(identity_nodes))
    print("Nodes with direct measure number:", len(measure_values))
    print("Measure range:", report["measureRange"])
    print("Most common keys:", report["commonIdentityNodeKeys"][:12])
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
