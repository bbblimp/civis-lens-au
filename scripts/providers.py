from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request

from common import load_repo_env_files


OPENAI_ENDPOINT = "https://api.openai.com/v1/responses"
ANTHROPIC_ENDPOINT = "https://api.anthropic.com/v1/messages"
GOOGLE_ENDPOINT_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


class ProviderError(RuntimeError):
    pass


@dataclass
class ProviderExecution:
    provider: str
    configured_model: str
    resolved_model: str
    endpoint: str
    request_payload: dict[str, Any]
    response_payload: dict[str, Any]
    output_text: str
    request_id: str | None
    usage: dict[str, Any] | None


def execute_prompt(model_config: dict[str, Any], prompt_text: str) -> ProviderExecution:
    load_repo_env_files()
    provider = str(model_config.get("provider", "")).strip().lower()
    if provider == "openai":
        return _execute_openai(model_config, prompt_text)
    if provider == "anthropic":
        return _execute_anthropic(model_config, prompt_text)
    if provider == "google":
        return _execute_google(model_config, prompt_text)
    raise ProviderError(f"Unsupported provider: {provider or '<missing>'}")


def _execute_openai(model_config: dict[str, Any], prompt_text: str) -> ProviderExecution:
    resolved_model = _resolve_model_name(
        configured_model=str(model_config.get("model", "")),
        env_names=["OPENAI_MODEL"],
        provider_label="openai",
    )
    payload = {
        "model": resolved_model,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt_text,
                    }
                ],
            }
        ],
    }
    parameters = _normalized_parameters(model_config)
    if "temperature" in parameters:
        payload["temperature"] = parameters["temperature"]
    if "max_output_tokens" in parameters:
        payload["max_output_tokens"] = parameters["max_output_tokens"]

    api_key = _require_env(["OPENAI_API_KEY"], "OpenAI")
    response_payload, response_headers = _post_json(
        url=OPENAI_ENDPOINT,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        payload=payload,
    )
    output_text = _extract_openai_text(response_payload)
    return ProviderExecution(
        provider="openai",
        configured_model=str(model_config.get("model", "")),
        resolved_model=resolved_model,
        endpoint=OPENAI_ENDPOINT,
        request_payload=payload,
        response_payload=response_payload,
        output_text=output_text,
        request_id=response_headers.get("x-request-id"),
        usage=_dict_or_none(response_payload.get("usage")),
    )


def _execute_anthropic(model_config: dict[str, Any], prompt_text: str) -> ProviderExecution:
    resolved_model = _resolve_model_name(
        configured_model=str(model_config.get("model", "")),
        env_names=["ANTHROPIC_MODEL"],
        provider_label="anthropic",
    )
    parameters = _normalized_parameters(model_config)
    payload = {
        "model": resolved_model,
        "messages": [
            {
                "role": "user",
                "content": prompt_text,
            }
        ],
        "max_tokens": int(parameters.get("max_output_tokens", 4096)),
    }
    if "temperature" in parameters:
        payload["temperature"] = parameters["temperature"]

    api_key = _require_env(["ANTHROPIC_API_KEY"], "Anthropic")
    response_payload, response_headers = _post_json(
        url=ANTHROPIC_ENDPOINT,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        payload=payload,
    )
    output_text = _extract_anthropic_text(response_payload)
    return ProviderExecution(
        provider="anthropic",
        configured_model=str(model_config.get("model", "")),
        resolved_model=resolved_model,
        endpoint=ANTHROPIC_ENDPOINT,
        request_payload=payload,
        response_payload=response_payload,
        output_text=output_text,
        request_id=response_headers.get("request-id"),
        usage=_dict_or_none(response_payload.get("usage")),
    )


