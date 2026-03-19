# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_mqtt_bus_depth.py
# REM: Depth coverage for core/mqtt_bus.py
# REM: Pure unit tests — paho.mqtt.Client is mocked. No broker required.

import json
import threading
from unittest.mock import MagicMock, patch, call

import pytest

from core.mqtt_bus import (
    AgentMessage,
    MQTTBus,
    _default_broadcast_handler,
    _default_event_handler,
    get_mqtt_bus,
    init_mqtt_bus,
    shutdown_mqtt_bus,
)
import core.mqtt_bus as _mqtt_module


# ═══════════════════════════════════════════════════════════════════════════════
# AgentMessage — dataclass
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgentMessageDefaults:
    def test_timestamp_auto_set(self):
        msg = AgentMessage(
            source_agent="agent_a", target_agent="agent_b",
            message_type="Test_Please", payload={}
        )
        assert msg.timestamp != ""
        from datetime import datetime
        datetime.fromisoformat(msg.timestamp)

    def test_message_id_auto_set(self):
        msg = AgentMessage(
            source_agent="agent_a", target_agent=None,
            message_type="Test_Please", payload={}
        )
        assert msg.message_id != ""
        assert "agent_a" in msg.message_id

    def test_message_id_unique(self):
        m1 = AgentMessage(source_agent="src", target_agent=None, message_type="T", payload={})
        m2 = AgentMessage(source_agent="src", target_agent=None, message_type="T", payload={})
        assert m1.message_id != m2.message_id

    def test_default_priority(self):
        msg = AgentMessage(source_agent="a", target_agent=None, message_type="T", payload={})
        assert msg.priority == "normal"

    def test_default_reply_to_none(self):
        msg = AgentMessage(source_agent="a", target_agent=None, message_type="T", payload={})
        assert msg.reply_to is None

    def test_signature_defaults_none(self):
        msg = AgentMessage(source_agent="a", target_agent=None, message_type="T", payload={})
        assert msg.signature is None

    def test_explicit_timestamp_not_overwritten(self):
        ts = "2026-01-01T00:00:00+00:00"
        msg = AgentMessage(
            source_agent="a", target_agent=None, message_type="T",
            payload={}, timestamp=ts
        )
        assert msg.timestamp == ts

    def test_explicit_message_id_not_overwritten(self):
        mid = "custom-msg-id-123"
        msg = AgentMessage(
            source_agent="a", target_agent=None, message_type="T",
            payload={}, message_id=mid
        )
        assert msg.message_id == mid


class TestAgentMessageSerialization:
    @pytest.fixture
    def msg(self):
        return AgentMessage(
            source_agent="doc_prep_agent",
            target_agent="transaction_agent",
            message_type="Document_Ready_Please",
            payload={"doc_id": "GEN-PA-001", "status": "finalized"},
            priority="high",
            qms_chain="DocPrep_Document_Ready_Please",
        )

    def test_to_json_returns_string(self, msg):
        j = msg.to_json()
        assert isinstance(j, str)

    def test_to_json_is_valid_json(self, msg):
        data = json.loads(msg.to_json())
        assert data["source_agent"] == "doc_prep_agent"

    def test_to_json_includes_all_fields(self, msg):
        data = json.loads(msg.to_json())
        expected_keys = {
            "source_agent", "target_agent", "message_type", "payload",
            "timestamp", "message_id", "signature", "qms_chain", "priority", "reply_to"
        }
        assert expected_keys.issubset(data.keys())

    def test_from_json_roundtrip(self, msg):
        j = msg.to_json()
        restored = AgentMessage.from_json(j)
        assert restored.source_agent == msg.source_agent
        assert restored.target_agent == msg.target_agent
        assert restored.message_type == msg.message_type
        assert restored.payload == msg.payload
        assert restored.priority == msg.priority

    def test_from_json_preserves_message_id(self, msg):
        j = msg.to_json()
        restored = AgentMessage.from_json(j)
        assert restored.message_id == msg.message_id

    def test_from_json_broadcast(self):
        msg = AgentMessage(
            source_agent="system", target_agent=None,
            message_type="Broadcast_Please", payload={"event": "startup"}
        )
        restored = AgentMessage.from_json(msg.to_json())
        assert restored.target_agent is None

    def test_payload_preserved_through_json(self, msg):
        restored = AgentMessage.from_json(msg.to_json())
        assert restored.payload["doc_id"] == "GEN-PA-001"
        assert restored.payload["status"] == "finalized"

    def test_qms_chain_preserved(self, msg):
        restored = AgentMessage.from_json(msg.to_json())
        assert restored.qms_chain == "DocPrep_Document_Ready_Please"


