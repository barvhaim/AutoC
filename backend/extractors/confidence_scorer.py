"""Confidence scoring system for IOC matches."""

import logging
from typing import Optional
from dataclasses import dataclass
from enum import Enum

from backend.extractors.regex_ioc_extractor import RegexIOCMatch
from backend.extractors.context_analyzer import ContextAnalyzer, ContextAnalysis
from backend.data_model.ioc import IOCType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfidenceLevel(str, Enum):
    """Confidence level categories."""

    VERY_HIGH = "very_high"  # 95-100%
    HIGH = "high"  # 85-94%
    MEDIUM = "medium"  # 70-84%
    LOW = "low"  # 50-69%
    VERY_LOW = "very_low"  # <50%


@dataclass
class ScoredIOCMatch:
    """IOC match with final confidence score."""

    match: RegexIOCMatch
    context_analysis: ContextAnalysis
    final_confidence: float
    confidence_level: ConfidenceLevel
    requires_llm_validation: bool


class ConfidenceScorer:
    """Score IOC matches based on pattern and context."""

    # Confidence thresholds for decision making
    DIRECT_ACCEPT_THRESHOLD = 95.0
    CONTEXT_CHECK_THRESHOLD = 85.0
    LLM_VALIDATION_THRESHOLD = 70.0

    # Weight factors for scoring components
    WEIGHTS = {
        "base_confidence": 1.0,  # Use full base confidence
        "context_adjustment": 1.0,  # Add full context adjustment
        "defanging_bonus": 1.0,  # Add full defanging bonus
    }

    def __init__(self, context_analyzer: Optional[ContextAnalyzer] = None):
        """
        Initialize the confidence scorer.

        Args:
            context_analyzer: Optional context analyzer (creates new if None)
        """
        self.context_analyzer = context_analyzer or ContextAnalyzer()

    def score(self, match: RegexIOCMatch, full_text: str) -> ScoredIOCMatch:
        """
        Calculate final confidence score for an IOC match.

        Args:
            match: The regex IOC match
            full_text: Full text for context analysis

        Returns:
            ScoredIOCMatch with final score and metadata
        """
        # Analyze context
        context_analysis = self.context_analyzer.analyze(
            text=full_text, position=match.position, radius=100
        )

        # Calculate final confidence
        final_confidence = self._calculate_final_confidence(
            match=match, context_analysis=context_analysis
        )

        # Determine confidence level
        confidence_level = self._get_confidence_level(final_confidence)

        # Determine if LLM validation is required
        requires_llm = self._requires_llm_validation(
            final_confidence=final_confidence,
            ioc_type=match.ioc_type,
            context_analysis=context_analysis,
        )

        return ScoredIOCMatch(
            match=match,
            context_analysis=context_analysis,
            final_confidence=final_confidence,
            confidence_level=confidence_level,
            requires_llm_validation=requires_llm,
        )

    def score_batch(
        self, matches: list[RegexIOCMatch], full_text: str
    ) -> list[ScoredIOCMatch]:
        """
        Score multiple IOC matches.

        Args:
            matches: List of regex matches
            full_text: Full text for context

        Returns:
            List of scored matches
        """
        scored = []
        for match in matches:
            scored_match = self.score(match, full_text)
            scored.append(scored_match)

        logger.info(
            "Scored %d matches: %d direct accept, %d need LLM validation",
            len(scored),
            sum(1 for s in scored if not s.requires_llm_validation),
            sum(1 for s in scored if s.requires_llm_validation),
        )

        return scored

    def _calculate_final_confidence(
        self, match: RegexIOCMatch, context_analysis: ContextAnalysis
    ) -> float:
        """
        Calculate final confidence score using weighted components.

        Args:
            match: The IOC match
            context_analysis: Context analysis results

        Returns:
            Final confidence score (0-100)
        """
        # Start with base confidence from pattern match
        score = match.base_confidence * self.WEIGHTS["base_confidence"]

        # Add context adjustment (weighted)
        context_contribution = (
            context_analysis.confidence_adjustment * self.WEIGHTS["context_adjustment"]
        )
        score += context_contribution

        # Add defanging bonus if present
        if match.has_defanging:
            defanging_bonus = 10.0 * self.WEIGHTS["defanging_bonus"]
            score += defanging_bonus

        # Apply IOC type specific adjustments
        score = self._apply_type_specific_adjustments(
            score, match.ioc_type, context_analysis
        )

        # Clamp to valid range
        return max(0.0, min(100.0, score))

    def _apply_type_specific_adjustments(
        self, score: float, ioc_type: IOCType, context_analysis: ContextAnalysis
    ) -> float:
        """
        Apply IOC type-specific confidence adjustments.

        Args:
            score: Current confidence score
            ioc_type: Type of IOC
            context_analysis: Context analysis

        Returns:
            Adjusted score
        """
        # Hash-based IOCs: Very reliable, minimal adjustment needed
        if ioc_type in [IOCType.MD5, IOCType.SHA256]:
            # Only reduce if strong benign indicators
            if context_analysis.benign_keyword_count > 2:
                score -= 5.0
            return score

        # IP addresses: Boost if in IOC section, reduce if private
        if ioc_type == IOCType.IP:
            if context_analysis.section_header:
                score += 5.0
            return score

        # URLs/Domains: Heavily context-dependent
        if ioc_type == IOCType.URL:
            # Strong boost if in IOC section with threat keywords
            if (
                context_analysis.section_header
                and context_analysis.threat_keyword_count > 0
            ):
                score += 10.0
            # Reduce if no threat context
            elif context_analysis.threat_keyword_count == 0:
                score -= 10.0
            return score

        # Chrome extensions: Need strong context
        if ioc_type == IOCType.CHROME_EXTENSION:
            # Require threat context or IOC section
            if not (
                context_analysis.section_header
                or context_analysis.threat_keyword_count > 0
            ):
                score -= 15.0
            return score

        # Bitcoin addresses: Moderate adjustment
        if ioc_type == IOCType.BITCOIN_WALLET_ADDRESS:
            if context_analysis.section_header:
                score += 5.0
            return score

        return score

    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """
        Convert numeric confidence to level category.

        Args:
            confidence: Numeric confidence (0-100)

        Returns:
            ConfidenceLevel enum
        """
        if confidence >= 95.0:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 85.0:
            return ConfidenceLevel.HIGH
        elif confidence >= 70.0:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 50.0:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _requires_llm_validation(
        self,
        final_confidence: float,
        ioc_type: IOCType,
        context_analysis: ContextAnalysis,
    ) -> bool:
        """
        Determine if LLM validation is required.

        Args:
            final_confidence: Final confidence score
            ioc_type: Type of IOC
            context_analysis: Context analysis

        Returns:
            True if LLM validation needed
        """
        # Very high confidence: No LLM needed
        if final_confidence >= self.DIRECT_ACCEPT_THRESHOLD:
            return False

        # High confidence with clear context: No LLM needed
        if final_confidence >= self.CONTEXT_CHECK_THRESHOLD:
            # Check for clear threat context
            has_clear_context = (
                context_analysis.section_header is not None
                or context_analysis.threat_keyword_count >= 2
                or len(context_analysis.malware_families) > 0
            )
            if has_clear_context:
                return False

        # Below threshold or ambiguous context: LLM validation required
        if final_confidence < self.LLM_VALIDATION_THRESHOLD:
            return True

        # Medium confidence: Check for ambiguous cases
        # URLs and domains always need validation in medium range
        if ioc_type == IOCType.URL and final_confidence < self.CONTEXT_CHECK_THRESHOLD:
            return True

        # Chrome extensions need validation unless very high confidence
        if ioc_type == IOCType.CHROME_EXTENSION and final_confidence < 90.0:
            return True

        # Default: validation needed for medium confidence
        return final_confidence < self.CONTEXT_CHECK_THRESHOLD

    def get_statistics(self, scored_matches: list[ScoredIOCMatch]) -> dict:
        """
        Get statistics about scored matches.

        Args:
            scored_matches: List of scored matches

        Returns:
            Dictionary with statistics
        """
        if not scored_matches:
            return {
                "total": 0,
                "by_level": {},
                "requires_llm": 0,
                "direct_accept": 0,
                "avg_confidence": 0.0,
            }

        by_level = {}
        for level in ConfidenceLevel:
            by_level[level.value] = sum(
                1 for m in scored_matches if m.confidence_level == level
            )

        return {
            "total": len(scored_matches),
            "by_level": by_level,
            "requires_llm": sum(1 for m in scored_matches if m.requires_llm_validation),
            "direct_accept": sum(
                1 for m in scored_matches if not m.requires_llm_validation
            ),
            "avg_confidence": sum(m.final_confidence for m in scored_matches)
            / len(scored_matches),
            "llm_validation_rate": sum(
                1 for m in scored_matches if m.requires_llm_validation
            )
            / len(scored_matches)
            * 100,
        }


