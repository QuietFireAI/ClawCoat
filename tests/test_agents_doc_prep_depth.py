# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_agents_doc_prep_depth.py
# REM: Depth coverage for agents/doc_prep_agent.py
# REM: Pure unit tests — no Redis, no Postgres required.

import sys
from unittest.mock import MagicMock, patch

if "celery" not in sys.modules:
    celery_mock = MagicMock()
    celery_mock.shared_task = lambda *args, **kwargs: (lambda f: f)
    sys.modules["celery"] = celery_mock

import hashlib
import pytest

from agents.doc_prep_agent import DocPrepAgent, TEMPLATES
from agents.base import AgentRequest


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def agent():
    return DocPrepAgent()


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATES constants
# ═══════════════════════════════════════════════════════════════════════════════

class TestTemplatesConstant:
    def test_has_seven_templates(self):
        assert len(TEMPLATES) == 7

    def test_all_template_keys(self):
        expected = {
            "purchase_agreement", "seller_disclosure", "agency_disclosure",
            "closing_checklist", "listing_agreement", "cma_report",
            "lead_paint_disclosure",
        }
        assert set(TEMPLATES.keys()) == expected

    def test_every_template_has_id(self):
        for key, tmpl in TEMPLATES.items():
            assert "id" in tmpl, f"{key} missing id"
            assert tmpl["id"].startswith("TPL-")

    def test_every_template_has_name(self):
        for key, tmpl in TEMPLATES.items():
            assert "name" in tmpl and tmpl["name"]

    def test_every_template_has_fields_list(self):
        for key, tmpl in TEMPLATES.items():
            assert isinstance(tmpl["fields"], list) and len(tmpl["fields"]) > 0

    def test_every_template_has_sections_list(self):
        for key, tmpl in TEMPLATES.items():
            assert isinstance(tmpl["sections"], list) and len(tmpl["sections"]) > 0

    def test_every_template_has_category(self):
        for key, tmpl in TEMPLATES.items():
            assert tmpl["category"] in {"contract", "disclosure", "checklist", "analysis"}

    def test_purchase_agreement_fields(self):
        tmpl = TEMPLATES["purchase_agreement"]
        assert "buyer_name" in tmpl["fields"]
        assert "purchase_price" in tmpl["fields"]
        assert "closing_date" in tmpl["fields"]

    def test_lead_paint_disclosure_category(self):
        assert TEMPLATES["lead_paint_disclosure"]["category"] == "disclosure"

    def test_cma_report_category(self):
        assert TEMPLATES["cma_report"]["category"] == "analysis"


# ═══════════════════════════════════════════════════════════════════════════════
# DocPrepAgent constants
# ═══════════════════════════════════════════════════════════════════════════════

class TestDocPrepAgentConstants:
    def test_agent_name(self, agent):
        assert agent.AGENT_NAME == "doc_prep_agent"

    def test_capabilities_is_list(self, agent):
        assert isinstance(agent.CAPABILITIES, list)
        assert any("filesystem" in c for c in agent.CAPABILITIES)

    def test_requires_approval_for_finalize(self, agent):
        assert "finalize_document" in agent.REQUIRES_APPROVAL_FOR

    def test_requires_approval_for_delete(self, agent):
        assert "delete_document" in agent.REQUIRES_APPROVAL_FOR

    def test_supported_actions(self, agent):
        expected = {
            "list_templates", "get_template", "generate_document",
            "preview_document", "finalize_document", "list_generated",
            "get_document", "delete_document", "validate_fields",
        }
        assert set(agent.SUPPORTED_ACTIONS) == expected

    def test_skip_quarantine(self, agent):
        assert agent.SKIP_QUARANTINE is True


# ═══════════════════════════════════════════════════════════════════════════════
# _render_template
# ═══════════════════════════════════════════════════════════════════════════════

