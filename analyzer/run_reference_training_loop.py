from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = ROOT / "analyzer" / "training_profiles" / "rhythm-guitar-reference.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def file_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def protected_hashes(profile: dict[str, Any]) -> dict[str, str | None]:
    return {
        relative: file_hash(ROOT / relative)
        for relative in profile.get("protectedInputs", [])
    }


def validate_result(result: dict[str, Any], profile: dict[str, Any]) -> tuple[float, bool, list[str]]:
    categories = result.get("categoryScoresPercent") or {}
    weights = profile["weights"]
    minimums = profile["minimumCategoryPercent"]
    errors: list[str] = []
    total = 0.0
    for key, weight in weights.items():
        try:
            value = float(categories[key])
        except (KeyError, TypeError, ValueError):
            errors.append(f"missing-category:{key}")
            value = 0.0
        if not 0.0 <= value <= 100.0:
            errors.append(f"invalid-category:{key}")
        if value < float(minimums[key]):
            errors.append(f"category-below-minimum:{key}")
        total += max(0.0, min(100.0, value)) * float(weight)

    protections = result.get("protections") or {}
    for key, required in profile.get("protectedRules", {}).items():
        if protections.get(key) is not required:
            errors.append(f"protection-failed:{key}")

    target_met = total >= float(profile["targetCompositePercent"]) and not errors
    return round(total, 6), target_met, errors


def git_save(attempt: int, checkpoint: Path, status: Path, best: Path, summary: Path) -> None:
    if os.environ.get("SAVE_TRAINING_CHECKPOINTS_TO_GIT", "false").lower() != "true":
        return
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], cwd=ROOT, check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=ROOT, check=True)
    paths = [path for path in (checkpoint, status, best, summary) if path.exists()]
    subprocess.run(["git", "add", *[str(path.relative_to(ROOT)) for path in paths]], cwd=ROOT, check=True)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
    if diff.returncode == 0:
        return
    subprocess.run(["git", "commit", "-m", f"Save rhythm training attempt {attempt}"], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", f"HEAD:{os.environ.get('TRAINING_BRANCH', 'jimmy-paige-v8-section-detection')}"], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE))
    parser.add_argument("--max-attempts", type=int, default=250)
    parser.add_argument("--max-hours", type=float, default=10.0)
    args = parser.parse_args()

    profile_path = Path(args.profile)
    if not profile_path.is_absolute():
        profile_path = ROOT / profile_path
    profile = load_json(profile_path)

    checkpoint_dir = ROOT / profile["checkpointDirectory"]
    best_path = ROOT / profile["bestCheckpointPath"]
    status_path = ROOT / profile["statusPath"]
    summary_path = ROOT / profile["summaryPath"]
    result_path = ROOT / profile["attemptResultPath"]
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    prior = sorted(checkpoint_dir.glob("attempt-*.json"))
    first_attempt = int(prior[-1].stem.split("-")[-1]) + 1 if prior else 1
    best = load_json(best_path) if best_path.exists() else None
    best_score = float(best.get("compositeScorePercent", 0.0)) if best else 0.0
    original_hashes = protected_hashes(profile)
    started = time.monotonic()

    state: dict[str, Any] = {
        "healthy": True,
        "phase": "starting",
        "attempt": first_attempt,
        "latestScorePercent": None,
        "bestScorePercent": best_score,
        "targetPercent": profile["targetCompositePercent"],
        "updatedAt": now_iso(),
    }
    stop_heartbeat = threading.Event()

    def heartbeat() -> None:
        interval = max(15, int(profile.get("heartbeatSeconds", 60)))
        while not stop_heartbeat.wait(interval):
            state["updatedAt"] = now_iso()
            write_json(status_path, state)
            print(
                "HEARTBEAT",
                state["updatedAt"],
                f"healthy={state['healthy']}",
                f"phase={state['phase']}",
                f"attempt={state['attempt']}",
                f"latest={state['latestScorePercent']}",
                f"best={state['bestScorePercent']}",
                flush=True,
            )

    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()

    try:
        for attempt in range(first_attempt, first_attempt + args.max_attempts):
            if (time.monotonic() - started) >= args.max_hours * 3600:
                break

            state.update({"phase": "running-attempt", "attempt": attempt, "updatedAt": now_iso()})
            write_json(status_path, state)
            if result_path.exists():
                result_path.unlink()

            command = profile["attemptCommand"]
            print(f"ATTEMPT {attempt} START {now_iso()} command={command}", flush=True)
            completed = subprocess.run(command, cwd=ROOT, shell=True, text=True)

            result: dict[str, Any] = {}
            errors: list[str] = []
            if completed.returncode != 0:
                errors.append(f"attempt-command-exit:{completed.returncode}")
            if result_path.exists():
                try:
                    result = load_json(result_path)
                except Exception as exc:  # checkpoint the parse failure
                    errors.append(f"result-parse-failed:{exc}")
            else:
                errors.append("attempt-result-missing")

            score, target_met, validation_errors = validate_result(result, profile)
            errors.extend(validation_errors)
            current_hashes = protected_hashes(profile)
            if current_hashes != original_hashes:
                errors.append("protected-input-hash-changed")
                target_met = False

            checkpoint = {
                "attempt": attempt,
                "startedAt": state.get("updatedAt"),
                "completedAt": now_iso(),
                "commandExitCode": completed.returncode,
                "compositeScorePercent": score,
                "targetMet": target_met,
                "errors": errors,
                "protectedInputHashes": current_hashes,
                "result": result,
            }
            checkpoint_path = checkpoint_dir / f"attempt-{attempt:06d}.json"
            write_json(checkpoint_path, checkpoint)

            if score > best_score and not any(error.startswith("protection-failed") for error in errors):
                best_score = score
                best = checkpoint
                write_json(best_path, checkpoint)

            state.update({
                "phase": "attempt-saved",
                "latestScorePercent": score,
                "bestScorePercent": best_score,
                "healthy": True,
                "updatedAt": now_iso(),
            })
            write_json(status_path, state)
            summary = {
                "profile": profile["profileName"],
                "measures": [profile["measureStart"], profile["measureEnd"]],
                "attemptsCompletedThisRun": attempt - first_attempt + 1,
                "lastAttempt": attempt,
                "latestScorePercent": score,
                "bestScorePercent": best_score,
                "targetPercent": profile["targetCompositePercent"],
                "targetMet": bool(best and best.get("targetMet")),
                "bestCheckpoint": str(best_path.relative_to(ROOT)) if best else None,
                "protectedBaselinesChanged": current_hashes != original_hashes,
                "updatedAt": now_iso(),
            }
            write_json(summary_path, summary)
            git_save(attempt, checkpoint_path, status_path, best_path, summary_path)
            print(f"ATTEMPT {attempt} SAVED score={score:.3f} best={best_score:.3f} target={target_met}", flush=True)

            if target_met:
                state["phase"] = "target-achieved"
                write_json(status_path, state)
                break
    finally:
        stop_heartbeat.set()
        thread.join(timeout=2)
        state["updatedAt"] = now_iso()
        write_json(status_path, state)
        print(f"TRAINING STOP phase={state['phase']} best={state['bestScorePercent']}", flush=True)


if __name__ == "__main__":
    main()
