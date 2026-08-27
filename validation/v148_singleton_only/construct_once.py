#!/usr/bin/env python3
"""Construct exactly one frozen V148 singleton-only candidate from preserved V147 evidence.

This is a reference-free projection only. It does not read audio, Gold/reference data,
the professional image, or any scorer. The only construction discriminator is the
accepted-baseline onset cardinality frozen in the V148 preregistration.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
if str(HOLDOUT_DIR) not in sys.path:
    sys.path.insert(0, str(HOLDOUT_DIR))

from canonical import canonical_events, sha256_json  # noqa: E402
from modal.v147_phase_c_artifact_support import (  # noqa: E402
    EXPECTED_ACCEPTED_EVENT_COUNT,
    EXPECTED_ACCEPTED_EVENT_SHA256,
    EXPECTED_MEASURE_COUNT,
    OPEN_MIDI_BY_STRING_INDEX,
    materialize_accepted_family,
    timing_and_metadata_violations,
)

V5_PATH = ROOT / "debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json"
V147_CANDIDATE_PATH = ROOT / "debug/v147-phase-c-real-audio/preserved-run-33038518285/candidate.json"
V147_DECISIONS_PATH = ROOT / "debug/v147-phase-c-real-audio/preserved-run-33038518285/decisions.json"
PREREG_PATH = ROOT / "debug/v148-singleton-only/phase-a-hypothesis-preregistration.json"
AUTH_PATH = ROOT / "debug/v148-singleton-only/construction-authorization.json"

EXPECTED_PREREG_BLOB = "fd3fb330d3aa80d1058656e3b2dd7eaa201f8e1c"
EXPECTED_AUTH_BLOB = "006f719c8c71570142cf6990c7542f3d8692d5e4"
EXPECTED_SUPPORT_BLOB = "f4278ffaacaca3f66baf7a3112e2af0f3bc387cf"
EXPECTED_CANONICAL_BLOB = "088d44827fb23e20d9aeeb4944a672989af5846c"
EXPECTED_RENDER_CONTRACT_BLOB = "ccbb93c48982798cc474309fd981f6ca02d5c8d4"
EXPECTED_V147_CANDIDATE_FILE_SHA256 = "c0215690d5bfd9d2d47b8784eee886e942fbd28c499f25c643635c45ff7a9636"
EXPECTED_V147_CANDIDATE_EVENT_SHA256 = "ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77"
EXPECTED_V147_DECISIONS_FILE_SHA256 = "3ec6c42730bf571c29258eca131c4e32da257c1ac6073e5319073818e8ac49b9"
EXPECTED_CHANGED_EVENTS = 106
EXPECTED_CHANGED_ONSETS = 106
EXPECTED_ONSET_COUNT = 844
MAX_FRET = 24


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(ROOT))], cwd=ROOT, text=True
    ).strip()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_frozen_code_and_authorization() -> dict[str, str]:
    identities = {
        "preregistration": git_blob(PREREG_PATH),
        "authorization": git_blob(AUTH_PATH),
        "phaseCArtifactSupport": git_blob(ROOT / "modal/v147_phase_c_artifact_support.py"),
        "canonicalAdapter": git_blob(ROOT / "validation/rhythm_holdout/canonical.py"),
        "renderContract": git_blob(ROOT / "lib/v143RenderContract.js"),
    }
    expected = {
        "preregistration": EXPECTED_PREREG_BLOB,
        "authorization": EXPECTED_AUTH_BLOB,
        "phaseCArtifactSupport": EXPECTED_SUPPORT_BLOB,
        "canonicalAdapter": EXPECTED_CANONICAL_BLOB,
        "renderContract": EXPECTED_RENDER_CONTRACT_BLOB,
    }
    if identities != expected:
        raise ValueError(f"frozen identity drift: actual={identities} expected={expected}")
    prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    auth = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    if prereg.get("singleFrozenConstructionPolicy", {}).get("name") != "accepted-onset-singleton-only-v147-projection":
        raise ValueError("unexpected V148 construction policy")
    if auth.get("constructionAuthorization") is not True:
        raise ValueError("V148 construction authorization is not true")
    if auth.get("referenceFacingScoringAuthorization") is not False:
        raise ValueError("reference-facing scoring must remain unauthorized")
    return identities


def load_accepted() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = json.loads(V5_PATH.read_text(encoding="utf-8"))
    accepted = canonical_events(materialize_accepted_family(payload))
    digest = sha256_json(accepted)
    measures = sorted({int(row["measure"]) for row in accepted})
    if len(accepted) != EXPECTED_ACCEPTED_EVENT_COUNT or digest != EXPECTED_ACCEPTED_EVENT_SHA256:
        raise ValueError("accepted family #10 identity mismatch")
    if measures != list(range(1, EXPECTED_MEASURE_COUNT + 1)):
        raise ValueError("accepted family #10 measure identity mismatch")
    return accepted, {
        "family": "singleton-onset-replace-be9e9aa7a734e3cd",
        "eventCount": len(accepted),
        "eventSha256": digest,
        "generatedMeasureCount": len(measures),
    }


def load_preserved_v147(accepted: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]], dict[str, Any]]:
    candidate_file_sha = file_sha256(V147_CANDIDATE_PATH)
    decisions_file_sha = file_sha256(V147_DECISIONS_PATH)
    if candidate_file_sha != EXPECTED_V147_CANDIDATE_FILE_SHA256:
        raise ValueError("preserved V147 candidate byte SHA mismatch")
    if decisions_file_sha != EXPECTED_V147_DECISIONS_FILE_SHA256:
        raise ValueError("preserved V147 decisions byte SHA mismatch")

    candidate_doc = json.loads(V147_CANDIDATE_PATH.read_text(encoding="utf-8"))
    candidate = canonical_events(candidate_doc.get("renderEvents", []))
    candidate_event_sha = sha256_json(candidate)
    if len(candidate) != EXPECTED_ACCEPTED_EVENT_COUNT or candidate_event_sha != EXPECTED_V147_CANDIDATE_EVENT_SHA256:
        raise ValueError("preserved V147 canonical candidate identity mismatch")

    raw_decisions = json.loads(V147_DECISIONS_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw_decisions, list) or len(raw_decisions) != EXPECTED_ACCEPTED_EVENT_COUNT:
        raise ValueError("preserved V147 decision count mismatch")
    decisions: dict[int, dict[str, Any]] = {}
    for item in raw_decisions:
        if not isinstance(item, Mapping):
            raise ValueError("malformed preserved V147 decision")
        event_index = int(item["eventIndex"])
        if event_index in decisions:
            raise ValueError(f"duplicate V147 decision eventIndex={event_index}")
        decisions[event_index] = dict(item)
    if len(decisions) != len(accepted):
        raise ValueError("V147 decision index cardinality mismatch")

    return candidate, decisions, {
        "candidateFileSha256": candidate_file_sha,
        "candidateEventSha256": candidate_event_sha,
        "decisionsFileSha256": decisions_file_sha,
        "decisionCount": len(decisions),
    }


def group_cardinality(events: Sequence[Mapping[str, Any]]) -> dict[tuple[int, int], int]:
    counts: dict[tuple[int, int], int] = {}
    for row in events:
        key = (int(row["measure"]), int(row["step"]))
        counts[key] = counts.get(key, 0) + 1
    if len(counts) != EXPECTED_ONSET_COUNT:
        raise ValueError(f"accepted onset count drift: {len(counts)} != {EXPECTED_ONSET_COUNT}")
    return counts


def build_projection(
    accepted: Sequence[Mapping[str, Any]],
    v147_candidate: Sequence[Mapping[str, Any]],
    decisions: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any]:
    if len(accepted) != len(v147_candidate):
        raise ValueError("accepted/V147 event cardinality mismatch")
    cardinality = group_cardinality(accepted)
    accepted_by_event = {int(row["eventIndex"]): dict(row) for row in accepted}
    v147_by_event = {int(row["eventIndex"]): dict(row) for row in v147_candidate}
    if len(accepted_by_event) != len(accepted) or len(v147_by_event) != len(v147_candidate):
        raise ValueError("duplicate eventIndex in accepted or V147 stream")

    output: list[dict[str, Any]] = []
    copied_singleton_indices: list[int] = []

    for accepted_row in accepted:
        event_index = int(accepted_row["eventIndex"])
        decision = decisions.get(event_index)
        v147_row = v147_by_event.get(event_index)
        if decision is None or v147_row is None:
            raise ValueError(f"missing preserved V147 row for eventIndex={event_index}")
        onset = (int(accepted_row["measure"]), int(accepted_row["step"]))
        if int(decision.get("measure")) != onset[0] or int(decision.get("step")) != onset[1]:
            raise ValueError(f"decision onset mismatch eventIndex={event_index}")
        if int(decision.get("originalMidi")) != int(accepted_row["midi"]):
            raise ValueError(f"decision original MIDI mismatch eventIndex={event_index}")
        if int(v147_row["measure"]) != onset[0] or int(v147_row["step"]) != onset[1]:
            raise ValueError(f"V147 row onset mismatch eventIndex={event_index}")

        changed = decision.get("changed") is True
        if cardinality[onset] == 1 and changed:
            selected_midi = int(decision.get("selectedMidi"))
            if int(v147_row["midi"]) != selected_midi:
                raise ValueError(f"V147 selected MIDI mismatch eventIndex={event_index}")
            if abs(selected_midi - int(accepted_row["midi"])) != 1:
                raise ValueError(f"singleton preserved delta is not +/-1 eventIndex={event_index}")
            if timing_and_metadata_violations([accepted_row], [v147_row]):
                raise ValueError(f"V147 singleton row changes protected metadata eventIndex={event_index}")
            output.append(copy.deepcopy(v147_row))
            copied_singleton_indices.append(event_index)
        else:
            output.append(copy.deepcopy(dict(accepted_row)))

    canonical = canonical_events(output)
    return {
        "events": canonical,
        "eventSha256": sha256_json(canonical),
        "copiedSingletonEventIndices": copied_singleton_indices,
        "cardinality": cardinality,
        "acceptedByEvent": accepted_by_event,
        "v147ByEvent": v147_by_event,
    }


def validate_projection(
    accepted: Sequence[Mapping[str, Any]],
    projection: Mapping[str, Any],
) -> dict[str, Any]:
    candidate = projection["events"]
    cardinality = projection["cardinality"]
    v147_by_event = projection["v147ByEvent"]

    if len(candidate) != EXPECTED_ACCEPTED_EVENT_COUNT:
        raise ValueError("V148 candidate event count changed")
    measures = sorted({int(row["measure"]) for row in candidate})
    if measures != list(range(1, EXPECTED_MEASURE_COUNT + 1)):
        raise ValueError("V148 candidate measure set changed")

    timing_violations = timing_and_metadata_violations(accepted, candidate)
    if timing_violations:
        raise ValueError(f"protected timing/metadata changed: {timing_violations[:3]}")

    changed_indices: list[int] = []
    changed_onsets: set[tuple[int, int]] = set()
    polyphonic_changed: list[int] = []
    copied_row_mismatches: list[int] = []
    position_violations: list[int] = []

    for before, after in zip(accepted, candidate):
        event_index = int(before["eventIndex"])
        if int(after["eventIndex"]) != event_index:
            raise ValueError("event order/index changed")
        onset = (int(before["measure"]), int(before["step"]))
        if dict(before) != dict(after):
            changed_indices.append(event_index)
            changed_onsets.add(onset)
            if cardinality[onset] != 1:
                polyphonic_changed.append(event_index)
            if dict(after) != dict(v147_by_event[event_index]):
                copied_row_mismatches.append(event_index)
        string_index = int(after["stringIndex"])
        fret = int(after["fret"])
        midi = int(after["midi"])
        if (
            string_index not in OPEN_MIDI_BY_STRING_INDEX
            or not (0 <= fret <= MAX_FRET)
            or OPEN_MIDI_BY_STRING_INDEX[string_index] + fret != midi
        ):
            position_violations.append(event_index)

    copied = list(projection["copiedSingletonEventIndices"])
    if len(changed_indices) != EXPECTED_CHANGED_EVENTS or len(copied) != EXPECTED_CHANGED_EVENTS:
        raise ValueError(
            f"expected exactly {EXPECTED_CHANGED_EVENTS} changed/copied singleton events, got "
            f"changed={len(changed_indices)} copied={len(copied)}"
        )
    if len(changed_onsets) != EXPECTED_CHANGED_ONSETS:
        raise ValueError(f"expected exactly {EXPECTED_CHANGED_ONSETS} changed onsets")
    if changed_indices != copied:
        raise ValueError("changed event indices differ from frozen copied singleton indices")
    if polyphonic_changed:
        raise ValueError(f"polyphonic events changed: {polyphonic_changed[:10]}")
    if copied_row_mismatches:
        raise ValueError(f"changed singleton rows differ from preserved V147 rows: {copied_row_mismatches[:10]}")
    if position_violations:
        raise ValueError(f"render-position violations: {position_violations[:10]}")

    return {
        "eventCount": len(candidate),
        "generatedMeasureCount": len(measures),
        "acceptedOnsetCount": len(cardinality),
        "changedEventCountVersusAccepted": len(changed_indices),
        "changedOnsetCountVersusAccepted": len(changed_onsets),
        "polyphonicChangedEventsVersusAccepted": len(polyphonic_changed),
        "allChangedOnsetsAcceptedCardinalityOne": all(cardinality[key] == 1 for key in changed_onsets),
        "changedSingletonRowsExactlyV147": len(copied_row_mismatches) == 0,
        "timingMetadataInvariantViolations": len(timing_violations),
        "positionIdentityViolations": len(position_violations),
        "changedEventIndices": changed_indices,
    }


def verify_pdf_projection(candidate: Sequence[Mapping[str, Any]], candidate_sha: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="v148-pdf-fidelity-") as temp:
        temp_dir = Path(temp)
        source = temp_dir / "candidate.json"
        projected = temp_dir / "projected.json"
        write_json(source, {"renderEvents": list(candidate)})
        js = """
