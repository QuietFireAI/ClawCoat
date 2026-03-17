# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_semantic_matching_depth.py
# REM: Depth coverage for core/semantic_matching.py
# REM: Enums, synonym maps, hierarchy traversal, path matching,
# REM: capability matching (all branches), convenience functions.

import pytest

from core.semantic_matching import (
    ACTION_SYNONYMS,
    RESOURCE_HIERARCHY,
    MatchResult,
    MatchStrictness,
    SemanticMatcher,
    _SYNONYM_TO_CANONICAL,
    check_capability_semantic,
)


# ═══════════════════════════════════════════════════════════════════════════════
# MatchStrictness enum
# ═══════════════════════════════════════════════════════════════════════════════

class TestMatchStrictnessEnum:
    def test_strict(self):
        assert MatchStrictness.STRICT == "strict"

    def test_standard(self):
        assert MatchStrictness.STANDARD == "standard"

    def test_relaxed(self):
        assert MatchStrictness.RELAXED == "relaxed"

    def test_all_unique(self):
        values = [s.value for s in MatchStrictness]
        assert len(values) == len(set(values))


# ═══════════════════════════════════════════════════════════════════════════════
# ACTION_SYNONYMS structure
# ═══════════════════════════════════════════════════════════════════════════════

class TestActionSynonyms:
    def test_has_read_key(self):
        assert "read" in ACTION_SYNONYMS

    def test_has_write_key(self):
        assert "write" in ACTION_SYNONYMS

    def test_has_create_key(self):
        assert "create" in ACTION_SYNONYMS

    def test_has_delete_key(self):
        assert "delete" in ACTION_SYNONYMS

    def test_has_execute_key(self):
        assert "execute" in ACTION_SYNONYMS

    def test_has_list_key(self):
        assert "list" in ACTION_SYNONYMS

    def test_has_send_key(self):
        assert "send" in ACTION_SYNONYMS

    def test_has_receive_key(self):
        assert "receive" in ACTION_SYNONYMS

    def test_read_synonyms_include_view(self):
        assert "view" in ACTION_SYNONYMS["read"]

    def test_read_synonyms_include_get(self):
        assert "get" in ACTION_SYNONYMS["read"]

    def test_write_synonyms_include_update(self):
        assert "update" in ACTION_SYNONYMS["write"]

    def test_delete_synonyms_include_remove(self):
        assert "remove" in ACTION_SYNONYMS["delete"]

    def test_execute_synonyms_include_run(self):
        assert "run" in ACTION_SYNONYMS["execute"]

    def test_all_values_are_lists(self):
        for k, v in ACTION_SYNONYMS.items():
            assert isinstance(v, list), f"{k} should have list of synonyms"


# ═══════════════════════════════════════════════════════════════════════════════
# _SYNONYM_TO_CANONICAL reverse lookup
# ═══════════════════════════════════════════════════════════════════════════════

class TestSynonymToCanonical:
    def test_canonical_maps_to_itself(self):
        for canonical in ACTION_SYNONYMS:
            assert _SYNONYM_TO_CANONICAL[canonical] == canonical

    def test_view_maps_to_read(self):
        assert _SYNONYM_TO_CANONICAL["view"] == "read"

    def test_remove_maps_to_delete(self):
        assert _SYNONYM_TO_CANONICAL["remove"] == "delete"

    def test_run_maps_to_execute(self):
        assert _SYNONYM_TO_CANONICAL["run"] == "execute"

    def test_update_maps_to_write(self):
        assert _SYNONYM_TO_CANONICAL["update"] == "write"

    def test_add_maps_to_create(self):
        assert _SYNONYM_TO_CANONICAL["add"] == "create"

    def test_enumerate_maps_to_list(self):
        assert _SYNONYM_TO_CANONICAL["enumerate"] == "list"

    def test_post_maps_to_send(self):
        assert _SYNONYM_TO_CANONICAL["post"] == "send"

    def test_pull_maps_to_receive(self):
        assert _SYNONYM_TO_CANONICAL["pull"] == "receive"


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE_HIERARCHY structure
# ═══════════════════════════════════════════════════════════════════════════════

