#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from collections import defaultdict
from pathlib import Path
from typing import Any

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CATEGORIES = ("chords", "scales", "singlenotes", "techniques", "music")
ROLES = ("lead", "rhythm")
PROVENANCE = {
    "original_project_composition", "public_domain",
    "commissioned_cleared", "explicit_rightsholder_grant",
}
CLOCK_MODES = {"single_shared_hardware_clock", "preregistered_hardware_sync_mapping"}

def is_sha(v: Any) -> bool:
    return isinstance(v, str) and bool(SHA256_RE.fullmatch(v))

def nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())

def validate(package: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(package, dict):
        return {"schema": "astra-guitar-fl-stage-b-precapture-validation-v2", "contractValid": False,
                "captureReady": False, "errors": ["TOP_LEVEL_OBJECT_REQUIRED"]}
    if package.get("schema") != "astra-guitar-fl-stage-b-precapture-package-v2":
        errors.append("SCHEMA_MISMATCH")

    authority = package.get("authority") if isinstance(package.get("authority"), dict) else {}
    for field in (
        "spendingAuthorized", "procurementAuthorized", "performerContactAuthorized",
        "vendorContactAuthorized", "calibrationRecordingAuthorized", "captureAuthorized",
        "empiricalExecutionAuthorized", "modelInferenceAuthorized", "referenceScoringAuthorized",
    ):
        if authority.get(field) is not False:
            errors.append(f"AUTHORITY_{field.upper()}_MUST_BE_FALSE")

    hw = package.get("hardwareReferenceArchitecture")
    if not isinstance(hw, dict):
        errors.append("HARDWARE_REFERENCE_ARCHITECTURE_REQUIRED"); hw = {}
    if hw.get("evaluatedAudioSource") != "clean_magnetic_guitar_di":
        errors.append("EVALUATED_AUDIO_SOURCE_INVALID")
    if hw.get("referenceTimingDerivedFromAudioOrModel") is not False:
        errors.append("AUDIO_OR_MODEL_DERIVED_REFERENCE_TIMING_FORBIDDEN")
    planes = hw.get("referencePlanes") if isinstance(hw.get("referencePlanes"), dict) else {}
    if planes.get("stringFretState") != "independent_physical_string_fret_state":
        errors.append("STRING_FRET_REFERENCE_PLANE_REQUIRED")
    if planes.get("eventBirth") != "independent_excitation_event_birth":
        errors.append("EVENT_BIRTH_REFERENCE_PLANE_REQUIRED")
    clock = hw.get("clock") if isinstance(hw.get("clock"), dict) else {}
    mode = clock.get("mode")
    if mode not in CLOCK_MODES:
        errors.append("CLOCK_MODE_INVALID")
    if mode == "preregistered_hardware_sync_mapping":
        if not is_sha(clock.get("mappingConfigurationSha256")):
            errors.append("CLOCK_SYNC_MAPPING_SHA_REQUIRED")
        if clock.get("mappingUsesOnlyHardwareSyncMarkers") is not True:
            errors.append("CLOCK_SYNC_MUST_USE_HARDWARE_MARKERS_ONLY")

    rights = package.get("rightsManifest")
    if not isinstance(rights, dict):
        errors.append("RIGHTS_MANIFEST_REQUIRED"); rights = {}
    if not nonempty(rights.get("manifestId")): errors.append("RIGHTS_MANIFEST_ID_REQUIRED")
    if not is_sha(rights.get("manifestSha256")): errors.append("RIGHTS_MANIFEST_SHA_INVALID")
    if rights.get("protectedSongsExcluded") is not True: errors.append("PROTECTED_SONG_EXCLUSION_REQUIRED")

    documents = rights.get("documents") if isinstance(rights.get("documents"), list) else []
    doc_ids: set[str] = set()
    for i, d in enumerate(documents):
        if not isinstance(d, dict): errors.append(f"DOCUMENT[{i}]_OBJECT_REQUIRED"); continue
        did = d.get("documentId")
        if not nonempty(did): errors.append(f"DOCUMENT[{i}]_ID_REQUIRED")
        elif did in doc_ids: errors.append(f"DOCUMENT[{i}]_ID_DUPLICATE")
        else: doc_ids.add(did)
        if not is_sha(d.get("sha256")): errors.append(f"DOCUMENT[{i}]_SHA_INVALID")
        if not nonempty(d.get("documentType")): errors.append(f"DOCUMENT[{i}]_TYPE_REQUIRED")

    performers = rights.get("performers") if isinstance(rights.get("performers"), list) else []
    pids: set[str] = set()
    if len(performers) < 6: errors.append("PERFORMER_COUNT_BELOW_MINIMUM")
    for i, p in enumerate(performers):
        if not isinstance(p, dict): errors.append(f"PERFORMER[{i}]_OBJECT_REQUIRED"); continue
        pid = p.get("performerId")
        if not nonempty(pid): errors.append(f"PERFORMER[{i}]_ID_REQUIRED")
        elif pid in pids: errors.append(f"PERFORMER[{i}]_ID_DUPLICATE")
        else: pids.add(pid)
        for field in ("releaseDocumentId", "recordingOwnershipUseGrantDocumentId"):
            if p.get(field) not in doc_ids: errors.append(f"PERFORMER[{i}]_{field.upper()}_LINK_INVALID")
        for field in ("recordingProductValidationUseGranted", "referenceSensorDataUseGranted", "internalRetentionGranted"):
            if p.get(field) is not True: errors.append(f"PERFORMER[{i}]_{field.upper()}_REQUIRED")

    contents = rights.get("contents") if isinstance(rights.get("contents"), list) else []
    cids: set[str] = set()
    for i, c in enumerate(contents):
        if not isinstance(c, dict): errors.append(f"CONTENT[{i}]_OBJECT_REQUIRED"); continue
        cid = c.get("contentId")
        if not nonempty(cid): errors.append(f"CONTENT[{i}]_ID_REQUIRED")
        elif cid in cids: errors.append(f"CONTENT[{i}]_ID_DUPLICATE")
        else: cids.add(cid)
        if c.get("provenanceClass") not in PROVENANCE: errors.append(f"CONTENT[{i}]_PROVENANCE_INVALID")
        if c.get("rightsDocumentId") not in doc_ids: errors.append(f"CONTENT[{i}]_RIGHTS_DOCUMENT_LINK_INVALID")
        if c.get("productValidationUseGranted") is not True: errors.append(f"CONTENT[{i}]_PRODUCT_VALIDATION_GRANT_REQUIRED")
        if c.get("protectedSong") is not False: errors.append(f"CONTENT[{i}]_PROTECTED_SONG_FORBIDDEN")

    calibration_ids = package.get("calibrationPopulationIds")
    holdout_ids = package.get("holdoutPopulationIds")
    if not isinstance(calibration_ids, list): calibration_ids = []; errors.append("CALIBRATION_POPULATION_IDS_REQUIRED")
    if not isinstance(holdout_ids, list): holdout_ids = []; errors.append("HOLDOUT_POPULATION_IDS_REQUIRED")
    if len(set(calibration_ids)) != len(calibration_ids): errors.append("CALIBRATION_POPULATION_ID_DUPLICATE")
    if len(set(holdout_ids)) != len(holdout_ids): errors.append("HOLDOUT_POPULATION_ID_DUPLICATE")
    overlap = sorted(set(calibration_ids) & set(holdout_ids))
    if overlap: errors.append("CALIBRATION_HOLDOUT_LEAKAGE:" + ",".join(overlap))

    plan = package.get("capturePlan")
    if not isinstance(plan, dict): errors.append("CAPTURE_PLAN_REQUIRED"); plan = {}
    if plan.get("rightsManifestId") != rights.get("manifestId"): errors.append("CAPTURE_PLAN_RIGHTS_MANIFEST_ID_MISMATCH")
    if plan.get("rightsManifestSha256") != rights.get("manifestSha256"): errors.append("CAPTURE_PLAN_RIGHTS_MANIFEST_SHA_MISMATCH")
    for field in ("hardwareConfigurationSha256", "referenceDecoderSha256", "clockConfigurationSha256"):
        if not is_sha(plan.get(field)): errors.append(f"CAPTURE_PLAN_{field.upper()}_INVALID")

    slots = plan.get("slots") if isinstance(plan.get("slots"), list) else []
    if len(slots) < 60: errors.append("SLOT_COUNT_BELOW_MINIMUM")
    slot_ids: set[str] = set(); population_ids: set[str] = set(); underlying_ids: set[str] = set()
    cells: dict[tuple[str, str], int] = defaultdict(int)
    slots_by_id: dict[str, dict[str, Any]] = {}
    calibration_set, holdout_set = set(calibration_ids), set(holdout_ids)
    for i, s in enumerate(slots):
        if not isinstance(s, dict): errors.append(f"SLOT[{i}]_OBJECT_REQUIRED"); continue
        sid, pid, cid = s.get("slotId"), s.get("performerId"), s.get("contentId")
        popid, uid = s.get("populationId"), s.get("underlyingPerformanceId")
        cat, role = s.get("category"), s.get("role")
        if not nonempty(sid): errors.append(f"SLOT[{i}]_ID_REQUIRED")
        elif sid in slot_ids: errors.append(f"SLOT[{i}]_ID_DUPLICATE")
        else: slot_ids.add(sid); slots_by_id[sid] = s
        if pid not in pids: errors.append(f"SLOT[{i}]_UNKNOWN_PERFORMER")
        if cid not in cids: errors.append(f"SLOT[{i}]_UNKNOWN_CONTENT")
        if cat not in CATEGORIES: errors.append(f"SLOT[{i}]_CATEGORY_INVALID")
        if role not in ROLES: errors.append(f"SLOT[{i}]_ROLE_INVALID")
        if not nonempty(popid): errors.append(f"SLOT[{i}]_POPULATION_ID_REQUIRED")
        elif popid in population_ids: errors.append(f"SLOT[{i}]_POPULATION_ID_DUPLICATE")
        else: population_ids.add(popid)
        if popid in calibration_set: errors.append(f"SLOT[{i}]_CALIBRATION_HOLDOUT_LEAKAGE")
        if holdout_ids and popid not in holdout_set: errors.append(f"SLOT[{i}]_NOT_IN_FROZEN_HOLDOUT_POPULATION")
        if not nonempty(uid): errors.append(f"SLOT[{i}]_UNDERLYING_PERFORMANCE_ID_REQUIRED")
        elif uid in underlying_ids: errors.append(f"SLOT[{i}]_MULTIPLE_VIEW_INFLATION")
        else: underlying_ids.add(uid)
        views = s.get("views")
        if not isinstance(views, list) or not views: errors.append(f"SLOT[{i}]_VIEWS_REQUIRED")
        elif any(v not in {"evaluated_di", "string_fret_truth", "event_birth_truth"} for v in views):
            errors.append(f"SLOT[{i}]_VIEW_INVALID")
        if pid in pids and cat in CATEGORIES: cells[(pid, cat)] += 1
    for pid in pids:
        for cat in CATEGORIES:
            if cells[(pid, cat)] < 2: errors.append(f"CELL_BELOW_MINIMUM:{pid}:{cat}")

    attempts = package.get("attempts") if isinstance(package.get("attempts"), list) else []
    attempts_by_slot: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    attempt_ids: set[str] = set()
    admitted_rows: list[dict[str, Any]] = []
    for i, a in enumerate(attempts):
        if not isinstance(a, dict): errors.append(f"ATTEMPT[{i}]_OBJECT_REQUIRED"); continue
        aid, sid = a.get("attemptId"), a.get("slotId")
        if not nonempty(aid): errors.append(f"ATTEMPT[{i}]_ID_REQUIRED")
        elif aid in attempt_ids: errors.append(f"ATTEMPT[{i}]_ID_DUPLICATE")
        else: attempt_ids.add(aid)
        if sid not in slot_ids: errors.append(f"ATTEMPT[{i}]_UNKNOWN_SLOT")
        num = a.get("attemptNumber")
        if not isinstance(num, int) or isinstance(num, bool) or num < 1: errors.append(f"ATTEMPT[{i}]_NUMBER_INVALID")
        else: attempts_by_slot[sid].append((i, a))
        if a.get("transportValid") not in (True, False): errors.append(f"ATTEMPT[{i}]_TRANSPORT_VALID_BOOL_REQUIRED")
        if a.get("admitted") not in (True, False): errors.append(f"ATTEMPT[{i}]_ADMITTED_BOOL_REQUIRED")
        if a.get("admitted") is True:
            for f in ("evaluatedDiSha256", "stringFretTruthSha256", "eventBirthTruthSha256", "clockOrSyncEvidenceSha256"):
                if not is_sha(a.get(f)): errors.append(f"ATTEMPT[{i}]_{f.upper()}_INVALID")
            births = a.get("referenceNoteBirthCount")
            if not isinstance(births, int) or isinstance(births, bool) or births < 0:
                errors.append(f"ATTEMPT[{i}]_REFERENCE_NOTE_BIRTH_COUNT_INVALID")
            else:
                slot = slots_by_id.get(sid, {})
                admitted_rows.append({"slotId": sid, "performerId": slot.get("performerId"),
                                      "category": slot.get("category"), "births": births})

    for sid in slot_ids:
        rows = sorted(attempts_by_slot.get(sid, []), key=lambda x: x[1].get("attemptNumber", 10**9))
        nums = [a.get("attemptNumber") for _, a in rows if isinstance(a.get("attemptNumber"), int)]
        if len(nums) != len(set(nums)): errors.append(f"SLOT[{sid}]_ATTEMPT_NUMBER_DUPLICATE")
        valid_rows = [(i, a) for i, a in rows if a.get("transportValid") is True]
        admitted = [(i, a) for i, a in rows if a.get("admitted") is True]
        if valid_rows:
            _, first = valid_rows[0]
            if first.get("admitted") is not True: errors.append(f"SLOT[{sid}]_FIRST_TRANSPORT_VALID_TAKE_NOT_ADMITTED")
            for _, a in admitted:
                if a.get("attemptNumber") != first.get("attemptNumber"):
                    errors.append(f"SLOT[{sid}]_LATER_TAKE_ADMISSION_FORBIDDEN")
        if len(admitted) > 1: errors.append(f"SLOT[{sid}]_MULTIPLE_ADMITTED_TAKES_FORBIDDEN")

    admitted_count = len(admitted_rows)
    if admitted_count < 60: errors.append("ADMITTED_PERFORMANCE_COUNT_BELOW_MINIMUM")
    births_total = sum(r["births"] for r in admitted_rows)
    if births_total < 3000: errors.append("POOLED_REFERENCE_NOTE_BIRTHS_BELOW_MINIMUM")
    births_by_performer: dict[str, int] = defaultdict(int)
    births_by_category: dict[str, int] = defaultdict(int)
    admitted_cell: dict[tuple[str, str], int] = defaultdict(int)
    for r in admitted_rows:
        births_by_performer[r["performerId"]] += r["births"]
        births_by_category[r["category"]] += r["births"]
        admitted_cell[(r["performerId"], r["category"])] += 1
    for pid in pids:
        if births_by_performer[pid] < 300: errors.append(f"PERFORMER_REFERENCE_NOTE_BIRTHS_BELOW_MINIMUM:{pid}")
        for cat in CATEGORIES:
            if admitted_cell[(pid, cat)] < 2: errors.append(f"ADMITTED_CELL_BELOW_MINIMUM:{pid}:{cat}")
    for cat in CATEGORIES:
        if births_by_category[cat] < 400: errors.append(f"CATEGORY_REFERENCE_NOTE_BIRTHS_BELOW_MINIMUM:{cat}")

    errors = sorted(set(errors))
    return {
        "schema": "astra-guitar-fl-stage-b-precapture-validation-v2",
        "contractValid": not errors,
        "captureReady": False,
        "errors": errors,
        "performerCount": len(pids), "contentCount": len(cids), "slotCount": len(slots),
        "admittedPerformanceCount": admitted_count, "pooledReferenceNoteBirthCount": births_total,
        "realCaptureAuthorized": False, "modelInferenceAuthorized": False, "referenceScoringAuthorized": False,
    }

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--package", required=True); ap.add_argument("--output")
    a = ap.parse_args(); result = validate(json.loads(Path(a.package).read_text(encoding="utf-8")))
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\\n"
    if a.output: Path(a.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["contractValid"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
