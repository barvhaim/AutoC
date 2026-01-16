"""Embeddings client initialization and configuration module."""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from backend.embeddings.provider_type import EmbeddingsProviderType

load_dotenv()

EMBEDDINGS_PROVIDER = EmbeddingsProviderType(
    os.getenv("EMBEDDINGS_PROVIDER", EmbeddingsProviderType.OLLAMA.value)
)


def _get_base_llm_settings(model_name: str) -> Dict:
    if EMBEDDINGS_PROVIDER == EmbeddingsProviderType.OLLAMA:
        return {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "model": model_name,
        }
    if EMBEDDINGS_PROVIDER == EmbeddingsProviderType.WATSONX:
        config = {
            "model_id": model_name,
            "url": os.getenv(
                "WATSONX_API_ENDPOINT", "https://us-south.ml.cloud.ibm.com"
            ),
            "project_id": os.getenv("WATSONX_PROJECT_ID"),
            "params": {
                "truncate_input_tokens": int(
                    os.getenv("WATSONX_TRUNCATE_INPUT_TOKENS", "3")
                ),
                "return_options": {"input_text": True},
            },
            "apikey": os.getenv("WATSONX_API_KEY"),
        }

        return config

    raise ValueError(f"Unsupported embeddings provider: {EMBEDDINGS_PROVIDER}")


def get_embeddings_client() -> Any:
    if EMBEDDINGS_PROVIDER == EmbeddingsProviderType.OLLAMA:
        model_name = os.getenv("EMBEDDINGS_MODEL_NAME", "mxbai-embed-large")
        from langchain_ollama import OllamaEmbeddings

        return OllamaEmbeddings(**_get_base_llm_settings(model_name=model_name))
    if EMBEDDINGS_PROVIDER == EmbeddingsProviderType.WATSONX:
        model_name = os.getenv(
            "EMBEDDINGS_MODEL_NAME", "ibm/granite-embedding-107m-multilingual"
        )
        from langchain_ibm import WatsonxEmbeddings

        return WatsonxEmbeddings(**_get_base_llm_settings(model_name=model_name))

    raise ValueError(f"Unsupported embeddings provider: {EMBEDDINGS_PROVIDER}")
