# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_phi_deidentification_depth.py
# REM: Depth coverage for core/phi_deidentification.py
# REM: PHIField, PHI_FIELD_PATTERNS, DeidentificationResult, PHIDeidentifier — all in-memory.

import pytest

from core.phi_deidentification import (
    REDACTED_VALUE,
    PHIField,
    PHI_FIELD_PATTERNS,
    DeidentificationResult,
    PHIDeidentifier,
)


# ─── Patch Redis so audit.log() uses in-memory path ────────────────────────────
@pytest.fixture(autouse=True)
def _no_redis(monkeypatch):
    monkeypatch.setattr("core.persistence.get_redis", lambda: None)


# ─── Shared deidentifier fixture ───────────────────────────────────────────────
@pytest.fixture
def deidentifier():
    return PHIDeidentifier()


# ═══════════════════════════════════════════════════════════════════════════════
# REDACTED_VALUE constant
# ═══════════════════════════════════════════════════════════════════════════════

class TestRedactedValue:
    def test_is_string(self):
        assert isinstance(REDACTED_VALUE, str)

    def test_value(self):
        assert REDACTED_VALUE == "[REDACTED]"

    def test_not_empty(self):
        assert len(REDACTED_VALUE) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# PHIField enum — all 18 HIPAA Safe Harbor identifiers
# ═══════════════════════════════════════════════════════════════════════════════

class TestPHIField:
    def test_name_value(self):
        assert PHIField.NAME == "name"

    def test_address_value(self):
        assert PHIField.ADDRESS == "address"

    def test_dates_value(self):
        assert PHIField.DATES == "dates"

    def test_phone_value(self):
        assert PHIField.PHONE == "phone"

    def test_fax_value(self):
        assert PHIField.FAX == "fax"

    def test_email_value(self):
        assert PHIField.EMAIL == "email"

    def test_ssn_value(self):
        assert PHIField.SSN == "ssn"

    def test_mrn_value(self):
        assert PHIField.MRN == "mrn"

    def test_health_plan_id_value(self):
        assert PHIField.HEALTH_PLAN_ID == "health_plan_id"

    def test_account_number_value(self):
        assert PHIField.ACCOUNT_NUMBER == "account_number"

    def test_license_number_value(self):
        assert PHIField.LICENSE_NUMBER == "license_number"

    def test_vehicle_id_value(self):
        assert PHIField.VEHICLE_ID == "vehicle_id"

    def test_device_id_value(self):
        assert PHIField.DEVICE_ID == "device_id"

    def test_url_value(self):
        assert PHIField.URL == "url"

    def test_ip_address_value(self):
        assert PHIField.IP_ADDRESS == "ip_address"

    def test_biometric_value(self):
        assert PHIField.BIOMETRIC == "biometric"

    def test_photo_value(self):
        assert PHIField.PHOTO == "photo"

    def test_other_unique_value(self):
        assert PHIField.OTHER_UNIQUE == "other_unique"

    def test_exactly_18_members(self):
        assert len(PHIField) == 18

    def test_is_str_subclass(self):
        assert isinstance(PHIField.NAME, str)


# ═══════════════════════════════════════════════════════════════════════════════
# PHI_FIELD_PATTERNS — spot-check key mappings
# ═══════════════════════════════════════════════════════════════════════════════

