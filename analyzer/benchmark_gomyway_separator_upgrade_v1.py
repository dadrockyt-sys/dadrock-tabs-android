from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-separator-upgrade-benchmark-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-separator-upgrade-benchmark-v1-manifest.json"

AUDIO_CANDIDATES = (
    PUBLIC / "gomywayfullaitest.m4a",
    PUBLIC / "gomywayfullaitest.wav",
    PUBLIC / "gomywayfullaitest.mp3",
)

# These model identifiers are intentionally explicit and remain benchmark-only.
# python-audio-separator can auto-download supported model weights on first use.
BS_ROFORMER_MODEL = os.environ.get(
    "JIMMY_BS_ROFORMER_MODEL",
    "model_bs_roformer_ep_317_sdr_12.9755.ckpt",
)
DEMUCS_6S_MODEL = os.environ.get("JIMMY_DEMUCS_6S_MODEL", "htdemucs_6s.yaml")

CONTROL_PITCH_F1 = 4.73
CONTROL_EXACT_TAB_F1 = 2.86
CONTROL_PRIORITY_MATCHED = 0
CONTROL_PRIORITY_MISSING = 51
CONTROL_PRIORITY_EXTRA = 187


def run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def find_audio() -> Path:
    for path in AUDIO_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError(
        "Training audio not found. Expected one of: "
        + ", ".join(str(path.relative_to(ROOT)) for path in AUDIO_CANDIDATES)
    )


def find_audio_separator() -> list[str]:
    executable = shutil.which("audio-separator")
    if executable:
        return [executable]

    probe = run([sys.executable, "-m", "audio_separator", "--help"])
    if probe.returncode == 0:
        return [sys.executable, "-m", "audio_separator"]

    raise RuntimeError(
        "python-audio-separator is not installed in this environment. "
        "Install it in the active .venv-audio-separation environment with: "
        "python -m pip install -U audio-separator"
    )


def list_models(cli: list[str]) -> str:
    result = run(cli + ["--list_models", "--list_format", "json"])
    if result.returncode != 0:
        raise RuntimeError("audio-separator --list_models failed:\n" + result.stdout[-4000:])
    return result.stdout


def model_available(model_listing: str, model_name: str) -> bool:
    return model_name in model_listing


def discover_outputs(directory: Path) -> list[Path]:
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in {".wav", ".flac", ".mp3", ".m4a", ".ogg"}
    )


def choose_stem(paths: list[Path], keywords: tuple[str, ...]) -> Path | None:
    scored: list[tuple[int, Path]] = []
    for path in paths:
        name = path.name.lower()
        score = sum(1 for keyword in keywords if keyword in name)
        if score:
            scored.append((score, path))
    if not scored:
        return None
    scored.sort(key=lambda row: (row[0], row[1].stat().st_size), reverse=True)
    return scored[0][1]


