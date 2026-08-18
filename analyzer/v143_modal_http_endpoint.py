from __future__ import annotations

import os
from typing import Any, Callable

import modal

from v143_modal_live_endpoint import (
    _legacy_request,
    app,
    dispatch_authorized_request,
    legacy_image,
    rhythm_v143_request,
)


LegacyHandler = Callable[[dict[str, Any]], dict[str, Any]]
RhythmHandler = Callable[[dict[str, Any]], dict[str, Any]]

# This endpoint module imports the live V143 routing module when Modal hydrates
# the web container, so include that sibling source explicitly. The legacy image
# already contains FastAPI, requests, FFmpeg, Basic Pitch, and modal_analyzer.
http_image = legacy_image.add_local_python_source("v143_modal_live_endpoint")


def route_http_payload(
    payload: dict[str, Any],
    *,
    expected_token: str,
    legacy_handler: LegacyHandler,
    rhythm_handler: RhythmHandler,
) -> dict[str, Any]:
    """Pure dispatch seam used by the deployed endpoint and local verifier."""
    return dispatch_authorized_request(
        payload,
        expected_token=expected_token,
        legacy_handler=legacy_handler,
        rhythm_handler=rhythm_handler,
    )


@app.function(
    image=http_image,
    timeout=1200,
    memory=4096,
    secrets=[
        modal.Secret.from_name("dadrock-analyzer-secret")
    ],
)
@modal.fastapi_endpoint(method="POST")
def analyze(payload: dict) -> dict:
    """Production HTTP bridge used by Vercel's /api/analyze-audio-tab route.

    Lead and Bass execute the existing modal_analyzer implementation in this
    web container. Rhythm alone is forwarded to the frozen V143 L4 worker.
    """
    from fastapi import HTTPException

    expected_token = str(
        os.environ.get("ANALYZER_API_TOKEN") or ""
    )

    def rhythm_handler(routed_payload: dict[str, Any]) -> dict[str, Any]:
        return rhythm_v143_request.remote(routed_payload)

    try:
        result = route_http_payload(
            dict(payload or {}),
            expected_token=expected_token,
            legacy_handler=_legacy_request,
            rhythm_handler=rhythm_handler,
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="The analyzer could not complete the request.",
        ) from error

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=502,
            detail="The analyzer returned an invalid response.",
        )
    if not str(result.get("generatedTab") or "").strip():
        raise HTTPException(
            status_code=502,
            detail="The analyzer returned no tablature.",
        )

    return result


__all__ = [
    "analyze",
    "http_image",
    "route_http_payload",
]