class TestRenderTemplate:
    def test_renders_purchase_agreement(self, agent):
        result = agent._render_template("purchase_agreement", {
            "buyer_name": "Alice Smith",
            "purchase_price": "$300,000",
        })
        assert "RESIDENTIAL PURCHASE AGREEMENT" in result
        assert "Alice Smith" in result
        assert "$300,000" in result

    def test_renders_all_templates_without_error(self, agent):
        for key in TEMPLATES:
            result = agent._render_template(key, {})
            assert isinstance(result, str)
            assert len(result) > 50

    def test_rendered_doc_contains_separator(self, agent):
        result = agent._render_template("seller_disclosure", {})
        assert "=" * 20 in result

    def test_rendered_doc_contains_template_id(self, agent):
        result = agent._render_template("closing_checklist", {})
        assert "TPL-CC-001" in result

    def test_rendered_doc_field_label_format(self, agent):
        result = agent._render_template("agency_disclosure", {
            "client_name": "Bob Jones",
        })
        assert "Client Name" in result
        assert "Bob Jones" in result

    def test_unknown_template_raises(self, agent):
        with pytest.raises(ValueError, match="Template not found"):
            agent._render_template("nonexistent_template", {})

    def test_empty_data_renders_sections(self, agent):
        result = agent._render_template("listing_agreement", {})
        assert "---" in result

    def test_return_type_is_string(self, agent):
        result = agent._render_template("cma_report", {"subject_address": "123 Main"})
        assert isinstance(result, str)

    def test_rendered_content_is_deterministic_for_data(self, agent):
        data = {"property_address": "456 Oak Ave", "seller_name": "Jane Doe"}
        r1 = agent._render_template("seller_disclosure", data)
        r2 = agent._render_template("seller_disclosure", data)
        # Content aside from timestamps should contain same fields
        assert "456 Oak Ave" in r1
        assert "456 Oak Ave" in r2


# ═══════════════════════════════════════════════════════════════════════════════
# _list_templates
# ═══════════════════════════════════════════════════════════════════════════════

class TestListTemplates:
    def test_returns_all_templates(self, agent):
        result = agent._list_templates({})
        assert result["count"] == 7
        assert len(result["templates"]) == 7

    def test_category_filter_disclosure(self, agent):
        result = agent._list_templates({"category": "disclosure"})
        for tmpl in result["templates"]:
            assert tmpl["category"] == "disclosure"
        assert result["count"] == 3  # seller, agency, lead_paint

    def test_category_filter_contract(self, agent):
        result = agent._list_templates({"category": "contract"})
        for tmpl in result["templates"]:
            assert tmpl["category"] == "contract"
        assert result["count"] == 2  # purchase_agreement, listing_agreement

    def test_category_filter_analysis(self, agent):
        result = agent._list_templates({"category": "analysis"})
        assert result["count"] == 1
        assert result["templates"][0]["key"] == "cma_report"

    def test_category_filter_no_match(self, agent):
        result = agent._list_templates({"category": "nonexistent"})
        assert result["count"] == 0
        assert result["templates"] == []

    def test_each_template_has_key(self, agent):
        result = agent._list_templates({})
        for tmpl in result["templates"]:
            assert "key" in tmpl
            assert tmpl["key"] in TEMPLATES

    def test_each_template_has_field_count(self, agent):
        result = agent._list_templates({})
        for tmpl in result["templates"]:
            assert "field_count" in tmpl
            assert tmpl["field_count"] > 0

    def test_no_category_returns_seven(self, agent):
        result = agent._list_templates({})
        assert result["count"] == 7


# ═══════════════════════════════════════════════════════════════════════════════
# _get_template
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetTemplate:
    def test_valid_template_key(self, agent):
        result = agent._get_template({"template_key": "purchase_agreement"})
        assert result["id"] == "TPL-PA-001"
        assert "buyer_name" in result["fields"]

    def test_template_alias_field(self, agent):
        result = agent._get_template({"template": "seller_disclosure"})
        assert result["id"] == "TPL-SD-001"

    def test_returns_fields_and_sections(self, agent):
        result = agent._get_template({"template_key": "closing_checklist"})
        assert isinstance(result["fields"], list)
        assert isinstance(result["sections"], list)
        assert len(result["fields"]) > 0
        assert len(result["sections"]) > 0

    def test_unknown_template_raises(self, agent):
        with pytest.raises(ValueError, match="Template not found"):
            agent._get_template({"template_key": "fake_template"})

    def test_none_key_raises(self, agent):
        with pytest.raises(ValueError):
            agent._get_template({})

    def test_returns_name_and_description(self, agent):
        result = agent._get_template({"template_key": "lead_paint_disclosure"})
        assert "name" in result
        assert "description" in result

    def test_cma_report_fields(self, agent):
        result = agent._get_template({"template_key": "cma_report"})
        assert "subject_address" in result["fields"]
        assert "comp_1_address" in result["fields"]


