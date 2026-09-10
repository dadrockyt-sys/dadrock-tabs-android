#!/usr/bin/env python3

import argparse
import json
import tempfile
from pathlib import Path

CONTRACT = "songsterr-fresh-demucs-cross-run-comparison-v1"
INPUT_CONTRACT = "songsterr-fresh-demucs-cross-run-provenance-v1"
EXPECTED_INPUT_SHA256 = "e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a"
REQUIRED_FALSE_GUARDS = (
    "basicPitchInvoked",
    "releaseEvidenceInvoked",
    "preferredStemSelection",
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
FIXED_DEMUCS = {
    "package": "demucs",
    "packageVersion": "4.1.0",
    "model": "htdemucs_6s",
    "device": "cpu",
    "shifts": 0,
    "overlap": 0.25,
    "segmentSeconds": 7,
    "stem": "guitar",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Compare independent hosted-run Demucs provenance records by content hashes and "
            "runtime metadata only. This diagnostic does not choose a preferred stem or define "
            "any downstream acceptance or duration rule."
        )
    )
    parser.add_argument("--inputs", nargs="+", help="cross-run provenance JSON files")
    parser.add_argument("--output", help="output comparison JSON")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test and (not args.inputs or not args.output):
        parser.error("--inputs and --output are required unless --self-test is used")
    return args


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_observation(payload):
    require(payload.get("contract") == INPUT_CONTRACT, "DEMUCS_CROSS_RUN_INPUT_CONTRACT_CHANGED")
    require(payload.get("referenceBlind") is True, "DEMUCS_CROSS_RUN_INPUT_NOT_REFERENCE_BLIND")
    require(payload.get("diagnosticOnly") is True, "DEMUCS_CROSS_RUN_INPUT_NOT_DIAGNOSTIC")
    source = payload.get("source") or {}
    require(
        source.get("decodedSeparationWavSha256") == EXPECTED_INPUT_SHA256,
        "DEMUCS_CROSS_RUN_INPUT_SHA_CHANGED",
    )
    require(isinstance(source.get("stemFileSha256"), str), "DEMUCS_CROSS_RUN_FILE_SHA_MISSING")
    require(isinstance(source.get("stemPcmSha256"), str), "DEMUCS_CROSS_RUN_PCM_SHA_MISSING")
    demucs = payload.get("demucs") or {}
    for key, expected in FIXED_DEMUCS.items():
        require(demucs.get(key) == expected, f"DEMUCS_CROSS_RUN_FIXED_SETTING_CHANGED:{key}")
    hard = payload.get("hardGuards") or {}
    for key in REQUIRED_FALSE_GUARDS:
        require(hard.get(key) is False, f"DEMUCS_CROSS_RUN_GUARD_CHANGED:{key}")
    require(str(payload.get("sampleLabel") or "").strip(), "DEMUCS_CROSS_RUN_SAMPLE_LABEL_MISSING")


def distinct_sorted(values):
    return sorted({value for value in values if value is not None}, key=lambda value: str(value))


def group_labels(rows, field):
    groups = {}
    for row in rows:
        groups.setdefault(row[field], []).append(row["sampleLabel"])
    return {
        key: sorted(labels)
        for key, labels in sorted(groups.items())
    }


