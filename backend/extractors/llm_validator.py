"""LLM-based validation for ambiguous IOC matches."""

import logging
import os
import json
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate

from backend.llm import get_chat_llm_client
from backend.prompts import get_prompts
from backend.extractors.confidence_scorer import ScoredIOCMatch
from backend.data_model.ioc import IOC, IOCType, ExtractionMethod, ConfidenceLevel

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMValidator:
    """Validate ambiguous IOCs using LLM."""

    # Batch size for validation
    DEFAULT_BATCH_SIZE = 10

    def __init__(self, batch_size: int = DEFAULT_BATCH_SIZE):
        """
        Initialize the LLM validator.

        Args:
            batch_size: Number of IOCs to validate per LLM call
        """
        self.batch_size = batch_size
        self.prompts = get_prompts()
        self._llm_client = None

    @property
    def llm(self):
        """Lazy load LLM client."""
        if self._llm_client is None:
            model_name = os.getenv("LLM_MODEL", "meta-llama/llama-3-3-70b-instruct")
            self._llm_client = get_chat_llm_client(
                model_name=model_name,
                model_parameters={
                    "temperature": 0.1,
                    "max_tokens": 2048,
                },
            )
        return self._llm_client

    def validate_batch(
        self, scored_matches: List[ScoredIOCMatch], full_text: str
    ) -> Tuple[List[IOC], int]:
        """
        Validate a batch of IOC matches using LLM.

        Args:
            scored_matches: List of scored IOC matches needing validation
            full_text: Full document text for context

        Returns:
            Tuple of (validated IOCs, number of LLM calls)
        """
        if not scored_matches:
            return [], 0

        validated_iocs = []
        llm_calls = 0

        # Group by IOC type for more efficient validation
        by_type: Dict[IOCType, List[ScoredIOCMatch]] = {}
        for match in scored_matches:
            ioc_type = match.match.ioc_type
            if ioc_type not in by_type:
                by_type[ioc_type] = []
            by_type[ioc_type].append(match)

        # Validate each type in batches
        for ioc_type, matches in by_type.items():
            for i in range(0, len(matches), self.batch_size):
                batch = matches[i : i + self.batch_size]

                # Use quick validation for batches
                validated = self._quick_validate_batch(batch, ioc_type, full_text)
                validated_iocs.extend(validated)
                llm_calls += 1

        logger.info(
            "LLM validation complete: %d IOCs validated, %d LLM calls",
            len(validated_iocs),
            llm_calls,
        )

        return validated_iocs, llm_calls

    def _quick_validate_batch(
        self, batch: List[ScoredIOCMatch], ioc_type: IOCType, full_text: str
    ) -> List[IOC]:
        """
        Quick validation for a batch of IOCs of the same type.

        Args:
            batch: Batch of scored matches
            ioc_type: Type of IOCs in batch
            full_text: Full document text

        Returns:
            List of validated IOC objects
        """
        # Prepare IOC list for prompt
        ioc_values = [match.match.value for match in batch]
        ioc_list_str = "\n".join(f"- {value}" for value in ioc_values)

        # Get context (use first match's context as representative)
        context = batch[0].match.context_window if batch else ""

        # Create prompt
        system_template = (
            self.prompts.get("validate_iocs", {})
            .get("quick_validation", {})
            .get("system", "")
        )
        user_template = (
            self.prompts.get("validate_iocs", {})
            .get("quick_validation", {})
            .get("user", "")
        )

        # Format the complete prompt with all variables
        formatted_user_content = user_template.format(
            context=context, ioc_type=ioc_type.value, ioc_list=ioc_list_str
        )

        # Create messages directly (system template has no variables)
        from langchain_core.messages import SystemMessage

        messages = [
            SystemMessage(content=system_template),
            HumanMessage(content=formatted_user_content),
        ]

        prompt = ChatPromptTemplate.from_messages(messages)

        # Call LLM
        try:
            chain = prompt | self.llm | self._json_escaping | JsonOutputParser()
            response = chain.invoke({})

            # Response should be a list of valid IOC values
            if isinstance(response, list):
                valid_values = set(response)
            else:
                logger.warning("Unexpected LLM response format: %s", type(response))
                valid_values = set()

            # Create IOC objects for validated indicators
            validated_iocs = []
            for match in batch:
                if match.match.value in valid_values:
                    ioc = self._create_validated_ioc(match, llm_validated=True)
                    validated_iocs.append(ioc)
                else:
                    logger.debug("LLM rejected IOC: %s", match.match.value)

            return validated_iocs

        except Exception as e:
            logger.error("LLM validation failed: %s", str(e))
            # On error, accept IOCs with medium+ confidence
            return [
                self._create_validated_ioc(match, llm_validated=False)
                for match in batch
                if match.final_confidence >= 70.0
            ]

    def validate_single(
        self, scored_match: ScoredIOCMatch, full_text: str, deep: bool = False
    ) -> Optional[IOC]:
        """
        Validate a single IOC with optional deep analysis.

        Args:
            scored_match: Scored IOC match
            full_text: Full document text
            deep: Whether to use deep validation with explanation

        Returns:
            Validated IOC or None if rejected
        """
        if deep:
            return self._deep_validate_single(scored_match, full_text)
        else:
            # Use quick validation for single IOC
            result = self._quick_validate_batch(
                [scored_match], scored_match.match.ioc_type, full_text
            )
            return result[0] if result else None

    def _deep_validate_single(
        self, scored_match: ScoredIOCMatch, full_text: str
    ) -> Optional[IOC]:
        """
        Deep validation with detailed explanation.

        Args:
            scored_match: Scored IOC match
            full_text: Full document text

        Returns:
            Validated IOC with explanation or None
        """
        # Get larger context for deep validation
        position = scored_match.match.position
        context_start = max(0, position - 500)
        context_end = min(len(full_text), position + 500)
        full_context = full_text[context_start:context_end]

        # Create prompt
        system_template = (
            self.prompts.get("validate_iocs", {})
            .get("deep_validation", {})
            .get("system", "")
        )
        user_template = (
            self.prompts.get("validate_iocs", {})
            .get("deep_validation", {})
            .get("user", "")
        )

        # Format the complete prompt with all variables
        formatted_user_content = user_template.format(
            full_context=full_context,
            ioc_type=scored_match.match.ioc_type.value,
            ioc_value=scored_match.match.value,
            confidence=round(scored_match.final_confidence, 1),
        )

        # Create messages directly (system template has no variables)
        from langchain_core.messages import SystemMessage

        messages = [
            SystemMessage(content=system_template),
            HumanMessage(content=formatted_user_content),
        ]

        prompt = ChatPromptTemplate.from_messages(messages)

        # Call LLM
        try:
            chain = prompt | self.llm | self._json_escaping | JsonOutputParser()
            response = chain.invoke({})

            # Parse response
            if isinstance(response, dict) and response.get("valid"):
                ioc = self._create_validated_ioc(
                    scored_match,
                    llm_validated=True,
                    llm_explanation=response.get("explanation"),
                    llm_confidence=response.get("confidence"),
                )
                return ioc
            else:
                logger.debug(
                    "LLM rejected IOC: %s (reason: %s)",
                    scored_match.match.value,
                    response.get("explanation", "no explanation"),
                )
                return None

        except Exception as e:
            logger.error("Deep validation failed: %s", str(e))
            # On error, fall back to confidence threshold
            if scored_match.final_confidence >= 70.0:
                return self._create_validated_ioc(scored_match, llm_validated=False)
            return None

    def _create_validated_ioc(
        self,
        scored_match: ScoredIOCMatch,
        llm_validated: bool,
        llm_explanation: Optional[str] = None,
        llm_confidence: Optional[float] = None,
    ) -> IOC:
        """
        Create an IOC object from a validated match.

        Args:
            scored_match: The scored match
            llm_validated: Whether LLM validated it
            llm_explanation: Optional LLM explanation
            llm_confidence: Optional LLM confidence override

        Returns:
            IOC object with metadata
        """
        from backend.extractors.regex_ioc_extractor import RegexIOCExtractor

        # Use LLM confidence if provided, otherwise use scored confidence
        final_confidence = (
            llm_confidence
            if llm_confidence is not None
            else scored_match.final_confidence
        )

        # Determine confidence level
        if final_confidence >= 95:
            confidence_level = ConfidenceLevel.VERY_HIGH
        elif final_confidence >= 85:
            confidence_level = ConfidenceLevel.HIGH
        elif final_confidence >= 70:
            confidence_level = ConfidenceLevel.MEDIUM
        elif final_confidence >= 50:
            confidence_level = ConfidenceLevel.LOW
        else:
            confidence_level = ConfidenceLevel.VERY_LOW

        # Normalize the IOC value
        extractor = RegexIOCExtractor()
        normalized_value = extractor.normalize_ioc(
            scored_match.match.value, scored_match.match.ioc_type
        )

        # Determine extraction method
        if llm_validated:
            extraction_method = ExtractionMethod.HYBRID
        else:
            extraction_method = ExtractionMethod.REGEX

        # Build metadata
        metadata = {
            "has_defanging": scored_match.match.has_defanging,
            "base_confidence": scored_match.match.base_confidence,
            "context_adjustment": scored_match.context_analysis.confidence_adjustment,
            "threat_keywords": scored_match.context_analysis.threat_keyword_count,
            "section_header": scored_match.context_analysis.section_header,
        }

        if scored_match.context_analysis.malware_families:
            metadata["malware_families"] = (
                scored_match.context_analysis.malware_families
            )
        if scored_match.context_analysis.threat_actors:
            metadata["threat_actors"] = scored_match.context_analysis.threat_actors

        return IOC(
            type=scored_match.match.ioc_type,
            value=scored_match.match.value,
            confidence=final_confidence,
            confidence_level=confidence_level,
            extraction_method=extraction_method,
            context=scored_match.match.context_window,
            position=scored_match.match.position,
            validated_by_llm=llm_validated,
            llm_explanation=llm_explanation,
            normalized_value=normalized_value,
            metadata=metadata,
        )

    @staticmethod
    def _json_escaping(response: AIMessage) -> AIMessage:
        """Clean and prepare LLM response for JSON parsing."""
        content = response.content

        # Ensure content is a string
        if not isinstance(content, str):
            content = str(content)

        # Log the raw response for debugging
        logger.debug("LLM response (first 200 chars): %s", content[:200])

        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = (
                    content.rsplit("\n", 1)[0] if "\n" in content else content[:-3]
                )

        # Strip whitespace
        content = content.strip()

        # Handle empty responses
        if not content or content == "":
            logger.info("Empty LLM response, converting to empty array []")
            content = "[]"

        return AIMessage(content=content)


if __name__ == "__main__":
    # Test the validator (requires LLM setup)
    from backend.extractors.regex_ioc_extractor import RegexIOCExtractor
    from backend.extractors.confidence_scorer import ConfidenceScorer

    test_text = """
    ## Indicators of Compromise
    
    The Emotet malware campaign uses:
    - C2 server: hxxps://evil[.]com/path
    - Backup C2: example[.]com (for demonstration)
    - File hash: 5d41402abc4b2a76b9719d911017c592
    """

    # Extract and score
    extractor = RegexIOCExtractor()
    scorer = ConfidenceScorer()

    matches = extractor.extract_all(test_text)
    scored_matches = scorer.score_batch(matches, test_text)

    # Filter those needing validation
    needs_validation = [m for m in scored_matches if m.requires_llm_validation]

    print(
        f"\nFound {len(scored_matches)} IOCs, {len(needs_validation)} need LLM validation"
    )

    if needs_validation:
        print("\nIOCs needing validation:")
        for match in needs_validation:
            print(f"  - {match.match.value} ({match.final_confidence:.1f}%)")

        # Note: Actual validation requires LLM setup
        print("\nNote: LLM validation requires API credentials to be configured")
