#!/bin/bash
set -e

echo "Running Backend Tests..."
cd ../../apps/api
pip install -r requirements.txt
python -m pytest

echo "Running Frontend Build..."
cd ../web
npm run build

echo "All tests passed successfully!"

