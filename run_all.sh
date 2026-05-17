#!/usr/bin/env bash
set -e

echo "Installing requirements..."
python3 -m pip install -r requirements.txt

echo "Generating dummy data..."
python3 src/generate_dummy_data.py

echo "Cleaning data..."
python3 src/load_clean.py

echo "Running stress test..."
python3 src/stress_runner.py

echo "Generating reports..."
python3 src/generate_reports.py

echo "Outputs written to outputs/"
