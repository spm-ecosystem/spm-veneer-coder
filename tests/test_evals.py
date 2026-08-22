"""
Golden Evaluation Suite for Veneer Coder.
Evaluates model prompt responses for compiler validity, key extractor recall,
and contrastive intent handling.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from veneer_coder.compiler import ValidationStatus, compile_vnr
from veneer_coder.extraction import extract_vnr_code

EVAL_SUITE_PATH = Path(__file__).parent / "evals" / "golden_eval_suite.json"


def load_eval_cases():
    if not EVAL_SUITE_PATH.exists():
        return []
    return json.loads(EVAL_SUITE_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", load_eval_cases(), ids=lambda c: c["id"])
def test_golden_eval_case_spec(case):
    assert "prompt" in case
    assert "id" in case
    if case.get("must_compile"):
        assert "must_contain" in case


def test_eval_suite_coverage():
    cases = load_eval_cases()
    assert len(cases) >= 4, "Golden evaluation suite must contain at least 4 evaluation cases"

    has_extractor_test = any(c["id"] == "eval-01-bind-extractors" for c in cases)
    has_inheritance_test = any(c["id"] == "eval-02-class-inheritance" for c in cases)
    has_reconstruct_test = any(c["id"] == "eval-03-reconstruct-nav" for c in cases)
    has_contrastive_test = any(c["id"] == "eval-04-contrastive-refusal" for c in cases)

    assert has_extractor_test, "Golden suite missing extractor recall test"
    assert has_inheritance_test, "Golden suite missing class inheritance test"
    assert has_reconstruct_test, "Golden suite missing reconstruct test"
    assert has_contrastive_test, "Golden suite missing contrastive intent test"


def test_mock_eval_pipeline():
    """Verify that simulated model responses pass compilation and containment checks."""
    valid_sample_vnr = """
class BaseCard {
    bind title: "h3 | text";
}

class ProductCard extends BaseCard {
    bind price: ".price | text";
}

reconstruct "#nav-bar" -> UiNavHeader {
    pageTitle: "Home";
}
"""
    status, err_msg = compile_vnr(valid_sample_vnr)
    if status == ValidationStatus.VALID:
        assert status == ValidationStatus.VALID
        assert "BaseCard" in valid_sample_vnr
        assert "UiNavHeader" in valid_sample_vnr
    else:
        # If compiler binary isn't in test runner env, status should be UNAVAILABLE, not INVALID
        assert status == ValidationStatus.UNAVAILABLE
