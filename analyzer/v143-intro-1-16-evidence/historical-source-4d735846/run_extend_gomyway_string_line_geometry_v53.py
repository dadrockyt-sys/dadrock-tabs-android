"""Run the proven v45 detector over measures 17-113 with full spacing support.

V52 exposed two implementation limits rather than a failure of the v45 method:
1. OpenCV may return HoughLinesP as either (N, 1, 4) or (N, 4).
2. The approved locked spacing is 18.4 px, but v52 only searched and accepted
   spacings through 18.0 px.

This read-only runner keeps the v45 evidence model unchanged, fixes those two
limits, writes separate v53 outputs, and does not modify measures 1-16.
"""

from __future__ import annotations

from pathlib import Path

SCRIPT = Path(__file__).with_name("extend_gomyway_string_line_geometry_v52.py")


def replace_once(source: str, old: str, new: str) -> str:
    if old not in source:
        raise RuntimeError(f"Expected source fragment not found: {old!r}")
    return source.replace(old, new, 1)


def main() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    source = replace_once(
        source,
        'OUTPUT = PUBLIC / "gomyway-full-song-string-line-geometry-v52.json"',
        'OUTPUT = PUBLIC / "gomyway-full-song-string-line-geometry-v53.json"',
    )
    source = replace_once(
        source,
        'PREVIEW_DIR = PUBLIC / "gomyway-full-song-string-line-geometry-v52"',
        'PREVIEW_DIR = PUBLIC / "gomyway-full-song-string-line-geometry-v53"',
    )
    source = replace_once(source, "for spacing_step in range(8, 37):", "for spacing_step in range(8, 49):")
    source = replace_once(source, "if spacing < 4.0 or spacing > 18.0:", "if spacing < 4.0 or spacing > 24.0:")
    source = replace_once(source, "for entry in lines[:, 0, :]:", "for entry in lines.reshape(-1, 4):")
    source = replace_once(source, "5.0 <= spacing <= 18.0", "5.0 <= spacing <= 24.0")
    source = source.replace(
        '"Gomyway full-song v45-method string-line geometry v52"',
        '"Gomyway full-song v45-method string-line geometry v53"',
    )
    source = source.replace(
        '"human-review-v52-full-song-v45-method-previews"',
        '"human-review-v53-full-song-v45-method-previews"',
    )
    source = source.replace(
        '"inspect-v52-v45-method-geometry-failures-v53"',
        '"inspect-v53-v45-method-geometry-failures-v54"',
    )
    source = source.replace(
        'Full-song v45-method string-line geometry extension v52',
        'Full-song v45-method string-line geometry extension v53',
    )

    namespace = {
        "__name__": "__main__",
        "__file__": str(SCRIPT),
        "__package__": None,
    }
    exec(compile(source, str(SCRIPT), "exec"), namespace)


if __name__ == "__main__":
    main()
