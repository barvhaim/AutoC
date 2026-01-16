"""Configuration for hybrid IOC extraction system."""

from typing import Dict, Optional
from pydantic import BaseModel, Field
from backend.data_model.ioc import IOCType


class IOCTypeConfig(BaseModel):
    """Configuration for a specific IOC type."""

    enable_regex: bool = Field(
        default=True, description="Enable regex extraction for this type"
    )
    enable_llm_fallback: bool = Field(
        default=True, description="Enable LLM fallback if regex fails"
    )
    confidence_boost: float = Field(
        default=0.0, ge=-20, le=20, description="Confidence adjustment for this type"
    )
    min_confidence_threshold: float = Field(
        default=50.0, ge=0, le=100, description="Minimum confidence to accept"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "enable_regex": True,
                "enable_llm_fallback": False,
                "confidence_boost": 5.0,
                "min_confidence_threshold": 70.0,
            }
        }


class HybridExtractionConfig(BaseModel):
    """
    Configuration for hybrid IOC extraction system.

    Controls thresholds, LLM usage, and performance settings.
    """

    # Confidence thresholds for decision making
    direct_accept_threshold: float = Field(
        default=95.0,
        ge=0,
        le=100,
        description="Confidence threshold for direct accept (no LLM)",
    )
    context_check_threshold: float = Field(
        default=85.0, ge=0, le=100, description="Confidence threshold for context check"
    )
    llm_validation_threshold: float = Field(
        default=70.0, ge=0, le=100, description="Minimum confidence for LLM validation"
    )

    # LLM settings
    enable_llm_validation: bool = Field(
        default=True, description="Enable LLM validation for ambiguous IOCs"
    )
    llm_batch_size: int = Field(
        default=10, ge=1, le=50, description="Number of IOCs to validate per LLM call"
    )
    llm_timeout_seconds: int = Field(
        default=30, ge=5, le=120, description="Timeout for LLM calls"
    )
    use_deep_validation: bool = Field(
        default=False,
        description="Use deep validation with explanations (slower, more expensive)",
    )

    # Performance settings
    enable_caching: bool = Field(
        default=True, description="Enable caching of LLM validation results"
    )
    cache_ttl_hours: int = Field(
        default=24, ge=1, le=168, description="Cache time-to-live in hours"
    )
    parallel_processing: bool = Field(
        default=True, description="Enable parallel processing of IOC types"
    )
    max_workers: int = Field(
        default=3, ge=1, le=10, description="Maximum parallel workers"
    )

    # Context analysis settings
    context_window_radius: int = Field(
        default=100,
        ge=50,
        le=500,
        description="Characters before/after IOC for context",
    )
    section_search_radius: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="Characters to search backwards for section headers",
    )

    # IOC type specific configurations
    ioc_type_configs: Dict[str, IOCTypeConfig] = Field(
        default_factory=lambda: {
            # Hash-based IOCs: Very reliable, no LLM needed
            "MD5 Hash": IOCTypeConfig(
                enable_regex=True,
                enable_llm_fallback=False,
                confidence_boost=0.0,
                min_confidence_threshold=90.0,
            ),
            "SHA256 Hash": IOCTypeConfig(
                enable_regex=True,
                enable_llm_fallback=False,
                confidence_boost=0.0,
                min_confidence_threshold=90.0,
            ),
            # Network IOCs: Reliable but may need context
            "IP Address": IOCTypeConfig(
                enable_regex=True,
                enable_llm_fallback=True,
                confidence_boost=0.0,
                min_confidence_threshold=70.0,
            ),
            # URLs/Domains: Context-dependent
            "Domain or URL": IOCTypeConfig(
                enable_regex=True,
                enable_llm_fallback=True,
                confidence_boost=0.0,
                min_confidence_threshold=70.0,
            ),
            # Cryptocurrency: Moderate reliability
            "Bitcoin Wallet Address": IOCTypeConfig(
                enable_regex=True,
                enable_llm_fallback=True,
                confidence_boost=0.0,
                min_confidence_threshold=75.0,
            ),
            # Browser extensions: High false positive rate
            "Chrome Extension ID": IOCTypeConfig(
                enable_regex=True,
                enable_llm_fallback=True,
                confidence_boost=-5.0,  # Reduce confidence due to false positives
                min_confidence_threshold=80.0,
            ),
        },
        description="Per-IOC-type configuration overrides",
    )

    # Metrics and monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    log_level: str = Field(
        default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    def get_ioc_type_config(self, ioc_type: IOCType) -> IOCTypeConfig:
        """
        Get configuration for a specific IOC type.

        Args:
            ioc_type: The IOC type

        Returns:
            IOCTypeConfig for the type, or default if not configured
        """
        return self.ioc_type_configs.get(
            ioc_type.value, IOCTypeConfig()  # Default config
        )

    def should_use_llm(self, confidence: float, ioc_type: IOCType) -> bool:
        """
        Determine if LLM validation should be used.

        Args:
            confidence: Current confidence score
            ioc_type: Type of IOC

        Returns:
            True if LLM validation should be used
        """
        if not self.enable_llm_validation:
            return False

        type_config = self.get_ioc_type_config(ioc_type)
        if not type_config.enable_llm_fallback:
            return False

        # Use LLM if below direct accept threshold
        if confidence < self.direct_accept_threshold:
            # But only if above minimum validation threshold
            return confidence >= self.llm_validation_threshold

        return False

    def validate_thresholds(self) -> bool:
        """
        Validate that thresholds are in correct order.

        Returns:
            True if valid
        """
        return (
            self.llm_validation_threshold
            <= self.context_check_threshold
            <= self.direct_accept_threshold
        )

    @classmethod
    def create_fast_config(cls) -> "HybridExtractionConfig":
        """
        Create a configuration optimized for speed.

        Returns:
            Fast configuration
        """
        return cls(
            direct_accept_threshold=90.0,  # Lower threshold
            context_check_threshold=80.0,
            llm_validation_threshold=60.0,
            enable_llm_validation=True,
            llm_batch_size=20,  # Larger batches
            use_deep_validation=False,
            parallel_processing=True,
            max_workers=5,
        )

    @classmethod
    def create_accurate_config(cls) -> "HybridExtractionConfig":
        """
        Create a configuration optimized for accuracy.

        Returns:
            Accurate configuration
        """
        return cls(
            direct_accept_threshold=98.0,  # Higher threshold
            context_check_threshold=90.0,
            llm_validation_threshold=75.0,
            enable_llm_validation=True,
            llm_batch_size=5,  # Smaller batches for better quality
            use_deep_validation=True,  # Use detailed validation
            parallel_processing=True,
            max_workers=3,
        )

    @classmethod
    def create_efficient_config(cls) -> "HybridExtractionConfig":
        """
        Create a configuration optimized for efficiency.

        Returns:
            Efficiency-optimized configuration
        """
        return cls(
            direct_accept_threshold=92.0,
            context_check_threshold=82.0,
            llm_validation_threshold=70.0,
            enable_llm_validation=True,
            llm_batch_size=15,  # Balance batch size
            use_deep_validation=False,
            enable_caching=True,  # Maximize caching
            cache_ttl_hours=48,  # Longer cache
            parallel_processing=True,
            max_workers=3,
        )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "direct_accept_threshold": 95.0,
                "context_check_threshold": 85.0,
                "llm_validation_threshold": 70.0,
                "enable_llm_validation": True,
                "llm_batch_size": 10,
                "enable_caching": True,
                "parallel_processing": True,
            }
        }


