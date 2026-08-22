"""
Engine abstraction layer for LLM inference.
Provides a unified interface for Ollama, Mock, and future LLM providers.
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
import urllib.request
import urllib.error


@dataclass
class EngineResponse:
    """Rich metadata response returned by an LLM engine."""
    text: str
    latency_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    tokens_per_second: float | None = None
    raw_metadata: dict | None = None


class BaseLLMEngine(ABC):
    """Abstract base class for all LLM inference engines."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None) -> EngineResponse:
        """Generate response text and inference metrics for a given prompt."""
        pass


class OllamaEngine(BaseLLMEngine):
    """Engine driver for local Ollama instances."""

    def __init__(self, model_name: str = "veneer-coder", api_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.api_url = api_url.rstrip("/")

    def generate(self, prompt: str, system_prompt: str | None = None) -> EngineResponse:
        endpoint = f"{self.api_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        start_time = time.perf_counter()

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise RuntimeError(f"Ollama connection error at {endpoint}: {e}") from e

        end_time = time.perf_counter()
        total_latency_ms = (end_time - start_time) * 1000.0

        response_text = data.get("response", "")
        eval_count = data.get("eval_count")
        eval_duration_ns = data.get("eval_duration")

        tokens_per_sec = None
        if eval_count and eval_duration_ns and eval_duration_ns > 0:
            tokens_per_sec = eval_count / (eval_duration_ns / 1e9)

        return EngineResponse(
            text=response_text,
            latency_ms=total_latency_ms,
            prompt_tokens=data.get("prompt_eval_count"),
            completion_tokens=eval_count,
            tokens_per_second=tokens_per_sec,
            raw_metadata=data,
        )


class MockEngine(BaseLLMEngine):
    """Mock engine for fast offline tests."""

    def __init__(self, predefined_response: str | None = None):
        self.predefined_response = predefined_response or """
class SampleCard {
    bind title: "h3 | text";
}
"""

    def generate(self, prompt: str, system_prompt: str | None = None) -> EngineResponse:
        return EngineResponse(
            text=self.predefined_response,
            latency_ms=1.5,
            prompt_tokens=10,
            completion_tokens=20,
            tokens_per_second=200.0,
            raw_metadata={"mock": True},
        )
