#!/usr/bin/env python3
"""Run the mandatory final Rhythm holdout gate in fail-closed order.

This wrapper makes it difficult to accidentally score a partial professional reference.
It first runs the strict completeness verifier (which itself validates the frozen/PDF
identity before opening the reference), then runs the professional scorer, and finally
binds both reports to the same frozen event hash and the same immutable reference bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent


def load_json(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_checked(args: list[str]) -> None:
    completed = subprocess.run(args, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("freeze_dir", type=Path)
    parser.add_argument("reference_json", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--minimum", type=float, default=0.99)
    args = parser.parse_args()

    freeze_dir = args.freeze_dir.resolve()
    reference_json = args.reference_json.resolve()
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else freeze_dir / "final-holdout"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    completeness_path = output_dir / "rhythm-reference-completeness.json"
    score_path = output_dir / "rhythm-professional-holdout-score.json"
    final_path = output_dir / "rhythm-final-holdout-gate.json"

    # The completeness verifier is intentionally first: it validates the frozen
    # analysis/PDF safety gate before it opens the professional reference.
    run_checked(
        [
            sys.executable,
            str(HERE / "verify_reference_completeness.py"),
            str(freeze_dir),
            str(reference_json),
            "--output",
            str(completeness_path),
        ]
    )

    completeness = load_json(completeness_path)
    if completeness.get("passed") is not True:
        raise SystemExit("reference completeness verifier did not pass")

    # Reference access is now authorized. Bind the exact bytes accepted by the
    # completeness verifier before invoking the scorer, then hash again after
    # scoring to fail closed on any concurrent or accidental reference change.
    completeness_reference_hash = str(completeness.get("referenceJsonSha256") or "")
    reference_hash_before_score = sha256_file(reference_json)
    if (
        len(completeness_reference_hash) != 64
        or reference_hash_before_score != completeness_reference_hash
    ):
        raise SystemExit(
            "professional reference changed after completeness verification and before scoring"
        )

    run_checked(
        [
            sys.executable,
            str(HERE / "score_rhythm_holdout.py"),
            str(freeze_dir),
            str(reference_json),
            "--output",
            str(score_path),
            "--minimum",
            str(args.minimum),
        ]
    )

    reference_hash_after_score = sha256_file(reference_json)
    score = load_json(score_path)
    frozen_hash = str(completeness.get("frozenEventSha256") or "")
    pdf_hash = str(completeness.get("pdfEventSha256") or "")
    score_frozen_hash = str(score.get("frozenEventSha256") or "")
    score_pdf_hash = str(score.get("pdfEventSha256") or "")

    checks = {
        "referenceCompletenessPassed": completeness.get("passed") is True,
        "referenceComplete": completeness.get("referenceComplete") is True,
        "sourceComplete": completeness.get("sourceComplete") is True,
        "contiguousMeasureCoverage": completeness.get("contiguousMeasureCoverage") is True,
        "referenceOpenedOnlyAfterFreezeValidation": completeness.get("referenceOpenedOnlyAfterFreezeValidation") is True,
        "v143RuntimeSafetyVerified": completeness.get("v143RuntimeSafetyVerified") is True,
        "runtimeLabelsNotRequired": completeness.get("runtimeLabelsRequired") is False,
        "referenceHashMatchesCompletenessBeforeScore": bool(completeness_reference_hash)
        and reference_hash_before_score == completeness_reference_hash,
        "referenceUnchangedDuringProfessionalScore": reference_hash_after_score
        == reference_hash_before_score,
        "professionalScorePassed": score.get("rhythmComplete") is True,
        "near100ProfessionalGatePassed": score.get("near100ProfessionalGatePassed") is True,
        "zeroCriticalMismatches": int(score.get("criticalMismatchCount") or 0) == 0,
        "pdfEventFidelityExact": float(score.get("pdfEventFidelity") or 0.0) == 1.0,
        "sameFrozenHashAcrossCompletenessAndScore": bool(frozen_hash) and frozen_hash == score_frozen_hash,
        "samePdfHashAcrossCompletenessAndScore": bool(pdf_hash) and pdf_hash == score_pdf_hash,
        "frozenAndPdfHashesIdentical": bool(frozen_hash) and frozen_hash == pdf_hash,
        "professionalReferenceUsedByAnalyzer": score.get("professionalReferenceUsedByAnalyzer") is False,
        "referenceRuntimeInputUsed": score.get("referenceRuntimeInputUsed") is False,
    }
    failed = [name for name, passed in checks.items() if not passed]

    report = {
        "schemaVersion": 3,
        "instrument": "rhythm",
        "gate": "rhythm-final-professional-holdout",
        "minimumProfessionalScore": args.minimum,
        "checks": checks,
        "failedChecks": failed,
        "referenceJsonSha256": completeness_reference_hash,
        "referenceJsonSha256BeforeScore": reference_hash_before_score,
        "referenceJsonSha256AfterScore": reference_hash_after_score,
        "professionalSourceSha256": completeness.get("sourceSha256"),
        "frozenEventSha256": frozen_hash,
        "pdfEventSha256": pdf_hash,
        "pdfEventFidelity": score.get("pdfEventFidelity"),
        "criticalMismatchCount": score.get("criticalMismatchCount"),
        "gatedMetrics": score.get("gatedMetrics"),
        "productionModified": False,
        "productionPromotionAuthorized": False,
        "rhythmComplete": not failed,
        "passed": not failed,
    }
    final_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
