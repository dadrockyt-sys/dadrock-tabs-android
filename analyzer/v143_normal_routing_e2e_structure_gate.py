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

PYTHON_PATHS = tuple(
    path for path in EXPECTED_BLOBS if path.endswith(".py")
)

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
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def parse_python(path: str) -> ast.Module:
    return ast.parse(source(path), filename=path)


def imported_modules(tree: ast.Module) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.append(node.module)
    return modules


def function_node(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise RuntimeError(f"function not found: {name}")


def call_count(node: ast.AST, function_name: str) -> int:
    count = 0
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if isinstance(func, ast.Name) and func.id == function_name:
            count += 1
        elif isinstance(func, ast.Attribute) and func.attr == function_name:
            count += 1
    return count


def contains_all(value: str, needles: tuple[str, ...]) -> bool:
    return all(needle in value for needle in needles)


def main() -> None:
    checks: dict[str, bool] = {}
    identities: dict[str, dict[str, Any]] = {}

    for relative, expected in EXPECTED_BLOBS.items():
        path = ROOT / relative
        actual = git_blob_sha(path) if path.is_file() else "missing"
        identities[relative] = {
            "expectedGitBlobSha": expected,
            "actualGitBlobSha": actual,
            "matched": actual == expected,
        }
        checks[f"identity::{relative}"] = actual == expected

    route = source("app/api/analyze-audio-tab/route.js")
    checks["vercel::v143_url_is_separate"] = (
        "process.env.ANALYZER_API_URL_V143;" in route
        and "process.env.ANALYZER_API_URL;" in route
    )
    checks["vercel::rhythm_only_selection"] = contains_all(
        route,
        (
            "transcriptionType === 'rhythm'",
            "Boolean(v143RhythmAnalyzerUrl)",
            "usingV143RhythmAnalyzer",
            "? v143RhythmAnalyzerUrl",
            ": legacyAnalyzerUrl;",
        ),
    )
    checks["vercel::normal_fetch_uses_selected_url"] = (
        "fetch(\n      analyzerUrl," in route
        or "fetch(analyzerUrl," in route
    )
    checks["vercel::request_contract_preserved"] = contains_all(
        route,
        (
            "token: analyzerToken",
            "blobToken,",
            "audioUrl,",
            "pathname,",
            "song,",
            "artist,",
            "transcriptionType,",
            "conditioning,",
        ),
    )
    checks["vercel::runtime_safety_fail_closed"] = contains_all(
        route,
        (
            "liveV143?.referenceFree === true",
            "liveV143?.professionalReferenceUsed === false",
            "liveV143?.referenceRuntimeInputUsed === false",
            "liveV143?.runtimeLabelsRequired === false",
            "usingV143RhythmAnalyzer &&",
            "!v143RuntimeSafetyVerified",
            "status: 502",
        ),
    )
    checks["vercel::canary_identity_propagated"] = contains_all(
        route,
        (
            "rhythmCanaryActive:",
            "usingV143RhythmAnalyzer",
        ),
    )

    http_path = "analyzer/v143_modal_http_endpoint.py"
    http_source = source(http_path)
    http_tree = parse_python(http_path)
    http_dispatch = function_node(http_tree, "dispatch_authorized_request")
    http_analyze = function_node(http_tree, "analyze")
    checks["http::worker_identity"] = contains_all(
        http_source,
        (
            'HTTP_APP_NAME = "dadrock-v143-http-bridge"',
            'WORKER_APP_NAME = "dadrock-v143-ai-tab-live"',
            'WORKER_FUNCTION_NAME = "rhythm_v143_request"',
        ),
    )
    checks["http::rhythm_dispatches_to_worker_handler"] = contains_all(
        ast.unparse(http_dispatch),
        (
            "if transcription_type == 'rhythm'",
            "return rhythm_handler(dict(payload))",
            "return legacy_handler(dict(payload))",
        ),
    )
    analyze_text = ast.unparse(http_analyze)
    checks["http::normal_worker_lookup"] = contains_all(
        analyze_text,
        (
            "modal.Function.from_name(WORKER_APP_NAME, WORKER_FUNCTION_NAME)",
            "worker.remote(routed_payload)",
            "route_http_payload",
        ),
    )

    live_path = "analyzer/v143_modal_live_endpoint.py"
    live_source = source(live_path)
    live_tree = parse_python(live_path)
    live_request = function_node(live_tree, "rhythm_v143_request")
    live_text = ast.unparse(live_request)
    checks["live::worker_app_identity"] = 'modal.App("dadrock-v143-ai-tab-live")' in live_source
    checks["live::normal_request_adapter_used"] = (
        call_count(live_request, "process_vercel_audio_request") == 1
        and "from v143_vercel_audio_request_adapter import process_vercel_audio_request" in live_text
    )
    checks["live::deterministic_provider_injected"] = contains_all(
        live_text,
        (
            "from v143_rhythm_deterministic_stem_provider import build_deterministic_rhythm_stem_bundle",
            "rhythm_stem_provider=build_deterministic_rhythm_stem_bundle",
            "rhythm_router=rhythm_router",
        ),
    )
    checks["live::anti_leakage_identity_emitted"] = contains_all(
        live_text,
        (
            "'referenceFree': True",
            "'professionalReferenceUsed': False",
            "'referenceRuntimeInputUsed': False",
            "'runtimeLabelsRequired': False",
        ),
    )

    adapter_path = "analyzer/v143_vercel_audio_request_adapter.py"
    adapter_tree = parse_python(adapter_path)
    adapter_fn = function_node(adapter_tree, "process_vercel_audio_request")
    adapter_text = ast.unparse(adapter_fn)
    download_pos = adapter_text.find("download_blob(")
    normalize_pos = adapter_text.find("normalize_audio(")
    router_pos = adapter_text.find("rhythm_router(")
    checks["adapter::request_scoped_tempdir"] = "tempfile.TemporaryDirectory" in adapter_text
    checks["adapter::download_normalize_route_order"] = (
        -1 < download_pos < normalize_pos < router_pos
    )
    checks["adapter::provider_forwarded"] = (
        "rhythm_stem_provider=rhythm_stem_provider" in adapter_text
    )
    checks["adapter::handoff_safety_contract"] = contains_all(
        adapter_text,
        (
            "'normalizedBeforeRouting': True",
            "'professionalReferenceUsed': False",
            "'runtimeLabelsRequired': False",
        ),
    )

    router_path = "analyzer/v143_modal_rhythm_router.py"
    router_tree = parse_python(router_path)
    router_fn = function_node(router_tree, "route_normalized_audio")
    router_text = ast.unparse(router_fn)
    provider_pos = router_text.find("bundle = rhythm_stem_provider(full_mix)")
    pipeline_pos = router_text.find("rhythm_result = rhythm_pipeline(")
    checks["router::non_rhythm_legacy_fallback"] = contains_all(
        router_text,
        (
            "if requested != 'rhythm'",
            "return legacy_analyzer(str(full_mix), requested)",
        ),
    )
    checks["router::rhythm_provider_before_pipeline"] = (
        -1 < provider_pos < pipeline_pos
    )
    checks["router::reference_free_route_identity"] = contains_all(
        router_text,
        (
            "'mode': 'v143-reference-free-rhythm-only'",
            "'professionalReferenceUsed': False",
            "'runtimeLabelsRequired': False",
        ),
    )

    deterministic_provider_path = "analyzer/v143_rhythm_deterministic_stem_provider.py"
    deterministic_provider_tree = parse_python(deterministic_provider_path)
    deterministic_provider_fn = function_node(
        deterministic_provider_tree,
        "build_deterministic_rhythm_stem_bundle",
    )
    deterministic_provider_text = ast.unparse(deterministic_provider_fn)
    checks["provider::deterministic_wrapper_default"] = (
        "separator_builder: DeterministicSeparatorBuilder=build_deterministic_v143_stems"
        in deterministic_provider_text.replace(" ", "")
    )
    checks["provider::builder_forwarded_to_bundle"] = (
        "separator_builder=separator_builder" in deterministic_provider_text
        and call_count(deterministic_provider_fn, "build_rhythm_stem_bundle") == 1
    )

    stem_provider_path = "analyzer/v143_rhythm_stem_provider.py"
    stem_provider_tree = parse_python(stem_provider_path)
    stem_provider_fn = function_node(stem_provider_tree, "build_rhythm_stem_bundle")
    stem_provider_text = ast.unparse(stem_provider_fn)
    checks["stem_bundle::supplied_separator_invoked_once"] = (
        call_count(stem_provider_fn, "separator_builder") == 1
        and "result = separator_builder(normalized, output_dir)" in stem_provider_text
    )
    checks["stem_bundle::paired_independent_views_required"] = contains_all(
        stem_provider_text,
        (
            "result.get('directGuitar')",
            "result.get('cascadeGuitar')",
            "direct.resolve() == cascade.resolve()",
            "candidate_stem_paths=(direct, cascade)",
            "carrier_stem_a_path=direct",
            "carrier_stem_b_path=cascade",
        ),
    )

    deterministic_path = "analyzer/v143_deterministic_separator.py"
    deterministic_tree = parse_python(deterministic_path)
    deterministic_fn = function_node(deterministic_tree, "build_deterministic_v143_stems")
    deterministic_text = ast.unparse(deterministic_fn)
    checks["deterministic_wrapper::seeded_scheduler_imported"] = (
        "from v143_seeded_separator import build_seeded_v143_stems" in source(deterministic_path)
    )
    checks["deterministic_wrapper::seeded_scheduler_called_once"] = (
        call_count(deterministic_fn, "build_seeded_v143_stems") == 1
        and "build_seeded_v143_stems(input_audio, output_dir)" in deterministic_text
    )
    checks["deterministic_wrapper::frozen_settings_enforced"] = contains_all(
        deterministic_text,
        (
            "demucsShifts",
            "demucsOverlap",
            "demucsSegmentSize",
            "deterministicSeed",
            "PRODUCTION_SEPARATOR_SEED",
        ),
    )

    seeded_source = source("analyzer/v143_seeded_separator.py")
    checks["scheduler::candidate_entrypoint_present"] = (
        "def build_seeded_v143_stems(" in seeded_source
    )
    checks["scheduler::literal_spawn_present"] = (
        'get_context("spawn")' in seeded_source
        or "get_context('spawn')" in seeded_source
    )

    restricted_imports: dict[str, list[str]] = {}
    for relative in PYTHON_PATHS:
        modules = imported_modules(parse_python(relative))
        hits = sorted(
            module
            for module in modules
            if any(fragment in module.lower() for fragment in FORBIDDEN_IMPORT_FRAGMENTS)
        )
        restricted_imports[relative] = hits
    checks["safety::no_restricted_or_reference_scoring_imports"] = not any(
        restricted_imports.values()
    )

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
