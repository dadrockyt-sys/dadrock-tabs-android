#!/usr/bin/env python3
"""Validate the prospectively frozen V168 cross-song holdout asset manifest.

This validator performs admission/integrity checks only. It does not read audio,
professional reference note events, generated candidates, or scorer code, and it
cannot score anything. It exists so future holdout assets cannot silently weaken
the V168 preregistration after they are seen.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping

SCHEMA = "dadrock.tabs.v168.holdout-asset-manifest.v1"
VERSION = "V168"
CALIBRATION_SONG_ID = "lenny-kravitz-are-you-gonna-go-my-way"
MIN_HOLDOUT_SONGS = 2
FROZEN_POLICY_IDS = [
    "v168-baseline-i005-policy",
    "v168-gap1-earliest-policy",
]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_BLOB_RE = re.compile(r"^[0-9a-f]{40}$")


class ManifestError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestError(message)


def require_text(value: Any, field: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{field} must be non-empty text")
    return value.strip()


def require_sha256(value: Any, field: str) -> str:
    text = require_text(value, field).lower()
    require(bool(SHA256_RE.fullmatch(text)), f"{field} must be lowercase SHA256")
    return text


def require_optional_git_blob(value: Any, field: str) -> str | None:
    if value is None:
        return None
    text = require_text(value, field).lower()
    require(bool(GIT_BLOB_RE.fullmatch(text)), f"{field} must be a 40-char lowercase Git blob SHA")
    return text


def normalize_song_key(artist: str, title: str) -> str:
    raw = f"{artist}-{title}".lower()
    return "-".join(part for part in re.split(r"[^a-z0-9]+", raw) if part)


def validate_identity(identity: Mapping[str, Any], field: str) -> tuple[str, str | None]:
    require(isinstance(identity, Mapping), f"{field} must be an object")
    require_text(identity.get("artifactLabel"), f"{field}.artifactLabel")
    sha256 = require_sha256(identity.get("sha256"), f"{field}.sha256")
    git_blob = require_optional_git_blob(identity.get("gitBlob"), f"{field}.gitBlob")
    require(identity.get("identityFrozen") is True, f"{field}.identityFrozen must be true")
    return sha256, git_blob


def validate_song(row: Mapping[str, Any], index: int) -> dict[str, Any]:
    prefix = f"songs[{index}]"
    require(isinstance(row, Mapping), f"{prefix} must be an object")
    song_id = require_text(row.get("songId"), f"{prefix}.songId")
    artist = require_text(row.get("artist"), f"{prefix}.artist")
    title = require_text(row.get("title"), f"{prefix}.title")
    require(song_id != CALIBRATION_SONG_ID, f"{prefix} cannot be the V167 calibration song id")
    require(
        normalize_song_key(artist, title) != CALIBRATION_SONG_ID,
        f"{prefix} cannot be Lenny Kravitz — Are You Gonna Go My Way",
    )
    require(row.get("independentFromV167CalibrationSong") is True, f"{prefix}.independentFromV167CalibrationSong must be true")
    require(row.get("admissionDecisionMadeWithoutComparativeScores") is True, f"{prefix}.admissionDecisionMadeWithoutComparativeScores must be true")

    source_sha, _ = validate_identity(row.get("sourceAudio") or {}, f"{prefix}.sourceAudio")
    reference = row.get("professionalReference") or {}
    reference_sha, _ = validate_identity(reference, f"{prefix}.professionalReference")
    require(reference.get("kind") == "professional_scorer_ready", f"{prefix}.professionalReference.kind must be professional_scorer_ready")
    require(reference.get("combinedGuitarCovered") is True, f"{prefix}.professionalReference.combinedGuitarCovered must be true")
    require(reference.get("uncertaintyAnnotationsFrozen") is True, f"{prefix}.professionalReference.uncertaintyAnnotationsFrozen must be true")
    require(reference.get("candidateGenerationMayReadNoteEvents") is False, f"{prefix}.professionalReference.candidateGenerationMayReadNoteEvents must be false")
    require(reference.get("referenceFrozenBeforeCandidateScoring") is True, f"{prefix}.professionalReference.referenceFrozenBeforeCandidateScoring must be true")

    return {
        "songId": song_id,
        "artist": artist,
        "title": title,
        "sourceSha256": source_sha,
        "referenceSha256": reference_sha,
    }


def validate_manifest(payload: Mapping[str, Any]) -> dict[str, Any]:
    require(isinstance(payload, Mapping), "manifest root must be an object")
    require(payload.get("schema") == SCHEMA, f"schema must equal {SCHEMA}")
    require(payload.get("version") == VERSION, f"version must equal {VERSION}")
    require(payload.get("status") == "HOLDOUT_ASSETS_FROZEN_BEFORE_CANDIDATE_GENERATION", "unexpected manifest status")
    require(payload.get("calibrationSongIdExcluded") == CALIBRATION_SONG_ID, "calibrationSongIdExcluded drift")
    require(payload.get("policyIds") == FROZEN_POLICY_IDS, "policyIds must equal the two frozen V168 policies in order")
    require(payload.get("minimumHoldoutSongs") == MIN_HOLDOUT_SONGS, "minimumHoldoutSongs drift")

    boundary = payload.get("boundary") or {}
    require(boundary.get("professionalReferenceReadByCandidateGeneration") is False, "candidate generation reference-read boundary must be false")
    require(boundary.get("comparativeScoresReadBeforeAdmissionFreeze") is False, "comparative scores must not be read before admission freeze")
    require(boundary.get("referenceFacingScoringArmed") is False, "reference-facing scoring must still be unarmed at asset freeze")
    require(boundary.get("v168ReferenceFacingScoreCallsBeforeAssetFreeze") == 0, "V168 score calls before asset freeze must be 0")
    require(boundary.get("mainOrProductionModified") is False, "main/Production modification boundary must be false")
    require(boundary.get("gpuCudaModalUsed") is False, "GPU/CUDA/Modal boundary must be false")

    songs = payload.get("songs")
    require(isinstance(songs, list), "songs must be an array")
    require(len(songs) >= MIN_HOLDOUT_SONGS, f"at least {MIN_HOLDOUT_SONGS} independent holdout songs are required")

    validated = [validate_song(row, i) for i, row in enumerate(songs)]
    song_ids = [row["songId"] for row in validated]
    source_hashes = [row["sourceSha256"] for row in validated]
    reference_hashes = [row["referenceSha256"] for row in validated]
    require(len(song_ids) == len(set(song_ids)), "holdout songId values must be unique")
    require(len(source_hashes) == len(set(source_hashes)), "holdout source-audio SHA256 values must be unique")
    require(len(reference_hashes) == len(set(reference_hashes)), "holdout reference SHA256 values must be unique")

    artists = {row["artist"].casefold() for row in validated}
    return {
        "schema": SCHEMA,
        "status": payload["status"],
        "songCount": len(validated),
        "uniqueArtistCount": len(artists),
        "songIds": song_ids,
        "policyIds": list(FROZEN_POLICY_IDS),
        "referenceFacingScoringArmed": False,
        "v168ReferenceFacingScoreCalls": 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    summary = validate_manifest(payload)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ManifestError as exc:
        raise SystemExit(f"V168 holdout manifest invalid: {exc}")
