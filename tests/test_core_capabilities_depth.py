# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_capabilities_depth.py
# REM: Depth coverage for core/capabilities.py
# REM: Enums, Capability, CapabilitySet, CapabilityEnforcer — all pure in-memory.

import pytest

from core.capabilities import (
    CAPABILITY_PROFILES,
    ActionType,
    Capability,
    CapabilityEnforcer,
    CapabilitySet,
    ResourceType,
)


# ═══════════════════════════════════════════════════════════════════════════════
# ResourceType enum
# ═══════════════════════════════════════════════════════════════════════════════

class TestResourceTypeEnum:
    def test_filesystem(self):
        assert ResourceType.FILESYSTEM == "filesystem"

    def test_external(self):
        assert ResourceType.EXTERNAL == "external"

    def test_mqtt(self):
        assert ResourceType.MQTT == "mqtt"

    def test_ollama(self):
        assert ResourceType.OLLAMA == "ollama"

    def test_redis(self):
        assert ResourceType.REDIS == "redis"

    def test_agent(self):
        assert ResourceType.AGENT == "agent"

    def test_all_unique(self):
        vals = [r.value for r in ResourceType]
        assert len(vals) == len(set(vals))


# ═══════════════════════════════════════════════════════════════════════════════
# ActionType enum
# ═══════════════════════════════════════════════════════════════════════════════

class TestActionTypeEnum:
    def test_read(self):
        assert ActionType.READ == "read"

    def test_write(self):
        assert ActionType.WRITE == "write"

    def test_execute(self):
        assert ActionType.EXECUTE == "execute"

    def test_publish(self):
        assert ActionType.PUBLISH == "publish"

    def test_subscribe(self):
        assert ActionType.SUBSCRIBE == "subscribe"

    def test_manage(self):
        assert ActionType.MANAGE == "manage"

    def test_none(self):
        assert ActionType.NONE == "none"

    def test_all_unique(self):
        vals = [a.value for a in ActionType]
        assert len(vals) == len(set(vals))


# ═══════════════════════════════════════════════════════════════════════════════
# Capability.matches()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCapabilityMatches:
    def test_resource_mismatch_returns_false(self):
        cap = Capability(resource=ResourceType.FILESYSTEM, action=ActionType.READ, scope="*")
        assert cap.matches(ResourceType.EXTERNAL, ActionType.READ, "any") is False

    def test_action_none_returns_false(self):
        cap = Capability(resource=ResourceType.EXTERNAL, action=ActionType.NONE, scope="*")
        assert cap.matches(ResourceType.EXTERNAL, ActionType.NONE, "any") is False

    def test_action_mismatch_returns_false(self):
        cap = Capability(resource=ResourceType.FILESYSTEM, action=ActionType.READ, scope="*")
        assert cap.matches(ResourceType.FILESYSTEM, ActionType.WRITE, "/data/file") is False

    def test_wildcard_scope_matches_any(self):
        cap = Capability(resource=ResourceType.FILESYSTEM, action=ActionType.READ, scope="*")
        assert cap.matches(ResourceType.FILESYSTEM, ActionType.READ, "/any/path") is True

    def test_glob_scope_matches_pattern(self):
        cap = Capability(resource=ResourceType.FILESYSTEM, action=ActionType.READ, scope="/data/*")
        assert cap.matches(ResourceType.FILESYSTEM, ActionType.READ, "/data/file.txt") is True

    def test_glob_scope_no_match(self):
        cap = Capability(resource=ResourceType.FILESYSTEM, action=ActionType.READ, scope="/data/*")
        assert cap.matches(ResourceType.FILESYSTEM, ActionType.READ, "/other/file.txt") is False

    def test_exact_scope_match(self):
        cap = Capability(resource=ResourceType.FILESYSTEM, action=ActionType.READ, scope="/specific/file.txt")
        assert cap.matches(ResourceType.FILESYSTEM, ActionType.READ, "/specific/file.txt") is True

    def test_exact_scope_no_match(self):
        cap = Capability(resource=ResourceType.FILESYSTEM, action=ActionType.READ, scope="/specific/file.txt")
        assert cap.matches(ResourceType.FILESYSTEM, ActionType.READ, "/specific/other.txt") is False

    def test_mqtt_subscribe_match(self):
        cap = Capability(resource=ResourceType.MQTT, action=ActionType.SUBSCRIBE, scope="telsonbase/*")
        assert cap.matches(ResourceType.MQTT, ActionType.SUBSCRIBE, "telsonbase/events") is True


