from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    ROOT / "lib" / "createTabPdfPolished.js": [
        ("const firstPageTop = 578;", "const firstPageTop = 566;"),
        ("    y: 585,\n    size: 10,", "    y: 592,\n    size: 10,"),
        ("    y: 585,\n    size: settingsSize,", "    y: 592,\n    size: settingsSize,"),
    ],
    ROOT / "lib" / "v7MeasureGridOverlay.js": [
        ("const firstPageTop = 578;", "const firstPageTop = 566;"),
    ],
}


def apply_replacements(path: Path, replacements: list[tuple[str, str]]) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    source = path.read_text(encoding="utf-8")
    updated = source

    for old, new in replacements:
        if new in updated:
            continue
        if old not in updated:
            raise RuntimeError(
                f"Expected source block not found in {path.relative_to(ROOT)}:\n{old}"
            )
        updated = updated.replace(old, new, 1)

    if updated != source:
        path.write_text(updated, encoding="utf-8")


def main() -> None:
    for path, replacements in FILES.items():
        apply_replacements(path, replacements)

    print("V7 polished PDF header clearance applied successfully 💚")
    print("Protected: logo, song/artist metadata, six-measure grid, bends, chords, and analyzer output.")
    print("LEAD and Standard Tuning / 4/4 / BPM now sit above the first notation row.")


if __name__ == "__main__":
    main()
