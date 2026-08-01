import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

REFERENCE_CANDIDATES = [
    PUBLIC / "gomyway-professional-rhythm-reference-v2.json",
    PUBLIC / "gomyway-professional-rhythm-reference.json",
]

INTERESTING_TOKENS = (
    "measure",
    "bar",
    "section",
    "event",
    "note",
    "attack",
    "timing",
    "duration",
    "technique",
    "pitch",
    "fret",
    "string",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def describe(value: Any) -> str:
    if isinstance(value, dict):
        return f"dict[{len(value)}]"
    if isinstance(value, list):
        return f"list[{len(value)}]"
    return type(value).__name__


def main() -> None:
    reference_path = next((path for path in REFERENCE_CANDIDATES if path.exists()), None)
    if reference_path is None:
        raise FileNotFoundError("No professional rhythm reference JSON found")

    payload = load_json(reference_path)
    print("Professional reference structure diagnostic")
    print(f"Reference: {reference_path.relative_to(ROOT)}")
    print(f"Root type: {describe(payload)}")

    if isinstance(payload, dict):
        print("Root keys:")
        for key, value in payload.items():
            print(f"  {key}: {describe(value)}")

    print("\nInteresting containers and sample paths:")
    emitted = 0

    def walk(value: Any, path: str = "root", depth: int = 0) -> None:
        nonlocal emitted
        if emitted >= 160 or depth > 10:
            return

        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{path}.{key}"
                lowered = str(key).lower()
                if any(token in lowered for token in INTERESTING_TOKENS):
                    print(f"  {child_path}: {describe(child)}")
                    if isinstance(child, (str, int, float, bool)) or child is None:
                        print(f"    value={child!r}")
                    emitted += 1
                    if emitted >= 160:
                        return
                walk(child, child_path, depth + 1)
        elif isinstance(value, list):
            for index, child in enumerate(value[:8]):
                walk(child, f"{path}[{index}]", depth + 1)

    walk(payload)

    print(f"\nDiagnostic paths printed: {emitted}")
    print("No files changed. Production remains disabled.")


if __name__ == "__main__":
    main()
