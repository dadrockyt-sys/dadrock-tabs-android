#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

CONTRACT = "songsterr-fresh-demucs-common-avx2-cross-host-comparison-v1"
INPUT_CONTRACT = "songsterr-fresh-demucs-common-avx2-provenance-v1"
EXPECTED_INPUT_SHA256 = "e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a"
REQUIRED_FALSE_GUARDS = (
    "preferredStemSelection",
    "basicPitchInvocation",
    "releaseEvidenceInvocation",
    "durationWrite",
    "sourceEndWrite",
    "pitchIdentityWrite",
    "thresholdSelection",
    "thresholdSweep",
    "downstreamAgreementObjective",
    "acceptanceDecision",
    "customerDeliveryInvoked",
    "legacyV143ScorerImported",
    "professionalScorerUsed",
    "referenceTabUsed",
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare fixed combined-AVX2 Demucs provenance across independent hosts."
    )
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate(payload):
    require(payload.get("contract") == INPUT_CONTRACT, "DEMUCS_COMMON_AVX2_INPUT_CONTRACT_CHANGED")
    require(payload.get("referenceBlind") is True, "DEMUCS_COMMON_AVX2_NOT_REFERENCE_BLIND")
    require(payload.get("diagnosticOnly") is True, "DEMUCS_COMMON_AVX2_NOT_DIAGNOSTIC")
    require(payload.get("source", {}).get("decodedSeparationWavSha256") == EXPECTED_INPUT_SHA256, "DEMUCS_COMMON_AVX2_INPUT_SHA_CHANGED")
    candidate = payload.get("executionContractCandidate") or {}
    require(candidate.get("productionAuthorized") is False, "DEMUCS_COMMON_AVX2_PRODUCTION_AUTH_CHANGED")
    require(candidate.get("atenCpuCapability") == "avx2", "DEMUCS_COMMON_AVX2_ATEN_CONTROL_CHANGED")
    require(candidate.get("onednnMaxCpuIsa") == "AVX2", "DEMUCS_COMMON_AVX2_ONEDNN_CONTROL_CHANGED")
    require(candidate.get("demucsModel") == "htdemucs_6s", "DEMUCS_COMMON_AVX2_MODEL_CHANGED")
    require(candidate.get("device") == "cpu", "DEMUCS_COMMON_AVX2_DEVICE_CHANGED")
    require(candidate.get("shifts") == 0, "DEMUCS_COMMON_AVX2_SHIFTS_CHANGED")
    require(candidate.get("overlap") == 0.25, "DEMUCS_COMMON_AVX2_OVERLAP_CHANGED")
    require(candidate.get("segmentSeconds") == 7, "DEMUCS_COMMON_AVX2_SEGMENT_CHANGED")
    runtime = payload.get("runtime") or {}
    require(runtime.get("effectiveTorchCpuCapability") == "AVX2", "DEMUCS_COMMON_AVX2_ATEN_NOT_EFFECTIVE")
    require("AVX2" in str(runtime.get("effectiveOneDnnIsaLine") or "").upper(), "DEMUCS_COMMON_AVX2_ONEDNN_NOT_EFFECTIVE")
    hard = payload.get("hardGuards") or {}
    for key in REQUIRED_FALSE_GUARDS:
        require(hard.get(key) is False, f"DEMUCS_COMMON_AVX2_GUARD_CHANGED:{key}")


def group(rows, field):
    result = {}
    for row in rows:
        result.setdefault(row[field], []).append(row["sampleLabel"])
    return {key: sorted(labels) for key, labels in sorted(result.items())}


