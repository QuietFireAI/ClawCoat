# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_secure_storage_depth.py
# REM: Depth coverage for core/secure_storage.py
# REM: EncryptedValue, SecureStorageManager (all methods), integrity checks.
# REM: All pure Python — no Redis required.

import base64
import os

import pytest

from core.secure_storage import (
    ENCRYPTION_KEY_ENV,
    ENCRYPTION_SALT_ENV,
    EncryptedValue,
    SecureStorageManager,
)


# ═══════════════════════════════════════════════════════════════════════════════
# EncryptedValue dataclass
# ═══════════════════════════════════════════════════════════════════════════════

class TestEncryptedValueToBytes:
    def test_version_byte_is_first(self):
        ev = EncryptedValue(ciphertext=b"CT", nonce=b"\x00" * 12, version=1)
        result = ev.to_bytes()
        assert result[0] == 1

    def test_nonce_follows_version(self):
        nonce = bytes(range(12))
        ev = EncryptedValue(ciphertext=b"CT", nonce=nonce, version=1)
        result = ev.to_bytes()
        assert result[1:13] == nonce

    def test_ciphertext_at_end(self):
        ev = EncryptedValue(ciphertext=b"CIPHER", nonce=b"\x00" * 12, version=1)
        result = ev.to_bytes()
        assert result[13:] == b"CIPHER"

    def test_total_length(self):
        ev = EncryptedValue(ciphertext=b"DATA", nonce=b"\x00" * 12, version=1)
        # 1 (version) + 12 (nonce) + 4 (ciphertext)
        assert len(ev.to_bytes()) == 17

    def test_returns_bytes_type(self):
        ev = EncryptedValue(ciphertext=b"x", nonce=b"\x00" * 12)
        assert isinstance(ev.to_bytes(), bytes)

    def test_default_version_is_1(self):
        ev = EncryptedValue(ciphertext=b"x", nonce=b"\x00" * 12)
        assert ev.version == 1

    def test_custom_version(self):
        ev = EncryptedValue(ciphertext=b"x", nonce=b"\x00" * 12, version=2)
        assert ev.to_bytes()[0] == 2


class TestEncryptedValueFromBytes:
    def _make_bytes(self, version=1, nonce=None, ciphertext=b"CT"):
        nonce = nonce or (b"\x00" * 12)
        return bytes([version]) + nonce + ciphertext

    def test_extracts_version(self):
        data = self._make_bytes(version=1)
        ev = EncryptedValue.from_bytes(data)
        assert ev.version == 1

    def test_extracts_nonce(self):
        nonce = bytes(range(12))
        data = self._make_bytes(nonce=nonce)
        ev = EncryptedValue.from_bytes(data)
        assert ev.nonce == nonce

    def test_extracts_ciphertext(self):
        data = self._make_bytes(ciphertext=b"HELLO")
        ev = EncryptedValue.from_bytes(data)
        assert ev.ciphertext == b"HELLO"

    def test_roundtrip_preserves_all_fields(self):
        original = EncryptedValue(
            ciphertext=b"ROUNDTRIP",
            nonce=bytes(range(12)),
            version=1
        )
        restored = EncryptedValue.from_bytes(original.to_bytes())
        assert restored.ciphertext == original.ciphertext
        assert restored.nonce == original.nonce
        assert restored.version == original.version

    def test_returns_encrypted_value_instance(self):
        data = self._make_bytes()
        result = EncryptedValue.from_bytes(data)
        assert isinstance(result, EncryptedValue)


# ═══════════════════════════════════════════════════════════════════════════════
# SecureStorageManager — initialization
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def manager():
    """Manager with explicit key+salt — deterministic."""
    return SecureStorageManager(
        encryption_key="test_key_for_unit_tests",
        salt="test_salt_for_unit_tests"
    )


