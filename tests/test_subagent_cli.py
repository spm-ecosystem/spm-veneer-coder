from pathlib import Path
from unittest.mock import patch, MagicMock
import json
import pytest
from scripts.subagent_cli import run_subagent_flow, main
from veneer_coder.compiler import ValidationStatus


def test_subagent_flow_invokes_grounding_and_semantics(tmp_path):
    mock_response = (
        "```vnr\n"
        "reconstruct \"#search\" -> UiSearchBar {\n"
        "    queryParamName: \"q\";\n"
        "}\n"
        "```\n\n"
        "```css\n"
        "/* styles */\n"
        "```"
    )

    with patch("scripts.subagent_cli.query_ollama", return_value=mock_response) as mock_query, \
         patch("scripts.subagent_cli.validate_vnr_semantics", return_value=(ValidationStatus.VALID, "")) as mock_val, \
         patch("scripts.subagent_cli.get_grounding_prompt", return_value="### Component Reference Schema: UiSearchBar") as mock_ground:

        res = run_subagent_flow(
            task_content="Search bar task",
            html_content='<form id="search"><input name="q"></form>',
            env_dir=tmp_path,
            model="test-model",
            max_retries=2
        )

        assert res["status"] == "success"
        assert (tmp_path / "generated.vnr").exists()
        assert (tmp_path / "content.css").exists()
        assert mock_ground.called
        assert mock_val.called
        assert mock_query.called


def test_subagent_flow_custom_styles_missing_css_retry(tmp_path):
    resp_without_css = (
        "```vnr\n"
        "reconstruct \"#custom\" -> UiWidget {\n"
        "    customStyles {\n"
        "        \"padding: 10px;\"\n"
        "    }\n"
        "}\n"
        "```"
    )
    resp_with_css = (
        "```vnr\n"
        "reconstruct \"#custom\" -> UiWidget {\n"
        "    customStyles {\n"
        "        \"padding: 10px;\"\n"
        "    }\n"
        "}\n"
        "```\n\n"
        "```css\n"
        ".custom { padding: 10px; }\n"
        "```"
    )

    with patch("scripts.subagent_cli.query_ollama", side_effect=[resp_without_css, resp_with_css]) as mock_query, \
         patch("scripts.subagent_cli.validate_vnr_semantics", return_value=(ValidationStatus.VALID, "")), \
         patch("scripts.subagent_cli.get_grounding_prompt", return_value=""):

        res = run_subagent_flow(
            task_content="Custom styles task",
            html_content='<div id="custom"></div>',
            env_dir=tmp_path,
            model="test-model",
            max_retries=3
        )

        assert res["status"] == "success"
        assert res["retries_used"] == 2
        assert len(res["errors_encountered"]) == 1
        assert "customStyles" in res["errors_encountered"][0]


def test_subagent_flow_validation_failure_and_retry(tmp_path):
    mock_resp = (
        "```vnr\n"
        "reconstruct \"#bad\" -> UiWidget {}\n"
        "```\n\n"
        "```css\n"
        "/* styles */\n"
        "```"
    )

    with patch("scripts.subagent_cli.query_ollama", return_value=mock_resp), \
         patch("scripts.subagent_cli.validate_vnr_semantics", side_effect=[(ValidationStatus.INVALID, "Bad selector"), (ValidationStatus.VALID, "")]), \
         patch("scripts.subagent_cli.get_grounding_prompt", return_value=""):

        res = run_subagent_flow(
            task_content="Test task",
            html_content="<div></div>",
            env_dir=tmp_path,
            model="test-model",
            max_retries=2
        )

        assert res["status"] == "success"
        assert res["retries_used"] == 2
        assert len(res["errors_encountered"]) == 1


def test_subagent_flow_max_retries_exceeded(tmp_path):
    mock_resp = (
        "```vnr\n"
        "reconstruct \"#bad\" -> UiWidget {}\n"
        "```\n\n"
        "```css\n"
        "/* styles */\n"
        "```"
    )

    with patch("scripts.subagent_cli.query_ollama", return_value=mock_resp), \
         patch("scripts.subagent_cli.validate_vnr_semantics", return_value=(ValidationStatus.INVALID, "Syntax error")), \
         patch("scripts.subagent_cli.get_grounding_prompt", return_value=""):

        res = run_subagent_flow(
            task_content="Test task",
            html_content="<div></div>",
            env_dir=tmp_path,
            model="test-model",
            max_retries=2
        )

        assert res["status"] == "failed"
        assert res["retries_used"] == 2
        assert len(res["errors"]) == 2


def test_subagent_flow_ollama_exception(tmp_path):
    with patch("scripts.subagent_cli.query_ollama", side_effect=RuntimeError("Connection refused")), \
         patch("scripts.subagent_cli.get_grounding_prompt", return_value=""):

        res = run_subagent_flow(
            task_content="Test task",
            html_content="<div></div>",
            env_dir=tmp_path,
            model="test-model",
            max_retries=2
        )

        assert res["status"] == "error"
        assert "Connection refused" in res["message"]


def test_main_cli_execution(tmp_path, capsys):
    payload = {
        "task": "Test task",
        "html": "<div id=\"test\"></div>",
        "env_dir": str(tmp_path)
    }

    mock_resp = (
        "```vnr\n"
        "reconstruct \"#test\" -> UiWidget {}\n"
        "```\n\n"
        "```css\n"
        "/* styles */\n"
        "```"
    )

    with patch("sys.argv", ["subagent_cli.py", "--input-json", json.dumps(payload)]), \
         patch("scripts.subagent_cli.query_ollama", return_value=mock_resp), \
         patch("scripts.subagent_cli.validate_vnr_semantics", return_value=(ValidationStatus.VALID, "")), \
         patch("scripts.subagent_cli.get_grounding_prompt", return_value=""):

        main()
        captured = capsys.readouterr()
        res = json.loads(captured.out)
        assert res["status"] == "success"
