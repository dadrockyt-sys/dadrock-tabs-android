from __future__ import annotations

from pathlib import Path

from v143_seeded_separator import DEMUCS_SINGLE_THREAD_ENV


EXPECTED = {
    "CUDA_VISIBLE_DEVICES": "",
    "V143_DEMUCS_FIXED_SHIFT_RNG": "1",
    "OMP_NUM_THREADS": "1",
    "OMP_DYNAMIC": "FALSE",
    "MKL_NUM_THREADS": "1",
    "MKL_DYNAMIC": "FALSE",
    "MKL_CBWR": "COMPATIBLE",
    "OPENBLAS_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "TBB_NUM_THREADS": "1",
    "ATEN_CPU_CAPABILITY": "avx2",
    "ONEDNN_MAX_CPU_ISA": "AVX2",
    "DNNL_MAX_CPU_ISA": "AVX2",
}

FORBIDDEN = (
    "Professionalexample",
    "professional-rhythm-complete",
    "rhythm-professional-holdout-score",
    "Songsterr",
    "Are You Gonna Go My Way",
    "Lenny Kravitz",
    "Craig Ross",
)


def main() -> None:
    actual = dict(DEMUCS_SINGLE_THREAD_ENV)
    missing = {key: value for key, value in EXPECTED.items() if actual.get(key) != value}
    if missing:
        raise SystemExit(f"dispatch control mismatch: {missing}")

    source = Path(__file__).with_name("v143_seeded_separator.py").read_text(encoding="utf-8")
    source += "\n" + Path(__file__).with_name("v143_seeded_audio_separator_cli.py").read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN if token in source]
    if hits:
        raise SystemExit(f"forbidden scorer/source token in reference-free dispatch path: {hits}")

    if '"demucsShifts": 1' not in source:
        raise SystemExit("Demucs shifts setting changed or missing")
    if '"demucsOverlap": 0.10' not in source:
        raise SystemExit("Demucs overlap setting changed or missing")
    if '"demucsSegmentSize": 6' not in source:
        raise SystemExit("Demucs segment setting changed or missing")

    print("PASS v143 Demucs CPU dispatch controls")


if __name__ == "__main__":
    main()
