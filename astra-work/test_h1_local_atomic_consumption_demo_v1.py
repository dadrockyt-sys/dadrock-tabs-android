"""No-media offline tests. No H1 launch file or repository modifications."""
import concurrent.futures
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest

from h1_local_atomic_consumption_demo_v1 import reserve_local_once, review_status

KEY = 'synthetic-h1-authorization-001'
SHA_A = 'a' * 64
SHA_B = 'b' * 64


class LocalOneUseDemoTests(unittest.TestCase):
    def test_first_reservation_and_duplicate_denial(self):
        with tempfile.TemporaryDirectory() as t:
            db = Path(t) / 'local-demo.sqlite'
            self.assertTrue(reserve_local_once(db, KEY, SHA_A))
            self.assertFalse(reserve_local_once(db, KEY, SHA_A))

    def test_same_id_different_payload_denied(self):
        with tempfile.TemporaryDirectory() as t:
            db = Path(t) / 'local-demo.sqlite'
            self.assertTrue(reserve_local_once(db, KEY, SHA_A))
            self.assertFalse(reserve_local_once(db, KEY, SHA_B))

    def test_many_threads_exactly_one_wins(self):
        with tempfile.TemporaryDirectory() as t:
            db = Path(t) / 'local-demo.sqlite'
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                values = list(pool.map(lambda _: reserve_local_once(db, KEY, SHA_A), range(16)))
            self.assertEqual(sum(values), 1)

    def test_consumption_persists_across_connections(self):
        with tempfile.TemporaryDirectory() as t:
            db = Path(t) / 'local-demo.sqlite'
            self.assertTrue(reserve_local_once(db, KEY, SHA_A))
            connection = sqlite3.connect(db)
            try:
                self.assertEqual(connection.execute('SELECT status FROM consumed').fetchone(),
                                 ('consumed_no_retry',))
            finally:
                connection.close()
            self.assertFalse(reserve_local_once(db, KEY, SHA_A))

    def test_two_independent_databases_both_accept_exposes_missing_globality(self):
        with tempfile.TemporaryDirectory() as t:
            one, two = Path(t) / 'runner-one.sqlite', Path(t) / 'runner-two.sqlite'
            self.assertTrue(reserve_local_once(one, KEY, SHA_A))
            self.assertTrue(reserve_local_once(two, KEY, SHA_A))
            self.assertFalse(review_status()['sharedPersistentGlobalStoreProvided'])

    def test_distinct_keys_are_independent(self):
        with tempfile.TemporaryDirectory() as t:
            db = Path(t) / 'local-demo.sqlite'
            self.assertTrue(reserve_local_once(db, KEY, SHA_A))
            self.assertTrue(reserve_local_once(db, KEY + '-other', SHA_A))

    def test_reject_invalid_identity_and_digest(self):
        with tempfile.TemporaryDirectory() as t:
            db = Path(t) / 'local-demo.sqlite'
            for key, digest in [('x', SHA_A), (KEY, 'bad'), (KEY, 'A' * 64)]:
                with self.assertRaises(ValueError):
                    reserve_local_once(db, key, digest)
            self.assertFalse(db.exists())

    def test_symlink_database_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            target = base / 'target.sqlite'
            target.write_bytes(b'not a sqlite database')
            (base / 'alias.sqlite').symlink_to(target)
            with self.assertRaises(ValueError):
                reserve_local_once(base / 'alias.sqlite', KEY, SHA_A)

    def test_review_never_authorizes_launch(self):
        s = review_status()
        self.assertIs(s['launchPermission'], False)
        self.assertEqual(s['independentSecurityReview'], 'PENDING')
        self.assertIs(s['githubHostedRunnersShareStore'], False)


    def test_git_first_add_in_independent_histories_is_not_global(self):
        # Equivalent to the dormant workflow's rev-list/diff-tree rule,
        # but uses ONLY a synthetic path in disposable local Git repositories.
        def eligible(root):
            def git(*args):
                return subprocess.check_output(['git', '-C', str(root), *args],
                                               text=True).strip()
            git('init', '-q')
            git('config', 'user.name', 'Synthetic Fixture')
            git('config', 'user.email', 'synthetic@example.invalid')
            filename = 'synthetic/receipt.txt'
            (root / 'synthetic').mkdir()
            (root / filename).write_text('not a real H1 launch\n')
            git('add', filename)
            git('commit', '-qm', 'independent synthetic first-add')
            count = git('rev-list', '--count', 'HEAD', '--', filename)
            changed = git('diff-tree', '--no-commit-id', '--name-status',
                          '-r', '--root', 'HEAD', '--', filename)
            return count == '1' and changed == 'A\t' + filename

        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            first = base / 'history-one'
            second = base / 'history-two'
            first.mkdir()
            second.mkdir()
            self.assertTrue(eligible(first))
            self.assertTrue(eligible(second))
            # Each history looks like a first-add, but they cannot jointly
            # establish globally unique consumption of an authorization.
            self.assertFalse(review_status()['launchPermission'])


if __name__ == '__main__':
    unittest.main()
