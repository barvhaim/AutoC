"""
IOC Extraction Evaluation Script

This script tests the IOC extraction functionality using a predefined evaluation dataset.
It helps systematically improve prompts without running the full analysis pipeline.

Usage:
    python tests/test_ioc_extraction.py
    python tests/test_ioc_extraction.py --verbose
    python tests/test_ioc_extraction.py --test-id url_test_1
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import argparse

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.extractors.iocs_extractor import IOCsExtractor
from backend.data_model.ioc import IOCType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IOCExtractionEvaluator:
    """Evaluates IOC extraction performance against a test dataset"""

    def __init__(self, dataset_path: str = "tests/ioc_extraction_eval_dataset.json"):
        self.dataset_path = Path(dataset_path)
        self.dataset = self._load_dataset()
        self.results = []

    def _load_dataset(self) -> Dict[str, Any]:
        """Load the evaluation dataset"""
        try:
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Dataset not found at {self.dataset_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse dataset: {e}")
            raise

    def _extract_iocs_for_type(self, content: str, ioc_type_str: str) -> List[str]:
        """Extract IOCs of a specific type from content"""
        try:
            # Map string to IOCType enum
            ioc_type = IOCType[ioc_type_str]

            # Create extractor with the content
            extractor = IOCsExtractor(article_content=content)

            # Extract IOCs
            iocs = extractor.extract_iocs_from_text()

            # Filter by type and return values
            return [ioc.value for ioc in iocs if ioc.type == ioc_type]
        except Exception as e:
            logger.error(f"Extraction failed for {ioc_type_str}: {str(e)}")
            return []

    def _calculate_metrics(
        self, expected: List[str], actual: List[str]
    ) -> Dict[str, Any]:
        """Calculate precision, recall, and F1 score"""
        expected_set = set(expected)
        actual_set = set(actual)

        true_positives = len(expected_set & actual_set)
        false_positives = len(actual_set - expected_set)
        false_negatives = len(expected_set - actual_set)

        # Special case: both empty is considered perfect match
        if len(expected) == 0 and len(actual) == 0:
            return {
                "precision": 1.0,
                "recall": 1.0,
                "f1": 1.0,
                "true_positives": 0,
                "false_positives": 0,
                "false_negatives": 0,
                "expected_count": 0,
                "actual_count": 0,
            }

        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0
            else 0
        )
        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0
            else 0
        )
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0
        )

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "expected_count": len(expected),
            "actual_count": len(actual),
        }

    def run_test_case(
        self, test_case: Dict[str, Any], verbose: bool = False
    ) -> Dict[str, Any]:
        """Run a single test case"""
        test_id = test_case["id"]
        ioc_type = test_case["ioc_type"]
        content = test_case["content"]
        expected_iocs = test_case["expected_iocs"]

        logger.info(f"Running test case: {test_id} (type: {ioc_type})")

        # Extract IOCs
        actual_iocs = self._extract_iocs_for_type(content, ioc_type)

        # Calculate metrics
        metrics = self._calculate_metrics(expected_iocs, actual_iocs)

        # Prepare result
        result = {
            "test_id": test_id,
            "ioc_type": ioc_type,
            "expected": expected_iocs,
            "actual": actual_iocs,
            "metrics": metrics,
            "passed": metrics["f1"] == 1.0,
        }

        if verbose:
            logger.info(f"  Expected: {expected_iocs}")
            logger.info(f"  Actual: {actual_iocs}")
            logger.info(
                f"  Metrics: P={metrics['precision']:.2f}, R={metrics['recall']:.2f}, F1={metrics['f1']:.2f}"
            )
            logger.info(f"  Status: {'✓ PASS' if result['passed'] else '✗ FAIL'}")

        return result

    def run_all_tests(
        self, verbose: bool = False, test_id: str = None
    ) -> Dict[str, Any]:
        """Run all test cases or a specific test"""
        test_cases = self.dataset["test_cases"]

        # Filter by test_id if specified
        if test_id:
            test_cases = [tc for tc in test_cases if tc["id"] == test_id]
            if not test_cases:
                logger.error(f"Test case '{test_id}' not found")
                return {"error": f"Test case '{test_id}' not found"}

        logger.info(f"Running {len(test_cases)} test case(s)...")

        results = []
        for test_case in test_cases:
            result = self.run_test_case(test_case, verbose=verbose)
            results.append(result)

        # Calculate overall metrics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["passed"])

        # Aggregate metrics by IOC type
        type_metrics = {}
        for result in results:
            ioc_type = result["ioc_type"]
            if ioc_type not in type_metrics:
                type_metrics[ioc_type] = {
                    "total": 0,
                    "passed": 0,
                    "avg_precision": 0,
                    "avg_recall": 0,
                    "avg_f1": 0,
                }

            type_metrics[ioc_type]["total"] += 1
            if result["passed"]:
                type_metrics[ioc_type]["passed"] += 1
            type_metrics[ioc_type]["avg_precision"] += result["metrics"]["precision"]
            type_metrics[ioc_type]["avg_recall"] += result["metrics"]["recall"]
            type_metrics[ioc_type]["avg_f1"] += result["metrics"]["f1"]

        # Calculate averages
        for ioc_type, metrics in type_metrics.items():
            total = metrics["total"]
            metrics["avg_precision"] /= total
            metrics["avg_recall"] /= total
            metrics["avg_f1"] /= total

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "type_metrics": type_metrics,
            "results": results,
        }

        return summary

    def print_summary(self, summary: Dict[str, Any]):
        """Print a formatted summary of results"""
        print("\n" + "=" * 80)
        print("IOC EXTRACTION EVALUATION SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']} ({summary['pass_rate']*100:.1f}%)")
        print(f"Failed: {summary['failed_tests']}")
        print("\nMetrics by IOC Type:")
        print("-" * 80)

        for ioc_type, metrics in summary["type_metrics"].items():
            print(f"\n{ioc_type}:")
            print(f"  Tests: {metrics['passed']}/{metrics['total']} passed")
            print(f"  Avg Precision: {metrics['avg_precision']:.3f}")
            print(f"  Avg Recall: {metrics['avg_recall']:.3f}")
            print(f"  Avg F1: {metrics['avg_f1']:.3f}")

        print("\n" + "=" * 80)

        # Show failed tests
        failed_tests = [r for r in summary["results"] if not r["passed"]]
        if failed_tests:
            print("\nFailed Tests:")
            print("-" * 80)
            for result in failed_tests:
                print(f"\n{result['test_id']} ({result['ioc_type']}):")
                print(f"  Expected: {result['expected']}")
                print(f"  Actual: {result['actual']}")
                print(f"  F1 Score: {result['metrics']['f1']:.3f}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate IOC extraction performance")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--test-id", "-t", type=str, help="Run specific test case by ID"
    )
    parser.add_argument(
        "--dataset",
        "-d",
        type=str,
        default="tests/ioc_extraction_eval_dataset.json",
        help="Path to evaluation dataset",
    )

    args = parser.parse_args()

    try:
        evaluator = IOCExtractionEvaluator(dataset_path=args.dataset)
        summary = evaluator.run_all_tests(verbose=args.verbose, test_id=args.test_id)

        if "error" not in summary:
            evaluator.print_summary(summary)

            # Exit with error code if tests failed
            if summary["failed_tests"] > 0:
                exit(1)
        else:
            logger.error(summary["error"])
            exit(1)

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