# ═══════════════════════════════════════════════════════════════════════════════
# _generate_document
# ═══════════════════════════════════════════════════════════════════════════════

class TestGenerateDocument:
    def test_generates_draft_document(self, agent):
        result = agent._generate_document({
            "template_key": "agency_disclosure",
            "data": {"client_name": "Test Client"},
            "transaction_id": "TXN-TEST-001",
        })
        assert result["status"] == "draft"
        assert result["document_id"].startswith("GEN-AG")
        assert "sha256" in result
        assert result["content_length"] > 0

    def test_stores_in_generated_documents(self, agent):
        result = agent._generate_document({
            "template_key": "closing_checklist",
            "data": {"property_address": "789 Elm"},
        })
        doc_id = result["document_id"]
        assert doc_id in agent._generated_documents

    def test_unknown_template_raises(self, agent):
        with pytest.raises(ValueError, match="Template not found"):
            agent._generate_document({
                "template_key": "invalid_tmpl",
                "data": {},
            })

    def test_sha256_is_hex_string(self, agent):
        result = agent._generate_document({
            "template_key": "listing_agreement",
            "data": {},
        })
        assert len(result["sha256"]) == 64
        int(result["sha256"], 16)  # must be valid hex

    def test_default_transaction_id(self, agent):
        result = agent._generate_document({
            "template_key": "lead_paint_disclosure",
            "data": {},
        })
        doc = agent._generated_documents[result["document_id"]]
        assert doc["transaction_id"] == "N/A"

    def test_template_alias_field(self, agent):
        result = agent._generate_document({
            "template": "cma_report",
            "data": {"subject_address": "Alias Test"},
        })
        assert result["status"] == "draft"

    def test_document_includes_field_data(self, agent):
        result = agent._generate_document({
            "template_key": "agency_disclosure",
            "data": {"agent_name": "Lisa Chen"},
        })
        doc = agent._generated_documents[result["document_id"]]
        assert doc["field_data"]["agent_name"] == "Lisa Chen"


# ═══════════════════════════════════════════════════════════════════════════════
# _preview_document
# ═══════════════════════════════════════════════════════════════════════════════

class TestPreviewDocument:
    @pytest.fixture
    def draft_doc_id(self, agent):
        result = agent._generate_document({
            "template_key": "seller_disclosure",
            "data": {"seller_name": "Preview Seller"},
        })
        return result["document_id"]

    def test_preview_returns_content(self, agent, draft_doc_id):
        result = agent._preview_document({"document_id": draft_doc_id})
        assert "preview" in result
        assert "Preview Seller" in result["preview"] or len(result["preview"]) > 0

    def test_preview_default_length_2000(self, agent, draft_doc_id):
        result = agent._preview_document({"document_id": draft_doc_id})
        assert len(result["preview"]) <= 2000

    def test_preview_custom_length(self, agent, draft_doc_id):
        result = agent._preview_document({
            "document_id": draft_doc_id,
            "preview_length": 50,
        })
        assert len(result["preview"]) <= 50

    def test_preview_truncated_flag_true(self, agent, draft_doc_id):
        result = agent._preview_document({
            "document_id": draft_doc_id,
            "preview_length": 1,
        })
        assert result["truncated"] is True

    def test_preview_truncated_flag_false_for_large_limit(self, agent, draft_doc_id):
        result = agent._preview_document({
            "document_id": draft_doc_id,
            "preview_length": 999999,
        })
        assert result["truncated"] is False

    def test_preview_returns_total_length(self, agent, draft_doc_id):
        result = agent._preview_document({"document_id": draft_doc_id})
        assert result["total_length"] > 0

    def test_preview_missing_doc_raises(self, agent):
        with pytest.raises(ValueError, match="Document not found"):
            agent._preview_document({"document_id": "GEN-NONEXISTENT-999"})

    def test_preview_none_id_raises(self, agent):
        with pytest.raises(ValueError):
            agent._preview_document({})


