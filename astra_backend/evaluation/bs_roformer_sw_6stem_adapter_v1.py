"""BS-Roformer-SW 6-stem FP16 ONNX adapter for bounded S0 development use.

The ONNX graph consumes pre-computed complex STFT coefficients, not raw audio.
This adapter follows the published I/O contract exactly:
- input real/imag: [1,2,1025,345]
- output real/imag: [1,6,2,1025,345]
- torch.stft/istft with Hann window, n_fft=2048, hop=512, center=True
- 4 s chunks at 44.1 kHz with 25% chunk overlap-add

Licensing/provenance note: the ONNX package is labeled MIT, while its own model
card says the original pretrained weights were rehosted without stated provenance.
The user explicitly directed development use. This file records that uncertainty;
it does not make a legal conclusion.
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
CHUNK_OVERLAP_SAMPLES=CHUNK_SAMPLES-HOP_SAMPLES
N_FFT=2048
STFT_HOP=512
WIN_LENGTH=2048
EXPECTED_FRAMES=345

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

def _chunk_starts(length: int) -> tuple[int,list[int]]:
    if length <= CHUNK_SAMPLES:
        return CHUNK_SAMPLES,[0]
    n_hops=int(np.ceil((length-CHUNK_SAMPLES)/HOP_SAMPLES))
    padded=CHUNK_SAMPLES+n_hops*HOP_SAMPLES
    starts=list(range(0,padded-CHUNK_SAMPLES+1,HOP_SAMPLES))
    return padded,starts

def _crossfade(length: int) -> tuple[np.ndarray,np.ndarray]:
    fadein=np.linspace(0.0,1.0,length,dtype=np.float32)
    return fadein,1.0-fadein

class BsRoformer6StemOnnxAdapter:
    spec=ModelSpec()
    stem_order=STEM_ORDER

    def __init__(self, model_path: Path, *, providers: list[str] | None=None):
        validate_model(model_path,fp16=True)
        try:
            import onnxruntime as ort
            import torch
        except ImportError as exc:
            raise RuntimeError("onnxruntime and torch are required") from exc
        self.torch=torch
        self.window=torch.hann_window(WIN_LENGTH,dtype=torch.float32)
        self.session=ort.InferenceSession(
            str(model_path),providers=providers or ["CPUExecutionProvider"]
        )
        input_names=[x.name for x in self.session.get_inputs()]
        output_names=[x.name for x in self.session.get_outputs()]
        if set(input_names)!={"spec_real","spec_imag"}:
            raise RuntimeError(f"unexpected ONNX inputs {input_names}")
        if set(output_names)!={"out_spec_real","out_spec_imag"}:
            raise RuntimeError(f"unexpected ONNX outputs {output_names}")

    def _separate_chunk(self, chunk: np.ndarray) -> np.ndarray:
        torch=self.torch
        t=torch.from_numpy(chunk.T.copy()).float()  # [2,T]
        spec=torch.stft(
            t,n_fft=N_FFT,hop_length=STFT_HOP,win_length=WIN_LENGTH,
            window=self.window,center=True,normalized=False,return_complex=True
        )
        if tuple(spec.shape)!=(2,1025,EXPECTED_FRAMES):
            raise RuntimeError(f"unexpected STFT shape {tuple(spec.shape)}")
        feeds={
            "spec_real":spec.real.numpy()[None].astype(np.float32),
            "spec_imag":spec.imag.numpy()[None].astype(np.float32),
        }
        real,imag=self.session.run(["out_spec_real","out_spec_imag"],feeds)
        if real.shape!=(1,6,2,1025,EXPECTED_FRAMES) or imag.shape!=real.shape:
            raise RuntimeError(f"unexpected ONNX output {real.shape}/{imag.shape}")
        out=[]
        for i in range(6):
            z=torch.complex(
                torch.from_numpy(real[0,i]),
                torch.from_numpy(imag[0,i])
            )
            # Match upstream zero_dc behavior.
            z[:,0,:]=0
            wav=torch.istft(
                z,n_fft=N_FFT,hop_length=STFT_HOP,win_length=WIN_LENGTH,
                window=self.window,center=True,normalized=False,
                length=CHUNK_SAMPLES
            )
            out.append(wav.T.numpy().astype(np.float32))
        return np.stack(out,axis=0)  # [6,T,2]

    def separate_array(self, stereo: np.ndarray, sample_rate: int) -> dict[str,np.ndarray]:
        if sample_rate!=SAMPLE_RATE:
            raise ValueError(f"expected {SAMPLE_RATE} Hz, got {sample_rate}")
        x=np.asarray(stereo,dtype=np.float32)
        if x.ndim!=2 or x.shape[1]!=2:
            raise ValueError("expected samples x 2 stereo float32")
        original_len=x.shape[0]
        padded_len,starts=_chunk_starts(original_len)
        padded=np.pad(x,((0,padded_len-original_len),(0,0)))
        outputs=np.zeros((6,padded_len,2),dtype=np.float32)
        written=np.zeros(padded_len,dtype=np.float32)
        fadein,fadeout=_crossfade(CHUNK_OVERLAP_SAMPLES)

        for idx,start in enumerate(starts):
            block=self._separate_chunk(padded[start:start+CHUNK_SAMPLES])
            if idx==0:
                outputs[:,start:start+CHUNK_SAMPLES]+=block
                written[start:start+CHUNK_SAMPLES]=1.0
                continue
            overlap_start=start
            overlap_end=start+CHUNK_OVERLAP_SAMPLES
            outputs[:,overlap_start:overlap_end]*=fadeout[None,:,None]
            block[:,:CHUNK_OVERLAP_SAMPLES]*=fadein[None,:,None]
            outputs[:,start:start+CHUNK_SAMPLES]+=block
            written[start:start+CHUNK_SAMPLES]=1.0

        if not np.all(written>0):
            raise RuntimeError("chunk overlap-add left unwritten samples")
        return {
            name:outputs[i,:original_len].astype(np.float32)
            for i,name in enumerate(STEM_ORDER)
        }
