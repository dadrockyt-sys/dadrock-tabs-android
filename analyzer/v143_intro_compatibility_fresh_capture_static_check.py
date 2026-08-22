#!/usr/bin/env python3
"""Static fail-closed safety checks for the V143 intro compatibility producer.

This validator never imports the producer, never invokes Modal, and never runs a
separator. It inspects source text/AST plus the committed comparator design.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRODUCER = REPO_ROOT / "analyzer/v143_intro_compatibility_fresh_capture.py"
DEFAULT_DESIGN = (
    REPO_ROOT
    / "debug/v143-contextual-prune/intro-compatibility-comparator-design.json"
)
EXPECTED_BRANCH = "v143-contextual-prune-lobo"
EXPECTED_PCM_METHOD = "soundfile-int16-always2d-numpy-tobytes-sha256-v1"
EXPECTED_DEBUG_FRAGMENT = "debug/v143-contextual-prune"
FORBIDDEN_WRITE_FRAGMENTS = (
    "public/training",
    "analyzer/v143-intro-1-16-evidence/codespace-snapshot",
)
FORBIDDEN_IMPORT_FRAGMENTS = (
    "professional",
    "reference_chunk",
)
FORBIDDEN_CALL_NAMES = (
    "deploy",
    "retrain",
    "fit",
    "partial_fit",
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_design(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Comparator design must be a JSON object")
    return payload


def _source_constants(tree: ast.AST) -> dict[str, Any]:
    constants: dict[str, Any] = {}
    for node in getattr(tree, "body", []):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            constants[target.id] = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            continue
    return constants


def _call_name(node: ast.Call) -> str:
    target = node.func
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        parts = [target.attr]
        value = target.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts))
    return ""


def _import_names(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.append(str(node.module or ""))
    return sorted(set(names))


def _string_literals(tree: ast.AST) -> list[str]:
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def _check(condition: bool, name: str, detail: Any = None) -> dict[str, Any]:
    return {"name": name, "passed": bool(condition), "detail": detail}


def validate(producer: Path, design_path: Path) -> dict[str, Any]:
    source = producer.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(producer))
    design = _load_design(design_path)
    constants = _source_constants(tree)
    calls = [_call_name(node) for node in ast.walk(tree) if isinstance(node, ast.Call)]
    imports = _import_names(tree)
    strings = _string_literals(tree)

    separator_calls = [
        name
        for name in calls
        if name == "build_deterministic_v143_stems"
    ]
    remote_calls = [name for name in calls if name.endswith(".remote")]

    source_lower = source.lower()
    imports_lower = "\n".join(imports).lower()

    write_call_nodes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and _call_name(node) in {"_write_new_text", "Path.write_text", "write_text"}
    ]

    checks = [
        _check(
            constants.get("EXPECTED_BRANCH") == EXPECTED_BRANCH,
            "branch-is-pinned-to-research-branch",
            constants.get("EXPECTED_BRANCH"),
        ),
        _check(
            str(constants.get("DECODED_PCM_HASH_METHOD") or "") == EXPECTED_PCM_METHOD,
            "decoded-pcm-method-is-pinned",
            constants.get("DECODED_PCM_HASH_METHOD"),
        ),
        _check(
            constants.get("INTRO_FIRST_MEASURE") == 1
            and constants.get("INTRO_LAST_MEASURE") == 16,
            "intro-boundary-is-measures-1-16",
            {
                "first": constants.get("INTRO_FIRST_MEASURE"),
                "last": constants.get("INTRO_LAST_MEASURE"),
            },
        ),
        _check(
            constants.get("WIDE_GRID_TOLERANCE_SECONDS") == 0.30
            and constants.get("PRODUCTION_GRID_TOLERANCE_SECONDS") == 0.10,
            "historical-grid-tolerances-preserved",
            {
                "wide": constants.get("WIDE_GRID_TOLERANCE_SECONDS"),
                "production": constants.get("PRODUCTION_GRID_TOLERANCE_SECONDS"),
            },
        ),
        _check(
            len(separator_calls) == 1,
            "exactly-one-separator-build-call-in-producer",
            separator_calls,
        ),
        _check(
            len(remote_calls) == 1 and remote_calls[0] == "capture_fresh_compatibility.remote",
            "only-local-entrypoint-invokes-one-remote-capture",
            remote_calls,
        ),
        _check(
            'len(intro_grid) != 244' in source,
            "244-row-intro-grid-has-fail-closed-guard",
        ),
        _check(
            'dtype="int16", always_2d=True' in source
            and "hashlib.sha256(audio.tobytes()).hexdigest()" in source,
            "decoded-pcm-hash-uses-pinned-soundfile-convention",
        ),
        _check(
            '"referenceFree": True' in source
            and '"professionalReferenceUsedByAnalyzer": False' in source,
            "raw-cache-reference-free-attestations-preserved",
        ),
        _check(
            '"freshCompatibilityEvidenceOnly": True' in source
            and '"historicalProvenanceClaimed": False' in source
            and '"productionModified": False' in source
            and '"liveEndpointModified": False' in source
            and '"professionalReferenceUsedAtRuntime": False' in source
            and '"historicalArtifactsOverwritten": False' in source,
            "comparator-safety-attestations-are-literal-and-fail-closed",
        ),
        _check(
            "_ensure_debug_path" in source
            and "Refusing write outside isolated debug root" in source
            and "_write_new_text" in source
            and "Refusing to overwrite existing compatibility artifact" in source,
            "isolated-debug-write-and-no-overwrite-guards-present",
        ),
        _check(
            all(fragment not in source for fragment in FORBIDDEN_WRITE_FRAGMENTS),
            "historical-production-write-paths-not-embedded",
            [
                fragment
                for fragment in FORBIDDEN_WRITE_FRAGMENTS
                if fragment in source
            ],
        ),
        _check(
            all(fragment not in imports_lower for fragment in FORBIDDEN_IMPORT_FRAGMENTS),
            "professional-reference-modules-not-imported",
            imports,
        ),
        _check(
            not any(
                name == forbidden or name.endswith("." + forbidden)
                for name in calls
                for forbidden in FORBIDDEN_CALL_NAMES
            ),
            "no-deploy-retrain-fit-calls",
            sorted(
                {
                    name
                    for name in calls
                    if any(
                        name == forbidden or name.endswith("." + forbidden)
                        for forbidden in FORBIDDEN_CALL_NAMES
                    )
                }
            ),
        ),
        _check(
            "HISTORICAL_WIDE_RECALL_SWEEPS" in source
            and "note_events_from_predict" in source
            and "estimate_reference_free_timing" in source
            and "build_subdivision_grid" in source,
            "historical-reference-free-basic-pitch-semantics-reused",
        ),
        _check(
            "source_metadata.get(\"duration\")" in source
            and 'json.dumps(raw_cache, indent=2) + "\\n"' in source,
            "historical-cache-json-shape-byte-conventions-preserved",
        ),
        _check(
            "recorded_commands" in source
            and "len(recorded_commands) != 3" in source,
            "single-graph-command-capture-is-guarded",
        ),
        _check(
            "installedPackageInventorySha256" in source
            and "runtimeFingerprintSha256" in source
            and "modelCacheManifestSha256" in source
            and "modelPayloadCaptureComplete" in source,
            "runtime-package-model-provenance-digests-captured",
        ),
        _check(
            len(write_call_nodes) >= 1,
            "producer-has-explicit-isolated-artifact-write-path",
            len(write_call_nodes),
        ),
        _check(
            EXPECTED_DEBUG_FRAGMENT
            in str(design.get("recommendedFutureArtifacts", {}).get("runDirectory", "")),
            "design-recommends-isolated-debug-run-directory",
            design.get("recommendedFutureArtifacts", {}).get("runDirectory"),
        ),
        _check(
            design.get("provenanceBoundary", {}).get("freshRunMayCloseHistoricalGap")
            is False,
            "design-keeps-historical-provenance-gap-open",
        ),
        _check(
            design.get("provenanceBoundary", {}).get("professionalReferenceAllowedAtRuntime")
            is False,
            "design-forbids-professional-reference-at-runtime",
        ),
    ]

    return {
        "artifact": "v143-intro-compatibility-fresh-capture-static-validation",
        "schemaVersion": 1,
        "producer": str(producer.relative_to(REPO_ROOT)),
        "producerSha256": _sha256_text(source),
        "design": str(design_path.relative_to(REPO_ROOT)),
        "staticOnly": True,
        "modalOrGpuExecuted": False,
        "passed": all(check["passed"] for check in checks),
        "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producer", type=Path, default=DEFAULT_PRODUCER)
    parser.add_argument("--design", type=Path, default=DEFAULT_DESIGN)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = validate(args.producer, args.design)
    except (OSError, ValueError, SyntaxError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "STATIC_VALIDATION_ERROR", "error": str(exc)}, indent=2))
        return 2

    rendered = json.dumps(result, indent=2) + "\n"
    print(rendered, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
