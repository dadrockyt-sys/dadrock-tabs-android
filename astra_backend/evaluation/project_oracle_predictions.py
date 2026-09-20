"""Project locked oracle Basic Pitch events onto the frozen reviewed-source clock."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

EXPECTED_SETTINGS = {
    "onset_threshold": 0.5,
    "frame_threshold": 0.3,
    "minimum_note_length": 127.7,
    "minimum_frequency": 82.4068892282175,
    "maximum_frequency": 1318.5102276514797,
    "multiple_pitch_bends": False,
    "melodia_trick": True,
    "midi_tempo": 120,
}
EXPECTED_MODEL_SHA256 = "3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676"
EXPECTED_RUNNER_GIT_BLOB = "95950c50e00777ba3c0398b917f95dcece70065c"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def load_json_bytes(path):
    raw = Path(path).read_bytes()

    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result

    return raw, json.loads(raw, object_pairs_hook=pairs)


def valid_sha256(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def validate_preregistration(spec):
    require(spec.get("kind") == "gomyway-oracle-basic-pitch-preregistration", "Unexpected preregistration kind")
    require(spec.get("version") == 1, "Unsupported preregistration version")
    require(spec.get("frozenBeforeOracleInference") is True, "Preregistration must be frozen before inference")
    require(spec.get("predictionsRead") is False, "Preregistration must be prediction-blind")
    require(spec.get("customerDeliveryEligible") is False, "Preregistration cannot authorize delivery")

    oracle = spec.get("oracleInput", {})
    source = spec.get("canonicalSource", {})
    for value, name in [
        (oracle.get("first30WavSha256"), "oracle audio"),
        (oracle.get("sourceM4aSha256"), "oracle source"),
        (source.get("audioSha256"), "canonical source"),
    ]:
        require(valid_sha256(value), f"Invalid {name} identity")

    runtime = spec.get("runtime", {})
    require(runtime.get("pythonVersion") == "3.10.21", "Python runtime identity changed")
    require(runtime.get("basicPitchVersion") == "0.4.0", "Basic Pitch version changed")
    require(runtime.get("modelSha256") == EXPECTED_MODEL_SHA256, "Basic Pitch model identity changed")
    require(runtime.get("runnerGitBlob") == EXPECTED_RUNNER_GIT_BLOB, "Inference runner identity changed")
    require(valid_sha256(runtime.get("requirementsLockSha256")), "Invalid runtime lock identity")
    require(runtime.get("settings") == EXPECTED_SETTINGS, "Inference settings changed")

    transform = spec.get("timeTransform", {})
    offset, scale = transform.get("offsetSeconds"), transform.get("scale")
    require(finite(offset) and finite(scale) and scale > 0, "Invalid oracle time transform")
    require(transform.get("equation") == "isolatedSeconds = offsetSeconds + scale * sourceSeconds",
            "Unexpected time-transform semantics")

    scoring = spec.get("scoring", {})
    window = scoring.get("windowSeconds")
    require(isinstance(window, list) and len(window) == 2 and all(finite(v) for v in window)
            and 0 <= window[0] < window[1], "Invalid scoring window")
    require(finite(scoring.get("onsetToleranceSeconds")) and scoring["onsetToleranceSeconds"] == 0.05,
            "Scoring tolerance changed")
    require(valid_sha256(scoring.get("labelsSha256")) and valid_sha256(scoring.get("alignmentSha256")),
            "Reviewed bundle identities missing")
    require(scoring.get("scope") == "whole-mix-to-rhythm", "Scoring scope changed")
    return offset, scale


def project_predictions(prediction, prereg, *, prediction_sha256, prereg_sha256):
    offset, scale = validate_preregistration(prereg)
    oracle_sha = prereg["oracleInput"]["first30WavSha256"]
    source_sha = prereg["canonicalSource"]["audioSha256"]

    require(prediction.get("kind") == "whole-mix-basic-pitch-development-only",
            "Unexpected Basic Pitch result kind")
    require(prediction.get("audioSha256") == oracle_sha, "Oracle prediction audio identity mismatch")
    require(prediction.get("roleAssignment") is None, "Oracle result must not claim a role")
    require(prediction.get("customerDeliveryEligible") is False, "Oracle result cannot authorize delivery")
    require(prediction.get("accuracyScore") is None, "Oracle inference cannot carry an accuracy score")
    events = prediction.get("events")
    require(isinstance(events, list), "Missing Basic Pitch event list")

    projected = []
    dropped_before_zero = 0
    for index, row in enumerate(events):
        start, end, midi = row.get("start"), row.get("end"), row.get("midi")
        require(finite(start) and finite(end) and 0 <= start < end, "Invalid Basic Pitch event time")
        require(isinstance(midi, int) and not isinstance(midi, bool) and 0 <= midi <= 127,
                "Invalid Basic Pitch MIDI")
        source_start = (start - offset) / scale
        source_end = (end - offset) / scale
        if source_start < 0:
            dropped_before_zero += 1
            continue
        require(source_end > source_start, "Projected event duration is not positive")
        event = {
            "id": f"oracle-{index}",
            "start": source_start,
            "end": source_end,
            "midi": midi,
        }
        amplitude = row.get("amplitude")
        if amplitude is not None:
            require(finite(amplitude), "Invalid Basic Pitch amplitude")
            event["amplitude"] = amplitude
        projected.append(event)

    return {
        "kind": "oracle-basic-pitch-source-clock-projection",
        "version": 1,
        "audioSha256": source_sha,
        "originAudioSha256": oracle_sha,
        "originPredictionSha256": prediction_sha256,
        "preregistrationSha256": prereg_sha256,
        "timeTransform": {
            "equation": "sourceSeconds = (isolatedSeconds - offsetSeconds) / scale",
            "offsetSeconds": offset,
            "scale": scale,
        },
        "sourceTimelineScoringWindow": prereg["scoring"]["windowSeconds"],
        "events": projected,
        "inputEventCount": len(events),
        "projectedEventCount": len(projected),
        "droppedBeforeSourceZero": dropped_before_zero,
        "roleAssignment": None,
        "accuracyScore": None,
        "customerDeliveryEligible": False,
        "limitations": [
            "This projection changes only the clock; it does not alter MIDI, add notes, delete in-window errors or assign rhythm/lead role truth.",
            "The affine relation was frozen before oracle transcription and must not be retuned against prediction matches.",
            "Events whose projected onset precedes source time zero are excluded before scoring because the onset scorer rejects negative timestamps.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    for flag in ["prediction", "preregistration", "output"]:
        parser.add_argument("--" + flag, required=True)
    args = parser.parse_args()
    output = Path(args.output)
    require(not output.exists(), "Refusing to overwrite existing projection")
    pred_raw, prediction = load_json_bytes(args.prediction)
    spec_raw, prereg = load_json_bytes(args.preregistration)
    result = project_predictions(
        prediction,
        prereg,
        prediction_sha256=sha256_bytes(pred_raw),
        prereg_sha256=sha256_bytes(spec_raw),
    )
    with output.open("x") as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({
        "inputEventCount": result["inputEventCount"],
        "projectedEventCount": result["projectedEventCount"],
        "droppedBeforeSourceZero": result["droppedBeforeSourceZero"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
