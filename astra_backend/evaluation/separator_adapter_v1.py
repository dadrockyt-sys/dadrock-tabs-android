"""Separator adapter contract for S0 evaluation.

Implementations must return named time-domain stems and must not silently
change model/checkpoint/config identity.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import numpy as np

@dataclass(frozen=True)
class SeparatorIdentity:
    name: str
    version: str
    repository_revision: str
    checkpoint_sha256: str
    license_basis: str

class SeparatorAdapter(Protocol):
    identity: SeparatorIdentity

    def separate(self, mixture_path: Path) -> tuple[int, dict[str,np.ndarray]]:
        """Return sample rate plus named stems, each samples x channels."""
        ...

class DisabledSeparator:
    identity=SeparatorIdentity(
        name="disabled",
        version="0",
        repository_revision="none",
        checkpoint_sha256="none",
        license_basis="none",
    )

    def separate(self, mixture_path: Path):
        raise RuntimeError(
            "No separator adapter is authorized. "
            "Select and freeze a rights-cleared checkpoint before execution."
        )
