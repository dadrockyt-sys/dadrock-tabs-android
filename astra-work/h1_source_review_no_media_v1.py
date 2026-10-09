#!/usr/bin/env python3
"""Review-only H1 source-closure inspection: no imports of project code, no media.

Requires an already available repository checkout. Reports static local closure,
executable package initializers, dynamic-import indications, and exact upstream
identity when explicitly staged. Never authorizes, creates or runs a launch.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

LOCK_SCHEMA = "astra-h1-pilot-reviewed-source-lock-draft-v1"
LOCK_STATUS = "DRAFT_REQUIRES_INDEPENDENT_REVIEW_NOT_LAUNCH_AUTHORIZATION"
WORKFLOW = ".github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml"
BACKEND = "astra_backend/"
SPECIAL = {"preprocessing": "astra_backend/tabcnn_runtime/preprocessing.py"}
UPSTREAM = {
    "models/common.py": "84beb4cf251b9cb9274d10cf203318314181af31",
    "models/tabcnn.py": "e09856db2fffd77642e005ab509846acc894b886",
    "tools/instrument.py": "eddc48a8b95de057035cd11ea2d1951e754ef349",
    "tools/constants.py": "79666ea0c5b0214ca664da454069b8d286cc5c18",
}
GENERATED_INIT = {
    "__init__.py": b"",
    "models/__init__.py": b"",
    "tools/__init__.py": b"from .constants import *\nfrom .instrument import *\n",
}
DYNAMIC_CALLS = {
    "__import__", "importlib.import_module", "importlib.util.spec_from_file_location",
    "exec", "eval", "runpy.run_path", "runpy.run_module", "sys.path.insert", "sys.path.append",
}


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def read_verified(root: Path, relative: str) -> bytes:
    if not isinstance(relative, str) or relative.startswith("/") or "\\" in relative:
        raise ValueError("INVALID_SOURCE_PATH")
    parts = relative.split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise ValueError("INVALID_SOURCE_PATH")
    path = root / relative
    if path.is_symlink() or not path.is_file() or path.resolve() != path:
        raise RuntimeError("MISSING_OR_SYMLINK_SOURCE:" + relative)
    return path.read_bytes()


def literal_required_set(text: str) -> set[str]:
    sets = re.findall(r"\brequired\s*=\s*(\{[^{}]*\})", text, re.S)
    if len(sets) != 1:
        raise RuntimeError("WORKFLOW_REQUIRED_SET_MISSING_OR_AMBIGUOUS")
    result = ast.literal_eval(sets[0])
    if not isinstance(result, set) or not all(type(s) is str for s in result):
        raise RuntimeError("WORKFLOW_REQUIRED_SET_INVALID")
    return result


def qualified_name(call_node: ast.AST) -> str:
    if isinstance(call_node, ast.Name):
        return call_node.id
    if isinstance(call_node, ast.Attribute):
        lhs = qualified_name(call_node.value)
        return lhs + "." + call_node.attr if lhs else ""
    return ""


def resolve_local_files(root: Path, module: str) -> set[str]:
    """Resolve importable source modules and their executable ancestor inits."""
    found: set[str] = set()
    candidates = [SPECIAL[module]] if module in SPECIAL else [
        BACKEND + module.replace(".", "/") + ".py",
        BACKEND + module.replace(".", "/") + "/__init__.py",
    ]
    for file in candidates:
        path = root / file
        if path.is_file():
            if path.is_symlink() or path.resolve() != path:
                raise RuntimeError("UNTRUSTED_SOURCE_LINK:" + file)
            found.add(file)
            directory = path.parent
            top = (root / BACKEND).resolve()
            while directory != top and directory.is_relative_to(top):
                initializer = directory / "__init__.py"
                if initializer.is_file():
                    if initializer.is_symlink() or initializer.resolve() != initializer:
                        raise RuntimeError("UNTRUSTED_PACKAGE_INIT:" + str(initializer))
                    found.add(initializer.relative_to(root).as_posix())
                directory = directory.parent
    return found


def inspect_imports(root: Path, path: str) -> tuple[set[str], list[dict], set[str]]:
    source = read_verified(root, path)
    syntax = ast.parse(source, filename=path)
    internal: set[str] = set()
    indicators: list[dict] = []
    external: set[str] = set()
    backend_names = {
        p.name for p in (root / BACKEND).iterdir()
        if p.is_dir() and not p.name.startswith(".")
    }
    pkg = Path(path).relative_to(BACKEND).parts[:-1]
    def add(mod: str):
        if not mod:
            return
        matches = resolve_local_files(root, mod)
        internal.update(matches)
        if not matches and mod.split(".")[0] not in backend_names and mod not in SPECIAL:
            external.add(mod.split(".")[0])
    for node in ast.walk(syntax):
        if isinstance(node, ast.Import):
            for alias in node.names:
                add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                if node.level > len(pkg):
                    raise RuntimeError("RELATIVE_IMPORT_ESCAPES_PACKAGE:" + path)
                base = list(pkg[:len(pkg) - node.level + 1])
                mod = ".".join(base + ([node.module] if node.module else []))
            else:
                mod = node.module or ""
            add(mod)
            for alias in node.names:
                if alias.name != "*":
                    add(mod + "." + alias.name if mod else alias.name)
        elif isinstance(node, ast.Call):
            target = qualified_name(node.func)
            if target in DYNAMIC_CALLS:
                indicators.append({"line": node.lineno, "call": target})
    return internal, sorted(indicators, key=lambda x: (x["line"], x["call"])), external


def verify_upstream(root: Path, expected: dict[str, str] = UPSTREAM) -> dict:
    root = root.resolve(strict=True)
    verified = []
    for name, want in expected.items():
        relative = "amt_tools/" + name
        if git_blob(read_verified(root, relative)) != want:
            raise RuntimeError("UPSTREAM_GIT_BLOB_MISMATCH:" + name)
        verified.append(name)
    for name, raw in GENERATED_INIT.items():
        if read_verified(root, "amt_tools/" + name) != raw:
            raise RuntimeError("UPSTREAM_GENERATED_INIT_MISMATCH:" + name)
    return {"upstreamBlobCount": len(verified), "generatedInitCount": len(GENERATED_INIT),
            "identityStatus": "match", "runtimeCompatibility": "NOT_RUN"}


def audit(root: Path, lock: dict, upstream_root: Path | None = None) -> dict:
    root = root.resolve(strict=True)
    if lock.get("schema") != LOCK_SCHEMA or lock.get("status") != LOCK_STATUS:
        raise RuntimeError("DRAFT_LOCK_IDENTITY_MISMATCH")
    required = lock.get("requiredLiveWorkflowSources")
    extras = lock.get("additionalOfflineTestAndBudgetSources")
    if not isinstance(required, dict) or not isinstance(extras, dict) or not required:
        raise RuntimeError("DRAFT_LOCK_MISSING_GROUPS")
    if set(required) & set(extras) or WORKFLOW not in required:
        raise RuntimeError("DRAFT_LOCK_DUPLICATE_OR_MISSING_WORKFLOW")
    for path, sha in {**required, **extras}.items():
        if not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{40}", sha):
            raise RuntimeError("DRAFT_LOCK_INVALID_SHA:" + path)
        if git_blob(read_verified(root, path)) != sha:
            raise RuntimeError("DRAFT_LOCK_BLOB_MISMATCH:" + path)
    workflow = read_verified(root, WORKFLOW).decode()
    if literal_required_set(workflow) != set(required):
        raise RuntimeError("WORKFLOW_LOCK_SET_MISMATCH")
    internals: set[str] = set()
    dynamic: dict[str, list[dict]] = {}
    externals: set[str] = set()
    for path in sorted(required):
        if not path.endswith(".py"):
            continue
        found, hints, outside = inspect_imports(root, path)
        internals.update(found)
        externals.update(outside)
        if hints:
            dynamic[path] = hints
    unpinned = sorted(internals - set(required))
    if unpinned:
        raise RuntimeError("UNPINNED_EXECUTABLE_LOCAL_SOURCE:" + json.dumps(unpinned))
    upstream = verify_upstream(upstream_root) if upstream_root else {"identityStatus": "NOT_RUN"}
    return {
        "schema": "astra-h1-offline-source-risk-audit-v1",
        "requiredSourceCount": len(required),
        "additionalSourceCount": len(extras),
        "staticInternalSourceCount": len(internals),
        "staticStatus": "MATCH_PENDING_INDEPENDENT_REVIEW",
        "potentialDynamicCalls": dynamic,
        "unresolvedExternalModuleRoots": sorted(externals),
        "externalPinAudit": upstream,
        "completeDynamicImportClosure": False,
        "independentReview": "PENDING",
        "launchPermission": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--lock", type=Path, required=True)
    p.add_argument("--upstream-root", type=Path)
    args = p.parse_args()
    result = audit(args.root, json.loads(args.lock.read_text()), args.upstream_root)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
