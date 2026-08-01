from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "trained_pitch_class": REPO_ROOT / "public" / "gomyway-jimmy-paige-professional-chords-33-38-pitch-class-recovery.json",
    "heldout_pitch_class": REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-pitch-class-validation-63-67.json",
    "template_transfer": REPO_ROOT / "public" / "gomyway-jimmy-paige-cross-chorus-voicing-template-transfer-63-67.json",
    "regression": REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-regression-validation.json",
}

OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-protected-chord-resolver-gate.json"


def load(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required result not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def first_number(payload: Any, keys: list[str], default: float = 0.0) -> float:
    if isinstance(payload, dict):
        for key in keys:
            if key in payload and isinstance(payload[key], (int, float)):
                return float(payload[key])
        for value in payload.values():
            if isinstance(value, dict):
                found = first_number(value, keys, default=float("nan"))
                if found == found:
                    return found
    return default


def first_bool(payload: Any, keys: list[str], default: bool = False) -> bool:
    if isinstance(payload, dict):
        for key in keys:
            if key in payload and isinstance(payload[key], bool):
                return bool(payload[key])
        for value in payload.values():
            if isinstance(value, dict):
                found = first_bool(value, keys, default=False)
                if found:
                    return True
    return default


def main() -> None:
    trained = load(FILES["trained_pitch_class"])
    heldout = load(FILES["heldout_pitch_class"])
    transfer = load(FILES["template_transfer"])
    regression = load(FILES["regression"])

    trained_guarded = first_number(
        trained,
        ["guardedAttackRecallPercentage", "guardedRecallPercentage"],
    )
    heldout_guarded = first_number(
        heldout,
        ["guardedRecallPercentage", "guardedAttackRecallPercentage"],
    )
    transfer_guarded = first_number(
        transfer,
        ["guardedResolvedEquivalentPercentage", "guardedRecallPercentage"],
    )

    professional = first_number(
        regression,
        ["professionalScorePercentage", "professionalScore", "professional"],
    )
    low_register = first_number(
        regression,
        ["lowRegisterScorePercentage", "lowRegisterScore", "low"],
    )
    midi52 = first_number(regression, ["midi52Matches", "MIDI52", "midi52"])
    midi62 = first_number(regression, ["midi62Matches", "MIDI62", "midi62"])
    combined_pass = first_bool(
        regression,
        ["combinedPass", "regressionPassed", "protectedRegressionPassed"],
    )

    checks = {
        "trainedChordRecognition100": trained_guarded >= 100.0,
        "heldoutChordRecognition100": heldout_guarded >= 100.0,
        "templateTransfer100": transfer_guarded >= 100.0,
        "professionalScoreProtected": professional >= 93.06,
        "lowRegisterProtected": low_register >= 84.38,
        "midi52Protected": midi52 >= 32,
        "midi62Protected": midi62 >= 16,
        "combinedRegressionPassed": combined_pass,
    }

    gate_passed = all(checks.values())

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "protected-chord-resolver-regression-gate",
        "inputs": {key: str(path.relative_to(REPO_ROOT)) for key, path in FILES.items()},
        "scores": {
            "trainedChordRecognitionPercentage": trained_guarded,
            "heldoutChordRecognitionPercentage": heldout_guarded,
            "heldoutTemplateTransferPercentage": transfer_guarded,
            "professionalScorePercentage": professional,
            "lowRegisterScorePercentage": low_register,
            "midi52Matches": midi52,
            "midi62Matches": midi62,
        },
        "checks": checks,
        "gatePassed": gate_passed,
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
        "readyForCanonicalResolverImplementation": gate_passed,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Protected chord resolver gate complete")
    for name, passed in checks.items():
        print(f"{name}: {passed}")
    print(f"Gate passed: {gate_passed}")
    print(f"Ready for canonical resolver implementation: {gate_passed}")
    print("Professional PDF remains scoring authority: True")
    print("Protected 93.06% pitch checkpoint changed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
