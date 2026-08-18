from __future__ import annotations

import ast
from pathlib import Path


SOURCE_PATH = Path(__file__).with_name("v143_modal_live_endpoint.py")


def _function_source(source: str, tree: ast.Module, name: str) -> str:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(source, node) or ""
    raise RuntimeError(f"Missing function: {name}")


def _assigned_string_tuple(tree: ast.Module, name: str) -> tuple[str, ...]:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        if not isinstance(node.value, (ast.Tuple, ast.List)):
            return ()
        values: list[str] = []
        for element in node.value.elts:
            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                values.append(element.value)
        return tuple(values)
    return ()


def main() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    modules = set(_assigned_string_tuple(tree, "V143_MODULES"))
    rhythm_source = _function_source(source, tree, "rhythm_v143_request")
    legacy_source = _function_source(source, tree, "_legacy_request")
    dispatch_source = _function_source(source, tree, "dispatch_authorized_request")
    dependency_source = _function_source(source, tree, "rhythm_dependency_smoke")

    deterministic_modules = {
        "v143_seeded_audio_separator_cli",
        "v143_seeded_separator",
        "v143_deterministic_separator",
        "v143_rhythm_deterministic_stem_provider",
    }

    checks = {
        "Deterministic separator modules packaged": deterministic_modules.issubset(modules),
        "Rhythm imports deterministic stem provider": (
            "from v143_rhythm_deterministic_stem_provider import" in rhythm_source
            and "build_deterministic_rhythm_stem_bundle" in rhythm_source
        ),
        "Rhythm request uses deterministic stem provider": (
            "rhythm_stem_provider=build_deterministic_rhythm_stem_bundle" in rhythm_source
        ),
        "Legacy stem provider removed from Rhythm request": (
            "from v143_rhythm_stem_provider import build_rhythm_stem_bundle" not in rhythm_source
            and "rhythm_stem_provider=build_rhythm_stem_bundle" not in rhythm_source
        ),
        "Seed 143 advertised by live V143 identity": '"separatorSeed": 143' in rhythm_source,
        "Deterministic separator advertised": '"separatorDeterministic": True' in rhythm_source,
        "Demucs shifts=1 advertised": '"demucsShifts": 1' in rhythm_source,
        "Reference-free identity preserved": '"referenceFree": True' in rhythm_source,
        "Professional reference excluded": '"professionalReferenceUsed": False' in rhythm_source,
        "Runtime labels not required": '"runtimeLabelsRequired": False' in rhythm_source,
        "Dependency smoke imports deterministic provider": (
            "build_deterministic_rhythm_stem_bundle" in dependency_source
            and "PRODUCTION_SEPARATOR_SEED" in dependency_source
        ),
        "Lead/Bass still use legacy analyzer": (
            "legacy.analyze_audio_file" in legacy_source
            and "build_deterministic_rhythm_stem_bundle" not in legacy_source
        ),
        "Dispatch remains Rhythm-only": (
            'if transcription_type == "rhythm":' in dispatch_source
            and "return rhythm_handler(dict(payload))" in dispatch_source
            and "return legacy_handler(dict(payload))" in dispatch_source
        ),
    }

    ready = all(checks.values())

    print("=== V143 DETERMINISTIC LIVE-ENDPOINT WIRING VERIFIED ===")
    for label, value in checks.items():
        print(f"{label}: {value}")
    print(f"READY FOR MODAL DEPENDENCY SMOKE: {ready}")

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