def compare_observations(observations):
    require(len(observations) >= 2, "DEMUCS_CROSS_RUN_NEEDS_AT_LEAST_TWO_INPUTS")
    for payload in observations:
        validate_observation(payload)
    labels = [payload["sampleLabel"] for payload in observations]
    require(len(set(labels)) == len(labels), "DEMUCS_CROSS_RUN_DUPLICATE_SAMPLE_LABEL")

    rows = []
    for payload in sorted(observations, key=lambda item: item["sampleLabel"]):
        source = payload["source"]
        runtime = payload.get("runtime") or {}
        torch_runtime = runtime.get("torch") or {}
        row = {
            "sampleLabel": payload["sampleLabel"],
            "stemFileSha256": source["stemFileSha256"],
            "stemPcmSha256": source["stemPcmSha256"],
            "sampleRate": source.get("sampleRate"),
            "shape": source.get("shape"),
            "totalPcmValues": source.get("totalPcmValues"),
            "stemRms": source.get("stemRms"),
            "cpuModel": runtime.get("cpuModel"),
            "imageOS": runtime.get("imageOS"),
            "imageVersion": runtime.get("imageVersion"),
            "platform": runtime.get("platform"),
            "machine": runtime.get("machine"),
            "libc": runtime.get("libc"),
            "runnerOS": runtime.get("runnerOS"),
            "runnerArch": runtime.get("runnerArch"),
            "torchVersion": torch_runtime.get("version"),
            "torchCpuCapability": torch_runtime.get("cpuCapability"),
            "torchNumThreads": torch_runtime.get("numThreads"),
            "torchNumInteropThreads": torch_runtime.get("numInteropThreads"),
            "torchMkldnnEnabled": torch_runtime.get("mkldnnEnabled"),
            "torchMklAvailable": torch_runtime.get("mklAvailable"),
            "torchOpenmpAvailable": torch_runtime.get("openmpAvailable"),
            "cudaAvailable": torch_runtime.get("cudaAvailable"),
            "githubRunId": runtime.get("githubRunId"),
            "githubJob": runtime.get("githubJob"),
        }
        rows.append(row)

    file_hashes = distinct_sorted(row["stemFileSha256"] for row in rows)
    pcm_hashes = distinct_sorted(row["stemPcmSha256"] for row in rows)
    pairwise = []
    for index, left in enumerate(rows):
        for right in rows[index + 1:]:
            pairwise.append({
                "a": left["sampleLabel"],
                "b": right["sampleLabel"],
                "fileBytesIdenticalBySha256": left["stemFileSha256"] == right["stemFileSha256"],
                "decodedPcmIdenticalBySha256": left["stemPcmSha256"] == right["stemPcmSha256"],
                "sameCpuModel": left["cpuModel"] == right["cpuModel"],
                "sameImageVersion": left["imageVersion"] == right["imageVersion"],
                "samePlatform": left["platform"] == right["platform"],
                "sameTorchCpuCapability": left["torchCpuCapability"] == right["torchCpuCapability"],
            })

    environment = {
        "cpuModels": distinct_sorted(row["cpuModel"] for row in rows),
        "imageOSValues": distinct_sorted(row["imageOS"] for row in rows),
        "imageVersions": distinct_sorted(row["imageVersion"] for row in rows),
        "platforms": distinct_sorted(row["platform"] for row in rows),
        "libcValues": distinct_sorted(tuple(row["libc"]) if isinstance(row["libc"], list) else row["libc"] for row in rows),
        "torchVersions": distinct_sorted(row["torchVersion"] for row in rows),
        "torchCpuCapabilities": distinct_sorted(row["torchCpuCapability"] for row in rows),
    }
    # JSON has no tuple type; normalize libc tuples back to lists for readability.
    environment["libcValues"] = [list(value) if isinstance(value, tuple) else value for value in environment["libcValues"]]

    return {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "diagnosticOnly": True,
        "scope": "independent-hosted-run-demucs-content-and-provenance-comparison",
        "observationCount": len(rows),
        "source": {
            "decodedSeparationWavSha256": EXPECTED_INPUT_SHA256,
            "fixedDemucs": dict(FIXED_DEMUCS),
        },
        "comparison": {
            "distinctStemFileSha256Count": len(file_hashes),
            "distinctStemPcmSha256Count": len(pcm_hashes),
            "allStemFileBytesIdentical": len(file_hashes) == 1,
            "allDecodedPcmIdentical": len(pcm_hashes) == 1,
            "crossRunFileVariationObserved": len(file_hashes) > 1,
            "crossRunPcmVariationObserved": len(pcm_hashes) > 1,
            "stemFileSha256Groups": group_labels(rows, "stemFileSha256"),
            "stemPcmSha256Groups": group_labels(rows, "stemPcmSha256"),
            "pairwise": pairwise,
        },
        "environmentDimensions": environment,
        "observations": rows,
        "hardGuards": {
            "preferredStemSelection": False,
            "durationWrite": False,
            "sourceEndWrite": False,
            "pitchIdentityWrite": False,
            "modelInferenceByComparator": False,
            "basicPitchInvocation": False,
            "releaseEvidenceInvocation": False,
            "thresholdSelection": False,
            "thresholdSweep": False,
            "downstreamAgreementObjective": False,
            "acceptanceDecision": False,
            "customerDeliveryInvoked": False,
            "legacyV143ScorerImported": False,
            "professionalScorerUsed": False,
            "referenceTabUsed": False,
        },
    }


