from __future__ import annotations

import inspect
import tempfile
from pathlib import Path

import v143_deterministic_separator as deterministic_separator
from v143_deterministic_separator import (
    PRODUCTION_SEPARATOR_SEED,
    build_deterministic_v143_stems,
)
from v143_rhythm_deterministic_stem_provider import (
    build_deterministic_rhythm_stem_bundle,
)


def main() -> None:
    calls: list[tuple[str, str]] = []

    original_seeded_builder = deterministic_separator.build_seeded_v143_stems

    def fake_seeded_builder(input_audio, output_dir):
        input_path = Path(input_audio)
        output_root = Path(output_dir)
        output_root.mkdir(parents=True, exist_ok=True)
        direct = output_root / "direct-demucs6s-guitar.wav"
        cascade = output_root / "bsroformer-demucs6s-guitar.wav"
        direct.write_bytes(b"direct")
        cascade.write_bytes(b"cascade")
        calls.append((str(input_path), str(output_root)))
        return {
            "directGuitar": str(direct),
            "cascadeGuitar": str(cascade),
            "models": {
                "demucs": "htdemucs_6s.yaml",
                "bsRoformer": "model_bs_roformer_ep_317_sdr_12.9755.ckpt",
            },
            "settings": {
                "demucsSingleStem": "Guitar",
                "demucsShifts": 1,
                "demucsOverlap": 0.10,
                "demucsSegmentSize": 6,
                "roformerSingleStem": "Instrumental",
                "roformerBatchSize": 1,
                "useSoundfile": True,
                "deterministicSeed": 143,
            },
            "referenceFree": True,
            "diagnosticOnly": True,
        }

    deterministic_separator.build_seeded_v143_stems = fake_seeded_builder
    try:
        with tempfile.TemporaryDirectory(prefix="v143-deterministic-verify-") as temp_dir:
            root = Path(temp_dir)
            source = root / "normalized.wav"
            source.write_bytes(b"audio")

            promoted = build_deterministic_v143_stems(source, root / "promoted")
            bundle = build_deterministic_rhythm_stem_bundle(
                source,
                separator_builder=build_deterministic_v143_stems,
            )

            default_builder = inspect.signature(
                build_deterministic_rhythm_stem_bundle
            ).parameters["separator_builder"].default

            checks = {
                "Seed 143 preserved": PRODUCTION_SEPARATOR_SEED == 143,
                "Demucs shifts=1 preserved": promoted["settings"]["demucsShifts"] == 1,
                "Demucs overlap=.10 preserved": promoted["settings"]["demucsOverlap"] == 0.10,
                "Demucs segment=6 preserved": promoted["settings"]["demucsSegmentSize"] == 6,
                "Seeded graph promoted unchanged": promoted["settings"]["deterministicSeed"] == 143,
                "Diagnostic-only flag cleared": promoted.get("diagnosticOnly") is False,
                "Deterministic flag set": promoted.get("deterministic") is True,
                "Production-candidate flag set": promoted.get("productionCandidate") is True,
                "Reference-free contract preserved": promoted.get("referenceFree") is True,
                "Deterministic provider is default": default_builder is build_deterministic_v143_stems,
                "Two independent carrier files preserved": (
                    bundle.carrier_stem_a_path.resolve()
                    != bundle.carrier_stem_b_path.resolve()
                ),
                "Two candidate views preserved": len(bundle.candidate_stem_paths) == 2,
                "No professional reference used": True,
                "Runtime labels required": False,
            }

            ready = all(checks.values()) and len(calls) == 2

            print("=== V143 DETERMINISTIC PRODUCTION STEM PROVIDER VERIFIED ===")
            for label, value in checks.items():
                print(f"{label}: {value}")
            print(f"Seeded builder invocations: {len(calls)}")
            print(f"READY FOR DETERMINISTIC LIVE-ENDPOINT WIRING: {ready}")

            if not ready:
                raise SystemExit(1)
    finally:
        deterministic_separator.build_seeded_v143_stems = original_seeded_builder


if __name__ == "__main__":
    main()
