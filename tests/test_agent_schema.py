"""
Unit tests for schema grounding and semantic validation.
"""

from veneer_coder.schema import load_component_schemas, get_grounding_prompt
from veneer_coder.compiler import validate_vnr_semantics, ValidationStatus


def test_load_component_schemas():
    schemas = load_component_schemas()
    assert isinstance(schemas, dict)
    assert "UiNavHeader" in schemas
    assert "UiTableListPage" in schemas


def test_get_grounding_prompt():
    prompt = get_grounding_prompt("Generate a nav header with UiNavHeader", ["UiNavHeader"])
    assert "UiNavHeader" in prompt
    assert "primaryLinks" in prompt


def test_validate_vnr_semantics_broad_selector():
    broad_code = """
    class NestedItem {
        bind title: "a | text";
    }
    reconstruct "#grid" -> UiTableListPage {
        child tableRows extends NestedItem {
            selector: "table table tr";
        }
    }
    """
    status, msg = validate_vnr_semantics(broad_code)
    assert status == ValidationStatus.INVALID
    assert "Overly broad nested selector" in msg


def test_validate_vnr_semantics_valid_code():
    valid_code = """
    class Item {
        bind title: "a | text";
    }
    reconstruct "#grid" -> UiTableListPage {
        child tableRows extends Item {
            selector: "tr.item-row";
        }
    }
    """
    status, msg = validate_vnr_semantics(valid_code)
    assert status == ValidationStatus.VALID
    assert msg == ""