if __name__ == "__main__":
    # Test the scorer
    from backend.extractors.regex_ioc_extractor import RegexIOCExtractor

    test_text = """
    ## Indicators of Compromise
    
    The Emotet malware campaign uses the following malicious infrastructure:
    - C2 server: hxxps://evil[.]com/path
    - IP address: 192.168.1.100
    - File hash: 5d41402abc4b2a76b9719d911017c592
    - SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    
    For example purposes, here's a sample domain: example.com
    """

    # Extract IOCs
    extractor = RegexIOCExtractor()
    matches = extractor.extract_all(test_text)

    # Score them
    scorer = ConfidenceScorer()
    scored_matches = scorer.score_batch(matches, test_text)

    print(f"\nScored {len(scored_matches)} IOC matches:\n")
    for scored in scored_matches:
        print(f"{scored.match.ioc_type.value}: {scored.match.value}")
        print(f"  Base confidence: {scored.match.base_confidence:.1f}")
        print(
            f"  Context adjustment: {scored.context_analysis.confidence_adjustment:+.1f}"
        )
        print(
            f"  Final confidence: {scored.final_confidence:.1f} ({scored.confidence_level.value})"
        )
        print(f"  Requires LLM: {scored.requires_llm_validation}")
        print()

    # Print statistics
    stats = scorer.get_statistics(scored_matches)
    print("\nStatistics:")
    print(f"  Total: {stats['total']}")
    print(f"  Direct accept: {stats['direct_accept']}")
    print(f"  Requires LLM: {stats['requires_llm']}")
    print(f"  LLM validation rate: {stats['llm_validation_rate']:.1f}%")
    print(f"  Average confidence: {stats['avg_confidence']:.1f}")