class TestResourceHierarchy:
    def test_file_parent_is_filesystem(self):
        assert RESOURCE_HIERARCHY["file"] == "filesystem"

    def test_directory_parent_is_filesystem(self):
        assert RESOURCE_HIERARCHY["directory"] == "filesystem"

    def test_document_parent_is_file(self):
        assert RESOURCE_HIERARCHY["document"] == "file"

    def test_table_parent_is_database(self):
        assert RESOURCE_HIERARCHY["table"] == "database"

    def test_record_parent_is_table(self):
        assert RESOURCE_HIERARCHY["record"] == "table"

    def test_database_parent_is_storage(self):
        assert RESOURCE_HIERARCHY["database"] == "storage"

    def test_api_parent_is_external(self):
        assert RESOURCE_HIERARCHY["api"] == "external"

    def test_agent_parent_is_internal(self):
        assert RESOURCE_HIERARCHY["agent"] == "internal"


# ═══════════════════════════════════════════════════════════════════════════════
# SemanticMatcher — initialization
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def matcher():
    return SemanticMatcher()


@pytest.fixture
def strict_matcher():
    return SemanticMatcher(strictness=MatchStrictness.STRICT)


class TestSemanticMatcherInit:
    def test_default_strictness_is_standard(self, matcher):
        assert matcher.strictness == MatchStrictness.STANDARD

    def test_custom_strictness(self, strict_matcher):
        assert strict_matcher.strictness == MatchStrictness.STRICT

    def test_custom_synonyms_initially_empty(self, matcher):
        assert matcher._custom_synonyms == {}

    def test_custom_hierarchy_initially_empty(self, matcher):
        assert matcher._custom_hierarchy == {}


# ═══════════════════════════════════════════════════════════════════════════════
# canonicalize_action()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCanonicalizeAction:
    def test_canonical_passes_through(self, matcher):
        assert matcher.canonicalize_action("read") == "read"

    def test_view_becomes_read(self, matcher):
        assert matcher.canonicalize_action("view") == "read"

    def test_get_becomes_read(self, matcher):
        assert matcher.canonicalize_action("get") == "read"

    def test_fetch_becomes_read(self, matcher):
        assert matcher.canonicalize_action("fetch") == "read"

    def test_remove_becomes_delete(self, matcher):
        assert matcher.canonicalize_action("remove") == "delete"

    def test_destroy_becomes_delete(self, matcher):
        assert matcher.canonicalize_action("destroy") == "delete"

    def test_run_becomes_execute(self, matcher):
        assert matcher.canonicalize_action("run") == "execute"

    def test_invoke_becomes_execute(self, matcher):
        assert matcher.canonicalize_action("invoke") == "execute"

    def test_save_becomes_write(self, matcher):
        assert matcher.canonicalize_action("save") == "write"

    def test_unknown_returns_itself(self, matcher):
        assert matcher.canonicalize_action("unknown_action") == "unknown_action"

    def test_uppercased_input_normalized(self, matcher):
        assert matcher.canonicalize_action("VIEW") == "read"

    def test_mixed_case_input(self, matcher):
        assert matcher.canonicalize_action("Remove") == "delete"


# ═══════════════════════════════════════════════════════════════════════════════
# get_resource_ancestors()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetResourceAncestors:
    def test_unknown_resource_returns_just_itself(self, matcher):
        result = matcher.get_resource_ancestors("unknown_resource")
        assert result == ["unknown_resource"]

    def test_file_hierarchy(self, matcher):
        result = matcher.get_resource_ancestors("file")
        assert "file" in result
        assert "filesystem" in result

    def test_document_hierarchy(self, matcher):
        result = matcher.get_resource_ancestors("document")
        # document → file → filesystem
        assert "document" in result
        assert "file" in result
        assert "filesystem" in result

    def test_record_hierarchy(self, matcher):
        result = matcher.get_resource_ancestors("record")
        # record → table → database → storage
        assert "record" in result
        assert "table" in result
        assert "database" in result
        assert "storage" in result

    def test_filesystem_no_parent(self, matcher):
        result = matcher.get_resource_ancestors("filesystem")
        assert result == ["filesystem"]

    def test_storage_no_parent(self, matcher):
        result = matcher.get_resource_ancestors("storage")
        assert result == ["storage"]

    def test_first_element_is_input(self, matcher):
        result = matcher.get_resource_ancestors("file")
        assert result[0] == "file"

    def test_directory_hierarchy(self, matcher):
        result = matcher.get_resource_ancestors("directory")
        assert "directory" in result
        assert "filesystem" in result

    def test_with_custom_hierarchy(self, matcher):
        matcher.add_custom_hierarchy("spreadsheet", "document")
        result = matcher.get_resource_ancestors("spreadsheet")
        assert "spreadsheet" in result
        assert "document" in result
        assert "file" in result
        assert "filesystem" in result


