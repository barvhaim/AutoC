"""LLM client initialization and configuration module."""

import os
from typing import Dict, Optional, Any
from dotenv import load_dotenv
from backend.llm.provider_type import LLMProviderType

load_dotenv()

LLM_PROVIDER = LLMProviderType(os.getenv("LLM_PROVIDER", LLMProviderType.WATSONX.value))


def _get_base_llm_settings(model_name: str, model_parameters: Optional[Dict]) -> Dict:
    if model_parameters is None:
        model_parameters = {}

    if LLM_PROVIDER == LLMProviderType.OLLAMA:
        parameters = {
            "temperature": model_parameters.get("temperature", 0.9),
            "top_k": model_parameters.get("top_k", 50),
            "top_p": model_parameters.get("top_p", 1.0),
            "num_predict": model_parameters.get("max_tokens", 100),
            "stop": model_parameters.get("stop_sequences", []),
            "repeat_penalty": model_parameters.get("repetition_penalty", 1.0),
        }

        return {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "model": model_name,
            **parameters,
        }

    if LLM_PROVIDER == LLMProviderType.OPENAI:
        parameters = {
            "max_tokens": model_parameters.get("max_tokens", 100),
            "temperature": model_parameters.get("temperature", 0),
            "stop": model_parameters.get("stop_sequences", []),
        }
        return {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": model_name,
            **parameters,
        }

    if LLM_PROVIDER == LLMProviderType.WATSONX:
        parameters = {
            "max_new_tokens": model_parameters.get("max_tokens", 100),
            "decoding_method": model_parameters.get("decoding_method", "greedy"),
            "temperature": model_parameters.get("temperature", 0.9),
            "repetition_penalty": model_parameters.get("repetition_penalty", 1.0),
            "top_k": model_parameters.get("top_k", 50),
            "top_p": model_parameters.get("top_p", 1.0),
            "stop_sequences": model_parameters.get("stop_sequences", []),
        }

        return {
            "url": os.getenv("WATSONX_API_ENDPOINT"),
            "project_id": os.getenv("WATSONX_PROJECT_ID"),
            "apikey": os.getenv("WATSONX_API_KEY"),
            "model_id": model_name,
            "params": parameters,
        }

    elif LLM_PROVIDER == LLMProviderType.RITS:
        rits_base_url = os.getenv("RITS_API_BASE_URL")

        parameters = {
            "max_tokens": model_parameters.get("max_tokens", 100),
            "temperature": model_parameters.get("temperature", 0.05),
            "repetition_penalty": model_parameters.get("repetition_penalty", 1.0),
            "top_k": model_parameters.get("top_k", 50),
            "top_p": model_parameters.get("top_p", 1.0),
            "stop": model_parameters.get("stop_sequences", []),
        }

        return {
            "base_url": f"{rits_base_url}/v1",
            "model": model_name,
            "api_key": os.getenv("RITS_API_KEY"),
            "extra_body": parameters,
        }

    raise ValueError(f"Incorrect LLM provider: {LLM_PROVIDER}")


def get_chat_llm_client(
    model_name: str = "meta-llama/llama-3-3-70b-instruct",
    model_parameters: Optional[Dict] = None,
) -> Any:
    if LLM_PROVIDER == LLMProviderType.OPENAI or LLM_PROVIDER == LLMProviderType.RITS:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            **_get_base_llm_settings(
                model_name=model_name, model_parameters=model_parameters
            )
        )

    if LLM_PROVIDER == LLMProviderType.WATSONX:
        from langchain_ibm import ChatWatsonx

        return ChatWatsonx(
            **_get_base_llm_settings(
                model_name=model_name, model_parameters=model_parameters
            )
        )

    if LLM_PROVIDER == LLMProviderType.OLLAMA:
        from langchain_ollama import ChatOllama

        return ChatOllama(
            **_get_base_llm_settings(
                model_name=model_name, model_parameters=model_parameters
            )
        )
    return None