# ═══════════════════════════════════════════════════════════════════════════════
# _finalize_document
# ═══════════════════════════════════════════════════════════════════════════════

class TestFinalizeDocument:
    @pytest.fixture
    def draft_doc_id(self, agent):
        result = agent._generate_document({
            "template_key": "closing_checklist",
            "data": {"property_address": "Finalize Test"},
        })
        return result["document_id"]

    def test_finalize_changes_status(self, agent, draft_doc_id):
        result = agent._finalize_document({"document_id": draft_doc_id})
        assert result["status"] == "finalized"

    def test_finalize_sets_finalized_at(self, agent, draft_doc_id):
        result = agent._finalize_document({"document_id": draft_doc_id})
        assert result["finalized_at"] is not None

    def test_finalize_returns_sha256(self, agent, draft_doc_id):
        result = agent._finalize_document({"document_id": draft_doc_id})
        assert len(result["sha256"]) == 64

    def test_already_finalized_raises(self, agent):
        result = agent._generate_document({
            "template_key": "listing_agreement",
            "data": {"seller_name": "DoubleFinalize"},
        })
        doc_id = result["document_id"]
        agent._finalize_document({"document_id": doc_id})
        with pytest.raises(ValueError, match="already finalized"):
            agent._finalize_document({"document_id": doc_id})

    def test_missing_doc_raises(self, agent):
        with pytest.raises(ValueError, match="Document not found"):
            agent._finalize_document({"document_id": "GEN-GHOST-000"})

    def test_stored_doc_status_is_finalized(self, agent, draft_doc_id):
        agent._finalize_document({"document_id": draft_doc_id})
        doc = agent._generated_documents[draft_doc_id]
        assert doc["status"] == "finalized"


# ═══════════════════════════════════════════════════════════════════════════════
# _list_generated
# ═══════════════════════════════════════════════════════════════════════════════

class TestListGenerated:
    def test_returns_documents_and_count(self, agent):
        result = agent._list_generated({})
        assert "documents" in result
        assert "count" in result
        assert result["count"] >= 3  # seeded demo docs

    def test_status_filter_draft(self, agent):
        result = agent._list_generated({"status": "draft"})
        for doc in result["documents"]:
            assert doc["status"] == "draft"

    def test_status_filter_finalized(self, agent):
        result = agent._list_generated({"status": "finalized"})
        for doc in result["documents"]:
            assert doc["status"] == "finalized"

    def test_transaction_id_filter(self, agent):
        result = agent._list_generated({"transaction_id": "TXN-2026-001"})
        for doc in result["documents"]:
            assert doc["transaction_id"] == "TXN-2026-001"

    def test_no_match_filter_returns_empty(self, agent):
        result = agent._list_generated({"transaction_id": "TXN-NONEXISTENT-999"})
        assert result["count"] == 0

    def test_sha256_truncated_in_list(self, agent):
        result = agent._list_generated({"status": "finalized"})
        if result["count"] > 0:
            sha = result["documents"][0]["sha256"]
            assert sha.endswith("...")
            assert len(sha) < 70

    def test_each_doc_has_required_fields(self, agent):
        result = agent._list_generated({})
        required = {"document_id", "template_name", "transaction_id", "status", "sha256", "generated_at"}
        for doc in result["documents"]:
            assert required.issubset(doc.keys())


