"""BS-Roformer-SW 6-stem ONNX adapter contract.

Prepared for S0 evaluation only. Execution is intentionally blocked until
the checkpoint provenance/usage boundary is explicitly cleared.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib

STEM_ORDER=("bass","drums","other","vocals","guitar","piano")
SAMPLE_RATE=44100
CHUNK_SAMPLES=176400
N_FFT=2048
HOP_LENGTH=512
WIN_LENGTH=2048

FP16_SHA256="d3d2bac77a7023282cb5f35a5807179e34076b60589867b572275f1a8ec36444"
FP32_SHA256="224f5f54a7ff9ff0e487aabca0a365d94513d51a6cdb7778152f2371716f2b68"
UPSTREAM_CKPT_SHA256="24e7d35ee9c64415673d3fd33e06a67cac2c103c5df6267ba1576459c775916e"

@dataclass(frozen=True)
class ModelSpec:
    name: str="BS-Roformer-SW 6-stem ONNX"
    source_repo: str="elicwhite/bs-roformer-sw-6stem-onnx"
    source_revision: str="a744f80957374e1735ad70fa122670b7961da8cc"
    upstream_repo: str="jarredou/BS-ROFO-SW-Fixed"
    upstream_revision: str="ad54168acf271482ad51702953e162a385b8fdcb"
    rights_status: str="blocked_upstream_weights_license_unknown"

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def validate_model(path: Path, *, fp16: bool=True) -> None:
    expected=FP16_SHA256 if fp16 else FP32_SHA256
    actual=sha256(path)
    if actual != expected:
        raise RuntimeError(f"model SHA mismatch: expected {expected}, got {actual}")

class BlockedBsRoformer6StemAdapter:
    spec=ModelSpec()
    stem_order=STEM_ORDER

    def separate(self, mixture_path: Path):
        raise RuntimeError(
            "BS-Roformer-SW adapter is prepared but execution is blocked: "
            "the original pretrained checkpoint is published with license=unknown. "
            "Do not download or run model weights until that rights boundary is cleared."
        )
