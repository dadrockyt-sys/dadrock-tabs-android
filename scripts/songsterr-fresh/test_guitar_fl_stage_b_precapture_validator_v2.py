#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("v2", HERE / "guitar_fl_stage_b_precapture_validator_v2.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
SHA = "a" * 64

def valid_package():
    documents = []; performers = []; contents = []; slots = []; attempts = []; holdout = []
    for pi in range(6):
        rel, own = f"release-{pi}", f"recording-grant-{pi}"
        documents += [{"documentId": rel, "documentType": "performer_release", "sha256": SHA},
                      {"documentId": own, "documentType": "recording_ownership_use_grant", "sha256": SHA}]
        performers.append({"performerId": f"p{pi}", "releaseDocumentId": rel,
                           "recordingOwnershipUseGrantDocumentId": own,
                           "recordingProductValidationUseGranted": True,
                           "referenceSensorDataUseGranted": True, "internalRetentionGranted": True})
    n = 0
    for pi in range(6):
        for cat in mod.CATEGORIES:
            cid, did = f"content-{pi}-{cat}", f"content-rights-{pi}-{cat}"
            documents.append({"documentId": did, "documentType": "content_rights", "sha256": SHA})
            contents.append({"contentId": cid, "provenanceClass": "original_project_composition",
                             "rightsDocumentId": did, "productValidationUseGranted": True, "protectedSong": False})
            for k in range(2):
                sid, pop, uid = f"slot-{n}", f"holdout-{n}", f"performance-{n}"
                slots.append({"slotId": sid, "populationId": pop, "underlyingPerformanceId": uid,
                              "performerId": f"p{pi}", "contentId": cid, "category": cat,
                              "role": "lead" if k == 0 else "rhythm",
                              "views": ["evaluated_di", "string_fret_truth", "event_birth_truth"]})
                holdout.append(pop)
                attempts.append({"attemptId": f"attempt-{n}-1", "slotId": sid, "attemptNumber": 1,
                                 "transportValid": True, "admitted": True, "referenceNoteBirthCount": 50,
                                 "evaluatedDiSha256": SHA, "stringFretTruthSha256": SHA,
                                 "eventBirthTruthSha256": SHA, "clockOrSyncEvidenceSha256": SHA})
                n += 1
    return {
        "schema": "astra-guitar-fl-stage-b-precapture-package-v2",
        "authority": {k: False for k in (
            "spendingAuthorized", "procurementAuthorized", "performerContactAuthorized", "vendorContactAuthorized",
            "calibrationRecordingAuthorized", "captureAuthorized", "empiricalExecutionAuthorized",
            "modelInferenceAuthorized", "referenceScoringAuthorized")},
        "hardwareReferenceArchitecture": {
            "evaluatedAudioSource": "clean_magnetic_guitar_di",
            "referenceTimingDerivedFromAudioOrModel": False,
            "referencePlanes": {"stringFretState": "independent_physical_string_fret_state",
                                "eventBirth": "independent_excitation_event_birth"},
            "clock": {"mode": "single_shared_hardware_clock"}},
        "rightsManifest": {"manifestId": "rights-v2", "manifestSha256": SHA, "protectedSongsExcluded": True,
                           "documents": documents, "performers": performers, "contents": contents},
        "calibrationPopulationIds": ["cal-1", "cal-2"], "holdoutPopulationIds": holdout,
        "capturePlan": {"rightsManifestId": "rights-v2", "rightsManifestSha256": SHA,
                        "hardwareConfigurationSha256": SHA, "referenceDecoderSha256": SHA,
                        "clockConfigurationSha256": SHA, "slots": slots},
        "attempts": attempts,
    }

class Tests(unittest.TestCase):
    def assert_invalid(self, x, needle):
        r = mod.validate(x); self.assertFalse(r["contractValid"], r)
        self.assertTrue(any(needle in e for e in r["errors"]), r["errors"])

    def test_valid_synthetic_contract_meets_population_and_birth_floors_but_does_not_authorize_capture(self):
        r = mod.validate(valid_package())
        self.assertTrue(r["contractValid"], r); self.assertFalse(r["captureReady"])
        self.assertEqual(r["admittedPerformanceCount"], 60); self.assertEqual(r["pooledReferenceNoteBirthCount"], 3000)
        self.assertFalse(r["realCaptureAuthorized"])

    def test_duplicate_population_identity_fails_closed(self):
        x = valid_package(); x["capturePlan"]["slots"][1]["populationId"] = x["capturePlan"]["slots"][0]["populationId"]
        self.assert_invalid(x, "POPULATION_ID_DUPLICATE")

    def test_calibration_holdout_leakage_fails_closed(self):
        x = valid_package(); x["calibrationPopulationIds"].append(x["holdoutPopulationIds"][0])
        self.assert_invalid(x, "CALIBRATION_HOLDOUT_LEAKAGE")

    def test_multiple_view_inflation_fails_closed(self):
        x = valid_package(); x["capturePlan"]["slots"][1]["underlyingPerformanceId"] = x["capturePlan"]["slots"][0]["underlyingPerformanceId"]
        self.assert_invalid(x, "MULTIPLE_VIEW_INFLATION")

    def test_missing_rights_linkage_fails_closed(self):
        x = valid_package(); x["rightsManifest"]["performers"][0]["releaseDocumentId"] = "missing-doc"
        self.assert_invalid(x, "RELEASEDOCUMENTID_LINK_INVALID")

    def test_missing_reference_plane_fails_closed(self):
        x = valid_package(); x["attempts"][0]["eventBirthTruthSha256"] = None
        self.assert_invalid(x, "EVENTBIRTHTRUTHSHA256_INVALID")

    def test_invalid_role_label_fails_closed(self):
        x = valid_package(); x["capturePlan"]["slots"][0]["role"] = "bass"
        self.assert_invalid(x, "ROLE_INVALID")

    def test_later_take_after_first_transport_valid_take_cannot_be_admitted(self):
        x = valid_package(); a = x["attempts"][0]; a["admitted"] = False
        later = copy.deepcopy(a); later.update({"attemptId": "attempt-later", "attemptNumber": 2, "admitted": True})
        x["attempts"].append(later)
        self.assert_invalid(x, "LATER_TAKE_ADMISSION_FORBIDDEN")

    def test_birth_floor_fails_closed(self):
        x = valid_package(); x["attempts"][0]["referenceNoteBirthCount"] = 0
        self.assert_invalid(x, "POOLED_REFERENCE_NOTE_BIRTHS_BELOW_MINIMUM")

    def test_audio_or_model_derived_reference_timing_forbidden(self):
        x = valid_package(); x["hardwareReferenceArchitecture"]["referenceTimingDerivedFromAudioOrModel"] = True
        self.assert_invalid(x, "AUDIO_OR_MODEL_DERIVED_REFERENCE_TIMING_FORBIDDEN")

    def test_preregistered_sync_mapping_requires_hash_and_hardware_markers_only(self):
        x = valid_package(); x["hardwareReferenceArchitecture"]["clock"] = {"mode": "preregistered_hardware_sync_mapping"}
        self.assert_invalid(x, "CLOCK_SYNC_MAPPING_SHA_REQUIRED")

    def test_any_authority_flip_fails_closed(self):
        for field in valid_package()["authority"]:
            with self.subTest(field=field):
                x = valid_package(); x["authority"][field] = True
                self.assert_invalid(x, "AUTHORITY_")

if __name__ == "__main__": unittest.main()