# ═══════════════════════════════════════════════════════════════════════════════
# _get_document
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetDocument:
    def test_returns_full_content(self, agent):
        result = agent._get_document({"document_id": "GEN-PA-001"})
        assert "content" in result
        assert len(result["content"]) > 100

    def test_returns_sha256(self, agent):
        result = agent._get_document({"document_id": "GEN-PA-001"})
        assert len(result["sha256"]) == 64

    def test_missing_doc_raises(self, agent):
        with pytest.raises(ValueError, match="Document not found"):
            agent._get_document({"document_id": "GEN-GHOST-999"})

    def test_none_id_raises(self, agent):
        with pytest.raises(ValueError):
            agent._get_document({})

    def test_returns_template_name(self, agent):
        result = agent._get_document({"document_id": "GEN-PA-001"})
        assert "template_name" in result
        assert result["template_name"] == "Residential Purchase Agreement"


# ═══════════════════════════════════════════════════════════════════════════════
# _delete_document
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeleteDocument:
    def test_deletes_document(self, agent):
        result = agent._generate_document({
            "template_key": "lead_paint_disclosure",
            "data": {},
        })
        doc_id = result["document_id"]
        del_result = agent._delete_document({"document_id": doc_id})
        assert del_result["deleted"] is True
        assert doc_id not in agent._generated_documents

    def test_returns_was_finalized_false_for_draft(self, agent):
        result = agent._generate_document({
            "template_key": "agency_disclosure",
            "data": {},
        })
        doc_id = result["document_id"]
        del_result = agent._delete_document({"document_id": doc_id})
        assert del_result["was_finalized"] is False

    def test_returns_was_finalized_true_for_finalized(self, agent):
        result = agent._generate_document({
            "template_key": "cma_report",
            "data": {},
        })
        doc_id = result["document_id"]
        agent._finalize_document({"document_id": doc_id})
        del_result = agent._delete_document({"document_id": doc_id})
        assert del_result["was_finalized"] is True

    def test_missing_doc_raises(self, agent):
        with pytest.raises(ValueError, match="Document not found"):
            agent._delete_document({"document_id": "GEN-FAKE-000"})

    def test_returns_document_id(self, agent):
        result = agent._generate_document({
            "template_key": "seller_disclosure",
            "data": {},
        })
        doc_id = result["document_id"]
        del_result = agent._delete_document({"document_id": doc_id})
        assert del_result["document_id"] == doc_id


# ═══════════════════════════════════════════════════════════════════════════════
# _validate_fields
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidateFields:
    def test_all_fields_provided(self, agent):
        all_fields = {f: "value" for f in TEMPLATES["agency_disclosure"]["fields"]}
        result = agent._validate_fields({
            "template_key": "agency_disclosure",
            "data": all_fields,
        })
        assert result["valid"] is True
        assert result["missing_fields"] == []

    def test_missing_fields_detected(self, agent):
        result = agent._validate_fields({
            "template_key": "purchase_agreement",
            "data": {"buyer_name": "Alice"},
        })
        assert result["valid"] is False
        assert len(result["missing_fields"]) > 0
        assert "purchase_price" in result["missing_fields"]

    def test_extra_fields_detected(self, agent):
        result = agent._validate_fields({
            "template_key": "agency_disclosure",
            "data": {"unknown_field": "extra"},
        })
        assert "unknown_field" in result["extra_fields"]

    def test_template_alias_field(self, agent):
        result = agent._validate_fields({
            "template": "closing_checklist",
            "data": {},
        })
        assert result["template"] == "closing_checklist"
        assert result["valid"] is False

    def test_unknown_template_raises(self, agent):
        with pytest.raises(ValueError, match="Template not found"):
            agent._validate_fields({"template_key": "fake", "data": {}})

    def test_returns_required_fields_count(self, agent):
        result = agent._validate_fields({
            "template_key": "lead_paint_disclosure",
            "data": {},
        })
        expected = len(TEMPLATES["lead_paint_disclosure"]["fields"])
        assert result["required_fields"] == expected

    def test_missing_fields_sorted(self, agent):
        result = agent._validate_fields({
            "template_key": "cma_report",
            "data": {},
        })
        assert result["missing_fields"] == sorted(result["missing_fields"])

    def test_extra_fields_sorted(self, agent):
        result = agent._validate_fields({
            "template_key": "agency_disclosure",
            "data": {"zzz_field": "z", "aaa_field": "a"},
        })
        assert result["extra_fields"] == sorted(result["extra_fields"])


