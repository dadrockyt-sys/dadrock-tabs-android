#!/usr/bin/env python3
"""Astra H1 model-free, no-media tensor-shape memory accounting.

Static byte arithmetic for individually identifiable arrays ONLY. It does not
run Torch, inference, VQT, any workflow, or attest peak RSS/runner headroom.
"""
from __future__ import annotations
import argparse
import json

CAPTURE_COUNT = 256
HISTORIC_TOTAL_FRAMES = 1_924_805
HISTORIC_MAX_FRAMES = 23_773
FEATURE_BINS = 192
STRINGS = 6
STATES = 21
CONTEXT = 9
EVAL_CHUNK = 512
TRAIN_SEQUENCE = 200
FLOAT32_BYTES = 4
FLOAT64_BYTES = 8
INT16_BYTES = 2
HOP = 512
SAMPLE_RATE = 22_050
SOURCE_ANCHORS = {
    'evaluation': {'path': 'astra_backend/guitartechs_training_v9/post_v9_output_admission_audit_v1.py',
                   'gitBlob': '8e4cf8a6aa052d0703fc69128a387de8eb2bf6d5'},
    'training': {'path': 'astra_backend/guitartechs_training_v10/h1_pilot_core_v1.py',
                 'gitBlob': '2bf8085b6cd69214d5e2ec198d80c40b35d13875'},
    'sampling': {'path': 'astra_backend/guitartechs_training_v2/train_v2.py',
                 'gitBlob': '4db5add96c58a8e54868ea06dacb1da724675163'},
    'augmentations': {'path': 'astra_backend/guitartechs_training_v9/paired_view.py',
                      'gitBlob': '9b704ea9c5bf153197dfde260c1b995142d062b5'},
    'audioPreparation': {'path': 'astra_backend/guitartechs_real_training/real_training.py',
                         'gitBlob': 'd4a3dd99c4a2c3cda16c10bde1a5dc63f6380254'},
    'preprocessing': {'path': 'astra_backend/tabcnn_runtime/preprocessing.py',
                      'gitBlob': 'e1d251a341b811b1b8e2df97d78b754d3379046b'},
}


def sizes_for_frames(frames: int) -> dict:
    if type(frames) is not int or frames < 200:
        raise ValueError('INVALID_SCALAR_FRAME_LENGTH')
    chunk = min(EVAL_CHUNK, frames)
    return {
        'frames': frames,
        'preparedFloat32FeaturePayloadBytes': FEATURE_BINS * frames * FLOAT32_BYTES,
        'preparedInt16LabelPayloadBytes': STRINGS * frames * INT16_BYTES,
        'paddedEvaluationCqtFloat32Bytes': FEATURE_BINS * (frames + CONTEXT - 1) * FLOAT32_BYTES,
        'fullStateFloat32Bytes': frames * STRINGS * STATES * FLOAT32_BYTES,
        'fullEventFloat32Bytes': frames * STRINGS * FLOAT32_BYTES,
        'singleFullStateFloat64CopyBytes': frames * STRINGS * STATES * FLOAT64_BYTES,
        'oneChunkContiguousInputFloat32Bytes': chunk * FEATURE_BINS * CONTEXT * FLOAT32_BYTES,
        'oneTrainingSequenceInputFloat32Bytes': TRAIN_SEQUENCE * FEATURE_BINS * CONTEXT * FLOAT32_BYTES,
        'twoPairedTrainingSequenceInputPayloadBytes': 2 * TRAIN_SEQUENCE * FEATURE_BINS * CONTEXT * FLOAT32_BYTES,
        'nominalHopEquivalentMonoPcmFloat32Bytes': frames * HOP * FLOAT32_BYTES,
        'nominalPcmPipePlusCopyBytes': 2 * frames * HOP * FLOAT32_BYTES,
        'nonOverlapDisclaimer': 'Every number is an individual allocation or conditional source-shape payload, NOT measured concurrent RSS, physical allocation or a worst-case upper bound.',
    }


def receipt() -> dict:
    s = sizes_for_frames(HISTORIC_MAX_FRAMES)
    return {
        'schema': 'astra-h1-phase16-static-memory-shape-review-v1',
        'acceptedCaptures': CAPTURE_COUNT,
        'historicPreparedTotalFrames': HISTORIC_TOTAL_FRAMES,
        'historicLargestCaptureFrames': HISTORIC_MAX_FRAMES,
        'preparedArrayPayloadAllCapturesBytes': HISTORIC_TOTAL_FRAMES * (FEATURE_BINS * FLOAT32_BYTES + STRINGS * INT16_BYTES),
        'maxCaptureIdentifiableArrayBytes': s,
        'sourceAnchorsFromExistingGitHubReadOnlyInspection': SOURCE_ANCHORS,
        'localPinnedSourceFilesVerifiedByThisModel': False,
        'sourceSemanticNotes': [
            'infer_raw() allocates padded (192,F+8) CQT, (F,6,21) float32 state, (F,6) float32 event, and 512-frame input chunks; it uses inference_mode(), not optimizer.',
            'summarize_capture() includes state.astype(float64), np.clip, log/multiply and entropy intermediates; the exact number and lifetimes of simultaneous buffers are not bounded by this arithmetic.',
            'sequence_windows() builds padded full-capture NumPy data and a contiguous (200,192,9) input per sequence. H1 uses two paired_tensor_views() with clones, gain/tilt/noise intermediates and autograd.',
            'V6/V7/V9 inherit upstream TabCNN convolutional module; upstream package model, Adadelta states, gradients, Torch activations/allocator and librosa VQT workspaces have no verified peak size here.',
            'FFmpeg pipe:1 stdout bytes coexist with np.frombuffer(...).copy() during decode_audio(); nominal hop-equivalent PCM is only a scenario and not actual decoded sample count.',
        ],
        'nominalPcmDerivedFromActualAudioDuration': False,
        'completePeakRamBoundEstablished': False,
        'runnerEffectiveAvailableRamMeasured': False,
        'completePeakDiskBoundEstablished': False,
        'twelveStageH1TimeBoundEstablished': False,
        'modelImported': False,
        'mediaRead': False,
        'launchPermission': False,
        'readiness': 'NO_GO_INSUFFICIENT_EVIDENCE',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frames', type=int, default=HISTORIC_MAX_FRAMES,
                        help='Optional synthetic scalar for per-capture array sizes (never an H1 measurement)')
    args = parser.parse_args()
    result = receipt() if args.frames == HISTORIC_MAX_FRAMES else {
        'schema': 'astra-h1-phase16-static-memory-scenario-v1',
        'scalarScenario': sizes_for_frames(args.frames),
        'realMeasuredPeak': None,
        'launchPermission': False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