class TestPHIFieldPatterns:
    def test_is_dict(self):
        assert isinstance(PHI_FIELD_PATTERNS, dict)

    def test_name_maps_to_name(self):
        assert PHI_FIELD_PATTERNS["name"] == PHIField.NAME

    def test_first_name_maps_to_name(self):
        assert PHI_FIELD_PATTERNS["first_name"] == PHIField.NAME

    def test_ssn_maps_to_ssn(self):
        assert PHI_FIELD_PATTERNS["ssn"] == PHIField.SSN

    def test_email_maps_to_email(self):
        assert PHI_FIELD_PATTERNS["email"] == PHIField.EMAIL

    def test_phone_maps_to_phone(self):
        assert PHI_FIELD_PATTERNS["phone"] == PHIField.PHONE

    def test_dob_maps_to_dates(self):
        assert PHI_FIELD_PATTERNS["dob"] == PHIField.DATES

    def test_mrn_maps_to_mrn(self):
        assert PHI_FIELD_PATTERNS["mrn"] == PHIField.MRN

    def test_ip_address_maps_to_ip_address(self):
        assert PHI_FIELD_PATTERNS["ip_address"] == PHIField.IP_ADDRESS

    def test_vin_maps_to_vehicle_id(self):
        assert PHI_FIELD_PATTERNS["vin"] == PHIField.VEHICLE_ID

    def test_biometric_maps_to_biometric(self):
        assert PHI_FIELD_PATTERNS["biometric"] == PHIField.BIOMETRIC

    def test_fingerprint_maps_to_biometric(self):
        assert PHI_FIELD_PATTERNS["fingerprint"] == PHIField.BIOMETRIC

    def test_photo_maps_to_photo(self):
        assert PHI_FIELD_PATTERNS["photo"] == PHIField.PHOTO

    def test_not_empty(self):
        assert len(PHI_FIELD_PATTERNS) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# DeidentificationResult.to_dict()
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeidentificationResultToDict:
    def _make_result(self, **kwargs):
        defaults = dict(
            original_field_count=5,
            removed_field_count=2,
            remaining_fields=["a", "b"],
            method="safe_harbor",
            timestamp="2026-01-01T00:00:00+00:00",
        )
        defaults.update(kwargs)
        return DeidentificationResult(**defaults)

    def test_returns_dict(self):
        r = self._make_result()
        assert isinstance(r.to_dict(), dict)

    def test_has_original_field_count(self):
        r = self._make_result(original_field_count=10)
        assert r.to_dict()["original_field_count"] == 10

    def test_has_removed_field_count(self):
        r = self._make_result(removed_field_count=3)
        assert r.to_dict()["removed_field_count"] == 3

    def test_has_remaining_fields(self):
        r = self._make_result(remaining_fields=["x", "y"])
        assert r.to_dict()["remaining_fields"] == ["x", "y"]

    def test_has_method(self):
        r = self._make_result(method="safe_harbor")
        assert r.to_dict()["method"] == "safe_harbor"

    def test_has_timestamp(self):
        r = self._make_result(timestamp="2026-01-01T00:00:00+00:00")
        assert r.to_dict()["timestamp"] == "2026-01-01T00:00:00+00:00"

    def test_all_five_keys_present(self):
        r = self._make_result()
        assert set(r.to_dict().keys()) == {
            "original_field_count", "removed_field_count",
            "remaining_fields", "method", "timestamp"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# PHIDeidentifier._detect_phi_field()
# ═══════════════════════════════════════════════════════════════════════════════

class TestDetectPhiField:
    def test_exact_match_ssn(self, deidentifier):
        assert deidentifier._detect_phi_field("ssn") == PHIField.SSN

    def test_exact_match_email(self, deidentifier):
        assert deidentifier._detect_phi_field("email") == PHIField.EMAIL

    def test_exact_match_phone(self, deidentifier):
        assert deidentifier._detect_phi_field("phone") == PHIField.PHONE

    def test_exact_match_name(self, deidentifier):
        assert deidentifier._detect_phi_field("name") == PHIField.NAME

    def test_substring_match_ssn_in_patient_ssn(self, deidentifier):
        # "ssn" is a pattern, "patient_ssn" contains "ssn"
        assert deidentifier._detect_phi_field("patient_ssn") == PHIField.SSN

    def test_substring_match_email_in_work_email(self, deidentifier):
        assert deidentifier._detect_phi_field("work_email") == PHIField.EMAIL

    def test_substring_match_phone_in_home_phone(self, deidentifier):
        assert deidentifier._detect_phi_field("home_phone") == PHIField.PHONE

    def test_case_insensitive_exact(self, deidentifier):
        assert deidentifier._detect_phi_field("SSN") == PHIField.SSN

    def test_case_insensitive_mixed(self, deidentifier):
        assert deidentifier._detect_phi_field("Email") == PHIField.EMAIL

    def test_non_phi_field_returns_none(self, deidentifier):
        assert deidentifier._detect_phi_field("diagnosis_code") is None

    def test_unknown_field_returns_none(self, deidentifier):
        assert deidentifier._detect_phi_field("completely_unknown_xyz") is None

    def test_empty_string_returns_none(self, deidentifier):
        assert deidentifier._detect_phi_field("") is None

    def test_whitespace_stripped(self, deidentifier):
        assert deidentifier._detect_phi_field("  ssn  ") == PHIField.SSN

    def test_dob_maps_to_dates(self, deidentifier):
        assert deidentifier._detect_phi_field("dob") == PHIField.DATES

    def test_vin_maps_to_vehicle_id(self, deidentifier):
        assert deidentifier._detect_phi_field("vin") == PHIField.VEHICLE_ID


# ═══════════════════════════════════════════════════════════════════════════════
# PHIDeidentifier.deidentify_record()
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeidentifyRecord:
    def test_returns_tuple(self, deidentifier):
        result = deidentifier.deidentify_record({"name": "Alice"})
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_phi_field_is_redacted(self, deidentifier):
        record = {"name": "Alice"}
        deidentified, _ = deidentifier.deidentify_record(record)
        assert deidentified["name"] == REDACTED_VALUE

    def test_non_phi_field_preserved(self, deidentifier):
        record = {"diagnosis_code": "J00", "name": "Alice"}
        deidentified, _ = deidentifier.deidentify_record(record)
        assert deidentified["diagnosis_code"] == "J00"

    def test_multiple_phi_fields_all_redacted(self, deidentifier):
        record = {"name": "Alice", "ssn": "123-45-6789", "email": "a@b.com"}
        deidentified, _ = deidentifier.deidentify_record(record)
        assert all(deidentified[k] == REDACTED_VALUE for k in ["name", "ssn", "email"])

    def test_result_removed_field_count(self, deidentifier):
        record = {"name": "Alice", "ssn": "123-45-6789", "diagnosis_code": "J00"}
        _, result = deidentifier.deidentify_record(record)
        assert result.removed_field_count == 2

    def test_result_original_field_count(self, deidentifier):
        record = {"name": "Alice", "diagnosis_code": "J00"}
        _, result = deidentifier.deidentify_record(record)
        assert result.original_field_count == 2

    def test_result_method_default(self, deidentifier):
        _, result = deidentifier.deidentify_record({"a": "b"})
        assert result.method == "safe_harbor"

    def test_result_method_custom(self, deidentifier):
        _, result = deidentifier.deidentify_record({"a": "b"}, method="custom")
        assert result.method == "custom"

    def test_result_has_timestamp(self, deidentifier):
        _, result = deidentifier.deidentify_record({"a": "b"})
        assert result.timestamp != ""

    def test_result_remaining_fields_sorted(self, deidentifier):
        record = {"z_field": 1, "a_field": 2, "name": "X"}
        _, result = deidentifier.deidentify_record(record)
        assert result.remaining_fields == sorted(result.remaining_fields)

    def test_original_record_not_mutated(self, deidentifier):
        record = {"name": "Alice", "age": 30}
        original_name = record["name"]
        deidentifier.deidentify_record(record)
        assert record["name"] == original_name  # Original unchanged

    def test_empty_record(self, deidentifier):
        deidentified, result = deidentifier.deidentify_record({})
        assert deidentified == {}
        assert result.removed_field_count == 0

    def test_no_phi_record_unchanged(self, deidentifier):
        record = {"department": "cardiology", "visit_count": 3}
        deidentified, result = deidentifier.deidentify_record(record)
        assert deidentified == record
        assert result.removed_field_count == 0

    def test_nested_dict_phi_redacted(self, deidentifier):
        record = {"contact": {"email": "a@b.com", "city": "NYC"}}
        deidentified, _ = deidentifier.deidentify_record(record)
        assert deidentified["contact"]["email"] == REDACTED_VALUE

    def test_nested_dict_non_phi_preserved(self, deidentifier):
        record = {"contact": {"email": "a@b.com", "code": "X"}}
        deidentified, _ = deidentifier.deidentify_record(record)
        assert deidentified["contact"]["code"] == "X"

    def test_list_of_dicts_each_deidentified(self, deidentifier):
        record = {
            "patients": [
                {"name": "Alice", "dept": "cardio"},
                {"name": "Bob", "dept": "neuro"},
            ]
        }
        deidentified, _ = deidentifier.deidentify_record(record)
        for patient in deidentified["patients"]:
            assert patient["name"] == REDACTED_VALUE
            assert patient["dept"] != REDACTED_VALUE

    def test_list_of_non_dicts_preserved(self, deidentifier):
        record = {"tags": ["a", "b", "c"]}
        deidentified, _ = deidentifier.deidentify_record(record)
        assert deidentified["tags"] == ["a", "b", "c"]

    def test_result_to_dict(self, deidentifier):
        _, result = deidentifier.deidentify_record({"name": "X"})
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["removed_field_count"] == 1


# ═══════════════════════════════════════════════════════════════════════════════
# PHIDeidentifier.is_deidentified()
# ═══════════════════════════════════════════════════════════════════════════════

class TestIsDeidentified:
    def test_empty_record_is_deidentified(self, deidentifier):
        assert deidentifier.is_deidentified({}) is True

    def test_no_phi_fields_is_deidentified(self, deidentifier):
        assert deidentifier.is_deidentified({"dept": "cardio", "code": "J00"}) is True

    def test_phi_field_with_value_not_deidentified(self, deidentifier):
        assert deidentifier.is_deidentified({"name": "Alice"}) is False

    def test_phi_field_redacted_is_deidentified(self, deidentifier):
        assert deidentifier.is_deidentified({"name": REDACTED_VALUE}) is True

    def test_mixed_redacted_and_non_phi(self, deidentifier):
        assert deidentifier.is_deidentified({
            "name": REDACTED_VALUE,
            "dept": "cardio"
        }) is True

    def test_one_unredacted_phi_makes_not_deidentified(self, deidentifier):
        assert deidentifier.is_deidentified({
            "name": REDACTED_VALUE,
            "ssn": "123-45-6789",  # NOT redacted
        }) is False

    def test_returns_bool(self, deidentifier):
        assert isinstance(deidentifier.is_deidentified({}), bool)

    def test_after_deidentify_record_is_deidentified(self, deidentifier):
        record = {"name": "Alice", "dept": "cardio"}
        deidentified, _ = deidentifier.deidentify_record(record)
        assert deidentifier.is_deidentified(deidentified) is True


# ═══════════════════════════════════════════════════════════════════════════════
# PHIDeidentifier.get_phi_fields_in_record()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetPhiFieldsInRecord:
    def test_returns_dict(self, deidentifier):
        assert isinstance(deidentifier.get_phi_fields_in_record({}), dict)

    def test_empty_record_empty_dict(self, deidentifier):
        assert deidentifier.get_phi_fields_in_record({}) == {}

    def test_no_phi_fields_empty_dict(self, deidentifier):
        result = deidentifier.get_phi_fields_in_record({"dept": "X", "code": "J00"})
        assert result == {}

    def test_phi_field_found(self, deidentifier):
        result = deidentifier.get_phi_fields_in_record({"ssn": "123-45-6789"})
        assert "ssn" in result
        assert result["ssn"] == PHIField.SSN.value

    def test_multiple_phi_fields(self, deidentifier):
        record = {"name": "Alice", "ssn": "123", "email": "a@b.com", "dept": "X"}
        result = deidentifier.get_phi_fields_in_record(record)
        assert "name" in result
        assert "ssn" in result
        assert "email" in result
        assert "dept" not in result

    def test_values_are_phi_field_values(self, deidentifier):
        result = deidentifier.get_phi_fields_in_record({"email": "x@y.com"})
        assert result["email"] == "email"  # PHIField.EMAIL.value

    def test_non_phi_fields_excluded(self, deidentifier):
        result = deidentifier.get_phi_fields_in_record({"visit_count": 5, "ssn": "123"})
        assert "visit_count" not in result
        assert "ssn" in result


# ═══════════════════════════════════════════════════════════════════════════════
# PHIDeidentifier.list_safe_harbor_identifiers()
# ═══════════════════════════════════════════════════════════════════════════════

class TestListSafeHarborIdentifiers:
    def test_returns_list(self, deidentifier):
        assert isinstance(deidentifier.list_safe_harbor_identifiers(), list)

    def test_returns_18_items(self, deidentifier):
        assert len(deidentifier.list_safe_harbor_identifiers()) == 18

    def test_each_item_is_dict(self, deidentifier):
        for item in deidentifier.list_safe_harbor_identifiers():
            assert isinstance(item, dict)

    def test_each_item_has_identifier_key(self, deidentifier):
        for item in deidentifier.list_safe_harbor_identifiers():
            assert "identifier" in item

    def test_each_item_has_enum_key(self, deidentifier):
        for item in deidentifier.list_safe_harbor_identifiers():
            assert "enum" in item

    def test_ssn_in_list(self, deidentifier):
        identifiers = [i["identifier"] for i in deidentifier.list_safe_harbor_identifiers()]
        assert "ssn" in identifiers

    def test_name_in_list(self, deidentifier):
        identifiers = [i["identifier"] for i in deidentifier.list_safe_harbor_identifiers()]
        assert "name" in identifiers

    def test_identifier_values_are_phi_field_values(self, deidentifier):
        phi_values = {phi.value for phi in PHIField}
        listed = {i["identifier"] for i in deidentifier.list_safe_harbor_identifiers()}
        assert listed == phi_values
