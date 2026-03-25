#!/bin/bash
set -e

echo "Running Python tests..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q pytest pytest-cov pymysql faker

pytest --cov=src --cov-report=term-missing src/tests/
echo "Tests completed successfully!"
