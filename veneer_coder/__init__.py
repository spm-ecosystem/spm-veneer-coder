"""
veneer_coder package
Subagent runtime, compiler integration, extraction, engine abstraction, and evaluation helpers for Veneer Coder.
"""

from veneer_coder.compiler import ValidationStatus, compile_vnr, resolve_spm_cli
from veneer_coder.extraction import extract_code_block, extract_vnr_code
from veneer_coder.ollama import query_ollama
from veneer_coder.agent import run_agent, VeneerAgentError
from veneer_coder.engine import BaseLLMEngine, EngineResponse, OllamaEngine, MockEngine
from veneer_coder.benchmark import BenchmarkRunner, BenchmarkReport, TestCaseResult

__all__ = [
    "ValidationStatus",
    "compile_vnr",
    "resolve_spm_cli",
    "extract_code_block",
    "extract_vnr_code",
    "query_ollama",
    "run_agent",
    "VeneerAgentError",
    "BaseLLMEngine",
    "EngineResponse",
    "OllamaEngine",
    "MockEngine",
    "BenchmarkRunner",
    "BenchmarkReport",
    "TestCaseResult",
]