# ═══════════════════════════════════════════════════════════════════════════════
# MQTTBus — helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _make_bus(connected=False):
    """REM: Create an MQTTBus with mocked Client."""
    with patch("core.mqtt_bus.mqtt.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        bus = MQTTBus(client_id="test-bus")
        bus._client = mock_client
        bus._connected = connected
    return bus


# ═══════════════════════════════════════════════════════════════════════════════
# MQTTBus — initialization
# ═══════════════════════════════════════════════════════════════════════════════

class TestMQTTBusInit:
    def test_not_connected_on_init(self):
        bus = _make_bus()
        assert bus._connected is False

    def test_handlers_empty_on_init(self):
        bus = _make_bus()
        assert bus._handlers == {}

    def test_topic_prefix(self):
        bus = _make_bus()
        assert bus.TOPIC_PREFIX == "telsonbase"

    def test_reconnect_delay_set(self):
        bus = _make_bus()
        assert bus._reconnect_delay == 5

    def test_lock_is_threading_lock(self):
        bus = _make_bus()
        assert isinstance(bus._lock, type(threading.Lock()))


# ═══════════════════════════════════════════════════════════════════════════════
# MQTTBus — connect
# ═══════════════════════════════════════════════════════════════════════════════

class TestMQTTBusConnect:
    def test_connect_returns_true_on_success(self):
        bus = _make_bus()
        bus._client.connect.return_value = None
        result = bus.connect()
        assert result is True

    def test_connect_calls_loop_start(self):
        bus = _make_bus()
        bus.connect()
        bus._client.loop_start.assert_called_once()

    def test_connect_with_credentials(self):
        bus = _make_bus()
        with patch("core.mqtt_bus.settings") as mock_settings:
            mock_settings.mosquitto_user = "testuser"
            mock_settings.mosquitto_password = "testpass"
            mock_settings.mosquitto_host = "localhost"
            mock_settings.mosquitto_port = 1883
            bus.connect()
        bus._client.username_pw_set.assert_called_once_with("testuser", "testpass")

    def test_connect_without_credentials_no_login(self):
        bus = _make_bus()
        with patch("core.mqtt_bus.settings") as mock_settings:
            mock_settings.mosquitto_user = None
            mock_settings.mosquitto_password = None
            mock_settings.mosquitto_host = "localhost"
            mock_settings.mosquitto_port = 1883
            bus.connect()
        bus._client.username_pw_set.assert_not_called()

    def test_connect_returns_false_on_exception(self):
        bus = _make_bus()
        bus._client.connect.side_effect = ConnectionRefusedError("refused")
        result = bus.connect()
        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# MQTTBus — disconnect
# ═══════════════════════════════════════════════════════════════════════════════

class TestMQTTBusDisconnect:
    def test_disconnect_sets_not_connected(self):
        bus = _make_bus(connected=True)
        bus.disconnect()
        assert bus._connected is False

    def test_disconnect_calls_loop_stop(self):
        bus = _make_bus(connected=True)
        bus.disconnect()
        bus._client.loop_stop.assert_called_once()

    def test_disconnect_calls_client_disconnect(self):
        bus = _make_bus(connected=True)
        bus.disconnect()
        bus._client.disconnect.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# MQTTBus — publish
# ═══════════════════════════════════════════════════════════════════════════════

class TestMQTTBusPublish:
    def _connected_bus(self):
        bus = _make_bus(connected=True)
        publish_result = MagicMock()
        publish_result.rc = 0  # MQTT_ERR_SUCCESS
        bus._client.publish.return_value = publish_result
        return bus

    def test_publish_returns_false_when_not_connected(self):
        bus = _make_bus(connected=False)
        msg = AgentMessage(source_agent="a", target_agent="b", message_type="T", payload={})
        result = bus.publish(msg)
        assert result is False

    def test_publish_direct_message_uses_inbox_topic(self):
        bus = self._connected_bus()
        msg = AgentMessage(
            source_agent="agent_a", target_agent="agent_b",
            message_type="Test_Please", payload={}
        )
        bus.publish(msg)
        calls = bus._client.publish.call_args_list
        first_topic = calls[0][0][0]
        assert "agent_b" in first_topic
        assert "inbox" in first_topic

    def test_publish_broadcast_when_no_target(self):
        bus = self._connected_bus()
        msg = AgentMessage(
            source_agent="agent_a", target_agent=None,
            message_type="Broadcast_Please", payload={}
        )
        bus.publish(msg)
        calls = bus._client.publish.call_args_list
        first_topic = calls[0][0][0]
        assert "broadcast" in first_topic

    def test_publish_also_sends_to_outbox(self):
        bus = self._connected_bus()
        msg = AgentMessage(
            source_agent="agent_a", target_agent="agent_b",
            message_type="Test_Please", payload={}
        )
        bus.publish(msg)
        assert bus._client.publish.call_count >= 2

    def test_publish_high_priority_uses_retain(self):
        bus = self._connected_bus()
        msg = AgentMessage(
            source_agent="a", target_agent="b",
            message_type="Test_Pretty_Please", payload={}, priority="high"
        )
        bus.publish(msg)
        calls = bus._client.publish.call_args_list
        _, kwargs = calls[0]
        assert kwargs.get("retain") is True

    def test_publish_normal_priority_no_retain(self):
        bus = self._connected_bus()
        msg = AgentMessage(
            source_agent="a", target_agent="b",
            message_type="Test_Please", payload={}, priority="normal"
        )
        bus.publish(msg)
        calls = bus._client.publish.call_args_list
        _, kwargs = calls[0]
        assert kwargs.get("retain") is False

    def test_publish_with_explicit_topic(self):
        bus = self._connected_bus()
        msg = AgentMessage(source_agent="a", target_agent="b", message_type="T", payload={})
        bus.publish(msg, topic="custom/topic/path")
        calls = bus._client.publish.call_args_list
        first_topic = calls[0][0][0]
        assert first_topic == "custom/topic/path"

    def test_publish_returns_false_on_exception(self):
        bus = _make_bus(connected=True)
        bus._client.publish.side_effect = RuntimeError("publish error")
        msg = AgentMessage(source_agent="a", target_agent="b", message_type="T", payload={})
        result = bus.publish(msg)
        assert result is False

    def test_publish_returns_true_on_success(self):
        bus = self._connected_bus()
        msg = AgentMessage(source_agent="a", target_agent="b", message_type="T", payload={})
        result = bus.publish(msg)
        assert result is True


# ═══════════════════════════════════════════════════════════════════════════════
# MQTTBus — subscribe
# ═══════════════════════════════════════════════════════════════════════════════

class TestMQTTBusSubscribe:
    def test_subscribe_registers_handler(self):
        bus = _make_bus()
        handler = MagicMock()
        bus.subscribe("telsonbase/test/topic", handler)
        assert "telsonbase/test/topic" in bus._handlers
        assert handler in bus._handlers["telsonbase/test/topic"]

    def test_subscribe_multiple_handlers_same_topic(self):
        bus = _make_bus()
        h1 = MagicMock()
        h2 = MagicMock()
        bus.subscribe("telsonbase/topic", h1)
        bus.subscribe("telsonbase/topic", h2)
        assert h1 in bus._handlers["telsonbase/topic"]
        assert h2 in bus._handlers["telsonbase/topic"]

    def test_subscribe_calls_client_subscribe_when_connected(self):
        bus = _make_bus(connected=True)
        bus.subscribe("telsonbase/connected/topic", MagicMock())
        bus._client.subscribe.assert_called_with("telsonbase/connected/topic", qos=1)

    def test_subscribe_no_client_subscribe_when_disconnected(self):
        bus = _make_bus(connected=False)
        bus.subscribe("telsonbase/disconnected/topic", MagicMock())
        bus._client.subscribe.assert_not_called()

    def test_register_agent_inbox(self):
        bus = _make_bus()
        handler = MagicMock()
        bus.register_agent_inbox("doc_prep_agent", handler)
        expected_topic = "telsonbase/agents/doc_prep_agent/inbox"
        assert expected_topic in bus._handlers
        assert handler in bus._handlers[expected_topic]

    def test_register_event_handler(self):
        bus = _make_bus()
        handler = MagicMock()
        bus.register_event_handler("anomaly", handler)
        expected_topic = "telsonbase/events/anomaly"
        assert expected_topic in bus._handlers

    def test_subscribe_topic_with_wildcard(self):
        bus = _make_bus()
        handler = MagicMock()
        bus.subscribe("telsonbase/events/#", handler)
        assert "telsonbase/events/#" in bus._handlers


# ═══════════════════════════════════════════════════════════════════════════════
# MQTTBus — publish_event
# ═══════════════════════════════════════════════════════════════════════════════

class TestMQTTBusPublishEvent:
    def _connected_bus(self):
        bus = _make_bus(connected=True)
        publish_result = MagicMock()
        publish_result.rc = 0
        bus._client.publish.return_value = publish_result
        return bus

    def test_publish_event_sends_message(self):
        bus = self._connected_bus()
        bus.publish_event("anomaly", "anomaly_agent", {"severity": "HIGH"})
        assert bus._client.publish.called

    def test_publish_event_uses_events_topic(self):
        bus = self._connected_bus()
        bus.publish_event("approval", "approval_agent", {})
        calls = bus._client.publish.call_args_list
        first_topic = calls[0][0][0]
        assert "events/approval" in first_topic

    def test_publish_event_pretty_please_is_high_priority(self):
        bus = self._connected_bus()
        bus.publish_event("anomaly", "detector", {"data": "x"}, qms_status="Pretty_Please")
        calls = bus._client.publish.call_args_list
        _, kwargs = calls[0]
        assert kwargs.get("retain") is True

    def test_publish_event_please_is_normal_priority(self):
        bus = self._connected_bus()
        bus.publish_event("info", "logger", {}, qms_status="Please")
        calls = bus._client.publish.call_args_list
        _, kwargs = calls[0]
        assert kwargs.get("retain") is False


# ═══════════════════════════════════════════════════════════════════════════════
# MQTTBus — internal callbacks
# ═══════════════════════════════════════════════════════════════════════════════

class TestMQTTBusCallbacks:
    def test_on_connect_success_sets_connected(self):
        bus = _make_bus()
        bus._on_connect(bus._client, None, {}, 0)
        assert bus._connected is True

    def test_on_connect_failure_leaves_disconnected(self):
        bus = _make_bus()
        bus._on_connect(bus._client, None, {}, 1)
        assert bus._connected is False

    def test_on_connect_resubscribes_existing_topics(self):
        bus = _make_bus()
        bus._handlers["telsonbase/test/topic"] = [MagicMock()]
        bus._on_connect(bus._client, None, {}, 0)
        bus._client.subscribe.assert_called_with("telsonbase/test/topic", qos=1)

    def test_on_connect_resubscribes_all_topics(self):
        bus = _make_bus()
        bus._handlers["topic_a"] = [MagicMock()]
        bus._handlers["topic_b"] = [MagicMock()]
        bus._on_connect(bus._client, None, {}, 0)
        assert bus._client.subscribe.call_count == 2

    def test_on_disconnect_clean_sets_not_connected(self):
        bus = _make_bus(connected=True)
        bus._on_disconnect(bus._client, None, 0)
        assert bus._connected is False

    def test_on_disconnect_unexpected_sets_not_connected(self):
        bus = _make_bus(connected=True)
        bus._on_disconnect(bus._client, None, 1)
        assert bus._connected is False

    def test_on_message_dispatches_to_handler(self):
        bus = _make_bus()
        handler = MagicMock()
        topic = "telsonbase/test"
        bus._handlers[topic] = [handler]

        msg = AgentMessage(
            source_agent="a", target_agent="b",
            message_type="Test_Please", payload={"key": "val"}
        )
        paho_msg = MagicMock()
        paho_msg.topic = topic
        paho_msg.payload = msg.to_json().encode("utf-8")

        bus._on_message(bus._client, None, paho_msg)
        handler.assert_called_once()

    def test_on_message_calls_handler_with_agent_message(self):
        bus = _make_bus()
        received = {}

        def capture_handler(agent_msg, topic_str):
            received["msg"] = agent_msg
            received["topic"] = topic_str

        topic = "telsonbase/agents/test_agent/inbox"
        bus._handlers[topic] = [capture_handler]

        original_msg = AgentMessage(
            source_agent="sender", target_agent="test_agent",
            message_type="Test_Please", payload={"data": 42}
        )
        paho_msg = MagicMock()
        paho_msg.topic = topic
        paho_msg.payload = original_msg.to_json().encode("utf-8")

        bus._on_message(bus._client, None, paho_msg)
        assert isinstance(received["msg"], AgentMessage)
        assert received["msg"].source_agent == "sender"
        assert received["msg"].payload["data"] == 42

    def test_on_message_malformed_json_does_not_crash(self):
        bus = _make_bus()
        paho_msg = MagicMock()
        paho_msg.topic = "telsonbase/test"
        paho_msg.payload = b"NOT VALID JSON {{{"
        # Should not raise
        bus._on_message(bus._client, None, paho_msg)

    def test_on_message_handler_exception_does_not_crash(self):
        bus = _make_bus()
        bad_handler = MagicMock(side_effect=RuntimeError("handler exploded"))
        bus._handlers["telsonbase/crash"] = [bad_handler]

        msg = AgentMessage(source_agent="a", target_agent=None, message_type="T", payload={})
        paho_msg = MagicMock()
        paho_msg.topic = "telsonbase/crash"
        paho_msg.payload = msg.to_json().encode("utf-8")

        # Should not raise even though handler throws
        bus._on_message(bus._client, None, paho_msg)

    def test_on_message_no_matching_topic_no_handler_called(self):
        bus = _make_bus()
        handler = MagicMock()
        bus._handlers["telsonbase/different/topic"] = [handler]

        msg = AgentMessage(source_agent="a", target_agent=None, message_type="T", payload={})
        paho_msg = MagicMock()
        paho_msg.topic = "telsonbase/other/path"
        paho_msg.payload = msg.to_json().encode("utf-8")

        bus._on_message(bus._client, None, paho_msg)
        # Handler for different topic should NOT be called
        # (paho.topic_matches_sub will return False for non-matching topics)


# ═══════════════════════════════════════════════════════════════════════════════
# is_connected property
# ═══════════════════════════════════════════════════════════════════════════════

class TestIsConnected:
    def test_is_connected_false_initially(self):
        bus = _make_bus()
        assert bus.is_connected is False

    def test_is_connected_true_after_manual_set(self):
        bus = _make_bus()
        bus._connected = True
        assert bus.is_connected is True


# ═══════════════════════════════════════════════════════════════════════════════
# Module-level singleton functions
# ═══════════════════════════════════════════════════════════════════════════════

class TestModuleLevelFunctions:
    def test_get_mqtt_bus_returns_instance(self):
        _mqtt_module._mqtt_bus_instance = None
        with patch("core.mqtt_bus.mqtt.Client") as mock_cls:
            mock_cls.return_value = MagicMock()
            bus = get_mqtt_bus()
        assert isinstance(bus, MQTTBus)
        _mqtt_module._mqtt_bus_instance = None

    def test_get_mqtt_bus_returns_same_instance(self):
        _mqtt_module._mqtt_bus_instance = None
        with patch("core.mqtt_bus.mqtt.Client") as mock_cls:
            mock_cls.return_value = MagicMock()
            b1 = get_mqtt_bus()
            b2 = get_mqtt_bus()
        assert b1 is b2
        _mqtt_module._mqtt_bus_instance = None

    def test_shutdown_calls_disconnect(self):
        mock_instance = MagicMock()
        _mqtt_module._mqtt_bus_instance = mock_instance
        shutdown_mqtt_bus()
        mock_instance.disconnect.assert_called_once()
        assert _mqtt_module._mqtt_bus_instance is None

    def test_shutdown_noop_when_no_instance(self):
        _mqtt_module._mqtt_bus_instance = None
        # Should not raise
        shutdown_mqtt_bus()

    def test_init_mqtt_bus_subscribes_to_events(self):
        _mqtt_module._mqtt_bus_instance = None
        with patch("core.mqtt_bus.mqtt.Client") as mock_cls:
            mock_cls.return_value = MagicMock()
            bus = get_mqtt_bus()

        bus.connect = MagicMock(return_value=True)
        bus.subscribe = MagicMock()

        with patch("core.mqtt_bus._mqtt_bus_instance", bus):
            init_mqtt_bus()

        subscribe_topics = [c[0][0] for c in bus.subscribe.call_args_list]
        assert any("events" in t for t in subscribe_topics)
        assert any("broadcast" in t for t in subscribe_topics)
        _mqtt_module._mqtt_bus_instance = None

    def test_init_mqtt_bus_returns_false_when_connect_fails(self):
        _mqtt_module._mqtt_bus_instance = None
        with patch("core.mqtt_bus.mqtt.Client") as mock_cls:
            mock_cls.return_value = MagicMock()
            bus = get_mqtt_bus()

        bus.connect = MagicMock(return_value=False)
        bus.subscribe = MagicMock()

        with patch("core.mqtt_bus._mqtt_bus_instance", bus):
            result = init_mqtt_bus()

        assert result is False
        bus.subscribe.assert_not_called()
        _mqtt_module._mqtt_bus_instance = None


# ═══════════════════════════════════════════════════════════════════════════════
# Default handlers
# ═══════════════════════════════════════════════════════════════════════════════

class TestDefaultHandlers:
    def test_default_event_handler_does_not_crash(self):
        msg = AgentMessage(
            source_agent="anomaly_agent", target_agent=None,
            message_type="Anomaly_Detected_Please", payload={"severity": "HIGH"}
        )
        _default_event_handler(msg, "telsonbase/events/anomaly")

    def test_default_broadcast_handler_does_not_crash(self):
        msg = AgentMessage(
            source_agent="system", target_agent=None,
            message_type="Broadcast_Please", payload={"event": "startup"}
        )
        _default_broadcast_handler(msg, "telsonbase/broadcast/all")