# ═══════════════════════════════════════════════════════════════════════════════
# execute — dispatch and unknown action
# ═══════════════════════════════════════════════════════════════════════════════

class TestExecuteDispatch:
    def test_list_templates_via_execute(self, agent):
        req = AgentRequest(action="list_templates", payload={})
        result = agent.execute(req)
        assert "templates" in result
        assert result["count"] == 7

    def test_get_template_via_execute(self, agent):
        req = AgentRequest(
            action="get_template",
            payload={"template_key": "agency_disclosure"},
        )
        result = agent.execute(req)
        assert result["id"] == "TPL-AD-001"

    def test_validate_fields_via_execute(self, agent):
        req = AgentRequest(
            action="validate_fields",
            payload={"template_key": "cma_report", "data": {}},
        )
        result = agent.execute(req)
        assert "valid" in result
        assert result["valid"] is False

    def test_unknown_action_raises(self, agent):
        req = AgentRequest(action="obliterate_everything", payload={})
        with pytest.raises(ValueError, match="Unknown action"):
            agent.execute(req)

    def test_action_case_insensitive(self, agent):
        req = AgentRequest(action="LIST_TEMPLATES", payload={})
        result = agent.execute(req)
        assert "templates" in result

    def test_list_generated_via_execute(self, agent):
        req = AgentRequest(action="list_generated", payload={})
        result = agent.execute(req)
        assert "documents" in result

    def test_generate_and_preview_cycle(self, agent):
        gen_req = AgentRequest(
            action="generate_document",
            payload={"template_key": "listing_agreement", "data": {"seller_name": "Cycle Test"}},
        )
        gen_result = agent.execute(gen_req)
        doc_id = gen_result["document_id"]

        preview_req = AgentRequest(
            action="preview_document",
            payload={"document_id": doc_id},
        )
        preview_result = agent.execute(preview_req)
        assert "preview" in preview_result

    def test_generate_get_delete_cycle(self, agent):
        gen_req = AgentRequest(
            action="generate_document",
            payload={"template_key": "lead_paint_disclosure", "data": {}},
        )
        gen_result = agent.execute(gen_req)
        doc_id = gen_result["document_id"]

        get_req = AgentRequest(action="get_document", payload={"document_id": doc_id})
        get_result = agent.execute(get_req)
        assert get_result["document_id"] == doc_id

        del_req = AgentRequest(action="delete_document", payload={"document_id": doc_id})
        del_result = agent.execute(del_req)
        assert del_result["deleted"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# Demo seeding
# ═══════════════════════════════════════════════════════════════════════════════

class TestDemoSeeding:
    def test_seeded_with_purchase_agreement(self, agent):
        assert "GEN-PA-001" in agent._generated_documents

    def test_seeded_with_seller_disclosure(self, agent):
        assert "GEN-SD-001" in agent._generated_documents

    def test_seeded_with_agency_disclosure(self, agent):
        assert "GEN-AD-001" in agent._generated_documents

    def test_purchase_agreement_is_finalized(self, agent):
        doc = agent._generated_documents["GEN-PA-001"]
        assert doc["status"] == "finalized"

    def test_seller_disclosure_is_draft(self, agent):
        doc = agent._generated_documents["GEN-SD-001"]
        assert doc["status"] == "draft"

    def test_seeded_docs_have_sha256(self, agent):
        for doc_id in ["GEN-PA-001", "GEN-SD-001", "GEN-AD-001"]:
            doc = agent._generated_documents[doc_id]
            assert len(doc["sha256"]) == 64

    def test_seeded_content_matches_sha256(self, agent):
        for doc_id in ["GEN-PA-001", "GEN-SD-001", "GEN-AD-001"]:
            doc = agent._generated_documents[doc_id]
            expected = hashlib.sha256(doc["content"].encode()).hexdigest()
            assert doc["sha256"] == expected
