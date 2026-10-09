#!/usr/bin/env python3
"""Offline-only source review for missing frozen-runtime enforcement.

Reads three already-local text files. Never imports model code, downloads media,
creates launch receipts, executes workflows, or declares launch approval.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

WORKFLOW = '.github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml'
LOCK = 'astra_backend/tabcnn_runtime/requirements.lock.txt'
PARITY = 'astra_backend/guitartechs_training_v10/h1_full_model_synthetic_parity_v1.py'
REFERENCE_PINS = {'python': '3.10.15', 'torch': '1.11.0+cpu', 'numpy': '1.21.6'}


def read_text(root: Path, relative: str) -> str:
    root = root.resolve(strict=True)
    file = root / relative
    if file.is_symlink() or not file.is_file() or file.resolve() != file:
        raise RuntimeError('MISSING_OR_LINKED_SOURCE:' + relative)
    return file.read_text(encoding='utf-8')


def extract_pins(workflow: str, lock: str) -> dict[str, str]:
    versions = re.findall(r'^\s*python-version:\s*[\'\"]?([0-9]+\.[0-9]+\.[0-9]+)[\'\"]?\s*$', workflow, re.M)
    if len(versions) != 1:
        raise RuntimeError('PYTHON_PIN_MISSING_OR_AMBIGUOUS')
    pins = {'python': versions[0]}
    for name in ('torch', 'numpy'):
        records = re.findall(r'^\s*' + name + r'\s*==\s*([^\s#]+)\s*(?:#.*)?$', lock, re.M | re.I)
        if len(records) != 1:
            raise RuntimeError('DEPENDENCY_PIN_MISSING_OR_AMBIGUOUS:' + name)
        pins[name] = records[0]
    if pins != REFERENCE_PINS:
        raise RuntimeError('FROZEN_DEPENDENCY_PIN_DRIFT:' + json.dumps(pins, sort_keys=True))
    return pins


def call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        owner = call_name(node.value)
        return owner + '.' + node.attr if owner else ''
    return ''


def pin_reference(node: ast.AST) -> str | None:
    text = call_name(node)
    if text == 'torch.__version__':
        return 'torch'
    if text in ('np.__version__', 'numpy.__version__'):
        return 'numpy'
    if isinstance(node, ast.Call) and call_name(node.func) == 'platform.python_version':
        return 'python'
    if text in ('sys.version', 'sys.version_info'):
        return 'python'
    return None


def scan_version_checks(script: str, pins: dict[str, str]) -> dict[str, bool]:
    tree = ast.parse(script, filename='offline-frozen-parity-probe.py')
    results = {name: False for name in pins}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        operands = [node.left, *node.comparators]
        for i, op in enumerate(node.ops):
            if not isinstance(op, (ast.Eq, ast.NotEq)):
                continue
            a, b = operands[i:i + 2]
            for candidate, value in ((a, b), (b, a)):
                identity = pin_reference(candidate)
                if identity and isinstance(value, ast.Constant) and value.value == pins[identity]:
                    results[identity] = True
    return results


def review_bytes(workflow: str, lock: str, parity: str) -> dict:
    pins = extract_pins(workflow, lock)
    checks = scan_version_checks(parity, pins)
    not_seen = sorted(name for name, seen in checks.items() if not seen)
    return {
        'schema': 'astra-h1-offline-frozen-runtime-source-review-v1',
        'frozenPins': pins,
        'literalVersionComparisonsSeen': checks,
        'missingExplicitVersionComparisons': not_seen,
        'observedSourceRisk': 'PROBE_HAS_NO_EXPLICIT_FROZEN_RUNTIME_COMPARISONS' if not_seen else 'LITERAL_COMPARISONS_PRESENT_NOT_RUNTIME_PROOF',
        'runtimeEnforcementProven': False,
        'fullModelParityExecuted': False,
        'safeToClaimFrozenParityPass': False,
        'launchPermission': False,
        'paritySourceGitBlob': hashlib.sha1(b'blob ' + str(len(parity.encode())).encode() + b'\0' + parity.encode()).hexdigest(),
    }


def review_checkout(root: Path) -> dict:
    return review_bytes(read_text(root, WORKFLOW), read_text(root, LOCK), read_text(root, PARITY))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='Already available complete repository checkout; never auto-downloads')
    args = parser.parse_args()
    print(json.dumps(review_checkout(args.root), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
