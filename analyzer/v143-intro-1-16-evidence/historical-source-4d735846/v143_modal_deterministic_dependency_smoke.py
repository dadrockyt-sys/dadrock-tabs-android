from __future__ import annotations

import json

from v143_modal_live_endpoint import app, rhythm_dependency_smoke


@app.local_entrypoint()
def main() -> None:
    result = rhythm_dependency_smoke.remote()

    print()
    print("=== V143 DETERMINISTIC MODAL DEPENDENCY SMOKE COMPLETE ===")
    print(json.dumps(result, indent=2, default=str))

    checks = {
        "cudaAvailable": result.get("cudaAvailable") is True,
        "featureCount148": int(result.get("featureCount") or 0) == 148,
        "referenceFree": result.get("referenceFree") is True,
        "demucsModel": str(result.get("demucsModel") or "") == "htdemucs_6s.yaml",
        "bsRoformerModel": str(result.get("bsRoformerModel") or "") == "model_bs_roformer_ep_317_sdr_12.9755.ckpt",
        "pkgResourcesImported": result.get("pkgResourcesImported") is True,
        "basicPitchImported": result.get("basicPitchImported") is True,
        "bendEvidenceImported": result.get("bendEvidenceImported") is True,
        "bendConsensusImported": result.get("bendConsensusImported") is True,
        "legatoEvidenceImported": result.get("legatoEvidenceImported") is True,
        "deterministicProviderImported": result.get("deterministicProviderImported") is True,
        "deterministicSeed143": int(result.get("deterministicSeparatorSeed") or 0) == 143,
        "demucsShifts1": int(result.get("demucsShifts") or 0) == 1,
    }

    print()
    print("=== DEPENDENCY GATES ===")
    for label, value in checks.items():
        print(f"{label}: {value}")

    ready = all(checks.values())
    print(f"READY FOR STRICT DETERMINISTIC MODAL DEPLOY: {ready}")

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
