#!/usr/bin/env python3
"""Assemble the immutable V154 private scorer payload from frozen parts.

This is reference-only preparation. It does not read the generated candidate and
it does not call any scoring function.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "research" / "v154-professional-references" / "scorer-ready"
RHYTHM = REF / "rhythm-scorer-ready.json"
LEAD = REF / "lead-scorer-ready.json"
BASS = REF / "bass-scorer-ready.json"
SCORER = ROOT / "validation" / "v154_cpu_multitrack" / "score_frontend_reference.py"
OUT = REF / "frontend-reference-payload.json"
RECEIPT = REF / "frontend-reference-payload-receipt.json"

EXPECTED_SHA256 = {
    RHYTHM: "d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555",
    LEAD: "8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be",
    BASS: "39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1",
}
EXPECTED_SCORER_GIT_BLOB = "9644e65719fbd361a9b39778ae9950c5e983e855"
EXPECTED_COUNTS = {"rhythm": 946, "lead": 447, "combinedGuitar": 1393, "bass": 547}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def load_pinned(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    actual = sha256(data)
    if actual != EXPECTED_SHA256[path]:
        raise RuntimeError(f"frozen reference identity drift {path}: {actual}")
    obj = json.loads(data)
    if not isinstance(obj, dict):
        raise TypeError(path)
    return obj


def row_key(row: dict[str, Any]) -> tuple[int, float, int]:
    measure = int(row["measure"])
    step = float(row["step"])
    midi = int(row["midi"])
    if measure < 1 or not (0.0 <= step < 16.0) or not (0 <= midi <= 127):
        raise ValueError(f"invalid scorer row {row}")
    return measure, step, midi


def main() -> int:
    if OUT.exists() or RECEIPT.exists():
        raise RuntimeError("frontend reference payload already exists; write-once")

    rhythm = load_pinned(RHYTHM)
    lead = load_pinned(LEAD)
    bass = load_pinned(BASS)

    scorer_bytes = SCORER.read_bytes()
    scorer_blob = git_blob_sha(scorer_bytes)
    if scorer_blob != EXPECTED_SCORER_GIT_BLOB:
        raise RuntimeError(f"scorer identity drift: {scorer_blob}")

    parts = {}
    counters = {}
    duplicate_extras = {}
    for name, payload, expected in (
        ("rhythm", rhythm, EXPECTED_COUNTS["rhythm"]),
        ("lead", lead, EXPECTED_COUNTS["lead"]),
        ("bass", bass, EXPECTED_COUNTS["bass"]),
    ):
        rows = payload.get("notes")
        if not isinstance(rows, list) or len(rows) != expected:
            raise ValueError(f"{name} row count mismatch")
        normalized = [{"measure": int(r["measure"]), "step": r["step"], "midi": int(r["midi"])} for r in rows]
        keys = [row_key(r) for r in normalized]
        c = Counter(keys)
        parts[name] = normalized
        counters[name] = c
        duplicate_extras[name] = sum(v - 1 for v in c.values() if v > 1)

    combined_count = len(parts["rhythm"]) + len(parts["lead"])
    if combined_count != EXPECTED_COUNTS["combinedGuitar"]:
        raise ValueError("combined Guitar count drift")
    rhythm_lead_overlap = sum((counters["rhythm"] & counters["lead"]).values())
    combined_counter = counters["rhythm"] + counters["lead"]

    payload = {
        "schema": "dadrock.tabs.v154.cpu-front-end-reference.v1",
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
        "referenceAuthorization": {
            "userProvidedOrAuthorized": True,
            "privateScoringOnly": True,
            "candidateGenerationMayReadReference": False,
            "mainOrProductionUseAuthorized": False,
        },
        "parts": parts,
        "counts": EXPECTED_COUNTS,
        "frozenInputs": {
            "rhythmSha256": EXPECTED_SHA256[RHYTHM],
            "leadSha256": EXPECTED_SHA256[LEAD],
            "bassSha256": EXPECTED_SHA256[BASS],
            "scorerGitBlobSha": EXPECTED_SCORER_GIT_BLOB,
        },
        "policy": {
            "combinedGuitarIsRhythmPlusLeadConcatenation": True,
            "crossPartMultiplicityPreserved": True,
            "crossPartUnisonRowsAreNotDeduplicated": True,
            "generatedCandidateRead": False,
            "generatedCandidateModified": False,
            "referenceFacingScoreCalls": 0,
            "scoringPerformed": False,
        },
    }

    # Interface-only compatibility audit. Loading/normalizing the reference is
    # permitted; no matching or score_stream function is called here.
    spec = importlib.util.spec_from_file_location("v154_frozen_scorer", SCORER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen scorer")
    scorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scorer)
    combined, scorer_bass, scorer_counts = scorer.load_reference(payload)
    if len(combined) != EXPECTED_COUNTS["combinedGuitar"] or len(scorer_bass) != EXPECTED_COUNTS["bass"]:
        raise ValueError("frozen scorer interface normalized unexpected row count")
    if scorer_counts != {
        "rhythmIncluded": 946,
        "leadIncluded": 447,
        "bassIncluded": 547,
        "rhythmExcluded": 0,
        "leadExcluded": 0,
        "bassExcluded": 0,
    }:
        raise ValueError(f"unexpected scorer part counts: {scorer_counts}")

    out_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    out_sha = sha256(out_bytes)
    receipt = {
        "schema": "dadrock.tabs.v154.cpu-front-end-reference-receipt.v1",
        "validation": "PASS",
        "outputPath": str(OUT.relative_to(ROOT)),
        "outputSha256": out_sha,
        "frozenInputs": payload["frozenInputs"],
        "counts": EXPECTED_COUNTS,
        "audit": {
            "scorerInterfaceLoadReferenceOnly": True,
            "scorerFunctionsCalled": ["load_reference"],
            "scoreStreamCalled": False,
            "rhythmLeadExactRowMultisetOverlap": rhythm_lead_overlap,
            "combinedGuitarUniqueRows": len(combined_counter),
            "duplicateExtrasWithinParts": duplicate_extras,
            "combinedGuitarRows": len(combined),
            "bassRows": len(scorer_bass),
            "referenceCounts": scorer_counts,
        },
        "policy": {
            "generatedCandidateRead": False,
            "generatedCandidateModified": False,
            "humanCandidateCorrection": False,
            "thresholdSweep": False,
            "referenceFacingScoreCalls": 0,
            "scoringPerformed": False,
            "modalL4CudaGpuUsed": False,
            "mainOrProductionModified": False,
        },
    }
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    OUT.write_bytes(out_bytes)
    RECEIPT.write_bytes(receipt_bytes)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
