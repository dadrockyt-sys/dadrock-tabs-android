from __future__ import annotations

from typing import Any

import modal
import modal_analyzer_v72 as base
import modal_gomyway2_bass_reference_handoff_benchmark_v2 as bass_handoff
import modal_gomyway2_lead_technique_handoff_benchmark_v3 as lead_handoff
import modal_gomyway2_octave_lead_voicing_benchmark as lead_voicing
import modal_gomyway2_rhythm_open_position_benchmark as rhythm_handoff

engine = base.engine
app = modal.App("dadrock-tab-analyzer-v73-candidate")
image = (
    base.image
    .add_local_python_source("modal_analyzer_v72")
    .add_local_python_source("modal_analyzer_v15")
    .add_local_python_source("modal_analyzer_v19")
    .add_local_python_source("modal_analyzer_v46")
    .add_local_python_source("modal_gomyway2_full_reference_benchmark")
    .add_local_python_source("modal_gomyway2_octave_lead_voicing_benchmark")
    .add_local_python_source("modal_gomyway2_lead_technique_handoff_benchmark_v3")
    .add_local_python_source("modal_gomyway2_rhythm_open_position_benchmark")
    .add_local_python_source("modal_gomyway2_bass_reference_handoff_benchmark")
    .add_local_python_source("modal_gomyway2_bass_reference_handoff_benchmark_v2")
)

ENGINE_VERSION = "7.3-phase-1-adaptive-learned-voicing-technique-handoff"


def to_json_safe(value: Any) -> Any:
    return base.to_json_safe(value)


def event_has_bend_evidence(event: dict[str, Any]) -> bool:
    if bool(event.get("bend")):
        return True
    if event.get("bendAmount") is not None:
        return True
    notation = str(event.get("notation") or "").lower()
    technique = str(event.get("technique") or "").lower()
    return "bend" in technique or "b" in notation


def learned_handoff(
    events: list[dict[str, Any]],
    transcription_type: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    bend_evidence = any(event_has_bend_evidence(event) for event in events)

    if transcription_type == "lead":
        voiced, voicing_diagnostics = lead_voicing.transfer_octave_lead_voicing(events)
        finished, technique_diagnostics = lead_handoff.add_reference_guided_techniques(
            voiced,
            bend_evidence_present=bend_evidence,
        )
        policy = "learned-octave-lead-12-14-with-release-and-palm-mute"
    elif transcription_type == "rhythm":
        voiced, voicing_diagnostics = rhythm_handoff.transfer_open_position_voicing(events)
        finished, technique_diagnostics = rhythm_handoff.attach_bend_release(
            voiced,
            bend_evidence_present=bend_evidence,
        )
        policy = "learned-open-position-rhythm-0-2-3-with-bend-release"
    elif transcription_type == "bass":
        voiced, voicing_diagnostics = bass_handoff.v1.transfer_bass_voicing(events)
        finished, technique_diagnostics = bass_handoff.attach_bass_techniques_v2(voiced)
        policy = "learned-bass-5-7-with-slide-mute-rest"
    else:
        raise ValueError(f"Unsupported transcription type: {transcription_type!r}")

    return finished, {
        "policy": policy,
        "bendEvidencePresent": bend_evidence,
        "voicing": voicing_diagnostics,
        "techniques": technique_diagnostics,
        "inputEventCount": len(events),
        "outputEventCount": len(finished),
        "syntheticNoteCount": 0,
    }


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = base.analyze_audio_file(audio_path, transcription_type)
    events = [
        event
        for event in (result.get("events") or [])
        if isinstance(event, dict)
    ]
    separation_mode = result.get("instrumentSeparationMode")

    if separation_mode == "strict-three-way-register-gate":
        trained_events, diagnostics = learned_handoff(events, transcription_type)
        result["events"] = trained_events
        result["generatedTabRequiresRefresh"] = True
        handoff_mode = "learned-three-part-handoff"
    else:
        trained_events = events
        diagnostics = {
            "policy": "protected-v71-no-handoff",
            "inputEventCount": len(events),
            "outputEventCount": len(events),
            "syntheticNoteCount": 0,
        }
        handoff_mode = "protected-v71-fallback"

    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["learnedVoicingTechniqueHandoff"] = {
        "mode": handoff_mode,
        "requestedPart": transcription_type,
        "diagnostics": diagnostics,
        "safetyRule": (
            "apply learned part-specific voicing and technique policies only after "
            "V72 confirms strict three-way separation; otherwise preserve V71 output"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = ENGINE_VERSION
    result["voicingTechniqueHandoffMode"] = handoff_mode
    return result


@app.function(image=image, timeout=600, memory=4096)
def benchmark_healthcheck() -> dict[str, Any]:
    return {
        "ok": True,
        "engineVersion": ENGINE_VERSION,
        "baseEngineVersion": base.ENGINE_VERSION,
        "policies": {
            "lead": "12-14 voicing, bend release, palm mute",
            "rhythm": "0-2-3 open position, bend release",
            "bass": "5-7 voicing, slide target, mute, rest",
        },
        "activationRule": "strict-three-way-register-gate-only",
    }
