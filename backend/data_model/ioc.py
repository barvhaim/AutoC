"""IOC data models and type definitions."""

from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class IOCType(str, Enum):
    URL = "Domain or URL"
    IP = "IP Address"
    MD5 = "MD5 Hash"
    SHA256 = "SHA256 Hash"
    CHROME_EXTENSION = "Chrome Extension ID"
    BITCOIN_WALLET_ADDRESS = "Bitcoin Wallet Address"


class ExtractionMethod(str, Enum):
    """Method used to extract the IOC."""

    REGEX = "regex"
    LLM = "llm"
    HYBRID = "hybrid"  # Regex extraction + LLM validation


class ConfidenceLevel(str, Enum):
    """Confidence level categories."""

    VERY_HIGH = "very_high"  # 95-100%
    HIGH = "high"  # 85-94%
    MEDIUM = "medium"  # 70-84%
    LOW = "low"  # 50-69%
    VERY_LOW = "very_low"  # <50%


class IOC(BaseModel):
    """
    Indicator of Compromise with extraction metadata.

    Enhanced to support hybrid extraction with confidence scoring.
    """

    type: IOCType
    value: str

    # Extraction metadata (optional for backward compatibility)
    confidence: Optional[float] = Field(
        default=None, ge=0, le=100, description="Confidence score 0-100"
    )
    confidence_level: Optional[ConfidenceLevel] = Field(
        default=None, description="Confidence category"
    )
    extraction_method: Optional[ExtractionMethod] = Field(
        default=None, description="How IOC was extracted"
    )

    # Context information
    context: Optional[str] = Field(default=None, description="Surrounding text context")
    position: Optional[int] = Field(
        default=None, description="Character position in source text"
    )

    # Validation metadata
    validated_by_llm: bool = Field(
        default=False, description="Whether LLM validated this IOC"
    )
    llm_explanation: Optional[str] = Field(
        default=None, description="LLM validation explanation"
    )

    # Normalization
    normalized_value: Optional[str] = Field(
        default=None, description="Normalized/deobfuscated value"
    )

    # Additional metadata
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional extraction metadata"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_schema_extra = {
            "example": {
                "type": "Domain or URL",
                "value": "hxxps://evil[.]com",
                "confidence": 95.5,
                "confidence_level": "very_high",
                "extraction_method": "regex",
                "context": "The malware connects to hxxps://evil[.]com for C2",
                "position": 150,
                "validated_by_llm": False,
                "normalized_value": "https://evil.com",
                "metadata": {
                    "has_defanging": True,
                    "threat_keywords": ["malware", "C2"],
                },
            }
        }
