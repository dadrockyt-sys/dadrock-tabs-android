from __future__ import annotations

from copy import deepcopy
from typing import Any

from v143_modal_http_endpoint import route_http_payload


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
            "liveV143": {"rhythmOnly": True},
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
    bass_payload = {**base, "transcriptionType": "bass"}
    rhythm_payload = {**base, "transcriptionType": "rhythm"}

    lead_before = deepcopy(lead_payload)
    bass_before = deepcopy(bass_payload)
    rhythm_before = deepcopy(rhythm_payload)

    lead = route_http_payload(
        lead_payload,
        expected_token="secret",
        legacy_handler=legacy_handler,
        rhythm_handler=rhythm_handler,
    )
    bass = route_http_payload(
        bass_payload,
        expected_token="secret",
        legacy_handler=legacy_handler,
        rhythm_handler=rhythm_handler,
    )
    rhythm = route_http_payload(
        rhythm_payload,
        expected_token="secret",
        legacy_handler=legacy_handler,
        rhythm_handler=rhythm_handler,
    )

    lead_legacy = lead.get("generatedTab") == "legacy-lead"
    bass_legacy = bass.get("generatedTab") == "legacy-bass"
    rhythm_v143 = rhythm.get("generatedTab") == "v143-rhythm"
    call_kinds = [kind for kind, _payload in calls]
    isolated_dispatch = call_kinds == ["legacy", "legacy", "rhythm"]
    payloads_preserved = bool(
        calls[0][1] == lead_before
        and calls[1][1] == bass_before
        and calls[2][1] == rhythm_before
        and lead_payload == lead_before
        and bass_payload == bass_before
        and rhythm_payload == rhythm_before
    )

    unauthorized_rejected = False
    try:
        route_http_payload(
            rhythm_payload,
            expected_token="wrong",
            legacy_handler=legacy_handler,
            rhythm_handler=rhythm_handler,
        )
    except PermissionError:
        unauthorized_rejected = True

    invalid_type_rejected = False
    try:
        route_http_payload(
            {**base, "transcriptionType": "drums"},
            expected_token="secret",
            legacy_handler=legacy_handler,
            rhythm_handler=rhythm_handler,
        )
    except ValueError:
        invalid_type_rejected = True

    invalid_url_rejected = False
    try:
        route_http_payload(
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

    deterministic_a = route_http_payload(
        rhythm_payload,
        expected_token="secret",
        legacy_handler=lambda payload: {"generatedTab": "legacy"},
        rhythm_handler=lambda payload: {"generatedTab": "same-rhythm"},
    )
    deterministic_b = route_http_payload(
        rhythm_payload,
        expected_token="secret",
        legacy_handler=lambda payload: {"generatedTab": "legacy"},
        rhythm_handler=lambda payload: {"generatedTab": "same-rhythm"},
    )
    deterministic_repeat = deterministic_a == deterministic_b

    checks = {
        "Lead stays on legacy handler": lead_legacy,
        "Bass stays on legacy handler": bass_legacy,
        "Rhythm enters V143 handler": rhythm_v143,
        "Lead/Bass/Rhythm dispatch isolated": isolated_dispatch,
        "Vercel payload preserved exactly": payloads_preserved,
        "Unauthorized request rejected": unauthorized_rejected,
        "Invalid transcription type rejected": invalid_type_rejected,
        "Invalid audio URL rejected": invalid_url_rejected,
        "Professional reference used": False,
        "Runtime labels required": False,
        "Deterministic repeat exact": deterministic_repeat,
    }

    ready = (
        lead_legacy
        and bass_legacy
        and rhythm_v143
        and isolated_dispatch
        and payloads_preserved
        and unauthorized_rejected
        and invalid_type_rejected
        and invalid_url_rejected
        and deterministic_repeat
    )

    print("=== V143 MODAL HTTP ENDPOINT VERIFIED ===")
    for label, value in checks.items():
        print(f"{label}: {value}")
    print(f"READY FOR SAFE MODAL DEPLOY: {ready}")

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
