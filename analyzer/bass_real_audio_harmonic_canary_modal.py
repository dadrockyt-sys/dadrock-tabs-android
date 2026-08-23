from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_modal_live_endpoint import rhythm_image as frozen_v143_image


app = modal.App("dadrock-v143-bass-harmonic-canary")

ANALYZER_ROOT = Path(__file__).resolve().parent
APPROVED_FIXTURE = "public/gomywayfullaitest.m4a"
MAX_CANARY_AUDIO_BYTES = 50 * 1024 * 1024

harmonic_canary_image = (
    frozen_v143_image
    .add_local_python_source(
        "v143_modal_live_endpoint",
        "bass_professional_separator_scaffold",
    )
    .add_local_file(
        ANALYZER_ROOT / "final_product" / "shared" / "timing_grid.py",
        "/root/final_product/shared/timing_grid.py",
    )
    .add_local_file(
        ANALYZER_ROOT
        / "final_product"
        / "bass"
        / "hz_features"
        / "bass_frequency_profile.py",
        "/root/final_product/bass/hz_features/bass_frequency_profile.py",
    )
    .add_local_file(
        ANALYZER_ROOT
        / "final_product"
        / "bass"
        / "candidate_detection"
        / "bass_candidate_timing.py",
        "/root/final_product/bass/candidate_detection/bass_candidate_timing.py",
    )
    .add_local_file(
        ANALYZER_ROOT
        / "final_product"
        / "bass"
        / "techniques"
        / "bass_technique_evidence.py",
        "/root/final_product/bass/techniques/bass_technique_evidence.py",
    )
    .add_local_file(
        ANALYZER_ROOT
        / "final_product"
        / "bass"
        / "techniques"
        / "bass_harmonic_evidence.py",
        "/root/final_product/bass/techniques/bass_harmonic_evidence.py",
    )
)


