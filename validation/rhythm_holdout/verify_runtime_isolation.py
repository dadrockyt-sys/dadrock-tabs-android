#!/usr/bin/env python3
"""Static guard preventing professional holdout material from entering Rhythm runtime.

Historical benchmark scripts are deliberately outside this scan. The guard covers the
production analyzer/PDF path used by the final scored run and fails on imports/reads of
holdout or known historical human-reference fixtures.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_RUNTIME_FILES = [
    "analyzer/modal_analyzer.py",
    "analyzer/modal_analyzer_v7.py",
    "analyzer/production_chord_diagnostics.py",
    "app/api/analyze-audio-tab/route.js",
    "lib/jimmyPaigeAnalysisPayload.js",
    "lib/v143RenderContract.js",
    "lib/createAiTabPdf.js",
    "lib/createV143RhythmPdf.js",
    "lib/createJimmyPaigeProfessionalPdf.js",
]

FORBIDDEN_TOKENS = [
    "validation/rhythm_holdout/reference",
    "rhythm_holdout/reference",
    "gomyway2_full_tab_reference.json",
    "gomyway_full_chord_sustain_reference.json",
    "modal_analyzer_v7_human_reference_benchmark",
    "modal_gomyway2_full_reference_benchmark",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--runtime-file", action="append", default=[])
    args = parser.parse_args()

    repo = args.repo.resolve()
    paths = args.runtime_file or DEFAULT_RUNTIME_FILES
    findings: list[dict[str, object]] = []
    checked: list[str] = []

    for relative in paths:
        path = (repo / relative).resolve()
        try:
            path.relative_to(repo)
        except ValueError as exc:
            raise ValueError(f"runtime file escapes repository: {relative}") from exc
        if not path.is_file():
            findings.append({"path": relative, "problem": "missing-runtime-file"})
            continue
        checked.append(relative)
        text = path.read_text(encoding="utf-8", errors="replace")
        lowered = text.lower()
        for token in FORBIDDEN_TOKENS:
            if token.lower() in lowered:
                findings.append({"path": relative, "problem": "forbidden-reference-token", "token": token})

    report = {
        "schemaVersion": 1,
        "instrument": "rhythm",
        "checkedRuntimeFiles": checked,
        "forbiddenTokens": FORBIDDEN_TOKENS,
        "findingCount": len(findings),
        "findings": findings,
        "professionalHoldoutRuntimeAccessible": bool(findings),
        "passed": not findings,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
