#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "analyzer"
CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"
REPORT_PATH = CAL / "contextual-prune-shadow-static-report.json"

CARRIER_PATH = ANALYZER / "v143_contextual_prune_reference_free_carrier.py"
SHADOW_PATH = ANALYZER / "v143_contextual_prune_shadow_modal.py"
RUNTIME_PATH = ANALYZER / "v143_contextual_prune_runtime.py"
RESEARCH_CAPTURE_PATH = ANALYZER / "v143_fresh_section5_reference_free_capture.py"

EXPECTED_LIVE_BLOBS = {
    "analyzer/v143_modal_live_endpoint.py": "3ae481bbc2a7b482a1ce50e0cfe30313bee9a850",
    "analyzer/v143_modal_rhythm_router.py": "7849f33cd3b849283ccebfda9f721cc40704231e",
    "analyzer/v143_reference_free_rhythm_pipeline.py": "7f72f8ed9b14af8bc93e95544195204d99c6bec1",
    "analyzer/v143_rhythm_runtime.py": "3f530da2c50c6b8c967a607a860c54135ee504af",
    "analyzer/v143_production_engine.py": "9201f8bb5671183051322b1ee739717336be762c",
    "analyzer/v143_candidate_timing_adapter.py": "99b90aaee4520dcde8acfad3b110d726262008cf",
}

EXPECTED_CARRIER_CONSTANTS = {
    "WIDE_GRID_TOLERANCE_SECONDS": 0.30,
    "CLUSTER_TOLERANCE_SECONDS": 0.030,
    "ONSET_GROUP_TOLERANCE_SECONDS": 0.030,
    "TARGET_SR": 22050,
    "HOP_LENGTH": 128,
    "BINS_PER_OCTAVE": 36,
    "CQT_MIDI_MIN": 28,
    "CQT_MIDI_MAX": 112,
    "GUITAR_MIDI_MIN": 40,
    "GUITAR_MIDI_MAX": 88,
}

EXPECTED_MODEL_SHA256 = "3e30fb28fb98febdd73d832d3bb31093488895820554064ab72afc9e75b2940c"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob(path: Path) -> str:
    result = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git hash-object failed for {path}")
    return result.stdout.strip()


def literal_assignments(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: dict[str, Any] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            values[target.id] = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            pass
    return values


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    for path in (CARRIER_PATH, SHADOW_PATH, RUNTIME_PATH, RESEARCH_CAPTURE_PATH):
        require(path.exists() and path.stat().st_size > 0, f"Missing static-gate source: {path}")
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    carrier_text = CARRIER_PATH.read_text(encoding="utf-8")
    shadow_text = SHADOW_PATH.read_text(encoding="utf-8")
    runtime_text = RUNTIME_PATH.read_text(encoding="utf-8")
    research_text = RESEARCH_CAPTURE_PATH.read_text(encoding="utf-8")

    forbidden_new_source_tokens = (
        "gomyway-professional-rhythm-reference",
        "gomyway-professional-rhythm-reference-v2",
    )
    for token in forbidden_new_source_tokens:
        require(token not in carrier_text, f"Carrier contains forbidden reference token: {token}")
        require(token not in shadow_text, f"Shadow contains forbidden reference token: {token}")
        require(token not in runtime_text, f"Runtime contains forbidden reference token: {token}")

    require(
        'modal.App("dadrock-v143-contextual-prune-shadow")' in shadow_text,
        "Shadow app name changed or is not isolated",
    )
    require(
        "v143_modal_live_endpoint" not in shadow_text,
        "Shadow must not import the live V143 endpoint",
    )
    require(
        "fastapi_endpoint" not in shadow_text and "web_endpoint" not in shadow_text,
        "Shadow unexpectedly exposes an HTTP endpoint",
    )
    require(
        "HISTORICAL_WIDE_RECALL_SWEEPS" in carrier_text,
        "Carrier no longer consumes the four historical wide-recall sweeps",
    )
    require(
        "for sweep_name, onset_threshold, frame_threshold in HISTORICAL_WIDE_RECALL_SWEEPS" in carrier_text,
        "Carrier sweep loop changed",
    )

    carrier_values = literal_assignments(CARRIER_PATH)
    research_values = literal_assignments(RESEARCH_CAPTURE_PATH)
    for name, expected in EXPECTED_CARRIER_CONSTANTS.items():
        actual = carrier_values.get(name)
        require(actual == expected, f"Carrier constant changed: {name}={actual!r} expected {expected!r}")
        research_actual = research_values.get(name)
        require(
            research_actual == expected,
            f"Research carrier constant drifted: {name}={research_actual!r} expected {expected!r}",
        )

    # The three whole-onset CQT windows are frozen research behavior.
    for fragment in (
        '"attackMax": (onset - 0.020, onset + 0.045, "max")',
        '"earlyMean": (onset + 0.020, onset + 0.095, "mean")',
        '"sustainMean": (onset + 0.070, onset + 0.180, "mean")',
    ):
        require(fragment in carrier_text, f"Carrier CQT window changed: {fragment}")
        require(fragment in research_text, f"Research CQT window changed: {fragment}")

    model_path = CAL / "contextual-prune-frozen-model.json"
    require(file_sha256(model_path) == EXPECTED_MODEL_SHA256, "Frozen contextual model fingerprint changed")

    live_blobs: dict[str, str] = {}
    for relative, expected_blob in EXPECTED_LIVE_BLOBS.items():
        path = ROOT / relative
        actual_blob = git_blob(path)
        live_blobs[relative] = actual_blob
        require(
            actual_blob == expected_blob,
            f"Protected live V143 file changed during shadow gate: {relative} {actual_blob} != {expected_blob}",
        )

    # Import graph guard: the shadow may package research scoring helpers but must
    # never package the professional reference JSON itself.
    require(
        "professionalReferenceUsed" in shadow_text,
        "Shadow output lost explicit reference-use invariant",
    )
    require(
        '"productionModified": False' in shadow_text,
        "Shadow output lost production-modified invariant",
    )

    report = {
        "schemaVersion": 1,
        "gate": "v143-contextual-prune-isolated-shadow-static",
        "carrierConstantsMatchedResearch": True,
        "fourHistoricalWideRecallSweepsRequired": True,
        "wholeOnsetCqtWindowsMatchedResearch": True,
        "frozenContextualModelSha256": file_sha256(model_path),
        "frozenContextualModelFingerprintMatched": True,
        "shadowAppIsolated": True,
        "shadowHttpEndpointExposed": False,
        "liveV143ProtectedBlobShas": live_blobs,
        "liveV143FilesUnchanged": True,
        "professionalReferencePathPresentInNewRuntimeSources": False,
        "productionModified": False,
        "gatePassed": True,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("=== V143 CONTEXTUAL PRUNE SHADOW STATIC GATE ===")
    print("CARRIER_CONSTANTS_MATCH_RESEARCH", True)
    print("FOUR_WIDE_RECALL_SWEEPS", True)
    print("CQT_WINDOWS_MATCH_RESEARCH", True)
    print("MODEL_FINGERPRINT_MATCHED", True)
    print("SHADOW_APP_ISOLATED", True)
    print("LIVE_V143_FILES_UNCHANGED", True)
    print("PROFESSIONAL_REFERENCE_IN_NEW_RUNTIME", False)
    print("PRODUCTION_MODIFIED", False)
    print(f"WROTE={REPORT_PATH}")


if __name__ == "__main__":
    main()
