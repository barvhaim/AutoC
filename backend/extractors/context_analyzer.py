"""Context analysis for IOC validation and confidence scoring."""

import re
import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextIndicator(str, Enum):
    """Types of context indicators."""

    THREAT_KEYWORD = "threat_keyword"
    BENIGN_KEYWORD = "benign_keyword"
    SECTION_HEADER = "section_header"
    DEFANGING = "defanging"
    MALWARE_FAMILY = "malware_family"
    THREAT_ACTOR = "threat_actor"


@dataclass
class ContextAnalysis:
    """Results of context analysis."""

    has_threat_keywords: bool
    has_benign_keywords: bool
    section_header: Optional[str]
    threat_keyword_count: int
    benign_keyword_count: int
    malware_families: List[str]
    threat_actors: List[str]
    confidence_adjustment: float  # -20 to +20
    indicators: List[ContextIndicator]


class ContextAnalyzer:
    """Analyze surrounding text for threat indicators and context clues."""

    # Threat-related keywords that increase confidence
    THREAT_KEYWORDS = {
        # General threat terms
        "malicious",
        "malware",
        "threat",
        "attack",
        "exploit",
        "vulnerability",
        "backdoor",
        "trojan",
        "ransomware",
        "spyware",
        "adware",
        "rootkit",
        # C2 and infrastructure
        "c2",
        "c&c",
        "command and control",
        "command-and-control",
        "botnet",
        "infrastructure",
        "exfiltration",
        "exfiltrate",
        "callback",
        # IOC-specific terms
        "ioc",
        "iocs",
        "indicator",
        "indicators of compromise",
        "observable",
        "artifact",
        "network indicator",
        "file indicator",
        "hash",
        # Attack activities
        "phishing",
        "credential",
        "stealing",
        "harvesting",
        "injection",
        "payload",
        "dropper",
        "loader",
        "downloader",
        "stager",
        # Detection and analysis
        "detected",
        "identified",
        "observed",
        "discovered",
        "analyzed",
        "suspicious",
        "anomalous",
        "malicious activity",
    }

    # Benign keywords that decrease confidence
    BENIGN_KEYWORDS = {
        "example",
        "tutorial",
        "documentation",
        "sample",
        "demo",
        "test",
        "placeholder",
        "illustration",
        "hypothetical",
        "for instance",
        "such as",
        "like this",
        "e.g.",
    }

    # Section headers that indicate IOC content
    IOC_SECTION_PATTERNS = [
        r"(?i)indicators?\s+of\s+compromise",
        r"(?i)iocs?",
        r"(?i)network\s+indicators?",
        r"(?i)file\s+indicators?",
        r"(?i)observables?",
        r"(?i)c2\s+(?:servers?|infrastructure)",
        r"(?i)command\s+(?:and|&)\s+control",
        r"(?i)malicious\s+(?:domains?|ips?|urls?)",
        r"(?i)threat\s+intelligence",
    ]

    # Common malware family patterns
    MALWARE_FAMILY_PATTERNS = [
        r"(?i)\b(?:emotet|trickbot|qakbot|dridex|ursnif|gozi|zeus|danabot)\b",
        r"(?i)\b(?:cobalt\s*strike|metasploit|mimikatz|powershell\s*empire)\b",
        r"(?i)\b(?:ransomware|cryptolocker|wannacry|ryuk|maze|conti|lockbit)\b",
        r"(?i)\b(?:apt\d+|lazarus|fancy\s*bear|cozy\s*bear)\b",
    ]

    # Threat actor patterns
    THREAT_ACTOR_PATTERNS = [
        r"(?i)\bapt\s*\d+\b",
        r"(?i)\b(?:lazarus|fancy\s*bear|cozy\s*bear|sandworm)\b",
        r"(?i)\b(?:carbanak|fin\d+|wizard\s*spider)\b",
    ]

    def __init__(self):
        """Initialize the context analyzer."""
        self.section_patterns = [re.compile(p) for p in self.IOC_SECTION_PATTERNS]
        self.malware_patterns = [re.compile(p) for p in self.MALWARE_FAMILY_PATTERNS]
        self.actor_patterns = [re.compile(p) for p in self.THREAT_ACTOR_PATTERNS]

    def analyze(self, text: str, position: int, radius: int = 100) -> ContextAnalysis:
        """
        Analyze context around an IOC match.

        Args:
            text: Full text content
            position: Position of the IOC in text
            radius: Number of characters to analyze before/after

        Returns:
            ContextAnalysis with findings
        """
        # Extract context window
        window = self.extract_window(text, position, radius)

        # Analyze keywords
        threat_keywords = self._find_keywords(window, self.THREAT_KEYWORDS)
        benign_keywords = self._find_keywords(window, self.BENIGN_KEYWORDS)

        # Detect section header
        section_header = self.detect_section_header(text, position)

        # Find malware families and threat actors
        malware_families = self._find_patterns(window, self.malware_patterns)
        threat_actors = self._find_patterns(window, self.actor_patterns)

        # Calculate confidence adjustment
        confidence_adjustment = self._calculate_adjustment(
            len(threat_keywords),
            len(benign_keywords),
            section_header is not None,
            len(malware_families),
            len(threat_actors),
        )

        # Collect indicators
        indicators = []
        if threat_keywords:
            indicators.append(ContextIndicator.THREAT_KEYWORD)
        if benign_keywords:
            indicators.append(ContextIndicator.BENIGN_KEYWORD)
        if section_header:
            indicators.append(ContextIndicator.SECTION_HEADER)
        if malware_families:
            indicators.append(ContextIndicator.MALWARE_FAMILY)
        if threat_actors:
            indicators.append(ContextIndicator.THREAT_ACTOR)

        return ContextAnalysis(
            has_threat_keywords=len(threat_keywords) > 0,
            has_benign_keywords=len(benign_keywords) > 0,
            section_header=section_header,
            threat_keyword_count=len(threat_keywords),
            benign_keyword_count=len(benign_keywords),
            malware_families=malware_families,
            threat_actors=threat_actors,
            confidence_adjustment=confidence_adjustment,
            indicators=indicators,
        )

    def extract_window(self, text: str, position: int, radius: int = 100) -> str:
        """
        Extract a window of text around a position.

        Args:
            text: Full text
            position: Center position
            radius: Characters before/after

        Returns:
            Text window
        """
        start = max(0, position - radius)
        end = min(len(text), position + radius)
        return text[start:end]

    def detect_section_header(
        self, text: str, position: int, search_radius: int = 500
    ) -> Optional[str]:
        """
        Detect if the IOC is in a section with a relevant header.

        Args:
            text: Full text
            position: IOC position
            search_radius: How far back to search for headers

        Returns:
            Section header text if found
        """
        # Look backwards from position for section headers
        start = max(0, position - search_radius)
        search_text = text[start:position]

        # Check each pattern
        for pattern in self.section_patterns:
            match = pattern.search(search_text)
            if match:
                return match.group(0)

        return None

    def _find_keywords(self, text: str, keywords: Set[str]) -> List[str]:
        """
        Find keywords in text.

        Args:
            text: Text to search
            keywords: Set of keywords to find

        Returns:
            List of found keywords
        """
        text_lower = text.lower()
        found = []

        for keyword in keywords:
            if keyword in text_lower:
                found.append(keyword)

        return found

    def _find_patterns(self, text: str, patterns: List[re.Pattern]) -> List[str]:
        """
        Find pattern matches in text.

        Args:
            text: Text to search
            patterns: List of compiled regex patterns

        Returns:
            List of matched strings
        """
        found = []

        for pattern in patterns:
            matches = pattern.findall(text)
            found.extend(matches)

        return list(set(found))  # Remove duplicates

    def _calculate_adjustment(
        self,
        threat_count: int,
        benign_count: int,
        has_section_header: bool,
        malware_count: int,
        actor_count: int,
    ) -> float:
        """
        Calculate confidence adjustment based on context.

        Args:
            threat_count: Number of threat keywords
            benign_count: Number of benign keywords
            has_section_header: Whether in IOC section
            malware_count: Number of malware families mentioned
            actor_count: Number of threat actors mentioned

        Returns:
            Confidence adjustment (-20 to +20)
        """
        adjustment = 0.0

        # Positive adjustments
        if has_section_header:
            adjustment += 10.0

        # Each threat keyword adds confidence (max +10)
        adjustment += min(threat_count * 2.0, 10.0)

        # Malware families and threat actors add confidence
        adjustment += min(malware_count * 3.0, 5.0)
        adjustment += min(actor_count * 3.0, 5.0)

        # Negative adjustments
        # Each benign keyword reduces confidence (max -15)
        adjustment -= min(benign_count * 5.0, 15.0)

        # Clamp to range
        return max(-20.0, min(20.0, adjustment))

    def is_in_ioc_section(self, text: str, position: int) -> bool:
        """
        Quick check if position is in an IOC-related section.

        Args:
            text: Full text
            position: Position to check

        Returns:
            True if in IOC section
        """
        return self.detect_section_header(text, position) is not None


if __name__ == "__main__":
    # Test the analyzer
    test_text = """
    ## Indicators of Compromise
    
    The malware campaign uses the following malicious infrastructure:
    - C2 server: hxxps://evil[.]com
    - IP address: 192.168.1.100
    - File hash: 5d41402abc4b2a76b9719d911017c592
    
    This is associated with the Emotet malware family and APT28 threat actor.
    """

    analyzer = ContextAnalyzer()

    # Analyze context at position of "evil[.]com"
    position = test_text.find("evil[.]com")
    analysis = analyzer.analyze(test_text, position, radius=200)

    print("\nContext Analysis Results:")
    print(f"  Threat keywords: {analysis.threat_keyword_count}")
    print(f"  Benign keywords: {analysis.benign_keyword_count}")
    print(f"  Section header: {analysis.section_header}")
    print(f"  Malware families: {analysis.malware_families}")
    print(f"  Threat actors: {analysis.threat_actors}")
    print(f"  Confidence adjustment: {analysis.confidence_adjustment:+.1f}")
    print(f"  Indicators: {[i.value for i in analysis.indicators]}")
