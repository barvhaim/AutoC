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

    elif LLM_PROVIDER == LLMProviderType.OPENAI:
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

    elif LLM_PROVIDER == LLMProviderType.WATSONX:
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
        model_to_url_path = {
            "mistralai/mixtral-8x22B-instruct-v0.1": "mixtral-8x22b-instruct-v01",
            "Qwen/Qwen2.5-72B-Instruct": "qwen2-5-72b-instruct",
            "meta-llama/llama-3-1-405b-instruct-fp8": "llama-3-1-405b-instruct-fp8",
            "deepseek-ai/DeepSeek-V3": "deepseek-v3",
            "meta-llama/llama-3-3-70b-instruct": "llama-3-3-70b-instruct",
            "ibm-granite/granite-3.1-8b-instruct": "granite-3-1-8b-instruct",
            "meta-llama/llama-4-maverick-17b-128e-instruct-fp8": "llama-4-mvk-17b-128e-fp8",
            "meta-llama/llama-4-scout-17b-16e": "llama-4-scout-17b-16e"
        }
        if model_name not in model_to_url_path:
            model_to_url_path[model_name] = model_name

        parameters = {
            "max_tokens": model_parameters.get("max_tokens", 100),
            "temperature": model_parameters.get("temperature", 0.9),
            "repetition_penalty": model_parameters.get("repetition_penalty", 1.0),
            "top_k": model_parameters.get("top_k", 50),
            "top_p": model_parameters.get("top_p", 1.0),
            "stop": model_parameters.get("stop_sequences", []),
        }

        return {
            "base_url": f"{rits_base_url}/{model_to_url_path[model_name]}/v1",
            "model": model_name,
            "api_key": "NotRequiredSinceWeAreLocal",
            "default_headers": {
                "RITS_API_KEY": os.getenv("RITS_API_KEY"),
            },
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

    elif LLM_PROVIDER == LLMProviderType.WATSONX:
        from langchain_ibm import ChatWatsonx

        return ChatWatsonx(
            **_get_base_llm_settings(
                model_name=model_name, model_parameters=model_parameters
            )
        )

    elif LLM_PROVIDER == LLMProviderType.OLLAMA:
        from langchain_ollama import ChatOllama

        return ChatOllama(
            **_get_base_llm_settings(
                model_name=model_name, model_parameters=model_parameters
            )
        )
    return None
