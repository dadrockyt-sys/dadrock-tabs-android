"""Run the v52 full-song string-line extension with OpenCV shape compatibility.

Some OpenCV builds return HoughLinesP as shape (N, 4) instead of (N, 1, 4).
The original v52 implementation indexed only the latter form. This read-only
runner patches that single iteration expression in memory and executes the same
v52 detector without modifying protected measures or source data.
"""

from __future__ import annotations

from pathlib import Path

SCRIPT = Path(__file__).with_name("extend_gomyway_string_line_geometry_v52.py")


def main() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    old = "for entry in lines[:, 0, :]:"
    new = "for entry in lines.reshape(-1, 4):"

    if old not in source:
        raise RuntimeError(
            "Expected v52 HoughLinesP loop was not found; refusing to run an "
            "unknown script version."
        )

    patched = source.replace(old, new, 1)
    namespace = {
        "__name__": "__main__",
        "__file__": str(SCRIPT),
        "__package__": None,
    }
    exec(compile(patched, str(SCRIPT), "exec"), namespace)


if __name__ == "__main__":
    main()