# ═══════════════════════════════════════════════════════════════════════════════
# normalize_path()
# ═══════════════════════════════════════════════════════════════════════════════

class TestNormalizePath:
    def test_empty_string_returns_empty(self, matcher):
        assert matcher.normalize_path("") == ""

    def test_backslashes_converted(self, matcher):
        result = matcher.normalize_path("data\\docs\\file.txt")
        assert "\\" not in result

    def test_double_slashes_collapsed(self, matcher):
        result = matcher.normalize_path("/data//docs///file.txt")
        assert "//" not in result

    def test_trailing_slash_removed(self, matcher):
        result = matcher.normalize_path("/data/docs/")
        assert not result.endswith("/")

    def test_simple_path_unchanged(self, matcher):
        assert matcher.normalize_path("/data/docs/file.txt") == "/data/docs/file.txt"

    def test_root_path(self, matcher):
        result = matcher.normalize_path("/")
        assert isinstance(result, str)

    def test_returns_string(self, matcher):
        assert isinstance(matcher.normalize_path("/some/path"), str)


# ═══════════════════════════════════════════════════════════════════════════════
# path_matches()
# ═══════════════════════════════════════════════════════════════════════════════

class TestPathMatches:
    def test_exact_match(self, matcher):
        assert matcher.path_matches("/data/file.txt", "/data/file.txt") is True

    def test_exact_no_match(self, matcher):
        assert matcher.path_matches("/data/file.txt", "/data/other.txt") is False

    def test_star_wildcard_matches_child(self, matcher):
        assert matcher.path_matches("/data/*", "/data/file.txt") is True

    def test_star_wildcard_matches_prefix_itself(self, matcher):
        assert matcher.path_matches("/data/*", "/data") is True

    def test_star_wildcard_no_match_different_prefix(self, matcher):
        assert matcher.path_matches("/data/*", "/other/file.txt") is False

    def test_double_star_matches_child(self, matcher):
        assert matcher.path_matches("/data/**", "/data/sub/file.txt") is True

    def test_double_star_matches_prefix(self, matcher):
        assert matcher.path_matches("/data/**", "/data") is True

    def test_double_star_no_match_different_prefix(self, matcher):
        assert matcher.path_matches("/data/**", "/other/file.txt") is False

    def test_mid_star_wildcard(self, matcher):
        assert matcher.path_matches("/data/*.txt", "/data/file.txt") is True

    def test_mid_star_no_match_subdir(self, matcher):
        # [^/]* won't cross directory boundary
        assert matcher.path_matches("/data/*.txt", "/data/sub/file.txt") is False

    def test_double_star_pattern_matches_deep(self, matcher):
        assert matcher.path_matches("/data/**/*.txt", "/data/sub/deep/file.txt") is True

    def test_no_wildcards_different_paths(self, matcher):
        assert matcher.path_matches("/a/b", "/a/c") is False


# ═══════════════════════════════════════════════════════════════════════════════
# _match_action() internal
# ═══════════════════════════════════════════════════════════════════════════════

class TestMatchAction:
    def test_exact_match(self, matcher):
        matched, match_type, canonical = matcher._match_action("read", "read")
        assert matched is True
        assert match_type == "exact"

    def test_wildcard_held_matches_anything(self, matcher):
        matched, match_type, _ = matcher._match_action("*", "read")
        assert matched is True
        assert match_type == "wildcard"

    def test_synonym_match_standard(self, matcher):
        matched, match_type, canonical = matcher._match_action("view", "read")
        assert matched is True
        assert match_type == "synonym"
        assert canonical == "read"

    def test_no_match_different_actions(self, matcher):
        matched, _, _ = matcher._match_action("read", "write")
        assert matched is False

    def test_strict_mode_rejects_synonym(self, strict_matcher):
        matched, _, _ = strict_matcher._match_action("view", "read")
        assert matched is False

    def test_strict_mode_allows_exact(self, strict_matcher):
        matched, match_type, _ = strict_matcher._match_action("read", "read")
        assert matched is True
        assert match_type == "exact"

    def test_canonical_returned_even_on_no_match(self, matcher):
        matched, _, canonical = matcher._match_action("read", "write")
        assert matched is False
        assert canonical == "write"


