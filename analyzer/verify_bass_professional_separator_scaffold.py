from __future__ import annotations

import json
import os
from pathlib import Path

from bass_professional_separator_scaffold import (
    BASS_DEMUCS_OVERLAP,
    BASS_DEMUCS_SEGMENT_SIZE,
    BASS_DEMUCS_SHIFTS,
    BASS_SEPARATOR_SEED,
    demucs_bass_command,
    describe,
    seeded_separator_cli,
)


def option_value(command: list[str], option: str) -> str:
    index = command.index(option)
    return command[index + 1]


def main() -> None:
    description = describe()
    command = demucs_bass_command(
        ["python", "-m", "v143_seeded_audio_separator_cli"],
        Path("fixture.wav"),
        Path("bass-output"),
    )

    assert description["mode"] == "inactive-bass-professional-separator-scaffold"
    assert description["directPath"] == "audio -> Demucs6s Bass"
    assert description["cascadePath"] == (
        "audio -> BS-RoFormer Instrumental -> Demucs6s Bass"
    )
    assert description["demucsSingleStem"] == "Bass"
    assert description["demucsShifts"] == BASS_DEMUCS_SHIFTS == 1
    assert description["demucsOverlap"] == BASS_DEMUCS_OVERLAP == 0.10
    assert description["demucsSegmentSize"] == BASS_DEMUCS_SEGMENT_SIZE == 6
    assert description["deterministicSeed"] == BASS_SEPARATOR_SEED == 143
    assert description["referenceFree"] is True
    assert description["diagnosticOnly"] is True
    assert description["productionCandidate"] is False
    assert description["analyzerRoutingEnabled"] is False
    assert description["professionalStructuredIdentityEnabled"] is False
    assert description["liveEndpointDeployedOrModified"] is False
    assert description["productionModified"] is False
    assert description["productionPromotionAuthorized"] is False

    assert option_value(command, "--single_stem") == "Bass"
    assert option_value(command, "--demucs_shifts") == "1"
    assert option_value(command, "--demucs_overlap") == "0.10"
    assert option_value(command, "--demucs_segment_size") == "6"
    assert "Guitar" not in command
    assert command[-1] == "--use_soundfile"

    seeded_cli = seeded_separator_cli()
    assert seeded_cli[-2:] == ["-m", "v143_seeded_audio_separator_cli"]

    evidence = {
        "schemaVersion": 1,
        "gate": "bass-professional-separator-scaffold",
        "mode": description["mode"],
        "directPath": description["directPath"],
        "cascadePath": description["cascadePath"],
        "demucsSingleStem": "Bass",
        "demucsShifts": 1,
        "demucsOverlap": 0.10,
        "demucsSegmentSize": 6,
        "deterministicSeed": 143,
        "referenceFree": True,
        "diagnosticOnly": True,
        "productionCandidate": False,
        "analyzerRoutingEnabled": False,
        "professionalStructuredIdentityEnabled": False,
        "realAudioBassCanaryPassed": False,
        "noteTimingTechniqueQualityProven": False,
        "liveEndpointDeployedOrModified": False,
        "vercelDeploymentAttempted": False,
        "productionModified": False,
        "productionPromotionAuthorized": False,
        "paidPurchaseAttempted": False,
        "customerTokenRedeemed": False,
        "customerEmailSent": False,
        "passed": True,
    }

    result_path = os.environ.get("BASS_SEPARATOR_SCAFFOLD_RESULT_PATH", "").strip()
    if result_path:
        path = Path(result_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(evidence, indent=2))
    print("BASS PROFESSIONAL SEPARATOR SCAFFOLD VERIFIED")


if __name__ == "__main__":
    main()
