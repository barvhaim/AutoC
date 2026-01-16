"""Hybrid IOC extractor orchestrating regex + LLM workflow."""

import logging
import time
from typing import List, Tuple, Optional

from backend.extractors.regex_ioc_extractor import RegexIOCExtractor
from backend.extractors.context_analyzer import ContextAnalyzer
from backend.extractors.confidence_scorer import ConfidenceScorer, ScoredIOCMatch
from backend.extractors.llm_validator import LLMValidator
from backend.extractors.hybrid_config import HybridExtractionConfig
from backend.data_model.ioc import IOC
from backend.data_model.extraction_metrics import ExtractionMetrics, IOCTypeMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridIOCExtractor:
    """
    Orchestrates hybrid IOC extraction workflow.

    Combines regex-based extraction with LLM validation for optimal
    performance and accuracy.
    """

    def __init__(self, config: Optional[HybridExtractionConfig] = None):
        """
        Initialize the hybrid extractor.

        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or HybridExtractionConfig()

        # Initialize components
        self.regex_extractor = RegexIOCExtractor()
        self.context_analyzer = ContextAnalyzer()
        self.confidence_scorer = ConfidenceScorer(self.context_analyzer)
        self.llm_validator = LLMValidator(batch_size=self.config.llm_batch_size)

        # Set logging level
        logger.setLevel(self.config.log_level)

        logger.info(
            "Hybrid IOC Extractor initialized with config: %s",
            {
                "direct_accept": self.config.direct_accept_threshold,
                "llm_enabled": self.config.enable_llm_validation,
                "batch_size": self.config.llm_batch_size,
            },
        )

    def extract(
        self, text: str, document_id: Optional[str] = None
    ) -> Tuple[List[IOC], ExtractionMetrics]:
        """
        Extract IOCs from text using hybrid approach.

        Args:
            text: Text to extract IOCs from
            document_id: Optional document identifier for metrics

        Returns:
            Tuple of (IOC list, extraction metrics)
        """
        start_time = time.time()

        # Initialize metrics
        metrics = ExtractionMetrics(document_id=document_id, document_size=len(text))

        # Phase 1: Regex extraction
        logger.info("Phase 1: Regex extraction")
        regex_start = time.time()
        regex_matches = self.regex_extractor.extract_all(text)
        metrics.regex_time_ms = (time.time() - regex_start) * 1000
        logger.info(
            "Extracted %d potential IOCs via regex in %.2fms",
            len(regex_matches),
            metrics.regex_time_ms,
        )

        if not regex_matches:
            metrics.total_time_ms = (time.time() - start_time) * 1000
            metrics.calculate_derived_metrics()
            return [], metrics

        # Phase 2: Confidence scoring
        logger.info("Phase 2: Confidence scoring")
        scoring_start = time.time()
        scored_matches = self.confidence_scorer.score_batch(regex_matches, text)
        metrics.scoring_time_ms = (time.time() - scoring_start) * 1000
        logger.info(
            "Scored %d IOCs in %.2fms", len(scored_matches), metrics.scoring_time_ms
        )

        # Phase 3: Categorize by confidence
        logger.info("Phase 3: Categorizing by confidence")
        categorized = self._categorize_by_confidence(scored_matches)

        direct_accept = categorized["direct_accept"]
        needs_validation = categorized["needs_validation"]
        rejected = categorized["rejected"]

        logger.info(
            "Categorization: %d direct accept, %d need validation, %d rejected",
            len(direct_accept),
            len(needs_validation),
            len(rejected),
        )

        # Phase 4: Convert direct accept to IOCs
        accepted_iocs = [
            self._scored_match_to_ioc(match, llm_validated=False)
            for match in direct_accept
        ]

        metrics.regex_extracted = len(regex_matches)
        metrics.direct_accept = len(direct_accept)

        # Phase 5: LLM validation (if enabled and needed)
        validated_iocs = []
        if self.config.enable_llm_validation and needs_validation:
            logger.info("Phase 5: LLM validation for %d IOCs", len(needs_validation))
            llm_start = time.time()

            validated_iocs, llm_calls = self.llm_validator.validate_batch(
                needs_validation, text
            )

            metrics.llm_time_ms = (time.time() - llm_start) * 1000
            metrics.llm_calls_made = llm_calls
            metrics.llm_validated = len(validated_iocs)

            logger.info(
                "LLM validated %d IOCs in %.2fms (%d calls)",
                len(validated_iocs),
                metrics.llm_time_ms,
                llm_calls,
            )
        elif needs_validation:
            logger.warning(
                "LLM validation disabled but %d IOCs need validation",
                len(needs_validation),
            )

        # Phase 6: Combine and deduplicate
        all_iocs = accepted_iocs + validated_iocs
        final_iocs = self._deduplicate(all_iocs)

        logger.info("Final: %d unique IOCs after deduplication", len(final_iocs))

        # Phase 7: Calculate metrics
        metrics.total_iocs = len(final_iocs)
        metrics.total_time_ms = (time.time() - start_time) * 1000

        # Build distributions
        metrics.confidence_distribution = self._build_confidence_distribution(
            scored_matches
        )
        metrics.ioc_type_distribution = self._build_type_distribution(final_iocs)

        # Build type metrics
        metrics.type_metrics = self._build_type_metrics(scored_matches, final_iocs)

        # Calculate derived metrics
        metrics.calculate_derived_metrics()

        logger.info(
            "Extraction complete: %d IOCs, %.2fms total, %.1f%% LLM rate",
            metrics.total_iocs,
            metrics.total_time_ms,
            metrics.llm_validation_rate,
        )

        return final_iocs, metrics

    def _categorize_by_confidence(self, scored_matches: List[ScoredIOCMatch]) -> dict:
        """
        Categorize scored matches by confidence level.

        Args:
            scored_matches: List of scored matches

        Returns:
            Dictionary with categorized matches
        """
        direct_accept = []
        needs_validation = []
        rejected = []

        for match in scored_matches:
            # Check type-specific minimum threshold
            type_config = self.config.get_ioc_type_config(match.match.ioc_type)

            if match.final_confidence < type_config.min_confidence_threshold:
                rejected.append(match)
                continue

            # Check if should use LLM
            if self.config.should_use_llm(match.final_confidence, match.match.ioc_type):
                needs_validation.append(match)
            else:
                direct_accept.append(match)

        return {
            "direct_accept": direct_accept,
            "needs_validation": needs_validation,
            "rejected": rejected,
        }

    def _scored_match_to_ioc(
        self, scored_match: ScoredIOCMatch, llm_validated: bool
    ) -> IOC:
        """
        Convert a scored match to an IOC object.

        Args:
            scored_match: The scored match
            llm_validated: Whether it was LLM validated

        Returns:
            IOC object
        """
        from backend.data_model.ioc import ExtractionMethod
        from backend.data_model.ioc import ConfidenceLevel as IOCConfidenceLevel

        # Determine extraction method
        if llm_validated:
            extraction_method = ExtractionMethod.HYBRID
        else:
            extraction_method = ExtractionMethod.REGEX

        # Map confidence level from scorer to IOC model
        confidence_level_map = {
            "very_high": IOCConfidenceLevel.VERY_HIGH,
            "high": IOCConfidenceLevel.HIGH,
            "medium": IOCConfidenceLevel.MEDIUM,
            "low": IOCConfidenceLevel.LOW,
            "very_low": IOCConfidenceLevel.VERY_LOW,
        }
        ioc_confidence_level = confidence_level_map.get(
            scored_match.confidence_level.value, IOCConfidenceLevel.MEDIUM
        )

        # Normalize value
        normalized_value = self.regex_extractor.normalize_ioc(
            scored_match.match.value, scored_match.match.ioc_type
        )

        # Build metadata
        metadata = {
            "has_defanging": scored_match.match.has_defanging,
            "base_confidence": scored_match.match.base_confidence,
            "context_adjustment": scored_match.context_analysis.confidence_adjustment,
            "threat_keywords": scored_match.context_analysis.threat_keyword_count,
        }

        if scored_match.context_analysis.section_header:
            metadata["section_header"] = scored_match.context_analysis.section_header
        if scored_match.context_analysis.malware_families:
            metadata["malware_families"] = (
                scored_match.context_analysis.malware_families
            )
        if scored_match.context_analysis.threat_actors:
            metadata["threat_actors"] = scored_match.context_analysis.threat_actors

        return IOC(
            type=scored_match.match.ioc_type,
            value=scored_match.match.value,
            confidence=scored_match.final_confidence,
            confidence_level=ioc_confidence_level,
            extraction_method=extraction_method,
            context=scored_match.match.context_window,
            position=scored_match.match.position,
            validated_by_llm=llm_validated,
            normalized_value=normalized_value,
            metadata=metadata,
        )

    def _deduplicate(self, iocs: List[IOC]) -> List[IOC]:
        """
        Remove duplicate IOCs, keeping the one with highest confidence.

        Args:
            iocs: List of IOCs

        Returns:
            Deduplicated list
        """
        seen = {}

        for ioc in iocs:
            # Use normalized value for deduplication
            key = (ioc.type, ioc.normalized_value or ioc.value)

            if key not in seen or ioc.confidence > seen[key].confidence:
                seen[key] = ioc

        return list(seen.values())

    def _build_confidence_distribution(
        self, scored_matches: List[ScoredIOCMatch]
    ) -> dict:
        """Build confidence level distribution."""
        distribution = {}
        for match in scored_matches:
            level = match.confidence_level.value
            distribution[level] = distribution.get(level, 0) + 1
        return distribution

    def _build_type_distribution(self, iocs: List[IOC]) -> dict:
        """Build IOC type distribution."""
        distribution = {}
        for ioc in iocs:
            # Handle both enum and string types
            ioc_type = ioc.type.value if hasattr(ioc.type, "value") else str(ioc.type)
            distribution[ioc_type] = distribution.get(ioc_type, 0) + 1
        return distribution

    def _build_type_metrics(
        self, scored_matches: List[ScoredIOCMatch], final_iocs: List[IOC]
    ) -> List[IOCTypeMetrics]:
        """Build per-type metrics."""
        from collections import defaultdict

        # Count by type
        type_counts = defaultdict(
            lambda: {
                "total": 0,
                "regex": 0,
                "llm_validated": 0,
                "direct_accept": 0,
                "confidence_sum": 0.0,
            }
        )

        # Count scored matches
        for match in scored_matches:
            ioc_type = match.match.ioc_type.value
            type_counts[ioc_type]["total"] += 1
            type_counts[ioc_type]["regex"] += 1
            type_counts[ioc_type]["confidence_sum"] += match.final_confidence

            if not match.requires_llm_validation:
                type_counts[ioc_type]["direct_accept"] += 1

        # Count validated IOCs
        for ioc in final_iocs:
            if ioc.validated_by_llm:
                type_counts[ioc.type.value]["llm_validated"] += 1

        # Build metrics objects
        metrics_list = []
        for ioc_type, counts in type_counts.items():
            avg_conf = (
                counts["confidence_sum"] / counts["total"]
                if counts["total"] > 0
                else 0.0
            )

            metrics_list.append(
                IOCTypeMetrics(
                    ioc_type=ioc_type,
                    total_extracted=int(counts["total"]),
                    regex_extracted=int(counts["regex"]),
                    llm_validated=int(counts["llm_validated"]),
                    direct_accept=int(counts["direct_accept"]),
                    avg_confidence=avg_conf,
                )
            )

        return metrics_list


if __name__ == "__main__":
    # Test the hybrid extractor
    import json

    test_text = """
    ## Indicators of Compromise
    
    The Emotet malware campaign uses the following infrastructure:
    - C2 server: hxxps://evil[.]com/path
    - Backup C2: example[.]com (for demonstration purposes)
    - IP address: 192.168.1.100
    - File hash: 5d41402abc4b2a76b9719d911017c592
    - SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    - Bitcoin wallet: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
    """

    # Test with default config
    print("Testing Hybrid IOC Extractor\n" + "=" * 50)
    extractor = HybridIOCExtractor()

    iocs, metrics = extractor.extract(test_text, document_id="test_doc_1")

    print(f"\nExtracted {len(iocs)} IOCs:")
    for ioc in iocs:
        ioc_type = ioc.type.value if hasattr(ioc.type, "value") else str(ioc.type)
        print(f"  [{ioc_type}] {ioc.value}")
        conf_level = (
            ioc.confidence_level.value
            if ioc.confidence_level and hasattr(ioc.confidence_level, "value")
            else "unknown"
        )
        method = (
            ioc.extraction_method.value
            if ioc.extraction_method and hasattr(ioc.extraction_method, "value")
            else "unknown"
        )
        conf = ioc.confidence if ioc.confidence is not None else 0.0
        print(f"    Confidence: {conf:.1f}% ({conf_level})")
        print(f"    Method: {method}")
        print(f"    LLM validated: {ioc.validated_by_llm}")

    print("\n" + "=" * 50)
    print("\nExtraction Metrics:")
    print(json.dumps(metrics.to_summary_dict(), indent=2))