@app.function(
    image=harmonic_canary_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def analyze_approved_bass_harmonics(source_audio: bytes) -> dict[str, Any]:
    """Run the green Bass subset then add isolated two-view harmonic evidence."""
    if not source_audio:
        raise ValueError("Bass harmonic canary source audio is empty")
    if len(source_audio) > MAX_CANARY_AUDIO_BYTES:
        raise ValueError("Bass harmonic canary audio cannot exceed 50 MB")

    from bass_professional_separator_scaffold import build_diagnostic_bass_stems
    from final_product.bass.candidate_detection.bass_candidate_timing import (
        detect_bass_candidate_events,
    )
    from final_product.bass.techniques.bass_harmonic_evidence import (
        enrich_bass_events_with_harmonic_evidence,
    )
    from final_product.bass.techniques.bass_technique_evidence import (
        enrich_bass_events_with_techniques,
    )
    from v143_production_separator import normalize_input_audio
    from v143_reference_free_timing import estimate_reference_free_timing

    with tempfile.TemporaryDirectory(prefix="dadrock-bass-harmonic-") as tmp:
        root = Path(tmp)
        source = root / "approved-fixture.m4a"
        source.write_bytes(source_audio)

        normalized = normalize_input_audio(source, root / "timing-normalized")
        timing = estimate_reference_free_timing(normalized)
        stems = build_diagnostic_bass_stems(source, root / "stems")
        direct = Path(stems["directBass"])
        cascade = Path(stems["cascadeBass"])

        candidates = detect_bass_candidate_events(
            [direct, cascade],
            timing.beat_times,
            first_beat_in_measure=timing.first_beat_in_measure,
        )
        base_events = list(candidates["events"])
        subset = enrich_bass_events_with_techniques(
            base_events,
            stem_paths=[direct, cascade],
        )
        subset_events = list(subset["events"])
        subset_diagnostics = dict(subset["diagnostics"])
        harmonic = enrich_bass_events_with_harmonic_evidence(
            subset_events,
            stem_paths=[direct, cascade],
        )
        enriched_events = list(harmonic["events"])
        harmonic_diagnostics = dict(harmonic["diagnostics"])

    return {
        "schemaVersion": 1,
        "mode": "isolated-reference-free-bass-harmonic-evidence-canary",
        "approvedFixture": APPROVED_FIXTURE,
        "sourceSha256": hashlib.sha256(source_audio).hexdigest(),
        "sourceBytes": len(source_audio),
        "separator": {
            "directPath": "audio -> Demucs6s Bass",
            "cascadePath": "audio -> BS-RoFormer Instrumental -> Demucs6s Bass",
            "settings": stems["settings"],
            "models": stems["models"],
        },
        "timing": {
            "tempoBpm": float(timing.tempo_bpm),
            "meterNumerator": 4,
            "meterDenominator": 4,
            "beatCount": len(timing.beat_times),
            "firstBeatInMeasure": int(timing.first_beat_in_measure),
            "referenceFree": True,
        },
        "candidateDiagnostics": candidates["diagnostics"],
        "baseEvents": base_events,
        "subsetEvents": subset_events,
        "events": enriched_events,
        "eventCount": len(enriched_events),
        "subsetTechniqueDiagnostics": subset_diagnostics,
        "harmonicDiagnostics": harmonic_diagnostics,
        "referenceFree": True,
        "crossViewConsensusRequired": True,
        "requiredConsensusViews": 2,
        "noteTimingPlayabilityPreconditionPassed": len(base_events) > 0,
        "subsetTechniqueBoundaryPreconditionPassed": int(
            subset_diagnostics.get("techniqueEventCount") or 0
        ) > 0,
        "harmonicEvidenceImplemented": True,
        "harmonicEvidenceObserved": bool(
            harmonic_diagnostics.get("harmonicEvidenceObserved")
        ),
        "harmonicFamilyProven": bool(
            harmonic_diagnostics.get("harmonicFamilyProven")
        ),
        "futureHighRiskFamiliesEnabled": False,
        "diagnosticOnly": True,
        "professionalBassComplete": False,
        "trainingRunAuthorized": False,
        "analyzerRoutingEnabled": False,
        "professionalStructuredIdentityEnabled": False,
        "pdfRendererEnabled": False,
        "liveEndpointDeployedOrModified": False,
        "vercelDeploymentAttempted": False,
        "productionModified": False,
        "productionPromotionAuthorized": False,
        "paidPurchaseAttempted": False,
        "customerTokenRedeemed": False,
        "customerEmailSent": False,
    }


@app.local_entrypoint(name="run")
def run(
    audio_path: str = APPROVED_FIXTURE,
    output_path: str = ".bass-harmonic/raw-bass-harmonic.json",
) -> None:
    source = Path(audio_path)
    if not source.is_file() or source.stat().st_size <= 0:
        raise RuntimeError(f"Approved Bass harmonic audio missing: {source}")
    if source.as_posix() != APPROVED_FIXTURE:
        raise RuntimeError(
            "Bass harmonic canary is locked to the approved fixture: "
            f"{APPROVED_FIXTURE}"
        )
    if source.stat().st_size > MAX_CANARY_AUDIO_BYTES:
        raise RuntimeError("Approved Bass harmonic audio exceeds 50 MB")

    result = analyze_approved_bass_harmonics.remote(source.read_bytes())
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    harmonic = result.get("harmonicDiagnostics") or {}
    print("=== BASS HARMONIC CANARY COMPLETE ===")
    print(f"rawOutput={output}")
    print(f"eventCount={result.get('eventCount')}")
    print(f"harmonicEventCount={harmonic.get('harmonicEventCount')}")
    print(f"harmonicFamilyProven={harmonic.get('harmonicFamilyProven')}")
    print("professionalBassComplete=false")
    print("analyzerRoutingEnabled=false")
    print("pdfRendererEnabled=false")
    print("productionModified=false")


if __name__ == "__main__":
    pass
