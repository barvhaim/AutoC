"""Configuration for the multi-agent system"""

import os
from dotenv import load_dotenv

load_dotenv()


class AgentConfig:
    """Configuration settings for the agent system"""

    # System-wide settings
    AGENT_SYSTEM_ENABLED = os.getenv("AGENT_SYSTEM_ENABLED", "false").lower() == "true"
    PARALLEL_EXECUTION = os.getenv("AGENT_PARALLEL_EXECUTION", "true").lower() == "true"
    MAX_WORKERS = int(os.getenv("AGENT_MAX_WORKERS", "3"))
    MAX_RETRIES = int(os.getenv("AGENT_MAX_RETRIES", "3"))
    TIMEOUT_SECONDS = int(os.getenv("AGENT_TIMEOUT_SECONDS", "300"))

    # Orchestrator settings
    ORCHESTRATOR_LLM = os.getenv(
        "ORCHESTRATOR_LLM_MODEL", "meta-llama/llama-3-3-70b-instruct"
    )
    ORCHESTRATOR_MAX_CONCURRENT = int(
        os.getenv("ORCHESTRATOR_MAX_CONCURRENT_AGENTS", "5")
    )

    # Agent-specific timeouts (in seconds)
    PARSER_TIMEOUT = int(os.getenv("PARSER_AGENT_TIMEOUT", "60"))
    IOC_TIMEOUT = int(os.getenv("IOC_AGENT_TIMEOUT", "120"))
    QNA_TIMEOUT = int(os.getenv("QNA_AGENT_TIMEOUT", "180"))
    MITRE_TIMEOUT = int(os.getenv("MITRE_AGENT_TIMEOUT", "120"))
    KEYWORDS_TIMEOUT = int(os.getenv("KEYWORDS_AGENT_TIMEOUT", "30"))
    ENRICHMENT_TIMEOUT = int(os.getenv("ENRICHMENT_AGENT_TIMEOUT", "60"))

    @classmethod
    def is_enabled(cls) -> bool:
        """Check if agent system is enabled"""
        return cls.AGENT_SYSTEM_ENABLED

    @classmethod
    def get_timeout(cls, agent_name: str) -> int:
        """Get timeout for specific agent"""
        timeouts = {
            "parser": cls.PARSER_TIMEOUT,
            "ioc_hunter": cls.IOC_TIMEOUT,
            "qna": cls.QNA_TIMEOUT,
            "mitre": cls.MITRE_TIMEOUT,
            "keywords": cls.KEYWORDS_TIMEOUT,
            "enrichment": cls.ENRICHMENT_TIMEOUT,
        }
        return timeouts.get(agent_name, cls.TIMEOUT_SECONDS)


# Made with Bob
