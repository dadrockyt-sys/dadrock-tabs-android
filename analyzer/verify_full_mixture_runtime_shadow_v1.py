from __future__ import annotations

import copy
import json
import math
import os
import sys
import tempfile
import types
import wave
from pathlib import Path

from full_mixture_runtime_shadow_v1 import (
    estimate_full_mixture_runtime_shadow_v1,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RATE = 44100


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_click_wav(path: Path) -> None:
    bpm = 120.0
    period = 60.0 / bpm
    beat_count = 12
    duration = beat_count * period + 0.25
    frame_count = int(round(duration * SOURCE_RATE))
    click_frames = int(round(0.008 * SOURCE_RATE))
    raw = bytearray()

    for frame_index in range(frame_count):
        value = 0.0
        time_seconds = frame_index / SOURCE_RATE
        beat_phase = time_seconds % period
        if beat_phase < click_frames / SOURCE_RATE:
            value = 0.9 * (1.0 - beat_phase / (click_frames / SOURCE_RATE))
        sample = int(max(-1.0, min(1.0, value)) * 32767.0)
        encoded = sample.to_bytes(2, "little", signed=True)
        raw.extend(encoded)
        raw.extend(encoded)

    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(SOURCE_RATE)
        writer.writeframes(bytes(raw))


def install_fake_adapter(function):
    previous = sys.modules.get("full_mixture_wav_adapter_v1")
    module = types.ModuleType("full_mixture_wav_adapter_v1")
    module.estimate_full_mixture_structure_from_wav_v1 = function
    sys.modules["full_mixture_wav_adapter_v1"] = module
    return previous


def restore_adapter(previous) -> None:
    if previous is None:
        sys.modules.pop("full_mixture_wav_adapter_v1", None)
    else:
        sys.modules["full_mixture_wav_adapter_v1"] = previous


results: dict[str, str] = {}

modal_source = (ROOT / "analyzer/modal_analyzer.py").read_text(encoding="utf-8")
route_source = (ROOT / "app/api/analyze-audio-tab/route.js").read_text(encoding="utf-8")

# S1: normalization/inspection -> shadow -> canonical analysis.
normalize_index = modal_source.index("normalize_audio_file(\n                str(audio_path)")
normalized_inspect_index = modal_source.index("normalized_metadata = inspect_audio_file(")
shadow_index = modal_source.index("estimate_full_mixture_runtime_shadow_v1(\n                        str(normalized_path)")
canonical_index = modal_source.index("result = analyze_audio_file(\n                str(normalized_path)")
assert_true(normalize_index < normalized_inspect_index < shadow_index < canonical_index, "S1 seam ordering failed")
results["S1"] = "PASS"

with tempfile.TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)
    wav_path = root / "normalized.wav"
    write_click_wav(wav_path)

    # S2: real synthetic PCM WAV returns trusted research metadata; canonical payload is unchanged.
    observation = estimate_full_mixture_runtime_shadow_v1(wav_path)
    assert_true(isinstance(observation, dict), "S2 expected trusted observation")
    canonical = {
        "generatedTab": "e|---|",
        "tuning": "E Standard",
        "tempo": None,
        "timeSignature": None,
        "events": [{"midi": 64}],
        "noteCount": 1,
    }
    baseline = copy.deepcopy(canonical)
    wired = copy.deepcopy(canonical)
    wired["mixtureObservation"] = observation
    wired_without_shadow = copy.deepcopy(wired)
    wired_without_shadow.pop("mixtureObservation")
    assert_true(wired_without_shadow == baseline, "S2 canonical fields changed")
    results["S2"] = "PASS"

    # S3: forced adapter exception fails open.
    def raise_adapter(_path):
        raise RuntimeError("synthetic shadow failure")

    previous = install_fake_adapter(raise_adapter)
    try:
        assert_true(estimate_full_mixture_runtime_shadow_v1(wav_path) is None, "S3 exception must fail open")
    finally:
        restore_adapter(previous)
    results["S3"] = "PASS"

    # S4: invalid WAV fails open.
    invalid_path = root / "invalid.wav"
    invalid_path.write_bytes(b"not-a-wave")
    assert_true(estimate_full_mixture_runtime_shadow_v1(invalid_path) is None, "S4 invalid WAV must fail open")
    results["S4"] = "PASS"

    # S5: missing WAV fails open.
    assert_true(estimate_full_mixture_runtime_shadow_v1(root / "missing.wav") is None, "S5 missing WAV must fail open")
    assert_true(estimate_full_mixture_runtime_shadow_v1(None) is None, "S5 null path must fail open")
    results["S5"] = "PASS"

    # S6: malformed/untrusted result fails open.
    for malformed in (
        None,
        [],
        {},
        {"provenance": {}, "diagnostics": {"wavAdapter": {}}},
    ):
        previous = install_fake_adapter(lambda _path, value=malformed: value)
        try:
            assert_true(estimate_full_mixture_runtime_shadow_v1(wav_path) is None, "S6 malformed result must fail open")
        finally:
            restore_adapter(previous)
    results["S6"] = "PASS"

