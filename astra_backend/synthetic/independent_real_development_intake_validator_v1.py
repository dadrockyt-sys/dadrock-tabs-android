#!/usr/bin/env python3
"""Pure intake validator for independent real-development evaluation V1."""
from __future__ import annotations

import json
import math
from pathlib import Path

REQUIRED_COVERAGE = {
    "single-note",
    "repeated-attacks",
    "legato",
    "palm-mute",
    "dyad-or-chord",
    "clean-capture",
    "distorted-or-overdriven-capture",
}


class IntakeValidationError(ValueError):
    pass


def _real(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise IntakeValidationError(f"{label}: expected number")
    value = float(value)
    if not math.isfinite(value):
        raise IntakeValidationError(f"{label}: non-finite")
    return value


def validate_intake(data):
    if not isinstance(data, dict):
        raise IntakeValidationError("intake must be object")
    if data.get("schema") != "astra-independent-real-development-intake-v1":
        raise IntakeValidationError("schema mismatch")

    ind = data.get("independence")
    if not isinstance(ind, dict):
        raise IntakeValidationError("independence missing")
    for key in (
        "createdOrSourcedAfterDesignFreeze",
        "noP1Overlap",
        "noP2Overlap",
        "noP3Overlap",
        "noPreviouslyInspectedOrTunedAudio",
    ):
        if ind.get(key) is not True:
            raise IntakeValidationError(f"independence {key} must be true")
    if not isinstance(ind.get("declaration"), str) or not ind["declaration"].strip():
        raise IntakeValidationError("independence declaration required")

    cand = data.get("candidate")
    if not isinstance(cand, dict):
        raise IntakeValidationError("candidate missing")
    for key in ("name", "weightsSha256", "sourceCommit", "modelSourcePath", "frontendSourcePath", "evaluatorSourcePath"):
        if not isinstance(cand.get(key), str) or not cand[key].strip():
            raise IntakeValidationError(f"candidate {key} required")
    if cand.get("stateThreshold") != 0.5 or cand.get("onsetThreshold") != 0.5:
        raise IntakeValidationError("candidate thresholds must remain 0.5/0.5")

    clips = data.get("clips")
    if not isinstance(clips, list) or len(clips) < 24:
        raise IntakeValidationError("at least 24 clips required")

    ids=set()
    pos=neg=0
    pos_sec=neg_sec=0.0
    coverage=set()
    for i, clip in enumerate(clips):
        if not isinstance(clip, dict):
            raise IntakeValidationError(f"clip {i}: object required")
        cid=clip.get("id")
        if not isinstance(cid,str) or not cid:
            raise IntakeValidationError(f"clip {i}: id required")
        if cid in ids:
            raise IntakeValidationError(f"duplicate clip id {cid}")
        ids.add(cid)

        sha=clip.get("sha256")
        if not isinstance(sha,str) or len(sha)!=64:
            raise IntakeValidationError(f"clip {cid}: sha256 required")
        dur=_real(clip.get("durationSeconds"),f"clip {cid} duration")
        if not 4 <= dur <= 10:
            raise IntakeValidationError(f"clip {cid}: duration outside 4-10 seconds")

        kind=clip.get("kind")
        tags=clip.get("coverage",[])
        if not isinstance(tags,list) or any(not isinstance(x,str) for x in tags):
            raise IntakeValidationError(f"clip {cid}: coverage invalid")
        coverage.update(tags)

        if kind=="positive":
            pos+=1; pos_sec+=dur
            anns=clip.get("annotations")
            if not isinstance(anns,list) or not anns:
                raise IntakeValidationError(f"clip {cid}: positive clip annotations required")
            for j,a in enumerate(anns):
                if not isinstance(a,dict):
                    raise IntakeValidationError(f"clip {cid} annotation {j}: object required")
                _real(a.get("eventStart"),f"clip {cid} annotation {j} eventStart")
                pitch=a.get("pitch")
                if isinstance(pitch,bool) or not isinstance(pitch,int) or not 0<=pitch<=127:
                    raise IntakeValidationError(f"clip {cid} annotation {j}: MIDI pitch required")
                if a.get("confidence") not in ("high","medium","low"):
                    raise IntakeValidationError(f"clip {cid} annotation {j}: confidence invalid")
        elif kind=="negative-only":
            neg+=1; neg_sec+=dur
            if clip.get("annotations") not in ([],None):
                raise IntakeValidationError(f"clip {cid}: negative clip must not have target annotations")
        else:
            raise IntakeValidationError(f"clip {cid}: kind invalid")

    if pos < 18 or neg < 6:
        raise IntakeValidationError("need at least 18 positive and 6 negative-only clips")
    if pos_sec < 90 or neg_sec < 30:
        raise IntakeValidationError("audio-duration minima not met")
    missing=REQUIRED_COVERAGE-coverage
    if missing:
        raise IntakeValidationError("missing coverage: "+",".join(sorted(missing)))

    if data.get("annotationsFrozenBeforeInference") is not True:
        raise IntakeValidationError("annotations must be frozen before inference")
    if data.get("modelInferenceCount") != 0:
        raise IntakeValidationError("pre-inference intake must report zero model inference")
    if data.get("optimizerSteps") != 0:
        raise IntakeValidationError("intake must report zero optimizer steps")
    for key in ("p1Accessed","p2Accessed","p3Accessed"):
        if data.get(key) is not False:
            raise IntakeValidationError(f"{key} must remain false")

    summary=data.get("summary")
    if not isinstance(summary,dict):
        raise IntakeValidationError("summary missing")
    expected={
        "clipCount":len(clips),
        "positiveClipCount":pos,
        "negativeOnlyClipCount":neg,
    }
    for k,v in expected.items():
        if summary.get(k)!=v:
            raise IntakeValidationError(f"summary {k} mismatch")
    if not math.isclose(_real(summary.get("positiveAudioSeconds"),"summary positiveAudioSeconds"),pos_sec,abs_tol=1e-9):
        raise IntakeValidationError("summary positiveAudioSeconds mismatch")
    if not math.isclose(_real(summary.get("negativeAudioSeconds"),"summary negativeAudioSeconds"),neg_sec,abs_tol=1e-9):
        raise IntakeValidationError("summary negativeAudioSeconds mismatch")
    if set(summary.get("coverage",[])) != coverage:
        raise IntakeValidationError("summary coverage mismatch")
    return True


def validate_file(path):
    return validate_intake(json.loads(Path(path).read_text()))