class TestSecureStorageManagerInit:
    def test_initialized_with_explicit_key(self):
        m = SecureStorageManager(encryption_key="mykey", salt="mysalt")
        assert m._initialized is True

    def test_initialized_without_args_ephemeral(self, monkeypatch):
        monkeypatch.delenv(ENCRYPTION_KEY_ENV, raising=False)
        monkeypatch.delenv(ENCRYPTION_SALT_ENV, raising=False)
        m = SecureStorageManager()
        assert m._initialized is True

    def test_env_var_key_used(self, monkeypatch):
        monkeypatch.setenv(ENCRYPTION_KEY_ENV, "env_key")
        monkeypatch.setenv(ENCRYPTION_SALT_ENV, "env_salt")
        m = SecureStorageManager()
        assert m._initialized is True

    def test_different_keys_produce_different_derived_keys(self):
        m1 = SecureStorageManager(encryption_key="key1", salt="salt")
        m2 = SecureStorageManager(encryption_key="key2", salt="salt")
        assert m1._encryption_key != m2._encryption_key

    def test_same_key_same_derived_key(self):
        m1 = SecureStorageManager(encryption_key="same", salt="same")
        m2 = SecureStorageManager(encryption_key="same", salt="same")
        assert m1._encryption_key == m2._encryption_key

    def test_derived_key_length_32(self):
        m = SecureStorageManager(encryption_key="k", salt="s")
        assert len(m._encryption_key) == 32


# ═══════════════════════════════════════════════════════════════════════════════
# SecureStorageManager.encrypt() / decrypt()
# ═══════════════════════════════════════════════════════════════════════════════

class TestEncryptDecrypt:
    def test_encrypt_returns_bytes(self, manager):
        result = manager.encrypt("hello")
        assert isinstance(result, bytes)

    def test_encrypt_string_roundtrip(self, manager):
        plaintext = "secret data"
        encrypted = manager.encrypt(plaintext)
        decrypted = manager.decrypt(encrypted)
        assert decrypted == plaintext.encode("utf-8")

    def test_encrypt_bytes_roundtrip(self, manager):
        plaintext = b"binary secret"
        encrypted = manager.encrypt(plaintext)
        decrypted = manager.decrypt(encrypted)
        assert decrypted == plaintext

    def test_different_nonces_each_call(self, manager):
        e1 = manager.encrypt("same data")
        e2 = manager.encrypt("same data")
        # Different nonces → different ciphertext
        assert e1 != e2

    def test_encrypted_longer_than_plaintext(self, manager):
        plaintext = b"hello"
        encrypted = manager.encrypt(plaintext)
        # 1 byte version + 12 bytes nonce + ciphertext (plaintext + 16 byte GCM tag)
        assert len(encrypted) > len(plaintext)

    def test_decrypt_wrong_manager_raises(self, manager):
        encrypted = manager.encrypt("secret")
        other = SecureStorageManager(encryption_key="different_key", salt="different_salt")
        with pytest.raises(Exception):
            other.decrypt(encrypted)

    def test_encrypt_empty_string(self, manager):
        encrypted = manager.encrypt("")
        decrypted = manager.decrypt(encrypted)
        assert decrypted == b""

    def test_encrypt_large_data(self, manager):
        plaintext = "x" * 10_000
        encrypted = manager.encrypt(plaintext)
        decrypted = manager.decrypt(encrypted)
        assert decrypted == plaintext.encode("utf-8")

    def test_encrypt_unicode(self, manager):
        plaintext = "こんにちは世界"
        encrypted = manager.encrypt(plaintext)
        decrypted = manager.decrypt(encrypted)
        assert decrypted.decode("utf-8") == plaintext

    def test_tampered_ciphertext_raises(self, manager):
        encrypted = bytearray(manager.encrypt("secret"))
        # Flip a byte in the ciphertext region
        encrypted[-1] ^= 0xFF
        with pytest.raises(Exception):
            manager.decrypt(bytes(encrypted))


