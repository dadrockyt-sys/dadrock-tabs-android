#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "analyzer"
SHADOW_PATH = ANALYZER / "v143_contextual_prune_shadow_modal.py"
REPORT_PATH = (
    ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "contextual-prune-shadow-packaging-report.json"
)

PROTECTED_LIVE_MODULES = {
    "v143_modal_live_endpoint",
    "v143_modal_rhythm_router",
    "v143_reference_free_rhythm_pipeline",
    "v143_rhythm_runtime",
    "v143_production_engine",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _literal_assignment(path: Path, name: str) -> Any:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == name:
            return ast.literal_eval(node.value)
    raise RuntimeError(f"Missing literal assignment {name} in {path}")


def _local_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        candidates: list[str] = []
        if isinstance(node, ast.Import):
            candidates.extend(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            candidates.append(node.module.split(".", 1)[0])
        for module in candidates:
            if (ANALYZER / f"{module}.py").exists():
                found.add(module)
    return found


def main() -> None:
    _require(SHADOW_PATH.exists(), f"Missing shadow source: {SHADOW_PATH}")
    modules_raw = _literal_assignment(SHADOW_PATH, "SHADOW_MODULES")
    _require(isinstance(modules_raw, tuple), "SHADOW_MODULES must remain a literal tuple")
    modules = tuple(str(value) for value in modules_raw)
    module_set = set(modules)

    _require(
        "v143_ai_tab_gpu_worker" in module_set,
        "Modal shadow image does not package v143_ai_tab_gpu_worker",
    )
    _require(
        not (module_set & PROTECTED_LIVE_MODULES),
        "Shadow image packages protected live V143 modules: "
        + repr(sorted(module_set & PROTECTED_LIVE_MODULES)),
    )

    missing_files: list[str] = []
    dependencies: dict[str, list[str]] = {}
    missing_dependencies: dict[str, list[str]] = {}

    for module in modules:
        path = ANALYZER / f"{module}.py"
        if not path.exists():
            missing_files.append(module)
            continue
        local = sorted(_local_imports(path))
        dependencies[module] = local
        missing = sorted(
            dependency
            for dependency in local
            if dependency != "v143_contextual_prune_shadow_modal"
            and dependency not in module_set
        )
        if missing:
            missing_dependencies[module] = missing

    shadow_imports = sorted(_local_imports(SHADOW_PATH))
    missing_shadow_imports = sorted(
        dependency for dependency in shadow_imports if dependency not in module_set
    )

    _require(not missing_files, f"SHADOW_MODULES contains missing files: {missing_files}")
    _require(
        not missing_shadow_imports,
        f"Shadow source imports local modules not packaged in SHADOW_MODULES: {missing_shadow_imports}",
    )
    _require(
        not missing_dependencies,
        "Packaged shadow modules have unresolved local imports: "
        + json.dumps(missing_dependencies, sort_keys=True),
    )

    report = {
        "schemaVersion": 1,
        "gate": "v143-contextual-prune-shadow-modal-local-dependency-closure",
        "shadowModuleCount": len(modules),
        "shadowModules": list(modules),
        "shadowLocalImports": shadow_imports,
        "gpuWorkerDependencyPackaged": True,
        "allPackagedModuleFilesPresent": True,
        "allLocalImportsPackaged": True,
        "protectedLiveModulesPackaged": False,
        "dependencyGraph": dependencies,
        "professionalReferenceOpened": False,
        "liveEndpointDeployedOrModified": False,
        "productionModified": False,
        "gatePassed": True,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("=== V143 CONTEXTUAL PRUNE SHADOW PACKAGING GATE ===")
    print("GPU_WORKER_PACKAGED", True)
    print("ALL_LOCAL_IMPORTS_PACKAGED", True)
    print("PROTECTED_LIVE_MODULES_PACKAGED", False)
    print("PROFESSIONAL_REFERENCE_OPENED", False)
    print("PRODUCTION_MODIFIED", False)
    print(f"WROTE={REPORT_PATH}")


if __name__ == "__main__":
    main()
