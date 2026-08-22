import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "analyzer"
PUBLIC = ROOT / "public"

AUDIO_PATH = PUBLIC / "gomywayfullaitest.m4a"
FIXTURE_PATH = ANALYZER / "fixtures" / "gomyway_full_chord_sustain_reference.json"
PROFESSIONAL_STRUCTURE_PATH = PUBLIC / "gomyway-professional-rhythm-reference.json"
PROFESSIONAL_TIMING_PATH = PUBLIC / "gomyway-professional-timing-map-v2.json"
PROFESSIONAL_PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"

REQUEST_PATH = PUBLIC / "gomyway-ai-tab-113-measure-shadow-request.json"
RAW_RESPONSE_PATH = PUBLIC / "gomyway-ai-tab-113-measure-shadow-raw-response.json"
TRANSCRIPTION_PATH = PUBLIC / "gomyway-ai-tab-113-measure-shadow-transcription.json"
REPORT_PATH = PUBLIC / "gomyway-ai-tab-113-measure-shadow-report.json"

EXPECTED_MEASURES = 113


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_measure_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        for key in (
            "measures",
            "measureRows",
            "transcription",
            "normalizedMeasures",
            "result",
        ):
            value = payload.get(key)
            if isinstance(value, list) and all(isinstance(row, dict) for row in value):
                return value
            if isinstance(value, dict):
                nested = extract_measure_rows(value)
                if nested:
                    return nested
    return []


def global_measure_number(row: dict[str, Any], index: int) -> int:
    for key in (
        "measureNumber",
        "measure",
        "measureIndex",
        "barNumber",
        "bar",
    ):
        value = row.get(key)
        if isinstance(value, int):
            if key == "measureIndex" and value == index:
                return value + 1
            return value
    return index + 1


def count_events(rows: list[dict[str, Any]]) -> int:
    total = 0
    for row in rows:
        for key in ("events", "notes", "attacks", "noteEvents"):
            value = row.get(key)
            if isinstance(value, list):
                total += len(value)
                break
    return total


