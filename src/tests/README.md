# Python Tests

This directory contains the automated tests for the Python codebase.

## Running Tests Locally

To run the tests locally, you can use the provided script:

```bash
./src/tests/run_tests.sh
```

This script will automatically create a virtual environment, install the necessary dependencies, and run the tests with coverage reporting.

Alternatively, if you already have a virtual environment set up, you can run `pytest` directly from the root directory:

```bash
pytest
```

## Test Coverage

We aim for high test coverage to ensure the reliability of our code. The current test suite covers 100% of the Python codebase.

## Continuous Integration

Tests are automatically run on every push and pull request to the `main` branch using GitHub Actions. The workflow configuration can be found in `.github/workflows/python-tests.yml`.
