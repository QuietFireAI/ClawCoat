# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_database_depth.py
# REM: Depth coverage for core/database.py
# REM: Tests: init_db, check_db_health, get_db — both success and failure paths.

import pytest
from unittest.mock import MagicMock, patch

# REM: Skip entire file if sqlalchemy is not installed (local dev env without full deps)
pytest.importorskip("sqlalchemy", reason="sqlalchemy required for database depth tests")


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE-LEVEL OBJECTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestDatabaseModuleObjects:
    def test_base_imported(self):
        from core.database import Base
        assert Base is not None

    def test_session_local_imported(self):
        from core.database import SessionLocal
        assert SessionLocal is not None

    def test_engine_imported(self):
        from core.database import engine
        assert engine is not None


# ═══════════════════════════════════════════════════════════════════════════════
# get_db
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetDb:
    def test_get_db_yields_and_closes(self):
        from core.database import get_db
        mock_session = MagicMock()
        with patch("core.database.SessionLocal", return_value=mock_session):
            gen = get_db()
            db = next(gen)
            assert db is mock_session
            # REM: Exhaust generator (triggers finally block → db.close())
            try:
                next(gen)
            except StopIteration:
                pass
        mock_session.close.assert_called_once()

    def test_get_db_closes_on_exception(self):
        from core.database import get_db
        mock_session = MagicMock()
        with patch("core.database.SessionLocal", return_value=mock_session):
            gen = get_db()
            next(gen)
            # REM: gen.throw() propagates the exception after finally runs
            try:
                gen.throw(RuntimeError("simulated error"))
            except RuntimeError:
                pass
        mock_session.close.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# init_db
# ═══════════════════════════════════════════════════════════════════════════════

class TestInitDb:
    def test_init_db_calls_create_all(self):
        from core.database import init_db, Base, engine
        with patch.object(Base.metadata, "create_all") as mock_create:
            init_db()
        mock_create.assert_called_once_with(bind=engine)

    def test_init_db_catches_exception(self):
        """REM: When postgres is unavailable, init_db logs warning and does not raise."""
        from core.database import init_db, Base
        with patch.object(Base.metadata, "create_all", side_effect=Exception("no db")):
            # REM: Should NOT raise — graceful failure
            init_db()


# ═══════════════════════════════════════════════════════════════════════════════
# check_db_health
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckDbHealth:
    def test_returns_true_when_healthy(self):
        from core.database import check_db_health
        mock_session = MagicMock()
        with patch("core.database.SessionLocal", return_value=mock_session):
            result = check_db_health()
        assert result is True
        mock_session.close.assert_called_once()

    def test_returns_false_when_unhealthy(self):
        from core.database import check_db_health
        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception("connection refused")
        with patch("core.database.SessionLocal", return_value=mock_session):
            result = check_db_health()
        assert result is False
