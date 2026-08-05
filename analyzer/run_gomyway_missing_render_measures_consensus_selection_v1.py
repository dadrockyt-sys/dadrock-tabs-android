from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
AUDIT_PATH = PUBLIC_DIR / "gomyway-missing-render-measures-cross-artifact-audit-v1.json"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-missing-render-measures-consensus-selection-v1.json"
TARGETS = (106, 113)


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def normalize_notes(value: Any) -> tuple[tuple[int, int], ...]:
    notes: list[tuple[int, int]] = []
    if isinstance(value, list):
        for note in value:
            if not isinstance(note, dict):
                continue
            string = note.get("string", note.get("stringIndex"))
            fret = note.get("fret")
            if isinstance(string, (int, float)) and isinstance(fret, (int, float)):
                notes.append((int(string), int(fret)))
    return tuple(sorted(notes))


def signature(item: dict[str, Any]) -> tuple[Any, ...] | None:
    payload = item.get("payload") if isinstance(item.get("payload"), dict) else item
    notes = normalize_notes(payload.get("notes"))
    if not notes:
        string = payload.get("string", payload.get("stringIndex"))
        fret = payload.get("fret")
        if isinstance(string, (int, float)) and isinstance(fret, (int, float)):
            notes = ((int(string), int(fret)),)
    if not notes:
        return None
    step = payload.get("quantizedStep", payload.get("step"))
    duration = payload.get("durationSteps", payload.get("duration"))
    techniques = payload.get("techniques")
    if not isinstance(techniques, list):
        techniques = []
    return (
        int(step) if isinstance(step, (int, float)) else None,
        int(duration) if isinstance(duration, (int, float)) else None,
        notes,
        tuple(sorted(str(value) for value in techniques)),
    )


def main() -> None:
    audit = load_json(AUDIT_PATH)
    findings = audit.get("findings")
    if not isinstance(findings, dict):
        findings = {}

    report_measures: dict[str, Any] = {}
    all_ready = True

    for measure in TARGETS:
        rows = findings.get(str(measure), findings.get(measure, []))
        if not isinstance(rows, list):
            rows = []

        signatures: Counter[tuple[Any, ...]] = Counter()
        sources: defaultdict[tuple[Any, ...], list[str]] = defaultdict(list)
        examples: dict[tuple[Any, ...], dict[str, Any]] = {}

        for row in rows:
            if not isinstance(row, dict) or row.get("renderable") is not True:
                continue
            sig = signature(row)
            if sig is None:
                continue
            source = str(row.get("file") or row.get("source") or "unknown")
            signatures[sig] += 1
            sources[sig].append(source)
            examples.setdefault(sig, row)

        ranked = sorted(signatures, key=lambda sig: (signatures[sig], len(set(sources[sig]))), reverse=True)
        selected = ranked[0] if ranked else None
        support = signatures[selected] if selected else 0
        distinct_sources = len(set(sources[selected])) if selected else 0
        ready = bool(selected and support >= 2 and distinct_sources >= 2)
        all_ready = all_ready and ready

        report_measures[str(measure)] = {
            "renderableFindings": sum(signatures.values()),
            "uniqueSignatures": len(signatures),
            "selectedSignature": {
                "quantizedStep": selected[0],
                "durationSteps": selected[1],
                "notes": [
                    {"string": string, "fret": fret}
                    for string, fret in selected[2]
                ],
                "techniques": list(selected[3]),
            } if selected else None,
            "supportCount": support,
            "distinctSourceCount": distinct_sources,
            "sources": sorted(set(sources[selected])) if selected else [],
            "readyForReadOnlyOverlay": ready,
            "topCandidates": [
                {
                    "quantizedStep": sig[0],
                    "durationSteps": sig[1],
                    "notes": [{"string": s, "fret": f} for s, f in sig[2]],
                    "techniques": list(sig[3]),
                    "supportCount": signatures[sig],
                    "distinctSourceCount": len(set(sources[sig])),
                }
                for sig in ranked[:10]
            ],
        }

    report = {
        "schemaVersion": 1,
        "auditType": "missing-render-measure-consensus-selection",
        "targets": list(TARGETS),
        "measures": report_measures,
        "readyForReadOnlyOverlayProjection": all_ready,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Missing render measures consensus selection V1 complete")
    for measure in TARGETS:
        item = report_measures[str(measure)]
        print()
        print("MEASURE", measure)
        print("Renderable findings:", item["renderableFindings"])
        print("Unique signatures:", item["uniqueSignatures"])
        print("Selected signature:", item["selectedSignature"])
        print("Support count:", item["supportCount"])
        print("Distinct source count:", item["distinctSourceCount"])
        print("Ready for read-only overlay:", item["readyForReadOnlyOverlay"])
    print()
    print("Ready for read-only overlay projection:", report["readyForReadOnlyOverlayProjection"])
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
