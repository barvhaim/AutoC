# IOC Extraction Evaluation System

This directory contains tools for systematically evaluating and improving IOC extraction without running the full analysis pipeline.

## Files

- **`ioc_extraction_eval_dataset.json`**: Evaluation dataset with test cases for different IOC types
- **`test_ioc_extraction.py`**: Test script to evaluate IOC extraction performance

## Quick Start

### Run All Tests

```bash
# From project root
uv run python tests/test_ioc_extraction.py
```

### Run with Verbose Output

```bash
uv run python tests/test_ioc_extraction.py --verbose
```

### Run Specific Test Case

```bash
uv run python tests/test_ioc_extraction.py --test-id url_test_1
```

### Use Custom Dataset

```bash
uv run python tests/test_ioc_extraction.py --dataset path/to/custom_dataset.json
```

## Understanding the Output

The script provides:

1. **Overall Summary**: Total tests, pass rate, failed tests
2. **Metrics by IOC Type**: Precision, Recall, F1 score for each IOC type (URL, IP, MD5, SHA256, CHROME_EXTENSION)
3. **Failed Test Details**: Shows expected vs actual IOCs for failed tests

### Metrics Explained

- **Precision**: Of the IOCs extracted, how many were correct?
- **Recall**: Of the expected IOCs, how many were found?
- **F1 Score**: Harmonic mean of precision and recall (1.0 = perfect)

## Dataset Structure

```json
{
  "description": "Dataset description",
  "source_url": "Source URL if applicable",
  "test_cases": [
    {
      "id": "unique_test_id",
      "ioc_type": "URL|IP|MD5|SHA256|CHROME_EXTENSION",
      "content": "Text content containing IOCs",
      "expected_iocs": ["list", "of", "expected", "iocs"]
    }
  ]
}
```

## Adding New Test Cases

1. Open `ioc_extraction_eval_dataset.json`
2. Add a new test case to the `test_cases` array:

```json
{
  "id": "my_new_test",
  "ioc_type": "URL",
  "content": "The malware connects to https://evil.com",
  "expected_iocs": ["https://evil.com"]
}
```

3. Run the tests to verify

## Improving IOC Extraction

### Workflow

1. **Run baseline evaluation**:
   ```bash
   uv run python tests/test_ioc_extraction.py --verbose
   ```

2. **Identify failing test cases** from the output

3. **Modify the prompt** in `backend/prompts/extract_iocs.yaml`

4. **Re-run evaluation** to measure improvement:
   ```bash
   uv run python tests/test_ioc_extraction.py
   ```

5. **Iterate** until desired performance is achieved

### Tips for Prompt Improvement

- **Be explicit** about output format (JSON array only)
- **Provide examples** of valid and invalid outputs
- **Specify edge cases** (e.g., obfuscated URLs with hxxps)
- **Use clear instructions** about what to include/exclude
- **Test incrementally** with specific test cases using `--test-id`

## Current Test Coverage

The dataset includes tests for:

- **URL extraction**: Single and multiple URLs, C2 servers
- **IP extraction**: IPv4 and IPv6 addresses
- **MD5 extraction**: Single and multiple MD5 hashes
- **SHA256 extraction**: SHA256 hashes in various formats
- **Chrome Extension extraction**: Extension IDs
- **Mixed content**: Multiple IOC types in same text
- **Empty cases**: Content with no IOCs (should return empty array)

## Example Session

```bash
$ uv run python tests/test_ioc_extraction.py --verbose

INFO:__main__:Running 13 test case(s)...
INFO:__main__:Running test case: url_test_1 (type: URL)
INFO:__main__:  Expected: ['hxxps://dlxfreights.site/uadmin/gate.php']
INFO:__main__:  Actual: ['hxxps://dlxfreights.site/uadmin/gate.php']
INFO:__main__:  Metrics: P=1.00, R=1.00, F1=1.00
INFO:__main__:  Status: ✓ PASS
...

================================================================================
IOC EXTRACTION EVALUATION SUMMARY
================================================================================
Total Tests: 13
Passed: 10 (76.9%)
Failed: 3

Metrics by IOC Type:
--------------------------------------------------------------------------------

URL:
  Tests: 4/5 passed
  Avg Precision: 0.850
  Avg Recall: 0.900
  Avg F1: 0.870
...
```

## Troubleshooting

### Import Errors

Make sure you're running from the project root:
```bash
cd /path/to/AutoC
uv run python tests/test_ioc_extraction.py
```

### LLM Connection Issues

Check your `.env` file has correct LLM configuration:
```bash
LLM_PROVIDER=watsonx
LLM_MODEL=meta-llama/llama-3-3-70b-instruct
WATSONX_API_KEY=your_key_here
```

### JSON Parsing Errors

This is the issue we're trying to fix! The test script will show which test cases are failing due to JSON parsing errors, helping you improve the prompt systematically.

## Next Steps

After achieving good performance on the evaluation dataset:

1. Test with real-world articles using the full pipeline
2. Add more diverse test cases based on failures
3. Consider implementing fallback extraction methods (regex-based)
4. Experiment with different LLM models or parameters