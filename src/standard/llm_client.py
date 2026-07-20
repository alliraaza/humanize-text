"""OpenAI-compatible LLM client with multi-provider config resolution."""

from __future__ import annotations

import os
from typing import Any

import httpx

PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "api_key_field": "deepseek_api_key",
        "display_name": "DeepSeek",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "deepseek/deepseek-chat",
        "api_key_field": "openrouter_api_key",
        "display_name": "OpenRouter",
    },
    "litellm": {
        "base_url": "",
        "model": "deepseek/deepseek-chat",
        "api_key_field": "litellm_api_key",
        "display_name": "LiteLLM",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "model": "",
        "api_key_field": "ollama_api_key",
        "display_name": "Ollama",
    },
}

DEFAULT_PROVIDER = "deepseek"


def normalize_chat_completions_url(base_url: str) -> str:
    """Ensure base_url points at the chat completions endpoint."""
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def resolve_llm_config(config: dict) -> dict[str, Any]:
    """Merge TOML config and environment variables into resolved LLM settings."""
    llm_cfg = config.get("llm", {})
    pipeline_cfg = config.get("pipeline", {})
    api_keys = config.get("api_keys", {})

    provider = llm_cfg.get("provider") or DEFAULT_PROVIDER
    if env_provider := os.environ.get("LLM_PROVIDER"):
        provider = env_provider

    if provider not in PROVIDER_DEFAULTS:
        raise ValueError(
            f"Unsupported LLM provider: {provider!r}. "
            f"Supported: {', '.join(PROVIDER_DEFAULTS)}"
        )

    defaults = PROVIDER_DEFAULTS[provider]

    base_url = llm_cfg.get("base_url") or defaults["base_url"]
    if env_base_url := os.environ.get("LLM_BASE_URL"):
        base_url = env_base_url

    model = llm_cfg.get("model") or pipeline_cfg.get("model") or defaults["model"]
    if env_model := os.environ.get("LLM_MODEL"):
        model = env_model

    temperature = llm_cfg.get("temperature", pipeline_cfg.get("temperature", 1.3))

    top_p = llm_cfg.get("top_p",0.92)
    top_k = llm_cfg.get("top_k",40)

    api_key_field = defaults["api_key_field"]
    api_key = api_keys.get(api_key_field, "")

    if env_api_key := os.environ.get("LLM_API_KEY"):
        api_key = env_api_key
    elif provider == "openrouter" and (or_key := os.environ.get("OPENROUTER_API_KEY")):
        api_key = or_key
    elif provider == "deepseek" and (ds_key := os.environ.get("DEEPSEEK_API_KEY")):
        api_key = ds_key

    if not api_key and provider not in ("litellm", "ollama"):
        raise ValueError(
            f"Missing API key for provider {provider!r}. "
            f"Set api_keys.{api_key_field} in config or LLM_API_KEY env var."
        )

    extra_headers: dict[str, str] = {}
    if http_referer := llm_cfg.get("http_referer"):
        extra_headers["HTTP-Referer"] = http_referer
    if app_title := llm_cfg.get("app_title"):
        extra_headers["X-Title"] = app_title

    return {
        "provider": provider,
        "display_name": defaults["display_name"],
        "base_url": base_url,
        "model": model,
        "temperature": temperature,
        # "top_p":top_p,
        "api_key": api_key,
        "extra_headers": extra_headers or None,
    }

