from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "debug/v143-contextual-prune/normal-routing-e2e-structure/summary.json"

EXPECTED_BLOBS = {
    "app/api/analyze-audio-tab/route.js": "06234db3e1cc1680b18fd62a765862b213ede3db",
    "analyzer/v143_modal_http_endpoint.py": "9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6",
    "analyzer/v143_modal_live_endpoint.py": "111bf14a8f91045d3478901f8e36b88a2e7f181a",
    "analyzer/v143_vercel_audio_request_adapter.py": "6d1787f34a3b7ca781ced8e5695993a3777406a8",
    "analyzer/v143_modal_rhythm_router.py": "7849f33cd3b849283ccebfda9f721cc40704231e",
    "analyzer/v143_rhythm_deterministic_stem_provider.py": "3c6dcf9b8e7360ba1dd886810f3c14c05ac0579b",
    "analyzer/v143_rhythm_stem_provider.py": "cd180bfb35e8110f031504035af5f11e502c3dc6",
    "analyzer/v143_deterministic_separator.py": "28b3e6fe0eb761178b142cf7dcbda533f0bf918d",
    "analyzer/v143_seeded_separator.py": "fc9b4c45c208d80be7abab64a8959f2a3babcee8",
}

PYTHON_PATHS = tuple(path for path in EXPECTED_BLOBS if path.endswith(".py"))
FORBIDDEN_IMPORT_FRAGMENTS = (
    "goat",
    "guitarset",
    "splitmysong",
    "align_gomyway_professional",
    "professional_reference",
    "reference_score",
    "score_reference",
)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def parse_python(path: str) -> ast.Module:
    return ast.parse(source(path), filename=path)


