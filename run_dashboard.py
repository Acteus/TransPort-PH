#!/usr/bin/env python3
"""
Launcher script for TransPort-PH Dashboard
===========================================
Run this script from the project root to launch the Streamlit dashboard.

Usage:
    python run_dashboard.py
"""

import subprocess
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.absolute()
dashboard_path = project_root / "src" / "visualization" / "dashboard_app.py"

if not dashboard_path.exists():
    print(f"Error: Dashboard not found at {dashboard_path}")
    sys.exit(1)

print("=" * 80)
print("Starting TransPort-PH Dashboard...")
print("=" * 80)
print(f"\nDashboard location: {dashboard_path}")
print("\nThe dashboard will open in your default web browser.")
print("Press Ctrl+C to stop the server.\n")

# Run streamlit
try:
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(dashboard_path),
        "--server.port", "8501",
        "--browser.gatherUsageStats", "false"
    ], check=True)
except KeyboardInterrupt:
    print("\n\nDashboard stopped by user.")
    sys.exit(0)
except subprocess.CalledProcessError as e:
    print(f"\nError running dashboard: {e}")
    sys.exit(1)

