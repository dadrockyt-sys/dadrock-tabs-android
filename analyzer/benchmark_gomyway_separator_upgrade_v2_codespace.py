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
OUTPUT_PATH = PUBLIC / "gomyway-separator-upgrade-benchmark-v2-codespace.json"
MANIFEST_PATH = PUBLIC / "gomyway-separator-upgrade-benchmark-v2-codespace-manifest.json"
STEM_DIR = PUBLIC / "separator-benchmark-v2"

AUDIO_CANDIDATES = (
    PUBLIC / "gomywayfullaitest.m4a",
    PUBLIC / "gomywayfullaitest.wav",
    PUBLIC / "gomywayfullaitest.mp3",
)

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

    probe = subprocess.run(
        [sys.executable, "-m", "audio_separator", "--help"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if probe.returncode == 0:
        return [sys.executable, "-m", "audio_separator"]

    raise RuntimeError(
        "audio-separator is unavailable. Install with: "
        "python -m pip install -U audio-separator onnxruntime"
    )


def discover_audio(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(
        p for p in directory.rglob("*")
        if p.is_file() and p.suffix.lower() in {".wav", ".flac", ".mp3", ".m4a", ".ogg"}
    )


def choose_stem(paths: list[Path], keywords: tuple[str, ...]) -> Path | None:
    scored: list[tuple[int, int, Path]] = []
    for path in paths:
        lower = path.name.lower()
        score = sum(1 for keyword in keywords if keyword.lower() in lower)
        if score:
            scored.append((score, path.stat().st_size, path))
    if not scored:
        return None
    scored.sort(reverse=True)
    return scored[0][2]


def separate_demucs_guitar(cli: list[str], input_audio: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = cli + [
        str(input_audio),
        "--model_filename", DEMUCS_6S_MODEL,
        "--output_dir", str(output_dir),
        "--output_format", "WAV",
        "--single_stem", "Guitar",
        "--demucs_shifts", "1",
        "--demucs_overlap", "0.10",
        "--demucs_segment_size", "6",
        "--use_soundfile",
    ]
    started = time.monotonic()
    result = run(command)
    elapsed = round(time.monotonic() - started, 2)
    outputs = discover_audio(output_dir)
    guitar = choose_stem(outputs, ("guitar",))
    return {
        "model": DEMUCS_6S_MODEL,
        "returnCode": result.returncode,
        "elapsedSeconds": elapsed,
        "outputs": [str(p) for p in outputs],
        "selectedGuitarStem": str(guitar) if guitar else None,
        "passed": result.returncode == 0 and guitar is not None,
        "guitar": guitar,
        "settings": {
            "singleStem": "Guitar",
            "shifts": 1,
            "overlap": 0.10,
            "segmentSize": 6,
            "useSoundfile": True,
            "codespaceSafe": True,
        },
    }


def separate_roformer_instrumental(cli: list[str], input_audio: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = cli + [
        str(input_audio),
        "--model_filename", BS_ROFORMER_MODEL,
        "--output_dir", str(output_dir),
        "--output_format", "WAV",
        "--single_stem", "Instrumental",
        "--mdxc_batch_size", "1",
        "--use_soundfile",
    ]
    started = time.monotonic()
    result = run(command)
    elapsed = round(time.monotonic() - started, 2)
    outputs = discover_audio(output_dir)
    instrumental = choose_stem(outputs, ("instrumental", "no_vocals", "novocals", "other"))
    return {
        "model": BS_ROFORMER_MODEL,
        "returnCode": result.returncode,
        "elapsedSeconds": elapsed,
        "outputs": [str(p) for p in outputs],
        "selectedInstrumentalStem": str(instrumental) if instrumental else None,
        "passed": result.returncode == 0 and instrumental is not None,
        "instrumental": instrumental,
        "settings": {
            "singleStem": "Instrumental",
            "batchSize": 1,
            "useSoundfile": True,
            "codespaceSafe": True,
        },
    }


def export(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if not destination.exists() or destination.stat().st_size <= 0:
        raise RuntimeError(f"Failed to export benchmark stem: {destination}")


def main() -> None:
    audio = find_audio()
    cli = find_audio_separator()
    STEM_DIR.mkdir(parents=True, exist_ok=True)

    direct_public = STEM_DIR / "gomyway-demucs6s-direct-guitar.wav"
    cascade_public = STEM_DIR / "gomyway-bsroformer-demucs6s-guitar.wav"

    print("GOMYWAY SEPARATOR UPGRADE BENCHMARK V2 - CODESPACE SAFE")
    print("Input:", audio.relative_to(ROOT))
    print("Control pitch F1:", CONTROL_PITCH_F1)
    print("Demucs safety settings: single Guitar, shifts=1, overlap=0.10, segment=6, soundfile=True")
    print("Production separator changed: False")
    print()

    with tempfile.TemporaryDirectory(prefix="jimmy-separator-v2-") as tmp:
        tmp_root = Path(tmp)

        print("STAGE 1/3: Direct Demucs 6-stem guitar extraction")
        direct = separate_demucs_guitar(cli, audio, tmp_root / "direct")
        if not direct["passed"]:
            raise RuntimeError(
                "Direct Demucs stage failed or produced no Guitar stem. "
                f"returnCode={direct['returnCode']} outputs={direct['outputs']}"
            )
        export(direct["guitar"], direct_public)
        direct["benchmarkStem"] = str(direct_public.relative_to(ROOT))
        direct["guitar"] = None
        print("Direct guitar exported:", direct_public.relative_to(ROOT))
        print()

        print("STAGE 2/3: BS-RoFormer instrumental cleanup")
        roformer = separate_roformer_instrumental(cli, audio, tmp_root / "roformer")
        if not roformer["passed"]:
            raise RuntimeError(
                "BS-RoFormer stage failed or produced no Instrumental stem. "
                f"returnCode={roformer['returnCode']} outputs={roformer['outputs']}"
            )
        print("Instrumental cleanup complete")
        print()

        print("STAGE 3/3: Demucs guitar extraction from cleaned instrumental")
        cascade = separate_demucs_guitar(cli, roformer["instrumental"], tmp_root / "cascade")
        if not cascade["passed"]:
            raise RuntimeError(
                "Cascade Demucs stage failed or produced no Guitar stem. "
                f"returnCode={cascade['returnCode']} outputs={cascade['outputs']}"
            )
        export(cascade["guitar"], cascade_public)
        cascade["benchmarkStem"] = str(cascade_public.relative_to(ROOT))
        cascade["guitar"] = None
        roformer["instrumental"] = None
        print("Cascade guitar exported:", cascade_public.relative_to(ROOT))

    output = {
        "schemaVersion": 2,
        "passed": True,
        "benchmarkType": "separator-upgrade-codespace-safe-read-only",
        "inputAudio": str(audio.relative_to(ROOT)),
        "controlMetrics": {
            "globalPitchF1": CONTROL_PITCH_F1,
            "globalExactTabF1": CONTROL_EXACT_TAB_F1,
            "priorityBatchMatchedPitchTokens": CONTROL_PRIORITY_MATCHED,
            "priorityBatchMissingPitchTokens": CONTROL_PRIORITY_MISSING,
            "priorityBatchExtraPitchTokens": CONTROL_PRIORITY_EXTRA,
        },
        "directDemucsGuitar": direct,
        "bsRoFormerInstrumental": roformer,
        "bsRoFormerThenDemucsGuitar": cascade,
        "benchmarkStems": [
            str(direct_public.relative_to(ROOT)),
            str(cascade_public.relative_to(ROOT)),
        ],
        "qualityNote": (
            "Codespace benchmark uses one Demucs shift and reduced overlap/segment size for resource safety. "
            "Winning architecture should be rerun on Modal GPU at maximum-quality settings before production promotion."
        ),
        "professionalReferenceUsedForSeparation": False,
        "protected949CandidateModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "automaticApplyAllowed": False,
        "readyForIdenticalAnalyzerComparison": True,
        "recommendedNextAction": "analyze-and-grade-gomyway-separator-benchmark-stems-v2",
    }
    manifest = {
        "schemaVersion": 2,
        "passed": True,
        "benchmarkStems": output["benchmarkStems"],
        "controlGlobalPitchF1": CONTROL_PITCH_F1,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": output["recommendedNextAction"],
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print()
    print("GOMYWAY SEPARATOR UPGRADE BENCHMARK V2 COMPLETE")
    print("Passed: True")
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
    print("Recommended next action: analyze-and-grade-gomyway-separator-benchmark-stems-v2")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