def function_node(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise RuntimeError(f"function not found: {name}")


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def calls(node: ast.AST, name: str) -> list[ast.Call]:
    return [item for item in ast.walk(node) if isinstance(item, ast.Call) and dotted_name(item.func) == name]


def one_call(node: ast.AST, name: str) -> ast.Call:
    matches = calls(node, name)
    if len(matches) != 1:
        raise RuntimeError(f"expected one {name} call, found {len(matches)}")
    return matches[0]


def expr(node: ast.AST) -> str:
    return ast.unparse(node)


def keyword_map(call: ast.Call) -> dict[str, str]:
    return {item.arg: expr(item.value) for item in call.keywords if item.arg}


def imported_modules(tree: ast.Module) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def contains_all(value: str, needles: tuple[str, ...]) -> bool:
    return all(needle in value for needle in needles)


def main() -> None:
    checks: dict[str, bool] = {}
    identities: dict[str, dict[str, Any]] = {}

    for relative, expected in EXPECTED_BLOBS.items():
        path = ROOT / relative
        actual = git_blob_sha(path) if path.is_file() else "missing"
        identities[relative] = {"expectedGitBlobSha": expected, "actualGitBlobSha": actual, "matched": actual == expected}
        checks[f"identity::{relative}"] = actual == expected

    route = source("app/api/analyze-audio-tab/route.js")
    checks["vercel::rhythm_only_v143_selection"] = contains_all(route, (
        "process.env.ANALYZER_API_URL;",
        "process.env.ANALYZER_API_URL_V143;",
        "transcriptionType === 'rhythm'",
        "Boolean(v143RhythmAnalyzerUrl)",
        "? v143RhythmAnalyzerUrl",
        ": legacyAnalyzerUrl;",
        "fetch(\n      analyzerUrl,",
    ))
    checks["vercel::private_blob_handoff"] = contains_all(route, (
        "token: analyzerToken", "blobToken,", "audioUrl,", "pathname,", "song,", "artist,", "transcriptionType,", "conditioning,",
    ))
    checks["vercel::runtime_safety_fail_closed"] = contains_all(route, (
        "liveV143?.referenceFree === true",
        "liveV143?.professionalReferenceUsed === false",
        "liveV143?.referenceRuntimeInputUsed === false",
        "liveV143?.runtimeLabelsRequired === false",
        "usingV143RhythmAnalyzer &&",
        "!v143RuntimeSafetyVerified",
        "status: 502",
    ))

    http_tree = parse_python("analyzer/v143_modal_http_endpoint.py")
    http_source = source("analyzer/v143_modal_http_endpoint.py")
    dispatch = function_node(http_tree, "dispatch_authorized_request")
    analyze = function_node(http_tree, "analyze")
    dispatch_text = ast.unparse(dispatch)
    checks["http::worker_identity"] = contains_all(http_source, (
        'HTTP_APP_NAME = "dadrock-v143-http-bridge"',
        'WORKER_APP_NAME = "dadrock-v143-ai-tab-live"',
        'WORKER_FUNCTION_NAME = "rhythm_v143_request"',
    ))
    checks["http::rhythm_worker_lead_bass_legacy"] = contains_all(dispatch_text, (
        "if transcription_type == 'rhythm'", "return rhythm_handler(dict(payload))", "return legacy_handler(dict(payload))",
    ))
    lookup = one_call(analyze, "modal.Function.from_name")
    checks["http::normal_worker_lookup"] = len(lookup.args) == 2 and expr(lookup.args[0]) == "WORKER_APP_NAME" and expr(lookup.args[1]) == "WORKER_FUNCTION_NAME" and len(calls(analyze, "worker.remote")) == 1

    live_tree = parse_python("analyzer/v143_modal_live_endpoint.py")
    live_source = source("analyzer/v143_modal_live_endpoint.py")
    live_fn = function_node(live_tree, "rhythm_v143_request")
    process_call = one_call(live_fn, "process_vercel_audio_request")
    process_keywords = keyword_map(process_call)
    checks["live::worker_app_identity"] = 'modal.App("dadrock-v143-ai-tab-live")' in live_source
    checks["live::normal_adapter_and_deterministic_provider"] = process_keywords.get("rhythm_stem_provider") == "build_deterministic_rhythm_stem_bundle" and process_keywords.get("rhythm_router") == "rhythm_router"
    live_text = ast.unparse(live_fn)
    checks["live::anti_leakage_contract"] = contains_all(live_text, (
        "'referenceFree': True", "'professionalReferenceUsed': False", "'referenceRuntimeInputUsed': False", "'runtimeLabelsRequired': False",
        "'separatorDeterministic': True", "'separatorSeed': 143", "'demucsShifts': 1",
    ))

    adapter_tree = parse_python("analyzer/v143_vercel_audio_request_adapter.py")
    adapter_fn = function_node(adapter_tree, "process_vercel_audio_request")
    adapter_text = ast.unparse(adapter_fn)
    checks["adapter::request_scoped_tempdir"] = "tempfile.TemporaryDirectory(prefix='dadrock-v143-')" in adapter_text
    download_pos, normalize_pos, router_pos = adapter_text.find("download_blob("), adapter_text.find("normalize_audio("), adapter_text.find("rhythm_router(")
    checks["adapter::download_normalize_route_order"] = -1 < download_pos < normalize_pos < router_pos
    router_call = one_call(adapter_fn, "rhythm_router")
    router_keywords = keyword_map(router_call)
    checks["adapter::normal_handoff"] = bool(router_call.args) and expr(router_call.args[0]) == "normalized_path" and router_keywords.get("legacy_analyzer") == "legacy_analyzer" and router_keywords.get("rhythm_stem_provider") == "rhythm_stem_provider"

    router_tree = parse_python("analyzer/v143_modal_rhythm_router.py")
    router_fn = function_node(router_tree, "route_normalized_audio")
    router_text = ast.unparse(router_fn)
    checks["router::non_rhythm_legacy_fallback"] = "if requested != 'rhythm':\n        return legacy_analyzer(str(full_mix), requested)" in router_text
    provider_call = one_call(router_fn, "rhythm_stem_provider")
    pipeline_call = one_call(router_fn, "rhythm_pipeline")
    checks["router::rhythm_provider_and_paired_pipeline"] = bool(provider_call.args) and expr(provider_call.args[0]) == "full_mix" and len(pipeline_call.args) >= 4 and expr(pipeline_call.args[0]) == "full_mix"

    deterministic_provider_source = source("analyzer/v143_rhythm_deterministic_stem_provider.py")
    deterministic_provider_tree = parse_python("analyzer/v143_rhythm_deterministic_stem_provider.py")
    deterministic_provider_fn = function_node(deterministic_provider_tree, "build_deterministic_rhythm_stem_bundle")
    bundle_call = one_call(deterministic_provider_fn, "build_rhythm_stem_bundle")
    checks["provider::deterministic_default_and_forwarding"] = "separator_builder: DeterministicSeparatorBuilder = build_deterministic_v143_stems" in deterministic_provider_source and keyword_map(bundle_call).get("separator_builder") == "separator_builder"

    stem_tree = parse_python("analyzer/v143_rhythm_stem_provider.py")
    stem_source = source("analyzer/v143_rhythm_stem_provider.py")
    stem_fn = function_node(stem_tree, "build_rhythm_stem_bundle")
    separator_call = one_call(stem_fn, "separator_builder")
    checks["stem_bundle::separator_invoked_once"] = len(separator_call.args) == 2 and expr(separator_call.args[0]) == "normalized" and expr(separator_call.args[1]) == "output_dir"
    checks["stem_bundle::paired_independent_views"] = contains_all(stem_source, (
        'result.get("directGuitar")', 'result.get("cascadeGuitar")', "direct.resolve() == cascade.resolve()", "candidate_stem_paths=(direct, cascade)", "carrier_stem_a_path=direct", "carrier_stem_b_path=cascade",
    ))

    deterministic_tree = parse_python("analyzer/v143_deterministic_separator.py")
    deterministic_source = source("analyzer/v143_deterministic_separator.py")
    deterministic_fn = function_node(deterministic_tree, "build_deterministic_v143_stems")
    seeded_call = one_call(deterministic_fn, "build_seeded_v143_stems")
    checks["deterministic_wrapper::seeded_scheduler_once"] = "from v143_seeded_separator import build_seeded_v143_stems" in deterministic_source and len(seeded_call.args) == 2 and expr(seeded_call.args[0]) == "input_audio" and expr(seeded_call.args[1]) == "output_dir"
    checks["deterministic_wrapper::frozen_settings"] = contains_all(deterministic_source, ("PRODUCTION_SEPARATOR_SEED = 143", 'settings.get("demucsShifts")', 'settings.get("demucsOverlap")', 'settings.get("demucsSegmentSize")', 'settings.get("deterministicSeed")'))

    seeded_source = source("analyzer/v143_seeded_separator.py")
    checks["scheduler::candidate_entrypoint_and_spawn"] = "def build_seeded_v143_stems(" in seeded_source and ('get_context("spawn")' in seeded_source or "get_context('spawn')" in seeded_source)

    restricted_imports: dict[str, list[str]] = {}
    for relative in PYTHON_PATHS:
        modules = imported_modules(parse_python(relative))
        restricted_imports[relative] = sorted(module for module in modules if any(fragment in module.lower() for fragment in FORBIDDEN_IMPORT_FRAGMENTS))
    checks["safety::no_restricted_or_reference_scoring_imports"] = not any(restricted_imports.values())

    all_passed = all(checks.values())
    summary = {
        "schemaVersion": 1,
        "gate": "v143-normal-routing-e2e-structure",
        "scope": "normal-routing-composition-only",
        "allPassed": all_passed,
        "checks": checks,
        "sourceIdentities": identities,
        "restrictedImportHits": restricted_imports,
        "callGraph": [
            "app/api/analyze-audio-tab/route.js",
            "v143_modal_http_endpoint.analyze",
            "v143_modal_live_endpoint.rhythm_v143_request",
            "v143_vercel_audio_request_adapter.process_vercel_audio_request",
            "v143_modal_rhythm_router.route_normalized_audio",
            "v143_rhythm_deterministic_stem_provider.build_deterministic_rhythm_stem_bundle",
            "v143_rhythm_stem_provider.build_rhythm_stem_bundle",
            "v143_deterministic_separator.build_deterministic_v143_stems",
            "v143_seeded_separator.build_seeded_v143_stems",
        ],
        "schedulerBlob": EXPECTED_BLOBS["analyzer/v143_seeded_separator.py"],
        "gate1StructuralEvidenceReused": True,
        "gate2RuntimeEvidenceReused": True,
        "approvedFixtureInvoked": False,
        "audioBytesRead": False,
        "modelExecutionPerformed": False,
        "modalCalled": False,
        "gpuUsed": False,
        "referenceFacingInputs": 0,
        "referenceFacingAccuracyScored": False,
        "referenceScoreCalls": 0,
        "qualityVerdictMade": False,
        "rawAudioRetained": False,
        "stemBytesRetained": False,
        "crossRequestPersistence": False,
        "productionWorkerChanged": False,
        "productionBridgeChanged": False,
        "vercelChanged": False,
        "mainMergePerformed": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
