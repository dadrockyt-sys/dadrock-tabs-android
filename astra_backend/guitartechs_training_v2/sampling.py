from __future__ import annotations

from collections import defaultdict
import hashlib

SEED = 20260921
SEQUENCE_FRAMES = 200
BATCH_SIZE = 32


def _u64(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")


def _group_key(row):
    return f"{row['performer']}|{row['category']}|{row['performanceKey']}"


def build_epoch_plan(rows, *, epoch, seed=SEED, sequence_frames=SEQUENCE_FRAMES):
    if not isinstance(epoch, int) or epoch < 0:
        raise ValueError("epoch must be a nonnegative integer")
    if not isinstance(sequence_frames, int) or sequence_frames <= 0:
        raise ValueError("sequence_frames must be positive")

    groups = defaultdict(list)
    for row in rows:
        required = ("key", "performer", "category", "performanceKey", "captureView", "frames")
        if any(field not in row for field in required):
            raise ValueError("row missing required training-manifest field")
        if not isinstance(row["frames"], int) or row["frames"] < sequence_frames:
            raise ValueError("accepted capture shorter than frozen sequence length")
        groups[_group_key(row)].append(dict(row))

    if not groups:
        raise ValueError("empty training manifest")

    plan = []
    for group_key in sorted(groups):
        views = sorted(groups[group_key], key=lambda row: (row["captureView"], row["key"]))
        view_index = _u64(f"{seed}|{epoch}|{group_key}|view") % len(views)
        row = views[view_index]
        max_start = row["frames"] - sequence_frames
        start = _u64(f"{seed}|{epoch}|{group_key}|start") % (max_start + 1)
        plan.append({
            "groupKey": group_key,
            "captureKey": row["key"],
            "captureView": row["captureView"],
            "startFrame": int(start),
            "endFrame": int(start + sequence_frames),
            "sequenceFrames": sequence_frames,
        })

    return plan


def batch_epoch_plan(plan, *, batch_size=BATCH_SIZE):
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be positive")
    return [plan[i:i + batch_size] for i in range(0, len(plan), batch_size)]


def supervised_frame_positions(plan):
    return sum(item["sequenceFrames"] for item in plan)
