"""AutoC Examples and Testing Documentation"""

# AutoC Testing and Examples

This directory contains tests and examples for AutoC (Automated IoC extraction tool).

## Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for API and services
└── e2e/           # End-to-end tests for complete workflows

examples/
├── basic_usage.py  # Basic usage examples
└── api_usage.py   # API usage examples
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install pytest pytest-asyncio pytest-mock httpx
```

### Unit Tests

Run fast, isolated unit tests:
```bash
pytest tests/unit/ -v
```

Test specific components:
```bash
pytest tests/unit/test_str_utils.py -v
pytest tests/unit/test_data_models.py -v
```

### Integration Tests

Run integration tests for API endpoints:
```bash
pytest tests/integration/ -v
```

Note: Integration tests may require additional dependencies.

### End-to-End Tests

Run comprehensive CLI and workflow tests:
```bash
pytest tests/e2e/ -v
```

### Run All Tests

Run all available tests:
```bash
pytest -v
```

## Examples

### Basic Usage Example

```bash
python examples/basic_usage.py
```

This example demonstrates:
- Basic URL analysis
- Raw text analysis  
- Custom keywords and analyst questions
- Ping mode for quick analysis

### API Usage Example

```bash
python examples/api_usage.py
```

This example demonstrates:
- Health check endpoint
- Analyze endpoint with URL
- Analyze endpoint with raw text
- Ping endpoint
- Feedback submission

Note: API examples require the AutoC server to be running:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Test Categories

### Unit Tests

Test individual functions and classes in isolation:
- String utilities (`test_str_utils.py`)
- Data models validation (`test_data_models.py`)
- Backend functions with mocks (`test_backend_run.py`)

### Integration Tests

Test component interactions:
- API endpoint functionality (`test_api.py`)
- Database interactions
- External service integrations

### End-to-End Tests

Test complete user workflows:
- CLI command execution (`test_cli.py`)
- Full analysis pipelines
- Error handling scenarios

## Testing Guidelines

1. **Write tests for new features**: All new functionality should include corresponding tests
2. **Test edge cases**: Include tests for error conditions and boundary cases
3. **Use appropriate test types**: Choose unit, integration, or e2e tests based on what you're testing
4. **Mock external dependencies**: Use mocks for external APIs and services in unit tests
5. **Keep tests fast**: Unit tests should run quickly; save slower tests for integration/e2e

## Test Configuration

Test configuration is in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
markers = [
    "unit: marks tests as unit tests (fast, isolated)",
    "integration: marks tests as integration tests (slower, requires components)",
    "e2e: marks tests as end-to-end tests (slowest, requires full setup)",
    "slow: marks tests as slow running"
]
```

## Running Specific Test Categories

Use markers to run specific test categories:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests  
pytest -m integration

# Run only e2e tests
pytest -m e2e

# Skip slow tests
pytest -m "not slow"
```

## Coverage

To run tests with coverage:

```bash
pip install pytest-cov
pytest --cov=backend --cov=api --cov-report=html
```

This generates an HTML coverage report in `htmlcov/`.

## Continuous Integration

These tests are designed to run in CI environments. The test suite includes:

- Fast unit tests that run on every commit
- Integration tests that run on pull requests
- E2E tests that run on releases

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Install required packages with pip
2. **Import errors**: Ensure PYTHONPATH includes the project root
3. **API tests failing**: Check if the AutoC server is running for integration tests
4. **Environment setup**: Copy `.env.sample` to `.env` and configure API keys for full functionality

### Getting Help

- Check test output for specific error messages
- Review the examples to understand expected behavior
- Check the main README.md for setup instructions
- Ensure all dependencies are properly installed