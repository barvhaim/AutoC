"""Test hybrid IOC extraction on real blog article."""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.extractors.hybrid_ioc_extractor import HybridIOCExtractor
from backend.extractors.hybrid_config import HybridExtractionConfig


def test_blog_article():
    """Test extraction on real blog article."""

    # Read the blog article
    blog_path = Path(__file__).parent / "test_blog_article.txt"
    with open(blog_path, "r", encoding="utf-8") as f:
        text = f.read()

    print("=" * 80)
    print("Testing Hybrid IOC Extraction on Real Blog Article")
    print("=" * 80)
    print(f"\nDocument size: {len(text)} characters")
    print(f"Document lines: {len(text.splitlines())}")

    # Test with default config
    print("\n" + "-" * 80)
    print("Test 1: Default Configuration")
    print("-" * 80)

    extractor = HybridIOCExtractor()
    iocs, metrics = extractor.extract(text, document_id="blog_article")

    print(f"\n✅ Extracted {len(iocs)} IOCs")

    # Group by type
    by_type = {}
    for ioc in iocs:
        ioc_type = ioc.type.value if hasattr(ioc.type, "value") else str(ioc.type)
        if ioc_type not in by_type:
            by_type[ioc_type] = []
        by_type[ioc_type].append(ioc)

    print("\nIOCs by Type:")
    for ioc_type, type_iocs in sorted(by_type.items()):
        print(f"\n  {ioc_type} ({len(type_iocs)}):")
        for ioc in type_iocs[:5]:  # Show first 5 of each type
            conf = ioc.confidence if ioc.confidence is not None else 0.0
            method = (
                ioc.extraction_method.value
                if ioc.extraction_method and hasattr(ioc.extraction_method, "value")
                else "unknown"
            )
            print(f"    - {ioc.value} ({conf:.1f}%, {method})")
        if len(type_iocs) > 5:
            print(f"    ... and {len(type_iocs) - 5} more")

    print("\n" + "-" * 80)
    print("Performance Metrics:")
    print("-" * 80)
    metrics_summary = metrics.to_summary_dict()

    print(f"\nTiming:")
    print(f"  Regex extraction: {metrics_summary['timing_ms']['regex']:.2f}ms")
    print(
        f"  Context analysis: {metrics_summary['timing_ms']['context_analysis']:.2f}ms"
    )
    print(f"  Scoring: {metrics_summary['timing_ms']['scoring']:.2f}ms")
    print(f"  LLM validation: {metrics_summary['timing_ms']['llm']:.2f}ms")
    print(f"  Total: {metrics_summary['timing_ms']['total']:.2f}ms")

    print(f"\nExtraction Breakdown:")
    print(
        f"  Regex only (direct accept): {metrics_summary['extraction_breakdown']['regex_only']}"
    )
    print(
        f"  Regex + LLM validated: {metrics_summary['extraction_breakdown']['regex_llm_validated']}"
    )
    print(f"  LLM only: {metrics_summary['extraction_breakdown']['llm_only']}")

    print(f"\nPerformance:")
    print(
        f"  LLM validation rate: {metrics_summary['performance']['llm_validation_rate']:.1f}%"
    )
    print(
        f"  Average confidence: {metrics_summary['performance']['avg_confidence']:.1f}%"
    )
    print(f"  Speedup factor: {metrics_summary['performance']['speedup_factor']:.2f}x")
    print(f"  LLM calls made: {metrics_summary['performance']['llm_calls']}")
    print(f"  Cost: ${metrics_summary['performance']['cost_usd']:.4f}")
    print(f"  Savings: ${metrics_summary['performance']['savings_usd']:.4f}")

    print(f"\nConfidence Distribution:")
    for level, count in sorted(metrics_summary["confidence_distribution"].items()):
        print(f"  {level}: {count}")

    # Test with cost-optimized config
    print("\n" + "=" * 80)
    print("Test 2: Cost-Optimized Configuration")
    print("=" * 80)

    cost_config = HybridExtractionConfig.create_cost_optimized_config()
    cost_extractor = HybridIOCExtractor(cost_config)
    cost_iocs, cost_metrics = cost_extractor.extract(
        text, document_id="blog_article_cost"
    )

    print(f"\n✅ Extracted {len(cost_iocs)} IOCs")
    print(f"  LLM validation rate: {cost_metrics.llm_validation_rate:.1f}%")
    print(f"  Cost: ${cost_metrics.estimated_cost_usd:.4f}")
    print(f"  Savings: ${cost_metrics.cost_savings_usd:.4f}")

    # Compare configurations
    print("\n" + "=" * 80)
    print("Configuration Comparison")
    print("=" * 80)
    print(f"\n{'Metric':<30} {'Default':<15} {'Cost-Optimized':<15}")
    print("-" * 60)
    print(f"{'IOCs extracted':<30} {len(iocs):<15} {len(cost_iocs):<15}")
    print(
        f"{'LLM validation rate':<30} {metrics.llm_validation_rate:.1f}%{'':<10} {cost_metrics.llm_validation_rate:.1f}%"
    )
    print(
        f"{'Total time (ms)':<30} {metrics.total_time_ms:.2f}{'':<10} {cost_metrics.total_time_ms:.2f}"
    )
    print(
        f"{'LLM calls':<30} {metrics.llm_calls_made:<15} {cost_metrics.llm_calls_made:<15}"
    )
    print(
        f"{'Cost (USD)':<30} ${metrics.estimated_cost_usd:.4f}{'':<10} ${cost_metrics.estimated_cost_usd:.4f}"
    )
    print(
        f"{'Savings (USD)':<30} ${metrics.cost_savings_usd:.4f}{'':<10} ${cost_metrics.cost_savings_usd:.4f}"
    )

    print("\n" + "=" * 80)
    print("✅ Test Complete!")
    print("=" * 80)

    return iocs, metrics


if __name__ == "__main__":
    test_blog_article()
