#!/usr/bin/env python3
"""Verify that the frozen runtime can resolve every amt_tools class referenced by the checkpoint.

No checkpoint is opened, imported, unpickled, or executed.
"""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import sys
from pathlib import Path

import librosa
import numpy as np
import scipy
import torch

EXPECTED = (
    ("amt_tools.models.common", "SoftmaxGroups"),
    ("amt_tools.models.tabcnn", "TabCNN"),
    ("amt_tools.tools.instrument", "GuitarProfile"),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    args = parser.parse_args()

    source_root = str(Path(args.source_root))
    sys.path.insert(0, source_root)
    try:
        resolved = []
        for module_name, class_name in EXPECTED:
            module = importlib.import_module(module_name)
            value = getattr(module, class_name)
            if value.__module__ != module_name or value.__name__ != class_name:
                raise AssertionError(
                    f"identity mismatch for {module_name}.{class_name}: "
                    f"{value.__module__}.{value.__name__}"
                )
            resolved.append(
                {
                    "module": module_name,
                    "name": class_name,
                    "kind": type(value).__name__,
                }
            )
    finally:
        sys.path.pop(0)

    receipt = {
        "schema": "astra-tabcnn-legacy-import-surface-v1",
        "checkpointOpened": False,
        "checkpointUnpickled": False,
        "modelInvoked": False,
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "librosa": librosa.__version__,
            "torch": torch.__version__,
        },
        "sourceRevision": "f50309ad06dc734ddae5e3a0eda756fca221e2e7",
        "sourceBlobs": {
            "modelCommon": "84beb4cf251b9cb9274d10cf203318314181af31",
            "tabcnn": "e09856db2fffd77642e005ab509846acc894b886",
            "instrument": "eddc48a8b95de057035cd11ea2d1951e754ef349",
            "constants": "79666ea0c5b0214ca664da454069b8d286cc5c18",
        },
        "resolvedGlobals": resolved,
    }
    print("TABCNN_LEGACY_IMPORT_SURFACE=" + json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
