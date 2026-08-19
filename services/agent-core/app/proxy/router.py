"""
AegisAgent-AI :: Multi-Provider Model Router
Tries a free-tier cloud provider first (if a key is configured), falls back
to local Ollama automatically. Zero-cost by default: with no API key set,
it routes straight to Ollama, matching Simhadri's existing local-inference
stack (Jarvis, SimhaOps).
"""
import os
import httpx

NVIDIA_NIM_API_KEY = os.getenv("NVIDIA_NIM_API_KEY", "")
NVIDIA_NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "nvidia/nemotron-3-super-120b-a12b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "qwen2.5-coder:7b")


async def route_completion(prompt: str, system: str = "") -> dict:
    """Returns {"text": str, "provider": str} — tries NIM, falls back to Ollama."""
    if NVIDIA_NIM_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    NVIDIA_NIM_URL,
                    headers={"Authorization": f"Bearer {NVIDIA_NIM_API_KEY}"},
                    json={
                        "model": PRIMARY_MODEL,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                        "max_tokens": 512,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return {"text": data["choices"][0]["message"]["content"], "provider": "nvidia_nim"}
        except Exception:
            pass  # fall through to local Ollama

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": FALLBACK_MODEL, "prompt": f"{system}\n\n{prompt}", "stream": False},
            )
            resp.raise_for_status()
            data = resp.json()
            return {"text": data.get("response", ""), "provider": "ollama_local"}
    except Exception as e:
        return {"text": "", "provider": "none", "error": str(e)}
