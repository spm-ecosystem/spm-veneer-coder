"""
Ollama HTTP API client wrapper.
"""

from __future__ import annotations

import json
import urllib.request
import sys

DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"


def query_ollama(prompt: str, model: str = "veneer-coder", url: str = DEFAULT_OLLAMA_URL, timeout: int = 90) -> str:
    """Sends a completion request to Ollama generate API."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            res = json.loads(response.read().decode("utf-8"))
            return res.get("response", "").strip()
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Ollama server at {url}: {e}") from e
