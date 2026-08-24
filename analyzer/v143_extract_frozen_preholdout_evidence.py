from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
RETIRED_EVENT_SHA256 = "a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb"
EXPECTED_RUN_ID = "32702772593"
EXPECTED_ARTIFACT_ID = "9511117529"
EXPECTED_ARTIFACT_DIGEST = "fe16e937bae1c4af9f52b0d7863846c9a8da4da91be0af03256947bc2f5deaf4"
EXPECTED_CANDIDATE_COMMIT = "289a04e0fe30b5668ddaf39427404d8472ca1f51"
EXPECTED_CANDIDATE_BLOB = "20e7a583fcb96249636cc63b01cf9ae0044f2c62"
EXPECTED_RAW_PRODUCT_SHA256 = "c4d2af1bdadea04b326205388227645b432ea1a8f99123fab6dd4c565c21f371"
LEGATO_TYPES = {"hammer-on", "pull-off", "slide-up", "slide-down"}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main(root_value: str, output_value: str) -> None:
    root = Path(root_value)
    raw_path = root / ".preholdout" / "raw-product-output.json"
    freeze_path = root / ".preholdout" / "rhythm-freeze-input.json"
    summary_path = root / "debug" / "v143-contextual-prune" / "rhythm-professional-preholdout-real-audio.json"
    for path in (raw_path, freeze_path, summary_path):
        if not path.exists() or path.stat().st_size <= 0:
            raise RuntimeError(f"required historical evidence missing: {path}")

    raw_bytes = raw_path.read_bytes()
    if sha256_bytes(raw_bytes) != EXPECTED_RAW_PRODUCT_SHA256:
        raise RuntimeError("historical raw product bytes changed")
    raw = json.loads(raw_bytes)
    freeze = read_json(freeze_path)
    summary = read_json(summary_path)

    if str(summary.get("workflowRunId")) != EXPECTED_RUN_ID:
        raise RuntimeError("historical preholdout run identity changed")
    if str(summary.get("candidateResultCommit")) != EXPECTED_CANDIDATE_COMMIT:
        raise RuntimeError("historical candidate commit changed")
    if str(summary.get("candidateBlob")) != EXPECTED_CANDIDATE_BLOB:
        raise RuntimeError("historical candidate blob changed")
    if str(summary.get("sourceAudioSha256")) != APPROVED_AUDIO_SHA256:
        raise RuntimeError("historical approved-audio identity changed")
    if str(summary.get("frozenEventSha256")) != RETIRED_EVENT_SHA256:
        raise RuntimeError("historical retired render identity changed")
    if summary.get("referenceFree") is not True:
        raise RuntimeError("historical preholdout was not reference-free")
    if summary.get("professionalReferenceUsed") is not False:
        raise RuntimeError("historical preholdout used professional reference")
    if summary.get("referenceRuntimeInputUsed") is not False:
        raise RuntimeError("historical preholdout used reference runtime input")
    if summary.get("professionalHumanScoreRun") is not False:
        raise RuntimeError("historical artifact is not pre-scorer")

    candidate = raw.get("candidate") or {}
    if candidate.get("approvedFixture") is not True or candidate.get("sourceSha256") != APPROVED_AUDIO_SHA256:
        raise RuntimeError("raw product is not bound to approved audio")
    if candidate.get("professionalReferenceUsed") is not False or candidate.get("productionModified") is not False:
        raise RuntimeError("raw product safety invariant changed")

    events = list(raw.get("events") or [])
    render_events = list(freeze.get("renderEvents") or [])
    if len(events) != 985 or len(render_events) != 985:
        raise RuntimeError("historical event count changed")
    for index, (event, render_event) in enumerate(zip(events, render_events)):
        if int(event.get("eventIndex", -1)) != index or int(render_event.get("eventIndex", -1)) != index:
            raise RuntimeError("historical event indices are not aligned")
        for key in ("measure", "step", "midi", "stringIndex", "fret"):
            if int(event[key]) != int(render_event[key]):
                raise RuntimeError(f"raw/freeze event mismatch at {index}:{key}")

    groups: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        groups[(int(event["measure"]), int(event["step"]))].append(event)
    if len(groups) != 725:
        raise RuntimeError("historical attack count changed")

    attacks: list[Any] = []
    for key in sorted(groups):
        group = sorted(groups[key], key=lambda event: int(event["eventIndex"]))
        first = group[0]
        hypotheses = []
        for item in first.get("pitchHypotheses") or []:
            hypotheses.append([
                int(item["midi"]),
                float(item["physicalAttack"]),
                float(item["physicalBody"]),
                float(item["physicalContinuity"]),
                float(item["physicalScore"]),
            ])
        notes = [
            [
                int(event["eventIndex"]),
                int(event["midi"]),
                int(event["stringIndex"]),
                int(event["fret"]),
                isinstance(event.get("rhythmSustainShadow"), dict),
            ]
            for event in group
        ]
        attacks.append([
            int(key[0]), int(key[1]), float(first["timeSeconds"]),
            int(first["dominantMidi"]), hypotheses, notes,
        ])

    links: list[Any] = []
    for event in events:
        raw_target = event.get("legatoTargetEventIndex")
        if raw_target is None:
            continue
        types = [
            str(item.get("type"))
            for item in event.get("rhythmTechniques") or []
            if isinstance(item, dict) and str(item.get("type")) in LEGATO_TYPES
        ]
        if len(types) != 1:
            raise RuntimeError("historical legato source does not have one legato type")
        links.append([int(event["eventIndex"]), int(raw_target), types[0]])
    if len(links) != 28:
        raise RuntimeError("historical legato-link count changed")

    output = {
        "schemaVersion": 1,
        "mode": "v143-frozen-approved-audio-preholdout-evidence",
        "provenance": {
            "workflowRunId": EXPECTED_RUN_ID,
            "artifactId": EXPECTED_ARTIFACT_ID,
            "artifactDigest": EXPECTED_ARTIFACT_DIGEST,
            "candidateResultCommit": EXPECTED_CANDIDATE_COMMIT,
            "candidateBlob": EXPECTED_CANDIDATE_BLOB,
            "sourceAudioSha256": APPROVED_AUDIO_SHA256,
            "retiredFrozenEventSha256": RETIRED_EVENT_SHA256,
            "rawProductSha256": EXPECTED_RAW_PRODUCT_SHA256,
            "rawProductBytes": len(raw_bytes),
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "referenceRuntimeInputUsed": False,
            "preScorer": True,
        },
        "tempoBpm": float(freeze["tempoBpm"]),
        "attacks": attacks,
        "oldRenderEvents": render_events,
        "oldLegatoLinks": links,
    }
    destination = Path(output_value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    destination.write_bytes(encoded + b"\n")
    print(json.dumps({
        "passed": True,
        "attackCount": len(attacks),
        "renderEventCount": len(render_events),
        "legatoLinkCount": len(links),
        "evidenceSha256": sha256_bytes(encoded + b"\n"),
        "evidenceBytes": len(encoded) + 1,
        "referenceFree": True,
        "modalUsed": False,
        "productionModified": False,
    }, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: v143_extract_frozen_preholdout_evidence.py ARTIFACT_ROOT OUTPUT_JSON")
    main(sys.argv[1], sys.argv[2])
