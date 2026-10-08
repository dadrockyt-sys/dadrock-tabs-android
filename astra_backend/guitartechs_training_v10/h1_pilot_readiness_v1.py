"""Model-free, fail-closed H1 pilot input and scalar progress guards.

These helpers do not authorize or launch the blocked real-data H1 study.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re

FROZEN_ALIGNMENT_BLOB = "9090d465422ebf5d4fdf170693fe0936934f3073"
STEP_CAP = 160
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def verify_population(rows, data_dir, alignment_path, expected_blob=FROZEN_ALIGNMENT_BLOB):
    """Verify the *independently frozen* 256-key identity and all prepared hashes.

    Returns scalar-only provenance. Must run before any optimizer step.
    """
    raw = Path(alignment_path).read_bytes()
    if git_blob_sha(raw) != expected_blob:
        raise RuntimeError("FROZEN_ALIGNMENT_BLOB_MISMATCH")
    alignment = json.loads(raw)
    if alignment.get("schema") != "astra-guitar-techs-primary-alignment-corrections-v1":
        raise RuntimeError("ALIGNMENT_SCHEMA_MISMATCH")
    expected = alignment["correctionsMs"]
    if len(expected) != 256 or alignment.get("acceptedPrimaryCount") != 256:
        raise RuntimeError("ALIGNMENT_POPULATION_MISMATCH")
    keys = [row["key"] for row in rows]
    if len(keys) != 256 or len(set(keys)) != 256 or set(keys) != set(expected):
        raise RuntimeError("FROZEN_ACCEPTED_KEYS_MISMATCH")
    root = Path(data_dir).resolve(strict=True)
    counts = {"P1": 0, "P2": 0}
    for row in rows:
        key = row["key"]
        parts = key.split("|")
        if len(parts) != 4 or parts[0] not in counts or parts[1] not in (
            "chords", "scales", "singlenotes", "techniques"
        ):
            raise RuntimeError("UNEXPECTED_CAPTURE_KEY")
        if (row["performer"], row["category"], row["performanceKey"],
                row["captureView"]) != tuple(parts):
            raise RuntimeError("CAPTURE_IDENTITY_MISMATCH")
        if type(row["lagMs"]) not in (int, float) or not math.isfinite(row["lagMs"]):
            raise RuntimeError("INVALID_ALIGNMENT_LAG")
        if row["lagMs"] != expected[key] or type(row["frames"]) is not int or row["frames"] <= 0:
            raise RuntimeError("CAPTURE_ALIGNMENT_OR_FRAME_MISMATCH")
        ident = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        for kind, filename, digest, expected_filename in (
            ("feature", row["featureFile"], row["featureSha256"], ident + ".features.npy"),
            ("label", row["labelFile"], row["labelSha256"], ident + ".labels.npy"),
        ):
            if filename != expected_filename or not isinstance(digest, str) or not SHA256.fullmatch(digest):
                raise RuntimeError("PREPARED_FILE_IDENTITY_MISMATCH_" + kind)
            location = (root / filename).resolve(strict=True)
            if location.parent != root or sha256_file(location) != digest:
                raise RuntimeError("PREPARED_FILE_HASH_MISMATCH_" + kind)
        counts[parts[0]] += 1
    if counts != {"P1": 136, "P2": 120}:
        raise RuntimeError("FROZEN_PERFORMER_COUNTS_MISMATCH")
    return {
        "alignmentGitBlob": git_blob_sha(raw),
        "acceptedKeysSha256": hashlib.sha256("\n".join(sorted(keys)).encode("utf-8")).hexdigest(),
        "captureCount": len(keys),
        "performerCounts": counts,
    }


def require_zero_control(metrics, totals):
    if metrics.get("f1") != 0 or not math.isfinite(metrics["f1"]):
        raise RuntimeError("ORIGINAL_CONTROL_NONZERO_F1")
    if totals.get("predictedEvents") != 0 or totals.get("activeRunsAfterPrune") != 0:
        raise RuntimeError("ORIGINAL_CONTROL_NONZERO_ADMISSION")


class ScalarProgress:
    """Atomic, scalar-only, non-resumable, last-confirmed-step evidence."""

    def __init__(self, path, identity):
        self.path = Path(path)
        self.payload = {
            "schema": "astra-h1-pilot-scalar-progress-v1",
            "identity": identity,
            "status": "running",
            "phase": "pre_optimizer",
            "optimizerStepsConfirmed": 0,
            "stepCap": STEP_CAP,
            "controlsVerified": [],
        }
        self.save()

    def save(self):
        encoded = json.dumps(self.payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        try:
            with tmp.open("w", encoding="utf-8") as out:
                out.write(encoded)
                out.flush()
                os.fsync(out.fileno())
            os.replace(tmp, self.path)
        finally:
            tmp.unlink(missing_ok=True)

    def before_step(self):
        if self.payload["optimizerStepsConfirmed"] >= STEP_CAP:
            raise RuntimeError("H1_GLOBAL_STEP_CAP_EXHAUSTED")

    def confirmed_step(self, fold, arm, epoch, arm_steps):
        self.before_step()
        self.payload["optimizerStepsConfirmed"] += 1
        self.payload["phase"] = "optimizer"
        self.payload["lastConfirmed"] = {
            "fold": fold, "arm": arm, "epoch": epoch, "armSteps": arm_steps
        }
        self.save()

    def control_verified(self, fold):
        if fold in self.payload["controlsVerified"]:
            raise RuntimeError("DUPLICATE_CONTROL")
        self.payload["controlsVerified"].append(fold)
        self.payload["phase"] = "control_verified"
        self.save()

    def phase(self, name):
        self.payload["phase"] = name
        self.save()

    def finish(self):
        if self.payload["optimizerStepsConfirmed"] != STEP_CAP or len(self.payload["controlsVerified"]) != 2:
            raise RuntimeError("H1_INCOMPLETE_STEP_OR_CONTROL_COUNT")
        self.payload["status"] = "completed"
        self.payload["phase"] = "complete"
        self.save()

    def fail(self, error):
        self.payload["status"] = "failed"
        self.payload["errorType"] = type(error).__name__
        self.payload["errorCode"] = str(error)[:160]
        self.save()