def synthetic(label, file_sha, pcm_sha, cpu):
    return {
        "contract": INPUT_CONTRACT,
        "version": 1,
        "sampleLabel": label,
        "referenceBlind": True,
        "diagnosticOnly": True,
        "source": {
            "decodedSeparationWavSha256": EXPECTED_INPUT_SHA256,
            "stemFileSha256": file_sha,
            "stemPcmSha256": pcm_sha,
            "sampleRate": 44100,
            "shape": [10, 2],
            "totalPcmValues": 20,
            "stemRms": 0.1,
        },
        "demucs": dict(FIXED_DEMUCS),
        "runtime": {
            "cpuModel": cpu,
            "imageOS": "ubuntu24",
            "imageVersion": "test-image",
            "platform": "test-platform",
            "machine": "x86_64",
            "libc": ["glibc", "2.39"],
            "runnerOS": "Linux",
            "runnerArch": "X64",
            "torch": {
                "version": "2.14.0+test",
                "cpuCapability": "AVX2",
                "numThreads": 1,
                "numInteropThreads": 4,
                "mkldnnEnabled": True,
                "mklAvailable": True,
                "openmpAvailable": True,
                "cudaAvailable": False,
            },
        },
        "hardGuards": {key: False for key in REQUIRED_FALSE_GUARDS},
    }


def self_test():
    equal = compare_observations([
        synthetic("a", "a" * 64, "b" * 64, "cpu-a"),
        synthetic("b", "a" * 64, "b" * 64, "cpu-a"),
    ])
    require(equal["comparison"]["allDecodedPcmIdentical"] is True, "DEMUCS_CROSS_RUN_SELF_TEST_EQUAL")
    different = compare_observations([
        synthetic("a", "a" * 64, "b" * 64, "cpu-a"),
        synthetic("b", "c" * 64, "d" * 64, "cpu-b"),
    ])
    require(different["comparison"]["crossRunPcmVariationObserved"] is True, "DEMUCS_CROSS_RUN_SELF_TEST_VARIATION")
    require(different["hardGuards"]["preferredStemSelection"] is False, "DEMUCS_CROSS_RUN_SELF_TEST_PREFERENCE")
    require(different["hardGuards"]["thresholdSweep"] is False, "DEMUCS_CROSS_RUN_SELF_TEST_THRESHOLD")
    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "PASS",
        "referenceBlind": True,
        "diagnosticOnly": True,
        "preferredStemSelection": False,
        "thresholdSweep": False,
        "acceptanceDecision": False,
    }, sort_keys=True))


def main():
    args = parse_args()
    if args.self_test:
        self_test()
        return
    observations = [load_json(path) for path in args.inputs]
    payload = compare_observations(observations)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "contract": payload["contract"],
        "observationCount": payload["observationCount"],
        "distinctStemFileSha256Count": payload["comparison"]["distinctStemFileSha256Count"],
        "distinctStemPcmSha256Count": payload["comparison"]["distinctStemPcmSha256Count"],
        "crossRunPcmVariationObserved": payload["comparison"]["crossRunPcmVariationObserved"],
        "cpuModels": payload["environmentDimensions"]["cpuModels"],
        "imageVersions": payload["environmentDimensions"]["imageVersions"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
