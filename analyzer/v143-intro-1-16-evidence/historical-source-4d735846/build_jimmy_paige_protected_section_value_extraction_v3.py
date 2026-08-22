import copy
from typing import Any

import build_jimmy_paige_protected_section_value_extraction as extractor


ORIGINAL_COLLECT = extractor.collect_measure_values


def add_measure_numbers(value: Any) -> Any:
    """Return a copy with index-based measure numbers added to measures arrays.

    The professional rhythm reference stores its song as:
        root.measures[0].events[...]  -> measure 1
        root.measures[1].events[...]  -> measure 2
        ...

    The original protected extractor intentionally requires a grounded measure
    identity. This adapter converts that known array position into an explicit
    measureNumber without changing the source JSON on disk.
    """
    adapted = copy.deepcopy(value)

    def walk(item: Any) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                lowered = str(key).lower()
                if lowered in {"measures", "bars"} and isinstance(child, list):
                    for index, measure_row in enumerate(child):
                        measure_number = index + 1
                        if measure_number > 113:
                            break
                        if isinstance(measure_row, dict):
                            has_explicit_measure = any(
                                str(existing_key).lower() in extractor.MEASURE_KEYS
                                for existing_key in measure_row
                            )
                            if not has_explicit_measure:
                                measure_row["measureNumber"] = measure_number
                        walk(measure_row)
                else:
                    walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)

    walk(adapted)
    return adapted


def collect_measure_values_with_indexed_measures(value: Any):
    return ORIGINAL_COLLECT(add_measure_numbers(value))


def main() -> None:
    extractor.collect_measure_values = collect_measure_values_with_indexed_measures
    print("Professional reference adapter: measures[index] -> measureNumber index + 1")
    extractor.main()


if __name__ == "__main__":
    main()
