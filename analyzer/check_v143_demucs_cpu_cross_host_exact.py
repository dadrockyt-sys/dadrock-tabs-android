from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_SETTINGS = {
    "atenCpuCapability": "default",
    "mklCbwr": "COMPATIBLE",
    "mklDynamic": "FALSE",
    "ompDynamic": "FALSE",
    "oneDnnMaxCpuIsa": "SSE41",
    "dnnlMaxCpuIsa": "SSE41",
}
EXPECTED_SHIFT = ["0,22050,6026"]


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _vendor(payload: dict) -> str:
    text = str((payload.get("host") or {}).get("lscpu") or "")
    for line in text.splitlines():
        if line.lower().startswith("vendor id:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: check_v143_demucs_cpu_cross_host_exact.py probe1.json probe2.json")
    first, second = (_load(sys.argv[1]), _load(sys.argv[2]))

    failures: list[str] = []
    for index, item in enumerate((first, second), start=1):
        inv = item.get("invariants") or {}
        if inv.get("approvedFixture") is not True or inv.get("referenceFree") is not True:
            failures.append(f"probe{index}:safety")
        if inv.get("modalGpuRequested") is not False or inv.get("productionModified") is not False:
            failures.append(f"probe{index}:gpu-or-production")
        if inv.get("childRuntimeTracePresent") is not True:
            failures.append(f"probe{index}:child-runtime-trace")
        if item.get("demucsShiftTrace") != EXPECTED_SHIFT:
            failures.append(f"probe{index}:shift")
        settings = item.get("settings") or {}
        for key, expected in REQUIRED_SETTINGS.items():
            if settings.get(key) != expected:
                failures.append(f"probe{index}:{key}={settings.get(key)!r}")
        child = item.get("childRuntime") or {}
        if str(child.get("torchCpuCapability") or "").upper() != "DEFAULT":
            failures.append(f"probe{index}:effective-aten={child.get('torchCpuCapability')!r}")
        if child.get("mkldnnEnabled") is not False:
            failures.append(f"probe{index}:mkldnn-enabled={child.get('mkldnnEnabled')!r}")
        env = child.get("environment") or {}
        if env.get("V143_DEMUCS_DISABLE_MKLDNN") != "1":
            failures.append(f"probe{index}:mkldnn-disable-env={env.get('V143_DEMUCS_DISABLE_MKLDNN')!r}")

    for key in ("sourceSha256", "normalizedWavSha256", "directGuitarSha256", "directPcmInt16Sha256"):
        if first.get(key) != second.get(key):
            failures.append(f"mismatch:{key}")

    vendors = [_vendor(first), _vendor(second)]
    if vendors[0] == vendors[1]:
        failures.append(f"same-host-vendor:{vendors[0]}")

    if failures:
        raise SystemExit("cross-host exactness failed: " + ", ".join(failures))

    print(json.dumps({
        "passed": True,
        "vendors": vendors,
        "directGuitarSha256": first.get("directGuitarSha256"),
        "directPcmInt16Sha256": first.get("directPcmInt16Sha256"),
        "shiftTrace": EXPECTED_SHIFT,
        "effectiveAten": "DEFAULT",
        "mkldnnEnabled": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
