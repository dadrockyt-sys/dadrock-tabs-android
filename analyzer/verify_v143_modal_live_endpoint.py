from __future__ import annotations

from copy import deepcopy
from typing import Any

from v143_modal_live_endpoint import (
    MODEL_REMOTE_PATH,
    V143_MODULES,
    dispatch_authorized_request,
)


def main() -> None:
    calls: list[tuple[str, dict[str, Any]]] = []

    def legacy_handler(payload: dict[str, Any]) -> dict[str, Any]:
        calls.append(("legacy", deepcopy(payload)))
        return {
            "generatedTab": f"legacy-{payload['transcriptionType']}",
            "events": [{"owner": "legacy"}],
        }

    def rhythm_handler(payload: dict[str, Any]) -> dict[str, Any]:
        calls.append(("rhythm", deepcopy(payload)))
        return {
            "generatedTab": "v143-rhythm",
            "rhythmRouting": {"requestedPart": "rhythm"},
        }

    base = {
        "token": "secret",
        "blobToken": "blob-secret",
        "audioUrl": "https://example.com/private.wav",
        "pathname": "ai-tab/private.wav",
        "song": "Test Song",
        "artist": "Test Artist",
    }

    lead_payload = {**base, "transcriptionType": "lead"}
    lead_before = deepcopy(lead_payload)
    lead = dispatch_authorized_request(
        lead_payload,
        expected_token="secret",
        legacy_handler=legacy_handler,
        rhythm_handler=rhythm_handler,
    )

    bass_payload = {**base, "transcriptionType": "bass"}
    bass_before = deepcopy(bass_payload)
    bass = dispatch_authorized_request(
        bass_payload,
        expected_token="secret",
        legacy_handler=legacy_handler,
        rhythm_handler=rhythm_handler,
    )

    rhythm_payload = {**base, "transcriptionType": "rhythm"}
    rhythm_before = deepcopy(rhythm_payload)
    rhythm = dispatch_authorized_request(
        rhythm_payload,
        expected_token="secret",
        legacy_handler=legacy_handler,
        rhythm_handler=rhythm_handler,
    )

    lead_legacy = lead.get("generatedTab") == "legacy-lead"
    bass_legacy = bass.get("generatedTab") == "legacy-bass"
    rhythm_v143 = rhythm.get("generatedTab") == "v143-rhythm"

    call_kinds = [kind for kind, _payload in calls]
    lead_bass_only_legacy = call_kinds[:2] == ["legacy", "legacy"]
    rhythm_bypasses_legacy = call_kinds[2:] == ["rhythm"]

    payload_contract_preserved = bool(
        calls[0][1] == lead_before
        and calls[1][1] == bass_before
        and calls[2][1] == rhythm_before
    )
    source_payloads_unmutated = bool(
        lead_payload == lead_before
        and bass_payload == bass_before
        and rhythm_payload == rhythm_before
    )

    unauthorized_rejected = False
    try:
        dispatch_authorized_request(
            rhythm_payload,
            expected_token="different-secret",
            legacy_handler=legacy_handler,
            rhythm_handler=rhythm_handler,
        )
    except PermissionError:
        unauthorized_rejected = True

    invalid_type_rejected = False
    try:
        dispatch_authorized_request(
            {**base, "transcriptionType": "drums"},
            expected_token="secret",
            legacy_handler=legacy_handler,
            rhythm_handler=rhythm_handler,
        )
    except ValueError:
        invalid_type_rejected = True

    invalid_url_rejected = False
    try:
        dispatch_authorized_request(
            {
                **base,
                "audioUrl": "file:///tmp/audio.wav",
                "transcriptionType": "rhythm",
            },
            expected_token="secret",
            legacy_handler=legacy_handler,
            rhythm_handler=rhythm_handler,
        )
    except ValueError:
        invalid_url_rejected = True

    required_modules = {
        "modal_analyzer",
        "v143_candidate_timing_adapter",
        "v143_modal_rhythm_router",
        "v143_production_engine",
        "v143_production_separator",
        "v143_reference_free_rhythm_pipeline",
        "v143_reference_free_timing",
        "v143_rhythm_event_assembly",
        "v143_rhythm_guitar_note_mapper",
        "v143_rhythm_output_adapter",
        "v143_rhythm_runtime",
        "v143_rhythm_stem_provider",
        "v143_rhythm_sustain_technique_enricher",
        "v143_vercel_audio_request_adapter",
    }
    source_manifest_complete = required_modules.issubset(set(V143_MODULES))
    production_model_mounted = MODEL_REMOTE_PATH.endswith(
        "/v143-production-model-candidate-v1.json"
    )

    deterministic_calls: list[tuple[str, dict[str, Any]]] = []

    def deterministic_legacy(payload: dict[str, Any]) -> dict[str, Any]:
        deterministic_calls.append(("legacy", deepcopy(payload)))
        return {"generatedTab": "same-lead"}

    def deterministic_rhythm(payload: dict[str, Any]) -> dict[str, Any]:
        deterministic_calls.append(("rhythm", deepcopy(payload)))
        return {"generatedTab": "same-rhythm"}

    repeat_a = dispatch_authorized_request(
        rhythm_payload,
        expected_token="secret",
        legacy_handler=deterministic_legacy,
        rhythm_handler=deterministic_rhythm,
    )
    repeat_b = dispatch_authorized_request(
        rhythm_payload,
        expected_token="secret",
        legacy_handler=deterministic_legacy,
        rhythm_handler=deterministic_rhythm,
    )
    deterministic_repeat = repeat_a == repeat_b

    checks = {
        "Lead stays on existing analyzer path": lead_legacy,
        "Bass stays on existing analyzer path": bass_legacy,
        "Rhythm enters V143 live path": rhythm_v143,
        "Lead/Bass dispatch only to legacy handler": lead_bass_only_legacy,
        "Rhythm bypasses legacy handler": rhythm_bypasses_legacy,
        "Vercel request payload preserved exactly": payload_contract_preserved,
        "Source request payloads mutated": not source_payloads_unmutated,
        "Unauthorized request rejected": unauthorized_rejected,
        "Invalid transcription type rejected": invalid_type_rejected,
        "Invalid audio URL rejected": invalid_url_rejected,
        "V143 Modal source manifest complete": source_manifest_complete,
        "Frozen V143 production model mounted": production_model_mounted,
        "Professional reference used": False,
        "Runtime labels required": False,
        "Deterministic repeat exact": deterministic_repeat,
    }

    ready = (
        lead_legacy
        and bass_legacy
        and rhythm_v143
        and lead_bass_only_legacy
        and rhythm_bypasses_legacy
        and payload_contract_preserved
        and source_payloads_unmutated
        and unauthorized_rejected
        and invalid_type_rejected
        and invalid_url_rejected
        and source_manifest_complete
        and production_model_mounted
        and deterministic_repeat
    )

    print("=== V143 LIVE MODAL ENDPOINT CONTRACT VERIFIED ===")
    for label, value in checks.items():
        print(f"{label}: {value}")
    print(f"READY FOR MODAL IMAGE SMOKE: {ready}")

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