# ═══════════════════════════════════════════════════════════════════════════════
# SecureStorageManager.encrypt_string() / decrypt_string()
# ═══════════════════════════════════════════════════════════════════════════════

class TestEncryptDecryptString:
    def test_encrypt_string_returns_str(self, manager):
        result = manager.encrypt_string("hello")
        assert isinstance(result, str)

    def test_encrypt_string_is_base64(self, manager):
        result = manager.encrypt_string("hello")
        # Should decode without error
        decoded = base64.b64decode(result)
        assert isinstance(decoded, bytes)

    def test_encrypt_decrypt_string_roundtrip(self, manager):
        original = "super secret password"
        encrypted = manager.encrypt_string(original)
        decrypted = manager.decrypt_string(encrypted)
        assert decrypted == original

    def test_encrypt_string_empty(self, manager):
        encrypted = manager.encrypt_string("")
        decrypted = manager.decrypt_string(encrypted)
        assert decrypted == ""

    def test_encrypt_string_special_chars(self, manager):
        original = "p@$$w0rd!#%&*"
        encrypted = manager.encrypt_string(original)
        decrypted = manager.decrypt_string(encrypted)
        assert decrypted == original

    def test_two_encryptions_differ(self, manager):
        e1 = manager.encrypt_string("hello")
        e2 = manager.encrypt_string("hello")
        assert e1 != e2


# ═══════════════════════════════════════════════════════════════════════════════
# SecureStorageManager.encrypt_dict() / decrypt_dict()
# ═══════════════════════════════════════════════════════════════════════════════

class TestEncryptDecryptDict:
    def test_encrypt_dict_marks_encrypted_flag(self, manager):
        data = {"api_key": "sk-secret", "name": "agent"}
        result = manager.encrypt_dict(data, ["api_key"])
        assert result.get("_api_key_encrypted") is True

    def test_encrypt_dict_value_changed(self, manager):
        data = {"api_key": "sk-secret"}
        result = manager.encrypt_dict(data, ["api_key"])
        assert result["api_key"] != "sk-secret"

    def test_encrypt_dict_non_sensitive_unchanged(self, manager):
        data = {"api_key": "sk-secret", "name": "agent"}
        result = manager.encrypt_dict(data, ["api_key"])
        assert result["name"] == "agent"

    def test_encrypt_dict_missing_key_ignored(self, manager):
        data = {"name": "agent"}
        result = manager.encrypt_dict(data, ["api_key"])
        assert "api_key" not in result
        assert "_api_key_encrypted" not in result

    def test_encrypt_dict_none_value_ignored(self, manager):
        data = {"api_key": None}
        result = manager.encrypt_dict(data, ["api_key"])
        # None value → not encrypted
        assert result["api_key"] is None

    def test_encrypt_dict_integer_value_converted(self, manager):
        data = {"token": 12345}
        result = manager.encrypt_dict(data, ["token"])
        assert result.get("_token_encrypted") is True

    def test_encrypt_dict_bytes_value_converted(self, manager):
        data = {"signing_key": b"raw bytes"}
        result = manager.encrypt_dict(data, ["signing_key"])
        assert result.get("_signing_key_encrypted") is True

    def test_decrypt_dict_roundtrip(self, manager):
        original = {"api_key": "sk-secret", "name": "agent"}
        encrypted = manager.encrypt_dict(original, ["api_key"])
        decrypted = manager.decrypt_dict(encrypted, ["api_key"])
        assert decrypted["api_key"] == "sk-secret"
        assert decrypted["name"] == "agent"

    def test_decrypt_dict_removes_flag(self, manager):
        original = {"api_key": "sk-secret"}
        encrypted = manager.encrypt_dict(original, ["api_key"])
        decrypted = manager.decrypt_dict(encrypted, ["api_key"])
        assert "_api_key_encrypted" not in decrypted

    def test_decrypt_dict_non_encrypted_key_untouched(self, manager):
        data = {"name": "agent"}
        result = manager.decrypt_dict(data, ["api_key"])
        assert result["name"] == "agent"

    def test_encrypt_multiple_keys(self, manager):
        data = {"api_key": "k1", "token": "t1", "name": "n"}
        result = manager.encrypt_dict(data, ["api_key", "token"])
        assert result.get("_api_key_encrypted") is True
        assert result.get("_token_encrypted") is True
        assert result["name"] == "n"

    def test_decrypt_multiple_keys_roundtrip(self, manager):
        data = {"api_key": "k1", "token": "t1", "name": "n"}
        enc = manager.encrypt_dict(data, ["api_key", "token"])
        dec = manager.decrypt_dict(enc, ["api_key", "token"])
        assert dec["api_key"] == "k1"
        assert dec["token"] == "t1"
        assert dec["name"] == "n"

    def test_original_dict_not_mutated(self, manager):
        data = {"api_key": "original"}
        manager.encrypt_dict(data, ["api_key"])
        assert data["api_key"] == "original"


