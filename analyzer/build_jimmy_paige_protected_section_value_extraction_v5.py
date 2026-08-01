import copy
from pathlib import Path
from typing import Any

import build_jimmy_paige_protected_section_value_extraction as extractor


ORIGINAL_LOAD_JSON = extractor.load_json


def is_professional_reference(path: Path) -> bool:
    resolved = Path(path).resolve()
    return any(resolved == candidate.resolve() for candidate in extractor.REFERENCE_CANDIDATES)


def adapt_professional_reference(payload: Any) -> Any:
    """Return an in-memory copy with global measure identities fixed.

    The verified professional reference stores all 113 measures in the
    top-level `measures` array. Array position is the authoritative global
    measure identity, even when a row contains a stale/local measure field.
    The source JSON on disk is never changed.
    """
    adapted = copy.deepcopy(payload)

    if not isinstance(adapted, dict):
        raise RuntimeError("Professional reference root must be a JSON object")

    measures = adapted.get("measures")
    if not isinstance(measures, list):
        raise RuntimeError("Professional reference is missing top-level measures array")

    if len(measures) < 113:
        raise RuntimeError(
            f"Professional reference has only {len(measures)} measure rows; expected 113"
        )

    for index, measure_row in enumerate(measures[:113]):
        if not isinstance(measure_row, dict):
            raise RuntimeError(
                f"Professional reference measures[{index}] is not an object"
            )

        global_measure = index + 1

        # Remove every recognized stale/local measure identity first so the
        # base extractor cannot select it ahead of the authoritative value.
        stale_keys = [
            key
            for key in measure_row
            if str(key).lower() in extractor.MEASURE_KEYS
        ]
        for key in stale_keys:
            del measure_row[key]

        measure_row["measureNumber"] = global_measure

    return adapted


def load_json_with_reference_adapter(path: Path) -> Any:
    payload = ORIGINAL_LOAD_JSON(path)
    if is_professional_reference(path):
        adapted = adapt_professional_reference(payload)
        print(
            "Professional reference adapter v5: "
            "load_json mapped top-level measures[0..112] to global measures 1..113"
        )
        return adapted
    return payload


def main() -> None:
    extractor.load_json = load_json_with_reference_adapter
    extractor.main()


if __name__ == "__main__":
    main()
