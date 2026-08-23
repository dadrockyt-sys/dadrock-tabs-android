from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_modal_live_endpoint import rhythm_image as frozen_v143_image


app = modal.App("dadrock-v143-bass-event-timing-canary")

ANALYZER_ROOT = Path(__file__).resolve().parent
APPROVED_FIXTURE = "public/gomywayfullaitest.m4a"
MAX_CANARY_AUDIO_BYTES = 50 * 1024 * 1024

# Reuse only the frozen V143 execution environment. The added files are isolated
# Bass/shared research modules and do not alter or deploy the live V143 app.
event_canary_image = (
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
)


@app.function(
    image=event_canary_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def analyze_approved_bass_event_timing(source_audio: bytes) -> dict[str, Any]:
    """Generate reference-free, cross-view Bass note/timing candidates.

    This canary ends before techniques, model training, professional identity,
    customer routing, or PDF rendering. Its accepted events must come from both
    deterministic Bass views and be authenticated onto an audio-derived timing
    grid before four-string placement.
    """
    if not source_audio:
        raise ValueError("Bass event/timing canary source audio is empty")
    if len(source_audio) > MAX_CANARY_AUDIO_BYTES:
        raise ValueError("Bass event/timing canary audio cannot exceed 50 MB")

    from bass_professional_separator_scaffold import build_diagnostic_bass_stems
    from final_product.bass.candidate_detection.bass_candidate_timing import (
        detect_bass_candidate_events,
    )
    from v143_production_separator import normalize_input_audio
    from v143_reference_free_timing import estimate_reference_free_timing

    with tempfile.TemporaryDirectory(prefix="dadrock-bass-event-timing-") as tmp:
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

    events = list(candidates["events"])
    diagnostics = dict(candidates["diagnostics"])
    return {
        "schemaVersion": 1,
        "mode": "isolated-reference-free-bass-candidate-note-timing-canary",
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
            "downbeatIndexMod4": int(timing.downbeat_index_mod4),
            "beatConfidence": float(timing.beat_confidence),
            "barConfidence": float(timing.bar_confidence),
            "sourceSampleRate": int(timing.source_sample_rate),
            "analysisSampleRate": int(timing.analysis_sample_rate),
            "referenceFree": True,
        },
        "candidateDiagnostics": diagnostics,
        "events": events,
        "eventCount": len(events),
        "referenceFree": True,
        "crossViewConsensusRequired": True,
        "requiredConsensusViews": 2,
        "diagnosticOnly": True,
        "candidateNoteTimingGenerated": len(events) > 0,
        "techniqueQualityProven": False,
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
    output_path: str = ".bass-event-timing/raw-bass-event-timing.json",
) -> None:
    source = Path(audio_path)
    if not source.is_file() or source.stat().st_size <= 0:
        raise RuntimeError(f"Approved Bass event/timing audio missing: {source}")
    if source.as_posix() != APPROVED_FIXTURE:
        raise RuntimeError(
            "Bass event/timing canary is locked to the approved fixture: "
            f"{APPROVED_FIXTURE}"
        )
    if source.stat().st_size > MAX_CANARY_AUDIO_BYTES:
        raise RuntimeError("Approved Bass event/timing audio exceeds 50 MB")

    result = analyze_approved_bass_event_timing.remote(source.read_bytes())
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    print("=== BASS EVENT/TIMING CANARY COMPLETE ===")
    print(f"rawOutput={output}")
    print(f"eventCount={result.get('eventCount')}")
    print(f"tempoBpm={result.get('timing', {}).get('tempoBpm')}")
    print("techniqueQualityProven=false")
    print("analyzerRoutingEnabled=false")
    print("pdfRendererEnabled=false")
    print("productionModified=false")


if __name__ == "__main__":
    pass