def main():
    args = parse_args()
    observations = [load(path) for path in args.inputs]
    require(len(observations) >= 2, "DEMUCS_COMMON_AVX2_NEEDS_MULTIPLE_HOSTS")
    for payload in observations:
        validate(payload)

    labels = [payload.get("sampleLabel") for payload in observations]
    require(all(labels), "DEMUCS_COMMON_AVX2_LABEL_MISSING")
    require(len(labels) == len(set(labels)), "DEMUCS_COMMON_AVX2_DUPLICATE_LABEL")

    rows = []
    for payload in sorted(observations, key=lambda item: item["sampleLabel"]):
        source = payload["source"]
        runtime = payload["runtime"]
        rows.append({
            "sampleLabel": payload["sampleLabel"],
            "nativeCpuVendor": runtime.get("nativeCpuVendor"),
            "nativeCpuModel": runtime.get("nativeCpuModel"),
            "nativeTorchCpuCapability": runtime.get("nativeTorchCpuCapability"),
            "effectiveTorchCpuCapability": runtime.get("effectiveTorchCpuCapability"),
            "effectiveOneDnnIsaLine": runtime.get("effectiveOneDnnIsaLine"),
            "azureRegion": runtime.get("azureRegion"),
            "imageVersion": runtime.get("imageVersion"),
            "platform": runtime.get("platform"),
            "stemFileSha256": source.get("stemFileSha256"),
            "stemPcmSha256": source.get("stemPcmSha256"),
            "stemRms": source.get("stemRms"),
            "sampleRate": source.get("sampleRate"),
            "shape": source.get("shape"),
        })

    file_hashes = sorted({row["stemFileSha256"] for row in rows})
    pcm_hashes = sorted({row["stemPcmSha256"] for row in rows})
    vendors = sorted({row["nativeCpuVendor"] for row in rows if row["nativeCpuVendor"]})
    vendor_models = sorted({f'{row["nativeCpuVendor"]}:{row["nativeCpuModel"]}' for row in rows})
    cross_vendor = len(vendors) >= 2
    all_pcm_identical = len(pcm_hashes) == 1

    if cross_vendor and all_pcm_identical:
        status = "CROSS_VENDOR_EXACT_PCM_CONVERGENCE_OBSERVED"
    elif cross_vendor:
        status = "CROSS_VENDOR_PCM_VARIATION_OBSERVED"
    elif all_pcm_identical:
        status = "SINGLE_VENDOR_EXACT_PCM_CONVERGENCE_ONLY"
    else:
        status = "SINGLE_VENDOR_PCM_VARIATION_OBSERVED"

    payload = {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "diagnosticOnly": True,
        "scope": "common-combined-avx2-independent-host-reproducibility",
        "observationCount": len(rows),
        "status": status,
        "vendorCount": len(vendors),
        "vendors": vendors,
        "vendorModelCount": len(vendor_models),
        "vendorModels": vendor_models,
        "crossVendorObserved": cross_vendor,
        "distinctStemFileSha256Count": len(file_hashes),
        "distinctStemPcmSha256Count": len(pcm_hashes),
        "allStemFileBytesIdentical": len(file_hashes) == 1,
        "allDecodedPcmIdentical": all_pcm_identical,
        "crossVendorExactPcmConvergenceObserved": bool(cross_vendor and all_pcm_identical),
        "stemFileSha256Groups": group(rows, "stemFileSha256"),
        "stemPcmSha256Groups": group(rows, "stemPcmSha256"),
        "observations": rows,
        "interpretationGuards": {
            "productionExecutionContractSelected": False,
            "preferredStemSelected": False,
            "correctnessInferredFromHash": False,
            "downstreamAgreementUsed": False,
            "acceptancePromoted": False,
        },
        "hardGuards": {key: False for key in REQUIRED_FALSE_GUARDS},
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "contract": CONTRACT,
        "status": status,
        "observationCount": len(rows),
        "vendors": vendors,
        "vendorModels": vendor_models,
        "distinctStemFileSha256Count": len(file_hashes),
        "distinctStemPcmSha256Count": len(pcm_hashes),
        "allDecodedPcmIdentical": all_pcm_identical,
        "stemFileSha256Groups": payload["stemFileSha256Groups"],
        "stemPcmSha256Groups": payload["stemPcmSha256Groups"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
