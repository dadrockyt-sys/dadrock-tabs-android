from __future__ import annotations

import json
import os
from typing import Any

import modal


app = modal.App("dadrock-v143-http-probe")

probe_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("requests")
)

DEFAULT_ENDPOINT = (
    "https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run"
)

# Public CC-licensed guitar test fixture described by the Mustango project as an
# instrumental blues excerpt containing lead guitar plus steady strummed acoustic
# guitar. This keeps the HTTP smoke independent of private Vercel Blob credentials;
# the real private-Blob boundary remains covered by the Vercel adapter verifier.
DEFAULT_AUDIO_URL = (
    "https://raw.githubusercontent.com/AMAAI-Lab/mustango/main/"
    "samples/mustango-pretrained/output_0.wav"
)


@app.function(
    image=probe_image,
    timeout=1200,
    memory=1024,
    secrets=[modal.Secret.from_name("dadrock-analyzer-secret")],
)
def probe_live_http(
    endpoint: str = DEFAULT_ENDPOINT,
    audio_url: str = DEFAULT_AUDIO_URL,
) -> dict[str, Any]:
    import requests

    token = str(os.environ.get("ANALYZER_API_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("ANALYZER_API_TOKEN is missing from Modal secret")

    payload = {
        "token": token,
        "blobToken": "",
        "audioUrl": str(audio_url),
        "pathname": "v143-http-smoke/public-guitar.wav",
        "song": "V143 HTTP Smoke",
        "artist": "Public guitar fixture",
        "transcriptionType": "rhythm",
    }

    response = requests.post(
        str(endpoint),
        json=payload,
        timeout=1100,
    )

    try:
        body = response.json()
    except ValueError:
        body = {"raw": response.text[:2000]}

    if not response.ok:
        raise RuntimeError(
            f"Live V143 HTTP endpoint returned {response.status_code}: {body}"
        )

    generated_tab = str(body.get("generatedTab") or "")
    routing = dict(body.get("rhythmRouting") or {})
    handoff = dict(body.get("vercelAudioHandoff") or {})
    live = dict(body.get("liveV143") or {})

    result = {
        "statusCode": int(response.status_code),
        "success": bool(generated_tab.strip()),
        "generatedTabCharacters": len(generated_tab),
        "generatedTabPreview": generated_tab[:500],
        "noteCount": int(body.get("noteCount") or 0),
        "tempo": body.get("tempo"),
        "timeSignature": body.get("timeSignature"),
        "tuning": body.get("tuning"),
        "candidateStemCount": routing.get("candidateStemCount"),
        "pairedCarrierStemContractPreserved": routing.get(
            "pairedCarrierStemContractPreserved"
        ),
        "requestedPart": routing.get("requestedPart"),
        "vercelHandoffRequestedPart": handoff.get("requestedPart"),
        "normalizedBeforeRouting": handoff.get("normalizedBeforeRouting"),
        "referenceFree": live.get("referenceFree"),
        "professionalReferenceUsed": live.get("professionalReferenceUsed"),
        "runtimeLabelsRequired": live.get("runtimeLabelsRequired"),
        "modalGpu": live.get("modalGpu"),
    }

    required_true = (
        result["statusCode"] == 200
        and result["success"] is True
        and result["candidateStemCount"] == 2
        and result["pairedCarrierStemContractPreserved"] is True
        and result["requestedPart"] == "rhythm"
        and result["vercelHandoffRequestedPart"] == "rhythm"
        and result["normalizedBeforeRouting"] is True
        and result["referenceFree"] is True
        and result["professionalReferenceUsed"] is False
        and result["runtimeLabelsRequired"] is False
        and result["modalGpu"] == "L4"
    )
    result["readyForVercelCanary"] = bool(required_true)
    return result


@app.local_entrypoint()
def main(
    endpoint: str = DEFAULT_ENDPOINT,
    audio_url: str = DEFAULT_AUDIO_URL,
) -> None:
    print("Probing deployed V143 HTTP endpoint:", endpoint)
    result = probe_live_http.remote(endpoint, audio_url)
    print()
    print("=== V143 LIVE HTTP SMOKE COMPLETE ===")
    print(json.dumps(result, indent=2, default=str))
    if result.get("readyForVercelCanary") is not True:
        raise RuntimeError("Live V143 HTTP smoke did not satisfy the canary gate")
