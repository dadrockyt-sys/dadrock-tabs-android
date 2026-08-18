from __future__ import annotations

import json
from pathlib import Path

from v143_intro_stage_diagnostic import (
    DEFAULT_AUDIO_PATH,
    REFERENCE_PATH,
    REPO_ROOT,
    app,
    grade_stages,
    run_v143_stages,
)

CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-analysis-cache.json"
)

# The remote stage function belongs to the diagnostic app, so this local
# entrypoint must run that same app in order for run_v143_stages to be hydrated.
# Give this entrypoint an explicit unique name so it can coexist with the
# diagnostic module's own local entrypoint without a duplicate-name error.
@app.local_entrypoint(name="capture_intro_cache")
def capture_intro_cache(audio_path: str = str(DEFAULT_AUDIO_PATH)) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Audio file missing or empty: {source}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Professional reference missing: {REFERENCE_PATH}")

    payload = source.read_bytes()
    if len(payload) / (1024 * 1024) >= 95:
        raise RuntimeError("Audio is too close to Modal's 100 MB payload limit")

    print("Capturing one deterministic V143 intro analysis for local calibration...")
    analysis = run_v143_stages.remote(payload, source.suffix)

    # Human reference enters only after the reference-free audio analysis has ended.
    reference = json.loads(REFERENCE_PATH.read_text())
    diagnostic = grade_stages(reference, analysis)

    cache = {
        "cacheVersion": 1,
        "scope": "professional-measures-1-16",
        "analysis": analysis,
        "baselineDiagnostic": diagnostic,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedByOfflineDiagnostic": True,
        "productionModified": False,
    }
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2) + "\n")

    print()
    print("=== V143 INTRO ANALYSIS CACHE CAPTURED ===")
    print("introCandidateCount:", len(analysis.get("introCandidates") or []))
    print("introRowCount:", len(analysis.get("introRows") or []))
    print("baselineDiagnosis:", diagnostic.get("diagnosis"))
    print("Professional reference used by analyzer: False")
    print("Production modified: False")
    print("Cache:", CACHE_PATH.relative_to(REPO_ROOT))
    print("READY FOR LOCAL SELECTION/RECONSTRUCTION SWEEPS: True")
