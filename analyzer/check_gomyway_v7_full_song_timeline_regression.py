#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_REPORT = Path("/tmp/gomyway-full-song-v7-timeline-report.json")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Timeline report not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    args = parser.parse_args()

    report = load_json(Path(args.report))
    checks = report.get("checks") or {}
    harmony = report.get("harmonyRanges") or []
    releases = report.get("leadReleaseRanges") or []
    palm_clusters = report.get("leadPalmMuteClusters") or []
    bass_points = report.get("bassPoints") or {}
    vocabulary = set(report.get("rhythmVocabulary") or [])
    promotions = report.get("rhythmPromotions") or {}
    duration = float(report.get("songDuration") or 0.0)

    required_vocabulary = {"A(tp2)", "D", "E", "G", "G6"}
    guard_checks = {
        "timelineBenchmarkPassed": report.get("passed") is True,
        "protectedBaselinesUnchanged": report.get("protectedBaselinesChanged") is False,
        "allTimelineChecksGreen": bool(checks) and all(checks.values()),
        "fullSongDurationPresent": duration > 60.0,
        "rhythmVocabularyPreserved": required_vocabulary.issubset(vocabulary),
        "rhythmPromotionsPreserved": promotions.get("E") is True and promotions.get("G") is True,
        "harmonyRangesPresent": len(harmony) >= 1,
        "leadReleaseRangesPresent": len(releases) >= 1,
        "leadPalmMuteClustersPresent": len(palm_clusters) >= 1,
        "leadPalmMuteCountExpanded": int(report.get("leadPalmMutedEventCount") or 0) >= 43,
        "bassSlideTimestamped": isinstance(bass_points.get("slide"), dict),
        "bassMuteTimestamped": isinstance(bass_points.get("mute"), dict),
        "bassRestTimestamped": isinstance(bass_points.get("rest"), dict),
        "bassSlideTargetLocked": (bass_points.get("slide") or {}).get("targetFret") == 14,
    }

    failed = False
    print("JIMMY PAIGE V7 FULL-SONG TIMELINE GUARD")
    print("=" * 72)
    for name, passed in guard_checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    print("Song duration:", duration)
    print("Harmony ranges:", len(harmony))
    print("Lead release ranges:", len(releases))
    print("Lead palm-mute clusters:", len(palm_clusters))
    print("Lead palm-muted events:", report.get("leadPalmMutedEventCount"))
    print("Bass points:", bass_points)

    if failed:
        raise SystemExit("\nV7 full-song diagnostic timeline regression detected. Do not advance.")

    print("\nV7 FULL-SONG DIAGNOSTIC TIMELINE PRESERVED 💚")
    print("Harmony, lead, and bass evidence is timestamped from existing events only.")
    print("Tab, events, pitches, frets, note count, and timing remain untouched.")


if __name__ == "__main__":
    main()
