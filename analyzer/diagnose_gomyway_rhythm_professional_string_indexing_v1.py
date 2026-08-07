from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"

MEASURE_START = 17
MEASURE_END = 113


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected object: {path.relative_to(ROOT)}")
    return payload


def integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def candidate_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def measure_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def fret_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("fret"))


def candidate_string(event: dict[str, Any]) -> int | None:
    if "stringIndex" in event:
        return integer(event.get("stringIndex"))
    return integer(event.get("string"))


def reference_string(note: dict[str, Any]) -> int | None:
    return integer(note.get("string"))


def f1(tp: int, predicted: int, expected: int) -> float:
    if predicted == 0 and expected == 0:
        return 1.0
    if predicted == 0 or expected == 0 or tp == 0:
        return 0.0
    precision = tp / predicted
    recall = tp / expected
    return 2.0 * precision * recall / (precision + recall)


def pct(value: float) -> float:
    return round(value * 100.0, 2)


def transform_string(value: int, mode: str) -> int:
    if mode == "raw":
        return value
    if mode == "plus1":
        return value + 1
    if mode == "minus1":
        return value - 1
    if mode == "reverse0based":
        return 6 - value
    if mode == "reverse1based":
        return 7 - value
    raise ValueError(mode)


def main() -> None:
    candidate = load(CANDIDATE_PATH)
    reference = load(REFERENCE_PATH)

    candidate_events = candidate_rows(candidate)
    reference_measures = reference.get("measures")
    if not isinstance(reference_measures, list):
        raise RuntimeError("Professional reference measures missing")

    candidate_string_values: Counter[int] = Counter()
    reference_string_values: Counter[int] = Counter()

    candidate_tokens_by_mode: dict[str, Counter[tuple[int, int, int, int]]] = {
        mode: Counter()
        for mode in ("raw", "plus1", "minus1", "reverse0based", "reverse1based")
    }
    candidate_fret_tokens: Counter[tuple[int, int, int]] = Counter()
    reference_tokens: Counter[tuple[int, int, int, int]] = Counter()
    reference_fret_tokens: Counter[tuple[int, int, int]] = Counter()

    per_measure_candidate: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in candidate_events:
        measure = measure_of(event)
        step = step_of(event)
        string = candidate_string(event)
        fret = fret_of(event)
        if None in (measure, step, string, fret):
            continue
        if not MEASURE_START <= measure <= MEASURE_END:
            continue
        candidate_string_values[string] += 1
        per_measure_candidate[measure].append(event)
        candidate_fret_tokens[(measure, step, fret)] += 1
        for mode, counter in candidate_tokens_by_mode.items():
            counter[(measure, step, transform_string(string, mode), fret)] += 1

    for measure_row in reference_measures:
        if not isinstance(measure_row, dict):
            continue
        measure = integer(measure_row.get("measureNumber"))
        if measure is None or not MEASURE_START <= measure <= MEASURE_END:
            continue
        events = measure_row.get("events")
        if not isinstance(events, list):
            continue
        for event in events:
            if not isinstance(event, dict):
                continue
            step = integer(event.get("quantizedStep"))
            notes = event.get("notes")
            if step is None or not isinstance(notes, list):
                continue
            for note in notes:
                if not isinstance(note, dict):
                    continue
                string = reference_string(note)
                fret = fret_of(note)
                if string is None or fret is None:
                    continue
                reference_string_values[string] += 1
                reference_tokens[(measure, step, string, fret)] += 1
                reference_fret_tokens[(measure, step, fret)] += 1

    print("GOMYWAY RHYTHM PROFESSIONAL STRING INDEXING DIAGNOSTIC V1")
    print("Candidate string values:", dict(sorted(candidate_string_values.items())))
    print("Reference string values:", dict(sorted(reference_string_values.items())))
    print("Candidate note tokens:", sum(candidate_tokens_by_mode["raw"].values()))
    print("Reference note tokens:", sum(reference_tokens.values()))
    print()

    expected = sum(reference_tokens.values())
    for mode, tokens in candidate_tokens_by_mode.items():
        tp = sum((tokens & reference_tokens).values())
        score = f1(tp, sum(tokens.values()), expected)
        print(f"String mapping {mode}: exact note/fret F1={pct(score)} matched={tp}")

    fret_tp = sum((candidate_fret_tokens & reference_fret_tokens).values())
    fret_score = f1(fret_tp, sum(candidate_fret_tokens.values()), sum(reference_fret_tokens.values()))
    print(f"Ignoring string, measure+step+fret F1={pct(fret_score)} matched={fret_tp}")
    print()

    mappings = {}
    for mode, tokens in candidate_tokens_by_mode.items():
        tp = sum((tokens & reference_tokens).values())
        mappings[mode] = f1(tp, sum(tokens.values()), expected)
    best_mode = max(mappings, key=mappings.get)
    raw_score = mappings["raw"]
    best_score = mappings[best_mode]

    indexing_mismatch_suspected = best_mode != "raw" and best_score > raw_score + 0.05
    print("Best mapping:", best_mode)
    print("Raw exact-note F1:", pct(raw_score))
    print("Best exact-note F1:", pct(best_score))
    print("String indexing mismatch suspected:", indexing_mismatch_suspected)

    if indexing_mismatch_suspected:
        print("Recommended next action: normalize grader string coordinates before any professional-grade training")
    elif fret_score > raw_score + 0.05:
        print("Recommended next action: inspect string-position inference; frets align better than full string/fret pairs")
    else:
        print("Recommended next action: professional-grade weakness appears substantive; proceed to targeted training")


if __name__ == "__main__":
    main()
