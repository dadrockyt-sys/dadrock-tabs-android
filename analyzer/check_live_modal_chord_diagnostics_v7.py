from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

DEFAULT_ENDPOINT = (
    "https://dadrockyt--dadrock-tab-analyzer-analyze.modal.run"
)


def post_json(
    endpoint: str,
    payload: dict[str, Any],
    timeout_seconds: int,
) -> dict[str, Any]:
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout_seconds,
        ) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Live analyzer returned HTTP {error.code}: {detail}"
        ) from error
    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Live analyzer request failed: {error.reason}"
        ) from error

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Live analyzer returned invalid JSON."
        ) from error

    if not isinstance(parsed, dict):
        raise RuntimeError(
            "Live analyzer response must be a JSON object."
        )

    return parsed


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the deployed Jimmy PAIge V7 Modal endpoint "
            "returns read-only rhythm chord diagnostics."
        )
    )
    parser.add_argument(
        "--audio-url",
        default=os.environ.get("JIMMY_PAIGE_LIVE_AUDIO_URL", ""),
        help=(
            "Public or authorized Blob URL for a valid audio file. "
            "Defaults to JIMMY_PAIGE_LIVE_AUDIO_URL."
        ),
    )
    parser.add_argument(
        "--blob-token",
        default=os.environ.get("BLOB_READ_WRITE_TOKEN", ""),
        help=(
            "Optional Blob bearer token. Defaults to BLOB_READ_WRITE_TOKEN."
        ),
    )
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("ANALYZER_URL", DEFAULT_ENDPOINT),
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
    )
    args = parser.parse_args()

    analyzer_token = os.environ.get("ANALYZER_API_TOKEN", "").strip()
    audio_url = str(args.audio_url or "").strip()

    if not analyzer_token:
        print(
            "Missing ANALYZER_API_TOKEN in the Codespaces environment.",
            file=sys.stderr,
        )
        return 2

    if not audio_url.startswith(("https://", "http://")):
        print(
            "Provide --audio-url or set JIMMY_PAIGE_LIVE_AUDIO_URL.",
            file=sys.stderr,
        )
        return 2

    payload: dict[str, Any] = {
        "token": analyzer_token,
        "audioUrl": audio_url,
        "transcriptionType": "rhythm",
    }

    if args.blob_token:
        payload["blobToken"] = args.blob_token

    result = post_json(
        str(args.endpoint),
        payload,
        args.timeout,
    )

    generated_tab = result.get("generatedTab")
    events = result.get("events")
    chord_analysis = result.get("chordAnalysis")

    require(
        isinstance(generated_tab, str) and bool(generated_tab.strip()),
        "generatedTab is missing from the live rhythm response.",
    )
    require(
        isinstance(events, list),
        "events must remain present as a list.",
    )
    require(
        result.get("noteCount") == len(events),
        "noteCount no longer matches the protected event list.",
    )
    require(
        isinstance(chord_analysis, dict),
        "Live rhythm response is missing chordAnalysis.",
    )
    require(
        chord_analysis.get("engineVersion") == 6,
        "Live chordAnalysis is not using the protected V6 engine.",
    )
    require(
        chord_analysis.get("noSyntheticNotes") is True,
        "Live chordAnalysis noSyntheticNotes guard failed.",
    )
    require(
        result.get("chordAnalysisMode") == "diagnostic-only",
        "Live chord diagnostics are not marked diagnostic-only.",
    )
    require(
        result.get("chordAnalysisAffectsTab") is False,
        "Live chord diagnostics claim to affect the generated tab.",
    )
    require(
        isinstance(chord_analysis.get("chordVocabulary"), list),
        "Live chord vocabulary is missing or invalid.",
    )
    require(
        isinstance(chord_analysis.get("sustainedChords"), list),
        "Live sustained chord data is missing or invalid.",
    )

    print("JIMMY PAIGE V7 LIVE MODAL DIAGNOSTICS PRESERVED 💚")
    print("Endpoint:", args.endpoint)
    print("Notes:", len(events))
    print(
        "Chord vocabulary:",
        chord_analysis.get("chordVocabulary"),
    )
    print(
        "Sustained chords:",
        chord_analysis.get("sustainedChordCount"),
    )
    print("generatedTab remains present and unchanged by diagnostics.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, RuntimeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
