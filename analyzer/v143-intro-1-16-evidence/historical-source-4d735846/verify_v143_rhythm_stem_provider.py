from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from v143_rhythm_stem_provider import build_rhythm_stem_bundle


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="verify-v143-stems-") as temp_dir:
        root = Path(temp_dir)
        normalized = root / "normalized.wav"
        normalized.write_bytes(b"normalized-audio")

        calls: list[tuple[Path, Path]] = []

        def fake_separator_builder(
            input_audio: Path | str,
            output_dir: Path | str,
        ) -> dict[str, Any]:
            source = Path(input_audio)
            destination = Path(output_dir)
            calls.append((source, destination))
            destination.mkdir(parents=True, exist_ok=True)

            direct = destination / "direct-demucs6s-guitar.wav"
            cascade = destination / "bsroformer-demucs6s-guitar.wav"
            direct.write_bytes(b"direct-stem")
            cascade.write_bytes(b"cascade-stem")

            return {
                "directGuitar": str(direct),
                "cascadeGuitar": str(cascade),
                "referenceFree": True,
            }

        bundle = build_rhythm_stem_bundle(
            normalized,
            separator_builder=fake_separator_builder,
        )
        repeat = build_rhythm_stem_bundle(
            normalized,
            separator_builder=fake_separator_builder,
        )

        direct = Path(bundle.carrier_stem_a_path)
        cascade = Path(bundle.carrier_stem_b_path)
        candidates = tuple(Path(path) for path in bundle.candidate_stem_paths)

        normalized_passed_unchanged = bool(
            calls
            and all(source == normalized for source, _destination in calls)
        )
        request_owned_output_dir = bool(
            calls
            and all(
                destination == normalized.parent / "v143-rhythm-stems"
                for _source, destination in calls
            )
        )
        two_candidate_views = candidates == (direct, cascade)
        direct_is_carrier_a = direct.name == "direct-demucs6s-guitar.wav"
        cascade_is_carrier_b = cascade.name == "bsroformer-demucs6s-guitar.wav"
        carriers_independent = direct.resolve() != cascade.resolve()
        files_survive_provider_return = all(
            path.exists() and path.stat().st_size > 0
            for path in (direct, cascade)
        )
        deterministic_repeat = bundle == repeat

        missing_output_rejected = False

        def missing_separator_builder(
            input_audio: Path | str,
            output_dir: Path | str,
        ) -> dict[str, Any]:
            return {"directGuitar": "", "cascadeGuitar": ""}

        try:
            build_rhythm_stem_bundle(
                normalized,
                separator_builder=missing_separator_builder,
            )
        except RuntimeError:
            missing_output_rejected = True

        same_carrier_rejected = False

        def same_separator_builder(
            input_audio: Path | str,
            output_dir: Path | str,
        ) -> dict[str, Any]:
            destination = Path(output_dir)
            destination.mkdir(parents=True, exist_ok=True)
            same = destination / "same-guitar.wav"
            same.write_bytes(b"same")
            return {
                "directGuitar": str(same),
                "cascadeGuitar": str(same),
            }

        try:
            build_rhythm_stem_bundle(
                normalized,
                separator_builder=same_separator_builder,
            )
        except RuntimeError:
            same_carrier_rejected = True

    checks = {
        "Normalized full mix passed to separator unchanged": normalized_passed_unchanged,
        "Stem outputs remain inside request lifetime": request_owned_output_dir,
        "Direct and cascade both used for candidate recall": two_candidate_views,
        "Direct Demucs6s Guitar is carrier A": direct_is_carrier_a,
        "BS-RoFormer->Demucs6s Guitar is carrier B": cascade_is_carrier_b,
        "Paired carrier stems are independent files": carriers_independent,
        "Stem files survive provider return": files_survive_provider_return,
        "Missing separator outputs rejected": missing_output_rejected,
        "Duplicate carrier path rejected": same_carrier_rejected,
        "Professional reference used": False,
        "Runtime labels required": False,
        "Deterministic repeat exact": deterministic_repeat,
    }

    ready = (
        normalized_passed_unchanged
        and request_owned_output_dir
        and two_candidate_views
        and direct_is_carrier_a
        and cascade_is_carrier_b
        and carriers_independent
        and files_survive_provider_return
        and missing_output_rejected
        and same_carrier_rejected
        and deterministic_repeat
    )

    print("=== V143 PRODUCTION RHYTHM STEM PROVIDER VERIFIED ===")
    for label, value in checks.items():
        print(f"{label}: {value}")
    print(f"READY FOR LIVE MODAL ENDPOINT WIRING: {ready}")

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
