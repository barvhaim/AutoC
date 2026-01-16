"""Regex-based IOC extraction with confidence scoring."""

import re
import logging
from typing import List, Dict, Pattern, Optional, Tuple
from dataclasses import dataclass
from backend.data_model.ioc import IOCType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RegexIOCMatch:
    """Represents a regex-matched IOC with metadata."""

    ioc_type: IOCType
    value: str
    position: int
    context_window: str
    base_confidence: float
    has_defanging: bool = False


class RegexIOCExtractor:
    """Extract IOCs using regex patterns with confidence scoring."""

    # Compiled regex patterns for each IOC type
    PATTERNS: Dict[IOCType, Pattern] = {}

    # Defanging patterns to detect obfuscated indicators
    DEFANGING_PATTERNS = [
        r"hxxp",
        r"h\[xx\]p",
        r"\[\.\]",
        r"\[dot\]",
        r"\[@\]",
        r"\[at\]",
    ]

    def __init__(self):
        """Initialize the regex extractor with compiled patterns."""
        if not self.PATTERNS:
            self._compile_patterns()
        self.defanging_regex = re.compile(
            "|".join(self.DEFANGING_PATTERNS), re.IGNORECASE
        )

    @classmethod
    def _compile_patterns(cls):
        """Compile all regex patterns once for performance."""
        cls.PATTERNS = {
            # Hash-based IOCs (Very High Confidence)
            IOCType.MD5: re.compile(r"\b[a-fA-F0-9]{32}\b"),
            IOCType.SHA256: re.compile(r"\b[a-fA-F0-9]{64}\b"),
            # Network IOCs
            IOCType.IP: re.compile(
                r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
                r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
            ),
            # URLs and Domains (including defanged)
            IOCType.URL: re.compile(
                r"\b(?:hxxps?|https?|h\[xx\]ps?)://[^\s]+|"
                r"\b[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?"
                r"(?:\[\.\]|\.)[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?"
                r"(?:\[\.\]|\.)[a-zA-Z]{2,}\b",
                re.IGNORECASE,
            ),
            # Cryptocurrency
            IOCType.BITCOIN_WALLET_ADDRESS: re.compile(
                r"\b(?:[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,87})\b"
            ),
            # Browser Extensions
            IOCType.CHROME_EXTENSION: re.compile(r"\b[a-z]{32}\b"),
        }
        logger.info("Compiled %d regex patterns", len(cls.PATTERNS))

    def extract_all(self, text: str) -> List[RegexIOCMatch]:
        """
        Extract all IOCs from text using regex patterns.

        Args:
            text: The text to extract IOCs from

        Returns:
            List of RegexIOCMatch objects with metadata
        """
        matches = []

        for ioc_type, pattern in self.PATTERNS.items():
            type_matches = self.extract_by_type(text, ioc_type, pattern)
            matches.extend(type_matches)

        logger.info("Extracted %d total IOC matches", len(matches))
        return matches

    def extract_by_type(
        self, text: str, ioc_type: IOCType, pattern: Optional[Pattern] = None
    ) -> List[RegexIOCMatch]:
        """
        Extract IOCs of a specific type.

        Args:
            text: The text to extract from
            ioc_type: The type of IOC to extract
            pattern: Optional pre-compiled pattern (uses default if None)

        Returns:
            List of matches for this IOC type
        """
        if pattern is None:
            pattern = self.PATTERNS.get(ioc_type)
            if pattern is None:
                logger.warning("No pattern found for IOC type: %s", ioc_type)
                return []

        matches = []
        for match in pattern.finditer(text):
            value = match.group(0)
            position = match.start()

            # Extract context window (100 chars before and after)
            context_start = max(0, position - 100)
            context_end = min(len(text), position + len(value) + 100)
            context_window = text[context_start:context_end]

            # Calculate base confidence based on IOC type
            base_confidence = self._calculate_base_confidence(ioc_type, value)

            # Detect defanging
            has_defanging = self._detect_defanging(value)

            matches.append(
                RegexIOCMatch(
                    ioc_type=ioc_type,
                    value=value,
                    position=position,
                    context_window=context_window,
                    base_confidence=base_confidence,
                    has_defanging=has_defanging,
                )
            )

        logger.info("Extracted %d matches for %s", len(matches), ioc_type.value)
        return matches

    def _calculate_base_confidence(self, ioc_type: IOCType, value: str) -> float:
        """
        Calculate base confidence score based on IOC type and pattern specificity.

        Args:
            ioc_type: The type of IOC
            value: The matched value

        Returns:
            Base confidence score (0-100)
        """
        # Very high confidence for hash-based IOCs (fixed length, hex only)
        if ioc_type in [IOCType.MD5, IOCType.SHA256]:
            return 98.0

        # High confidence for IP addresses
        if ioc_type == IOCType.IP:
            # Lower confidence for private/reserved IPs
            if self._is_private_ip(value):
                return 70.0
            return 90.0

        # High confidence for Bitcoin addresses (specific format)
        if ioc_type == IOCType.BITCOIN_WALLET_ADDRESS:
            return 85.0

        # Medium confidence for URLs/domains (needs context)
        if ioc_type == IOCType.URL:
            # Higher confidence if defanged
            if self._detect_defanging(value):
                return 85.0
            return 70.0

        # Lower confidence for Chrome extensions (many false positives)
        if ioc_type == IOCType.CHROME_EXTENSION:
            return 60.0

        # Default medium confidence
        return 70.0

    def _detect_defanging(self, value: str) -> bool:
        """
        Detect if a value contains defanging markers.

        Args:
            value: The IOC value to check

        Returns:
            True if defanging detected
        """
        return bool(self.defanging_regex.search(value))

    def _is_private_ip(self, ip: str) -> bool:
        """
        Check if an IP address is in a private/reserved range.

        Args:
            ip: The IP address string

        Returns:
            True if private/reserved
        """
        try:
            parts = [int(p) for p in ip.split(".")]

            # Private ranges: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
            if parts[0] == 10:
                return True
            if parts[0] == 172 and 16 <= parts[1] <= 31:
                return True
            if parts[0] == 192 and parts[1] == 168:
                return True

            # Loopback: 127.0.0.0/8
            if parts[0] == 127:
                return True

            # Link-local: 169.254.0.0/16
            if parts[0] == 169 and parts[1] == 254:
                return True

            return False
        except (ValueError, IndexError):
            return False

    def normalize_ioc(self, value: str, ioc_type: IOCType) -> str:
        """
        Normalize an IOC value (remove defanging, lowercase, etc.).

        Args:
            value: The IOC value to normalize
            ioc_type: The type of IOC

        Returns:
            Normalized value
        """
        normalized = value

        # Remove defanging
        normalized = normalized.replace("hxxp", "http")
        normalized = normalized.replace("h[xx]p", "http")
        normalized = normalized.replace("[.]", ".")
        normalized = normalized.replace("[dot]", ".")
        normalized = normalized.replace("[@]", "@")
        normalized = normalized.replace("[at]", "@")

        # Lowercase for certain types
        if ioc_type in [IOCType.URL, IOCType.MD5, IOCType.SHA256]:
            normalized = normalized.lower()

        return normalized


if __name__ == "__main__":
    # Test the extractor
    test_text = """
    The malware communicates with hxxps://evil[.]com/path and 192.168.1.100.
    File hash: 5d41402abc4b2a76b9719d911017c592
    SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    Bitcoin: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
    """

    extractor = RegexIOCExtractor()
    matches = extractor.extract_all(test_text)

    print(f"\nFound {len(matches)} IOC matches:")
    for match in matches:
        print(
            f"  {match.ioc_type.value}: {match.value} (confidence: {match.base_confidence})"
        )