# ═══════════════════════════════════════════════════════════════════════════════
# Capability.from_string()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCapabilityFromString:
    def test_parse_standard_format(self):
        cap = Capability.from_string("filesystem.read:/data/*")
        assert cap.resource == ResourceType.FILESYSTEM
        assert cap.action == ActionType.READ
        assert cap.scope == "/data/*"

    def test_parse_external(self):
        cap = Capability.from_string("external.write:api.example.com")
        assert cap.resource == ResourceType.EXTERNAL
        assert cap.action == ActionType.WRITE
        assert cap.scope == "api.example.com"

    def test_parse_none_format(self):
        cap = Capability.from_string("external.none")
        assert cap.resource == ResourceType.EXTERNAL
        assert cap.action == ActionType.NONE
        assert cap.scope == "*"

    def test_parse_ollama_execute(self):
        cap = Capability.from_string("ollama.execute:*")
        assert cap.resource == ResourceType.OLLAMA
        assert cap.action == ActionType.EXECUTE

    def test_invalid_format_raises_value_error(self):
        with pytest.raises(ValueError):
            Capability.from_string("invalid-format")

    def test_invalid_resource_raises(self):
        with pytest.raises(Exception):
            Capability.from_string("unknown.read:/path")

    def test_invalid_action_raises(self):
        with pytest.raises(Exception):
            Capability.from_string("filesystem.jump:/path")


# ═══════════════════════════════════════════════════════════════════════════════
# Capability.__str__()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCapabilityStr:
    def test_str_format(self):
        cap = Capability(resource=ResourceType.FILESYSTEM, action=ActionType.READ, scope="/data/*")
        assert str(cap) == "filesystem.read:/data/*"

    def test_str_includes_resource(self):
        cap = Capability(resource=ResourceType.EXTERNAL, action=ActionType.WRITE, scope="api.example.com")
        assert "external" in str(cap)

    def test_str_includes_action(self):
        cap = Capability(resource=ResourceType.FILESYSTEM, action=ActionType.WRITE, scope="*")
        assert "write" in str(cap)

    def test_str_includes_scope(self):
        cap = Capability(resource=ResourceType.MQTT, action=ActionType.PUBLISH, scope="events/*")
        assert "events/*" in str(cap)


# ═══════════════════════════════════════════════════════════════════════════════
# CapabilitySet.permits()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCapabilitySetPermits:
    def test_no_rules_default_deny(self):
        cs = CapabilitySet(allow=[], deny=[])
        assert cs.permits(ResourceType.FILESYSTEM, ActionType.READ, "/data/file") is False

    def test_allow_rule_grants_access(self):
        cs = CapabilitySet.from_strings(["filesystem.read:/data/*"])
        assert cs.permits(ResourceType.FILESYSTEM, ActionType.READ, "/data/file.txt") is True

    def test_deny_rule_blocks_matching_access(self):
        cs = CapabilitySet.from_strings([
            "filesystem.read:/data/*",
            "!filesystem.read:/data/secret.txt"
        ])
        # Deny takes precedence
        assert cs.permits(ResourceType.FILESYSTEM, ActionType.READ, "/data/secret.txt") is False

    def test_deny_does_not_block_non_matching(self):
        cs = CapabilitySet.from_strings([
            "filesystem.read:/data/*",
            "!filesystem.read:/data/secret.txt"
        ])
        assert cs.permits(ResourceType.FILESYSTEM, ActionType.READ, "/data/other.txt") is True

    def test_deny_is_action_specific(self):
        # Deny only for WRITE, allow READ
        cs = CapabilitySet.from_strings(["filesystem.read:/data/*"])
        assert cs.permits(ResourceType.FILESYSTEM, ActionType.WRITE, "/data/file.txt") is False

    def test_wildcard_scope_grants_all(self):
        cs = CapabilitySet.from_strings(["filesystem.read:*"])
        assert cs.permits(ResourceType.FILESYSTEM, ActionType.READ, "/any/path/at/all") is True

    def test_multiple_allow_rules(self):
        cs = CapabilitySet.from_strings([
            "filesystem.read:/data/*",
            "external.read:api.example.com"
        ])
        assert cs.permits(ResourceType.EXTERNAL, ActionType.READ, "api.example.com") is True
        assert cs.permits(ResourceType.FILESYSTEM, ActionType.READ, "/data/file") is True


# ═══════════════════════════════════════════════════════════════════════════════
# CapabilitySet.from_strings()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCapabilitySetFromStrings:
    def test_parses_allow_rules(self):
        cs = CapabilitySet.from_strings(["filesystem.read:/data/*"])
        assert len(cs.allow) == 1
        assert len(cs.deny) == 0

    def test_parses_deny_rules_with_prefix(self):
        cs = CapabilitySet.from_strings(["!filesystem.read:/data/secret"])
        assert len(cs.deny) == 1
        assert len(cs.allow) == 0

    def test_mixed_allow_and_deny(self):
        cs = CapabilitySet.from_strings([
            "filesystem.read:/data/*",
            "!filesystem.read:/data/secret",
        ])
        assert len(cs.allow) == 1
        assert len(cs.deny) == 1

    def test_empty_list(self):
        cs = CapabilitySet.from_strings([])
        assert cs.allow == []
        assert cs.deny == []

    def test_research_profile_has_deny_rule(self):
        cs = CapabilitySet.from_strings(CAPABILITY_PROFILES["research_agent"])
        assert len(cs.deny) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# CapabilityEnforcer
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def enforcer():
    return CapabilityEnforcer()


