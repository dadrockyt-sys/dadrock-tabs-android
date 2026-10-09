"""Synthetic no-network tests of canonical prepared-array contract."""
import tempfile
from pathlib import Path
import unittest

import numpy as np

from guitartechs_training_v10.h1_prepared_array_guard_v1 import verify_prepared_pair


class PreparedArrayGuardTests(unittest.TestCase):
    def make_pair(self, root, frames=4200):
        x = root / 'features.npy'
        y = root / 'labels.npy'
        np.save(x, np.zeros((192, frames), dtype=np.float32), allow_pickle=False)
        labels = np.full((6, frames), -1, dtype=np.int16)
        labels[0, 10:20] = 3
        labels[1, 200:215] = -100
        np.save(y, labels, allow_pickle=False)
        return x, y

    def test_valid_synthetic_pair_two_chunks(self):
        with tempfile.TemporaryDirectory() as name:
            x, y = self.make_pair(Path(name))
            self.assertEqual(verify_prepared_pair(x, y, 4200)['verifiedFrames'], 4200)

    def test_reject_feature_dtype_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            x, y = self.make_pair(root)
            np.save(x, np.zeros((192, 4200), dtype=np.float64), allow_pickle=False)
            with self.assertRaisesRegex(RuntimeError, 'H1_PREPARED_DTYPE_MISMATCH'):
                verify_prepared_pair(x, y, 4200)
            self.make_pair(root)
            bad = np.load(x, mmap_mode='r+')
            bad[0, 4199] = float('nan')
            bad.flush()
            with self.assertRaisesRegex(RuntimeError, 'H1_PREPARED_NONFINITE_FEATURE'):
                verify_prepared_pair(x, y, 4200)

    def test_reject_invalid_labels_and_dtype(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            x, y = self.make_pair(root)
            labels = np.load(y, mmap_mode='r+')
            labels[5, 4098] = 20
            labels.flush()
            with self.assertRaisesRegex(RuntimeError, 'H1_PREPARED_INVALID_LABEL_CLASS'):
                verify_prepared_pair(x, y, 4200)
            self.make_pair(root)
            np.save(y, np.zeros((6, 4200), dtype=np.int32), allow_pickle=False)
            with self.assertRaisesRegex(RuntimeError, 'H1_PREPARED_DTYPE_MISMATCH'):
                verify_prepared_pair(x, y, 4200)

    def test_reject_shapes_frames_and_bad_npy(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            x, y = self.make_pair(root)
            with self.assertRaisesRegex(RuntimeError, 'H1_PREPARED_SHAPE_MISMATCH'):
                verify_prepared_pair(x, y, 4201)
            with self.assertRaisesRegex(RuntimeError, 'H1_PREPARED_FRAME_COUNT_INVALID'):
                verify_prepared_pair(x, y, True)
            x.write_bytes(b'not an npy')
            with self.assertRaisesRegex(RuntimeError, 'H1_PREPARED_NPY_DECODE_ERROR'):
                verify_prepared_pair(x, y, 4200)


if __name__ == '__main__':
    unittest.main()