import fs from 'node:fs';
import { projectV143RenderEvents } from './lib/v143RenderContract.js';
const input = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
const renderEvents = projectV143RenderEvents(input.renderEvents || []);
fs.writeFileSync(process.argv[2], JSON.stringify({renderEvents}));
"""
        subprocess.check_call(
            [
                "node",
                "--experimental-default-type=module",
                "--input-type=module",
                "-e",
                js,
                str(source),
                str(projected),
            ],
            cwd=ROOT,
        )
        projected_doc = json.loads(projected.read_text(encoding="utf-8"))
        projected_events = canonical_events(projected_doc.get("renderEvents", []))
        projected_sha = sha256_json(projected_events)
        exact = projected_events == list(candidate) and projected_sha == candidate_sha
        report = {
            "schema": "dadrock.tabs.v148.pdf-event-fidelity.v1",
            "instrument": "rhythm",
            "rendererProjection": "lib/v143RenderContract.js::projectV143RenderEvents",
            "referenceOpened": False,
            "runtimeLabelsRequired": False,
            "candidateEventCount": len(candidate),
            "pdfEventCount": len(projected_events),
            "candidateEventSha256": candidate_sha,
            "pdfEventSha256": projected_sha,
            "pdfEventFidelity": 1.0 if exact else 0.0,
            "passed": exact,
        }
        if not exact:
            raise ValueError("V143 render projection differs from V148 candidate")
        return report


def construct(output_dir: Path) -> dict[str, Any]:
    if output_dir.exists():
        raise ValueError(f"output directory already exists: {output_dir}")
    frozen = verify_frozen_code_and_authorization()
    accepted, accepted_meta = load_accepted()
    v147_candidate, decisions, v147_meta = load_preserved_v147(accepted)

    first = build_projection(accepted, v147_candidate, decisions)
    first_metrics = validate_projection(accepted, first)
    second = build_projection(accepted, v147_candidate, decisions)
    second_metrics = validate_projection(accepted, second)
    deterministic = (
        first["eventSha256"] == second["eventSha256"]
        and first["events"] == second["events"]
        and first_metrics == second_metrics
    )
    if not deterministic:
        raise ValueError("V148 deterministic replay mismatch")

    output_dir.mkdir(parents=True, exist_ok=False)
    candidate_doc = {
        "schema": "dadrock.tabs.v148.singleton-only-candidate.v1",
        "instrument": "rhythm",
        "renderEvents": first["events"],
    }
    write_json(output_dir / "candidate.json", candidate_doc)

    pdf_report = verify_pdf_projection(first["events"], first["eventSha256"])
    write_json(output_dir / "pdf-event-fidelity.json", pdf_report)

    proof = {
        "schema": "dadrock.tabs.v148.singleton-only-construction-proof.v1",
        "classification": "reference-free-preserved-artifact-single-candidate-construction",
        "policy": "accepted-onset-singleton-only-v147-projection",
        "acceptedBaseline": accepted_meta,
        "preservedV147": v147_meta,
        "frozenSourceBlobs": frozen,
        "candidate": {
            "eventCount": len(first["events"]),
            "eventSha256": first["eventSha256"],
            "generatedMeasureCount": first_metrics["generatedMeasureCount"],
        },
        "metrics": first_metrics,
        "deterministicReplayEventSha256": second["eventSha256"],
        "deterministic": deterministic,
        "pdfEventFidelity": pdf_report["pdfEventFidelity"],
        "pdfEventSha256": pdf_report["pdfEventSha256"],
        "candidateVariantsConstructed": 1,
        "referenceRead": False,
        "goldRead": False,
        "professionalImageRead": False,
        "calibrationScoreRun": False,
        "audioRead": False,
        "hpssOrCqtRecomputed": False,
        "candidateSearchRun": False,
        "thresholdRetuningRun": False,
        "modalGpuUsed": False,
        "productionIntegrated": False,
        "automaticPromotion": False,
        "gate": "GO",
    }
    write_json(output_dir / "construction-proof.json", proof)

    files = {}
    for name in ("candidate.json", "construction-proof.json", "pdf-event-fidelity.json"):
        path = output_dir / name
        files[name] = {"bytes": path.stat().st_size, "sha256": file_sha256(path)}
    manifest = {
        "schema": "dadrock.tabs.v148.singleton-only-preservation-manifest.v1",
        "classification": "durable-reference-free-single-candidate-preservation",
        "policy": "accepted-onset-singleton-only-v147-projection",
        "candidateEventSha256": first["eventSha256"],
        "eventCount": len(first["events"]),
        "generatedMeasureCount": first_metrics["generatedMeasureCount"],
        "changedEventCountVersusAccepted": first_metrics["changedEventCountVersusAccepted"],
        "changedOnsetCountVersusAccepted": first_metrics["changedOnsetCountVersusAccepted"],
        "files": files,
        "rawAudioPreserved": False,
        "normalizedPcmPreserved": False,
        "cqtPreserved": False,
        "referenceMaterialPreserved": False,
        "referenceFacingScoringAuthorized": False,
    }
    write_json(output_dir / "preservation-manifest.json", manifest)

    result = {
        "gate": "GO",
        "candidateEventSha256": first["eventSha256"],
        "eventCount": len(first["events"]),
        "generatedMeasureCount": first_metrics["generatedMeasureCount"],
        "changedEvents": first_metrics["changedEventCountVersusAccepted"],
        "changedOnsets": first_metrics["changedOnsetCountVersusAccepted"],
        "polyphonicChangedEvents": first_metrics["polyphonicChangedEventsVersusAccepted"],
        "pdfEventFidelity": pdf_report["pdfEventFidelity"],
        "deterministic": deterministic,
        "candidateFileSha256": file_sha256(output_dir / "candidate.json"),
        "constructionProofSha256": file_sha256(output_dir / "construction-proof.json"),
        "pdfFidelitySha256": file_sha256(output_dir / "pdf-event-fidelity.json"),
        "manifestSha256": file_sha256(output_dir / "preservation-manifest.json"),
    }
    print("V148_SINGLETON_CONSTRUCTION=" + json.dumps(result, sort_keys=True, separators=(",", ":")))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "debug/v148-singleton-only/candidate",
    )
    args = parser.parse_args()
    construct(args.output_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
