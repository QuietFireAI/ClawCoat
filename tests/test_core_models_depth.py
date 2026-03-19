# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_models_depth.py
# REM: Depth coverage for core/models.py
# REM: Pure import and structural tests — no database connection required.

import pytest


class TestImports:
    def test_import_user_model(self):
        from core.models import UserModel
        assert UserModel is not None

    def test_import_audit_entry_model(self):
        from core.models import AuditEntryModel
        assert AuditEntryModel is not None

    def test_import_tenant_model(self):
        from core.models import TenantModel
        assert TenantModel is not None

    def test_import_compliance_record_model(self):
        from core.models import ComplianceRecordModel
        assert ComplianceRecordModel is not None

    def test_import_agent_identity_model(self):
        from core.models import AgentIdentityModel
        assert AgentIdentityModel is not None

    def test_import_openclaw_instance_model(self):
        from core.models import OpenClawInstanceModel
        assert OpenClawInstanceModel is not None


class TestTableNames:
    def test_user_model_table(self):
        from core.models import UserModel
        assert UserModel.__tablename__ == "users"

    def test_audit_entry_table(self):
        from core.models import AuditEntryModel
        assert AuditEntryModel.__tablename__ == "audit_entries"

    def test_tenant_table(self):
        from core.models import TenantModel
        assert TenantModel.__tablename__ == "tenants"

    def test_compliance_record_table(self):
        from core.models import ComplianceRecordModel
        assert ComplianceRecordModel.__tablename__ == "compliance_records"

    def test_agent_identity_table(self):
        from core.models import AgentIdentityModel
        assert AgentIdentityModel.__tablename__ == "agent_identities"

    def test_openclaw_instance_table(self):
        from core.models import OpenClawInstanceModel
        assert OpenClawInstanceModel.__tablename__ == "openclaw_instances"


class TestUserModelColumns:
    def test_user_id_is_primary_key(self):
        from core.models import UserModel
        col = UserModel.__table__.c.user_id
        assert col.primary_key is True

    def test_username_is_unique(self):
        from core.models import UserModel
        col = UserModel.__table__.c.username
        assert col.unique is True

    def test_username_not_nullable(self):
        from core.models import UserModel
        col = UserModel.__table__.c.username
        assert col.nullable is False

    def test_email_column_exists(self):
        from core.models import UserModel
        assert "email" in UserModel.__table__.c

    def test_roles_column_exists(self):
        from core.models import UserModel
        assert "roles" in UserModel.__table__.c

    def test_mfa_enabled_default_false(self):
        from core.models import UserModel
        col = UserModel.__table__.c.mfa_enabled
        assert col.default.arg is False

    def test_is_active_default_true(self):
        from core.models import UserModel
        col = UserModel.__table__.c.is_active
        assert col.default.arg is True

    def test_email_verified_default_false(self):
        from core.models import UserModel
        col = UserModel.__table__.c.email_verified
        assert col.default.arg is False


class TestAuditEntryModelColumns:
    def test_sequence_not_nullable(self):
        from core.models import AuditEntryModel
        col = AuditEntryModel.__table__.c.sequence
        assert col.nullable is False

    def test_chain_id_not_nullable(self):
        from core.models import AuditEntryModel
        col = AuditEntryModel.__table__.c.chain_id
        assert col.nullable is False

    def test_message_column_exists(self):
        from core.models import AuditEntryModel
        assert "message" in AuditEntryModel.__table__.c

    def test_entry_hash_column_exists(self):
        from core.models import AuditEntryModel
        assert "entry_hash" in AuditEntryModel.__table__.c

    def test_details_column_exists(self):
        from core.models import AuditEntryModel
        assert "details" in AuditEntryModel.__table__.c


class TestOpenClawInstanceModelColumns:
    def test_instance_id_unique(self):
        from core.models import OpenClawInstanceModel
        col = OpenClawInstanceModel.__table__.c.instance_id
        assert col.unique is True

    def test_trust_level_default_quarantine(self):
        from core.models import OpenClawInstanceModel
        col = OpenClawInstanceModel.__table__.c.trust_level
        assert col.default.arg == "quarantine"

    def test_manners_score_default_1(self):
        from core.models import OpenClawInstanceModel
        col = OpenClawInstanceModel.__table__.c.manners_score
        assert col.default.arg == 1.0

    def test_suspended_default_false(self):
        from core.models import OpenClawInstanceModel
        col = OpenClawInstanceModel.__table__.c.suspended
        assert col.default.arg is False

    def test_action_count_default_0(self):
        from core.models import OpenClawInstanceModel
        col = OpenClawInstanceModel.__table__.c.action_count
        assert col.default.arg == 0

    def test_columns_exist(self):
        from core.models import OpenClawInstanceModel
        for col in ["allowed_tools", "blocked_tools", "api_key_hash", "name"]:
            assert col in OpenClawInstanceModel.__table__.c


class TestAgentIdentityModelColumns:
    def test_did_unique(self):
        from core.models import AgentIdentityModel
        col = AgentIdentityModel.__table__.c.did
        assert col.unique is True

    def test_revoked_default_false(self):
        from core.models import AgentIdentityModel
        col = AgentIdentityModel.__table__.c.revoked
        assert col.default.arg is False

    def test_trust_level_default_quarantine(self):
        from core.models import AgentIdentityModel
        col = AgentIdentityModel.__table__.c.trust_level
        assert col.default.arg == "quarantine"

    def test_public_key_hex_not_nullable(self):
        from core.models import AgentIdentityModel
        col = AgentIdentityModel.__table__.c.public_key_hex
        assert col.nullable is False


class TestComplianceRecordModelColumns:
    def test_record_id_unique(self):
        from core.models import ComplianceRecordModel
        col = ComplianceRecordModel.__table__.c.record_id
        assert col.unique is True

    def test_data_not_nullable(self):
        from core.models import ComplianceRecordModel
        col = ComplianceRecordModel.__table__.c.data
        assert col.nullable is False

    def test_status_default_active(self):
        from core.models import ComplianceRecordModel
        col = ComplianceRecordModel.__table__.c.status
        assert col.default.arg == "active"
