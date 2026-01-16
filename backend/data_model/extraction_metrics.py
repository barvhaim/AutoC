"""Extraction metrics for tracking hybrid IOC extraction performance."""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class IOCTypeMetrics(BaseModel):
    """Metrics for a specific IOC type."""

    ioc_type: str
    total_extracted: int = 0
    regex_extracted: int = 0
    llm_validated: int = 0
    llm_only: int = 0
    direct_accept: int = 0
    avg_confidence: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "ioc_type": self.ioc_type,
            "total": self.total_extracted,
            "regex": self.regex_extracted,
            "llm_validated": self.llm_validated,
            "llm_only": self.llm_only,
            "direct_accept": self.direct_accept,
            "avg_confidence": round(self.avg_confidence, 2),
        }


class ExtractionMetrics(BaseModel):
    """
    Comprehensive metrics for IOC extraction performance.

    Tracks extraction methods, timing, and confidence distribution.
    """

    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Document info
    document_id: Optional[str] = None
    document_size: int = 0  # Characters

    # IOC counts
    total_iocs: int = 0
    regex_extracted: int = 0
    llm_validated: int = 0
    llm_only: int = 0
    direct_accept: int = 0

    # Timing (milliseconds)
    regex_time_ms: float = 0.0
    context_analysis_time_ms: float = 0.0
    scoring_time_ms: float = 0.0
    llm_time_ms: float = 0.0
    total_time_ms: float = 0.0

    # LLM usage
    llm_calls_made: int = 0

    # Confidence distribution
    confidence_distribution: Dict[str, int] = Field(default_factory=dict)
    # Example: {"very_high": 5, "high": 3, "medium": 2, "low": 1}

    # IOC type breakdown
    ioc_type_distribution: Dict[str, int] = Field(default_factory=dict)
    # Example: {"MD5 Hash": 3, "Domain or URL": 5, "IP Address": 2}

    # Detailed type metrics
    type_metrics: List[IOCTypeMetrics] = Field(default_factory=list)

    # Performance indicators
    llm_validation_rate: float = 0.0  # Percentage of IOCs needing LLM
    avg_confidence: float = 0.0
    speedup_factor: float = 0.0  # vs LLM-only baseline

    def calculate_derived_metrics(self):
        """Calculate derived metrics from base metrics."""
        if self.total_iocs > 0:
            self.llm_validation_rate = (
                (self.llm_validated + self.llm_only) / self.total_iocs * 100
            )

            # Calculate average confidence from distribution
            if self.confidence_distribution:
                total_weighted = 0
                total_count = 0
                confidence_values = {
                    "very_high": 97.5,
                    "high": 89.5,
                    "medium": 77.0,
                    "low": 59.5,
                    "very_low": 25.0,
                }
                for level, count in self.confidence_distribution.items():
                    total_weighted += confidence_values.get(level, 70.0) * count
                    total_count += count
                if total_count > 0:
                    self.avg_confidence = total_weighted / total_count

        # Calculate speedup vs LLM-only baseline (assume 2000ms per LLM call)
        if self.total_iocs > 0:
            llm_only_time = self.total_iocs * 2000  # 2 seconds per IOC
            if self.total_time_ms > 0:
                self.speedup_factor = llm_only_time / self.total_time_ms

    def add_ioc_type_metrics(self, metrics: IOCTypeMetrics):
        """Add metrics for a specific IOC type."""
        self.type_metrics.append(metrics)

    def to_summary_dict(self) -> Dict:
        """Convert to summary dictionary for logging/display."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "document_size": self.document_size,
            "total_iocs": self.total_iocs,
            "extraction_breakdown": {
                "regex_only": self.direct_accept,
                "regex_llm_validated": self.llm_validated,
                "llm_only": self.llm_only,
            },
            "timing_ms": {
                "regex": round(self.regex_time_ms, 2),
                "context_analysis": round(self.context_analysis_time_ms, 2),
                "scoring": round(self.scoring_time_ms, 2),
                "llm": round(self.llm_time_ms, 2),
                "total": round(self.total_time_ms, 2),
            },
            "performance": {
                "llm_validation_rate": round(self.llm_validation_rate, 1),
                "avg_confidence": round(self.avg_confidence, 1),
                "speedup_factor": round(self.speedup_factor, 2),
                "llm_calls": self.llm_calls_made,
            },
            "confidence_distribution": self.confidence_distribution,
            "ioc_type_distribution": self.ioc_type_distribution,
        }

    def to_detailed_dict(self) -> Dict:
        """Convert to detailed dictionary with all metrics."""
        summary = self.to_summary_dict()
        summary["type_metrics"] = [m.to_dict() for m in self.type_metrics]
        return summary

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-01T12:00:00",
                "document_size": 5000,
                "total_iocs": 10,
                "regex_extracted": 8,
                "llm_validated": 2,
                "llm_only": 0,
                "direct_accept": 8,
                "regex_time_ms": 25.5,
                "llm_time_ms": 1500.0,
                "total_time_ms": 1550.0,
                "llm_calls_made": 1,
                "llm_validation_rate": 20.0,
                "avg_confidence": 92.5,
                "speedup_factor": 12.9,
            }
        }


class AggregatedMetrics(BaseModel):
    """Aggregated metrics across multiple extractions."""

    start_time: datetime
    end_time: datetime
    total_documents: int = 0
    total_iocs: int = 0

    # Aggregated counts
    total_regex_extracted: int = 0
    total_llm_validated: int = 0
    total_llm_only: int = 0
    total_direct_accept: int = 0

    # Aggregated timing
    total_regex_time_ms: float = 0.0
    total_llm_time_ms: float = 0.0
    total_processing_time_ms: float = 0.0

    # Aggregated LLM usage
    total_llm_calls: int = 0

    # Averages
    avg_iocs_per_document: float = 0.0
    avg_confidence: float = 0.0
    avg_llm_validation_rate: float = 0.0
    avg_speedup_factor: float = 0.0

    # Confidence distribution across all documents
    overall_confidence_distribution: Dict[str, int] = Field(default_factory=dict)
    overall_ioc_type_distribution: Dict[str, int] = Field(default_factory=dict)

    def add_extraction_metrics(self, metrics: ExtractionMetrics):
        """Add metrics from a single extraction."""
        self.total_documents += 1
        self.total_iocs += metrics.total_iocs

        self.total_regex_extracted += metrics.regex_extracted
        self.total_llm_validated += metrics.llm_validated
        self.total_llm_only += metrics.llm_only
        self.total_direct_accept += metrics.direct_accept

        self.total_regex_time_ms += metrics.regex_time_ms
        self.total_llm_time_ms += metrics.llm_time_ms
        self.total_processing_time_ms += metrics.total_time_ms

        self.total_llm_calls += metrics.llm_calls_made

        # Merge confidence distributions
        for level, count in metrics.confidence_distribution.items():
            self.overall_confidence_distribution[level] = (
                self.overall_confidence_distribution.get(level, 0) + count
            )

        # Merge IOC type distributions
        for ioc_type, count in metrics.ioc_type_distribution.items():
            self.overall_ioc_type_distribution[ioc_type] = (
                self.overall_ioc_type_distribution.get(ioc_type, 0) + count
            )

    def calculate_averages(self):
        """Calculate average metrics."""
        if self.total_documents > 0:
            self.avg_iocs_per_document = self.total_iocs / self.total_documents

            # Calculate average confidence
            if self.overall_confidence_distribution:
                total_weighted = 0
                total_count = 0
                confidence_values = {
                    "very_high": 97.5,
                    "high": 89.5,
                    "medium": 77.0,
                    "low": 59.5,
                    "very_low": 25.0,
                }
                for level, count in self.overall_confidence_distribution.items():
                    total_weighted += confidence_values.get(level, 70.0) * count
                    total_count += count
                if total_count > 0:
                    self.avg_confidence = total_weighted / total_count

        if self.total_iocs > 0:
            self.avg_llm_validation_rate = (
                (self.total_llm_validated + self.total_llm_only) / self.total_iocs * 100
            )

        if self.total_processing_time_ms > 0:
            llm_only_time = self.total_iocs * 2000
            self.avg_speedup_factor = llm_only_time / self.total_processing_time_ms

    def to_summary_dict(self) -> Dict:
        """Convert to summary dictionary."""
        return {
            "period": {
                "start": self.start_time.isoformat(),
                "end": self.end_time.isoformat(),
                "duration_hours": (self.end_time - self.start_time).total_seconds()
                / 3600,
            },
            "totals": {
                "documents": self.total_documents,
                "iocs": self.total_iocs,
                "llm_calls": self.total_llm_calls,
            },
            "averages": {
                "iocs_per_document": round(self.avg_iocs_per_document, 1),
                "confidence": round(self.avg_confidence, 1),
                "llm_validation_rate": round(self.avg_llm_validation_rate, 1),
                "speedup_factor": round(self.avg_speedup_factor, 2),
            },
            "distributions": {
                "confidence": self.overall_confidence_distribution,
                "ioc_types": self.overall_ioc_type_distribution,
            },
        }


if __name__ == "__main__":
    # Test the metrics models
    import json

    # Create sample extraction metrics
    metrics = ExtractionMetrics(
        document_size=5000,
        total_iocs=10,
        regex_extracted=8,
        llm_validated=2,
        llm_only=0,
        direct_accept=8,
        regex_time_ms=25.5,
        llm_time_ms=1500.0,
        total_time_ms=1550.0,
        llm_calls_made=1,
        confidence_distribution={"very_high": 6, "high": 2, "medium": 2},
        ioc_type_distribution={"MD5 Hash": 3, "Domain or URL": 5, "IP Address": 2},
    )

    metrics.calculate_derived_metrics()

    print("Extraction Metrics Summary:")
    print(json.dumps(metrics.to_summary_dict(), indent=2))

    print("\n" + "=" * 50 + "\n")

    # Create aggregated metrics
    agg = AggregatedMetrics(start_time=datetime.utcnow(), end_time=datetime.utcnow())

    # Add multiple extraction metrics
    for i in range(5):
        agg.add_extraction_metrics(metrics)

    agg.calculate_averages()

    print("Aggregated Metrics Summary:")
    print(json.dumps(agg.to_summary_dict(), indent=2))
