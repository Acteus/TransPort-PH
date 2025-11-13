#!/usr/bin/env python3
"""
Launcher script for TransPort-PH Full Pipeline
==============================================
Run this script from the project root to execute the full data pipeline.

Usage:
    python run_pipeline.py [--skip-gathering] [--skip-eda]
    
Options:
    --skip-gathering    Skip data gathering steps (use existing data)
    --skip-eda          Skip exploratory data analysis
"""

import subprocess
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.absolute()
run_all_path = project_root / "src" / "utils" / "run_all.py"

if not run_all_path.exists():
    print(f"Error: Pipeline script not found at {run_all_path}")
    sys.exit(1)

print("=" * 80)
print("Starting TransPort-PH Pipeline...")
print("=" * 80)
print(f"\nPipeline script: {run_all_path}")
print("\nThis will run all data collection, preprocessing, and analysis steps.")
print("This may take several hours depending on your system.\n")

# Forward any command line arguments
args = [sys.executable, str(run_all_path)] + sys.argv[1:]

try:
    subprocess.run(args, check=True, cwd=str(project_root))
except KeyboardInterrupt:
    print("\n\nPipeline stopped by user.")
    sys.exit(0)
except subprocess.CalledProcessError as e:
    print(f"\nError running pipeline: {e}")
    sys.exit(1)

