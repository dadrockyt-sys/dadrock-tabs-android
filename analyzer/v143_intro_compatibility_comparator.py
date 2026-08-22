#!/usr/bin/env python3
"""Research-only V143 measures 1-16 compatibility comparator.

This tool intentionally does *not* run Modal or a separator. It consumes a
future fresh-capture manifest, checks that the capture is provenance-complete,
and compares only authenticated historical invariants. A fresh run can provide
compatibility evidence; it cannot recover missing historical separator-family
provenance by itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESIGN = REPO_ROOT / "debug/v143-contextual-prune/intro-compatibility-comparator-design.json"
DEFAULT_GAP = REPO_ROOT / "debug/v143-contextual-prune/intro-separator-family-evidence-gap.json"
DEFAULT_SUMS = REPO_ROOT / "analyzer/v143-intro-1-16-evidence/codespace-snapshot/SHA256SUMS.txt"
DEFAULT_RAW_CACHE = REPO_ROOT / "analyzer/v143-intro-1-16-evidence/codespace-snapshot/intro-raw-attack-cache.json"

FAMILY_A = {
    "direct": "30cffcc2e472abe6d613b3853295c47b71ae8c4318f8709c8c9d45d69d9351f8",
    "cascade": "68a1c75e59bf45fbae340938e580575c043e7a94a70e7be2361e4c2d4621cb56",
}
FAMILY_B = {
    "direct": "1542856aca8275c727e6c77edd941588aa359b65b8b897c1b3ada2926f2d579e",
    "cascade": "e26f7a430b835adcd7a284db8a18c3aa93632b81e1c1a653eeffa16c02a62bc3",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_sha256sums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                raise ValueError(f"Malformed checksum line in {path}: {raw_line!r}")
            checksum, name = parts
            result[name.lstrip("*")] = checksum
    return result


def is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def missing_required_fields(capture: dict[str, Any], design: dict[str, Any]) -> list[str]:
    required = design.get("freshCaptureRequiredFields") or {}
    missing: list[str] = []
    if not isinstance(required, dict):
        return ["design.freshCaptureRequiredFields"]
    for section, fields in required.items():
        section_payload = capture.get(section)
        if not isinstance(section_payload, dict):
            missing.append(section)
            continue
        if not isinstance(fields, list):
            missing.append(f"design.freshCaptureRequiredFields.{section}")
            continue
        for field in fields:
            if field not in section_payload or not is_present(section_payload.get(field)):
                missing.append(f"{section}.{field}")
    return missing


def exact_equal(actual: Any, expected: Any) -> bool:
    # JSON numeric values such as 1 and 1.0 are intentionally equivalent here.
    return actual == expected


def compare_fields(actual: dict[str, Any], expected: dict[str, Any], prefix: str) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        checks.append(
            {
                "field": f"{prefix}.{key}",
                "expected": expected_value,
                "actual": actual_value,
                "passed": exact_equal(actual_value, expected_value),
            }
        )
    return checks


def all_passed(checks: list[dict[str, Any]]) -> bool:
    return all(bool(check.get("passed")) for check in checks)


def classify_family(stem_identity: dict[str, Any]) -> str | None:
    direct = stem_identity.get("directDecodedPcmSha256")
    cascade = stem_identity.get("cascadeDecodedPcmSha256")
    if direct == FAMILY_A["direct"] and cascade == FAMILY_A["cascade"]:
        return "CURRENT_RESEARCH_FAMILY_A_COMPATIBLE"
    if direct == FAMILY_B["direct"] and cascade == FAMILY_B["cascade"]:
        return "CURRENT_RESEARCH_FAMILY_B_COMPATIBLE"
    return None


def build_result(
    capture: dict[str, Any],
    design: dict[str, Any],
    gap: dict[str, Any],
    checksum_manifest: dict[str, str],
    historical_raw_cache_sha: str,
) -> dict[str, Any]:
    expected = design["historicalReadOnlyBaseline"]
    expected_intro = expected["introRawAttackCache"]
    expected_recipe = expected["separatorRecipe"]

    manifest_raw_sha = checksum_manifest.get("intro-raw-attack-cache.json")
    baseline_integrity_checks = [
        {
            "field": "historicalRawCache.fileSha256",
            "expected": expected_intro["sha256"],
            "actual": historical_raw_cache_sha,
            "passed": historical_raw_cache_sha == expected_intro["sha256"],
        },
        {
            "field": "SHA256SUMS.intro-raw-attack-cache.json",
            "expected": expected_intro["sha256"],
            "actual": manifest_raw_sha,
            "passed": manifest_raw_sha == expected_intro["sha256"],
        },
        {
            "field": "evidenceGap.status",
            "expected": "EVIDENCE_GAP*",
            "actual": gap.get("status"),
            "passed": str(gap.get("status", "")).startswith("EVIDENCE_GAP"),
        },
    ]

    missing = missing_required_fields(capture, design)

    identity = capture.get("captureIdentity") or {}
    source_checks = compare_fields(
        identity,
        {"sourceAudioGitBlobSha": expected["sourceAudio"]["gitBlobSha"]},
        "captureIdentity",
    )

    invocation = capture.get("separatorInvocation") or {}
    recipe_expected = {
        "seed": expected_recipe["seed"],
        "demucsShifts": expected_recipe["demucsShifts"],
        "demucsOverlap": expected_recipe["demucsOverlap"],
        "demucsSegmentSize": expected_recipe["demucsSegmentSize"],
        "roformerBatchSize": expected_recipe["roformerBatchSize"],
    }
    recipe_checks = compare_fields(invocation, recipe_expected, "separatorInvocation")

    model_identity = capture.get("modelPayloadIdentity") or {}
    model_identifier_checks = compare_fields(
        model_identity,
        {
            "bsRoformerModelIdentifier": expected_recipe["bsRoformerModelIdentifier"],
            "demucsModelIdentifier": expected_recipe["demucsModelIdentifier"],
        },
        "modelPayloadIdentity",
    )

    runtime = capture.get("runtimeIdentity") or {}
    runtime_checks = compare_fields(
        runtime,
        {"audioSeparatorVersion": expected_recipe["audioSeparatorVersion"]},
        "runtimeIdentity",
    )

    intro = capture.get("introFingerprint") or {}
    intro_count_expected = {
        "rawEventCount": expected_intro["rawEventCount"],
        "directStemEventCount": expected_intro["stemEventCounts"]["direct-demucs6s-guitar.wav"],
        "cascadeStemEventCount": expected_intro["stemEventCounts"]["bsroformer-demucs6s-guitar.wav"],
        "sweepEventCounts": expected_intro["sweepEventCounts"],
    }
    intro_count_checks = compare_fields(intro, intro_count_expected, "introFingerprint")
    intro_cache_check = {
        "field": "introFingerprint.rawAttackCacheSha256",
        "expected": expected_intro["sha256"],
        "actual": intro.get("rawAttackCacheSha256"),
        "passed": intro.get("rawAttackCacheSha256") == expected_intro["sha256"],
    }

    baseline_ok = all_passed(baseline_integrity_checks)
    source_recipe_ok = all_passed(source_checks + recipe_checks + model_identifier_checks + runtime_checks)
    intro_counts_ok = all_passed(intro_count_checks)
    intro_cache_exact = bool(intro_cache_check["passed"])

    family_label = classify_family(capture.get("stemIdentity") or {})
    compatibility_labels: list[str] = []
    if family_label:
        compatibility_labels.append(family_label)

    if not baseline_ok:
        primary = "INCOMPATIBLE"
        reason = "Authenticated historical baseline integrity check failed; comparison is not trustworthy."
    elif missing:
        primary = "INCOMPLETE_CAPTURE"
        reason = "Fresh capture is missing required provenance fields."
    elif not source_recipe_ok or not intro_counts_ok:
        primary = "INCOMPATIBLE"
        reason = "Fresh source/recipe/runtime identifiers or intro event fingerprints differ from the authenticated baseline."
    elif intro_cache_exact:
        primary = "INTRO_CACHE_EXACT_COMPATIBLE"
        reason = "Fresh intro raw-attack cache digest and all authenticated intro fingerprints exactly match."
    else:
        primary = "COUNT_COMPATIBLE_ONLY"
        reason = "Fresh intro counts match, but the raw-attack cache digest is not exact."

    if primary == "INTRO_CACHE_EXACT_COMPATIBLE":
        compatibility_labels.append("INTRO_CACHE_EXACT_COMPATIBLE")
    elif primary == "COUNT_COMPATIBLE_ONLY":
        compatibility_labels.append("COUNT_COMPATIBLE_ONLY")

    downstream = capture.get("downstreamFrozenReplay") or {}
    downstream_status = {
        "provided": isinstance(downstream, dict) and bool(downstream),
        "comparison": "NOT_EVALUATED_NO_AUTHENTICATED_HISTORICAL_DIGEST_BASELINE_IN_THIS_COMPARATOR",
        "note": "Downstream fields are retained in the capture for audit. Exact downstream classification must only be enabled after its expected historical digests are independently authenticated and pinned.",
    }

    return {
        "artifact": "v143-intro-compatibility-comparison",
        "schemaVersion": 1,
        "comparisonMode": "FRESH_COMPATIBILITY_EVIDENCE_ONLY",
        "captureId": identity.get("captureId"),
        "primaryClassification": primary,
        "classificationReason": reason,
        "compatibilityLabels": compatibility_labels,
        "historicalProvenanceClosed": False,
        "historicalIntroFamilyAuthenticated": False,
        "productionPromotionAllowed": False,
        "freshCaptureCompleteness": {
            "passed": not missing,
            "missingFields": missing,
        },
        "historicalBaselineIntegrity": {
            "passed": baseline_ok,
            "checks": baseline_integrity_checks,
        },
        "sourceRecipeCompatibility": {
            "passed": source_recipe_ok,
            "checks": source_checks + recipe_checks + model_identifier_checks + runtime_checks,
        },
        "introCountCompatibility": {
            "passed": intro_counts_ok,
            "checks": intro_count_checks,
        },
        "introCacheExactCompatibility": intro_cache_check,
        "currentResearchFamilyClassification": family_label,
        "downstreamFrozenReplay": downstream_status,
        "explicitlyExcludedClaims": design.get("forbiddenConclusions", []),
        "evidenceGapStatusAtComparison": gap.get("status"),
        "evidenceGapConclusionAtComparison": gap.get("conclusion"),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", required=True, type=Path, help="Fresh compatibility capture JSON")
    parser.add_argument("--design", type=Path, default=DEFAULT_DESIGN)
    parser.add_argument("--gap", type=Path, default=DEFAULT_GAP)
    parser.add_argument("--sha256sums", type=Path, default=DEFAULT_SUMS)
    parser.add_argument("--historical-raw-cache", type=Path, default=DEFAULT_RAW_CACHE)
    parser.add_argument("--output", type=Path, help="Optional result JSON path; stdout is always printed")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        design = load_json(args.design)
        gap = load_json(args.gap)
        capture = load_json(args.capture)
        checksum_manifest = parse_sha256sums(args.sha256sums)
        historical_raw_cache_sha = sha256_file(args.historical_raw_cache)
        result = build_result(capture, design, gap, checksum_manifest, historical_raw_cache_sha)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "COMPARATOR_ERROR", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2

    rendered = json.dumps(result, indent=2, sort_keys=False) + "\n"
    print(rendered, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")

    if result["primaryClassification"] in {"INCOMPLETE_CAPTURE", "INCOMPATIBLE"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