# ═══════════════════════════════════════════════════════════════════════════════
# _match_resource() internal
# ═══════════════════════════════════════════════════════════════════════════════

class TestMatchResource:
    def test_exact_match(self, matcher):
        matched, match_type = matcher._match_resource("file", "file")
        assert matched is True
        assert match_type == "exact"

    def test_wildcard_held_matches_anything(self, matcher):
        matched, match_type = matcher._match_resource("*", "file")
        assert matched is True
        assert match_type == "wildcard"

    def test_hierarchy_match(self, matcher):
        # held=filesystem, required=file — filesystem is in file's ancestors
        matched, match_type = matcher._match_resource("filesystem", "file")
        assert matched is True
        assert match_type == "hierarchy"

    def test_hierarchy_deep(self, matcher):
        # held=storage, required=record — storage is an ancestor of record
        matched, match_type = matcher._match_resource("storage", "record")
        assert matched is True
        assert match_type == "hierarchy"

    def test_no_match_unrelated(self, matcher):
        matched, _ = matcher._match_resource("database", "file")
        assert matched is False

    def test_strict_mode_rejects_hierarchy(self, strict_matcher):
        matched, _ = strict_matcher._match_resource("filesystem", "file")
        assert matched is False

    def test_strict_mode_allows_exact(self, strict_matcher):
        matched, match_type = strict_matcher._match_resource("file", "file")
        assert matched is True
        assert match_type == "exact"


# ═══════════════════════════════════════════════════════════════════════════════
# match_capability()
# ═══════════════════════════════════════════════════════════════════════════════

class TestMatchCapability:
    def test_exact_match(self, matcher):
        result = matcher.match_capability("file.read", "file.read")
        assert result.matched is True
        assert result.match_type == "exact"
        assert result.confidence == 1.0

    def test_synonym_action_match(self, matcher):
        result = matcher.match_capability("file.read", "file.view")
        assert result.matched is True
        assert result.match_type == "synonym"

    def test_hierarchy_resource_match(self, matcher):
        # held=filesystem.read, required=file.read
        result = matcher.match_capability("filesystem.read", "file.read")
        assert result.matched is True
        assert result.match_type == "hierarchy"

    def test_synonym_and_hierarchy(self, matcher):
        # held=filesystem.read, required=file.view
        result = matcher.match_capability("filesystem.read", "file.view")
        assert result.matched is True
        # hierarchy overrides synonym in match_type labeling
        assert result.match_type == "hierarchy"

    def test_confidence_reduced_for_synonym(self, matcher):
        result = matcher.match_capability("file.read", "file.view")
        assert result.confidence < 1.0
        assert result.confidence == pytest.approx(0.95)

    def test_confidence_reduced_for_hierarchy(self, matcher):
        result = matcher.match_capability("filesystem.read", "file.read")
        assert result.confidence == pytest.approx(0.90)

    def test_action_mismatch_no_match(self, matcher):
        result = matcher.match_capability("file.read", "file.write")
        assert result.matched is False
        assert result.match_type == "action_mismatch"

    def test_resource_mismatch_no_match(self, matcher):
        result = matcher.match_capability("database.read", "file.read")
        assert result.matched is False
        assert result.match_type == "resource_mismatch"

    def test_path_mismatch_no_match(self, matcher):
        result = matcher.match_capability("file.read:/data/a", "file.read:/data/b")
        assert result.matched is False
        assert result.match_type == "path_mismatch"

    def test_path_wildcard_match(self, matcher):
        result = matcher.match_capability("file.read:/data/*", "file.read:/data/report.txt")
        assert result.matched is True

    def test_wildcard_action(self, matcher):
        result = matcher.match_capability("file.*", "file.read")
        assert result.matched is True

    def test_wildcard_resource(self, matcher):
        result = matcher.match_capability("*.read", "file.read")
        assert result.matched is True

    def test_no_path_in_held_still_matches(self, matcher):
        # held has no path restriction → no path comparison
        result = matcher.match_capability("file.read", "file.read:/data/file.txt")
        assert result.matched is True

    def test_parse_error_returns_no_match(self, matcher):
        # Empty string → parse error
        result = matcher.match_capability("", "")
        assert result.matched is False

    def test_returns_match_result_instance(self, matcher):
        result = matcher.match_capability("file.read", "file.read")
        assert isinstance(result, MatchResult)

    def test_canonical_action_in_result(self, matcher):
        result = matcher.match_capability("file.view", "file.read")
        assert result.canonical_action is not None