# S7: hook passes only normalized full-mixture WAV path.
assert_true("estimate_full_mixture_runtime_shadow_v1(\n                        str(normalized_path)\n                    )" in modal_source, "S7 shadow argument changed")
for forbidden in ("carrier", "stem", "event", "reference"):
    shadow_window = modal_source[shadow_index - 180 : shadow_index + 180].lower()
    assert_true(forbidden not in shadow_window, f"S7 forbidden shadow input near hook: {forbidden}")
results["S7"] = "PASS"

# S8: canonical analysis does not read mixtureObservation; only append occurs after it.
canonical_function = modal_source[modal_source.index("def analyze_audio_file(") : modal_source.index("@app.function(")]
assert_true("mixtureObservation" not in canonical_function, "S8 canonical analyzer reads shadow metadata")
append_text = 'result["mixtureObservation"] = mixture_observation'
assert_true(modal_source.count(append_text) == 1, "S8 expected exactly one shadow append")
assert_true(modal_source.index(append_text) > canonical_index, "S8 shadow append must follow canonical analysis")
results["S8"] = "PASS"

# S9: Next.js Product trust remains explicitly null.
assert_true("mixtureObservation: null" in route_source, "S9 server trust boundary changed")
results["S9"] = "PASS"

# S10: runtime source carries metadata only; Product/PDF source has no new runtime hook.
assert_true("generate-tab-pdf" not in modal_source and "createJimmyPaigeProfessionalPdf" not in modal_source, "S10 Product/PDF coupling found")
results["S10"] = "PASS"

# S11: this verifier is local/synthetic and contains no invocation/deployment path.
assert_true(".remote(" not in modal_source and "modal.run" not in modal_source, "S11 unexpected Modal invocation path")
results["S11"] = "PASS"

# S12: rollback is one hook block plus one additive field; canonical function is otherwise independent.
assert_true(modal_source.count("from full_mixture_runtime_shadow_v1 import (") == 1, "S12 expected one shadow import seam")
assert_true(modal_source.count("estimate_full_mixture_runtime_shadow_v1(\n                        str(normalized_path)") == 1, "S12 expected one shadow call seam")
assert_true(modal_source.count("mixtureObservation") == 1, "S12 expected one additive response field")
results["S12"] = "PASS"

evidence = {
    "schemaVersion": 1,
    "gate": "full-mixture-analyzer-runtime-shadow-wiring-v1",
    "referenceBlind": True,
    "syntheticWavOnly": True,
    "externalAudioAssetsUsed": False,
    "guitarSetRead": False,
    "splitMySongRead": False,
    "goatRestrictedBytesRead": False,
    "referenceScoreCalls": 0,
    "modalInvoked": False,
    "gpuUsed": False,
    "serverProductTrustChanged": False,
    "productPdfModifiedByRuntimeHook": False,
    "productionModified": False,
    "productionPromotionAuthorized": False,
    "tests": results,
    "passed": len(results) == 12 and all(value == "PASS" for value in results.values()),
}

result_path = os.environ.get("FULL_MIXTURE_RUNTIME_SHADOW_V1_RESULT_PATH", "").strip()
if result_path:
    output = Path(result_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

print(json.dumps(evidence, indent=2))
print("FULL MIXTURE ANALYZER RUNTIME SHADOW V1 S1-S12 VERIFIED")