def _execute_google(model_config: dict[str, Any], prompt_text: str) -> ProviderExecution:
    resolved_model = _resolve_model_name(
        configured_model=str(model_config.get("model", "")),
        env_names=["GEMINI_MODEL", "GOOGLE_MODEL"],
        provider_label="google",
    )
    parameters = _normalized_parameters(model_config)
    generation_config: dict[str, Any] = {}
    if "temperature" in parameters:
        generation_config["temperature"] = parameters["temperature"]
    if "max_output_tokens" in parameters:
        generation_config["maxOutputTokens"] = parameters["max_output_tokens"]

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt_text}],
            }
        ]
    }
    if generation_config:
        payload["generationConfig"] = generation_config

    api_key = _require_env(["GEMINI_API_KEY", "GOOGLE_API_KEY"], "Google Gemini")
    endpoint = GOOGLE_ENDPOINT_TEMPLATE.format(model=parse.quote(resolved_model, safe=""))
    response_payload, response_headers = _post_json(
        url=f"{endpoint}?key={parse.quote(api_key, safe='')}",
        headers={"Content-Type": "application/json"},
        payload=payload,
    )
    output_text = _extract_google_text(response_payload)
    return ProviderExecution(
        provider="google",
        configured_model=str(model_config.get("model", "")),
        resolved_model=resolved_model,
        endpoint=endpoint,
        request_payload=payload,
        response_payload=response_payload,
        output_text=output_text,
        request_id=response_headers.get("x-request-id"),
        usage=_dict_or_none(response_payload.get("usageMetadata")),
    )


def _normalized_parameters(model_config: dict[str, Any]) -> dict[str, Any]:
    raw_parameters = model_config.get("parameters", {})
    if not isinstance(raw_parameters, dict):
        return {}

    normalized: dict[str, Any] = {}
    if "temperature" in raw_parameters and raw_parameters["temperature"] is not None:
        normalized["temperature"] = raw_parameters["temperature"]
    if (
        "max_output_tokens" in raw_parameters
        and raw_parameters["max_output_tokens"] is not None
    ):
        normalized["max_output_tokens"] = int(raw_parameters["max_output_tokens"])
    return normalized


def _resolve_model_name(
    configured_model: str, env_names: list[str], provider_label: str
) -> str:
    cleaned = configured_model.strip()
    if cleaned and cleaned != "set-me":
        return cleaned
    for env_name in env_names:
        candidate = os.getenv(env_name, "").strip()
        if candidate:
            return candidate
    env_list = ", ".join(env_names)
    raise ProviderError(
        f"No model configured for {provider_label}. Set models/registry.yaml or export one of: {env_list}"
    )


def _require_env(env_names: list[str], provider_label: str) -> str:
    for env_name in env_names:
        candidate = os.getenv(env_name, "").strip()
        if candidate:
            return candidate
    env_list = ", ".join(env_names)
    raise ProviderError(
        f"Missing API key for {provider_label}. Export one of: {env_list}"
    )


def _post_json(
    url: str, headers: dict[str, str], payload: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, str]]:
    request_body = json.dumps(payload).encode("utf-8")
    req = request.Request(url=url, data=request_body, headers=headers, method="POST")

    try:
        with request.urlopen(req, timeout=300) as response:
            body = response.read().decode("utf-8")
            parsed = json.loads(body)
            if not isinstance(parsed, dict):
                raise ProviderError("Provider returned non-object JSON.")
            return parsed, {key.lower(): value for key, value in response.headers.items()}
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ProviderError(
            f"Provider request failed with HTTP {exc.code}: {body}"
        ) from exc
    except error.URLError as exc:
        raise ProviderError(f"Provider request failed: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise ProviderError("Provider response was not valid JSON.") from exc


def _extract_openai_text(response_payload: dict[str, Any]) -> str:
    if isinstance(response_payload.get("output_text"), str):
        text = response_payload["output_text"].strip()
        if text:
            return text

    texts: list[str] = []
    for item in response_payload.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            if content.get("type") == "output_text":
                text = str(content.get("text", "")).strip()
                if text:
                    texts.append(text)

    if texts:
        return "\n\n".join(texts)
    raise ProviderError("OpenAI response did not contain extractable output text.")


def _extract_anthropic_text(response_payload: dict[str, Any]) -> str:
    texts: list[str] = []
    for block in response_payload.get("content", []):
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text":
            text = str(block.get("text", "")).strip()
            if text:
                texts.append(text)

    if texts:
        return "\n\n".join(texts)
    raise ProviderError("Anthropic response did not contain extractable text blocks.")


def _extract_google_text(response_payload: dict[str, Any]) -> str:
    texts: list[str] = []
    for candidate in response_payload.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        content = candidate.get("content", {})
        if not isinstance(content, dict):
            continue
        for part in content.get("parts", []):
            if not isinstance(part, dict):
                continue
            text = str(part.get("text", "")).strip()
            if text:
                texts.append(text)

    if texts:
        return "\n\n".join(texts)
    raise ProviderError("Google response did not contain extractable text parts.")


def _dict_or_none(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    return None
