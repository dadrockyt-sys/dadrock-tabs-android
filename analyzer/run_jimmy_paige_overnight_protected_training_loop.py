from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
ARCHIVE_ROOT = PUBLIC_DIR / "jimmy-paige-protected-history"
STATE_PATH = PUBLIC_DIR / "gomyway-jimmy-paige-overnight-training-state.json"
SUMMARY_PATH = PUBLIC_DIR / "gomyway-jimmy-paige-overnight-training-summary.json"
LOG_PATH = REPO_ROOT / "jimmy-paige-overnight-protected-training.log"

PROTECTED_FILES = [
    "gomyway-professional-rhythm-reference-v2.json",
    "gomyway-professional-timing-map-v2.json",
    "gomyway-jimmy-paige-93-06-regression-validation.json",
    "gomyway-jimmy-paige-93-06-protected-checkpoint.json",
    "gomyway-jimmy-paige-93-06-events.json",
    "gomyway-jimmy-paige-midi62-neighbor-recovery-sweep.json",
    "gomyway-jimmy-paige-full-song-8-of-9-checkpoint.json",
]

# Existing tests are deliberately reused. Nothing in this loop changes the
# professional reference, protected checkpoints, renderer, or production code.
STAGES = [
    {
        "name": "protected-93-06-regression",
        "command": [sys.executable, "analyzer/validate_jimmy_paige_93_06_regressions.py"],
        "timeoutSeconds": 1800,
        "required": True,
    },
    {
        "name": "professional-chord-recovery-sweep",
        "command": [sys.executable, "analyzer/run_jimmy_paige_chord_recovery_extraction_sweep.py"],
        "timeoutSeconds": 2400,
        "required": False,
    },
    {
        "name": "raw-chord-rule-score",
        "command": [sys.executable, "analyzer/score_jimmy_paige_raw_chord_evidence_rules.py"],
        "timeoutSeconds": 300,
        "required": False,
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str) -> None:
    line = f"{utc_now()} | {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_protected_files(label: str) -> dict[str, Any]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = ARCHIVE_ROOT / f"{stamp}-{label}"
    destination.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, Any]] = []

    for filename in PROTECTED_FILES:
        source = PUBLIC_DIR / filename
        row: dict[str, Any] = {"filename": filename, "exists": source.is_file()}
        if source.is_file():
            copied = destination / filename
            shutil.copy2(source, copied)
            row.update(
                {
                    "sha256": sha256(source),
                    "bytes": source.stat().st_size,
                    "archivePath": str(copied.relative_to(REPO_ROOT)),
                }
            )
        files.append(row)

    manifest = {
        "createdAt": utc_now(),
        "label": label,
        "professionalPdfRemainsMeasurementAuthority": True,
        "protectedCheckpointsAreReadOnly": True,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "files": files,
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    log(f"Protected snapshot created | {destination.relative_to(REPO_ROOT)}")
    return manifest


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def protected_regression_passed() -> bool:
    report = load_json(PUBLIC_DIR / "gomyway-jimmy-paige-93-06-regression-validation.json")
    return bool(report.get("combinedRegressionPassed"))


def run_stage(stage: dict[str, Any], cycle: int) -> dict[str, Any]:
    started = time.time()
    log(f"Cycle {cycle} stage started | {stage['name']}")
    env = os.environ.copy()
    env.setdefault("JIMMY_HEARTBEAT_SECONDS", "15")
    env.setdefault("JIMMY_MAX_ATTEMPTS", "5")
    env.setdefault("JIMMY_MAX_RETRIES", "3")
    env.setdefault("JIMMY_WORKER_START_TIMEOUT_SECONDS", "180")
    env.setdefault("JIMMY_TOTAL_TIMEOUT_SECONDS", "1800")

    try:
        completed = subprocess.run(
            stage["command"],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=int(stage["timeoutSeconds"]),
            check=False,
        )
        output = completed.stdout or ""
        for line in output.splitlines():
            log(f"[{stage['name']}] {line}")
        row = {
            "name": stage["name"],
            "required": stage["required"],
            "returnCode": completed.returncode,
            "passed": completed.returncode == 0,
            "elapsedSeconds": round(time.time() - started, 3),
        }
    except subprocess.TimeoutExpired as error:
        output = (error.stdout or "") if isinstance(error.stdout, str) else ""
        for line in output.splitlines():
            log(f"[{stage['name']}] {line}")
        row = {
            "name": stage["name"],
            "required": stage["required"],
            "returnCode": None,
            "passed": False,
            "timedOut": True,
            "elapsedSeconds": round(time.time() - started, 3),
        }

    log(
        f"Cycle {cycle} stage complete | {stage['name']} | "
        f"passed={row['passed']} | elapsed={row['elapsedSeconds']}s"
    )
    return row


def write_state(payload: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    hours = max(1.0, float(os.getenv("JIMMY_OVERNIGHT_HOURS", "6")))
    pause_seconds = max(60, int(os.getenv("JIMMY_OVERNIGHT_PAUSE_SECONDS", "900")))
    max_cycles = max(1, int(os.getenv("JIMMY_OVERNIGHT_MAX_CYCLES", "8")))
    deadline = time.time() + hours * 3600.0

    LOG_PATH.write_text("", encoding="utf-8")
    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    starting_manifest = snapshot_protected_files("before-overnight-loop")

    state: dict[str, Any] = {
        "benchmarkVersion": 1,
        "benchmarkType": "jimmy-paige-overnight-protected-training-loop",
        "startedAt": utc_now(),
        "requestedHours": hours,
        "maximumCycles": max_cycles,
        "professionalPdfRemainsMeasurementAuthority": True,
        "protected93_06CheckpointRequired": True,
        "successfulTestsPreserved": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "startingManifest": starting_manifest,
        "cycles": [],
        "status": "running",
    }
    write_state(state)

    cycle = 0
    stop_reason = "time-limit-reached"
    while time.time() < deadline and cycle < max_cycles:
        cycle += 1
        cycle_started = time.time()
        log(f"Overnight cycle {cycle}/{max_cycles} started")
        cycle_row: dict[str, Any] = {
            "cycle": cycle,
            "startedAt": utc_now(),
            "stages": [],
        }

        for stage in STAGES:
            result = run_stage(stage, cycle)
            cycle_row["stages"].append(result)

            if stage["name"] == "protected-93-06-regression":
                guard = result["passed"] and protected_regression_passed()
                cycle_row["protectedRegressionPassed"] = guard
                if not guard:
                    stop_reason = "protected-regression-failed"
                    log("STOP GUARD: protected 93.06 regression did not pass")
                    break

            if stage["required"] and not result["passed"]:
                stop_reason = f"required-stage-failed:{stage['name']}"
                break

        cycle_row["completedAt"] = utc_now()
        cycle_row["elapsedSeconds"] = round(time.time() - cycle_started, 3)
        cycle_row["snapshot"] = snapshot_protected_files(f"after-cycle-{cycle}")
        state["cycles"].append(cycle_row)
        write_state(state)

        if stop_reason != "time-limit-reached":
            break
        if time.time() >= deadline or cycle >= max_cycles:
            break

        log(f"Cycle {cycle} protected; sleeping {pause_seconds}s before next cycle")
        sleep_until = min(deadline, time.time() + pause_seconds)
        while time.time() < sleep_until:
            remaining = int(sleep_until - time.time())
            log(f"[overnight heartbeat] cycle={cycle} | nextCycleIn={remaining}s")
            time.sleep(min(60, max(1, remaining)))

    final_manifest = snapshot_protected_files("after-overnight-loop")
    state.update(
        {
            "completedAt": utc_now(),
            "status": "complete" if stop_reason == "time-limit-reached" else "stopped-by-guard",
            "stopReason": stop_reason,
            "cyclesCompleted": cycle,
            "finalManifest": final_manifest,
            "protectedRegressionStillPassed": protected_regression_passed(),
        }
    )
    write_state(state)
    SUMMARY_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    log(
        f"Overnight loop finished | cycles={cycle} | stopReason={stop_reason} | "
        f"protectedRegression={state['protectedRegressionStillPassed']}"
    )
    return 0 if state["protectedRegressionStillPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
