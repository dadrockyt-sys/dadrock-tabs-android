#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "analyzer/final_product/bass/hz_features/bass_frequency_profile.py"
TRAINING_PATH = ROOT / "analyzer/final_product/bass/training/training_contract.json"
RESULT_PATH = ROOT / "debug/v143-contextual-prune/bass-final-product-hz-training.json"


def load_profile():
    spec = importlib.util.spec_from_file_location("bass_frequency_profile", PROFILE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Bass frequency profile")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    profile = load_profile()
    training = json.loads(TRAINING_PATH.read_text(encoding="utf-8"))
    description = profile.describe()

    checks = {
        "stringLabels": description["stringLabels"] == ["G", "D", "A", "E"],
        "openMidi": description["openMidi"] == [43, 38, 33, 28],
        "maximumFret": description["maximumFret"] == 24,
        "playableMidiBounds": (
            description["playableMidiMinimum"] == 28
            and description["playableMidiMaximum"] == 67
        ),
        "openEHz": abs(profile.position(3, 0).hz - 41.203445) < 0.00001,
        "openAHz": abs(profile.position(2, 0).hz - 55.0) < 0.00001,
        "openDHz": abs(profile.position(1, 0).hz - 73.416192) < 0.00001,
        "openGHz": abs(profile.position(0, 0).hz - 97.998859) < 0.00001,
        "highestPlayableFundamental": abs(profile.position(0, 24).hz - 391.995436) < 0.00001,
        "positionConsistency": (
            profile.pitch_matches_position(40, 3, 12)
            and profile.pitch_matches_position(45, 2, 12)
            and not profile.pitch_matches_position(41, 3, 12)
        ),
        "referenceFreeProfile": description["referenceFree"] is True,
        "profileInactive": (
            description["diagnosticOnly"] is True
            and description["analyzerRoutingEnabled"] is False
            and description["professionalStructuredIdentityEnabled"] is False
        ),
        "trainingInstrument": training.get("instrument") == "bass",
        "trainingReferenceFree": training.get("referenceFreeRuntimeRequired") is True,
        "independentWeights": (
            training.get("independentFromRhythmWeights") is True
            and training.get("independentFromLeadWeights") is True
        ),
        "rightsRequired": training.get("trainingAudioRightsRequired") is True,
        "recordingSplitRequired": training.get("recordingLevelTrainValidationTestSeparationRequired") is True,
        "noRuntimeSongIdentity": (
            training.get("fixtureSpecificRuntimeLabelsAllowed") is False
            and training.get("songIdentityRuntimeFeaturesAllowed") is False
            and training.get("artistIdentityRuntimeFeaturesAllowed") is False
        ),
        "trainingTargets": set(training.get("allowedTrainingTargets") or []) >= {
            "fundamental_pitch",
            "note_onset",
            "note_offset",
            "duration_sustain",
            "timing_grid_alignment",
            "bass_string_fret_position",
            "bass_technique_evidence",
            "confidence",
        },
        "activationDisabled": all(
            value is False
            for value in dict(training.get("activation") or {}).values()
        ),
    }

    passed = all(checks.values())
    evidence = {
        "schemaVersion": 1,
        "gate": "bass-final-product-hz-training-contract",
        "profile": description,
        "trainingContract": {
            "instrument": training.get("instrument"),
            "referenceFreeRuntimeRequired": training.get("referenceFreeRuntimeRequired"),
            "independentFromRhythmWeights": training.get("independentFromRhythmWeights"),
            "independentFromLeadWeights": training.get("independentFromLeadWeights"),
            "trainingAudioRightsRequired": training.get("trainingAudioRightsRequired"),
            "recordingLevelTrainValidationTestSeparationRequired": training.get("recordingLevelTrainValidationTestSeparationRequired"),
            "fixtureSpecificRuntimeLabelsAllowed": training.get("fixtureSpecificRuntimeLabelsAllowed"),
            "songIdentityRuntimeFeaturesAllowed": training.get("songIdentityRuntimeFeaturesAllowed"),
            "artistIdentityRuntimeFeaturesAllowed": training.get("artistIdentityRuntimeFeaturesAllowed"),
            "activation": training.get("activation"),
        },
        "checks": checks,
        "realAudioBassCanaryPassed": False,
        "trainingRunAuthorized": False,
        "customerRoutingEnabled": False,
        "professionalStructuredIdentityEnabled": False,
        "pdfRendererEnabled": False,
        "productionModified": False,
        "productionPromotionAuthorized": False,
        "passed": passed,
    }

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    if not passed:
        raise SystemExit("Bass final-product Hz/training contract failed")


if __name__ == "__main__":
    main()