def separate(
    cli: list[str],
    input_audio: Path,
    model: str,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    before = set(discover_outputs(output_dir))
    started = time.monotonic()
    command = cli + [
        str(input_audio),
        "--model_filename",
        model,
        "--output_dir",
        str(output_dir),
        "--output_format",
        "WAV",
    ]
    result = run(command)
    elapsed = round(time.monotonic() - started, 2)
    after = set(discover_outputs(output_dir))
    created = sorted(after - before)
    return {
        "model": model,
        "command": command,
        "returnCode": result.returncode,
        "elapsedSeconds": elapsed,
        "outputs": [str(path) for path in created],
        "logTail": result.stdout[-6000:],
    }


def copy_benchmark_stem(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> None:
    audio = find_audio()
    cli = find_audio_separator()
    models = list_models(cli)

    required = {
        "bsRoFormer": BS_ROFORMER_MODEL,
        "demucs6s": DEMUCS_6S_MODEL,
    }
    availability = {name: model_available(models, value) for name, value in required.items()}
    missing = [required[name] for name, available in availability.items() if not available]
    if missing:
        raise RuntimeError(
            "Required benchmark model(s) not present in audio-separator registry: "
            + ", ".join(missing)
            + ". Run `audio-separator --list_models` and set JIMMY_BS_ROFORMER_MODEL or "
            "JIMMY_DEMUCS_6S_MODEL to an available equivalent if the registry changed."
        )

    public_stem_dir = PUBLIC / "separator-benchmark-v1"
    public_stem_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="jimmy-separator-v1-") as tmp:
        tmp_root = Path(tmp)

        # Candidate A: direct 6-stem Demucs guitar extraction.
        direct_dir = tmp_root / "demucs6s-direct"
        direct = separate(cli, audio, DEMUCS_6S_MODEL, direct_dir)
        direct_outputs = [Path(path) for path in direct["outputs"]]
        direct_guitar = choose_stem(direct_outputs, ("guitar",))
        direct["selectedGuitarStem"] = str(direct_guitar) if direct_guitar else None
        direct["passed"] = direct["returnCode"] == 0 and direct_guitar is not None
        if not direct["passed"]:
            raise RuntimeError(
                "Direct htdemucs_6s benchmark did not produce a recognizable guitar stem.\n"
                + direct["logTail"]
            )
        direct_public = public_stem_dir / "gomyway-demucs6s-direct-guitar.wav"
        copy_benchmark_stem(direct_guitar, direct_public)
        direct["benchmarkStem"] = str(direct_public.relative_to(ROOT))

        # Candidate B: BS-RoFormer vocal cleanup, then 6-stem Demucs guitar extraction.
        roformer_dir = tmp_root / "bs-roformer"
        roformer = separate(cli, audio, BS_ROFORMER_MODEL, roformer_dir)
        roformer_outputs = [Path(path) for path in roformer["outputs"]]
        instrumental = choose_stem(
            roformer_outputs,
            ("instrumental", "no_vocals", "novocals", "other"),
        )
        roformer["selectedInstrumentalStem"] = str(instrumental) if instrumental else None
        roformer["passed"] = roformer["returnCode"] == 0 and instrumental is not None
        if not roformer["passed"]:
            raise RuntimeError(
                "BS-RoFormer benchmark did not produce a recognizable instrumental stem.\n"
                + roformer["logTail"]
            )

        cascade_dir = tmp_root / "roformer-then-demucs6s"
        cascade = separate(cli, instrumental, DEMUCS_6S_MODEL, cascade_dir)
        cascade_outputs = [Path(path) for path in cascade["outputs"]]
        cascade_guitar = choose_stem(cascade_outputs, ("guitar",))
        cascade["selectedGuitarStem"] = str(cascade_guitar) if cascade_guitar else None
        cascade["passed"] = cascade["returnCode"] == 0 and cascade_guitar is not None
        if not cascade["passed"]:
            raise RuntimeError(
                "RoFormer -> htdemucs_6s cascade did not produce a recognizable guitar stem.\n"
                + cascade["logTail"]
            )
        cascade_public = public_stem_dir / "gomyway-bsroformer-demucs6s-guitar.wav"
        copy_benchmark_stem(cascade_guitar, cascade_public)
        cascade["benchmarkStem"] = str(cascade_public.relative_to(ROOT))

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "separator-upgrade-read-only-audio-stem-generation",
        "inputAudio": str(audio.relative_to(ROOT)),
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "automaticApplyAllowed": False,
        "protected949CandidateModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "professionalReferenceUsedForSeparation": False,
        "professionalReferenceRole": "downstream-grading-only",
        "controlMetrics": {
            "globalPitchF1": CONTROL_PITCH_F1,
            "globalExactTabF1": CONTROL_EXACT_TAB_F1,
            "priorityBatchMatchedPitchTokens": CONTROL_PRIORITY_MATCHED,
            "priorityBatchMissingPitchTokens": CONTROL_PRIORITY_MISSING,
            "priorityBatchExtraPitchTokens": CONTROL_PRIORITY_EXTRA,
        },
        "modelAvailability": availability,
        "candidates": {
            "demucs6sDirectGuitar": direct,
            "bsRoFormerThenDemucs6sGuitar": {
                "roformerStage": roformer,
                "guitarStage": cascade,
                "benchmarkStem": cascade["benchmarkStem"],
                "passed": True,
            },
        },
        "benchmarkStems": [
            str(direct_public.relative_to(ROOT)),
            str(cascade_public.relative_to(ROOT)),
        ],
        "readyForIdenticalAnalyzerComparison": True,
        "recommendedNextAction": "analyze-and-grade-gomyway-separator-benchmark-stems-v1",
    }

    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "inputAudio": str(audio.relative_to(ROOT)),
        "models": required,
        "benchmarkStems": output["benchmarkStems"],
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": output["recommendedNextAction"],
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY SEPARATOR UPGRADE BENCHMARK V1 COMPLETE")
    print("Passed: True")
    print("Input audio:", audio.relative_to(ROOT))
    print("BS-RoFormer model:", BS_ROFORMER_MODEL)
    print("Demucs 6-stem model:", DEMUCS_6S_MODEL)
    print("Direct guitar stem:", direct_public.relative_to(ROOT))
    print("RoFormer -> Demucs guitar stem:", cascade_public.relative_to(ROOT))
    print("Control global pitch F1:", CONTROL_PITCH_F1)
    print("Control priority batch matched/missing/extra: 0 / 51 / 187")
    print("Professional reference used for separation: False")
    print("Protected 949-event candidate modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Ready for identical analyzer comparison: True")
    print("Recommended next action: analyze-and-grade-gomyway-separator-benchmark-stems-v1")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
