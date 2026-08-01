import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ANALYZER = ROOT / "analyzer"
TARGET = ANALYZER / "run_jimmy_page_ai_tab_113_measure_shadow_request.py"

STATE_PATH = PUBLIC / "gomyway-ai-tab-113-measure-resilient-state.json"
HEARTBEAT_LOG = ROOT / "jimmy-ai-tab-113-heartbeat.log"
RUN_LOG = ROOT / "jimmy-ai-tab-113-resilient-run.log"
HISTORY_DIR = PUBLIC / "jimmy-ai-tab-113-history"

OUTPUTS = [
    PUBLIC / "gomyway-ai-tab-113-measure-shadow-request.json",
    PUBLIC / "gomyway-ai-tab-113-measure-shadow-raw-response.json",
    PUBLIC / "gomyway-ai-tab-113-measure-shadow-transcription.json",
    PUBLIC / "gomyway-ai-tab-113-measure-shadow-report.json",
]

HEARTBEAT_SECONDS = int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15"))
MAX_ATTEMPTS = int(os.getenv("JIMMY_MAX_ATTEMPTS", "5"))
MAX_RETRIES = int(os.getenv("JIMMY_MAX_RETRIES", "3"))
RETRY_PAUSE_SECONDS = int(os.getenv("JIMMY_RETRY_PAUSE_SECONDS", "60"))
TOTAL_TIMEOUT_SECONDS = int(os.getenv("JIMMY_TOTAL_TIMEOUT_SECONDS", "7200"))

_stop_heartbeat = threading.Event()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_log(path: Path, message: str) -> None:
    line = f"[{now_iso()}] {message}\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())
    print(message, flush=True)


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(**updates: Any) -> dict[str, Any]:
    state = load_state()
    state.update(updates)
    state["updatedAt"] = now_iso()
    atomic_json(STATE_PATH, state)
    return state


def snapshot_outputs(label: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = HISTORY_DIR / f"{stamp}-{label}"
    destination.mkdir(parents=True, exist_ok=True)
    copied = 0
    for source in OUTPUTS:
        if source.exists():
            shutil.copy2(source, destination / source.name)
            copied += 1
    shutil.copy2(STATE_PATH, destination / STATE_PATH.name) if STATE_PATH.exists() else None
    append_log(RUN_LOG, f"Fallback snapshot saved: {destination.relative_to(ROOT)} files={copied}")
    return destination


def heartbeat_worker(started_at: float) -> None:
    while not _stop_heartbeat.wait(HEARTBEAT_SECONDS):
        state = load_state()
        elapsed = int(time.monotonic() - started_at)
        message = (
            f"heartbeat status={state.get('status', 'unknown')} "
            f"attempt={state.get('attempt', 0)}/{MAX_ATTEMPTS} "
            f"elapsedSeconds={elapsed} "
            f"lastCheckpoint={state.get('lastCheckpoint', 'none')}"
        )
        append_log(HEARTBEAT_LOG, message)
        save_state(lastHeartbeatAt=now_iso(), elapsedSeconds=elapsed)


def run_attempt(attempt: int) -> int:
    append_log(RUN_LOG, f"Starting protected shadow attempt {attempt}/{MAX_ATTEMPTS}")
    save_state(
        status="running",
        attempt=attempt,
        maxAttempts=MAX_ATTEMPTS,
        lastCheckpoint="attempt-start",
        target=str(TARGET.relative_to(ROOT)),
        productionAllowed=False,
    )

    with RUN_LOG.open("a", encoding="utf-8") as handle:
        process = subprocess.Popen(
            [sys.executable, str(TARGET)],
            cwd=ROOT,
            stdout=handle,
            stderr=subprocess.STDOUT,
            env=os.environ.copy(),
        )
        try:
            return_code = process.wait(timeout=TOTAL_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            append_log(RUN_LOG, f"Attempt {attempt} timed out after {TOTAL_TIMEOUT_SECONDS} seconds")
            return_code = 124

    save_state(
        lastCheckpoint="attempt-finished",
        lastReturnCode=return_code,
        lastAttemptFinishedAt=now_iso(),
    )
    snapshot_outputs(f"attempt-{attempt}-rc-{return_code}")
    return return_code


def report_passed() -> bool:
    report_path = PUBLIC / "gomyway-ai-tab-113-measure-shadow-report.json"
    if not report_path.exists():
        return False
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return bool(
        report.get("full113MeasureCoveragePassed")
        and report.get("sourceAudioShaUnchanged")
        and not report.get("productionPromotionAllowed")
    )


def main() -> None:
    if not TARGET.exists():
        raise FileNotFoundError(f"Missing target script: {TARGET.relative_to(ROOT)}")

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    started_at = time.monotonic()
    previous_state = load_state()
    previous_attempt = int(previous_state.get("attempt", 0) or 0)

    save_state(
        status="starting",
        resumedFromAttempt=previous_attempt,
        startedAt=previous_state.get("startedAt") or now_iso(),
        restartAt=now_iso(),
        heartbeatSeconds=HEARTBEAT_SECONDS,
        maxAttempts=MAX_ATTEMPTS,
        maxRetries=MAX_RETRIES,
        retryPauseSeconds=RETRY_PAUSE_SECONDS,
        totalTimeoutSeconds=TOTAL_TIMEOUT_SECONDS,
        lastCheckpoint="restart-initialized",
        productionAllowed=False,
    )

    heartbeat = threading.Thread(target=heartbeat_worker, args=(started_at,), daemon=True)
    heartbeat.start()

    try:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            return_code = run_attempt(attempt)
            if return_code == 0 and report_passed():
                snapshot_outputs("completed")
                save_state(
                    status="completed",
                    completedAt=now_iso(),
                    lastCheckpoint="verified-complete",
                    productionAllowed=False,
                )
                append_log(RUN_LOG, "Protected 113-measure shadow run completed and verified")
                return

            save_state(
                status="retrying" if attempt < MAX_ATTEMPTS else "failed",
                lastCheckpoint="fallback-saved",
            )
            if attempt < MAX_ATTEMPTS:
                append_log(RUN_LOG, f"Waiting {RETRY_PAUSE_SECONDS} seconds before restart")
                time.sleep(RETRY_PAUSE_SECONDS)

        snapshot_outputs("final-failure")
        save_state(
            status="failed",
            failedAt=now_iso(),
            lastCheckpoint="all-attempts-exhausted",
            productionAllowed=False,
        )
        raise RuntimeError("All resilient shadow attempts were exhausted")
    finally:
        _stop_heartbeat.set()
        heartbeat.join(timeout=HEARTBEAT_SECONDS + 2)
        append_log(HEARTBEAT_LOG, "heartbeat stopped")


if __name__ == "__main__":
    main()