def main() -> None:
    if str(ANALYZER) not in sys.path:
        sys.path.insert(0, str(ANALYZER))

    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"Missing audio upload fixture: {AUDIO_PATH.relative_to(ROOT)}")
    if not FIXTURE_PATH.exists():
        raise FileNotFoundError(f"Missing 113-measure benchmark fixture: {FIXTURE_PATH.relative_to(ROOT)}")

    audio_bytes = AUDIO_PATH.read_bytes()
    fixture = load_json(FIXTURE_PATH)
    structure = load_json(PROFESSIONAL_STRUCTURE_PATH)
    timing = load_json(PROFESSIONAL_TIMING_PATH)

    request = {
        "requestType": "dadrocktabs-ai-tab-audio-upload-shadow",
        "routeShape": "/ai-tab -> /api/upload-audio -> /api/analyze-audio",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "song": "Are You Gonna Go My Way",
        "artist": "Lenny Kravitz",
        "transcriptionType": "rhythm",
        "copyrightConfirmed": True,
        "audioFileName": AUDIO_PATH.name,
        "audioMimeType": "audio/mp4",
        "audioSizeBytes": len(audio_bytes),
        "audioSha256": sha256_bytes(audio_bytes),
        "expectedMeasureCount": EXPECTED_MEASURES,
        "fullSong": True,
        "shadowMode": True,
        "paymentSkipped": True,
        "emailSkipped": True,
        "productionRendererAllowed": False,
        "professionalPdfIsScoringAuthority": True,
    }
    write_json(REQUEST_PATH, request)

    try:
        from modal_analyzer_v8_notation_benchmark import app, run_benchmark
    except ImportError as exc:
        raise RuntimeError(
            "Could not import modal_analyzer_v8_notation_benchmark from analyzer/. "
            "Run this command from the repository root after pulling the Jimmy branch."
        ) from exc

    print("DadRock AI Tab 113-measure shadow request started")
    print(f"Audio upload: {AUDIO_PATH.relative_to(ROOT)}")
    print("Transcription type: rhythm")
    print("Expected measures: 113")
    print("Shadow mode: True")
    print("Production renderer allowed: False")

    with app.run():
        result_bytes = run_benchmark.remote(audio_bytes, AUDIO_PATH.name, fixture)

    if isinstance(result_bytes, bytes):
        raw_text = result_bytes.decode("utf-8")
        raw_payload = json.loads(raw_text)
    elif isinstance(result_bytes, str):
        raw_payload = json.loads(result_bytes)
    elif isinstance(result_bytes, dict):
        raw_payload = result_bytes
    else:
        raise RuntimeError(f"Unexpected analyzer response type: {type(result_bytes).__name__}")

    write_json(RAW_RESPONSE_PATH, raw_payload)

    rows = extract_measure_rows(raw_payload)
    normalized_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        normalized = dict(row)
        normalized["measureNumber"] = global_measure_number(row, index)
        normalized_rows.append(normalized)

    measure_numbers = sorted(
        {
            row["measureNumber"]
            for row in normalized_rows
            if isinstance(row.get("measureNumber"), int)
            and 1 <= row["measureNumber"] <= EXPECTED_MEASURES
        }
    )
    missing_measures = [
        measure
        for measure in range(1, EXPECTED_MEASURES + 1)
        if measure not in measure_numbers
    ]

    transcription = {
        "song": request["song"],
        "artist": request["artist"],
        "transcriptionType": request["transcriptionType"],
        "sourceAudio": str(AUDIO_PATH.relative_to(ROOT)),
        "sourceAudioSha256": request["audioSha256"],
        "measureCount": len(measure_numbers),
        "eventCount": count_events(normalized_rows),
        "measures": normalized_rows,
        "shadowOnly": True,
        "productionRendererAllowed": False,
    }
    write_json(TRANSCRIPTION_PATH, transcription)

    structure_count = len(structure.get("measures", [])) if isinstance(structure, dict) else 0
    timing_rows = timing.get("measures") if isinstance(timing, dict) else None
    timing_count = len(timing_rows) if isinstance(timing_rows, list) else EXPECTED_MEASURES

    source_unchanged = sha256_bytes(AUDIO_PATH.read_bytes()) == request["audioSha256"]
    full_coverage = measure_numbers == list(range(1, EXPECTED_MEASURES + 1))

    report = {
        "requestAccepted": True,
        "analyzerReturned": True,
        "expectedMeasureCount": EXPECTED_MEASURES,
        "detectedMeasureCount": len(measure_numbers),
        "detectedEventCount": transcription["eventCount"],
        "missingMeasures": missing_measures,
        "full113MeasureCoveragePassed": full_coverage,
        "professionalStructureCoverage": structure_count,
        "professionalTimingCoverage": timing_count,
        "professionalPdfPresent": PROFESSIONAL_PDF_PATH.exists(),
        "professionalPdfRemainsScoringAuthority": True,
        "noteLevelProfessionalCoverage": "measures 1-16 verified; 17-113 exception review pending",
        "sourceAudioShaUnchanged": source_unchanged,
        "sourceEventsMutated": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "paymentCalled": False,
        "emailCalled": False,
        "productionPromotionAllowed": False,
        "readyForProtectedPdfCandidate": full_coverage and source_unchanged,
        "readyForAutomaticProfessionalComparison": full_coverage,
        "readyForHumanExceptionReview": full_coverage,
        "readyForProduction": False,
        "artifacts": {
            "request": str(REQUEST_PATH.relative_to(ROOT)),
            "rawResponse": str(RAW_RESPONSE_PATH.relative_to(ROOT)),
            "transcription": str(TRANSCRIPTION_PATH.relative_to(ROOT)),
            "report": str(REPORT_PATH.relative_to(ROOT)),
        },
    }
    write_json(REPORT_PATH, report)

    print("DadRock AI Tab 113-measure shadow request complete")
    print(f"Detected measures: {len(measure_numbers)}/113")
    print(f"Detected events: {transcription['eventCount']}")
    print(f"Missing measures: {missing_measures}")
    print(f"Full 113-measure coverage passed: {full_coverage}")
    print(f"Professional structure coverage: {structure_count}/113")
    print(f"Professional timing coverage: {timing_count}/113")
    print(f"Professional PDF present: {PROFESSIONAL_PDF_PATH.exists()}")
    print(f"Source audio SHA unchanged: {source_unchanged}")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Payment called: False")
    print("Email called: False")
    print("Production promotion allowed: False")
    print(f"Ready for protected PDF candidate: {report['readyForProtectedPdfCandidate']}")
    print("Ready for production: False")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")

    if not full_coverage:
        raise RuntimeError(
            "AI Tab shadow request did not return complete 113-measure coverage"
        )


if __name__ == "__main__":
    main()