if __name__ == "__main__":
    import json

    # Test default configuration
    config = HybridExtractionConfig()
    print("Default Configuration:")
    print(json.dumps(config.model_dump(), indent=2))
    print(f"\nThresholds valid: {config.validate_thresholds()}")

    # Test preset configurations
    print("\n" + "=" * 50)
    print("\nFast Configuration:")
    fast_config = HybridExtractionConfig.create_fast_config()
    print(f"  Direct accept: {fast_config.direct_accept_threshold}%")
    print(f"  LLM batch size: {fast_config.llm_batch_size}")
    print(f"  Max workers: {fast_config.max_workers}")

    print("\nAccurate Configuration:")
    accurate_config = HybridExtractionConfig.create_accurate_config()
    print(f"  Direct accept: {accurate_config.direct_accept_threshold}%")
    print(f"  Deep validation: {accurate_config.use_deep_validation}")
    print(f"  LLM batch size: {accurate_config.llm_batch_size}")

    print("\nEfficiency-Optimized Configuration:")
    efficient_config = HybridExtractionConfig.create_efficient_config()
    print(f"  Direct accept: {efficient_config.direct_accept_threshold}%")
    print(f"  Cache TTL: {efficient_config.cache_ttl_hours}h")
    print(f"  LLM batch size: {efficient_config.llm_batch_size}")

    # Test IOC type config
    print("\n" + "=" * 50)
    print("\nIOC Type Configurations:")
    for ioc_type in ["MD5 Hash", "Domain or URL", "Chrome Extension ID"]:
        type_config = config.ioc_type_configs.get(ioc_type)
        if type_config:
            print(f"\n{ioc_type}:")
            print(f"  Regex enabled: {type_config.enable_regex}")
            print(f"  LLM fallback: {type_config.enable_llm_fallback}")
            print(f"  Confidence boost: {type_config.confidence_boost:+.1f}")
            print(f"  Min threshold: {type_config.min_confidence_threshold}%")
