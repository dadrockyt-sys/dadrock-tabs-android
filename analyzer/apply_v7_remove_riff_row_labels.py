from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = {
    ROOT / "lib" / "createTabPdf.js": [
        (
            """    if (SECTION_PATTERN.test(trimmed)) {\n      flushRows();\n      pendingSection = trimmed.replace(/[:\\-]+$/, '').toUpperCase();\n      continue;\n    }\n""",
            """    if (SECTION_PATTERN.test(trimmed)) {\n      flushRows();\n      const normalizedSection = trimmed\n        .replace(/[:\\-]+$/, '')\n        .toUpperCase();\n      pendingSection = /^RIFF(?:\\s+\\d+)?$/i.test(normalizedSection)\n        ? ''\n        : normalizedSection;\n      continue;\n    }\n""",
        ),
    ],
    ROOT / "lib" / "createTabPdfPolished.js": [
        (
            """    if (SECTION_PATTERN.test(trimmed)) {\n      if (currentRows === expectedRows) {\n        systems.push(pendingSection);\n      }\n      currentRows = 0;\n      pendingSection = true;\n      continue;\n    }\n""",
            """    if (SECTION_PATTERN.test(trimmed)) {\n      if (currentRows === expectedRows) {\n        systems.push(pendingSection);\n      }\n      currentRows = 0;\n      pendingSection = !/^RIFF(?:\\s+\\d+)?$/i.test(\n        trimmed.replace(/[:\\-]+$/, '')\n      );\n      continue;\n    }\n""",
        ),
    ],
    ROOT / "lib" / "v7MeasureGridOverlay.js": [
        (
            """    if (SECTION_PATTERN.test(trimmed)) {\n      if (currentRows === expectedRows) systems.push(pendingSection);\n      currentRows = 0;\n      pendingSection = true;\n      continue;\n    }\n""",
            """    if (SECTION_PATTERN.test(trimmed)) {\n      if (currentRows === expectedRows) systems.push(pendingSection);\n      currentRows = 0;\n      pendingSection = !/^RIFF(?:\\s+\\d+)?$/i.test(\n        trimmed.replace(/[:\\-]+$/, '')\n      );\n      continue;\n    }\n""",
        ),
    ],
}


def apply_replacement(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")

    if new in text:
        print(f"PASS already updated: {path.relative_to(ROOT)}")
        return

    if old not in text:
        raise RuntimeError(
            f"Expected protected block not found in {path.relative_to(ROOT)}"
        )

    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"PASS updated: {path.relative_to(ROOT)}")


def main() -> None:
    for path, replacements in TARGETS.items():
        if not path.exists():
            raise FileNotFoundError(path)
        for old, new in replacements:
            apply_replacement(path, old, new)

    print()
    print("V7 redundant RIFF row labels removed successfully 💚")
    print("INTRO, VERSE, CHORUS, SOLO, BRIDGE, OUTRO, and other real section labels remain available.")
    print("Measure numbers, six-measure rows, chords, techniques, bends, spacing, and branding remain unchanged.")


if __name__ == "__main__":
    main()