# ═══════════════════════════════════════════════════════════════════════════════
# SecureStorageManager.compute_integrity_hash() / verify_integrity()
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegrityHash:
    def test_returns_hex_string(self, manager):
        result = manager.compute_integrity_hash(b"data")
        assert isinstance(result, str)
        # SHA256 hex = 64 chars
        assert len(result) == 64

    def test_consistent_for_same_input(self, manager):
        h1 = manager.compute_integrity_hash(b"data", "ctx")
        h2 = manager.compute_integrity_hash(b"data", "ctx")
        assert h1 == h2

    def test_different_for_different_data(self, manager):
        h1 = manager.compute_integrity_hash(b"data1", "ctx")
        h2 = manager.compute_integrity_hash(b"data2", "ctx")
        assert h1 != h2

    def test_different_context_changes_hash(self, manager):
        h1 = manager.compute_integrity_hash(b"data", "ctx1")
        h2 = manager.compute_integrity_hash(b"data", "ctx2")
        assert h1 != h2

    def test_empty_context_valid(self, manager):
        result = manager.compute_integrity_hash(b"data")
        assert len(result) == 64

    def test_empty_data_valid(self, manager):
        result = manager.compute_integrity_hash(b"")
        assert len(result) == 64

    def test_verify_integrity_true_for_correct(self, manager):
        data = b"important data"
        h = manager.compute_integrity_hash(data, "test")
        assert manager.verify_integrity(data, h, "test") is True

    def test_verify_integrity_false_for_wrong_data(self, manager):
        data = b"important data"
        h = manager.compute_integrity_hash(data, "test")
        assert manager.verify_integrity(b"tampered data", h, "test") is False

    def test_verify_integrity_false_for_wrong_hash(self, manager):
        data = b"important data"
        assert manager.verify_integrity(data, "a" * 64, "") is False

    def test_verify_integrity_false_for_wrong_context(self, manager):
        data = b"important data"
        h = manager.compute_integrity_hash(data, "ctx1")
        assert manager.verify_integrity(data, h, "ctx2") is False

    def test_verify_integrity_returns_bool(self, manager):
        data = b"test"
        h = manager.compute_integrity_hash(data)
        result = manager.verify_integrity(data, h)
        assert isinstance(result, bool)

    def test_different_managers_same_key_same_hash(self):
        m1 = SecureStorageManager(encryption_key="k", salt="s")
        m2 = SecureStorageManager(encryption_key="k", salt="s")
        h1 = m1.compute_integrity_hash(b"data", "ctx")
        h2 = m2.compute_integrity_hash(b"data", "ctx")
        assert h1 == h2

    def test_different_managers_different_key_different_hash(self):
        m1 = SecureStorageManager(encryption_key="key1", salt="salt")
        m2 = SecureStorageManager(encryption_key="key2", salt="salt")
        h1 = m1.compute_integrity_hash(b"data")
        h2 = m2.compute_integrity_hash(b"data")
        assert h1 != h2