def resolve_translators_config(config: dict) -> dict[str, Any]:
    """Merge TOML config and environment variables into resolved LLM settings."""
    trans_cfg = config.get("translator", {})
    pipeline_cfg = config.get("pipeline", {})
    api_keys = config.get("api_keys", {})
    llm_cfg = config.get("llm", {})

    provider = trans_cfg.get("provider") or DEFAULT_PROVIDER
    if env_provider := os.environ.get("LLM_PROVIDER"):
        provider = env_provider

    if provider not in PROVIDER_DEFAULTS:
        raise ValueError(
            f"Unsupported LLM provider: {provider!r}. "
            f"Supported: {', '.join(PROVIDER_DEFAULTS)}"
        )

    defaults = PROVIDER_DEFAULTS[provider]

    base_url = trans_cfg.get("base_url") or defaults["base_url"]
    if env_base_url := os.environ.get("LLM_BASE_URL"):
        base_url = env_base_url

    model = trans_cfg.get("model") or llm_cfg.get("model") or defaults["model"]
    if env_model := os.environ.get("LLM_MODEL"):
        model = env_model

    timeout = trans_cfg.get("timeout") or llm_cfg.get("timeout") or defaults["timeout"]
    temperature = trans_cfg.get("temperature", pipeline_cfg.get("temperature", 0.5))
    max_tokens = trans_cfg.get("max_tokens") or llm_cfg.get("max_tokens") or defaults["max_tokens"]


    top_p = trans_cfg.get("top_p",0.92)
    top_k = trans_cfg.get("top_k",40)

    api_key_field = defaults["api_key_field"]
    api_key = api_keys.get(api_key_field, "")

    if env_api_key := os.environ.get("LLM_API_KEY"):
        api_key = env_api_key
    elif provider == "openrouter" and (or_key := os.environ.get("OPENROUTER_API_KEY")):
        api_key = or_key
    elif provider == "deepseek" and (ds_key := os.environ.get("DEEPSEEK_API_KEY")):
        api_key = ds_key

    if not api_key and provider not in ("litellm", "ollama"):
        raise ValueError(
            f"Missing API key for provider {provider!r}. "
            f"Set api_keys.{api_key_field} in config or LLM_API_KEY env var."
        )

    extra_headers: dict[str, str] = {}
    if http_referer := trans_cfg.get("http_referer"):
        extra_headers["HTTP-Referer"] = http_referer
    if app_title := trans_cfg.get("app_title"):
        extra_headers["X-Title"] = app_title

    return {
        "provider": provider,
        "display_name": defaults["display_name"],
        "base_url": base_url,
        "model": model,
        "temperature": temperature,
        "top_p":top_p,
        "top_k":top_k,
        "timeout":timeout,
        "api_key": api_key,
        "extra_headers": extra_headers or None,
        "max_tokens": max_tokens,
    }


def chat_completions(
    messages: list[dict],
    *,
    api_key: str,
    base_url: str,
    model: str,
    temperature: float| None = 1.3,
    extra_headers: dict | None = None,
    provider: str | None = None,
    top_p: float | None = None,
    top_k: float | None = None,
    timeout: int |None = 600,

) -> str:
    """Call an OpenAI-compatible /chat/completions endpoint."""
    if provider == "litellm":
        return _litellm_chat_completions(
            messages,
            api_key=api_key,
            model=model,
            temperature=temperature,
            top_p=top_p,
            timeout=timeout,
        )

    if not api_key and provider not in ("litellm", "ollama"):
        raise ValueError("API key is required for LLM chat completions.")

    url = normalize_chat_completions_url(base_url)
    headers = {"Authorization": f"Bearer {api_key}"}
    if extra_headers:
        headers.update(extra_headers)

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if top_p is not None:
        payload["top_p"] = top_p
    if top_k is not None:
        payload["top_k"] = top_k

    # print (f"url: {url} : {payload}")


    # response = httpx.post(url, headers=headers, json=payload, timeout=timeout)
    # # print(f"res: "+response.text)
    # response.raise_for_status()
    # return response.json()["choices"][0]["message"]["content"].strip()

    try:
        # 1. Make the request
        response = httpx.post(url, headers=headers, json=payload, timeout=timeout)

        # 2. Check for HTTP errors (400, 429, 500, etc.)
        response.raise_for_status()

        # 3. Safely parse the JSON structure
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        if content is None:
            print("Warning: Model returned an empty response body or a safety refusal.")
            return ""

        return content.strip()

    except httpx.HTTPStatusError as e:
        # This captures the EXACT reason OpenRouter failed (e.g., specific 400 or 429 message)
        error_message = e.response.text
        print(f"API Error ({e.response.status_code}): {error_message}")

        # Decide how your app should fallback
        if e.response.status_code == 429:
            print("Rate limit reached. Consider adding a sleep delay or retrying.")
        elif e.response.status_code == 400:
            print("Bad Request. Check your model name string or payload formatting.")

        return ""  # Or raise your own custom error

    except httpx.TimeoutException:
        print("Error: The request timed out.")
        return ""

    except httpx.RequestError as e:
        print(f"Network Error: A connection issue occurred while requesting {e.request.url}.")
        return ""

    except (KeyError, IndexError) as e:
        # Handles cases where the model succeeds but the JSON structure is unexpected
        print(f"Data Structure Error: The API response format changed or is missing keys: {e}")
        print(f"Raw response was: {response.text}")
        return ""


def _litellm_chat_completions(
    messages: list[dict],
    *,
    api_key: str,
    model: str,
    temperature: float = 1.3,
    top_p: float | None = None,
    timeout: int = 600,
) -> str:
    """Route through LiteLLM SDK for 100+ provider support."""
    import litellm

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "drop_params": True,
        "timeout": timeout,
    }
    if api_key:
        kwargs["api_key"] = api_key
    if top_p is not None:
        kwargs["top_p"] = top_p

    response = litellm.completion(**kwargs)
    return response.choices[0].message.content.strip()
