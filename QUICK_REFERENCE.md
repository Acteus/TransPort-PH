# TransPort-PH Quick Reference Card

## Quick Commands

```bash
# Start Dashboard
python run_dashboard.py

# Run Full Pipeline
python run_pipeline.py

# Run Tests
python tests/test_config.py

# Install Dependencies
pip install -r requirements.txt

# Install as Package (Development Mode)
pip install -e .
```

## 📁 Directory Guide

| Directory | Purpose | Example Files |
|-----------|---------|---------------|
| `config/` | Configuration | `config.py` |
| `src/data_collection/` | Data gathering | `data_gathering_worldbank.py` |
| `src/preprocessing/` | Data cleaning | `feature_engineering.py` |
| `src/models/` | Model training | `train_tft_model.py` |
| `src/analysis/` | Analysis | `causal_modeling_dowhy.py` |
| `src/visualization/` | Dashboard | `dashboard_app.py` |
| `src/utils/` | Orchestration | `run_all.py` |
| `tests/` | Testing | `test_config.py` |
| `data/` | Data files | `*.csv` (gitignored) |
| `output/` | Results | `*.png` (gitignored) |
| `models/` | Trained models | `*.ckpt` (gitignored) |
| `docs/` | Documentation | `*.md` |

## Configuration Import

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import configuration
from config import (
    DATA_DIR,          # Path to data directory
    OUTPUT_DIR,        # Path to output directory
    MODELS_DIR,        # Path to models directory
    RAW_DATA,          # Dict of raw data file paths
    PROCESSED_DATA,    # Dict of processed data paths
    MODEL_PARAMS,      # Model hyperparameters
    get_path,          # Helper function
)
```

## Common Paths

```python
# Raw data files
RAW_DATA["worldbank"]  # World Bank data
RAW_DATA["dpwh"]       # DPWH data
RAW_DATA["jica"]       # JICA transit data
RAW_DATA["tomtom"]     # Traffic data
RAW_DATA["openaq"]     # Air quality data

# Processed data
PROCESSED_DATA["clean_panel"]       # Main dataset
PROCESSED_DATA["clean_panel_train"] # Training set
PROCESSED_DATA["clean_panel_test"]  # Test set

# Using get_path helper
path = get_path("raw", "worldbank")
path = get_path("processed", "clean_panel")
```

## Dashboard Pages

| Page | Description |
|------|-------------|
| **Overview** | Project summary and key metrics |
| **Data Quality** | Data coverage and improvements |
| **Scenario Comparison** | Policy scenario results |
| **Country Analysis** | Country-specific impacts |
| **Time Series** | Temporal trends |
| **Uncertainty Analysis** | Model uncertainty quantification |
| **Custom Simulator** | Interactive policy simulator |
| **Deep Dive** | Detailed analysis |
| **Reports** | Generated reports |

## File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Data Collection | `data_gathering_<source>.py` | `data_gathering_worldbank.py` |
| Analysis | `<analysis_type>_*.py` | `causal_modeling_dowhy.py` |
| EDA | `eda_<type>.py` | `eda_correlation_clustering.py` |
| Utilities | `<action>_<object>.py` | `run_all.py` |

## Finding Code

**Need to...** | **Look in...**
---|---
Gather new data | `src/data_collection/`
Clean data | `src/preprocessing/`
Train model | `src/models/`
Run analysis | `src/analysis/`
Create visualization | `src/visualization/`
Run full pipeline | `src/utils/run_all.py`
Launch dashboard | `python run_dashboard.py`

## Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes**
   - Edit files in appropriate `src/` subdirectory
   - Use config for paths
   - Add docstrings

3. **Test locally**
   ```bash
   python tests/test_config.py
   # Run affected scripts
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: Description"
   git push origin feature/my-feature
   ```

5. **Create Pull Request**

## Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main project documentation |
| `QUICK_START.md` | 5-minute quick start |
| `CONTRIBUTING.md` | How to contribute |
| `MIGRATION_GUIDE.md` | Using new structure |
| `CHANGELOG.md` | Version history |
| `REORGANIZATION_SUMMARY.md` | Reorganization details |
| `QUICK_REFERENCE.md` | This file |

## Key Features

- **7,430** observations
- **275** countries/regions
- **100%** panel coverage
- **0.24** validation loss (TFT model)
- **12** data sources
- **5** analysis modules
- **9** visualization types

##Important Links

- **Repository**: [GitHub URL]
- **Issues**: [GitHub Issues URL]
- **Discussions**: [GitHub Discussions URL]
- **Documentation**: See `docs/` directory

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Import errors | Add project root to `sys.path` |
| Path not found | Use config paths, ensure directories exist |
| Dashboard won't start | Check if port 8501 is available |
| Missing data | Run data collection scripts |
| Config errors | Run `python tests/test_config.py` |

---


