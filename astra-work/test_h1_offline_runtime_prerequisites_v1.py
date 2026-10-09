"""Synthetic-only tests for read-only H1 runtime prerequisite audit."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import tempfile
import unittest

from h1_offline_runtime_prerequisites_v1 import (
    EXPECTED, GENERATED_INIT, UPSTREAM_BLOBS,
    blob_sha, inspect_upstream, local_imported_versions, read_exact_file, review, version_report,
)


class RuntimePrerequisiteTests(unittest.TestCase):
    def good_versions(self):
        return version_report(dict(EXPECTED), cuda_available=False)

    def test_exact_pins_are_accepted_as_local_only(self):
        result = self.good_versions()
        self.assertTrue(result["versionsAndCpuMatch"])
        self.assertFalse(review(result, {"allSourcesAndInitsMatch": True})["launchPermission"])
        self.assertFalse(review(result, {"allSourcesAndInitsMatch": True})["fullModelParityExecuted"])
        self.assertEqual(review(result, {"allSourcesAndInitsMatch": True})["status"],
                         "LOCAL_IDENTITIES_ONLY_REVIEW_REQUIRED")

    def test_torch_version_str_subclass_is_recognized(self):
        # Actual torch uses a TorchVersion object, a str subclass.
        class TorchVersion(str):
            pass
        torch = SimpleNamespace(__version__=TorchVersion('1.11.0+cpu'),
                                cuda=SimpleNamespace(is_available=lambda: False))
        numpy = SimpleNamespace(__version__='1.21.6')
        with patch('h1_offline_runtime_prerequisites_v1.importlib.import_module',
                   side_effect=lambda name: {'torch': torch, 'numpy': numpy}[name]):
            result = local_imported_versions()
        self.assertEqual(result['observed']['torch'], '1.11.0+cpu')
        self.assertNotIn('torch', result['importErrors'])

    def test_str_subclass_matches_exact_frozen_pin(self):
        class TorchVersion(str):
            pass
        observed = dict(EXPECTED, torch=TorchVersion('1.11.0+cpu'))
        self.assertTrue(version_report(observed, cuda_available=False)['versionsAndCpuMatch'])

    def test_each_non_frozen_version_fails_closed(self):
        for key, wrong in (("python", "3.13.5"), ("torch", "2.10.0+cpu"), ("numpy", "2.3.5")):
            with self.subTest(key=key):
                versions = dict(EXPECTED, **{key: wrong})
                self.assertFalse(version_report(versions, cuda_available=False)["versionsAndCpuMatch"])

    def test_installed_version_alias_is_not_accepted(self):
        self.assertFalse(version_report(dict(EXPECTED, torch="1.11.0"), cuda_available=False)["versionsAndCpuMatch"])

    def test_cuda_or_missing_device_status_blocks_local_match(self):
        for value in (True, None):
            with self.subTest(cuda=value):
                self.assertFalse(version_report(dict(EXPECTED), cuda_available=value)["versionsAndCpuMatch"])

    def test_incomplete_version_set_rejected(self):
        with self.assertRaisesRegex(ValueError, "VERSION_KEYS_MISSING_OR_EXTRA"):
            version_report({"torch": "1.11.0+cpu"}, cuda_available=False)

    def test_unstaged_upstream_does_not_pass(self):
        result = review(self.good_versions(), None)
        self.assertFalse(result["prerequisitesLocallyMatched"])
        self.assertFalse(result["launchPermission"])

    def make_fake_tree(self, root):
        sources = {}
        for name in UPSTREAM_BLOBS:
            fake = ("synthetic-only-" + name).encode()
            file = root / "amt_tools" / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(fake)
            sources[name] = blob_sha(fake)
        for name, expected in GENERATED_INIT.items():
            file = root / "amt_tools" / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(expected)
        return sources

    def test_fake_upstream_all_bytes_match_fixture_not_real_pins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = self.make_fake_tree(root)
            result = inspect_upstream(root, expected_blobs=expected)
            self.assertTrue(result["allSourcesAndInitsMatch"])
            self.assertEqual(result["expectedUpstreamCount"], 4)
            # Production pins correctly reject these dummy fixture bytes.
            self.assertFalse(inspect_upstream(root)["allSourcesAndInitsMatch"])

    def test_upstream_hash_tamper_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = self.make_fake_tree(root)
            p = root / "amt_tools" / "models/common.py"
            p.write_bytes(p.read_bytes() + b"tamper")
            self.assertFalse(inspect_upstream(root, expected_blobs=expected)["allSourcesAndInitsMatch"])

    def test_generated_initializer_tamper_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = self.make_fake_tree(root)
            (root / "amt_tools" / "tools/__init__.py").write_bytes(b"different")
            self.assertFalse(inspect_upstream(root, expected_blobs=expected)["allSourcesAndInitsMatch"])

    def test_symlink_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = self.make_fake_tree(root)
            f = root / "amt_tools" / "models/common.py"
            payload = f.read_bytes()
            f.unlink()
            target = root / "target.py"
            target.write_bytes(payload)
            f.symlink_to(target)
            with self.assertRaisesRegex(RuntimeError, "UPSTREAM_PATH_SYMLINK"):
                inspect_upstream(root, expected_blobs=expected)

    def test_symlink_parent_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = self.make_fake_tree(root)
            p = root / "amt_tools" / "models"
            p.rename(root / "actual-models")
            p.symlink_to(root / "actual-models", target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "UPSTREAM_PATH_SYMLINK"):
                inspect_upstream(root, expected_blobs=expected)

    def test_missing_upstream_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = self.make_fake_tree(root)
            (root / "amt_tools" / "tools/constants.py").unlink()
            with self.assertRaisesRegex(RuntimeError, "UPSTREAM_FILE_MISSING"):
                inspect_upstream(root, expected_blobs=expected)

    def test_relative_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "INVALID_RELATIVE_PATH"):
                read_exact_file(Path(tmp), "../escapes")


if __name__ == "__main__":
    unittest.main(verbosity=2)
