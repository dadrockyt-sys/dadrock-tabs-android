"""BS-Roformer-SW 6-stem FP16 ONNX adapter for bounded S0 development use.

Legal/provenance note:
- The ONNX distribution is labeled MIT.
- Its model card explicitly states the original pretrained weights were rehosted
  without a stated license/provenance.
- The user has explicitly directed this project to use the ONNX package for
  educational/development evaluation.
- This code records that uncertainty; it does not assert fair use or commercial rights.

No model is bundled in Git. The caller must supply the exact verified ONNX file.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib
import numpy as np

STEM_ORDER=("bass","drums","other","vocals","guitar","piano")
SAMPLE_RATE=44100
CHUNK_SAMPLES=176400
OVERLAP=0.25
HOP_SAMPLES=int(CHUNK_SAMPLES*(1.0-OVERLAP))
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
    rights_status: str="user_authorized_dev_use_license_provenance_unresolved"

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

def _window(n: int) -> np.ndarray:
    # sqrt-Hann permits smooth overlap-add when applied on both sides.
    return np.sqrt(np.hanning(n).astype(np.float32) + 1e-8)

class BsRoformer6StemOnnxAdapter:
    spec=ModelSpec()
    stem_order=STEM_ORDER

    def __init__(self, model_path: Path, *, providers: list[str] | None=None):
        validate_model(model_path, fp16=True)
        try:
            import onnxruntime as ort
        except ImportError as exc:
            raise RuntimeError("onnxruntime is required for ONNX execution") from exc
        self.model_path=Path(model_path)
        self.session=ort.InferenceSession(
            str(model_path),
            providers=providers or ["CPUExecutionProvider"],
        )
        inputs=self.session.get_inputs()
        outputs=self.session.get_outputs()
        if len(inputs)!=1 or len(outputs)!=1:
            raise RuntimeError("unexpected ONNX I/O contract")
        self.input_name=inputs[0].name
        self.output_name=outputs[0].name

    def separate_array(self, stereo: np.ndarray, sample_rate: int) -> dict[str,np.ndarray]:
        if sample_rate != SAMPLE_RATE:
            raise ValueError(f"expected {SAMPLE_RATE} Hz, got {sample_rate}")
        x=np.asarray(stereo,dtype=np.float32)
        if x.ndim != 2 or x.shape[1] != 2:
            raise ValueError("expected samples x 2 stereo float32")
        length=x.shape[0]
        pad=max(0,CHUNK_SAMPLES-length)
        if pad:
            x=np.pad(x,((0,pad),(0,0)))
        total_len=x.shape[0]
        if total_len > CHUNK_SAMPLES:
            remainder=(total_len-CHUNK_SAMPLES)%HOP_SAMPLES
            if remainder:
                x=np.pad(x,((0,HOP_SAMPLES-remainder),(0,0)))
                total_len=x.shape[0]
        starts=list(range(0,max(1,total_len-CHUNK_SAMPLES+1),HOP_SAMPLES))
        if starts[-1] != total_len-CHUNK_SAMPLES:
            starts.append(total_len-CHUNK_SAMPLES)

        win=_window(CHUNK_SAMPLES)
        accum={name:np.zeros((total_len,2),dtype=np.float32) for name in STEM_ORDER}
        weight=np.zeros(total_len,dtype=np.float32)

        for start in starts:
            chunk=x[start:start+CHUNK_SAMPLES].T[None,:,:]  # [1,2,T]
            y=self.session.run([self.output_name],{self.input_name:chunk})[0]
            arr=np.asarray(y,dtype=np.float32)
            # Accept common [1,6,2,T] or [6,2,T] layouts.
            if arr.ndim==4 and arr.shape[0]==1:
                arr=arr[0]
            if arr.shape[:2] != (6,2):
                raise RuntimeError(f"unexpected output shape {arr.shape}")
            for i,name in enumerate(STEM_ORDER):
                seg=arr[i].T*win[:,None]
                accum[name][start:start+CHUNK_SAMPLES]+=seg
            weight[start:start+CHUNK_SAMPLES]+=win

        safe=np.maximum(weight,1e-8)[:,None]
        return {name:(value/safe)[:length].astype(np.float32) for name,value in accum.items()}
