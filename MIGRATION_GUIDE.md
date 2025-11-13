# Migration Guide: Using the Reorganized Codebase

This guide helps you transition from the old `scripts/` directory structure to the new organized structure.

## What Changed?

### Directory Structure

**Before:**
```
TransPort-PH/
├── scripts/
│   ├── data_gathering_*.py
│   ├── train_tft_model.py
│   ├── dashboard_app.py
│   └── run_all.py
├── data/
├── output/
└── models/
```

**After:**
```
TransPort-PH/
├── src/
│   ├── data_collection/      # Data gathering scripts
│   ├── preprocessing/         # Data cleaning
│   ├── models/               # Model training
│   ├── analysis/             # Analysis scripts
│   ├── visualization/        # Dashboard & plots
│   └── utils/               # Orchestration scripts
├── config/                   # Configuration
├── data/                     # Data files
├── output/                   # Generated outputs
├── models/                   # Trained models
├── docs/                     # Documentation
├── tests/                    # Tests
├── run_dashboard.py          # Easy launcher
├── run_pipeline.py           # Easy launcher
└── requirements.txt          # Dependencies
```

## How to Use the New Structure

### Running the Dashboard

**Before:**
```bash
cd scripts
streamlit run dashboard_app.py
```

**After (Option 1 - Recommended):**
```bash
python run_dashboard.py
```

**After (Option 2):**
```bash
cd src/visualization
streamlit run dashboard_app.py
```

### Running the Full Pipeline

**Before:**
```bash
cd scripts
python run_all.py
```

**After (Option 1 - Recommended):**
```bash
python run_pipeline.py
```

**After (Option 2):**
```bash
cd src/utils
python run_all.py
```

### Running Individual Scripts

**Before:**
```bash
cd scripts
python data_gathering_worldbank.py
```

**After:**
```bash
cd src/data_collection
python data_gathering_worldbank.py
```

Or use the module structure:
```bash
python -m src.data_collection.data_gathering_worldbank
```

## Path Handling Updates

### Old Way (Hardcoded Paths)
```python
import os

data_path = os.path.join('..', 'data', 'worldbank_data.csv')
output_path = '../output/results.png'
```

### New Way (Config-Based)
```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config import DATA_DIR, OUTPUT_DIR, RAW_DATA

data_path = RAW_DATA["worldbank"]
output_path = OUTPUT_DIR / "results.png"
```

## Configuration Management

All paths and parameters are now centralized in `config/config.py`:

```python
from config import (
    DATA_DIR,          # data/ directory
    OUTPUT_DIR,        # output/ directory
    MODELS_DIR,        # models/ directory
    RAW_DATA,          # Dictionary of raw data file paths
    PROCESSED_DATA,    # Dictionary of processed data paths
    MODEL_PARAMS,      # Model hyperparameters
    DATA_PARAMS,       # Data processing parameters
)
```

## Package Installation

The project can now be installed as a package:

```bash
# Development mode (editable install)
pip install -e .

# With development dependencies
pip install -e .[dev]
```

## Finding Scripts

| Old Location | New Location | Purpose |
|-------------|--------------|---------|
| `scripts/data_gathering_*.py` | `src/data_collection/` | Data collection |
| `scripts/data_inspection.py` | `src/preprocessing/` | Data inspection |
| `scripts/feature_engineering.py` | `src/preprocessing/` | Feature engineering |
| `scripts/train_tft_model.py` | `src/models/` | Model training |
| `scripts/causal_modeling_dowhy.py` | `src/analysis/` | Causal analysis |
| `scripts/dashboard_app.py` | `src/visualization/` | Dashboard |
| `scripts/run_all.py` | `src/utils/` | Pipeline orchestration |

## Troubleshooting

### Import Errors

If you get import errors:

```python
# Add this at the top of your script
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
```

### Path Not Found Errors

Make sure you're using config paths:

```python
from config import DATA_DIR
DATA_DIR.mkdir(parents=True, exist_ok=True)
```

### Running from Wrong Directory

Use the wrapper scripts from project root:
```bash
cd /path/to/TransPort-PH
python run_dashboard.py
```

## Additional Resources

- [README.md](README.md) - Project overview
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [docs/QUICK_START.md](docs/QUICK_START.md) - Quick start guide
- [config/config.py](config/config.py) - Configuration reference

## Deprecation Notice

The old `scripts/` directory is kept for backward compatibility but may be removed in future versions. Please migrate to the new structure.

## Tips

1. **Always run from project root** using wrapper scripts
2. **Use config paths** instead of hardcoding
3. **Import from src modules** rather than copying code
4. **Update your bookmarks** to point to new script locations
5. **Check config.py** when adding new data sources

---

**Questions?** Open an issue or check the documentation!

