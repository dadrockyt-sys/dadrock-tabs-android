from __future__ import annotations

import inspect
import json

import modal

try:
    import modal_analyzer_v7 as analyzer
except ImportError:
    from analyzer import modal_analyzer_v7 as analyzer

app = modal.App("dadrock-v8-basic-pitch-training-parameter-inspection")
image = analyzer.image.add_local_python_source(
    "modal_analyzer_v7",
    "modal_analyzer",
    "production_chord_diagnostics",
    "chord_sustain",
    "reference_aware_harmony",
    "production_lead_technique_diagnostics",
    "lead_technique_diagnostics_v7",
    "production_bass_technique_diagnostics",
    "bass_technique_diagnostics_v7",
)


@app.function(image=image, timeout=300, memory=2048)
def inspect_predict_signature() -> bytes:
    from basic_pitch.inference import predict

    signature = inspect.signature(predict)
    parameters = []

    for name, parameter in signature.parameters.items():
        default = None
        has_default = parameter.default is not inspect.Parameter.empty
        if has_default:
            try:
                json.dumps(parameter.default)
                default = parameter.default
            except TypeError:
                default = repr(parameter.default)

        annotation = None
        if parameter.annotation is not inspect.Parameter.empty:
            annotation = repr(parameter.annotation)

        parameters.append(
            {
                "name": name,
                "kind": str(parameter.kind),
                "hasDefault": has_default,
                "default": default,
                "annotation": annotation,
            }
        )

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "basic-pitch-read-only-training-parameter-inspection",
        "passed": bool(parameters),
        "predictSignature": str(signature),
        "parameters": parameters,
        "candidateTrainingParameters": [
            item["name"]
            for item in parameters
            if item["name"]
            in {
                "onset_threshold",
                "frame_threshold",
                "minimum_note_length",
                "minimum_frequency",
                "maximum_frequency",
                "melodia_trick",
                "multiple_pitch_bends",
            }
        ],
        "safeguards": {
            "readOnlyInspection": True,
            "audioNotAnalyzed": True,
            "doesNotModifyV7OrV8Events": True,
            "doesNotModifyLockedTiming": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
            "noSyntheticNotes": True,
        },
    }

    return json.dumps(report, separators=(",", ":")).encode("utf-8")


def main() -> None:
    with app.run():
        result_bytes = inspect_predict_signature.remote()

    report = json.loads(result_bytes.decode("utf-8"))

    print("Basic Pitch training parameter inspection pass:", report["passed"])
    print("Predict signature:", report["predictSignature"])
    print(
        "Candidate training parameters:",
        report["candidateTrainingParameters"],
    )
    print("Renderer changed: False")
    print("Protected baselines changed: False")

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
