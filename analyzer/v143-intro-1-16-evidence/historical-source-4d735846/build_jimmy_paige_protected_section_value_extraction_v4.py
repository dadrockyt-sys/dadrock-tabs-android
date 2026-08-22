import copy
from pathlib import Path
from typing import Any

import build_jimmy_paige_protected_section_value_extraction as extractor


ORIGINAL_LOAD_JSON = extractor.load_json
REFERENCE_FILENAMES = {
    "gomyway-professional-rhythm-reference-v2.json",
    "gomyway-professional-rhythm-reference.json",
}


def normalize_professional_reference(value: Any) -> Any:
    """Map the professional top-level measures array to global measures 1..113.

    The source contains measure rows whose existing measure labels can be local
    to a section. The authoritative full-song identity is the top-level array
    position demonstrated by the structure diagnostic:

        root.measures[0]   -> global measure 1
        root.measures[112] -> global measure 113

    This function changes only an in-memory copy. The JSON on disk is untouched.
    """
    adapted = copy.deepcopy(value)

    if not isinstance(adapted, dict):
        return adapted

    measures = adapted.get("measures")
    if not isinstance(measures, list):
        return adapted

    for index, row in enumerate(measures[:113]):
        if not isinstance(row, dict):
            continue

        global_measure = index + 1

        # Override every recognized explicit measure key so insertion order
        # cannot cause a stale section-local value to win during extraction.
        for key in list(row.keys()):
            if str(key).lower() in extractor.MEASURE_KEYS:
                row[key] = global_measure

        row["measureNumber"] = global_measure

    return adapted


def load_json_with_global_professional_measures(path: Path) -> Any:
    payload = ORIGINAL_LOAD_JSON(path)
    if path.name in REFERENCE_FILENAMES:
        return normalize_professional_reference(payload)
    return payload


def main() -> None:
    extractor.load_json = load_json_with_global_professional_measures
    print(
        "Professional reference adapter v4: "
        "top-level measures[index] forced to global measure index + 1"
    )
    extractor.main()


if __name__ == "__main__":
    main()
