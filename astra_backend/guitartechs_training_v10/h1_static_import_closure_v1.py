"""Read-only AST audit of internal H1 imports against the reviewed source lock.

Only static imports are covered. Dynamic imports, upstream AMT-Tools and
installed distributions still require independent, pinned review.
"""
from __future__ import annotations
import ast
import json
from pathlib import Path
from guitartechs_training_v10.h1_source_lock_audit_v1 import verify_lock

PREFIX = "astra_backend/"
# The frozen real_training module explicitly prepends tabcnn_runtime to sys.path.
SPECIAL_MODULE_PATHS = {"preprocessing": "astra_backend/tabcnn_runtime/preprocessing.py"}


def _module_path(module: str) -> str:
    return PREFIX + module.replace(".", "/") + ".py"


def _within_repo(root: Path, candidate: str) -> bool:
    target = (root / candidate).resolve()
    return target.is_file() and target.is_relative_to(root.resolve())


def internal_imports(root: Path, source_path: str) -> set[str]:
    """Find literal imports whose corresponding Python files exist in this checkout."""
    current = Path(source_path)
    if not current.as_posix().startswith(PREFIX) or current.suffix != ".py":
        raise ValueError("not an astra_backend Python source")
    tree = ast.parse((root / current).read_text(encoding="utf-8"), filename=source_path)
    # Packages are namespace packages here; relative imports still resolve to parent.
    package = list(current.with_suffix("").parts[1:-1])
    found: set[str] = set()
    def include(module: str) -> None:
        direct = SPECIAL_MODULE_PATHS.get(module, _module_path(module))
        if _within_repo(root, direct):
            found.add(direct)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                include(alias.name)
        if isinstance(node, ast.ImportFrom):
            if node.level:
                if node.level > len(package):
                    raise RuntimeError("H1_RELATIVE_IMPORT_ESCAPE:" + source_path)
                prefix = package[:len(package) - node.level + 1]
                full = ".".join(prefix + ([node.module] if node.module else []))
            else:
                full = node.module or ""
            if full:
                include(full)
            for alias in node.names:
                if alias.name != "*":
                    include(".".join([full, alias.name]) if full else alias.name)
    return found


def audit_import_closure(root, lock: dict) -> dict:
    root = Path(root).resolve(strict=True)
    result = verify_lock(root, lock)
    pinned = set(lock["requiredLiveWorkflowSources"])
    omitted: dict[str, list[str]] = {}
    all_imports: set[str] = set()
    for path in sorted(pinned):
        if not path.endswith(".py"):
            continue
        imports = internal_imports(root, path)
        all_imports.update(imports)
        missing = sorted(imports - pinned)
        if missing:
            omitted[path] = missing
    if omitted:
        raise RuntimeError("H1_UNPINNED_STATIC_INTERNAL_IMPORTS:" + json.dumps(omitted, sort_keys=True))
    return {
        **result,
        "staticInternalDependencies": len(all_imports),
        "staticImportClosure": "match",
        "dynamicAndExternalDependenciesReviewed": False,
        "independentReview": "PENDING",
        "launchPermission": False,
    }


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--lock", required=True)
    args = p.parse_args()
    result = audit_import_closure(args.root, json.loads(Path(args.lock).read_text()))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
