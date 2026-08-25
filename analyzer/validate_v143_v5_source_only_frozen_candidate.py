#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], text=True).strip()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"Expected object JSON: {path}")
    return value


def validate(manifest_path: Path) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    checks: dict[str, bool] = {}
    mismatches: list[dict[str, str]] = []

    checks["classificationExact"] = manifest.get("classification") == "v143-v5-source-only-frozen-candidate"
    checks["branchExact"] = manifest.get("branch") == "v143-contextual-prune-lobo"

    status = manifest.get("status") if isinstance(manifest.get("status"), dict) else {}
    checks["sourceOnlyFrozenDeclared"] = status.get("sourceOnlyFrozen") is True
    checks["referenceFreeDeclared"] = status.get("referenceFree") is True
    checks["professionalReferenceUnusedDeclared"] = status.get("professionalReferenceUsed") is False
    checks["professionalHoldoutClosedDeclared"] = status.get("professionalHoldoutOpened") is False
    checks["finalCompletionNotDeclared"] = status.get("finalCompletionReady") is False
    checks["modalUnusedDeclared"] = status.get("modalInvoked") is False
    checks["productionUntouchedDeclared"] = status.get("productionModified") is False
    checks["timingFrozenDeclared"] = status.get("timingFrozen") is True
    checks["tempoExact"] = float((manifest.get("boundaries") or {}).get("tempo", 0.0)) == 129.19921875

    blob_pins = manifest.get("gitBlobPins") if isinstance(manifest.get("gitBlobPins"), dict) else {}
    blob_ok = True
    for path, expected in sorted(blob_pins.items()):
        actual = _git_blob(path)
        if actual != expected:
            blob_ok = False
            mismatches.append({"kind": "gitBlob", "path": path, "expected": str(expected), "actual": actual})
    checks["allGitBlobPinsExact"] = blob_ok and bool(blob_pins)

    sha_pins = manifest.get("sha256Pins") if isinstance(manifest.get("sha256Pins"), dict) else {}
    sha_ok = True
    for path, expected in sorted(sha_pins.items()):
        actual = _sha256(Path(path))
        if actual != expected:
            sha_ok = False
            mismatches.append({"kind": "sha256", "path": path, "expected": str(expected), "actual": actual})
    checks["allSha256PinsExact"] = sha_ok and bool(sha_pins)

    root = Path("debug/v143-contextual-prune/v5-professional-pdf")
    neutral = _load_json(root / "neutral-metadata-policy-report.json")
    render = _load_json(root / "render-report.json")
    stream = _load_json(root / "v5-render-stream.json")

    checks["neutralPolicyValidationPassed"] = neutral.get("validationPassed") is True
    checks["neutralPolicyResolved"] = neutral.get("metadataPolicyResolved") is True
    checks["neutralPolicyReferenceFree"] = neutral.get("referenceFree") is True
    checks["neutralPolicyProfessionalReferenceUnused"] = neutral.get("professionalReferenceUsed") is False
    checks["neutralPolicyModalUnused"] = neutral.get("modalInvoked") is False
    checks["neutralPolicyProductionUntouched"] = neutral.get("productionModified") is False
    checks["neutralPolicyFinalSentinelStillFalse"] = neutral.get("freezeReady") is False

    checks["streamValidationPassed"] = stream.get("validationPassed") is True
    checks["streamReferenceFree"] = stream.get("referenceFree") is True
    checks["streamProfessionalReferenceUnused"] = stream.get("professionalReferenceUsed") is False
    checks["streamModalUnused"] = stream.get("modalInvoked") is False
    checks["streamProductionUntouched"] = stream.get("productionModified") is False
    checks["streamFinalSentinelStillFalse"] = stream.get("freezeReady") is False

    summary = stream.get("summary") if isinstance(stream.get("summary"), dict) else {}
    content = manifest.get("contentIdentity") if isinstance(manifest.get("contentIdentity"), dict) else {}
    checks["renderedEventCountExact"] = int(summary.get("renderedEventCount") or -1) == int(content.get("renderedEventCount") or -2) == 1209
    checks["retainedAttackCountExact"] = int(summary.get("retainedOnsetCount") or -1) == int(content.get("retainedAttackCount") or -2) == 891
    checks["baselineRenderedCountExact"] = int(summary.get("baselineRenderedEventCount") or -1) == int(content.get("baselineRenderedEventCount") or -2) == 967
    checks["rescuedRenderedCountExact"] = int(summary.get("rescuedRenderedEventCount") or -1) == int(content.get("rescuedRenderedEventCount") or -2) == 242
    checks["preservedMetadataCountExact"] = int(summary.get("preservedBaselineMetadataEventCount") or -1) == int(content.get("preservedMetadataEventCount") or -2) == 933
    checks["techniqueEventCountExact"] = int(summary.get("techniqueEventCount") or -1) == int(content.get("techniqueEventCount") or -2) == 21
    checks["measureCoverageExact"] = int(summary.get("measureCoverageCount") or -1) == int(content.get("measureCoverageCount") or -2) == 113

    checks["renderReportReferenceFree"] = render.get("referenceFree") is True
    checks["renderReportProfessionalReferenceUnused"] = render.get("professionalReferenceUsed") is False
    checks["renderReportModalUnused"] = render.get("modalInvoked") is False
    checks["renderReportProductionUntouched"] = render.get("productionModified") is False
    checks["renderReportFinalSentinelStillFalse"] = render.get("freezeReady") is False
    checks["renderReportEventCountExact"] = int(render.get("renderedEventCount") or -1) == 1209
    checks["renderReportOnsetCountExact"] = int(render.get("uniqueOnsetCount") or -1) == 891
    checks["renderReportMeasureCountExact"] = int(render.get("uniqueMeasureCount") or -1) == 113
    checks["renderReportPdfBytesExact"] = int(render.get("pdfBytes") or -1) == 1748095

    freeze_semantics = manifest.get("freezeSemantics") if isinstance(manifest.get("freezeSemantics"), dict) else {}
    checks["sourceOnlyFreezeVerdictFrozen"] = freeze_semantics.get("sourceOnlyFreezeVerdict") == "FROZEN"
    checks["finalProfessionalGatePending"] = freeze_semantics.get("finalProfessionalGateVerdict") == "PENDING"
    checks["postFreezeTuningForbidden"] = freeze_semantics.get("tuningAfterThisManifestIsForbiddenBeforeFinalHoldout") is True
    checks["holdoutSelectionForbidden"] = freeze_semantics.get("candidateSelectionAfterProfessionalHoldoutIsForbidden") is True

    passed = all(checks.values()) and not mismatches
    return {
        "schemaVersion": 1,
        "classification": "v143-v5-source-only-frozen-candidate-validation",
        "manifest": str(manifest_path),
        "sourceOnlyFreezeValidationPassed": passed,
        "sourceOnlyFrozen": passed,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "professionalHoldoutOpened": False,
        "finalProfessionalGatePending": True,
        "finalCompletionReady": False,
        "modalInvoked": False,
        "productionModified": False,
        "existingFinalGateFreezeReadySentinelsRemainFalse": True,
        "checks": checks,
        "mismatches": mismatches,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = validate(args.manifest)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    return 0 if report["sourceOnlyFreezeValidationPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
