from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_ai_tab_gpu_worker import image as separator_gpu_image


APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
PROTECTED_PIPELINE_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"

MODULES = (
    "v143_ai_tab_gpu_worker",
    "v143_production_separator",
    "v143_seeded_separator",
    "v143_seeded_audio_separator_cli",
    "v143_deterministic_separator",
)

app = modal.App("dadrock-v143-separator-cold-determinism-probe")

image = separator_gpu_image.add_local_python_source(*MODULES)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_suffix(value: str) -> str:
    suffix = str(value or ".audio").strip().lower()
    return suffix if suffix in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"} else ".audio"


def _normalize(source: Path, destination: Path) -> None:
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", str(source),
            "-map", "0:a:0", "-vn", "-ar", "44100", "-ac", "2",
            "-c:a", "pcm_s16le", str(destination),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not destination.exists() or destination.stat().st_size <= 0:
        raise RuntimeError((result.stderr or result.stdout or "normalization failed")[-4000:])


@app.function(image=image, gpu="L4", timeout=1800, memory=12288)
def probe(source_audio: bytes, suffix: str = ".audio") -> dict[str, Any]:
    if not source_audio:
        raise ValueError("source audio empty")

    from v143_deterministic_separator import build_deterministic_v143_stems

    with tempfile.TemporaryDirectory(prefix="v143-separator-cold-proof-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"source{_safe_suffix(suffix)}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        _normalize(source, normalized)

        stems = build_deterministic_v143_stems(normalized, root / "stems")
        direct = Path(str(stems.get("directGuitar") or ""))
        roformer = Path(str(stems.get("roformerInstrumental") or ""))
        cascade = Path(str(stems.get("cascadeGuitar") or ""))
        for name, path in (("direct", direct), ("roformer", roformer), ("cascade", cascade)):
            if not path.exists() or path.stat().st_size <= 0:
                raise RuntimeError(f"{name} separator output missing")

        source_sha = _sha256_bytes(source_audio)
        return {
            "schemaVersion": 1,
            "gate": "v143-separator-cold-determinism-probe",
            "sourceSha256": source_sha,
            "normalizedWavSha256": _sha256_file(normalized),
            "directGuitarSha256": _sha256_file(direct),
            "roformerInstrumentalSha256": _sha256_file(roformer),
            "cascadeGuitarSha256": _sha256_file(cascade),
            "directBytes": direct.stat().st_size,
            "roformerBytes": roformer.stat().st_size,
            "cascadeBytes": cascade.stat().st_size,
            "settings": stems.get("settings"),
            "invariants": {
                "approvedFixture": source_sha == APPROVED_AUDIO_SHA256,
                "referenceFree": stems.get("referenceFree") is True,
                "deterministicFlag": stems.get("deterministic") is True,
                "productionModified": False,
                "protectedPipelineModified": False,
            },
        }


@app.local_entrypoint(name="approved_audio")
def approved_audio(
    audio_path: str = "public/gomywayfullaitest.m4a",
    output_path: str = "debug/v143-contextual-prune/separator-cold-determinism-pass.json",
) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"approved fixture missing: {source}")
    data = source.read_bytes()
    digest = _sha256_bytes(data)
    if digest != APPROVED_AUDIO_SHA256:
        raise RuntimeError(f"approved fixture SHA changed: {digest}")
    result = probe.remote(data, source.suffix)
    invariants = result.get("invariants") or {}
    required = ("approvedFixture", "referenceFree", "deterministicFlag")
    failed = [name for name in required if invariants.get(name) is not True]
    if invariants.get("productionModified") is not False:
        failed.append("productionModified")
    if invariants.get("protectedPipelineModified") is not False:
        failed.append("protectedPipelineModified")
    if failed:
        raise RuntimeError(f"separator cold proof invariant failure: {failed}")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    print(f"WROTE={output}")


if __name__ == "__main__":
    pass
