"""Audit exactly which V64 tab-system recovery gates reject each row.

Read-only diagnostic. Does not rerun geometry, recognize frets, modify measures
1-16 or V7 events, use audio, or promote anything to production.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "public" / "gomyway-tab-system-band-recovery-v64.json"
OUTPUT = ROOT / "public" / "gomyway-v64-failure-gate-audit-v65.json"

MIN_ROWS_WITH_RUN = 5
MIN_MEAN_RUN = 0.40
MAX_SPACING_DEVIATION = 2.25


def main() -> None:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = []
    gate_counts: Counter[str] = Counter()

    for job in data.get("recognitionJobs", []):
        recovery = job.get("v64TabSystemBandRecovery", {}) or {}
        best = recovery.get("bestCandidate", {}) or {}

        strong_rows = int(best.get("rowsWithStrongHorizontalEvidence", 0) or 0)
        mean_run = float(best.get("meanRunContinuity", 0.0) or 0.0)
        min_run = float(best.get("minimumRunContinuity", 0.0) or 0.0)
        spacing_dev = float(best.get("maximumSpacingDeviationPixels", 999.0) or 999.0)
        margin = float(recovery.get("scoreMargin", 0.0) or 0.0)

        failed = []
        if strong_rows < MIN_ROWS_WITH_RUN:
            failed.append("insufficient-strong-horizontal-rows")
        if mean_run < MIN_MEAN_RUN:
            failed.append("mean-horizontal-run-too-low")
        if spacing_dev > MAX_SPACING_DEVIATION:
            failed.append("spacing-deviation-too-high")
        if not failed and not job.get("v64TabSystemBandRecoveryPassed", False):
            failed.append("unexpected-wrapper-or-metadata-failure")

        gate_counts.update(failed)
        rows.append({
            "page": job.get("page"),
            "row": job.get("row"),
            "measures": job.get("measures", []),
            "passed": bool(job.get("v64TabSystemBandRecoveryPassed", False)),
            "failedGates": failed,
            "rowsWithStrongHorizontalEvidence": strong_rows,
            "meanRunContinuity": round(mean_run, 6),
            "minimumRunContinuity": round(min_run, 6),
            "maximumSpacingDeviationPixels": round(spacing_dev, 6),
            "scoreMargin": round(margin, 6),
            "offsetPixels": best.get("offsetPixels"),
        })

    summary = {
        "diagnosticName": "Gomyway V64 failure gate audit V65",
        "jobsInspected": len(rows),
        "jobsPassed": sum(1 for row in rows if row["passed"]),
        "jobsFailed": sum(1 for row in rows if not row["passed"]),
        "failureGateCounts": dict(gate_counts),
        "lockedMeasures1To16Modified": False,
        "v7EventsModified": False,
        "candidateAudioUsed": False,
        "professionalFretGlyphRecognitionPerformed": False,
        "productionPromotionAllowed": False,
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print("V64 failure gate audit V65 complete")
    print(f"Jobs inspected: {summary['jobsInspected']}")
    print(f"Jobs passed: {summary['jobsPassed']}")
    print(f"Jobs failed: {summary['jobsFailed']}")
    for gate, count in gate_counts.most_common():
        print(f"{gate}: {count}")
    print("Locked measures 1-16 modified: False")
    print("V7 events modified: False")
    print("Candidate audio used: False")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
