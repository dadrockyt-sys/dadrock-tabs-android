"""Offline SQLite illustration of fail-closed one-use authorization consumption.

NOT a global GitHub Actions store, NOT a launch gate, and NOT an approval.
No workflow, media, model, or network interactions.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{7,127}\Z")


def _connect(database: Path) -> sqlite3.Connection:
    # This demonstration deliberately requires an already-created local directory.
    # It is not suitable for ephemeral, independently provisioned CI runners.
    root = database.parent.resolve(strict=True)
    if database.is_symlink() or database.parent != root or database.name in ("", ".", ".."):
        raise ValueError("UNSAFE_DEMO_DATABASE_PATH")
    connection = sqlite3.connect(str(database), timeout=5, isolation_level=None)
    connection.execute("PRAGMA busy_timeout=5000")
    connection.execute("PRAGMA synchronous=FULL")
    return connection


def reserve_local_once(database: str | Path, authorization_key: str, payload_sha256: str) -> bool:
    """Atomically reserve one scoped identity within ONE SHARED LOCAL DB.

    True is an illustrative reservation, *never* permission to start H1.
    False means already consumed, including same identity/different payload.
    Database corruption/locking errors raise and must fail closed.
    """
    if not isinstance(authorization_key, str) or not _KEY.fullmatch(authorization_key):
        raise ValueError("INVALID_DEMO_AUTHORIZATION_KEY")
    if not isinstance(payload_sha256, str) or not _SHA256.fullmatch(payload_sha256):
        raise ValueError("INVALID_DEMO_PAYLOAD_DIGEST")
    db = Path(database)
    conn = _connect(db)
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("CREATE TABLE IF NOT EXISTS consumed ("
                     "authorization_key TEXT PRIMARY KEY NOT NULL, "
                     "payload_sha256 TEXT NOT NULL, "
                     "status TEXT NOT NULL CHECK(status='consumed_no_retry'))")
        try:
            conn.execute("INSERT INTO consumed VALUES (?, ?, 'consumed_no_retry')",
                         (authorization_key, payload_sha256))
        except sqlite3.IntegrityError:
            conn.execute("ROLLBACK")
            return False
        conn.execute("COMMIT")
        return True
    except BaseException:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def review_status() -> dict:
    """Invariant verdict: a local single-store demo is never global authorization."""
    return {
        "schema": "astra-h1-local-atomic-consumption-demo-v1",
        "localSqliteUniquenessIllustrated": True,
        "sharedPersistentGlobalStoreProvided": False,
        "githubHostedRunnersShareStore": False,
        "independentSecurityReview": "PENDING",
        "launchPermission": False,
    }