# ═══════════════════════════════════════════════════════════════════════════════
# find_matching_capability()
# ═══════════════════════════════════════════════════════════════════════════════

class TestFindMatchingCapability:
    def test_exact_match_found(self, matcher):
        result = matcher.find_matching_capability(["file.read", "file.write"], "file.read")
        assert result is not None
        assert result.matched is True

    def test_no_match_returns_none(self, matcher):
        result = matcher.find_matching_capability(["file.write"], "file.read")
        assert result is None

    def test_empty_list_returns_none(self, matcher):
        result = matcher.find_matching_capability([], "file.read")
        assert result is None

    def test_best_match_returned(self, matcher):
        # filesystem.read (hierarchy, lower confidence) vs file.read (exact, higher)
        result = matcher.find_matching_capability(
            ["filesystem.read", "file.read"],
            "file.read"
        )
        assert result is not None
        assert result.match_type == "exact"
        assert result.confidence == 1.0

    def test_synonym_match_found(self, matcher):
        result = matcher.find_matching_capability(["file.view"], "file.read")
        assert result is not None
        assert result.matched is True


# ═══════════════════════════════════════════════════════════════════════════════
# add_custom_synonym() and add_custom_hierarchy()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCustomExtensions:
    def test_add_custom_synonym(self, matcher):
        matcher.add_custom_synonym("process", ["handle", "digest"])
        assert matcher.canonicalize_action("handle") == "process"
        assert matcher.canonicalize_action("digest") == "process"

    def test_add_custom_hierarchy_used_in_ancestors(self, matcher):
        matcher.add_custom_hierarchy("spreadsheet", "document")
        ancestors = matcher.get_resource_ancestors("spreadsheet")
        assert "document" in ancestors
        assert "file" in ancestors
        assert "filesystem" in ancestors

    def test_add_custom_hierarchy_match_uses_it(self, matcher):
        matcher.add_custom_hierarchy("spreadsheet", "document")
        # held=filesystem.read should match required=spreadsheet.read
        result = matcher.match_capability("filesystem.read", "spreadsheet.read")
        assert result.matched is True


# ═══════════════════════════════════════════════════════════════════════════════
# explain_match()
# ═══════════════════════════════════════════════════════════════════════════════

class TestExplainMatch:
    def test_matched_result_says_match(self, matcher):
        result = matcher.match_capability("file.read", "file.read")
        explanation = matcher.explain_match(result)
        assert "MATCH" in explanation

    def test_no_match_says_no_match(self, matcher):
        result = matcher.match_capability("file.read", "file.write")
        explanation = matcher.explain_match(result)
        assert "NO MATCH" in explanation

    def test_returns_string(self, matcher):
        result = matcher.match_capability("file.read", "file.read")
        assert isinstance(matcher.explain_match(result), str)

    def test_explanation_includes_capability(self, matcher):
        result = matcher.match_capability("file.read", "file.read")
        explanation = matcher.explain_match(result)
        assert "file.read" in explanation


# ═══════════════════════════════════════════════════════════════════════════════
# check_capability_semantic() convenience function
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckCapabilitySemantic:
    def test_matching_cap_returns_true(self):
        matched, result = check_capability_semantic(["file.read"], "file.read")
        assert matched is True
        assert result is not None

    def test_no_matching_cap_returns_false(self):
        matched, result = check_capability_semantic(["file.write"], "file.read")
        assert matched is False

    def test_empty_capabilities_returns_false(self):
        matched, result = check_capability_semantic([], "file.read")
        assert matched is False

    def test_synonym_match_returns_true(self):
        matched, _ = check_capability_semantic(["file.view"], "file.read")
        assert matched is True

    def test_agent_id_param_accepted(self):
        matched, _ = check_capability_semantic(["file.read"], "file.read", agent_id="agent_001")
        assert matched is True

    def test_returns_tuple(self):
        result = check_capability_semantic(["file.read"], "file.read")
        assert isinstance(result, tuple)
        assert len(result) == 2