class TestCapabilityEnforcerRegister:
    def test_register_agent_stores_capability_set(self, enforcer):
        enforcer.register_agent("agent-001", ["filesystem.read:/data/*"])
        assert enforcer.get_agent_capabilities("agent-001") is not None

    def test_get_capabilities_unknown_returns_none(self, enforcer):
        assert enforcer.get_agent_capabilities("unknown") is None

    def test_list_agents_empty_initially(self, enforcer):
        assert enforcer.list_agents() == []

    def test_list_agents_after_register(self, enforcer):
        enforcer.register_agent("agent-001", ["filesystem.read:/data/*"])
        assert "agent-001" in enforcer.list_agents()

    def test_multiple_agents_listed(self, enforcer):
        enforcer.register_agent("agent-001", ["filesystem.read:/data/*"])
        enforcer.register_agent("agent-002", ["external.read:api.example.com"])
        agents = enforcer.list_agents()
        assert "agent-001" in agents
        assert "agent-002" in agents


class TestCapabilityEnforcerCheckPermission:
    def test_unknown_agent_denied(self, enforcer):
        result = enforcer.check_permission(
            "unknown-agent",
            ResourceType.FILESYSTEM,
            ActionType.READ,
            "/data/file"
        )
        assert result is False

    def test_permitted_access_returns_true(self, enforcer):
        enforcer.register_agent("agent-001", ["filesystem.read:/data/*"])
        result = enforcer.check_permission(
            "agent-001",
            ResourceType.FILESYSTEM,
            ActionType.READ,
            "/data/file.txt"
        )
        assert result is True

    def test_denied_access_returns_false(self, enforcer):
        enforcer.register_agent("agent-001", ["filesystem.read:/data/*"])
        result = enforcer.check_permission(
            "agent-001",
            ResourceType.FILESYSTEM,
            ActionType.WRITE,
            "/data/file.txt"
        )
        assert result is False

    def test_deny_rule_blocks_permission(self, enforcer):
        enforcer.register_agent("agent-001", [
            "filesystem.read:/data/*",
            "!filesystem.read:/data/secret.txt"
        ])
        result = enforcer.check_permission(
            "agent-001",
            ResourceType.FILESYSTEM,
            ActionType.READ,
            "/data/secret.txt"
        )
        assert result is False

    def test_external_none_denies_all_external(self, enforcer):
        enforcer.register_agent("backup", CAPABILITY_PROFILES["backup_agent"])
        result = enforcer.check_permission(
            "backup",
            ResourceType.EXTERNAL,
            ActionType.READ,
            "api.example.com"
        )
        assert result is False

    def test_returns_bool(self, enforcer):
        enforcer.register_agent("agent-001", ["filesystem.read:/data/*"])
        result = enforcer.check_permission(
            "agent-001", ResourceType.FILESYSTEM, ActionType.READ, "/data/x"
        )
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════════════════════════
# CAPABILITY_PROFILES
# ═══════════════════════════════════════════════════════════════════════════════

class TestCapabilityProfiles:
    def test_backup_agent_profile_exists(self):
        assert "backup_agent" in CAPABILITY_PROFILES

    def test_research_agent_profile_exists(self):
        assert "research_agent" in CAPABILITY_PROFILES

    def test_orchestrator_profile_exists(self):
        assert "orchestrator" in CAPABILITY_PROFILES

    def test_backup_agent_cannot_access_external(self, enforcer):
        enforcer.register_agent("backup", CAPABILITY_PROFILES["backup_agent"])
        # external.none → no external reads
        result = enforcer.check_permission(
            "backup", ResourceType.EXTERNAL, ActionType.READ, "example.com"
        )
        assert result is False

    def test_backup_agent_can_read_data(self, enforcer):
        enforcer.register_agent("backup", CAPABILITY_PROFILES["backup_agent"])
        result = enforcer.check_permission(
            "backup", ResourceType.FILESYSTEM, ActionType.READ, "/data/file"
        )
        assert result is True

    def test_backup_agent_can_write_backups(self, enforcer):
        enforcer.register_agent("backup", CAPABILITY_PROFILES["backup_agent"])
        result = enforcer.check_permission(
            "backup", ResourceType.FILESYSTEM, ActionType.WRITE, "/app/backups/backup.tar.gz"
        )
        assert result is True
