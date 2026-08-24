from __future__ import annotations

import subprocess

from v143_repair_index_alignment_shadow import summarize_repair_index_alignment


EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"


def main() -> int:
    period = 0.5
    repaired = [0.5 + index * period for index in range(40)]
    raw = list(repaired)
    raw.append(repaired[8] + 0.25)
    raw.sort()

    summary = summarize_repair_index_alignment(raw, repaired, period)
    assert summary["matchedBeatCount"] == len(repaired), summary
    assert summary["multipleModuloOffsetsObserved"] is True, summary
    assert summary["offsetChangePointCount"] >= 1, summary
    runs = summary["offsetRuns"]
    assert runs[0]["rawMinusRepairedIndexMod4"] == 0, summary
    assert runs[-1]["rawMinusRepairedIndexMod4"] == 1, summary
    assert runs[0]["endRepairedIndexExclusive"] == 9, summary
    assert runs[-1]["startRepairedIndex"] == 9, summary
    assert summary["referenceFree"] is True
    assert summary["professionalReferenceUsed"] is False
    assert summary["runtimeLabelsRequired"] is False
    assert summary["runtimePhaseChanged"] is False
    assert summary["productionModified"] is False

    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        text=True,
    ).strip()
    assert protected == EXPECTED_PROTECTED_BLOB, protected
    print("V143 repair index alignment checker: PASS")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
