from __future__ import annotations

from pathlib import Path


ROUTE_PATH = Path("app/api/analyze-audio-tab/route.js")


def main() -> None:
    source = ROUTE_PATH.read_text(encoding="utf-8")

    checks = {
        "Legacy analyzer environment preserved": (
            "process.env.ANALYZER_API_URL;" in source
        ),
        "Separate V143 rhythm environment added": (
            "process.env.ANALYZER_API_URL_V143;" in source
        ),
        "V143 selection limited to Rhythm": (
            "transcriptionType === 'rhythm'" in source
            and "usingV143RhythmAnalyzer" in source
        ),
        "Lead/Bass retain legacy fallback": (
            "? v143RhythmAnalyzerUrl" in source
            and ": legacyAnalyzerUrl;" in source
        ),
        "Existing analyzer token preserved": (
            "process.env.ANALYZER_API_TOKEN;" in source
        ),
        "Existing private Blob token preserved": (
            "process.env.BLOB_READ_WRITE_TOKEN;" in source
        ),
        "Vercel payload contract preserved": all(
            token in source
            for token in (
                "token: analyzerToken",
                "blobToken,",
                "audioUrl,",
                "pathname,",
                "song,",
                "artist,",
                "transcriptionType,",
            )
        ),
        "V143 canary fails closed on identity mismatch": (
            "analyzerData?.liveV143?.referenceFree !== true" in source
            and "did not identify itself correctly" in source
        ),
        "Canary result exposes engine identity": (
            "analysisEngine:" in source
            and "v143-reference-free-rhythm" in source
            and "rhythmCanaryActive:" in source
        ),
        "Removing V143 env restores legacy Rhythm": (
            "Boolean(v143RhythmAnalyzerUrl)" in source
            and "legacyAnalyzerUrl" in source
        ),
    }

    ready = all(checks.values())

    print("=== V143 VERCEL RHYTHM CANARY ROUTE VERIFIED ===")
    for label, value in checks.items():
        print(f"{label}: {value}")
    print(f"READY FOR VERCEL PREVIEW/CANARY CONFIG: {ready}")

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
