from enum import Enum


class LLMProviderType(Enum):
    WATSONX = "watsonx"
    OPENAI = "openai"
    RITS = "rits"
    OLLAMA = "ollama"
    LITELLM = "litellm"
